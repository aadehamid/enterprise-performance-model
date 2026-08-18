# Walkthrough - Unbilled USD on Databricks Free (Track B)

Teaching companion to `README.md`. Parallel to Track A
(`demos/o2c-unbilled-semantic-layer/WALKTHROUGH.md`) but **Metric Views
compile here**. Do not run Track A's `demo.sh`. Do not open DuckDB.

Live numbers below are computed from `data/*.csv` and were loaded
2026-08-14 via `sql/99_full_load.generated.sql` (Metric View version 0.1).
Do not put a workspace URL in this file.

---

## Layer story

```
ODS        Lakebase dataexpert-day1 / databricks_postgres / o2c_unbilled  (ops tables)
Bronze     workspace.o2c_unbilled.raw_*   (replica; Python pipe; no federated join)
Silver     dim_party, dim_site, dim_product, br_party_role
           + dim_kpi_metadata   - one row per KPI (all certified; pointer, not the formula)
Population fct_unbilled  (ticket grain; compiler source; ticket gate + gallons_net * contract_price; NOT gold)
Compiler   Metric View workspace.o2c_unbilled.unbilled_usd  (SUM/GROUP BY via MEASURE())
Gold       gold_kpi_value  - published KPI values FROM MEASURE(), not a second SUM()
```

Honest seats: `fct_unbilled` holds the ticket gate +
`gallons_net * contract_price` (population / compiler source). The
Metric View compiles SUM/GROUP BY (`MEASURE()`). Gold and Genie consume
`MEASURE()` and must not re-encode. RC-1 still holds for Gold/Genie
(one compile path, no second SUM). C-10: ontology = meaning.
`dim_kpi_metadata` does **not** author the formula.

---

## 1. What a consumption semantic layer is (this pack)

A **consumption semantic layer** is **not** a dashboard and **not** a warehouse table.

```
YAML (fields, measures) inside CREATE VIEW … WITH METRICS
        ↓  compiler (Unity Catalog Metric Views)
SQL that hits the warehouse (here: Free Edition SQL warehouse)
        ↓
The same number in every consumer
```

The **certified population** is sealed in `fct_unbilled` (`sql/02_facts.sql`):
delivered, no posted invoice as of 2026-08-01, quality-hold never
unbilled, `gallons_net * contract_price`. Delete the Metric View and
Act 1 still works. That is the production pattern.

The YAML in `sql/03_metric_view.sql` names the metric, the grain
dimensions (`payer`, `sold_to`, `site`, `as_of`), and which column to
`SUM`. The compiler writes the `SELECT` / `GROUP BY`. It does **not**
re-encode the unbilled rule. `04_queries.sql` has no second copy of
that formula.

Act 1 A/B already query the fact (two group-bys, same tickets). Act 2
is the **same number** through `MEASURE()`. Act 3 (`SELECT *`) is
refused on purpose.

---

## 2. Why Databricks Free is here (and why Azure is not)

Track A used DuckDB as a warehouse stand-in and MetricFlow as the
compiler, so a Mac could run the lesson offline. This pack moves both
jobs onto **one Free Edition workspace**:

| Job | Track A | This pack (Track B) |
| --- | --- | --- |
| Warehouse | DuckDB file | Free SQL warehouse (2XS, serverless) |
| Compiler | MetricFlow (`mf query`) | Unity Catalog Metric Views |
| How you ask | `mf query --metrics unbilled_usd --group-by ticket__payer` | `SELECT payer, MEASURE(unbilled_usd) … GROUP BY payer` |
| Local Python | `uv` + dbt + mf | `uv` scripts in `scripts/` (SQL connector). Not MetricFlow. |

Azure Databricks (`*.azuredatabricks.net`, Entra, Purview, classic
compute in your subscription) is for the **actual project**. Hamid
said so. This pack signs in at [login.databricks.com](https://login.databricks.com)
and stays on Free.

Free facts this lesson depends on (official, 2026):

- One SQL warehouse, 2X-Small; serverless only; quota can stop compute
  for the day.
- Unity Catalog on by default; workspace catalog + `default` schema;
  Free users have `USE CATALOG` / `USE SCHEMA` / `WRITE VOLUME` there.
- Outbound internet restricted - upload CSV via the UI.
- Metric Views: `CAN USE` on a SQL warehouse (or DBR 17.3+). YAML
  `source` / `fields` / `measures` with `expr`. Every measure uses
  `MEASURE()`. `SELECT *` is refused. Warehouse auto-updates DBSQL.

Metric Views **do create** on Free: live compile 2026-08-14 with
`version: 0.1` (`sql/03_metric_view.sql` / `scripts/04_metric_view.py` /
`sql/99_full_load.generated.sql`). Official Free pages still do not
name them. Pack dialect is 0.1 (fields + measures only).

---

## 3. Party roles vs sites

Downstream O2C overloads the word "customer".

| Role | Who in this demo | What it is for |
| --- | --- | --- |
| **Payer** | Apex Fuels LLC; Metro Lubricants; Gulf Coast Aviation Inc | Who is invoiced. Credit and cash live here. |
| **Sold-to** | Apex Houston Rack; Apex Dallas Dealer; Metro Lubes Beaumont; GCA | Who is entitled to lift under the contract. |
| **Bill-to** | Apex AP; Metro Shared Services; GCA | Who receives the invoice document. |
| **Site / ship-to** | **Not a party.** HSC / DAL / BMT | A **terminal** (location). |

Gulf Coast Aviation is payer *and* sold-to (same org). Apex is not:
one payer, two sold-tos. An Apex invoice can cover Houston *and*
Dallas tickets in the same week - billed to Apex Fuels LLC, not to
the rack desk. `INV-2026-0001` does exactly that.

If you default every KPI to "customer = sold-to", credit and unbilled
lie. If you default every KPI to "customer = payer", dealer
performance lies. The certified metric does not pick a customer for
you. **You choose the group-by.** The formula stays still.

`customer_grain ∈ {payer, sold-to, site}`.

---

## 4. The population rule

As of **2026-08-01**:

- `status = delivered`
- no posted invoice line with `invoice_date <= 2026-08-01`
- `unbilled_usd = gallons_net * contract_price_usd`
- quality-hold tickets are **never** billed and **never** unbilled

**Fact grain** (`fct_unbilled`): one row per BOL ticket. Easy to audit.
12 tickets in this pack.

**Published grain** is snapshotted in `gold_kpi_value` (`sql/05_store.sql`)
FROM `MEASURE()` at enterprise / payer / sold_to / site. That table is
not a second `SUM(fct_unbilled)`. Population holds the ticket gate +
`gallons_net * contract_price`. The Metric View compiles SUM/GROUP BY.
Gold and Genie use MEASURE() and must not re-encode (RC-1).

`INV-2026-0005` is posted on 2026-08-03 against `BOL-2026-0104`. After
as-of, so that ticket stays unbilled. `INV-2026-0006` is `draft` and
does not count. Those two rows exist so the as-of rule is visible.

---

## 5. Why Report A and Report B both say "customer" and lie

Both reports are labeled **Unbilled USD**. Both use the certified
ticket set. Their **grand totals match**:

```
Report A (sold-to): $179,934.00   4 customer rows
Report B (payer):   $179,934.00   3 customer rows
```

They still fight, because someone will compare *rows*:

| Report A "customer" | USD | Report B "customer" | USD |
| --- | ---: | --- | ---: |
| Apex Fuels Houston Rack | 79,362.40 | Apex Fuels LLC | 115,960.80 |
| Apex Fuels Dallas Dealer | 36,598.40 | | |
| Metro Lubes Beaumont | 37,454.40 | Metro Lubricants | 37,454.40 |
| Gulf Coast Aviation Inc | 26,518.80 | Gulf Coast Aviation Inc | 26,518.80 |

Apex Fuels LLC **equals** Houston + Dallas. Those are the same eight
tickets rolled to the payer. If a slide adds the Apex payer line to
the two Apex sold-to lines, Unbilled USD is double-counted.

Report B has fewer rows than Report A **because two sold-tos roll to
one payer**. That is the grain lesson, not a data-quality bug.

Aviation matches on both reports - same org, both roles.

Metro looks like a rename (Beaumont vs Lubricants) until you remember
the sloppy twin at the bottom of `04_queries.sql` will put Metro on
the **payer** label while Apex stays on **sold-to** labels. That is
role-mixing.

Site grain (same tickets, third group-by):

| site | name | USD | tickets |
| --- | --- | ---: | ---: |
| HSC | Houston Ship Channel | 97,145.20 | 6 |
| DAL | Dallas | 45,334.40 | 4 |
| BMT | Beaumont | 37,454.40 | 2 |

`BOL-2026-0105` is a Houston sold-to lift at Dallas, so Houston's
$79,362.40 is not all HSC.

---

## 6. Act 2 - the compiler, not a second SQL copy

```sql
SELECT sold_to, MEASURE(unbilled_usd)
FROM {{catalog}}.{{schema}}.unbilled_usd
GROUP BY sold_to;
```

must match Report A. Swap `sold_to` for `payer` and it matches Report
B. Swap for `site` and you get the terminal rollup. The YAML did not
change. `04` did not grow a second `gallons_net * contract_price`.

That is the whole point of a consumption semantic layer.

`MEASURE()` inherits the aggregation from the Metric View. You do not
write `SUM` at query time for that measure. Official query page:
every measure uses `MEASURE()`; `SELECT *` is refused.

---

## 7. Act 3 - SELECT * fails

Uncomment the `SELECT *` in `04_queries.sql`. Expect an error. Write
the message down. That refusal is how Databricks stops a consumer from
treating a metric view like a regular table and accidentally
re-aggregating a measure.

Then go back to `MEASURE(unbilled_usd)`.

---

## 8. Store vs consumption semantic layer vs ontology

| | KPI Store (this demo) | Compiler (this demo) | Ontology (sidecar) |
| --- | --- | --- | --- |
| Job | Certify definition, owner, status, grain rule; publish instances | **Compute** the certified formula on demand | System of record for *meaning* |
| Artifact | `dim_kpi_metadata` + `gold_kpi_value` | Metric View YAML + `fct_unbilled` | RDF / OWL (`ontology/o2c-meaning.ttl`) |
| Consumer | "What is Unbilled USD, who owns it, what is the published number?" | "Give me Unbilled USD by payer" | "sold-to ≠ payer ≠ site" |

**C-10:** ontology = meaning; Store catalog + this Metric View =
certified formula for **this** demo. Do not pretend the Metric View
is the ontology. Honest seats: population on `fct_unbilled`; Metric
View compiles SUM/GROUP BY; Gold/Genie consume `MEASURE()` and must
not re-encode. RC-1 still holds for Gold/Genie.

`dim_kpi_metadata` is the Store catalog (one row per KPI). Unbilled
`formula_pointer` = `unbilled_usd` (measure name). `formula_object` =
`{{catalog}}.{{schema}}.unbilled_usd`. After a full run the catalog has
three certified rows. `gold_kpi_value` publishes each KPI FROM its
own `MEASURE()` - RC-1 per KPI, one compile path each. Genie is
the ad hoc path for all three certified KPIs (MEASURE() only).

---

## 9. How the Metric View is wired

`sql/03_metric_view.sql` authors YAML spec **0.1** (fields + measures
only). Same dialect as `scripts/04_metric_view.py` and `99`.

- **source** `{{catalog}}.{{schema}}.fct_unbilled` (no joins - names
  are already on the fact)
- **fields** `payer`, `sold_to`, `site`, `site_name`, `as_of`,
  `delivery_date`, `product`
- **measures** `unbilled_usd` = `SUM(source.unbilled_usd)`,
  `unbilled_ticket_count` = `COUNT(1)`

No YAML 1.1 `comment` / `display_name` / `synonyms`. No time spine.
No MetricFlow entity prefix (`ticket__sold_to`). Group by the field
names as written.

---


---

## 9b. Second and third KPIs (not a second Unbilled)

`unbilled_usd` is still the Unbilled compiler (YAML 0.1, one source
table, fields + measures). Two extra views demonstrate that the
**same** compiler writes joins, filters, and cross-table multiply.
Consumers still only `MEASURE()`. Gold publishes each KPI FROM its own `MEASURE()`. Genie is the ad hoc path for all three (MEASURE() only; not a second formula).

- **`contract_vs_list_usd`** (`sql/06_complex_metric.sql` /
  `scripts/08_complex_metric.py`) - delivered-ticket value at contract
  vs list. Source `raw_tickets`. Four star joins. Filter: delivered,
  temp ≥ 80, gallons ≥ 5000, July 2026, gasoline|distillate.
  Expected unsliced: contract **$110,064.00** / list **$114,450.00** /
  7 tickets.
- **`temp_adjusted_delivered_usd`** (`sql/07_temp_adjusted.sql` /
  `scripts/09_temp_adjusted.py`) - volume-correction / temperature-
  adjusted delivered value (rack math). Same joins. Filter: delivered,
  gallons ≥ 4000, Jun–Jul 2026, gasoline|distillate|aviation.
  Expected unsliced: net **$252,617.20** / adj **$256,066.39** /
  17 tickets.

Try YAML **0.1** first. If Free refuses `joins`/`filter`, retry the
same shape as **1.1** on that view only. Do not change `unbilled_usd`.
Do not flatten the formula into a new fact.

Join aliases on Free cannot match field names (`product` as a field
shadows join `product` → `INVALID_EXTRACT_BASE_FIELD_TYPE`). The
views use `product_dim` / `payer_dim` / `site_dim` / `sold` so
`GROUP BY product` / `site` / `payer` still work.

The four-join star is copy-pasted on purpose (same shape, two formulas).
The engine default is LEFT OUTER; the filter on
`product_dim.product_family` is an implicit inner join (every ticket
has a product).

## 10. Data notes

- 19 BOL tickets, 2026-06-10 … 2026-07-30. Hand-authored, not the
  Track A 1,200-row generator. Small enough for 2XS.
- Products: RBOB, ULSD, Jet-A. Contract price ≠ list price.
- 2 quality-hold tickets (never invoiced, never unbilled).
- 5 delivered tickets billed by posted invoices on or before as-of.
- 12 delivered tickets still unbilled as of 2026-08-01, including
  `BOL-2026-0104` whose invoice is dated 2026-08-03.
- Invoices billed to the **payer**. Apex `INV-2026-0001` covers both
  sold-tos.
- One cross-terminal lift (`BOL-2026-0105`) so sold-to ↔ site is not
  fake-clean.

There is no `generate_data.py` in this pack. Edit the CSVs if you
want different dollars; then re-run 01 Part B → 02 → 03.

---

## 11. Ossie projection

`osi/unbilled.ossie.yaml` is Apache Ossie spec **0.1.1**, same stance
as Track A: interchange only. Databricks does not parse `osi/`.
Ossie is not the compiler. Relationships are join paths, not OWL.

When ontology lands later, project IRIs *into* Ossie. Do not import
this YAML - or the Metric View YAML - as OWL.

---

## 12. Store objects

`sql/05_store.sql` / `scripts/06_store.py` add two Unity Catalog tables:

- **`dim_kpi_metadata`** - one row per KPI (all `certified`). Owner,
  definition, allowed grain, gating rule, status. `formula_pointer`
  is the Metric View **measure name**, not a SQL formula and not the
  view name. `formula_object` is the view. Unbilled `ontology_iri` is
  `#UnbilledState`; KPI 2 and 3 use `#Obligation` (the delivered-
  ticket class - do not add `#DeliveredTicket`). After 05/06 the
  Unbilled row is present. After a full run expect **3** certified
  rows. Gold publishes all three FROM their own `MEASURE()`. Genie
  is the ad hoc path for all three (MEASURE() only).
- **`gold_kpi_value`** - published snapshots FROM each KPI's own
  `MEASURE()`. Unbilled grains: enterprise / payer / sold_to / site
  (11 rows; each slice **$179,934.00** / 12). Contract-vs-list:
  enterprise / sold_to / product (`MEASURE(delivered_contract_usd)`).
  Temp-adjusted: enterprise / product / site
  (`MEASURE(temp_adjusted_usd)`). Replace-by-`kpi_id` (never
  `CREATE OR REPLACE` the whole table). Join to metadata on `kpi_id`.

If the warehouse refuses `CREATE TABLE … AS SELECT MEASURE()`, the
script falls back to `VALUES` built from those same `MEASURE()`
results. Still not `SUM(fct_unbilled)`.

---

## Meaning sidecar

`ontology/o2c-meaning.ttl` is the thin meaning sidecar for this pack.
Same terms the walkthrough already uses (sold-to ≠ payer ≠ site;
Unbilled is a **state** of an Obligation). The Metric View header
points at that file. They **agree**. They are **not** one object.

C-10: ontology = meaning; Store catalog + Metric View = certified
formula. This sidecar does not author the formula and does not compile.
IRIs are demo-only (`https://example.org/domain-ontology-kpi/o2c#`),
not G3/G4 signed. Full OWL / SHACL / triple store is parked
(Ontologist). See `ontology/README.md`.

---

## 13. Genie Agent (ad hoc only)

Genie Agent (was Genie Space) is the **ad hoc KPI path for all three
certified Metric Views**. It does not author a second formula. It
asks grain questions against the view you already compiled.

- Title: **O2C certified KPIs** (find by title only). Script updates
  the leftover `O2C Unbilled (certified)` agent in place.
- Attach all three views: `unbilled_usd`, `contract_vs_list_usd`,
  `temp_adjusted_delivered_usd`. Not `fct_unbilled` or `raw_*`.
- Answer with `MEASURE()` on the matching view. Unsliced = enterprise.
  Unbilled grain is enterprise | payer | sold_to | site; contract is
  enterprise | sold_to | product; temp-adjusted is enterprise |
  product | site. Never a generic "customer". If the question does
  not name a KPI, ask which one (Unbilled / contract-vs-list /
  temp-adjusted). Do not guess between contract-vs-list and
  temp-adjusted on a vague "delivered USD."
- Do **not** Export-to-metric-view (that would mint a second formula).
- Expected unsliced: Unbilled **$179,934.00 / 12**; contract
  **$110,064.00 / 7**; temp-adjusted **$256,066.39 / 17**.

Details: `scripts/07_genie.md`. Recreate/re-ask: `scripts/07_genie.py`.

---

## 14. Controlled vocabulary + map (after Genie)

Working-pack pointer only. Stakeholder language is `THE-PROBLEM.md`.
This is **not** a new KPI and **not** an ontology load. Tickets stay
as they are (no `customer_id` column). `scripts/config.py` `TABLES`
is not edited - the sidecar is not Lakebase/raw.

```bash
uv run python scripts/10_cv_map.py
uv run python scripts/12_cv_hunt.py
uv run python scripts/11_cv_search_genie.py
```

`12` is the hunt itself (open the source tables, read columns and
values, show the map rows that came from that work). After 10.
Includes Salesforce (`sf_account.account_id` / `SF-APEX` no map) and TAS (`consignee` / `CONS-4412` → loading-authorized-party). RightAngle remittance `APEX-PAYER` → payer; `BA-APEX` no map; no credit_party. Warehouse `1000123` no map. SAP `1000123` is two rows (sold-to + bill-to). Hunt stubs stay off both Genies. TABS skipped.

`10` lands `cv_term` / `cv_alias` / `cv_map` / `dim_customer` and
proves `cv_lookup('customer')` returns **two** IDs (`id:sold-to` and
`id:loading-authorized-party`). `cv_term` now has `ontology_iri`
(bind, not a replacement of `term_id`). Apex payer `MEASURE()` is still
**$115,960.80 / 8**. `customer_id` and `CONS-4412` are refused as
Unbilled grains. Catalog about-ID stays `#UnbilledState`.


`11` stands up a **second** Genie Agent titled `O2C vocabulary search`
(cv tables only; never a dollar). It does **not** update
`O2C certified KPIs`. Ask the search agent *What is customer?* and
expect both IDs. Ask the certified agent the same question and expect
a guess - that contrast is the point.

Details: `scripts/11_cv_search_genie.md`. Rule: Unbilled `MEASURE()`
may only slice on keys that map to `id:payer` / `id:sold-to` /
`id:ship-to`.

