# O2C Unbilled USD - learner pack (Databricks Free)

This folder is the **empty workbook**. The answers live next door.

| Folder | What it is |
| --- | --- |
| `demos/o2c-unbilled-databricks-free-learn/` | **This pack.** Instructions, seed CSVs, empty stubs. You write the SQL, YAML, and Turtle. |
| `demos/o2c-unbilled-databricks-free/` | **Complete pack.** Working SQL, `uv` scripts, ontology. Peek when stuck. Do **not** empty it. |
| `demos/o2c-unbilled-semantic-layer/` | **Demo 1 / Track A** (MetricFlow + DuckDB + dbt). A different pack. Do **not** touch it. |

Start in `LEARN.md`. Work the exercises in order. If you get stuck, open the matching **path** in the complete pack - do not copy it blindly.

---

## What this demo is

Demo **2** / Track B. Oil-and-gas O2C. Unbilled is a **state** of an
obligation (delivered BOL not yet invoiced), not a KPI kind.
`customer_grain ∈ {payer, sold-to, site}`. You choose the group-by.
The formula stays still.

The compiler is Unity Catalog **Metric Views**
(`CREATE VIEW … WITH METRICS` / `MEASURE()`), not MetricFlow.

Two ways to work: the **SQL editor** in the Free workspace (default),
or **from your Mac with `uv`** talking to the same warehouse. Either
way, sign in at [login.databricks.com](https://login.databricks.com)
and attach the **Serverless Starter Warehouse** (2X-Small).

## What this demo is not

| Not this | That lives… |
| --- | --- |
| Demo 1 / Track A (MetricFlow + DuckDB + dbt) | `demos/o2c-unbilled-semantic-layer/` - **do not edit it** |
| Azure Databricks (`*.azuredatabricks.net`) | The actual project, not this pack. Parked. |
| MetricFlow / `mf query` / dbt / DuckDB | Demo 1 only |
| A second Unbilled formula in the Store | Metadata points at the Metric View; gold snapshots FROM `MEASURE()` |
| An ontology that compiles | Ontology = meaning. The YAML is a formula |
| Working Python answers | Complete pack `scripts/*.py`. This pack has stubs only |

**C-10 one-liner:** ontology = meaning; Store catalog + this Metric View
= certified formula for **this** demo. Do not pretend the Metric View
is the ontology.

---

## Sign in (Free Edition only)

1. Open [login.databricks.com](https://login.databricks.com).
2. Use the Free Edition workspace Databricks created for you.
3. Workspace URL is usually `*.cloud.databricks.com`, **not**
   `*.azuredatabricks.net`. If you land on Azure, you are in the wrong
   product - stop and go back to Free. Azure is parked.
4. Attach the default **Serverless Starter Warehouse** (2X-Small).
   Free allows **one** SQL warehouse, serverless only. Quota can shut
   compute for the rest of the day.

Official limits:
[Free Edition limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).

Non-commercial. No R/Scala. No custom storage. One workspace + one
metastore.

---

## Mac + uv (optional)

This pack does **not** ship working `.py` files. You write SQL in the
warehouse editor, or you write your own connector scripts. The complete
pack's `scripts/` is the peek-if-stuck path.

On a Mac with [uv](https://docs.astral.sh/uv/) (`brew install uv`):

See `scripts/LEARN-PYTHON.md` for the exact commands.

```bash
cp scripts/.env.example .env
```

Fill `.env` on your machine only. Never commit it. There is no
workspace URL, token, or password in this pack - and there must not be.

Databricks scripts should refuse to start if `DATABRICKS_TOKEN` is empty.
Lakebase scripts should refuse if `LAKEBASE_PASSWORD` is empty.

---

## Placeholders

Every `sql/*.sql` stub you fill in should use:

| Token | Default | What it is |
| --- | --- | --- |
| `{{catalog}}` | `workspace` | Workspace catalog (name under **Catalog** in the sidebar; may match the workspace name, not the literal word `workspace`) |
| `{{schema}}` | `o2c_unbilled` | Demo schema. Fall back to `default` if `CREATE SCHEMA` is denied |

Do **not** commit a workspace URL or a token.

---

## Parked (do not add to this pack)

- **Azure / Synapse / Fabric** - actual project only. This pack is Free.
- **MetricFlow / dbt / DuckDB** - demo 1. Leave that directory alone.
- **A second Lakebase project** - no. Act 0 is schema `o2c_unbilled` on
  existing `dataexpert-day1` / `databricks_postgres` only.
- **Committed PAT / workspace URL / `.databrickscfg`** - never. Local
  `.env` is gitignored.
- **Writing into other day1 schemas / DROP SCHEMA** - never.
- **Genie Export to metric view** - you author version 0.1 yourself.
- **CRM / Lift / TABS** - no. Six hunt systems only (Demo2, SAP,
  Salesforce, Warehouse, RightAngle, TAS). No sixth `term_id`.
- **Hunt stubs on the certified Genie** - no. Certified Genie is
  Metric View / `MEASURE()` only. Hunt stubs stay off it.

---

## Project layout

```
o2c-unbilled-databricks-free-learn/
  README.md                 # why two folders exist
  LEARN.md                  # numbered exercises - do these yourself
  LEARN.html                # same exercises as LEARN.md, in the browser
  EXPLAIN-COMPONENTS.html   # seats / what each component is doing
  THE-PROBLEM.md            # why "customer" is not one thing
  data/                     # seven O2C seeds PLUS hunt sidecar CSVs (cv_* + six-system stubs)
  sql/00_lakebase_ods.sql   # stub - schema o2c_unbilled only on day1
  sql/01_land.sql           # stub - land CSVs into raw_*
  sql/02_facts.sql          # stub - fct_unbilled
  sql/03_metric_view.sql    # stub - version 0.1 first
  sql/04_queries.sql        # stub - no second formula
  sql/05_store.sql          # stub - metadata + gold FROM MEASURE()
  sql/06_complex_metric.sql # stub - second KPI (contract vs list; not Unbilled)
  sql/07_temp_adjusted.sql  # stub - third KPI (temp-adjusted delivered)
  ontology/o2c-meaning.ttl  # prefixes only - write the classes
  scripts/.env.example      # placeholders, no secrets
  scripts/LEARN-PYTHON.md   # uv commands; no working .py
```

No `demo.sh`. No Docker. No Azure CLI. No token in git. Do not zip yet.

Read `LEARN.md` and do the work.
