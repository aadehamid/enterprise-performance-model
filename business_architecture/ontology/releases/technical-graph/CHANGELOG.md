# technical-graph changelog

## 1.0.0 (2026-11-02)

The module's first release, a major. Approved by the decision owner ("1. approve 1.0.0", saved in `step4/review-evidence/decision-owner-answers/answers-2026-11-02-follow-up-release.md`; EPM-DEC-001-0112, amendment of 2026-11-02, later). It defines the kinds of thing a technical graph records about a data platform as built, and the links between them (EPM-DEC-001-0112, item 2). Definitions only: the graph's nodes, row counts, refresh times and check results stay in the technical graph, never in the ontology.

- **12 classes:** `tg:TechnicalObject` and its kinds, from host and source database to table, view, metric view, definitions view, pipeline step, quality check, agent and orchestrator.
- **The check-result code list,** `tg:CheckResults`: pass, fail and differs.
- **22 properties,** 13 links and 9 values. Four reach other modules by IRI: `tg:designedAs` points a built thing to its design in data-product, `tg:layer` takes a value of data-product's layer code list, `tg:implements` names the kpi measure a metric view computes, and `tg:standsFor` names the system whose records a source database holds.
- **Its shapes,** checked with the data-product, kpi and system releases loaded.
- It answers competency questions 45 to 50, on the package plus the example graph in `technical-graph/example/`, which is test data and is not part of the package (the ontology skill's new-module rule 9).
- It requires data-product 1.2.0, kpi 1.3.0 and system 1.5.0, and imports no module.

### Known gaps

- **Who answers for it (question 49)** finds no owner in the ontology today: the pricing data products record no producing process, and the two data products that do are produced by processes with no RACI assignment.
- **The demo's technical graph keeps its own terms** until a later change moves it to this module's.
