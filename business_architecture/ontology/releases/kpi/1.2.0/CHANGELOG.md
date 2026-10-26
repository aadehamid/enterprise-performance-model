# kpi changelog

## 1.2.0 (2026-10-25)

A minor release: it adds an identifier, notes and top-concept statements, narrows one measure's definition and label, removes one alternative label, and removes no IRI. Approved by the decision owner with item F's release plan ("Approve the plan (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`; EPM-DEC-001-0097, 0100).

- [minor] **KPI-0001.** Crack Spreads Pricing carries `dcterms:identifier` "KPI-0001", the crack-spread Genie agent's identifier, with a note: the gold table's constant `KPI_ID` value "KPI Crack Spread 3-2-1" labels all 127 series alike, so it names the measure (EPM-DEC-001-0097, item 3).
- [minor] **Additional Market Prices** is narrowed to renewables and NGLs: its label is now "Additional Market Prices (Renewables, NGLs)", and its definition and classification reason change; benchmark and crude prices are Crude Market Pricing's (EPM-DEC-001-0097, item 4). The slug stays, and a change note keeps the planner list's name. It stays a market indicator.
- [patch] **R&M Margin Indicator** drops its alternative label, which repeated its preferred label (SKOS S13; EPM-DEC-001-0098, item 3). The build now refuses such an alias.
- [minor] **Top concepts** (EPM-DEC-001-0098, item 5): every measure of `kpi:Measures` and every kind of `kpi:MeasureKind`, stated both ways.
- It requires core 2.3.0, the current release.

## 1.1.1 (2026-10-23)

A patch: one range, and no IRI changes. Approved by the decision owner with the close-out releases ("Approve all six (Recommended)", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md`; EPM-DEC-001-0088, 0093).

- [patch] `pop:populationEvidence` gains `rdfs:range xsd:string`, the datatype every value already has, closing its projection gap (EPM-DEC-001-0036).
- It requires core 2.3.0, the current release.

## 1.1.0 (2026-10-22)

Minor. Approved by the decision owner with the release plan ("release plan approved", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md`; EPM-DEC-001-0079). No IRI changes and nothing is removed.

- [minor] **The eight measure populations** (EPM-DEC-001-0062) join the package: what each MPC-defined measure includes and excludes, in MPC's wording, with the evidence row (`population/vocabulary.ttl`, `population/population.ttl`). They keep their `pop:` IRIs, which the integration package's consumer rules and the regression name.
- [minor] **The measure shape is closed:** a measure carries only its definition, classification, links and population, so no value, target or actual can be stated on one (EPM-DEC-001-0005). Every released measure already conforms. Cardinalities are stated for the three population properties.
- Requires core 2.2.0 (1.0.1 required 2.1.0); the 41 measures and their process links are unchanged on it.

## 1.0.1 (2026-10-19)

Patch. The source that the 32 planner-list measures and the four personas cite now names the product the list was written for: Value Chain Optimization Decision Support and Visualization (VCO DSV), with "VCO DSV" as its short name. The decision owner: "It should be "Value Chain Optimization Decision Support and Visualization (VCO DSV)"" (saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-19-vco-dsv.md`). The source keeps its IRI; only its title and short name change. Released under the decision owner's standing approval ("You have my approval to keep going and release things as needed. while I am out", `answers-2026-10-19-releases.md`). Requires core 2.1.0, as 1.0.0 did.

## 1.0.0 (2026-10-19)

The module's first release, a major. Approved by the decision owner ("Approve kpi 1.0.0 release too", saved in `step4/review-evidence/decision-owner-answers/answers-2026-10-19-kpi.md`; their standing release approval is in `answers-2026-10-19-releases.md`). It holds the vocabulary and 41 measure definitions: 32 from the decision owner's planner measure list, 8 that MPC publishes and 1 from industry practice. Each is classified by kind (EPM-DEC-001-0042), with its personas and the core processes it informs, as context (EPM-DEC-001-0043). Definitions only, never values (EPM-DEC-001-0005). It requires core 2.1.0.
