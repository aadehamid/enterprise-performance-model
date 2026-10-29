"""Paths, the demo window, the seed and the environment. Secrets are read, never printed."""
import datetime as dt
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
SQL = os.path.join(ROOT, "sql")
OUT = os.path.join(ROOT, "out")

# The demo window: three years of trading days, ending on the scenario's last EIA spot date (the decision owner,
# 2026-10-28: "extedn it and use the current EIA key"). Until 2026-10-28 it began on 2026-04-01.
WINDOW_START = dt.date(2023, 10, 21)
WINDOW_END = dt.date(2026, 10, 20)
# EIA's weekly data by PADD reaches six years back, so a five-year seasonal average exists for every week in the window.
WEEKLY_START = dt.date(2020, 10, 16)
SEED = 20261025

# The names the demo uses for the source systems: a public product name where one exists (RightAngle, Aspen PIMS),
# otherwise a generic one (the decision owner, 2026-10-28). The real names stay in the ontology; README.md maps
# each. Every module takes the systems from here.
SYSTEMS = {
    "price_assessment": "Market Price Assessment System",
    "price_reference": "Price Reference Master",
    "reference_data_hub": "Commercial Reference Data Hub",
    "rightangle": "RightAngle, the Commodity Trading and Risk Management (CTRM) system",
    "aspen_pims": "Aspen PIMS, the refinery planning model",
    "production_accounting": "Refinery Production Accounting",
    # Public data, not an MPC system: EIA's Weekly Petroleum Status Report series by PADD, landed as its own source
    # database so the replication and the layers treat it like any other source (2026-10-28).
    "eia_weekly": "EIA Weekly Petroleum Status Report, by PADD (public data)",
}

# Databases the loader fills but the replication never reads: the decision dossiers, the hidden truth the tests check
# the agents' answers against (README.md, "Use cases"; DATA.md, "decision_truth"). Nothing downstream may see them.
HIDDEN_SYSTEMS = {
    "decision_truth": "The decision dossiers: the whole of each synthetic decision, read only by the tests",
}

# Every price and operations row carries one of these: Claude's design under EPM-DEC-001-0028 (EPM-DEC-001-0102, item 2).
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
    """Host, token, HTTP path and catalog, from the environment, .env, or ~/.config/databricks/epm.env, and EPM_TRIPLES,
    the ontology's triple table, which the projection driver writes to epm.env's catalog and schema."""
    values = {k: env(k) for k in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_HTTP_PATH", "DEMO_CATALOG", "EPM_TRIPLES")}
    projection = {"DATABRICKS_CATALOG": "workspace", "DATABRICKS_SCHEMA": "epm_ontology"}
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
                if k in projection and v:
                    projection[k] = v
    missing = [k for k in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_HTTP_PATH") if not values[k]]
    if missing:
        raise SystemExit("Databricks settings missing: " + ", ".join(missing))
    values["DEMO_CATALOG"] = values["DEMO_CATALOG"] or "workspace"
    values["EPM_TRIPLES"] = values["EPM_TRIPLES"] or "{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.epm_triples".format(**projection)
    values["DATABRICKS_HOST"] = values["DATABRICKS_HOST"].rstrip("/")
    if not values["DATABRICKS_HOST"].startswith("https://"):
        values["DATABRICKS_HOST"] = "https://" + values["DATABRICKS_HOST"]
    return values


def source_dsn():
    return env("SOURCE_PG_DSN", "postgresql://demo:demo@localhost:55432")
