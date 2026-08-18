# LEARN - do these yourself

Work in this folder. The complete pack is

`../o2c-unbilled-databricks-free/`

(absolute: `/workspace/domain-ontology-kpi/demos/o2c-unbilled-databricks-free/`).

Each exercise has a **goal**, what **done** looks like, and a **hint**
that points at a complete-pack **path** - not the answer SQL. Peek if
stuck; write your own.

Do **not** edit `../o2c-unbilled-semantic-layer/` (demo 1 / Track A).
Do **not** put a workspace URL, token, or password in this pack.
Do **not** empty the complete pack.

---

## 0. Sign in and attach the warehouse

**Goal.** Get onto Databricks **Free** with a warehouse you can run SQL on.

1. Sign in at [login.databricks.com](https://login.databricks.com) (Free).
2. Attach **Serverless Starter Warehouse** (2X-Small).

**Done.** The workspace URL is `*.cloud.databricks.com`, not
`*.azuredatabricks.net`. The 2XS warehouse is attached and running.
`SELECT current_user(), current_catalog();` returns a row.

**Hint.** Complete pack `README.md` § "Sign in (Free Edition only)".
If you landed on Azure, stop and go back to Free. Azure is parked.

---

## 1. Create / use the schema

**Goal.** Have a Unity Catalog schema for this demo.

Create or use `workspace.o2c_unbilled` (or your own catalog/schema name
if **Catalog** in the sidebar is not literally `workspace`). Fall back
to `default` if `CREATE SCHEMA` is denied.

**Done.** The schema exists. You wrote the catalog and schema names
down. Later files use `{{catalog}}` / `{{schema}}` as placeholders.

**Hint.** Complete pack `sql/01_land.sql` - Part A only (schema +
volume). Do not copy Part B yet.

---

## 2. Act 0 - Lakebase ODS (optional)

**Goal.** If you have Lakebase, land the seven seeds as ops tables on
the **existing** project. If you do not, skip and load CSVs in
exercise 3.

Constraints (non-negotiable):

- Project **dataexpert-day1** only. Database `databricks_postgres`.
- Schema **`o2c_unbilled` only**.
- Do **not** create a second Lakebase project.
- Do **not** touch other day1 schemas.
- Do **not** `DROP SCHEMA`.

**Done (if you run it).** Schema `o2c_unbilled` on dataexpert-day1 has
the seven tables with counts **8 / 10 / 3 / 3 / 19 / 6 / 6**. Host /
password stayed in local `.env`, never in the repo.

**Done (if you skip).** You decided to load CSVs in exercise 3. That
is fine.

**Hint.** Complete pack `sql/00_lakebase_ods.sql` and
`sql/00_README.md`. Write yours in this pack's `sql/00_lakebase_ods.sql`.

---

## 3. Land replica / load CSVs into `raw_*`

**Goal.** Get the seven seeds into Databricks as `raw_*` tables.

Two valid paths:

- **Replica:** read Lakebase `o2c_unbilled` tables in Python and write
  `workspace.o2c_unbilled.raw_*` via the SQL connector. No federated
  join from the warehouse.
- **CSV:** upload this pack's `data/*.csv` into a `landing` volume via
  Catalog Explorer, then `read_files` / `COPY INTO`. Do **not** wget
  (Free outbound internet is restricted).

**Done.** Tables `raw_parties`, `raw_party_roles`, `raw_products`,
`raw_terminals`, `raw_tickets`, `raw_invoices`, `raw_invoice_lines`
exist in your schema with counts **8 / 10 / 3 / 3 / 19 / 6 / 6**.

**Hint.** Complete pack `sql/01_land.sql` (volume + land) and
`scripts/00b_land_replica.py` (replica path). Seed files are in this
pack's `data/` - that is not an answer. Write yours in
`sql/01_land.sql`.

---

## 4. Build `fct_unbilled`

**Goal.** Seal the certified **population** at ticket grain.

A ticket is unbilled when:

1. `status = delivered`
2. no **posted** invoice line with `invoice_date <= 2026-08-01`
3. quality-hold is never billed and never unbilled
4. `unbilled_usd = gallons_net * contract_price`

This table is the population. It is **not** a second published formula
and **not** a gold KPI snapshot.

**Done.** `fct_unbilled` has **12** tickets and a grand total of
**$179,934.00**.

**Hint.** Complete pack `sql/02_facts.sql`. Write yours in
`sql/02_facts.sql`. As-of date is **2026-08-01**. Names can be
denormalized onto the fact so the Metric View stays one source table.

---

## 5. `CREATE VIEW … WITH METRICS` (version 0.1)

**Goal.** Author the Metric View YAML yourself. Compile it.

- `CREATE VIEW … WITH METRICS LANGUAGE YAML`
- Author **version 0.1** (fields + measures only). That is the
  pack dialect and the live-proven dialect.
- Source is `fct_unbilled`.
- You choose the group-by later; the formula stays still.
- **Do not Export from Genie.** You author this.

Do **not** author YAML 1.1 (`comment` / `display_name` / `synonyms`).
Monaco auto-indent can mangle YAML - paste as one block.

**Done.** The view creates as **one** statement. `MEASURE(unbilled_usd)`
returns a number. You wrote the YAML; you did not export it from Genie.

**Hint.** Complete pack `scripts/04_metric_view.py` (the 0.1 runner)
and `sql/03_metric_view.sql` (the same 0.1 YAML). Official:
[Create a metric view](https://docs.databricks.com/aws/en/uc-semantics/metric-views/create).
Write yours in `sql/03_metric_view.sql`.

---

## 6. Act 1 - two conflicting “customer” queries against the fact

**Goal.** Prove that two honest group-bys, both labeled "customer",
fight at the row level. Query **`fct_unbilled`**, not the Metric View
yet.

- Report A: group by sold-to, alias the name as `customer`.
- Report B: group by payer, alias the name as `customer`.

Same ticket set. Same grand total. Different rows.

Do **not** paste a second valuation into `sql/04_queries.sql`. The
population (ticket gate + `gallons_net * contract_price`) is on the
fact. Consumers use `MEASURE()`.

**Done.** Report A is 4 rows totaling **$179,934.00**. Report B is 3
rows totaling **$179,934.00**. Apex Fuels LLC (payer) equals Houston
Rack + Dallas Dealer. Adding those three "customer" lines
double-counts. Aviation matches on both reports (same org, both roles).

**Hint.** Complete pack `sql/04_queries.sql` (Act 1 section) and
`WALKTHROUGH.md` § 5. Write yours in `sql/04_queries.sql`.

---

## 7. Act 2 - `MEASURE()` at payer, sold_to, site

**Goal.** Same ticket set, same total, three grains - through the
compiler, not a second SQL copy of the formula.

```
SELECT … MEASURE(unbilled_usd) … GROUP BY payer
SELECT … MEASURE(unbilled_usd) … GROUP BY sold_to
SELECT … MEASURE(unbilled_usd) … GROUP BY site
```

You do not write `SUM` at query time for that measure. You do not
re-encode `gallons_net * contract_price`.

**Done.** Unsliced `MEASURE(unbilled_usd)` = **$179,934.00**. The three
group-bys still total **$179,934.00** with different row shapes
(3 / 4 / 3). Same tickets.

**Hint.** Complete pack `sql/04_queries.sql` (Act 2) and
`WALKTHROUGH.md` § 6. Official:
[Query metric views](https://docs.databricks.com/aws/en/uc-semantics/metric-views/query).

---

## 8. Act 3 - `SELECT *` should fail

**Goal.** See Databricks refuse a metric view treated as a regular
table.

Run `SELECT * FROM {{catalog}}.{{schema}}.unbilled_usd` (or whatever
you named the view).

**Done.** The statement errors. You wrote the message down (expect
something like `METRIC_VIEW_MISSING_MEASURE_FUNCTION`). Then you went
back to `MEASURE(unbilled_usd)`.

**Hint.** Complete pack `sql/04_queries.sql` (Act 3 - the commented
`SELECT *`) and `WALKTHROUGH.md` § 7.

---

## 9. Meaning sidecar - three sentences

**Goal.** Separate meaning from formula (C-10).

1. Read the complete pack's `ontology/o2c-meaning.ttl`
   (`../o2c-unbilled-databricks-free/ontology/o2c-meaning.ttl`).
2. Write **three sentences** (as comments in this pack's
   `ontology/o2c-meaning.ttl`, or a short note beside it):
   - what **Unbilled** is
   - what **customer_grain** is
   - why **C-10** splits meaning from formula
3. Fill in the classes in this pack's Turtle. Prefixes are already
   there.

Do not copy the formula into Turtle. Ontology does not compile.
Databricks does not read this folder.

Store catalog meaning bindings (do **not** add a `#DeliveredTicket`
class - Turtle already has `o2c:Obligation`, “A delivered BOL / ticket”):
Unbilled → `#UnbilledState`; contract-vs-list and temp-adjusted →
`#Obligation`.

**Done.** Three sentences in your own words, plus classes in
`ontology/o2c-meaning.ttl`. Unbilled is a **state**, not a KPI kind.
`customer_grain ∈ {payer, sold-to, site}`. Meaning ≠ formula.

**Hint.** Complete pack `ontology/o2c-meaning.ttl` and
`ontology/README.md`. See also complete pack `WALKTHROUGH.md` § 8
(Store vs consumption semantic layer vs ontology).

---

## 10. Store - `dim_kpi_metadata` + `gold_kpi_value`

**Goal.** Write Silver KPI metadata (one row per KPI) and Gold
snapshots FROM `MEASURE()`. Metadata points at the Metric View. Gold
does **not** re-encode `gallons_net * contract_price`. Honest seats:
the population is on `fct_unbilled`; the Metric View compiles
SUM/GROUP BY; Gold consumes `MEASURE()`. RC-1 per KPI (one compile
path each, no second SUM).

Layer story (locked):

```
ODS        Lakebase dataexpert-day1 / databricks_postgres / o2c_unbilled
Bronze     workspace.o2c_unbilled.raw_*   (replica; no federated join)
Silver     dim_* + dim_kpi_metadata   - one row per KPI (all certified)
Population fct_unbilled  (ticket grain; compiler source; NOT gold)
Compiler   Metric View unbilled_usd  (SUM/GROUP BY via MEASURE())
Gold       gold_kpi_value  - published KPI values FROM MEASURE(), not a second SUM()
```

- `dim_kpi_metadata`: one row per KPI. After this store step the
  Unbilled row exists (`kpi_id` = `KPI-O2C-UNBILLED-USD`, status
  `certified`). `formula_pointer` is the **measure name**
  (`unbilled_usd`), not a SQL formula. `formula_object` points at
  the Metric View. `ontology_iri` is `#UnbilledState`. After
  exercises 11–12 the catalog is 3 rows (1 certified Unbilled +
  2 more certified rows with Gold).
- `gold_kpi_value`: published Unbilled instances at enterprise /
  payer / sold_to / site. Values come FROM `MEASURE()`, not
  `SUM(fct_unbilled)`. First run: `CREATE TABLE IF NOT EXISTS`
  `gold_kpi_value`. Then **replace-by-kpi_id**: `DELETE` that
  `kpi_id`, `INSERT … MEASURE() … UNION ALL` the Unbilled grains.
  Never `CREATE OR REPLACE` the whole gold table (that wipes KPI
  2/3). If the warehouse refuses `INSERT` from a Metric View, run
  the four `MEASURE()` queries and load those results - still not
  a second `SUM()`.

Join gold to metadata on `kpi_id`.

**Done.** After this store step the Unbilled row exists in
`dim_kpi_metadata` (`KPI-O2C-UNBILLED-USD`, status `certified`).
`gold_kpi_value` enterprise grain is **$179,934** (12 tickets). Each
grain slice still totals **$179,934**. After exercises 11–12 the
catalog is **3** certified rows and Gold has all three KPIs.

**Hint.** Complete pack `sql/05_store.sql` and
`scripts/06_store.py`. Write yours in this pack's `sql/05_store.sql`.

---

## 11. Second Metric View - `contract_vs_list_usd` (not Unbilled)

**Goal.** Prove the compiler writes SQL for a **complex** formula:
joins + filters + cross-table multiply. This is a **second KPI**, not a
second Unbilled.

Author `workspace.o2c_unbilled.contract_vs_list_usd`:

- Source: `raw_tickets` (not `fct_unbilled`).
- Four star joins (many-to-one, `on:` boolean, prefix `source.`):
  `product_dim`, `sold`, `payer_dim`, `site_dim`
  (not `product`, `sold`, `payer`, `site` - those aliases collide
  with field names → `INVALID_EXTRACT_BASE_FIELD_TYPE`).
- View filter (all of): delivered, `temperature_f >= 80`,
  `gallons_net >= 5000`, July 2026, `product_family` in gasoline /
  distillate. Quality-hold drops out via status.
- Measures the compiler must emit (you only `MEASURE()`):
  `delivered_contract_usd`, `delivered_list_usd`,
  `list_minus_contract_usd`, `delivered_ticket_count`,
  `hot_rack_contract_usd` (temp >= 88), `marine_contract_usd`,
  `rbob_contract_usd`.

Version **0.1** first. No `comment` / `display_name` / `synonyms`.
On Free, a field name shadows a join of the same name - use
`product_dim` / `site_dim` / `payer_dim` so field `product` /
`site` / `payer` still work in `GROUP BY`.
If Free refuses `joins` / `filter` on 0.1, retry the **same** shape
with `version: 1.1` on **this** view only. Do **not** change
`unbilled_usd`.

**Done.** Unsliced `MEASURE(delivered_contract_usd)` = **$110,064.00**
/ 7 tickets. List = **$114,450.00**. Spread = **$4,386.00**.
`SELECT *` is refused. `unbilled_usd` still compiles as version 0.1.

**Hint.** Complete pack `sql/06_complex_metric.sql` and
`scripts/08_complex_metric.py`. Write yours in
`sql/06_complex_metric.sql`.

---

## 12. Third Metric View - `temp_adjusted_delivered_usd` (rack math)

**Goal.** A **third** KPI: volume-correction / temperature-adjusted
delivered value. Not Unbilled. Not contract-vs-list.

Author `workspace.o2c_unbilled.temp_adjusted_delivered_usd`:

- Same four star joins on `raw_tickets`.
- Filter: delivered, `gallons_net >= 4000`, Jun–Jul 2026,
  `product_family` in gasoline / distillate / aviation.
- Measures: `contract_at_net_usd`, `contract_at_gross_usd`,
  `temp_adjusted_usd` =
  `gallons_net * contract_price * (1 + expansion_per_f * (temp - 60))`,
  `expansion_delta_usd`, `delivered_ticket_count`, `net_gallons`,
  `gross_gallons`, `weighted_temp_x_gallons`,
  `marine_temp_adjusted_usd`.

Version **0.1** first; 1.1 only if this view needs it for joins/filter.
Do **not** change `unbilled_usd`. Do **not** flatten into a new fact.

**Done.** Unsliced `MEASURE(temp_adjusted_usd)` ≈ **$256,066.39** /
17 tickets. Net contract = **$252,617.20**. `SELECT *` is refused.

**Hint.** Complete pack `sql/07_temp_adjusted.sql` and
`scripts/09_temp_adjusted.py`. Write yours in
`sql/07_temp_adjusted.sql`.

---

## 13. Genie Agent - O2C certified KPIs / three views

**Goal.** Create one **Genie Agent** titled **O2C certified KPIs**
(official name; was Genie Space) that is the **ad hoc KPI path** for
**all three** certified Metric Views. Do this **after** exercises 11
and 12 so `contract_vs_list_usd` and `temp_adjusted_delivered_usd`
exist. Do **not** create an Unbilled-only agent first.

1. Create or find an agent titled `O2C certified KPIs`. If a leftover
   `O2C Unbilled (certified)` exists, **update it in place** (title +
   sources). Do not stand up a second agent.
   Official UI: sidebar **Genie Agents** → **New** (or open the
   leftover) → choose the three Metric Views → **Create** / save.
   Or use the complete-pack API script `scripts/07_genie.py` (peek if
   stuck). That script runs after 08/09.
2. Attach **all three** views:
   - `{{catalog}}.{{schema}}.unbilled_usd`
   - `{{catalog}}.{{schema}}.contract_vs_list_usd`
   - `{{catalog}}.{{schema}}.temp_adjusted_delivered_usd`
   Not `fct_unbilled`. Not `raw_*`.
3. Default warehouse = **Serverless Starter Warehouse**.
4. Instructions: only answer via `MEASURE()` on the matching view.
   Unsliced = enterprise. Grains:
   - Unbilled: **enterprise | payer | sold_to | site**
   - contract-vs-list: **enterprise | sold_to | product**
   - temp-adjusted: **enterprise | product | site**
   Never a generic "customer". If the question does not name a KPI,
   ask which one (Unbilled / contract-vs-list / temp-adjusted). Do
   not guess between contract-vs-list and temp-adjusted on a vague
   "delivered USD." Do not invent a second formula.
5. Ask these questions:
   - *What is total unbilled USD as of 2026-08-01?*
   - *What is unbilled USD by payer?*
   - *What is delivered contract USD as of 2026-08-01?*
   - *What is delivered contract USD by product?*
   - *What is temp-adjusted delivered USD as of 2026-08-01?*
   - *What is temp-adjusted USD by site?*
6. **Do not Export to metric view** (kebab menu). That would mint a
   second formula. You already authored the three views in exercises
   5 / 11 / 12.

**Done.** Unsliced Unbilled = **$179,934.00 / 12 tickets**. Delivered
contract = **$110,064.00 / 7**. Temp-adjusted = **$256,066.39 / 17**.
Generated SQL uses `MEASURE()` on the **matching** view. You did not
click Export to metric view. You have one agent, three views.

If Genie answers from `fct_unbilled` / `raw_*` (or re-encodes
`gallons_net * contract_price` or the temp expansion) that is a
**fail**, even if the dollars match. If it guesses a view on a vague
"delivered USD," that is also a fail - it must ask which KPI.

**Hint.** Complete pack `scripts/07_genie.md` and `scripts/07_genie.py`.
Official:
[Create and manage a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up).

---

## 14. Word hunt

**Goal.** Make the overloaded word "customer" visible without inventing
a KPI or renaming tickets.

1. Read `THE-PROBLEM.md` in this pack and/or complete-pack
   `THE-PROBLEM.md`.
2. Open / `DESCRIBE` the six sources: `raw_tickets`, `sap_partner`,
   `sf_account`, `dim_customer`, `ra_business_associate`, `tas_lift`.
   Table name is already a clue.
3. Read party columns and live values: `APEX-PAYER`, SAP `1000123` in
   two columns, `CONS-4412`, warehouse `1000123`, `SF-APEX`, `BA-APEX`,
   remittance `APEX-PAYER`.
4. Write a map as system + field + key → `term_id` (or empty = no map).
   Use only existing term_ids (`id:payer`, `id:sold-to`, `id:bill-to`,
   `id:ship-to`, `id:loading-authorized-party`). Do not invent a sixth
   `term_id`.
5. Same digits `1000123` are two SAP map rows (sold-to and bill-to);
   warehouse `customer_id` has no map. Salesforce `account_id` `SF-APEX`
   has no map (a relationship, not a role). `CONS-4412` is TAS consignee
   / LAP, not a payer. RA remittance → existing Payer id; BA field
   itself no map; credit is not mapped.
6. Prove: `cv_lookup('customer')` returns exactly two IDs. Apex payer
   `MEASURE` still **$115,960.80 / 8**. `customer_id` and `CONS-4412`
   refused as Unbilled grains. Catalog about-ID stays `#UnbilledState`.
7. Optional: second Genie titled **O2C vocabulary search** (cv tables
   only, never a dollar). Do not attach hunt stubs or `cv_*` to O2C
   certified KPIs.

**Done.** Six systems opened; map is system+field+key; no CRM; no Lift;
no `credit_party`; `sf_account` has no `customer_id`; lookup two IDs;
Apex still holds.

**Hint.** Complete pack `THE-PROBLEM.md`, `WALKTHROUGH.md` §14,
`scripts/10_cv_map.py`, `scripts/12_cv_hunt.py` (`paste_ready_sql`),
`scripts/11_cv_search_genie.py`. Peek after you have tried. Do not copy
blindly.

Do **not** invent a new KPI. Do **not** rename tickets. Do **not** stand
up a TABS stub. Do **not** stand up a rack-pricing stub. Hunt stubs stay
off both Genies. `system_name` lives only on source stubs, not
on `cv_*`.
