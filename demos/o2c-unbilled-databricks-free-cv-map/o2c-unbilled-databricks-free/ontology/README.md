# Meaning sidecar (demo, unsigned)

## What this is

Thin Turtle that names the O2C terms this pack already uses in English:
Customer Account, Sold-to, Bill-to, Payer, Ship-to, Site, Loading-Authorized Party, Credit Account,
Obligation, Unbilled (a **state**), and Customer grain.

CV bind (`cv_term.term_id` → class IRI; do not replace `term_id`):
`id:payer` → `#Payer`; `id:sold-to` → `#SoldTo`; `id:bill-to` → `#BillTo`;
`id:ship-to` → `#ShipTo` (not `#Site`); `id:loading-authorized-party` → `#LoadingAuthorizedParty`.

It is **meaning**. It agrees with the Metric View comments. It is not
the Metric View.

File: `ontology/o2c-meaning.ttl`. Prefix `o2c:` →
`https://example.org/domain-ontology-kpi/o2c#`.

## What this is not

- Not a formula. No `gallons_net * contract_price`. No SQL.
- Not a compiler. Databricks does not read this folder.
- Not SHACL. No shapes.
- Not a triple store. No SPARQL endpoint. No GraphDB / Jena load.
- Not Neo4j. Neo4j is a serving projection, not meaning SoT.
- Not G3/G4 signed. These IRIs are demo-only, replaceable by the
  Ontologist.

## C-10 one-liner

Ontology = meaning. Store catalog + this pack's Metric View = certified
formula for **this** demo. They agree. They are not one object.

## How the Metric View points here

`sql/03_metric_view.sql` header comments point at
`ontology/o2c-meaning.ttl`. The pack dialect is YAML **0.1** (fields +
measures only) in `03`, `scripts/04_metric_view.py`, and
`sql/99_full_load.generated.sql`. Version 0.1 does **not** embed these
IRIs or field comments. Do not claim it does. Unbilled is typed here
as a **state of an Obligation** (`o2c:UnbilledState`), not a KPI class.

The Store catalog (`dim_kpi_metadata`) carries `formula_pointer` as
the measure name and `ontology_iri` at this sidecar: Unbilled →
`#UnbilledState`; the two delivered KPIs → `#Obligation`.
`formula_object` is the view. We do not add a `#DeliveredTicket` class.

## Parked (Ontologist)

Full OWL (imports, reasoner, competency questions), SHACL shapes, and a
triple store are parked. This file is a teaching sidecar so the demo
does not pretend the Metric View is the ontology.
