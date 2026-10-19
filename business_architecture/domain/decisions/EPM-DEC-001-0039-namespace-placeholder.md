# EPM-DEC-001-0039: the w3id namespace is a placeholder; nothing is registered or hosted

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-14) |
| Date | 2026-10-14 |
| Questions | Whether to register `w3id.org/lsc` and host the release files (EPM-DEC-001-0037, For the decision owner items 2 and 3) |
| Source | Claude Code session, 2026-10-14 |

## Context

The URI policy of 2026-09-18 set the base `https://w3id.org/lsc/ontology/` and left one open action: register `w3id.org/lsc` (worklog, "URI policy — decided 2026-09-18"). Every released module mints its IRIs under that base: `core` 1.0.0 and 2.0.0, `organization` 1.0.0 and `ref-mpc` 1.0.0. EPM-DEC-001-0037 listed the registration and the hosting for the decision owner, because the playbook's Step 10 gate is "the catalog resolves and the release is retrievable".

## Decision

**The decision owner's decision:** do not host the namespace. The domain may change, so `https://w3id.org/lsc/ontology/` stays a placeholder.

**What follows (Claude, under EPM-DEC-001-0028):**
1. No request goes to w3id.org, and no release file is hosted anywhere.
2. The IRIs stay as released. They identify terms; they do not resolve. No release changes.
3. Step 10's gate ("the catalog resolves and the release is retrievable") is parked by this decision. Releases stay retrievable from the repository under their tags. The revival trigger is a decision on the domain.
4. If the domain changes, the base IRI changes with it. That is a change to every term's identity, so it needs its own decision and major releases of every module (playbook Appendix B). Choosing the domain before anyone uses the ontology keeps that cost low.

The licence question (EPM-DEC-001-0037, For the decision owner item 3) is separate and still open. *2026-10-18:* decided, proprietary (EPM-DEC-001-0041).

## Alternatives considered

- **Register `w3id.org/lsc` now.** Not chosen: The decision owner expects the domain may change, and a registered redirect is a public commitment.
- **Change the base IRI now to a neutral placeholder such as `example.org`.** Not chosen: it would need major releases of every module for no present benefit; the current base already works as a placeholder.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/namespace-hosting.md`: "By the way I do not wnat to host the namespace. the domain may chnage. we can use it as placeholder for now." Items 1 to 4 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and the decision owner can reverse them.

## Evidence

The worklog's URI policy (2026-09-18); EPM-DEC-001-0037; `ontology-playbook.md` Step 10 and Appendix B; the release manifests under `ontology/releases/`.

## Consequences

- The ontology README, EPM-DEC-001-0037, the worklog and the playbook's worked example no longer list the registration or the hosting as waiting for the decision owner.
