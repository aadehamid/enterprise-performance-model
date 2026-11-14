"""
load_lineage.py — Load table-level DERIVED_FROM lineage into Neo4j.

Overview
--------
Phase 3 of the Medallion Architecture Knowledge Graph build. This script
creates (Table)-[:DERIVED_FROM]->(Table) relationships that trace data flow
from Replica tables through Silver/Gold layers up to Semantic views.

Data Flow (executed in order)
-----------------------------
1. Read the master mapping Excel ("Phase 3 Reports Full Data Mapping.xlsx").
   Each row may contain newline-separated lists of tables, producing cross-product
   DERIVED_FROM pairs.

2. Scan all STTM files in Data/sttms/ to extract ground-truth lineage.
   Two STTM formats are supported:
     a) **Standard DD & STTM** — most files. Contains a 'DD & STTM' sheet (or
        variant sheets like 'DD & STTM - Enverus_Wells'). The 'Source' and
        'Source Table Name' columns identify upstream tables.
     b) **Alteryx Table Mapping** — 7 files identified by having a 'Table Mapping'
        sheet (ExecutiveSummary, GulfCoast, InventoryFluctuation, LPSAPricingDisplay,
        New Industry Outages, Southwest Netbacks, ULSD Brand Decoupling). Contains
        columns for each medallion layer (Replica -> Silver -> Gold -> Semantic),
        producing multi-hop DERIVED_FROM chains. When the Semantic Layer column is
        null, a semantic QN is auto-generated as sem_commercial.<TableName>_vw.

3. Apply STTM overrides: for every table that has an STTM, remove the Excel
   cross-product pairs and replace with STTM-confirmed sources only.

4. Merge Alteryx multi-hop pairs (intermediate layer edges).

5. Create the full Alteryx provenance graph for tables that originated in the
   pre-IDP Alteryx Sandbox environment:
     a) Server nodes (e.g., MPR.prod.db.mgroupnet.com) → HOSTS → DataSystem
     b) Operational source Table nodes → CONTAINS under their DataSystem
     c) Operational source Table → REPLICATED_TO → IDP Replica Table
     d) Sandbox DataSystem nodes (e.g., "Commercial Analysis") with platform metadata
     e) Gold/Target Table → MIGRATED_FROM → Sandbox DataSystem
     f) Report → CONSUMES → Semantic View (if Report Name present)

6. Ensure all referenced Table nodes exist in Neo4j (auto-create stub nodes
   with sourceFile provenance for traceability).

7. Clear old DERIVED_FROM edges for overridden tables, then MERGE the final set.

Key Design Decisions
--------------------
- **Column-level provenance exclusion**: Values 'config' and 'ETL Generated' in
  the Source column are column-level provenance markers, not table-level sources.
  They are filtered out of table-level lineage but will be used later by the
  column-level lineage loader (load_sttm.py).

- **Name corrections**: STTM_NAME_CORRECTIONS maps known mismatched qualified
  names (e.g., 'udm_core.Enverus_Frac_Crews' → 'udm_core.Enverus_Frac_Crews_Fact')
  so lineage connects properly even when two STTMs use different names for the
  same table. Add new entries here when discovered.

- **Stub nodes**: Tables referenced in STTMs but not yet in the graph (e.g.,
  Replica tables loaded from external systems) are auto-created via MERGE with
  a sourceFile property recording which STTM file first referenced them.

- **Idempotent**: Safe to re-run. Uses MERGE for nodes and relationships;
  deletes old edges only for STTM-overridden tables before re-creating them.

Prerequisites
-------------
  - Run load_schemas.py and load_tables.py first (Schema + Table nodes must exist)
  - pip install neo4j pandas python-dotenv openpyxl

Usage
-----
    python src/load_lineage.py
"""

import glob
import os
import re
import pandas as pd
from excel_cells import pair_positional, split_multivalue
from medallion import (
    cypher_is_legacy_schema,
    cypher_schema_layer,
    is_legacy,
    schema_layer,
    stamp_report_keys,
)
from neo4j_loader import Neo4jLoader, canonicalize_server_name

# ── Path resolution ────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXCEL_PATH = os.path.join(PROJECT_ROOT, "Data", "Phase 3 Reports Full Data Mapping.xlsx")
SHEET_NAME = "Full Mapping"
STTM_DIR = os.path.join(PROJECT_ROOT, "Data", "sttms")
STTM_SHEET = "DD & STTM"

# Known/expected sheets in each STTM file
STTM_KNOWN_SHEETS = {"DD & STTM", "Silver Layer Object List"}

# Columns required for lineage extraction (must be present)
STTM_LINEAGE_CRITICAL = {
    "Physical Table Name",
    "Source Table Name",
    "Silver Layer Field Name",
    "Source Field Name",
}

# Columns that are useful metadata but not blocking for lineage
STTM_METADATA_COLUMNS = {
    "Silver Layer Object Type",
    "Data Type",
    "Keys",
    "Definition",
    "Source",
    "Source Data Type",
    "Transformations",
}

# Alias map: variant column names → canonical names
# Handles newline-separated headers, misspellings, and Gold layer equivalents
STTM_COLUMN_ALIASES = {
    "Silver Layer \n Object Type": "Silver Layer Object Type",
    "Silver Layer\nObject Type": "Silver Layer Object Type",
    "Silver Layer  Object Type": "Silver Layer Object Type",
    "Gold Layer \n Object Type": "Silver Layer Object Type",
    "Gold Layer\nObject Type": "Silver Layer Object Type",
    "Gold Layer Object Type": "Silver Layer Object Type",
    "Gold Layer Field Name": "Silver Layer Field Name",
    "Gold Layer \n Field Name": "Silver Layer Field Name",
    "Gold Layer\nField Name": "Silver Layer Field Name",
    "Defintion": "Definition",
}

# ── Alteryx-format STTM constants ─────────────────────────────────────────
# Alteryx STTMs use a different sheet structure: 'Table Mapping' + 'Field Mapping'
# instead of the standard 'DD & STTM' sheet. These are identified by the presence
# of a 'Table Mapping' (or 'Table mapping') sheet.
ALTERYX_TABLE_MAPPING_SHEETS = {"Table Mapping", "Table mapping"}

# Columns in the Alteryx 'Table Mapping' sheet that hold qualified table names
# at each medallion layer. Each row maps one source through intermediate layers
# to a final target, producing multi-hop DERIVED_FROM pairs.
#
# The Gold column has naming variants across files, so we list all known variants.
# At runtime, the first matching column name found in the DataFrame is used.
ALTERYX_LAYER_COLUMNS = [
    "Replica Layer",      # e.g. replica_trr.PipelineRate
    "Silver Layer",       # e.g. mdm_core.Commodity_Union_Dim
    ("Gold Layer - Target Table",  # ExecutiveSummary uses this
     "Gold Layer -Target Table",   # GulfCoast uses this (missing space)
     "Gold Layer"),                 # InventoryFluctuation uses this
    "Semantic Layer",     # e.g. sem_commercial.Gulf_Coast_PL_Tariffs_Fact_vw
]

# Known qualified-name corrections: wrong name → correct name.
# Some STTMs reference tables by a slightly different name than the table's own
# STTM defines. This map auto-corrects at parse time so lineage connects properly.
STTM_NAME_CORRECTIONS = {
    "udm_core.Enverus_Frac_Crews": "udm_core.Enverus_Frac_Crews_Fact",
    "udm_core.Enverus_Rigs_Through_Time": "udm_core.Enverus_Rigs_Through_Time_Fact",
    # Case normalization: LPSAPricingDisplay STTM uses capital-C schema prefix
    "Commercial_core.Pricing_Display_Fact": "commercial_core.Pricing_Display_Fact",
}

# ── Alteryx provenance: DataSystem name mapping ──────────────────────────
# Maps the "Database" column values in Alteryx STTMs to existing DataSystem
# node names in the graph. These are the operational source systems.
ALTERYX_DS_NAME_MAP = {
    "MPR_Alteryx_Reporting_Proxy": "MPR",
    "MPR-Prod(MPR-Reporting-Proxy)": "MPR",
    "TRR-Prod": "TRR",
    "KittyHawk": "Kittyhawk",
    "MarketingPA_EIS": "EIS",
    "MarketingPA_TMR": "TMR",
    "MIPS-Reporting": "MIPS",
    "Refining Prod": "Refining_OLAP",
}

# Normalizes inconsistent Sandbox DataSystem names (Database.1 column) across
# the 7 Alteryx STTM files. Some files omit underscores/spaces.
ALTERYX_SANDBOX_NAME_MAP = {
    "BusinessOperations": "Business_Operations",
    "CommercialAnalysis": "Commercial Analysis",
}

# canonicalize_server_name is imported from neo4j_loader (centralized)


# ── Cypher: Alteryx provenance — Server nodes ────────────────────────────
# Creates Server nodes for the operational source servers referenced in
# Alteryx STTMs, and wires them to their DataSystem via HOSTS.
ENSURE_SERVER_QUERY = """
UNWIND $rows AS row
MERGE (srv:Server {serverName: row.serverName})
ON CREATE SET srv.createdAt = datetime()
WITH srv, row
MATCH (ds:DataSystem {name: row.dataSystemName})
MERGE (srv)-[:HOSTS]->(ds)
"""

# ── Cypher: Alteryx provenance — Operational source tables ───────────────
# Creates Table nodes for the original operational source tables (pre-IDP),
# wires them to their DataSystem, and creates REPLICATED_TO to Replica tables.
ENSURE_OP_SOURCE_TABLE_QUERY = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET t.name = row.name,
  t.layer = 'Operational',
  t.sourceFile = row.sourceFile,
  t.createdAt = datetime()
WITH t, row
MATCH (ds:DataSystem {name: row.dataSystemName})
MERGE (ds)-[:CONTAINS]->(t)
"""

# Wires operational source table → IDP replica table via REPLICATED_TO.
OP_SOURCE_REPLICATED_TO_QUERY = """
UNWIND $rows AS row
MATCH (src:Table {qualifiedName: row.sourceQN})
MATCH (rep:Table {qualifiedName: row.replicaQN})
MERGE (src)-[:REPLICATED_TO]->(rep)
"""

# ── Cypher: Alteryx Sandbox DataSystems ──────────────────────────────────
# Creates DataSystem nodes for the Alteryx Sandbox databases (e.g.,
# "Commercial Analysis", "Business_Operations") with platform metadata.
ENSURE_SANDBOX_DS_QUERY = """
UNWIND $rows AS row
MERGE (ds:DataSystem {name: row.name})
ON CREATE SET ds.platform = "Alteryx Sandbox",
  ds.status = "sunsetting",
  ds.description = row.description,
  ds.createdAt = datetime()
ON MATCH SET ds.platform = "Alteryx Sandbox",
  ds.status = "sunsetting"
"""

# ── Cypher: MIGRATED_FROM — Gold/Target table originated in Sandbox ──────
MIGRATED_FROM_QUERY = """
UNWIND $rows AS row
MATCH (t:Table {qualifiedName: row.tableQN})
MATCH (ds:DataSystem {name: row.sandboxName})
MERGE (t)-[:MIGRATED_FROM]->(ds)
"""

# ── Cypher: Report CONSUMES Semantic view ────────────────────────────────
ENSURE_REPORT_CONSUMES_QUERY = """
UNWIND $rows AS row
MERGE (r:Report {reportKey: row.reportKey})
ON CREATE SET r.name = row.reportName,
              r.createdAt = datetime()
WITH r, row
MERGE (t:Table {qualifiedName: row.semanticQN})
ON CREATE SET t.layer = 'Semantic',
              t.name = split(row.semanticQN, '.')[1],
              t.sourceFile = 'auto-generated from Alteryx STTM'
MERGE (r)-[:CONSUMES]->(t)
"""

# ── Cypher: Create DERIVED_FROM relationships ──────────────────────────────
DERIVED_FROM_QUERY = """
UNWIND $rows AS row
MATCH (child:Table {qualifiedName: row.child})
MATCH (parent:Table {qualifiedName: row.parent})
MERGE (child)-[:DERIVED_FROM]->(parent)
"""

# Cypher: Create stub Table nodes for STTM-referenced sources missing from the graph.
# Uses MERGE so existing nodes are untouched. Also wires to Schema via CONTAINS.
ENSURE_TABLE_NODE_QUERY = f"""
UNWIND $rows AS row
MERGE (t:Table {{qualifiedName: row.qualifiedName}})
ON CREATE SET t.name = row.name,
  t.layer = row.layer,
  t.sourceFile = row.sourceFile,
  t.createdAt = datetime()
ON MATCH SET t.sourceFile = coalesce(t.sourceFile, row.sourceFile)
REMOVE t.source
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET t:Legacy)
WITH t, row
MERGE (s:Schema {{qualifiedName: row.schema}})
  ON CREATE SET s.createdAt = datetime(),
                s.layer = {cypher_schema_layer("row.schema", "Silver")}
FOREACH (_ IN CASE WHEN {cypher_is_legacy_schema("row.schema")} THEN [1] ELSE [] END | SET s:Legacy)
MERGE (s)-[:CONTAINS]->(t)
"""

# Cypher: Delete all DERIVED_FROM edges from a specific table (used before STTM override)
DELETE_DERIVED_FROM_QUERY = """
MATCH (t:Table {qualifiedName: $tableName})-[r:DERIVED_FROM]->()
DELETE r
RETURN count(r) AS deletedCount
"""

# ── Verification queries ───────────────────────────────────────────────────
VERIFY_LINEAGE_COUNT = """
MATCH ()-[r:DERIVED_FROM]->()
RETURN count(r) AS totalDerivedFromRelationships
"""

VERIFY_LINEAGE_BY_LAYER = """
MATCH (child:Table)-[:DERIVED_FROM]->(parent:Table)
RETURN child.layer + ' -> ' + parent.layer AS direction, count(*) AS count
ORDER BY count DESC
"""

VERIFY_FULL_LINEAGE_SAMPLE = """
MATCH path = (v:Table:View)-[:DERIVED_FROM*]->(src:Table)
WHERE src.layer = 'Replica'
RETURN v.qualifiedName AS semanticView,
       [n IN nodes(path) | n.qualifiedName] AS lineagePath,
       length(path) AS depth
ORDER BY depth DESC
LIMIT 5
"""

VERIFY_ORPHAN_LINEAGE = """
MATCH (t:Table)
WHERE t.layer IN ['Gold', 'Silver', 'Semantic']
  AND NOT (t)-[:DERIVED_FROM]->()
  AND NOT t:View
RETURN t.qualifiedName AS tableWithNoLineage, t.layer AS layer
ORDER BY t.layer, t.qualifiedName
"""


def split_qualified_names(cell_value):
    """Qualified names in a multi-value cell, skipping 'No Insight' placeholders."""
    return [p for p in split_multivalue(cell_value) if "No Insight" not in p]


def normalize_sttm_columns(df):
    """Normalize STTM DataFrame column headers.

    Steps:
      1. Collapse newlines and extra whitespace in column names.
      2. Apply alias mapping (Gold→Silver equivalents, misspellings).
      3. Detect schema-name columns as fallback for missing 'Source'.
    Returns the DataFrame with renamed columns and a list of warnings.
    """
    warnings = []

    # Step 1: Collapse newlines and extra whitespace in column names
    cleaned = {}
    for col in df.columns:
        normalized = re.sub(r"\s+", " ", str(col)).strip()
        if normalized != str(col):
            cleaned[col] = normalized
    if cleaned:
        df = df.rename(columns=cleaned)

    # Step 2: Apply alias mapping
    alias_renames = {}
    for col in df.columns:
        if str(col) in STTM_COLUMN_ALIASES:
            alias_renames[col] = STTM_COLUMN_ALIASES[str(col)]
    if alias_renames:
        df = df.rename(columns=alias_renames)
        for old, new in alias_renames.items():
            warnings.append(f"Aliased column '{old}' -> '{new}'")

    # Step 3: If 'Source' column is missing, detect a schema-name column as fallback
    if "Source" not in df.columns:
        for col in df.columns:
            col_str = str(col).strip()
            if col_str.startswith("replica_") or col_str.startswith("config."):
                df["Source"] = col_str
                warnings.append(f"Using column '{col_str}' as fallback for missing 'Source'")
                break

    return df, warnings


def validate_sttm_file(filepath):
    """Validate an STTM file has the expected sheet and columns.

    Normalizes column headers (newlines, aliases, misspellings) before checking.
    Only requires lineage-critical columns; logs warnings for missing metadata.
    Returns (True, DataFrame) if valid, (False, error_message) if not.
    """
    try:
        xl = pd.ExcelFile(filepath)
    except Exception as e:
        return False, f"Cannot read file: {e}"

    # Report any sheets beyond the known ones (exclude DD & STTM variants)
    extra_sheets = {s for s in xl.sheet_names
                    if s not in STTM_KNOWN_SHEETS and not s.startswith("DD & STTM")}
    if extra_sheets:
        filename = os.path.basename(filepath)
        print(f"    NOTE {filename} has extra sheet(s): {sorted(extra_sheets)}")

    if STTM_SHEET in xl.sheet_names:
        # Exact match — single sheet
        sheets_to_read = [STTM_SHEET]
    else:
        # Fallback: look for variant sheets starting with 'DD & STTM'
        # e.g. 'DD & STTM - Enverus_Wells', 'DD & STTM -Price Fact'
        variant_sheets = [s for s in xl.sheet_names if s.startswith("DD & STTM")]
        if not variant_sheets:
            return False, f"Missing sheet '{STTM_SHEET}'. Found: {xl.sheet_names}"
        sheets_to_read = variant_sheets
        filename = os.path.basename(filepath)
        print(f"      Using {len(variant_sheets)} variant sheet(s): {sorted(variant_sheets)}")

    # Read, normalize, and concatenate all matching sheets
    frames = []
    all_warnings = []
    for sheet_name in sheets_to_read:
        sheet_df = pd.read_excel(filepath, sheet_name=sheet_name)
        sheet_df, norm_warnings = normalize_sttm_columns(sheet_df)
        all_warnings.extend(norm_warnings)
        frames.append(sheet_df)

    df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    for w in all_warnings:
        print(f"      {w}")

    # Check lineage-critical columns
    actual_cols = set(df.columns)
    missing_critical = STTM_LINEAGE_CRITICAL - actual_cols
    if missing_critical:
        return False, f"Missing critical columns: {missing_critical}"

    # Warn about missing metadata columns (non-blocking)
    missing_meta = STTM_METADATA_COLUMNS - actual_cols
    if missing_meta:
        filename = os.path.basename(filepath)
        print(f"      WARN {filename}: missing metadata columns (non-blocking): {sorted(missing_meta)}")

    return True, df


def extract_sttm_lineage(sttm_df):
    """Extract correct (target_table, source_table) pairs from an STTM DataFrame.

    Handles cases where:
      - Source column exists: builds schema.table qualified name
      - Source column missing but Source Table Name already qualified: uses as-is
    Returns:
        target_table: str — the fully qualified target table name
        source_pairs: set of str — fully qualified source table names
    """
    target_table = sttm_df["Physical Table Name"].dropna().iloc[0].strip()

    has_source_col = "Source" in sttm_df.columns
    source_pairs = set()

    # Source values that indicate column-level provenance, not table-level lineage.
    # 'config'        = column value comes from a config lookup table
    # 'ETL Generated' = column value is generated by the ETL process
    COLUMN_LEVEL_SOURCES = {"config", "etl generated"}

    if has_source_col:
        # Get unique Source + Source Table Name pairs (skip column-level sources)
        # Strip whitespace and compare case-insensitively
        source_stripped = sttm_df["Source"].astype(str).str.strip()
        source_rows = sttm_df[
            (sttm_df["Source"].notna())
            & (sttm_df["Source Table Name"].notna())
            & (~source_stripped.str.lower().isin(COLUMN_LEVEL_SOURCES))
        ][["Source", "Source Table Name"]].drop_duplicates()

        for _, row in source_rows.iterrows():
            for schema, table in pair_positional(
                split_multivalue(row["Source"]), split_multivalue(row["Source Table Name"]), target_table
            ):
                source_pairs.add(f"{schema}.{table}")
    else:
        # Fallback: Source Table Name may already contain qualified names
        source_tables = sttm_df["Source Table Name"].dropna().unique()
        for t in source_tables:
            t_str = str(t).strip()
            if t_str and "." in t_str:
                source_pairs.add(t_str)

    # Apply known name corrections
    target_table = STTM_NAME_CORRECTIONS.get(target_table, target_table)
    source_pairs = {STTM_NAME_CORRECTIONS.get(s, s) for s in source_pairs}

    return target_table, source_pairs


def validate_alteryx_sttm_file(filepath):
    """Validate an Alteryx-format STTM file and return its Table Mapping data.

    Alteryx STTMs have 'Table Mapping' + 'Field Mapping' sheets instead of
    the standard 'DD & STTM'. The Table Mapping sheet contains one row per
    source table, with columns for each medallion layer (Replica → Silver →
    Gold → Semantic).

    Returns:
        (True, DataFrame) if the file has a valid Alteryx Table Mapping sheet.
        (False, error_message) if the file is not an Alteryx STTM or is invalid.
    """
    try:
        xl = pd.ExcelFile(filepath)
    except Exception as e:
        return False, f"Cannot read file: {e}"

    # Detect Alteryx format by looking for a 'Table Mapping' or 'Table mapping' sheet
    mapping_sheet = None
    for candidate in ALTERYX_TABLE_MAPPING_SHEETS:
        if candidate in xl.sheet_names:
            mapping_sheet = candidate
            break

    if not mapping_sheet:
        return False, "Not an Alteryx STTM (no 'Table Mapping' sheet)"

    df = pd.read_excel(filepath, sheet_name=mapping_sheet)

    # Verify at least some of the expected layer columns exist.
    # Entries can be strings or tuples of variant names; a tuple matches if
    # any of its candidates exist in the DataFrame columns.
    found_cols = []
    for entry in ALTERYX_LAYER_COLUMNS:
        if isinstance(entry, tuple):
            matched = next((c for c in entry if c in df.columns), None)
            if matched:
                found_cols.append(matched)
        elif entry in df.columns:
            found_cols.append(entry)
    if len(found_cols) < 2:
        return False, (f"Alteryx Table Mapping has too few layer columns. "
                       f"Found: {found_cols}, Expected: {ALTERYX_LAYER_COLUMNS}")

    return True, df


def extract_alteryx_lineage(df):
    """Extract multi-hop DERIVED_FROM pairs from an Alteryx Table Mapping sheet.

    Each row in the sheet maps a source table through intermediate layers:
        Replica Layer → Silver Layer → Gold Layer → Semantic Layer

    For each row, this function creates (child, parent) pairs for every
    adjacent pair of layers that both have non-null qualified names.
    For example, if a row has Replica='replica_trr.X' and Silver='mdm_core.Y',
    we emit ('mdm_core.Y', 'replica_trr.X').

    Returns:
        overrides: dict { target_qualifiedName: set of source_qualifiedNames }
            where each target is the highest-layer table in its lineage chain.
        all_pairs: set of (child, parent) tuples across all layers.
    """
    overrides = {}
    all_pairs = set()

    # Resolve each layer column entry: strings are used directly, tuples are
    # searched for the first matching column name in the DataFrame.
    resolved_cols = []
    for entry in ALTERYX_LAYER_COLUMNS:
        if isinstance(entry, tuple):
            matched = next((c for c in entry if c in df.columns), None)
            if matched:
                resolved_cols.append(matched)
        elif entry in df.columns:
            resolved_cols.append(entry)

    for _, row in df.iterrows():
        # Build an ordered list of non-null qualified names for this row.
        # Each layer slot is a list because cells may contain \n-separated
        # multiple QNs (e.g., Gold Layer -Target Table with 3 gold tables).
        layer_slots = []
        last_gold_slot = None
        for col in resolved_cols:
            val = row.get(col)
            if pd.notna(val):
                qns = [q for q in split_multivalue(val) if "." in q]
                if qns:
                    # Apply name corrections to each QN
                    qns = [STTM_NAME_CORRECTIONS.get(q, q) for q in qns]
                    layer_slots.append(qns)
                    # Track if this is a Gold column (for semantic auto-gen)
                    if col != "Semantic Layer":
                        last_gold_slot = qns
            # Skip empty/null layers (don't append an empty slot)

        # If the Semantic Layer was null but we have Gold Target QNs,
        # auto-generate semantic QNs: sem_commercial.<TableName>_vw
        if resolved_cols and resolved_cols[-1] == "Semantic Layer":
            sem_val = row.get("Semantic Layer")
            if (pd.isna(sem_val) or str(sem_val).strip() == "") and last_gold_slot:
                auto_sem = [f"sem_commercial.{qn.split('.', 1)[1]}_vw"
                            for qn in last_gold_slot]
                layer_slots.append(auto_sem)

        # Create DERIVED_FROM pairs for each adjacent pair of layer slots.
        # If a slot has multiple QNs, each child pairs with each parent
        # (cross-product within adjacent layers).
        for i in range(len(layer_slots) - 1):
            parents = layer_slots[i]      # lower layer (e.g., Replica)
            children = layer_slots[i + 1] # higher layer (e.g., Silver)
            for parent in parents:
                parent = STTM_NAME_CORRECTIONS.get(parent, parent)
                for child in children:
                    child = STTM_NAME_CORRECTIONS.get(child, child)
                    all_pairs.add((child, parent))

        # The highest-layer slot contains the "target" QNs for override purposes.
        # All QNs in lower-layer slots are sources (direct or transitive).
        if layer_slots:
            # Flatten all QNs from lower-layer slots as sources
            all_sources = set()
            for slot in layer_slots[:-1]:
                for qn in slot:
                    all_sources.add(STTM_NAME_CORRECTIONS.get(qn, qn))
            # Each QN in the highest slot is a target
            for target_qn in layer_slots[-1]:
                target_qn = STTM_NAME_CORRECTIONS.get(target_qn, target_qn)
                if target_qn not in overrides:
                    overrides[target_qn] = set()
                overrides[target_qn] |= all_sources

    return overrides, all_pairs


def extract_alteryx_provenance(df, filename):
    """Extract full provenance metadata from an Alteryx Table Mapping sheet.

    Parses every row to build lists of records for:
      - Server nodes + Server→DataSystem HOSTS edges
      - Operational source Table nodes + DataSystem→Table CONTAINS edges
      - Operational source → Replica REPLICATED_TO edges
      - Sandbox DataSystem nodes (from Database.1 column)
      - Gold/Target table → Sandbox MIGRATED_FROM edges
      - Report → Semantic view CONSUMES edges

    Args:
        df: DataFrame from the Alteryx 'Table Mapping' sheet.
        filename: STTM filename for sourceFile provenance.

    Returns:
        dict with keys: servers, op_tables, replication, sandboxes,
                        migrated_from, report_consumes
    """
    servers = {}          # serverName → dataSystemName
    op_tables = []        # {qualifiedName, name, dataSystemName, sourceFile}
    replication = []      # {sourceQN, replicaQN}
    sandboxes = set()     # sandbox DataSystem names (from Database.1)
    migrated_from = []    # {tableQN, sandboxName}
    report_consumes = []  # {reportName, semanticQN}

    # Detect whether Gold Layer -Target Table column exists — if so, Gold Layer
    # is an intermediate input, and the Target Table is the final Gold object.
    has_gold_target = "Gold Layer -Target Table" in df.columns
    # Also check the ExecutiveSummary variant
    if not has_gold_target:
        has_gold_target = "Gold Layer - Target Table" in df.columns
    gold_target_col = (
        "Gold Layer -Target Table" if "Gold Layer -Target Table" in df.columns
        else "Gold Layer - Target Table" if "Gold Layer - Target Table" in df.columns
        else None
    )

    for _, row in df.iterrows():
        server_name = row.get("Server/File System")
        db_name = row.get("Database")
        table_name = row.get("Table")
        source_type = str(row.get("Source Type", "")).strip().lower()
        replica_qn = row.get("Replica Layer")
        sandbox_db = row.get("Database.1")
        report_name = row.get("Report Name")
        semantic_qn = row.get("Semantic Layer")

        # Determine the final Gold table(s) — may be \n-separated multi-value.
        # Each gets a MIGRATED_FROM edge to the sandbox.
        final_gold_qns = []
        gold_raw = None
        if gold_target_col and pd.notna(row.get(gold_target_col)):
            gold_raw = str(row.get(gold_target_col)).strip()
        elif pd.notna(row.get("Gold Layer")):
            gold_raw = str(row.get("Gold Layer")).strip()
        for qn in split_multivalue(gold_raw):
            qn = STTM_NAME_CORRECTIONS.get(qn, qn)
            if "." in qn:
                final_gold_qns.append(qn)

        # ── 1. Server → DataSystem (only for Database source types) ──────
        # Skip non-database sources: TextInput, Text Input, Excel, etc.
        is_db_source = "database" in source_type
        if is_db_source and pd.notna(server_name) and pd.notna(db_name):
            srv = canonicalize_server_name(str(server_name).strip())
            ds_raw = str(db_name).strip()
            ds_mapped = ALTERYX_DS_NAME_MAP.get(ds_raw, ds_raw)
            if srv and ds_mapped:
                servers[srv] = ds_mapped

            # ── 2. Operational source table ──────────────────────────────
            if pd.notna(table_name):
                tbl = str(table_name).strip()
                op_qn = f"{ds_mapped}.{tbl}"
                op_tables.append({
                    "qualifiedName": op_qn,
                    "name": tbl,
                    "dataSystemName": ds_mapped,
                    "sourceFile": filename,
                })

                # ── 3. Operational → Replica REPLICATED_TO ───────────────
                # Replica cells may contain \n-separated multi-value QNs
                for rep in split_multivalue(replica_qn):
                    if "." in rep:
                        replication.append({
                            "sourceQN": op_qn,
                            "replicaQN": rep,
                        })

        # ── 4. Sandbox DataSystem (normalized name) ─────────────────────
        if pd.notna(sandbox_db):
            sb = str(sandbox_db).strip()
            sb = ALTERYX_SANDBOX_NAME_MAP.get(sb, sb)
            if sb:
                sandboxes.add(sb)

        # ── 5. Gold/Target → Sandbox MIGRATED_FROM ───────────────────────
        if final_gold_qns and pd.notna(sandbox_db):
            sb = str(sandbox_db).strip()
            sb = ALTERYX_SANDBOX_NAME_MAP.get(sb, sb)
            if sb:
                for gqn in final_gold_qns:
                    migrated_from.append({
                        "tableQN": gqn,
                        "sandboxName": sb,
                    })

        # ── 6. Report CONSUMES Semantic view (split \n multi-value) ──────
        # If Semantic Layer is null but Report Name + Gold Target exist,
        # auto-generate the semantic QN: sem_commercial.<TableName>_vw
        sem_qns = []
        if pd.notna(semantic_qn):
            sem_qns = [sem for sem in split_multivalue(semantic_qn) if "." in sem]
        elif final_gold_qns:
            # Derive semantic QN from Gold Target: schema.Table -> sem_commercial.Table_vw
            for gqn in final_gold_qns:
                _, tbl_name = gqn.split(".", 1)
                sem_qns.append(f"sem_commercial.{tbl_name}_vw")

        if pd.notna(report_name) and sem_qns:
            rpt = str(report_name).strip()
            if rpt:
                for sem in sem_qns:
                    report_consumes.append({
                        "reportName": rpt,
                        "semanticQN": sem,
                    })

    # Deduplicate lists
    seen_op = set()
    unique_op = []
    for rec in op_tables:
        if rec["qualifiedName"] not in seen_op:
            seen_op.add(rec["qualifiedName"])
            unique_op.append(rec)

    seen_rep = set()
    unique_rep = []
    for rec in replication:
        key = (rec["sourceQN"], rec["replicaQN"])
        if key not in seen_rep:
            seen_rep.add(key)
            unique_rep.append(rec)

    seen_mig = set()
    unique_mig = []
    for rec in migrated_from:
        key = (rec["tableQN"], rec["sandboxName"])
        if key not in seen_mig:
            seen_mig.add(key)
            unique_mig.append(rec)

    seen_rpt = set()
    unique_rpt = []
    for rec in report_consumes:
        key = (rec["reportName"], rec["semanticQN"])
        if key not in seen_rpt:
            seen_rpt.add(key)
            unique_rpt.append(rec)

    return {
        "servers": servers,
        "op_tables": unique_op,
        "replication": unique_rep,
        "sandboxes": sandboxes,
        "migrated_from": unique_mig,
        "report_consumes": unique_rpt,
    }


def build_stub_records(pairs, provenance=None):
    """Build stub Table node records for all qualified names in lineage pairs.

    Args:
        pairs: set of (child, parent) qualified name tuples.
        provenance: optional dict mapping qualifiedName -> STTM filename.
    Returns a list of dicts with qualifiedName, name, schema, layer, legacy, sourceFile.
    Filters out malformed names (containing '/' or missing '.').
    """
    provenance = provenance or {}
    all_qnames = set()
    for child, parent in pairs:
        all_qnames.add(child)
        all_qnames.add(parent)

    records = []
    for qn in sorted(all_qnames):
        # Skip malformed qualified names
        if "/" in qn or "." not in qn:
            continue
        schema, table_name = qn.split(".", 1)
        layer = schema_layer(schema) or "Unknown"
        records.append({
            "qualifiedName": qn,
            "name": table_name,
            "schema": schema,
            "layer": layer,
            "legacy": is_legacy(qn, layer),
            "sourceFile": provenance.get(qn, ""),
        })
    return records


def load_sttm_overrides(sttm_dir=STTM_DIR):
    """Scan the target directory recursively for STTM files and extract correct lineage overrides.

    Tries two formats per file:
      1. Standard DD & STTM format (most files)
      2. Alteryx Table Mapping format (ExecutiveSummary, GulfCoast, InventoryFluctuation)

    Returns:
        overrides: dict { target_qualifiedName: set of source_qualifiedNames }
        provenance: dict { qualifiedName: STTM_filename } for all tables referenced
        extra_pairs: set of (child, parent) tuples from Alteryx multi-hop lineage
        alteryx_provenance: dict with accumulated provenance metadata from all
            Alteryx STTMs (servers, op_tables, replication, sandboxes,
            migrated_from, report_consumes). Empty dict if no Alteryx STTMs found.
    Only includes files that pass validation.
    """
    overrides = {}
    provenance = {}
    empty_prov = {
        "servers": {}, "op_tables": [], "replication": [],
        "sandboxes": set(), "migrated_from": [], "report_consumes": [],
    }
    if not os.path.isdir(sttm_dir):
        print(f"  No STTM directory found at {sttm_dir}, skipping overrides.")
        return overrides, provenance, set(), empty_prov

    sttm_files = []
    for root, _, fs in os.walk(sttm_dir):
        for f in fs:
            if (f.endswith(".xlsx") or f.endswith(".xls")) and not f.startswith("~"):
                sttm_files.append(os.path.join(root, f))
    sttm_files = sorted(set(sttm_files))

    if not sttm_files:
        print(f"  No STTM files found in {sttm_dir}.")
        return overrides, provenance, set(), empty_prov

    # extra_pairs collects multi-hop lineage from Alteryx STTMs
    # (e.g., Silver→Replica edges that aren't target→source overrides)
    extra_pairs = set()
    # Accumulated Alteryx provenance across all 3 STTM files
    all_servers = {}
    all_op_tables = []
    all_replication = []
    all_sandboxes = set()
    all_migrated_from = []
    all_report_consumes = []

    print(f"  Found {len(sttm_files)} STTM file(s) in {STTM_DIR}")
    for filepath in sorted(sttm_files):
        filename = os.path.basename(filepath)

        # ── Try standard DD & STTM format first ──────────────────────────
        valid, result = validate_sttm_file(filepath)
        if valid:
            target_table, source_pairs = extract_sttm_lineage(result)
            overrides[target_table] = source_pairs
            provenance[target_table] = filename
            for src in source_pairs:
                provenance.setdefault(src, filename)
            print(f"    OK {filename}: {target_table} -> {sorted(source_pairs)}")
            continue

        # ── Try Alteryx format as fallback ────────────────────────────────
        alt_valid, alt_result = validate_alteryx_sttm_file(filepath)
        if alt_valid:
            alt_overrides, alt_pairs = extract_alteryx_lineage(alt_result)
            # Merge Alteryx overrides into the main overrides dict
            for target, sources in alt_overrides.items():
                overrides[target] = sources
                provenance[target] = filename
                for src in sources:
                    provenance.setdefault(src, filename)
            # Collect intermediate-layer pairs (e.g., Silver→Replica)
            extra_pairs |= alt_pairs

            # Extract full provenance metadata from this Alteryx STTM
            prov_data = extract_alteryx_provenance(alt_result, filename)
            all_servers.update(prov_data["servers"])
            all_op_tables.extend(prov_data["op_tables"])
            all_replication.extend(prov_data["replication"])
            all_sandboxes |= prov_data["sandboxes"]
            all_migrated_from.extend(prov_data["migrated_from"])
            all_report_consumes.extend(prov_data["report_consumes"])

            targets_str = sorted(alt_overrides.keys())
            print(f"    OK [Alteryx] {filename}: {targets_str} "
                  f"({len(alt_pairs)} multi-hop pair(s))")
            continue

        # ── Neither format matched ────────────────────────────────────────
        print(f"    SKIP {filename}: {result}")

    alteryx_provenance = {
        "servers": all_servers,
        "op_tables": all_op_tables,
        "replication": all_replication,
        "sandboxes": all_sandboxes,
        "migrated_from": all_migrated_from,
        "report_consumes": all_report_consumes,
    }
    return overrides, provenance, extra_pairs, alteryx_provenance


def extract_lineage_pairs(df):
    """Extract all (child, parent) DERIVED_FROM pairs from the mapping file.

    Two column pairs:
      1. 'Report Connected to SemanticLayer View' → 'Semantic layer view derived from :Gold:Silver'
         (Semantic → Gold/Silver)
      2. 'Semantic layer view derived from :Gold:Silver' → 'Gold:Silver objects derived from'
         (Gold/Silver → Replica)

    Multi-value cells produce multiple pairs (one per combination).
    """
    pairs = set()

    for _, row in df.iterrows():
        # ── Semantic → Gold/Silver ─────────────────────────────────────────
        sem_views = split_qualified_names(row.get("Semantic View / Direct Table Connection"))
        gs_tables = split_qualified_names(row.get("UDM Table"))

        # Filter out non-schema values (e.g., 'Excel', 'Dev_Deals_with_Price_Curves_Concat')
        sem_views = [v for v in sem_views if "." in v]
        gs_tables = [t for t in gs_tables if "." in t]

        # Each semantic view is derived from each Gold/Silver table in this row
        for sem in sem_views:
            for gs in gs_tables:
                pairs.add((sem, gs))

        # ── Gold/Silver → Replica ──────────────────────────────────────────
        rep_tables = split_qualified_names(row.get("IDP Replica Entities"))
        rep_tables = [t for t in rep_tables if "." in t]

        # Each Gold/Silver table is derived from each Replica table in this row
        for gs in gs_tables:
            for rep in rep_tables:
                pairs.add((gs, rep))

    return pairs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Load table-level DERIVED_FROM lineage into Neo4j.")
    parser.add_argument("--dir", type=str, default="Data/sttms", help="Directory containing STTM files (relative or absolute)")
    args = parser.parse_args()

    # Resolve target directory path
    sttm_dir = os.path.join(PROJECT_ROOT, args.dir) if not os.path.isabs(args.dir) else args.dir
    if not os.path.exists(sttm_dir):
        print(f"ERROR: Directory not found: {sttm_dir}")
        sys.exit(1)

    loader = Neo4jLoader()

    try:
        # ── Read Excel ─────────────────────────────────────────────────────
        print(f"Reading: {EXCEL_PATH}")
        df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
        print(f"Rows: {len(df)}")

        # ── Extract lineage pairs ──────────────────────────────────────────
        pairs = extract_lineage_pairs(df)
        print(f"\nUnique DERIVED_FROM pairs: {len(pairs)}")

        # ── Apply STTM overrides ───────────────────────────────────────────
        # STTM files provide the ground truth for table-level lineage.
        # For each table with an STTM, remove cross-product pairs and replace
        # with only the STTM-confirmed source tables.
        print("\nScanning for STTM overrides...")
        overrides, provenance, extra_pairs, alteryx_prov = load_sttm_overrides(sttm_dir)
        if overrides:
            overridden_count = 0
            for target_table, correct_sources in overrides.items():
                # Remove all pairs where this table is the child
                old_pairs = {p for p in pairs if p[0] == target_table}
                new_pairs = {(target_table, src) for src in correct_sources}
                removed = old_pairs - new_pairs
                added = new_pairs - old_pairs
                if removed or added:
                    pairs -= removed
                    pairs |= new_pairs
                    overridden_count += 1
                    print(f"    Override {target_table}:")
                    for r in sorted(removed):
                        print(f"      - REMOVED: {r[0]} -> {r[1]}")
                    for a in sorted(added):
                        print(f"      + ADDED:   {a[0]} -> {a[1]}")
            print(f"  Applied {overridden_count} STTM override(s). "
                  f"Final pair count: {len(pairs)}")
        else:
            print("  No STTM overrides to apply.")

        # ── Merge Alteryx multi-hop pairs ─────────────────────────────────
        # Alteryx STTMs produce intermediate lineage pairs (e.g., Silver→Replica)
        # that are not captured by the target-level override logic above.
        # Filter out any pair where the child has an STTM override and the
        # parent is NOT in that override's correct source set — otherwise the
        # Alteryx cross-product would re-add false edges just removed above.
        if extra_pairs:
            if overrides:
                conflicting = {
                    (child, parent) for child, parent in extra_pairs
                    if child in overrides and parent not in overrides[child]
                }
                if conflicting:
                    extra_pairs -= conflicting
                    print(f"\n  Filtered {len(conflicting)} Alteryx pair(s) that "
                          f"conflict with STTM overrides.")
            new_from_alteryx = extra_pairs - pairs
            pairs |= extra_pairs
            print(f"  Merged {len(new_from_alteryx)} new Alteryx multi-hop pair(s). "
                  f"Total pairs: {len(pairs)}")

        # ── Canonicalize table qualifiedNames ──────────────────────────
        # Prevent case-variant duplicate Table nodes by normalizing all
        # qualifiedNames to match existing nodes in the graph.
        print("\nCanonicalizing table qualifiedNames...")
        qn_lookup = loader.build_table_qn_lookup()
        canon = lambda qn: Neo4jLoader.canonicalize_table_qn(qn, qn_lookup)
        pairs = {(canon(child), canon(parent)) for child, parent in pairs}
        if overrides:
            overrides = {canon(k): {canon(s) for s in v}
                         for k, v in overrides.items()}
        if alteryx_prov:
            for tbl_rec in alteryx_prov.get("op_tables", []):
                tbl_rec["qualifiedName"] = canon(tbl_rec["qualifiedName"])
            for rep_rec in alteryx_prov.get("replication", []):
                rep_rec["sourceQN"] = canon(rep_rec["sourceQN"])
                rep_rec["replicaQN"] = canon(rep_rec["replicaQN"])
            for rec in alteryx_prov.get("migrated_from", []):
                rec["tableQN"] = canon(rec["tableQN"])
            for rec in alteryx_prov.get("report_consumes", []):
                rec["semanticQN"] = canon(rec["semanticQN"])

        # ── Ensure all referenced Table nodes exist ─────────────────────
        # STTM files may reference replica/config tables not yet in the graph.
        # Create stub nodes so the DERIVED_FROM MATCH can find them.
        print("Ensuring all referenced Table nodes exist...")
        stub_records = build_stub_records(pairs, provenance)
        # Filter to only valid records (skip malformed)
        malformed = [p for p in pairs if "/" in p[0] or "/" in p[1]]
        if malformed:
            print(f"  Skipping {len(malformed)} malformed pair(s) (contain '/'):")
            for m in sorted(malformed)[:10]:
                print(f"    {m[0]} -> {m[1]}")
            pairs -= set(malformed)

        loader.write_batches(ENSURE_TABLE_NODE_QUERY, stub_records)
        print(f"  Ensured {len(stub_records)} Table node(s) (new stubs created as needed).")

        # Convert to dicts for Cypher
        records = [{"child": child, "parent": parent} for child, parent in pairs]

        # ── Load into Neo4j ────────────────────────────────────────────────
        # For tables with STTM overrides, first delete their old edges
        # then MERGE the correct ones (handles re-runs cleanly).
        if overrides:
            print("\nClearing old DERIVED_FROM for STTM-overridden tables...")
            with loader.driver.session(database=loader.database) as session:
                for target_table in overrides:
                    result = session.run(
                        DELETE_DERIVED_FROM_QUERY, tableName=target_table
                    )
                    record = result.single()
                    deleted = record["deletedCount"] if record else 0
                    if deleted:
                        print(f"    Deleted {deleted} old edge(s) from {target_table}")

        print("\nLoading DERIVED_FROM relationships...")
        loader.write_batches(DERIVED_FROM_QUERY, records)
        print(f"  Loaded {len(records)} pairs.")

        # ── Create Alteryx provenance graph ──────────────────────────────
        # Full provenance for Alteryx-originated tables:
        #   Server → DataSystem → Op Source Table → REPLICATED_TO → Replica
        #   Sandbox DataSystem ← MIGRATED_FROM ← Gold/Target Table
        #   Report → CONSUMES → Semantic View
        if alteryx_prov.get("servers"):
            print("\nCreating Alteryx provenance graph...")
            with loader.driver.session(database=loader.database) as session:
                # 1. Server nodes + Server→DataSystem HOSTS
                srv_rows = [{"serverName": srv, "dataSystemName": ds}
                            for srv, ds in alteryx_prov["servers"].items()]
                loader.write_batches(ENSURE_SERVER_QUERY, srv_rows)
                print(f"  Created {len(srv_rows)} Server node(s): "
                      f"{sorted(alteryx_prov['servers'].keys())}")

                # 2a. Clean stale Op Table nodes with raw DB name prefixes.
                # Prior runs may have created nodes like MIPS-Reporting.X or
                # MPR-Prod(...).X before the DS name map was complete.
                stale_deleted = 0
                for raw_db, mapped_ds in ALTERYX_DS_NAME_MAP.items():
                    if raw_db == mapped_ds:
                        continue  # no rename needed
                    # Simply delete stale nodes; correct nodes + edges are
                    # recreated fresh in steps 2b and 3 below.
                    result = session.run("""
                        MATCH (stale:Table {layer: 'Operational'})
                        WHERE stale.qualifiedName STARTS WITH $rawPrefix
                        DETACH DELETE stale
                        RETURN count(stale) AS cnt
                    """, rawPrefix=raw_db + ".")
                    rec = result.single()
                    stale_deleted += rec["cnt"] if rec else 0
                if stale_deleted:
                    print(f"  Cleaned {stale_deleted} stale Op Table node(s) "
                          f"with raw DB name prefixes.")

                # 2b. Operational source Table nodes + DataSystem→Table CONTAINS
                if alteryx_prov["op_tables"]:
                    loader.write_batches(ENSURE_OP_SOURCE_TABLE_QUERY, alteryx_prov["op_tables"])
                    print(f"  Created {len(alteryx_prov['op_tables'])} "
                          f"operational source Table node(s).")

                # 3. Operational source → Replica REPLICATED_TO
                if alteryx_prov["replication"]:
                    loader.write_batches(OP_SOURCE_REPLICATED_TO_QUERY, alteryx_prov["replication"])
                    print(f"  Created {len(alteryx_prov['replication'])} "
                          f"REPLICATED_TO edge(s).")

                # 4a. Clean stale un-normalized sandbox nodes from prior runs
                for old_name, new_name in ALTERYX_SANDBOX_NAME_MAP.items():
                    session.run("""
                        MATCH (old:DataSystem {name: $oldName})
                        MATCH (new:DataSystem {name: $newName})
                        WHERE old <> new
                        OPTIONAL MATCH (t)-[r:MIGRATED_FROM]->(old)
                        WITH old, new, collect(t) AS tables, collect(r) AS rels
                        FOREACH (r IN rels | DELETE r)
                        FOREACH (t IN tables |
                            MERGE (t)-[:MIGRATED_FROM]->(new))
                        DETACH DELETE old
                    """, oldName=old_name, newName=new_name).consume()

                # 4b. Sandbox DataSystem nodes
                if alteryx_prov["sandboxes"]:
                    sb_rows = [{"name": sb,
                                "description": f"Alteryx Sandbox database: {sb}"}
                               for sb in sorted(alteryx_prov["sandboxes"])]
                    loader.write_batches(ENSURE_SANDBOX_DS_QUERY, sb_rows)
                    print(f"  Created {len(sb_rows)} Sandbox DataSystem(s): "
                          f"{sorted(alteryx_prov['sandboxes'])}")

                # 5. Gold/Target table → Sandbox MIGRATED_FROM
                if alteryx_prov["migrated_from"]:
                    loader.write_batches(MIGRATED_FROM_QUERY, alteryx_prov["migrated_from"])
                    print(f"  Created {len(alteryx_prov['migrated_from'])} "
                          f"MIGRATED_FROM edge(s).")

                # 6. Report → Semantic view CONSUMES
                if alteryx_prov["report_consumes"]:
                    stamp_report_keys(
                        alteryx_prov["report_consumes"],
                        loader.build_report_key_lookup(),
                        "reportName",
                    )
                    loader.write_batches(ENSURE_REPORT_CONSUMES_QUERY, alteryx_prov["report_consumes"])
                    print(f"  Created {len(alteryx_prov['report_consumes'])} "
                          f"Report CONSUMES edge(s).")

        # ── Post-load manual corrections ─────────────────────────────────
        # Corrections to DERIVED_FROM edges that cannot be fixed in the source
        # Excel file.  Each entry: (child, wrong_parent, correct_parent).
        MANUAL_CORRECTIONS = [
            # sem_masterdata.Location_Vw derives from Kittyhawk_Location_Dim,
            # not the generic Location_Dim.
            ("sem_masterdata.Location_Vw",
             "mdm_core.Location_Dim",
             "mdm_core.Kittyhawk_Location_Dim"),
        ]
        print("\nApplying manual DERIVED_FROM corrections...")
        with loader.driver.session(database=loader.database) as session:
            for child, wrong, correct in MANUAL_CORRECTIONS:
                # Remove wrong edge
                session.run(
                    "MATCH (c:Table {qualifiedName: $child})"
                    "-[r:DERIVED_FROM]->"
                    "(p:Table {qualifiedName: $wrong}) DELETE r",
                    child=child, wrong=wrong,
                )
                # Add correct edge
                session.run(
                    "MATCH (c:Table {qualifiedName: $child}), "
                    "(p:Table {qualifiedName: $correct}) "
                    "MERGE (c)-[:DERIVED_FROM]->(p)",
                    child=child, correct=correct,
                )
                print(f"  Fixed: {child} -> {correct} (was {wrong})")

        # ── Verification ───────────────────────────────────────────────────
        print("\n=== Verification ===")

        print("\nTotal DERIVED_FROM relationships:")
        loader.verify(VERIFY_LINEAGE_COUNT)

        print("\nLineage by layer direction:")
        loader.verify(VERIFY_LINEAGE_BY_LAYER)

        print("\nSample full lineage paths (Semantic -> Replica):")
        loader.verify(VERIFY_FULL_LINEAGE_SAMPLE)

        print("\nGold/Silver/Semantic tables with NO lineage (potential gaps):")
        orphans = loader.verify(VERIFY_ORPHAN_LINEAGE)
        if not orphans:
            print("  None -- all non-View tables have lineage!")

    finally:
        loader.close()


if __name__ == "__main__":
    main()
