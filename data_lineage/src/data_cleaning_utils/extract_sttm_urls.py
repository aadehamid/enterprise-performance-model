"""
Extract hyperlink URLs from the 'STTM Link' column in Phase 3 Reports Full Data Mapping.xlsx.

Adds a new column 'STTM URL' containing the raw URL that each 'STTM Link' cell
is hyperlinked to. Saves the file in place.

Uses openpyxl to read embedded hyperlinks (pandas cannot read these).

Usage (from notebook in src/):
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")
    %run data_cleaning_utils/extract_sttm_urls.py

Or from command line:
    python src/data_cleaning_utils/extract_sttm_urls.py

Prerequisites:
    pip install openpyxl
"""

import os
from openpyxl import load_workbook

# ── Paths ──────────────────────────────────────────────────────────────────
# Works both as a standalone script (__file__ available) and in a notebook (fallback to cwd)
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data")
except NameError:
    # Running in a Jupyter notebook
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")

EXCEL_PATH = os.path.join(DATA_DIR, "Phase 3 Reports Full Data Mapping.xlsx")


def find_column_index(header_row, column_name):
    """Find the 1-based column index for a given header name."""
    for idx, cell in enumerate(header_row, start=1):
        if cell.value and str(cell.value).strip() == column_name:
            return idx
    return None


def main():
    print(f"Loading workbook: {EXCEL_PATH}")
    wb = load_workbook(EXCEL_PATH)

    # Process each sheet in the workbook
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"\nProcessing sheet: '{sheet_name}' ({ws.max_row} rows, {ws.max_column} cols)")

        # ── 1. Find 'STTM Link' column in header row (row 1) ──────────────
        header_row = list(ws.iter_rows(min_row=1, max_row=1))[0]
        sttm_col = find_column_index(header_row, "STTM Link")

        if sttm_col is None:
            print(f"  'STTM Link' column not found in sheet '{sheet_name}', skipping.")
            continue

        print(f"  Found 'STTM Link' at column {sttm_col}")

        # ── 2. Find or create 'STTM URL' column ───────────────────────────
        sttm_url_col = find_column_index(header_row, "STTM URL")
        if sttm_url_col is None:
            # Add new column after the last column
            sttm_url_col = ws.max_column + 1
            ws.cell(row=1, column=sttm_url_col, value="STTM URL")
            print(f"  Created 'STTM URL' column at position {sttm_url_col}")
        else:
            print(f"  'STTM URL' column already exists at position {sttm_url_col}, updating.")

        # ── 3. Extract hyperlink URL from each 'STTM Link' cell ───────────
        url_count = 0
        for row_num in range(2, ws.max_row + 1):
            cell = ws.cell(row=row_num, column=sttm_col)
            url = None

            # Check for embedded hyperlink
            if cell.hyperlink and cell.hyperlink.target:
                url = cell.hyperlink.target
            # Fallback: if the cell value itself looks like a URL
            elif cell.value and str(cell.value).startswith("http"):
                url = str(cell.value)

            if url:
                ws.cell(row=row_num, column=sttm_url_col, value=url)
                url_count += 1

        print(f"  Extracted {url_count} URLs from {ws.max_row - 1} data rows")

    # ── 4. Save ────────────────────────────────────────────────────────────
    wb.save(EXCEL_PATH)
    print(f"\nSaved updated workbook to: {EXCEL_PATH}")


if __name__ == "__main__":
    main()
