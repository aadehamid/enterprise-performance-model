# The problem - “customer” is not one thing

When someone asks “what is unbilled for this customer?” they are not
asking one question. Across the systems that already feed this demo,
the same everyday word - and sometimes the same digits - names
different parties.

**Sold-to** is who the product is sold to. **Payer** is who settles
the invoice. **Bill-to** is who receives the invoice. **Ship-to** is
the terminal. Those four already disagree on a weekly close. Two more
party meanings sit next to those four:

- A **loading-authorized party** (`CONS-4412`) may lift at the rack.
  That is not a payer, not a sold-to, and not a site. Treating it as
  “the customer” on Unbilled is the wrong meaning.
- A warehouse **`customer_id`** (`1000123`) is overloaded. The same
  digits are a sold-to in one system and a bill-to in another. The
  warehouse key itself does not pick a role.

That is why a **controlled vocabulary** exists here: a preferred
label, a short list of aliases, a scope note, and a stable ID
(`id:payer`, `id:sold-to`, `id:ship-to`, …). A **map** then says
what a live key *is* (`APEX-PAYER` → Payer; `CONS-4412` →
Loading-Authorized Party; warehouse `1000123` → no map). The map
does not rewrite anyone’s SQL. It does not invent a new KPI.

The hunt is how those map rows were found - the work, not a second
catalog. Open the source tables (`raw_tickets`, `dim_customer`,
`sap_partner`, `tas_lift`, `sf_account`,
`ra_business_associate`); the table name is already a clue. Read the
party columns. Read the live values (`APEX-PAYER`, SAP `1000123` in
two columns, `CONS-4412`, ticket keys, warehouse `1000123`,
Salesforce `SF-APEX`, RightAngle `BA-APEX`). Then write the map as system + field + key.
Same digits `1000123` are two SAP map rows (sold-to and bill-to);
warehouse `customer_id` has no map. Salesforce `account_id` `SF-APEX` has no map (a relationship, not a role). `CONS-4412` is a TAS consignee / loading-authorized party, not a payer. RightAngle speaks Business
Associate / remittance - not SAP sold-to / bill-to / payer
columns (those names were not taken from ION). Remittance maps to the existing Payer id; the BA field itself has no map. Credit is not mapped (credit lives on the payer; it is not the payer). Stubs
exist so those sources can be opened. TABS is skipped (it would
invent a meaning or duplicate sold-to). Rack pricing is skipped (no
party field). No new KPI.

Three paths stay distinct on purpose:

1. **Raw SQL is honest.** `SELECT customer_id FROM dim_customer`
   still returns `1000123`. Tickets were not renamed. There is no
   interceptor. Analysts can still write the query they already have.
2. **The published Unbilled number may only slice on certified
   grains.** Unbilled `MEASURE()` groups on keys that map to Payer,
   Sold-To, or Ship-To. `customer_id` is not a dimension on that
   view. `CONS-4412` is not a payer. Join on those keys is not a
   certified grain.
3. **Two Genie agents sit side by side.** The certified agent
   answers dollars via `MEASURE()` on the Metric Views. Ask it
   “What is customer?” and it will still **guess** - it has no map.
   The vocabulary-search agent returns the two IDs for “customer”
   (Sold-To and Loading-Authorized Party) and never a dollar.

Unbilled remains a **state** of an obligation (delivered, not yet
invoiced). The catalog about-ID stays `UnbilledState`. This act does
not load an ontology and does not add a new KPI. It only makes the
overloaded word visible, and keeps the certified number on the
grains that actually mean Unbilled.

`term_id` is the join key (aliases and the map still point at it).
`ontology_iri` on `cv_term` binds that key to the meaning sidecar
(`#Payer`, `#SoldTo`, `#BillTo`, `#ShipTo`, `#LoadingAuthorizedParty`).
It does not replace `term_id`. All five term_ids bind; Loading-Authorized
Party is `#LoadingAuthorizedParty`. Catalog Unbilled bind stays
`#UnbilledState` - a different seat, not collapsed into a party class.
Ship-To is `#ShipTo`, not `#Site`. No new KPI.

Each hunt stub carries system_name (Demo2 / SAP / Salesforce / TAS / Warehouse / RightAngle) so DESCRIBE/SELECT shows which system it simulates. Tickets stay unlabeled on the table; the hunt SELECT labels them Demo2. cv_map.local_system uses the same names. The hunt is table name → column → live value → map (`system + field +
key` → `term_id`, or no map). Thin stubs (`sap_partner`,
`tas_lift`, warehouse `dim_customer`, `sf_account`,
`ra_business_associate`) exist so those sources can be opened;
`raw_tickets` is already landed. The map is the result. TABS is
skipped - a TABS stub would invent a system-specific meaning or just
duplicate an existing sold-to key. Rack pricing is skipped. No new
KPI.
