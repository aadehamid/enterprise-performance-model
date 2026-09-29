# Step 4 Supersession Register (consolidated 2026-09-29)

All row-level verdict supersessions across the Step 4 review, reconciled
from `step4-decisions.md` and `ledger-v2.md` on main `1c8c1a09`.

Principle (Hamid 2026-09-26): a prior row-level verdict may be superseded
when a newly approved gate/control exposes a missing required premise.
The old decision remains traceable with its reason, date, and superseding
decision — retained in provenance as superseded, never deleted.

## Governed-by: 10 supersessions (Hamid 2026-09-26)

Pattern: **Supersedes2026-09-25Approval**
Verdict: HOLD / D:hamid-verdict / NoAffirmativeCitation

| Row | Superseded rationale (retained in provenance) |
|---|---|
| REL-00050 | "Inventory monitoring operates against policy-set min/max/safety-stock/operating-limit rules (set-versus-apply)." |
| REL-00067 | "Replenishment explicitly operates within approved inventory policies and projected stock against policy levels." |
| REL-00394 | "External compliance monitoring checks obligations against the exact compliance policies/procedures." |
| REL-00399 | "Internal trade-control monitoring verifies controls against compliance-program requirements and policies." |
| REL-00406 | "RIN reporting coordination operates under trading compliance program requirements, reporting controls, escalation model." |
| REL-00907 | "SCOPE: IP, licensing, protected-mark, and Legal/IP governance boundaries only." Scope condition lapses. |
| REL-00937 | "Financing/payment-method definition depends on Treasury-approved instruments and Credit-approved exposure/eligibility rules." |
| REL-01005 | "Self-billing operates only under executed agreements; commercial terms/contracts establish the governing agreement framework." |
| REL-01228 | "SCOPE: trading-compliance, reporting, market-rule, and policy boundaries applicable to confirmations." Scope condition lapses. |
| REL-01256 | "SCOPE: credit-control gates within fulfillment (no-self-exception rule)." Scope condition lapses. |

All ten routed to source workbooks for correction.

## Triggers: 11 supersessions (Hamid 2026-09-26)

Pattern: **Supersedes2026-09-26Approval**
Verdict: HOLD / D:hamid-verdict / NoAffirmativeTriggerLink

| Row | Reason |
|---|---|
| REL-00049 | Exclusion/boundary: scope excludes replenishment planning; not an invoking event. |
| REL-00291 | States where limit actions happen, not that monitoring findings trigger them. |
| REL-00892 | Boundary-only citation; no event-to-target link. |
| REL-00163 | States where amendments are done, not that findings start them. |
| REL-00169 | No slug/label/range citation. |
| REL-00170 | No slug/label/range citation. |
| REL-00252 | No slug/label/range citation. |
| REL-00396 | Sibling nearness alone is not a route for `triggers`. |
| REL-00398 | Sibling nearness alone is not a route for `triggers`. |
| REL-00400 | Sibling nearness alone is not a route for `triggers`. |
| REL-00403 | Sibling nearness alone is not a route for `triggers`. |

All eleven routed to source workbooks for correction.

## Precedes/follows: 20 supersessions (Hamid 2026-09-27, amending 2026-09-26)

Pattern: **Supersedes2026-09-26Approval**
Verdict: HOLD / D:hamid-verdict
All 20 facts verified unique single-row; zero knock-on.

| Row | Reason |
|---|---|
| REL-01223 | ExclusionBoundaryCitation — "owned by Regional Optimization"; boundary, not sequence. |
| REL-01227 | ExclusionBoundaryCitation — "excludes settlement"; boundary, not sequence. |
| REL-01241 | ExclusionBoundaryCitation — "Excludes the monthly plan itself"; boundary, not sequence. |
| REL-01289 | ExclusionBoundaryCitation — "Excludes trade capture"; boundary, not sequence. |
| REL-01291 | ExclusionBoundaryCitation — "Excludes settlement and invoicing"; boundary, not sequence. |
| REL-01294 | ExclusionBoundaryCitation — target in boundary dump; no sequence verb. |
| REL-00008 | "owned by Regional Optimization" — who owns what, not sequence. |
| REL-00068 | "owned by Physical Distribution Scheduling" — not sequence. |
| REL-00112 | "owned by Refinery Planning and Optimization" — not sequence. |
| REL-00149 | "owned by Perform RINs/REC Actualization" — not sequence. |
| REL-00184 | "may be handled by" — conditional, not affirmative sequence. |
| REL-00188 | Target in branch list, then excluded — not sequence. |
| REL-00193 | "excludes confirmation with the counterparty" — exclusion. |
| REL-00200 | "excludes storage settlement" — exclusion. |
| REL-00206 | "excludes confirmation" — exclusion. |
| REL-00307 | Reference-data usage + "Excludes lease contract administration" — boundary. |
| REL-00319 | "Excludes trade capture" — exclusion. |
| REL-00351 | "Excludes transmission deal capture" — exclusion. |
| REL-00374 | "Excludes settlement calculation and invoice validation" — exclusion. |
| REL-00930 | "Out of scope: Quote content composition" — exclusion. |

All 20 routed to source workbooks for correction.

## Requires: 0 active supersessions

REL-00208 is a plain HOLD (D:hamid-verdict 2026-09-25), not a supersession.
The one requires-row supersession (REL-00873) was reversed — see below.

## Enables prior-approval supersessions: 13 (2026-09-26)

Not "enables G3" — these are the enables nearness-only prior approvals
superseded across G3 B2–B5. Seven of the thirteen sit inside the 96
Section B holds; they are not disjoint sets.

| Row | Pattern | Population |
|---|---|---|
| REL-00428 | Supersedes2026-09-25Review32Approval | G3 B2; removed from EN_ENABLEDBY_OVERRIDE. |
| REL-00437 | Supersedes2026-09-26 (S&T) | G3 B3; moved to hold control list. |
| REL-00770 | Supersedes2026-09-25Approval | G3 B3. |
| REL-00939 | Supersedes2026-09-25Approval | G3 B4; removed from EN_ENABLEDBY_OVERRIDE. |
| REL-00129 | Supersedes2026-09-25Review32Approval | G2 (outside Section B). |
| REL-00728 | Supersedes2026-09-25Review32Approval | G2 (outside Section B). |
| REL-00243 | Supersedes2026-09-25Review32Approval | review32 (outside Section B). |
| REL-00304 | Supersedes2026-09-25Review32Approval | review32 (outside Section B). |
| REL-01006 | Supersedes2026-09-25Review32Approval | review32 (outside Section B). |
| REL-00489 | Supersedes2026-09-26STApproval | G1b (outside Section B); workbook backlog. |
| REL-01016 | Supersedes2026-09-25Review32Approval | Section B; removed from EN_ENABLEDBY_OVERRIDE. |
| REL-01124 | Supersedes2026-09-26STApproval | Section B; S&T stored controls removed. |
| REL-01174 | Supersedes2026-09-26STApproval | Section B; S&T stored controls removed. |

## Reversed supersession

| Row | Verb | History |
|---|---|---|
| REL-00873 | requires | Superseded 2026-09-26 (no rule 5 route); fact removed. **REVERSED 2026-09-26**: corrected citation test found the scope note names the target's exact unique prefLabel affirmatively. Fact restored. |

## Totals

- Active supersessions: **54** (10 governed-by + 11 triggers + 20 precedes/follows + 13 enables prior-approval)
- Reversed: **1** (REL-00873, requires)
- Requires active: 0 (REL-00208 is a plain HOLD)
- All superseded rationales retained in provenance, never deleted.

Pre-reviewed by Cursor EPM on Slack (labeling and population corrections applied before raising).
