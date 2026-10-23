# EPM-DEC-001-0086: Q17 is parked until the ontology is first shared with business consumers; a business close-out package lists what the business must settle

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-23, for parking Q17 and for the package; its contents delegated under EPM-DEC-001-0028) |
| Date | 2026-10-23 |
| Questions | Competency question 17, "Who owns the meaning of a concept, and who only stewards the data?" (EPM-DEC-001-0045, decision 7); the items EPM-DEC-001-0083 lists as waiting on a process owner, the business or no named confirmer |
| Source | Claude Code session of 2026-10-23; `answers-2026-10-23-closeout.md` |

## Context

On 2026-10-18 the decision owner chose to settle who owns a concept's meaning through a separate governance decision with explicit assignments, kept apart from process RACI (EPM-DEC-001-0045, decision 7). No source in the repository, and none of MPC's filings, says who owns each concept's meaning, so the assignments have to come from the business. Q17 was the only competency question still waiting (EPM-DEC-001-0083). EPM-DEC-001-0019 counts a question parked by a recorded decision as green.

The decision owner already ruled the same way for four customer-system codes: they are settled when the ontology is shared for consumption, "at which point we will confirm what these means from the business" (EPM-DEC-001-0072, amendment of 2026-10-22).

## Decision

**The decision owner's decision:** Q17 is parked until the ontology is first shared with business consumers, and a package that goes with the ontology lists what to close out with the business.

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Q17 is parked.** `regression/expected.csv` gives it the status `parked:EPM-DEC-001-0086`. `regression/run.py` accepts that status, counts it as parked, and fails if a parked question lists a query. The regression now stands at 43 answerable, 0 partial, 0 waiting and 1 parked.
2. **The trigger** is the ontology's first sharing with business consumers. The business then names, for each module or concept scheme, the role that owns the meaning, the role that stewards the data and the role that keeps the systems. A minor release of `organization` then adds the qualified governance assignment that EPM-DEC-001-0045, item 7, proposes, and Q17 gets its queries.
3. **The package is `business_architecture/ontology/business-closeout.md`.** It lists each point only the business can settle: Q17; Market Data's accountable group (EPM-DEC-001-0046); the four codes and TID Nbr (EPM-DEC-001-0069, 0072); the product list (EPM-DEC-001-0088); Forecaster, Crude RFC, PSM and four working role definitions (EPM-DEC-001-0045); and the 33 measures with no stated population (EPM-DEC-001-0062). For each it gives what the ontology holds today, what the business needs to say, who can say it, and the record and module the answer goes to. It also lists, apart, the items parked for reasons that are not the business's.

## Alternatives considered

- **Build the meaning-owner relation now and assign later.** Not chosen by the decision owner: a relation with no assignments answers nothing, and Q17 would still wait.
- **Assign one meaning owner per module now.** Not chosen by the decision owner: it needs a role for every module from the business, which is the input this record waits for.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`: "I agree with 1. Can we document this as a package to go with the ontology so that we know what to close out with the business."

## Evidence

- EPM-DEC-001-0019, 0045, 0046, 0062, 0069, 0072, 0083.
- `business_architecture/ontology/competency-questions.md`, question 17.

## Consequences

- Every competency question is answerable or parked by a recorded decision, so Step 11 is all green.
- EPM-DEC-001-0045's item 7, EPM-DEC-001-0083's lists and the regression README carry dated notes.
- When the business answers a point in the package, its answer is recorded as an amendment to the record the package names.
