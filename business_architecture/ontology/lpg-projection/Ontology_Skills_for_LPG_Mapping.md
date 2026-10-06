# Ontology_Skills_for_LPG_Mapping: Learning Guide

**What you need to get good at in the W3C stack so your ontologies map cleanly and deterministically to a Neo4j LPG**

Companion to *Ontology_to_LPG_Conversion_Playbook v2* · October 2026

---

## How to use this guide

The skills are in priority order. Each one lists **why it matters for LPG mapping**, **what to master**, a **practice exercise** (based on your refinery domain), and **resources**.

Priority levels:

- ★★★ = essential, needed for the 5 Core Rules.
- ★★ = important.
- ★ = good to know.

Suggested pace: about 6–8 weeks at a few hours per week.

| # | Skill | Priority | Playbook rule it supports |
|---|---|---|---|
| 1 | RDF 1.2 data model & IRIs | ★★★ | Rules 3, 4 |
| 2 | Turtle 1.2 syntax (incl. reifiers) | ★★★ | Rule 4 |
| 3 | RDFS: classes, properties, domain/range | ★★★ | Rule 1 |
| 4 | OWL 2: property kinds, OWL 2 EL profile, reasoning | ★★★ | Rule 1, Step 2 |
| 5 | XSD datatypes & literals | ★★★ | Rule 1, §8 |
| 6 | SHACL core shapes | ★★★ | Rule 2, Steps 1 & 5 |
| 7 | SPARQL 1.2 (CONSTRUCT, triple terms) | ★★ | Step 3 |
| 8 | Modelling patterns (n-ary, reification, qualified relations) | ★★ | Rule 4 |
| 9 | SKOS for taxonomies and labels | ★★ | Add-on B |
| 10 | Reusing standard vocabularies (QUDT, PROV-O, OWL-Time) | ★ | Add-ons E, F |
| 11 | Canonicalisation & graph comparison | ★ | Step 5 |
| 12 | LPG modelling in Neo4j + n10s | ★★★ | Step 4 |

---

## 1. RDF 1.2 data model & IRIs ★★★

**Why it matters:** the LPG mapping rule is "literal → property, IRI → relationship". That only works if you think in terms of RDF's term types: IRI, literal, blank node and, new in 1.2, triple term.

**Master:**

- Triples and graphs, and named graphs / datasets.
- The four kinds of term, and where each is allowed. In RDF 1.2, a triple term can only appear in object position.
- Reifying triples (`rdf:reifies`), and the difference between asserting a triple and only reifying it.
- IRI design: stable, opaque or business-key IRIs; why blank nodes break determinism.

**Practice:** model TK-101 feeds CDU-1 with two reifiers for two validity periods. Explain why that becomes two Neo4j relationships.

**Resources:**

- [RDF 1.2 Primer (W3C)](https://www.w3.org/TR/rdf12-primer/)
- [RDF 1.2 Concepts and Abstract Data Model (W3C)](https://www.w3.org/TR/rdf12-concepts/), especially the sections on triple terms and reification
- [RDF 1.2 Interoperability (W3C)](https://w3c.github.io/rdf-interop/spec/), on Basic vs Full RDF 1.2
- [Cool URIs for the Semantic Web (W3C)](https://www.w3.org/TR/cooluris/)
- [Best Practice Recipes for Publishing RDF Vocabularies (W3C)](https://www.w3.org/TR/swbp-vocab-pub/)

---

## 2. Turtle 1.2 syntax ★★★

**Why it matters:** you'll write ontologies, shapes and test fixtures in Turtle. The reifier syntax is how relationship properties are written.

**Master:**

- Prefixes, `;` and `,` shorthands, typed and language-tagged literals.
- `<<( s p o )>>` (triple term), `<< s p o ~ ex:r >>` (reified triple with a named reifier), and `s p o ~ ex:r {| ... |}` (assert + annotate).
- N-Triples / N-Quads, for sorted, diffable outputs.

**Practice:** write the same feed annotation in all three Turtle 1.2 forms. Convert each to N-Triples with Jena `riot` and confirm they match.

**Resources:**

- [RDF 1.2 Turtle (W3C)](https://www.w3.org/TR/rdf12-turtle/)
- [RDF 1.2 N-Triples (W3C)](https://www.w3.org/TR/rdf12-n-triples/)
- [Apache Jena RIOT command-line tools](https://jena.apache.org/documentation/io/)
- [Eclipse RDF4J: RDF 1.2 guide](https://rdf4j.org/documentation/programming/rdf12/)

---

## 3. RDFS ★★★

**Why it matters:** classes become labels, `subClassOf` becomes label hierarchies, and domain/range tell you which relationships connect which labels.

**Master:**

- `rdfs:Class`, `rdfs:subClassOf`, `rdfs:subPropertyOf`, `rdfs:domain`, `rdfs:range`, `rdfs:label`, `rdfs:comment`.
- That domain/range **infer** types rather than restrict them. This is a common surprise. Use SHACL for restrictions.

**Practice:** build `Asset → StorageTank / ProcessUnit / Pipeline`. Predict what the inferred types are when `ex:feeds` has domain `ex:Asset`.

**Resources:**

- [RDF 1.2 Schema (W3C)](https://www.w3.org/TR/rdf12-schema/)
- [RDF 1.2 Semantics (W3C)](https://www.w3.org/TR/rdf12-semantics/) (optional, deep)
- Book: Allemang, Hendler & Gandon, *Semantic Web for the Working Ontologist*, 3rd ed. (ACM Books), chapters on RDFS

---

## 4. OWL 2 ★★★

**Why it matters:** OWL's three kinds of property map directly to the three LPG outcomes. Choosing the OWL 2 EL profile keeps reasoning fast and predictable at scale.

**Master:**

- `owl:ObjectProperty` vs `owl:DatatypeProperty` vs `owl:AnnotationProperty`. This is Rule 1.
- `owl:Class`, named individuals, `owl:equivalentClass`, `owl:disjointWith`.
- Property characteristics (functional, inverse, transitive), and why the LPG doesn't enforce them.
- The open-world vs closed-world difference (OWL vs Neo4j/SHACL).
- The OWL 2 profiles: **EL** (large hierarchies, ELK reasoner), QL, RL.
- What to keep only in the ontology file (complex class expressions, property chains).

**Practice:** in Protégé, build the refinery ontology in the EL profile. Run ELK, and export the inferred class assertions with ROBOT.

**Resources:**

- [OWL 2 Primer (W3C)](https://www.w3.org/TR/owl2-primer/)
- [OWL 2 Profiles (W3C)](https://www.w3.org/TR/owl2-profiles/)
- [OWL 2 Quick Reference Guide (W3C)](https://www.w3.org/TR/owl2-quick-reference/)
- [Protégé](https://protege.stanford.edu/) and the [New Protégé Pizza Tutorial (M. DeBellis)](https://www.michaeldebellis.com/post/new-protege-pizza-tutorial)
- [ROBOT tool (OBO)](http://robot.obolibrary.org/), especially `reason`, `report`, `convert`
- [OBO Academy](https://oboacademy.github.io/obook/): free, practical ontology-engineering training

---

## 5. XSD datatypes & literals ★★★

**Why it matters:** each literal's datatype decides its Cypher type. Vague types give you a non-deterministic or lossy result.

**Master:**

- `xsd:string`, `integer`, `decimal`, `double`, `boolean`, `date`, `dateTime`, `dateTimeStamp`, `duration`.
- Lexical form vs value (`"01"^^xsd:integer` = `"1"^^xsd:integer`).
- Timezones, and decimal precision vs float.
- Language tags, and RDF 1.2 directional language strings (`rdf:dirLangString`).

**Practice:** write SHACL that rejects `xsd:dateTime` values with no timezone.

**Resources:**

- [XML Schema 1.1 Part 2: Datatypes (W3C)](https://www.w3.org/TR/xmlschema11-2/)
- [RDF 1.2 Concepts: Literals section](https://www.w3.org/TR/rdf12-concepts/#section-Graph-Literal)
- [Neo4j Cypher values and types](https://neo4j.com/docs/cypher-manual/current/values-and-types/)

---

## 6. SHACL ★★★

**Why it matters:** SHACL turns open-world OWL into closed-world rules. It decides single value vs array (Rule 2), enforces the 5 Rules (Step 1), and validates the LPG inside Neo4j (Step 5).

**Master:**

- Node shapes and property shapes; `sh:targetClass`.
- `sh:minCount`, `sh:maxCount`, `sh:datatype`, `sh:class`, `sh:nodeKind`, `sh:in`, `sh:pattern`.
- Validation reports and severities.
- SHACL-SPARQL constraints, for the meta-shapes that check the 5 Rules.
- Which constraints n10s supports inside Neo4j.

**Practice:** write `TankShape` and `FeedReifierShape` (literal-only annotations, IRI reifier). Validate with pySHACL in a notebook.

**Resources:**

- [SHACL (W3C Recommendation)](https://www.w3.org/TR/shacl/)
- [SHACL 1.2 Core (W3C Data Shapes WG, draft)](https://www.w3.org/TR/shacl12-core/)
- Book: Labra Gayo et al., [*Validating RDF Data*](https://book.validatingrdf.com/) (free online)
- [SHACL Playground](https://shacl.org/playground/)
- [pySHACL](https://github.com/RDFLib/pySHACL)
- [n10s SHACL validation docs](https://neo4j.com/labs/neosemantics/4.0/validation/)

---

## 7. SPARQL 1.2 ★★

**Why it matters:** Step 3 (flattening reifiers) is a single SPARQL CONSTRUCT. SPARQL is also how you write meta-checks and fidelity reports.

**Master:**

- SELECT / CONSTRUCT / ASK, `FILTER`, `OPTIONAL`, `EXISTS`, `BIND`, `GRAPH`.
- SPARQL 1.2 triple-term functions: `SUBJECT()`, `PREDICATE()`, `OBJECT()`, `isTRIPLE()`.

**Practice:** run the Step 3 query in Jena `arq` on your feed example and inspect the `EdgeRecord`s.

**Resources:**

- [SPARQL 1.2 Query Language (W3C)](https://www.w3.org/TR/sparql12-query/)
- [Apache Jena ARQ tutorial](https://jena.apache.org/tutorials/sparql.html)
- Bob DuCharme, *Learning SPARQL*, 2nd ed. (O'Reilly)

---

## 8. Modelling patterns ★★

**Why it matters:** the hardest part of mapping is deciding what is a node, what is a relationship, and what is a relationship property.

**Master:**

- **The node vs relationship-with-properties test:** if anything points at it, or it has its own lifecycle, it's a node (an event or connection class). Otherwise use a reifier.
- N-ary relations and qualified relations (e.g. PROV-O `qualifiedAssociation`).
- RDF 1.2 reification vs old `rdf:Statement` reification vs RDF-star.

**Practice:** model a "tank transfer". First as a reified `FEEDS` edge, then as a `:Transfer` event node. Write down which one fits a custody-transfer use case and why.

**Resources:**

- [Defining N-ary Relations on the Semantic Web (W3C Note)](https://www.w3.org/TR/swbp-n-aryRelations/)
- [RDF 1.2 Primer: statements about statements](https://www.w3.org/TR/rdf12-primer/)
- [ODP: Ontology Design Patterns portal](http://ontologydesignpatterns.org/)
- [J. Barrasa: RDF\* and property graphs (QuickGraph#14)](https://jbarrasa.com/2021/01/19/quickgraph14-using-rdf-with-neo4j/)

---

## 9. SKOS ★★

**Why it matters:** equipment types, product grades and failure codes are usually taxonomies, not OWL classes. SKOS concepts become nodes with `BROADER` relationships, which is much easier for an LPG than deep class hierarchies.

**Master:**

- `skos:Concept`, `ConceptScheme`, `prefLabel` / `altLabel`, `broader` / `narrower`, `exactMatch` / `closeMatch`.
- When to use a SKOS concept and when to use an OWL class.

**Resources:**

- [SKOS Primer (W3C)](https://www.w3.org/TR/skos-primer/)
- [SKOS Reference (W3C)](https://www.w3.org/TR/skos-reference/)
- [n10s: importing SKOS](https://neo4j.com/labs/neosemantics/4.0/importing-ontologies/)

---

## 10. Reusing standard vocabularies ★

- [QUDT](https://qudt.org/): units and quantities (bbl, °F, psig).
- [PROV-O (W3C)](https://www.w3.org/TR/prov-o/): provenance for reifier annotations.
- [OWL-Time (W3C)](https://www.w3.org/TR/owl-time/): validity periods.
- [SOSA/SSN (W3C)](https://www.w3.org/TR/vocab-ssn/): sensors and observations, relevant to historians and SCADA.
- [Linked Open Vocabularies](https://lov.linkeddata.es/): find existing terms before inventing new ones.

---

## 11. Canonicalisation & graph comparison ★

**Why it matters:** this is how you prove the output is deterministic and loses nothing (Step 5).

- [RDF Dataset Canonicalization RDFC-1.0 (W3C)](https://www.w3.org/TR/rdf-canon/)
- [rdflib.compare (isomorphism, graph_diff)](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.compare/)
- [W3C wiki: How to diff RDF](https://www.w3.org/2001/sw/wiki/How_to_diff_RDF)

---

## 12. LPG modelling in Neo4j + n10s ★★★

**Why it matters:** you need to know the target model well to design for it.

- [Neo4j GraphAcademy: Graph Data Modeling Fundamentals (free)](https://graphacademy.neo4j.com/courses/modeling-fundamentals/)
- [Neo4j GraphAcademy: Cypher Fundamentals (free)](https://graphacademy.neo4j.com/courses/cypher-fundamentals/)
- [neosemantics docs](https://neo4j.com/labs/neosemantics/) and [GitHub](https://github.com/neo4j-labs/neosemantics)
- [Neo4j video: n10s with Jesús Barrasa & Adam Cowley](https://neo4j.com/videos/neosemantics-n10s-a-linked-data-toolkit-for-neo4j-with-jesus-barrasa-and-adam-cowley/)
- [APOC docs](https://neo4j.com/docs/apoc/current/), for `apoc.merge.relationship` and `apoc.coll.sort`

---

## Suggested 8-week plan

| Week | Focus | Deliverable |
|---|---|---|
| 1 | RDF 1.2 + Turtle 1.2 (skills 1–2) | `data.ttl` with reifiers, converted to sorted N-Triples |
| 2 | RDFS + XSD (skills 3, 5) | Class/property hierarchy with typed ranges |
| 3 | OWL 2 + Protégé + ROBOT (skill 4) | EL ontology + `inferred.ttl` |
| 4 | SHACL (skill 6) | `shapes.ttl` + meta-shapes for the 5 Rules |
| 5 | SPARQL 1.2 (skill 7) | Step 3 flatten query working in Jena |
| 6 | Neo4j + n10s (skill 12) | Steps 4–5 working end-to-end |
| 7 | Patterns + SKOS (skills 8–9) | Equipment taxonomy in SKOS; transfer modelled both ways |
| 8 | Vocabularies + canonicalisation (skills 10–11) | QUDT units, determinism test passing in CI |

## Flashcard seeds

- Literal object → ? *(node property)*
- IRI object → ? *(relationship)*
- `rdf:reifies` object must be a ? *(triple term)*
- Where can a triple term appear in RDF 1.2? *(object position only)*
- Two reifiers for one triple → how many Neo4j relationships? *(two)*
- Which SHACL property decides single value vs array? *(`sh:maxCount`)*
- Why must reifiers be IRIs? *(they become the relationship's stable `uri`)*
- What does Neo4j not do that OWL needs? *(open-world reasoning)*
- Which OWL profile suits large hierarchies? *(EL, with the ELK reasoner)*
