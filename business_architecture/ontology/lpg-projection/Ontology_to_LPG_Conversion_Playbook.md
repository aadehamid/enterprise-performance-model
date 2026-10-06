# Ontology_to_LPG_Conversion_Playbook (v2: RDF 1.2 edition)

**Converting a W3C ontology (RDF 1.2 / RDFS / OWL 2 / SKOS / SHACL) into a Neo4j Labelled Property Graph: deterministic, repeatable, high fidelity, and as simple as possible.**

Version 2.0 · October 2026 · Author: Hamid Adesokan (with Perplexity)

> **What changed in v2**
> - Relationship properties now use **RDF 1.2 triple terms with `rdf:reifies`** (W3C RDF 1.2) instead of RDF-star. This is now the standard pattern.
> - The playbook is split into a **Core Path** (5 rules + 5 steps, which work at any scale and for any use case) and **optional add-ons** that you adopt only when needed.
> - One collapse mechanism handles every relationship property, which keeps the pipeline small.

---

## 1. Scope: what you get

If the ontology follows the **5 Core Rules** (§3), the Core Path produces an LPG that is equivalent to the ontology and its data **for that profile**, from 10 triples to hundreds of millions. Only the loader changes with scale (§6). The mapping rules stay the same.

**Equivalent** here means:

| Preserved | How |
|---|---|
| Every individual, type, literal value and link | Nodes, labels, properties, relationships |
| Statement-level metadata (flow rate, valid-from, source, confidence) | Relationship properties, via RDF 1.2 reifiers |
| Class / property hierarchy, domain, range | Schema nodes (`:Class`, `:Relationship`, `:Property`) |
| Cardinality and constraints | SHACL shapes, checked in Neo4j |
| A full round trip back to RDF | Verified by an automated diff |

**Not preserved:** OWL *reasoning* (open world, complex class expressions, property chains). Neo4j has no reasoner. The Core Path runs a reasoner first and loads the inferred results as data. The OWL axioms themselves stay in the `.ttl` files, which remain the master copy.

---

## 2. The one-line mental model

```
Literal object            → node property
IRI object                → relationship
rdf:type                  → label
Reifier (rdf:reifies)     → properties on that relationship
Everything else           → stays in the ontology file (the master copy)
```

---

## 3. The 5 Core Rules for designing the ontology

These five rules make the conversion deterministic. Without them, the converter has to guess. Each rule can be checked automatically (§5, step 1).

### Rule 1: Every predicate has one kind and a concrete range

```turtle
ex:tagNumber  a owl:DatatypeProperty ; rdfs:range xsd:string .     # → node property
ex:feeds      a owl:ObjectProperty   ; rdfs:range ex:Asset .        # → relationship
rdfs:label    a owl:AnnotationProperty .                            # → node property
```

- Not allowed: bare `rdf:Property`, `rdfs:Literal` ranges, or one IRI used as two kinds of property.
- Always use concrete xsd types, preferably zoned `xsd:dateTimeStamp` for timestamps.

### Rule 2: Every property declares its cardinality in SHACL

```turtle
ex:TankShape a sh:NodeShape ; sh:targetClass ex:StorageTank ;
  sh:property [ sh:path ex:tagNumber ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 ] ;
  sh:property [ sh:path ex:alias     ; sh:datatype xsd:string ] ;                  # no maxCount → array
  sh:property [ sh:path ex:feeds     ; sh:class ex:ProcessUnit ; sh:nodeKind sh:IRI ] .
```

- `sh:maxCount 1` → single value.
- Anything else → array, with values sorted so the output is deterministic.

### Rule 3: Stable IRIs and fixed prefixes

- Individuals get permanent IRIs (`ex:asset/TK-101`). Never generate them per run.
- No blank nodes in data. Reifiers in particular must be IRIs (`~ ex:feed/TK-101_CDU-1_2026`), because the reifier's IRI becomes the relationship's identity.
- Each namespace has one registered prefix in `prefixes.ttl`.

### Rule 4: Relationship properties use RDF 1.2 reifiers, and only reifiers

**RDF 1.2 Turtle, short form (asserts the triple and annotates it):**

```turtle
ex:TK-101 ex:feeds ex:CDU-1 ~ ex:feed_0042 {| ex:maxFlowBblPerDay 120000 ; ex:validFrom "2026-01-01"^^xsd:date ; ex:source "P&ID-0042 rev C" |} .
```

**What this means in plain triples (RDF 1.2 abstract syntax):**

```turtle
ex:TK-101 ex:feeds ex:CDU-1 .                                        # the asserted triple
ex:feed_0042 rdf:reifies <<( ex:TK-101 ex:feeds ex:CDU-1 )>> .       # the reifying triple (triple term as object)
ex:feed_0042 ex:maxFlowBblPerDay 120000 ;
             ex:validFrom "2026-01-01"^^xsd:date ;
             ex:source "P&ID-0042 rev C" .
```

**LPG result:** one relationship per reifier.

```
(TK-101)-[:FEEDS {uri:"…feed_0042", maxFlowBblPerDay:120000, validFrom:date('2026-01-01'), source:"P&ID-0042 rev C"}]->(CDU-1)
```

**Determinism rules for reifiers:**

- One reifier → one relationship, and the relationship carries the reifier's `uri`.
- Two reifiers for the same triple (e.g. two validity periods) → **two parallel relationships**, never merged.
- An asserted triple with no reifier → one plain relationship.
- A triple term with no asserted triple (a claim that isn't asserted as true) → a relationship with `asserted:false`. Alternatively, leave it out by design and record that in the exclusions list (Add-on D).
- Reifier properties must be **literal-valued** (Rule 1 still applies). If a reifier needs to point at another resource (e.g. `ex:approvedBy ex:Engineer7`), store that IRI as a string property `approvedBy_uri`. It can be restored on the round trip.

> Why reifiers and not a custom n-ary class? RDF 1.2 makes the reifier the W3C-standard identity of "this specific link". That maps one-to-one onto a Neo4j relationship with properties. One pattern means one piece of conversion code.

### Rule 5: Name the LPG explicitly where the IRI local name isn't good enough

Use a single annotation property in a small module (`lpg-mapping.ttl`):

```turtle
lpg:name a owl:AnnotationProperty .
ex:alias  lpg:name "aliases" .
ex:feeds  lpg:name "FEEDS" .
```

Where there's no `lpg:name`, the IRI local name is used as-is. A CI check fails the build if two IRIs end up with the same name.

That's the whole required design discipline. Optional annotations (`lpg:cypherType`, `lpg:langPolicy`, …) are covered in the add-ons.

---

## 4. Core Path architecture

```
 ontology.ttl ─┐
 shapes.ttl ───┤  1 check  ─▶  2 reason  ─▶  3 flatten  ─▶  4 load  ─▶  5 verify
 data.ttl ─────┤   (SHACL)     (ELK)         (RDF 1.2 →     (n10s)      (round-trip diff
 prefixes.ttl ─┘                              loadable)                   + fingerprint)
```

Tools (all free / open source):

| Purpose | Tool |
|---|---|
| Parse RDF 1.2 / run SPARQL 1.2 | Apache Jena or Eclipse RDF4J (both support RDF 1.2 triple terms). rdflib support is in progress |
| Reason | ROBOT (`robot reason --reasoner ELK`) |
| Validate | pySHACL / Jena SHACL |
| Load into Neo4j | neosemantics (n10s) |
| Diff | rdflib `compare` (on the flattened form), or Jena `rdfcompare` |

---

## 5. Core Path: the five steps

### Step 1: Check the ontology against the 5 Rules

Run SHACL "meta-shapes" over the ontology file itself:

- Every property is typed and has a concrete range (Rule 1).
- Every data property has a shape with `sh:maxCount` defined or deliberately omitted (Rule 2).
- No blank-node reifiers or individuals (Rule 3).
- Every reifier has only literal-valued properties, or `_uri` handling is declared (Rule 4).
- No `lpg:name` collisions (Rule 5).

Then validate the data against `shapes.ttl`. **Any violation stops the build.**

### Step 2: Reason (once, upstream)

```bash
robot reason --reasoner ELK --input ontology.ttl --axiom-generators "SubClass ClassAssertion" \
             --output inferred.ttl
```

Load the inferred `rdf:type` / `subClassOf` triples into a separate named graph (`ex:graph/inferred`), so you can always tell them apart from asserted triples.

### Step 3: Flatten RDF 1.2 into a loadable form

n10s is built around RDF 1.1 / RDF-star, not RDF 1.2 triple terms. So the pipeline does one small, deterministic conversion with SPARQL 1.2 (Jena / RDF4J). Each reifier becomes a plain node that n10s can load:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX lpg: <https://example.org/lpg-mapping#>
CONSTRUCT {
  ?r a lpg:EdgeRecord ;
     lpg:edgeSource ?s ; lpg:edgePredicate ?p ; lpg:edgeTarget ?o ;
     lpg:asserted ?asserted .
}
WHERE {
  ?r rdf:reifies ?tt .
  BIND(SUBJECT(?tt) AS ?s) BIND(PREDICATE(?tt) AS ?p) BIND(OBJECT(?tt) AS ?o)
  BIND(EXISTS { ?s ?p ?o } AS ?asserted)
}
```

- Output: the original triples, minus the `rdf:reifies` triples, plus these `EdgeRecord` triples. The reifier's own literal properties stay attached to `?r`.
- Serialise as **sorted N-Triples**. Its SHA-256 is the *input fingerprint*.

### Step 4: Load into Neo4j

```cypher
// 4a. Clean DB + constraint
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;

// 4b. Fixed prefixes and names (generated from prefixes.ttl + lpg:name)
CALL n10s.nsprefixes.add('ex','https://example.org/refinery#');
CALL n10s.mapping.add('https://example.org/refinery#alias','aliases');
CALL n10s.mapping.add('https://example.org/refinery#feeds','FEEDS');

// 4c. Config (generated; multivalPropList comes from SHACL maxCount)
CALL n10s.graphconfig.init({
  handleVocabUris:'MAP', handleRDFTypes:'LABELS_AND_NODES',
  handleMultival:'ARRAY', multivalPropList:['https://example.org/refinery#alias'],
  keepLangTag:true, keepCustomDataTypes:true
});

// 4d. Load in fixed order: schema, shapes, data, inferred
CALL n10s.onto.import.fetch('file:///ontology.ttl','Turtle');
CALL n10s.validation.shacl.import.fetch('file:///shapes.ttl','Turtle');
CALL n10s.rdf.import.fetch('file:///flattened.nt','N-Triples');

// 4e. The ONE post-load transform: EdgeRecord → relationship with properties
MATCH (r:EdgeRecord)-[:edgeSource]->(s), (r)-[:edgeTarget]->(t), (r)-[:edgePredicate]->(p)
WITH r, s, t, p ORDER BY r.uri
CALL apoc.merge.relationship(s, coalesce(p.lpgName, n10s.rdf.getIRILocalName(p.uri)),
     {uri: r.uri}, apoc.map.removeKeys(properties(r), ['uri']), t, {}) YIELD rel
DETACH DELETE r;

// 4f. Remove plain edges that duplicate a reified one. An asserted triple with
//     reifiers is represented only by its reified edges; the round trip restores it.
MATCH (s)-[plain]->(t), (s)-[reified]->(t)
WHERE type(plain) = type(reified) AND plain.uri IS NULL AND reified.uri IS NOT NULL
DELETE plain;

// 4g. Sort array properties (generated per multivalued key)
MATCH (n:Resource) WHERE n.aliases IS NOT NULL SET n.aliases = apoc.coll.sort(n.aliases);
```

Every statement uses `MERGE` / `SET` with explicit ordering, so running it again gives the same graph.

### Step 5: Verify

1. `CALL n10s.validation.shacl.validate()` returns **zero** violations.
2. **Round trip:** export with `n10s.rdf.export.cypher`, rebuild `EdgeRecord`s from relationships that have a `uri`, and diff against `flattened.nt`:

```python
from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff
src = to_isomorphic(Graph().parse("flattened.nt"))
out = to_isomorphic(Graph().parse("roundtrip.nt"))
both, lost, added = graph_diff(src, out)
assert len(lost) == 0 and len(added) == 0, (len(lost), len(added))
```

3. **Determinism:** load twice into clean databases, with the triple order shuffled the second time. Hash the graphs (nodes sorted by `uri`, edges by `(src, type, tgt, uri)`). The two hashes must match.

If all three pass, the LPG is a verified, repeatable projection of the ontology.

---

## 6. Scale: same rules, different loader

| Size | Loader | What changes |
|---|---|---|
| Up to ~10M triples | n10s `rdf.import.fetch` (Step 4) | Nothing |
| ~10M – 1B+ triples | Generate node/edge CSVs from `flattened.nt` using the **same** mapping, then run `neo4j-admin database import` | Only Step 4. Steps 1–3 and 5 stay the same |
| Incremental updates | Load each delta with n10s (`MERGE` by `uri`); for deletions, use `n10s.rdf.delete` | Add a nightly full-rebuild comparison |

The big biomedical graphs (RTX-KG2, BioCypher-based KGs) use this same "canonical intermediate → bulk import" approach.

---

## 7. Optional add-ons (adopt only when needed)

| Add-on | Use when | What to add |
|---|---|---|
| **A. Superclass labels** | You want `MATCH (:Asset)` to find tanks without traversing the hierarchy | After Step 4, add the labels of inferred superclasses, excluding `owl:Thing` and upper-ontology roots |
| **B. Language policy** | Multilingual labels | `lpg:langPolicy "splitKeys"` → `label_en`, `label_fr` |
| **C. Exact decimals** | Custody transfer, accounting | `lpg:cypherType "STRING"` on `xsd:decimal` properties |
| **D. Known exclusions** | Complex OWL axioms you won't project | List them in `exclusions.nt`; the diff ignores them |
| **E. Units** | Engineering quantities | QUDT value + unit pattern, rather than custom datatypes |
| **F. Named graphs / provenance** | Several sources or versions | Load each graph separately; tag nodes/edges with `graph` |
| **G. Business keys** | You MERGE on tag numbers etc. | `lpg:keyProperty true` → extra uniqueness constraint |

---

## 8. xsd → Cypher type table (fixed)

| xsd | Cypher |
|---|---|
| string, token, normalizedString | STRING |
| boolean | BOOLEAN |
| integer, long, int, nonNegativeInteger | INTEGER (64-bit, range-checked) |
| double, float | FLOAT |
| decimal | FLOAT (or STRING with Add-on C) |
| date | DATE |
| dateTimeStamp / dateTime with timezone | ZONED DATETIME |
| dateTime without timezone | LOCAL DATETIME (better: forbid it in SHACL) |
| duration | DURATION |
| anyURI | STRING |
| rdf:langString / rdf:dirLangString (RDF 1.2) | STRING with tag (`keepLangTag`), or Add-on B |

---

## 9. Checklist

**Ontology (the 5 Rules)**

- [ ] Every predicate has one kind and a concrete range.
- [ ] SHACL `sh:maxCount` defined for every property.
- [ ] Stable IRIs, no blank nodes, IRI reifiers, fixed prefixes.
- [ ] Relationship properties only through RDF 1.2 `rdf:reifies` reifiers, with literal-valued annotations.
- [ ] `lpg:name` where needed, with no collisions.

**Pipeline**

- [ ] Versions pinned (Neo4j, n10s, APOC, Jena/RDF4J, ROBOT).
- [ ] Steps 1–5 automated in CI.
- [ ] SHACL clean, round-trip diff zero, determinism hashes equal.

---

## 10. Anti-patterns

- Relying on n10s defaults (`OVERWRITE` for multivalues, auto-generated `ns0` prefixes).
- Blank-node reifiers. The relationship then has no stable identity.
- Merging two reifiers of the same triple into one relationship.
- Handwritten Cypher that isn't generated from the ontology.
- Expecting Neo4j to do OWL reasoning.
- Treating Neo4j as the master copy instead of the `.ttl` files.

---

## 11. Sources

- W3C: RDF 1.2 Concepts (triple terms, `rdf:reifies`, reifiers). https://www.w3.org/TR/rdf12-concepts/
- W3C: RDF 1.2 Primer. https://www.w3.org/TR/rdf12-primer/
- W3C: RDF 1.2 Turtle (`<<( )>>`, `~ reifier`, `{| |}` annotation syntax). https://www.w3.org/TR/rdf12-turtle/
- W3C: RDF 1.2 Interoperability. https://w3c.github.io/rdf-interop/spec/
- W3C: SHACL. https://www.w3.org/TR/shacl/
- Eclipse RDF4J: RDF 1.2 and SPARQL 1.2. https://rdf4j.org/documentation/programming/rdf12/
- rdflib RDF 1.2 tracking issue. https://github.com/RDFLib/rdflib/issues/3524
- rdflib.compare. https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.compare/
- Neo4j Labs: neosemantics. https://neo4j.com/labs/neosemantics/ · https://github.com/neo4j-labs/neosemantics
- RTX-KG2. https://github.com/RTXteam/RTX-KG2 · BioCypher. https://biocypher.github.io/biocypher-paper/
