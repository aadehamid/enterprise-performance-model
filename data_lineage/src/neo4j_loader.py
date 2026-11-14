"""
Reusable Neo4j CSV loader module.

Provides connection management and a generic function to load any CSV
into Neo4j using a caller-supplied Cypher query and row-transform function.

Usage:
    from neo4j_loader import Neo4jLoader

    loader = Neo4jLoader()

    # Define how to transform each CSV row into a dict for Cypher
    def transform(row):
        return {"name": row["col_a"].strip(), "value": row["col_b"]}

    # Define the Cypher query (use $rows as the parameter name)
    query = '''
        UNWIND $rows AS row
        MERGE (n:MyLabel {name: row.name})
        ON CREATE SET n.value = row.value
    '''

    loader.load_csv("path/to/file.csv", query, transform)
    loader.close()
"""

import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

# -- Resolve paths relative to project root --
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ENV_PATH = os.path.join(PROJECT_ROOT, "neo4j_instance_credentials.env")



# ---------------------------------------------------------------------------
# Centralized Server name canonicalization
# ---------------------------------------------------------------------------
# toLower(serverName) → preferred casing.
# Rule: lowercase wins for all servers.  Explicit overrides only where the
# prefix MUST keep specific casing (e.g., HELIOS).
CANONICAL_SERVER_NAMES = {
    # ── lsc.internal pattern ({system}.{env}.db.lsc.internal) ───────────
    "helios.prod.db.lsc.internal":   "HELIOS.prod.db.lsc.internal",
    "atlas.prod.db.lsc.internal":    "ATLAS.prod.db.lsc.internal",
    "meridian.prod.db.lsc.internal": "MERIDIAN.prod.db.lsc.internal",
    # ── Short hostnames ─────────────────────────────────────────────────
    "sqlsrv-001.lsc.internal": "sqlsrv-001.lsc.internal",
}

# Test/QA server → PROD server mapping.
# If a test server has a prod equivalent, use the prod server instead.
TEST_TO_PROD_SERVER = {
    "helios.test.db.lsc.internal": "HELIOS.prod.db.lsc.internal",
    "atlas.test.db.lsc.internal":  "ATLAS.prod.db.lsc.internal",
    # Azure Synapse QA → Prod
    "lsc-idp-qa.sql.azuresynapse.net": "lsc-idp-prod.sql.azuresynapse.net",
}


def canonicalize_server_name(name):
    """Return the canonical casing for a server name.

    Steps:
      1. Map test/QA servers to their prod equivalent (if known).
      2. Look up the explicit CANONICAL_SERVER_NAMES dict.
      3. Fallback: lowercase the entire name (small letter wins).
    """
    if not name:
        return name
    lower = name.strip().lower()

    # Step 1: Collapse test → prod
    if lower in TEST_TO_PROD_SERVER:
        return TEST_TO_PROD_SERVER[lower]

    # Step 2: Explicit canonical mapping
    if lower in CANONICAL_SERVER_NAMES:
        return CANONICAL_SERVER_NAMES[lower]

    # Step 3: Fallback — lowercase wins
    return lower


class Neo4jLoader:
    """Generic CSV-to-Neo4j loader with connection management."""

    def __init__(self, env_path=ENV_PATH, database=None):
        """Initialize connection from .env credentials.

        Args:
            env_path: Path to the .env file with Neo4j credentials.
            database: Neo4j database name. Defaults to NEO4J_DATABASE env var
                      or 'governancemetadata'.
        """
        load_dotenv(env_path)

        self.uri = os.getenv("NEO4J_URL")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = database or os.getenv("NEO4J_DATABASE", "governancemetadata")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.driver.verify_connectivity()
        print(f"Connected to Neo4j at {self.uri}")

    def load_csv(self, csv_path, cypher_query, transform_fn, null_values=None,
                 filter_fn=None, batch_size=500):
        """Load a CSV file into Neo4j using a Cypher query.

        Args:
            csv_path:      Path to the CSV file.
            cypher_query:  Cypher query using UNWIND $rows AS row.
            transform_fn:  Function that takes a pandas row and returns a dict
                           for the Cypher query parameters.
            null_values:   List of strings to treat as NULL (default: ["NULL"]).
            filter_fn:     Optional function to filter rows before transform.
                           Takes a pandas row, returns True to include.
            batch_size:    Number of rows per transaction (default: 500).

        Returns:
            Number of rows loaded.
        """
        if null_values is None:
            null_values = ["NULL"]

        # Read and clean CSV
        df = pd.read_csv(csv_path)
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

        # Apply optional filter BEFORE null cleanup so raw string values are intact
        if filter_fn is not None:
            mask = df.apply(filter_fn, axis=1)
            df = df[mask]

        # Replace null-like strings with None
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].apply(
                lambda x: None if pd.isna(x) or str(x).strip() in null_values else x
            )

        records = [transform_fn(row) for _, row in df.iterrows()]
        total_loaded = self.write_batches(cypher_query, records, batch_size)
        print(f"Loaded {total_loaded} rows from {os.path.basename(csv_path)}")
        return total_loaded

    def write_batches(self, cypher_query, rows, batch_size=500, **params):
        """Run an `UNWIND $rows` write query over `rows`, one transaction per batch.

        Extra keyword arguments are passed as query parameters to every batch.

        Returns:
            Number of rows written.
        """
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(rows), batch_size):
                session.execute_write(self._run_query, cypher_query, rows[i:i + batch_size], params)
        return len(rows)

    def run_query(self, cypher_query, **params):
        """Run an arbitrary read query and return results.

        Args:
            cypher_query: Cypher query string.
            **params:     Query parameters.

        Returns:
            List of records.
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher_query, **params)
            return [record.data() for record in result]

    def run_write(self, cypher_query):
        """Run a write query (e.g., DELETE, CREATE, MERGE).

        Args:
            cypher_query: Cypher write query string.
        """
        with self.driver.session(database=self.database) as session:
            session.execute_write(lambda tx: tx.run(cypher_query))

    def verify(self, cypher_query):
        """Run a verification query and print results.

        Args:
            cypher_query: Cypher query to verify loaded data.
        """
        results = self.run_query(cypher_query)
        for record in results:
            print(f"  {record}")
        return results

    def build_report_key_lookup(self):
        """Map Report.name to the stored reportKey so a name-only reload hits that node."""
        results = self.run_query(
            "MATCH (r:Report) WHERE r.name IS NOT NULL "
            "RETURN r.name AS name, r.reportKey AS reportKey"
        )
        return {r["name"]: r["reportKey"] for r in results}

    def build_table_qn_lookup(self):
        """Fetch all existing Table qualifiedNames and return a case-insensitive
        lookup dict: toLower(qualifiedName) -> qualifiedName as stored in Neo4j.

        Use with canonicalize_table_qn() to prevent case-variant duplicates.
        """
        results = self.run_query(
            "MATCH (t:Table) RETURN t.qualifiedName AS qn"
        )
        return {r["qn"].lower(): r["qn"] for r in results if r["qn"]}

    @staticmethod
    def canonicalize_table_qn(qn, lookup):
        """Return the existing qualifiedName if a case-insensitive match exists,
        otherwise return the original value unchanged.

        Args:
            qn:     The qualifiedName to canonicalize.
            lookup: Dict from build_table_qn_lookup().

        Returns:
            The canonical qualifiedName (existing casing if found, else original).
        """
        if not qn:
            return qn
        return lookup.get(str(qn).lower(), qn)

    @staticmethod
    def canonicalize_table_fields(rows, lookup, *fields):
        """Rewrite table qualifiedName fields to the stored casing.

        A later MERGE on that field hits the existing node.
        """
        for row in rows:
            for field in fields:
                if field in row:
                    row[field] = Neo4jLoader.canonicalize_table_qn(row[field], lookup)
        return rows

    @staticmethod
    def _run_query(tx, query, rows, params):
        """Execute a parameterized Cypher query within a transaction."""
        tx.run(query, rows=rows, **params)

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()
        print("Connection closed.")
