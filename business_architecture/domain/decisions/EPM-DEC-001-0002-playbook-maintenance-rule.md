# EPM-DEC-001-0002: Playbook maintenance rule

| Field | Value |
|---|---|
| Status | Decided (an amendment is proposed in EPM-DEC-001-0024) |
| Date | 2026-10-05 |
| Questions | Q2 |
| Source | Grilling session on the handover plan |

## Context

The rule was proposed on 2026-09-30: a decision change lands in playbook §2 first, and the worklog §4 carries a dated pointer.

## Decision

Adopt the rule as written, with one addition: the PR that changes the playbook must add the worklog pointer in the same diff, so a reviewer can HOLD a PR that has one without the other.

## Alternatives considered

Adopt without the same-diff addition; reject the rule.

## Hamid's recorded words

Round 1: "Agree with the rest." Later the same day Hamid stated: "Remember the Playbook is not a worklog but a playbook that someone can follow to create their own ontology." EPM-DEC-001-0024 proposes how that changes where project decisions land.

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

`business_architecture/ontology/ontology-playbook.md` (before this PR) §2 "Playbook maintenance (proposed 2026-09-30)".
