# Enterprise Ontology Design — Best Practices Standard

*A durable reference for anyone building or extending an RDF/OWL ontology on this team. Synthesized from (a) Casey Hart's ontology critique video and (b) hands-on lessons from designing, reviewing, and correcting the Enterprise KPI Ontology (v1.0.0 → v2.0.0), worked through the Downstream Oil & Gas Commercial "Rack Price Capture Rate %" example.*

*Maintain this document as a living standard: update it whenever a review of a new ontology surfaces a genuinely new lesson. Treat it as the checklist a reviewer runs before signing off on any ontology, not just this one.*

---

## Why this document exists

Large language models are good at producing an ontology that *parses* — valid Turtle, plausible-looking classes, reasonable labels and comments. They are much less reliable at producing an ontology that *models the domain correctly*. The gap between "compiles" and "is actually right" is exactly where a human ontologist's judgment has to do the work. Casey Hart's video ["I Asked ChatGPT to Build an Ontology. Here's What Happened."](https://youtu.be/pNwHu5ecsmI) (*Ontology Explained: Philosophy and AI*, Jul 31, 2026) demonstrates this gap directly: he gives ChatGPT a real estate listing, has it generate a Turtle ontology, and then reviews the result as a working ontologist — finding a syntactically valid file riddled with structural mistakes that only show up once you ask "does this actually hold up as a model of the domain?"

We ran our own KPI ontology through the same style of review and found the identical failure modes, in our own domain-specific clothing. This document distills both experiences into standing rules — not a one-time fix log, but a checklist to apply to *every* ontology this team builds from here on.

---

## The core discipline: two different questions, and never confusing them

Almost every mistake below reduces to conflating two questions that must be asked and answered separately:

1. **"Is this a genuine kind of that thing?"** — the question `rdfs:subClassOf` answers. It is a logical claim: every member of the subclass really *is* a member of the superclass, full stop, in every context.
2. **"Do I want to group these together for some other reason (documentation, browsing, module ownership)?"** — a *metadata* question. It should never be answered with `rdfs:subClassOf`.

Every one of the "bucket superclass," "orphan class," and "free-text field" mistakes below is, underneath, a case of reaching for the taxonomy tool to solve a grouping or labeling problem. Once you internalize this distinction, most of the rest of this document is just its consequences worked out in different parts of an ontology.

---

## 1. The "genuine kind" test — don't build bucket superclasses

**The mistake, as Hart found it:** ChatGPT's top class `Property` had `Address`, `Parcel`, `Building`, `Listing`, and `Transaction` all as subclasses — things *related to* a property, but not themselves properties. He also flagged `OutdoorFeature` (patio + hot tub + irrigation system bundled together) as an arbitrary "hodgepodge."

**The mistake, as we found it in our own ontology:** we had introduced six abstract superclasses — `BusinessArchitectureElement`, `SemanticAsset`, `LineageNode`, `GovernanceElement`, `KPISpecificationElement` — purely to organize our six documentation modules, not because their members shared any essential nature. For example, `SemanticAsset` had `SemanticModel`, `SemanticAttribute`, `BusinessTerm`, and `MappingRule` as children — a model, an attribute, a glossary term, and a mapping rule are simply not the same *kind* of thing; they just all happen to live in the "semantic module" of our documentation.

**The test to apply, every time you're about to write `rdfs:subClassOf`:** ask "is every single member of the subclass *always and necessarily* a member of the superclass, in every context, with no exceptions?" If the honest answer is "well, they're all kind of related to the same topic" — that is a grouping, not a taxonomy, and `rdfs:subClassOf` is the wrong tool.

**The fix that passed the test and the fix that failed it, side by side:**

| Superclass | Verdict | Why |
|---|---|---|
| `ConsumptionAsset` (parent of `Report`, `Dashboard`, `Scorecard`, `AnalyticalModel`) | **Kept** — genuine subsumption | Every single member really is "a surface a human consumes KPI values through." No exceptions. |
| `PerformanceIndicator` (parent of `Metric`, `Measure`) | **Kept** — genuine subsumption | Every member really is "a quantification of performance." |
| `Dataset` (parent of `RawLayerDataset`/`SilverLayerDataset`/`GoldLayerDataset`) | **Kept** — genuine subsumption, and it makes the `owl:disjointWith` axioms between the three layers meaningful (disjointness only makes sense between siblings under a real shared parent) | Every member really is "a dataset at some medallion layer." |
| `BusinessArchitectureElement`, `SemanticAsset`, `LineageNode`, `GovernanceElement`, `KPISpecificationElement` | **Removed entirely** | Members were only "related to the same module," not the same kind of thing. |

**The standing rule:** before writing any abstract superclass whose only job is to group things, run the genuine-kind test above out loud. If it fails, do not create the class — solve the grouping need with the module-tagging pattern in section 2 instead.

---

## 2. Solve grouping needs with `dcterms:isPartOf` + `skos:Collection`, never with false taxonomy

**The fix we landed on:** replace every bucket superclass with a `skos:Collection` individual representing the module, and tag each class's *real* membership in that module with `dcterms:isPartOf` — a plain metadata fact, not a class-hierarchy claim.

```turtle
ekpi:BusinessArchitectureModule a skos:Collection ;
    rdfs:label "Business Architecture Module"@en .

ekpi:BusinessCapability a owl:Class ;
    dcterms:isPartOf ekpi:BusinessArchitectureModule ;
    rdfs:label "Business Capability"@en .
```

This preserves everything the bucket superclass was actually useful for — you can still query "everything in the Business Architecture module" by matching `dcterms:isPartOf ekpi:BusinessArchitectureModule` — while asserting nothing false about shared kind-hood. `skos:Collection` exists precisely for "a group of things with no implied shared essence," which is exactly the semantics a documentation module needs.

**The standing rule:** any time you want to group classes for browsing, ownership, module structure, or documentation — and the genuine-kind test in section 1 fails — use `dcterms:isPartOf` pointing at a `skos:Collection` individual. Never let a grouping need pull you back into `rdfs:subClassOf`.

---

## 3. Model transactions/measurements as their own event/fact class, not as a nested attribute

**The mistake, as Hart found it:** the generated ontology modeled the property's *sale* as an oddly-nested attribute on the property rather than as its own event with a value, a unit, and a date — which quietly blocks the query he cares about most: comparing multiple sales or price points over time.

**The mistake, as we found it:** our v1.0.0 ontology fully modeled a KPI's *definition*, its *lineage*, and its *governance* — but never modeled an actual measured value over time. There was no class carrying a number, a unit, a period, a dimension context, and a computed status. As built, the graph could answer "what is Rack Price Capture Rate and where does its data come from," but not "what was Rack Price Capture Rate at Beaumont Terminal 1 last Tuesday, and was it above target?" — which is the entire point of a KPI store.

**The fix — the Observation/Fact pattern:** add a class (we called it `KPIObservation`) whose instances are *events*, not attributes, each carrying:
- a pointer back to what's being measured (`measuresKPI` → `KPI`)
- the actual value and its unit (`hasObservedValue` datatype property, `hasUnitOfMeasure`)
- when (`observedForPeriod` → `TimePeriod`)
- in what context (`observedForDimensionValue` → specific `DimensionValue` individuals — which terminal, which product)
- what it was evaluated against (`computedAgainstTarget`, `computedAgainstThreshold`)
- a derived/functional status (`hasObservationStatus`, declared `owl:FunctionalProperty` so at most one status can hold at a time)

**The standing rule:** whenever a domain has something that happens repeatedly over time and needs to be compared across occurrences (a sale, a reading, a shift's output, a KPI value), give it its own event/fact class from day one. Do not let it live as a nested attribute on the "static" definition object — that structurally blocks the time-series queries the domain almost certainly needs.

---

## 4. Reconcile the design narrative against the actual implementation — don't let them drift

**The mistake, as Hart found it:** he repeatedly checks the model's own internal claims against what was actually built — e.g., a declared `SingleFamilyResidence` class that's never used anywhere.

**The mistake, as we found it:** a design-doc audit turned up real drift between our Stage 1 narrative and the Stage 2 Turtle:
- `Target` was documented as having both `targetValue` **and** `targetPeriod` — only `targetValue` was ever implemented.
- `TimePeriod` was documented as a full class with `periodStart`/`periodEnd`/`periodGranularity` — zero individuals of it existed anywhere.
- `Synonym` and `SemanticRelationship` were declared classes, never instantiated or connected by any property — pure orphans.
- Several classes (`ValueStream`, `BusinessFunction`, `ProcessStep`, `DataProduct`, `AnalyticalModel`, `AccessRule`) had no individuals anywhere in the worked example — untested, unverified.
- `StewardshipAssignment` existed as a class but the one individual of it had zero properties beyond a label — it didn't even link to a steward or a time period. An inert placeholder, not a real record.

**The fix:** we closed every one of these gaps rather than letting them stand as silent debt — implemented `targetPeriod` and real `TimePeriod` individuals, removed `Synonym` (its job is fully covered by `skos:altLabel`) and `SemanticRelationship` as classes with no supporting properties, gave `StewardshipAssignment` real properties (`assignmentSteward`, `assignmentStartDate`, `assignmentEndDate`) and a populated individual, and made sure every remaining declared class has at least one individual in the worked example.

**The standing rule:** periodically (and always before calling an ontology "done") run a literal side-by-side audit: for every class/property mentioned in the design doc, confirm it's actually used in the Turtle with at least one real individual; for every class/property in the Turtle, confirm the design doc's description still matches. Anything declared but never used should be removed, implemented, or explicitly flagged "future extension" — never left to silently imply coverage that doesn't exist.

---

## 5. Back up every meaningful subclass distinction with an `owl:Restriction`

**The mistake, as Hart found it:** `Bedroom` had a label and a comment, but nothing in the ontology actually said what makes a room a bedroom (a closet? an egress window? a minimum area?). A human reading the comment understands the distinction; a reasoner — or another system querying the graph — cannot.

**The mistake, as we found it:** outside one restriction on `KPI hasDefinition`, every other class distinction we'd introduced lived only in prose: nothing formally distinguished a `KPI` from a plain `Metric` beyond `rdfs:subClassOf`, and nothing formally distinguished `GoldLayerDataset` from `SilverLayerDataset` beyond `owl:disjointWith` (which says they're mutually exclusive but not *why*).

**The fix:** for every subclass pair introduced for a real reason, add at least one restriction that operationalizes the distinction:
- `KPI rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ekpi:hasDefinition ; owl:someValuesFrom ekpi:KPIDefinition ]` **and** a second restriction requiring `ownedBy someValuesFrom BusinessOwner` — a `Metric` isn't required to have either; a `KPI` is, and now a reasoner can check it.
- `RawLayerDataset` requires `prov:wasDerivedFrom someValuesFrom SourceField`.
- `SilverLayerDataset` requires `prov:wasDerivedFrom someValuesFrom RawLayerDataset`.
- `GoldLayerDataset` requires `feedsSemanticModel someValuesFrom SemanticModel`.

**The standing rule:** a comment describing what makes a subclass different is a starting point, not an ending point. Before considering a subclass distinction "modeled," ask "could a reasoner or a validator actually tell these two classes apart from the asserted facts alone?" If not, add the restriction.

---

## 6. Give properties a hierarchy too — not just classes

**The mistake, as Hart found it:** he wants object properties organized under general relations like `hasPart`, so narrow properties either justify themselves individually or fold into the general relation.

**The mistake, as we found it:** we had roughly 35 object properties declared completely flat, with zero `rdfs:subPropertyOf` anywhere. Properties like `hasFormula`, `hasAggregationRule`, `hasUnitOfMeasure`, `hasTarget`, `hasThreshold`, `hasTimePeriod`, and `hasGrain` are all conceptually siblings — each is "a piece of a KPI's specification" — but the graph offered no way to query "everything that specifies this KPI" without naming all seven predicates individually.

**The fix:** introduce a small number of super-properties via `rdfs:subPropertyOf`:
- `hasSpecificationElement` — parent of the seven KPI-spec properties above.
- `hasGovernanceRecord` — parent of `hasCertificationStatus`, `hasVersion`, `auditedBy`, `restrictedBy`.
- `hasSemanticComponent` — parent of `hasSemanticEntity`, `hasSemanticMeasure`, `hasSemanticAttribute`.

While doing this, we also resolved a related redundancy: we had both a denormalized `stewardedBy` shortcut directly on the KPI *and* a full `StewardshipAssignment` record class. Rather than collapsing one into the other, we kept both deliberately — see section 9.

**The standing rule:** once you have more than a handful of properties that answer "what kind of information about X is this," add a super-property with `rdfs:subPropertyOf` so "give me everything of this general kind" is a one-hop query instead of an enumeration a caller has to keep in sync by hand.

---

## 7. Close free-text fields into controlled vocabularies with `owl:oneOf`

**The mistake, as Hart found it:** underspecified terms get interpreted inconsistently by different users — his example is "city," which could mean a plain string or a geographic entity depending on who's populating the data.

**The mistake, as we found it:** we had correctly closed `CertificationStatus` into an `owl:oneOf` enumeration, but left several other categorical fields as free `xsd:string` values, inviting exactly the inconsistency Hart warns about — `criticality` ("High" vs. "high" vs. "HIGH" vs. "Critical"), `thresholdSeverity` ("Red" with no enumeration), `aggregationType` ("SUM" vs. "Sum" vs. "total").

**The fix:** apply the same `owl:oneOf` pattern everywhere a field has a genuinely fixed, governed set of allowed values:

```turtle
ekpi:Criticality a owl:Class ;
    owl:oneOf ( data:Criticality_High data:Criticality_Medium data:Criticality_Low ) .
```

We closed `Criticality`, `ThresholdSeverity`, and `AggregationType` this way, and added a new one for the observation layer, `ObservationStatus` (`OnTarget`/`Watch`/`Breach`).

**The standing rule:** any time a field's legal values are a small, known, governed set — not open-ended free text — model it as a class closed with `owl:oneOf` over named individuals, not as an `xsd:string`. This turns "find every record with an invalid value" from a data-quality monitoring problem into a structural impossibility.

---

## 8. Write competency questions before (and after) modeling, and actually trace them

**What Hart flagged:** good ontology engineering starts from "what will people actually need to query" and checks the vocabulary against that list before calling the model complete — not after, and not "eventually."

**Where we fell short initially:** our Stage 1 doc listed benefits qualitatively ("supports impact analysis," "supports reuse") but never wrote an explicit, checkable list of competency questions, and never verified the ontology could actually answer each one via a real graph traversal.

**The fix — and the standing practice:** write 10–15 concrete competency questions up front, phrased the way a real user would ask them — e.g., "Which dashboards break if this source field changes?", "Which KPIs are currently below threshold, by domain?", "Who approved the last change to this KPI's formula, and when?", "What was this KPI's value at this location on this date, and was it in breach?" For each one, trace the exact SPARQL path (or actually run it once loaded into a triple store) that answers it using only the current classes and properties. Any question you can't trace end-to-end is a real modeling gap, not a hypothetical one — this exercise is precisely what would have caught our missing Observation layer months earlier, had we done it first.

**The standing rule:** treat competency questions as a design input, not a post-hoc QA step. Write them before modeling begins where possible, and re-run the trace after every significant ontology revision — a new version that can no longer answer an old competency question is a regression, even if it parses cleanly.

---

## 9. Promote structured facts out of `rdfs:comment` — but don't discard denormalized shortcuts without checking they're pulling separate weight

**The mistake, as Hart found it:** a chef's kitchen's island, granite countertops, and custom cabinetry were described only in a comment string — never modeled as queryable facts a system could actually filter or compare on.

**The mistake, as we found it:** our SQL calculation logic for a KPI lived entirely inside an `rdfs:comment` string, with no structured datatype property — so, unlike a KPI's formula expression, the calculation logic wasn't queryable or comparable across KPIs.

**The fix:** promote it to a real datatype property (`logicExpression`), keeping the comment only as an *additional*, human-friendly gloss — never the sole carrier of a fact anyone might need to query.

**A related, subtler lesson — don't over-correct into false redundancy:** during the property-hierarchy pass (section 6) we noticed both a denormalized `stewardedBy` edge directly on the KPI and a full `StewardshipAssignment` class with `assignmentSteward`/`assignmentStartDate`/`assignmentEndDate`. The instinct is to treat this as duplication and collapse it to one. We deliberately kept both, because they answer different questions: `stewardedBy` answers "who owns this *right now*, in one hop, for a dashboard tooltip" cheaply; `StewardshipAssignment` answers "who has been the steward of this asset, over what date ranges, as an authoritative auditable record" — a question `stewardedBy` alone cannot answer once a steward changes. The rule isn't "eliminate every shortcut that duplicates information also present elsewhere" — it's "keep a shortcut only if it demonstrably serves a query that the authoritative record makes expensive, and keep the authoritative record only if it captures something the shortcut structurally cannot (here: time-boundedness and history)." Cutting either one loses real capability.

**The standing rule:** anything a person might reasonably want to filter, compare, or query on should be a structured property, not comment prose. Separately, before collapsing two properties that look redundant, check whether one is a cheap denormalized shortcut and the other an authoritative time-bound record — if so, keep both, and document why in a comment so a future reviewer doesn't "fix" it away.

---

## 10. Anchor floating classes to a recognized upper-ontology concept

**What Hart flagged:** he wants `Organization` declared as a subclass of `Agent` rather than left floating as an isolated, un-anchored term — connecting it to a shared, widely-understood upper concept makes the ontology's "who/what can act, own, approve" semantics explicit instead of implicit.

**Where we had the same issue:** `BusinessOwner` and `DataSteward` were subclasses of our local `Role` class, and individuals even carried a `foaf:name` — but `Role` itself was never related to `foaf:Agent`, `foaf:Person`, or any equivalent recognized upper concept, so the "this is a thing capable of approving/owning/stewarding" semantics were implicit rather than declared.

**The fix:** `ekpi:Role rdfs:subClassOf foaf:Agent`. One line, and now any tool or reasoner that already understands FOAF's `Agent` concept understands that our roles are agents too, without us having to explain our local vocabulary from scratch.

**The standing rule:** before inventing a purely local root class for people/organizations/systems that act, check whether a widely-adopted vocabulary (`foaf:Agent`, `prov:Agent`, `schema:Thing`, etc.) already has the right concept, and anchor to it with `rdfs:subClassOf`. Reserve fully local root classes for concepts that are genuinely domain-specific with no reasonable upper-ontology analog.

---

## 11. Use SKOS labeling consistently, not on just one class

**What Hart flagged:** he'd like to see `skos:prefLabel`/`skos:altLabel` used even in a first pass, not reserved for a single showcase class.

**Where we had the same issue:** we used `skos:prefLabel`/`altLabel`/`definition` only on `BusinessTerm` individuals; every other class and property used plain `rdfs:label`/`rdfs:comment` only.

**The fix — applied pragmatically, not maximally:** we extended `skos:altLabel` to a few more heavily-reused classes/properties where a genuine alternate name exists (e.g., a KPI's business-glossary synonym), without mechanically turning every single class into a full SKOS concept — that would add ceremony with no query benefit for classes nobody refers to by more than one name.

**The standing rule:** reserve SKOS labeling for terms that actually have alternate names or benefit from a formal preferred/alternate distinction. Don't apply it as decoration, and don't limit it to a single showcase example either — apply it wherever the underlying need (a real synonym, a real preferred-vs-informal name) actually exists.

---

## Quick-reference checklist

Run this list before signing off on any ontology (new or revised):

- [ ] Every `rdfs:subClassOf` passes the genuine-kind test — no bucket superclasses built purely for documentation grouping.
- [ ] Every module/documentation grouping is expressed via `dcterms:isPartOf` → `skos:Collection`, not via a false taxonomy.
- [ ] Anything that happens repeatedly over time (a measurement, a transaction, an event) has its own Fact/Observation/Event class — never nested as an attribute on a static definition.
- [ ] Every class and property mentioned in the design narrative has at least one real individual/usage in the implementation, and vice versa — no silent drift, no orphans.
- [ ] Every subclass distinction that matters has at least one `owl:Restriction` a reasoner could check — not just a comment.
- [ ] Properties with more than a handful of siblings answering the same general question have a super-property via `rdfs:subPropertyOf`.
- [ ] Any field with a small, known, governed set of legal values is closed with `owl:oneOf`, not left as free `xsd:string`.
- [ ] A written, traceable list of competency questions exists and has been walked end-to-end against the current model.
- [ ] Anything a user would filter/compare/query on is a structured property, not comment prose — while genuinely distinct shortcut-vs-authoritative-record pairs are kept, not collapsed.
- [ ] Locally-invented root classes for agents/actors are anchored to a recognized upper-ontology concept (`foaf:Agent`, `prov:Agent`, etc.) where a reasonable one exists.
- [ ] SKOS labeling (`prefLabel`/`altLabel`) is applied wherever a real alternate-name need exists — consistently, not as a one-off showcase.

---

## Provenance

- Primary external source: [I Asked ChatGPT to Build an Ontology. Here's What Happened.](https://youtu.be/pNwHu5ecsmI) — Casey Hart, *Ontology Explained: Philosophy and AI* (Jul 31, 2026).
- Primary internal source: the Enterprise KPI Ontology review-and-correction cycle (v1.0.0 → v2.0.0), worked through the Downstream Oil & Gas Commercial "Rack Price Capture Rate %" example — see the companion artifacts "Ontology Review & Improvement Plan," "Stage 1 — KPI Ontology Design Blueprint," "Stage 2 — Enterprise KPI Ontology (Turtle)," "Stage 2 — Ontology Explanation," and "Stage 3 — RDF/OWL Teaching Document."
