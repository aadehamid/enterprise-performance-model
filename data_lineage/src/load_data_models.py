"""
Phase 12: Load ER Studio Data Model artifacts into the knowledge graph.

Creates DataModel nodes from the UDM Data Model Approval Status spreadsheet
and wires them to CapabilityDataDomain (BELONGS_TO) and DataSystem (MODELS).

Usage:
    python src/load_data_models.py            # full load
    python src/load_data_models.py --dry-run   # preview without writing
"""

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excel_cells import clean_cell
from neo4j_loader import Neo4jLoader

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(
    PROJECT_ROOT, "Data", "Data_Models",
    "UDM Data Model Approval Status.xlsx",
)
SOURCE_FILE_NAME = "UDM Data Model Approval Status.xlsx"

# ---------------------------------------------------------------------------
# CDD name canonicalization — map spreadsheet values to graph node names
# ---------------------------------------------------------------------------
CDD_NAME_MAP = {
    "Brand Data Integration": "Brand Data & Integration",
    "Logistic Execution":     "Logistics Execution",
}

# New CDDs to create (not in the graph today)
NEW_CDDS = {
    "Terminal Operations",
    "ES&S",
    "Legal",
    "Revenue Accounting & Scheduling",
}

# ---------------------------------------------------------------------------
# DataSystem name canonicalization
# ---------------------------------------------------------------------------
DS_NAME_MAP = {
    "Nvision": "NVision",  # graph stores as NVision
}

# New DataSystems to create
NEW_DATASYSTEMS = {"Corp_Vetting", "BAT", "APS"}

# ---------------------------------------------------------------------------
# Parse model type from file name
# ---------------------------------------------------------------------------
def derive_model_type(file_name: str) -> str:
    """Return 'Conceptual' or 'Logical' based on file name pattern."""
    if "Conceptual" in file_name:
        return "Conceptual"
    return "Logical"


# ---------------------------------------------------------------------------
# Read and transform the Excel data
# ---------------------------------------------------------------------------
def read_excel(path: str) -> pd.DataFrame:
    """Read the Excel file and handle merged cells via forward-fill.

    Uses keep_default_na=False so pandas does NOT silently convert the
    literal text "NA" (used as a domain value meaning "no domain") into
    NaN.  Merged cells appear as empty strings, which we convert to NaN
    before forward-filling.

    Hyperlink URLs in the Folder Link column are extracted via openpyxl
    (pandas only reads display text, not the underlying URL).
    """
    import openpyxl

    df = pd.read_excel(path, sheet_name=0, keep_default_na=False)

    # Drop the internal "Exists/Added" column (col G, unnamed)
    cols_to_keep = [
        "Data Capability Domain", "Database", "Model File Name",
        "A&I Approval Status", "Business Approval Status", "Folder Link",
    ]
    df = df[[c for c in cols_to_keep if c in df.columns]]

    # --- Extract hyperlink URLs from Folder Link column (col F = 6) ---
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    # Build a map: row_index (0-based data row) -> hyperlink target URL
    hyperlink_map = {}
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=6, max_col=6):
        cell = row[0]
        if cell.hyperlink and cell.hyperlink.target:
            data_row_idx = cell.row - 2  # row 2 in Excel = index 0 in DataFrame
            hyperlink_map[data_row_idx] = cell.hyperlink.target
    wb.close()

    # Replace Folder Link display text with actual URL where available
    for idx, url in hyperlink_map.items():
        if idx < len(df):
            df.at[idx, "Folder Link"] = url

    # Convert empty strings (from merged cells) to NaN so ffill works
    df.replace("", pd.NA, inplace=True)

    # Forward-fill merged cells
    df["Data Capability Domain"] = df["Data Capability Domain"].ffill()
    df["Database"] = df["Database"].ffill()
    df["Folder Link"] = df["Folder Link"].ffill()

    # Clean all string columns
    for col in df.columns:
        df[col] = df[col].apply(clean_cell)

    # Drop rows with no model file name (shouldn't happen, but defensive)
    df = df.dropna(subset=["Model File Name"])

    return df


# ---------------------------------------------------------------------------
# Transform rows into records for Cypher
# ---------------------------------------------------------------------------
def transform_rows(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame rows to dicts ready for Cypher parameters."""
    records = []
    for _, row in df.iterrows():
        file_name = row["Model File Name"]
        name = file_name.replace(".DM1", "")
        model_type = derive_model_type(file_name)

        # Canonicalize CDD name (skip "NA" — means no domain assigned)
        raw_domain = row["Data Capability Domain"]
        if raw_domain and raw_domain.upper() != "NA":
            cdd_name = CDD_NAME_MAP.get(raw_domain, raw_domain)
        else:
            cdd_name = None

        # Canonicalize DataSystem name
        raw_db = row["Database"]
        if raw_db and raw_db.lower() == "multiple":
            ds_name = None
        else:
            ds_name = DS_NAME_MAP.get(raw_db, raw_db) if raw_db else None

        folder_link = row.get("Folder Link")

        records.append({
            "name": name,
            "fileName": file_name,
            "modelType": model_type,
            "cddName": cdd_name,
            "dsName": ds_name,
            "folderLink": folder_link,
            "sourceFile": SOURCE_FILE_NAME,
        })

    return records


# ---------------------------------------------------------------------------
# Cypher queries
# ---------------------------------------------------------------------------
CONSTRAINT_QUERY = """
CREATE CONSTRAINT DataModel_name_key IF NOT EXISTS
  FOR (n:DataModel) REQUIRE n.name IS NODE KEY
"""

MERGE_DATAMODEL_QUERY = """
UNWIND $rows AS row
MERGE (dm:DataModel {name: row.name})
  ON CREATE SET dm.fileName    = row.fileName,
                dm.modelType   = row.modelType,
                dm.folderLink  = row.folderLink,
                dm.sourceFile  = row.sourceFile,
                dm.createdAt   = datetime()
  ON MATCH SET  dm.fileName    = row.fileName,
                dm.modelType   = row.modelType,
                dm.folderLink  = row.folderLink,
                dm.sourceFile  = row.sourceFile,
                dm.updatedAt   = datetime()
"""

MERGE_MODELS_CDD_QUERY = """
UNWIND $rows AS row
WITH row WHERE row.cddName IS NOT NULL
MERGE (dm:DataModel {name: row.name})
MERGE (cdd:CapabilityDataDomain {name: row.cddName})
  ON CREATE SET cdd.createdAt = datetime()
MERGE (dm)-[:MODELS]->(cdd)
"""

MERGE_BELONGS_TO_DS_QUERY = """
UNWIND $rows AS row
WITH row WHERE row.dsName IS NOT NULL
MERGE (dm:DataModel {name: row.name})
MERGE (ds:DataSystem {name: row.dsName})
  ON CREATE SET ds.createdAt = datetime()
MERGE (dm)-[:BELONGS_TO]->(ds)
"""

# ---------------------------------------------------------------------------
# Validation queries
# ---------------------------------------------------------------------------
COUNT_DATAMODELS = "MATCH (dm:DataModel) RETURN count(dm) AS cnt"
COUNT_MODELS_CDD = """
MATCH (dm:DataModel)-[:MODELS]->(cdd:CapabilityDataDomain)
RETURN count(*) AS cnt
"""
COUNT_BELONGS_TO_DS = """
MATCH (dm:DataModel)-[:BELONGS_TO]->(ds:DataSystem)
RETURN count(*) AS cnt
"""
NEW_CDDS_CHECK = """
MATCH (cdd:CapabilityDataDomain)
WHERE cdd.name IN $names
RETURN cdd.name AS name
ORDER BY name
"""
NEW_DS_CHECK = """
MATCH (ds:DataSystem)
WHERE ds.name IN $names
RETURN ds.name AS name
ORDER BY name
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Load ER Studio Data Models")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview records without writing to Neo4j")
    args = parser.parse_args()

    # 1. Read and transform
    print(f"Reading {DATA_PATH} ...")
    df = read_excel(DATA_PATH)
    records = transform_rows(df)
    print(f"  {len(records)} DataModel records prepared")

    # Summarize
    n_with_cdd = sum(1 for r in records if r["cddName"])
    n_with_ds = sum(1 for r in records if r["dsName"])
    n_conceptual = sum(1 for r in records if r["modelType"] == "Conceptual")
    n_logical = sum(1 for r in records if r["modelType"] == "Logical")
    print(f"  {n_conceptual} Conceptual, {n_logical} Logical")
    print(f"  {n_with_cdd} with CDD link, {n_with_ds} with DataSystem link")

    if args.dry_run:
        print("\n--- DRY RUN: Records ---")
        for r in records:
            print(f"  {r['name']:55s} type={r['modelType']:12s} "
                  f"cdd={r['cddName']!r:55s} ds={r['dsName']!r}")
        print("\nDry run complete. No changes written.")
        return

    # 2. Connect and load
    loader = Neo4jLoader()

    # Create constraint
    print("\nCreating constraint ...")
    loader.run_write(CONSTRAINT_QUERY)

    # Merge DataModel nodes
    print("Merging DataModel nodes ...")
    loader.write_batches(MERGE_DATAMODEL_QUERY, records)
    print(f"  Merged {len(records)} DataModel nodes")

    # Merge MODELS -> CDD
    print("Merging MODELS -> CapabilityDataDomain ...")
    loader.write_batches(MERGE_MODELS_CDD_QUERY, records)
    print(f"  Merged {n_with_cdd} MODELS edges")

    # Merge BELONGS_TO -> DataSystem
    print("Merging BELONGS_TO -> DataSystem ...")
    loader.write_batches(MERGE_BELONGS_TO_DS_QUERY, records)
    print(f"  Merged {n_with_ds} BELONGS_TO edges")

    # 3. Validate
    print("\n=== Validation ===")
    dm_count = loader.run_query(COUNT_DATAMODELS)[0]["cnt"]
    models_count = loader.run_query(COUNT_MODELS_CDD)[0]["cnt"]
    bt_count = loader.run_query(COUNT_BELONGS_TO_DS)[0]["cnt"]
    print(f"  DataModel nodes:          {dm_count} (expected {len(records)})")
    print(f"  MODELS edges (->CDD):     {models_count} (expected {n_with_cdd})")
    print(f"  BELONGS_TO edges (->DS):   {bt_count} (expected {n_with_ds})")

    # Verify new CDDs
    new_cdd_results = loader.run_query(NEW_CDDS_CHECK, names=list(NEW_CDDS))
    found_cdds = {r["name"] for r in new_cdd_results}
    print(f"  New CDDs created:         {sorted(found_cdds)}")
    missing_cdds = NEW_CDDS - found_cdds
    if missing_cdds:
        print(f"  WARNING: Missing CDDs:    {sorted(missing_cdds)}")

    # Verify new DataSystems
    new_ds_results = loader.run_query(NEW_DS_CHECK, names=list(NEW_DATASYSTEMS))
    found_ds = {r["name"] for r in new_ds_results}
    print(f"  New DataSystems created:  {sorted(found_ds)}")
    missing_ds = NEW_DATASYSTEMS - found_ds
    if missing_ds:
        print(f"  WARNING: Missing DS:      {sorted(missing_ds)}")

    # Assertions
    assert dm_count == len(records), f"DataModel count mismatch: {dm_count} != {len(records)}"
    assert models_count == n_with_cdd, f"MODELS count mismatch: {models_count} != {n_with_cdd}"
    assert bt_count == n_with_ds, f"BELONGS_TO count mismatch: {bt_count} != {n_with_ds}"
    assert not missing_cdds, f"Missing CDDs: {missing_cdds}"
    assert not missing_ds, f"Missing DataSystems: {missing_ds}"

    print("\n[OK] All validations passed.")

    # 4. Visual verification query
    print("\n=== Neo4j Browser Verification Query ===")
    print("""
MATCH (dm:DataModel)-[m:MODELS]->(cdd:CapabilityDataDomain)
OPTIONAL MATCH (dm)-[bt:BELONGS_TO]->(ds:DataSystem)
RETURN dm, m, cdd, bt, ds
""")

    loader.close()


if __name__ == "__main__":
    main()
