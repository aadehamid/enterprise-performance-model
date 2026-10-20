# EPM-DEC-001-0062: Measure populations from MPC's own wording; the planner measures' populations parked

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency question 28 (what population is in a Named KPI, and what is out, in business words); Phase E of EPM-DEC-001-0052 |
| Source | Claude Code session, 2026-10-19 |

## Context

The kpi module holds each measure's definition, grain and basis, but no statement of what it includes and excludes. MPC's filings state it for the measures MPC defines: the regional R&M margin per barrel leaves out inter-refinery transfer volumes; refining operating costs exclude planned turnaround and depreciation and amortization; the crack spreads do not reflect the market cost of RINs (`business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 7, 8, 10, 14, 15, 16, 19 and 20). The planning team's list, the source of 33 measures, states no population. The kpi package is released (1.0.1), so a change to its tables needs a new release.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A small `population` module** states `pop:includes` and `pop:excludes` on the kpi module's measure IRIs, with the evidence row, without touching the released kpi tables.
2. **Eight measures, from MPC's wording:** R&M margin per barrel, margin capture, refining operating cost per barrel, distribution cost per barrel, turnaround cost per barrel, crack spreads, relative refining margin by region, and relative adjusted EBITDA per barrel.
3. **The planner measures' populations are parked.** Their source does not state them, and a population written from the definition would be a guess. Each can be added when its owner states it.
4. **Question 28 is answerable** for the measures whose source states a population, with the rest parked by this record. The next kpi release can take the statements into the kpi module.

## Alternatives considered

- **Add a population column to the kpi tables.** Not chosen now: the released package's check rebuilds from those tables, so the change belongs in the next kpi release, which needs the decision owner's approval.
- **Write populations for the planner measures from their definitions.** Not chosen, for the reason in item 3.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 7, 8, 10, 14, 15, 16, 19 and 20, and finding 5; EPM-DEC-001-0040, 0043.

## Consequences

- The regression stands at 34 answerable, 1 partial (Q7) and 9 waiting. Every waiting question waits on the decision owner: question 17 (EPM-DEC-001-0045) and questions 19 to 26, the Customer module (EPM-DEC-001-0004).
