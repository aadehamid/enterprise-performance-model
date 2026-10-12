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

## 2026-10-11 — branch `phase1/205-batch1`, pin `532eeee`

- **Evidence pin (`PINNED_SHA.txt`):** `532eeeeff7988d2304cc5b876dacca39f745a855`
- **Gate:** `evidence-gate.py` — 433 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1066, held==237, canonical-facts==457,
  contradictions==0. Section 2j now checks 7 precedes/follows rows still
  held and 13 reviewed and not emitted (#205 batch 1).

## 2026-10-12 — branch `step4/repin-3a54b46`, pin `3a54b46`

- **Evidence pin (`PINNED_SHA.txt`):** `3a54b46978ad4d2ba6e491e116713bebc1bedeaf`
  (PR #225's merge on `main`; the squash merge left the earlier pin
  `532eeee` off `main`, with byte-identical workbook and taxonomy).
- **Gate:** `evidence-gate.py` — 433 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** unchanged: promoted==1066, held==237,
  canonical-facts==457, contradictions==0.

## 2026-10-12 — branch `phase1/205-batch2`, pin `d8b4827`

- **Evidence pin (`PINNED_SHA.txt`):** `d8b482751e418338203e976e5741dcfe538b4800`
- **Gate:** `evidence-gate.py` — 433 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** unchanged: promoted==1066, held==237,
  canonical-facts==457, contradictions==0. Section 2j now checks all 20
  precedes/follows rows as reviewed and not emitted (#205 batches 1 and 2).

## 2026-10-12 — branch `design/226-scoped-sequence`, pin `d8b4827`

- **Evidence pin (`PINNED_SHA.txt`):** `d8b482751e418338203e976e5741dcfe538b4800` (unchanged; no workbook edit)
- **Gate:** `evidence-gate.py` — 436 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** unchanged: promoted==1066, held==237,
  canonical-facts==457, contradictions==0. New section 2k checks the
  scoped-sequence source table (`scoped-sequence/build.py`), that its rows
  are the 17 #205 scoped rows, and 17 nodes / 16 handoffs. Section 2j still
  checks that none of the 20 #205 rows emits a core fact.

## 2026-10-12 — branch `phase1/204-batch1`, pin `51a32aa`

- **Evidence pin (`PINNED_SHA.txt`):** `51a32aa2eea43a819a7fff23b624ff8bd291bfad`
- **Gate:** `evidence-gate.py` — 426 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1066, held==237, canonical-facts==468,
  contradictions==0. Section 2i now checks, in one check, that the 11 #204
  batch 1 review rows match Hamid's saved answer row by row and emit their
  `core:triggeredBy` facts (`batch_checks.py`), replacing eleven per-row
  checks: 436 → 426 PASS.
