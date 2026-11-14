"""
Fix DataSystem.Id for appended Sharepoint-only systems.

The append script incorrectly used auto-incremented IDs (193+).
The correct ID should come from Source_System_Id in the Sharepoint CSV.

This script:
  1. Identifies the appended systems (blank DataSystem.name in Sharepoint)
  2. Maps each system's Source Name → Source_System_Id
  3. Updates the IDP CSV with the correct IDs
  4. Prints Cypher to update systemId on existing graph nodes

Usage (from notebook in src/):
    %run data_cleaning_utils/fix_system_ids.py
"""

import pandas as pd
import json
import os

# ── Paths ──────────────────────────────────────────────────────────────────
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data")
except NameError:
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")

SP_PATH = os.path.join(DATA_DIR, "Source System Repository from Sharepoint.csv")
IDP_PATH = os.path.join(DATA_DIR, "Source_System_from_IDP.csv")


def clean_source_name(name):
    """Strip '-Prod' suffix and trailing whitespace from Source Name."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    for suffix in ["-Prod", " -Prod"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip()


def main():
    sp = pd.read_csv(SP_PATH)
    idp = pd.read_csv(IDP_PATH)

    # ── 1. Find Sharepoint rows with blank DataSystem.name ─────────────────
    sp["DataSystem.name"] = sp["DataSystem.name"].astype(str).str.strip().str.replace(r'\n|\r', '', regex=True)
    blank_mask = sp["DataSystem.name"].isna() | sp["DataSystem.name"].astype(str).str.strip().isin(["", "nan"])
    sp_blank = sp[blank_mask].copy()

    # ── 2. Build mapping: clean Source Name → Source_System_Id ─────────────
    sp_blank["clean_name"] = sp_blank["Source Name"].apply(clean_source_name)
    # Deduplicate — keep first Source_System_Id per clean name
    sp_blank_dedup = sp_blank.drop_duplicates(subset="clean_name", keep="first")
    name_to_sp_id = dict(zip(sp_blank_dedup["clean_name"], sp_blank_dedup["Source_System_Id"]))

    print(f"Sharepoint name → Source_System_Id mapping ({len(name_to_sp_id)} entries):")
    for name, sp_id in sorted(name_to_sp_id.items(), key=lambda x: str(x[0])):
        print(f"  {name} → {sp_id}")

    # ── 3. Update IDP CSV ──────────────────────────────────────────────────
    updated_count = 0
    cypher_lines = []

    for idx, row in idp.iterrows():
        ds_name = str(row["DataSystem.name"]).strip()
        if ds_name in name_to_sp_id:
            old_id = row["DataSystem.Id"]
            new_id = name_to_sp_id[ds_name]

            # Skip if ID is already correct or Source_System_Id is NaN
            if pd.isna(new_id):
                print(f"  WARNING: No Source_System_Id for '{ds_name}', skipping.")
                continue

            new_id = int(new_id)
            if int(old_id) == new_id:
                continue

            idp.at[idx, "DataSystem.Id"] = new_id
            updated_count += 1
            print(f"  Updated: '{ds_name}' ID {int(old_id)} → {new_id}")

            # Build Cypher to fix the graph
            cypher_lines.append(
                f"MATCH (ds:DataSystem {{name: '{ds_name}'}}) SET ds.systemId = {new_id};"
            )

    # ── 4. Save updated IDP CSV ────────────────────────────────────────────
    idp.to_csv(IDP_PATH, index=False)
    print(f"\nUpdated {updated_count} IDs in IDP CSV.")
    print(f"Saved to: {IDP_PATH}")

    # ── 5. Print Cypher to update the graph ────────────────────────────────
    if cypher_lines:
        print("\n=== Run this Cypher to update the graph ===")
        for line in cypher_lines:
            print(line)


if __name__ == "__main__":
    main()
