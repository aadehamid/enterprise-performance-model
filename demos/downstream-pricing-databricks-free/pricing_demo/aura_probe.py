"""Runs inside Databricks (a serverless job aura_test.py submits): can Databricks reach AuraDB? (EPM-DEC-001-0109,
decision 7). It reads the AuraDB login from the secret scope epm-neo4j, never prints it, and prints one JSON line: the
DNS lookup, a TCP connection to the Bolt port, and a driver query counting the ontology's nodes, each with its result
or its error. Free Edition limits outbound access, so any step may fail; the error is the finding.
"""
import json
import socket
from urllib.parse import urlparse

SCOPE = "epm-neo4j"


def secret(key):
    from databricks.sdk.runtime import dbutils
    return dbutils.secrets.get(scope=SCOPE, key=key)


def step(result, name, fn):
    try:
        result[name] = {"ok": True, "value": fn()}
    except Exception as err:  # the error is the finding
        result[name] = {"ok": False, "error": f"{type(err).__name__}: {str(err).splitlines()[0][:300] if str(err) else ''}"}
    return result[name]["ok"]


def main():
    uri, user, password = secret("uri"), secret("username"), secret("password")
    host = urlparse(uri).hostname
    result = {}
    step(result, "dns", lambda: len(socket.getaddrinfo(host, 7687)) > 0)
    step(result, "tcp_7687", lambda: socket.create_connection((host, 7687), timeout=10).close() is None)

    def query():
        from neo4j import GraphDatabase
        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            driver.verify_connectivity()
            records, _, _ = driver.execute_query("MATCH (n:Resource) RETURN count(n) AS nodes")
            return records[0]["nodes"]
    step(result, "bolt_query", query)
    print("AURA_PROBE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
