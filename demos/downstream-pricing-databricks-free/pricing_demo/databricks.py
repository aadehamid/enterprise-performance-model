"""Run the Databricks side: the catalog and schemas, the upload to a volume, the SQL layers, the metric views.

    uv run python -m pricing_demo.databricks setup     # catalog, schemas, volume
    uv run python -m pricing_demo.databricks upload    # out/replica/*.parquet to the volume
    uv run python -m pricing_demo.databricks build     # sql/02 to sql/07: replica, silver, gold, metric views, definitions, tech_graph tables
    uv run python -m pricing_demo.databricks counts    # row counts of every table and view
    uv run python -m pricing_demo.databricks purge     # list what a purge drops; --yes drops it

The catalog is idp_sbx when the workspace lets you create it, otherwise DEMO_CATALOG (Free Edition: workspace), and
every schema except the replica schemas keeps the name it has in idp_sbx, so the objects read like the shared ones;
the replica schemas follow the source databases' names since 2026-10-28 (README.md, "The source systems"). One rule picks the catalog
for every step: idp_sbx only if it holds this demo's landing schema, which setup creates (Kimi round 1, finding 11).
Upload refuses an incomplete replica, and build checks each replica table against the replica's manifest (finding 5).
Secrets stay in variables.
"""
import argparse
import glob
import io
import os
import re

from . import replicate
from .config import OUT, SQL, SYSTEMS, databricks_env

SCHEMAS = (("replica_landing",) + tuple(f"replica_{s}" for s in SYSTEMS)
           + ("silver_udm_core", "silver_mdm_core", "gold_commercial_core", "semantic_sem_commercial",
              "ontology_definitions", "tech_graph"))
# What a complete build holds outside the replica layer: every silver and gold table, metric view and definitions view.
# The tech_graph tables are not here: the build creates them empty, and tech_graph.py's sync fills them.
BUILT = {
    "silver_mdm_core": {"mpr_price_master_dim", "mips_price_batch_dim", "mips_price_sheet_dim", "mips_price_group_dim",
                        "mips_price_assessment_group_dim", "refinery_dim", "market_event_dim", "eia_weekly_series_dim",
                        "decision_dim", "external_citation_dim"},
    "silver_udm_core": {"mpr_price_detail_fact", "mips_price_assessment_fact", "refinery_production_daily_fact",
                        "refinery_plan_target_fact", "ctrm_deal_fact", "refinery_unit_daily_fact", "freight_rate_fact",
                        "eia_weekly_fact", "refinery_plan_version_fact", "decision_evidence_fact",
                        "external_event_fact", "forward_scan_fact"},
    "gold_commercial_core": {"mpr_mips_crack_spread_price_fact", "mips_mpr_executive_summary_fact", "refinery_operations_daily_fact",
                             "refinery_unit_operations_daily_fact", "refinery_plan_backcast_fact", "decision_evidence_detail_fact"},
    "semantic_sem_commercial": {"mpr_mips_crack_spread_price_fact_metrics_vw", "mips_mpr_executive_summary_fact_vw",
                                "mips_mpr_benchmark_prices_fact_vw", "refinery_operations_metrics_vw",
                                "pricing_market_margin_metrics_vw", "refinery_unit_operations_metrics_vw"},
    "ontology_definitions": {"measure_definitions_vw", "crack_spread_definitions_vw", "executive_summary_definitions_vw",
                             "pricing_market_margin_definitions_vw", "refinery_operations_definitions_vw"},
}
VOLUME = "replica_landing.raw"
DEMO_COMMENT = "Synthetic sandbox mirror for the pricing demo"


def connect():
    from databricks import sql as dbsql
    e = databricks_env()
    return dbsql.connect(server_hostname=e["DATABRICKS_HOST"].replace("https://", ""), http_path=e["DATABRICKS_HTTP_PATH"],
                         access_token=e["DATABRICKS_TOKEN"]), e


def run(cur, statement):
    cur.execute(statement)
    try:
        return cur.fetchall()
    except Exception:
        return []


def catalog(cur, e):
    try:
        run(cur, f"CREATE CATALOG IF NOT EXISTS idp_sbx COMMENT '{DEMO_COMMENT}'")
        return "idp_sbx"
    except Exception as err:
        print(f"idp_sbx not created ({type(err).__name__}); using {e['DEMO_CATALOG']}")
        return e["DEMO_CATALOG"]


def setup():
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = catalog(cur, e)
        if cat == "idp_sbx":
            try:
                run(cur, "CREATE SCHEMA IF NOT EXISTS idp_sbx.replica_landing")
            except Exception as err:  # a catalog the token cannot write to is not usable
                print(f"idp_sbx not usable ({type(err).__name__}); using {e['DEMO_CATALOG']}")
                cat = e["DEMO_CATALOG"]
        for s in SCHEMAS:
            run(cur, f"CREATE SCHEMA IF NOT EXISTS {cat}.{s}")
        run(cur, f"CREATE VOLUME IF NOT EXISTS {cat}.{VOLUME}")
        print(f"catalog {cat}: {len(SCHEMAS)} schemas, volume {cat}.{VOLUME}")
        return cat


def current_catalog(cur, e):
    """idp_sbx only when it holds this demo's landing schema, which setup creates there; otherwise DEMO_CATALOG.
    A visible idp_sbx that setup could not use does not count."""
    cats = {r[0] for r in run(cur, "SHOW CATALOGS")}
    if "idp_sbx" in cats and "replica_landing" in {r[0] for r in run(cur, "SHOW SCHEMAS IN idp_sbx")}:
        return "idp_sbx"
    return e["DEMO_CATALOG"]


def upload():
    from databricks.sdk import WorkspaceClient
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
    manifest = replicate.check_replica()  # refuses an empty or partial replica before anything is sent
    w = WorkspaceClient(host=e["DATABRICKS_HOST"], token=e["DATABRICKS_TOKEN"])
    files = [os.path.join(OUT, "replica", f"{key}.parquet") for key in sorted(manifest)]
    for path in files:
        system, name = path.split(os.sep)[-2:]
        target = f"/Volumes/{cat}/replica_landing/raw/{system}/{name}"
        with open(path, "rb") as f:
            w.files.upload(target, io.BytesIO(f.read()), overwrite=True)
        print(f"uploaded {system}/{name}")
    return len(files)


def statements(path, cat, triples):
    """The file's statements for catalog `cat`; `triples` names the ontology's triple table (sql/06_definitions.sql)."""
    text = open(path).read().replace("${catalog}", cat).replace("${epm_triples}", triples)
    text = re.sub(r"^--.*$", "", text, flags=re.M)
    return [s.strip() for s in re.split(r";\s*\n", text) if s.strip()]


def build(files=None):
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        for path in files or sorted(glob.glob(os.path.join(SQL, "0[2-9]_*.sql"))):
            for st in statements(path, cat, e["EPM_TRIPLES"]):
                run(cur, st)
            print(f"ran {os.path.basename(path)}")
            if os.path.basename(path).startswith("02_"):
                check_replica_tables(cur, cat)
        check_built(cur, cat)


def check_replica_tables(cur, cat, manifest=None, taken=None):
    """Each replica table holds exactly the rows of the local replica's manifest, and every row comes from that same
    run: its _replicated_at equals the manifest's. A volume left holding an earlier run's files has the same counts
    but another _replicated_at, so a skipped upload is caught (finding 5; Pi round 2, finding 2)."""
    manifest = manifest or replicate.check_replica()
    taken = taken or replicate.replicated_at()
    for key, rows in sorted(manifest.items()):
        system, table = key.split("/")
        n, first, last = run(cur, f"SELECT COUNT(*), MIN(_replicated_at), MAX(_replicated_at) FROM {cat}.replica_{system}.{table}")[0]
        if n != rows:
            raise SystemExit(f"{cat}.replica_{system}.{table} has {n} rows; the replica manifest says {rows}")
        stamps = {str(v).replace(" ", "T") for v in (first, last)}
        if stamps != {taken}:
            raise SystemExit(f"{cat}.replica_{system}.{table} holds rows replicated at {sorted(stamps)}, not this run's {taken}: "
                             "upload the current replica")


def check_built(cur, cat):
    """Every silver and gold table, metric view and definitions view of a complete build exists and holds rows
    (finding 5; Pi round 2)."""
    for schema, names in BUILT.items():
        found = {r[1] for r in run(cur, f"SHOW TABLES IN {cat}.{schema}")}
        if names - found:
            raise SystemExit(f"{cat}.{schema} lacks {sorted(names - found)}")
        for name in sorted(names):
            n = count(cur, f"{cat}.{schema}.{name}", metric_view=schema == "semantic_sem_commercial")
            if not n:
                raise SystemExit(f"{cat}.{schema}.{name} is empty")


def counts():
    conn, e = connect()
    found = {}
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        for s in SCHEMAS[1:]:
            for row in run(cur, f"SHOW TABLES IN {cat}.{s}"):
                name = row[1]
                n = count(cur, f"{cat}.{s}.{name}", metric_view=s == "semantic_sem_commercial")
                found[f"{s}.{name}"] = n
                print(f"{cat}.{s}.{name}: {n}")
    return found


CREATED = re.compile(r"CREATE OR REPLACE (TABLE|VIEW) \$\{catalog\}\.(\w+)\.(\w+)")


def created_objects():
    """Every table and view the build's SQL creates, as (kind, schema, name): the purge drops exactly these."""
    found = []
    for path in sorted(glob.glob(os.path.join(SQL, "0[2-9]_*.sql"))):
        found += CREATED.findall(open(path).read())
    return found


def purge_statements(cat):
    """The demo's objects, dropped one by one, then its volume and schemas without CASCADE: a schema that still
    holds anything the demo did not create is not dropped, and the statement fails instead."""
    drops = [f"DROP {kind} IF EXISTS {cat}.{schema}.{name}" for kind, schema, name in reversed(created_objects())]
    drops.append(f"DROP VOLUME IF EXISTS {cat}.{VOLUME}")
    drops += [f"DROP SCHEMA IF EXISTS {cat}.{s}" for s in reversed(SCHEMAS)]
    return drops


def demo_owns(cur, cat):
    """True for idp_sbx only when it carries the comment setup gives it: a catalog of that name made by anyone else
    is not the demo's."""
    if cat != "idp_sbx":
        return False
    rows = run(cur, "DESCRIBE CATALOG idp_sbx")
    return any(str(r[0]).strip().lower() == "comment" and str(r[1]).strip() == DEMO_COMMENT for r in rows)


def purge(execute=False, catalog=None, connection=None):
    """Prints the drop statements; runs them only with --yes. Stops at the first statement that fails. A catalog the
    demo does not own (DEMO_CATALOG, or an idp_sbx without setup's comment) is purged only when --catalog names it."""
    conn, e = connection or connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        print(f"catalog {cat}")
        if execute and not demo_owns(cur, cat) and catalog != cat:
            raise SystemExit(f"{cat} is not a catalog the demo created; to purge the demo's objects in it, "
                             f"add --catalog {cat}")
        for st in purge_statements(cat):
            print(st)
            if execute:
                run(cur, st)
    print("purged" if execute else "dry run: nothing dropped; add --yes to drop")


def count(cur, name, metric_view):
    """Rows of a table, or of a metric view through its Record_Count measure, which every view defines (finding 4)."""
    query = f"SELECT MEASURE(Record_Count) FROM {name}" if metric_view else f"SELECT COUNT(*) FROM {name}"
    return run(cur, query)[0][0]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("setup", "upload", "build", "counts", "purge"))
    ap.add_argument("--yes", action="store_true", help="purge: drop the objects instead of listing them")
    ap.add_argument("--catalog", help="purge: confirm a catalog the demo did not create, by name")
    args = ap.parse_args()
    if args.step == "purge":
        purge(execute=args.yes, catalog=args.catalog)
    else:
        {"setup": setup, "upload": upload, "build": build, "counts": counts}[args.step]()
