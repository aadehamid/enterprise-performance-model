# Blast-Radius Proof: PR #170 Re-pin (pin 1ba2ab0 -> d7310c9a)

Date: 2026-09-29. Run against main `b04c8d89`.

## Scope

This proof covers the seven SHA-stamped CSVs only — not the whole #170
commit. #170 also edited `PINNED_SHA.txt`, `release-checklist.md`, and
`verb-predicate-mapping-v2.md`; those are out of scope here.

## Method

Cell-by-cell CSV comparison of the seven files at parent `d7310c9a` (#169)
vs merge `fe83a3845` (#170). Every row, every column.

## Result

| File | Rows | Changed columns |
|---|---|---|
| target-dispositions-v2.csv | 1318 -> 1318 | baseline_sha only |
| context-pass.csv | 1021 -> 1021 | baseline_sha only |
| sibling-review-package-v2.csv | 42 -> 42 | baseline_sha only |
| label-dispositions-v1.2.csv | 104 -> 104 | baseline_sha only |
| requires-review.csv | 6 -> 6 | baseline_sha only |
| assures-review.csv | 8 -> 8 | baseline_sha only |
| enables-review.csv | 399 -> 399 | baseline_sha only |

- Row counts identical. Column sets identical.
- The only changed cell in any file is `baseline_sha`.
- Every `baseline_sha` cell moved from
  `1ba2ab0bd8ae1d98ebaeed5129bd190130936624`
  to
  `d7310c9acd37c893d7d6926645c715f425eb9dc8`.
- No cell became `fe83a3845` — that is the #170 merge commit (the diff
  range), not the pin. The pin transition is `1ba2ab0` -> `d7310c9a`.
- `PINNED_SHA.txt` on main remains
  `d7310c9acd37c893d7d6926645c715f425eb9dc8`.

**Blast radius: PASS.** The re-pin touched nothing but `baseline_sha`
cells in the seven evidence CSVs.

Pre-reviewed by Cursor EPM on Slack (pin-transition correction applied
before raising).
