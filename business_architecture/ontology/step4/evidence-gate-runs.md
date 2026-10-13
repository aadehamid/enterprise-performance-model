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

## 2026-10-12 — branch `phase1/sweep-register`, pin `2bc25cb`

- **Evidence pin (`PINNED_SHA.txt`):** `2bc25cb899943d29fa486565e447b50d7ca80782`
- **Gate:** `evidence-gate.py` — 418 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1066, held==237, canonical-facts==478,
  contradictions==0. A new check runs `batch_checks.sweep_batch_problems`
  over each adopted issue's `review-evidence/phase1-sweep/<issue>-review.csv`:
  the file holds exactly that issue's register rows, each row matches the
  approved register, its outcome and Hamid_decision follow from it, emitting
  rows carry their fact and no-relationship rows carry none. It replaces ten per-row hold checks for the #206 rows
  that now emit: 426 → 417 PASS. A second check requires exactly one review
  file per adopted issue (`batch_checks.SWEEP_ADOPTED`), and the per-issue
  check requires every register row of that issue: 417 → 418 PASS.

## 2026-10-12 — branch `phase1/sweep-203`, pin `adc7483`

- **Evidence pin (`PINNED_SHA.txt`):** `adc7483522a7f3845dceca90c95187b6253372a4`
- **Gate:** `evidence-gate.py` — 401 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1078, held==225, canonical-facts==490,
  contradictions==0. `batch_checks.SWEEP_ADOPTED` adds #203, so the sweep
  check covers its 15 rows (+1). The 12 rows that now emit leave the
  property-hold set, and their 22 per-row control-case hold checks go (−22):
  418 → 397 PASS. `batch_checks.SWEEP_PROVENANCE` lets REL-00436, answered
  no relationship, keep its recorded duplicate provenance on the REL-00447
  fact and no other.
  The sweep check now also compares each row's `direction` and `reason`
  with the register, and requires each emitting row's approved sentence in
  a `skos:scopeNote` literal of its source in the pinned baseline taxonomy.
  A new check requires the published `build/output/step3-taxonomy.ttl` to
  equal that baseline: 397 → 398 PASS. The sweep check also requires each
  emitting row's corrected verb and target exactly once in its source's
  published `intake:relatedConcepts`, and the same verb in the dispositions.
  Three new checks require `enables-review.csv`, `requires-review.csv` and
  `assures-review.csv` to list exactly the dispositions' rows of their verb,
  so a corrected verb cannot leave a stale review row: 398 → 401 PASS. The
  12 #203 rows that left `enables` were removed from `enables-review.csv`.

## 2026-10-13 — branch `phase1/sweep-210`, pin `efc4715`

- **Evidence pin (`PINNED_SHA.txt`):** `efc47150504face11bee5fdb2d57d737cfb170ca`
- **Gate:** `evidence-gate.py` — 394 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1086, held==217, canonical-facts==498,
  contradictions==0. `batch_checks.SWEEP_ADOPTED` adds #210, so the sweep check covers its 22 rows (+1); the 8 rows that now emit leave the gate's property-hold set and its control-case hold loop (−8): 401 → 394 PASS.

## 2026-10-13 — branch `phase1/sweep-202`, pin `37fed94`

- **Evidence pin (`PINNED_SHA.txt`):** `37fed949fbd2e7b333663e170717262e26ca73ac`
- **Gate:** `evidence-gate.py` — 367 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1114, held==189, canonical-facts==522,
  contradictions==0. `batch_checks.SWEEP_ADOPTED` adds #202, so the sweep check covers its 44 rows (+1); 28 per-row G1b "emits no triple" checks go with the rows that now emit (−28). The 28 G1b removed-fact checks now let a fact return only through an adopted register row whose approved stored fact it is (no count change): 394 → 367 PASS.

## 2026-10-13 — branch `phase1/sweep-209`, pin `883bd57`

- **Evidence pin (`PINNED_SHA.txt`):** `883bd57a1a1f98267489c875887462e11ed99027`
- **Gate:** `evidence-gate.py` — 368 PASS, 0 FAIL — **GATE GREEN**
- **Gate-asserted figures:** promoted==1114, held==189, canonical-facts==562,
  contradictions==0. `batch_checks.SWEEP_ADOPTED` adds #209, so the sweep check covers its 47 rows (+1). The 41 rows that now emit were mapping-level holds with no per-row gate check (no other change): 367 → 368 PASS.
