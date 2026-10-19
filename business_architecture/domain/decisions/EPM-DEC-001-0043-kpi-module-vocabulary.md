# EPM-DEC-001-0043: the kpi module's vocabulary: measure definitions, measure kinds, planning personas and process links

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | How the `kpi` module represents the measures classified in EPM-DEC-001-0042 |
| Source | Claude Code session, 2026-10-18 (night run) |

## Context

EPM-DEC-001-0040 seeds the `kpi` module from Hamid's planner measure list, and EPM-DEC-001-0042 classifies its 41 measures. The module now needs a vocabulary that answers the Named KPI competency questions (13, 14, 27 to 36) without holding a value (EPM-DEC-001-0005).

## Decision

1. **A measure is a `kpi:MeasureDefinition`**, also a `skos:Concept` in the scheme `kpi:Measures`, with one name, one definition and a notation equal to its row ID. It carries no value.
2. **Its kind comes from the code list `kpi:MeasureKind`**: the eight kinds of EPM-DEC-001-0042, exactly one per measure. A SHACL shape lets only a measure definition carry a kind, so Customer or a process cannot be classified as a KPI (competency question 13's "done when"). Another shape lets only an operational metric be a KPI candidate, and a third gives a tracker, report or non-measure no grain. Q13's locked "done when" ("Customer" cannot be classified as a KPI, and "3-2-1 Crack Spread" can) is read as a capability: a measure definition such as the crack spread can carry any kind, including `kpi`, and Customer can carry none. EPM-DEC-001-0042 gives the crack spread the kind market indicator; that is a classification, not a limit of the model.
3. **Comparison is an attribute, not a new measure.** `kpi:comparedAgainst` lists the plans, forecasts, plan versions or history a measure is asked against (competency question 30). `kpi:grain` and `kpi:basis` state the grain and, in words, the numerator, denominator and unit. The basis is a description; the ontology computes nothing (competency question 34's "without putting the formula in the ontology").
4. **"What it is not" is a link.** `kpi:notToBeConfusedWith` names a nearby measure that is often mistaken for this one, and the measure's `skos:scopeNote` says how they differ. The 3-2-1 crack spread links to R&M margin per barrel, margin capture and the R&M Margin Indicator (competency questions 32 and 36). Where the nearby thing is not a measure in the module (distillate sales, MPLX pipeline throughput, a contract tariff), the scope note says what the measure is not without a link; six measures carry a note of that kind. Aliases such as "the crack" are `skos:altLabel`.
5. **Personas are `org:Role` instances in the kpi module**, each with a plan type and a plan horizon. They stay out of the organization module, whose role register reconciles every role with the process map's RACI strings (EPM-DEC-001-0031); these four come from Hamid's list instead.
6. **`kpi:informsProcess` links a measure to the core processes it informs, as context, not certification** (competency question 38). Each link was chosen by matching the measure's use to a process name in `core` 2.0.0, for example demand against forecast to CM 1.1.1.1.5 Monitor Demand Forecasting Performance and Reporting, and margin capture to CM 1.1.5 Regional Backcasting and CM 1.3.5.1.4 Analyze Gaps Between Forecast & Actual Margins. Four measures have no link: the two capabilities parked as not measures, and MPC's two bonus KPIs, which no process in the map covers.
7. **The module is built, not released.** `build_measures.py` builds `measures.ttl` from three tables (`measure-classification.csv`, `measure-details.csv`, `personas.csv`) and `--verify` fails unless the file equals a fresh build. A first release would be 1.0.0, a major, which needs Hamid ("Major (including any deprecation): Hamid. No exceptions"). It is not released.

## Alternatives considered

- **A qualified node per persona and measure**, carrying each persona's horizon and comparison. Not chosen: the competency questions ask what a measure is and what it is compared against, not who compares it at which horizon. The persona's horizon sits on the persona.
- **Put the personas in the organization module.** Not chosen: see decision 5.
- **Record the formula.** Not chosen: competency question 34 asks for the concepts a measure quantifies "without putting the formula in the ontology".

## Hamid's recorded words

This record relies on Hamid's instructions in EPM-DEC-001-0040, saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "As far as Personae goes I dont wnat you to add names listed, but still represents the notion of persona". Everything in "Decision" is Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse it.

## Evidence

`business_architecture/ontology/kpi/` (the tables, `vocabulary.ttl`, `shapes.ttl`, `measures.ttl`, `test_measures.py`); EPM-DEC-001-0042 and its evidence; `core` 2.0.0 (`releases/core/2.0.0/core.ttl`) for the process IRIs; competency questions 13, 14 and 27 to 38.

## Consequences

- The regression loads the module. Q13, Q14, Q27, Q29, Q30, Q32, Q33 and Q36 are answerable and Q37 partial: 17 answerable, 6 partial, 21 waiting.
- The module's first release (1.0.0) waits for Hamid.
