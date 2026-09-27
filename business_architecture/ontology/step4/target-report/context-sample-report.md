# Context-confirmation sample check — 2026-09-25 (SUPERSEDES the 47-row report)

**This report supersedes the earlier 47-row sample report**, which was drawn with an
incorrect sampling formula (`max(1, round(5%))`) and against the defective
context-pass implementation. Do not cite the 47/47 figure.

Baseline: `6ab2197ba3fe6246bdb501391d22b71d0338d2c7`
Method: corrected `context_pass.py` (16/16 regression tests green), sample drawn
per domain at `max(10, ceil(5%))`, seed 42, from `context-pass.csv`.

## Pass results (corrected implementation)

- SoleCandidate rows: 1,021
- Promoted: **852** (was 915 under the defective implementation)
- Held: **169** (was 106)
  - Commercial & Marketing: 148
  - Refining: 20
  - Finance: 1

Test pass counts (rows may pass multiple): A explicit-reference 441, C two-way 164,
B structural-nearness 743. The strict inverse table cut 245 false two-way
confirmations; the ancestor exclusion cut 126 hierarchy-as-relationship B passes.

## Sample

51 rows: 41 Commercial & Marketing (of 808), 10 Refining (of 44).
Primary-test mix: A 26, B 24, C 1.

## Verdict

**51/51 target resolutions judged correct. Zero wrong resolutions. Per the review
rule, no test-tightening triggered; the corrected premise holds.**

Full per-row verdicts: `context-sample-review.md`. Notes (resolution correct,
mapping-level questions for Hamid):

- REL-00008 / REL-00112: `precedes` aimed at a whole L2 — the sequence claim is
  sound; scope of the claim is mapping v2's read.
- REL-00190 / REL-01005: B-only `governed-by` — plausible but the weakest
  evidence tier; flagged for batch-reviewer eyes.
- REL-00089 / REL-00122 / REL-01133: G1/G2 `enables` — resolutions correct;
  merge-vs-emit is Hamid's mapping decision.
- REL-00715 (`Ideation` governed-by its parent): now correctly HELD by the
  ancestor exclusion — hierarchy is not a relationship.
- REL-00374 (`AR/AP actuals` follows `Settlements`): the false two-way (backed by
  `enables`) is gone; promotes on an explicit scope-note citation instead.
- REL-00712 (`R&D implementation plans` enables `Concept & Feasibility Study`):
  promoted on B; the direction question stands for the enables review.

## Held rows (169)

Label match is the only evidence (different branch, no citation, no consistent
two-way link, or hierarchy-adjacent). Grouped by domain above for the later
domain-batch review. Includes cross-branch rows created by the R1 re-anchor
(e.g. `Allocate Crude and Feedstock` informed-by → `Refinery Planning and
Optimization`).
