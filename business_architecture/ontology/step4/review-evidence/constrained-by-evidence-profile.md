# Constrained-by Evidence Profile

**Date:** 2026-09-28
**Basis:** Hamid 2026-09-26 review verdicts; dispositions from `target-dispositions-v2.csv` (verbatim).
**Scope:** Evidence only. No bucket moves. No verdict changes. No new match-type rows.

## Identity basis

Per Hamid 2026-09-28: `match_type` stays blank for all 11 rows (none are in `identity-scope-match-types.csv`; no default). Disposition and confidence are copied verbatim from `target-dispositions-v2.csv` — they are recorded here, not written into `match_type`.

`existing_verdict` below is the 2026-09-26 review, not `emission_decision`.

## Rows

| row_id | existing_verdict | raw_verb | stored_predicate | disposition | confidence |
|--------|-----------------|----------|-----------------|-------------|------------|
| REL-00015 | APPROVE | constrained-by | core:constrainedBy | ResolvedToConcept | StableIdentifier |
| REL-00018 | APPROVE | constrained-by | core:constrainedBy | ResolvedToConcept | StableIdentifier |
| REL-00024 | APPROVE | constrained-by | core:constrainedBy | ResolvedToConcept | StableIdentifier |
| REL-00087 | APPROVE | constrained-by | core:constrainedBy | SoleCandidate | CandidateOnly |
| REL-00091 | APPROVE | constrained-by | core:constrainedBy | SoleCandidate | CandidateOnly |
| REL-00097 | HOLD | constrained-by | core:constrainedBy | SoleCandidate | CandidateOnly |
| REL-00099 | APPROVE | constrains | core:constrainedBy (approved inversion) | SoleCandidate | CandidateOnly |
| REL-00103 | APPROVE | constrained-by | core:constrainedBy | ResolvedToConcept | StableIdentifier |
| REL-00574 | APPROVE | constrained-by | core:constrainedBy | ResolvedToConcept | StableIdentifier |
| REL-00894 | APPROVE | constrained-by | core:constrainedBy | SoleCandidate | CandidateOnly |
| REL-01284 | APPROVE | constrained-by | core:constrainedBy | ResolvedToConcept | StableIdentifier |

## Notes

- **REL-00099:** Raw verb is `constrains`. Stored predicate is the approved inversion to `core:constrainedBy`.
- **REL-00097:** Stays HOLD. Sole candidate is L1-refining; the author still has to name a specific target.
- **Verdict summary:** 10 APPROVE / 1 HOLD (REL-00097). Unchanged from #156.

## Assures

No new assures artifact per Hamid 2026-09-28. Merged PR #164 is the governing note: five approvals are nearness-only, #155 verdicts stay 5 APPROVE / 3 HOLD, no re-review, no bucket move, no Rule 6 gate. `shared-l3` and `sibling` stay out of the evidence profile.
