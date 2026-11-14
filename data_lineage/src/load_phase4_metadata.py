"""
Phase 4 Metadata Loader.
Loads master mapping metadata from Data/Phase4_Entities_with_UDM_Naming_Convention.xlsx
into the Neo4j knowledge graph database (governancemetadata).

Bypasses locked files by copying to a temp location via PowerShell fallback,
filters out cells with strikethroughs programmatically,
handles 'dbo' to conformed 'replica_' layer mapping,
and processes data portfolios (except IT, Legal, Finance, ES&S) into CapabilityDataDomain links.
"""

import os
import sys
import openpyxl
from dotenv import load_dotenv

# Resolve paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

from excel_cells import readable_copy
from medallion import is_legacy, is_legacy_schema, schema_layer
from neo4j_loader import Neo4jLoader, canonicalize_server_name

EXCEL_FILE = os.path.join(PROJECT_ROOT, "Data", "Phase4_Entities_with_UDM_Naming_Convention.xlsx")
SHEET_NAME = "Entities with UDM column names"

def load_phase4_metadata():
    print("Reading Excel sheet using openpyxl...")
    with readable_copy(EXCEL_FILE) as excel_copy:
        wb = openpyxl.load_workbook(excel_copy, data_only=True)

    try:
        if SHEET_NAME not in wb.sheetnames:
            print(f"Error: Sheet '{SHEET_NAME}' not found in Excel workbook.")
            return
        
        sheet = wb[SHEET_NAME]
        
        # Read header row
        header = [cell.value for cell in sheet[1]]
        print("Headers found:", header)
        
        # Get column indices
        try:
            idx_portfolio = header.index("Data Portfolio")
            idx_server = header.index("Server")
            idx_database = header.index("Database")
            idx_entities = header.index("Entities")
            idx_source = header.index("Source")
            idx_phys_table = header.index("Physical Table Name")
            idx_source_field = header.index("Source Field Name")
            idx_source_type = header.index("Source Data Type")
            idx_silver_field = header.index("Silver Layer Field Name")
            idx_data_type = header.index("Data Type")
            idx_keys = header.index("Keys")
            idx_transformations = header.index("Transformations")
        except ValueError as e:
            print(f"Error mapping headers: {e}")
            return
        
        # Read all rows (skip header row 1)
        records = []
        skipped_strikethrough = 0
        skipped_empty_phys_table = 0
        
        for row_num in range(2, sheet.max_row + 1):
            row_cells = list(sheet[row_num])
            if not row_cells or all(c.value is None for c in row_cells):
                continue
            
            # Check for strikethrough in 'Physical Table Name' or 'Entities' or any core cells
            # We strictly check if the row has a strikethrough in Physical Table Name or Silver Layer Field Name
            phys_cell = row_cells[idx_phys_table]
            silver_cell = row_cells[idx_silver_field]
            
            if (phys_cell.font and phys_cell.font.strike) or (silver_cell.font and silver_cell.font.strike):
                skipped_strikethrough += 1
                continue
            
            phys_table = phys_cell.value
            if not phys_table or str(phys_table).strip() == "":
                skipped_empty_phys_table += 1
                continue
            
            # Extract values
            portfolio = row_cells[idx_portfolio].value
            server = row_cells[idx_server].value
            database = row_cells[idx_database].value
            entities = row_cells[idx_entities].value
            source = row_cells[idx_source].value
            source_field = row_cells[idx_source_field].value
            source_type = row_cells[idx_source_type].value
            silver_field = silver_cell.value
            data_type = row_cells[idx_data_type].value
            keys = row_cells[idx_keys].value
            transformations = row_cells[idx_transformations].value
            
            records.append({
                "portfolio": str(portfolio).strip() if portfolio else None,
                "server": str(server).strip() if server else None,
                "database": str(database).strip() if database else None,
                "entities": str(entities).strip() if entities else None,
                "source": str(source).strip() if source else None,
                "phys_table": str(phys_table).strip(),
                "source_field": str(source_field).strip() if source_field else None,
                "source_type": str(source_type).strip() if source_type else None,
                "silver_field": str(silver_field).strip() if silver_field else None,
                "data_type": str(data_type).strip() if data_type else None,
                "keys": str(keys).strip() if keys else None,
                "transformations": str(transformations).strip() if transformations else None,
                "row_num": row_num
            })
            
        print(f"Total rows parsed: {len(records)}")
        print(f"Skipped strike-through rows: {skipped_strikethrough}")
        print(f"Skipped empty Physical Table Name rows: {skipped_empty_phys_table}")
        
        # Initialize Loader
        loader = Neo4jLoader()
        
        # Build casing lookup for Table qualifiedNames
        table_lookup = loader.build_table_qn_lookup()
        
        # Process and build ingestion lists
        servers_set = set()
        systems_set = set()
        schemas_set = set()
        tables_map = {} # qualifiedName -> table_info
        columns_map = {} # qualifiedName -> column_info
        
        # Relationship lists
        server_system_edges = set()     # (server, system)
        system_table_edges = set()      # (system, table_qn)
        table_replicated_edges = set()  # (op_table_qn, replica_table_qn)
        table_derived_edges = set()     # (silver_table_qn, replica_table_qn)
        table_column_edges = set()      # (table_qn, col_qn)
        column_derived_edges = set()    # (silver_col_qn, replica_col_qn)
        portfolio_table_edges = set()   # (portfolio_name, table_qn)
        
        for r in records:
            # 1. Server mapping & canonicalization
            srv_raw = r["server"]
            srv_canon = canonicalize_server_name(srv_raw) if srv_raw else None
            
            # 2. DataSystem name from Database
            db_raw = r["database"]
            ds_name = db_raw.strip() if db_raw else None
            
            if srv_canon and ds_name:
                servers_set.add(srv_canon)
                systems_set.add(ds_name)
                server_system_edges.add((srv_canon, ds_name))
            
            # 3. Operational schema/table handling
            # Operational schema is the Database name
            op_schema = ds_name
            op_table_name = r["entities"] if r["entities"] else r["phys_table"]
            op_table_qn = f"{op_schema}.{op_table_name}" if op_schema and op_table_name else None
            
            # 4. Replica schema/table handling
            source_raw = r["source"]
            if source_raw:
                source_clean = source_raw.strip()
                if source_clean.lower() == "dbo":
                    # Do NOT load "dbo" schema replicas
                    rep_schema = None
                else:
                    rep_schema = source_clean
            else:
                rep_schema = None
                
            rep_table_qn = f"{rep_schema}.{op_table_name}" if rep_schema and op_table_name else None
            
            # 5. Silver/Gold schema/table handling
            # Physical Table Name is the Silver/Gold table qualifiedName
            sg_table_qn = r["phys_table"]
            sg_parts = sg_table_qn.split(".")
            sg_schema = sg_parts[0] if len(sg_parts) > 1 else None
            sg_table_name = sg_parts[1] if len(sg_parts) > 1 else sg_table_qn
            
            # Set layers and canonicalize
            if sg_schema:
                schemas_set.add(sg_schema)
            if op_schema:
                schemas_set.add(op_schema)
            if rep_schema:
                schemas_set.add(rep_schema)
                
            # canonicalize qualifiedNames with existing casing lookup
            op_table_qn = Neo4jLoader.canonicalize_table_qn(op_table_qn, table_lookup)
            rep_table_qn = Neo4jLoader.canonicalize_table_qn(rep_table_qn, table_lookup)
            sg_table_qn = Neo4jLoader.canonicalize_table_qn(sg_table_qn, table_lookup)
            
            sg_layer = schema_layer(sg_schema) or "Silver"
            
            # Safe table registration
            if op_table_qn:
                tables_map[op_table_qn] = {
                    "qualifiedName": op_table_qn,
                    "name": op_table_name,
                    "layer": "Operational",
                    "role": "Table"
                }
                if ds_name:
                    system_table_edges.add((ds_name, op_table_qn))
                    
            if rep_table_qn:
                tables_map[rep_table_qn] = {
                    "qualifiedName": rep_table_qn,
                    "name": op_table_name,
                    "layer": "Replica",
                    "role": "Table"
                }
                if op_table_qn:
                    table_replicated_edges.add((op_table_qn, rep_table_qn))
                    
            if sg_table_qn:
                # Deduce dimensionalRole from casing or legacy rules
                # Default role
                role = "Table"
                if "union" in sg_table_name.lower():
                    role = "Dimension" # Typically union dims
                tables_map[sg_table_qn] = {
                    "qualifiedName": sg_table_qn,
                    "name": sg_table_name,
                    "layer": sg_layer,
                    "role": role
                }
                if rep_table_qn:
                    table_derived_edges.add((sg_table_qn, rep_table_qn))
                    
            # 6. Column-level structures
            src_field = r["source_field"]
            sl_field = r["silver_field"]
            
            # Operational Column
            if op_table_qn and src_field:
                op_col_qn = f"{op_table_qn}.{src_field}"
                columns_map[op_col_qn] = {
                    "qualifiedName": op_col_qn,
                    "name": src_field,
                    "dataType": r["source_type"]
                }
                table_column_edges.add((op_table_qn, op_col_qn))
                
            # Replica Column
            if rep_table_qn and src_field:
                rep_col_qn = f"{rep_table_qn}.{src_field}"
                columns_map[rep_col_qn] = {
                    "qualifiedName": rep_col_qn,
                    "name": src_field,
                    "dataType": r["source_type"]
                }
                table_column_edges.add((rep_table_qn, rep_col_qn))
                
            # Silver/Gold Column & lineage mapping
            if sg_table_qn and sl_field:
                sg_col_qn = f"{sg_table_qn}.{sl_field}"
                
                # Check for primary key designation
                key_type = r["keys"]
                is_pk = False
                if key_type and any(pk in key_type.upper() for pk in ["PK", "PKEY", "PRIMARY"]):
                    is_pk = True
                    
                columns_map[sg_col_qn] = {
                    "qualifiedName": sg_col_qn,
                    "name": sl_field,
                    "dataType": r["data_type"],
                    "isPrimaryKey": is_pk,
                    "transformation": r["transformations"]
                }
                table_column_edges.add((sg_table_qn, sg_col_qn))
                
                # Wire column lineage
                if rep_table_qn and src_field:
                    rep_col_qn = f"{rep_table_qn}.{src_field}"
                    column_derived_edges.add((sg_col_qn, rep_col_qn))
            
            # 7. Portfolio (CapabilityDataDomain) rules
            portfolio_name = r["portfolio"]
            if portfolio_name:
                # 1. Clean multi-line values split by newlines
                lines = [line.strip() for line in str(portfolio_name).split('\n') if line.strip()]
                
                for line in lines:
                    if line.lower() == 'nan' or line.strip() == '':
                        continue
                        
                    p_clean = line.strip()
                    
                    # 2. Skip non-portfolio categories
                    if p_clean.lower() == 'tas_datawarehouse migration to idp':
                        continue
                    
                    # 3. Strip standard prefixes like "M&S - " or "P&O - "
                    prefixes = ["m&s -", "p&o -", "ms&lm -"]
                    p_lower = p_clean.lower()
                    for pref in prefixes:
                        if p_lower.startswith(pref):
                            p_clean = p_clean[len(pref):].strip()
                            p_lower = p_clean.lower()
                            break
                    
                    # 4. Conform Terminals Ops / Terminal Operations / Terminals - Terminal Ops -> Terminal Ops
                    if p_clean.lower() in ["terminals ops", "terminals op", "terminal operations", "terminals - terminal ops", "terminals-terminal ops"]:
                        p_clean = "Terminal Ops"
                        p_lower = p_clean.lower()
                    
                    bypass_domains = ["it", "legal", "finance", "es&s", "es&s - safety", "es&s - environmental", "it - security"]
                    root_prefix = p_lower.split("-")[0].strip()
                    if root_prefix not in bypass_domains and p_lower not in bypass_domains:
                        if sg_table_qn:
                            portfolio_table_edges.add((p_clean, sg_table_qn))

        # ── Step 1: Bulk Ingest Servers ──────────────────────────────────────
        print(f"Loading {len(servers_set)} Server nodes...")
        srv_rows = [{"serverName": s} for s in servers_set]
        srv_query = """
        UNWIND $rows AS row
        MERGE (srv:Server {serverName: row.serverName})
        ON CREATE SET srv.createdAt = datetime()
        """
        loader.write_batches(srv_query, srv_rows)
            
        # ── Step 2: Bulk Ingest DataSystems ──────────────────────────────────
        print(f"Loading {len(systems_set)} DataSystem nodes...")
        sys_rows = [{"name": s} for s in systems_set]
        sys_query = """
        UNWIND $rows AS row
        MERGE (ds:DataSystem {name: row.name})
        ON CREATE SET ds.createdAt = datetime()
        """
        loader.write_batches(sys_query, sys_rows)

        # ── Step 3: Wire Server to DataSystem ────────────────────────────────
        print(f"Wiring {len(server_system_edges)} Server -> DataSystem edges...")
        srv_ds_rows = [{"serverName": s, "systemName": d} for s, d in server_system_edges]
        srv_ds_query = """
        UNWIND $rows AS row
        MATCH (srv:Server {serverName: row.serverName})
        MATCH (ds:DataSystem {name: row.systemName})
        MERGE (srv)-[r:HOSTS]->(ds)
        """
        loader.write_batches(srv_ds_query, srv_ds_rows)

        # ── Step 4: Bulk Schema Registration ──────────────────────────────────
        print(f"Loading {len(schemas_set)} Schema nodes...")
        schema_rows = [
            {"qualifiedName": s, "layer": schema_layer(s) or "Silver", "legacy": is_legacy_schema(s)}
            for s in schemas_set
        ]
        schema_query = """
        UNWIND $rows AS row
        MERGE (s:Schema {qualifiedName: row.qualifiedName})
        ON CREATE SET s.name = row.qualifiedName,
                      s.layer = row.layer,
                      s.createdAt = datetime()
        FOREACH (ignore IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET s:Legacy)
        """
        loader.write_batches(schema_query, schema_rows)

        # ── Step 5: Bulk Table Insertion ──────────────────────────────────────
        # Segment by dimensional role to support multi-labels
        print(f"Loading {len(tables_map)} Table nodes...")
        tables_list = [{**t, "legacy": is_legacy(t["qualifiedName"], t["layer"])} for t in tables_map.values()]
        
        # Query supporting dynamic legacy assignment
        table_query = """
        UNWIND $rows AS row
        MERGE (t:Table {qualifiedName: row.qualifiedName})
        ON CREATE SET t.name = row.name,
                      t.layer = row.layer,
                      t.createdAt = datetime()
        ON MATCH SET t.updatedAt = datetime()
        WITH t, row
        
        // Dynamic Role assignment
        FOREACH (ignore IN CASE WHEN row.role = 'Dimension' THEN [1] ELSE [] END | SET t:Dimension)
        FOREACH (ignore IN CASE WHEN row.role = 'Fact' THEN [1] ELSE [] END | SET t:Fact)
        FOREACH (ignore IN CASE WHEN row.role = 'View' THEN [1] ELSE [] END | SET t:View)
        
        FOREACH (ignore IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET t:Legacy)
        
        WITH t, row
        MATCH (s:Schema {qualifiedName: split(row.qualifiedName, '.')[0]})
        MERGE (s)-[:CONTAINS]->(t)
        """
        loader.write_batches(table_query, tables_list)

        # ── Step 6: System Contains Table Lineage ─────────────────────────────
        print(f"Wiring {len(system_table_edges)} System -> Operational Table edges...")
        sys_tab_rows = [{"system": sys, "table": tab} for sys, tab in system_table_edges]
        sys_tab_query = """
        UNWIND $rows AS row
        MATCH (ds:DataSystem {name: row.system})
        MATCH (t:Table {qualifiedName: row.table})
        MERGE (ds)-[:CONTAINS]->(t)
        """
        loader.write_batches(sys_tab_query, sys_tab_rows)

        # ── Step 7: Wire Table Lineage (REPLICATED_TO, DERIVED_FROM) ──────────
        print(f"Wiring {len(table_replicated_edges)} Operational -> Replica Table edges...")
        rep_edges_rows = [{"op": op, "rep": rep} for op, rep in table_replicated_edges]
        rep_edges_query = """
        UNWIND $rows AS row
        MATCH (op:Table {qualifiedName: row.op})
        MATCH (rep:Table {qualifiedName: row.rep})
        MERGE (op)-[:REPLICATED_TO]->(rep)
        """
        loader.write_batches(rep_edges_query, rep_edges_rows)

        print(f"Wiring {len(table_derived_edges)} Silver/Gold -> Replica Table edges...")
        der_edges_rows = [{"sg": sg, "rep": rep} for sg, rep in table_derived_edges]
        der_edges_query = """
        UNWIND $rows AS row
        MATCH (sg:Table {qualifiedName: row.sg})
        MATCH (rep:Table {qualifiedName: row.rep})
        MERGE (sg)-[:DERIVED_FROM]->(rep)
        """
        loader.write_batches(der_edges_query, der_edges_rows)

        # ── Step 8: Bulk Column Insertion ─────────────────────────────────────
        print(f"Loading {len(columns_map)} Column nodes...")
        cols_list = list(columns_map.values())
        col_query = """
        UNWIND $rows AS row
        MERGE (c:Column {qualifiedName: row.qualifiedName})
        ON CREATE SET c.name = row.name,
                      c.dataType = row.dataType,
                      c.isPrimaryKey = COALESCE(row.isPrimaryKey, false),
                      c.transformation = row.transformation,
                      c.createdAt = datetime()
        ON MATCH SET c.dataType = COALESCE(row.dataType, c.dataType),
                     c.isPrimaryKey = COALESCE(row.isPrimaryKey, c.isPrimaryKey),
                     c.transformation = COALESCE(row.transformation, c.transformation),
                     c.updatedAt = datetime()
        """
        loader.write_batches(col_query, cols_list)

        # ── Step 9: Wire Column to Table edges ────────────────────────────────
        print(f"Wiring {len(table_column_edges)} Table -> Column edges...")
        tab_col_rows = [{"table": tab, "col": col} for tab, col in table_column_edges]
        tab_col_query = """
        UNWIND $rows AS row
        MATCH (t:Table {qualifiedName: row.table})
        MATCH (c:Column {qualifiedName: row.col})
        MERGE (t)-[:HAS_COLUMN]->(c)
        """
        loader.write_batches(tab_col_query, tab_col_rows)

        # ── Step 10: Wire Column Lineage (DERIVED_FROM) ───────────────────────
        print(f"Wiring {len(column_derived_edges)} Column-to-Column lineages...")
        col_der_rows = [{"sg_col": sg, "rep_col": rep} for sg, rep in column_derived_edges]
        col_der_query = """
        UNWIND $rows AS row
        MATCH (sg:Column {qualifiedName: row.sg_col})
        MATCH (rep:Column {qualifiedName: row.rep_col})
        MERGE (sg)-[:DERIVED_FROM]->(rep)
        """
        loader.write_batches(col_der_query, col_der_rows)

        # ── Step 11: Link Table to CapabilityDataDomain (Portfolio) ───────────
        print(f"Wiring {len(portfolio_table_edges)} Table -> CapabilityDataDomain edges...")
        port_tab_rows = [{"domain": dom, "table": tab} for dom, tab in portfolio_table_edges]
        port_tab_query = """
        UNWIND $rows AS row
        MERGE (cdd:CapabilityDataDomain {name: row.domain})
        WITH cdd, row
        MATCH (t:Table {qualifiedName: row.table})
        MERGE (t)-[:BELONGS_TO]->(cdd)
        """
        loader.write_batches(port_tab_query, port_tab_rows)

        print("\nIngest complete! Running dynamic post-processing validations...")
        
        # Verification counts
        print("\nNodes validation counts:")
        loader.verify("MATCH (n:Server) RETURN 'Server' as label, count(n) as count")
        loader.verify("MATCH (n:DataSystem) RETURN 'DataSystem' as label, count(n) as count")
        loader.verify("MATCH (n:Schema) RETURN 'Schema' as label, count(n) as count")
        loader.verify("MATCH (n:Table) RETURN 'Table' as label, count(n) as count")
        loader.verify("MATCH (n:Column) RETURN 'Column' as label, count(n) as count")
        loader.verify("MATCH (n:CapabilityDataDomain) RETURN 'CapabilityDataDomain' as label, count(n) as count")
        
        loader.close()

    finally:
        wb.close()

if __name__ == "__main__":
    load_phase4_metadata()
