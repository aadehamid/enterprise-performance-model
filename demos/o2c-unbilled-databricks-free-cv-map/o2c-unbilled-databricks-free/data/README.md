# Data files - what to upload

Small Gulf Coast O2C seeds (19 BOL tickets). Same party / product / terminal
shape as Track A (`demos/o2c-unbilled-semantic-layer/`), cut down for a
Free-edition **2X-Small** SQL warehouse. Do **not** wget these from a
notebook: Free outbound internet is restricted. Preferred: skip upload and run `sql/99_full_load.generated.sql`
(VALUES embed of these files). Alternate: upload via the workspace UI
into the Unity Catalog volume created by `sql/01_land.sql`.

As-of date used by `sql/02_facts.sql`: **2026-08-01**.

| File | What it is | Rows |
| --- | --- | ---: |
| `parties.csv` | Legal / operating parties (payer, sold-to, bill-to) | 8 |
| `party_roles.csv` | Role codes on those parties (`payer` / `sold_to` / `bill_to`) | 10 |
| `products.csv` | RBOB, ULSD, Jet-A. Contract price ≠ list price | 3 |
| `terminals.csv` | Sites / ship-to locations (HSC, DAL, BMT). Ship-to is a **terminal**, not a customer role | 3 |
| `tickets.csv` | BOL lifts (delivered + quality-hold). Ticket grain | 19 |
| `invoices.csv` | Invoices billed to the **payer**. Includes one post-as-of posted invoice and one draft | 6 |
| `invoice_lines.csv` | Invoice ↔ ticket. Apex weekly invoice `INV-2026-0001` covers Houston **and** Dallas tickets | 6 |

## Expected volume path after `01_land.sql`

```
/Volumes/{{catalog}}/{{schema}}/landing/<filename>.csv
```

Defaults: `{{catalog}}` = `workspace`, `{{schema}}` = `o2c_unbilled`.
If your workspace catalog is not literally named `workspace`, use the name
shown under **Catalog** in the sidebar.

Upload **all seven** CSVs into that `landing` volume (flat - no subfolders).

## Certified unbilled population (built in `02_facts.sql`, not here)

A ticket is unbilled when:

1. `status = delivered`
2. no **posted** invoice line with `invoice_date <= 2026-08-01`
3. `unbilled_usd = gallons_net * contract_price_usd`

Quality-hold tickets are never billed and never unbilled.

That yields **12 unbilled tickets** and a grand total of **$179,934.00**.
`INV-2026-0005` (2026-08-03) covers `BOL-2026-0104` but is after as-of, so
that ticket stays unbilled. `INV-2026-0006` is `draft` and does not count.

## Expected certified totals (from these seeds)

Computed locally from the CSVs. Also embedded in `sql/99_full_load.generated.sql` (no upload required).

| Grain | Key | Unbilled USD | Tickets |
| --- | --- | ---: | ---: |
| sold-to | Apex Fuels Houston Rack | 79,362.40 | 5 |
| sold-to | Apex Fuels Dallas Dealer | 36,598.40 | 3 |
| sold-to | Metro Lubes Beaumont | 37,454.40 | 2 |
| sold-to | Gulf Coast Aviation Inc | 26,518.80 | 2 |
| payer | Apex Fuels LLC | 115,960.80 | 8 |
| payer | Metro Lubricants | 37,454.40 | 2 |
| payer | Gulf Coast Aviation Inc | 26,518.80 | 2 |
| site | HSC (Houston Ship Channel) | 97,145.20 | 6 |
| site | DAL (Dallas) | 45,334.40 | 4 |
| site | BMT (Beaumont) | 37,454.40 | 2 |
| all | grand total | **179,934.00** | **12** |

Apex Fuels LLC (payer) **equals** Houston Rack + Dallas Dealer. Those are
the same eight tickets. Adding the Apex payer line to the two Apex sold-to
lines double-counts. That is the grain lesson, not a data-quality bug.

`BOL-2026-0105` is a Houston sold-to lift at Dallas - one cross-terminal
row so sold-to ↔ site is not fake-clean.

---

## Sidecar (not a ticket rename; not in Act 0 TABLES)

Hunt stubs carry a `system_name` column (SAP / Salesforce / TAS / Warehouse / RightAngle) matching `cv_map.local_system`. `tickets.csv` / `raw_tickets` do not - the hunt SELECT labels them Demo2.

CV files are landed by `scripts/10_cv_map.py` (`cv_*` / `dim_customer`); hunt stubs by `scripts/12_cv_hunt.py` (`sap_partner` / `tas_lift` / `sf_account` / `ra_business_associate`; may re-land `dim_customer`) into Unity Catalog
only. They are **not** added to `scripts/config.py` `TABLES` and are
**not** restaged through Lakebase. `tickets.csv` is unchanged (no
`customer_id` column).

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
column. No `crm_account`.

RightAngle: remittance stays; no `credit_party`. TAS `consignee`
`CONS-4412` → Loading-Authorized Party. Warehouse `1000123` has no map.
SAP `1000123` is two map rows (sold-to and bill-to). Hunt stubs stay
off both Genies.
