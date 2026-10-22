# ref-mpc changelog

## 1.2.0 (2026-10-22)

Minor. Approved by the decision owner ("Approve ref-mpc 1.2.0 (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-ref-mpc-release.md`; EPM-DEC-001-0080). MPC and MPLX as parties, in the `party` module's terms, join the module (`reference-parties.ttl`, moved from `party/`; EPM-DEC-001-0071, 0075): MPC holds the Throughput Holder and Payer roles and MPLX the Carrier and Vendor roles under MPLX's fee-based services agreements, each held since 2012-10-31 and sourced to MPLX's FY2025 Form 10-K. The roles and the agreement are on this module's namespace. No released IRI changes. It requires organization 2.0.0, as 1.1.0 did, and party 1.0.0; the parties conform to the party module's shapes.

## 1.1.0 (2026-10-19)

Minor. Approved by the decision owner ("Approve the ref-mpc release too if needed", and "You have my approval to keep going and release things as needed. while I am out", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-19-ref-mpc.md` and `answers-2026-10-19-releases.md`). The module now requires organization 2.0.0 in place of 1.0.0 (EPM-DEC-001-0045). Its facts, shapes and IRIs are unchanged: it uses only the control relationship, which organization 2.0.0 keeps as it was.

## 1.0.0 (2026-10-13)

Approved by the decision owner on 2026-10-13 ("aprove now", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md`). The release is 1.0.0-rc.1 with the issued and modified dates set (2026-10-13) and the stage removed, and its requirement moved from organization 1.0.0-rc.1 to organization 1.0.0, released the same day; nothing else changed. EPM-DEC-001-0037.

## 1.0.0-rc.1 (release candidate, not issued)

The first release candidate of the `ref-mpc` module. A module's first release is a major, so 1.0.0 is issued only when the decision owner approves it (module policy, 2026-09-18; EPM-DEC-001-0037).

- MPC and MPLX with their LEIs, MPC's control of MPLX, MPC's three reportable segments and its 13 refineries, from the FY2025 Form 10-K and GLEIF (EPM-DEC-001-0015, EPM-DEC-001-0033).
- Depends on `organization` 1.0.0-rc.1 by IRI (the candidate it shipped with); imports nothing.
