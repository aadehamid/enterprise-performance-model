# EPM-DEC-001-0044: Step 9: one evidence node per canonical fact, the controlled-value shapes in the release, and core 2.1.0

| Field | Value |
|---|---|
| Status | Decided (Hamid, 2026-10-18: the shapes, the evidence pattern and cutting 2.1.0; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-18 |
| Questions | Step 9 walkthrough (`decision-packages/2026-10-14/step9-walkthrough.md`), questions 1 and 2; whether Claude may cut the minor release |
| Source | Claude Code session, 2026-10-18 |

## Context

EPM-DEC-001-0035 left two things for Hamid: approving the eleven controlled-value shapes, and choosing how canonical facts carry their evidence in the next `core` release. The walkthrough set out both. `core` 2.0.0 holds 640 canonical facts on nine predicates, supported by 812 workbook rows, which sat only in `releases/core/1.0.0/canonical-facts.csv`.

## Decision

**Hamid's decisions:**
1. Approve the eleven controlled-value shapes as written and include them in the next `core` release, keeping the existing release constraints.
2. Add one evidence node per canonical fact and keep the direct triple. Each node names exactly one subject, predicate and object and carries every distinct supporting REL ID, in a new evidence property, not `core:sourceRow`. Triples and nodes come from one mapping, with the checks his answer lists. The evidence mapping travels with the release.
3. Cut the minor release, `core` 2.1.0.

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Names.** `core:CanonicalFact`, with `core:factSubject`, `core:factPredicate`, `core:factObject` and `core:evidenceRow`. Fact IRIs are `https://w3id.org/lsc/ontology/fact/<subject>--<predicate>--<object>`, so a fact's IRI follows its triple.
2. **One build.** `release/build_core_2_1.py` reads the 1.0.0 canonical-fact mapping, stops unless its 640 rows are exactly the 640 direct triples of 2.0.0, and then writes one node per row. The mapping ships in the package as `canonical-facts.csv`.
3. **Hamid's seven checks.** Fact structure, predicate scope, evidence presence and both directions between triple and node are release shapes (`shp:CanonicalFact`, `shp:CanonicalTriple`). Evidence correctness is a build check (`evidence_problems`): a node's rows must equal the mapping's rows for that exact fact, so a well-formed REL ID on the wrong fact fails. Reproducibility is `--verify` in `scripts/check.sh`. `release/test_build_core_2_1.py` breaks each check once and shows it fails.
4. **The controlled-value shapes** are appended to the release shapes verbatim. They check scheme membership; no `sh:maxCount 1` is put on `skos:inScheme`. `validation/test_controlled_values.py` now reads `core` 2.1.0 and counts `core:businessDomain` as covered by the release's own shape from 2.0.0.
5. **Rights.** The header's dangling `dcterms:license` gives way to `dcterms:rights`: all rights reserved, with APQC's attribution (EPM-DEC-001-0041). This removes a triple, but only one that named no licence text, so the release stays minor.
6. **Consumers.** The projection (Rule 4a now names `core:CanonicalFact`) and the regression read 2.1.0. The projection was rerun end to end on Neo4j 2025.06.2 with n10s 2025.06.1: 2,811 nodes and 14,862 relationships, no SHACL violation in the graph, an empty round-trip diff, equal hashes for two load orders. The regression is unchanged: 9 answerable, 5 partial, 30 waiting.

## Alternatives considered

- **2b, the node alone.** Not chosen by Hamid; it would remove triples queries read (a major).
- **Reuse `core:sourceRow`.** Not chosen: its domain is the scoped sequence, so a reasoner would type every fact node as one.
- **Check evidence correctness in SHACL.** Not chosen: the shapes cannot know which row supports which fact without loading the mapping into the graph; the build check reads it directly.

## Hamid's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "1a, 2a." and "Add one evidence node per canonical fact and keep the direct triple." His approval of the cut is saved in `answers-2026-10-18-night.md`: "Yes, cut 2.1.0 (Recommended)". Items 1 to 6 under "What follows" are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`decision-packages/2026-10-14/step9-walkthrough.md`; EPM-DEC-001-0014, 0020, 0035, 0041; `releases/core/2.1.0/` (manifest, changelog, counts); `projection/projection-report.json`.

## Consequences

- EPM-DEC-001-0035's evidence-link item is done. Step 9's three shape sets (EPM-DEC-001-0014) are all in a release.
- The next `organization` release carries the RACI level shape in its own shapes as well.
