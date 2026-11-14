"""
Ingest Power BI Dataset and Report Lineage into Neo4j Knowledge Graph.

Creates:
  1. Server infrastructure nodes
  2. DataSystem nodes
  3. Schema & Table nodes (conformed medallion Views)
  4. BusinessArea nodes
  5. Report nodes (tagged with workspace and metadata)
  6. RoleAssignment nodes (for report creators)
  7. consumption (:CONSUMES) edges connecting Report -> Table

Pruning:
  Uses a session-level runStart UTC timestamp to automatically identify and delete
  stale Report nodes and CONSUMES edges that no longer exist in the source databases.

Source:
  --source (or SOURCE_DB_URL) is any SQLAlchemy URL holding the sem_internal_x export tables:
  DuckDB, Postgres or SQL Server (Express and Developer editions work). Without one, the
  script reads the IDP over SQL Server with MFA. The generated synthetic catalog ships one
  at synthetic_data/source.duckdb.

Usage:
    python src/load_powerbi_lineage.py --database lsc --source duckdb:///synthetic_data/source.duckdb
"""

import argparse
import os
import sys
import re
import logging
from pathlib import Path
from datetime import datetime, timezone
import polars as pl
from dotenv import load_dotenv

# Setup paths relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Append internal project folders to sys.path
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "src"))
sys.path.append(os.path.join(PROJECT_ROOT, "db_connect", "src"))

from connect import query_database, query_sql_server_mfa_idp
from medallion import is_idp_schema, stamp_report_keys
from neo4j_loader import ENV_PATH as CREDENTIALS_PATH, Neo4jLoader

load_dotenv(dotenv_path=Path(PROJECT_ROOT) / ".env")
load_dotenv(dotenv_path=CREDENTIALS_PATH)

IDP_SERVER = "lsc-idp-prod.sql.azuresynapse.net"
IDP_DATABASE = "LSC Data Platform (IDP)"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_source_query(query: str, source_url: str | None) -> pl.DataFrame:
    if source_url:
        return pl.from_pandas(query_database(query, source_url))
    _, rel = query_sql_server_mfa_idp(
        query=query, environment="prod", write_to_duckdb=False, duckdb_table=None,
        duckdb_path=":memory:", log_level=logging.ERROR,
    )
    return rel.pl()


def extract_powerbi_metadata(source_url: str | None = None) -> pl.DataFrame:
    """Extract raw Power BI dataset and report metadata from the source database."""
    logging.info("Stage 1: Extracting raw dataset-to-report metadata...")

    query = """
    SELECT 
        pbid.Workspace_Name, 
        pbir.Creator_Principal_Display_Name, 
        pbir.Report_Name, 
        pbid.Table_Name AS PBI_Table_Name, 
        pbid.Source_Text AS Expression,
        pbid.Connection_Type_Code, 
        pbid.Dataset_Id,
        pbid.Server_Name, 
        pbid.Database_File_Name AS "Database",
        pbid.Schema_Name, 
        pbid.View_Name, 
        pbir.State_Code, 
        pbir.Web_Url_Text, 
        pbir.Embed_Url_Text
    FROM sem_internal_x.PowerBi_Dataset_Table_Dim_vw  pbid
    INNER JOIN sem_internal_x.PowerBi_Report_Dim_vw  pbir
      ON pbid.Dataset_Id = pbir.Dataset_Id
    WHERE Schema_Name IS NOT NULL 
      AND Schema_Name NOT IN ('None', 'nan', '')
      AND View_Name IS NOT NULL 
      AND View_Name NOT IN ('None', 'nan', '')
    """

    df_pl = run_source_query(query, source_url)
    logging.info(f"  Extracted {len(df_pl)} raw metadata rows successfully.")
    return df_pl


def clean_and_map_schemas_views(df_raw: pl.DataFrame, source_url: str | None = None) -> pl.DataFrame:
    """Conform, split, and map schemas/views with ground-truth catalog validation."""
    logging.info("Stage 2: Cleansing, exploding, and mapping views to schemas...")
    
    if df_raw.height == 0:
        return pl.DataFrame(schema=df_raw.schema)

    meta_query = """
    SELECT TABLE_SCHEMA AS Schema_Name, TABLE_NAME AS View_Name
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'VIEW'
      AND (TABLE_SCHEMA LIKE 'sem_%' OR TABLE_SCHEMA LIKE 'replica_%' OR TABLE_SCHEMA = 'dbo')
    """
    view_to_schema_map = {
        str(row["View_Name"]).lower(): str(row["Schema_Name"])
        for row in run_source_query(meta_query, source_url).iter_rows(named=True)
    }

    area_query = "SELECT Schema_Name, Business_Area FROM sem_internal_x.Schema_Business_Area_vw"
    business_area_map = {
        str(row["Schema_Name"]).lower(): row["Business_Area"]
        for row in run_source_query(area_query, source_url).iter_rows(named=True)
    }

    # 2. Iterate, split, explode and apply conformance heuristics
    mapped_rows = []
    delimiter_pattern = re.compile(r"[,;\n\r\t/|]")

    for row in df_raw.iter_rows(named=True):
        schema_val = str(row.get("Schema_Name", "") or "")
        view_val = str(row.get("View_Name", "") or "")

        if delimiter_pattern.search(schema_val) or delimiter_pattern.search(view_val):
            schemas = [s.strip() for s in schema_val.split(",") if s.strip()]
            views = [v.strip() for v in view_val.split(",") if v.strip()]
            schemas_lower = {s.lower() for s in schemas}

            for view in views:
                view_lower = view.lower()
                mapped_schema = view_to_schema_map.get(view_lower)

                if mapped_schema and mapped_schema.lower() in schemas_lower:
                    status = "Mapped"
                else:
                    mapped_schema = schemas[0] if schemas else None
                    status = "Fallback (Not in Catalog)"

                new_row = row.copy()
                new_row["Schema_Name"] = mapped_schema
                new_row["View_Name"] = view
                new_row["Mapping_Status"] = status

                # Apply Synapse defaults for medallion layers if empty
                s_lower = (mapped_schema or "").lower()
                if is_idp_schema(s_lower):
                    srv = new_row.get("Server_Name")
                    db = new_row.get("Database")
                    if not srv or str(srv).strip() in ("None", "", "nan"):
                        new_row["Server_Name"] = IDP_SERVER
                    if not db or str(db).strip() in ("None", "", "nan"):
                        new_row["Database"] = IDP_DATABASE

                new_row["Business Area"] = business_area_map.get(s_lower, None)
                mapped_rows.append(new_row)
        else:
            new_row = row.copy()
            new_row["Mapping_Status"] = "Clean"

            s_lower = (schema_val or "").lower()
            if is_idp_schema(s_lower):
                srv = new_row.get("Server_Name")
                db = new_row.get("Database")
                if not srv or str(srv).strip() in ("None", "", "nan"):
                    new_row["Server_Name"] = IDP_SERVER
                if not db or str(db).strip() in ("None", "", "nan"):
                    new_row["Database"] = IDP_DATABASE

            new_row["Business Area"] = business_area_map.get(s_lower, None)
            mapped_rows.append(new_row)

    df_conformed = pl.DataFrame(mapped_rows)
    logging.info(f"  Exploded raw rows into {len(df_conformed)} conformed rows.")
    return df_conformed


def ingest_lineage_to_neo4j(df_conformed: pl.DataFrame, database: str):
    """Load conformed lineage to Neo4j transactionally and prune stale structures."""
    logging.info(f"Stage 3: Loading conformed dataset lineage into '{database}'...")

    run_start = datetime.now(timezone.utc).isoformat()
    loader = Neo4jLoader(database=database)
    
    batch_size = 500
    rows = df_conformed.to_dicts()
    qn_lookup = loader.build_table_qn_lookup()
    for row in rows:
        schema_name = row.get("Schema_Name")
        view_name = row.get("View_Name")
        if schema_name and view_name:
            row["qualifiedName"] = Neo4jLoader.canonicalize_table_qn(
                f"{schema_name}.{view_name}", qn_lookup
            )
    stamp_report_keys(rows, loader.build_report_key_lookup(), "Report_Name", "Web_Url_Text")

    # Uniqueness-aware safe merging Cypher Query
    cypher_ingest = """
    UNWIND $rows AS row

    // Infrastructure
    WITH row WHERE row.Server_Name IS NOT NULL AND row.Database IS NOT NULL
    MERGE (srv:Server {serverName: row.Server_Name})
    MERGE (ds:DataSystem {name: row.Database})
    MERGE (srv)-[:HOSTS]->(ds)

    // Schema & Table (Semantic Views)
    WITH row, ds
    WHERE row.Schema_Name IS NOT NULL AND row.View_Name IS NOT NULL
    MERGE (sch:Schema {qualifiedName: row.Schema_Name})
    ON CREATE SET sch.layer = "Semantic"
    MERGE (ds)-[:HOSTS]->(sch)

    MERGE (t:Table {qualifiedName: row.qualifiedName})
    ON CREATE SET t.name = row.View_Name,
                  t.layer = "Semantic",
                  t.createdAt = datetime()
    ON MATCH SET t.updatedAt = datetime()
    SET t:View
    MERGE (sch)-[:CONTAINS]->(t)

    // Business Area
    WITH row, ds, sch, t
    FOREACH (ba_name IN CASE WHEN row['Business Area'] IS NOT NULL THEN [row['Business Area']] ELSE [] END |
        MERGE (ba:BusinessArea {name: ba_name})
        MERGE (ds)-[:BELONGS_TO]->(ba)
        MERGE (sch)-[:BELONGS_TO]->(ba)
    )

    // Power BI Report (Tagged with runStart and source)
    WITH row, t
    MERGE (rpt:Report {reportKey: row.reportKey})
    ON CREATE SET rpt.name = row.Report_Name,
                  rpt.connectionType = row.Connection_Type_Code,
                  rpt.webUrl = row.Web_Url_Text,
                  rpt.state = row.State_Code,
                  rpt.workspaceName = row.Workspace_Name,
                  rpt.source = "PowerBI_Workspace",
                  rpt.lastSeen = datetime($runStart),
                  rpt.createdAt = datetime()
    ON MATCH SET rpt.connectionType = row.Connection_Type_Code,
                 rpt.webUrl = row.Web_Url_Text,
                 rpt.state = row.State_Code,
                 rpt.workspaceName = row.Workspace_Name,
                 rpt.source = "PowerBI_Workspace",
                 rpt.lastSeen = datetime($runStart),
                 rpt.updatedAt = datetime()

    // RoleAssignment for Report Creator (Existing pattern)
    FOREACH (creator IN CASE WHEN row.Creator_Principal_Display_Name IS NOT NULL THEN [row.Creator_Principal_Display_Name] ELSE [] END |
        MERGE (p:Person {name: creator})
        MERGE (ra:RoleAssignment {type: "Report Creator", scope: row.Report_Name})
        ON CREATE SET ra.status = "Active", ra.createdAt = datetime()
        MERGE (p)-[:HAS_ROLE]->(ra)
        MERGE (ra)-[:APPLIES_TO]->(rpt)
    )

    // Lineage link (CONSUMES) (Tagged with runStart and source)
    MERGE (rpt)-[con:CONSUMES]->(t)
    ON CREATE SET con.expression = row.Expression,
                  con.source = "PowerBI_Workspace",
                  con.lastSeen = datetime($runStart),
                  con.createdAt = datetime()
    ON MATCH SET con.expression = row.Expression,
                 con.source = "PowerBI_Workspace",
                 con.lastSeen = datetime($runStart),
                 con.updatedAt = datetime()
    """

    # 2. Run Ingestion Batches
    logging.info(f"  Starting ingestion with run timestamp: {run_start}")
    for i in range(0, len(rows), batch_size):
        loader.write_batches(cypher_ingest, rows[i:i+batch_size], batch_size, runStart=run_start)
        logging.info(f"    Ingested batch {i // batch_size + 1} / {len(rows) // batch_size + 1}...")

    # 3. State Synchronization (Pruning stale records)
    logging.info("  Pruning stale Power BI consumption edges...")
    prune_edges_query = """
    MATCH (rpt:Report {source: "PowerBI_Workspace"})-[con:CONSUMES {source: "PowerBI_Workspace"}]->(t:Table)
    WHERE con.lastSeen < datetime($runStart) OR con.lastSeen IS NULL
    DELETE con
    """
    loader.run_query(prune_edges_query, runStart=run_start)

    logging.info("  Pruning stale Report nodes...")
    prune_reports_query = """
    MATCH (rpt:Report {source: "PowerBI_Workspace"})
    WHERE rpt.lastSeen < datetime($runStart) OR rpt.lastSeen IS NULL
    DETACH DELETE rpt
    """
    loader.run_query(prune_reports_query, runStart=run_start)

    logging.info("Graph synchronization and loading complete!")
    loader.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", required=True, help="Target Neo4j database, for example lsc")
    parser.add_argument("--source", default=os.getenv("SOURCE_DB_URL"), help="SQLAlchemy URL of the export tables")
    args = parser.parse_args()
    try:
        df_raw = extract_powerbi_metadata(args.source)
        df_conformed = clean_and_map_schemas_views(df_raw, args.source)
        ingest_lineage_to_neo4j(df_conformed, args.database)

    except Exception as e:
        logging.error("Ingestion job failed with exception:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
