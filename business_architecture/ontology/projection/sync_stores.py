"""Keeps the ontology stores in step with the repository (brief item 7c, 2026-10-29).

The Neo4j stores and the Delta table each hold a marker saying which release set they were loaded from: the catalog's
datasets (their count and a digest of their IRIs, from releases/catalog.ttl) and the projection's input fingerprint
(projection-manifest.json). The drift check compares each marker with main's newest catalog and manifest. Jena holds
no marker: its named graphs are version IRIs, so the check reads its graph names and each graph's triple count and
compares them with the newest release files, and the technical graph's two named graphs, which stay out of the release's
proof, with the graph files the demo would load. Each store also holds the technical graph's own marker, a digest of
those graph files, which the demo's tech_graph load writes (and tech_graph sync, for the Delta copy); the check reports
it on a tech:<store> line beside the ontology's, so a missing or stale technical graph shows when the ontology is
current. sync reloads what is behind with the ontology-to-lpg driver, takes the driver's result into this folder,
loads the pricing demo's technical graph again where a reload wiped it or its marker is not current, copies it to
Delta with tech_graph sync when the Delta copy is reloaded or behind, and marks the stores it reloaded.

    python3 sync_stores.py expected [--ref origin/main]   # what a current store holds
    python3 sync_stores.py mark --store driver ...         # check a store against the repository, then mark it
    python3 sync_stores.py check [--ref origin/main] [--store driver ...]   # the drift check, ontology and technical graph (default: all stores)
    python3 sync_stores.py sync [--cloud] [--dry-run]      # reload what is behind, then mark it

The markers stay out of the projection: in Neo4j a node labelled EpmStoreMarker, never Resource, which the
projection's counts, hash and round trip do not read (test_sync_stores.py, OntologyLabelsOnly); in Databricks a row in
epm_store_markers, beside epm_triples. A reload's wipe removes the Neo4j marker, so a store reloaded by hand reads as
unmarked until it is marked again. Jena's dataset is in memory, so a restart empties it and the check reads empty.
Logins come from the files LOCAL-STORES.md names; none is printed.
Needs rdflib; mark, check and sync also need neo4j and databricks-sql-connector (uv run --with ...).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
CATALOG = "business_architecture/ontology/releases/catalog.ttl"
MANIFEST = "business_architecture/ontology/projection/projection-manifest.json"
REPORT = os.path.join(HERE, "projection-report.json")
DEMO = os.path.join(REPO, "demos", "downstream-pricing-databricks-free")
NEO4J_STORES = {  # LOCAL-STORES.md; the driver's login is in whichever of its two run files is newer
    "driver": ("bolt://127.0.0.1:17711", ("~/lpg-out/epm-rebuild/neo4j-run/run.env", "~/lpg-out/epm/neo4j-run/run.env")),
    "aura": (None, ("~/.config/neo4j/aura.env",)),
}
JENA_QUERY = "http://127.0.0.1:13031/ds/query"  # skill-run/epm-run.json's "jena"
DATABRICKS_ENV = "~/.config/databricks/epm.env"
RUN_CONFIG = os.path.join(HERE, "skill-run", "epm-run.json")
DRIVER_OUT = "~/lpg-out/epm"  # the run configuration's "out"
TRIPLES_TABLE = "epm_triples"  # the run configuration's "databricks" table
RELEASE_GRAPHS = ("shapes", "catalog")  # skill-run/epm-run.json's "release_graphs"
TECH_GRAPHS = {"tech-graph.ttl": "urn:pricing-demo:graph:tech-graph", "decision-trail.ttl": "urn:pricing-demo:graph:decision-trail"}  # tech_graph.JENA_GRAPHS
# The technical graph's marker, as the demo's tech_graph load and sync write it (tech_graph.MARKER_LABEL, MARKER_GRAPH,
# MARKER_DIGEST, MARKER_ROW): a digest of the graph files a store holds.
TECH_MARKER_LABEL = "TechGraphMarker"
TECH_MARKER_GRAPH = "urn:pricing-demo:graph:tech-marker"
TECH_MARKER_DIGEST = "urn:pricing-demo:tech-marker:digest"
TECH_MARKER_ROW = "tech_graph"
STORES = (*NEO4J_STORES, "jena", "databricks")
MARKER_FIELDS = ("catalog_datasets", "catalog_digest", "input_fingerprint")


def apply_store_overrides():
    """EPM_STORES_JSON names other stores for a test run, so the test never points at the loaded ones (the share
    release's validation): {"driver": {"bolt": ..., "env": [...]}, "aura": {"env": [...]}, "jena": {"query": ...},
    "databricks_env": "...", "run_config": "...", "driver_out": "...", "triples_table": "..."}. Each key is optional; the
    same keys point the tool at another environment's stores."""
    global JENA_QUERY, DATABRICKS_ENV, RUN_CONFIG, DRIVER_OUT, TRIPLES_TABLE
    raw = os.environ.get("EPM_STORES_JSON")
    if not raw:
        return
    over = json.loads(raw)
    for store in NEO4J_STORES:
        if store in over:
            bolt = over[store].get("bolt", NEO4J_STORES[store][0])
            envs = tuple(over[store].get("env", NEO4J_STORES[store][1]))
            NEO4J_STORES[store] = (bolt, envs)
    if "jena" in over:
        JENA_QUERY = over["jena"].get("query", JENA_QUERY)
    DATABRICKS_ENV = over.get("databricks_env", DATABRICKS_ENV)
    RUN_CONFIG = over.get("run_config", RUN_CONFIG)
    DRIVER_OUT = over.get("driver_out", DRIVER_OUT)
    TRIPLES_TABLE = over.get("triples_table", TRIPLES_TABLE)


apply_store_overrides()


# ---------- what a current store holds ----------

def repo_file(path, ref=None):
    """A file's text in the working tree, or at a git ref (main's newest catalog for the drift check). The ref
    `worktree` reads the tree itself, for a tree without Git such as the share release."""
    if ref is None or ref == "worktree":
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


def jena_graphs(newest, ref=None):
    """{graph IRI: triple count} that a current Jena holds: for each newest release, its content under the version IRI
    and each release graph under <version IRI>/<name>, counted from the release's files."""
    from rdflib import Graph
    graphs = {}
    for iri in newest:
        module, version = iri.rsplit("/", 2)[-2:]
        folder = f"business_architecture/ontology/releases/{module}/{version}"
        for name, graph in ((module, iri), *((n, f"{iri}/{n}") for n in RELEASE_GRAPHS)):
            graphs[graph] = len(Graph().parse(data=repo_file(f"{folder}/{name}.ttl", ref), format="turtle"))
    return graphs


def tech_folder():
    """The folder the demo's tech_graph load reads: a refreshed copy when a build wrote one, or what the release ships."""
    refreshed = os.path.join(DEMO, "out", "tech", "graph")
    return refreshed if all(os.path.isfile(os.path.join(refreshed, n)) for n in TECH_GRAPHS) else os.path.join(DEMO, "graph")


def tech_graph_counts():
    """{graph IRI: triple count} of the technical graph as the demo would load it."""
    from rdflib import Graph
    folder = tech_folder()
    return {iri: len(Graph().parse(os.path.join(folder, name), format="turtle")) for name, iri in TECH_GRAPHS.items()}


def tech_digest(folder=None):
    """The digest a current store's technical-graph marker holds: tech_graph.graph_digest of the files load reads."""
    h = hashlib.sha256()
    for name in TECH_GRAPHS:
        with open(os.path.join(folder or tech_folder(), name), "rb") as f:
            h.update(name.encode() + b"\0" + f.read() + b"\0")
    return h.hexdigest()


def judge_jena(held, want, tech=None):
    """Jena's status from the graphs it holds and those the release files say it should: its graph names are its marker.
    The technical graph's named graphs stay out of that comparison and are judged on their own against tech."""
    tech = tech or {}
    held = dict(held)
    held.pop(TECH_MARKER_GRAPH, None)  # the technical graph's marker, judged by tech_drift
    held_tech = {g: held.pop(g) for g in list(held) if g in TECH_GRAPHS.values()}
    if not held and not held_tech:
        return "empty", "it holds no graph; a restart empties its in-memory dataset; sync reloads it"
    missing, stray = sorted(set(want) - set(held)), sorted(set(held) - set(want))
    if missing or stray:
        return "behind", f"{len(missing)} graph(s) of the newest releases missing and {len(stray)} other(s) held"
    moved = [g for g in want if held[g] != want[g]]
    if moved:
        return "changed", f"{len(moved)} graph(s) hold another triple count than the release files, e.g. {moved[0]}"
    if held_tech != tech:
        return "changed", f"the technical graph differs from its files: {sum(held_tech.values())} triples, not {sum(tech.values())}; run tech_graph load --store jena"
    return "current", (f"{len(held)} graphs, {sum(held.values())} triples, each equal to the release files"
                       + (f"; technical graph {sum(tech.values())} triples" if tech else ""))


# ---------- the drift check ----------

def drift(markers, live, want, stores=STORES):
    """Each store's status from its marker, its live count and the repository's expected values:
    current, behind (marked from another release set), changed (its count moved since it was marked), unmarked, or
    unreachable (the store could not be read: no connection, no login file or a missing table, for example; the
    error's name follows the word). Jena has no marker: judge_jena reads it as current, behind, changed or empty.
    `stores` narrows the report to the stores named (check --store)."""
    rows = []
    for store in stores:
        m = markers.get(store)
        if isinstance(live.get(store), str):
            rows.append((store, "unreachable", live[store]))
        elif store == "jena":
            rows.append((store, *judge_jena(live.get(store) or {}, want["jena_graphs"], want.get("jena_tech"))))
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


def tech_drift(markers, live, digest, stores=STORES):
    """Each store's technical-graph status from its marker (read_tech_markers) and the digest of the files the demo
    loads: current, behind (it holds other graph files), changed (a Neo4j store's Tech node count moved since load
    marked it), unmarked (no marker: a reload wiped it, or the graph was never loaded) or unreachable. The Delta copy
    is the databricks store's: tech_graph sync marks it with the digest of the Neo4j store it copied."""
    rows = []
    for store in stores:
        m = markers.get(store)
        if isinstance(m, str):
            rows.append((store, "unreachable", m))
        elif not m:
            how = "tech_graph sync" if store == "databricks" else f"tech_graph load --store {store}"
            rows.append((store, "unmarked", f"no technical-graph marker: run {how}, or sync"))
        elif m.get("digest") != digest:
            rows.append((store, "behind", f"marked {m.get('marked_at')} from other graph files ({str(m.get('digest'))[:12]}, "
                                          f"not {digest[:12]})"))
        elif store in NEO4J_STORES and isinstance(live.get(store), list) and live[store][2:] != [m.get("nodes")]:
            rows.append((store, "changed", f"marked with {m.get('nodes')} Tech nodes, now holds {live[store][2:]}"))
        else:
            rows.append((store, "current", f"marked {m.get('marked_at')} with the graph files' digest {digest[:12]}"))
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


def jena_select(query):
    request = urllib.request.Request(JENA_QUERY + "?" + urllib.parse.urlencode({"query": query}),
                                     headers={"Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)["results"]["bindings"]


def read_jena():
    """{graph IRI: triple count} of what Jena holds; triples in the default graph, where nothing should be, count as a
    graph of their own so the check reports them."""
    select = jena_select
    held = {r["g"]["value"]: int(r["n"]["value"])
            for r in select("SELECT ?g (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g")}
    in_default = int(select("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }")[0]["n"]["value"])
    if in_default:
        held["(the default graph)"] = in_default
    return held


def resource_counts(session):
    nodes = session.run("MATCH (n:Resource) RETURN count(n) AS n").single()["n"]
    edges = session.run("MATCH (:Resource)-[r]->(:Resource) RETURN count(r) AS n").single()["n"]
    return nodes, edges


def tech_count(session):
    return session.run("MATCH (n:Tech) RETURN count(n) AS n").single()["n"]


def read_markers_and_counts(stores=STORES):
    """Each named store's marker and live count; a store not named is not read (check --store, so a validation whose
    test store is the local Neo4j never touches AuraDB, Jena or Databricks)."""
    markers, live = {}, {}
    for store in [s for s in NEO4J_STORES if s in stores]:
        try:
            driver, session = neo4j_session(store)
            with driver, session:
                rec = session.run("MATCH (m:EpmStoreMarker {store: $s}) RETURN properties(m) AS p", s=store).single()
                markers[store] = rec["p"] if rec else None
                live[store] = [*resource_counts(session), tech_count(session)]
        except Exception as err:  # a store that can't be read (down, or no login file) reads as unreachable, with the reason
            markers[store], live[store] = None, f"unreachable ({type(err).__name__})"
    if "jena" in stores:
        try:
            markers["jena"], live["jena"] = None, read_jena()
        except Exception as err:  # as above: a store that can't be read reads as unreachable, with the reason
            markers["jena"], live["jena"] = None, f"unreachable ({type(err).__name__})"
    if "databricks" not in stores:
        return markers, live
    try:
        conn, schema = databricks()
        with conn, conn.cursor() as cur:
            cur.execute(f"SELECT count(*) FROM {schema}.{TRIPLES_TABLE}")
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


def read_tech_markers(stores=STORES):
    """Each named store's technical-graph marker: a dict, None when it has none, or "unreachable (<error>)"."""
    markers = {}
    for store in stores:
        try:
            if store in NEO4J_STORES:
                driver, session = neo4j_session(store)
                with driver, session:
                    rec = session.run(f"MATCH (m:{TECH_MARKER_LABEL}) RETURN properties(m) AS p").single()
                    markers[store] = rec["p"] if rec else None
            elif store == "jena":
                rows = jena_select(f"SELECT ?d WHERE {{ GRAPH <{TECH_MARKER_GRAPH}> {{ <{TECH_MARKER_GRAPH}> <{TECH_MARKER_DIGEST}> ?d }} }}")
                markers[store] = {"digest": rows[0]["d"]["value"], "marked_at": "by tech_graph load"} if rows else None
            else:
                conn, schema = databricks()
                with conn, conn.cursor() as cur:
                    try:
                        cur.execute(f"SELECT marker FROM {schema}.epm_store_markers WHERE store = '{TECH_MARKER_ROW}'")
                        row = cur.fetchone()
                    except Exception:  # no marker table yet
                        row = None
                    markers[store] = json.loads(row[0]) if row else None
        except Exception as err:  # as read_markers_and_counts: a store that can't be read says so, with the reason
            markers[store] = f"unreachable ({type(err).__name__})"
    return markers


# ---------- marking ----------

def commit():
    """The checkout's commit, written into each marker; a tree without Git (the share release) says so instead."""
    if not os.path.exists(os.path.join(REPO, ".git")):
        return "unknown (not a Git checkout)"
    return subprocess.run(["git", "-C", REPO, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()


def default_ref():
    """Where check and sync read the newest catalog: origin/main in a checkout; the tree itself where there is no Git."""
    return "origin/main" if os.path.exists(os.path.join(REPO, ".git")) else "worktree"


def now():
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def neo4j_checked(store, session, want):
    """A Neo4j store's measured counts, refused unless they match the committed report of the last load, and unless it
    holds one release record for each newest release."""
    report = json.load(open(REPORT))
    nodes, edges = resource_counts(session)
    if (nodes, edges) != (report["nodes"], report["relationships"]):
        raise SystemExit(f"{store}: {nodes} nodes and {edges} relationships, not the last load's {report['nodes']} "
                         f"nodes and {report['relationships']} relationships")
    records = session.run("MATCH (r:ModuleRelease) RETURN r.version_iri AS iri").value()
    if sorted(records) != want["newest"]:
        raise SystemExit(f"{store}: its {len(records)} release record(s) are not one for each of the "
                         f"{len(want['newest'])} newest releases")
    return [nodes, edges, tech_count(session)]


def databricks_checked(cur, schema, want):
    """The triple table's row count, refused unless it holds exactly the graphs a current Jena holds (each newest
    release and its release graphs), each with the release files' triple count: a load that stopped part way, or one
    from other files, is not marked."""
    graphs = want.get("jena_graphs") or jena_graphs(want["newest"])
    cur.execute(f"SELECT graph, count(*) FROM {schema}.{TRIPLES_TABLE} GROUP BY graph")
    held = {r[0]: r[1] for r in cur.fetchall()}
    missing, stray = sorted(set(graphs) - set(held)), sorted(set(held) - set(graphs))
    if missing or stray:
        raise SystemExit(f"databricks: {TRIPLES_TABLE} lacks {len(missing)} graph(s) of the newest releases, e.g. {missing[:3]}, "
                         f"and holds {len(stray)} other(s), e.g. {stray[:3]}")
    moved = sorted(g for g in graphs if held[g] != graphs[g])
    if moved:
        raise SystemExit(f"databricks: {len(moved)} graph(s) hold another row count than the release files' triples, "
                         f"e.g. {moved[0]}: {held[moved[0]]}, not {graphs[moved[0]]}")
    return [sum(held.values())]


def mark(stores, want=None):
    want = want or expected()
    base = {k: want[k] for k in MARKER_FIELDS} | {"marked_at": now(), "commit": commit()}
    for store in stores:
        if store == "jena":  # its graph names are its marker: nothing is written to it
            status, why = judge_jena(read_jena(), jena_graphs(want["newest"]), tech_graph_counts())
            if status != "current":
                raise SystemExit(f"jena: {status}: {why}")
            print(f"jena: current, {why}")
            continue
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
                marker = base | {"store": store, "count": neo4j_checked(store, session, want)}
                session.run("MERGE (m:EpmStoreMarker {store: $s}) SET m = $p", s=store, p=marker).consume()
        print(f"{store}: marked, holding {marker['count']}, from {want['catalog_datasets']} catalog datasets")


# ---------- sync ----------

def plan(behind, cloud, skills, tech_behind=()):
    """The commands that reload the stores that are behind, in order. Local stores always; AuraDB and Databricks only
    with --cloud, through the full driver run, which also reloads the local Neo4j and Jena. A local driver run skips the
    driver's copy, databricks and rebuild steps, so its Neo4j is loaded from the repository, not back from epm_triples.
    Jena alone needs only the driver's jena step. A run that loads Neo4j takes its result into this folder.
    tech_behind names the stores whose technical graph is not current (tech_drift): each gets tech_graph load again,
    as does every store a reload wiped, and the Delta copy follows with tech_graph sync. AuraDB and Databricks again
    only with --cloud."""
    steps, reloaded = [], []
    driver_cmd = ["uv", "run", "--no-project", "--with", "rdflib", "python3", "run_projection.py",
                  "--config", RUN_CONFIG]
    driver_dir = os.path.join(os.path.expanduser(skills), "ontology-to-lpg", "scripts")
    cloud_behind = [s for s in ("aura", "databricks") if s in behind]
    if cloud and cloud_behind:
        steps.append((driver_dir, driver_cmd))
        reloaded += ["driver", "jena", "aura", "databricks"]
    elif "driver" in behind:
        steps.append((driver_dir, driver_cmd + ["--skip", "copy,databricks,rebuild"]))
        reloaded += ["driver", "jena"]
    elif "jena" in behind:
        steps.append((driver_dir, driver_cmd + ["--only", "jena"]))
        reloaded.append("jena")
    if "driver" in reloaded:
        steps.append((HERE, ["uv", "run", "-q", "--with", "rdflib", "--with", "pyshacl", "python", "pipeline.py",
                             "record", "--run", DRIVER_OUT]))
    reachable = [s for s in tech_behind if cloud or s not in ("aura", "databricks")]
    tech = [s for s in [*reloaded, *(s for s in reachable if s not in reloaded)] if s in NEO4J_STORES or s == "jena"]
    if tech:  # a reload wipes the technical graph (runbook, Reload, step 5); load writes each store's marker
        steps.append((DEMO, ["uv", "run", "--group", "graph", "python", "-m", "pricing_demo.tech_graph", "load"]
                      + [a for s in tech for a in ("--store", s)]))
    if "databricks" in reloaded or "databricks" in reachable:  # the Delta copy follows Neo4j, and sync marks it
        steps.append((DEMO, ["uv", "run", "--group", "graph", "python", "-m", "pricing_demo.tech_graph", "sync"]))
    return steps, reloaded


def expected_for(ref, stores):
    """What the named stores should hold; Jena's graph counts are read from the release files only when it is named."""
    want = expected(ref)
    return want | {"jena_graphs": jena_graphs(want["newest"], ref), "jena_tech": tech_graph_counts()} if "jena" in stores else want


def sync(cloud, dry_run, ref, skills):
    markers, live = read_markers_and_counts()
    rows = drift(markers, live, expected_for(ref, STORES))
    behind = [s for s, status, _ in rows if status != "current"]
    tech_behind = [s for s, status, _ in tech_drift(read_tech_markers(), live, tech_digest()) if status != "current"]
    steps, reloaded = plan(behind, cloud, skills, tech_behind)
    skipped = [s for s in behind if s not in reloaded] + [f"{s} (technical graph)" for s in tech_behind
                                                          if s in ("aura", "databricks") and not cloud]
    for cwd, cmd in steps:
        print(f"({os.path.relpath(cwd, REPO) if cwd.startswith(REPO) else cwd}) {' '.join(cmd)}")
        if not dry_run:
            subprocess.run(cmd, cwd=cwd, check=True)
    if skipped:
        print(f"not reloaded (cloud stores need --cloud): {', '.join(skipped)}")
    if not dry_run and reloaded:
        mark(reloaded, expected())
    if not behind and not tech_behind:
        print("every store is current, ontology and technical graph")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=("expected", "mark", "check", "sync"))
    ap.add_argument("--ref", default=default_ref(), help="check, sync: the git ref whose catalog is newest (default origin/main "
                    "in a checkout; worktree, the default without Git, reads this tree)")
    ap.add_argument("--store", action="append", choices=STORES,
                    help="mark: these stores; check: read and judge only these stores (default: every store)")
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
        stores = tuple(args.store) if args.store else STORES
        markers, live = read_markers_and_counts(stores)
        rows = drift(markers, live, expected_for(args.ref, stores), stores)
        tech = tech_drift(read_tech_markers(stores), live, tech_digest(), stores)
        for store, status, why in rows:
            print(f"{store:<11} {status:<9} {why}")
        for store, status, why in tech:  # the technical graph, beside the ontology: tech:<store>
            print(f"{'tech:' + store:<16} {status:<9} {why}")
        sys.exit(0 if all(status == "current" for _, status, _ in rows + tech) else 1)
    else:
        sync(args.cloud, args.dry_run, args.ref, args.skills)


if __name__ == "__main__":
    main()
