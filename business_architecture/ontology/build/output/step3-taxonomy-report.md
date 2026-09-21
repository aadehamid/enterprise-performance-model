# Step 3 — SKOS taxonomy report

- Concepts: 680 (one per process-map node, stable document order)
- Triples: 14397
- `skos:broader` links: 678 (every concept except the two L0 roots)
- Top concepts: `L0-downstream-operations`, `L0-enabling-functions`
- `skos:notation` present: 669 (every ID'd node; original codes preserved)
- `skos:definition` present: 675 of 680 (0 triangulated APQC/EIA, 0 human-authored L1-L3, 498 workbook-approved)
- Workbook overlay: 498 approved rows (definitions, scope notes, 307 altLabels, 498 APQC references, intake annotations); 3 blocked rows (definition-less, parked); 1 retired row(s) marked owl:deprecated
- Untagged literals: 0 (language policy holds)

## ConceptScheme
The core module namespace URI
`https://w3id.org/lsc/ontology/modules/core`
doubles as the `skos:ConceptScheme`. Rationale: the module's entire
current content *is* the taxonomy; one URI, one thing.

## Workbook overlay (Step 3c)
Approved workbook rows overlay the taxonomy with definition precedence
workbook > human-authored L1–L3 > step3b adoption > repo description.
Each approved row contributes: `skos:definition`, `skos:scopeNote`
(scope note with in/out-of-scope boundaries folded in),
`skos:altLabel`s, a `dcterms:references` link to the APQC PCF element,
`dcterms:source` provenance, and verbatim Phase-1 capture under the
provisional `intake:` namespace
(`https://w3id.org/lsc/ontology/intake/` — level, keyInputs,
primaryOutput, relatedConcepts, responsibleDomain, processHorizon,
primaryPurpose, referenceSources, terminologyNotes, conceptTypeCheck,
parkedChildren, apqcDecision, status).
These annotations are explicitly NOT the Step 4 model: they preserve the
reviewer's text in the graph so nothing is lost, and Step 4 promotes them
to real properties between concept URIs. `intake:level` carries the locked
L0–L6 taxonomy level; `intake:apqcDecision` records the mapping call
(REVIEW LINK / ADOPTED / REJECTED / NO CANDIDATE / NO SOURCE) — REJECTED
rows are the deliberate APQC divergences (competency Q12).
Blocked rows appear with `intake:status "blocked"` and no definition
(the locked rule: a parked row must not carry one). Retired rows are
`owl:deprecated` (not deleted, per version policy); `dcterms:isReplacedBy`
is left for the Step 3d tree pass, when destinations are decided.

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
