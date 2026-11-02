# technical-graph: the vocabulary of what was built

The `technical-graph` module defines the kinds of thing a technical graph records about a data platform as built, and the links between them: hosts, source databases, tables, views, metric views, pipeline steps, quality checks and agents (EPM-DEC-001-0112). It holds definitions only. The graph's nodes, row counts, refresh times and check results stay in the technical graph and its Delta copy, never in the ontology. Designed lineage stays in `data-product`; a built thing points to its design with `tg:designedAs`. Its namespace is `https://w3id.org/lsc/ontology/modules/technical-graph/`.

It answers competency questions 45 to 50 (`../competency-questions.md`, section XI): where a number comes from, whether it can be trusted today, what a change affects, whether it is built as designed, who answers for it, and which agent or report answers for a measure. The vocabulary cannot answer them alone, so `example/example-graph.ttl`, a small graph cut from the pricing demo's technical graph, is test data the regression runs them on. Live, the same queries (`../regression/queries/q45` to `q50`) run on the technical graph.

| File | What |
|---|---|
| `vocabulary.ttl` | 12 classes, the check-result code list and 22 properties. The platform layer is a value of `data-product`'s layer code list, not a list of its own. Measures are `kpi` measure definitions and systems are `system` systems, by IRI |
| `shapes.ttl` | The shapes a technical graph meets, checked with the `data-product`, `kpi` and `system` releases loaded |
| `build_example.py`, `example/example-graph.ttl` | The example: everything upstream of the metric views that compute the crack-spreads measure, with the agents, checks and steps that touch it, in the module's terms. It adds one test design so question 49 has an owner to find. `--verify` fails unless the file equals a fresh build. `scripts/check.sh` runs it |
| `test_technical_graph.py` | Tests: every term defined and cited, no layer list or owner property of its own, the example current and conforming, the demo's graph conforming in the module's terms, and a negative test for each shape |

**Who answers for it (question 49)** follows a built object's design to its data product, the process that produces it, and that process's Accountable role in `organization`. In the ontology today no path reaches an owner: the pricing data products record no producing process, and the two data products that do are produced by processes with no RACI assignment. On the demo's graph the question returns no rows.

**Status:** a candidate, not released. The decision owner approves its `1.0.0` (EPM-DEC-001-0112, item 6). Until then it has no package in `../releases/`, no store holds it, and the demo's technical graph keeps its own terms; the demo moves to the module's terms after the release.
