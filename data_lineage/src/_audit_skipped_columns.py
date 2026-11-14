"""
Investigate what columns the skipped STTM files actually have in their 'DD & STTM' sheet.
Identifies which required columns are missing and what columns exist instead.
Outputs results to Data/skipped_sttm_columns_audit.xlsx
"""

import glob
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STTM_DIR = os.path.join(PROJECT_ROOT, "Data", "sttms")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "Data", "skipped_sttm_columns_audit.xlsx")

STTM_SHEET = "DD & STTM"

# Current required columns
REQUIRED_COLUMNS = {
    "Silver Layer Object Type",
    "Physical Table Name",
    "Silver Layer Field Name",
    "Data Type",
    "Keys",
    "Definition",
    "Source",
    "Source Table Name",
    "Source Field Name",
    "Source Data Type",
    "Transformations",
}

# Columns needed strictly for lineage extraction
LINEAGE_CRITICAL = {
    "Physical Table Name",
    "Source Table Name",
    "Silver Layer Field Name",
    "Source Field Name",
}


def main():
    sttm_files = sorted(glob.glob(os.path.join(STTM_DIR, "*.xlsx")))
    print(f"Scanning {len(sttm_files)} STTM files...\n")

    records = []
    # Track which missing columns are most common
    missing_col_counts = {}

    for filepath in sttm_files:
        filename = os.path.basename(filepath)
        try:
            xl = pd.ExcelFile(filepath)
        except Exception:
            continue

        # Only look at files that HAVE the DD & STTM sheet but are missing columns
        if STTM_SHEET not in xl.sheet_names:
            continue

        df = pd.read_excel(filepath, sheet_name=STTM_SHEET, nrows=0)
        actual_cols = set(df.columns)
        missing = REQUIRED_COLUMNS - actual_cols

        if not missing:
            continue  # This file passes validation, skip

        # Check if lineage-critical columns are present
        lineage_missing = LINEAGE_CRITICAL - actual_cols
        has_lineage_cols = len(lineage_missing) == 0

        for col in missing:
            missing_col_counts[col] = missing_col_counts.get(col, 0) + 1

        records.append({
            "filename": filename,
            "missing_columns": "; ".join(sorted(missing)),
            "missing_count": len(missing),
            "has_lineage_critical": has_lineage_cols,
            "lineage_cols_missing": "; ".join(sorted(lineage_missing)) if lineage_missing else "",
            "actual_columns": "; ".join(sorted(actual_cols)),
            "actual_col_count": len(actual_cols),
        })

    df_results = pd.DataFrame(records)

    # Summary: which columns are missing most often
    df_missing_summary = pd.DataFrame([
        {"missing_column": col, "files_affected": count}
        for col, count in sorted(missing_col_counts.items(), key=lambda x: -x[1])
    ])

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        df_results.to_excel(writer, sheet_name="skipped_files", index=False)
        df_missing_summary.to_excel(writer, sheet_name="missing_col_summary", index=False)

    print(f"Files with DD & STTM sheet but missing columns: {len(df_results)}")
    print(f"\nMost commonly missing columns:")
    for _, row in df_missing_summary.iterrows():
        print(f"  {row['missing_column']}: {row['files_affected']} file(s)")

    # How many would be unlocked if we relax Silver Layer Object Type?
    if not df_results.empty:
        has_lineage = df_results[df_results["has_lineage_critical"] == True]
        print(f"\nFiles that HAVE all lineage-critical columns: {len(has_lineage)} / {len(df_results)}")
        print(f"  (These would be unlocked by relaxing non-critical column requirements)")

        only_missing_object_type = df_results[df_results["missing_columns"] == "Silver Layer Object Type"]
        print(f"\nFiles missing ONLY 'Silver Layer Object Type': {len(only_missing_object_type)}")

    print(f"\nAudit saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
