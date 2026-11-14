"""
load_retail_payments_views.py - One-off loader for Retail Payments Semantic Views.

Sheet: "SQLs and Links"
Columns: "Semantic View Name", "Semantic View Logic"
Source tables parsed from SQL (FROM/JOIN clauses).

Usage:
    python src/load_retail_payments_views.py           # dry-run
    python src/load_retail_payments_views.py --load     # load into Neo4j
"""
import os, re, sys, openpyxl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from neo4j_loader import Neo4jLoader

PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXCEL_PATH = os.path.join(PROJECT_ROOT, "Data", "semantic_views",
                          "Retail Payments Semantic Views.xlsx")
SHEET_NAME = "SQLs and Links"
SOURCE_FILE = "Retail Payments Semantic Views.xlsx"

MERGE_VIEW_Q = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET t.tableName=row.tableName, t.layer='Semantic',
  t.viewDefinition=row.viewDefinition, t.sourceFile=row.sourceFile
ON MATCH SET t.viewDefinition=COALESCE(row.viewDefinition, t.viewDefinition)
WITH t, row
MERGE (s:Schema {qualifiedName: row.schemaQN})
ON CREATE SET s.name=row.schemaQN, s.createdAt=datetime()
MERGE (s)-[:CONTAINS]->(t)
"""

DERIVED_FROM_Q = """
UNWIND $rows AS row
MATCH (sem:Table {qualifiedName: row.semQN})
MERGE (src:Table {qualifiedName: row.srcQN})
ON CREATE SET src.tableName=row.srcTableName, src.sourceFile=row.sourceFile
MERGE (sem)-[:DERIVED_FROM]->(src)
WITH src, row
MERGE (s:Schema {qualifiedName: row.srcSchemaQN})
ON CREATE SET s.name=row.srcSchemaQN, s.createdAt=datetime()
MERGE (s)-[:CONTAINS]->(src)
"""

def extract_tables_from_sql(sql):
    if not sql:
        return []
    s = re.sub(r'\s+', ' ', sql)
    matches = re.findall(r'(?:FROM|JOIN)\s+\(?\s*(\w+\.\w+)', s, re.IGNORECASE)
    seen, result = set(), []
    for m in matches:
        if m.lower() not in seen:
            seen.add(m.lower())
            result.append(m)
    return result

def read_file():
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    ws = wb[SHEET_NAME]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    records = []
    for r in rows[1:]:
        name = str(r[0]).strip() if r[0] else None
        logic = str(r[1]).strip() if r[1] else None
        if not name or not logic:
            continue
        sources = extract_tables_from_sql(logic)
        records.append({"viewName": name, "logic": logic, "sources": sources})
    return records

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", action="store_true")
    args = parser.parse_args()

    records = read_file()
    print(f"Parsed {len(records)} views from {SOURCE_FILE}\n")

    view_rows, df_rows = [], []
    qn_lookup = {}

    if args.load:
        loader = Neo4jLoader()
        qn_lookup = loader.build_table_qn_lookup()

    for rec in records:
        vn = rec["viewName"]
        vn = Neo4jLoader.canonicalize_table_qn(vn, qn_lookup) if qn_lookup else vn
        schema = vn.rsplit(".", 1)[0] if "." in vn else vn
        tbl = vn.rsplit(".", 1)[1] if "." in vn else vn

        view_rows.append({
            "qualifiedName": vn, "tableName": tbl, "schemaQN": schema,
            "viewDefinition": rec["logic"], "sourceFile": SOURCE_FILE,
        })

        for src in rec["sources"]:
            src = Neo4jLoader.canonicalize_table_qn(src, qn_lookup) if qn_lookup else src
            src_schema = src.rsplit(".", 1)[0] if "." in src else src
            src_tbl = src.rsplit(".", 1)[1] if "." in src else src
            df_rows.append({
                "semQN": vn, "srcQN": src, "srcTableName": src_tbl,
                "srcSchemaQN": src_schema, "sourceFile": SOURCE_FILE,
            })

        print(f"  {vn}")
        print(f"    sources: {rec['sources']}")

    print(f"\n  View nodes: {len(view_rows)}")
    print(f"  DERIVED_FROM edges: {len(df_rows)}")

    if not args.load:
        print("\nDry-run complete. Use --load to write to Neo4j.")
        return

    loader.write_batches(MERGE_VIEW_Q, view_rows)
    print(f"\n  Merged {len(view_rows)} Semantic View node(s)")
    loader.write_batches(DERIVED_FROM_Q, df_rows)
    print(f"  Merged {len(df_rows)} DERIVED_FROM edge(s)")

    # Verify
    for rec in records:
        vn = rec["viewName"]
        vn = Neo4jLoader.canonicalize_table_qn(vn, qn_lookup) if qn_lookup else vn
        r = loader.run_query("""
            MATCH (sem:Table {qualifiedName: $qn})-[:DERIVED_FROM]->(src:Table)
            RETURN sem.qualifiedName AS view, collect(src.qualifiedName) AS sources
        """, qn=vn)
        if r:
            print(f"\n  {r[0]['view']} -> {r[0]['sources']}")

    loader.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
