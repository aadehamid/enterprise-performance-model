# EPM-DEC-001-0021: Where the LPG guideline lives in this repo

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q31 |
| Source | Grilling session on the handover plan |

## Context

The decision owner asked to add the guideline to this repo's documentation.

## Decision

Copy both guideline files into `business_architecture/ontology/lpg-projection/` as a snapshot pinned to enterprise-people-graph commit cd63e12. enterprise-people-graph stays the master copy. Each update is recorded as a new commit reference.

## Alternatives considered

Make this repo the master copy; link only.

## The decision owner's recorded words

Q24: "Also can we add this to our documentation in this repo". Q31: Not commented on; agreed per the decision owner's rule "If i dont comment on a question, it means I am aligned."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with the decision owner). The decision owner answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." They also stated: "If i dont comment on a question, it means I am aligned." A question they did not comment on is therefore recorded as agreed with the recommendation.

## Snapshot updates

- 2026-10-06: re-pinned to `e7b09e8` (guideline v2.1, enterprise-people-graph PR #1).
- 2026-10-14: re-pinned to `8ce9ada` (guideline v2.2, enterprise-people-graph PR #3), which takes in the projection pipeline's findings (EPM-DEC-001-0036).

## Evidence

the enterprise-people-graph repository (`guideline_to_map_ontology_to_LPG`)
