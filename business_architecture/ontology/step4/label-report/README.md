# Historical-label disposition report — v1.1 (APPROVED)

Source: committed `step2-identity-map.json` (prior_name /
scoped_historical_alias overlays) cross-checked against the emitted
`step3-taxonomy.ttl` (`skos:prefLabel` / `skos:altLabel`).

Supersedes v1: adds the `MigrationOnly` disposition; corrects rows
Step 3d deliberately excluded from active aliases; adds `searchable`,
`scope_context`, and `step3d_precedent` columns; runs normalized
collision validation on every add candidate.

## Universe reconciliation

The Step 3d naming queue held 92 entries; **84 renames landed** (the
remainder were keep-decisions, metadata repairs, and definition-only
rows). This report covers the **90 historical labels that actually
exist**: 84 `prior_name` + 6 `scoped_historical_alias`.

Conservation check passed: all 84 TTL `prefLabel`s match the identity
map's new names; zero TTL prefLabels still show an old name.

## Success condition

**90 records, 90 governed dispositions, zero undispositioned** — not
"every historic label becomes an ontology alias."

## Dispositions (v1.1)

| Disposition | Rows | Searchable | Meaning |
|---|---|---|---|
| `RetainAsAltLabel` | 68 | yes | Already emitted; no action |
| `AddAsAltLabel` | 5 | yes | Validator-clean; safe to emit |
| `MigrationOnly` | 11 | no | Preserved in identity map / `core:priorPreferredLabel`; excluded from alias search |
| `RetireAsAmbiguous` | 6 | no | Bare `Define KPI Framework`; restoring it would recreate the 6-way collision |

**MigrationOnly** (11): 6 scoped aliases (`Define KPI Framework
(Offer)` etc. — migration conventions, not business synonyms, per
Q10) + `Demand Forecasting` (L3/L4 collision with `CM-1-1-1`) +
`Manage Customer` (prefix of three live labels) + 2 parenthetical
card labels (narrow legacy qualifiers) + `Manage feedstock Data
Quality` (case-only predecessor).

**AddAsAltLabel** (5): `Loading Shipment`, `Manage Inventory`,
`Manage and Support Emission Trading`, `Perform Position & PNL
Analysis` (validator: PNL ≠ P&L under normalization; PNL notation is
live vocabulary), `Manage R&D Portfolios`. Each passed normalized
collision checks against all live prefLabels and altLabels.

## Columns

concept_slug, current_prefLabel, historical_label, label_kind,
ttl_altLabels_now, rename_note, proposed_disposition, searchable,
scope_context, step3d_precedent, rationale, decision (approve on all 90 rows),
reviewer_rationale (one-line rationale per disposition).

## Deliberately not decided here

- Implementation route for the 5 adds (workbook `alt_labels` column
  vs Step 4 build script).
- Structured representation of scoped aliases until a reified
  historical-label record exists (`core:priorPreferredLabel`
  proposal).
- The future terminology pass on duplicate labels (`Define KPI
  Framework`, `Determine Taxability`) — logged, not scheduled.
