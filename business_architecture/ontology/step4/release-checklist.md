# Step 4 Release Checklist — v1.0 PROMOTED

**Status:** PROMOTED 2026-09-30 — the decision owner: "I approved the promotion" (2026-09-30 03:26 UTC, recorded on PR #190). All 10 checklist boxes complete.
**Date:** 2026-09-27 (status); re-pin 2026-09-29

## Current state (as of the commit containing this file; promotion was approved at 6a155bc2)

### Methodology
- **PR #159** merged as `7b85121` — verb review methodology Approved
- **Phase 3 sibling fix** at `e9b80d3` — `core:precedes` siblings may use structural nearness under Rule 5

### Verb packages
Snapshot as of #204 batch 1 (2026-10-12). Current per-verb figures: `python3 scripts/epm_facts.py counts`.

| Verb | PR | Status |
|------|-----|--------|
| requires | #154 | 5 APPROVE / 1 HOLD (REL-00208) |
| assures | #155 | 5 APPROVE / 3 HOLD |
| constrained-by | #156 | 10 APPROVE / 1 HOLD (REL-00097) |
| precedes/follows | #152 | 38 STAND / 20 HOLD / 256 PROMOTE |
| governed-by | — | 7 recorded hierarchy exceptions (REL-01309, REL-00106, REL-00531, REL-00542, REL-00588, REL-00601, REL-00623), each not a precedent. Pass: 5 STAND / 13 PROMOTE / 20 HOLD → 18 emitting |
| triggers | — | 2 STAND / 5 PROMOTE / 11 HOLD → 7 emitting (2026-09-26); the 11 held rows were answered in #204 batch 1 (2026-10-12) and emit → 18 emitting |

### Conservation
Current figures: `python3 scripts/epm_facts.py counts`; every bucket conserves to the total of all mentions.
*(At promotion, 2026-09-30: 617 emitting + 686 held + 12 deferred + 1 external-governance + 2 structured-flow = 1,318, corrected 2026-09-29 from 615/688. Each later change is a dated entry in ledger-v2.md.)*

### Pinned Evidence
- **PINNED_SHA:** `388d8a0517cc74eaedbfca1cc963f4a4a0dc15d9` (re-pinned 2026-10-13 for the #201 answers from the Phase 1 register, from `883bd57a1a1f98267489c875887462e11ed99027`; all 7 SHA-stamped CSVs re-stamped, 2,807 rows; the re-pin itself changes only the SHA column. The #201 adoption that followed changed content: 75 rows left their verb-review file and REL-00138 left `context-pass.csv` (its retarget names a stable ID, so it now resolves directly), 2,731 stamped rows after it, and the dispositions, context notes and canonical facts took the corrected verbs). Promotion was approved against `6a155bc2`.
  - Previous pin: `883bd57a1a1f98267489c875887462e11ed99027` (re-pinned 2026-10-13 for the #209 answers from the Phase 1 register, from `37fed949fbd2e7b333663e170717262e26ca73ac`; all 7 SHA-stamped CSVs re-stamped, 2,848 rows; the re-pin itself changes only the SHA column. The #209 adoption that followed changed content: 41 rows left their verb-review file (2,807 stamped rows after it), and the dispositions, context notes and canonical facts took the corrected verbs). Promotion was approved against `6a155bc2`.
  - Previous pin: `37fed949fbd2e7b333663e170717262e26ca73ac` (re-pinned 2026-10-12 for the #202 answers from the Phase 1 register, from `efc47150504face11bee5fdb2d57d737cfb170ca`; all 7 SHA-stamped CSVs re-stamped, 2,876 rows; the re-pin itself changes only the SHA column. The #202 adoption that followed changed content: its 28 rows left `enables-review.csv` (2,848 stamped rows after it), and the dispositions, context notes and canonical facts took the corrected verbs). Promotion was approved against `6a155bc2`.
  - Previous pin: `efc47150504face11bee5fdb2d57d737cfb170ca` (re-pinned 2026-10-12 for the #210 answers from the Phase 1 register, from `adc7483522a7f3845dceca90c95187b6253372a4`; all 7 SHA-stamped CSVs re-stamped, 2,884 rows; the re-pin itself changes only the SHA column. The #210 adoption that followed changed content: its 8 rows left `enables-review.csv` (2,876 stamped rows after it), and the dispositions, context notes and canonical facts took the corrected verbs). Promotion was approved against `6a155bc2`.
  - Previous pin: `adc7483522a7f3845dceca90c95187b6253372a4` (re-pinned 2026-10-12 for the #203 answers from the Phase 1 register, from `2bc25cb899943d29fa486565e447b50d7ca80782`; all 7 SHA-stamped CSVs re-stamped, 2,897 rows; the re-pin itself changes only the SHA column). Promotion was approved against `6a155bc2`.
  - Previous pin: `2bc25cb899943d29fa486565e447b50d7ca80782` (re-pinned 2026-10-12 for the #206 answers from the Phase 1 register, from `51a32aa2eea43a819a7fff23b624ff8bd291bfad`; all 7 SHA-stamped CSVs re-stamped, 2,898 rows; the re-pin itself changes only the SHA column). Promotion was approved against `6a155bc2`.
  - Previous pin: `51a32aa2eea43a819a7fff23b624ff8bd291bfad` (re-pinned 2026-10-12 for the #204 batch 1 trigger sentences, from `d8b482751e418338203e976e5741dcfe538b4800`; all 7 SHA-stamped CSVs re-stamped, 2,898 rows; the re-pin itself changed only the SHA column, and the batch commit then updated `context-pass.csv` for eight #204 rows (REL-00169, REL-00170, REL-00252, REL-00396, REL-00398, REL-00400, REL-00403, REL-00892), whose new scope-note sentences give an explicit reference in place of structural nearness). Promotion was approved against `6a155bc2`.
- Re-pin completed 2026-09-29; all promotion preconditions satisfied 2026-09-30.

### PR #124 Proof
- Canonical file SHA-256 before #124: `e50d1b6f00085521979a3ee825e765c494c0b3aa5e1374f8573bcea96869f091`
- At #124: `7b21bd2402721cfa1eef4103b8d460a92e996268a1c6495bfed4ea12ac2d3a58`
- At promotion (`6a155bc2`) and unchanged through #205: `fc5d2db759358638557198dea43a13027236ae80c0aa8a569b8f8492651539d0` (457 facts)
- After #204 batch 1 (468 facts, 11 `core:triggeredBy` added): `8726f8057b048f21dc19152a65c145465d27360fa46cd64d17fc4bf49091ec13`
- `no-consumer-attestation.md` re-attested 2026-09-29 (the decision owner) against pin `6a155bc23ba3971ce430b774b4ddd6f4a933e380` — supersedes the stale #124 attestation.

## Promotion Preconditions

### Done
- [x] Every row verdict-recorded
- [x] Ledger reconciles with canonical data
- [x] Methodology approved (PR #159)

### Pending — Assistant
- [x] Evidence gate passes on current main (GREEN 2026-09-29, post re-pin to `6a155bc2`)
- [x] Re-pin evidence to current main SHA (2026-09-29 → `6a155bc2`)
- [x] Regression tests pass (`test_context_pass.py` 17/17; evidence-gate GREEN post re-pin)
- [x] Blast-radius proof against real artifacts (re-pin proven content-neutral: 7 CSVs differ only in `baseline_sha`, 2,898 rows, no verdict-column change)

### Pending — the decision owner
- [x] Fresh no-consumer attestation (dated after re-pin) — attested 2026-09-29
- [x] Mapping document sign-off (section by section) — all 16 sections approved by the decision owner 2026-09-29:
  1. The 5 mapping answers, 2. Canonical direction table, 3. Mention → canonical fact → mirror accounting,
  4. Per-verb proposed predicate counts, 5. Contradictions, 6. Review instruments, 7. How to review,
  8. Basis change versus bucket change, 9. `core:assuredBy` scope boundary, 10. No-two-cycle rule,
  11. Unique-candidate triage-signal rule, 12. Hierarchy non-duplication rule, 13. Enablement definition,
  14. Duplicate-evidence merge, 15. Recommendation versus enablement, 16. G1b no-verb-change rule.
  (5 verb sections previously reviewed; Section 1 accounting approved 2026-09-29.)
- [x] Explicit promotion approval — the decision owner: "I approved the promotion" (2026-09-30 03:26 UTC, recorded on PR #190)

## core 1.0.0 release (EPM-DEC-001-0013; built as EPM-DEC-001-0029 decides)

- [x] Every Phase 1 row has a fresh verdict: the six sweep batches (#206, #203, #210, #202, #209, #201) after #204 and #205; 51 Phase 1 rows stay held with recorded reasons (`epm_facts.py counts`). #202 merged in #244, #209 in #247 and #201 in #248.
- [x] The release builds from the pinned evidence: `release/build_core.py` writes `releases/core/1.0.0/`; `check.sh` runs `--verify`.
- [x] Zero `intake:` and full conservation: `conservation.csv` reconciles 5,571 source = 5,571 migrated; the build stops on any leftover `intake:` triple or blank node.
- [x] SHACL release slice conforms (`release/shapes.ttl`; EPM-DEC-001-0014).
- [x] LPG rules 1, 2, 3 and 5 (EPM-DEC-001-0020): one kind and one range per property (tested), a stated cardinality on every core property (shapes; tested), no blank nodes, fixed prefixes.
- [x] **Conservation ledger approval: The decision owner.** Given 2026-10-13 (`review-evidence/decision-owner-answers/core-1-0-0-release.md`). The before/after run reconciles (`conservation.csv`); `ledger-v2.md` is ready for approval.
- [x] MPC-P02 process-map ID proposal raised (EPM-DEC-001-0011, 0012) and merged in #245. The three Refining nodes ship their minted IRIs, which stay stable when the IDs land (Step 2 pins them).
- [x] **Fresh no-consumer attestation: The decision owner.** Given 2026-10-13 (`review-evidence/decision-owner-answers/core-1-0-0-release.md`). It states a fact about consumers, so it is not delegated. Repo-side evidence: outside the ontology build, `intake:` appears only in `scripts/epm_facts.py` (a counting tool) and in decision-record prose; nothing reads or consumes the namespace.
- [x] **Release approval: The decision owner.** Given 2026-10-13 (`review-evidence/decision-owner-answers/core-1-0-0-release.md`). A major release needs the decision owner's approval (`playbook/ontology-worklog.md`, "Who approves a release": "Major ... The decision owner. No exceptions").
- [x] At the cut (2026-10-13): in `build_core.py` set `STAGE = None` and `ISSUED` to the cut date, change the release-candidate test in `test_build_core.py` to the dated 1.0.0, replace the changelog's "not yet released" note with the approver and date, rebuild. Merged in #249 as d8b16e1, tagged `core-v1.0.0`.

## Notes
- PR #160 closed without merge (was stacked: 4 verb packages + checklist).
- PR #161 closed without merge (requires revision reverted; #154 package stands).
- Rule 6 on main: precedes/follows 18/18 PASS (`precedes-follows-rule6-samples.md`). Assures, constrained-by, and requires Rule 6 samples are not recorded on main.
