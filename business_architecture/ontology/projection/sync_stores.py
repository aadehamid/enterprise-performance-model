"""Keeps the four ontology stores in step with the repository (brief item 7c, 2026-10-29).

Each store holds a marker saying which release set it was loaded from: the catalog's datasets (their count and a
digest of their IRIs, from releases/catalog.ttl) and the projection's input fingerprint (projection-manifest.json).
The drift check compares each marker with main's newest catalog and manifest; sync reloads what is behind with the
existing commands (run_local.sh and the ontology-to-lpg driver), loads the pricing demo's technical graph again,
because a reload wipes it, and marks the stores it reloaded.

    python3 sync_stores.py expected [--ref origin/main]   # what a current store holds
    python3 sync_stores.py mark --store pipeline ...       # check a store against the repository, then mark it
    python3 sync_stores.py check [--ref origin/main]       # the drift check: which stores are behind
    python3 sync_stores.py sync [--cloud] [--dry-run]      # reload what is behind, then mark it

The markers stay out of the projection: in Neo4j a node labelled EpmStoreMarker, never Resource, which the
projection's counts, hash and round trip do not read (test_pipeline.py, OntologyLabelsOnly); in Databricks a row in
epm_store_markers, beside epm_triples. A pipeline reload's wipe removes the Neo4j marker, so a store reloaded by
hand reads as unmarked until it is marked again. Logins come from the files LOCAL-STORES.md names; none is printed.
Needs rdflib; mark, check and sync also need neo4j and databricks-sql-connector (uv run --with ...).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
CATALOG = "business_architecture/ontology/releases/catalog.ttl"
MANIFEST = "business_architecture/ontology/projection/projection-manifest.json"
REPORT = os.path.join(HERE, "projection-report.json")
DEMO = os.path.join(REPO, "demos", "downstream-pricing-databricks-free")
NEO4J_STORES = {  # LOCAL-STORES.md; the driver's login is in whichever of its two run files is newer
    "pipeline": ("bolt://127.0.0.1:17687", ("~/epm-lpg/run.env",)),
    "driver": ("bolt://127.0.0.1:17711", ("~/lpg-out/epm-rebuild/neo4j-run/run.env", "~/lpg-out/epm/neo4j-run/run.env")),
    "aura": (None, ("~/.config/neo4j/aura.env",)),
}
DRIVER_REPORTS = ("~/lpg-out/epm-rebuild/projection-report.json", "~/lpg-out/epm/projection-report.json")
DATABRICKS_ENV = "~/.config/databricks/epm.env"
STORES = (*NEO4J_STORES, "databricks")
MARKER_FIELDS = ("catalog_datasets", "catalog_digest", "input_fingerprint")


def apply_store_overrides():
    """EPM_STORES_JSON names other stores for a test run, so the test never points at the loaded ones (the share
    release's validation): {"pipeline": {"bolt": ..., "env": [...]}, "driver": {...}, "aura": {"env": [...]},
    "driver_reports": [...], "databricks_env": "..."}. Each key is optional."""
    global DRIVER_REPORTS, DATABRICKS_ENV
    raw = os.environ.get("EPM_STORES_JSON")
    if not raw:
        return
    over = json.loads(raw)
    for store in NEO4J_STORES:
        if store in over:
            bolt = over[store].get("bolt", NEO4J_STORES[store][0])
            envs = tuple(over[store].get("env", NEO4J_STORES[store][1]))
            NEO4J_STORES[store] = (bolt, envs)
    if "driver_reports" in over:
        DRIVER_REPORTS = tuple(over["driver_reports"])
    if "databricks_env" in over:
        DATABRICKS_ENV = over["databricks_env"]


apply_store_overrides()


# ---------- what a current store holds ----------

def repo_file(path, ref=None):
    """A file's text in the working tree, or at a git ref (main's newest catalog for the drift check)."""
    if ref is None:
        return open(os.path.join(REPO, path)).read()
    return subprocess.run(["git", "-C", REPO, "show", f"{ref}:{path}"], check=True, capture_output=True, text=True).stdout


def catalog_datasets(text):
    from rdflib import Graph, Namespace
    DCAT = Namespace("http://www.w3.org/ns/dcat#")
    return sorted(str(d) for d in Graph().parse(data=text, format="turtle").objects(None, DCAT.dataset))


def newest_releases(datasets):
    """Each module's newest release IRI: .../modules/<module>/<major>.<minor>.<patch>."""
    newest = {}
    for iri in datasets:
        module, version = iri.rsplit("/", 2)[-2:]
        key = tuple(int(p) for p in version.split("."))
        if module not in newest or key > newest[module][0]:
            newest[module] = (key, iri)
    return sorted(iri for _, iri in newest.values())


def expected(ref=None):
    datasets = catalog_datasets(repo_file(CATALOG, ref))
    return {"catalog_datasets": len(datasets),
            "catalog_digest": hashlib.sha256("\n".join(datasets).encode()).hexdigest(),
            "input_fingerprint": json.loads(repo_file(MANIFEST, ref))["input_fingerprint"],
            "newest": newest_releases(datasets)}


# ---------- the drift check ----------

def drift(markers, live, want):
    """Each store's status from its marker, its live count and the repository's expected values:
    current, behind (marked from another release set), changed (its count moved since it was marked), unmarked, or
    unreachable (the store could not be read: no connection, no login file or a missing table, for example; the
    error's name follows the word)."""
    rows = []
    for store in STORES:
        m = markers.get(store)
        if isinstance(live.get(store), str):
            rows.append((store, "unreachable", live[store]))
        elif not m:
            rows.append((store, "unmarked", "no marker: mark it after a checked load, or sync it"))
        elif any(m.get(k) != want[k] for k in MARKER_FIELDS):
            moved = [k for k in MARKER_FIELDS if m.get(k) != want[k]]
            rows.append((store, "behind", f"marked {m.get('marked_at')} from another release set ({', '.join(moved)})"))
        elif live.get(store) != m.get("count"):
            rows.append((store, "changed", f"marked with {m.get('count')}, now holds {live.get(store)}"))
        else:
            rows.append((store, "current", f"marked {m.get('marked_at')} at commit {m.get('commit')}"))
    return rows


# ---------- logins and readers ----------

def read_env(path):
    values = {}
    for line in open(os.path.expanduser(path)):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def newest(paths):
    found = [os.path.expanduser(p) for p in paths if os.path.exists(os.path.expanduser(p))]
    if not found:
        raise FileNotFoundError(f"none of {', '.join(paths)} exists")  # an Exception, so a status check reports it
    return max(found, key=os.path.getmtime)


def neo4j_session(store):
    from neo4j import GraphDatabase
    bolt, paths = NEO4J_STORES[store]
    values = read_env(newest(paths))
    uri = bolt or values["NEO4J_URI"]
    password = values.get("NEO4J_PASSWORD") or values["PASSWORD"]
    driver = GraphDatabase.driver(uri, auth=(values.get("NEO4J_USERNAME", "neo4j"), password))
    return driver, driver.session()


def databricks():
    from databricks import sql as dbsql
    e = read_env(DATABRICKS_ENV)
    conn = dbsql.connect(server_hostname=e["DATABRICKS_HOST"].replace("https://", ""),
                         http_path=e["DATABRICKS_HTTP_PATH"], access_token=e["DATABRICKS_TOKEN"])
    return conn, f"{e['DATABRICKS_CATALOG']}.{e['DATABRICKS_SCHEMA']}"


def resource_counts(session):
    nodes = session.run("MATCH (n:Resource) RETURN count(n) AS n").single()["n"]
    edges = session.run("MATCH (:Resource)-[r]->(:Resource) RETURN count(r) AS n").single()["n"]
    return nodes, edges


def read_markers_and_counts():
    markers, live = {}, {}
    for store in NEO4J_STORES:
        try:
            driver, session = neo4j_session(store)
            with driver, session:
                rec = session.run("MATCH (m:EpmStoreMarker {store: $s}) RETURN properties(m) AS p", s=store).single()
                markers[store] = rec["p"] if rec else None
                live[store] = list(resource_counts(session))
        except Exception as err:  # a store that can't be read (down, or no login file) reads as unreachable, with the reason
            markers[store], live[store] = None, f"unreachable ({type(err).__name__})"
    try:
        conn, schema = databricks()
        with conn, conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM {schema}.epm_triples")
            live["databricks"] = [cur.fetchone()[0]]
            try:
                cur.execute(f"SELECT marker FROM {schema}.epm_store_markers WHERE store = 'databricks'")
                row = cur.fetchone()
                markers["databricks"] = json.loads(row[0]) if row else None
            except Exception:
                markers["databricks"] = None
    except Exception as err:
        markers["databricks"], live["databricks"] = None, f"unreachable ({type(err).__name__})"
    return markers, live


# ---------- marking ----------

def commit():
    return subprocess.run(["git", "-C", REPO, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()


def now():
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def neo4j_checked(store, session):
    """A Neo4j store's measured counts, refused unless they match what the repository says it should hold."""
    report = json.load(open(REPORT))
    nodes, edges = resource_counts(session)
    if store == "pipeline":
        import pipeline  # beside this file
        h, n, e = pipeline.graph_hash(session)
        if (h, n, e) != (report["determinism_hash_sorted"], report["nodes"], report["relationships"]):
            raise SystemExit(f"pipeline: graph hash {h[:8]} with {n} nodes and {e} relationships, not the committed "
                             f"report's {report['determinism_hash_sorted'][:8]}, {report['nodes']}, {report['relationships']}")
    else:  # the driver's graph (and Aura, its copy) counts edges by guideline v2.3, so its own report gives them
        driver_report = json.load(open(newest(DRIVER_REPORTS)))
        if (nodes, edges) != (report["nodes"], driver_report["relationships"]):
            raise SystemExit(f"{store}: {nodes} nodes and {edges} relationships, not the projection's {report['nodes']} "
                             f"nodes and the driver report's {driver_report['relationships']} relationships")
    return [nodes, edges]


def databricks_checked(cur, schema, want):
    cur.execute(f"SELECT DISTINCT graph FROM {schema}.epm_triples")
    graphs = {r[0] for r in cur.fetchall()}
    missing = [g for g in want["newest"] if g not in graphs]
    if missing:
        raise SystemExit(f"databricks: epm_triples lacks the newest release of {len(missing)} module(s), e.g. {missing[:3]}")
    cur.execute(f"SELECT count(*) FROM {schema}.epm_triples")
    return [cur.fetchone()[0]]


def mark(stores, want=None):
    want = want or expected()
    base = {k: want[k] for k in MARKER_FIELDS} | {"marked_at": now(), "commit": commit()}
    for store in stores:
        if store == "databricks":
            conn, schema = databricks()
            with conn, conn.cursor() as cur:
                marker = base | {"store": store, "count": databricks_checked(cur, schema, want)}
                cur.execute(f"CREATE TABLE IF NOT EXISTS {schema}.epm_store_markers (store STRING, marker STRING) "
                            "COMMENT 'Which release set each ontology store was loaded from (sync_stores.py)'")
                cur.execute(f"DELETE FROM {schema}.epm_store_markers WHERE store = 'databricks'")
                cur.execute(f"INSERT INTO {schema}.epm_store_markers VALUES ('databricks', ?)", [json.dumps(marker)])
        else:
            driver, session = neo4j_session(store)
            with driver, session:
                marker = base | {"store": store, "count": neo4j_checked(store, session)}
                session.run("MERGE (m:EpmStoreMarker {store: $s}) SET m = $p", s=store, p=marker).consume()
        print(f"{store}: marked, holding {marker['count']}, from {want['catalog_datasets']} catalog datasets")


# ---------- sync ----------

def plan(behind, cloud, skills):
    """The commands that reload the stores that are behind, in order. Local stores always; AuraDB and Databricks only
    with --cloud, through the full driver run, which also reloads the driver's Neo4j. A local driver run skips the
    driver's copy, databricks and rebuild steps, so its Neo4j is loaded from the repository, not back from epm_triples."""
    steps, reloaded = [], []
    driver_cmd = ["uv", "run", "--no-project", "--with", "rdflib", "python3", "run_projection.py",
                  "--config", os.path.join(HERE, "skill-run", "epm-run.json")]
    driver_dir = os.path.join(os.path.expanduser(skills), "ontology-to-lpg", "scripts")
    if "pipeline" in behind:
        steps.append((HERE, ["./run_local.sh", "--keep"]))
        reloaded.append("pipeline")
    cloud_behind = [s for s in ("aura", "databricks") if s in behind]
    if cloud and cloud_behind:
        steps.append((driver_dir, driver_cmd))
        reloaded += ["driver", "aura", "databricks"]
    elif "driver" in behind:
        steps.append((driver_dir, driver_cmd + ["--skip", "copy,databricks,rebuild"]))
        reloaded.append("driver")
    tech = [s for s in reloaded if s in NEO4J_STORES]
    if tech:  # a reload wipes the technical graph (runbook, Reload, step 5)
        steps.append((DEMO, ["uv", "run", "--group", "graph", "python", "-m", "pricing_demo.tech_graph", "load"]
                      + [a for s in tech for a in ("--store", s)]))
    return steps, reloaded


def sync(cloud, dry_run, ref, skills):
    rows = drift(*read_markers_and_counts(), expected(ref))
    behind = [s for s, status, _ in rows if status != "current"]
    steps, reloaded = plan(behind, cloud, skills)
    skipped = [s for s in behind if s not in reloaded]
    for cwd, cmd in steps:
        print(f"({os.path.relpath(cwd, REPO) if cwd.startswith(REPO) else cwd}) {' '.join(cmd)}")
        if not dry_run:
            subprocess.run(cmd, cwd=cwd, check=True)
    if skipped:
        print(f"not reloaded (cloud stores need --cloud): {', '.join(skipped)}")
    if not dry_run and reloaded:
        mark(reloaded, expected())
    if not behind:
        print("every store is current")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=("expected", "mark", "check", "sync"))
    ap.add_argument("--ref", default="origin/main", help="check, sync: the git ref whose catalog is newest (default origin/main)")
    ap.add_argument("--store", action="append", choices=STORES, help="mark: these stores")
    ap.add_argument("--cloud", action="store_true", help="sync: also reload AuraDB and Databricks (the full driver run)")
    ap.add_argument("--dry-run", action="store_true", help="sync: print the commands, run nothing")
    ap.add_argument("--skills", default=os.environ.get("EPM_SKILLS", "~/.agents/skills"),
                    help="sync: the folder holding the ontology-to-lpg skill (default $EPM_SKILLS or ~/.agents/skills)")
    args = ap.parse_args()
    if args.command == "expected":
        print(json.dumps(expected(args.ref), indent=2))
    elif args.command == "mark":
        if not args.store:
            raise SystemExit("mark: name the stores with --store")
        mark(args.store)  # a marker records what the working tree's catalog says the store was loaded from
    elif args.command == "check":
        rows = drift(*read_markers_and_counts(), expected(args.ref))
        for store, status, why in rows:
            print(f"{store:<11} {status:<9} {why}")
        sys.exit(0 if all(status == "current" for _, status, _ in rows) else 1)
    else:
        sync(args.cloud, args.dry_run, args.ref, args.skills)


if __name__ == "__main__":
    main()
