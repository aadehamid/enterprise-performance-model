# Mac + uv - optional local path

This learner pack does **not** ship working `.py` files. You write
SQL in the warehouse editor (default), or you write your own connector
scripts. Peek at the complete pack if stuck:

`../o2c-unbilled-databricks-free/scripts/`

Do **not** copy those files into this folder until you have tried the
exercise. They are answers.

Not demo 1. Not MetricFlow. Not Azure.

---

## 1. Create the venv and install

From this directory (`o2c-unbilled-databricks-free-learn/`), on a Mac
with [uv](https://docs.astral.sh/uv/) (Homebrew: `brew install uv`):

```bash
uv venv --python 3.12
source .venv/bin/activate
```

Needs Python >= 3.12. `uv` will fetch 3.12 if your Mac default is older.

Install the same libraries the complete pack uses (you still write the
scripts):

```bash
uv pip install "databricks-sdk==0.128.0" "databricks-sql-connector==4.4.0" "psycopg[binary]==3.3.4"
```

Or look at the complete pack's `pyproject.toml` and `uv sync` **there**
if you only want to run the answered scripts after you have tried.

---

## 2. Copy env and fill in values

```bash
cp scripts/.env.example .env
```

Edit `.env` (never commit it):

| Variable | What to put |
| --- | --- |
| `DATABRICKS_HOST` | Your Free workspace URL, `https://….cloud.databricks.com` (not Azure). Do not commit the real host. |
| `DATABRICKS_WAREHOUSE_ID` | The id in **SQL Warehouses → Serverless Starter Warehouse → Connection details**. HTTP path looks like `/sql/1.0/warehouses/<this>` |
| `DATABRICKS_CATALOG` | `workspace` unless **Catalog** in the sidebar shows a different name |
| `DATABRICKS_SCHEMA` | `o2c_unbilled` (or `default` if `CREATE SCHEMA` is denied) |
| `DATABRICKS_TOKEN` | PAT or a short-lived OAuth access token. Never commit the real value |
| `LAKEBASE_HOST` | Compute endpoint from **Lakebase App → dataexpert-day1 → Connect**. Empty in the example. Do not invent or commit it. |
| `LAKEBASE_DATABASE` | `databricks_postgres` (locked) |
| `LAKEBASE_USER` | Postgres role from that Connect dialog |
| `LAKEBASE_PASSWORD` | Role password (or OAuth token used as password). Never commit it. |
| `LAKEBASE_SCHEMA` | `o2c_unbilled` only. Refuse any other schema. |

There is no workspace URL, token, or password in this pack.

---

## 3. Get a token (PAT first; OAuth if Free will not mint one)

**PAT - try this first.** Username → **Settings** → **Developer** →
**Access tokens** → **Manage** → **Generate new token**. Copy once
into `.env` as `DATABRICKS_TOKEN`.

If **Manage** is missing or **Generate** fails on Free, use the OAuth
CLI fallback (do not invent a UI workaround):

```bash
# CLI if needed: brew install databricks
databricks auth login --host "$DATABRICKS_HOST"
databricks auth token --host "$DATABRICKS_HOST"
```

Paste the `access_token` into `.env` as `DATABRICKS_TOKEN`. OAuth
access tokens last about one hour.

Official pages:

- [Authenticate with Databricks personal access tokens (legacy)](https://docs.databricks.com/aws/en/dev-tools/auth/pat)
- [Authentication for the Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/authentication)
- [Authorize user access to Databricks with OAuth](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m)

---

## 4. What you write (or peek)

Suggested script names if you roll your own - same order as `LEARN.md`:

```bash
uv run python scripts/01_connect.py          # prove warehouse
uv run python scripts/00_lakebase_ods.py     # Act 0, optional
uv run python scripts/00b_land_replica.py    # Lakebase → raw_*
# or skip Act 0 and load data/*.csv into raw_*
uv run python scripts/03_facts.py            # fct_unbilled
uv run python scripts/04_metric_view.py      # version 0.1
uv run python scripts/05_query.py            # Act 1 / 2 / 3
uv run python scripts/06_store.py            # dim_kpi_metadata + gold FROM MEASURE()
uv run python scripts/08_complex_metric.py   # KPI 2 contract_vs_list_usd
uv run python scripts/09_temp_adjusted.py    # KPI 3 temp_adjusted_delivered_usd
uv run python scripts/07_genie.py            # Genie after 08/09; all three views
# after Genie - hunt (peek complete pack; do not copy first)
# ../o2c-unbilled-databricks-free/scripts/10_cv_map.py
# ../o2c-unbilled-databricks-free/scripts/12_cv_hunt.py
# ../o2c-unbilled-databricks-free/scripts/11_cv_search_genie.py
```

Those files are **not** in this folder. Write them, or open the
complete pack's copies when stuck:

`../o2c-unbilled-databricks-free/scripts/`

Hunt is after Genie. You write the `DESCRIBE` / `SELECT` / map yourself. Those three complete-pack scripts are answers. Peek after you have tried. Do not copy them into this folder first.

Act 0 constraints still apply: schema `o2c_unbilled` only on existing
project `dataexpert-day1`. Do not create a second Lakebase project.
Do not write into other day1 schemas.

Lakebase connection details come from the official Connect dialog
(port **5432**, `sslmode=require`, database `databricks_postgres`).
Do not invent a workspace URL or a Lakebase host.
