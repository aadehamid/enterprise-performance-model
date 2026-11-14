"""
Audit all STTM files in Data/sttms/ for extra sheets beyond the two known ones.

Produces Data/sttm_sheets_audit.xlsx with three tabs:
  1. extra_sheets   — files that have sheets beyond 'DD & STTM' and 'Silver Layer Object List'
  2. all_sheets     — complete inventory of every sheet in every file
  3. summary        — per-file overview: total sheets, extra count, list of extra names

Usage:
    python src/audit_sttm_sheets.py
"""

import glob
import os
import pandas as pd

# ── Path resolution ───────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STTM_DIR = os.path.join(PROJECT_ROOT, "Data", "sttms")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "Data", "sttm_sheets_audit.xlsx")

# Known/expected sheets
KNOWN_SHEETS = {"DD & STTM", "Silver Layer Object List"}


def main():
    sttm_files = sorted(glob.glob(os.path.join(STTM_DIR, "*.xlsx")))
    print(f"Scanning {len(sttm_files)} STTM file(s) in {STTM_DIR}...\n")

    # Collect records for each tab
    all_sheets_records = []
    extra_sheets_records = []
    summary_records = []
    errors = []

    for filepath in sttm_files:
        filename = os.path.basename(filepath)
        try:
            xl = pd.ExcelFile(filepath)
        except Exception as e:
            errors.append({"filename": filename, "error": str(e)})
            continue

        sheet_names = xl.sheet_names
        extra = [s for s in sheet_names if s not in KNOWN_SHEETS]

        # All sheets inventory
        for sheet in sheet_names:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet, nrows=0)
                col_count = len(df.columns)
            except Exception:
                col_count = None
            try:
                df_full = pd.read_excel(filepath, sheet_name=sheet)
                row_count = len(df_full)
            except Exception:
                row_count = None

            all_sheets_records.append({
                "filename": filename,
                "sheet_name": sheet,
                "is_known": sheet in KNOWN_SHEETS,
                "row_count": row_count,
                "col_count": col_count,
            })

        # Extra sheets only
        for sheet in extra:
            try:
                df_full = pd.read_excel(filepath, sheet_name=sheet)
                row_count = len(df_full)
                col_count = len(df_full.columns)
                columns = ", ".join(df_full.columns.tolist()[:10])
                if len(df_full.columns) > 10:
                    columns += f" ... (+{len(df_full.columns) - 10} more)"
            except Exception:
                row_count = None
                col_count = None
                columns = "ERROR reading sheet"

            extra_sheets_records.append({
                "filename": filename,
                "extra_sheet_name": sheet,
                "row_count": row_count,
                "col_count": col_count,
                "sample_columns": columns,
            })

        # Summary per file
        summary_records.append({
            "filename": filename,
            "total_sheets": len(sheet_names),
            "known_sheets": len([s for s in sheet_names if s in KNOWN_SHEETS]),
            "extra_sheet_count": len(extra),
            "extra_sheet_names": "; ".join(extra) if extra else "",
        })

    # Build DataFrames
    df_all = pd.DataFrame(all_sheets_records)
    df_extra = pd.DataFrame(extra_sheets_records)
    df_summary = pd.DataFrame(summary_records)

    # Write to Excel with multiple tabs
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        df_extra.to_excel(writer, sheet_name="extra_sheets", index=False)
        df_summary.to_excel(writer, sheet_name="summary", index=False)
        df_all.to_excel(writer, sheet_name="all_sheets", index=False)

    # Console summary
    files_with_extras = df_summary[df_summary["extra_sheet_count"] > 0]
    print(f"Total files scanned:        {len(sttm_files)}")
    print(f"Files with extra sheets:    {len(files_with_extras)}")
    print(f"Total extra sheets found:   {len(df_extra)}")
    if errors:
        print(f"Files with read errors:     {len(errors)}")
        for e in errors:
            print(f"  ERROR {e['filename']}: {e['error']}")
    print(f"\nAudit saved to: {OUTPUT_PATH}")

    # Show top 10 most common extra sheet names
    if not df_extra.empty:
        print("\nTop extra sheet names:")
        top = df_extra["extra_sheet_name"].value_counts().head(10)
        for name, count in top.items():
            print(f"  {name}: {count} file(s)")


if __name__ == "__main__":
    main()
