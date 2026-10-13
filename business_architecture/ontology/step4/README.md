# Step 4 working area — verb-predicate mapping review

This directory is the working area for **Step 4**: mapping the source
workbook's relationship verbs (`uses-input`, `informed-by`, `enables`,
`requires`, `governed-by`, …) to ontology predicates, row by row, under
Hamid's review.

- **Step 4 is PROMOTED** (2026-09-30; Hamid: "I approved the promotion",
  recorded on PR #190). All 10 boxes in `release-checklist.md` are complete.
  Promotion approved the review. The `core` 1.0.0 release (serializing the
  canonical facts to Turtle and retiring `intake:` in one flag-day release,
  per decision Q2) was released on 2026-10-13 with Hamid's approval
  (`release/build_core.py`, EPM-DEC-001-0029; `release-checklist.md`, core
  1.0.0). `intake:` is retired in `releases/core/1.0.0/`.
- **Nothing here merges to `main`** without Hamid's explicit approval.
  EPM-DEC-001-0028 records his approval for Claude to merge, while he is away,
  a PR whose PR reviewer posted MERGE for its current head.
- **Figures and row status:** run `python3 scripts/epm_facts.py counts`, `row REL-xxxxx` or
  `section <issue>` from the repo root. It computes them from the files below;
  `scripts/test_published_figures.py` fails if this file states a figure.
- **Counts.** This file states no live figures, so no batch has to edit
  it. `python3 scripts/epm_facts.py counts` prints both cuts, each
  conserving to the total of all mentions: the ledger (emitting / held / deferred
  / external governance / structured flow / scoped sequence, with the
  canonical-fact count and the per-verb breakdown) and the evidence gate
  (promoted / held from the context pass, with PASS and FAIL counts).
  `ledger-v2.md` records each dated change.
- Key files: `verb-predicate-mapping-v2.md` (the signed-off mapping
  document, 16/16 sections), `canonical-facts.csv` (stored facts), `mapping_v2.py` (the
  pipeline), `evidence-gate.py` (the evidence gate), `ledger-v2.md`
  (decision log), `source-workbook-backlog.md` (workbook corrections),
  `source-question-template.md` (how to ask the source author about a batch),
  `scoped-sequence/` (the scoped sequence relation, EPM-DEC-001-0026: source
  table, vocabulary, SHACL shapes, nodes and `build.py`),
  `review-evidence/` (row-level review batches; `hamid-answers/` holds his
  answers verbatim, which `epm_facts.py quotes` checks quotes against).
