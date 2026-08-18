# Genie Agent - O2C vocabulary search (second agent)

Demo **2** / Track B. Official name is **Genie Agent** (was Genie Space).
Search only. Preferred label + stable ID. **Never a dollar.**

This is **not** the certified KPI agent. The certified agent stays
titled `O2C certified KPIs` and stays on the three Metric Views /
`MEASURE()` only. `07_genie.py` is not changed. Do **not** attach
`cv_*` to that agent.

Do **not** put a workspace URL, PAT, or warehouse id in this file.

---

## What this agent is

A second Genie Agent that answers “what does this party word or code
mean?” It reads the controlled vocabulary and the live-key map:

| Object | Job |
| --- | --- |
| `cv_term` | preferred label + scope note + stable `term_id` + optional `ontology_iri` bind (not a replacement) |
| `cv_alias` | aliases (`customer` is on **two** IDs) |
| `cv_map` | live keys (`APEX-PAYER`, `CONS-4412`, SAP digits) → `term_id` |
| `cv_lookup(q)` | table function (or the documented JOIN if Free refuses `CREATE FUNCTION`) |

It does **not** attach Metric Views, gold, `fct_*`, `raw_*`,
`dim_customer`, `sap_partner`, `sf_account`, `tas_lift`,
`ra_business_associate`, or `dim_kpi_metadata`. Hunt stubs stay
off both Genies.

---

## Agent (find by title only)

| Field | Value |
| --- | --- |
| Title | `O2C vocabulary search` |
| Description | search only. Preferred label + stable ID. Never a dollar. |
| Data sources | `cv_term`, `cv_alias`, `cv_map` (and `cv_lookup` if the API keeps a function identifier) |
| Warehouse | Serverless Starter Warehouse (id stays in local `.env`) |
| Parent folder | the workspace user folder (API `parent_path`) |

`scripts/11_cv_search_genie.py` finds this title only. If
`O2C certified KPIs` appears in `list_spaces`, it is listed and
**left alone**.

---

## Instructions (SKILL.md shape)

The live Text box is `general_instruction_text()` in
`11_cv_search_genie.py` (`name: o2c-vocabulary-search`).

- **When to use** - the user asks what a party word or code means
  (customer, RG, APEX-PAYER, CONS-4412, payer, sold-to, …).
- **Do** - run `cv_lookup` / join term+alias+map; return every
  matching preferred_label + `term_id`; if two hits, return both and
  say the word is overloaded.
- **Don't** - never `MEASURE()`, never a dollar, never attach or
  query `unbilled_usd` / gold / fct / raw, never pick one meaning of
  “customer” and hide the other, never say a certified Unbilled number.

Example SQL (the fix seat), at least:

```sql
SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('customer');
SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('RG');
SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('APEX-PAYER');
SELECT term_id, preferred_label FROM workspace.o2c_unbilled.cv_lookup('CONS-4412');
```

If `CREATE FUNCTION` was refused on Free, the script attaches the
equivalent JOIN (still two IDs for `customer`).

The Genie API on this Free workspace will **not** attach `cv_lookup` as
a table (`Table '…cv_lookup' does not exist`) and rejects a
`data_sources.functions` field (`Unknown field 'functions'`). Tables +
example SQL that call `cv_lookup('…')` are enough - live ask used that
SQL and returned both IDs.

Sample questions match those four.

---

## Live ask

After create/update the script asks **What is customer?**

Pass = the SQL/blob contains both `id:sold-to` and
`id:loading-authorized-party` (or both preferred labels) and does
**not** contain `MEASURE(` or a dollar amount like 179934 / 115960.

Fail if it picks only one meaning.

It also live-asks the **certified** agent the same question,
read-only, as the contrast. A guess is OK. Fail only if that agent
now has `cv_*` attached.

---

## Recreate / re-ask from the Mac

Run **after** `scripts/10_cv_map.py` so the cv tables (and lookup)
exist.

```bash
uv run python scripts/11_cv_search_genie.py
```

Token stays in `.env`. The script never prints the token, host, or
warehouse id.

---

## If you must use the UI

Official create / manage page:
[Create and manage a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up)

Official API:
[Use the Genie Agents API](https://docs.databricks.com/aws/en/genie/conversation-api)

1. Sidebar → **Genie Agents** → **New**
2. Title `O2C vocabulary search`
3. Attach `cv_term`, `cv_alias`, `cv_map` (and `cv_lookup` if listed).
   Do **not** attach Metric Views, gold, fct, raw, `dim_customer`,
   `sap_partner`, `sf_account`, `tas_lift`, `ra_business_associate`,
   or `dim_kpi_metadata`. Hunt stubs stay off both Genies.
4. Paste the instruction from `general_instruction_text()` (or the
   SKILL.md shape above).
5. Add the four example SQLs.
6. Ask *What is customer?* Confirm both IDs and no dollar.

The certified Genie stays Metric View / `MEASURE()` only. Do not
rename it. Do not attach `cv_*` to it.

---

## Why two agents

See `THE-PROBLEM.md`. Raw SQL still returns `customer_id = 1000123`.
Unbilled `MEASURE()` may only slice on keys that map to Payer /
Sold-To / Ship-To. Vocabulary search returns the two IDs and never
a dollar. Certified Genie will still guess “customer” - that is the
contrast, not a bug in this act.
