# ref-mpc changelog

## 1.1.0 (2026-10-19)

Minor. Approved by Hamid ("Approve the ref-mpc release too if needed", and "You have my approval to keep going and release things as needed. while I am out", saved in `step4/review-evidence/hamid-answers/answers-2026-10-19-releases.md`). The module now requires organization 2.0.0 in place of 1.0.0 (EPM-DEC-001-0045). Its facts, shapes and IRIs are unchanged: it uses only the control relationship, which organization 2.0.0 keeps as it was.

## 1.0.0 (2026-10-13)

Approved by Hamid on 2026-10-13 ("aprove now", saved in `step4/review-evidence/hamid-answers/answers-2026-10-13-session2.md`). The release is 1.0.0-rc.1 with the issued and modified dates set (2026-10-13) and the stage removed, and its requirement moved from organization 1.0.0-rc.1 to organization 1.0.0, released the same day; nothing else changed. EPM-DEC-001-0037.

## 1.0.0-rc.1 (release candidate, not issued)

The first release candidate of the `ref-mpc` module. A module's first release is a major, so 1.0.0 is issued only when Hamid approves it (module policy, 2026-09-18; EPM-DEC-001-0037).

- MPC and MPLX with their LEIs, MPC's control of MPLX, MPC's three reportable segments and its 13 refineries, from the FY2025 Form 10-K and GLEIF (EPM-DEC-001-0015, EPM-DEC-001-0033).
- Depends on `organization` 1.0.0-rc.1 by IRI (the candidate it shipped with); imports nothing.
