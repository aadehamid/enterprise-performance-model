"""
Load Schema nodes into Neo4j — Phase 1 of Medallion Architecture implementation.

Creates:
  1. IDP DataSystem node (role: 'Platform')
  2. Schema nodes with layer, role, and ownership properties
  3. Relationships:
     - (IDP:DataSystem)-[:HOSTS]->(Schema)
     - (Schema)-[:BELONGS_TO]->(BusinessArea)          for Gold/Semantic schemas
     - (DataSystem)-[:REPLICATED_TO]->(Schema)          for Replica schemas

Prerequisites:
  - Run extract_mapping_metadata.py first to produce Data/schemas.csv
  - Steps 1-8 from 2_load_data.cypher must be run (BusinessArea + DataSystem nodes)
  - pip install neo4j pandas python-dotenv

Usage:
    python src/load_schemas.py
"""

import os
import pandas as pd
from medallion import is_legacy_schema, schema_layer
from neo4j_loader import Neo4jLoader

# ── Path resolution ────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCHEMAS_CSV = os.path.join(PROJECT_ROOT, "Data", "schemas.csv")

# ── Step 1: Create IDP DataSystem node ─────────────────────────────────────
IDP_QUERY = """
MERGE (idp:DataSystem {name: 'Insight and Discovery Platform (IDP)'})
ON CREATE SET idp.role = 'Platform',
  idp.description = 'Enterprise data platform implementing Medallion Architecture',
  idp.createdAt = datetime()
ON MATCH SET idp.role = 'Platform',
  idp.updatedAt = datetime()
"""

# ── Step 2: Create Schema nodes and wire IDP -[:HOSTS]-> Schema ────────────
SCHEMA_QUERY = """
UNWIND $rows AS row
MERGE (s:Schema {qualifiedName: row.qualifiedName})
ON CREATE SET s.layer = row.layer,
  s.role = row.role,
  s.sourceType = row.sourceType,
  s.isCrossCutting = row.isCrossCutting,
  s.refactorTarget = row.refactorTarget,
  s.createdAt = datetime()
ON MATCH SET s.layer = row.layer,
  s.role = row.role,
  s.sourceType = row.sourceType,
  s.isCrossCutting = row.isCrossCutting,
  s.refactorTarget = row.refactorTarget,
  s.updatedAt = datetime()
FOREACH (_ IN CASE WHEN row.legacy THEN [1] ELSE [] END | SET s:Legacy)
WITH s, row

// Wire IDP -[:HOSTS]-> Schema
MATCH (idp:DataSystem {name: 'Insight and Discovery Platform (IDP)'})
MERGE (idp)-[:HOSTS]->(s)

// Wire Schema -[:BELONGS_TO]-> BusinessArea (for Gold/Semantic schemas with a BA)
WITH s, row
WHERE row.businessArea IS NOT NULL
MATCH (ba:BusinessArea {name: row.businessArea})
MERGE (s)-[:BELONGS_TO]->(ba)
"""

# ── Step 3: Wire Replica schemas to source DataSystems ─────────────────────
# Explicit mapping from replica schema name → DataSystem.name.
# This is the single source of truth for replica-to-source wiring.
# Add new entries here as new replica schemas are discovered.
REPLICA_TO_DATASYSTEM = {
    "replica_eis":              "EIS",
    "replica_genscape":         "Genscape",
    "replica_kittyhawk":        "Kittyhawk",
    "replica_kpler":            "Kpler",
    "replica_ltpf":             "LTPF",
    "replica_mips":             "MIPS",
    "replica_mips_ltpf":        "MIPS-LTPF",
    "replica_mpr":              "MPR",
    "replica_weather":          "Weather",
    # replica_files_commercial has no single source DataSystem — it ingests flat
    # files from the Commercial business area. Schema gets BELONGS_TO Commercial
    # via businessArea in the CSV; no REPLICATED_TO is needed.
}

# DataSystems that may not exist yet and must be created before wiring.
# Each entry: name → {properties to set on create}
MISSING_DATASYSTEMS = {
    "Kpler": {
        "description": "Kpler commodity market data and analytics platform",
        "businessArea": "Commercial",
    },
    "Weather": {
        "description": "Weather data source for Commercial analytics",
        "businessArea": "Commercial",
    },
    "LTPF": {
        "description": "LTPF data source",
        "businessArea": "Commercial",
    },
}

# Cypher: Create missing DataSystems and wire to BusinessArea
CREATE_MISSING_DS_QUERY = """
UNWIND $rows AS row
MERGE (ds:DataSystem {name: row.name})
ON CREATE SET ds.description = row.description,
  ds.scope = 'area-specific',
  ds.createdAt = datetime()
ON MATCH SET ds.updatedAt = datetime()
WITH ds, row
WHERE row.businessArea IS NOT NULL
MATCH (ba:BusinessArea {name: row.businessArea})
MERGE (ds)-[:BELONGS_TO]->(ba)
"""

# Cypher: Wire replica schemas to DataSystems using explicit mapping
# First pass: match by purviewReplicaSchemaName (existing DataSystems from IDP CSV)
REPLICA_LINK_QUERY = """
MATCH (s:Schema)
WHERE s.layer = 'Replica'
WITH s
MATCH (ds:DataSystem)
WHERE toLower(ds.purviewReplicaSchemaName) = s.qualifiedName
  AND ds.name <> 'Insight and Discovery Platform (IDP)'
MERGE (ds)-[:REPLICATED_TO]->(s)
"""

# Second pass: wire remaining replicas using the explicit mapping dict
REPLICA_LINK_EXPLICIT_QUERY = """
UNWIND $rows AS row
MATCH (s:Schema {qualifiedName: row.schemaName})
MATCH (ds:DataSystem {name: row.dataSystemName})
MERGE (ds)-[:REPLICATED_TO]->(s)
"""

# ── Verification queries ───────────────────────────────────────────────────
VERIFY_SCHEMAS = """
MATCH (s:Schema)
RETURN s.layer AS layer, count(s) AS schemaCount
ORDER BY schemaCount DESC
"""

VERIFY_IDP_HOSTS = """
MATCH (idp:DataSystem {name: 'Insight and Discovery Platform (IDP)'})-[:HOSTS]->(s:Schema)
RETURN count(s) AS schemasHostedByIDP
"""

VERIFY_REPLICA_LINKS = """
MATCH (ds:DataSystem)-[:REPLICATED_TO]->(s:Schema)
RETURN ds.name AS sourceSystem, s.qualifiedName AS replicaSchema
ORDER BY ds.name
"""

VERIFY_BA_LINKS = """
MATCH (s:Schema)-[:BELONGS_TO]->(ba:BusinessArea)
RETURN ba.name AS businessArea, collect(s.qualifiedName) AS schemas
ORDER BY ba.name
"""

VERIFY_UNLINKED_REPLICA = """
MATCH (s:Schema)
WHERE s.layer = 'Replica' AND NOT ()-[:REPLICATED_TO]->(s)
RETURN s.qualifiedName AS unlinkedReplicaSchema
ORDER BY s.qualifiedName
"""


def safe_value(val):
    """Convert NaN/empty to None for Neo4j."""
    if pd.isna(val) or str(val).strip() == "":
        return None
    return str(val).strip()


def transform_row(row):
    """Transform a schemas.csv row into a dict for the Cypher query."""
    return {
        "qualifiedName": row["qualifiedName"],
        "layer": schema_layer(row["qualifiedName"]) or "Unknown",
        "legacy": is_legacy_schema(row["qualifiedName"]),
        "role": safe_value(row.get("role")),
        "businessArea": safe_value(row.get("businessArea")),
        "sourceType": safe_value(row.get("sourceType")),
        "isCrossCutting": bool(row.get("isCrossCutting", False)),
        "refactorTarget": safe_value(row.get("refactorTarget")),
    }


def main():
    loader = Neo4jLoader()

    try:
        # ── Step 1: Create IDP DataSystem ──────────────────────────────────
        print("Step 1: Creating IDP DataSystem node...")
        loader.run_write(IDP_QUERY)
        print("  Done.")

        # ── Step 2: Create Schema nodes + HOSTS + BELONGS_TO ───────────────
        print("\nStep 2: Loading Schema nodes from CSV...")
        loader.load_csv(
            csv_path=SCHEMAS_CSV,
            cypher_query=SCHEMA_QUERY,
            transform_fn=transform_row,
        )

        # ── Step 3a: Create any missing DataSystems ─────────────────────────
        if MISSING_DATASYSTEMS:
            print("\nStep 3a: Creating missing DataSystems...")
            ds_records = [
                {"name": name, **props}
                for name, props in MISSING_DATASYSTEMS.items()
            ]
            loader.write_batches(CREATE_MISSING_DS_QUERY, ds_records)
            for name in MISSING_DATASYSTEMS:
                print(f"    MERGE DataSystem: {name}")

        # ── Step 3b: Wire Replica schemas to source DataSystems ────────────
        print("\nStep 3b: Linking Replica schemas to source DataSystems...")
        loader.run_write(REPLICA_LINK_QUERY)
        print("  Primary link (by purviewReplicaSchemaName) done.")

        # Explicit mapping for all replicas (catches anything missed above)
        explicit_records = [
            {"schemaName": schema, "dataSystemName": ds_name}
            for schema, ds_name in REPLICA_TO_DATASYSTEM.items()
        ]
        loader.write_batches(REPLICA_LINK_EXPLICIT_QUERY, explicit_records)
        print("  Explicit mapping applied for all replica schemas.")

        # ── Verification ───────────────────────────────────────────────────
        print("\n=== Verification ===")

        print("\nSchemas by layer:")
        loader.verify(VERIFY_SCHEMAS)

        print("\nSchemas hosted by IDP:")
        loader.verify(VERIFY_IDP_HOSTS)

        print("\nReplica schemas linked to source DataSystems:")
        loader.verify(VERIFY_REPLICA_LINKS)

        print("\nSchemas linked to BusinessAreas:")
        loader.verify(VERIFY_BA_LINKS)

        print("\nUnlinked Replica schemas (no REPLICATED_TO):")
        unlinked = loader.verify(VERIFY_UNLINKED_REPLICA)
        if not unlinked:
            print("  All Replica schemas are linked!")
        else:
            print(f"  {len(unlinked)} Replica schemas still unlinked — "
                  "these need manual DataSystem mapping.")

    finally:
        loader.close()


if __name__ == "__main__":
    main()
