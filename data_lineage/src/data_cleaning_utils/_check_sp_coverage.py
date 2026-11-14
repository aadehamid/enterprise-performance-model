"""Check which Sharepoint systems are NOT present in the IDP CSV."""
import pandas as pd
import os

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..", "Data")
except NameError:
    DATA_DIR = os.path.join(os.getcwd(), "..", "Data")

SP_PATH = os.path.join(DATA_DIR, "Source System Repository from Sharepoint.csv")
IDP_PATH = os.path.join(DATA_DIR, "Source_System_from_IDP.csv")

# Same mapping used in merge script
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

# ── Read CSVs ──────────────────────────────────────────────────────────────
sp = pd.read_csv(SP_PATH)
idp = pd.read_csv(IDP_PATH)

idp_names = set(idp["DataSystem.name"].dropna().astype(str).str.strip())

# ── Pass 1: Named Sharepoint systems (excluding APS) ──────────────────────
sp_named = sp.copy()
sp_named["DataSystem.name"] = sp_named["DataSystem.name"].astype(str).str.strip().str.replace(r'\n|\r', '', regex=True)

# Exclude APS and blank
sp_named = sp_named[~sp_named["DataSystem.name"].isin(["APS", "", "nan"])]
sp_named["DataSystem.name"] = sp_named["DataSystem.name"].replace(SP_TO_IDP_NAME_MAP)
sp_named_dedup = sp_named.drop_duplicates(subset="DataSystem.name", keep="first")

named_set = set(sp_named_dedup["DataSystem.name"].dropna())
missing_named = sorted(named_set - idp_names)

print(f"=== Sharepoint systems with DataSystem.name (non-APS, deduped): {len(named_set)} ===")
print(f"Present in IDP: {len(named_set - set(missing_named))}")
if missing_named:
    print(f"MISSING from IDP ({len(missing_named)}):")
    for name in missing_named:
        print(f"  - {name}")
else:
    print("All present in IDP. ✓")

# ── Pass 2: Blank DataSystem.name (by Source Name) ────────────────────────
blank_mask = sp["DataSystem.name"].isna()
str_col = sp["DataSystem.name"].astype(str).str.strip().str.replace(r'\n|\r', '', regex=True)
blank_mask = blank_mask | str_col.isin(["", "nan"])
sp_blank = sp[blank_mask].copy()

def clean_source_name(name):
    if pd.isna(name):
        return None
    name = str(name).strip()
    for suffix in ["-Prod", " -Prod"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.strip()

sp_blank["clean_name"] = sp_blank["Source Name"].apply(clean_source_name)
sp_blank_dedup = sp_blank.drop_duplicates(subset="clean_name", keep="first")

blank_set = set(sp_blank_dedup["clean_name"].dropna())
missing_blank = sorted(blank_set - idp_names)

print(f"\n=== Sharepoint systems with blank DataSystem.name (by Source Name, deduped): {len(blank_set)} ===")
print(f"Present in IDP: {len(blank_set - set(missing_blank))}")
if missing_blank:
    print(f"MISSING from IDP ({len(missing_blank)}):")
    for name in missing_blank:
        print(f"  - {name}")
else:
    print("All present in IDP. ✓")

# ── Summary ───────────────────────────────────────────────────────────────
total_missing = len(missing_named) + len(missing_blank)
print(f"\n=== TOTAL: {total_missing} Sharepoint systems not in IDP ===")
