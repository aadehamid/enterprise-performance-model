# EPM-DEC-001-0001: PPC is a planned consumer, not an active one

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q1 |
| Source | Grilling session on the handover plan |

## Context

PR #198 (2026-10-02) registered PPC as a downstream proving-ground consumer (D-18, Candidate) and drafted EPM-ARCH-REL-001, an EPM consumer release contract (Draft). The handover plan still said the ontology has no consumer. The `core` 1.0.0 release gate (playbook evidence rule 10) needs a fresh no-consumer attestation.

## Decision

Treat PPC as planned but not yet active. Build the ontology as if there is no consumer. Use EPM-ARCH-REL-001 as the target shape for the Step 10 release package, and avoid choices in `core` 1.0.0 that would block it (for example, unversioned or unstable IRIs). The no-consumer attestation stays valid while D-18 and REL-001 are Candidate or Draft.

## Alternatives considered

(a) PPC is a real consumer now, and `core` 1.0.0 must meet REL-001's manifest and checksum shape. (c) Ignore PPC until D-18 is decided.

## Hamid's recorded words

Round 1: "Agree with the rest."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

`EPM-FOUND-000.md` section "Downstream consumers and the PPC proving ground"; decision D-18; `architecture/EPM-ARCH-REL-001_EPM_Consumer_Release_Contract.md`.
