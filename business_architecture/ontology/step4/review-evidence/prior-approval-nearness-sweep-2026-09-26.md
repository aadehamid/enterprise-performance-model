# Prior-approval nearness-only sweep — 2026-09-26

Request: find every earlier approval whose target was matched by nearness only.

Method: census of all currently emitting `core:enabledBy` facts (126 facts / 126 rows),
cross-checked against (a) EN_ENABLEDBY_OVERRIDE, (b) S&T stored-emission controls,
(c) G3 Section A/B identity basis, (d) target-dispositions-v2 classifier disposition,
(e) raw mention text for stable identifiers, (f) source definitions for explicit
target-slug/label citation.

Result: **9 prior approvals rest on nearness-only targets.** All 9 raw mention texts
carry no stable identifier; all 9 classifier dispositions are SoleCandidate
("unique exact preferred-label match (candidate filter only, per PR #120)",
confidence CandidateOnly); no source definition or scope evidence names the target.
Every approval rationale is predicate plausibility, none establishes target identity.

Already superseded (4): REL-00428 (B2), REL-00437 (B3), REL-00770 (B3), REL-00939 (B4).

| Row | Prior approval | Candidate target | Identity evidence |
|---|---|---|---|
| REL-00129 | review32 2026-09-25 ("schedule exceptions produce exception records/causes that performance measurement explicitly analyzes") + G2 ExistingRowLevelApproval | Measure Production Scheduling Performance | nearness-only |
| REL-00243 | review32 2026-09-25 ("confirmation templates and controlled wording are direct prerequisites for confirmation generation") | Generate Confirms | nearness-only |
| REL-00304 | review32 2026-09-25 ("vessel/barge actualization produces actualized movement evidence used to identify demurrage/despatch/detention") | Identify Potential Demurrage | nearness-only |
| REL-00489 | st-enables 2026-09-26, reviewer-approved predicate change ("exchange utilization operates against the entitlement rules, differentials, contractual imbalance calculations, and governed agreement terms") | Manage Refined Product Exchanges | nearness-only |
| REL-00728 | review32 2026-09-25 ("IP framework defines the classification/handling basis under which protection operates") + G2 ExistingRowLevelApproval | Protect Intellectual Assets | nearness-only |
| REL-01006 | review32 2026-09-25 ("validated self-billing records are necessary inputs to revenue recognition, cutoff, accounting") | Perform Revenue Accounting | nearness-only |
| REL-01016 | review32 2026-09-25 ("corrected billing documents are necessary to accurate receivables, cash application, revenue accounting"); in EN_ENABLEDBY_OVERRIDE; B-population undecided | Manage Cash Application, A/R & Revenue Accounting | nearness-only |
| REL-01124 | st-enables 2026-09-26 ("validated feedstock-demand signal and coordinated requirements make relevant feedstock-trading action executable within the supply plan"); S&T stored control; B-population undecided | Trading Management | nearness-only |
| REL-01174 | st-enables 2026-09-26 ("quality-screened slates and validated quality information make execution of feedstock trading requirements feasible"); S&T stored control; B-population undecided | Coordinate Feedstock Trading | nearness-only |

Cleared by the sweep (not nearness-only): all Section A emitting approvals
(explicit-reference identity basis + row-level approval), REL-01056, REL-01303,
REL-00433, REL-01172 (A-approved + control-listed).

**No action taken on the 9 — each needs Hamid's verdict** (supersede under the
identity rule with formal supersession lineage, or confirm target identity with
source-backed evidence).
