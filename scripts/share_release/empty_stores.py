#!/usr/bin/env python3
"""Empty the named ontology stores before they are reloaded from the release (step 9 of the cut, the owner's instruction
of 2026-11-01). It reports counts before and after, and prints no login value.

    python3 scripts/share_release/empty_stores.py --env <stores env> <store> [<store> ...]         # counts only
    python3 scripts/share_release/empty_stores.py --env <stores env> --yes <store> [<store> ...]   # delete

A store is named on the command line or not touched: there is no default set. `--env` holds one line per store, and a
store it does not list cannot run:

    NEO4J_LOCAL=<bolt address>|<login file>    a local Neo4j
    NEO4J_AURA=<login file>                    AuraDB; the address comes from the login file
    DATABRICKS=<login file>                    the catalog and schema the login file names; only that schema's tables go

This deletes data. Run it only when the data can be reloaded from the release, and read the counts first.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrubbing  # noqa: E402


def read_env(path):
    values = {}
    with open(os.path.expanduser(path), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def neo4j_login(path, bolt=None):
    """(address, user, password) from a login file; the password never reaches a printed line."""
    v = read_env(path)
    password = v.get("NEO4J_PASSWORD") or v.get("PASSWORD")
    if not password:
        raise SystemExit(f"{path} holds no NEO4J_PASSWORD")
    scrubbing.register(password)
    return bolt or v["NEO4J_URI"], v.get("NEO4J_USERNAME", "neo4j"), password


def neo4j_counts(session):
    one = lambda q: session.run(q).single()["c"]
    return {"nodes": one("MATCH (n) RETURN count(n) AS c"), "relationships": one("MATCH ()-[r]->() RETURN count(r) AS c")}


def empty_neo4j(session, yes):
    """Counts before and after; with yes, deletes in batches, so a large graph does not exhaust one transaction."""
    before = neo4j_counts(session)
    deleted = 0
    if yes:
        while True:
            n = session.run("MATCH (n) WITH n LIMIT 5000 DETACH DELETE n RETURN count(*) AS c").single()["c"]
            deleted += n
            if n == 0:
                break
    return {"before": before, "deleted": deleted, "after": neo4j_counts(session) if yes else before}


def empty_databricks(cursor, schema, yes):
    """The tables of one schema, with their rows; with yes, drops them. `schema` is catalog.schema, from the login file."""
    cursor.execute(f"SHOW TABLES IN {schema}")
    tables = [r[1] for r in cursor.fetchall()]
    counts = {}
    for t in tables:
        cursor.execute(f"SELECT count(*) FROM {schema}.{t}")
        counts[t] = cursor.fetchone()[0]
    out = {"schema": schema, "tables_before": tables, "counts_before": counts}
    if yes:
        for t in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {schema}.{t}")
        cursor.execute(f"SHOW TABLES IN {schema}")
        out["tables_after"] = [r[1] for r in cursor.fetchall()]
    return out


def run_store(name, config, yes):
    if name == "local" or name == "aura":
        from neo4j import GraphDatabase
        if name == "local":
            bolt, login = config["NEO4J_LOCAL"].split("|", 1)
            uri, user, password = neo4j_login(login, bolt)
        else:
            uri, user, password = neo4j_login(config["NEO4J_AURA"])
        with GraphDatabase.driver(uri, auth=(user, password)) as driver, driver.session() as session:
            return empty_neo4j(session, yes)
    from databricks import sql
    v = read_env(config["DATABRICKS"])
    scrubbing.register(v["DATABRICKS_TOKEN"])
    with sql.connect(server_hostname=v["DATABRICKS_HOST"].replace("https://", ""), http_path=v["DATABRICKS_HTTP_PATH"],
                     access_token=v["DATABRICKS_TOKEN"]) as conn, conn.cursor() as cursor:
        return empty_databricks(cursor, f'{v["DATABRICKS_CATALOG"]}.{v["DATABRICKS_SCHEMA"]}', yes)


KEYS = {"local": "NEO4J_LOCAL", "aura": "NEO4J_AURA", "databricks": "DATABRICKS"}


def main(argv=None, runner=run_store):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--env", required=True)
    ap.add_argument("--yes", action="store_true", help="delete; without it, counts only")
    ap.add_argument("stores", nargs="+", choices=sorted(KEYS))
    a = ap.parse_args(argv)
    config = read_env(a.env)
    missing = [s for s in a.stores if KEYS[s] not in config]
    if missing:
        ap.error(f"{a.env} does not list {', '.join(KEYS[s] for s in missing)}")
    failed = False
    for name in a.stores:
        try:
            print(json.dumps({"store": name, **runner(name, config, a.yes)}))
        except Exception as err:  # one store's failure is reported; the others are still reported on
            failed = True
            print(json.dumps({"store": name, "error": scrubbing.scrub(f"{type(err).__name__}: {str(err)[:200]}")}))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
