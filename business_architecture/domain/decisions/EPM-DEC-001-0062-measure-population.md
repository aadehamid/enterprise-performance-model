# EPM-DEC-001-0062: Measure populations from MPC's own wording; the rest parked where no source states one

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency question 28 (what population is in a Named KPI, and what is out, in business words); Phase E of EPM-DEC-001-0052, its Step 11 item (every competency question answerable or parked by decision) |
| Source | Claude Code session, 2026-10-19 |

## Context

The kpi module holds each measure's definition, grain and basis, but no statement of what it includes and excludes. MPC's filings state it for the measures MPC defines: the regional R&M margin per barrel leaves out inter-refinery transfer volumes; refining operating costs exclude planned turnaround and depreciation and amortization; the crack spreads do not reflect the market cost of RINs (`business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 7, 8, 10, 14, 15, 16, 19 and 20). The other 33 measures have no stated population: 31 from the planning team's list (crack spreads is on that list too, but MPC states what its benchmark excludes), the R&M Margin Indicator, whose formula MPC publishes nowhere, and turnaround lost margin, from the industry evidence. The kpi package is released (1.0.1), so a change to its tables needs a new release.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **A small `population` module** states `pop:includes` and `pop:excludes` on the kpi module's measure IRIs, with the evidence row, without touching the released kpi tables.
2. **Eight measures, from MPC's wording:** R&M margin per barrel, margin capture, refining operating cost per barrel, distribution cost per barrel, turnaround cost per barrel, crack spreads, relative refining margin by region, and relative adjusted EBITDA per barrel.
3. **The other 33 measures' populations are parked.** No source states them, and a population written from the definition would be a guess. Each can be added when its owner states it.
4. **A seventh may-answer rule** joins the consumer rules (EPM-DEC-001-0061): what a measure includes and excludes, where its source says so, relying on `pop:includes`, `pop:excludes` and `pop:populationEvidence`.
5. **Question 28 is answerable** for the measures whose source states a population, with the rest parked by this record. The next kpi release can take the statements into the kpi module. *2026-10-22:* `kpi` 1.1.0 carries them, with their `pop:` IRIs (EPM-DEC-001-0079).

## Alternatives considered

- **Add a population column to the kpi tables.** Not chosen now: the released package's check rebuilds from those tables, so the change belongs in the next kpi release, which needs the decision owner's approval. *2026-10-22:* under the module policy (worklog, "Who approves a release"; EPM-DEC-001-0037), a minor or patch release is the module owner's and a major the decision owner's; Claude asked the decision owner before every release issued on 2026-10-22 (EPM-DEC-001-0074, and 0076 to 0080). The populations shipped in kpi 1.1.0, a minor (EPM-DEC-001-0079).
- **Write populations for the other measures from their definitions.** Not chosen, for the reason in item 3.

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 7, 8, 10, 14, 15, 16, 19 and 20, and finding 5; EPM-DEC-001-0040, 0043.

## Consequences

- The regression stands at 34 answerable, 1 partial (Q7) and 9 waiting. Every waiting question waits on the decision owner: question 17 (EPM-DEC-001-0045) and questions 19 to 26, the Customer module (EPM-DEC-001-0004). *2026-10-21:* the decision owner's customer information arrived, so questions 19 to 26 now wait on the plan's pull request 5, which answers them after the `party` module and its data (pull requests 2 to 4; EPM-DEC-001-0067, item 13), not on the decision owner. *2026-10-21:* the plan's pull request 5 made Q19 to Q26 answerable: 42 answerable, 1 partial (Q7), 1 waiting (Q17) (EPM-DEC-001-0071).
