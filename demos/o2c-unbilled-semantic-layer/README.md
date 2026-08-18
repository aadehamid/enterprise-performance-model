# O2C Unbilled USD — consumption semantic layer demo

A **runnable** local demo of a consumption semantic layer for downstream oil & gas
order-to-cash. It shows why two reports both named **Unbilled USD** disagree
(payer vs sold-to vs site grain; net vs gross gallons; quality-hold), then shows
**one certified fact** (`fct_unbilled`) and **one MetricFlow metric** that
compiles to SQL over that fact. Act 1 A/B already query the fact. Act 3 is the
same number through `mf query`.

This is **not** a KPI Store catalog. There is one certified metric
(`unbilled_usd`) plus two supporting metrics. No ontology build.

Stack: **DuckDB file** + **dbt Core** + **dbt-duckdb** + **dbt-metricflow**.
No Docker. No cloud account. No paid dbt Cloud.

Verified on this project's Linux box with Python 3.12. A Mac with Python 3.11
or 3.12 should match.

---

## What you are looking at (the story)

A Gulf Coast fuels marketer lifts product at three terminals (Houston Ship
Channel, Dallas, Beaumont). Invoices go to the **payer**, not the sold-to.

- **Apex Fuels LLC** is the payer for two sold-tos: Houston Rack and Dallas Dealer.
- **Gulf Coast Aviation Inc** is payer *and* sold-to (same org).
- **Metro Lubricants** pays for Metro Lubes Beaumont.
- **Ship-to is a terminal**, not a customer role.

Finance publishes two "Unbilled USD" workbooks. They do not match.

1. **Report A** groups the certified ticket set by **sold-to** ("customer").
2. **Report B** groups the **same tickets** by **payer** ("customer").
3. **Report C** is sloppy: ambient (gross) gallons × list price, includes
   quality-hold tickets, and mixes sold-to / payer into one customer column.

Act 2 shows that **metadata is one row** (`dim_kpi_metadata`) while **grain
lives on the fact** (Houston vs Dallas are many rows).

Act 3 compiles `unbilled_usd` with MetricFlow. Slice by sold-to or payer —
the ticket set does not change. Report C stays different because it never
used `fct_unbilled` / the metric.

---

## Mac setup (Python 3.11 or 3.12) — uv first

Homebrew is **not** required. Docker is **not** required.

**Python 3.13 will not work** with this pin set (`dbt-metricflow` 0.10/0.11
requires Python `<3.13`). Check first:

```bash
python3 --version
```

If you only have 3.13, install 3.12 from [python.org](https://www.python.org/downloads/)
and pass `--python 3.12` to `uv venv` (or use `python3.12` in the fallback).

### 1. Unzip and enter the project

```bash
unzip o2c-unbilled-semantic-layer.zip
cd o2c-unbilled-semantic-layer
```

### 2. Create the venv and install (uv)

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) if you
do not already have it. `requirements.txt` is what `uv pip install -r` reads.

```bash
# Python 3.11 or 3.12 only (3.13 will not resolve dbt-metricflow 0.11)
# Install uv: https://docs.astral.sh/uv/getting-started/installation/

uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
chmod +x scripts/demo.sh
./scripts/demo.sh
```

`demo.sh` sets `DBT_PROFILES_DIR` to the project root so dbt does **not**
need `~/.dbt/profiles.yml`.

### Without uv (fallback)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
chmod +x scripts/demo.sh
./scripts/demo.sh
```

---

## What success looks like

You should see three different *presentations* of "Unbilled USD", then a
MetricFlow table that matches Report A/B's ticket set.

**Act 1 grand totals** (deterministic seed=42; your Mac must match):

```
Report A (sold-to, certified ticket set): $6,049,649.77
Report B (payer,   certified ticket set): $6,049,649.77
Report C (sloppy basis + holds + mix):    $7,393,499.19
```

A and B share a total (same 446 delivered-unbilled tickets) but **not** a
customer grain: 4 sold-to rows vs 3 payer rows. Apex Fuels LLC (payer)
`$4,095,877.44` equals Houston Rack + Dallas Dealer. Adding those three
lines double-counts.

Report C is a different number because it uses gross gallons, list price,
and quality-hold tickets.

**Act 3** — MetricFlow (`--decimals 2` for readable money):

```
$ mf query --metrics unbilled_usd --decimals 2

  unbilled_usd
--------------
    6049649.77
```

```
$ mf query --metrics unbilled_usd --group-by ticket__sold_to --decimals 2

ticket__sold_to               unbilled_usd
------------------------  ----------------
Apex Fuels Houston Rack         2726475.31
Apex Fuels Dallas Dealer        1369402.13
Metro Lubes Beaumont            1134397.03
Gulf Coast Aviation Inc          819375.30
```

`mf query --metrics unbilled_usd --explain` must print SQL that `SUM`s
`unbilled_usd` from `fct_unbilled`. That is the compiler: YAML → SQL.

MetricFlow prefixes categorical dimensions with the primary entity
(`ticket`), so the group-by names are `ticket__sold_to`, `ticket__payer`,
`ticket__terminal` — not the bare words `sold_to` / `payer`.

---

## Two semantic files

This zip has two YAML files that talk about the **same** metric. They are
not interchangeable, and only one of them is compiled in this demo.

| File | Job | Who reads it in this demo |
| --- | --- | --- |
| `models/semantic_models.yml` | Compile to SQL | MetricFlow (`mf query`, `mf --explain`) |
| `osi/unbilled.ossie.yaml` | Portable interchange (Apache Ossie / formerly OSI) | Nobody in this demo. Projection of the same metric. |

The **formula source of truth** is still the dbt fact (`fct_unbilled`), not
either YAML. Both files *describe* `unbilled_usd` (`SUM` of
`fct_unbilled.unbilled_usd` on the certified ticket set). MetricFlow is the
compiler that turns the dbt YAML into SQL. The Ossie file is interchange:
another tool *could* read the metric name, grain, and expression. Nothing
in this zip does.

dbt Core only parses `osi/` on **1.12+**. This project stays on **1.10** so
`mf --explain` keeps working with MetricFlow 0.11. **Do not upgrade dbt to
"use Ossie"** — that breaks the 0.11 compiler pin.

Ossie is **not** an ontology. `relationships` in the Ossie file are join
paths for a semantic model, not OWL object properties. Do not import
`osi/unbilled.ossie.yaml` as OWL.

---

## Can Cube speak Ossie?

**Not yet.** Cube is an OSI / Ossie launch partner and plans adapters, but
as of August 2026 there is no shipped Cube import of Ossie YAML. Apache
Ossie issue [#248](https://github.com/apache/ossie/issues/248) ("Add a Cube
converter") is open / not merged. No `cube` CLI in this zip reads
`osi/unbilled.ossie.yaml`.

A "second Cube lane" today would mean hand-writing a `cube.yml` that
re-encodes `unbilled_usd`. That is a **second formula** — the thing this
demo exists to stop. When `ossie-cube` (or Cube's own adapter) ships, the
intended lane is: Ossie file → converter → Cube model → Cube compiles SQL.
Park that. **Do not add Cube to this zip.**

---

## Airflow — what role, why not in this zip

Airflow would be the **orchestrator**, not a compiler and not a semantic
layer. In production it would schedule:

1. Land / generate operational extracts
2. `dbt seed` + `dbt run` (rebuild silver/gold, including `fct_unbilled`
   and `gold_kpi_unbilled` at a given `as_of`)
3. Optionally publish / test

`demo.sh` is that DAG, run once by hand. Adding Airflow (scheduler +
webserver, usually Docker) to a Mac zip that is `uv + ./scripts/demo.sh`
is the same class of glue as adding Postgres: real later, muddies this
lesson. Park it.

---

## What we plan to add later (do not add now)

Each of these is a **separate lesson**, not this zip:

- **Ontology (RDF / OWL / SHACL)** — system of record for *meaning*
  (sold-to ≠ payer ≠ ship-to). Project IRIs *into* Ossie; do not import
  Ossie YAML as OWL.
- **Postgres as ODS** — operational store; replicate into the DuckDB
  warehouse; medallion raw → silver → gold / star. DuckDB stays the
  compile target for MetricFlow in the laptop demo.
- **Cube lane** — only after an Ossie→Cube converter exists. Same Ossie
  file, second compiler. Not a second hand-authored formula.
- **Airflow** — schedule the dbt / gold refresh. Replaces `demo.sh` as
  the runner, does not replace MetricFlow.
- **dbt 1.12 + native Ossie parse** — only when MetricFlow on that line
  is stable. Until then keep 1.10 + sidecar `osi/`.

---

## Manual commands (after the venv is active)

```bash
export DBT_PROFILES_DIR=.
export DBT_TARGET=dev

python scripts/generate_data.py          # optional; seeds/ CSVs are already in the zip
dbt seed --target dev
dbt run --target dev
dbt parse --target dev
dbt test --target dev                    # optional

python scripts/act1_reports.py
python scripts/act2_grain.py

mf list metrics
mf query --metrics unbilled_usd --explain
mf query --metrics unbilled_usd --decimals 2
mf query --metrics unbilled_usd --group-by ticket__sold_to --decimals 2
mf query --metrics unbilled_usd --group-by ticket__payer --decimals 2
mf query --metrics unbilled_usd --group-by ticket__sold_to,ticket__terminal,metric_time__day --decimals 2
```

DuckDB file: `./o2c.duckdb` (regenerated by `dbt seed` / `dbt run`).

---

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `mf: command not found` | `source .venv/bin/activate`. `which mf` should be `.venv/bin/mf`. |
| `dbt: command not found` | Same venv. Or `python -m dbt.cli.main seed`. |
| Empty / missing tables | Run `dbt seed && dbt run` first. `mf query` reads materialized tables. |
| `Could not find profile` | `export DBT_PROFILES_DIR=.` from the project root. |
| `sold_to` is not a group-by item | Use `ticket__sold_to` (MetricFlow prefixes with the primary entity). `mf list dimensions --metrics unbilled_usd`. |
| Python 3.13 / `No matching distribution for dbt-metricflow` | Use Python 3.11 or 3.12. 0.10/0.11 require `<3.13`. |
| `mf` opens Metafont (rare on Mac) | Your PATH resolved a TeX binary. Use `.venv/bin/mf` or `python -m dbt.cli.main` is **not** the MetricFlow CLI — call `.venv/bin/mf` explicitly. |
| Time-spine / empty `metric_time` results | Spine is 2026-01-01 … 2026-08-31. Lifts are Jun–Jul 2026. Re-run `dbt run`. |
| Totals do not match README | You changed the generator seed, or did not `dbt run` after regenerating seeds. |

---

## Project layout

```
o2c-unbilled-semantic-layer/
  README.md
  WALKTHROUGH.md
  VERIFY.txt                 # actual commands + output from the verification box
  requirements.txt           # what `uv pip install -r` (or pip) reads
  profiles.yml               # duckdb path: ./o2c.duckdb
  dbt_project.yml
  scripts/generate_data.py
  scripts/demo.sh
  scripts/act1_reports.py
  scripts/act2_grain.py
  seeds/*.csv
  models/staging/
  models/intermediate/
  models/marts/              # dims, facts, fct_unbilled, gold_kpi_unbilled, dim_kpi_metadata
  models/metricflow_time_spine.sql
  models/semantic_models.yml # compile SoT for MetricFlow (semantic_models: / metrics:)
  osi/unbilled.ossie.yaml    # Ossie projection; nobody in this demo reads it
  analyses/act1_conflicting_reports.sql
  tests/                     # dbt tests (holds excluded; one metadata row)
```

Read `WALKTHROUGH.md` for grain, party roles, and what each number means.

---

## Version pins (what actually installed)

The originally requested pins (`dbt-core>=1.8,<1.10` **and**
`dbt-metricflow>=0.10`) **cannot resolve**: published `dbt-metricflow` 0.10.x
requires `dbt-core>=1.10.4,<1.11.0`. We relaxed only the dbt-core / dbt-duckdb
upper bound to the **1.10 line** so the **legacy standalone YAML spec** still
applies (dbt 1.12's embedded `semantic_model:` under models is avoided).

Resolved on the verification box (Python 3.12.13):

- `dbt-core==1.10.23`
- `dbt-duckdb==1.10.1`
- `dbt-metricflow==0.11.0`
- `metricflow==0.209.0`
- `duckdb==1.5.5`
