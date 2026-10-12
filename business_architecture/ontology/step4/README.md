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
- **Figures and row status:** run `python3 scripts/epm_facts.py counts`, `row REL-xxxxx` or
  `section <issue>` from the repo root. It computes them from the files below;
  `scripts/test_published_figures.py` fails if the counts here drift from it.
- **Counts** (verified 2026-10-12 after #204 batch 1). Two cuts, both
  conserving to 1,318 mentions:
  - **Ledger** (`ledger-v2.md`, verb-bucket totals): 628 emitting / 658
    held / 12 deferred / 1 external governance / 2 structured flow / 17
    scoped sequence = 1,318; 468 canonical facts (`canonical-facts.csv`,
    468 rows). The 17 scoped-sequence rows emit 17 nodes (16 handoffs) in
    `scoped-sequence/`, not canonical facts.
  - **Evidence gate** (`evidence-gate.py`): promoted 1,066 / held 237,
    plus the same 12 / 1 / 2 = 1,318; 436 PASS / 0 FAIL. The gate's cut
    is the context pass, so the scoped-sequence rows are inside its 1,066.
- Key files: `verb-predicate-mapping-v2.md` (the signed-off mapping
  document, 16/16 sections), `canonical-facts.csv` (stored facts), `mapping_v2.py` (the
  pipeline), `evidence-gate.py` (the evidence gate), `ledger-v2.md`
  (decision log), `source-workbook-backlog.md` (workbook corrections),
  `source-question-template.md` (how to ask the source author about a batch),
  `scoped-sequence/` (the scoped sequence relation, EPM-DEC-001-0026: source
  table, vocabulary, SHACL shapes, nodes and `build.py`),
  `review-evidence/` (row-level review batches; `hamid-answers/` holds his
  answers verbatim, which `epm_facts.py quotes` checks quotes against).
