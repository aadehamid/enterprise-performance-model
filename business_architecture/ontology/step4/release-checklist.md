# Step 4 Release Checklist — v0.4 Draft

**Status:** Draft — re-pinned to `main` at `6a155bc2` (2026-09-29)
**Date:** 2026-09-27 (status); re-pin 2026-09-29

## Current State (main @ 6a155bc2)

### Methodology
- **PR #159** merged as `7b85121` — verb review methodology Approved
- **Phase 3 sibling fix** at `e9b80d3` — `core:precedes` siblings may use structural nearness under Rule 5

### Verb Packages (on main)
| Verb | PR | Status |
|------|-----|--------|
| requires | #154 | 5 APPROVE / 1 HOLD (REL-00208) |
| assures | #155 | 5 APPROVE / 3 HOLD |
| constrained-by | #156 | 10 APPROVE / 1 HOLD (REL-00097) |
| precedes/follows | #152 | 38 STAND / 20 HOLD / 256 PROMOTE |
| governed-by | — | 7 recorded hierarchy exceptions (REL-01309, REL-00106, REL-00531, REL-00542, REL-00588, REL-00601, REL-00623), each not a precedent. Pass: 5 STAND / 13 PROMOTE / 20 HOLD → 18 emitting |
| triggers | — | 2 STAND / 5 PROMOTE / 11 HOLD → 7 emitting |

### Conservation
**617 emitting + 686 held + 12 deferred + 1 external-governance + 2 structured-flow = 1,318**
*(corrected 2026-09-29 from 615/688; see ledger-v2.md figure-correction entry)*

### Pinned Evidence
- **PINNED_SHA:** `6a155bc23ba3971ce430b774b4ddd6f4a933e380` (re-pinned 2026-09-29 from `d7310c9acd37c893d7d6926645c715f425eb9dc8`; all 7 SHA-stamped CSVs re-stamped, content verified identical except the SHA column)
- Re-pin completed 2026-09-29; remaining promotion preconditions below still apply.

### PR #124 Proof
- Canonical file SHA-256 before #124: `e50d1b6f00085521979a3ee825e765c494c0b3aa5e1374f8573bcea96869f091`
- At #124: `7b21bd2402721cfa1eef4103b8d460a92e996268a1c6495bfed4ea12ac2d3a58`
- Current: `fc5d2db759358638557198dea43a13027236ae80c0aa8a569b8f8492651539d0`
- `no-consumer-attestation.md` re-attested 2026-09-29 (Hamid) against pin `6a155bc23ba3971ce430b774b4ddd6f4a933e380` — supersedes the stale #124 attestation.

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

### Pending — Hamid
- [x] Fresh no-consumer attestation (dated after re-pin) — attested 2026-09-29
- [x] Mapping document sign-off (section by section) — all 16 sections approved by Hamid 2026-09-29:
  1. The 5 mapping answers, 2. Canonical direction table, 3. Mention → canonical fact → mirror accounting,
  4. Per-verb proposed predicate counts, 5. Contradictions, 6. Review instruments, 7. How to review,
  8. Basis change versus bucket change, 9. `core:assuredBy` scope boundary, 10. No-two-cycle rule,
  11. Unique-candidate triage-signal rule, 12. Hierarchy non-duplication rule, 13. Enablement definition,
  14. Duplicate-evidence merge, 15. Recommendation versus enablement, 16. G1b no-verb-change rule.
  (5 verb sections previously reviewed; Section 1 accounting approved 2026-09-29.)
- [ ] Explicit promotion approval

## Notes
- PR #160 closed without merge (was stacked: 4 verb packages + checklist).
- PR #161 closed without merge (requires revision reverted; #154 package stands).
- Rule 6 on main: precedes/follows 18/18 PASS (`precedes-follows-rule6-samples.md`). Assures, constrained-by, and requires Rule 6 samples are not recorded on main.
