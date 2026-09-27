# Step 4 Q2 Conservation Ledger — DRAFT v1

**Rule:** `emitted + held = source total`, reconciled by source predicate/field.
Zero `intake:` triples proves deletion only, not successful migration.

## A. Relationship targets (source: 1,317 relationship mentions)

| Bucket | Count | Disposition |
|---|---|---|
| Emitted resolved dependencies | 1,302 | `ResolvedToConcept`: 203 StableIdentifier + 1,057 UniquePreferredLabel + 40 ApprovedLocalAnalysisCycle + 2 ApprovedSiblingTaxability |
| Ambiguous deferred | 12 | No triple; candidates + review triggers preserved |
| Structured flow values | 2 | No process-dependency triple |
| External governance references | 1 | No triple until external-reference property is designed |
| Parked future concepts | 0 | Valid disposition; no current members |
| Dropped as non-process prose | 0 | Valid disposition; no current members |
| **Source total** | **1,317** | **1,302 + 12 + 2 + 1 + 0 + 0 = 1,317 ✓** |

Emission guards (all 1,302): subject/target existence checks; sibling-pattern
rows additionally require exact-row/pattern guards per the approved review
package. No guessed triples.

## B. Historical labels (source: 90 historical-label records)

| Bucket | Count | Disposition |
|---|---|---|
| Retained aliases | 68 | `RetainAsAltLabel`; carried through cutover |
| Added aliases | 4 | `AddAsAltLabel`; validator-clean |
| Migration-only history | 12 | `MigrationOnly`; preserved in identity map / `core:priorPreferredLabel`, excluded from alias search |
| Retired ambiguous | 6 | `RetireAsAmbiguous`; bare `Define KPI Framework` |
| **Source total** | **90** | **68 + 4 + 12 + 6 = 90 ✓** |

## C. Release-evidence checklist (all required before flag-day)

- [ ] Target-disposition report v1.1 — **APPROVED** (decision cells completed)
- [ ] Sibling-review package — **APPROVED** (42/42)
- [ ] Label-disposition report v1.1 — **APPROVED** (decision cells completed)
- [ ] This ledger — DRAFT (this file)
- [ ] Verb→predicate mapping — CANDIDATE (separate review required)
- [ ] Promotion-script emission guards implemented — PENDING
- [ ] Fresh no-consumer attestation — PENDING (must immediately precede flag-day)
- [ ] `intake:` predicate retirement — NOT STARTED

## D. What "complete" means

The Step 4 cutover is complete only when every source record has a
governed disposition AND the emitted set is provably the right
projection — not when the old predicates are merely deleted.
