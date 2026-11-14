"""
load_master_data.py — Load MasterDataDomain nodes and REALIZED_IN relationships into Neo4j.

Overview
--------
Phase 6 of the Medallion Architecture Knowledge Graph build.  This script
reads master data domain mappings from two Excel files and creates:

  1. MasterDataDomain nodes  — abstract business entities (Location, Product, etc.)
  2. Table nodes              — operational tables (if not already in graph)
  3. DataSystem nodes         — operational data systems (MERGE, safe for existing)
  4. Server nodes             — servers hosting the data systems
  5. Relationships:
     - (MasterDataDomain)-[:REALIZED_IN]->(Table)
     - (DataSystem)-[:CONTAINS]->(Table)       for operational tables
     - (Server)-[:HOSTS]->(DataSystem)

Data Flow
---------
File 1: "List of Master Data June5_2025.xlsx" (sheet: Phase 3 Unique Master Data)
  Columns: Server, Database, Schema, Master_Data_Domain, Entity
  IDP identifier: Database == 'shsdlakeprdwsql'

File 2: "report_alteryx_master_data_requirements_DEC4th.xlsx" (sheet: Sheet1)
  Columns: Data Domain, Server, Database/Schema, Table
  IDP identifier: Server == 'shsdataldevwsql (IDP)'
  Table names prefixed with 'dbo.' are operational (prefix stripped).
  Tables already fully qualified (schema.Table) are IDP tables.

For each row in either spreadsheet:
  a) Determine if the table is IDP or Operational.
  b) IDP tables:  qualifiedName = '{Schema}.{Entity}', likely already in graph.
  c) Operational:  qualifiedName = '{Database}.{Entity}', layer = 'Operational'.
  d) Wire MasterDataDomain -[:REALIZED_IN]-> Table for every row.
  e) Wire DataSystem -[:CONTAINS]-> Table and Server -[:HOSTS]-> DataSystem
     for operational tables.

Deduplication Rules
-------------------
  - QA/test server rows are filtered out when a prod row exists for the same
    (Database, Schema, Master_Data_Domain, Entity).
  - For remaining duplicates on the same (DB, Schema, Domain, Entity),
    prefer 'pgwsql*' style server names, else keep first encountered.
  - Final dedup key: (Database, Schema, Master_Data_Domain, Entity).

Prerequisites
-------------
  - DataSystem and Schema nodes should already exist (run load_schemas.py first)
  - pip install neo4j openpyxl python-dotenv

Usage
-----
    python src/load_master_data.py
"""

import os
import sys
import re
import openpyxl

# Ensure src/ is on the path so neo4j_loader can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from medallion import is_legacy, schema_layer
from neo4j_loader import Neo4jLoader, canonicalize_server_name

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXCEL_PATH = os.path.join(
    PROJECT_ROOT, "Data", "new data system files to process",
    "List of Master Data June5_2025.xlsx",
)
SHEET_NAME = "Phase 3 Unique Master Data"

# Second master data file — Alteryx requirements with different column layout
ALTERYX_MD_EXCEL_PATH = os.path.join(
    PROJECT_ROOT, "Data", "new data system files to process",
    "report_alteryx_master_data_requirements_DEC4th.xlsx",
)
ALTERYX_MD_SHEET_NAME = "Master Data"
ALTERYX_MD_SOURCE_FILE = "report_alteryx_master_data_requirements_DEC4th.xlsx"

# ---------------------------------------------------------------------------
# IDP database identifier — rows with this Database value are IDP tables
# ---------------------------------------------------------------------------
IDP_DATABASE = "shsdlakeprdwsql"

# The DEV IDP server value used in the Alteryx master data file.
# Rows with this server are treated as IDP tables (same as IDP_DATABASE rows).
IDP_DEV_SERVER = "shsdataldevwsql (IDP)"

# canonicalize_server_name is imported from neo4j_loader (centralized).
# It handles test→prod mapping internally, so QA_TO_PROD_SERVER is no longer needed here.

# ---------------------------------------------------------------------------
# Canonical DataSystem names — toLower(name) → preferred casing.
# ---------------------------------------------------------------------------
CANONICAL_DATASYSTEM_NAMES = {
    "kittyhawk":            "Kittyhawk",
    "brandcreditcardmaster": "BrandCreditCardMaster",
    "lightproductsdashboard": "LightProductsDashboard",
    "transportationrates":   "TransportationRates",
    "marketingdatahub":      "marketingdatahub",
    "refining_olap":         "Refining_OLAP",
}


# canonicalize_server_name removed — imported from neo4j_loader


def canonicalize_datasystem_name(name):
    """Return the canonical casing for a DataSystem name."""
    if not name:
        return name
    lower = name.lower()
    if lower in CANONICAL_DATASYSTEM_NAMES:
        return CANONICAL_DATASYSTEM_NAMES[lower]
    return name  # no change if not in the dict


# ---------------------------------------------------------------------------
# Test server patterns to filter out (when prod exists)
# ---------------------------------------------------------------------------
TEST_SERVER_PATTERNS = [".test.", "-qa-"]

# ---------------------------------------------------------------------------
# Source file tag for provenance
# ---------------------------------------------------------------------------
SOURCE_FILE = "List of Master Data June5_2025.xlsx"

# ---------------------------------------------------------------------------
# Known persistence table -> IDP refactored equivalent mapping.
# Format: {persistence qualifiedName: IDP qualifiedName}
# These are legacy tables that have been refactored into Medallion tables.
# ---------------------------------------------------------------------------
PERSISTENCE_TO_IDP = {
    "persistence.Enverus_Production":       "udm_core.Enverus_Production",
    "persistence.Enverus_Rigs":             "udm_core.Enverus_Rigs",
    "persistence.Enverus_Rigs_Through_Time": "udm_core.Enverus_Rigs_Through_Time_Fact",
    "persistence.Enverus_Wells":            "udm_core.Enverus_Wells",
    "persistence.stuzo_location_daily":     None,  # No known IDP equivalent yet
}

# ---------------------------------------------------------------------------
# Cypher: Create MasterDataDomain nodes
# ---------------------------------------------------------------------------
MERGE_DOMAIN_QUERY = """
UNWIND $rows AS row
MERGE (mdd:MasterDataDomain {name: row.name})
ON CREATE SET mdd.status    = 'Fragmented',
              mdd.sourceFile = row.sourceFile,
              mdd.createdAt  = datetime()
ON MATCH SET  mdd.updatedAt  = datetime()
"""

# ---------------------------------------------------------------------------
# Cypher: Create/merge operational Table nodes and wire to DataSystem
# ---------------------------------------------------------------------------
MERGE_OP_TABLE_QUERY = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET t.name       = row.tableName,
              t.layer      = 'Operational',
              t.sourceFile = row.sourceFile,
              t.createdAt  = datetime()
ON MATCH SET  t.updatedAt  = datetime()
WITH t, row
MERGE (ds:DataSystem {name: row.dataSystemName})
ON CREATE SET ds.createdAt = datetime()
MERGE (ds)-[:CONTAINS]->(t)
"""

# ---------------------------------------------------------------------------
# Cypher: Wire Server -[:HOSTS]-> DataSystem (operational only)
# ---------------------------------------------------------------------------
MERGE_SERVER_QUERY = """
UNWIND $rows AS row
MERGE (srv:Server {serverName: row.serverName})
ON CREATE SET srv.createdAt = datetime()
WITH srv, row
MERGE (ds:DataSystem {name: row.dataSystemName})
MERGE (srv)-[:HOSTS]->(ds)
"""

# ---------------------------------------------------------------------------
# Cypher: Create stub Table nodes for IDP tables not yet in graph.
# Infers layer from schema prefix. Wires to Schema via CONTAINS.
# ---------------------------------------------------------------------------
MERGE_IDP_STUB_QUERY = """
UNWIND $rows AS row
MERGE (t:Table {qualifiedName: row.qualifiedName})
ON CREATE SET t.name       = row.tableName,
              t.layer      = row.layer,
              t.sourceFile = row.sourceFile,
              t.createdAt  = datetime()
ON MATCH SET  t.updatedAt  = datetime()
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET t:Legacy)
WITH t, row
MATCH (s:Schema {qualifiedName: row.schemaQN})
MERGE (s)-[:CONTAINS]->(t)
"""

# ---------------------------------------------------------------------------
# Cypher: Wire MasterDataDomain -[:REALIZED_IN]-> Table
# Uses toLower() for case-insensitive matching on qualifiedName.
# ---------------------------------------------------------------------------
REALIZED_IN_QUERY = """
UNWIND $rows AS row
MATCH (mdd:MasterDataDomain {name: row.domainName})
MATCH (t:Table) WHERE toLower(t.qualifiedName) = toLower(row.tableQN)
MERGE (mdd)-[:REALIZED_IN]->(t)
"""

# ---------------------------------------------------------------------------
# Cypher: Wire legacy persistence Table -[:REFACTORED_TO]-> IDP Table
# ---------------------------------------------------------------------------
REFACTORED_TO_QUERY = """
UNWIND $rows AS row
MATCH (legacy:Table {qualifiedName: row.legacyQN})
MATCH (idp:Table {qualifiedName: row.idpQN})
MERGE (legacy)-[:REFACTORED_TO]->(idp)
"""

# ---------------------------------------------------------------------------
# Cypher: Constraint for MasterDataDomain
# ---------------------------------------------------------------------------
DOMAIN_CONSTRAINT = (
    "CREATE CONSTRAINT MasterDataDomain_name_key IF NOT EXISTS "
    "FOR (mdd:MasterDataDomain) REQUIRE mdd.name IS UNIQUE"
)


def is_test_server(server_name):
    """Return True if the server name looks like a test/QA environment."""
    if not server_name:
        return False
    lower = server_name.lower()
    return any(pat in lower for pat in TEST_SERVER_PATTERNS)


def is_pgwsql_server(server_name):
    """Return True if the server name follows the pgwsql* naming pattern."""
    if not server_name:
        return False
    return server_name.lower().startswith("pgwsql")


def read_and_clean(excel_path, sheet_name):
    """Read the Excel sheet and return cleaned rows as list of dicts.

    Each dict has keys: server, database, schema, domain, entity.
    Whitespace is stripped. QA servers are mapped to PROD equivalents.
    """
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    raw_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    # Skip header
    records = []
    for r in raw_rows[1:]:
        server = str(r[0]).strip() if r[0] else None
        database = str(r[1]).strip() if r[1] else None
        schema = str(r[2]).strip() if r[2] else None
        domain = str(r[3]).strip() if r[3] else None
        entity = str(r[4]).strip() if r[4] else None

        if not database or not domain or not entity:
            continue  # skip incomplete rows

        # Canonicalize server name (handles test→prod mapping + case normalization)
        server = canonicalize_server_name(server)

        # Canonicalize database name (used as DataSystem name for operational)
        database = canonicalize_datasystem_name(database)

        records.append({
            "server": server,
            "database": database,
            "schema": schema,
            "domain": domain,
            "entity": entity,
        })

    print(f"  Read {len(records)} rows from '{sheet_name}' (after skipping incomplete rows)")
    return records


def read_alteryx_master_data(excel_path, sheet_name):
    """Read the Alteryx master data requirements file and return cleaned rows.

    This file has a different layout from the primary master data file:
      Col 0: Data Domain   (maps to 'domain')
      Col 1: Server        (IDP rows have 'shsdataldevwsql (IDP)')
      Col 2: Database/Schema (operational DB name or IDP schema)
      Col 3: Table         ('dbo.X' for operational, 'schema.X' for IDP)

    For IDP rows (Server == IDP_DEV_SERVER):
      - The Table column is already fully qualified (e.g., 'mdm_core.Product_Dim')
      - database is set to IDP_DATABASE so build_graph_records treats it as IDP
      - schema is extracted from the qualifiedName prefix
      - entity is extracted from the qualifiedName suffix

    For operational rows:
      - 'dbo.' prefix is stripped from the Table column
      - database becomes the DataSystem name
      - schema is 'dbo' (informational only, not used in qualifiedName)
      - entity is the table name after stripping 'dbo.'
    """
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    raw_rows = list(ws.iter_rows(values_only=True))
    wb.close()

    records = []
    for r in raw_rows[1:]:  # skip header
        domain = str(r[0]).strip() if r[0] else None
        server_raw = str(r[1]).strip() if r[1] else None
        db_schema = str(r[2]).strip() if r[2] else None
        table_raw = str(r[3]).strip() if r[3] else None

        if not domain or not db_schema or not table_raw:
            continue  # skip incomplete rows

        # Detect IDP rows by server value
        is_idp = server_raw and IDP_DEV_SERVER.lower() in server_raw.lower()

        if is_idp:
            # IDP row: Table column is already fully qualified (e.g., 'mdm_core.Product_Dim')
            # or may have 'dbo.' prefix for IDP tables listed with dbo schema
            if '.' in table_raw and not table_raw.lower().startswith('dbo.'):
                # Already fully qualified: 'mdm_core.Product_Dim'
                parts = table_raw.split('.', 1)
                schema = parts[0]
                entity = parts[1]
            else:
                # Has 'dbo.' prefix or no dot — use db_schema as the schema
                entity = table_raw.replace('dbo.', '').strip()
                schema = db_schema

            records.append({
                "server": None,  # IDP rows don't create server nodes
                "database": IDP_DATABASE,  # triggers IDP path in build_graph_records
                "schema": schema,
                "domain": domain,
                "entity": entity,
            })
        else:
            # Operational row: strip 'dbo.' prefix from table name
            entity = table_raw
            if entity.lower().startswith('dbo.'):
                entity = entity[4:]  # strip 'dbo.'

            # Canonicalize server and database names
            server = canonicalize_server_name(server_raw)
            database = canonicalize_datasystem_name(db_schema)

            records.append({
                "server": server,
                "database": database,
                "schema": "dbo",  # informational; not used in qualifiedName
                "domain": domain,
                "entity": entity,
            })

    print(f"  Read {len(records)} rows from '{sheet_name}' (after skipping incomplete rows)")
    return records


def deduplicate(records):
    """Deduplicate records based on (database, schema, domain, entity).

    Rules:
      1. Filter out test/QA server rows when a prod row exists for same key.
      2. For remaining duplicates, prefer pgwsql* server, else keep first.
    """
    from collections import defaultdict

    # Group by dedup key
    groups = defaultdict(list)
    for rec in records:
        key = (rec["database"], rec["schema"], rec["domain"], rec["entity"])
        groups[key].append(rec)

    deduped = []
    filtered_test = 0
    filtered_dupe = 0

    for key, recs in groups.items():
        if len(recs) == 1:
            deduped.append(recs[0])
            continue

        # Separate prod and test rows
        prod_recs = [r for r in recs if not is_test_server(r["server"])]
        test_recs = [r for r in recs if is_test_server(r["server"])]
        filtered_test += len(test_recs)

        if not prod_recs:
            # All test — keep first test row (unlikely but defensive)
            deduped.append(test_recs[0])
            filtered_dupe += len(test_recs) - 1
            continue

        if len(prod_recs) == 1:
            deduped.append(prod_recs[0])
            continue

        # Multiple prod rows — prefer pgwsql* server
        pgwsql_recs = [r for r in prod_recs if is_pgwsql_server(r["server"])]
        if pgwsql_recs:
            deduped.append(pgwsql_recs[0])
        else:
            deduped.append(prod_recs[0])
        filtered_dupe += len(prod_recs) - 1

    print(f"  Filtered {filtered_test} test/QA rows, {filtered_dupe} duplicate rows")
    print(f"  {len(deduped)} unique records after deduplication")
    return deduped


def build_graph_records(records, source_file=SOURCE_FILE):
    """Transform cleaned, deduplicated records into graph-ready payloads.

    Args:
      records:     list of dicts from read_and_clean() or read_alteryx_master_data()
      source_file: provenance tag for sourceFile property on created nodes

    Returns:
      domain_records:   list of dicts for MERGE_DOMAIN_QUERY
      op_table_records: list of dicts for MERGE_OP_TABLE_QUERY (operational only)
      idp_stub_records: list of dicts for MERGE_IDP_STUB_QUERY (IDP stubs)
      server_records:   list of dicts for MERGE_SERVER_QUERY (operational only)
      realized_records: list of dicts for REALIZED_IN_QUERY (all)
      refactored_records: list of dicts for REFACTORED_TO_QUERY
    """
    # Unique domains
    domain_names = sorted(set(r["domain"] for r in records))
    domain_records = [{"name": d, "sourceFile": source_file} for d in domain_names]

    op_table_records = []
    idp_stub_records = []
    server_records = []
    realized_records = []
    refactored_records = []

    # Track unique (server, dataSystem) pairs for server wiring
    seen_server_ds = set()
    # Track IDP stub qualifiedNames to avoid duplicates
    seen_idp_stubs = set()

    for rec in records:
        is_idp = rec["database"].lower() == IDP_DATABASE.lower()

        if is_idp:
            # IDP table: qualifiedName = schema.entity
            table_qn = f"{rec['schema']}.{rec['entity']}"

            # Create stub record for IDP tables that may not exist yet
            if table_qn not in seen_idp_stubs:
                seen_idp_stubs.add(table_qn)
                layer = schema_layer(rec["schema"]) or "Unknown"
                idp_stub_records.append({
                    "qualifiedName": table_qn,
                    "tableName": rec["entity"],
                    "layer": layer,
                    "legacy": is_legacy(table_qn, layer),
                    "schemaQN": rec["schema"],
                    "sourceFile": source_file,
                })

            # Check if this is a persistence table with a known IDP equivalent
            if rec["schema"] == "persistence" and table_qn in PERSISTENCE_TO_IDP:
                idp_qn = PERSISTENCE_TO_IDP[table_qn]
                if idp_qn:  # None means no known equivalent
                    refactored_records.append({
                        "legacyQN": table_qn,
                        "idpQN": idp_qn,
                    })
        else:
            # Operational table: qualifiedName = database.entity
            table_qn = f"{rec['database']}.{rec['entity']}"

            # Operational table record
            op_table_records.append({
                "qualifiedName": table_qn,
                "tableName": rec["entity"],
                "dataSystemName": rec["database"],
                "sourceFile": source_file,
            })

            # Server record (deduplicate server->DS pairs)
            if rec["server"]:
                pair = (rec["server"], rec["database"])
                if pair not in seen_server_ds:
                    seen_server_ds.add(pair)
                    server_records.append({
                        "serverName": rec["server"],
                        "dataSystemName": rec["database"],
                    })

        # REALIZED_IN for all rows
        realized_records.append({
            "domainName": rec["domain"],
            "tableQN": table_qn,
        })

    print(f"  Domains: {len(domain_records)}")
    print(f"  Operational tables to create/merge: {len(op_table_records)}")
    print(f"  IDP stub tables to create/merge: {len(idp_stub_records)}")
    print(f"  Server->DataSystem pairs: {len(server_records)}")
    print(f"  REALIZED_IN edges to create: {len(realized_records)}")
    print(f"  REFACTORED_TO edges to create: {len(refactored_records)}")

    return domain_records, op_table_records, idp_stub_records, server_records, realized_records, refactored_records


def _merge_graph_payloads(*payloads):
    """Merge multiple build_graph_records() outputs, deduplicating domains and server pairs."""
    domain_recs, op_recs, idp_recs, srv_recs, real_recs, refac_recs = [], [], [], [], [], []
    seen_domains, seen_srv = set(), set()
    for (d, o, i, s, r, f) in payloads:
        for rec in d:
            if rec["name"] not in seen_domains:
                seen_domains.add(rec["name"])
                domain_recs.append(rec)
        op_recs.extend(o)
        idp_recs.extend(i)
        for rec in s:
            pair = (rec["serverName"], rec["dataSystemName"])
            if pair not in seen_srv:
                seen_srv.add(pair)
                srv_recs.append(rec)
        real_recs.extend(r)
        refac_recs.extend(f)
    return domain_recs, op_recs, idp_recs, srv_recs, real_recs, refac_recs


def main():
    print("=" * 60)
    print("load_master_data.py — MasterDataDomain + REALIZED_IN")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1a: File 1 — primary master data
    # ------------------------------------------------------------------
    print("\nStep 1a: Reading File 1 (List of Master Data)...")
    recs1 = read_and_clean(EXCEL_PATH, SHEET_NAME)
    print("  Deduplicating...")
    recs1 = deduplicate(recs1)
    print("  Building graph records...")
    payload1 = build_graph_records(recs1, source_file=SOURCE_FILE)

    # ------------------------------------------------------------------
    # Step 1b: File 2 — Alteryx master data requirements
    # ------------------------------------------------------------------
    print("\nStep 1b: Reading File 2 (Alteryx Master Data Requirements)...")
    recs2 = read_alteryx_master_data(ALTERYX_MD_EXCEL_PATH, ALTERYX_MD_SHEET_NAME)
    print("  Deduplicating...")
    recs2 = deduplicate(recs2)
    print("  Building graph records...")
    payload2 = build_graph_records(recs2, source_file=ALTERYX_MD_SOURCE_FILE)

    # ------------------------------------------------------------------
    # Step 2: Merge payloads from both files
    # ------------------------------------------------------------------
    print("\nStep 2: Merging payloads from both files...")
    (domain_recs, op_table_recs, idp_stub_recs,
     server_recs, realized_recs, refactored_recs) = _merge_graph_payloads(payload1, payload2)
    print(f"  Combined totals:")
    print(f"    Domains:           {len(domain_recs)}")
    print(f"    Operational tables: {len(op_table_recs)}")
    print(f"    IDP stubs:         {len(idp_stub_recs)}")
    print(f"    Server->DS pairs:  {len(server_recs)}")
    print(f"    REALIZED_IN edges: {len(realized_recs)}")
    print(f"    REFACTORED_TO:     {len(refactored_recs)}")

    # Step 3: Connect to Neo4j and load
    print("\nStep 3: Connecting to Neo4j...")
    loader = Neo4jLoader()

    # Canonicalize table qualifiedNames to prevent case-variant duplicates.
    # Fetches all existing Table nodes and reuses their casing.
    print("  Building Table qualifiedName lookup for case-insensitive dedup...")
    qn_lookup = loader.build_table_qn_lookup()
    canon = lambda qn: Neo4jLoader.canonicalize_table_qn(qn, qn_lookup)
    canonicalized = 0
    for rec in op_table_recs:
        new_qn = canon(rec["qualifiedName"])
        if new_qn != rec["qualifiedName"]:
            canonicalized += 1
            rec["qualifiedName"] = new_qn
    for rec in idp_stub_recs:
        new_qn = canon(rec["qualifiedName"])
        if new_qn != rec["qualifiedName"]:
            canonicalized += 1
            rec["qualifiedName"] = new_qn
    for rec in realized_recs:
        new_qn = canon(rec["tableQN"])
        if new_qn != rec["tableQN"]:
            rec["tableQN"] = new_qn
    if canonicalized:
        print(f"  Canonicalized {canonicalized} qualifiedName(s) to match existing nodes.")

    # Constraint
    print("\n  Creating MasterDataDomain constraint...")
    loader.run_write(DOMAIN_CONSTRAINT)

    # Create MasterDataDomain nodes
    print(f"\n  Creating {len(domain_recs)} MasterDataDomain node(s)...")
    loader.write_batches(MERGE_DOMAIN_QUERY, domain_recs)

    # Create IDP stub tables (ensures missing IDP tables exist before REALIZED_IN)
    print(f"\n  Creating/merging {len(idp_stub_recs)} IDP stub Table node(s)...")
    loader.write_batches(MERGE_IDP_STUB_QUERY, idp_stub_recs)

    # Create operational tables and wire to DataSystem
    print(f"  Creating/merging {len(op_table_recs)} operational Table node(s)...")
    loader.write_batches(MERGE_OP_TABLE_QUERY, op_table_recs)

    # Wire servers
    print(f"  Wiring {len(server_recs)} Server->DataSystem pair(s)...")
    loader.write_batches(MERGE_SERVER_QUERY, server_recs)

    # Wire REALIZED_IN (case-insensitive matching)
    print(f"\n  Wiring {len(realized_recs)} REALIZED_IN edge(s)...")
    loader.write_batches(REALIZED_IN_QUERY, realized_recs)

    # Wire REFACTORED_TO for persistence -> IDP tables
    if refactored_recs:
        print(f"  Wiring {len(refactored_recs)} REFACTORED_TO edge(s)...")
        loader.write_batches(REFACTORED_TO_QUERY, refactored_recs)

    # Step 4: Verification
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    # Domain count
    results = loader.run_query("MATCH (mdd:MasterDataDomain) RETURN count(mdd) AS cnt")
    print(f"\n  MasterDataDomain nodes: {results[0]['cnt']}")

    # REALIZED_IN count
    results = loader.run_query(
        "MATCH (:MasterDataDomain)-[r:REALIZED_IN]->(:Table) RETURN count(r) AS cnt"
    )
    print(f"  REALIZED_IN edges: {results[0]['cnt']}")

    # Fragmentation summary
    print("\n  Fragmentation summary (implementations per domain):")
    results = loader.run_query("""
        MATCH (mdd:MasterDataDomain)-[:REALIZED_IN]->(t:Table)
        RETURN mdd.name AS domain, mdd.status AS status, count(t) AS implementations
        ORDER BY implementations DESC
    """)
    for r in results:
        print(f"    {r['domain']:<15} status={r['status']:<12} implementations={r['implementations']}")

    # REFACTORED_TO verification
    if refactored_recs:
        results = loader.run_query(
            "MATCH ()-[r:REFACTORED_TO]->() RETURN count(r) AS cnt"
        )
        print(f"  REFACTORED_TO edges: {results[0]['cnt']}")

    # Check for unmatched REALIZED_IN (domain or table not found)
    print("\n  Checking for unmatched REALIZED_IN targets...")
    expected = len(realized_recs)
    actual = loader.run_query(
        "MATCH (:MasterDataDomain)-[r:REALIZED_IN]->(:Table) RETURN count(r) AS cnt"
    )[0]["cnt"]
    if actual < expected:
        print(f"  WARNING: Expected {expected} REALIZED_IN edges, but only {actual} created.")
        print("  Some Table nodes may not exist in the graph. Investigating...")
        # Find which tables are missing (case-insensitive check)
        for rec in realized_recs:
            check = loader.run_query(
                "MATCH (t:Table) WHERE toLower(t.qualifiedName) = toLower($qn) RETURN count(t) AS cnt",
                qn=rec["tableQN"],
            )
            if check[0]["cnt"] == 0:
                print(f"    MISSING: {rec['tableQN']} (domain: {rec['domainName']})")
    else:
        print(f"  All {actual} REALIZED_IN edges created successfully.")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
