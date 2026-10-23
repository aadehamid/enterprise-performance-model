# EPM-DEC-001-0083: Phase E is closed: Steps 5 to 12 are done, each with its listed exceptions

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-22 |
| Questions | Phase E of EPM-DEC-001-0052: which plan steps are done, what each leaves open, and which items wait on the decision owner |
| Source | Claude Code session of 2026-10-22 (Phase E); `answers-2026-10-22-phase-e.md` |

## Context

EPM-DEC-001-0052 orders the remaining work in phases A to F, and says the ontology is complete when every competency question is answerable or parked by a recorded decision, every module is released and approved, the external mappings are done, and the projection passes. Phases A to D are done (EPM-DEC-001-0053 to 0080). Phase E's work has merged: Step 9's release-package test (EPM-DEC-001-0081), Step 10's catalog of every release (EPM-DEC-001-0082), the re-check of the external-mapping triggers (EPM-DEC-001-0064, note of 2026-10-22), and Step 12's projection of every released package (EPM-DEC-001-0036, amendment of 2026-10-22). The R2 backlog was decided earlier (EPM-DEC-001-0063), and so were the partial questions Q11, Q40, Q43 and Q44 (EPM-DEC-001-0059 and 0060).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Steps 5, 6, 7, 9, 10, 11 and 12 are done.** The worklog's plan table marks each one, with its exceptions:
   - Step 5: Forecaster stays apart from the Local Refinery Forecaster until the refinery Economics and Planning process owner confirms they are the same (EPM-DEC-001-0045, decision 2), and PSM stays unresolved (decision 6).
   - Step 6: runs stay with the consumers, by design (EPM-DEC-001-0016); `provenance/run-shapes.ttl` checks them there (EPM-DEC-001-0034).
   - Step 7: PIDX and OEO wait for product values, and IOF Supply Chain is parked, each with its trigger (EPM-DEC-001-0064). MPC-P10 is the decision owner's (EPM-DEC-001-0070). The four codes and TID Nbr wait for the business to confirm them when the ontology is shared (EPM-DEC-001-0072).
   - Step 9: the run shapes stay with the consumers, by design (EPM-DEC-001-0081).
   - Step 10: "catalog resolves" stays parked, because the namespace is not hosted (EPM-DEC-001-0039).
   - Step 11: 43 questions answerable, 0 partial, 1 waiting (`regression/run.py`). Q17 waits on the decision owner (EPM-DEC-001-0045, decision 7).
   - Step 12: 16 rule gaps in released modules are listed, each to close at that module's next release (EPM-DEC-001-0036, amendment of 2026-10-22).
2. **Steps 0 to 4 and 8 stand as recorded.** Step 3d is complete with its open exceptions; its sub-step 3d-b holds PTC-001-B by design (the decision owner, 2026-09-22). Step 4 is promoted.
3. **The held rows stay held, each with its reason.** `python3 scripts/epm_facts.py counts` gives 462 held rows: 51 Phase 1 rows (EPM-DEC-001-0025), and 411 outside Phase 1: 167 context-pass holds, 114 uses-input holds, 80 informed-by holds, 40 uses-input G1a holds, 9 governed-by holds and 1 property-rule hold. None blocks completion. A held row gets a fresh verdict only if its source is corrected, through the source-correction backlog (EPM-DEC-001-0025).
4. **Phase E is complete, except for items that wait on others.** None waits on this work.
   - **On the decision owner:**
     - Q17, meaning ownership (EPM-DEC-001-0045, decision 7);
     - MPC-P10 (EPM-DEC-001-0070; `business_process/proposals/MPC-P10-customer-lifecycle.md`);
     - a product code list, which would let PIDX and OEO be mapped; Claude asks the decision owner before building it (EPM-DEC-001-0064);
     - Phase F, rebuilding the `ontology` skill, which starts only on the decision owner's yes (EPM-DEC-001-0052, item 6).
   - **On a process owner:** Forecaster, until the refinery Economics and Planning process owner confirms it is the Local Refinery Forecaster (EPM-DEC-001-0045, decision 2).
   - **On the business:** the four codes and TID Nbr, which the business confirms when the ontology is shared (EPM-DEC-001-0072).
   - **Unresolved by decision:** PSM (EPM-DEC-001-0045, decision 6).
   - **On the next releases:** the 16 projection gaps close at the next release of value-stream, kpi, party and integration. Each is a patch or minor, the module owner's under the module policy; Claude asks the decision owner before building any (EPM-DEC-001-0036).

## Alternatives considered

- **Keep the steps "Started" until every exception closes.** Not chosen: each exception is a recorded decision, or an item that waits on the decision owner, a process owner, the business or a later release, and EPM-DEC-001-0052 counts a question parked by a recorded decision as done.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-22-phase-e.md`: "Start Phase E now". The choices above are Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

- `business_architecture/ontology/step4/playbook/ontology-worklog.md`, §2; `regression/run.py`; `scripts/epm_facts.py counts`.
- EPM-DEC-001-0016, 0025, 0034, 0036, 0039, 0045, 0052, 0063, 0064, 0070, 0072, 0081, 0082.

## Consequences

- The ontology README's Status section names where the build stands, and what waits on whom.
- Phase F waits for the decision owner's yes.
