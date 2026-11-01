"""The technical graph: the demo pipeline the business ontology does not model, and the decision trail as PROV-O
(EPM-DEC-001-0109, decisions 5 to 7). Run from this machine, in this order:

    uv run --group graph python -m pricing_demo.tech_graph collect   # live facts -> out/tech/live.json; checks; lineage
    uv run --group graph python -m pricing_demo.tech_graph build     # SPARQL Anything over the demo's files -> graph/*.ttl
    uv run --group graph python -m pricing_demo.tech_graph load      # Tech nodes into the local Neo4j stores and AuraDB
    uv run --group graph python -m pricing_demo.tech_graph sync      # Neo4j -> Delta tech_graph_nodes, tech_graph_edges
    uv run --group graph python -m pricing_demo.tech_graph walk      # the Cypher walk from a gold table to its measures

collect reads Postgres (SOURCE_PG_DSN: the exe.dev VM through its tunnel, or the local container), Databricks and
the replica manifest, runs the data-quality checks, compares the ontology's designed lineage with Unity Catalog's
observed lineage, and writes the facts as JSON. build runs the SPARQL Anything queries in sparql/ over the SQL files,
the README's run commands, that JSON and the ontology's CSV tables, then wiring.rq over the result, and writes Turtle.
load gives every node the label Tech and no Resource label, and starts every edge at a Tech node (ending at another
Tech node or an ontology node), so the projection's counts and hashes, which read :Resource nodes and the edges between them, do not change;
load checks that on each store. A driver run empties its store, so run load again after one.
Logins come from the files LOCAL-STORES.md names; no secret is printed.
Sources: SPARQL Anything documentation, v1.3.0 ("Introduction": Facade-X, fx:properties, the location and content
options; the text, CSV and JSON triplifiers); Neo4j Cypher Manual 25, "CREATE" (dynamic labels and relationship types
with $()); Databricks, "Lineage system tables reference" (updated 2026-09-28: one record per read or write of a table,
with its source, target and event time).
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
from decimal import Decimal

from .aura_test import read_env
from .config import GRAPH_SEP, HIDDEN_SYSTEMS, OUT, PROVENANCE, ROOT, SYSTEMS, source_dsn

REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
SPARQL = os.path.join(ROOT, "sparql")
GRAPH = os.path.join(ROOT, "graph")
LIVE = os.path.join(OUT, "tech", "live.json")
LINEAGE = os.path.join(OUT, "tech", "lineage.json")
AURA_TEST = os.path.join(OUT, "tech", "aura-test.json")
MANIFEST = os.path.join(OUT, "replica", "manifest.json")
TECH = "urn:pricing-demo:tech:"
VOCAB = "urn:pricing-demo:tech-vocab#"
ONTOLOGY = "https://w3id.org/lsc/ontology/"
PROV = "http://www.w3.org/ns/prov#"
GRAPH_QUERIES = ("objects.rq", "runtime.rq", "links.rq", "steps.rq")
TRAIL_QUERIES = ("decisions.rq",)
# The designed replica schemas carry the shared asset's system names; the demo's follow its source databases'
# (README.md, "The source systems").
DESIGNED_REPLICA = {"synapse_dev.replica_mips.": "replica_price_assessment.", "synapse_dev.replica_mpr.": "replica_price_reference.",
                    "synapse_dev.replica_kittyhawk.": "replica_reference_data_hub."}
WAS_DERIVED_FROM = PROV + "wasDerivedFrom"
FULL_NAME = ONTOLOGY + "modules/data-product/fullName"
TABLE = ONTOLOGY + "modules/data-product/table/"
LINEAGE_WINDOW_MINUTES = 10  # observed edges count from a target's latest build: its statement's edges share one time
STORES = {  # the stores LOCAL-STORES.md lists, with their login files; the newest file that exists is the live one
    # a full driver run writes the rebuild's login; a run with --skip rebuild writes only the first container's
    "driver": ("bolt://127.0.0.1:17711", ("~/lpg-out/epm-rebuild/neo4j-run/run.env", "~/lpg-out/epm/neo4j-run/run.env")),
    "aura": (None, ("~/.config/neo4j/aura.env",)),
}
WALK = f"""MATCH (gold:Tech:GoldTable {{name: $gold}})<-[:READS_FROM]-(view:Tech:MetricView)-[:IMPLEMENTS]->(m:Resource)
OPTIONAL MATCH (agent:Tech:GenieAgent)-[:BINDS]->(view)
RETURN gold.name AS gold, view.name AS metric_view, m.uri AS measure, m.skos{GRAPH_SEP}prefLabel AS label,
       collect(DISTINCT agent.name) AS agents ORDER BY metric_view, measure"""


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso(value):
    return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if value else None


# ---------- collect ----------

def source_facts(dsn):
    """Each source database, its tables' exact row counts, and the two decision tables the agents may see."""
    import psycopg
    databases, decisions, evidence = [], [], []
    for name in list(SYSTEMS) + list(HIDDEN_SYSTEMS):
        with psycopg.connect(f"{dsn}/{name}") as conn, conn.cursor() as cur:
            cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
            tables = [r[0] for r in cur.fetchall()]
            rows = 0
            for t in tables:
                cur.execute(f'SELECT COUNT(*) FROM public."{t}"')
                rows += cur.fetchone()[0]
            databases.append({"name": name, "hidden": name in HIDDEN_SYSTEMS, "tables": len(tables), "rows": rows})
            if name == "aspen_pims":
                decisions = table_rows(cur, "decision_log", ("OwnerRoleSlugs", "RefineryIris", "MeasureIdentifiers"))
                evidence = table_rows(cur, "decision_evidence", ())
    return databases, decisions, evidence


def table_rows(cur, table, list_columns):
    """A table's rows as dicts with ISO timestamps; the named columns hold ;-separated lists and come back as lists."""
    cur.execute(f'SELECT * FROM public."{table}" ORDER BY 1')
    names = [d.name for d in cur.description]
    out = []
    for row in cur.fetchall():
        item = {}
        for k, v in zip(names, row):
            if isinstance(v, (dt.datetime, dt.date)):
                v = v.isoformat()
            item[k] = [x for x in v.split(";") if x] if k in list_columns and isinstance(v, str) else v
        out.append(item)
    return out


def host_of(dsn):
    """The VM when the DSN goes through its tunnel (README.md, "Run it": port 5433), otherwise the local container."""
    if ":5433" in dsn:
        return {"name": "databases.exe.xyz", "kind": "exe.dev VM, reached through an SSH tunnel"}
    return {"name": "pricing-demo-sources", "kind": "local Docker container"}


def databricks_objects(cur, cat, schemas):
    """Every table and view in the demo's schemas outside the landing schema, with its rows and its last change."""
    from .databricks import count, run
    listed = ", ".join(f"'{s}'" for s in schemas)
    found = run(cur, f"SELECT table_schema, table_name, last_altered FROM {cat}.information_schema.tables "
                     f"WHERE table_schema IN ({listed}) ORDER BY 1, 2")
    return [{"id": f"{s}.{n}", "rows": count(cur, f"{cat}.{s}.{n}", metric_view=s == "semantic_sem_commercial"),
             "last_refresh": iso(t)} for s, n, t in found]


def check(cid, label, covers, fn):
    """Runs one data-quality check: pass when fn returns no problem, otherwise fail with the problem."""
    try:
        problem = fn()
        result, detail = ("pass", "no problem found") if not problem else ("fail", problem)
    except SystemExit as err:  # the demo's own checks stop with the problem as their message
        result, detail = "fail", str(err)
    return {"id": cid, "label": label, "result": result, "detail": detail, "checked_at": now(), "covers": covers}


def quality_checks(cur, cat, objects, manifest, tags):
    from . import databricks as dbx
    ids = [o["id"] for o in objects]
    in_layer = lambda *prefixes: [i for i in ids if i.startswith(prefixes)]
    views = in_layer("semantic_sem_commercial.")

    def tagged():
        found = {t["view"]: t["identifiers"] for t in tags}
        missing = [v for v in views if not str(found.get(v, "")).strip()]
        return f"no epm_measure_identifiers tag on {', '.join(missing)}" if missing else None

    def labelled():
        cols = dbx.run(cur, f"SELECT table_schema, table_name, column_name FROM {cat}.information_schema.columns "
                            "WHERE lower(column_name) LIKE '%provenance%' AND (table_schema LIKE 'silver_%' OR table_schema LIKE 'gold_%')")
        if not cols:
            return "no provenance column found in silver or gold"
        allowed = ", ".join(f"'{p}'" for p in PROVENANCE)
        bad = {f"{s}.{t}.{c}": n for s, t, c in cols
               for n in [dbx.run(cur, f"SELECT COUNT(*) FROM {cat}.{s}.{t} WHERE `{c}` IS NULL OR `{c}` NOT IN ({allowed})")[0][0]] if n}
        return f"rows without a provenance label: {bad}" if bad else None

    def hidden():
        leaked = dbx.run(cur, f"SELECT table_schema, table_name FROM {cat}.information_schema.tables "
                              "WHERE table_schema LIKE '%decision_truth%' OR table_name = 'decision_dossier'")
        named = [f for f in sorted(os.listdir(os.path.join(ROOT, "sql")))
                 if "decision_truth" in re.sub(r"^\s*--.*$", "", open(os.path.join(ROOT, "sql", f)).read(), flags=re.M)]
        return f"decision_truth reached Databricks: {leaked or named}" if leaked or named else None

    return [
        check("replica-matches-manifest", "Each replica table holds the replica manifest's rows, all from its run",
              in_layer("replica_"), lambda: dbx.check_replica_tables(cur, cat, manifest["tables"], manifest["replicated_at"])),
        check("built-objects-hold-rows", "Every silver and gold table, metric view and definitions view exists and holds rows",
              in_layer("silver_", "gold_", "semantic_", "ontology_"), lambda: dbx.check_built(cur, cat)),
        check("metric-views-tagged", "Every metric view carries its epm_measure_identifiers tag", views, tagged),
        check("rows-labelled", "Every silver and gold row with a provenance column says real, spot-anchored or synthesized",
              in_layer("silver_", "gold_"), labelled),
        check("decision-truth-hidden", "No table of decision_truth reaches Databricks, and no SQL file names it",
              ["database:decision_truth"], hidden),
    ]


def designed_lineage(cur, triples):
    """The data-product module's table lineage from the ontology's triple table, in the demo's schema.name form."""
    from .databricks import run
    names = dict(run(cur, f"SELECT DISTINCT subject, object FROM {triples} WHERE predicate = '{FULL_NAME}' AND subject LIKE '{TABLE}%'"))
    edges = run(cur, f"SELECT DISTINCT object, subject FROM {triples} WHERE predicate = '{WAS_DERIVED_FROM}' "
                     f"AND subject LIKE '{TABLE}%' AND object LIKE '{TABLE}%'")
    return {demo_name(names[s]) for s in names}, {(demo_name(names[s]), demo_name(names[t])) for s, t in edges if s in names and t in names}


def demo_name(full_name):
    """synapse_dev.replica_mips.mips_currency -> replica_price_assessment.mips_currency; idp_sbx.x.y -> x.y."""
    for designed, demo in DESIGNED_REPLICA.items():
        if full_name.startswith(designed):
            return demo + full_name[len(designed):]
    return full_name.split(".", 1)[1]


def observed_lineage(cur, cat):
    """Unity Catalog's table lineage into the demo's catalog, keeping for each target only the edges of its latest
    build (the statements that build a table record its edges together)."""
    from .databricks import run
    rows = run(cur, f"""WITH l AS (SELECT source_table_full_name AS s, target_table_full_name AS t, event_time AS e
                          FROM system.access.table_lineage
                          WHERE target_table_catalog = '{cat}' AND source_table_full_name IS NOT NULL AND target_table_full_name IS NOT NULL),
                        latest AS (SELECT t, MAX(e) AS m FROM l GROUP BY t)
                        SELECT DISTINCT l.s, l.t FROM l JOIN latest ON l.t = latest.t
                        WHERE l.e >= latest.m - INTERVAL {LINEAGE_WINDOW_MINUTES} MINUTES""")
    prefix = f"{cat}."
    return {(s[len(prefix):], t[len(prefix):]) for s, t in rows if s.startswith(prefix) and t.startswith(prefix)}


def compare_lineage(designed_tables, designed, observed, present):
    """Edges found in only one place, within the tables the design names. A designed edge to or from a table the
    demo does not build is listed apart: it cannot be observed."""
    absent = {e for e in designed if e[0] not in present or e[1] not in present}
    in_scope = {e for e in observed if e[0] in designed_tables and e[1] in designed_tables}
    return {"designed_only": sorted(designed - absent - in_scope), "observed_only": sorted(in_scope - designed),
            "matched": sorted(designed & in_scope), "designed_not_built": sorted(absent)}


def lineage_check(cur, cat, triples, present):
    try:
        tables, designed = designed_lineage(cur, triples)
        found = compare_lineage(tables, designed, observed_lineage(cur, cat), set(present))
    except Exception as err:  # Free Edition may lack the system tables: the test is skipped with the reason
        return {"id": "designed-vs-observed-lineage", "label": "Designed lineage matches Unity Catalog's observed lineage",
                "result": "skipped", "detail": f"{type(err).__name__}: {str(err).splitlines()[0][:300]}", "checked_at": now(),
                "covers": []}
    os.makedirs(os.path.dirname(LINEAGE), exist_ok=True)
    with open(LINEAGE, "w") as f:
        json.dump(found, f, indent=2)
    differs = found["designed_only"] or found["observed_only"]
    detail = (f"{len(found['matched'])} edges match; {len(found['designed_only'])} designed only; "
              f"{len(found['observed_only'])} observed only; {len(found['designed_not_built'])} designed edges touch "
              "a table the demo does not build")
    covered = sorted({n for e in found["matched"] + found["designed_only"] + found["observed_only"] for n in e} & set(present))
    return {"id": "designed-vs-observed-lineage", "label": "Designed lineage matches Unity Catalog's observed lineage",
            "result": "differs" if differs else "pass", "detail": detail, "checked_at": now(), "covers": covered}


def aura_check():
    if not os.path.exists(AURA_TEST):
        return None
    result = json.load(open(AURA_TEST))
    probe = result.get("probe") or {}
    ok = bool(probe) and all(step["ok"] for step in probe.values())
    detail = "; ".join(f"{k}: {'ok' if v['ok'] else v['error']}" for k, v in sorted(probe.items())) or "no probe result"
    return {"id": "databricks-reaches-auradb", "label": "A Databricks job reaches AuraDB with the login in secret scope epm-neo4j",
            "result": "pass" if ok else "fail", "detail": detail, "checked_at": result["started"],
            "covers": ["epm_triples"]}


def collect(manifest_path=MANIFEST):
    from . import genie
    from .databricks import SCHEMAS, connect, current_catalog, run
    dsn = source_dsn()
    databases, decisions, evidence = source_facts(dsn)
    manifest = json.load(open(manifest_path))
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        objects = databricks_objects(cur, cat, SCHEMAS[1:])
        tags = [{"view": f"{s}.{t}", "identifiers": v} for s, t, v in run(
            cur, f"SELECT schema_name, table_name, tag_value FROM {cat}.information_schema.table_tags "
                 "WHERE tag_name = 'epm_measure_identifiers' ORDER BY 1, 2")]
        checks = quality_checks(cur, cat, objects, manifest, tags)
        checks.append(lineage_check(cur, cat, e["EPM_TRIPLES"], [o["id"] for o in objects]))
    aura = aura_check()
    if aura:
        checks.append(aura)
    agents = [{"slug": slug(title), "title": title, "views": [t for t, _ in spec["tables"]]} for title, spec in genie.AGENTS.items()]
    live = {"collected_at": now(), "catalog": cat, "triples": e["EPM_TRIPLES"], "host": host_of(dsn),
            "replicated_at": manifest["replicated_at"], "databases": databases, "objects": objects, "tags": tags,
            "agents": agents, "checks": checks, "decisions": decisions, "evidence": evidence}
    os.makedirs(os.path.dirname(LIVE), exist_ok=True)
    with open(LIVE, "w") as f:
        json.dump(live, f, indent=2, default=str)
    for c in checks:
        print(f"check {c['id']}: {c['result']} ({c['detail'][:160]})")
    print(f"wrote {LIVE}: {len(databases)} databases, {len(objects)} objects, {len(decisions)} decisions, {len(evidence)} evidence items")
    return live


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


# ---------- build ----------

def query_text(name, **fill):
    text = open(os.path.join(SPARQL, name)).read()
    for key, value in {"DEMO": ROOT, "REPO": REPO, "LIVE": LIVE, **fill}.items():
        text = text.replace(f"%{key}%", value)
    return text


def queries(names):
    """(query file, its text) for each run: objects.rq once per SQL file, the others once."""
    for name in names:
        if name == "objects.rq":
            for path in sorted(glob.glob(os.path.join(ROOT, "sql", "0[2-9]_*.sql"))):
                yield name, query_text(name, SQL_FILE=path, SQL_NAME=f"sql/{os.path.basename(path)}")
        else:
            yield name, query_text(name)


def construct(names):
    import pysparql_anything as sa
    from rdflib import Graph
    engine = sa.SparqlAnything()
    g = Graph()
    for _, text in queries(names):
        g += engine.construct(query=text)
    return g


def typed_only(g, typed):
    """Drops statements about technical-graph IRIs no query typed: a designed table the demo does not build."""
    from rdflib import URIRef
    for s, p, o in list(g):
        if (str(s).startswith(TECH) and s not in typed) or (isinstance(o, URIRef) and str(o).startswith(TECH) and o not in typed):
            g.remove((s, p, o))
    return g


def build():
    from rdflib import RDF, Namespace
    graph = construct(GRAPH_QUERIES)
    graph += graph.query(open(os.path.join(SPARQL, "wiring.rq")).read()).graph
    trail = construct(TRAIL_QUERIES)
    typed = set(graph.subjects(RDF.type, None)) | set(trail.subjects(RDF.type, None))
    os.makedirs(GRAPH, exist_ok=True)
    for name, g in (("tech-graph.ttl", graph), ("decision-trail.ttl", trail)):
        g = typed_only(g, typed)
        for prefix, ns in (("tv", VOCAB), ("tech", TECH), ("prov", PROV), ("measure", ONTOLOGY + "modules/kpi/measure/")):
            g.bind(prefix, Namespace(ns))
        g.serialize(os.path.join(GRAPH, name), format="turtle")
        nodes, edges = graph_rows(g)
        print(f"wrote graph/{name}: {len(nodes)} nodes, {len(edges)} edges")
    return graph, trail


# ---------- Neo4j ----------

def local_name(iri):
    return re.split(r"[#/:]", str(iri))[-1]


def edge_type(predicate):
    """readsFrom -> READS_FROM, prov:wasGeneratedBy -> WAS_GENERATED_BY."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", local_name(predicate)).upper()


def neo4j_value(value):
    """A literal as Neo4j stores it: dates as ISO text; JSON numbers, which reach the graph as xsd:decimal, as
    integers when whole and floats otherwise (Bolt has no decimal type)."""
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


def graph_rows(g):
    """Neo4j rows from the Turtle: a node per typed technical-graph IRI, labelled Tech and its tv: classes, with its
    literals as properties; an edge per IRI-valued statement, to a Tech node or to an ontology resource."""
    from rdflib import RDF, Literal, URIRef
    nodes, edges = {}, []
    for s in sorted(set(g.subjects(RDF.type, None)), key=str):
        if not str(s).startswith(TECH):
            continue
        classes = sorted(local_name(c) for c in g.objects(s, RDF.type) if str(c).startswith(VOCAB))
        props = {"uri": str(s)}
        for p, o in g.predicate_objects(s):
            if isinstance(o, Literal):
                props[local_name(p)] = neo4j_value(o.toPython())
        props["types"] = sorted(str(c) for c in g.objects(s, RDF.type))
        nodes[str(s)] = {"labels": ["Tech"] + classes, "props": props}
    for s, p, o in sorted(g, key=lambda t: tuple(map(str, t))):
        if str(s) in nodes and isinstance(o, URIRef) and p != RDF.type:
            edges.append({"s": str(s), "t": edge_type(p), "o": str(o), "ontology": not str(o).startswith(TECH)})
    return list(nodes.values()), edges


def apply_store_overrides():
    """EPM_STORES_JSON names other stores for a test run (as in projection/sync_stores.py): each of driver and
    aura may give {"bolt": ..., "env": [...]}."""
    raw = os.environ.get("EPM_STORES_JSON")
    if not raw:
        return
    over = json.loads(raw)
    for store in list(STORES):
        if store in over:
            STORES[store] = (over[store].get("bolt", STORES[store][0]), tuple(over[store].get("env", STORES[store][1])))


apply_store_overrides()


def login_file(paths):
    """The newest of a store's login files that exists: the one its running container wrote."""
    found = [p for p in (os.path.expanduser(q) for q in paths) if os.path.exists(p)]
    if not found:
        raise SystemExit(f"no login file: {', '.join(paths)}")
    return max(found, key=os.path.getmtime)


def neo4j_login(store):
    bolt, paths = STORES[store]
    values = read_env(login_file(paths))
    uri = bolt or values["NEO4J_URI"]
    return uri, values.get("NEO4J_USERNAME", "neo4j"), values.get("NEO4J_PASSWORD") or values["PASSWORD"]


def ontology_counts(session):
    """What the projection counts: :Resource nodes and the edges between them (the skill's load_verify.hash_graph; runbook, Check)."""
    nodes = session.run("MATCH (n:Resource) RETURN count(n) AS n").single()["n"]
    edges = session.run("MATCH (:Resource)-[r]->(:Resource) RETURN count(r) AS n").single()["n"]
    return nodes, edges


def load_store(store, nodes, edges):
    from neo4j import GraphDatabase
    uri, user, password = neo4j_login(store)
    with GraphDatabase.driver(uri, auth=(user, password)) as driver, driver.session() as session:
        before = ontology_counts(session)
        session.run("MATCH (n:Tech) DETACH DELETE n").consume()
        session.run("UNWIND $rows AS row CREATE (n:$(row.labels)) SET n = row.props", rows=nodes).consume()
        made = {"tech": 0, "ontology": 0}
        for kind, target in (("tech", "Tech"), ("ontology", "Resource")):
            rows = [e for e in edges if e["ontology"] == (kind == "ontology")]
            made[kind] = session.run(f"UNWIND $rows AS row MATCH (a:Tech {{uri: row.s}}), (b:{target} {{uri: row.o}}) "
                                     "CREATE (a)-[:$(row.t)]->(b) RETURN count(*) AS n", rows=rows).single()["n"]
            if made[kind] != len(rows):
                found = set(session.run(f"UNWIND $uris AS u MATCH (b:{target} {{uri: u}}) RETURN b.uri AS u",
                                        uris=sorted({e["o"] for e in rows})).value())
                missing = sorted({e["o"] for e in rows} - found)
                raise SystemExit(f"{store}: {len(rows) - made[kind]} {kind} edges found no target, e.g. {missing[:5]}")
        after = ontology_counts(session)
    if before != after:
        raise SystemExit(f"{store}: the ontology's counts changed from {before} to {after}")
    print(f"{store}: {len(nodes)} Tech nodes, {made['tech']} edges between them, {made['ontology']} to ontology nodes; "
          f"ontology unchanged at {after[0]} nodes and {after[1]} relationships")
    return {"store": store, "nodes": len(nodes), "tech_edges": made["tech"], "ontology_edges": made["ontology"],
            "resource_nodes": after[0], "resource_relationships": after[1]}


def read_graph():
    from rdflib import Graph
    g = Graph()
    for name in ("tech-graph.ttl", "decision-trail.ttl"):
        g.parse(os.path.join(GRAPH, name), format="turtle")
    return g


def load(stores=tuple(STORES)):
    nodes, edges = graph_rows(read_graph())
    return [load_store(s, nodes, edges) for s in stores]


def walk(store="driver", gold="gold_commercial_core.mips_mpr_executive_summary_fact"):
    from neo4j import GraphDatabase
    uri, user, password = neo4j_login(store)
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        records, _, _ = driver.execute_query(WALK, gold=gold)
    print(WALK)
    for r in records:
        print(dict(r))
    return [dict(r) for r in records]


# ---------- Delta ----------

def sync(store="driver"):
    """Copies the Tech nodes and their edges from Neo4j, the source, into the two Delta tables sql/07 creates."""
    from neo4j import GraphDatabase
    from .databricks import connect, current_catalog, run
    uri, user, password = neo4j_login(store)
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        nodes, _, _ = driver.execute_query("MATCH (n:Tech) RETURN n.uri AS uri, labels(n) AS labels, properties(n) AS p ORDER BY uri")
        edges, _, _ = driver.execute_query("MATCH (a:Tech)-[r]->(b) RETURN a.uri AS s, type(r) AS t, b.uri AS o, "
                                           "b:Resource AS ontology ORDER BY s, t, o")
    synced = now()
    node_rows = [(n["uri"], next((l for l in sorted(n["labels"]) if l != "Tech"), "Tech"), n["p"].get("name"),
                  json.dumps({k: v for k, v in n["p"].items() if k not in ("uri", "name")}, sort_keys=True, default=str))
                 for n in nodes]
    edge_rows = [(r["s"], r["t"], r["o"], bool(r["ontology"])) for r in edges]
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        for table, rows in (("tech_graph_nodes", node_rows), ("tech_graph_edges", edge_rows)):
            run(cur, f"DELETE FROM {cat}.tech_graph.{table}")
            for i in range(0, len(rows), 100):
                batch = rows[i:i + 100]
                marks = ", ".join("(" + ", ".join(["?"] * len(row)) + f", TIMESTAMP '{synced}')" for row in batch)
                cur.execute(f"INSERT INTO {cat}.tech_graph.{table} VALUES {marks}", [v for row in batch for v in row])
            n = run(cur, f"SELECT COUNT(*) FROM {cat}.tech_graph.{table}")[0][0]
            if n != len(rows):
                raise SystemExit(f"{cat}.tech_graph.{table} holds {n} rows; Neo4j has {len(rows)}")
            print(f"{cat}.tech_graph.{table}: {n} rows from Neo4j ({store})")
    return len(node_rows), len(edge_rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("collect", "build", "load", "sync", "walk"))
    ap.add_argument("--store", action="append", choices=tuple(STORES), help="load: these stores only (default: all)")
    ap.add_argument("--manifest", default=MANIFEST, help="collect: the replica manifest the Databricks replica came from")
    args = ap.parse_args()
    if args.step == "collect":
        collect(args.manifest)
    elif args.step == "load":
        load(tuple(args.store or STORES))
    else:
        {"build": build, "sync": sync, "walk": walk}[args.step]()
