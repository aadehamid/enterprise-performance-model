"""The technical graph: the demo pipeline the business ontology does not model, and the decision trail as PROV-O
(EPM-DEC-001-0109, decisions 5 to 7). Run from this machine, in this order:

    uv run --group graph python -m pricing_demo.tech_graph collect   # live facts -> out/tech/live.json; checks; lineage
    uv run --group graph python -m pricing_demo.tech_graph build     # SPARQL Anything over the demo's files -> out/tech/graph/*.ttl
    uv run --group graph python -m pricing_demo.tech_graph compare   # the refreshed graph's structure against graph/*.ttl
    uv run --group graph python -m pricing_demo.tech_graph lineage   # designed, SQL and observed lineage against graph/lineage-known.json
    uv run --group graph python -m pricing_demo.tech_graph load      # Tech nodes into the local Neo4j and AuraDB, named graphs in Jena
    uv run --group graph python -m pricing_demo.tech_graph sync      # Neo4j -> Delta tech_graph_nodes, tech_graph_edges
    uv run --group graph python -m pricing_demo.tech_graph walk      # the Cypher walk from a gold table to its measures

collect reads Postgres (SOURCE_PG_DSN: the exe.dev VM through its tunnel, or the local container), Databricks and
the replica manifest, runs the data-quality checks, compares the ontology's designed lineage with Unity Catalog's
observed lineage, and writes the facts as JSON. It also writes out/tech/proposals.json: what it saw with no ontology
match, drafted for kpi or data-product with the observed lineage behind it. Databricks writes to the technical graph,
never to the ontology (#457). build runs the SPARQL Anything queries in sparql/ over the SQL files, the README's run
commands, that JSON and the ontology's CSV tables, then wiring.rq over the result, and writes Turtle; an object
Databricks holds that no SQL file creates gets its node from collect's facts. lineage sets each edge between the
design's tables beside the sources that hold it: the design (data-product), the SQL files (the graph's readsFrom) and
Unity Catalog.
load gives every node the label Tech and no Resource label, and starts every edge at a Tech node (ending at another
Tech node or an ontology node), so the projection's counts and hashes, which read :Resource nodes and the edges between them, do not change;
load checks that on each store. The technical graph uses the technical-graph module's terms (EPM-DEC-001-0112, item 4),
so the shapes in business_architecture/ontology/technical-graph/shapes.ttl check it; a node's labels are its module
class (a replica, silver or gold table is a Table with a layer property). The decision trail keeps the demo's own
vocabulary (VOCAB) for the terms the module does not define: Decision, EvidenceItem, affects, concerns, domain, kind,
name, recordedIn and selectedOption. A driver run empties its store, so run load again after one. In Jena each file is its
own named graph beside the release graphs, and load fails when an edge's ontology target is in no release graph.

graph/*.ttl is what the release ships, from an earlier collect. build writes a refreshed copy to out/tech/graph/, which
Git ignores, and load takes that copy when it exists. compare separates volatile values (row counts, refresh times, a
check's result, the host) from everything else (objects, edges and stable values), and a difference there fails. build --to-repo
writes graph/*.ttl instead, for a change that is meant to ship.
Logins come from the files LOCAL-STORES.md names; no secret is printed.
Sources: SPARQL Anything documentation, v1.3.0 ("Introduction": Facade-X, fx:properties, the location and content
options; the text, CSV and JSON triplifiers); Neo4j Cypher Manual 25, "CREATE" (dynamic labels and relationship types
with $()); Databricks, "Lineage system tables reference" (updated 2026-09-28: one record per read or write of a table,
with its source, target and event time); "SCHEMA_TAGS" (updated 2026-09-11: catalog_name, schema_name, tag_name,
tag_value).
"""
import argparse
import csv
import datetime as dt
import glob
import itertools
import json
import os
import re
import time
import urllib.parse
import urllib.request
from decimal import Decimal

from .aura_test import read_env
from .config import GRAPH_SEP, HIDDEN_SYSTEMS, OUT, PROVENANCE, ROOT, SOURCE_TAG, SYSTEM_MODULE, SYSTEMS, source_dsn

REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
SPARQL = os.path.join(ROOT, "sparql")
GRAPH = os.path.join(ROOT, "graph")
REFRESHED = os.path.join(OUT, "tech", "graph")
GRAPH_FILES = ("tech-graph.ttl", "decision-trail.ttl")
KNOWN_LINEAGE = os.path.join(GRAPH, "lineage-known.json")
JENA_GRAPHS = {"tech-graph.ttl": "urn:pricing-demo:graph:tech-graph", "decision-trail.ttl": "urn:pricing-demo:graph:decision-trail"}
JENA_QUERY = "http://127.0.0.1:13031/ds/query"  # projection/skill-run/epm-run.json's "jena"
LIVE = os.path.join(OUT, "tech", "live.json")
LINEAGE = os.path.join(OUT, "tech", "lineage.json")
PROPOSALS = os.path.join(OUT, "tech", "proposals.json")
MEASURE_IDENTIFIERS = os.path.join(REPO, "business_architecture", "ontology", "kpi", "measure-identifiers.csv")
AURA_TEST = os.path.join(OUT, "tech", "aura-test.json")
MANIFEST = os.path.join(OUT, "replica", "manifest.json")
TECH = "urn:pricing-demo:tech:"
VOCAB = "urn:pricing-demo:tech-vocab#"  # the decision trail's own terms, which the technical-graph module does not define
TG = "https://w3id.org/lsc/ontology/modules/technical-graph/"
LAYER = "https://w3id.org/lsc/ontology/modules/data-product/layer/"
RESULT = TG + "check-result/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
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
LINEAGE_POLL_SECONDS = 60  # how often collect --lineage-wait reads Unity Catalog's lineage again
SOURCES = ("designed", "sql", "observed")  # where lineage reads an edge: data-product, the SQL files, Unity Catalog
# A schema's layer, the module class and the value of data-product's layer list (None: no layer), as sparql/objects.rq
# gives them; the last entry takes any other schema.
LAYERS = (("replica_", "replica", "Table", "replica"), ("silver_", "silver", "Table", "silver"), ("gold_", "gold", "Table", "gold"),
          ("semantic_sem_commercial", "metric-view", "MetricView", "metric-view"),
          ("ontology_definitions", "definitions", "DefinitionsView", None), ("", "tech-graph", "Table", None))
STORES = {  # the stores LOCAL-STORES.md lists, with their login files; the newest file that exists is the live one
    # a full driver run writes the rebuild's login; a run with --skip rebuild writes only the first container's
    "driver": ("bolt://127.0.0.1:17711", ("~/lpg-out/epm-rebuild/neo4j-run/run.env", "~/lpg-out/epm/neo4j-run/run.env")),
    "aura": (None, ("~/.config/neo4j/aura.env",)),
}
WALK = f"""MATCH (gold:Tech:Table {{name: $gold, layer: 'gold'}})<-[:READS_FROM]-(view:Tech:MetricView)-[:IMPLEMENTS]->(m:Resource)
OPTIONAL MATCH (agent:Tech:Agent)-[:BINDS]->(view)
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


def quality_checks(cur, cat, objects, manifest, tags, source_tags):
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
        check("source-systems-agree", "Each replica schema's epm_source_system tag names the system README.md maps its database to",
              [f"database:{d}" for d in sorted(source_tags)], lambda: systems_disagree(source_tags)),
    ]


def source_systems(source_tags):
    """The system each source database stands for: its replica schema's epm_source_system tag as deployed, or, with no
    tag, README.md's map (config.SYSTEM_MODULE). links.rq reads this list from live.json."""
    found = {**{d: (s, "README.md") for d, s in SYSTEM_MODULE.items()}, **{d: (s, "tag") for d, s in source_tags.items()}}
    return [{"database": d, "system": s, "from": source} for d, (s, source) in sorted(found.items())]


def systems_disagree(source_tags):
    """A tag that names another system than README.md's map does for the same database."""
    bad = [f"{d}: tag {s}, README.md {SYSTEM_MODULE[d]}" for d, s in sorted(source_tags.items())
           if d in SYSTEM_MODULE and s != SYSTEM_MODULE[d]]
    return "; ".join(bad) or None


def designed_lineage(cur, triples):
    """The data-product module's table lineage from the ontology's triple table, in the demo's schema.name form."""
    from .databricks import run
    names = run(cur, f"SELECT DISTINCT subject, object FROM {triples} WHERE predicate = '{FULL_NAME}' AND subject LIKE '{TABLE}%'")
    edges = run(cur, f"SELECT DISTINCT object, subject FROM {triples} WHERE predicate = '{WAS_DERIVED_FROM}' "
                     f"AND subject LIKE '{TABLE}%' AND object LIKE '{TABLE}%'")
    return designed_from(names, edges)


def designed_from(names, edges):
    """(table IRI, fullName) rows and (source IRI, target IRI) rows -> the designed tables and edges in schema.name form."""
    names = dict(names)
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


def lineage_gaps(designed, present, observed):
    """Built tables the design says read something, with no observed edge into them yet: Unity Catalog can lag a build."""
    return sorted({t for s, t in designed if s in present and t in present} - {t for _, t in observed})


def lineage_check(cur, cat, triples, present, wait=0, sleep=time.sleep, clock=time.monotonic):
    """The lineage comparison. With wait, a table whose events have not arrived is read again until they do or the seconds
    run out, so a lag does not read as a difference; an edge still missing then is reported as it stands."""
    try:
        tables, designed = designed_lineage(cur, triples)
        deadline = clock() + wait
        observed = observed_lineage(cur, cat)
        while lineage_gaps(designed, set(present), observed) and clock() < deadline:
            sleep(LINEAGE_POLL_SECONDS)
            observed = observed_lineage(cur, cat)
        found = compare_lineage(tables, designed, observed, set(present))
    except Exception as err:  # Free Edition may lack the system tables: the test is skipped with the reason
        return {"id": "designed-vs-observed-lineage", "label": "Designed lineage matches Unity Catalog's observed lineage",
                "result": "skipped", "detail": f"{type(err).__name__}: {str(err).splitlines()[0][:300]}", "checked_at": now(),
                "covers": []}, None
    # What lineage compares with the SQL files once build has run: every observed edge in the catalog, not only the design's.
    inputs = {"designed_tables": sorted(tables), "designed": sorted(designed), "observed": sorted(observed), "present": sorted(present)}
    os.makedirs(os.path.dirname(LINEAGE), exist_ok=True)
    with open(LINEAGE, "w") as f:
        json.dump(inputs, f, indent=2)
    differs = found["designed_only"] or found["observed_only"]
    detail = (f"{len(found['matched'])} edges match; {len(found['designed_only'])} designed only; "
              f"{len(found['observed_only'])} observed only; {len(found['designed_not_built'])} designed edges touch "
              "a table the demo does not build")
    covered = sorted({n for e in found["matched"] + found["designed_only"] + found["observed_only"] for n in e} & set(present))
    return {"id": "designed-vs-observed-lineage", "label": "Designed lineage matches Unity Catalog's observed lineage",
            "result": "differs" if differs else "pass", "detail": detail, "checked_at": now(), "covers": covered}, inputs


def aura_check():
    """The AuraDB probe's result as a check, or None when there is none. A result from before the run that
    EPM_RUN_STARTED names (rebuild_stores.py and the share-release validation set it) is an earlier run's: it does not
    count, so a stale out/tech/aura-test.json cannot stand in for this run's probe."""
    if not os.path.exists(AURA_TEST):
        return None
    result = json.load(open(AURA_TEST))
    run_started = os.environ.get("EPM_RUN_STARTED")
    if run_started and result.get("started", "") < run_started:
        print(f"{AURA_TEST} is from {result.get('started')}, before this run started at {run_started}: not counted")
        return None
    probe = result.get("probe") or {}
    ok = bool(probe) and all(step["ok"] for step in probe.values())
    detail = "; ".join(f"{k}: {'ok' if v['ok'] else v['error']}" for k, v in sorted(probe.items())) or "no probe result"
    return {"id": "databricks-reaches-auradb", "label": "A Databricks job reaches AuraDB with the login in secret scope epm-neo4j",
            "result": "pass" if ok else "fail", "detail": detail, "checked_at": result["started"],
            "covers": ["epm_triples"]}


def category(sources):
    """The name of the sources that hold an edge: all three, one (designed_only) or two (designed_and_sql)."""
    return "in_all_three" if len(sources) == 3 else f"{sources[0]}_only" if len(sources) == 1 else "_and_".join(sources)


CATEGORIES = [category(c) for n in (3, 2, 1) for c in itertools.combinations(SOURCES, n)]


def sql_lineage(g):
    """The graph's readsFrom edges that objects.rq read from the SQL files (the reader has tg:definedIn), as
    (source, target) in schema.name form."""
    from rdflib import URIRef
    obj = TECH + "object/"
    defined = set(g.subjects(URIRef(TG + "definedIn"), None))
    return {(str(o)[len(obj):], str(s)[len(obj):]) for s, o in g.subject_objects(URIRef(TG + "readsFrom"))
            if s in defined and str(o).startswith(obj)}


def confirm_lineage(designed_tables, designed, sql, observed, present):
    """Each edge between tables the design names, under the sources that hold it. A designed edge to or from a table
    the demo does not build can be neither built nor observed, so it is listed apart, as designed_not_built."""
    designed = {tuple(e) for e in designed}
    absent = {e for e in designed if e[0] not in present or e[1] not in present}
    inside = lambda edges: {tuple(e) for e in edges if e[0] in designed_tables and e[1] in designed_tables}
    held = {"designed": designed - absent, "sql": inside(sql), "observed": inside(observed)}
    found = {c: [] for c in CATEGORIES}
    for e in sorted(set().union(*held.values())):
        found[category([s for s in SOURCES if e in held[s]])].append(list(e))
    return {**found, "designed_not_built": [list(e) for e in sorted(absent)]}


def lineage_gate(found, known):
    """What differs between a lineage comparison and the differences the release states it expects: the demo is simpler
    than the design in known places. Empty means the comparison holds nothing new. An edge in all three sources is no
    difference."""
    problems = []
    for key in CATEGORIES[1:] + ["designed_not_built"]:
        got, want = {tuple(e) for e in found.get(key, [])}, {tuple(e) for e in known.get(key, [])}
        problems += [f"{key}: new {e[0]} -> {e[1]}" for e in sorted(got - want)]
        problems += [f"{key}: no longer {e[0]} -> {e[1]}" for e in sorted(want - got)]
    return problems


def lineage():
    """Sets each edge beside the sources that hold it: the last collect's designed and observed lineage, and the SQL
    files' as the graph build wrote it (or as the release ships it). Writes the result into out/tech/lineage.json and
    fails on a difference graph/lineage-known.json does not state."""
    if not os.path.exists(LINEAGE):
        raise SystemExit(f"no {LINEAGE}: the lineage check was skipped or collect has not run")
    inputs, known = json.load(open(LINEAGE)), json.load(open(KNOWN_LINEAGE))
    found = confirm_lineage(set(inputs["designed_tables"]), inputs["designed"], sql_lineage(read_graph()), inputs["observed"],
                            set(inputs["present"]))
    with open(LINEAGE, "w") as f:
        json.dump({**inputs, "edges": found}, f, indent=2)
    problems = lineage_gate(found, known)
    for problem in problems:
        print(f"FAIL {problem}")
    print("; ".join(f"{len(found[c])} {c}" for c in CATEGORIES + ["designed_not_built"])
          + f"; {len(problems)} not stated in {os.path.basename(KNOWN_LINEAGE)}")
    if problems:
        raise SystemExit(1)


def proposals(tags, objects, inputs, identifiers):
    """What collect saw with no ontology match, drafted for a person to take to kpi or data-product: an identifier a
    metric view's tag lists that no kpi measure carries, and a built table or view the data-product design does not
    name (known only when the lineage check ran). Each carries the observed edges into it. Nothing writes to the ontology."""
    observed = [tuple(e) for e in (inputs or {}).get("observed", [])]
    into = lambda name: [[s, t] for s, t in observed if t == name]
    found = [{"module": "kpi", "draft": f"a measure with the identifier {i}", "identifier": i, "view": t["view"],
              "observed_lineage": into(t["view"])}
             for t in tags for i in str(t["identifiers"]).split() if i not in identifiers]
    if inputs:
        designed = set(inputs["designed_tables"])
        found += [{"module": "data-product", "draft": f"a table design for {o['id']}", "table": o["id"],
                   "observed_lineage": into(o["id"])} for o in objects if o["id"] not in designed]
    return found


def collect(manifest_path=MANIFEST, lineage_wait=0):
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
        source_tags = {s[len("replica_"):]: v for s, v in run(
            cur, f"SELECT schema_name, tag_value FROM {cat}.information_schema.schema_tags "
                 f"WHERE tag_name = '{SOURCE_TAG}' ORDER BY 1") if s.startswith("replica_")}
        checks = quality_checks(cur, cat, objects, manifest, tags, source_tags)
        lineage_result, inputs = lineage_check(cur, cat, e["EPM_TRIPLES"], [o["id"] for o in objects], lineage_wait)
        checks.append(lineage_result)
    aura = aura_check()
    if aura:
        checks.append(aura)
    agents = [{"slug": slug(title), "title": title, "views": [t for t, _ in spec["tables"]]} for title, spec in genie.AGENTS.items()]
    live = {"collected_at": now(), "catalog": cat, "triples": e["EPM_TRIPLES"], "host": host_of(dsn),
            "replicated_at": manifest["replicated_at"], "databases": databases, "objects": objects, "tags": tags,
            "source_systems": source_systems(source_tags), "agents": agents, "checks": checks, "decisions": decisions,
            "evidence": evidence}
    os.makedirs(os.path.dirname(LIVE), exist_ok=True)
    with open(LIVE, "w") as f:
        json.dump(live, f, indent=2, default=str)
    identifiers = {row["identifier"] for row in csv.DictReader(open(MEASURE_IDENTIFIERS))}
    drafted = proposals(tags, objects, inputs, identifiers)
    with open(PROPOSALS, "w") as f:
        json.dump(drafted, f, indent=2)
    print(f"wrote {PROPOSALS}: {len(drafted)} proposals for kpi or data-product, for a person to review")
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


def databricks_only(g, objects, observed):
    """Objects Databricks holds that no SQL file creates, such as a metric view made in the workspace: each gets its
    class and layer from its schema, as objects.rq gives the rest, and reads what Unity Catalog's lineage says it reads.
    links.rq links its tag's identifiers as for any view. Returns their names."""
    from rdflib import RDF, Literal, URIRef
    typed, added = set(g.subjects(RDF.type, None)), []
    for o in objects:
        iri = URIRef(TECH + "object/" + o["id"])
        if iri not in typed:
            cls, layer = next((cls, layer) for prefix, _, cls, layer in LAYERS if o["id"].startswith(prefix))
            g.add((iri, RDF.type, URIRef(TG + cls)))
            g.add((iri, URIRef(TG + "name"), Literal(o["id"])))
            if layer:
                g.add((iri, URIRef(TG + "layer"), URIRef(LAYER + layer)))
            added.append(o["id"])
    for source, target in observed:
        if target in added:
            g.add((URIRef(TECH + "object/" + target), URIRef(TG + "readsFrom"), URIRef(TECH + "object/" + source)))
    return added


def build(to_repo=False):
    from rdflib import RDF, Namespace
    graph = construct(GRAPH_QUERIES)
    graph += graph.query(open(os.path.join(SPARQL, "wiring.rq")).read()).graph
    observed = json.load(open(LINEAGE)).get("observed", []) if os.path.exists(LINEAGE) else []
    databricks_only(graph, json.load(open(LIVE))["objects"], observed)
    trail = construct(TRAIL_QUERIES)
    typed = set(graph.subjects(RDF.type, None)) | set(trail.subjects(RDF.type, None))
    folder = GRAPH if to_repo else REFRESHED
    os.makedirs(folder, exist_ok=True)
    for name, g in zip(GRAPH_FILES, (graph, trail)):
        g = typed_only(g, typed)
        for prefix, ns in (("tv", VOCAB), ("tg", TG), ("layer", LAYER), ("result", RESULT), ("rdfs", RDFS), ("tech", TECH),
                           ("prov", PROV), ("measure", ONTOLOGY + "modules/kpi/measure/")):
            g.bind(prefix, Namespace(ns))
        g.serialize(os.path.join(folder, name), format="turtle")
        nodes, edges = graph_rows(g)
        print(f"wrote {os.path.relpath(os.path.join(folder, name), ROOT)}: {len(nodes)} nodes, {len(edges)} edges")
    return graph, trail


# What a run changes, named one by one: anything else that differs is a difference in structure.
VOLATILE = tuple(TG + name for name in ("rows", "tables", "lastRefresh", "checkedAt", "result", "detail"))


def structure(g):
    """A graph's objects, edges and stable values, without what a run changes: the VOLATILE values, and the host, which
    names the machine the source databases ran on. Returns (typed nodes, statements)."""
    from rdflib import RDF
    host = TG + "hostedOn"
    hosts = {s for s, o in g.subject_objects(RDF.type) if str(o) == TG + "Host"}
    nodes = {(str(s), str(o)) for s, o in g.subject_objects(RDF.type) if s not in hosts}
    statements = {(str(s), str(p), str(o)) for s, p, o in g
                  if p != RDF.type and str(p) != host and str(p) not in VOLATILE and s not in hosts}
    return nodes, statements


def compare_structure(refreshed, shipped):
    """What the refreshed graph adds to or lacks from the shipped one, as sorted lines."""
    (new_nodes, new_edges), (old_nodes, old_edges) = structure(refreshed), structure(shipped)
    return ([f"new object {n[0]}" for n in sorted(new_nodes - old_nodes)] + [f"missing object {n[0]}" for n in sorted(old_nodes - new_nodes)]
            + [f"new statement {' '.join(e)}" for e in sorted(new_edges - old_edges)] + [f"missing statement {' '.join(e)}" for e in sorted(old_edges - new_edges)])


def compare():
    """Fails when the refreshed graph's objects or edges differ from what the release ships."""
    if not all(os.path.exists(os.path.join(REFRESHED, n)) for n in GRAPH_FILES):
        raise SystemExit(f"no refreshed graph in {REFRESHED}: run collect and build")
    differences = compare_structure(read_graph(REFRESHED), read_graph(GRAPH))
    for line in differences[:50]:
        print(f"FAIL {line}")
    print(f"{len(differences)} structural difference(s) between {os.path.relpath(REFRESHED, ROOT)} and graph/")
    if differences:
        raise SystemExit(1)


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
    if isinstance(value, str):
        return str(value)  # a language-tagged label comes back from rdflib as a Literal
    return value


# Values of a code list the node carries as a property holding the value's name (a Table's layer: 'gold'; a check's
# result: 'pass'), as the graph held them before the module's terms, not as an edge to the code list.
CODED = (TG + "layer", TG + "result")


def graph_rows(g):
    """Neo4j rows from the Turtle: a node per typed technical-graph IRI, labelled Tech and its class, of the module
    (tg:) or of the decision trail (tv:), with its literals and CODED values as properties; an edge per other IRI-valued
    statement, to a Tech node or to an ontology resource."""
    from rdflib import RDF, Literal, URIRef
    nodes, edges = {}, []
    for s in sorted(set(g.subjects(RDF.type, None)), key=str):
        if not str(s).startswith(TECH):
            continue
        classes = sorted(local_name(c) for c in g.objects(s, RDF.type) if str(c).startswith((TG, VOCAB)))
        props = {"uri": str(s)}
        for p, o in g.predicate_objects(s):
            if isinstance(o, Literal):
                props[local_name(p)] = neo4j_value(o.toPython())
            elif str(p) in CODED:
                props[local_name(p)] = local_name(o)
        props["types"] = sorted(str(c) for c in g.objects(s, RDF.type))
        nodes[str(s)] = {"labels": ["Tech"] + classes, "props": props}
    for s, p, o in sorted(g, key=lambda t: tuple(map(str, t))):
        if str(s) in nodes and isinstance(o, URIRef) and p != RDF.type and str(p) not in CODED:
            edges.append({"s": str(s), "t": edge_type(p), "o": str(o), "ontology": not str(o).startswith(TECH)})
    return list(nodes.values()), edges


def apply_store_overrides():
    """EPM_STORES_JSON names other stores for a test run or another environment (as in projection/sync_stores.py): each
    of driver and aura may give {"bolt": ..., "env": [...]}, and jena {"query": ...}."""
    global JENA_QUERY
    raw = os.environ.get("EPM_STORES_JSON")
    if not raw:
        return
    over = json.loads(raw)
    for store in list(STORES):
        if store in over:
            STORES[store] = (over[store].get("bolt", STORES[store][0]), tuple(over[store].get("env", STORES[store][1])))
    JENA_QUERY = over.get("jena", {}).get("query", JENA_QUERY)


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


def graph_folder():
    """The refreshed graph when a build wrote one, otherwise what the release ships."""
    return REFRESHED if all(os.path.exists(os.path.join(REFRESHED, n)) for n in GRAPH_FILES) else GRAPH


def read_graph(folder=None):
    from rdflib import Graph
    g = Graph()
    for name in GRAPH_FILES:
        g.parse(os.path.join(folder or graph_folder(), name), format="turtle")
    return g


def sparql_select(query):
    """Rows of a SELECT on Jena, each {variable: value}."""
    request = urllib.request.Request(JENA_QUERY + "?" + urllib.parse.urlencode({"query": query}),
                                     headers={"Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return [{k: v["value"] for k, v in row.items()} for row in json.load(response)["results"]["bindings"]]


def newest_releases(catalog=os.path.join(REPO, "business_architecture", "ontology", "releases", "catalog.ttl")):
    """Each module's newest release IRI from the catalog: the graphs a current Jena holds its content under."""
    from rdflib import Graph, URIRef
    newest = {}
    for iri in Graph().parse(catalog).objects(None, URIRef("http://www.w3.org/ns/dcat#dataset")):
        module, version = str(iri).rsplit("/", 2)[-2:]
        key = tuple(int(p) for p in version.split("."))
        if module not in newest or key > newest[module][0]:
            newest[module] = (key, str(iri))
    return sorted(iri for _, iri in newest.values())


def ontology_targets(g):
    from rdflib import URIRef
    return sorted({str(o) for o in g.objects() if isinstance(o, URIRef) and str(o).startswith(ONTOLOGY)})


def jena_found_query(targets, releases):
    """The targets some current release's graph, content or shapes or catalog, says something about."""
    graphs = " ".join(f"<{iri}>" for r in releases for iri in (r, f"{r}/shapes", f"{r}/catalog"))
    return (f"SELECT DISTINCT ?o WHERE {{ VALUES ?o {{ {' '.join(f'<{o}>' for o in targets)} }} VALUES ?g {{ {graphs} }} "
            "GRAPH ?g { ?o ?x ?y } }")


def load_jena(folder):
    """Each graph file as its own named graph in Jena, replaced whole, once every ontology target is found in a current
    release's graph; a target that is not fails, as it does in Neo4j, and leaves Jena as it was. The release's proof ran
    before these graphs arrive and never covers them."""
    targets = ontology_targets(read_graph(folder))
    found = {r["o"] for r in sparql_select(jena_found_query(targets, newest_releases()))}
    missing = sorted(set(targets) - found)
    if missing:
        raise SystemExit(f"jena: {len(missing)} edge target(s) in no current release graph, e.g. {missing[:5]}; nothing was changed")
    data = JENA_QUERY.rsplit("/", 1)[0] + "/data"
    counts = {}
    for name, iri in JENA_GRAPHS.items():
        with open(os.path.join(folder, name), "rb") as f:
            body = f.read()
        request = urllib.request.Request(data + "?" + urllib.parse.urlencode({"graph": iri}), data=body, method="PUT",
                                         headers={"Content-Type": "text/turtle"})
        urllib.request.urlopen(request, timeout=120).close()
        counts[name] = int(sparql_select(f"SELECT (COUNT(*) AS ?n) WHERE {{ GRAPH <{iri}> {{ ?s ?p ?o }} }}")[0]["n"])
    print(f"jena: {', '.join(f'{iri} {counts[n]} triples' for n, iri in JENA_GRAPHS.items())}; every ontology target found")
    return {"store": "jena", "graphs": counts}


def load(stores=(*STORES, "jena")):
    folder = graph_folder()
    print(f"loading from {os.path.relpath(folder, ROOT)}")
    nodes, edges = graph_rows(read_graph(folder))
    return [load_jena(folder) if s == "jena" else load_store(s, nodes, edges) for s in stores]


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
    ap.add_argument("step", choices=("collect", "build", "compare", "lineage", "load", "sync", "walk"))
    ap.add_argument("--store", action="append", choices=(*STORES, "jena"), help="load: these stores only (default: all)")
    ap.add_argument("--lineage-wait", type=int, default=0, help="collect: seconds to wait for Unity Catalog's lineage to arrive")
    ap.add_argument("--to-repo", action="store_true", help="build: write graph/*.ttl, what the release ships, not out/tech/graph/")
    ap.add_argument("--manifest", default=MANIFEST, help="collect: the replica manifest the Databricks replica came from")
    args = ap.parse_args()
    if args.step == "collect":
        collect(args.manifest, args.lineage_wait)
    elif args.step == "build":
        build(args.to_repo)
    elif args.step == "load":
        load(tuple(args.store or (*STORES, "jena")))
    else:
        {"compare": compare, "lineage": lineage, "sync": sync, "walk": walk}[args.step]()
