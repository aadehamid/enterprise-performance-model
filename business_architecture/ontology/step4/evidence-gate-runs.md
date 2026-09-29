# Evidence Gate Runs

## 2026-09-29 — main `bdd5026f`, pin `d7310c9a`

- **Main SHA at run:** `bdd5026fff59c0810f5811b4ef70f326a11bae55` (PR #171)
- **Evidence pin (`PINNED_SHA.txt`):** `d7310c9acd37c893d7d6926645c715f425eb9dc8`
- **Gate:** `evidence-gate.py` — 433 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1066, held==237, canonical-facts==457,
  contradictions==0, no orphans, sample-verdicts==51, label rows 104
  (90 carried-approved, 14 approved 2026-09-25)
- **Documented bucket totals** (from `release-checklist.md`, `ledger-v2.md`
  conservation line, `step4-decisions.md`, `verb-predicate-mapping-v2.md`
  header — not gate assertions): 615 emitting / 688 held / 457 canonical facts.
  Conservation: 615 + 688 + 12 deferred + 1 external-governance
  + 2 structured-flow = 1,318.

Note: the pin is `d7310c9a` (PR #170). `bdd5026f` is the main commit the
gate was run against, not the pin. Do not retitle the checklist's
"main @ d7310c9" line to a run SHA.
