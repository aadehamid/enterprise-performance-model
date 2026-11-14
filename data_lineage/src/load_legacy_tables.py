"""
load_legacy_tables.py - Load legacy schema tables and REFACTORED_TO edges.

Sources:
  - Data/legacy_systems.xlsx (sheet "Unique tables") — 77 rows across 4 legacy schemas
  - KH_Core Counts file supplement — 9 additional KH_Core tables not in legacy_systems.xlsx

Phases:
  A. Create/merge Legacy Schema nodes (KH_Core, dwh, persistence, dwh_core)
  B. Create Legacy Table nodes + Schema CONTAINS
  C. Create REFACTORED_TO edges (legacy → IDP target)
  D. Mark 4 sem_comm_kh_mpc_rstd views :Legacy (layer stays Semantic)
  E. Create 11 missing KH semantic views + DERIVED_FROM to legacy source
  F. Verification

Usage:
    python src/load_legacy_tables.py            # dry-run
    python src/load_legacy_tables.py --load     # write to Neo4j
"""
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import logging
import warnings

import pandas as pd
from medallion import schema_layer
from neo4j_loader import Neo4jLoader

BASE_DIR = os.path.join(SCRIPT_DIR, "..")

# =====================================================================
# Data: 9 additional KH_Core rows from Counts file (not in legacy_systems)
# =====================================================================
EXTRA_KH_CORE = [
    ("Brand",                      "mdm_core.Kittyhawk_Brand_Dim"),
    ("BrandProduct",               "mdm_core.Kittyhawk_Brand_Product_Xref"),
    ("HolidayCalendar",            "mdm_core.Kittyhawk_Holiday_Calendar_Dim"),
    ("HolidayCalendarDetail",      "mdm_core.Kittyhawk_Holiday_Calendar_Detail_Dim"),
    ("Location",                   "mdm_core.Kittyhawk_Location_Dim"),
    ("SalesForecast_mpc",          "udm_core.Kittyhawk_Sales_Forecast_Fact"),
    ("SalesForecastToRightAngle",  "mdm_core.Kittyhawk_Sales_Forecast_To_Right_Anlge_Dim"),
    ("SchedulingObligation_mpc",   "udm_core.Kittyhawk_Scheduling_Obligation_Fact"),
    ("TransactionType",            "mdm_core.Kittyhawk_Transaction_Type_Dim"),
]

# =====================================================================
# Data: 11 missing KH semantic views + their legacy source (Col 3)
# Case-sensitive qualifiedNames — will be resolved against graph.
# =====================================================================
MISSING_KH_VIEWS = [
    # (view qualifiedName, legacy source qualifiedName)
    ("sem_comm_kh_mpc_rstd.Movement_vw",                        "replica_kittyhawk.Movement"),
    ("sem_comm_kh_mpc_rstd.MovementTransaction_vw",             "replica_kittyhawk.MovementTransaction"),
    ("sem_comm_kh_mpc_rstd.Deal_vw",                            "replica_kittyhawk.Deal"),
    ("sem_comm_kh_mpc_rstd.Transfer_vw",                        "replica_kittyhawk.Transfer"),
    ("sem_comm_kh_mpc_rstd.TerminalProductStatus_vw",           "KH_Core.TerminalProductStatus_mpc"),
    ("sem_masterdata.Businessassociate_vw",                      "KH_Core.Businessassociate"),
    ("sem_comm_kh_mpc_rstd.DealForecastOrgClassDistrictCurrent_vw", "replica_kittyhawk.DealForecastOrgClassDistrict"),
    ("sem_masterdata.Product_vw",                                "KH_Core.Product"),
    ("sem_masterdata.pipelinecycle_vw",                          "replica_kittyhawk.LeaseDeal"),
    ("sem_masterdata.PositionGroup_vw",                          "KH_Core.PositionGroup"),
    ("sem_comm_kh_mpc_rstd.SalesForecast_vw",                   "KH_Core.SalesForecast_mpc"),
]

# =====================================================================
# Data: 4 KH views to mark :Legacy
# =====================================================================
LEGACY_KH_VIEWS = [
    "sem_comm_kh_mpc_rstd.Inventory_VW",
    "sem_comm_kh_mpc_rstd.InventoryHistory_VW",
    "sem_comm_kh_mpc_rstd.LeaseDeal_VW",
    "sem_comm_kh_mpc_rstd.SaleForecast_vw",
]

# =====================================================================
# Cypher Queries
# =====================================================================

# Phase A: Create Legacy Schema
MERGE_SCHEMA = """
MERGE (s:Schema {qualifiedName: $qn})
ON CREATE SET s.layer = $layer, s.createdAt = datetime()
SET s:Legacy
"""

# Phase B: Create Legacy Table + wire to Schema
MERGE_LEGACY_TABLE = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.legacyQN})
ON CREATE SET t.tableName = row.tableName, t.layer = row.layer,
              t.createdAt = datetime()
ON MATCH SET  t.layer = row.layer
SET t:Legacy
WITH t, row
MATCH (s:Schema {qualifiedName: row.schemaName})
MERGE (s)-[:CONTAINS]->(t)
"""

# Phase C: Create REFACTORED_TO edges
MERGE_REFACTORED_TO = """
UNWIND $rows AS row
MATCH (legacy:Table {qualifiedName: row.legacyQN})
MERGE (idp:Table {qualifiedName: row.idpQN})
ON CREATE SET idp.tableName = row.idpTableName, idp.createdAt = datetime()
MERGE (legacy)-[:REFACTORED_TO]->(idp)
"""

# Phase D: Mark KH views as Legacy (layer stays Semantic)
MARK_LEGACY = """
MATCH (t:Table {qualifiedName: $qn})
SET t:Legacy
"""

# Phase E: Create missing views + DERIVED_FROM
MERGE_MISSING_VIEW = """
UNWIND $rows AS row
MERGE (v:Table {qualifiedName: row.viewQN})
ON CREATE SET v.tableName = row.viewTableName, v.layer = row.layer,
              v.createdAt = datetime()
ON MATCH SET  v.layer = row.layer
SET v:Legacy
WITH v, row
MERGE (src:Table {qualifiedName: row.sourceQN})
MERGE (v)-[:DERIVED_FROM]->(src)
"""

# Wire missing views to their schema
WIRE_VIEW_SCHEMA = """
UNWIND $rows AS row
MATCH (v:Table {qualifiedName: row.viewQN})
MATCH (s:Schema {qualifiedName: row.schemaName})
MERGE (s)-[:CONTAINS]->(v)
"""


def load_legacy_systems_file():
    """Load legacy_systems.xlsx 'Unique tables' sheet."""
    path = os.path.join(BASE_DIR, "Data", "legacy_systems.xlsx")
    df = pd.read_excel(path, sheet_name="Unique tables")
    df.columns = df.columns.str.strip()
    return df


def build_legacy_rows(df):
    """Build list of dicts for legacy table creation from legacy_systems.xlsx."""
    rows = []
    for _, r in df.iterrows():
        schema = str(r['Legacy Schema']).strip()
        table = str(r['Legacy Table Name']).strip()
        idp_schema = str(r['IDP Schema']).strip()
        idp_table = str(r['IDP Table Name']).strip()
        rows.append({
            "schemaName": schema,
            "tableName": table,
            "legacyQN": f"{schema}.{table}",
            "layer": schema_layer(schema) or "Silver",
            "idpQN": f"{idp_schema}.{idp_table}",
            "idpTableName": idp_table,
        })
    return rows


def build_extra_kh_rows():
    """Build rows for the 9 additional KH_Core tables from Counts file."""
    rows = []
    for table, idp_qn in EXTRA_KH_CORE:
        idp_parts = idp_qn.split('.', 1)
        rows.append({
            "schemaName": "KH_Core",
            "tableName": table,
            "legacyQN": f"KH_Core.{table}",
            "layer": schema_layer("KH_Core"),
            "idpQN": idp_qn,
            "idpTableName": idp_parts[1] if len(idp_parts) > 1 else idp_qn,
        })
    return rows


def build_missing_view_rows():
    """Build rows for the 11 missing KH semantic views."""
    rows = []
    for view_qn, source_qn in MISSING_KH_VIEWS:
        schema = view_qn.split('.')[0]
        view_name = view_qn.split('.', 1)[1]
        rows.append({
            "viewQN": view_qn,
            "viewTableName": view_name,
            "layer": schema_layer(schema),
            "sourceQN": source_qn,
            "schemaName": schema,
        })
    return rows


def main():
    warnings.filterwarnings("ignore")
    logging.disable(logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", action="store_true")
    args = parser.parse_args()

    loader = Neo4jLoader()

    # ---- Load data ----
    df = load_legacy_systems_file()
    legacy_rows = build_legacy_rows(df)
    extra_kh = build_extra_kh_rows()
    all_rows = legacy_rows + extra_kh
    view_rows = build_missing_view_rows()
    qn_lookup = loader.build_table_qn_lookup()
    Neo4jLoader.canonicalize_table_fields(all_rows, qn_lookup, "legacyQN", "idpQN")
    Neo4jLoader.canonicalize_table_fields(view_rows, qn_lookup, "viewQN", "sourceQN")

    # ---- Deduplicate by legacyQN (in case of overlap) ----
    seen = set()
    deduped = []
    for r in all_rows:
        if r['legacyQN'] not in seen:
            seen.add(r['legacyQN'])
            deduped.append(r)
    all_rows = deduped

    # ---- Extract unique schemas ----
    schemas = sorted(set(r['schemaName'] for r in all_rows))

    # ---- Summary ----
    print("=" * 60)
    print("Legacy Tables Load — Summary")
    print("=" * 60)
    print(f"\nPhase A: {len(schemas)} Legacy Schemas: {schemas}")
    print(f"Phase B: {len(all_rows)} Legacy Table nodes")
    for s in schemas:
        cnt = sum(1 for r in all_rows if r['schemaName'] == s)
        print(f"    {s}: {cnt}")
    print(f"Phase C: {len(all_rows)} REFACTORED_TO edges")
    print(f"Phase D: {len(LEGACY_KH_VIEWS)} KH views marked :Legacy")
    for v in LEGACY_KH_VIEWS:
        print(f"    {v}")
    print(f"Phase E: {len(view_rows)} missing KH views + DERIVED_FROM")
    for v in view_rows:
        print(f"    {v['viewQN']} → {v['sourceQN']}")

    if not args.load:
        print("\nDry-run complete. Use --load to write to Neo4j.")
        loader.close()
        return

    # ---- Execute ----
    with loader.driver.session(database=loader.database) as session:

        # Phase A: Schemas
        for s in schemas:
            session.execute_write(lambda tx, n=s: tx.run(MERGE_SCHEMA, qn=n, layer=schema_layer(n) or "Silver"))
        print(f"\nPhase A: Merged {len(schemas)} Legacy Schema nodes")

        # Phase B: Legacy Tables + Schema CONTAINS
        loader.write_batches(MERGE_LEGACY_TABLE, all_rows)
        print(f"Phase B: Merged {len(all_rows)} Legacy Table nodes + CONTAINS")

        # Phase C: REFACTORED_TO
        loader.write_batches(MERGE_REFACTORED_TO, all_rows)
        print(f"Phase C: Merged {len(all_rows)} REFACTORED_TO edges")

        # Phase D: Mark KH views as Legacy
        for v in LEGACY_KH_VIEWS:
            stored = Neo4jLoader.canonicalize_table_qn(v, qn_lookup)
            session.execute_write(lambda tx, qn=stored: tx.run(MARK_LEGACY, qn=qn))
        print(f"Phase D: Marked {len(LEGACY_KH_VIEWS)} KH views as :Legacy")

        # Phase E: Missing views
        loader.write_batches(MERGE_MISSING_VIEW, view_rows)
        loader.write_batches(WIRE_VIEW_SCHEMA, view_rows)
        print(f"Phase E: Merged {len(view_rows)} missing views + DERIVED_FROM + Schema wiring")

    # ---- Phase F: Verification ----
    print("\n" + "=" * 60)
    print("Phase F: Verification")
    print("=" * 60)

    # Check legacy tables with REFACTORED_TO
    rt_count = loader.run_query("""
        MATCH (t:Table:Legacy)-[:REFACTORED_TO]->()
        RETURN count(t) AS cnt
    """)
    print(f"  Legacy tables with REFACTORED_TO: {rt_count[0]['cnt']}")

    # Check legacy tables WITHOUT REFACTORED_TO
    no_rt = loader.run_query("""
        MATCH (t:Table:Legacy)
        WHERE NOT (t)-[:REFACTORED_TO]->()
        RETURN t.qualifiedName AS qn ORDER BY qn
    """)
    print(f"  Legacy tables WITHOUT REFACTORED_TO: {len(no_rt)}")
    for r in no_rt:
        print(f"    {r['qn']}")

    # Check sem_comm_kh_mpc_rstd layer consistency
    kh_views = loader.run_query("""
        MATCH (t:Table)
        WHERE t.qualifiedName STARTS WITH 'sem_comm_kh_mpc_rstd.'
        RETURN t.qualifiedName AS qn, t.layer AS layer, t:Legacy AS legacy ORDER BY qn
    """)
    non_legacy = [r for r in kh_views if not r['legacy']]
    print(f"\n  sem_comm_kh_mpc_rstd views total: {len(kh_views)}")
    print(f"  sem_comm_kh_mpc_rstd views NOT Legacy: {len(non_legacy)}")
    for r in non_legacy:
        print(f"    {r['qn']} layer={r['layer']}")

    # Check missing views now have DERIVED_FROM
    for v in view_rows:
        r = loader.run_query("""
            MATCH (t:Table {qualifiedName: $qn})-[:DERIVED_FROM]->(src)
            RETURN src.qualifiedName AS src
        """, qn=v['viewQN'])
        sources = [x['src'] for x in r]
        print(f"  {v['viewQN']:60s} → {sources}")

    # Spot check REFACTORED_TO
    spots = ["KH_Core.Contact", "persistence.Enverus_Rigs", "dwh.vw_Argus_Deals",
             "KH_Core.Brand", "persistence.WFOR_Weather_Forecast"]
    print("\n  REFACTORED_TO spot checks:")
    for qn in spots:
        r = loader.run_query("""
            MATCH (t:Table {qualifiedName: $qn})-[:REFACTORED_TO]->(idp)
            RETURN idp.qualifiedName AS target
        """, qn=qn)
        if r:
            print(f"    {qn:45s} → {r[0]['target']}")
        else:
            print(f"    {qn:45s} → NOT FOUND")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
