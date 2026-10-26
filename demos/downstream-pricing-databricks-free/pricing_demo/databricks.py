"""Run the Databricks side: the catalog and schemas, the upload to a volume, the SQL layers, the metric views.

    uv run python -m pricing_demo.databricks setup     # catalog, schemas, volume
    uv run python -m pricing_demo.databricks upload    # out/replica/*.parquet to the volume
    uv run python -m pricing_demo.databricks build     # sql/02 to sql/05: replica, silver, gold, metric views
    uv run python -m pricing_demo.databricks counts    # row counts of every table and view

The catalog is idp_sbx when the workspace lets you create it, otherwise DEMO_CATALOG (Free Edition: workspace), and
every schema keeps the name it has in idp_sbx, so the objects read like the shared ones. Secrets stay in variables.
"""
import argparse
import glob
import io
import os
import re

from databricks import sql as dbsql

from .config import OUT, SQL, databricks_env

SCHEMAS = ("replica_landing", "replica_mips", "replica_mpr", "replica_kittyhawk", "replica_ctrm", "replica_planning",
           "replica_prodacct", "silver_udm_core", "silver_mdm_core", "gold_commercial_core", "semantic_sem_commercial")
VOLUME = "replica_landing.raw"


def connect():
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
        run(cur, "CREATE CATALOG IF NOT EXISTS idp_sbx COMMENT 'Synthetic sandbox mirror for the pricing demo'")
        return "idp_sbx"
    except Exception as err:
        print(f"idp_sbx not created ({type(err).__name__}); using {e['DEMO_CATALOG']}")
        return e["DEMO_CATALOG"]


def setup():
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = catalog(cur, e)
        for s in SCHEMAS:
            run(cur, f"CREATE SCHEMA IF NOT EXISTS {cat}.{s}")
        run(cur, f"CREATE VOLUME IF NOT EXISTS {cat}.{VOLUME}")
        print(f"catalog {cat}: {len(SCHEMAS)} schemas, volume {cat}.{VOLUME}")
        return cat


def current_catalog(cur, e):
    cats = {r[0] for r in run(cur, "SHOW CATALOGS")}
    return "idp_sbx" if "idp_sbx" in cats else e["DEMO_CATALOG"]


def upload():
    from databricks.sdk import WorkspaceClient
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
    w = WorkspaceClient(host=e["DATABRICKS_HOST"], token=e["DATABRICKS_TOKEN"])
    files = sorted(glob.glob(os.path.join(OUT, "replica", "*", "*.parquet")))
    for path in files:
        system, name = path.split(os.sep)[-2:]
        target = f"/Volumes/{cat}/replica_landing/raw/{system}/{name}"
        with open(path, "rb") as f:
            w.files.upload(target, io.BytesIO(f.read()), overwrite=True)
        print(f"uploaded {system}/{name}")
    return len(files)


def statements(path, cat):
    text = open(path).read().replace("${catalog}", cat)
    text = re.sub(r"^--.*$", "", text, flags=re.M)
    return [s.strip() for s in re.split(r";\s*\n", text) if s.strip()]


def build(files=None):
    conn, e = connect()
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        for path in files or sorted(glob.glob(os.path.join(SQL, "0[2-9]_*.sql"))):
            for st in statements(path, cat):
                run(cur, st)
            print(f"ran {os.path.basename(path)}")


def counts():
    conn, e = connect()
    found = {}
    with conn, conn.cursor() as cur:
        cat = current_catalog(cur, e)
        for s in SCHEMAS[1:]:
            for row in run(cur, f"SHOW TABLES IN {cat}.{s}"):
                name = row[1]
                try:
                    n = run(cur, f"SELECT COUNT(*) FROM {cat}.{s}.{name}")[0][0]
                except Exception:
                    n = run(cur, f"SELECT MEASURE(Record_Count) FROM {cat}.{s}.{name}")[0][0]
                found[f"{s}.{name}"] = n
                print(f"{cat}.{s}.{name}: {n}")
    return found


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("setup", "upload", "build", "counts"))
    {"setup": setup, "upload": upload, "build": build, "counts": counts}[ap.parse_args().step]()
