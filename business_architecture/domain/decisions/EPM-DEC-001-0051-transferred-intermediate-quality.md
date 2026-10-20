# EPM-DEC-001-0051: The quality of a transferred intermediate is managed as feed to the receiving refinery

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-19; the description's wording delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | MPC-P03 coverage check, question 2: the quality of transferred intermediates (`business_architecture/business_process/proposals/MPC-P03-transfer-coverage-gaps.md`) |
| Source | Claude Code session, 2026-10-19 |

## Context

The decision owner accepted MPC-P03 "with a physical-execution coverage check" (EPM-DEC-001-0047). The check found two gaps. The first, loss and gain, was filled by CM 1.1.3.7.13 (EPM-DEC-001-0048). The second is quality: CM 1.2.5.1 Crude/Feed Quality Management covers crude and feedstock quality, and no step named the quality of an intermediate that one refinery sends and another receives. The proposal gave three options: (A, recommended) widen CM 1.2.5.1's description so it covers intermediates received as feed from another refinery; (B) add a step under CM 1.1.7; (C) leave it.

## Decision

**The decision owner's decision:** option A, "Widen CM 1.2.5.1 (Recommended)".

**What follows (Claude, under EPM-DEC-001-0028):**
1. **CM 1.2.5.1 gets a description,** which it lacked. It covers the crude oil and other feedstocks a refinery runs, including intermediate products it receives as feed from another refinery, and cites MPC's FY2025 Form 10-K, Item 1, for the intermediate products that move between MPC's refineries. No process is added.
2. **CM 1.1.7's description** no longer says that no step names the quality of a transferred intermediate. It points to CM 1.2.5.1.
3. **The node's name and variants stay.** Released packages stay fixed; the description reaches the ontology in a later `core` release (EPM-DEC-001-0047, What follows, item 2).

## Alternatives considered

- **(B) A step under CM 1.1.7.** Not chosen: the decision owner chose A.
- **(C) Leave the gap.** Not chosen, for the same reason.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-after-run.md`: "Widen CM 1.2.5.1 (Recommended)". Items 1 to 3 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

`business_architecture/reference/mpc/mpc-fy2025-10k-fact-sheet.md`, Item 1 operating facts; `business_architecture/business_process/proposals/MPC-P03-transfer-coverage-gaps.md`.

## Consequences

- Every step of an inter-refinery transfer in the coverage check is now covered by a named process.
- The MPC-P03 coverage check is closed, on the proposal's stated assumption that CM 1.1.3 handles intermediates as well as finished products. If the decision owner reads CM 1.1.3 as finished products only, the rows that rest on it reopen (`MPC-P03-transfer-coverage-gaps.md`, the paragraph after the table).
