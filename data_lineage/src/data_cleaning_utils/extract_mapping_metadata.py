"""
Extract schema, table, and report metadata from the Phase 3 Reports Full Data Mapping Excel.

Reads the 'Full Mapping' sheet and produces three clean CSVs:
  1. Data/schemas.csv         — unique schemas with layer, role, ownership
  2. Data/tables.csv          — unique tables with schema, layer, dimensional role
  3. Data/reports.csv         — unique reports with connectionType and CDD

These CSVs feed the Neo4j loader scripts (load_schemas.py, load_tables.py, etc.).

Multi-value cells (newline-separated) are split into individual rows.

Usage:
    python src/data_cleaning_utils/extract_mapping_metadata.py
"""

import os
import re
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from excel_cells import split_multivalue
from medallion import is_legacy, is_legacy_schema, schema_layer

# ── Path resolution ────────────────────────────────────────────────────────
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
EXCEL_PATH = os.path.join(DATA_DIR, "Phase 3 Reports Full Data Mapping.xlsx")
SHEET_NAME = "Full Mapping"

# ── Output paths ───────────────────────────────────────────────────────────
SCHEMAS_CSV = os.path.join(DATA_DIR, "schemas.csv")
TABLES_CSV = os.path.join(DATA_DIR, "tables.csv")
REPORTS_CSV = os.path.join(DATA_DIR, "reports.csv")

# ── CDD name mapping (file abbreviation → graph canonical name) ────────────
CDD_NAME_MAP = {
    "Logistic Execution": "Logistics Execution",
    "External Marketing Data": "External Market Data",
    "Local Production Planning": "Local Production Planning & Crude Scheduling",
    "Regional Production": "Regional Production & Distribution Planning",
}

def infer_role(schema_name):
    """Determine the functional role of a schema."""
    if schema_name == "udm_core":
        return "Facts"
    if schema_name == "mdm_core":
        return "Dimensions"
    if schema_name == "sem_masterdata":
        return "Master Data"
    return None


def infer_business_area(schema_name):
    """Extract the BusinessArea from a Gold/Semantic schema name.

    Returns the BA name or None if not applicable.
    Gold pattern:  <ba>_core       → ba (title-cased)
    Semantic:      sem_<ba>        → ba (title-cased)
    Special:       replica_files_commercial → Commercial (flat file ingestion)
    """
    if is_legacy_schema(schema_name):
        # sem_comm_kh_mpc_rstd maps to Commercial
        if schema_name == "sem_comm_kh_mpc_rstd":
            return "Commercial"
        return None
    # replica_files_commercial is a flat-file ingestion schema for Commercial
    if schema_name == "replica_files_commercial":
        return "Commercial"
    if schema_name == "sem_masterdata":
        return None  # cross-cutting
    if schema_name.startswith("sem_"):
        ba = schema_name.replace("sem_", "")
        return ba.replace("_", " ").title()
    if schema_name.endswith("_core") and not schema_name.startswith("replica_"):
        if schema_name in ("udm_core", "mdm_core", "dwh_core"):
            return None
        ba = schema_name.replace("_core", "")
        return ba.replace("_", " ").title()
    return None


def infer_dimensional_role(table_name, schema_name):
    """Determine the dimensional role label from a table name.

    Rules (order matters):
      1. Semantic schema objects are always View (they expose data for reports)
      2. _vw, _Vw, _VW suffix → View
      3. _Fact or _Fact_ → Fact
      4. _Dim or _Dim_ or _Xref → Dimension
      5. Fallback → Table (plain replica or unclassified)
    """
    # Semantic schema objects are views by convention, regardless of name
    if schema_name.startswith("sem_"):
        return "View"
    lower = table_name.lower()
    if lower.endswith("_vw") or "_vw_" in lower or lower.endswith("_vw "):
        return "View"
    if "_fact" in lower:
        return "Fact"
    if "_dim" in lower or "_xref" in lower:
        return "Dimension"
    return "Table"


def parse_qualified_name(qualified_name):
    """Split 'schema.table' into (schema, table). Returns (None, None) if no dot."""
    if "." not in qualified_name:
        return None, qualified_name
    schema, table = qualified_name.split(".", 1)
    return schema.strip(), table.strip()


def connection_type_from_datasystem(ds_name):
    """Map DataSystem.name or Live Report or Connected to IDP? to a connectionType value."""
    mapping = {
        "Insight and Discovery Platform (IDP)": "IDP",
        "IDP": "IDP",
        "Live": "Live",
        "Excel": "FlatFile",
        "Data Armory": "DataArmory",
    }
    return mapping.get(str(ds_name).strip(), "Unknown")


def extract_schemas(df):
    """Extract all unique schemas from all three table columns.

    Returns a DataFrame with columns:
      qualifiedName, layer, role, businessArea, isCrossCutting, refactorTarget
    """
    all_schemas = set()

    # Column: Semantic View / Direct Table Connection
    for val in df["Semantic View / Direct Table Connection"].dropna():
        for item in split_multivalue(val):
            schema, _ = parse_qualified_name(item)
            if schema:
                all_schemas.add(schema)

    # Column: UDM Table
    for val in df["UDM Table"].dropna():
        for item in split_multivalue(val):
            if "No Insight" in item:
                continue
            schema, _ = parse_qualified_name(item)
            if schema:
                all_schemas.add(schema)

    # Column: IDP Replica Entities
    for val in df["IDP Replica Entities"].dropna():
        for item in split_multivalue(val):
            if "No Insight" in item:
                continue
            schema, _ = parse_qualified_name(item)
            if schema:
                all_schemas.add(schema)

    # Build schema records
    records = []
    for s in sorted(all_schemas):
        legacy = is_legacy_schema(s)
        # replica_files_commercial contains flat files injected into Replica layer
        source_type = "FlatFile" if s == "replica_files_commercial" else None
        records.append({
            "qualifiedName": s,
            "layer": schema_layer(s) or "Unknown",
            "legacy": legacy,
            "role": infer_role(s),
            "businessArea": infer_business_area(s),
            "sourceType": source_type,
            "isCrossCutting": s == "sem_masterdata",
            "refactorTarget": "Medallion" if legacy else None,
        })

    return pd.DataFrame(records)


def extract_tables(df):
    """Extract all unique tables from all three table columns.

    Returns a DataFrame with columns:
      qualifiedName, name, schema, layer, dimensionalRole
    """
    all_tables = {}  # qualifiedName → record dict

    def add_table(qualified_name):
        """Parse and register a table."""
        schema, table = parse_qualified_name(qualified_name)
        if not schema:
            return  # skip non-schema values like 'Excel'
        qn = f"{schema}.{table}"
        if qn not in all_tables:
            layer = schema_layer(schema) or "Unknown"
            all_tables[qn] = {
                "qualifiedName": qn,
                "name": table,
                "schema": schema,
                "layer": layer,
                "legacy": is_legacy(qn, layer),
                "dimensionalRole": infer_dimensional_role(table, schema),
            }

    # Semantic views
    for val in df["Semantic View / Direct Table Connection"].dropna():
        for item in split_multivalue(val):
            if "." in item:
                add_table(item)

    # Gold/Silver tables
    for val in df["UDM Table"].dropna():
        for item in split_multivalue(val):
            if "No Insight" in item:
                continue
            if "." in item:
                add_table(item)

    # Replica/source tables
    for val in df["IDP Replica Entities"].dropna():
        for item in split_multivalue(val):
            if "No Insight" in item:
                continue
            if "." in item:
                add_table(item)

    return pd.DataFrame(list(all_tables.values()))


def extract_reports(df):
    """Extract unique reports with their connectionType and CDD.

    Returns a DataFrame with columns:
      name, connectionType, capabilityDataDomain
    """
    records = {}
    EXCLUDED_PORTFOLIOS = {"IT", "Legal", "Finance", "ES&S"}
    
    for _, row in df.iterrows():
        report_name = str(row["Report"]).strip()
        if pd.isna(row["Report"]) or not report_name or report_name.lower() == "nan":
            continue

        conn_type = connection_type_from_datasystem(row.get("Live Report or Connected to IDP?"))
        
        cdd_raw = str(row.get("Data Portfolio", "")).strip()
        if cdd_raw in EXCLUDED_PORTFOLIOS or cdd_raw.lower() == "nan" or not cdd_raw:
            cdd = ""
        else:
            cdd = CDD_NAME_MAP.get(cdd_raw, cdd_raw)

        # A report may appear in multiple rows (one per semantic view consumed).
        # Keep the first connectionType seen; collect all CDDs.
        if report_name not in records:
            records[report_name] = {
                "name": report_name,
                "connectionType": conn_type,
                "capabilityDataDomains": {cdd} if cdd else set(),
            }
        else:
            if cdd:
                records[report_name]["capabilityDataDomains"].add(cdd)

    # Flatten CDDs to pipe-separated string for CSV
    result = []
    for r in records.values():
        result.append({
            "name": r["name"],
            "connectionType": r["connectionType"],
            "capabilityDataDomain": "|".join(sorted(r["capabilityDataDomains"])),
        })

    return pd.DataFrame(result)


def main():
    print(f"Reading: {EXCEL_PATH}")
    print(f"Sheet:   {SHEET_NAME}")

    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    print(f"Rows:    {len(df)}")

    # ── Extract schemas ────────────────────────────────────────────────────
    schemas_df = extract_schemas(df)
    schemas_df.to_csv(SCHEMAS_CSV, index=False)
    print(f"\nSchemas: {len(schemas_df)} unique -> {SCHEMAS_CSV}")
    print(schemas_df.to_string(index=False))

    # ── Extract tables ─────────────────────────────────────────────────────
    tables_df = extract_tables(df)
    tables_df.to_csv(TABLES_CSV, index=False)
    print(f"\nTables:  {len(tables_df)} unique -> {TABLES_CSV}")
    print(f"  By layer: {tables_df['layer'].value_counts().to_dict()}")
    print(f"  By role:  {tables_df['dimensionalRole'].value_counts().to_dict()}")

    # ── Extract reports ────────────────────────────────────────────────────
    reports_df = extract_reports(df)
    reports_df.to_csv(REPORTS_CSV, index=False)
    print(f"\nReports: {len(reports_df)} unique -> {REPORTS_CSV}")
    print(f"  By connectionType: {reports_df['connectionType'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
