"""
Load DataSystem nodes from CSV into Neo4j.

Creates DataSystem nodes and BELONGS_TO relationships to BusinessArea.
BuisnessArea column supports three formats:
  - Single value:          "Refining"
  - "and"-separated pair:  "Refining and Midstream"
  - JSON-like list:        '["Commercial", "Finance", ...]'

Each row is parsed into a list of BA names. Scope is set based on count:
  1 BA  → 'area-specific'
  2 BAs → 'multi-area'
  3+ BAs → 'enterprise'

Prerequisites:
  - pip install neo4j pandas python-dotenv
  - Steps 1-4 from 2_load_data.cypher must be run first (BusinessArea nodes must exist)

Usage:
    python src/load_datasystems.py
"""

import os
import json
from medallion import flag_bool
from neo4j_loader import Neo4jLoader

# -- Path to CSV --
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CSV_PATH = os.path.join(PROJECT_ROOT, "Data", "Source_System_from_IDP.csv")

# -- Single Cypher query: creates DataSystem and BELONGS_TO for each BA in the list --
LOAD_QUERY = """
UNWIND $rows AS row
MERGE (ds:DataSystem {name: row.name})
ON CREATE SET ds.systemId = row.systemId,
  ds.description = row.description,
  ds.isRecordActive = row.isRecordActive,
  ds.scope = row.scope,
  ds.createdAt = datetime()
ON MATCH SET ds.updatedAt = datetime()
SET ds.applicationService       = CASE WHEN row.applicationService IS NOT NULL THEN row.applicationService ELSE ds.applicationService END,
    ds.confidentialityClassification = CASE WHEN row.confidentialityClassification IS NOT NULL THEN row.confidentialityClassification ELSE ds.confidentialityClassification END,
    ds.isSoxRelevant             = CASE WHEN row.isSoxRelevant IS NOT NULL THEN row.isSoxRelevant ELSE ds.isSoxRelevant END,
    ds.dataModality              = CASE WHEN row.dataModality IS NOT NULL THEN row.dataModality ELSE ds.dataModality END,
    ds.applicationType           = CASE WHEN row.applicationType IS NOT NULL THEN row.applicationType ELSE ds.applicationType END,
    ds.purviewReplicaSchemaName  = CASE WHEN row.purviewReplicaSchemaName IS NOT NULL THEN row.purviewReplicaSchemaName ELSE ds.purviewReplicaSchemaName END,
    ds.purviewSourceTypeAssetLink = CASE WHEN row.purviewSourceTypeAssetLink IS NOT NULL THEN row.purviewSourceTypeAssetLink ELSE ds.purviewSourceTypeAssetLink END,
    ds.ingestionMethod           = CASE WHEN row.ingestionMethod IS NOT NULL THEN row.ingestionMethod ELSE ds.ingestionMethod END,
    ds.refreshFrequency          = CASE WHEN row.refreshFrequency IS NOT NULL THEN row.refreshFrequency ELSE ds.refreshFrequency END
WITH ds, row
UNWIND row.businessAreas AS areaName
MATCH (ba:BusinessArea {name: areaName})
MERGE (ds)-[:BELONGS_TO]->(ba)
"""

# -- Verification query --
VERIFY_QUERY = """
MATCH (ds:DataSystem)-[:BELONGS_TO]->(ba:BusinessArea)
RETURN ba.name AS businessArea, count(ds) AS systemCount
ORDER BY systemCount DESC
"""


def parse_business_areas(raw_value):
    """Parse the BuisnessArea column into a list of BA names.

    Handles:
      - JSON list:  '["Commercial", "Finance"]' → ["Commercial", "Finance"]
      - "and" pair: 'Refining and Midstream'    → ["Refining", "Midstream"]
      - Single:     'Commercial'                → ["Commercial"]
    """
    if raw_value is None:
        return []

    raw_value = str(raw_value).strip()

    # JSON-like list (starts with '[')
    if raw_value.startswith("["):
        try:
            return [s.strip() for s in json.loads(raw_value)]
        except json.JSONDecodeError:
            pass

    # "and"-separated pair
    if " and " in raw_value:
        return [s.strip() for s in raw_value.split(" and ")]

    # Single value
    return [raw_value]


def scope_from_count(count):
    """Determine scope label based on number of BusinessAreas."""
    if count <= 1:
        return "area-specific"
    elif count == 2:
        return "multi-area"
    return "enterprise"


def safe_str(value):
    """Return None for NaN/empty values, otherwise stripped string."""
    if value is None or (isinstance(value, float) and str(value) == "nan"):
        return None
    s = str(value).strip()
    return s if s else None


def parse_ingestion_method(raw_value):
    """Parse ingestionMethod from JSON string to list, e.g. '["Pipeline"]' → ['Pipeline']."""
    s = safe_str(raw_value)
    if s is None:
        return None
    if s.startswith("["):
        try:
            return [item.strip() for item in json.loads(s)]
        except json.JSONDecodeError:
            pass
    return [s]


def transform_row(row):
    """Transform a CSV row into a dict for the Cypher query."""
    areas = parse_business_areas(row["BuisnessArea"])
    return {
        "name": row["DataSystem.name"],
        "systemId": int(row["DataSystem.Id"]),
        "description": row["DataSystem.Description"],
        "isRecordActive": flag_bool(row["Record_Active_Indicator"]),
        "businessAreas": areas,
        "scope": scope_from_count(len(areas)),
        # -- Enriched attributes from Sharepoint merge --
        "applicationService": safe_str(row.get("applicationService")),
        "confidentialityClassification": safe_str(row.get("confidentialityClassification")),
        "isSoxRelevant": flag_bool(row.get("isSoxRelevant")),
        "dataModality": safe_str(row.get("dataModality")),
        "applicationType": safe_str(row.get("applicationType")),
        "purviewReplicaSchemaName": safe_str(row.get("purviewReplicaSchemaName")),
        "purviewSourceTypeAssetLink": safe_str(row.get("purviewSourceTypeAssetLink")),
        "ingestionMethod": parse_ingestion_method(row.get("ingestionMethod")),
        "refreshFrequency": safe_str(row.get("refreshFrequency")),
    }


def main():
    loader = Neo4jLoader()

    try:
        # Load all DataSystem nodes with their BusinessArea relationships
        loader.load_csv(
            csv_path=CSV_PATH,
            cypher_query=LOAD_QUERY,
            transform_fn=transform_row,
        )

        # Verify
        print("\nDataSystem count per BusinessArea:")
        loader.verify(VERIFY_QUERY)

    finally:
        loader.close()


if __name__ == "__main__":
    main()
