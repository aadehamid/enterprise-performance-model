# Walkthrough — Unbilled USD consumption semantic layer

This file is the teaching companion to `README.md`. Run `./scripts/demo.sh`
first, then read this with the numbers in front of you.

---

## 1. What a semantic layer is

A semantic layer is **not** a dashboard and **not** a warehouse table.

```
YAML (entities, dimensions, measures, metrics)
        ↓  compiler (MetricFlow)
SQL that hits the warehouse (here: DuckDB)
        ↓
The same number in every consumer
```

The **certified population and formula** are sealed in the dbt fact
(`int_ticket_billing` + `fct_unbilled`): delivered, no posted invoice as
of 2026-08-01, quality-hold never unbilled, `gallons_net * contract_price`.
Delete `semantic_models.yml` and Act 1 still works. That is the production
pattern.

The YAML names the metric, the dimensions, and which column to sum. The
compiler writes the `SELECT` / `GROUP BY` SQL. It does **not** re-encode
the unbilled rule. `--explain` is `SUM(unbilled_usd) FROM fct_unbilled`
on purpose.

Act 1 A/B already query that fact (two group-bys, same tickets). Act 3
is the **same number** through `mf query`. Report C stays different
because it never used the fact.

---

## 2. Why dbt is here

dbt Core is free. In this demo it does two jobs:

1. **Build tables** from CSV seeds (`stg_*` → dims/facts → `fct_unbilled`).
2. **Host the YAML** that MetricFlow compiles (`models/semantic_models.yml`).

We use the **legacy standalone spec**: top-level `semantic_models:` and
`metrics:` keys, not the dbt 1.12 embedded `semantic_model:` block under
`models:`. The 1.8–1.11 line is the one this YAML is written for.

`dbt parse` writes `target/semantic_manifest.json`. `mf` reads that
manifest plus the materialized DuckDB tables.

---

## 3. Why DuckDB

DuckDB is a warehouse stand-in that lives in one file (`o2c.duckdb`).
No Snowflake account, no Docker, no network. MetricFlow has a native
DuckDB SQL renderer. The same project pattern (MotherDuck cookbook)
promotes to MotherDuck by changing the dbt target; this zip stays local.

---

## 4. Party roles vs terminals

Downstream O2C overloads the word "customer".

| Role | Who in this demo | What it is for |
| --- | --- | --- |
| **Payer** | Apex Fuels LLC; Metro Lubricants; Gulf Coast Aviation Inc | Who is invoiced. Credit and cash live here. |
| **Sold-to** | Apex Houston Rack; Apex Dallas Dealer; Metro Lubes Beaumont; GCA | Who is entitled to lift under the contract. |
| **Bill-to** | Apex AP; Metro Shared Services; GCA | Who receives the invoice document. |
| **Ship-to** | **Not a party.** HSC / DAL / BMT | A **terminal** (location). |

Gulf Coast Aviation is payer *and* sold-to (same org). Apex is not: one
payer, two sold-tos. An Apex invoice can cover Houston *and* Dallas
tickets in the same week — billed to Apex Fuels LLC, not to the rack desk.

If you default every KPI to "customer = sold-to", credit and unbilled
lie. If you default every KPI to "customer = payer", dealer performance
lies. The certified metric does not pick a customer for you. **You
choose the group-by.** The formula stays still.

---

## 5. The certified rule

As of **2026-08-01**:

- `status = delivered`
- no posted invoice line with `invoice_date <= 2026-08-01`
- `unbilled_usd = gallons_net * contract_price_usd`
- quality-hold tickets are **never** billed and **never** unbilled
  (they are not billable until released)

**Fact grain** (`fct_unbilled`): one row per BOL ticket. Easy to audit.

**Default published grain** (`gold_kpi_unbilled`): sold-to + terminal + day.
Product is a slice dimension, not part of the default published grain.

`dim_kpi_metadata` has **one row**. `formula_pointer = unbilled_usd`.
That pointer is the MetricFlow metric name.

---

## 6. Why Report A and Report B both say "customer" and lie

Both reports are labeled **Unbilled USD**. Both use the certified ticket
set. Their **grand totals match**:

```
Report A (sold-to): $6,049,649.77   4 customer rows
Report B (payer):   $6,049,649.77   3 customer rows
```

They still fight, because someone will compare *rows*:

| Report A "customer" | USD | Report B "customer" | USD |
| --- | ---: | --- | ---: |
| Apex Fuels Houston Rack | 2,726,475.31 | Apex Fuels LLC | 4,095,877.44 |
| Apex Fuels Dallas Dealer | 1,369,402.13 | | |
| Metro Lubes Beaumont | 1,134,397.03 | Metro Lubricants | 1,134,397.03 |
| Gulf Coast Aviation Inc | 819,375.30 | Gulf Coast Aviation Inc | 819,375.30 |

Apex Fuels LLC **equals** Houston + Dallas. Those are the same 296 tickets
rolled to the payer. If a slide adds the Apex payer line to the two Apex
sold-to lines, Unbilled USD is double-counted.

Report B has fewer rows than Report A **because two sold-tos roll to one
payer**. That is the grain lesson, not a data-quality bug.

Aviation matches on both reports — same org, both roles.

Metro looks like a rename (Beaumont vs Lubricants) until you remember
Report C will put Metro on the **payer** label while Apex stays on
**sold-to** labels. That is role-mixing.

---

## 7. Report C — the sloppy twin

Report C is also titled Unbilled USD. It is a different number:

```
Report C: $7,393,499.19
```

What it did wrong, on purpose:

1. **Quantity basis** — `gallons_gross` (ambient) instead of `gallons_net` (60°F).
2. **Price** — list price instead of contract price.
3. **Population** — includes `quality_hold` tickets (not billable).
4. **Customer** — Apex rows use sold-to names; Metro rows use the payer name.

That is how two workbooks with the same title drift. The semantic layer
does not "average" them. It **replaces** them.

---

## 8. Metadata is 1 row; grain lives on the fact

Act 2 prints `dim_kpi_metadata` (one certified definition) and joins it
to `gold_kpi_unbilled` (195 rows at sold-to + terminal + day; 446 tickets
underneath).

Houston vs Dallas is the same KPI, same `formula_pointer`, different
fact rows:

| sold-to | terminal | unbilled USD | tickets |
| --- | --- | ---: | ---: |
| Apex Fuels Houston Rack | HSC | 2,666,499.54 | 190 |
| Apex Fuels Houston Rack | DAL / BMT | (cross-terminal exceptions) | 4 |
| Apex Fuels Dallas Dealer | DAL | 1,324,859.69 | 99 |
| Apex Fuels Dallas Dealer | HSC | (exceptions) | 3 |

A catalog row does not explode into one row per site. The fact does.
If you put grain on the metadata table you will fight this every quarter.

---

## 9. Store vs semantic layer

| | KPI Store (not this demo) | This demo |
| --- | --- | --- |
| Job | Certify the definition, owner, status, grain rule | **Compute** the certified formula on demand |
| Artifact | Registry / metadata (we only stub `dim_kpi_metadata`) | MetricFlow YAML + `fct_unbilled` |
| Consumer | "What is Unbilled USD and who owns it?" | "Give me Unbilled USD by payer" |

A Store would certify. **This demo is the consumption layer.** The
formula is in the fact; the YAML + compiler are how consumers ask for
it without writing a second SQL. `dim_kpi_metadata.formula_pointer`
joins the one certified name to the one metric. Act 1 calls the fact.
Act 3 calls the metric, which reads the same fact.

Do not grow `dim_kpi_metadata` into a catalog here.

---

## 10. How MetricFlow is wired

`models/semantic_models.yml` (legacy standalone spec):

- **semantic model** `unbilled_tickets` on `ref('fct_unbilled')`
- **primary entity** `ticket` (`ticket_id`)
- **foreign entities** `sold_to_party`, `payer_party`, `terminal_loc`, `product_sku`
- **time** `delivery_date` (day) — default `agg_time_dimension`
- **categorical dimensions** `sold_to`, `payer`, `terminal`, `product`, `status`
  (names are distinct from entity names so they do not collide)
- **measures** `unbilled_usd_measure`, `unbilled_gallons_net_measure`, `ticket_count`
- **metrics** `unbilled_usd`, `unbilled_gallons_net`, `unbilled_ticket_count`

MetricFlow 0.209 exposes categorical dimensions as `ticket__sold_to`,
`ticket__payer`, `ticket__terminal` (primary entity + dimension). Time
slices are `metric_time__day`. That is why the CLI group-bys use those
names. `ticket__` is **compiler namespacing** of a dimension onto the
ticket-grained model. It is not a claim that sold-to is a child of ticket.

Time spine: `models/metricflow_time_spine.sql` (`generate_series` of
dates 2026-01-01 … 2026-08-31), declared in:

1. `dbt_project.yml` → `semantic-models.time-spine` (1.8/1.9 cookbook;
   unused warning on dbt 1.10 — kept for the documented pattern)
2. `semantic_models.yml` → `time_spines:`
3. `metricflow_time_spine.yml` → model-level `time_spine:` (what dbt 1.10
   actually reads)

`--explain` shows the compiled SQL. For the unsliced metric it is:

```sql
SELECT
  SUM(unbilled_usd) AS unbilled_usd
FROM "o2c"."main"."fct_unbilled" unbilled_tickets_src_10000
```

No second formula. Group-by only changes the `GROUP BY` list.

---

## 11. Data notes

- 1,200 BOL tickets, 2026-06-01 … 2026-07-31, generator seed **42**.
- Products: RBOB, ULSD, Jet-A. Contract price ≠ list price.
- ~6% quality-hold (never invoiced).
- ~39% of *delivered* tickets still unbilled as of 2026-08-01
  (random partial billing + 3–14 day invoice lag past as-of).
- Invoices billed to the **payer**. Apex weekly invoices can cover both
  sold-tos.
- A few cross-terminal lifts so the sold-to ↔ terminal join is not fake-clean.

`scripts/generate_data.py` rewrites `seeds/*.csv`. The zip already
includes those CSVs so you can `dbt seed` without reading the generator
first.


---

## 12. Ossie projection

The file you shared as "the semantic standard" is **Apache Ossie**
(Open Semantic Interchange). This zip includes a projection of the
certified metric at `osi/unbilled.ossie.yaml` (spec **0.1.1**).

| | MetricFlow YAML | Ossie file |
| --- | --- | --- |
| Path | `models/semantic_models.yml` | `osi/unbilled.ossie.yaml` |
| Job | Compile to SQL (`mf query`) | Portable interchange |
| Parsed by this demo? | Yes (`dbt parse` + `mf`) | **No** (needs dbt 1.12) |
| Formula SoT? | No — formula is in `fct_unbilled` | No — same fact, copied expression |

Ossie `relationships` are join paths, not OWL object properties. This
file is not an ontology. When we add ontology later, we will project
IRIs *into* Ossie, not import this YAML as OWL.
