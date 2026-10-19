# core changelog

## 2.1.0 (2026-10-18)

A minor release: it adds terms and shapes and removes nothing that queries read. Built from the released 2.0.0 graph; 2.0.0 is unchanged. It carries out the decision owner's Step 9 answer of 2026-10-18, "1a, 2a", and they approved cutting it the same day (EPM-DEC-001-0044; their words in `step4/review-evidence/decision-owner-answers/answers-2026-10-18.md` and `answers-2026-10-18-night.md`).

- [minor] **Evidence on canonical facts.** New class `core:CanonicalFact` and properties `core:factSubject`, `core:factPredicate`, `core:factObject` and `core:evidenceRow`. One node per canonical fact (640), each naming exactly one subject, predicate and object and carrying every workbook row that supports it (812 rows; 172 facts rest on two or more). The direct triples stay. Nodes and triples come from one mapping, the core 1.0.0 canonical-fact mapping, which this package carries as `canonical-facts.csv`. Approved: The decision owner, 2026-10-18.
- [minor] **Controlled-value shapes.** The eleven shapes of `validation/controlled-values.ttl` join the release shapes: each code-list value must be in its own list (`skos:inScheme`). The 2.0.0 constraints stay; these supplement them. The RACI level shape fires only when the organization module's data is loaded with core. Approved: The decision owner, 2026-10-18.
- [minor] **Canonical-fact shapes.** Each fact names exactly one subject, predicate and object; the predicate is one of the nine canonical relationship predicates; it carries at least one REL ID; the graph holds its direct triple; and every canonical triple has exactly one fact node.
- [patch] **Rights.** The header's `dcterms:license` pointed at an IRI that no file describes. It is replaced by a `dcterms:rights` statement: all rights reserved, proprietary (EPM-DEC-001-0041), with APQC's attribution. The DCAT record carries the same statement.
