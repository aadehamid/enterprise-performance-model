# EPM-DEC-001-0024: The playbook is a method; project decisions live in EPM-DEC-001

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 (proposed); 2026-10-06 (decided) |
| Questions | Follow-up to Q2 |
| Source | Grilling session on the handover plan |

## Context

EPM-DEC-001-0002 says a decision change lands in playbook §2 first. Hamid then asked that the playbook be a playbook someone can follow to build their own ontology, not a worklog, and asked for a review to make it so. Project decisions (EPM IRIs, the Step 4 Q1 to Q12 locks, MPC choices) cannot stay in a company-neutral §2.

## Decision

Amendment to EPM-DEC-001-0002: the playbook holds the method (company-neutral steps, rules and reasons) and changes only when the method changes. Project decisions land in an EPM-DEC-001 record. The worklog's §4 journal carries a dated pointer to the record, and to the playbook section when a decision also changes the method. Project examples stay in the playbook's worked example (§7).

## Alternatives considered

Keep project decisions in playbook §2 (EPM-DEC-001-0002 as written).

## Hamid's recorded words

"Remember the Playbook is not a worklog but a playbook that someone can follow to create their own ontology. Write it as such. Actually. Review the playbook to make sure it is a playbook that shows how an ontology can be created from scratch and it is written as such and not a worklog." The amendment was Claude's inference from that request, recorded as Proposed. On 2026-10-06 Hamid decided it: "Playbook holds the method, yes."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

`business_architecture/ontology/ontology-playbook.md` (this PR's rewrite).
