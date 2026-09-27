# Step 4 Release Checklist — v0.4 Draft

**Status:** Draft — status of `main` at `e9b80d3`
**Date:** 2026-09-27

## Current State (main @ e9b80d3)

### Methodology
- **PR #159** merged as `7b85121` — verb review methodology Approved
- **Phase 3 sibling fix** at `e9b80d3` (current tip) — `core:precedes` siblings may use structural nearness under Rule 5

### Verb Packages (on main)
| Verb | PR | Status |
|------|-----|--------|
| requires | #154 | 5 APPROVE / 1 HOLD (REL-00208) |
| assures | #155 | 5 APPROVE / 3 HOLD |
| constrained-by | #156 | 10 APPROVE / 1 HOLD (REL-00097) |
| precedes/follows | #152 | 38 STAND / 20 HOLD / 256 PROMOTE |
| governed-by | — | 10 governed-by exceptions (exact §5 rule) |
| triggers | — | 11 triggers |

### Conservation
**615 emitting + 688 held + 12 deferred + 1 external-governance + 2 structured-flow = 1,318**

### Pinned Evidence
- **PINNED_SHA:** `579ed89b479529d179485f633828df89399ad3c5`
- Re-pin blocked on promotion preconditions (below), not on closed PRs #160/#161.

### PR #124 Proof
- Canonical file SHA-256 before #124: `e50d1b6f00085521979a3ee825e765c494c0b3aa5e1374f8573bcea96869f091`
- At #124: `7b21bd2402721cfa1eef4103b8d460a92e996268a1c6495bfed4ea12ac2d3a58`
- Current: `fc5d2db759358638557198dea43a13027236ae80c0aa8a569b8f8492651539d0`
- `no-consumer-attestation.md` (from #124) is stale/superseded — needs fresh attestation dated after re-pin.

## Promotion Preconditions

### Done
- [x] Every row verdict-recorded
- [x] Ledger reconciles with canonical data
- [x] Methodology approved (PR #159)

### Pending — Assistant
- [ ] Evidence gate passes on current main
- [ ] Re-pin evidence to current main SHA
- [ ] Regression tests pass
- [ ] Blast-radius proof against real artifacts

### Pending — Hamid
- [ ] Fresh no-consumer attestation (dated after re-pin)
- [ ] Mapping document sign-off (section by section)
- [ ] Explicit promotion approval

## Notes
- PR #160 closed without merge (was stacked: 4 verb packages + checklist).
- PR #161 closed without merge (requires revision reverted; #154 package stands).
- Assures Rule 6 samples: pending Hamid's review.
- Constrained-by Rule 6: REL-00015, REL-00018 PASS; REL-00091 pending re-review.
- Requires Rule 6: REL-00873 PASS (Hamid 2026-09-27).
