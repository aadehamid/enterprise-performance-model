"""
Load Report-to-View CONSUMES edges from Decommissioning of KH_Core.xlsx.

Phase 11: Reads the "Report to View" sheet to create:
  1. New Report nodes (MERGE) for reports not already in the graph
  2. (Report)-[:CONSUMES]->(Table) edges for all unique pairs

Data source:
  Data/new data system files to process/Decommissioning of KH_Core.xlsx
  Sheet: "Report to View"
  Columns used: "View Name", "Report Name"

Prerequisites:
  - Semantic view Table nodes must exist (Phases 7/7a/10)
  - pip install neo4j pandas python-dotenv openpyxl

Usage:
    python src/load_report_to_view.py              # dry-run (default)
    python src/load_report_to_view.py --load        # write to Neo4j
    python src/load_report_to_view.py --pilot       # pilot: first 3 views only
"""

import os
import sys
import argparse
import pandas as pd
from medallion import stamp_report_keys
from neo4j_loader import Neo4jLoader

# ── Path resolution ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXCEL_PATH = os.path.join(
    PROJECT_ROOT, "Data", "new data system files to process",
    "Decommissioning of KH_Core.xlsx",
)
SHEET_NAME = "Report to View"
SOURCE_FILE = "Decommissioning of KH_Core.xlsx"

# ── Canonicalization map: Excel view name → graph qualifiedName ──────────
# Built from the inspection run — resolves casing mismatches, the
# SalesForecast→SaleForecast rename, and the malformed double-prefix row.
CANON_MAP = {
    "sem_comm_kh_mpc_rstd.Deal_vw":       "sem_comm_kh_mpc_rstd.Deal_Vw",
    "sem_comm_kh_mpc_rstd.MovementTransaction_vw": "sem_comm_kh_mpc_rstd.MovementTransaction_VW",
    "sem_comm_kh_mpc_rstd.Movement_vw":    "sem_comm_kh_mpc_rstd.Movement_VW",
    "sem_comm_kh_mpc_rstd.Transfer_vw":    "sem_comm_kh_mpc_rstd.Transfer_VW",
    "sem_comm_kh_mpc_rstd.SalesForecast_vw": "sem_comm_kh_mpc_rstd.SaleForecast_vw",
    "sem_comm_kh_mplx_rstd.sem_comm_kh_mpc_rstd.Movement_vw": "sem_comm_kh_mpc_rstd.Movement_VW",
}

# ── Cypher: MERGE Report nodes ──────────────────────────────────────────
MERGE_REPORT_QUERY = """
UNWIND $rows AS row
MERGE (r:Report {reportKey: row.reportKey})
ON CREATE SET r.name = row.name,
              r.sourceFile = row.sourceFile,
              r.createdAt  = datetime()
"""

# ── Cypher: MERGE CONSUMES edges ────────────────────────────────────────
MERGE_CONSUMES_QUERY = """
UNWIND $rows AS row
MATCH (r:Report {name: row.reportName})
MATCH (v:Table  {qualifiedName: row.viewQN})
MERGE (r)-[:CONSUMES]->(v)
"""


def load_pairs():
    """Read and deduplicate (view, report) pairs from Excel."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    pairs = df[["View Name", "Report Name"]].drop_duplicates()
    # Strip whitespace and invisible unicode
    _invis = "[\u200b\u200c\u200d\ufeff]"
    pairs["View Name"] = pairs["View Name"].str.strip().str.replace(
        _invis, "", regex=True
    )
    pairs["Report Name"] = pairs["Report Name"].str.strip().str.replace(
        _invis, "", regex=True
    )
    # Canonicalize view names
    pairs["viewQN"] = pairs["View Name"].map(lambda v: CANON_MAP.get(v, v))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", action="store_true", help="Write to Neo4j")
    parser.add_argument("--pilot", action="store_true", help="Pilot: first 3 views only")
    args = parser.parse_args()
    dry_run = not args.load

    pairs = load_pairs()
    print(f"Unique (view, report) pairs: {len(pairs)}")
    print(f"Unique views: {pairs['viewQN'].nunique()}")
    print(f"Unique reports: {pairs['Report Name'].nunique()}")

    if args.pilot:
        pilot_views = sorted(pairs["viewQN"].unique())[:3]
        pairs = pairs[pairs["viewQN"].isin(pilot_views)]
        print(f"\n[PILOT] Filtered to {len(pairs)} pairs for views: {pilot_views}")

    if dry_run:
        print("\n[DRY RUN] Would create/merge:")
        print(f"  Report nodes: {pairs['Report Name'].nunique()}")
        print(f"  CONSUMES edges: {len(pairs)}")
        print("\nSample pairs:")
        for _, row in pairs.head(15).iterrows():
            print(f"  {row['Report Name']:50s} -> {row['viewQN']}")
        print("\nRe-run with --load to write to Neo4j.")
        return

    loader = Neo4jLoader()
    try:
        # ── Step 1: MERGE Report nodes ───────────────────────────────────
        print("\nStep 1: Merging Report nodes...")
        report_rows = [
            {"name": rn, "sourceFile": SOURCE_FILE}
            for rn in sorted(pairs["Report Name"].unique())
        ]
        stamp_report_keys(report_rows, loader.build_report_key_lookup(), "name")
        loader.write_batches(MERGE_REPORT_QUERY, report_rows)
        print(f"  Merged {len(report_rows)} Report nodes.")

        # ── Step 2: MERGE CONSUMES edges ─────────────────────────────────
        print("\nStep 2: Merging CONSUMES edges...")
        consumes_rows = [
            {"reportName": row["Report Name"], "viewQN": row["viewQN"]}
            for _, row in pairs.iterrows()
        ]
        loader.write_batches(MERGE_CONSUMES_QUERY, consumes_rows)
        print(f"  Merged {len(consumes_rows)} CONSUMES edges.")

        # ── Step 3: Verification ─────────────────────────────────────────
        print("\n=== Verification ===")

        # Total Report count
        r = loader.run_query("MATCH (r:Report) RETURN count(r) AS c")
        print(f"Total Report nodes: {r[0]['c']}")

        # Total CONSUMES count
        r = loader.run_query("MATCH ()-[c:CONSUMES]->() RETURN count(c) AS c")
        print(f"Total CONSUMES edges: {r[0]['c']}")

        # CONSUMES edges for the 24 views in this file
        view_list = list(pairs["viewQN"].unique())
        r = loader.run_query("""
            MATCH (r:Report)-[:CONSUMES]->(v:Table)
            WHERE v.qualifiedName IN $views
            RETURN count(*) AS c
        """, views=view_list)
        print(f"CONSUMES edges for these {len(view_list)} views: {r[0]['c']}")

        # Reports with sourceFile from this load
        r = loader.run_query(
            "MATCH (r:Report {sourceFile: $sf}) RETURN count(r) AS c",
            sf=SOURCE_FILE,
        )
        print(f"New Report nodes (sourceFile={SOURCE_FILE}): {r[0]['c']}")

        # Spot check: top 5 views by CONSUMES count
        print("\nTop 5 views by report count:")
        r = loader.run_query("""
            MATCH (r:Report)-[:CONSUMES]->(v:Table)
            WHERE v.qualifiedName IN $views
            RETURN v.qualifiedName AS view, count(r) AS reports
            ORDER BY reports DESC LIMIT 5
        """, views=view_list)
        for x in r:
            print(f"  {x['view']:55s} {x['reports']} reports")

        # Check for any pairs that didn't wire (view not found)
        print("\nEdge-count sanity check:")
        r = loader.run_query("""
            MATCH (r:Report)-[:CONSUMES]->(v:Table)
            WHERE v.qualifiedName IN $views
            RETURN count(*) AS wired
        """, views=view_list)
        wired = r[0]["wired"]
        expected = len(consumes_rows)
        if wired >= expected:
            print(f"  All {expected} pairs wired (total for these views: {wired}).")
        else:
            print(f"  WARNING: Expected {expected}, got {wired}. Some pairs may not have matched.")

    finally:
        loader.close()


if __name__ == "__main__":
    main()
