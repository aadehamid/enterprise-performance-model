"""
load_role_assignments.py - Load Person nodes, RoleAssignment nodes, and wire
them to Semantic Views (APPLIES_TO) from the IDP Index spreadsheet.

Source: Data/new data system files to process/CAT_Reports_IDP Index_RV0126.xlsx
Sheet:  IDP Index

Graph pattern created per row:
  (:Person)-[:HAS_ROLE]->(:RoleAssignment)-[:APPLIES_TO]->(:Table {layer:'Semantic'})

Each row may produce up to 2 RoleAssignment nodes:
  - type = "Data Analyst"
  - type = "Data Analyst Backup"

Also creates:
  - New CapabilityDataDomain "Market Sensing" (for Market Sensing Phase 1/2 rows)
  - Stub Table nodes for any IDP Tables or Semantic Views missing from the graph

Usage:
    python src/load_role_assignments.py           # dry-run
    python src/load_role_assignments.py --load    # write to Neo4j
"""
import argparse
import os
import re
import sys

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from excel_cells import clean_cell
from medallion import is_legacy, schema_layer, schema_of
from neo4j_loader import Neo4jLoader

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXCEL_PATH = os.path.join(
    PROJECT_ROOT, "Data", "new data system files to process",
    "CAT_Reports_IDP Index_RV0126.xlsx",
)
SHEET_NAME = "IDP Index"

# ---------------------------------------------------------------------------
# CDD name corrections: file value → graph name
# ---------------------------------------------------------------------------
CDD_CORRECTIONS = {
    "Logistic Execution": "Logistics Execution",
}

# ---------------------------------------------------------------------------
# Parse CDD name: extract part after " - ", collapse Market Sensing
# ---------------------------------------------------------------------------
def parse_cdd_name(raw):
    """Extract the CapabilityDataDomain name from the file value."""
    if raw is None:
        return None
    if "Market Sensing" in raw:
        return "Market Sensing"
    parts = raw.split(" - ", 1)
    name = parts[1].strip() if len(parts) > 1 else raw.strip()
    return CDD_CORRECTIONS.get(name, name)


# ---------------------------------------------------------------------------
# Parse IDP Table: handle "multiple(...)" pattern
# ---------------------------------------------------------------------------
def parse_idp_tables(raw):
    """Return a list of qualifiedName strings from the IDP Table cell."""
    if raw is None:
        return []
    match = re.search(r"\((.+)\)", raw)
    if match:
        return [clean_cell(t) for t in match.group(1).split(",") if clean_cell(t)]
    cleaned = clean_cell(raw)
    return [cleaned] if cleaned else []


# ---------------------------------------------------------------------------
# Cypher Queries
# ---------------------------------------------------------------------------

# 1. Create new CapabilityDataDomain node
MERGE_CDD_QUERY = """
UNWIND $rows AS row
MERGE (c:CapabilityDataDomain {name: row.name})
ON CREATE SET c.description = row.description, c.createdAt = datetime()
"""

# 2. Create Person nodes
MERGE_PERSON_QUERY = """
UNWIND $rows AS row
MERGE (p:Person {name: row.name})
ON CREATE SET p.createdAt = datetime()
"""

# 3. Create stub Table nodes for missing IDP tables / Semantic views
MERGE_STUB_TABLE_QUERY = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET
    t.name      = row.tableName,
    t.layer     = row.layer,
    t.createdAt = datetime(),
    t.sourceFile = 'CAT_Reports_IDP Index_RV0126.xlsx'
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET t:Legacy)
WITH t, row
WHERE row.schemaQN IS NOT NULL
MERGE (s:Schema {qualifiedName: row.schemaQN})
ON CREATE SET s.name = row.schemaName, s.createdAt = datetime()
MERGE (s)-[:CONTAINS]->(t)
"""

# 4. Create RoleAssignment + relationships
MERGE_ROLE_ASSIGNMENT_QUERY = """
UNWIND $rows AS row
MATCH (p:Person {name: row.personName})
MATCH (t:Table {qualifiedName: row.viewQN})
MERGE (ra:RoleAssignment {type: row.roleType, scope: row.viewQN})
ON CREATE SET
    ra.status    = 'Active',
    ra.createdAt = datetime()
MERGE (p)-[:HAS_ROLE]->(ra)
MERGE (ra)-[:APPLIES_TO]->(t)
"""

# 5. Update constraint
DROP_OLD_CONSTRAINT = "DROP CONSTRAINT RoleAssignment_key IF EXISTS"
CREATE_NEW_CONSTRAINT = (
    "CREATE CONSTRAINT RoleAssignment_key IF NOT EXISTS "
    "FOR (n:RoleAssignment) REQUIRE (n.type, n.scope) IS UNIQUE"
)


def main():
    parser = argparse.ArgumentParser(description="Load role assignments from IDP Index")
    parser.add_argument("--load", action="store_true", help="Write to Neo4j (default: dry-run)")
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # 1. Read and parse Excel
    # -----------------------------------------------------------------------
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

    # Identify columns
    cdd_col = [c for c in df.columns if "capability" in str(c).lower()][0]
    idp_col = [c for c in df.columns if "idp table" in str(c).lower()][0]
    sem_col = [c for c in df.columns if "semantic" in str(c).lower()][0]
    da_col  = [c for c in df.columns if "data analyst" in str(c).lower()
               and "backup" not in str(c).lower()][0]
    dab_col = [c for c in df.columns if "backup" in str(c).lower()][0]

    print(f"Loaded {len(df)} rows from '{SHEET_NAME}'")
    print(f"  Columns: CDD={cdd_col}, IDP={idp_col}, Sem={sem_col}, DA={da_col}, Backup={dab_col}")

    # Clean and parse
    df["parsed_cdd"]    = df[cdd_col].apply(clean_cell).apply(parse_cdd_name)
    df["parsed_tables"] = df[idp_col].apply(lambda x: parse_idp_tables(clean_cell(x)))
    df["parsed_view"]   = df[sem_col].apply(clean_cell)
    df["parsed_da"]     = df[da_col].apply(clean_cell)
    df["parsed_dab"]    = df[dab_col].apply(clean_cell)

    # -----------------------------------------------------------------------
    # 2. Connect and build lookup of existing Table qualifiedNames
    # -----------------------------------------------------------------------
    loader = Neo4jLoader()
    qn_lookup = loader.build_table_qn_lookup()
    existing_tables = set(qn_lookup.values())
    existing_cdds = {r["name"] for r in loader.run_query(
        "MATCH (c:CapabilityDataDomain) RETURN c.name AS name"
    )}

    # -----------------------------------------------------------------------
    # 3. Determine new CDD nodes needed
    # -----------------------------------------------------------------------
    file_cdds = set(df["parsed_cdd"].dropna().unique())
    new_cdds = file_cdds - existing_cdds
    cdd_rows = [{"name": n, "description": None} for n in sorted(new_cdds)]
    print(f"\nNew CapabilityDataDomain nodes to create: {len(cdd_rows)}")
    for r in cdd_rows:
        print(f"  {r['name']}")

    # -----------------------------------------------------------------------
    # 4. Collect unique Person names
    # -----------------------------------------------------------------------
    all_persons = set()
    all_persons.update(df["parsed_da"].dropna().unique())
    all_persons.update(df["parsed_dab"].dropna().unique())
    person_rows = [{"name": n} for n in sorted(all_persons)]
    print(f"\nPerson nodes to create: {len(person_rows)}")
    for r in person_rows:
        print(f"  {r['name']}")

    # -----------------------------------------------------------------------
    # 5. Identify missing Table/View stubs needed
    # -----------------------------------------------------------------------
    # Collect all IDP table QNs and Semantic view QNs referenced
    all_idp_qns = set()
    for tlist in df["parsed_tables"]:
        all_idp_qns.update(
            Neo4jLoader.canonicalize_table_qn(q, qn_lookup) for q in tlist
        )
    all_view_qns = {
        Neo4jLoader.canonicalize_table_qn(q, qn_lookup)
        for q in df["parsed_view"].dropna()
    }

    missing_idp   = sorted(all_idp_qns - existing_tables)
    missing_views = sorted(all_view_qns - existing_tables)

    stub_rows = []
    for qns, default_layer in ((missing_idp, "Silver"), (missing_views, "Semantic")):
        for qn in qns:
            schema = schema_of(qn) if "." in qn else None
            layer = schema_layer(schema) or default_layer
            stub_rows.append({
                "qualifiedName": qn,
                "tableName": qn.split(".")[-1],
                "layer": layer,
                "legacy": is_legacy(qn, layer),
                "schemaQN": schema,
                "schemaName": schema,
            })

    print(f"\nStub Table nodes to create: {len(stub_rows)}")
    print(f"  Missing IDP tables:    {len(missing_idp)}")
    print(f"  Missing Semantic views: {len(missing_views)}")
    for s in stub_rows[:10]:
        print(f"    {s['qualifiedName']} (layer={s['layer']})")
    if len(stub_rows) > 10:
        print(f"    ... and {len(stub_rows) - 10} more")

    # -----------------------------------------------------------------------
    # 6. Build RoleAssignment rows (one per person × view)
    # -----------------------------------------------------------------------
    role_rows = []
    skipped_no_view = 0
    for _, row in df.iterrows():
        view_qn = Neo4jLoader.canonicalize_table_qn(row["parsed_view"], qn_lookup)
        if not view_qn:
            skipped_no_view += 1
            continue

        # Data Analyst assignment
        if row["parsed_da"]:
            role_rows.append({
                "personName": row["parsed_da"],
                "roleType": "Data Analyst",
                "viewQN": view_qn,
            })

        # Data Analyst Backup assignment
        if row["parsed_dab"]:
            role_rows.append({
                "personName": row["parsed_dab"],
                "roleType": "Data Analyst Backup",
                "viewQN": view_qn,
            })

    print(f"\nRoleAssignment nodes to create: {len(role_rows)}")
    print(f"  Data Analyst:        {sum(1 for r in role_rows if r['roleType'] == 'Data Analyst')}")
    print(f"  Data Analyst Backup: {sum(1 for r in role_rows if r['roleType'] == 'Data Analyst Backup')}")
    print(f"  Skipped (no view):   {skipped_no_view}")

    # -----------------------------------------------------------------------
    # DRY-RUN summary
    # -----------------------------------------------------------------------
    if not args.load:
        print("\n=== DRY-RUN COMPLETE ===")
        print("Use --load to write to Neo4j.")
        loader.close()
        return

    # -----------------------------------------------------------------------
    # 7. WRITE to Neo4j
    # -----------------------------------------------------------------------
    print("\n=== WRITING TO NEO4J ===")

    # 7a. Update constraint
    print("\nUpdating RoleAssignment constraint...")
    loader.run_write(DROP_OLD_CONSTRAINT)
    loader.run_write(CREATE_NEW_CONSTRAINT)
    print("  Constraint updated: (type, scope) IS UNIQUE")

    # 7b. Create CDD nodes
    if cdd_rows:
        loader.write_batches(MERGE_CDD_QUERY, cdd_rows)
        print(f"\nMerged {len(cdd_rows)} CapabilityDataDomain node(s)")

    # 7c. Create Person nodes
    loader.write_batches(MERGE_PERSON_QUERY, person_rows)
    print(f"Merged {len(person_rows)} Person node(s)")

    # 7d. Create stub Table nodes (batch by 500)
    if stub_rows:
        loader.write_batches(MERGE_STUB_TABLE_QUERY, stub_rows)
        print(f"Merged {len(stub_rows)} stub Table node(s)")

    # 7e. Create RoleAssignment nodes + edges (batch by 500)
    loader.write_batches(MERGE_ROLE_ASSIGNMENT_QUERY, role_rows)
    print(f"Merged {len(role_rows)} RoleAssignment node(s) with HAS_ROLE + APPLIES_TO edges")

    # -----------------------------------------------------------------------
    # 8. VERIFICATION
    # -----------------------------------------------------------------------
    print("\n=== VERIFICATION ===")

    # Person count
    person_count = loader.run_query("MATCH (p:Person) RETURN count(p) AS cnt")[0]["cnt"]
    print(f"\nPerson nodes: {person_count}")

    # RoleAssignment count
    ra_count = loader.run_query("MATCH (ra:RoleAssignment) RETURN count(ra) AS cnt")[0]["cnt"]
    print(f"RoleAssignment nodes: {ra_count}")

    # CDD count
    cdd_count = loader.run_query("MATCH (c:CapabilityDataDomain) RETURN count(c) AS cnt")[0]["cnt"]
    print(f"CapabilityDataDomain nodes: {cdd_count}")

    # Sample: analysts per CDD (via view lineage)
    print("\nAnalysts per CapabilityDataDomain (top 5):")
    sample = loader.run_query("""
        MATCH (p:Person)-[:HAS_ROLE]->(ra:RoleAssignment)-[:APPLIES_TO]->(t:Table)
        WHERE ra.type = 'Data Analyst'
        RETURN p.name AS analyst, ra.type AS role, count(t) AS viewCount
        ORDER BY viewCount DESC
        LIMIT 10
    """)
    for r in sample:
        print(f"  {r['analyst']:30s} {r['role']:25s} ({r['viewCount']} views)")

    # Orphan check: RoleAssignments without HAS_ROLE or APPLIES_TO
    orphan_check = loader.run_query("""
        MATCH (ra:RoleAssignment)
        WHERE NOT (ra)<-[:HAS_ROLE]-() OR NOT (ra)-[:APPLIES_TO]->()
        RETURN count(ra) AS orphans
    """)[0]["orphans"]
    print(f"\nOrphan RoleAssignments (missing HAS_ROLE or APPLIES_TO): {orphan_check}")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
