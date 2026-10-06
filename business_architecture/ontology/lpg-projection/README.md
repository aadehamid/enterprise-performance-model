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
| Pinned commit | `cd63e12` |
| Guideline version | v2 (RDF 1.2 edition), October 2026 |
| Copied | 2026-10-05 |

## How this build uses it

The ontology playbook (`../ontology-playbook.md`, Step 12 and §2) is the
authority for how this build applies the guideline. In short
(EPM-DEC-001-0020):

- Rules 1, 2, 3 and 5 apply from the `core` 1.0.0 release on.
- Rule 4 (RDF 1.2 reifiers) is not adopted. When a relationship needs its
  own properties, the build models it as a qualified-relation node with its
  own IRI. That node loads into Neo4j as an ordinary node, so the pipeline's
  flatten step is not needed.
- The pipeline runs once the ontology is built (Step 12). Turtle stays the
  master copy.

## Points checked on 2026-10-05

An external check found that two statements in this snapshot need care:

- The guideline calls RDF 1.2 reifiers "now the standard pattern". The W3C
  RDF 1.2 Concepts document is a Candidate Recommendation Snapshot dated
  7 April 2026, not yet a Recommendation (https://www.w3.org/TR/rdf12-concepts/).
- The guideline lists rdflib as "in progress" for RDF 1.2. In rdflib's
  tracking issue every stage is still open, and no release supports it
  (https://github.com/RDFLib/rdflib/issues/3524). pySHACL depends on rdflib.
  RDF4J documents full support, and Apache Jena has supported RDF 1.2
  syntax since 5.4.0 (corrected 2026-10-06; an earlier note called Jena's
  support unconfirmed because its tracking issue is still open).

These notes are for the master copy's next revision.
