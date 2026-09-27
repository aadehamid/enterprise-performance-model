# Step 4 working area — verb-predicate mapping review

This directory is the working area for **Step 4**: mapping the source
workbook's relationship verbs (`uses-input`, `informed-by`, `enables`,
`requires`, `governed-by`, …) to ontology predicates, row by row, under
Hamid's review.

- **Promotion is BLOCKED.** Nothing in this directory may be promoted into
  the ontology (and no `intake:` predicates may retire) until the mapping
  document (`verb-predicate-mapping-v2.md`) and the release checklist are
  approved, and Hamid gives explicit approval.
- **Nothing here merges to `main`** without Hamid's explicit approval.
- **Source of truth for counts:** the gate, `evidence-gate.py`. Current
  projection: 917 emitting mentions / 386 held / 716 canonical facts.
- Key files: `verb-predicate-mapping-v2.md` (the mapping document under
  review), `canonical-facts.csv` (stored facts), `mapping_v2.py` (the
  pipeline), `evidence-gate.py` (the evidence gate), `ledger-v2.md`
  (decision log), `source-workbook-backlog.md` (workbook corrections),
  `review-evidence/` (row-level review batches).
