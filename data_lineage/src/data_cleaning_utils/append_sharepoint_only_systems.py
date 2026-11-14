"""
Append Sharepoint-only DataSystems (blank DataSystem.name) to the IDP CSV.

These are systems that exist in the Sharepoint source repository but were not
in the original IDP extract. For these rows, the Source Name is used as the
DataSystem.name.

Deduplicates by Source Name before appending.
Uses Source_System_Id from the Sharepoint CSV as DataSystem.Id.
Sets Record_Active_Indicator to true and description to empty.

Usage:
    python src/data_cleaning_utils/append_sharepoint_only_systems.py

Prerequisites:
    - Run merge_sharepoint_into_idp.py first (so IDP CSV has the 9 enriched columns)
"""

import pandas as pd
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from medallion import flag_bool

# ── Paths ──────────────────────────────────────────────────────────────────
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data")
except NameError:
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")
SP_PATH = os.path.join(DATA_DIR, "Source System Repository from Sharepoint.csv")
IDP_PATH = os.path.join(DATA_DIR, "Source_System_from_IDP.csv")
OUTPUT_PATH = IDP_PATH  # overwrite in place; change if you want a separate file

# ── Sharepoint column → IDP column mapping ─────────────────────────────────
SP_TO_IDP_COLUMN_MAP = {
    "Source Name":                      "DataSystem.name",
    "BusinessArea":                     "BuisnessArea",
    "applicationService":               "applicationService",
    "confidentialityClassification":    "confidentialityClassification",
    "isSoxRelevant":                    "isSoxRelevant",
    "dataModality":                     "dataModality",
    "applicationType":                  "applicationType",
    "purviewReplicaSchemaName":         "purviewReplicaSchemaName",
    "purviewSourceTypeAssetLink":       "purviewSourceTypeAssetLink",
    "ingestionMethod":                  "ingestionMethod",
    "refreshFrequency":                 "refreshFrequency",
}


def clean_source_name(name):
    """Strip '-Prod' suffix and trailing whitespace from Source Name."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    # Remove common suffixes to get a clean system name
    for suffix in ["-Prod", " -Prod"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip()


def parse_business_area(raw_value):
    """Parse BusinessArea from JSON list string to plain string for IDP format.
    
    Sharepoint stores as '["Commercial"]' → return 'Commercial'.
    If multiple areas, return the first one (these are single-area systems).
    """
    if pd.isna(raw_value):
        return None
    s = str(raw_value).strip()
    if s.startswith("["):
        try:
            areas = json.loads(s)
            return areas[0] if areas else None
        except json.JSONDecodeError:
            pass
    return s


def main():
    # ── 1. Read both CSVs ──────────────────────────────────────────────────
    sp = pd.read_csv(SP_PATH)
    idp = pd.read_csv(IDP_PATH)
    print(f"IDP rows (before): {len(idp)}")
    print(f"Sharepoint rows (raw): {len(sp)}")

    # ── 2. Identify blank DataSystem.name BEFORE string conversion ──────────
    #    NaN detection must happen before .astype(str) which converts NaN → "nan"
    blank_mask = sp["DataSystem.name"].isna()
    # Also catch whitespace-only or newline-only values
    str_col = sp["DataSystem.name"].astype(str).str.strip().str.replace(r'\n|\r', '', regex=True)
    blank_mask = blank_mask | str_col.isin(["", "nan"])

    sp_blank = sp[blank_mask].copy()
    print(f"Sharepoint rows with blank DataSystem.name: {len(sp_blank)}")

    # ── 4. Use Source Name as the system name ──────────────────────────────
    sp_blank["clean_name"] = sp_blank["Source Name"].apply(clean_source_name)

    # ── 5. Deduplicate by clean_name ───────────────────────────────────────
    sp_blank = sp_blank.drop_duplicates(subset="clean_name", keep="first")
    print(f"After dedup by Source Name: {len(sp_blank)}")

    # ── 6. Exclude any that already exist in IDP (by name) ────────────────
    idp_names = set(idp["DataSystem.name"].astype(str).str.strip())
    sp_new = sp_blank[~sp_blank["clean_name"].isin(idp_names)].copy()
    print(f"Truly new systems (not in IDP): {len(sp_new)}")

    if len(sp_new) == 0:
        print("Nothing to append.")
        return

    # ── 7. Build new IDP rows ──────────────────────────────────────────────
    new_rows = []
    for _, row in sp_new.iterrows():
        # Use Source_System_Id from Sharepoint as the DataSystem.Id
        sp_id = row.get("Source_System_Id")
        if pd.notna(sp_id):
            sp_id = int(sp_id)
        new_row = {
            "DataSystem.Id": sp_id,
            "DataSystem.name": row["clean_name"],
            "DataSystem.Description": "",
            "BuisnessArea": parse_business_area(row["BusinessArea"]),
            "Record_Active_Indicator": flag_bool("Y"),
            "applicationService": row.get("applicationService"),
            "confidentialityClassification": row.get("confidentialityClassification"),
            "isSoxRelevant": flag_bool(row.get("isSoxRelevant")),
            "dataModality": row.get("dataModality"),
            "applicationType": row.get("applicationType"),
            "purviewReplicaSchemaName": row.get("purviewReplicaSchemaName"),
            "purviewSourceTypeAssetLink": row.get("purviewSourceTypeAssetLink"),
            "ingestionMethod": row.get("ingestionMethod"),
            "refreshFrequency": row.get("refreshFrequency"),
        }
        new_rows.append(new_row)

    new_df = pd.DataFrame(new_rows)

    # ── 8. Preview new rows ────────────────────────────────────────────────
    print("\n=== New systems to append ===")
    for _, r in new_df.iterrows():
        print(f"  ID={int(r['DataSystem.Id'])}: {r['DataSystem.name']} → {r['BuisnessArea']}")

    # ── 9. Append and save ─────────────────────────────────────────────────
    idp_updated = pd.concat([idp, new_df], ignore_index=True)
    idp_updated.to_csv(OUTPUT_PATH, index=False)
    print(f"\nIDP rows (after): {len(idp_updated)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
