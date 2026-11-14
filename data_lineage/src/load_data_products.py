"""
load_data_products.py - Create DataProduct nodes and wire them to
CapabilityDataDomain (BELONGS_TO) and Semantic Views (REALIZED_BY).

One DataProduct per semantic view file (12 total).
Each semantic view (Table, layer='Semantic') loaded from that file
gets a REALIZED_BY edge from the DataProduct.

Mapping:
  - File name → DataProduct name (e.g., "Master Pricing Data Product")
  - File name → CapabilityDataDomain (matched by name)
  - APS and BAT both map to "Local Production Planning & Crude Scheduling"

Usage:
    python src/load_data_products.py           # dry-run
    python src/load_data_products.py --load     # write to Neo4j
"""
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from neo4j_loader import Neo4jLoader

# ---------------------------------------------------------------------------
# File → DataProduct name → CapabilityDataDomain name
# ---------------------------------------------------------------------------
FILE_TO_PRODUCT = {
    "APS Semantic Views.xlsx": {
        "product": "APS Data Product",
        "capability": "Local Production Planning & Crude Scheduling",
    },
    "BAT Semantic Views.xlsx": {
        "product": "BAT Data Product",
        "capability": "Local Production Planning & Crude Scheduling",
    },
    "Backcasting & Refining Continuous Improvement Semantic Views.xlsx": {
        "product": "Backcasting & Refining CI Data Product",
        "capability": "Backcasting & Refining Continuous Improvement",
    },
    "Brand Data Integration Semantic Views.xlsx": {
        "product": "Brand Data & Integration Data Product",
        "capability": "Brand Data & Integration",
    },
    "External Market Data Semantic Views.xlsx": {
        "product": "External Market Data Data Product",
        "capability": "External Market Data",
    },
    "Local Production Planning & Crude Scheduling Semantic Views.xlsx": {
        "product": "Local Production Planning Data Product",
        "capability": "Local Production Planning & Crude Scheduling",
    },
    "Logistic Execution Semantic Views.xlsx": {
        "product": "Logistics Execution Data Product",
        "capability": "Logistics Execution",
    },
    "Master Pricing Semantic Views.xlsx": {
        "product": "Master Pricing Data Product",
        "capability": "Master Pricing",
    },
    "Operational Margin Semantic Views.xlsx": {
        "product": "Operational Margin Data Product",
        "capability": "Operational Margin",
    },
    "Physical Trading Semantic Views.xlsx": {
        "product": "Physical Trading Data Product",
        "capability": "Physical Trading",
    },
    "Regional Production & Distribution Planning Semantic Views.xlsx": {
        "product": "Regional Production & Distribution Data Product",
        "capability": "Regional Production & Distribution Planning",
    },
    "Retail Payments Semantic Views.xlsx": {
        "product": "Retail Payments Data Product",
        "capability": "Retail Payments",
    },
}

# ---------------------------------------------------------------------------
# Cypher Queries
# ---------------------------------------------------------------------------

# Create DataProduct node and wire BELONGS_TO CapabilityDataDomain
MERGE_DATA_PRODUCT_QUERY = """
UNWIND $rows AS row
MERGE (dp:DataProduct {name: row.productName})
ON CREATE SET
    dp.sourceFile = row.sourceFile,
    dp.createdAt  = datetime()
WITH dp, row
MATCH (cap:CapabilityDataDomain {name: row.capabilityName})
MERGE (dp)-[:BELONGS_TO]->(cap)
"""

# Wire DataProduct → REALIZED_BY → Semantic View (Table)
REALIZED_BY_QUERY = """
UNWIND $rows AS row
MATCH (dp:DataProduct {name: row.productName})
MATCH (t:Table {qualifiedName: row.viewQN})
MERGE (dp)-[:REALIZED_BY]->(t)
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", action="store_true")
    args = parser.parse_args()

    # Connect to get semantic views grouped by sourceFile
    loader = Neo4jLoader()

    # Fetch all Semantic views with their sourceFile
    views = loader.run_query("""
        MATCH (t:Table)
        WHERE t.layer = 'Semantic' AND t.sourceFile IS NOT NULL
        RETURN t.qualifiedName AS qn, t.sourceFile AS file
        ORDER BY t.sourceFile, t.qualifiedName
    """)

    # Build payloads
    product_rows = []  # For MERGE_DATA_PRODUCT_QUERY
    realized_rows = []  # For REALIZED_BY_QUERY
    seen_products = set()
    skipped = 0

    for v in views:
        source_file = v["file"]
        mapping = FILE_TO_PRODUCT.get(source_file)
        if not mapping:
            skipped += 1
            continue

        product_name = mapping["product"]
        capability_name = mapping["capability"]

        # Only add the DataProduct row once per product
        if product_name not in seen_products:
            seen_products.add(product_name)
            product_rows.append({
                "productName": product_name,
                "sourceFile": source_file,
                "capabilityName": capability_name,
            })

        realized_rows.append({
            "productName": product_name,
            "viewQN": v["qn"],
        })

    # Print summary
    print(f"DataProduct nodes to create: {len(product_rows)}")
    for p in product_rows:
        count = sum(1 for r in realized_rows if r["productName"] == p["productName"])
        print(f"  {p['productName']:50s} → {p['capabilityName']} ({count} views)")
    print(f"\nREALIZED_BY edges: {len(realized_rows)}")
    print(f"Skipped views (no mapping, e.g. Alteryx): {skipped}")

    if not args.load:
        print("\nDry-run complete. Use --load to write to Neo4j.")
        loader.close()
        return

    # Load
    loader.write_batches(MERGE_DATA_PRODUCT_QUERY, product_rows)
    print(f"\nMerged {len(product_rows)} DataProduct node(s) with BELONGS_TO edges")
    loader.write_batches(REALIZED_BY_QUERY, realized_rows)
    print(f"Merged {len(realized_rows)} REALIZED_BY edge(s)")

    # Verify
    print("\n=== Verification ===")
    results = loader.run_query("""
        MATCH (dp:DataProduct)-[:BELONGS_TO]->(cap:CapabilityDataDomain)
        OPTIONAL MATCH (dp)-[:REALIZED_BY]->(t:Table)
        RETURN dp.name AS product, cap.name AS capability, count(t) AS viewCount
        ORDER BY dp.name
    """)
    for r in results:
        print(f"  {r['product']:50s} → {r['capability']} ({r['viewCount']} views)")

    loader.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
