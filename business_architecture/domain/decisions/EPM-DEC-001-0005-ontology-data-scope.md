# EPM-DEC-001-0005: What the ontology holds: concepts and public reference facts, no records of what happened

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q6, Q11, Q19, Q26 |
| Source | Grilling session on the handover plan |

## Context

The anchor-company research produced many figures (capacities, margins, counts). The build needed a rule for which of them, if any, belong in the ontology.

## Decision

The ontology holds concepts, definitions, relationships, and publicly available reference facts about downstream companies and assets (for example MPC, its refineries, MPLX), each with a cited source. Stable numeric attributes of an entity, such as refinery capacity, an ownership share or a terminal count, are reference facts and carry an as-of date and a filing citation. The ontology holds no records of events or transactions ("Customer A bought 5 barrels") and no observed values of a measure over time ("the crack spread is $5"). Measure definitions are in scope; their values are not.

## Alternatives considered

No figures at all (the first reading of Q6 and Q11); public figures of every kind, including measure values.

## Hamid's recorded words

Q11: "We will not have the actual data. The ontology is only for concept structuring, definition, and relationship to enable semantic knowledge management system. We have Pricing domain KPI category or type such as Crack Spread. I will share them later." Q19: "I do want this kind of data. The data that I dont want is to say something like Crack Spread is $5 or something like Cusomer A bout 5 barrels of oil. I do want data that are oublickly available about the downstream oil and gas. So having the MPC, refrienery is fine where appropriate. [...] Excatly record of what happen is what we dont want in the ontology." Q26: Not commented on; agreed per Hamid's rule "If i dont comment on a question, it means I am aligned."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Evidence

All 44 competency questions (`business_architecture/ontology/competency-questions.md`) ask about concepts or structure; none needs an observed value.
