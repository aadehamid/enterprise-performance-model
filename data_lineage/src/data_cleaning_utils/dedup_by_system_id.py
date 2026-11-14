"""
Deduplicate IDP CSV rows that share the same DataSystem.Id.

For each group of rows with the same ID, keeps the row with the most
non-null attribute values. Removes the others.

Also prints which rows were removed so you can verify and clean up
the corresponding graph nodes.

Usage:
    %run data_cleaning_utils/dedup_by_system_id.py
"""

import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────────────────────────
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data")
except NameError:
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")

IDP_PATH = os.path.join(DATA_DIR, "Source_System_from_IDP.csv")

# Attribute columns used to determine which row is "most populated"
ATTR_COLUMNS = [
    "applicationService",
    "confidentialityClassification",
    "isSoxRelevant",
    "dataModality",
    "applicationType",
    "purviewReplicaSchemaName",
    "purviewSourceTypeAssetLink",
    "ingestionMethod",
    "refreshFrequency",
]


def main():
    idp = pd.read_csv(IDP_PATH)
    print(f"IDP rows (before): {len(idp)}")

    # ── 1. Find duplicate DataSystem.Id groups ─────────────────────────────
    id_dupes = idp[idp.duplicated(subset="DataSystem.Id", keep=False)]
    dupe_ids = sorted(id_dupes["DataSystem.Id"].unique())

    if not len(dupe_ids):
        print("No duplicate DataSystem.Id values. Nothing to do.")
        return

    print(f"\nFound {len(dupe_ids)} duplicate DataSystem.Id groups ({len(id_dupes)} total rows):")

    # ── 2. For each group, pick the best row (most non-null attrs) ─────────
    rows_to_drop = []
    drop_details = []  # For Cypher cleanup output

    for sid in dupe_ids:
        group = idp[idp["DataSystem.Id"] == sid].copy()

        # Count non-null attributes for each row
        group["_attr_count"] = group[ATTR_COLUMNS].notna().sum(axis=1)

        # Sort: most attributes first, then alphabetical name as tiebreaker
        group = group.sort_values(["_attr_count", "DataSystem.name"], ascending=[False, True])

        keep_row = group.iloc[0]
        remove_rows = group.iloc[1:]

        print(f"\n  ID {int(sid)}:")
        print(f"    KEEP:   '{keep_row['DataSystem.name']}' ({int(keep_row['_attr_count'])} attrs, BA: {keep_row['BuisnessArea']})")
        for _, rr in remove_rows.iterrows():
            print(f"    REMOVE: '{rr['DataSystem.name']}' ({int(rr['_attr_count'])} attrs, BA: {rr['BuisnessArea']})")
            rows_to_drop.append(rr.name)  # pandas index
            drop_details.append(rr["DataSystem.name"])

    # ── 3. Drop the duplicate rows ────────────────────────────────────────
    idp_clean = idp.drop(index=rows_to_drop)
    print(f"\nDropped {len(rows_to_drop)} duplicate rows.")
    print(f"IDP rows (after): {len(idp_clean)}")

    # ── 4. Save ───────────────────────────────────────────────────────────
    idp_clean.to_csv(IDP_PATH, index=False)
    print(f"Saved to: {IDP_PATH}")

    # ── 5. Print Cypher to remove stale graph nodes ───────────────────────
    if drop_details:
        print("\n=== Run this Cypher to remove stale nodes from the graph ===")
        names_str = ", ".join([f"'{n}'" for n in drop_details])
        print(f"MATCH (ds:DataSystem) WHERE ds.name IN [{names_str}]")
        print("DETACH DELETE ds;")


if __name__ == "__main__":
    main()
