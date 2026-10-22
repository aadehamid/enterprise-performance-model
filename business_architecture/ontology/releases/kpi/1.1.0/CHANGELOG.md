# kpi changelog

## 1.1.0 (2026-10-22)

Minor. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0079). No IRI changes and nothing is removed.

- [minor] **The eight measure populations** (EPM-DEC-001-0062) join the package: what each MPC-defined measure includes and excludes, in MPC's wording, with the evidence row (`population/vocabulary.ttl`, `population/population.ttl`). They keep their `pop:` IRIs, which the integration package's consumer rules and the regression name.
- [minor] **The measure shape is closed:** a measure carries only its definition, classification, links and population, so no value, target or actual can be stated on one (EPM-DEC-001-0005). Every released measure already conforms. Cardinalities are stated for the three population properties.
- Requires core 2.2.0 (1.0.1 required 2.1.0); the 41 measures and their process links are unchanged on it.

## 1.0.1 (2026-10-19)

Patch. The source that the 32 planner-list measures and the four personas cite now names the product the list was written for: Value Chain Optimization Decision Support and Visualization (VCO DSV), with "VCO DSV" as its short name. The decision owner: "It should be "Value Chain Optimization Decision Support and Visualization (VCO DSV)"" (saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-19-vco-dsv.md`). The source keeps its IRI; only its title and short name change. Released under the decision owner's standing approval ("You have my approval to keep going and release things as needed. while I am out", `answers-2026-10-19-releases.md`). Requires core 2.1.0, as 1.0.0 did.

## 1.0.0 (2026-10-19)

The module's first release, a major. Approved by the decision owner ("Approve kpi 1.0.0 release too", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-19-kpi.md`; their standing release approval is in `answers-2026-10-19-releases.md`). It holds the vocabulary and 41 measure definitions: 32 from the decision owner's planner measure list, 8 that MPC publishes and 1 from industry practice. Each is classified by kind (EPM-DEC-001-0042), with its personas and the core processes it informs, as context (EPM-DEC-001-0043). Definitions only, never values (EPM-DEC-001-0005). It requires core 2.1.0.
