# EPM-DEC-001-0014: Build a small SHACL slice before the release; Step 9 order

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q13, Q23 |
| Source | Grilling session on the handover plan |

## Context

The release must pass a gate. Step 9 (full SHACL) comes later in the sequence.

## Decision

Build a minimal SHACL set before the `core` 1.0.0 release: labels present, IDs present, no `intake:` namespace, references resolve, plus the meta-shapes for the LPG design rules adopted in EPM-DEC-001-0020. Step 9 then adds, in order: every relationship fact links to its source evidence; controlled values come from their allowed lists; no definition is typed as an occurrence. Claude walks Hamid through each shape and a violation report when the slice is built.

## Alternatives considered

Script checks only until Step 9.

## Hamid's recorded words

Q13: "I agree. I want to learn how you do this when we get there." Q23: Not commented on; agreed per Hamid's rule "If i dont comment on a question, it means I am aligned."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

Playbook Step 9.
