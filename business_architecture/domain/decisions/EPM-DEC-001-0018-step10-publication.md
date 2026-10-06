# EPM-DEC-001-0018: Step 10: publication target

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q24 |
| Source | Grilling session on the handover plan |

## Context

Step 10 publishes the ontology.

## Decision

Use w3id permanent IRIs, a DCAT catalog of the release and its files, and a release package shaped to EPM-ARCH-REL-001's manifest. The Neo4j projection is a separate step after the build (EPM-DEC-001-0020).

## Alternatives considered

Decide the Neo4j load path inside Step 10.

## Hamid's recorded words

Q24: "we will do projection to Neo4j when we finish building out the ontology."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

Playbook Step 10; `architecture/EPM-ARCH-REL-001_EPM_Consumer_Release_Contract.md`.
