"""Paths, the demo window, the seed and the environment. Secrets are read, never printed."""
import datetime as dt
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
SQL = os.path.join(ROOT, "sql")
OUT = os.path.join(ROOT, "out")

# The demo window: about six months of trading days, ending on the last EIA spot date pulled.
WINDOW_START = dt.date(2026, 4, 1)
WINDOW_END = dt.date(2026, 10, 20)
SEED = 20261025

# The generic names the demo uses for the source systems (the decision owner: "they work").
# The real names stay in the ontology; README.md maps each.
SYSTEMS = {
    "mips": "Market Price Assessment System",
    "mpr": "Price Reference Master",
    "kittyhawk": "Commercial Reference Data Hub",
    "ctrm": "Commodity Trading and Risk Management (CTRM) System",
    "planning": "Refinery Planning Model",
    "prodacct": "Refinery Production Accounting",
}

# Every price row carries one of these (the decision owner: every row labelled).
PROVENANCE = ("real", "spot-anchored", "synthesized")


def env(name, default=None):
    value = os.environ.get(name)
    if value:
        return value
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path):
            if line.strip().startswith(name + "="):
                found = line.split("=", 1)[1].strip().strip('"').strip("'")
                if found:
                    return found
    return default


def databricks_env():
    """Host, token, HTTP path and catalog, from the environment, .env, or ~/.config/databricks/epm.env."""
    values = {k: env(k) for k in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_HTTP_PATH", "DEMO_CATALOG")}
    path = os.path.expanduser("~/.config/databricks/epm.env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k in values and not values[k]:
                    values[k] = v
                if k == "DATABRICKS_CATALOG" and not values["DEMO_CATALOG"]:
                    values["DEMO_CATALOG"] = v
    missing = [k for k in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_HTTP_PATH") if not values[k]]
    if missing:
        raise SystemExit("Databricks settings missing: " + ", ".join(missing))
    values["DEMO_CATALOG"] = values["DEMO_CATALOG"] or "workspace"
    values["DATABRICKS_HOST"] = values["DATABRICKS_HOST"].rstrip("/")
    if not values["DATABRICKS_HOST"].startswith("https://"):
        values["DATABRICKS_HOST"] = "https://" + values["DATABRICKS_HOST"]
    return values


def source_dsn():
    return env("SOURCE_PG_DSN", "postgresql://demo:demo@localhost:55432")
