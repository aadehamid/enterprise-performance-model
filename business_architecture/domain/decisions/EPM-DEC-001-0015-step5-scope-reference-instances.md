# EPM-DEC-001-0015: Step 5: classes plus public reference instances in a separate module; MPLX

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q19, Q27, Q28 (and Q21 of the handover plan) |
| Source | Grilling session on the handover plan |

## Context

Step 5 builds ORG and RACI. The question was whether MPC itself (segments, refineries, MPLX) appears as instances.

## Decision

Step 5 models the classes and relations (role, organization, site, the RACI assignment pattern) and adds MPC reference instances where appropriate, under EPM-DEC-001-0005. Reference instances live in a separate module (`ref-mpc`); the core modules stay company-neutral. MPLX is an Organization. MPC controls and consolidates MPLX through a control relation separate from `org:subOrganizationOf`. The ownership share, as-of date and source sit on a qualified-relation node (EPM-DEC-001-0020). The Midstream segment is a separate concept that MPLX's operations roll up into. Customer roles wait (EPM-DEC-001-0004).

## Alternatives considered

Classes only, with MPC as evidence and not as instances (the Round 3 recommendation, which Hamid changed); MPC instances inside the core modules.

## Hamid's recorded words

Q19: "This is a tricky one. I do want this kind of data. [...] So having the MPC, refrienery is fine where appropriate. MPLX should alos be modeled in way that is reasonable accoring to [ublicly avialble information." Q27, Q28: Not commented on; agreed per Hamid's rule "If i dont comment on a question, it means I am aligned."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

MPC FY2025 10-K (MPLX about 64% owned, controlled and consolidated), `business_architecture/reference/mpc/`.
