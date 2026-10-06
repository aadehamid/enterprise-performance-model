# EPM-DEC-001-0020: Adopt the ontology-to-LPG guideline: Step 12, design Rules 1, 2, 3 and 5, no reifiers

| Field | Value |
|---|---|
| Status | Decided |
| Date | 2026-10-05 |
| Questions | Q24, Q29, Q30, Q33 |
| Source | Grilling session on the handover plan |

## Context

Hamid asked to project the finished ontology to a Neo4j labelled property graph using his guideline (Ontology_to_LPG_Conversion_Playbook v2, enterprise-people-graph commit cd63e12). An external check on 2026-10-05 found: RDF 1.2 is a W3C Candidate Recommendation Snapshot (7 April 2026), not a Recommendation; rdflib has no RDF 1.2 support (issue #3524, all stages open), and pySHACL depends on rdflib; RDF4J documents support; Jena's tracking issue #2805 is open; n10s is maintained (commit 29 May 2026, Neo4j 2025.06.2) and does not read RDF 1.2.

## Decision

(1) Add Step 12, LPG projection, after Step 11. It follows the guideline's pipeline (check, reason, load, verify) once the ontology is built. (2) Apply the guideline's design Rules 1, 2, 3 and 5 from `core` 1.0.0 on: one kind and a concrete range per property; SHACL cardinality on every property; stable IRIs, no blank nodes, fixed prefixes; explicit LPG names where the local name is not good enough. (3) Do not adopt Rule 4 (RDF 1.2 reifiers). When a relationship needs its own properties, model it as a qualified-relation node with its own IRI, the pattern of `org:Membership` and PROV-O qualified relations. This needs no RDF 1.2 tooling and removes the guideline's flatten step. (4) Record the playbook policy: LPG projection follows the guideline with this deviation, and Turtle stays the master copy.

## Alternatives considered

Apply the guideline only at projection time; adopt all five rules including RDF 1.2 reifiers; adopt Rule 4 at Step 5.

## Hamid's recorded words

Q24: "can we adopt the guideline to project ontology to label property graph at https://github.com/aadehamid/enterprise-people-graph/tree/main/guideline_to_map_ontology_to_LPG Can we update our playbook with this." Q29: "I am aligned . But can you check this ontology to LPG projection guideline by doing a quick extrrnal search to make sure the guideline hold up and that it does not make the ontology unnecessarily complex." Q33: "We still have a way of representing this behavious without using reifers." Q30: Not commented on; agreed per Hamid's rule "If i dont comment on a question, it means I am aligned."

Session: Grilling session on the handover plan, 2026-10-05 (Claude Code with Hamid). Hamid answered numbered questions Q1 to Q34 in five rounds and confirmed the full decision list with: "Confirmed, go ahead and open the two PRs." He also stated: "If i dont comment on a question, it means I am aligned." A question he did not comment on is therefore recorded as agreed with the recommendation.

## Correction (2026-10-06)

The context above says Jena's RDF 1.2 support was unconfirmed because its tracking issue (#2805) is open. That was wrong. Apache Jena has read and written RDF 1.2 since 5.4.0 (April 2025, experimental), and 6.2.0 is current (https://github.com/apache/jena/blob/main/CHANGES.txt). The reviewer of enterprise-people-graph PR #1 found the error. The decision stands: this build's Python toolchain (rdflib, pySHACL) has no RDF 1.2 support, which is why Rule 4 uses qualified-relation nodes.

## Evidence

https://www.w3.org/TR/rdf12-concepts/ ; https://github.com/RDFLib/rdflib/issues/3524 ; https://rdf4j.org/documentation/programming/rdf12/ ; https://github.com/apache/jena/issues/2805 ; https://github.com/neo4j-labs/neosemantics ; `business_architecture/ontology/lpg-projection/`.
