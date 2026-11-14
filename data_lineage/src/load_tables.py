"""
Load Table nodes into Neo4j — Phase 2 of Medallion Architecture implementation.

Creates:
  1. Table nodes with multi-labels for dimensional role (:Table:Fact, :Table:Dimension, :Table:View)
  2. Relationships: (Schema)-[:CONTAINS]->(Table)

The dimensional role is applied as a Neo4j label (not just a property) to enable
efficient pattern matching like MATCH (t:Table:Fact WHERE t.layer = 'Gold').

Prerequisites:
  - Run extract_mapping_metadata.py first to produce Data/tables.csv
  - Run load_schemas.py first (Schema nodes must exist)
  - pip install neo4j pandas python-dotenv

Usage:
    python src/load_tables.py
"""

import os
import pandas as pd
from medallion import is_legacy, schema_layer
from neo4j_loader import Neo4jLoader

# ── Path resolution ────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TABLES_CSV = os.path.join(PROJECT_ROOT, "Data", "tables.csv")

# ── Step 0: Fix constraint — drop name uniqueness, add qualifiedName ──────────
# The original data model template created Table_name_key on Table.name, but
# tables can share names across schemas (e.g., MPR_Product_Class_Group_Xref in
# both mdm_core and udm_core). We need uniqueness on qualifiedName instead.
DROP_NAME_CONSTRAINT = "DROP CONSTRAINT Table_name_key IF EXISTS"
CREATE_QN_CONSTRAINT = (
    "CREATE CONSTRAINT Table_qualifiedName_key IF NOT EXISTS "
    "FOR (t:Table) REQUIRE t.qualifiedName IS UNIQUE"
)

# ── Cypher: Create Table nodes and wire to Schema ──────────────────────────
# MERGE on :Table alone, then add the dimensional-role label, so a Table that
# already exists without that label is matched instead of colliding with it.
TABLE_QUERY = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET t.name = row.name,
  t.layer = row.layer,
  t.createdAt = datetime()
ON MATCH SET t.updatedAt = datetime()
FOREACH (_ IN CASE WHEN row.role = 'Fact' THEN [1] ELSE [] END | SET t:Fact)
FOREACH (_ IN CASE WHEN row.role = 'Dimension' THEN [1] ELSE [] END | SET t:Dimension)
FOREACH (_ IN CASE WHEN row.role = 'View' THEN [1] ELSE [] END | SET t:View)
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET t:Legacy)
WITH t, row
MATCH (s:Schema {qualifiedName: row.schema})
MERGE (s)-[:CONTAINS]->(t)
"""

# ── Verification queries ───────────────────────────────────────────────────
VERIFY_TABLES_BY_LAYER = """
MATCH (t:Table)
RETURN t.layer AS layer, count(t) AS tableCount
ORDER BY tableCount DESC
"""

VERIFY_TABLES_BY_ROLE = """
MATCH (t:Table)
RETURN
  CASE
    WHEN t:Fact THEN 'Fact'
    WHEN t:Dimension THEN 'Dimension'
    WHEN t:View THEN 'View'
    ELSE 'Table'
  END AS role,
  count(t) AS tableCount
ORDER BY tableCount DESC
"""

VERIFY_CONTAINS = """
MATCH (s:Schema)-[:CONTAINS]->(t:Table)
RETURN s.qualifiedName AS schema, count(t) AS tableCount
ORDER BY tableCount DESC
"""

VERIFY_ORPHAN_TABLES = """
MATCH (t:Table)
WHERE NOT ()<-[:CONTAINS]-(t) AND NOT ()-[:CONTAINS]->(t)
RETURN t.qualifiedName AS orphanTable
ORDER BY t.qualifiedName
"""


def transform_row(row):
    """Transform a tables.csv row into a dict for the Cypher query."""
    qualified_name = str(row["qualifiedName"]).strip()
    schema = str(row["schema"]).strip()
    layer = schema_layer(schema) or "Unknown"
    return {
        "qualifiedName": qualified_name,
        "name": str(row["name"]).strip(),
        "schema": schema,
        "layer": layer,
        "legacy": is_legacy(qualified_name, layer),
        "role": row["dimensionalRole"],
    }


def main():
    loader = Neo4jLoader()

    try:
        # ── Step 0: Fix Table constraint ────────────────────────────────────
        print("Step 0: Updating Table constraints...")
        print("  Dropping Table_name_key (uniqueness on name)...")
        loader.run_write(DROP_NAME_CONSTRAINT)
        print("  Creating Table_qualifiedName_key (uniqueness on qualifiedName)...")
        loader.run_write(CREATE_QN_CONSTRAINT)
        print("  Done.")

        df = pd.read_csv(TABLES_CSV)
        print(f"Total tables in CSV: {len(df)}")
        print(f"  By role: {df['dimensionalRole'].value_counts().to_dict()}")

        records = [transform_row(row) for _, row in df.iterrows()]
        qn_lookup = loader.build_table_qn_lookup()
        Neo4jLoader.canonicalize_table_fields(records, qn_lookup, "qualifiedName")
        for rec in records:
            rec["legacy"] = is_legacy(rec["qualifiedName"], rec["layer"])
        loader.write_batches(TABLE_QUERY, records)
        print(f"  Loaded {len(records)} Table nodes.")

        # ── Verification ───────────────────────────────────────────────────
        print("\n=== Verification ===")

        print("\nTables by layer:")
        loader.verify(VERIFY_TABLES_BY_LAYER)

        print("\nTables by dimensional role:")
        loader.verify(VERIFY_TABLES_BY_ROLE)

        print("\nTables per schema (CONTAINS):")
        loader.verify(VERIFY_CONTAINS)

        print("\nOrphan tables (no CONTAINS relationship):")
        orphans = loader.verify(VERIFY_ORPHAN_TABLES)
        if not orphans:
            print("  None — all tables are linked to a schema!")

    finally:
        loader.close()


if __name__ == "__main__":
    main()
