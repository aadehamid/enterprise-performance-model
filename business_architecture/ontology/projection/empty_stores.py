"""Counts what each ontology store holds and, with --yes, empties it. rebuild_stores.py calls it; it also runs alone.

    python3 empty_stores.py --store driver --store jena          # counts only: changes nothing
    python3 empty_stores.py --store driver --store jena --yes    # deletes, then counts again

Without --yes it writes nothing. It takes the stores from sync_stores.py, so EPM_STORES_JSON names another environment's.
In Neo4j and AuraDB it deletes every node in the database. In Jena it drops every graph. In Databricks it drops only
the triple table and the marker table, and leaves the demo's tables and anything else in the schema. Prints one JSON
line per store, with no login value; a store that cannot be read says "unreachable" and the error's name, and the local
Neo4j says "no_login" when the output folder holds no login for it yet.
Needs neo4j for the Neo4j stores and databricks-sql-connector for Databricks (uv run --with ...).
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

import sync_stores as ss


def neo4j_counts(session):
    return session.run("MATCH (n) RETURN count(n) AS n").single()["n"]


def empty_neo4j(session):
    """Deletes in batches, so a store of any size fits one transaction per batch. Returns the nodes deleted."""
    deleted = 0
    while True:
        n = session.run("MATCH (n) WITH n LIMIT 5000 DETACH DELETE n RETURN count(*) AS c").single()["c"]
        deleted += n
        if n == 0:
            return deleted


def jena_update(statement):
    url = ss.JENA_QUERY.rsplit("/", 1)[0] + "/update"
    body = urllib.parse.urlencode({"update": statement}).encode()
    urllib.request.urlopen(urllib.request.Request(url, data=body, method="POST"), timeout=120).close()


def databricks_tables(cur, schema):
    """The tables of this tool's own in the schema: never the whole schema."""
    cur.execute(f"SHOW TABLES IN {schema}")
    return sorted({row[1] for row in cur.fetchall()} & {ss.TRIPLES_TABLE, "epm_store_markers"})


def one_store(store, yes):
    if store == "jena":
        held = sum(ss.read_jena().values())
        if yes:
            jena_update("DROP ALL")
            return {"store": store, "held": held, "after": sum(ss.read_jena().values())}
        return {"store": store, "held": held}
    if store == "databricks":
        conn, schema = ss.databricks()
        with conn, conn.cursor() as cur:
            tables = databricks_tables(cur, schema)
            if yes:
                for table in tables:
                    cur.execute(f"DROP TABLE IF EXISTS {schema}.{table}")
                return {"store": store, "held": len(tables), "after": len(databricks_tables(cur, schema))}
            return {"store": store, "held": len(tables)}
    driver, session = ss.neo4j_session(store)
    with driver, session:
        held = neo4j_counts(session)
        if yes:
            empty_neo4j(session)
            return {"store": store, "held": held, "after": neo4j_counts(session)}
        return {"store": store, "held": held}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--store", action="append", required=True, choices=ss.STORES)
    ap.add_argument("--yes", action="store_true", help="delete; without it, count only")
    args = ap.parse_args(argv)
    failed = False
    for store in args.store:
        try:
            print(json.dumps(one_store(store, args.yes)))
        except Exception as err:  # the reason, never a value: a driver's message can carry a URI
            # A local store that is not running has nothing to delete, and the load creates it. A cloud store must answer.
            failed = failed or (args.yes and store in ("aura", "databricks"))
            if store == "driver" and isinstance(err, FileNotFoundError):  # sync_stores.newest: no run.env in the output folder
                print(json.dumps({"store": store, "no_login": "the output folder holds no login yet; the load creates one"}))
            else:
                print(json.dumps({"store": store, "unreachable": type(err).__name__}))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
