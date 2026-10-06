# EPM-DEC-001-0013: Release `core` 1.0.0 after Phase 1

| Field | Value |
|---|---|
| Status | Decided; amended by EPM-DEC-001-0025 (2026-10-06) |
| Date | 2026-10-05 |
| Questions | Q12, and Q3 of the handover plan |
| Source | Grilling session on the handover plan |

## Context

The release serializes the canonical relationship facts to Turtle and retires all 5,571 `intake:` triples in one release (Step 4 decision Q2).

## Decision

Release after Phase 1, so the held rows get their fresh verdicts before the `intake:` layer is retired. Scope: the canonical facts at that time, zero `intake:`, and a fresh attestation run on the post-Phase 1 ledger right before the release PR. The order after that is Step 5, 6, 7, 9, 10, 11, then Step 12 (EPM-DEC-001-0020).

## Alternatives considered

Release before Phase 1; release after Step 5.

## Hamid's recorded words

Q12: "I agree ."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Amendment (2026-10-06)

EPM-DEC-001-0025 defines Phase 1 as the source-correction backlog. The release needs fresh verdicts for the rows on that backlog. The 411 held mentions outside it stay held with their recorded reasons and wait for a later release.

## Evidence

`business_architecture/ontology/step4/step4-decisions.md` Q2 and Q3; playbook evidence rule 10.
