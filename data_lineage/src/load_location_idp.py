"""
load_location_idp.py — Load Location IDP master data into Neo4j.

Overview
--------
Standalone loader for the Location Tables In IDP spreadsheet.  Every row
represents an IDP table that belongs to the **Location** MasterDataDomain.

Data source
-----------
  File : Data/new data system files to process/Location_Tables_In_IDP.xlsx
  Sheet: Location Tables
  Cols : IDP Schema, IDP Table Name, Operational Source DataSystem, Comments

What this script does
---------------------
1. Read the Excel sheet.
2. For each row, build qualifiedName = {schema}.{table}.
3. MERGE the Table node (Silver layer IDP stub) with a comment property.
4. MERGE (MasterDataDomain {name:'Location'})-[:REALIZED_IN]->(Table).
5. If Operational Source DataSystem is non-null, store it as sourceDataSystem
   on the Table node for reference (DERIVED_FROM lineage from STTMs is already
   in the graph).
6. Verify results.

Idempotent — safe to re-run.

Usage
-----
    python src/load_location_idp.py
"""

import os
import sys
import openpyxl

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from medallion import cypher_schema_layer, is_legacy, schema_layer
from neo4j_loader import Neo4jLoader

PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

EXCEL_PATH = os.path.join(
    PROJECT_ROOT, "Data", "new data system files to process",
    "Location_Tables_In_IDP.xlsx",
)
SHEET_NAME = "Location Tables"
SOURCE_FILE = "Location_Tables_In_IDP.xlsx"
DOMAIN_NAME = "Location"

# ---------------------------------------------------------------------------
# DataSystem name mapping — align file values to existing graph node names
# ---------------------------------------------------------------------------
DS_NAME_MAP = {
    "Refining OLAP": "Refining_OLAP",
}

# ---------------------------------------------------------------------------
# Cypher queries
# ---------------------------------------------------------------------------

# MERGE IDP Table stub — sets comment and sourceDataSystem properties
MERGE_TABLE_QUERY = f"""
UNWIND $rows AS row
MERGE (t:Table {{qualifiedName: row.qualifiedName}})
ON CREATE SET
    t.tableName      = row.tableName,
    t.layer          = row.layer,
    t.sourceFile     = row.sourceFile,
    t.comment        = row.comment,
    t.sourceDataSystem = row.sourceDataSystem
ON MATCH SET
    t.comment          = COALESCE(row.comment, t.comment),
    t.sourceDataSystem = COALESCE(row.sourceDataSystem, t.sourceDataSystem)
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET t:Legacy)
WITH t, row
// Wire table into its Schema → Table containment
MERGE (s:Schema {{qualifiedName: row.schemaQN}})
ON CREATE SET s.name = row.schemaQN, s.createdAt = datetime(),
              s.layer = {cypher_schema_layer("row.schemaQN", "Silver")}
MERGE (s)-[:CONTAINS]->(t)
"""

# MERGE REALIZED_IN edge from Location domain to each table
REALIZED_IN_QUERY = """
UNWIND $rows AS row
MATCH (mdd:MasterDataDomain {name: row.domainName})
MATCH (t:Table {qualifiedName: row.tableQN})
MERGE (mdd)-[:REALIZED_IN]->(t)
"""


# ---------------------------------------------------------------------------
# Read & transform
# ---------------------------------------------------------------------------
def read_location_tables(excel_path, sheet_name):
    """Read the Location Tables sheet and return cleaned records.

    Returns list of dicts with keys:
      schema, tableName, qualifiedName, layer, sourceDataSystem, comment
    """
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    raw_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    records = []
    for r in raw_rows[1:]:  # skip header
        schema = str(r[0]).strip() if r[0] else None
        table_name = str(r[1]).strip() if r[1] else None
        source_ds = str(r[2]).strip() if r[2] else None
        comment = str(r[3]).strip() if r[3] else None

        if not schema or not table_name:
            continue

        # Map DataSystem name to canonical graph name
        if source_ds and source_ds in DS_NAME_MAP:
            source_ds = DS_NAME_MAP[source_ds]

        qn = f"{schema}.{table_name}"
        layer = schema_layer(schema) or "Silver"

        records.append({
            "schema": schema,
            "tableName": table_name,
            "qualifiedName": qn,
            "layer": layer,
            "legacy": is_legacy(qn, layer),
            "sourceDataSystem": source_ds,
            "comment": comment,
        })

    print(f"  Read {len(records)} rows from '{sheet_name}'")
    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("load_location_idp.py — Location IDP Master Data")
    print("=" * 60)

    # -- Step 1: Read --
    print("\nStep 1: Reading Excel...")
    records = read_location_tables(EXCEL_PATH, SHEET_NAME)

    # -- Step 2: Build payloads --
    print("\nStep 2: Building graph payloads...")

    # Table canonicalization — reuse existing qualifiedNames in graph
    loader = Neo4jLoader()
    qn_lookup = loader.build_table_qn_lookup()

    table_rows = []
    realized_rows = []

    for rec in records:
        # Canonicalize qualifiedName to match existing node if present
        canon_qn = Neo4jLoader.canonicalize_table_qn(rec["qualifiedName"], qn_lookup)

        table_rows.append({
            "qualifiedName": canon_qn,
            "tableName": rec["tableName"],
            "layer": rec["layer"],
            "legacy": rec["legacy"],
            "schemaQN": rec["schema"],
            "sourceFile": SOURCE_FILE,
            "comment": rec["comment"],
            "sourceDataSystem": rec["sourceDataSystem"],
        })

        realized_rows.append({
            "domainName": DOMAIN_NAME,
            "tableQN": canon_qn,
        })

    print(f"  Tables to MERGE: {len(table_rows)}")
    print(f"  REALIZED_IN edges to MERGE: {len(realized_rows)}")

    # -- Step 3: Load --
    print("\nStep 3: Loading into Neo4j...")

    # Ensure Location domain exists
    loader.run_write(
        f"MERGE (mdd:MasterDataDomain {{name: '{DOMAIN_NAME}'}}) "
        f"ON CREATE SET mdd.sourceFile = '{SOURCE_FILE}', mdd.createdAt = datetime()"
    )

    # MERGE tables
    loader.write_batches(MERGE_TABLE_QUERY, table_rows)
    print(f"  Merged {len(table_rows)} Table nodes")

    # MERGE REALIZED_IN
    loader.write_batches(REALIZED_IN_QUERY, realized_rows)
    print(f"  Merged {len(realized_rows)} REALIZED_IN edges")

    # -- Step 4: Verify --
    print("\nStep 4: Verification...")

    # Count Location REALIZED_IN
    r = loader.run_query("""
        MATCH (mdd:MasterDataDomain {name: 'Location'})-[:REALIZED_IN]->(t:Table)
        RETURN count(t) AS cnt
    """)
    print(f"  Location REALIZED_IN edges: {r[0]['cnt']}")

    # Show tables with comments
    r = loader.run_query("""
        MATCH (mdd:MasterDataDomain {name: 'Location'})-[:REALIZED_IN]->(t:Table)
        WHERE t.sourceFile = $sf
        RETURN t.qualifiedName AS qn, t.layer AS layer,
               t.comment AS comment, t.sourceDataSystem AS srcDS
        ORDER BY qn
    """, sf=SOURCE_FILE)
    print(f"\n  Tables loaded from this file ({len(r)}):")
    for x in r:
        src = f" [from {x['srcDS']}]" if x['srcDS'] else ""
        cmt = f" — {x['comment']}" if x['comment'] else ""
        print(f"    {x['qn']} ({x['layer']}){src}{cmt}")

    # Total graph counts
    print("\n  Graph totals:")
    for label in ['Table', 'Server', 'DataSystem', 'MasterDataDomain']:
        c = loader.run_query(f"MATCH (n:{label}) RETURN count(n) AS cnt")
        print(f"    {label}: {c[0]['cnt']}")

    r = loader.run_query("MATCH ()-[r:REALIZED_IN]->() RETURN count(r) AS cnt")
    print(f"    REALIZED_IN edges: {r[0]['cnt']}")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
