"""
Cypher Query Validator for the Data Lineage Knowledge Graph.

Runs a Cypher query against Neo4j and validates it against standard assertions.
Outputs structured JSON results for grading.

Usage:
    python validate_cypher.py --query "MATCH (n:Table) RETURN n LIMIT 5"
    python validate_cypher.py --file path/to/query.cypher
    python validate_cypher.py --query "..." --env path/to/credentials.env
    python validate_cypher.py --query "..." --output grading.json

Dependencies: neo4j, python-dotenv
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError, ClientError

# -- Default paths --
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_ENV_PATH = os.path.join(PROJECT_ROOT, "neo4j_instance_credentials.env")

# The live graph is the schema: EXPLAIN reports every label / relationship type
# the query names that the database has never seen, as these GQL statuses.
UNKNOWN_LABEL_STATUS = "01N50"
UNKNOWN_REL_TYPE_STATUS = "01N51"
_BACKTICKED = re.compile(r"`([^`]+)`")


def connect(env_path):
    """Connect to Neo4j using credentials from .env file."""
    if not os.path.exists(env_path):
        print(f"ERROR: Credentials file not found: {env_path}")
        sys.exit(1)

    load_dotenv(env_path)
    uri = os.getenv("NEO4J_URL")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "governancemetadata")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    return driver, database


def validate_query(driver, database, cypher_query):
    """Run assertions against a Cypher query and return grading results."""
    results = []

    # ── Assertion 1: Syntactically valid Cypher ──────────────────────────
    try:
        with driver.session(database=database) as session:
            explain_summary = session.run(f"EXPLAIN {cypher_query}").consume()
        results.append({
            "text": "Query is syntactically valid Cypher",
            "passed": True,
            "evidence": "EXPLAIN executed without errors"
        })
    except (CypherSyntaxError, ClientError) as e:
        results.append({
            "text": "Query is syntactically valid Cypher",
            "passed": False,
            "evidence": f"Syntax error: {str(e)[:200]}"
        })
        # If syntax fails, skip remaining assertions
        return _build_grading(results, cypher_query)

    # ── Assertions 4–5: every label / rel type named exists in the live graph ──
    unknown_labels = _unknown_tokens(explain_summary, UNKNOWN_LABEL_STATUS)
    results.append({
        "text": "All node labels used exist in the schema",
        "passed": len(unknown_labels) == 0,
        "evidence": "All labels exist in the live graph" if not unknown_labels
                    else f"Unknown labels: {sorted(unknown_labels)}"
    })
    unknown_rels = _unknown_tokens(explain_summary, UNKNOWN_REL_TYPE_STATUS)
    results.append({
        "text": "All relationship types used exist in the schema",
        "passed": len(unknown_rels) == 0,
        "evidence": "All rel types exist in the live graph" if not unknown_rels
                    else f"Unknown rel types: {sorted(unknown_rels)}"
    })

    # ── Execute the query (with LIMIT safety net) ────────────────────────
    try:
        with driver.session(database=database) as session:
            result = session.run(cypher_query)
            records = [record for record in result]
            summary = result.consume()
    except Exception as e:
        results.append({
            "text": "Query executes without runtime errors",
            "passed": False,
            "evidence": f"Runtime error: {str(e)[:200]}"
        })
        return _build_grading(results, cypher_query)

    results.append({
        "text": "Query executes without runtime errors",
        "passed": True,
        "evidence": f"Returned {len(records)} records"
    })

    # ── Assertion 2: Returns at least 1 result ───────────────────────────
    results.append({
        "text": "Query returns at least 1 result",
        "passed": len(records) > 0,
        "evidence": f"Returned {len(records)} records"
    })

    if not records:
        return _build_grading(results, cypher_query)

    # ── Assertion 3: Returns nodes and relationships (not scalars only) ──
    has_nodes = False
    has_rels = False
    found_labels = set()
    found_rel_types = set()

    for record in records:
        for value in record.values():
            has_nodes, has_rels, found_labels, found_rel_types = \
                _inspect_value(value, has_nodes, has_rels,
                               found_labels, found_rel_types)

    results.append({
        "text": "Query returns nodes (not just scalar values)",
        "passed": has_nodes,
        "evidence": f"Found node labels: {sorted(found_labels)}" if has_nodes
                    else "No nodes found in result — only scalar values returned"
    })

    results.append({
        "text": "Query returns relationships (graph-visualization-ready)",
        "passed": has_rels,
        "evidence": f"Found relationship types: {sorted(found_rel_types)}" if has_rels
                    else "No relationships found in result"
    })

    return _build_grading(results, cypher_query)


def _unknown_tokens(summary, gql_status):
    """Names the EXPLAIN summary flags with `gql_status`, e.g. `BogusLabel`."""
    found = set()
    for status in summary.gql_status_objects:
        if status.gql_status == gql_status:
            match = _BACKTICKED.search(status.status_description)
            found.add(match.group(1) if match else status.status_description)
    return found


def _inspect_value(value, has_nodes, has_rels, found_labels, found_rel_types):
    """Recursively inspect a result value for nodes, relationships, and paths."""
    from neo4j.graph import Node, Relationship, Path

    if isinstance(value, Node):
        has_nodes = True
        found_labels.update(value.labels)
    elif isinstance(value, Relationship):
        has_rels = True
        found_rel_types.add(value.type)
    elif isinstance(value, Path):
        has_nodes = True
        has_rels = True
        for node in value.nodes:
            found_labels.update(node.labels)
        for rel in value.relationships:
            found_rel_types.add(rel.type)
    elif isinstance(value, list):
        for item in value:
            has_nodes, has_rels, found_labels, found_rel_types = \
                _inspect_value(item, has_nodes, has_rels,
                               found_labels, found_rel_types)

    return has_nodes, has_rels, found_labels, found_rel_types


def _build_grading(assertion_results, cypher_query):
    """Build the grading JSON structure."""
    passed = sum(1 for a in assertion_results if a["passed"])
    failed = sum(1 for a in assertion_results if not a["passed"])
    total = len(assertion_results)

    return {
        "query": cypher_query,
        "timestamp": datetime.now().isoformat(),
        "assertion_results": assertion_results,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total > 0 else 0
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Cypher query against the Data Lineage Knowledge Graph"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", "-q", help="Cypher query string to validate")
    group.add_argument("--file", "-f", help="Path to a .cypher file to validate")
    parser.add_argument("--env", "-e", default=DEFAULT_ENV_PATH,
                        help=f"Path to Neo4j credentials .env file (default: {DEFAULT_ENV_PATH})")
    parser.add_argument("--output", "-o", help="Path to write grading.json (default: stdout)")
    args = parser.parse_args()

    # Read query
    if args.file:
        with open(args.file, "r") as f:
            cypher_query = f.read().strip()
    else:
        cypher_query = args.query

    # Connect and validate with timing
    driver, database = connect(args.env)
    try:
        start = time.time()
        grading = validate_query(driver, database, cypher_query)
        duration_ms = round((time.time() - start) * 1000)
    finally:
        driver.close()

    # Output grading
    output_json = json.dumps(grading, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Grading written to {args.output}")

        # Write timing.json alongside grading.json
        timing_path = os.path.join(os.path.dirname(args.output), "timing.json")
        timing = {"duration_ms": duration_ms, "timestamp": datetime.now().isoformat()}
        with open(timing_path, "w") as f:
            json.dump(timing, f, indent=2)
        print(f"Timing written to {timing_path} ({duration_ms}ms)")
    else:
        print(output_json)

    # Exit with non-zero if any assertion failed
    if grading["summary"]["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
