"""
Merge Sharepoint source system attributes into the IDP CSV.

Two-pass merge (idempotent — safe to re-run on already-enriched CSV):
  Pass 1: Match on DataSystem.name (with manual name mapping for mismatches).
  Pass 2: For Sharepoint rows with blank DataSystem.name, match clean(Source Name)
           against IDP DataSystem.name to catch systems like Experian and Saviynt.

Excludes APS rows from Sharepoint (already handled in Step 6 of 2_load_data.cypher).
Deduplicates Sharepoint rows by DataSystem.name / Source Name (keeps first occurrence).
Drops any previously-merged columns before re-merging to avoid _x/_y duplicates.
Saves enriched IDP CSV to Data/Source_System_from_IDP.csv (overwrites).

Usage:
    python src/data_cleaning_utils/merge_sharepoint_into_idp.py

    Or run from a Jupyter notebook:
        %run data_cleaning_utils/merge_sharepoint_into_idp.py
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

# ── Manual name mapping: Sharepoint name → IDP name (IDP is truth) ────────
# Update this dict when new mismatches are discovered.
SP_TO_IDP_NAME_MAP = {
    "Asphalt 2.0":      "Asphalt Suite",
    "CDR":              "CrossReference",
    "CLM":              "Sirion",
    "COS":              "COSDB",
    "LTPF":             "MIPS-LTPF",
    "MDH":              "Marketing_Datahub",
    "MPIS":             "MIPS",
    "PBI":              "Power BI System DB",
    "PIBI":             "PIBI_Refining",
    "Refining OLAP":    "Refining_OLAP",
    "SAP BW HANA":      "SAP BW",
    "SAP S4":           "SAP_S4",
    "SBN, ePermitting": "SBN-Midstream-L&S",
    "SNOW":             "ServiceNow",
}

# ── Columns to merge from Sharepoint into IDP ─────────────────────────────
MERGE_COLUMNS = [
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


def clean_source_name(name):
    """Strip '-Prod' suffix and trailing whitespace from Source Name."""
    if pd.isna(name):
        return None
    name = str(name).strip()
    for suffix in ["-Prod", " -Prod"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip()


def parse_business_area(raw_value):
    """Parse BusinessArea from JSON list string, e.g. '["Commercial"]' → 'Commercial'.
    
    Returns the raw string (possibly JSON list) for downstream handling.
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
    print(f"IDP rows: {len(idp)}")
    print(f"Sharepoint rows (raw): {len(sp)}")

    # ── 2. Idempotency: drop previously-merged columns if they exist ──────
    #    This prevents _x/_y suffix conflicts on re-run.
    existing_merge_cols = [c for c in MERGE_COLUMNS if c in idp.columns]
    if existing_merge_cols:
        idp.drop(columns=existing_merge_cols, inplace=True)
        print(f"Dropped {len(existing_merge_cols)} existing enriched columns for clean re-merge")

    # ── 3. Clean DataSystem.name in both ───────────────────────────────────
    sp["DataSystem.name"] = sp["DataSystem.name"].astype(str).str.strip().str.replace(r'\n|\r', '', regex=True)
    idp["DataSystem.name"] = idp["DataSystem.name"].astype(str).str.strip()

    # ── 4. Exclude APS rows from Sharepoint ────────────────────────────────
    sp = sp[sp["DataSystem.name"] != "APS"].copy()
    print(f"Sharepoint rows (after excluding APS): {len(sp)}")

    # ── 5. Apply name mapping so Sharepoint names align with IDP ───────────
    sp["DataSystem.name"] = sp["DataSystem.name"].replace(SP_TO_IDP_NAME_MAP)

    # ── 6. Deduplicate Sharepoint by DataSystem.name (keep first) ──────────
    #    Many SP rows are per-schema; we only need system-level attributes.
    sp_dedup = sp.drop_duplicates(subset="DataSystem.name", keep="first")
    print(f"Sharepoint rows (after dedup): {len(sp_dedup)}")

    # ── 7. Select only the columns we want to merge ────────────────────────
    sp_subset = sp_dedup[["DataSystem.name"] + MERGE_COLUMNS].copy()

    # ── 8. Diagnostic: show matches and misses ─────────────────────────────
    sp_names = set(sp_subset["DataSystem.name"].dropna()) - {"nan", ""}
    idp_names = set(idp["DataSystem.name"].dropna()) - {"nan", ""}
    matched = sp_names & idp_names
    unmatched_sp = sorted(sp_names - idp_names)

    print(f"\nPass 1 matched systems: {len(matched)}")
    if unmatched_sp:
        print(f"Unmatched Sharepoint names (no IDP match): {unmatched_sp}")
        print("  → Add these to SP_TO_IDP_NAME_MAP if a match exists in IDP.")

    # ── 9. Left join: IDP ← Sharepoint on DataSystem.name ─────────────────
    idp_enriched = idp.merge(sp_subset, on="DataSystem.name", how="left")

    # ── 10. Report Pass 1 results ─────────────────────────────────────────
    enriched_count = idp_enriched[MERGE_COLUMNS].notna().any(axis=1).sum()
    print(f"Pass 1 enriched: {enriched_count} / {len(idp_enriched)}")

    # ══════════════════════════════════════════════════════════════════════
    # PASS 2: Sharepoint rows with blank DataSystem.name → match by Source Name
    # This catches systems like Experian and Saviynt where Sharepoint has
    # attributes but DataSystem.name was left blank.
    # ══════════════════════════════════════════════════════════════════════
    print("\n--- Pass 2: matching blank DataSystem.name rows by Source Name ---")

    # Re-read original Sharepoint (Pass 1 modified sp in memory)
    sp2 = pd.read_csv(SP_PATH)
    sp2["DataSystem.name"] = sp2["DataSystem.name"].astype(str).str.strip().str.replace(r'\n|\r', '', regex=True)

    # Filter to rows with blank DataSystem.name
    blank_mask = sp2["DataSystem.name"].isna() | sp2["DataSystem.name"].isin(["", "nan"])
    sp_blank = sp2[blank_mask].copy()

    # Clean Source Name for matching
    sp_blank["clean_name"] = sp_blank["Source Name"].apply(clean_source_name)

    # Deduplicate by clean_name (keep first)
    sp_blank = sp_blank.drop_duplicates(subset="clean_name", keep="first")
    print(f"Sharepoint rows with blank DataSystem.name (deduped): {len(sp_blank)}")

    # Find matches against IDP names
    idp_name_set = set(idp_enriched["DataSystem.name"].astype(str).str.strip())
    pass2_matches = sp_blank[sp_blank["clean_name"].isin(idp_name_set)].copy()
    print(f"Pass 2 matches (Source Name → IDP name): {len(pass2_matches)}")

    # Apply attributes to matching IDP rows
    pass2_count = 0
    for _, sp_row in pass2_matches.iterrows():
        idp_name = sp_row["clean_name"]
        idp_mask = idp_enriched["DataSystem.name"].astype(str).str.strip() == idp_name

        # Update attributes: only fill where IDP currently has no value
        for col in MERGE_COLUMNS:
            sp_val = sp_row.get(col)
            if pd.notna(sp_val):
                idp_enriched.loc[idp_mask & idp_enriched[col].isna(), col] = sp_val

        # Update BusinessArea: append Sharepoint BA if different from existing
        sp_ba = parse_business_area(sp_row.get("BusinessArea"))
        if sp_ba:
            for idx in idp_enriched.index[idp_mask]:
                existing_ba = str(idp_enriched.at[idx, "BuisnessArea"]).strip()
                if existing_ba != sp_ba:
                    if existing_ba.startswith("["):
                        try:
                            ba_list = json.loads(existing_ba)
                        except json.JSONDecodeError:
                            ba_list = [existing_ba]
                    else:
                        ba_list = [existing_ba]
                    if sp_ba not in ba_list:
                        ba_list.append(sp_ba)
                        idp_enriched.at[idx, "BuisnessArea"] = json.dumps(ba_list)

        pass2_count += 1
        print(f"  Updated: {idp_name} (BA: {sp_ba})")

    print(f"Pass 2 enriched: {pass2_count} systems")

    # ── Final report ──────────────────────────────────────────────────────
    total_enriched = idp_enriched[MERGE_COLUMNS].notna().any(axis=1).sum()
    print(f"\nTotal IDP rows with Sharepoint data: {total_enriched} / {len(idp_enriched)}")

    idp_enriched["isSoxRelevant"] = idp_enriched["isSoxRelevant"].map(flag_bool)

    # ── Save ──────────────────────────────────────────────────────────────
    idp_enriched.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved enriched IDP CSV to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
