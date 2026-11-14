"""Quick verification: check for duplicate rows, columns, and IDs in IDP CSV."""
import pandas as pd
import os

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data")
except NameError:
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")

idp = pd.read_csv(os.path.join(DATA_DIR, "Source_System_from_IDP.csv"))

print(f"Total rows: {len(idp)}")
print(f"Unique DataSystem.name: {idp['DataSystem.name'].nunique()}")
print(f"Columns ({len(idp.columns)}): {list(idp.columns)}")

# Check for _x/_y duplicate columns
bad_cols = [c for c in idp.columns if c.endswith("_x") or c.endswith("_y")]
if bad_cols:
    print(f"\nWARNING: _x/_y columns found: {bad_cols}")
else:
    print("\nNo _x/_y duplicate columns.")

# Check for duplicate DataSystem.name
dupes = idp[idp.duplicated(subset="DataSystem.name", keep=False)]
if len(dupes):
    print(f"\nDuplicate DataSystem.name ({len(dupes)} rows):")
    for name in sorted(dupes["DataSystem.name"].unique()):
        rows = idp[idp["DataSystem.name"] == name]
        print(f"  '{name}': IDs = {list(rows['DataSystem.Id'])}")
else:
    print("No duplicate DataSystem.name values.")

# Check for duplicate DataSystem.Id
id_dupes = idp[idp.duplicated(subset="DataSystem.Id", keep=False)]
if len(id_dupes):
    print(f"\nDuplicate DataSystem.Id ({len(id_dupes)} rows):")
    for sid in sorted(id_dupes["DataSystem.Id"].unique()):
        rows = idp[idp["DataSystem.Id"] == sid]
        print(f"  ID {int(sid)}: names = {list(rows['DataSystem.name'])}")
else:
    print("No duplicate DataSystem.Id values.")
