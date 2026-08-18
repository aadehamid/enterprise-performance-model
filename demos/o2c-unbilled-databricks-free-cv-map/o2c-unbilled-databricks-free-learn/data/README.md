# Data files - seed CSVs (not answers)

Small Gulf Coast O2C seeds (19 BOL tickets). Same party / product /
terminal shape as demo 1 (`demos/o2c-unbilled-semantic-layer/`), cut
down for a Free-edition **2X-Small** SQL warehouse.

These files are the **seed**. They are not the fact, not the Metric
View, and not the formula. You still have to land them and write
`fct_unbilled` yourself (see `LEARN.md` exercises 3–4).

Do **not** wget these from a notebook: Free outbound internet is
restricted. Upload via Catalog Explorer into the Unity Catalog volume
you create in `sql/01_land.sql`, or land a Lakebase replica (exercise 2).

As-of date used by the fact you will write: **2026-08-01**.

| File | What it is | Rows |
| --- | --- | ---: |
| `parties.csv` | Legal / operating parties (payer, sold-to, bill-to) | 8 |
| `party_roles.csv` | Role codes on those parties (`payer` / `sold_to` / `bill_to`) | 10 |
| `products.csv` | RBOB, ULSD, Jet-A. Contract price ≠ list price | 3 |
| `terminals.csv` | Sites / ship-to locations (HSC, DAL, BMT). Ship-to is a **terminal**, not a customer role | 3 |
| `tickets.csv` | BOL lifts (delivered + quality-hold). Ticket grain | 19 |
| `invoices.csv` | Invoices billed to the **payer**. Includes one post-as-of posted invoice and one draft | 6 |
| `invoice_lines.csv` | Invoice ↔ ticket. One weekly invoice can cover more than one sold-to | 6 |

## Expected volume path after you create the volume

```
/Volumes/{{catalog}}/{{schema}}/landing/<filename>.csv
```

Defaults: `{{catalog}}` = `workspace`, `{{schema}}` = `o2c_unbilled`.
If your workspace catalog is not literally named `workspace`, use the
name shown under **Catalog** in the sidebar.

Upload **all seven** CSVs into that `landing` volume (flat - no
subfolders). Filenames must match exactly.

## What "landed" looks like

`raw_*` counts: **8 / 10 / 3 / 3 / 19 / 6 / 6**.

## Certified population (you build this in `sql/02_facts.sql`)

A ticket is unbilled when:

1. `status = delivered`
2. no **posted** invoice line with `invoice_date <= 2026-08-01`
3. `unbilled_usd = gallons_net * contract_price_usd`

Quality-hold tickets are never billed and never unbilled.

If your fact is right you should see **12 unbilled tickets** and
**$179,934.00**. That check is in `LEARN.md` exercise 4. The SQL is
not in this folder.

## Hint if the land step is stuck

Complete pack: `../o2c-unbilled-databricks-free/sql/01_land.sql` and
`../o2c-unbilled-databricks-free/data/README.md`.

---

## Sidecar (not a ticket rename; not in Act 0 TABLES)

Hunt stubs carry a `system_name` column (SAP / Salesforce / TAS /
Warehouse / RightAngle) matching `cv_map.local_system`. `tickets.csv` /
`raw_tickets` do not - the hunt SELECT labels them Demo2.

These eight files are seeds so you can `DESCRIBE` / `SELECT` them (or
land them). They are **not** the hunt answer. They are **not** restaged
through Lakebase. They are **not** in Act 0 `TABLES`. `tickets.csv` is
unchanged (no `customer_id` column).

| File | What it is | Rows |
| --- | --- | ---: |
| `cv_term.csv` | Preferred label + scope + stable `term_id` + `ontology_iri` bind (not a replacement) | 5 |
| `cv_alias.csv` | Aliases. `customer` is on **both** Sold-To and Loading-Authorized Party | 22 |
| `cv_map.csv` | Live Demo 2 keys + SAP/TAS/Warehouse/Salesforce/RightAngle teaching rows. Empty `term_id` = no map | 22 |
| `dim_customer.csv` | Tiny warehouse sidecar (`customer_id = 1000123`). Not a certified Unbilled grain | 1 |
| `sap_partner.csv` | Thin SAP partner-function stub (same digits in `sold_to` and `bill_to`) | 1 |
| `tas_lift.csv` | Thin TAS stub (`consignee` = `CONS-4412` → Loading-Authorized Party) | 1 |
| `sf_account.csv` | Thin Salesforce stub (`account_id` = `SF-APEX`, no map). No `customer_id` column | 1 |
| `ra_business_associate.csv` | Thin RightAngle BA stub (`BA-APEX` no map; remittance → Payer; no credit_party) | 1 |

Salesforce is `sf_account.account_id` / `SF-APEX` only. No `customer_id`
column. No `crm_account`. No `lift_authorization`.

RightAngle: remittance stays; no `credit_party`. TAS `consignee`
`CONS-4412` → Loading-Authorized Party. Warehouse `1000123` has no map.
SAP `1000123` is two map rows (sold-to and bill-to).

**Hint.** After you have tried: complete pack `scripts/10_cv_map.py` and
`scripts/12_cv_hunt.py`. Peek. Do not copy blindly. Do not restage
through Lakebase. Not in Act 0 TABLES.
