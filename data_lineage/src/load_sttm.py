"""
load_sttm.py — Load column-level nodes and lineage from STTM files into Neo4j.

Overview
--------
Phase 5 of the Medallion Architecture Knowledge Graph build.  This script
reads DD & STTM sheets from STTM Excel files and creates:

  1. Column nodes          — one per field in the target (Silver/Gold) table
  2. Column nodes          — one per referenced source (Replica) field
  3. (Table)-[:HAS_COLUMN]->(Column)   — containment
  4. (Column)-[:DERIVED_FROM]->(Column) — column-level lineage

Data Flow
---------
For each STTM file:
  a) Open the workbook and locate the 'DD & STTM' sheet (supports variants
     like 'DD & STTM - <suffix>').
  b) Parse the header row to find key columns using flexible matching:
     Physical Table Name, Silver Layer Field Name, Data Type, Keys,
     Source, Source Table Name, Source Field Name.
  c) For each data row:
     - Create/merge a Column node for the target field with properties:
       name, qualifiedName, dataType, keyType.
     - MERGE a HAS_COLUMN edge from the parent Table to the Column.
     - If the source is a valid table reference (not 'ETL Generated',
       'NA', 'config', or blank):
       * Create/merge a Column node for the source field.
       * MERGE HAS_COLUMN from the source Table to the source Column.
       * MERGE DERIVED_FROM from target Column to source Column.

Naming Conventions
------------------
  - Column qualifiedName = '{tableQualifiedName}.{fieldName}'
    e.g. 'mdm_core.MPR_Price_Master_Dim.Price_Master_Id'
  - Source table qualifiedName = '{sourceSchema}.{sourceTableName}'
    e.g. 'replica_mpr.PriceMaster'

Excluded Source Values
----------------------
  These values in the Source column are NOT table references:
    'ETL Generated', 'NA', 'config', '' (blank)
  Rows with these values still get a target Column node but no
  DERIVED_FROM edge (the column is system-generated, not sourced).

Prerequisites
-------------
  - Table nodes must already exist in Neo4j (run load_tables.py first)
  - pip install neo4j openpyxl python-dotenv

Usage
-----
    python src/load_sttm.py                         # Process pilot files only
    python src/load_sttm.py --all                   # Process all STTM files
    python src/load_sttm.py --file "SomeFile.xlsx"  # Process a single file
"""

import argparse
import os
import sys
import openpyxl

# Ensure src/ is on the path so neo4j_loader can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from excel_cells import pair_positional, split_multivalue
from medallion import cypher_is_legacy_schema, cypher_schema_layer
from neo4j_loader import Neo4jLoader

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STTM_DIR = os.path.join(PROJECT_ROOT, "Data", "sttms")

# ---------------------------------------------------------------------------
# Pilot files (used when no --all or --file flag)
# ---------------------------------------------------------------------------
PILOT_FILES = [
    "MPR_Price_Master_Dim - Silver Data Dictionary and STTM.xlsx",
    "MPR_Price_Detail_Fact - Silver Data Dictionary and STTM.xlsx",
    "Kittyhawk_Location_Dim - Silver Data Dictionary and STTM.xlsx",
]

# ---------------------------------------------------------------------------
# Replica schema → source DataSystem name mapping.
# Mirrors the mapping in load_schemas.py.  Used to create Operational source
# Table nodes and table-level REPLICATED_TO edges.
# ---------------------------------------------------------------------------
REPLICA_TO_DATASYSTEM = {
    "replica_eis":              "EIS",
    "replica_genscape":         "Genscape",
    "replica_kittyhawk":        "Kittyhawk",
    "replica_kpler":            "Kpler",
    "replica_ltpf":             "LTPF",
    "replica_mips":             "MIPS",
    "replica_mips_ltpf":        "MIPS-LTPF",
    "replica_mpr":              "MPR",
    "replica_weather":          "Weather",
}

# ---------------------------------------------------------------------------
# Source values that are NOT table references — skip DERIVED_FROM for these
# ---------------------------------------------------------------------------
SKIP_SOURCES = {"etl", "etl generated", "na", "config", ""}

# ---------------------------------------------------------------------------
# Cypher Queries
# ---------------------------------------------------------------------------

# Create a Column node and link it to its parent Table via HAS_COLUMN.
# Uses MERGE on qualifiedName to be idempotent.
MERGE_COLUMN_QUERY = """
UNWIND $rows AS row
MERGE (col:Column {qualifiedName: row.colQN})
  ON CREATE SET col.name            = row.colName,
                col.dataType        = row.dataType,
                col.keyType         = row.keyType,
                col.sourceDataType  = row.sourceDataType,
                col.definition      = row.definition,
                col.transformation  = row.transformation,
                col.sourceFile      = row.sourceFile
  ON MATCH SET  col.dataType        = row.dataType,
                col.keyType         = row.keyType,
                col.sourceDataType  = row.sourceDataType,
                col.definition      = row.definition,
                col.transformation  = row.transformation
WITH col, row
MATCH (t:Table {qualifiedName: row.tableQN})
MERGE (t)-[:HAS_COLUMN]->(col)
"""

# Create a DERIVED_FROM edge between target Column and source Column.
# Also ensures the source Table + Column + HAS_COLUMN exist, and wires
# the source Table into its parent Schema via CONTAINS.
MERGE_COL_DERIVED_FROM_QUERY = f"""
UNWIND $rows AS row
MERGE (tgtCol:Column {{qualifiedName: row.tgtColQN}})
MERGE (srcCol:Column {{qualifiedName: row.srcColQN}})
  ON CREATE SET srcCol.name       = row.srcColName,
                srcCol.sourceFile = row.sourceFile
WITH tgtCol, srcCol, row
MERGE (tgtCol)-[:DERIVED_FROM]->(srcCol)
WITH srcCol, row
MERGE (srcTable:Table {{qualifiedName: row.srcTableQN}})
  ON CREATE SET srcTable.name       = row.srcTableName,
               srcTable.layer      = {cypher_schema_layer("coalesce(row.srcSchemaQN, '')", "Replica")},
               srcTable.sourceFile = row.sourceFile,
               srcTable.createdAt  = datetime()
MERGE (srcTable)-[:HAS_COLUMN]->(srcCol)
WITH srcTable, row
FOREACH (_ IN CASE WHEN row.srcSchemaQN IS NOT NULL THEN [1] ELSE [] END |
  MERGE (sch:Schema {{qualifiedName: row.srcSchemaQN}})
  MERGE (sch)-[:CONTAINS]->(srcTable)
)
"""

# Post-processing: link any orphan Tables to their parent Schema.
# Derives the schema name from the qualifiedName prefix (before the dot).
LINK_ORPHAN_TABLES_QUERY = f"""
MATCH (t:Table)
WHERE t.sourceFile IS NOT NULL
  AND NOT (:Schema)-[:CONTAINS]->(t)
WITH t, split(t.qualifiedName, '.')[0] AS prefix
MERGE (s:Schema {{qualifiedName: prefix}})
  ON CREATE SET s.createdAt = datetime(),
                s.layer = {cypher_schema_layer("prefix", "Silver")}
FOREACH (_ IN CASE WHEN {cypher_is_legacy_schema("prefix")} THEN [1] ELSE [] END | SET s:Legacy)
MERGE (s)-[:CONTAINS]->(t)
RETURN count(t) AS linked
"""

# Post-processing: for each Replica table whose schema maps to a known
# DataSystem, create an Operational source Table and wire:
#   (DataSystem)-[:CONTAINS]->(OpTable)-[:REPLICATED_TO]->(ReplicaTable)
# This moves the REPLICATED_TO relationship to the table level where it
# semantically belongs.
ENSURE_OP_TABLES_QUERY = """
UNWIND $rows AS row
MERGE (op:Table {qualifiedName: row.opQN})
  ON CREATE SET op.name       = row.tableName,
               op.layer      = 'Operational',
               op.createdAt  = datetime()
WITH op, row
MATCH (ds:DataSystem {name: row.dsName})
MERGE (ds)-[:CONTAINS]->(op)
WITH op, row
MATCH (rep:Table {qualifiedName: row.replicaQN})
MERGE (op)-[:REPLICATED_TO]->(rep)
"""


# ---------------------------------------------------------------------------
# Header Matching
# ---------------------------------------------------------------------------
def find_column_indices(header_row):
    """Find key column indices from a header row using flexible matching.

    Returns a dict mapping logical names to column indices.
    Returns None for any column not found.
    """
    hdr = [str(c).strip().replace("\n", " ").lower() if c else "" for c in header_row]
    col_map = {}

    for i, h in enumerate(hdr):
        if "physical table" in h and "phys_table" not in col_map:
            col_map["phys_table"] = i
        elif ("silver layer field" in h or "gold layer field" in h) and "field_name" not in col_map:
            col_map["field_name"] = i
        elif h == "data type" and "data_type" not in col_map:
            col_map["data_type"] = i
        elif h == "keys" and "keys" not in col_map:
            col_map["keys"] = i
        elif (h == "source") and "source_schema" not in col_map:
            col_map["source_schema"] = i
        elif "source table" in h and "source_table" not in col_map:
            col_map["source_table"] = i
        elif "source field" in h and "source data" not in h and "source_field" not in col_map:
            col_map["source_field"] = i
        elif "source data" in h and "type" in h and "src_data_type" not in col_map:
            col_map["src_data_type"] = i
        elif ("definition" in h or "defintion" in h) and "definition" not in col_map:
            col_map["definition"] = i
        elif "transformation" in h and "transformation" not in col_map:
            col_map["transformation"] = i

    # Validate required columns are present
    required = ["phys_table", "field_name", "source_schema", "source_table", "source_field"]
    missing = [r for r in required if r not in col_map]
    if missing:
        return None, missing

    return col_map, []


# ---------------------------------------------------------------------------
# Cell value helper
# ---------------------------------------------------------------------------
def cell_val(row, col_map, key, default=""):
    """Safely extract a trimmed string value from a row."""
    # Not excel_cells.clean_cell: it rewrites the inner NBSP in the loaded
    # Column mdm_core.IIR_Plants_Dim.SIC\xa0_Code_Name and would fork that node.
    idx = col_map.get(key)
    if idx is None or idx >= len(row):
        return default
    v = row[idx]
    return str(v).strip() if v else default


def source_columns(schema_cell, table_cell, field_cell, context="", known_tables=()):
    """(schema, table, field) triples from the three Source cells of one STTM row, paired by position.

    Schema cells also use "/" as a separator ("udm_core/ mdm_core"); schema names never contain one.
    Analysts list several schemas in an order unrelated to the tables, so a table that already exists
    under one of the listed schemas (`known_tables`, lowercase qualifiedNames) takes that schema.
    """
    schemas = split_multivalue((schema_cell or "").replace("/", ","))
    tables = split_multivalue(table_cell)
    fields = split_multivalue(field_cell)
    if not schemas or not tables or not fields:
        return []

    def home_schema(paired_schema, table):
        if len(schemas) > 1 and f"{paired_schema}.{table}".lower() not in known_tables:
            return next((s for s in schemas if f"{s}.{table}".lower() in known_tables), paired_schema)
        return paired_schema

    return [
        (home_schema(schema, table), table, field)
        for schema, (table, field) in pair_positional(schemas, pair_positional(tables, fields, context), context)
        if schema.lower() not in SKIP_SOURCES
        and "," not in schema
        and "," not in table
        and "," not in field
    ]


# ---------------------------------------------------------------------------
# Process one STTM file
# ---------------------------------------------------------------------------
def process_sttm(filepath, loader):
    """Parse one STTM file and load Column nodes + DERIVED_FROM edges.

    Returns (n_columns, n_derived) counts.
    """
    fname = os.path.basename(filepath)
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)

    # Find DD & STTM sheet
    sttm_sheet = None
    for sn in wb.sheetnames:
        if "DD & STTM" in sn:
            sttm_sheet = sn
            break

    if not sttm_sheet:
        print(f"  SKIP {fname}: no 'DD & STTM' sheet found")
        wb.close()
        return 0, 0

    ws = wb[sttm_sheet]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 2:
        print(f"  SKIP {fname}: no data rows")
        return 0, 0

    # Parse header
    col_map, missing = find_column_indices(rows[0])
    if col_map is None:
        print(f"  SKIP {fname}: missing columns {missing}")
        return 0, 0

    qn_lookup = getattr(loader, "_qn_lookup", {})

    # Collect batches
    column_records = []     # For MERGE_COLUMN_QUERY
    derived_records = []    # For MERGE_COL_DERIVED_FROM_QUERY

    for row in rows[1:]:
        # Skip fully empty rows
        vals = [str(c).strip() if c else "" for c in row]
        if not any(vals[:12]):
            continue

        # Target table and field
        table_qn = cell_val(row, col_map, "phys_table")
        field_name = cell_val(row, col_map, "field_name")
        data_type = cell_val(row, col_map, "data_type")
        key_type = cell_val(row, col_map, "keys")

        if not table_qn or not field_name:
            continue

        # Target Column qualifiedName
        tgt_col_qn = f"{table_qn}.{field_name}"

        # Optional enrichment fields
        src_data_type = cell_val(row, col_map, "src_data_type") or None
        definition = cell_val(row, col_map, "definition") or None
        transformation = cell_val(row, col_map, "transformation") or None

        # Add target Column record
        column_records.append({
            "colQN": tgt_col_qn,
            "colName": field_name,
            "dataType": data_type,
            "keyType": key_type,
            "sourceDataType": src_data_type,
            "definition": definition,
            "transformation": transformation,
            "tableQN": table_qn,
            "sourceFile": fname,
        })

        for src_schema, src_table, src_field in source_columns(
            cell_val(row, col_map, "source_schema"),
            cell_val(row, col_map, "source_table"),
            cell_val(row, col_map, "source_field"),
            f"{fname} {tgt_col_qn}",
            qn_lookup,
        ):
            src_table_qn = Neo4jLoader.canonicalize_table_qn(f"{src_schema}.{src_table}", qn_lookup)
            derived_records.append({
                "tgtColQN": tgt_col_qn,
                "srcColQN": f"{src_table_qn}.{src_field}",
                "srcColName": src_field,
                "srcTableQN": src_table_qn,
                "srcTableName": src_table,
                "srcSchemaQN": src_schema,
                "sourceFile": fname,
            })

    # Load into Neo4j
    n_cols = len(column_records)
    n_derived = len(derived_records)

    if column_records:
        loader.write_batches(MERGE_COLUMN_QUERY, column_records)

    if derived_records:
        loader.write_batches(MERGE_COL_DERIVED_FROM_QUERY, derived_records)

    print(f"  {fname}")
    print(f"    Columns: {n_cols}  |  Column DERIVED_FROM: {n_derived}")

    return n_cols, n_derived


# ---------------------------------------------------------------------------
# Constraint setup
# ---------------------------------------------------------------------------
def ensure_constraints(loader):
    """Create uniqueness constraint on Column.qualifiedName if not exists."""
    query = """
    CREATE CONSTRAINT Column_qualifiedName_key IF NOT EXISTS
    FOR (c:Column) REQUIRE c.qualifiedName IS UNIQUE
    """
    try:
        loader.run_write(query)
        print("Constraint Column_qualifiedName_key ensured.")
    except Exception as e:
        # Constraint may already exist in a different form
        if "equivalent" in str(e).lower() or "already exists" in str(e).lower():
            print("Constraint Column_qualifiedName_key already exists.")
        else:
            raise


# ---------------------------------------------------------------------------
# Operational source table creation
# ---------------------------------------------------------------------------
def ensure_operational_tables(loader):
    """Create Operational source Tables and table-level REPLICATED_TO edges.

    For every Replica table whose schema prefix maps to a known DataSystem
    (via REPLICA_TO_DATASYSTEM), this function:
      1. Creates an Operational Table node  (e.g. 'MPR.PriceMaster')
      2. Wires  DataSystem -[:CONTAINS]-> OpTable
      3. Wires  OpTable -[:REPLICATED_TO]-> ReplicaTable

    Skips replica tables that already have an inbound REPLICATED_TO edge
    (e.g. those created by load_lineage.py for Alteryx provenance).
    """
    # Find all Replica tables that don't yet have an inbound REPLICATED_TO
    candidates = loader.run_query("""
        MATCH (rep:Table)
        WHERE rep.layer = 'Replica'
          AND NOT ()-[:REPLICATED_TO]->(rep)
        RETURN rep.qualifiedName AS qn, rep.name AS name
    """)

    rows = []
    for rec in candidates:
        qn = rec["qn"]          # e.g. 'replica_mpr.PriceMaster'
        table_name = rec["name"] # e.g. 'PriceMaster'
        schema_prefix = qn.split(".")[0] if "." in qn else None
        ds_name = REPLICA_TO_DATASYSTEM.get(schema_prefix)
        if ds_name and table_name:
            op_qn = f"{ds_name}.{table_name}"
            # Canonicalize to match existing Table nodes
            if hasattr(loader, '_qn_lookup'):
                op_qn = Neo4jLoader.canonicalize_table_qn(op_qn, loader._qn_lookup)
                qn = Neo4jLoader.canonicalize_table_qn(qn, loader._qn_lookup)
            rows.append({
                "opQN": op_qn,
                "tableName": table_name,
                "dsName": ds_name,
                "replicaQN": qn,
            })

    if not rows:
        print("  No new Operational tables to create.")
        return

    # Execute in batches
    loader.write_batches(ENSURE_OP_TABLES_QUERY, rows)

    print(f"  Created {len(rows)} Operational table(s) with REPLICATED_TO edges.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Load column-level lineage from STTM files")
    parser.add_argument("--all", action="store_true", help="Process all STTM files recursively in target directory")
    parser.add_argument("--file", type=str, help="Process a single STTM file by name (will search recursively if path is relative)")
    parser.add_argument("--dir", type=str, default="Data/sttms", help="Directory containing STTM files (relative to project root or absolute)")
    args = parser.parse_args()

    # Resolve target directory path
    sttm_dir = os.path.join(PROJECT_ROOT, args.dir) if not os.path.isabs(args.dir) else args.dir
    if not os.path.exists(sttm_dir):
        print(f"ERROR: Directory not found: {sttm_dir}")
        sys.exit(1)

    # Determine which files to process
    if args.file:
        # Walk recursively to find the file if it's not a direct absolute path
        found_file = None
        if os.path.isabs(args.file) and os.path.exists(args.file):
            found_file = args.file
        else:
            for root, _, fs in os.walk(sttm_dir):
                if args.file in fs:
                    found_file = os.path.join(root, args.file)
                    break
        if not found_file:
            print(f"ERROR: File not found: {args.file} under {sttm_dir}")
            sys.exit(1)
        files = [found_file]
    elif args.all:
        files = []
        for root, _, fs in os.walk(sttm_dir):
            for f in fs:
                if f.endswith(".xlsx") and not f.startswith("~"):
                    files.append(os.path.join(root, f))
        files = sorted(files)
    else:
        # Default: pilot files only
        files = []
        for f in PILOT_FILES:
            # Check top level first
            path = os.path.join(sttm_dir, f)
            if os.path.exists(path):
                files.append(path)
            else:
                # Recursive search fallback
                found = False
                for root, _, fs in os.walk(sttm_dir):
                    if f in fs:
                        files.append(os.path.join(root, f))
                        found = True
                        break
                if not found:
                    print(f"ERROR: Pilot file not found: {f}")
                    sys.exit(1)

    print(f"Processing {len(files)} STTM file(s)...\n")

    # Connect to Neo4j
    loader = Neo4jLoader()
    ensure_constraints(loader)

    # Build Table qualifiedName lookup for case-insensitive dedup
    print("Building Table qualifiedName lookup for case-insensitive dedup...")
    loader._qn_lookup = loader.build_table_qn_lookup()

    # Process each file
    total_cols = 0
    total_derived = 0
    for fpath in files:
        n_c, n_d = process_sttm(fpath, loader)
        total_cols += n_c
        total_derived += n_d

    # Post-processing: link orphan stub tables to their Schema
    print("\nLinking orphan tables to their parent Schema...")
    results = loader.run_query(LINK_ORPHAN_TABLES_QUERY)
    linked = results[0]['linked'] if results else 0
    print(f"  Linked {linked} orphan table(s) to their Schema.")

    # Post-processing: create Operational source tables + table-level REPLICATED_TO
    print("\nCreating Operational source tables and table-level REPLICATED_TO...")
    ensure_operational_tables(loader)

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Files processed:        {len(files)}")
    print(f"  Column nodes created:   {total_cols}")
    print(f"  Column DERIVED_FROM:    {total_derived}")
    print(f"{'='*60}")

    # Quick verification
    print("\nVerification:")
    results = loader.run_query("MATCH (c:Column) RETURN count(c) AS columnCount")
    print(f"  Total Column nodes in graph: {results[0]['columnCount']}")

    results = loader.run_query(
        "MATCH (:Column)-[d:DERIVED_FROM]->(:Column) RETURN count(d) AS colDerivedCount"
    )
    print(f"  Total Column DERIVED_FROM edges: {results[0]['colDerivedCount']}")

    results = loader.run_query(
        "MATCH (:Table)-[h:HAS_COLUMN]->(:Column) RETURN count(h) AS hasColCount"
    )
    print(f"  Total HAS_COLUMN edges: {results[0]['hasColCount']}")

    loader.close()


if __name__ == "__main__":
    main()
