# LPG projection guideline (snapshot)

These two files are a pinned copy of Hamid's guideline for projecting a W3C
ontology into a Neo4j labelled property graph (LPG). The master copy is in
the enterprise-people-graph repo. This folder is not edited here. To update
it, change the master first, then copy the files again and record the new
commit below (EPM-DEC-001-0021).

| File | What it is |
|---|---|
| `Ontology_to_LPG_Conversion_Playbook.md` | The conversion method: five design rules, a five-step pipeline (check, reason, flatten, load, verify), add-ons and anti-patterns |
| `Ontology_Skills_for_LPG_Mapping.md` | The learning guide that goes with it: twelve skills in priority order, with exercises and resources |

| Field | Value |
|---|---|
| Source | https://github.com/aadehamid/enterprise-people-graph/tree/main/guideline_to_map_ontology_to_LPG |
| Pinned commit | `e7b09e8` (v2.1; earlier pin `cd63e12`, v2) |
| Guideline version | v2.1, October 2026 |
| Copied | 2026-10-06 (v2 first copied 2026-10-05) |

## How this build uses it

The ontology playbook (`../ontology-playbook.md`, Step 12 and §2) is the
authority for how this build applies the guideline. In short
(EPM-DEC-001-0020):

- Rules 1, 2, 3 and 5 apply from the `core` 1.0.0 release on.
- For Rule 4, the build uses option 4a, qualified-relation nodes, which v2.1
  makes the default. When a relationship needs its own properties, the build
  models it as a node with its own IRI that points at both ends. Option 4b
  (RDF 1.2 reifiers) is not used, because the build's Python tools (rdflib,
  pySHACL) cannot read RDF 1.2. With 4a, Step 3 of the pipeline only
  serialises the files; the flatten queries are not needed.
- The pipeline runs once the ontology is built (Step 12). Turtle stays the
  master copy.

## Points checked on 2026-10-05 (resolved in v2.1)

The external check of v2 found two statements that needed care: v2 called
RDF 1.2 reifiers "now the standard pattern", and it listed rdflib as "in
progress" for RDF 1.2. Guideline v2.1 (enterprise-people-graph PR #1) fixed
both. It states that RDF 1.2 is a W3C Candidate Recommendation (Snapshot of
7 April 2026), that Apache Jena 6.1.0+ and Eclipse RDF4J 6.0.0+ support it,
and that rdflib and pySHACL do not. Three older pipeline defects that v2.1
did not change are tracked in enterprise-people-graph issue #2.
