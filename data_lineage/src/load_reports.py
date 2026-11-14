"""
Load Report nodes into Neo4j — Phase 4 of Medallion Architecture implementation.

Creates:
  1. Report nodes with connectionType property
  2. Relationships:
     - (Report)-[:CONSUMES]->(Table:View)     for IDP reports
     - (Report)-[:BELONGS_TO]->(CapabilityDataDomain)

Reads the original Excel mapping file to extract report-to-view consumption pairs
and the clean reports.csv for connectionType and CDD associations.

Prerequisites:
  - Run load_schemas.py and load_tables.py first (Schema + Table nodes must exist)
  - Run extract_mapping_metadata.py to produce Data/reports.csv
  - pip install neo4j pandas python-dotenv openpyxl

Usage:
    python src/load_reports.py
"""

import os
import pandas as pd
from excel_cells import readable_copy, split_multivalue
from medallion import is_legacy, schema_layer, schema_of, stamp_report_keys
from neo4j_loader import Neo4jLoader

# ── Path resolution ────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
REPORTS_CSV = os.path.join(PROJECT_ROOT, "Data", "reports.csv")
EXCEL_PATH = os.path.join(PROJECT_ROOT, "Data", "Phase 3 Reports Full Data Mapping.xlsx")
SHEET_NAME = "Full Mapping"

CDD_NAME_MAP = {
    "Logistic Execution": "Logistics Execution",
    "External Marketing Data": "External Market Data",
    "Local Production Planning": "Local Production Planning & Crude Scheduling",
    "Regional Production": "Regional Production & Distribution Planning",
    "Terminals - Terminal Ops": "Terminal Ops",
    "Terminals Ops": "Terminal Ops",
    "Terminal Operations": "Terminal Ops",
}

# ── Cypher: Create Report nodes ───────────────────────────────────────────
REPORT_QUERY = """
UNWIND $rows AS row
MERGE (r:Report {reportKey: row.reportKey})
ON CREATE SET r.name = row.name,
  r.connectionType = row.connectionType,
  r.createdAt = datetime()
ON MATCH SET r.connectionType = row.connectionType,
  r.updatedAt = datetime()
"""

# ── Cypher: Wire Report -[:BELONGS_TO]-> CapabilityDataDomain ──────────────
REPORT_CDD_QUERY = """
UNWIND $rows AS row
MATCH (r:Report {name: row.reportName})
MERGE (cdd:CapabilityDataDomain {name: row.cddName})
ON CREATE SET cdd.createdAt = datetime()
MERGE (r)-[:BELONGS_TO]->(cdd)
"""

# ── Cypher: Wire Report -[:CONSUMES]-> Table:View ─────────────────────────
REPORT_CONSUMES_QUERY = """
UNWIND $rows AS row
MATCH (r:Report {name: row.reportName})
MERGE (v:Table {qualifiedName: row.viewQualifiedName})
ON CREATE SET v.name = split(row.viewQualifiedName, '.')[1],
              v.layer = row.layer,
              v.sourceFile = 'Direct connection mapping'
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET v:Legacy)
MERGE (r)-[:CONSUMES]->(v)
WITH v, row
WHERE row.layer = 'Operational' AND row.viewQualifiedName CONTAINS '.'
MERGE (ds:DataSystem {name: split(row.viewQualifiedName, '.')[0]})
ON CREATE SET ds.platform = 'Direct Connection Source',
              ds.createdAt = datetime()
MERGE (ds)-[:CONTAINS]->(v)
"""

# ── Verification queries ───────────────────────────────────────────────────
VERIFY_REPORTS = """
MATCH (r:Report)
RETURN r.connectionType AS connectionType, count(r) AS reportCount
ORDER BY reportCount DESC
"""

VERIFY_CONSUMES = """
MATCH (r:Report)-[:CONSUMES]->(v:Table)
RETURN count(DISTINCT r) AS reportsWithConsumes,
       count(*) AS totalConsumesRelationships
"""

VERIFY_CDD_LINKS = """
MATCH (r:Report)-[:BELONGS_TO]->(cdd:CapabilityDataDomain)
RETURN cdd.name AS capabilityDataDomain, count(r) AS reportCount
ORDER BY reportCount DESC
"""

VERIFY_SAMPLE_REPORT = """
MATCH (r:Report {connectionType: 'IDP'})-[:CONSUMES]->(v:Table:View)
WITH r, collect(v.qualifiedName) AS views
RETURN r.name AS report, r.connectionType AS type, views
ORDER BY size(views) DESC
LIMIT 5
"""

VERIFY_UNLINKED_IDP_REPORTS = """
MATCH (r:Report {connectionType: 'IDP'})
WHERE NOT (r)-[:CONSUMES]->()
RETURN r.name AS reportWithNoConsumes
"""


import re

def infer_layer_from_qn(qn):
    return (schema_layer(schema_of(qn)) if "." in qn else None) or "Operational"

def extract_consumes_pairs(df):
    """Extract (report_name, view_qualifiedName, layer) triples from the mapping file.

    Handles both IDP reports (conformed Semantic views) and Direct Connection reports.
    """
    pairs = set()
    for _, row in df.iterrows():
        report_name = str(row["Report"]).strip()
        if pd.isna(row["Report"]) or not report_name or report_name.lower() == "nan":
            continue

        conn_val = str(row.get("Live Report or Connected to IDP?", "")).strip()
        
        if conn_val == "IDP":
            # IDP reports consume conformed semantic views
            sem_view = row.get("Semantic View / Direct Table Connection")
            if pd.isna(sem_view):
                continue
            for view in split_multivalue(sem_view):
                if "." in view:
                    pairs.add((report_name, view, infer_layer_from_qn(view)))
        else:
            # Non-IDP direct connection reports consume operational tables
            source_sys = str(row.get("If No IDP, Source System?", "")).strip()
            if not source_sys or source_sys.lower() == "nan":
                continue
            
            # Clean up source system name (e.g. strip whitespace, replace newlines)
            source_sys = re.sub(r"\s+", "_", source_sys).strip("_")
            
            direct_tables = row.get("Semantic View / Direct Table Connection")
            if pd.isna(direct_tables):
                continue
            for tbl in split_multivalue(direct_tables):
                # If it already contains a dot (e.g. mpc.AccountingTransaction),
                # extract the table name after the dot
                if "." in tbl:
                    tbl_name = tbl.split(".", 1)[1].strip()
                else:
                    tbl_name = tbl
                
                # Strip raw trailing markers/Unicode trash if any
                tbl_name = re.sub(r"[^\w_]", "", tbl_name)
                if tbl_name:
                    qualified_name = f"{source_sys}.{tbl_name}"
                    pairs.add((report_name, qualified_name, "Operational"))
                    
    return pairs


def main():
    loader = Neo4jLoader()

    try:
        # ── Step 1: Create Report nodes from CSV ──────────────────────────
        print("Step 1: Loading Report nodes from CSV...")
        reports_df = pd.read_csv(REPORTS_CSV)
        print(f"  Total reports in CSV: {len(reports_df)}")

        records = [
            {"name": str(row["name"]).strip(),
             "connectionType": str(row["connectionType"]).strip()}
            for _, row in reports_df.iterrows()
        ]
        stamp_report_keys(records, loader.build_report_key_lookup(), "name")
        loader.write_batches(REPORT_QUERY, records)
        print(f"  Loaded {len(records)} Report nodes.")

        # ── Step 2: Wire Report -[:BELONGS_TO]-> CDD ──────────────────────
        print("\nStep 2: Linking Reports to CapabilityDataDomains...")
        cdd_records = []
        for _, row in reports_df.iterrows():
            report_name = str(row["name"]).strip()
            cdd_raw = str(row.get("capabilityDataDomain", "")).strip()
            if not cdd_raw:
                continue
            # CDDs are pipe-separated in CSV
            for cdd in cdd_raw.split("|"):
                cdd = cdd.strip()
                if cdd and cdd.lower() != 'nan':
                    # Apply canonical conversions
                    conformed_cdd = CDD_NAME_MAP.get(cdd, cdd)
                    cdd_records.append({
                        "reportName": report_name,
                        "cddName": conformed_cdd,
                    })

        loader.write_batches(REPORT_CDD_QUERY, cdd_records)
        print(f"  Created {len(cdd_records)} BELONGS_TO relationships.")

        # ── Step 3: Wire Report -[:CONSUMES]-> View ────────────────────────
        print("\nStep 3: Linking Reports to Semantic Views (CONSUMES)...")
        with readable_copy(EXCEL_PATH) as excel_copy:
            df = pd.read_excel(excel_copy, sheet_name=SHEET_NAME)
        consumes_pairs = extract_consumes_pairs(df)
        print(f"  Unique (report, view) pairs: {len(consumes_pairs)}")

        consumes_records = [
            {"reportName": rpt, "viewQualifiedName": view, "layer": layer}
            for rpt, view, layer in consumes_pairs
        ]
        qn_lookup = loader.build_table_qn_lookup()
        Neo4jLoader.canonicalize_table_fields(consumes_records, qn_lookup, "viewQualifiedName")
        for rec in consumes_records:
            rec["legacy"] = is_legacy(rec["viewQualifiedName"], rec["layer"])

        loader.write_batches(REPORT_CONSUMES_QUERY, consumes_records)
        print(f"  Created {len(consumes_records)} CONSUMES relationships.")

        # ── Verification ───────────────────────────────────────────────────
        print("\n=== Verification ===")

        print("\nReports by connectionType:")
        loader.verify(VERIFY_REPORTS)

        print("\nCONSUMES relationship counts:")
        loader.verify(VERIFY_CONSUMES)

        print("\nReports per CapabilityDataDomain:")
        loader.verify(VERIFY_CDD_LINKS)

        print("\nTop 5 IDP reports by views consumed:")
        loader.verify(VERIFY_SAMPLE_REPORT)

        print("\nIDP reports with NO CONSUMES (potential gaps):")
        gaps = loader.verify(VERIFY_UNLINKED_IDP_REPORTS)
        if not gaps:
            print("  None — all IDP reports have CONSUMES relationships!")

    finally:
        loader.close()


if __name__ == "__main__":
    main()
