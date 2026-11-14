"""
load_semantic_views.py — Load semantic view definitions into Neo4j.

Overview
--------
Standalone loader for semantic view Excel files.  Each row describes a
semantic-layer view, its SQL definition, one or more Silver/Gold source
tables, and the upstream replica table(s).

Data source
-----------
  Folder: Data/semantic_views/
  Sheet : Views
  Cols  : Semantic View, Code, Tableau Report Entity,
          IDP Replica Entity, Fully Qualified Name Silver or Gold,
          STTM Link

Lineage chain per row
---------------------
  Replica[i] -[:DERIVED_FROM]-> Silver/Gold[i] -[:DERIVED_FROM]-> Semantic View

  Both "Fully Qualified Name Silver or Gold" and "IDP Replica Entity" may
  contain multiple newline-separated values.  These are paired positionally:
    Silver/Gold[0] ← Replica[0], Silver/Gold[1] ← Replica[1], etc.
  When there is only one Silver but multiple Replicas, the single Silver
  is treated as a fan-in (derived from all listed Replicas).
  The Semantic View is always derived from ALL listed Silver/Gold tables.

Data cleaning
-------------
  - Invisible Unicode (\u200b zero-width space, BOM, etc.) is stripped.
  - "NA" values (case-insensitive) are filtered out.
  - Comma-separated values within cells are split alongside newlines.

What this script creates / enriches
------------------------------------
1. Semantic View Table nodes with:
   - qualifiedName, tableName, layer='Semantic'
   - viewDefinition  (full SQL CREATE VIEW statement)
   - tableauReportEntity  (entity name used by Tableau)
   - sttmLink  (reference to the STTM file)
2. Schema → CONTAINS → Table wiring for the semantic view.
3. DERIVED_FROM edges: Semantic View → each Silver/Gold table (fan-out).
4. Silver/Gold stub nodes (MERGE) if they don't already exist, with Schema
   wiring.
5. Replica stub nodes (MERGE) if missing, with DERIVED_FROM edge from the
   positionally paired Silver/Gold table (defensive — may already exist
   from STTM loading).

Idempotent — safe to re-run.

Usage
-----
    python src/load_semantic_views.py [file1.xlsx] [file2.xlsx] ...

    If no files are specified, all .xlsx files in Data/semantic_views/ are
    processed.
"""

import os
import sys
import glob
import openpyxl

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from excel_cells import clean_cell, split_multivalue
from neo4j_loader import Neo4jLoader


def route_direct_replica(replicas, parents_of):
    """Split replica names into a single existing Gold/Silver parent, or the replica itself.

    Zero parents, or more than one, leaves the replica edge. Trimming `_vw` is not a parent.
    """
    silver = []
    replica = []
    for rep in replicas:
        parents = list(parents_of.get(rep, ()))
        if len(parents) == 1:
            silver.append(parents[0])
        else:
            replica.append(rep)
    return silver, replica

PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VIEWS_DIR = os.path.join(PROJECT_ROOT, "Data", "semantic_views")
SHEET_NAME = "Views"

# ---------------------------------------------------------------------------
# Cypher queries
# ---------------------------------------------------------------------------

# MERGE a Semantic View Table node and wire it into its Schema
MERGE_SEMANTIC_VIEW_QUERY = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET
    t.tableName             = row.tableName,
    t.layer                 = 'Semantic',
    t.viewDefinition        = row.viewDefinition,
    t.tableauReportEntity   = row.tableauReportEntity,
    t.sttmLink              = row.sttmLink,
    t.sourceFile            = row.sourceFile
ON MATCH SET
    t.viewDefinition        = COALESCE(row.viewDefinition, t.viewDefinition),
    t.tableauReportEntity   = COALESCE(row.tableauReportEntity, t.tableauReportEntity),
    t.sttmLink              = COALESCE(row.sttmLink, t.sttmLink)
WITH t, row
MERGE (s:Schema {qualifiedName: row.schemaQN})
ON CREATE SET s.name = row.schemaQN, s.createdAt = datetime()
MERGE (s)-[:CONTAINS]->(t)
"""

# MERGE DERIVED_FROM: Semantic View → Silver/Gold table.
# Creates stub Silver/Gold nodes if they don't already exist, and wires
# them into their Schema via CONTAINS.
DERIVED_FROM_SEM_TO_SILVER_QUERY = """
UNWIND $rows AS row
MATCH (sem:Table {qualifiedName: row.semQN})
MERGE (silver:Table {qualifiedName: row.silverQN})
ON CREATE SET
    silver.tableName  = row.silverTableName,
    silver.sourceFile = row.sourceFile
MERGE (sem)-[:DERIVED_FROM]->(silver)
WITH silver, row
MERGE (s:Schema {qualifiedName: row.silverSchemaQN})
ON CREATE SET s.name = row.silverSchemaQN, s.createdAt = datetime()
MERGE (s)-[:CONTAINS]->(silver)
"""

# MERGE DERIVED_FROM: Semantic View → Replica (direct, no Silver intermediate).
# Used when the "Fully Qualified Name Silver or Gold" column is NA, meaning
# the Semantic View was constructed directly from the Replica table(s).
DERIVED_FROM_SEM_TO_REPLICA_QUERY = """
UNWIND $rows AS row
MATCH (sem:Table {qualifiedName: row.semQN})
MERGE (replica:Table {qualifiedName: row.replicaQN})
ON CREATE SET
    replica.tableName  = row.replicaTableName,
    replica.layer      = 'Replica',
    replica.sourceFile = row.sourceFile
MERGE (sem)-[:DERIVED_FROM]->(replica)
WITH replica, row
MERGE (s:Schema {qualifiedName: row.replicaSchemaQN})
ON CREATE SET s.name = row.replicaSchemaQN, s.createdAt = datetime()
MERGE (s)-[:CONTAINS]->(replica)
"""

# MERGE DERIVED_FROM: Silver/Gold → Replica.
# Creates stub Replica Table nodes if they don't already exist, and wires
# them into their Schema via CONTAINS.
DERIVED_FROM_SILVER_TO_REPLICA_QUERY = """
UNWIND $rows AS row
MATCH (silver:Table {qualifiedName: row.silverQN})
MERGE (replica:Table {qualifiedName: row.replicaQN})
ON CREATE SET
    replica.tableName  = row.replicaTableName,
    replica.layer      = 'Replica',
    replica.sourceFile = row.sourceFile
MERGE (silver)-[:DERIVED_FROM]->(replica)
WITH replica, row
MERGE (s:Schema {qualifiedName: row.replicaSchemaQN})
ON CREATE SET s.name = row.replicaSchemaQN, s.createdAt = datetime()
MERGE (s)-[:CONTAINS]->(replica)
"""


# ---------------------------------------------------------------------------
# Read & transform
# ---------------------------------------------------------------------------
def _clean(val):
    """clean_cell, plus SQL-style square brackets removed: [schema].[table] → schema.table."""
    s = clean_cell(val)
    return clean_cell(s.replace("[", "").replace("]", "")) if s else None


def read_views_sheet(excel_path, sheet_name):
    """Read the Views sheet and return cleaned records.

    Returns list of dicts with keys:
      semanticView, code, tableauReportEntity, replicaEntities (list),
      silverEntities (list), sttmLink
    """
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        wb.close()
        print(f"  WARNING: Sheet '{sheet_name}' not found in {os.path.basename(excel_path)}. Skipping.")
        return []

    ws = wb[sheet_name]
    raw_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(raw_rows) < 2:
        print(f"  WARNING: No data rows in '{sheet_name}'. Skipping.")
        return []

    records = []
    for r in raw_rows[1:]:  # skip header
        sem_view = _clean(r[0])
        code = _clean(r[1])
        tableau_entity = _clean(r[2])
        replica_entity = _clean(r[3])
        fqn_raw = _clean(r[4])
        sttm_link = _clean(r[5])

        row_replicas = split_multivalue(replica_entity)
        row_silvers = split_multivalue(fqn_raw)

        if sem_view:
            # New semantic view group — start a new record
            records.append({
                "semanticView": sem_view,
                "code": code,
                "tableauReportEntity": tableau_entity,
                "replicaEntities": row_replicas,
                "silverEntities": row_silvers,
                "sttmLink": sttm_link,
            })
        elif records and (row_replicas or row_silvers):
            # Continuation row — append Silver/Replica to the last record
            records[-1]["replicaEntities"].extend(row_replicas)
            records[-1]["silverEntities"].extend(row_silvers)

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("load_semantic_views.py — Semantic View Definitions")
    print("=" * 60)

    # -- Determine files to process --
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = sorted(glob.glob(os.path.join(VIEWS_DIR, "*.xlsx")))

    if not files:
        print("No .xlsx files found in Data/semantic_views/. Nothing to do.")
        return

    print(f"\nFiles to process: {len(files)}")
    for f in files:
        print(f"  {os.path.basename(f)}")

    # -- Read all files --
    all_records = []
    file_sources = {}  # record index → source file name
    for fpath in files:
        fname = os.path.basename(fpath)
        print(f"\nReading '{fname}'...")
        recs = read_views_sheet(fpath, SHEET_NAME)
        print(f"  {len(recs)} rows")
        for rec in recs:
            rec["sourceFile"] = fname
        all_records.extend(recs)

    if not all_records:
        print("\nNo records to load. Done.")
        return

    print(f"\nTotal records across all files: {len(all_records)}")

    # -- Connect & canonicalize --
    loader = Neo4jLoader()
    qn_lookup = loader.build_table_qn_lookup()
    parent_rows = loader.run_query(
        """
        MATCH (parent:Table)-[:DERIVED_FROM|REPLICATED_TO]->(rep:Table)
        WHERE parent.layer IN ['Gold', 'Silver'] AND rep.layer = 'Replica'
        RETURN rep.qualifiedName AS rep, collect(DISTINCT parent.qualifiedName) AS parents
        """
    )
    parents_of = {row["rep"]: row["parents"] for row in parent_rows}

    # -- Build payloads --
    print("\nBuilding graph payloads...")

    view_rows = []        # For MERGE_SEMANTIC_VIEW_QUERY
    sem_silver_rows = []  # For DERIVED_FROM_SEM_TO_SILVER_QUERY
    silver_rep_rows = []  # For DERIVED_FROM_SILVER_TO_REPLICA_QUERY
    sem_replica_rows = [] # For DERIVED_FROM_SEM_TO_REPLICA_QUERY (direct, no Silver)

    for rec in all_records:
        # Canonicalize qualifiedNames to match existing graph nodes
        sem_qn = Neo4jLoader.canonicalize_table_qn(rec["semanticView"], qn_lookup)

        # Extract schema from semantic view qualifiedName
        schema_qn = sem_qn.rsplit(".", 1)[0] if "." in sem_qn else sem_qn
        # Extract table name (everything after the last dot)
        table_name = sem_qn.rsplit(".", 1)[1] if "." in sem_qn else sem_qn

        view_rows.append({
            "qualifiedName": sem_qn,
            "tableName": table_name,
            "schemaQN": schema_qn,
            "viewDefinition": rec["code"],
            "tableauReportEntity": rec["tableauReportEntity"],
            "sttmLink": rec["sttmLink"],
            "sourceFile": rec["sourceFile"],
        })

        # Canonicalize Silver/Gold and Replica lists
        silvers = [Neo4jLoader.canonicalize_table_qn(s, qn_lookup)
                   for s in rec["silverEntities"]]
        replicas = [Neo4jLoader.canonicalize_table_qn(r, qn_lookup)
                    for r in rec["replicaEntities"]]

        # When Silver is NA but Replicas exist, use the one Gold or Silver table
        # that already derives from that Replica. Otherwise the view stays on the Replica.
        if not silvers and replicas:
            routed_silver, routed_replica = route_direct_replica(replicas, parents_of)
            for parent_qn in routed_silver:
                parent_schema = parent_qn.rsplit(".", 1)[0] if "." in parent_qn else parent_qn
                parent_table = parent_qn.rsplit(".", 1)[1] if "." in parent_qn else parent_qn
                sem_silver_rows.append({
                    "semQN": sem_qn,
                    "silverQN": parent_qn,
                    "silverTableName": parent_table,
                    "silverSchemaQN": parent_schema,
                    "sourceFile": rec["sourceFile"],
                })
            for rep_qn in routed_replica:
                rep_schema = rep_qn.rsplit(".", 1)[0] if "." in rep_qn else rep_qn
                rep_table = rep_qn.rsplit(".", 1)[1] if "." in rep_qn else rep_qn
                sem_replica_rows.append({
                    "semQN": sem_qn,
                    "replicaQN": rep_qn,
                    "replicaTableName": rep_table,
                    "replicaSchemaQN": rep_schema,
                    "sourceFile": rec["sourceFile"],
                })
            # Skip Silver→Replica pairing since there are no Silvers
            continue

        # Semantic View → each Silver/Gold table (fan-out)
        for silver_qn in silvers:
            silver_schema = silver_qn.rsplit(".", 1)[0] if "." in silver_qn else silver_qn
            silver_table = silver_qn.rsplit(".", 1)[1] if "." in silver_qn else silver_qn
            sem_silver_rows.append({
                "semQN": sem_qn,
                "silverQN": silver_qn,
                "silverTableName": silver_table,
                "silverSchemaQN": silver_schema,
                "sourceFile": rec["sourceFile"],
            })

        # Positional 1:1 pairing: Silver[i] → Replica[i]
        # If counts differ, pair up to min length and log a warning.
        if len(silvers) == len(replicas):
            for silver_qn, rep_qn in zip(silvers, replicas):
                rep_schema = rep_qn.rsplit(".", 1)[0] if "." in rep_qn else rep_qn
                rep_table = rep_qn.rsplit(".", 1)[1] if "." in rep_qn else rep_qn
                silver_rep_rows.append({
                    "silverQN": silver_qn,
                    "replicaQN": rep_qn,
                    "replicaTableName": rep_table,
                    "replicaSchemaQN": rep_schema,
                    "sourceFile": rec["sourceFile"],
                })
        elif len(silvers) == 1 and len(replicas) > 1:
            # Single Silver table derived from multiple Replicas (fan-in)
            silver_qn = silvers[0]
            for rep_qn in replicas:
                rep_schema = rep_qn.rsplit(".", 1)[0] if "." in rep_qn else rep_qn
                rep_table = rep_qn.rsplit(".", 1)[1] if "." in rep_qn else rep_qn
                silver_rep_rows.append({
                    "silverQN": silver_qn,
                    "replicaQN": rep_qn,
                    "replicaTableName": rep_table,
                    "replicaSchemaQN": rep_schema,
                    "sourceFile": rec["sourceFile"],
                })
        else:
            # Mismatch — pair up to min length and warn
            if replicas:
                print(f"  WARNING: Silver count ({len(silvers)}) != Replica count "
                      f"({len(replicas)}) for {sem_qn}. Pairing up to min length.")
                for silver_qn, rep_qn in zip(silvers, replicas):
                    rep_schema = rep_qn.rsplit(".", 1)[0] if "." in rep_qn else rep_qn
                    rep_table = rep_qn.rsplit(".", 1)[1] if "." in rep_qn else rep_qn
                    silver_rep_rows.append({
                        "silverQN": silver_qn,
                        "replicaQN": rep_qn,
                        "replicaTableName": rep_table,
                        "replicaSchemaQN": rep_schema,
                        "sourceFile": rec["sourceFile"],
                    })

    print(f"  Semantic View nodes to MERGE: {len(view_rows)}")
    print(f"  Semantic→Silver DERIVED_FROM edges: {len(sem_silver_rows)}")
    print(f"  Semantic→Replica DERIVED_FROM edges (direct, no Silver): {len(sem_replica_rows)}")
    print(f"  Silver→Replica DERIVED_FROM edges (defensive): {len(silver_rep_rows)}")

    # -- Load into Neo4j --
    print("\nLoading into Neo4j...")

    loader.write_batches(MERGE_SEMANTIC_VIEW_QUERY, view_rows)
    print(f"  Merged {len(view_rows)} Semantic View node(s)")

    loader.write_batches(DERIVED_FROM_SEM_TO_SILVER_QUERY, sem_silver_rows)
    print(f"  Merged {len(sem_silver_rows)} Semantic→Silver DERIVED_FROM edge(s)")

    # Only rows whose Silver cell is NA link Semantic straight to Replica.
    if sem_replica_rows:
        loader.write_batches(DERIVED_FROM_SEM_TO_REPLICA_QUERY, sem_replica_rows)
        print(f"  Merged {len(sem_replica_rows)} Semantic→Replica DERIVED_FROM edge(s) (direct)")

    if silver_rep_rows:
        loader.write_batches(DERIVED_FROM_SILVER_TO_REPLICA_QUERY, silver_rep_rows)
        print(f"  Merged {len(silver_rep_rows)} Silver→Replica DERIVED_FROM edge(s) (defensive)")

    # -- Verify --
    print("\nVerification...")

    # Show what was loaded
    for rec in all_records:
        sem_qn = Neo4jLoader.canonicalize_table_qn(rec["semanticView"], qn_lookup)
        r = loader.run_query("""
            MATCH (sem:Table {qualifiedName: $qn})
            OPTIONAL MATCH (sem)-[:DERIVED_FROM]->(silver:Table)
            OPTIONAL MATCH (silver)-[:DERIVED_FROM]->(rep:Table)
            RETURN sem.qualifiedName AS semView,
                   sem.layer AS layer,
                   sem.viewDefinition IS NOT NULL AS hasCode,
                   sem.tableauReportEntity AS tableauEntity,
                   silver.qualifiedName AS silverTable,
                   rep.qualifiedName AS replicaTable
        """, qn=sem_qn)
        for x in r:
            print(f"\n  {x['semView']} ({x['layer']})")
            print(f"    hasCode: {x['hasCode']}, tableauEntity: {x['tableauEntity']}")
            print(f"    → {x['silverTable']} → {x['replicaTable']}")

    # Graph totals
    print("\n  Graph totals:")
    for label in ['Table', 'Server', 'DataSystem', 'MasterDataDomain']:
        c = loader.run_query(f"MATCH (n:{label}) RETURN count(n) AS cnt")
        print(f"    {label}: {c[0]['cnt']}")
    r = loader.run_query("MATCH ()-[r:DERIVED_FROM]->() RETURN count(r) AS cnt")
    print(f"    DERIVED_FROM edges: {r[0]['cnt']}")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
