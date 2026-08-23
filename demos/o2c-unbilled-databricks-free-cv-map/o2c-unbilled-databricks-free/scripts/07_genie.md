# Genie Agent - ad hoc KPI path for all three approved views

Demo **2** / Track B. Official name is **Genie Agent** (was Genie Space).
Not MetricFlow. Not Track A. Not a second formula.

One agent answers ad hoc questions against **all three** approved
Metric Views. Live create/update + conversation on Databricks Free
Edition via `databricks-sdk` (`w.genie.create_space` /
`update_space` + `start_conversation_and_wait`). This is **not**
UI-only on Free.

Do **not** put a workspace URL, PAT, or warehouse id in this file.

---

## What Genie is in this demo

Genie Agent is the **ad hoc KPI path**. Business users ask grain
questions in natural language. Each approved Metric View compiles
its own formula. Genie must **consume** the matching view with
`MEASURE()`. It must **not** author a second formula, re-encode a
valuation, or Export-to-metric-view.

| Job | Who does it |
| --- | --- |
| Population / compiler source (Unbilled) | `fct_unbilled` (ticket gate + valuation; not gold) |
| Compiler (SUM/GROUP BY / joins / multiply) | The three Metric Views (`CREATE VIEW … WITH METRICS` / `MEASURE()`) |
| Ad hoc grain questions (all three KPIs) | **This Genie Agent** (consumes MEASURE(); no second SUM) |
| Published snapshot | Gold `gold_kpi_value` FROM each view's `MEASURE()` |
| Meaning (sold-to ≠ payer ≠ site) | Ontology sidecar - not Genie |

---

## Agent (find by title only)

| Field | Value |
| --- | --- |
| Title | `O2C certified KPIs` (find by this title only; no space id) |
| Previous title | `O2C Unbilled (certified)` - script **updates** that agent in place (title + serialized_space) so this workspace still has one agent |
| Data sources | the three Metric Views below **plus** `dim_kpi_metadata`. Do **not** attach `fct_unbilled`, `gold_kpi_value`, or `raw_*` |
| Warehouse | Serverless Starter Warehouse (id stays in local `.env`) |
| Parent folder | the workspace user folder (API `parent_path`) |

The create/update payload sends `data_sources.metric_views` with all
three identifiers and `data_sources.tables` with `dim_kpi_metadata`. GET `serialized_space` may store those same
identifiers under `data_sources.tables` (server-normalized). The
identifiers are still the Metric Views, **not** `fct_unbilled`.
Conversation SQL must use `MEASURE()` on the matching view - that
is the pass condition.

---

## The three approved sources

| View | Published measure | Grains (unsliced = enterprise) | Unsliced (as-of 2026-08-01) |
| --- | --- | --- | --- |
| `workspace.o2c_unbilled.unbilled_usd` | `unbilled_usd` | enterprise \| payer \| sold_to \| site | **$179,934.00 / 12** |
| `workspace.o2c_unbilled.contract_vs_list_usd` | `delivered_contract_usd` | enterprise \| sold_to \| product | **$110,064.00 / 7** |
| `workspace.o2c_unbilled.temp_adjusted_delivered_usd` | `temp_adjusted_usd` | enterprise \| product \| site | **$256,066.39 / 17** |

Other measures on `contract_vs_list_usd` (list, hot_rack, rbob, …)
and on `temp_adjusted_delivered_usd` are query-only. Still
`MEASURE()`. Never a generic "customer" grain.

---

## Forbidden: Export-to-metric-view

Official UI action (kebab menu → **Export to metric view**) would
**mint a second formula** from Genie context. Do **not** use it.
You already authored the three views (`sql/03_metric_view.sql`,
`sql/06_complex_metric.sql`, `sql/07_temp_adjusted.sql`). Genie
consumes those views. It does not replace them.

Official create / manage page (updated 2026-07-30):
[Create and manage a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up)

Official API (updated 2026-08-13):
[Use the Genie Agents API](https://docs.databricks.com/aws/en/genie/conversation-api)

---

## Instructions the agent is given

- Look up `dim_kpi_metadata.status` first. `MEASURE()` only when status = `approved`. If `drifted`, `proposed`, or `archived`: say not approved (status=<status>) and do not give a number.
- Answer only via `MEASURE()` on the matching Metric View (when approved)
- Unbilled USD → `unbilled_usd` (enterprise \| payer \| sold_to \| site; unsliced = enterprise). Never a generic "customer"
- Contract vs list / delivered contract USD → `contract_vs_list_usd`, published measure `delivered_contract_usd` (enterprise \| sold_to \| product; unsliced = enterprise). Other measures on that view are query-only, still `MEASURE()`
- Temp-adjusted / temperature-adjusted delivered USD → `temp_adjusted_delivered_usd`, published measure `temp_adjusted_usd` (enterprise \| product \| site; unsliced = enterprise)
- If the question does not name a KPI, ask which one (Unbilled / contract-vs-list / temp-adjusted). Do not guess between contract-vs-list and temp-adjusted on a vague "delivered USD."
- Do not invent a second formula
- Do not query `fct_unbilled` or `raw_*`
- Do not Export-to-metric-view
- As-of is **2026-08-01**
- Never say "customer". Say payer, sold-to, or site
- If the question names a grain (payer, sold_to, site, product), GROUP BY only that grain. Do not GROUP BY ALL extra dimensions unless the user asked for a breakdown
- Filter the named party with equality on that role only (example: `WHERE payer = 'Apex Fuels LLC'`). Do not `ILIKE '%name%'` OR across payer / sold_to / site
- A sold-to lifting at another site is a real cross-terminal ticket, not a data error. Do not call sold-to a "customer location"
- If they asked for a payer total, lead with the payer number. Extra product/site charts only if they asked

The live Text box is the SKILL.md-shaped string from `general_instruction_text()` in `07_genie.py`. Do not duplicate a second conflicting instruction.

Example SQL attached to the agent is catalog status SELECT first, then
`MEASURE()` only when status = approved. No `gallons_net * contract_price` copy.

---

## Suggested questions

1. *What is total unbilled USD as of 2026-08-01?*
2. *What is unbilled USD by payer?*
3. *What is delivered contract USD as of 2026-08-01?*
4. *What is delivered contract USD by product?*
5. *What is temp-adjusted delivered USD as of 2026-08-01?*
6. *What is temp-adjusted USD by site?*

Also attached: unbilled by sold_to / site; contract by sold_to;
temp-adjusted by product.

Filtered-grain examples (GROUP BY the named grain only; equality on that role):

7. *What is unbilled USD for payer Apex Fuels LLC?*
   `SELECT kpi_id, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'` then (only if approved) `SELECT payer, MEASURE(unbilled_usd) AS unbilled_usd, MEASURE(unbilled_ticket_count) AS tickets FROM {unbilled} WHERE payer = 'Apex Fuels LLC' GROUP BY payer`
8. *What is unbilled USD by sold_to for Apex Fuels Houston Rack?*
   `SELECT kpi_id, status FROM {catalog} WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'` then (only if approved) `SELECT sold_to, MEASURE(unbilled_usd) AS unbilled_usd FROM {unbilled} WHERE sold_to = 'Apex Fuels Houston Rack' GROUP BY sold_to`

## Expected numbers (must match `MEASURE()`)

```
unbilled unsliced              $179,934.00 / 12 tickets
delivered contract unsliced    $110,064.00 / 7 tickets
temp-adjusted unsliced         $256,066.39 / 17 tickets
```

Locked Unbilled catalog-status facts (as-of 2026-08-01):
- approved → **$179,934.00 / 12**
- drifted → refused, no number (not approved, status=drifted)
- re-approve → **$179,934.00 / 12**

`scripts/07_genie.py` live-asks the three unsliced questions after
create/update. Pass = `MEASURE()` on the right view, not fct/raw,
and the numbers above. If Genie ever answers from `fct_unbilled`,
`raw_tickets`, or re-encodes `gallons_net * contract_price`, that
is a **fail**, even if the dollar figure matches.

Live conversation test 2026-08-14 (CT): all three unsliced questions
passed. Generated SQL used `MEASURE()` on the matching view.

```sql
SELECT kpi_id, status
FROM `workspace`.`o2c_unbilled`.`dim_kpi_metadata`
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD';
-- only if status = approved:
SELECT MEASURE(`unbilled_usd`) AS `unbilled_usd`,
       MEASURE(`unbilled_ticket_count`) AS `tickets`
FROM `workspace`.`o2c_unbilled`.`unbilled_usd`
-- $179,934.00 / 12

SELECT kpi_id, status
FROM `workspace`.`o2c_unbilled`.`dim_kpi_metadata`
WHERE kpi_id = 'KPI-O2C-CONTRACT-VS-LIST-USD';
-- only if status = approved:
SELECT MEASURE(`delivered_contract_usd`) AS `delivered_contract_usd`,
       MEASURE(`delivered_ticket_count`) AS `tickets`
FROM `workspace`.`o2c_unbilled`.`contract_vs_list_usd`
GROUP BY ALL
-- $110,064.00 / 7

SELECT kpi_id, status
FROM `workspace`.`o2c_unbilled`.`dim_kpi_metadata`
WHERE kpi_id = 'KPI-O2C-TEMP-ADJUSTED-USD';
-- only if status = approved:
SELECT MEASURE(`temp_adjusted_usd`) AS `temp_adjusted_usd`,
       MEASURE(`delivered_ticket_count`) AS `tickets`
FROM `workspace`.`o2c_unbilled`.`temp_adjusted_delivered_usd`
-- $256,066.39 / 17
```

Write payload must send `data_sources.metric_views` **sorted by
identifier** (`update_space` rejects an unsorted list).

---

## Recreate / re-ask from the Mac

Run **after** `08_complex_metric.py` and `09_temp_adjusted.py` so all
three views exist. A clean 01→09 creates the agent only once those
views are compiled.

```bash
uv run python scripts/07_genie.py
```

Finds `O2C certified KPIs` by title (or updates the old
`O2C Unbilled (certified)` agent in place), then asks the three
unsliced questions. Token stays in `.env`. The script never prints
the token, host, or warehouse id.

---

## If you must use the UI (not required on this Free workspace)

API create/update worked here. If a later Free workspace rejects
`POST /api/2.0/genie/spaces`, official UI steps from
[Create and manage a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up):

1. Sidebar → **Genie Agents**
2. Find `O2C certified KPIs` (or the leftover `O2C Unbilled (certified)` and rename it). Or **New**
3. Choose data sources - all three Metric Views above. Do **not** add `fct_unbilled` or `raw_*`
4. **Create** / save
5. Configure → Settings: title `O2C certified KPIs`; default warehouse = Serverless Starter Warehouse
6. Add the instructions and sample questions above
7. Ask the six questions. Confirm numbers match `MEASURE()`
8. Do **not** kebab → Export to metric view

Do not invent extra click-path. Those are the official steps.
