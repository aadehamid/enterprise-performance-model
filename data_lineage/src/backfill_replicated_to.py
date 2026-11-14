"""
backfill_replicated_to.py - Backfill Operational nodes, REPLICATED_TO edges,
and DataSystem CONTAINS for orphan Replica tables.

Phases:
  1. Merge duplicate DataSystems (TargetTracking, MarketingDashboard)
  2. Create 3 new DataSystems (AM_EFE, AM_Shared, AM_WBE)
  3. Create 1 new FlatFile node (Files_Commercial)
  4. For each orphan Replica table:
     - Resolve replica prefix to correct DataSystem/FlatFile name
     - MERGE Operational Table node
     - MERGE REPLICATED_TO edge
     - MERGE DataSystem/FlatFile CONTAINS Operational Table

Usage:
    python src/backfill_replicated_to.py            # dry-run
    python src/backfill_replicated_to.py --load      # write to Neo4j
"""
import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from neo4j_loader import Neo4jLoader

# ---------------------------------------------------------------------------
# Alias map: replica prefix (lowercase) → actual DataSystem name
# For prefixes NOT in this map, we do case-insensitive lookup against
# existing DataSystem nodes.
# ---------------------------------------------------------------------------
EXPLICIT_ALIAS = {
    "target_tracking":          "TargetTracking",
    "marketing_dashboard":      "MarketingDashboard",
    "aps_canadian":             "APS_CRUDE_CANADIAN",
    "aps_west":                 "APS_CRUDE_WEST",
    "aps_gulf":                 "APS_CRUDE_GULF",
    "aps_midwest":              "APS_CRUDE_MIDWEST",
    "aps_rockies":              "APS_CRUDE_ROCKIES",
    "brand_credit_card":        "BrandCreditCard",
    "brand_credit_card_master": "BrandCreditCardMaster",
    "ice_crudecash":            "CrudeCash",
    "onexchange":               "ONE EXCHANGE",
    "product_certification":    "ProdCert",
    "files_commercial":         "Files_Commercial",  # FlatFile, not DataSystem
}

# New DataSystem nodes to create (name, createdAt)
NEW_DATASYSTEMS = ["AM_EFE", "AM_Shared", "AM_WBE"]

# FlatFile node to create
NEW_FLATFILE = "Files_Commercial"

# Duplicate DataSystem merges: (keep, remove)
DUPLICATE_MERGES = [
    ("TargetTracking", "Target Tracking"),
    ("MarketingDashboard", "Marketing Dashboards"),
]

# ---------------------------------------------------------------------------
# Cypher Queries
# ---------------------------------------------------------------------------

# Phase 1: Move all relationships from old DS to new DS, then delete old
MERGE_DUPLICATE_DS = """
MATCH (old:DataSystem {name: $oldName})
MATCH (keep:DataSystem {name: $keepName})
// Move outgoing relationships
WITH old, keep
OPTIONAL MATCH (old)-[r_out]->(target)
WHERE target <> keep
FOREACH (x IN CASE WHEN type(r_out) = 'BELONGS_TO' THEN [1] ELSE [] END |
    MERGE (keep)-[:BELONGS_TO]->(target)
)
FOREACH (x IN CASE WHEN type(r_out) = 'CONTAINS' THEN [1] ELSE [] END |
    MERGE (keep)-[:CONTAINS]->(target)
)
FOREACH (x IN CASE WHEN type(r_out) = 'HOSTS' THEN [1] ELSE [] END |
    MERGE (keep)-[:HOSTS]->(target)
)
WITH old, keep
// Move incoming relationships
OPTIONAL MATCH (source)-[r_in]->(old)
WHERE source <> keep
FOREACH (x IN CASE WHEN type(r_in) = 'HOSTS' THEN [1] ELSE [] END |
    MERGE (source)-[:HOSTS]->(keep)
)
FOREACH (x IN CASE WHEN type(r_in) = 'BELONGS_TO' THEN [1] ELSE [] END |
    MERGE (source)-[:BELONGS_TO]->(keep)
)
WITH old
DETACH DELETE old
"""

# Phase 2: Create new DataSystem nodes
CREATE_DS = """
MERGE (ds:DataSystem {name: $name})
ON CREATE SET ds.createdAt = datetime()
"""

# Phase 3: Create FlatFile node
CREATE_FLATFILE = """
MERGE (ff:FlatFile {name: $name})
ON CREATE SET ff.createdAt = datetime()
"""

# Phase 4a: Backfill for DataSystem sources
BACKFILL_DS_QUERY = """
UNWIND $rows AS row
MATCH (r:Table {qualifiedName: row.replicaQN})
MERGE (op:Table {qualifiedName: row.opQN})
ON CREATE SET op.tableName = row.opTableName, op.layer = 'Operational',
              op.createdAt = datetime()
MERGE (op)-[:REPLICATED_TO]->(r)
WITH op, row
MATCH (ds:DataSystem {name: row.dsName})
MERGE (ds)-[:CONTAINS]->(op)
"""

# Phase 4b: Backfill for FlatFile sources
BACKFILL_FF_QUERY = """
UNWIND $rows AS row
MATCH (r:Table {qualifiedName: row.replicaQN})
MERGE (op:Table {qualifiedName: row.opQN})
ON CREATE SET op.tableName = row.opTableName, op.layer = 'Operational',
              op.createdAt = datetime()
MERGE (op)-[:REPLICATED_TO]->(r)
WITH op, row
MATCH (ff:FlatFile {name: row.dsName})
MERGE (ff)-[:CONTAINS]->(op)
"""


def build_ds_lookup(loader):
    """Build case-insensitive lookup: uppercase name → actual name."""
    ds_nodes = loader.run_query(
        "MATCH (ds:DataSystem) RETURN ds.name AS name"
    )
    return {r['name'].upper(): r['name'] for r in ds_nodes}


def resolve_ds_name(prefix_lower, ds_lookup):
    """Resolve a replica prefix to the correct DataSystem/FlatFile name."""
    # Check explicit alias first
    if prefix_lower in EXPLICIT_ALIAS:
        return EXPLICIT_ALIAS[prefix_lower]
    # Case-insensitive lookup
    return ds_lookup.get(prefix_lower.upper())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", action="store_true")
    args = parser.parse_args()

    loader = Neo4jLoader()

    # --- Phase 1: Check duplicates ---
    print("=== Phase 1: Merge Duplicate DataSystems ===")
    for keep, remove in DUPLICATE_MERGES:
        exists_keep = loader.run_query(
            "MATCH (ds:DataSystem {name: $n}) RETURN count(ds) AS c", n=keep
        )[0]['c']
        exists_remove = loader.run_query(
            "MATCH (ds:DataSystem {name: $n}) RETURN count(ds) AS c", n=remove
        )[0]['c']
        if exists_keep and exists_remove:
            print(f"  Will merge '{remove}' → '{keep}'")
        elif not exists_remove:
            print(f"  SKIP: '{remove}' not found (already merged?)")
        else:
            print(f"  WARNING: '{keep}' not found!")

    # --- Phase 2: New DataSystems ---
    print(f"\n=== Phase 2: Create {len(NEW_DATASYSTEMS)} New DataSystems ===")
    for ds in NEW_DATASYSTEMS:
        print(f"  {ds}")

    # --- Phase 3: New FlatFile ---
    print(f"\n=== Phase 3: Create FlatFile: {NEW_FLATFILE} ===")

    # --- Phase 4: Build backfill rows ---
    print("\n=== Phase 4: Backfill Operational + REPLICATED_TO ===")

    # Build DS lookup (include the new ones we're about to create)
    ds_lookup = build_ds_lookup(loader)
    for ds in NEW_DATASYSTEMS:
        ds_lookup[ds.upper()] = ds

    # Get all orphan replicas
    orphans = loader.run_query("""
        MATCH (r:Table {layer: 'Replica'})
        WHERE NOT ()-[:REPLICATED_TO]->(r)
        RETURN r.qualifiedName AS qn ORDER BY qn
    """)

    ds_rows = []   # DataSystem backfill rows
    ff_rows = []   # FlatFile backfill rows
    unresolved = []

    for row in orphans:
        qn = row['qn']
        m = re.match(r'^replica_(\w+)\.(.+)$', qn, re.IGNORECASE)
        if not m:
            unresolved.append(qn)
            continue

        prefix = m.group(1).lower()
        table_name = m.group(2)
        ds_name = resolve_ds_name(prefix, ds_lookup)

        if not ds_name:
            unresolved.append(qn)
            continue

        op_qn = f"{ds_name}.{table_name}"
        rec = {
            "replicaQN": qn,
            "opQN": op_qn,
            "opTableName": table_name,
            "dsName": ds_name,
        }

        if ds_name == NEW_FLATFILE:
            ff_rows.append(rec)
        else:
            ds_rows.append(rec)

    qn_lookup = loader.build_table_qn_lookup()
    Neo4jLoader.canonicalize_table_fields(ds_rows, qn_lookup, "replicaQN", "opQN")
    Neo4jLoader.canonicalize_table_fields(ff_rows, qn_lookup, "replicaQN", "opQN")

    # Summary
    print(f"  DataSystem backfill rows: {ds_rows.__len__()}")
    print(f"  FlatFile backfill rows:   {ff_rows.__len__()}")
    print(f"  Unresolved:               {len(unresolved)}")
    if unresolved:
        for u in unresolved:
            print(f"    UNRESOLVED: {u}")

    # Show sample
    print("\n  Sample DataSystem rows (first 10):")
    for r in ds_rows[:10]:
        print(f"    {r['replicaQN']} → {r['opQN']} (DS: {r['dsName']})")

    print(f"\n  Sample FlatFile rows (first 5):")
    for r in ff_rows[:5]:
        print(f"    {r['replicaQN']} → {r['opQN']} (FF: {r['dsName']})")

    if not args.load:
        print("\nDry-run complete. Use --load to write to Neo4j.")
        loader.close()
        return

    # --- Execute ---
    with loader.driver.session(database=loader.database) as session:
        # Phase 1: Merge duplicates
        for keep, remove in DUPLICATE_MERGES:
            exists_remove = loader.run_query(
                "MATCH (ds:DataSystem {name: $n}) RETURN count(ds) AS c", n=remove
            )[0]['c']
            if exists_remove:
                session.execute_write(
                    lambda tx, kn=keep, rn=remove: tx.run(
                        MERGE_DUPLICATE_DS, keepName=kn, oldName=rn
                    )
                )
                print(f"  Merged '{remove}' → '{keep}'")

        # Phase 2: Create new DataSystems
        for ds in NEW_DATASYSTEMS:
            session.execute_write(
                lambda tx, n=ds: tx.run(CREATE_DS, name=n)
            )
        print(f"  Created {len(NEW_DATASYSTEMS)} new DataSystem(s)")

        # Phase 3: Create FlatFile
        session.execute_write(
            lambda tx: tx.run(CREATE_FLATFILE, name=NEW_FLATFILE)
        )
        print(f"  Created FlatFile: {NEW_FLATFILE}")

        # Phase 4: Backfill
        if ds_rows:
            loader.write_batches(BACKFILL_DS_QUERY, ds_rows)
            print(f"  Backfilled {len(ds_rows)} DataSystem Operational + REPLICATED_TO")
        if ff_rows:
            loader.write_batches(BACKFILL_FF_QUERY, ff_rows)
            print(f"  Backfilled {len(ff_rows)} FlatFile Operational + REPLICATED_TO")

    # --- Verification ---
    print("\n=== Verification ===")
    remaining = loader.run_query("""
        MATCH (r:Table {layer: 'Replica'})
        WHERE NOT ()-[:REPLICATED_TO]->(r)
        RETURN count(r) AS cnt
    """)
    print(f"  Remaining orphan Replicas: {remaining[0]['cnt']}")

    # Spot check a few
    checks = ["replica_trr.BargeSegment", "replica_files_commercial.Executivesummarykeyprices_Text_Input_1",
              "replica_am_efe.EFE_Crude_Assay"]
    for qn in checks:
        r = loader.run_query("""
            MATCH (op:Table)-[rt:REPLICATED_TO]->(rep:Table {qualifiedName: $qn})
            OPTIONAL MATCH (ds)-[c:CONTAINS]->(op)
            RETURN op.qualifiedName AS op, labels(ds) AS dsLabels,
                   ds.name AS dsName
        """, qn=qn)
        if r:
            print(f"  {qn} → {r[0]['op']} (source: {r[0]['dsName']}, label: {r[0]['dsLabels']})")
        else:
            print(f"  {qn} → NOT FOUND (may not exist)")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
