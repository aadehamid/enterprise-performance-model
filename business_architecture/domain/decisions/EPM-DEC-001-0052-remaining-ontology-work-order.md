# EPM-DEC-001-0052: Remaining ontology work, in this order

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-19: the order; the order's content is Claude's recommendation, delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | When the Commercial Lifecycle and Order to Cash value streams and the Customer domain are handled, and in what order the remaining ontology work runs |
| Source | Claude Code sessions, 2026-10-19 (sessions 5 and 6) |

## Context

At the end of session 5 the released modules were `core` 2.1.0, `organization` 2.0.0, `ref-mpc` 1.1.0 and `kpi` 1.0.1. The competency regression stood at 17 answerable, 6 partial and 21 waiting (`business_architecture/ontology/regression/expected.csv`). Step 7 item 3, the data products (EPM-DEC-001-0017), had not started. Ten merged pull requests had changed the process map since `core` 2.1.0. The decision owner asked when the two value streams and the Customer domain would be handled, and said they have customer information to share. Claude recommended an order for the remaining work, and the decision owner chose it.

## Decision

**The decision owner's decision:** go with Claude's recommended order, through to the completion of the ontology. They added the rebuild of the `ontology` skill once every other task is done, and, in session 6, the rule for resolving ambiguity: external search for high-quality downstream sources, Marathon Petroleum first and the downstream peers second.

**What follows (Claude, under EPM-DEC-001-0028):**

The order is Claude's recommendation. Each phase is one or more pull requests, one concern each.

1. **Phase A, data products (Step 7, item 3 of EPM-DEC-001-0017).** Each data product in `business_architecture/business_process/data_product_portfolio.json` is modelled as a definition, linked to the processes that produce and consume it, or parked with a reason. Loss Control ownership is settled. The competency questions this answers move in the regression.
2. **Phase B, the two value streams (Step 7).** Commercial Lifecycle and Order to Cash, with their stages, capabilities and process links, the `kpi` measure links MPC-P09 added, and the systems and lanes overlays.
3. **Phase C, the Customer domain (Steps 5 to 7).** It waits for the decision owner's customer information (EPM-DEC-001-0004). *2026-10-21:* it arrived (EPM-DEC-001-0067). Scope: a conceptual data model of Customer, the customer lifecycle from onboarding as proposed process-map nodes, and the channel dimension of MPC-P06 (EPM-DEC-001-0047). *2026-10-21:* the lifecycle's stages map to existing processes; only MPC-P10.1 would add a node, if the decision owner accepts it (EPM-DEC-001-0070). *2026-10-23:* the decision owner accepted MPC-P10 (EPM-DEC-001-0087); `core` 2.3.0 adds CM 1.3.7.1.7 (EPM-DEC-001-0089).
4. **Phase D, a `core` release with the process-map changes.** Identity, definitions and the release build. Each release needs the decision owner's approval. *2026-10-22:* under the module policy (worklog, "Who approves a release"; EPM-DEC-001-0037), a minor or patch release is the module owner's and a major the decision owner's; Claude asked the decision owner before every release issued on 2026-10-22 (EPM-DEC-001-0074, and 0076 to 0080). The Phase D release, core 2.2.0, is a minor the decision owner approved (EPM-DEC-001-0076).
5. **Phase E, the remaining steps.** SHACL shapes for the new modules (Step 9), DCAT records (Step 10), every competency question answerable or parked by decision (Step 11), the projection on the final releases (Step 12), the 3d-d backlog, the external mappings (EPM-DEC-001-0023) and the partial questions. *2026-10-22:* done, with the exceptions and the open items listed in EPM-DEC-001-0083, each with who it waits on.
6. **Phase F, the `ontology` skill rebuilt** from the playbook and the work done, after phases A to E. It starts only after the decision owner approves the plan. *2026-10-22:* approved (EPM-DEC-001-0084); the skill ships through pull requests in `personal-agent-skills`. *2026-10-23:* done: personal-agent-skills pull request #45 merged.

The ontology is complete when every competency question is answerable or parked by a recorded decision, every module is released and approved, the external mappings are done, and the projection passes.

**Evidence for ambiguity.** Where a choice is unclear, Claude searches high-quality external sources in the order AGENTS.md sets: Marathon Petroleum (MPC) filings and public materials first, then U.S. refining peers' SEC filings, then downstream industry sources. Each source used is cited with its date.

## Alternatives considered

- **The Customer domain first.** Not chosen: it waits for the decision owner's information, and Phases A and B need nothing from them. *2026-10-21:* the information arrived (EPM-DEC-001-0067).
- **A `core` release before the overlays.** Not chosen: the customer lifecycle nodes from Phase C go into the same release, so one release covers both. *2026-10-21:* the lifecycle adds no node unless the decision owner accepts MPC-P10.1 (EPM-DEC-001-0070). *2026-10-23:* the decision owner accepted MPC-P10 (EPM-DEC-001-0087); `core` 2.3.0 adds CM 1.3.7.1.7 (EPM-DEC-001-0089).

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-completion-order.md`: "At waht point I will ging to handle Commercial Lifecyle and Order to cash."; "go with your recommended order that will see the remianing activities to complete the ontology through."; "Add the update of ontology skill to the handoff when all tasks are complete."; "It will be generic enough to build any ontology and robut enough to make ontologu enterpise ready". Saved in `answers-2026-10-19-completion-goal.md`: "Work through phases A to F in order, one PR per concern." and "Everything else is delegated under EPM-DEC-001-0028." Saved in `answers-2026-10-19-completion-search.md`: "Do external search for high quality downstream oil and gas refrenceces to resolve any ambiguity. Use Marathon petroleum comapnies as the stand in company as primary and sue all other downstream oil and gas peer as secondary sources of refrecnes." The phases' content under "What follows" is Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse it.

## Evidence

`business_architecture/ontology/regression/expected.csv`; `business_architecture/ontology/step4/playbook/ontology-worklog.md`, the Step 7 row; EPM-DEC-001-0004, 0017, 0023, 0047.

## Consequences

- Work runs phase by phase. A phase that waits on the decision owner (C, the release in D, F) does not stop the phases that do not depend on it. *2026-10-21:* Phase C no longer waits: the decision owner's customer information arrived (EPM-DEC-001-0067). *2026-10-22:* Phase D's release, core 2.2.0, is a minor, which the module policy gives to the module owner; the decision owner approved it (EPM-DEC-001-0076), as item 4's note says. *2026-10-22:* Phase F is approved (EPM-DEC-001-0084).
- EPM-DEC-001-0004 still holds: the Customer domain work waits for the decision owner's details. *2026-10-21:* the details arrived, and Phase C runs as EPM-DEC-001-0067 plans it.
