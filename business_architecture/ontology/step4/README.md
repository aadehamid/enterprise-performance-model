# Step 4 working area — verb-predicate mapping review

This directory is the working area for **Step 4**: mapping the source
workbook's relationship verbs (`uses-input`, `informed-by`, `enables`,
`requires`, `governed-by`, …) to ontology predicates, row by row, under
Hamid's review.

- **Step 4 is PROMOTED** (2026-09-30; Hamid: "I approved the promotion",
  recorded on PR #190). All 10 boxes in `release-checklist.md` are complete.
  Promotion approved the review. The `core` 1.0.0 release (serializing the
  canonical facts to Turtle and retiring `intake:` in one flag-day release,
  per decision Q2) is still an open decision, and nothing retires until it
  is approved.
- **Nothing here merges to `main`** without Hamid's explicit approval.
- **Source of truth for counts:** the gate, `evidence-gate.py`, and
  `ledger-v2.md`. Current: 617 emitting / 686 held / 12 deferred / 1
  external governance / 2 structured flow = 1,318 mentions; 457 canonical
  facts (verified 2026-09-30 on `main` 37ab0a0: gate 433 PASS / 0 FAIL,
  `canonical-facts.csv` 457 rows).
- Key files: `verb-predicate-mapping-v2.md` (the signed-off mapping
  document, 16/16 sections), `canonical-facts.csv` (stored facts), `mapping_v2.py` (the
  pipeline), `evidence-gate.py` (the evidence gate), `ledger-v2.md`
  (decision log), `source-workbook-backlog.md` (workbook corrections),
  `review-evidence/` (row-level review batches).
