# EPM-DEC-001-0088: Six close-out releases are approved; `party` takes product values from MPC's FY2025 Form 10-K, mapped to PIDX and OEO

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for the releases, the product values' source and module, and the reviewer; how each is built delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | The product code list that the PIDX and OEO mappings wait for (EPM-DEC-001-0064); the releases that close the 16 projection gaps (EPM-DEC-001-0036, amendment of 2026-10-22) and carry MPC-P10 (EPM-DEC-001-0087); the independent reviewer while Pi has no usage |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |


*2026-10-23:* the title's "mapped to PIDX" became PIDX family letters as plain identifiers; OEO is mapped (EPM-DEC-001-0092).
## Context

`party:Product` exists with no values, so PIDX and OEO wait (EPM-DEC-001-0064, note of 2026-10-22). The projection lists 16 rule gaps that only the next release of value-stream, kpi, party and integration can close (EPM-DEC-001-0036). MPC-P10 needs releases of core, value-stream, data-product and party (EPM-DEC-001-0087). Minor and patch releases are the module owner's under the module policy; Claude asks the decision owner before each, as for every release issued on 2026-10-22 (EPM-DEC-001-0074, and 0076 to 0080).

## Decision

**The decision owner's decisions:**

1. **Product values come from MPC's FY2025 Form 10-K,** in the `party` module, mapped to PIDX product codes by identifier and to OEO fuel classes, in a minor release. *2026-10-23:* PIDX publishes no IRIs and its codes name company-requested grades, so the decision owner chose instead to record each product's PIDX family letters as plain identifiers: "Family codes, flagged (Recommended)" (EPM-DEC-001-0092).
2. **Six releases are approved:**
   - `core` 2.3.0: CM 1.3.7.1.7 Coordinate Customer Onboarding;
   - `value-stream` 1.1.0: the credit review's link to CM 1.3.7.4.2, and ranges for `vs:produces` and `vs:consumes`;
   - `data-product` 1.1.0: the Customer Master data product;
   - `party` 1.1.0: the product values with their mappings, the onboarding stage linked to the new process, and its 8 projection fixes;
   - `kpi` 1.1.1: a range for `pop:populationEvidence`;
   - `integration` 1.0.1: its 5 projection fixes.
3. **Codex gives the independent review** and the Cursor bot the PR verdict, while Pi has no usage.

The question put to the decision owner said 7 fixes for party and 3 for integration. `projection/pipeline.py` lists 8 and 5: party's ranges for `evidenceInput`, `customerRole` and `carries` and cardinality for `plays`, `mpcClassification`, `implements`, `governedBy` and `feeds`; integration's range and cardinality for `placementKind`, a range for `reliesOn`, and cardinality for `authority:rank` and `authority:evidenceTier`. Claude told the decision owner straight after the answer, and later asked them to approve the corrected counts; they did: "Approve 8 and 5 (Recommended)".

**What follows (Claude, under EPM-DEC-001-0028):**

1. **The product scheme** takes the 10-K's six refinery product groups (gasoline, distillates, propane, NGLs and petrochemicals, heavy fuel oil, asphalt) as top concepts and its named products beneath them, each cited to the filing (`reference/mpc/mpc-fy2025-10k-fact-sheet.md`, section 4). A mapping is added only where the external term's own definition matches; each cites the source's version and date. Under PIDX's licence, a mapping points to a PIDX code by identifier and copies no PIDX list (EPM-DEC-001-0064, item 1). *2026-10-23:* superseded for PIDX: products carry PIDX family letters, not mappings to codes; the decision owner chose "Family codes, flagged (Recommended)" (EPM-DEC-001-0092).
2. **Each release has its own pull request and release record,** in the order above, through `check.sh`, the sweep, Codex's independent review, the Cursor bot's verdict and a merge.
3. **The product list is a point for the business** in the close-out package (EPM-DEC-001-0086): MPC's own product list can refine or replace the public categories.

## Alternatives considered

- **A new Product domain module.** Not chosen by the decision owner. Its first release would be a major.
- **Park the product list with the business.** Not chosen by the decision owner: the PIDX and OEO mappings would stay unmade.
- **Ask before each tag.** Not chosen by the decision owner.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "10-K slate in party (Recommended)", "Approve all six (Recommended)", "Approve 8 and 5 (Recommended)" and "Keep Codex (Recommended)". The session goal: "aligned. keep gooing until the ontology is done after addressing all the outstanding question. stop the goal gracefully when you are completely done".

## Evidence

- `business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md`, section 4 (MPC-S01, FY2025 Form 10-K, filed 2026-02-26).
- `business_architecture/ontology/projection/pipeline.py`, `RELEASE_EXCEPTIONS`.
- EPM-DEC-001-0036, 0037, 0064, 0074, 0076 to 0080, 0086, 0087.

## Consequences

- When the six releases merge, the projection's list of release gaps is empty, and PIDX and OEO are mapped where a match holds. *2026-10-23:* OEO is mapped with SKOS; PIDX is recorded as family letters, not mapped, after the decision owner chose "Family codes, flagged (Recommended)" (EPM-DEC-001-0092).
- EPM-DEC-001-0036 and 0064 carry dated notes.
