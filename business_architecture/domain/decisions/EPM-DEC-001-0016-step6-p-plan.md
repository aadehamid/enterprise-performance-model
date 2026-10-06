# EPM-DEC-001-0016: Step 6: adopt P-Plan; occurrences belong to consumers

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q20 |
| Source | Grilling session on the handover plan |

## Context

Step 6 separates planned process definitions from what happened.

## Decision

Adopt P-Plan, the PROV-O extension for plans and steps, as the bridge from definitions to activities. The ontology defines the pattern and holds no occurrence records (EPM-DEC-001-0005). Occurrences belong to consumers such as PPC, which compare executed instances against EPM's designed processes (EPM-ARCH-PPC-003).

## Alternatives considered

Plain PROV-O without P-Plan.

## Hamid's recorded words

Not commented on; agreed per Hamid's rule "If i dont comment on a question, it means I am aligned."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

P-Plan: http://purl.org/net/p-plan#; `architecture/EPM-ARCH-PPC-003_Process_Conformance_and_Executable_Semantics_Extension.md`.
