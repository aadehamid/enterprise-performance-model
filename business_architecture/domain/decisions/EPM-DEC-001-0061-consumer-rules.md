# EPM-DEC-001-0061: Rules for consumers: the catalog binding, and what an agent may answer and must refuse

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency questions 35 (how a catalog row points at a Named KPI, and what must exist first), 41 (what an agent may answer without reading a table or inventing a formula) and 42 (what it must refuse); Phase E of EPM-DEC-001-0052, its Step 11 item (every competency question answerable or parked by decision) |
| Source | Claude Code session, 2026-10-19 |

## Context

The questions say what the answers must cover. Question 42 names three refusals: "calculate a crack from legs, treat a report column as the KPI, answer 'who is the customer' without a role". Question 35 asks for a binding and its preconditions. The graph now defines measures with kinds (EPM-DEC-001-0042, 0043), data products (0053), series with recipes (0057), placement kinds (0058) and source tiers (0059). Values stay in the systems (EPM-DEC-001-0005). The session 5 handoff listed the agent rules among the decision owner's open questions; for this session the decision owner delegated everything except four named items, and the agent rules are not among them ("Everything else is delegated under EPM-DEC-001-0028.").

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**
1. **The catalog binding (35).** `con:publishesMeasure` points from the data product that publishes a measure's values to the measure's IRI. A shape requires both ends to be defined first: the measure in the kpi module, the data product in the data-product module. No binding is recorded yet, because no source says which data product publishes which measure.
2. **What an agent may answer (41)**, from the graph alone: what a thing is (definition, names, kind); what a measure is not; where a thing sits and what the placement claims; what a series is built from; who is responsible for a process; which source says so and which one wins.
3. **What an agent must refuse (42):** computing or quoting a value; building a crack from its legs; treating a report column or a KPI candidate as a KPI; naming the customer without a role; presenting a context placement as ownership. The first three come from the question's own words; the last two follow from EPM-DEC-001-0042 and 0058.
4. **Each rule names the graph terms it relies on,** so a test can check that they exist.

## Alternatives considered

- **Park 41 and 42 for the decision owner.** Not chosen: the decision owner delegated everything outside four named items, and the questions themselves give the refusals. They can reverse or extend the rules.
- **Record bindings for the measures MPC publishes.** Not chosen: no source names the data product that holds each measure's values.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-19-completion-goal.md`: "Everything else is delegated under EPM-DEC-001-0028." The delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/ontology/competency-questions.md`, questions 35, 41 and 42; EPM-DEC-001-0004, 0005, 0042, 0043, 0053, 0057, 0058, 0059.

## Consequences

- The regression stands at 33 answerable, 1 partial (Q7) and 10 waiting: question 17 waits on EPM-DEC-001-0045 and questions 19 to 26 on the Customer module (EPM-DEC-001-0004).
- Question 28 (population) is the only Step 7 question still waiting.
