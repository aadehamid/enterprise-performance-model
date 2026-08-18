# Click-through checklist (workspace UI)

No `demo.sh`. No Docker. No Azure CLI. No token in git.
SQL-editor click-through. Mac `uv` path is in README (01–06, then 08, 09, then 07 Genie).

Live compile of version 0.1 succeeded 2026-08-14. Preferred path is
`sql/99_full_load.generated.sql` (no CSV upload). Do not write a
workspace URL into this pack.

## Before SQL

- [ ] Signed in at https://login.databricks.com (Free Edition)
- [ ] URL is `*.cloud.databricks.com`, not `*.azuredatabricks.net`
- [ ] Default **Serverless Starter Warehouse** (2XS) is running
- [ ] Looked at **Catalog** and wrote down the workspace catalog name
- [ ] Either open `sql/99_full_load.generated.sql` (placeholders already
      `workspace` / `o2c_unbilled`) **or** find/replace in `sql/01`–`05`

## Optional smoke test (no upload)

- [ ] Ran the `mv_o2c_smoke` `CREATE VIEW … WITH METRICS` from README
- [ ] `SELECT MEASURE(order_count) FROM …mv_o2c_smoke` returned a number
- [ ] If `samples.tpch` is missing: skip, use `03` as the compile proof

Optional. The 2026-08-14 proof used `99`, not this smoke view.

## Preferred: 99 (no upload)

- [ ] Ran the raw `CREATE OR REPLACE TABLE … VALUES` block in `99`
- [ ] Raw counts 8 / 10 / 3 / 3 / 19 / 6 / 6
- [ ] Facts block: `fct_unbilled` = 12 tickets, `$179,934.00`
- [ ] Metric View version 0.1 created (YAML indent intact)
- [ ] Act 1 A/B + Act 2 `MEASURE()` grids recorded
- [ ] Store: Unbilled row in `dim_kpi_metadata`; `gold_kpi_value` enterprise = `$179,934.00`

## Alternate: Land via volume

- [ ] `01_land.sql` Part A: schema + `landing` volume created
- [ ] Uploaded all seven `data/*.csv` via Catalog Explorer (no wget)
- [ ] `01_land.sql` Part B: row counts 8 / 10 / 3 / 3 / 19 / 6 / 6

## Facts

- [ ] `02_facts.sql` ran
- [ ] `fct_unbilled` = 12 tickets, `$179,934.00`

## Compile (the real proof)

- [ ] `03_metric_view.sql` `CREATE OR REPLACE VIEW … WITH METRICS` succeeded
- [ ] `DESCRIBE TABLE EXTENDED` shows the YAML in View Text

Live compile of version 0.1 succeeded 2026-08-14.

## Query

- [ ] Act 1 Report A: 4 sold-to rows, total `$179,934.00`
- [ ] Act 1 Report B: 3 payer rows, Apex Fuels LLC = `$115,960.80`
- [ ] Act 2 `MEASURE(unbilled_usd)` unsliced = `$179,934.00`
- [ ] Act 2 by `sold_to` / `payer` / `site` — same total, different rows
- [ ] Act 3 `SELECT *` failed (document the error)
- [ ] Did **not** paste a second `gallons_net * contract_price` into `04`

## Store (Silver metadata + Gold FROM MEASURE())

- [ ] `05_store.sql` / `scripts/06_store.py` ran
- [ ] After 05/06 only: Unbilled row present (`KPI-O2C-UNBILLED-USD`, status certified)
- [ ] After full run (08/09): **3** certified metadata rows (Unbilled + contract-vs-list + temp-adjusted)
- [ ] `formula_pointer` = `unbilled_usd` (measure name, not a SQL formula)
- [ ] `gold_kpi_value` grains: enterprise 1 / payer 3 / sold_to 4 / site 3
- [ ] Each grain slice `SUM(value_usd)` = `$179,934.00` / 12 tickets
- [ ] Enterprise published value = `$179,934.00`
- [ ] Gold joined to metadata on `kpi_id`
- [ ] Gold sourced FROM `MEASURE()`, not `SUM(fct_unbilled)`

## Do not

- [ ] Do not edit `demos/o2c-unbilled-semantic-layer/`
- [ ] Do not add a workspace URL, PAT, or `.databrickscfg` to this pack
- [ ] Do not run dbt / MetricFlow / DuckDB / Azure CLI
- [ ] Do not treat the Metric View as the ontology
- [ ] Do not Export-to-metric-view from Genie (second formula)

## Second / third KPIs (not Unbilled)

These prove the compiler writes joins + filters + multiply.
Do **not** change `unbilled_usd`. Gold publishes all three KPIs FROM their own `MEASURE()`. Genie is the ad hoc path for all three (MEASURE() only; not a second formula).

- [ ] `sql/06_complex_metric.sql` / `scripts/08_complex_metric.py` compiled
- [ ] `contract_vs_list_usd` unsliced contract = `$110,064.00` / 7 tickets
- [ ] List `$114,450.00` / spread `$4,386.00` / hot `$50,887.20`
- [ ] `SELECT *` on `contract_vs_list_usd` refused
- [ ] `sql/07_temp_adjusted.sql` / `scripts/09_temp_adjusted.py` compiled
- [ ] `temp_adjusted_delivered_usd` unsliced adj ≈ `$256,066.39` / 17 tickets
- [ ] Net `$252,617.20` / marine adj ≈ `$138,692.75`
- [ ] `SELECT *` on `temp_adjusted_delivered_usd` refused
- [ ] KPI 2 pointer = `delivered_contract_usd` (measure), object = view, status `certified`, iri `#Obligation`
- [ ] KPI 2 gold grains enterprise / sold_to / product; enterprise `$110,064.00` / 7
- [ ] KPI 3 pointer = `temp_adjusted_usd`, status `certified`, iri `#Obligation`
- [ ] KPI 3 gold grains enterprise / product / site; enterprise ≈ `$256,066.39` / 17
- [ ] Full-run catalog = 3 certified rows; gold has all three kpi_ids; Unbilled gold still 11 / `$179,934.00`
- [ ] `unbilled_usd` YAML still version 0.1 (fields + measures only)

## Genie Agent (ad hoc only)

Genie Agent is the ad hoc KPI path for **all three** certified
Metric Views. Run it **after** KPI 2 (08) and KPI 3 (09) so those
views exist. It must query the matching view with `MEASURE()`.
It must **not** author a second formula. Export-to-metric-view
is forbidden.

Official: [Create and manage a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up)
· [Genie Agents API](https://docs.databricks.com/aws/en/genie/conversation-api)

Find the agent by title `O2C certified KPIs` only (script updates
the leftover `O2C Unbilled (certified)` in place). Not UI-only on
this workspace. See `scripts/07_genie.md`.
Mac path: `uv run python scripts/07_genie.py` (after 08 and 09).

- [ ] Agent titled **O2C certified KPIs** exists (one agent)
- [ ] Data sources are the three Metric Views (`unbilled_usd`, `contract_vs_list_usd`, `temp_adjusted_delivered_usd`)
- [ ] Did **not** attach `fct_unbilled` or `raw_*` as the semantic source
- [ ] Warehouse is Serverless Starter Warehouse
- [ ] Instructions: MEASURE() only on the matching view; unsliced = enterprise; Unbilled grain enterprise | payer | sold_to | site; contract enterprise | sold_to | product; temp-adjusted enterprise | product | site
- [ ] Instructions: if the question does not name a KPI, ask which one (Unbilled / contract-vs-list / temp-adjusted). Do not guess between contract-vs-list and temp-adjusted on a vague "delivered USD."
- [ ] Did **not** kebab → Export to metric view
- [ ] Unbilled unsliced → **$179,934.00 / 12 tickets** (`MEASURE()` on `unbilled_usd`)
- [ ] Unbilled by payer → 3 rows, same total
- [ ] Delivered contract unsliced → **$110,064.00 / 7** (`MEASURE()` on `contract_vs_list_usd`)
- [ ] Delivered contract by product → same total
- [ ] Temp-adjusted unsliced → **$256,066.39 / 17** (`MEASURE()` on `temp_adjusted_delivered_usd`)
- [ ] Temp-adjusted by site → same total
- [ ] Generated SQL uses `MEASURE()` on the matching view (not `fct_unbilled` / `raw_*`)
