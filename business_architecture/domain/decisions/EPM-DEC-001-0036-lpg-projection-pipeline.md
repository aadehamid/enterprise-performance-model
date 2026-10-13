# EPM-DEC-001-0036: Step 12: the property-graph projection pipeline

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-13 |
| Questions | Step 12: how the ontology is projected into Neo4j under the guideline in `lpg-projection/` (v2.1, Rule 4a), and what the pipeline proves |
| Source | Claude Code session, 2026-10-13, under Hamid's extension of the delegation to Steps 5 to 12 (EPM-DEC-001-0028, amended in #252) |

## Context

EPM-DEC-001-0020 adds Step 12: follow the guideline's pipeline (check, reason, load, verify), apply its Rules 1, 2, 3 and 5 from `core` 1.0.0 on, and use Rule 4a, qualified-relation nodes. EPM-DEC-001-0021 pins the guideline in `lpg-projection/`. The guideline's done-when: SHACL clean in the graph, an empty round-trip diff, and equal determinism hashes.

## Decision

`business_architecture/ontology/projection/pipeline.py` runs the guideline's five steps over `core` 1.0.0, the organization module and `ref-mpc`, with every shape file the build has:

1. **Check.** The five rules over the ontology, then pySHACL over the data with all the shapes, with SHACL-AF on. Any problem stops the build.
2. **Reason.** ELK through ROBOT 1.9.10, once. The OWL API writes declarations into the reasoner's output (`owl:NamedIndividual` on 2,086 instances, plus `owl:Class`, `owl:AnnotationProperty`, `owl:Thing`, `rdfs:Datatype`). They are not inferences about the domain, so `inferred.nt` drops any triple whose object is an OWL or RDFS built-in. Today that leaves no inferred triples: the ontology is SKOS-first and has almost no class axioms.
3. **Serialise.** Sorted, de-duplicated N-Triples and an input fingerprint (SHA-256 of `loadable.nt` and `inferred.nt`), recorded in `projection-manifest.json`.
4. **Load.** Neo4j 2025.06.2 with n10s 2025.06.1 and APOC, `n10s.rdf.import` of both files, with generated configuration and the fixed prefixes.
5. **Verify.** n10s SHACL in the graph, a round-trip diff, and two loads (sorted, and shuffled) whose hashes must match. The result is `projection-report.json`, which records the input fingerprint and a fingerprint of every shape file, so a change to either makes the committed report stale.

Choices where the guideline leaves room or does not fit the tools:

- **SHORTEN, not the guideline's MAP example.** In MAP mode, n10s 2025.06.1 would not import the shapes here: `n10s.validation.shacl.import.fetch` failed with "The graph is not namespace aware". The same mode is behind neosemantics issue #237 (open since 2021-11-09: SHACL not validating with `handleVocabUris` set to MAP); its fix, PR #361, is still open. In SHORTEN mode each name is the fixed prefix plus the local name (`skos__prefLabel`), so no two terms share a name (Rule 5) without a separate names file.
- **A subset of the shapes runs in the graph.** The in-graph subset leaves out `sh:datatype rdf:langString`, which n10s rejects, and `sh:not`, `sh:languageIn`, object and subject targets and `sh:node`, which it does not support. Step 1 checks all of them with pySHACL, SHACL-AF included (SPARQL targets such as core's `ProcessConcept`, and SPARQL constraints such as the scoped-sequence ancestor check), on every triple that is loaded: the asserted data and `inferred.nt`. Shapes with a SPARQL target do not run in the graph at all. A zero round-trip diff proves the graph holds those triples, so the full shapes hold in the graph. To show the in-graph check can fail, Step 5 removes one role's name and requires n10s to report it.
- **The round trip compares values, not spellings.** A plain literal and an `xsd:string` literal are the same (RDF 1.1). Integers load as INTEGER and return as `xsd:long`, and decimals load as FLOAT and return as `xsd:double` (guideline section 8). n10s keeps a language tag inside the stored string, and the export returns it untagged, so the comparison reads the tag back. The build refuses a source string that ends like a tag, and a decimal whose value, printed as a double, is not its own lexical form (0.64 prints back as 0.64; a decimal such as 0.1000000000000000055 would not).
- **Add-on C (exact decimals) is not adopted.** The one decimal property is the two-place ownership share, and no query computes with it. Adopt Add-on C if a decimal needs exact arithmetic.
- **Release gaps are listed, not hidden.** `core` 1.0.0 gives `core:earlierProcess` and `core:laterProcess` no `rdfs:range`, which breaks Rule 1. Only a new `core` release can fix that. The pipeline names both gaps with their fix and fails on any other gap, and on a listed gap that no longer occurs.
- **Steps 2, 4 and 5 run locally.** They need Java and a Neo4j container. `scripts/check.sh` runs Steps 1 and 3 and checks that the committed report matches the current inputs and passed.

The first run found a defect in `ref-mpc`, fixed in #261 (merged as d5eb311): its source nodes linked their URLs through `dcterms:source`, which core's source shape forbids.

### For Hamid

The next `core` release should add `rdfs:range skos:Concept` to `core:earlierProcess` and `core:laterProcess`. The pipeline then fails until the two listed gaps are removed.

## Alternatives considered

- **MAP mode with explicit names.** Rejected: the SHACL import failed in that mode (above).
- **Keep the OWL API declarations in `inferred.nt`.** Rejected: every instance would gain an `owl__NamedIndividual` label and nothing about the domain.
- **Skip the in-graph SHACL.** Rejected: the guideline requires it; the subset plus the round trip keeps the guarantee.

## Hamid's recorded words

Hamid extended the delegation in the Claude Code session on 2026-10-13 (saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/delegation-steps-5-12.md`): "yes, extend the delegation to steps 5 to 12." Hamid did not make the choices above himself. Claude made them under that delegation, and Hamid can reverse any of them.

## Evidence

EPM-DEC-001-0020, 0021, 0033; `lpg-projection/Ontology_to_LPG_Conversion_Playbook.md` (v2.1), sections 3, 5, 7 and 8; ROBOT v1.9.10 (https://github.com/ontodev/robot/releases/tag/v1.9.10, 2026-02-18); n10s 2025.06.1 (https://github.com/neo4j-labs/neosemantics/releases/tag/2025.06.1, 2026-06-16); Neo4j 2025.06.2 (tag 2025.06.2, "Release 2025.06.2", 2025-07-11, https://github.com/neo4j/neo4j/releases/tag/2025.06.2); `projection-report.json`.

## Consequences

- `scripts/check.sh` runs `pipeline.py build --verify` and `test_pipeline.py`. A change to any input or shape file fails it until the pipeline is rerun and the manifest and report are committed.
- The graph can be rebuilt from the Turtle files at any time; Turtle stays the master copy.
