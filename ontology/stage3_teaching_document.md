# Learning RDF, OWL, and Turtle Through the Enterprise KPI Ontology

*A teaching document for readers who understand graphs (nodes, edges, labels, schemas) but are new to RDF, RDFS, OWL, Turtle, and semantic modeling.*

*Version 2.0.0 — walks through the corrected ontology structure (no more "bucket" superclasses, a new observation/fact layer, closed vocabularies, and a small property hierarchy) using the Downstream Oil & Gas Commercial worked example: Rack Price Capture Rate %.*

---

## Part 1 — The big ideas, before any syntax

### 1.1 What RDF is

RDF (**Resource Description Framework**) is a **data model** — a way of describing *anything* as a graph of simple facts called **triples**:

```
subject   predicate   object
```

Each triple is one edge in a graph: `subject —predicate→ object`. That's it. Every RDF graph, no matter how large, is just a big pile of these three-part statements.

Example in plain English: *"Rack Price Capture Rate KPI — aligns to objective — Improve Rack Capture to 99% by Q4 FY26"* is one triple. *"Rack Price Capture Rate KPI — has unit — Percent"* is another. Stack thousands of these and you get an enterprise-wide knowledge graph.

**Analogy:** if you've used a property graph database (like Neo4j), RDF triples are like `(node)-[:RELATIONSHIP]->(node)` — but RDF additionally lets the object be a plain value ("98.4") instead of another node, and every subject/predicate/object is *globally addressable* (see IRIs, below), so graphs from different systems can be merged without renaming clashes.

### 1.2 What an RDF graph looks like

A graph is just a set of triples. Visually:

```
        alignsToObjective
RackPriceCaptureRateKPI ─────────► ImproveRackCapture99pctQ4FY26
        │
        │ hasUnitOfMeasure
        ▼
    PercentUnit
```

Nothing here is "the file format" yet — this is the abstract graph. Turtle (next section) is just *one way to write this graph down as text*.

### 1.3 What Turtle is

**Turtle** ("Terse RDF Triple Language") is a **text syntax** for writing RDF triples. It is not a different data model — it's a human-friendly notation for the exact same subject-predicate-object triples. The same graph could also be written in other syntaxes (RDF/XML, JSON-LD, N-Triples) — Turtle is simply the most readable one, which is why it's used for ontology authoring.

### 1.4 The three-layer distinction (this trips up almost every beginner)

| Layer | Question it answers | Example |
|---|---|---|
| **Data model** — RDF | "What is a fact, structurally?" | A triple: subject–predicate–object |
| **Ontology language** — RDFS / OWL | "What *kinds* of things and relationships can I declare, and what can be logically inferred?" | "KPI is a subclass of Metric"; "every KPI must have a definition and an owner" |
| **Serialization syntax** — Turtle (or RDF/XML, JSON-LD...) | "How do I write triples down as text?" | `ekpi:KPI rdfs:subClassOf ekpi:Metric .` |

RDF is the *model*. RDFS/OWL are *vocabularies written in that model* that let you describe schemas and constraints. Turtle is *how you type it*. You could throw away Turtle and use JSON-LD instead, and the ontology's meaning (RDFS/OWL facts) would be identical.

### 1.5 What namespaces, prefixes, and IRIs are — and why they matter

An **IRI** (Internationalized Resource Identifier — think "a URL that names a concept, not a webpage you necessarily visit") is RDF's way of giving every class, property, and individual a **globally unique name**. Instead of a term like `KPI` — which could mean anything to anyone — RDF uses something like:

```
https://ontology.enterprise.example.com/kpi-store/core#KPI
```

This is unique across the entire world. Two companies can both have a concept called "KPI," and because their IRIs differ, their graphs never collide if merged.

Typing full IRIs constantly is unreadable, so Turtle lets you declare a **prefix** — a short alias for a namespace (the common "stem" of a family of IRIs):

```turtle
@prefix ekpi: <https://ontology.enterprise.example.com/kpi-store/core#> .
```

After this line, `ekpi:KPI` is shorthand for the full IRI above. This is exactly like a `import numpy as np` alias in Python — `np` is not numpy itself, it's a nickname that expands back to the full thing.

### 1.6 What each standard vocabulary is for

| Prefix | Full name | What it's for | Where it appears in our ontology |
|---|---|---|---|
| `rdf:` | RDF Core | The base vocabulary of RDF itself — most importantly `rdf:type`, which says "this thing is an instance of that class." | Every `a` shorthand (see §2.3) is secretly `rdf:type`. |
| `rdfs:` | RDF Schema | A light vocabulary for describing classes, hierarchies, and simple metadata: `rdfs:Class`, `rdfs:subClassOf`, `rdfs:subPropertyOf`, `rdfs:label`, `rdfs:comment`, `rdfs:domain`, `rdfs:range`. | Used constantly — every class/property has an `rdfs:label`; class hierarchies use `rdfs:subClassOf`; the new v2.0.0 property hierarchy uses `rdfs:subPropertyOf` (§2.13). |
| `owl:` | Web Ontology Language | A richer vocabulary on top of RDFS that adds real logical power: `owl:Class`, `owl:ObjectProperty`, `owl:DatatypeProperty`, `owl:Restriction`, `owl:equivalentClass`, `owl:disjointWith`, `owl:FunctionalProperty`, `owl:oneOf`. | Declares every class/property; used for the `CertifiedDefinition` inference rule, the raw/silver/gold disjointness and medallion restrictions, and every closed vocabulary. |
| `xsd:` | XML Schema Datatypes | Defines primitive datatypes for literal values: strings, dates, decimals, integers, booleans. | `"98.4"^^xsd:decimal`, `"2026-07-31"^^xsd:date`. |
| `dcterms:` | Dublin Core Terms | A general-purpose metadata vocabulary for describing *documents/resources* — title, creator, date created, license, and (used in a new way in v2.0.0) `dcterms:isPartOf` for module membership. | Used in the ontology header **and**, new in v2.0.0, on every single class to tag its module (§2.14). |
| `dc:` | Dublin Core Elements | The older, simpler predecessor of `dcterms:`. | Declared as a prefix for compatibility; not heavily used in this ontology (we prefer `dcterms:`). |
| `foaf:` | Friend of a Friend | Vocabulary for describing people and their basic attributes/relationships (`foaf:Person`, `foaf:Agent`, `foaf:name`, `foaf:knows`). | New in v2.0.0: `ekpi:Role` is declared `rdfs:subClassOf foaf:Agent`, anchoring ownership/stewardship roles to a recognized upper-ontology concept. `foaf:name` is used on the Commercial Pricing Manager individual. |
| `skos:` | Simple Knowledge Organization System | Vocabulary purpose-built for controlled vocabularies/thesauri: concepts, preferred/alternate labels, broader/narrower relationships, and **collections** (grouping without taxonomy). | `BusinessTerm` is declared as a `skos:Concept`; uses `skos:prefLabel`, `skos:altLabel`, `skos:definition`. New in v2.0.0: `skos:Collection` individuals represent the six ontology modules (§2.14) — this is the SKOS feature that replaces the removed "bucket" superclasses. |
| `prov:` | PROV-O | Vocabulary for describing provenance: activities, entities, and how things were derived from or generated by other things. | `prov:wasDerivedFrom` chains the medallion layers; `TransformationStep`/`ProvenanceEvent`/`ApprovalEvent`/`AuditEvent` are `prov:Activity` subclasses; `prov:generated`/`prov:wasGeneratedBy` link a dataset to its producing run. |
| `schema:` | Schema.org | A broad, web-scale vocabulary for common entities (people, organizations, products). | Declared as a prefix for potential interoperability with web/SEO tooling; not required by our core model. |

### 1.7 Classes, properties, individuals — and our custom namespace vs. standard vocabularies

- **Classes** are *categories of things* (`ekpi:KPI`, `ekpi:GoldLayerDataset`, `ekpi:KPIObservation`). Written with `owl:Class`.
- **Properties** are *relationships or attributes* (`ekpi:hasDefinition`, `ekpi:targetValue`). Written with `owl:ObjectProperty` (relates two things/individuals) or `owl:DatatypeProperty` (relates a thing to a plain value like a number or string).
- **Individuals** are *specific instances* (`data:RackPriceCaptureRateKPI` is one specific KPI, not the category "KPI" itself).
- Our **custom enterprise namespace** (`ekpi:`) holds only *our* classes and properties — the schema we invented for this business.
- **Standard vocabularies** (`rdf:`, `rdfs:`, `owl:`, `skos:`, `prov:`, `foaf:`, etc.) are reused, not reinvented, so tools built for the wider Semantic Web ecosystem understand parts of our graph automatically.
- We keep **individuals in a separate namespace** (`data:`) from **schema in `ekpi:`** — this is a deliberate design choice explained in Stage 2, so data can be reloaded without ever touching the ontology definitions.

---

## Part 2 — Reading Turtle, piece by piece

### 2.1 "How to read a Turtle file" (quick-reference before the details)

A Turtle file is read top to bottom as:

1. **Prefix declarations** — the dictionary of shorthand names.
2. **One or more "ontology metadata" triples** — describing the file itself.
3. **Module-tagging individuals** — the six `skos:Collection`s classes will point back to (new in v2.0.0, see §2.14).
4. **Class declarations** — the nouns of your domain.
5. **Property declarations** — the verbs/attributes connecting those nouns.
6. **Individuals** — real data using the classes and properties above.

Every block you'll see follows the same visual pattern:

```turtle
SUBJECT
    predicate1 object1 ;
    predicate2 object2 ;
    predicate3 object3 .
```

Read the semicolon `;` as "same subject, next fact." Read the final period `.` as "end of this subject's facts." This is just a shorthand for repeating the subject on every line.

### 2.2 The prefix block

```turtle
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix ekpi:    <https://ontology.enterprise.example.com/kpi-store/core#> .
@prefix data:    <https://data.enterprise.example.com/kpi-store/> .
```

- `@prefix` — a Turtle directive (not an RDF triple itself) that registers a shorthand.
- `rdf:` — the alias you'll type.
- `<http://www.w3.org/1999/02/22-rdf-syntax-ns#>` — the full namespace IRI, in angle brackets. Angle brackets `< >` always mean "this is a full, literal IRI, not shorthand."
- The trailing `.` ends the directive line (Turtle directives, like triples, end in a period).

**Mini-glossary check:** *namespace* = the common IRI stem; *prefix* = the short alias for that stem; *IRI* = the full, globally unique identifier.

### 2.3 Declaring a class

```turtle
ekpi:KPI a owl:Class ;
    rdfs:subClassOf ekpi:Metric ;
    dcterms:isPartOf ekpi:KPIModelModule ;
    rdfs:label "KPI"@en ;
    rdfs:comment "A governed, named indicator of performance against a goal."@en .
```

Line by line:

- `ekpi:KPI` — the **subject**. Shorthand for `<https://ontology.enterprise.example.com/kpi-store/core#KPI>`.
- `a` — special Turtle shorthand for the predicate `rdf:type`. Reads as "is a." So `ekpi:KPI a owl:Class` means "KPI is a Class" — i.e., we're declaring KPI to *be* a class (a category), not an individual.
- `owl:Class` — the **object**: the built-in OWL type meaning "this is a category of things."
- `;` — "same subject (`ekpi:KPI`), here's another fact about it."
- `rdfs:subClassOf ekpi:Metric` — the predicate `rdfs:subClassOf` says every KPI is *also* a Metric — this is how genuine class hierarchies are built. (Recall from Stage 1: `KPI ⊑ Metric` means "every KPI is a Metric, but not vice versa," and this is a real logical claim we're comfortable making because every KPI genuinely *is* a kind of Metric.)
- `dcterms:isPartOf ekpi:KPIModelModule` — **new in v2.0.0.** This is a *metadata* fact, not a taxonomy fact — it says "for organizational/discovery purposes, KPI belongs to the KPI Model module." Crucially, this line makes no claim that `KPI` and, say, `Target` (also tagged with the same module) share any essential nature — it's a label, not a `subClassOf`. See §2.14 for why this replaces the old "bucket superclass" pattern.
- `rdfs:label "KPI"@en` — a human-readable name. `"KPI"` is a **string literal** (text data, in double quotes). The `@en` suffix is a **language tag** meaning "this text is in English" — useful if the ontology were later translated.
- `rdfs:comment "...."@en` — a longer human-readable description, same literal syntax.
- `.` — final period: "no more facts about `ekpi:KPI` in this block."

### 2.4 Declaring a property, with domain and range

```turtle
ekpi:hasDefinition a owl:ObjectProperty ;
    rdfs:label "has definition"@en ;
    rdfs:domain ekpi:KPI ;
    rdfs:range ekpi:KPIDefinition ;
    rdfs:comment "Relates a KPI to its documented, versioned KPIDefinition."@en .
```

- `a owl:ObjectProperty` — this declares `hasDefinition` to be a *relationship between two things* (an object property), as opposed to a *datatype property* (a relationship between a thing and a plain literal value, see next).
- `rdfs:domain ekpi:KPI` — "the subject side of this relationship should be a KPI."
- `rdfs:range ekpi:KPIDefinition` — "the object side should be a KPIDefinition."
- Think of `domain`/`range` exactly like a function signature: `hasDefinition: KPI → KPIDefinition`.

Compare with a **datatype property**:

```turtle
ekpi:targetValue a owl:DatatypeProperty ;
    rdfs:label "target value"@en ;
    rdfs:domain ekpi:Target ;
    rdfs:range xsd:decimal .
```

Here the **range is `xsd:decimal`**, a datatype, not a class — because a `Target`'s value is a plain number like `99.0`, not another linked resource.

### 2.5 Typed literals — `^^xsd:datatype`

```turtle
data:Target_99pct_Q4FY26 a ekpi:Target ;
    rdfs:label "Target 99% FY26 Q4"@en ;
    ekpi:targetValue "99.0"^^xsd:decimal .
```

- `"99.0"` — a string literal (everything in RDF starts as text).
- `^^xsd:decimal` — a **datatype suffix**: "interpret this text as a decimal number, not as a plain string." Without it, `"99.0"` would just be a piece of text a computer couldn't do math on. This is the RDF equivalent of type-casting.
- Compare: `"2026-07-31"^^xsd:date` (a calendar date), `"2026-07-15T10:00:00"^^xsd:dateTime` (date + time).

### 2.6 An individual, tying it all together

```turtle
data:RackPriceCaptureRateKPI a ekpi:KPI ;
    rdfs:label "Rack Price Capture Rate %"@en ;
    ekpi:kpiCode "KPI-COM-001" ;
    ekpi:criticality data:Criticality_High ;
    ekpi:alignsToObjective data:ImproveRackCapture99pctQ4FY26 ;
    ekpi:hasDefinition data:RackPriceCaptureRateDefinition_v1 ;
    ekpi:hasUnitOfMeasure data:PercentUnit .
```

- `data:RackPriceCaptureRateKPI a ekpi:KPI` — this is the crucial line where an **individual** is created: "there exists a specific thing, named `RackPriceCaptureRateKPI`, and it *is a* KPI." Notice `data:` (individual namespace) vs. `ekpi:` (schema namespace) — same syntax, different *role* in the graph.
- `ekpi:kpiCode "KPI-COM-001"` — a plain string literal with no datatype suffix; Turtle defaults untyped quoted strings to `xsd:string`.
- `ekpi:criticality data:Criticality_High` — **notice this is an object property, not a plain string.** `Criticality_High` is itself an individual belonging to a closed set (§2.11) — this is stricter, and more queryable, than writing `ekpi:criticality "High"` as free text.
- `ekpi:alignsToObjective data:ImproveRackCapture99pctQ4FY26` — an object-property edge connecting **two individuals**: this specific KPI aligns to this specific objective.
- Each of these lines is literally one triple: `(data:RackPriceCaptureRateKPI, ekpi:alignsToObjective, data:ImproveRackCapture99pctQ4FY26)`, etc. The semicolon syntax is just avoiding retyping the subject five times.

### 2.7 Chained/derived facts — `rdfs:subClassOf` vs. instance-level properties

Compare these two, which both use the word "narrower," but at different layers:

```turtle
ekpi:StrategicObjective a owl:Class ;
    rdfs:subClassOf ekpi:BusinessGoal .          # CLASS-level: every objective IS a goal-type thing

data:ImproveRackCapture99pctQ4FY26 a ekpi:StrategicObjective ;
    ekpi:narrowsGoal data:ProtectGrowCommercialMarginGoal .   # INSTANCE-level: this specific objective narrows that specific goal
```

This is a common beginner trap: `rdfs:subClassOf` only ever connects two **classes**. To connect two **individuals**, you need an ordinary object property (like `narrowsGoal`) — you cannot use `subClassOf` between two specific named things.

### 2.8 Lists and multiple values — the comma `,`

```turtle
data:RackPriceCaptureRateKPI
    ekpi:slicedByDimension data:TerminalDimension, data:ProductDimension .
```

- `,` — "same subject **and** same predicate, another object." This one line is actually two triples: the KPI is sliced by Terminal, and the KPI is sliced by Product.
- Contrast with `;` (same subject, *different* predicate) and `,` (same subject *and* predicate, different object). `.` always ends the whole subject block.

### 2.9 Restrictions and blank nodes — `[ ... ]`

```turtle
ekpi:KPI rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ekpi:ownedBy ;
    owl:someValuesFrom ekpi:BusinessOwner
] .
```

- The square brackets `[ ... ]` create a **blank node** — an unnamed, "anonymous" resource that exists only to hold this bundle of facts. It has no IRI of its own because nothing else in the graph needs to point *at* it directly; it's a throwaway helper node.
- Inside, `a owl:Restriction` says "this anonymous thing is an OWL restriction" — a formal constraint, not a real-world object.
- `owl:onProperty ekpi:ownedBy` — "the restriction is about the `ownedBy` property."
- `owl:someValuesFrom ekpi:BusinessOwner` — "...and requires at least one value of type BusinessOwner."
- Put together in plain English: *"Every KPI must have `rdfs:subClassOf` this restriction"* → *"Every KPI must have at least one `ownedBy` pointing to a `BusinessOwner`."* This is how OWL expresses a constraint that plain RDFS cannot: RDFS alone can't say "must have at least one" — that requires OWL's restriction machinery.
- **This particular restriction is the actual, checkable answer to "what makes a KPI different from a plain Metric"** — a `Metric` is not required to have an owner; a `KPI` is. Before v2.0.0, that distinction lived only in a comment; now a reasoner can verify it.

### 2.10 Inference with `owl:equivalentClass`

```turtle
ekpi:CertifiedDefinition owl:equivalentClass [
    a owl:Class ;
    owl:intersectionOf (
        ekpi:KPIDefinition
        [ a owl:Restriction ;
          owl:onProperty ekpi:hasCertificationStatus ;
          owl:hasValue data:Status_Certified ]
    )
] .
```

- `owl:equivalentClass` says the class on the left (`CertifiedDefinition`) means *exactly* the same thing as the anonymous class on the right — they're interchangeable.
- `owl:intersectionOf ( ... )` — a parenthesized **RDF list** of two things that must *both* be true: (1) being a `KPIDefinition`, and (2) matching the restriction that follows.
- The nested `owl:Restriction` with `owl:hasValue data:Status_Certified` says "the certification status property must equal exactly `Certified`."
- Net effect: a reasoning tool can automatically figure out *which* KPIDefinitions count as "Certified Definitions" just from their certification-status value — you never have to manually re-tag an individual as `CertifiedDefinition`; it's inferred.

### 2.11 Enumerations with `owl:oneOf`

```turtle
ekpi:Criticality a owl:Class ;
    owl:oneOf ( data:Criticality_High data:Criticality_Medium data:Criticality_Low ) .
```

- `owl:oneOf ( ... )` closes the class to *exactly* this list of individuals — nothing else can ever be a `Criticality`. This is how you model a fixed, governed set of allowed values (like an enum in a programming language) directly in the ontology.
- v2.0.0 adds three of these closed vocabularies that were previously loose `xsd:string` fields: `Criticality`, `ThresholdSeverity`, and `AggregationType` — alongside the one that already existed, `CertificationStatus`, and a brand-new one for the observation layer, `ObservationStatus` (§2.15). Closing a field like this means a data-quality check like "find every KPI with an invalid criticality value" becomes structurally impossible to violate, instead of something you hope every ETL job enforces.

### 2.12 Reusing a standard vocabulary property directly

```turtle
data:RackLiftings_SilverDataset a ekpi:SilverLayerDataset ;
    prov:wasDerivedFrom data:RackLiftings_RawDataset .
```

- Here we didn't invent our own "came from" predicate — we reused `prov:wasDerivedFrom` straight from the PROV-O vocabulary. Any provenance-aware graph tool already knows how to interpret this edge, which is the whole point of reusing standard vocabularies instead of reinventing them.

### 2.13 A small property hierarchy — `rdfs:subPropertyOf` (new in v2.0.0)

Just as classes can form a hierarchy with `rdfs:subClassOf`, *properties* can form a hierarchy with `rdfs:subPropertyOf`:

```turtle
ekpi:hasFormula a owl:ObjectProperty ;
    rdfs:subPropertyOf ekpi:hasSpecificationElement ;
    rdfs:domain ekpi:KPIDefinition ;
    rdfs:range ekpi:KPIFormula .
```

- `rdfs:subPropertyOf ekpi:hasSpecificationElement` says: "whenever `hasFormula` holds between two things, the broader `hasSpecificationElement` relationship also holds between them." This is the property-level equivalent of "every KPI is also a Metric."
- Practically, this means a query or reasoner asking "give me everything that specifies this KPI" via `hasSpecificationElement` will automatically pick up formulas, aggregation rules, units, targets, thresholds, time periods, and grains — without the query author needing to know or list all seven narrow predicate names.
- v2.0.0 introduces three such super-properties: `hasSpecificationElement` (groups KPI-spec properties), `hasGovernanceRecord` (groups certification/version/audit/access properties), and `hasSemanticComponent` (groups semantic-model composition properties).

### 2.14 Module tagging with `dcterms:isPartOf` and `skos:Collection` (new in v2.0.0 — replaces "bucket" superclasses)

v1.0.0 of this ontology grouped classes using four abstract superclasses — `BusinessArchitectureElement`, `SemanticAsset`, `LineageNode`, `GovernanceElement` — and every class in that module used `rdfs:subClassOf` to point at one of them. A review caught the problem: `rdfs:subClassOf` is a *logical* claim ("every member of the subclass genuinely is a kind of the superclass"), and it is simply false that a `BusinessCapability` and an `OrganizationalUnit` are the same *kind* of thing just because both belong to the business-architecture module. This is exactly the mistake Casey Hart's video critique flags: putting a bedroom and a shoe in one class because both are "things in a house."

The v2.0.0 fix separates *grouping* from *taxonomy*:

```turtle
ekpi:BusinessArchitectureModule a skos:Collection ;
    rdfs:label "Business Architecture Module"@en .

ekpi:BusinessCapability a owl:Class ;
    dcterms:isPartOf ekpi:BusinessArchitectureModule ;
    rdfs:label "Business Capability"@en .
```

- `ekpi:BusinessArchitectureModule a skos:Collection` — declares an individual (not a class!) whose whole job is to act as a labeled bucket. `skos:Collection` is purpose-built for exactly this: "a group of things," with zero implied shared essence.
- `ekpi:BusinessCapability ... dcterms:isPartOf ekpi:BusinessArchitectureModule` — a plain metadata fact: "for browsing/discovery purposes, this class is filed under the Business Architecture module." No claim about shared kind-hood is made.
- You can still write a query for "everything in the Business Architecture module" — you just do it by matching `dcterms:isPartOf ekpi:BusinessArchitectureModule`, not by matching `rdfs:subClassOf ekpi:BusinessArchitectureElement`. The query is equally easy to write; the difference is that the ontology no longer asserts something untrue to make that query possible.
- **Three superclasses survived this review** because they pass the "genuinely one kind of thing" test rather than the "convenient grouping" test: `ConsumptionAsset` (everything under it really is "a surface a human consumes KPI values through"), `PerformanceIndicator` (everything under it really is "a quantification of performance"), and `Dataset` (everything under it really is "a dataset at some medallion layer," which is also what makes the `owl:disjointWith` axioms between Raw/Silver/Gold meaningful — disjointness only makes sense between siblings under a shared parent).

### 2.15 The observation / fact layer — `KPIObservation` (new in v2.0.0)

Everything up to this point describes how a KPI is *defined*. But a definition alone can't answer "what did Rack Price Capture Rate actually read at Beaumont Terminal 1 last Tuesday, and was that good or bad?" That requires a separate class for the *fact* of a measurement:

```turtle
data:RackCaptureObs_Beaumont1_RBOB_20260731 a ekpi:KPIObservation ;
    rdfs:label "Rack Price Capture Rate — Beaumont Rack Terminal 1 / RBOB Gasoline — 2026-07-31"@en ;
    ekpi:measuresKPI data:RackPriceCaptureRateKPI ;
    ekpi:hasObservedValue "96.2"^^xsd:decimal ;
    ekpi:hasUnitOfMeasure data:PercentUnit ;
    ekpi:observedForPeriod data:Day_20260731 ;
    ekpi:observedForDimensionValue data:BeaumontRackTerminal1, data:RBOBGasolineProduct ;
    ekpi:computedAgainstTarget data:Target_99pct_Q4FY26 ;
    ekpi:computedAgainstThreshold data:RedThreshold_97pct ;
    ekpi:hasObservationStatus data:ObsStatus_Breach .
```

Reading this the same way we read §2.6: this individual *is a* `KPIObservation` (a fact/event, not a definition); it points at *which* KPI it's a reading of (`measuresKPI`); it carries the actual number (`hasObservedValue "96.2"`); it says *when* (`observedForPeriod`) and *for which specific dimension values* — note the plural, comma-separated object in §2.8's pattern — it applies (`observedForDimensionValue`, pointing at individuals of the new `DimensionValue` class, distinct from `Dimension` itself, which just names the axis "Terminal" or "Product" in the abstract); and finally, because `hasObservationStatus` is declared `owl:FunctionalProperty` (exactly one current value allowed, same pattern as §2.11's `hasCertificationStatus`), it has exactly one status — here, `ObsStatus_Breach`, because 96.2% is below the 97% red threshold.

This is the pattern to reuse any time you need to move an ontology from "describes definitions" to "describes what actually happened": add a Fact/Observation/Event class with a `measures`-style pointer back to the thing being measured, a value, a time period, and (if relevant) the dimension values and evaluated-against target/threshold.

---

## Part 3 — Mini glossary

| Term | Plain-language meaning |
|---|---|
| **Triple** | One fact: subject–predicate–object. The atomic unit of RDF. |
| **IRI** | A globally unique name for a thing, like a very precise, permanent address. |
| **Prefix** | A short nickname for a namespace, so you don't type full IRIs. |
| **Namespace** | The common IRI "stem" shared by a family of related terms. |
| **Class** | A category of things (e.g., KPI, Dataset, KPIObservation). |
| **Individual** | One specific instance of a class (e.g., *this* Rack Price Capture Rate KPI, *this* observation of it on 2026-07-31). |
| **Object property** | A relationship between two things/individuals. |
| **Datatype property** | A relationship between a thing and a plain literal value (string, number, date). |
| **Literal** | A plain value like `"99.0"` or `"2026-07-31"`, optionally typed with `^^xsd:...`. |
| **Blank node** | An unnamed helper node, written `[ ... ]`, used for facts that don't need their own address. |
| **rdfs:subClassOf** | "Every member of the first class is also a member of the second." Class-level only — and a real logical claim, not just a convenient label (§2.14). |
| **rdfs:subPropertyOf** | The same idea as `subClassOf`, one level up: "every use of this property implies the broader property also holds." *(new)* |
| **dcterms:isPartOf** + **skos:Collection** | The v2.0.0 pattern for honest grouping without a false taxonomy claim — tags a class as belonging to a module without asserting shared kind-hood. *(new)* |
| **owl:Restriction** | A formal constraint on how a property may be used for members of a class. |
| **owl:equivalentClass** | "These two class descriptions mean the same thing" — enables inference. |
| **owl:oneOf** | Closes a class to an exact, fixed list of individuals — a governed enumeration. |
| **owl:FunctionalProperty** | A property that can hold at most one value per subject — e.g., an observation has exactly one status. |
| **Ontology** | A formal, machine-readable specification of the concepts and relationships in a domain. |
| **Reasoner** | Software that derives new facts (like inferred class membership) from asserted RDF/OWL facts. |
| **Lineage** | The traceable path showing where a piece of data came from and how it was transformed. |
| **Medallion architecture** | The Raw (Bronze) → Silver → Gold data-refinement pattern used in modern data platforms. |
| **Semantic layer** | A governed translation layer that maps physical data to business-friendly meaning. |
| **Certification** | A governance state confirming an asset (KPI, definition, dataset) is trusted and approved. |
| **Fact / observation layer** | The part of an ontology that records what was actually measured/happened, as opposed to how something is defined. *(new concept for this version — see §2.15)* |

---

## Part 4 — How this ontology maps to enterprise data architecture

| Enterprise architecture concept | Ontology representation |
|---|---|
| Source systems (CTRM/ETRM, market-data feeds) | `ekpi:OperationalSystem`, `ekpi:SourceApplication`, `ekpi:SourceTable`, `ekpi:SourceField` — worked example: RightAngle CTRM and OPIS Market Data Service |
| Medallion architecture (bronze/silver/gold) | `ekpi:RawLayerDataset` → `ekpi:SilverLayerDataset` → `ekpi:GoldLayerDataset`, chained with `prov:wasDerivedFrom`, and now backed by `owl:Restriction`s that make each hop a checkable requirement, not just a convention |
| ETL/ELT pipelines | `ekpi:DataPipeline` composed of `ekpi:TransformationStep` individuals (each a `prov:Activity`) |
| Semantic/BI layer (e.g., a metrics layer or BI tool's model) | `ekpi:SemanticLayer` → `ekpi:SemanticModel` → `ekpi:SemanticEntity`/`ekpi:SemanticMeasure`/`ekpi:SemanticRelationship` |
| Business glossary | `ekpi:BusinessTerm` (a `skos:Concept`) with `skos:prefLabel`/`skos:altLabel`/`skos:definition` — `skos:altLabel` also absorbs the job the removed `Synonym` class used to do |
| KPI catalog (definitions) | `ekpi:KPI` individuals, each with a `ekpi:KPIDefinition`, `ekpi:KPIFormula`, and governance edges |
| KPI performance history (new) | `ekpi:KPIObservation` individuals — actual dated, dimensioned readings, each with a status relative to its target/threshold |
| BI dashboards/reports | `ekpi:Dashboard`, `ekpi:Report`, `ekpi:Scorecard`, `ekpi:AnalyticalModel`, linked via `consumedBy`/`usedInUseCase` |
| Data governance program | `ekpi:Policy` → `ekpi:Standard` → `ekpi:Control`, plus `ekpi:CertificationStatus`, `ekpi:Version`, `ekpi:ApprovalEvent`, `ekpi:AuditEvent`, `ekpi:StewardshipAssignment` |
| Module organization (new) | Six `skos:Collection` individuals (`BusinessArchitectureModule`, `KPIModelModule`, `SemanticModelModule`, `LineageModule`, `ConsumptionModule`, `GovernanceModule`) tagged via `dcterms:isPartOf`, replacing the old bucket-superclass approach |

## Part 5 — How governance is represented *semantically*

Governance is not a separate spreadsheet bolted onto the ontology — it's expressed as ordinary RDF/OWL facts attached to the same nodes everything else touches:

- **Ownership/stewardship** are graph edges: `data:RackPriceCaptureRateKPI ekpi:ownedBy data:CommercialPricingManager` and `ekpi:stewardedBy data:CommercialDataSteward` are triples exactly like any other — no different mechanism than "KPI aligns to objective."
- **A KPI is now required to have an owner** — new in v2.0.0, via the `owl:Restriction` from §2.9. This is the actual reasoner-checkable difference between a governed `KPI` and a plain `Metric`.
- **Trust state** is a class membership fact: `hasCertificationStatus` is declared `owl:FunctionalProperty`, meaning OWL logically guarantees a governed asset can have *only one* current status at a time — the ontology itself enforces "you can't be simultaneously Draft and Certified."
- **Certification as inference:** because `CertifiedDefinition` is defined via `owl:equivalentClass` from the certification-status value, a reasoner can *derive* "this is a certified definition" automatically — governance status and class membership can never silently drift out of sync.
- **Change history** is modeled as its own individuals (`ekpi:Version`, `ekpi:ApprovalEvent`, `ekpi:AuditEvent`) with timestamps and links back to the definition they apply to — so "what changed, when, and who approved it" is answerable by walking edges, not by searching a change log outside the graph.
- **Stewardship now has a real, time-bound record**, not just a label: `data:CommercialPricingStewardshipAssignment` carries `assignmentSteward` and `assignmentStartDate`, distinct from (and complementary to) the denormalized `stewardedBy` shortcut on the KPI itself.

## Part 6 — Tracing a dashboard back to a source field

Take `data:CommercialPricingDashboard`. To find out exactly where its numbers physically originate, you walk the graph *backwards* through these edges (each one a real triple in the Turtle file):

```
CommercialPricingDashboard
   ← consumedBy ←  RackPriceCaptureSemanticMeasure       (the governed semantic measure that feeds this dashboard)
   ← realizesKPI ←  RackPriceCaptureRateKPI                (the KPI this semantic measure implements)
   RackPriceCaptureSemanticMeasure is part of → CommercialPricingSemanticModel
   CommercialPricingSemanticModel ← feedsSemanticModel ← RackLiftings_GoldDataset   (one of two gold datasets behind the semantic model)
   RackLiftings_GoldDataset ← prov:wasDerivedFrom ← RackLiftings_SilverDataset
   RackLiftings_SilverDataset ← prov:wasDerivedFrom ← RackLiftings_RawDataset
   RackLiftings_RawDataset ← prov:wasDerivedFrom ← NetPricePerGalField
   NetPricePerGalField → originatesIn → RightAngleCTRM   (the RightAngle CTRM/ETRM system, source of truth for realized revenue)
```

A second, parallel chain exists behind the same dashboard for the benchmark side of the KPI:

```
CommercialPricingSemanticModel ← feedsSemanticModel ← OPISBenchmark_GoldDataset
   OPISBenchmark_GoldDataset ← prov:wasDerivedFrom ← OPISBenchmark_SilverDataset
   OPISBenchmark_SilverDataset ← prov:wasDerivedFrom ← OPISBenchmark_RawDataset
   OPISBenchmark_RawDataset ← prov:wasDerivedFrom ← RackPriceUSDGalField
   RackPriceUSDGalField → originatesIn → OPISMarketDataService   (the OPIS Rack Price Feed, source of truth for the published benchmark)
```

Every arrow above is a *literal edge* asserted in Stage 2's Turtle file — nothing here is guesswork or documentation living outside the graph. A SPARQL query (RDF's query language) could walk either exact path programmatically, which is precisely why lineage was modeled as first-class graph structure instead of a diagram in a wiki page. Notice that one KPI can legitimately have *two* independent lineage chains feeding it (realized revenue and published benchmark) — the ontology doesn't force a single-source assumption.

You can go one step further than v1.0.0 could: from `RackPriceCaptureRateKPI`, follow `measuresKPI` *backwards* from any `KPIObservation` (e.g., `data:RackCaptureObs_Beaumont1_RBOB_20260731`) to land on the same KPI, then continue the same trace above — so a single query can go from "this specific number, on this specific day, at this specific terminal, was in breach" all the way back to the exact source field, in one graph.

---

## Closing note: what the ontology is actually "doing"

Every `@prefix`, every `a owl:Class`, every `;` and `.` is ultimately in service of one goal: building a **graph of meaning**, not just a file. The Turtle syntax is disposable — you could regenerate the exact same facts as JSON-LD tomorrow. What matters, and what persists, is the *graph*: a KPI connected to its formula, its source data, its dashboard, its approver, and now its actual observed history, all as traversable, queryable, machine-checkable relationships instead of tribal knowledge scattered across spreadsheets, wikis, and people's memories. The v2.0.0 corrections didn't add complexity for its own sake — every fix (removing false groupings, adding the observation layer, closing loose vocabularies, adding restrictions) makes the graph say something *truer* and something a reasoner or query can actually *check*, which is the whole point of choosing OWL over a plain diagram in the first place.
