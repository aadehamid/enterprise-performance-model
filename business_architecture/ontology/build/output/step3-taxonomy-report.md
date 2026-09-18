# Step 3 — SKOS taxonomy report

- Concepts: 680 (one per process-map node, stable document order)
- Triples: 3660
- `skos:broader` links: 678 (every concept except the two L0 roots)
- Top concepts: `L0-downstream-operations`, `L0-enabling-functions`
- `skos:notation` present: 669 (every ID'd node; original codes preserved)
- `skos:definition` present: 192 of 680 (1 triangulated APQC/EIA, 14 human-authored)
- Untagged literals: 0 (language policy holds)

## ConceptScheme
The core module namespace URI
`https://w3id.org/lsc/ontology/modules/core`
doubles as the `skos:ConceptScheme`. Rationale: the module's entire
current content *is* the taxonomy; one URI, one thing.

## Known gaps (not invented here)
- **Concepts without `skos:definition`.** The repo describes only 177
  nodes. Step 3b triangulates APQC element descriptions against public
  industry definitions (EIA glossary): where the two sources agree and
  the APQC link is strong, the APQC text is adopted with full
  `dcterms:source` provenance. Everything else stays definition-less
  until authored or human-reviewed — see `step3b-definition-review.csv`.
- `skos:narrower` is not materialized: it is `owl:inverseOf`
  `skos:broader` in the SKOS ontology, so it is entailed, not stored.
- RACI, systems, lanes, and other node fields are **not** in this file —
  they belong to Steps 4/5. This file is the taxonomy, nothing more.

## Validation (rdflib, mechanical)
Parsed clean; 680 concepts; exactly one `@en` prefLabel per concept;
every concept in scheme; 678 broader links, no dangling targets, no
self-references; 2 top concepts; zero untagged literals; Turtle
round-trip lossless.
