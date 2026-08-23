# O2C Unbilled USD - Databricks Free consumption semantic layer demo (Track B)

A **scaffold** you run in a Databricks **Free Edition** workspace. Same
teaching story as Track A (two "Unbilled USD" workbooks that fight at
payer vs sold-to vs site grain), but **Databricks Free is both the
warehouse and the consumption semantic layer**. The compiler is Unity
Catalog **Metric Views** (`CREATE VIEW … WITH METRICS` / `MEASURE()`),
not MetricFlow.

Live compile **succeeded 2026-08-14** on Databricks Free Edition:
`CREATE VIEW … WITH METRICS` **version 0.1** + `MEASURE()` + `SELECT *`
refused `METRIC_VIEW_MISSING_MEASURE_FUNCTION`. Official Free pages
still do not name Metric Views; the workspace run is the proof.
Do **not** put a workspace URL in this pack.

---

## What this pack is

- Demo **2** / Track B. Oil-and-gas O2C. Unbilled is a **state** of an
  obligation (delivered BOL not yet invoiced), not a KPI kind.
- `customer_grain ∈ {payer, sold-to, site}`. You choose the group-by.
  The formula stays still.
- Consumption semantic layer on Free Edition: land CSVs → build
  `fct_unbilled` → create the Metric View → query with `MEASURE()` →
  publish Store metadata + gold snapshots FROM `MEASURE()`.
- Two ways to run it: **from your Mac with `uv`** (SQL connector
  scripts in `scripts/`) or in the **SQL editor**. Sign in at
  [login.databricks.com](https://login.databricks.com) and attach the
  **2XS** warehouse either way. Not Azure. Not demo 1. Not MetricFlow.

## What this pack is not

| Not this | That lives… |
| --- | --- |
| Track A (MetricFlow + DuckDB + dbt) | `demos/o2c-unbilled-semantic-layer/` - **do not edit it** |
| Azure Databricks (`*.azuredatabricks.net`) | The actual project, not this pack |
| MetricFlow / `mf query` / dbt / DuckDB | Track A only |
| A second Unbilled formula in the Store | `dim_kpi_metadata` points at the Metric View; `gold_kpi_value` snapshots FROM `MEASURE()` |
| An ontology | Ontology = meaning. This YAML is a formula |
| Cube, Airflow, Postgres, Synapse, Fabric | Parked (see below) |

**C-10 one-liner:** ontology = meaning; Store catalog + this Metric View
= certified formula for **this** demo. Do not pretend the Metric View
is the ontology. Honest seats: `fct_unbilled` holds the ticket gate +
`gallons_net * contract_price` (population / compiler source). The
Metric View compiles SUM/GROUP BY (`MEASURE()`). Gold and Genie consume
`MEASURE()` and must not re-encode. RC-1 still holds for Gold/Genie
(one compile path, no second SUM).

---

## Layer story

```
ODS        Lakebase dataexpert-day1 / databricks_postgres / o2c_unbilled  (ops tables)
Bronze     workspace.o2c_unbilled.raw_*   (replica; Python pipe; no federated join)
Silver     dim_party, dim_site, dim_product, br_party_role
           + dim_kpi_metadata   - one row per KPI (status approved/drifted/proposed/archived; pointer, not the formula)
Population fct_unbilled  (ticket grain; compiler source; ticket gate + gallons_net * contract_price; NOT gold)
Compiler   Metric View workspace.o2c_unbilled.unbilled_usd  (SUM/GROUP BY via MEASURE())
Gold       gold_kpi_value  - published KPI values FROM MEASURE(), not a second SUM()
```

Two new objects: `dim_kpi_metadata` (Silver, one row per KPI,
status approved/drifted/proposed/archived) and `gold_kpi_value` (Gold, published instances per
approved KPI FROM that view's `MEASURE()`). Both live in
`sql/05_store.sql` / `scripts/06_store.py`. After a full run the
catalog has three approved rows and Gold has all three KPIs.
Unbilled gold grains are enterprise / payer / sold_to / site.
Contract-vs-list gold grains are enterprise / sold_to / product
(`MEASURE(delivered_contract_usd)` only). Temp-adjusted gold grains
are enterprise / product / site (`MEASURE(temp_adjusted_usd)` only).
`contract_vs_list_usd` and `temp_adjusted_delivered_usd` compile
from the bronze star, have no population fact, and put the multiply
in YAML. The locked diagram still shows the Unbilled path; the extra
Metric Views are the joins/filter/multiply teaching point. Genie
is the ad hoc path for all three approved KPIs (MEASURE() only;
not a second formula).

---

## Sign in (Free Edition only)

1. Open [login.databricks.com](https://login.databricks.com).
2. Use the Free Edition workspace Databricks created for you.
3. Workspace URL is usually `*.cloud.databricks.com`, **not**
   `*.azuredatabricks.net`. If you land on Azure, you are in the wrong
   product - stop and go back to Free.
4. Attach the default **Serverless Starter Warehouse** (2X-Small).
   Free allows **one** SQL warehouse, serverless only. Quota can shut
   compute for the rest of the day.

Official limits (updated 2026-07-20):
[Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).

Non-commercial. No R/Scala. No custom storage. One workspace + one
metastore.

---

## Placeholders

Every `sql/*.sql` file uses:

| Token | Default | What it is |
| --- | --- | --- |
| `{{catalog}}` | `workspace` | Workspace catalog (name under **Catalog** in the sidebar; may match the workspace name, not the literal word `workspace`) |
| `{{schema}}` | `o2c_unbilled` | Demo schema. Fall back to `default` if `CREATE SCHEMA` is denied - Free users have `USE` / `WRITE VOLUME` on `default` by default |

Find/replace those two tokens in `01`–`05` if you run the human-authored
files. `sql/99_full_load.generated.sql` already has
`workspace` / `o2c_unbilled` substituted - run that file as-is.
Do **not** commit a workspace URL or a token. There is none in this pack.

---

## Run from your Mac (uv)

This is the local path. Demo **2** / Track B. **Not demo 1. Not MetricFlow.**
You still need a Free Edition workspace and the 2XS warehouse; the
scripts talk to it over the Databricks SQL connector. No workspace URL
or token belongs in this repo - only in your local `.env` (gitignored).

**Act 0 Lakebase** uses the **existing** project `dataexpert-day1`
(database `databricks_postgres`, new schema `o2c_unbilled` only).
Do **not** create a second Lakebase project. Do **not** write into
other day1 schemas. Host / password / token stay in `.env`, never
in the repo.

### 1. Create the venv and install

From this directory (`o2c-unbilled-databricks-free/`), on a Mac with
[uv](https://docs.astral.sh/uv/) (Homebrew: `brew install uv`):

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

Or the equivalent project sync:

```bash
uv sync
```

Needs Python >= 3.12. `uv` will fetch 3.12 if your Mac default is older.

### 2. Copy env and fill in values

```bash
cp .env.example .env
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
| `LAKEBASE_SCHEMA` | `o2c_unbilled` only. Scripts refuse any other schema. |

Databricks scripts refuse to start if `DATABRICKS_TOKEN` is empty.
Lakebase scripts refuse if `LAKEBASE_PASSWORD` is empty.

### 3. Get a token (PAT first; OAuth if Free will not mint one)

**PAT - try this first.** Official workspace-user steps, last updated
2026-06-17, from
[Authenticate with Databricks personal access tokens (legacy)](https://docs.databricks.com/aws/en/dev-tools/auth/pat):

1. In the workspace, click your username → **Settings**.
2. Click **Developer**.
3. Next to **Access tokens**, click **Manage**.
4. Click **Generate new token**. Copy it once into `.env` as `DATABRICKS_TOKEN`.

Official [Databricks Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)
(updated 2026-07-20) do **not** list PAT as unsupported. Those pages
also do **not** specifically say Free can mint PATs. If **Manage** is
missing or **Generate** fails on Free, do not invent a UI workaround  - 
use the OAuth CLI fallback.

**OAuth / CLI fallback** (official; the PAT page itself prefers OAuth
for user accounts).
[Authentication for the Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/authentication)
and
[Authorize user access to Databricks with OAuth](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-u2m)
(updated 2026-07-22):

```bash
# CLI if needed: brew install databricks
databricks auth login --host "$DATABRICKS_HOST"
databricks auth token --host "$DATABRICKS_HOST"
```

Paste the `access_token` from that output into `.env` as
`DATABRICKS_TOKEN`. OAuth access tokens last about one hour; re-run
`databricks auth token` when `01_connect.py` starts failing auth.

The SQL connector also supports interactive OAuth
(`auth_type="databricks-oauth"`). These scripts require
`DATABRICKS_TOKEN` so a missing token fails closed.

### 4. Run the scripts

Prove the warehouse, then Act 0 ODS → replica → facts → metric view → queries → store → KPI 2 → KPI 3 → Genie → catalog status (13/14/15) → CV/map → hunt → vocabulary-search Genie:

```bash
uv run python scripts/01_connect.py
uv run python scripts/00_lakebase_ods.py
uv run python scripts/00b_land_replica.py
uv run python scripts/03_facts.py
uv run python scripts/04_metric_view.py
uv run python scripts/05_query.py
uv run python scripts/06_store.py
uv run python scripts/08_complex_metric.py
uv run python scripts/09_temp_adjusted.py
uv run python scripts/07_genie.py
uv run python scripts/13_status_drift.py
uv run python scripts/14_reapprove.py
uv run python scripts/15_edit_reset_prove.py
uv run python scripts/10_cv_map.py
uv run python scripts/12_cv_hunt.py
uv run python scripts/11_cv_search_genie.py
```

13 marks drifted only after a live-text mismatch. Edit the Unbilled view first; revert before 14. See WALKTHROUGH §13b.

`02_load.py` is a shortcut that lands `data/*.csv` straight into Databricks
`raw_*` and **skips Lakebase**. Use it only if you are not running Act 0.

| Script | What success looks like |
| --- | --- |
| `01_connect.py` | Prints warehouse id + `current_user()` / `current_catalog()` |
| `00_lakebase_ods.py` | `CREATE SCHEMA IF NOT EXISTS o2c_unbilled` on **dataexpert-day1** / `databricks_postgres`; ops tables **8 / 10 / 3 / 3 / 19 / 6 / 6**. Refuses if password missing. Never DROPs other schemas. |
| `00b_land_replica.py` | Reads those Lakebase tables in Python; writes `workspace.o2c_unbilled.raw_*` via the SQL connector (**no federated join**). Same raw counts. |
| `02_load.py` | Optional shortcut: CSVs → `raw_*` (skip 00/00b) |
| `03_facts.py` | Runs `sql/02_facts.sql`; `fct_unbilled` = **12** tickets, **$179,934.00** |
| `04_metric_view.py` | `CREATE VIEW … WITH METRICS` **version 0.1** as **one** statement (live-proven 2026-08-14) |
| `05_query.py` | Act 1 fights; Act 2 `MEASURE()` at payer / sold_to / site agrees; Act 3 `SELECT *` errors `METRIC_VIEW_MISSING_MEASURE_FUNCTION` |
| `06_store.py` | Unbilled row in `dim_kpi_metadata` (`approved`, pointer `unbilled_usd`); Unbilled gold FROM `MEASURE()` (11 rows); enterprise **$179,934.00** / 12. Other kpi_id gold/metadata rows are kept. After 08/09 the catalog is 3 approved rows. |
| `08_complex_metric.py` | Second KPI `contract_vs_list_usd` (not Unbilled): joins + filters + multiply. Unsliced contract **$110,064.00** / 7. `SELECT *` refused. Does not change `unbilled_usd`. |
| `09_temp_adjusted.py` | Third KPI `temp_adjusted_delivered_usd` (rack math, not Unbilled): expansion multiply. Unsliced adj ≈ **$256,066.39** / 17. `SELECT *` refused. |
| `07_genie.py` | Run **after** 08/09. Creates/updates Genie Agent **O2C certified KPIs** on all three approved Metric Views; live-asks unsliced Unbilled / contract / temp-adjusted. MEASURE() only if approved. No Export-to-metric-view. |
| `13_status_drift.py` | Hash live Metric View text vs `definition_hash`. Sets drifted only when status is already approved. Proposed and archived stay. |
| `14_reapprove.py` | Steward re-approve: refresh `definition_hash` from live view text, set status = approved. The only approve path. Genie Unbilled **$179,934.00 / 12**. |
| `15_edit_reset_prove.py` | Prove edit-resets-approval: pointer/object/definition change on an approved row → proposed. Restores the row. |
| `catalog_status.py` | Shared helper (hash, drift, re-approve, upsert). Not a run-alone step. |
| `sql/08_catalog_status.sql` | Catalog-status notes / ALTER helper. Table is kept; no CREATE OR REPLACE wipe. |
| `10_cv_map.py` | Land `cv_term` / `cv_alias` / `cv_map` / sidecar `dim_customer` + `cv_lookup`. `cv_term` now has `ontology_iri` (bind, not a replacement of `term_id`). Prove `customer` → two IDs; Apex payer MEASURE() **$115,960.80 / 8**; refuse `customer_id` and `CONS-4412` grains. Does not change `TABLES` or tickets. |
| `12_cv_hunt.py` | After 10. Open hunt sources (table → column → value → map). Lands `sap_partner` / `tas_lift` / `sf_account` / `ra_business_associate`; re-lands `dim_customer`. TABS skipped. Apex still **$115,960.80 / 8**. Hunt stubs stay off both Genies. |
| `11_cv_search_genie.py` | Second Genie Agent **O2C vocabulary search** (cv tables only; never a dollar). Live-asks *What is customer?* Expect both IDs. Does **not** update `O2C certified KPIs`. Notes: `scripts/11_cv_search_genie.md`. Problem statement: `THE-PROBLEM.md`. |

Each script prints the SQL it sends. Nothing is hidden.

Lakebase connection details come from the official Connect dialog
([Postgres clients](https://docs.databricks.com/aws/en/oltp/projects/postgres-clients),
[Connection strings](https://docs.databricks.com/aws/en/oltp/projects/connection-strings)):
port **5432**, `sslmode=require`, database `databricks_postgres`.
Do not invent a workspace URL or a Lakebase host.

---

## Run order (SQL editor, warehouse attached)

This is the **SQL editor** path (no local Python). No Azure CLI.
Not demo 1. Not MetricFlow. If you already ran the `uv` scripts above,
you do not need this.

**Preferred in the warehouse UI:** run `sql/99_full_load.generated.sql` in
chunks (raw VALUES → facts → Metric View → Act 1 / Act 2), then
`sql/05_store.sql` for Store metadata + gold. `99` embeds
the seven CSVs as `CREATE OR REPLACE TABLE … AS SELECT * FROM VALUES …`
so you do **not** need UI CSV upload (Free outbound internet is
restricted; UI upload is flaky). Placeholders are already
`workspace` / `o2c_unbilled`.

Monaco auto-indent can mangle the Metric View YAML. Paste that
statement as one block, or set the editor value, then run. The pack
dialect is **version 0.1** in `sql/03_metric_view.sql`,
`scripts/04_metric_view.py`, and `99` (fields + measures only).

### Alternate: upload CSVs + 01→04

If you want the volume path instead of `99`:

1. Open `sql/01_land.sql`. Run **Part A** only
   (`CREATE SCHEMA` / `CREATE VOLUME`). Find/replace placeholders first.
2. Catalog Explorer → `{{catalog}}` → `{{schema}}` → Volumes → `landing`
   → Upload the seven files from `data/`. **Do not wget.**
3. Then 01 Part B → 02 → 03 → 04 → 05.

| Step | File | What success looks like |
| --- | --- | --- |
| Full load (preferred) | `sql/99_full_load.generated.sql` | raw 8 / 10 / 3 / 3 / 19 / 6 / 6; `fct_unbilled` = **12** / **$179,934.00**; Metric View version 0.1; Act 1 fights; Act 2 `MEASURE()` agrees |
| Land (alternate) | `sql/01_land.sql` Part B | 8 / 10 / 3 / 3 / 19 / 6 / 6 row counts |
| Facts | `sql/02_facts.sql` | `fct_unbilled` = **12** tickets, **$179,934.00** |
| Metric View | `sql/03_metric_view.sql` (version 0.1; same as `99`) | `CREATE VIEW … WITH METRICS` succeeds |
| Queries | `sql/04_queries.sql` (or the Act 1 / Act 2 tail of `99`) | Act 1 rows fight; Act 2 `MEASURE()` agrees; Act 3 `SELECT *` fails |
| Store | `sql/05_store.sql` | Unbilled metadata + Unbilled gold FROM `MEASURE()`; enterprise `$179,934.00`. After 08/09: 3 approved catalog rows and gold for all three KPIs. |

`02` / the facts block in `99` builds the certified **population**
(ticket grain). It is the compiler source, not gold published KPI
values. `04` does not re-encode `gallons_net * contract_price`.
`05` publishes Store metadata + gold snapshots FROM `MEASURE()`.

---

## First SQL to prove Metric Views compile

**Optional** and **not the pack dialect**. The pack dialect is YAML
**version 0.1** on `fct_unbilled` (`sql/03_metric_view.sql` /
`scripts/04_metric_view.py`). The live proof on 2026-08-14 used
`workspace.o2c_unbilled` (version 0.1), not this smoke view. Keep this
only if you want a `samples.tpch` check before loading O2C.

```sql
CREATE OR REPLACE VIEW workspace.default.mv_o2c_smoke
WITH METRICS
LANGUAGE YAML
AS $$
version: 0.1
source: samples.tpch.orders
fields:
  - name: order_status
    expr: o_orderstatus
measures:
  - name: order_count
    expr: COUNT(1)
$$;

SELECT MEASURE(order_count) AS order_count
FROM workspace.default.mv_o2c_smoke;
```

If `CREATE VIEW` succeeds, Metric Views compile on this warehouse.
Then run `sql/03_metric_view.sql` for the real Unbilled measure
(after 01 + 02). If `samples` is missing on Free, skip the smoke test
and use `03` as the proof.

Official create / query:
[Create a metric view](https://docs.databricks.com/aws/en/uc-semantics/metric-views/create) ·
[Query metric views](https://docs.databricks.com/aws/en/uc-semantics/metric-views/query) ·
[Feature availability](https://docs.databricks.com/aws/en/uc-semantics/metric-views/feature-availability)
(2026-08-05: Metric Views work on a SQL warehouse; warehouse auto-updates DBSQL).

---

## Expected Act 1 / Act 2 numbers

Computed from `data/*.csv`. Live-loaded 2026-08-14 via `99` (version 0.1).

```
Report A (sold-to, 4 rows)          $179,934.00
  Apex Fuels Houston Rack             79,362.40
  Metro Lubes Beaumont                37,454.40
  Apex Fuels Dallas Dealer            36,598.40
  Gulf Coast Aviation Inc             26,518.80

Report B (payer, 3 rows)            $179,934.00
  Apex Fuels LLC                     115,960.80   ← Houston + Dallas
  Metro Lubricants                    37,454.40
  Gulf Coast Aviation Inc             26,518.80

MEASURE(unbilled_usd) unsliced      $179,934.00
MEASURE() by sold_to / payer / site   same grand total, different rows
SELECT * FROM unbilled_usd            refused (Act 3)
```

Apex Fuels LLC **equals** Houston Rack + Dallas Dealer. Adding those
three "customer" lines double-counts. Aviation matches on both reports
(same org, both roles).

---


---

## Second and third KPIs (compiler joins / filters)

`unbilled_usd` stays the certified Unbilled measure (YAML 0.1, source
`fct_unbilled`, no joins). Two extra Metric Views prove the compiler
writes SQL for a complex formula. They are **not** a second Unbilled. Each is approved and publishes
its own Gold rows FROM its own `MEASURE()` (RC-1 per KPI). Gold grains
follow `allowed_grain`: contract-vs-list = enterprise / sold_to /
product; temp-adjusted = enterprise / product / site. One published
measure each (`delivered_contract_usd`, `temp_adjusted_usd`).
`formula_pointer` is the measure name; `formula_object` is the view.
Meaning IRIs: Unbilled `#UnbilledState`; the two delivered KPIs
`#Obligation`. Genie is the ad hoc path for all three (MEASURE() only).

| View | What it is | Source |
| --- | --- | --- |
| `unbilled_usd` | Unbilled USD (SUM/GROUP BY) | `fct_unbilled` |
| `contract_vs_list_usd` | Delivered-ticket value at contract vs list | `raw_tickets` + 4 star joins |
| `temp_adjusted_delivered_usd` | Temperature-adjusted delivered value (rack math) | `raw_tickets` + 4 star joins |

Author version **0.1** first (fields + measures + joins + filter). No
1.1 agent metadata. If Free refuses `joins`/`filter` on 0.1, retry the
same shape with `version: 1.1` on that view only.

## Two YAML files

| File | Job | Who reads it in this demo |
| --- | --- | --- |
| `sql/03_metric_view.sql` (YAML inside `WITH METRICS`) | Compile to SQL | Databricks (`CREATE VIEW` + `MEASURE()`) |
| `osi/unbilled.ossie.yaml` | Portable interchange (Apache Ossie 0.1.1) | Nobody. Projection of the same metric. |

Ossie is **not** the compiler and **not** an ontology. `relationships`
in that file are join paths, not OWL object properties. Do not import
it as OWL.

---

## Parked (do not add to this pack)

- **Azure / Synapse / Fabric** - actual project only. This pack is Free.
- **MetricFlow / dbt / DuckDB** - Track A. Leave that directory alone.
- **Cube** - no shipped Ossie→Cube converter as of August 2026. A
  hand-written `cube.yml` would be a second formula.
- **Airflow** - orchestrator, not a compiler. `01→02→03` run by hand
  is that DAG for this lesson.
- **Ontology (RDF / OWL / SHACL)** - system of record for *meaning*.
  Project IRIs *into* Ossie later; do not import Ossie or the Metric
  View as OWL.
- **A second Lakebase project** - no. Act 0 is schema `o2c_unbilled` on
  existing `dataexpert-day1` / `databricks_postgres` only.
- **A second `SUM(fct_unbilled)` as gold** - no. `gold_kpi_value` is
  sourced FROM `MEASURE()` on the Metric View (RC-1). Metadata points;
  it does not author the formula.
- **Genie Export-to-metric-view** - no. That would mint a second
  formula. Genie is ad hoc only; it queries the Metric View you authored.
- **Committed PAT / workspace URL / `.databrickscfg`** - never. Local
  `.env` is gitignored. The Mac `uv` path reads a token you mint;
  it is not in the repo.
- **Writing into other day1 schemas / DROP SCHEMA** - never. Scripts
  refuse `LAKEBASE_SCHEMA` other than `o2c_unbilled`.

---

## Project layout

```
o2c-unbilled-databricks-free/
  README.md                 # this file
  WALKTHROUGH.md            # teaching narrative
  pyproject.toml            # uv deps (databricks-sdk, sql-connector, psycopg)
  .env.example              # no secrets - copy to .env on your Mac
  data/                     # seven O2C CSVs + cv_* / dim_customer / sap_partner / tas / sf / ra sidecar + README
  sql/01_land.sql                  # human-authored: schema, volume, land from volume
  sql/02_facts.sql                 # human-authored: star-ish dims + fct_unbilled
  sql/03_metric_view.sql           # human-authored YAML 0.1 (pack dialect; fields + measures)
  sql/04_queries.sql               # human-authored Act 1 / Act 2 / Act 3
  sql/05_store.sql                 # Silver dim_kpi_metadata + Gold FROM MEASURE()
  sql/06_complex_metric.sql        # second KPI contract_vs_list_usd (not Unbilled)
  sql/07_temp_adjusted.sql         # third KPI temp_adjusted_delivered_usd (rack math)
  sql/99_full_load.generated.sql   # generated: VALUES + facts + version 0.1 + queries
  osi/unbilled.ossie.yaml   # Ossie 0.1.1 sidecar; nobody compiles it
  scripts/config.py         # env + SQL helpers; refuses missing token/password
  scripts/00_lakebase_ods.py     # Act 0: schema o2c_unbilled on dataexpert-day1
  scripts/00b_land_replica.py    # Lakebase ops → Databricks raw_* (no federation)
  scripts/01_connect.py     # current_user / current_catalog / warehouse
  scripts/02_load.py        # optional CSV → raw_* shortcut (skips Act 0)
  scripts/03_facts.py       # sql/02_facts.sql with placeholders substituted
  scripts/04_metric_view.py # version 0.1 WITH METRICS, one statement
  scripts/05_query.py       # Act 1 / Act 2 MEASURE() / Act 3 SELECT *
  scripts/06_store.py       # dim_kpi_metadata + gold_kpi_value FROM MEASURE()
  scripts/08_complex_metric.py  # second KPI: joins + filters + multiply
  scripts/09_temp_adjusted.py   # third KPI: temp-adjusted delivered (rack math)
  scripts/07_genie.py       # Genie Agent; run AFTER 08/09; MEASURE() on all three approved views
  scripts/07_genie.md       # Genie Agent notes (no secrets)
  scripts/catalog_status.py # status hash / drift / re-approve helper
  scripts/13_status_drift.py
  scripts/14_reapprove.py
  scripts/15_edit_reset_prove.py
  sql/08_catalog_status.sql
  scripts/10_cv_map.py      # controlled vocabulary + live-key map + prove
  scripts/12_cv_hunt.py     # word-hunt: table → column → value → map (TABS skipped)
  scripts/11_cv_search_genie.py  # second Genie: vocabulary search only
  scripts/11_cv_search_genie.md  # search-Genie notes (no secrets)
  THE-PROBLEM.md            # stakeholder language: overloaded "customer"
  scripts/CHECKLIST.md      # SQL-editor click-through
```

No `demo.sh`. No Docker. No Azure CLI. No token in git.

Read `WALKTHROUGH.md` for grain, party roles, and what each number means.

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `CREATE SCHEMA` denied | Use `{{schema}}` = `default` (Free default privileges). Recreate the volume there. |
| Catalog is not `workspace` | Use the name under **Catalog** in the sidebar. |
| `read_files` fails | Upload path wrong, or use the commented `COPY INTO` fallback in `01_land.sql`. |
| `wget` / `dbutils.fs.cp` from https | Free outbound internet is restricted. Upload via UI. |
| `WITH METRICS` / `MEASURE` unknown | Warehouse not attached, or Metric Views unavailable on this Free workspace. That is the live proof this pack cannot fake. |
| `SELECT *` errors | Expected (Act 3). Use `MEASURE(unbilled_usd)`. |
| Quota / warehouse stopped | Free fair-use. Data stays; compute returns tomorrow. |
| Landed on `*.azuredatabricks.net` | Wrong product. Sign in at login.databricks.com for Free. |
| Totals ≠ $179,934.00 | CSVs not the ones in `data/`, or `02_facts.sql` not run, or as-of filter changed. |
| `01_connect.py` refuses / missing token | Copy `.env.example` → `.env` and set `DATABRICKS_TOKEN`. Never commit it. |
| PAT **Manage** missing on Free | Official Free page does not confirm PAT minting. Use `databricks auth login` then `databricks auth token`. |
| OAuth token expired (~1 hour) | Re-run `databricks auth token --host "$DATABRICKS_HOST"` and update `.env`. |
| `00_lakebase_ods.py` refuses / missing password | Fill `LAKEBASE_*` from **dataexpert-day1 → Connect**. Never commit them. |
| Tempted to create a new Lakebase project | Don't. Act 0 is a new **schema** on the existing project. |
| Federated Lakebase query from the warehouse | Out of scope. `00b` copies rows in Python, then 03/04 stay on Databricks. |
| Tempted to Export-to-metric-view from Genie | Don't. That mints a second formula. Attach the existing Metric View. See `scripts/07_genie.md`. |
| Genie answers from `fct_unbilled` or `raw_*` | Fail. Agent must MEASURE() the matching approved view (unbilled / contract / temp-adjusted). |
