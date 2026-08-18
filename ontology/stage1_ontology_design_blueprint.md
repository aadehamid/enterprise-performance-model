# Enterprise KPI Ontology — Design Blueprint (Stage 1)

*Version 2.0.0 — corrects the v1.0.0 class-tree issues identified in the companion "Ontology Review & Improvement Plan" document (itself triggered by a critique of ["I Asked ChatGPT to Build an Ontology. Here's What Happened."](https://youtu.be/pNwHu5ecsmI), Casey Hart) and replaces the worked example with a Downstream Oil & Gas Commercial scenario: Rack Price Capture Rate %.*

## 0. Scope and framing

This blueprint is the conceptual design for a governed **Enterprise KPI Ontology**: the semantic foundation that ties KPI definitions to business architecture, a semantic layer, medallion-architecture data lineage, and governance/certification — so that every KPI a dashboard shows can be traced back to a trusted definition, a trusted calculation, and a trusted source field.

Six modules make up the ontology. Each is designed to stand alone (so teams can adopt incrementally) while sharing a common namespace and a small set of "bridge" object properties that stitch the modules into one graph. **Module membership is expressed honestly as metadata (`dcterms:isPartOf` a `skos:Collection`), not as a false shared superclass** — see §1a and the class tables in §2 for why this matters.

| # | Module | Answers the question |
|---|--------|----------------------|
| 1 | Business Architecture | Why does this KPI exist, and who in the business cares? |
| 2 | KPI Model | What exactly is being measured, how, against what target, and what was actually observed? |
| 3 | Semantic Model | What is the one governed, reusable definition consumers should bind to? |
| 4 | Lineage & Data Architecture | Where did the numbers physically come from, and how did they get transformed? |
| 5 | Consumption | Where does the KPI actually show up for a human? |
| 6 | Governance | Who owns/approved/certified this, and can we audit it? |

---

## 1. Major domains / modules of the ontology

**1. Business Architecture Module** — captures the enterprise's strategic and operating structure: capabilities, value streams, domains, functions, processes, process steps, goals, strategic objectives, org units, roles.

**2. KPI Module** — the measurement core, in two layers:
  - *Specification layer* (the KPI's definition): KPI, KPIDefinition, Measure, Metric, KPIFormula, CalculationLogic, AggregationRule, UnitOfMeasure, Target, Threshold, Dimension, TimePeriod, Grain.
  - *Observation / fact layer* (an actual reading of the KPI over time): **KPIObservation, DimensionValue, ObservationStatus** — new in v2.0.0.

**3. Semantic Model Module** — the governed "single source of meaning" layer: SemanticModel, SemanticLayer, SemanticEntity, SemanticAttribute, SemanticMeasure, SemanticRelationship, BusinessTerm, BusinessDefinition, MappingRule, CertifiedDefinition. (`Synonym` removed in v2.0.0 — see §1a.)

**4. Lineage & Data Architecture Module** — physical/technical provenance across the medallion layers: OperationalSystem, SourceApplication, SourceTable, SourceField, Dataset (RawLayerDataset, SilverLayerDataset, GoldLayerDataset), DataProduct, DataPipeline, TransformationStep, DataQualityRule, ProvenanceEvent.

**5. Consumption Module** — where KPIs surface to humans and systems: Report, Dashboard, Scorecard, AnalyticalModel, ConsumerUseCase.

**6. Governance Module** — trust and control: Policy, Standard, Control, AccessRule, CertificationStatus, Version, ApprovalEvent, AuditEvent, StewardshipAssignment, and the owner/steward roles that connect back to Business Architecture.

The current Turtle file (Stage 2) implements all six modules **monolithically in one file and one `ekpi:` namespace** rather than as six separate `owl:imports`-linked files. Module sub-namespaces (`ba:`, `kpim:`, `sem:`, `lin:`, `cons:`, `gov:`) remain a documented option for a future physical split (see §7–§8) but are not in use today; treat §8's file list as a roadmap, not the current state.

### 1a. What changed in v2.0.0 and why (read this before §2)

The v1.0.0 design and Turtle grouped classes under four "bucket" superclasses — `BusinessArchitectureElement`, `SemanticAsset`, `LineageNode`, `GovernanceElement` — each with a long, heterogeneous `rdfs:subClassOf` fan-out. A reviewer applying Casey Hart's "would you put a bedroom and a shoe in the same class because they're both 'things in a house'?" test caught the problem: a `BusinessCapability` and an `OrganizationalUnit` are not the same *kind of thing* just because both happen to belong to business architecture, and asserting `rdfs:subClassOf BusinessArchitectureElement` for both makes a false logical claim (that every business-architecture-module member shares whatever essential nature `BusinessArchitectureElement` has) purely to get a grouping label.

**Fix:** module membership is now recorded as metadata, not taxonomy — every class carries `dcterms:isPartOf` pointing at a `skos:Collection` individual for its module (`ekpi:BusinessArchitectureModule`, `ekpi:KPIModelModule`, `ekpi:SemanticModelModule`, `ekpi:LineageModule`, `ekpi:ConsumptionModule`, `ekpi:GovernanceModule`). This still lets you query "everything in the Lineage module," but it no longer pretends those things share a kind.

Three superclasses were **kept** because they pass the "genuinely one kind of thing" test:
- `ekpi:ConsumptionAsset` — every member really is "a surface a human consumes KPI values through."
- `ekpi:PerformanceIndicator` (parent of `Metric`/`Measure`) — every member really is "a quantification of performance."
- `ekpi:Dataset` (parent of Raw/Silver/Gold) — every member really is "a dataset at some medallion layer," and this abstraction is what lets `hasQualityRule`/`transformedBy` be declared once instead of three times, and lets `owl:disjointWith` do useful work between the three layers.

`ekpi:Synonym` was removed as a class entirely: in v1.0.0 it was declared but never instantiated (an orphan class), and everything it was meant to do is already covered by `skos:altLabel` directly on `BusinessTerm` individuals (see the worked example in §10). Modeling the same concept twice — once as a class, once as a SKOS annotation — would be redundant, so the decision was to document the choice rather than keep the unused class.

---

## 2. Core classes grouped by module

Every class below is tagged `dcterms:isPartOf` its module collection in the Turtle (omitted from these tables for readability — see §1a).

### 2.1 Business Architecture

| Class | Description |
|---|---|
| `BusinessCapability` | An enterprise ability to do something of value (e.g., "Rack Price Management & Publication"). |
| `ValueStream` | An end-to-end sequence of activities that delivers value to a stakeholder. |
| `BusinessDomain` | A logical grouping of related business activity (e.g., "Downstream Commercial"). |
| `BusinessFunction` | A recurring organizational activity grouping (e.g., "Pricing & Margin Management"). |
| `BusinessProcess` | A structured set of activities producing a specific outcome. |
| `ProcessStep` | An atomic activity within a `BusinessProcess`. |
| `BusinessGoal` | A directional business intent (e.g., "Protect and Grow Commercial Margin"). |
| `StrategicObjective` | A specific, time-bound target that operationalizes a `BusinessGoal`, via `narrowsGoal`. |
| `OrganizationalUnit` | A team, department, plant, or site. Now carries `unitName`/`unitType` data properties and is actually instantiated (was declared but never instantiated in v1.0.0). |
| `Role` | A functional responsibility a person can hold. **Anchored as `rdfs:subClassOf foaf:Agent`** in v2.0.0 — connects the ontology to a recognized upper-level "agent" concept instead of leaving `Role` floating with no upper anchor. |
| `BusinessOwner` | Subclass of `Role`; accountable for the business meaning/use of a KPI or data asset. |
| `DataSteward` | Subclass of `Role`; accountable for data quality and definitional integrity. |

### 2.2 KPI Model — specification layer

| Class | Description |
|---|---|
| `KPI` | A governed, named indicator of performance against a goal. |
| `KPIDefinition` | The versioned, documented specification of a KPI (scope, business meaning, formula reference). |
| `Measure` | A raw or lightly aggregated quantity computed from data (building block of a KPI). |
| `Metric` | A quantifiable value derived from one or more Measures; broader than KPI (not all Metrics are KPIs). |
| `KPIFormula` | The mathematical expression defining how a KPI is calculated. |
| `CalculationLogic` | Implementation-level logic (SQL/DAX/pseudo-code) realizing a `KPIFormula`, now carrying a real `logicExpression` data property (was prose-only in v1.0.0). |
| `AggregationRule` | Rule describing how a measure rolls up across time/dimensions — now via the closed `AggregationType` vocabulary (SUM/AVG/LAST/RATIO), not free text. |
| `UnitOfMeasure` | The unit a KPI/Measure/Observation is expressed in (%, USD, hours, barrels). |
| `Target` | A desired value for a KPI, now with a working `targetPeriod` **object property** to `TimePeriod` (declared but unimplemented in v1.0.0). |
| `Threshold` | A boundary value that triggers a status — via the closed `ThresholdSeverity` vocabulary (Red/Yellow/Green). |
| `Dimension` | An axis for slicing a KPI (e.g., Terminal, Product) — the *axis*, not a specific value on it (contrast `DimensionValue`, new below). |
| `TimePeriod` | A defined interval a KPI value or Target applies to — now with real `periodStart`/`periodEnd`/`periodGranularity` data properties and real individuals (v1.0.0 declared the class and properties but created zero individuals). |
| `Grain` | The lowest level of detail at which a KPI/Measure is recorded (e.g., per-terminal-per-product-per-day). |

### 2.2a KPI Model — observation / fact layer *(new in v2.0.0)*

| Class | Description |
|---|---|
| `KPIObservation` | One dated, dimensioned, valued reading of a KPI — e.g., "Rack Price Capture Rate for Houston Terminal 3, ULSD, on 2026-07-31 = 98.4%." Closes the single biggest functional gap identified in the review: v1.0.0 could describe how a KPI is *defined* but had no class for what it *actually measured* over time. |
| `DimensionValue` | A specific value along a `Dimension` axis (e.g., "Houston Rack Terminal 3" as a value of the Terminal `Dimension`). |
| `ObservationStatus` | Closed vocabulary (`owl:oneOf`): OnTarget, Watch, Breach — the state of an observation relative to its Target/Threshold. |

### 2.3 Semantic Model

| Class | Description |
|---|---|
| `SemanticModel` | A governed logical model binding business meaning to physical/gold-layer data. |
| `SemanticLayer` | The overall platform/service hosting one or more `SemanticModel`s (e.g., a BI semantic layer). |
| `SemanticEntity` | A business-meaningful object in the semantic model (e.g., "Rack Loading Transaction", "Terminal"). |
| `SemanticAttribute` | A descriptive field on a `SemanticEntity`. |
| `SemanticMeasure` | The semantic-layer representation of a Measure/KPI, bound to gold data and an aggregation rule. |
| `SemanticRelationship` | A named relationship between `SemanticEntity` instances (e.g., "Rack Loading occurs at Terminal"). **Now instantiated** in v2.0.0 — it was declared but had zero individuals in v1.0.0, making it an untested/orphan class. |
| `BusinessTerm` | A controlled-vocabulary business word or phrase (glossary entry), modeled as a `skos:Concept`. Alternate labels use `skos:altLabel` directly — this is also where the removed `Synonym` class's job now lives (see §1a). |
| `BusinessDefinition` | The authoritative textual definition of a `BusinessTerm`. |
| `MappingRule` | An explicit rule mapping a `BusinessTerm`/`SemanticAttribute` to a physical column/field. |
| `CertifiedDefinition` | Equivalent class: `KPIDefinition` (or `BusinessDefinition`) ⊓ `hasCertificationStatus value Certified` — inferable, not manually re-typed. |

### 2.4 Lineage & Data Architecture

| Class | Description |
|---|---|
| `OperationalSystem` | A source-of-record system (e.g., OPIS Market Data Service, RightAngle CTRM/ETRM). |
| `SourceApplication` | A specific application instance within an `OperationalSystem`. |
| `SourceTable` | A physical/logical table in a source application. |
| `SourceField` | A column in a `SourceTable`; the ultimate physical origin of a data value. |
| `Dataset` | Genuine abstract superclass of the three medallion layers (kept in v2.0.0 — not a bucket; see §1a). |
| `RawLayerDataset` | Bronze/raw ingested copy of source data, minimally transformed. |
| `SilverLayerDataset` | Cleansed, conformed, business-rule-applied dataset. |
| `GoldLayerDataset` | Curated, aggregate-ready dataset intended for consumption. |
| `DataProduct` | A packaged, owned, discoverable data asset that wraps a Gold dataset — now instantiated (`wrapsDataset` property, new in v2.0.0). |
| `DataPipeline` | An orchestrated set of `TransformationStep`s moving/transforming data between layers. |
| `TransformationStep` | An atomic transformation (join, filter, aggregate) within a pipeline; `rdfs:subClassOf prov:Activity`. |
| `DataQualityRule` | A rule (e.g., not-null, range check) applied to a dataset or field. |
| `ProvenanceEvent` | A specific run/execution that produced/transformed data; `rdfs:subClassOf prov:Activity`. |

*(v1.0.0's `LineageNode` abstract superclass and standalone `LineageEdge` class are removed — see §1a for `LineageNode`; `LineageEdge` was never instantiated and its job is fully covered by reused `prov:wasDerivedFrom`/`prov:wasGeneratedBy` edges, so keeping a parallel unused class added no value.)*

### 2.5 Consumption

| Class | Description |
|---|---|
| `ConsumptionAsset` | Genuine superclass — kept in v2.0.0, not a bucket (see §1a). |
| `Report` | A static or on-demand document presenting KPI/measure values. |
| `Dashboard` | An interactive, typically live, visualization surface. |
| `Scorecard` | A structured, goal-vs-actual performance view, usually tied to `StrategicObjective`. |
| `AnalyticalModel` | A downstream model (forecast, ML model) consuming certified measures/KPIs — now instantiated in the worked example (§10). |
| `ConsumerUseCase` | A named business use case describing why/how a KPI is consumed. |

### 2.6 Governance

| Class | Description |
|---|---|
| `Policy` | A high-level governance rule (e.g., "All KPIs must have a certified owner"). |
| `Standard` | A concrete specification implementing a Policy (e.g., naming standard). |
| `Control` | An enforceable check implementing a Standard (technical or procedural). |
| `AccessRule` | A rule restricting who can view/edit a governed asset — now instantiated (was declared but untested in v1.0.0). |
| `CertificationStatus` | A closed vocabulary (Draft, InReview, Certified, Deprecated). |
| `Version` | A versioned snapshot of a governed asset (KPIDefinition, SemanticModel, etc.). |
| `ApprovalEvent` | A recorded approval/sign-off action; `rdfs:subClassOf prov:Activity`. |
| `AuditEvent` | A recorded change/access event for traceability; `rdfs:subClassOf prov:Activity`. |
| `StewardshipAssignment` | A time-bound assignment linking a `DataSteward` to a governed asset — now carries real properties (`assignmentSteward`, `assignmentStartDate`, `assignmentEndDate`); was an inert, property-less individual in v1.0.0. |

---

## 3. Object properties between classes

| Property | Domain → Range | Meaning |
|---|---|---|
| `hasSpecificationElement` *(super-property, new)* | KPI → any spec element | Groups `hasFormula`, `hasAggregationRule`, `hasUnitOfMeasure`, `hasTarget`, `hasThreshold`, `hasTimePeriod`, `hasGrain`, `targetPeriod` so "everything specifying this KPI" is one query. |
| `hasGovernanceRecord` *(super-property, new)* | any governed asset → governance fact | Groups `hasCertificationStatus`, `hasVersion`, `auditedBy`, `restrictedBy`, `hasStewardshipAssignment`. |
| `hasSemanticComponent` *(super-property, new)* | SemanticModel/Entity → component | Groups `hasSemanticEntity`, `hasSemanticMeasure`, `hasSemanticAttribute`, `hasSemanticRelationship`. |
| `alignsToGoal` | KPI → BusinessGoal | KPI supports a business goal. |
| `alignsToObjective` | KPI → StrategicObjective | KPI supports a strategic objective. |
| `supportsCapability` | KPI → BusinessCapability | KPI measures performance of a capability. |
| `supportsValueStream` | KPI → ValueStream | KPI measures a value stream. |
| `belongsToDomain` | KPI → BusinessDomain | KPI is categorized under a domain. |
| `measuresProcess` | KPI → BusinessProcess | KPI measures a business process. |
| `hasProcessStep` | BusinessProcess → ProcessStep | Process composition. |
| `narrowsGoal` *(new)* | StrategicObjective → BusinessGoal | An objective operationalizes a broader goal (was described in prose in v1.0.0, now a real property with an asserted individual). |
| `belongsToUnit` *(new)* | Role → OrganizationalUnit | Connects a Role (and the BusinessOwner/DataSteward holding it) to its OrganizationalUnit — closes the gap where OrganizationalUnit existed in the class model but nothing pointed to it. |
| `hasDefinition` / `isDefinitionOf` (inverse) | KPI ↔ KPIDefinition | KPI is defined by / defines. |
| `hasFormula` | KPIDefinition → KPIFormula | Definition specifies a formula. |
| `implementedBy` | KPIFormula → CalculationLogic | Formula is implemented by concrete logic. |
| `hasAggregationRule` | KPI/Measure → AggregationRule | Roll-up behavior. |
| `hasUnitOfMeasure` | KPI/Measure/**KPIObservation** → UnitOfMeasure | Unit binding — domain extended to KPIObservation in v2.0.0. |
| `hasTarget` | KPI → Target | Desired performance value. |
| `hasThreshold` | KPI → Threshold | Alert boundary. |
| `targetPeriod` *(now implemented as ObjectProperty)* | Target → TimePeriod | The period a Target value applies to. |
| `slicedByDimension` | KPI → Dimension | Available slicing axis. |
| `hasTimePeriod` | KPI → TimePeriod | Reporting interval. |
| `hasGrain` | KPI/Measure → Grain | Lowest recorded detail level. |
| `derivedFromMeasure` | KPI → Measure | KPI is computed from Measures. |
| `derivedFromDataset` | Measure → GoldLayerDataset | Measure sourced from gold data. |
| `measuresKPI` *(new)* | KPIObservation → KPI | Which KPI this observation is a reading of. |
| `observedForPeriod` *(new)* | KPIObservation → TimePeriod | Which period this observation applies to. |
| `observedForDimensionValue` *(new)* | KPIObservation → DimensionValue | Which specific dimension values (e.g. which terminal, which product) this observation applies to; multi-valued. |
| `valueOfDimension` *(new)* | DimensionValue → Dimension | Which Dimension axis a DimensionValue belongs to. |
| `hasObservationStatus` *(new, functional)* | KPIObservation → ObservationStatus | The single current status of an observation relative to its Target/Threshold. |
| `computedAgainstTarget` *(new)* | KPIObservation → Target | Which Target this observation was evaluated against. |
| `computedAgainstThreshold` *(new)* | KPIObservation → Threshold | Which Threshold this observation was evaluated against. |
| `originatesIn` | SourceField → OperationalSystem | Ultimate physical origin. |
| `transformedBy` | Dataset → TransformationStep | Which step produced it. |
| `partOfPipeline` | TransformationStep → DataPipeline | Composition. |
| `wrapsDataset` *(new)* | DataProduct → Dataset | A packaged DataProduct wraps a specific Gold dataset for downstream consumption. |
| `feedsSemanticModel` / `isFedBy` (inverse) | GoldLayerDataset ↔ SemanticModel | Gold data feeds the semantic layer. |
| `hasSemanticEntity` | SemanticModel → SemanticEntity | Composition. |
| `hasSemanticMeasure` | SemanticModel → SemanticMeasure | Composition. |
| `hasSemanticAttribute` | SemanticEntity → SemanticAttribute | Composition. |
| `hasSemanticRelationship` *(new)* | SemanticModel/SemanticEntity → SemanticRelationship | Instantiates the previously-orphan relationship class. |
| `hasSourceEntity` / `hasTargetEntity` *(new)* | SemanticRelationship → SemanticEntity | The two entities a SemanticRelationship connects. |
| `mapsToBusinessTerm` | SemanticMeasure/SemanticAttribute → BusinessTerm | Binds physical semantics to governed vocabulary. |
| `mappedByRule` | SemanticAttribute → MappingRule | Explicit mapping rule. |
| `realizesKPI` | SemanticMeasure → KPI | The semantic measure is the governed implementation of a KPI. |
| `consumedBy` | SemanticMeasure/KPIDefinition → Report/Dashboard/Scorecard/AnalyticalModel | Consumption edge. |
| `usedInUseCase` | Report/Dashboard/Scorecard/AnalyticalModel → ConsumerUseCase | Why it's consumed. |
| `hasQualityRule` | Dataset/SourceField → DataQualityRule | Quality governance. |
| `ownedBy` | KPI/DataProduct/SemanticModel → BusinessOwner | Business accountability. |
| `stewardedBy` | KPI/Dataset/SemanticModel → DataSteward | Denormalized "current steward" shortcut — deliberately kept alongside `hasStewardshipAssignment` (see §6). |
| `hasStewardshipAssignment` | governed asset → StewardshipAssignment | The authoritative, time-bound stewardship record. |
| `assignmentSteward` *(new)* | StewardshipAssignment → DataSteward | Who is assigned. |
| `governedByPolicy` | KPI/SemanticModel → Policy | Applicable policy. |
| `implementsStandard` | Policy → Standard | Composition. |
| `enforcedByControl` | Standard → Control | Enforcement mechanism. |
| `hasCertificationStatus` *(functional)* | KPIDefinition/SemanticModel → CertificationStatus | Trust state. |
| `hasVersion` | KPIDefinition/SemanticModel → Version | Versioning. |
| `approvedBy` | Version → ApprovalEvent | Sign-off trace. |
| `auditedBy` | governed asset → AuditEvent | Change/access trace. |
| `restrictedBy` | governed asset → AccessRule | Access control. |
| `prov:wasDerivedFrom` (reused) | any dataset/field → predecessor | Generic provenance edge used across the whole lineage chain. |
| `prov:wasGeneratedBy` (reused) | Dataset → ProvenanceEvent | Ties a dataset to the pipeline run that produced it. |

## 4. Data properties per class (representative)

| Class | Key data properties |
|---|---|
| `KPI` | `kpiCode` (xsd:string); `rdfs:label` for name; `criticality` is now an **object property** to the closed `Criticality` vocabulary (High/Medium/Low), not a datatype property as loosely implied in v1.0.0. |
| `KPIDefinition` | `definitionText`, `effectiveDate` (xsd:date) |
| `KPIFormula` | `formulaExpression` (xsd:string) |
| `CalculationLogic` | `logicExpression` (xsd:string) — **new in v2.0.0**; the concrete SQL/DAX text is now queryable/comparable, not only prose in `rdfs:comment`. |
| `UnitOfMeasure` | `unitSymbol` |
| `Target` | `targetValue` (xsd:decimal); `targetPeriod` is an **object property**, not a data property (corrected ambiguity from v1.0.0). |
| `Threshold` | `thresholdValue` (xsd:decimal); `thresholdSeverity` is an object property to the closed vocabulary. |
| `Grain` | `grainLabel` |
| `TimePeriod` | `periodStart` (xsd:date), `periodEnd` (xsd:date), `periodGranularity` (xsd:string) — **all new in v2.0.0**; declared in v1.0.0 but never implemented. |
| `DimensionValue` *(new class)* | `dimensionValueLabel` (xsd:string) |
| `KPIObservation` *(new class)* | `hasObservedValue` (xsd:decimal) |
| `SourceField` | `fieldName` (xsd:string) |
| `Dataset` (Raw/Silver/Gold) | `datasetName`, `refreshFrequency` |
| `DataQualityRule` | `ruleExpression` |
| `BusinessTerm` | `skos:prefLabel`, `skos:altLabel` (replaces the removed `Synonym` class — see §1a), `skos:definition` |
| `SemanticRelationship` *(new class)* | `relationshipType` (xsd:string) |
| `Version` | `versionNumber` (xsd:string), `versionDate` (xsd:date) |
| `ApprovalEvent` / `AuditEvent` | `eventTimestamp` (xsd:dateTime) |
| `OrganizationalUnit` | `unitName`, `unitType` — declared in v1.0.0 but never implemented; now real and instantiated. |
| `StewardshipAssignment` | `assignmentStartDate` (xsd:date), `assignmentEndDate` (xsd:date, left open on active assignments) — **new in v2.0.0**. |

## 5. Class hierarchy (corrected)

```
owl:Thing
├─ [Business Architecture Module — module-tagged, no shared superclass]
│   ├─ BusinessCapability
│   ├─ ValueStream
│   ├─ BusinessDomain
│   ├─ BusinessFunction
│   ├─ BusinessProcess
│   │   └─ ProcessStep
│   ├─ BusinessGoal
│   │   └─ StrategicObjective   (subClassOf BusinessGoal — narrower/time-bound; narrowsGoal → BusinessGoal)
│   └─ OrganizationalUnit
├─ Role  (subClassOf foaf:Agent)
│   ├─ BusinessOwner
│   └─ DataSteward
├─ PerformanceIndicator   (genuine superclass — kept)
│   ├─ Metric
│   │   └─ KPI                  (subClassOf Metric — governed subset; requires hasDefinition + ownedBy via restrictions)
│   └─ Measure
├─ [KPI specification elements — module-tagged, no shared superclass]
│   ├─ KPIDefinition
│   │   └─ CertifiedDefinition  (equivalentClass KPIDefinition ⊓ hasCertificationStatus value Certified)
│   ├─ KPIFormula
│   ├─ CalculationLogic
│   ├─ AggregationRule
│   ├─ UnitOfMeasure
│   ├─ Target
│   ├─ Threshold
│   ├─ Dimension
│   ├─ TimePeriod
│   └─ Grain
├─ [KPI observation / fact layer — new in v2.0.0]
│   ├─ KPIObservation
│   ├─ DimensionValue
│   └─ ObservationStatus  (owl:oneOf: OnTarget, Watch, Breach)
├─ [Semantic Model Module — module-tagged, no shared superclass]
│   ├─ SemanticLayer
│   ├─ SemanticModel
│   ├─ SemanticEntity
│   ├─ SemanticAttribute
│   ├─ SemanticMeasure
│   ├─ SemanticRelationship      (now instantiated)
│   ├─ BusinessTerm  (subClassOf skos:Concept)
│   ├─ BusinessDefinition
│   │   └─ CertifiedDefinition   (also here, via equivalentClass — see §2.3)
│   └─ MappingRule
│   [Synonym — REMOVED; see §1a]
├─ [Lineage & Data Architecture Module — module-tagged, no shared superclass]
│   ├─ OperationalSystem
│   ├─ SourceApplication
│   ├─ SourceTable
│   ├─ SourceField
│   ├─ Dataset  (genuine abstract superclass — kept)
│   │   ├─ RawLayerDataset      (disjoint with Silver, Gold)
│   │   ├─ SilverLayerDataset   (disjoint with Raw, Gold)
│   │   └─ GoldLayerDataset     (disjoint with Raw, Silver)
│   ├─ DataProduct               (now instantiated; wrapsDataset)
│   ├─ DataPipeline
│   │   └─ TransformationStep   (subClassOf prov:Activity)
│   ├─ DataQualityRule
│   └─ ProvenanceEvent          (subClassOf prov:Activity)
│   [LineageNode, LineageEdge — REMOVED; see §1a and §2.4]
├─ ConsumptionAsset   (genuine superclass — kept)
│   ├─ Report
│   ├─ Dashboard
│   ├─ Scorecard
│   └─ AnalyticalModel
├─ ConsumerUseCase
└─ [Governance Module — module-tagged, no shared superclass]
    ├─ Policy
    ├─ Standard
    ├─ Control
    ├─ AccessRule                (now instantiated)
    ├─ CertificationStatus  (owl:oneOf: Draft, InReview, Certified, Deprecated)
    ├─ Version
    ├─ ApprovalEvent             (subClassOf prov:Activity)
    ├─ AuditEvent                (subClassOf prov:Activity)
    └─ StewardshipAssignment     (now carries real properties)
```

Notes (updated):
- `KPI ⊑ Metric` — every KPI is a Metric, but not every Metric is governed/strategic enough to be a KPI. An `owl:Restriction` now requires every `KPI` to have `hasDefinition someValuesFrom KPIDefinition` **and** `ownedBy someValuesFrom BusinessOwner` — this is the actual logical distinction between a governed KPI and a plain Metric, not just a naming convention.
- `StrategicObjective ⊑ BusinessGoal` — an objective is a specific, measurable instance of a goal, connected via the new `narrowsGoal` property.
- `Dataset` remains an abstract superclass of the three medallion layers — a deliberate, genuine abstraction (not a bucket), because `hasQualityRule`/`transformedBy` need declaring only once, and `owl:disjointWith` between the three layers only makes sense if they share a common parent to be siblings under.
- `CertifiedDefinition` intentionally sits at the intersection of `KPIDefinition` and `BusinessDefinition`, expressed as `owl:equivalentClass` so a reasoner infers membership from certification status rather than a human manually re-typing the individual.
- Every remaining class not shown with an explicit `rdfs:subClassOf` chain above is tagged with `dcterms:isPartOf` its module `skos:Collection` — this is metadata for discovery/query convenience, deliberately not a taxonomy claim.

## 6. Constraints and modeling guidance (where OWL adds value)

| Guidance | Rationale |
|---|---|
| Use `owl:Restriction` with `owl:someValuesFrom` to require every `KPI` to have **at least one** `hasDefinition` value of type `KPIDefinition`. | Prevents "orphan" KPIs with no documented definition. |
| Use `owl:Restriction` to require every `KPI` to have `ownedBy someValuesFrom BusinessOwner`. **(new in v2.0.0)** | This is the operational, reasoner-checkable difference between a `KPI` and a plain `Metric` — a Metric is not required to have an accountable owner. |
| Use `owl:Restriction` to require `RawLayerDataset` to have `prov:wasDerivedFrom someValuesFrom SourceField`, `SilverLayerDataset` to have `prov:wasDerivedFrom someValuesFrom RawLayerDataset`, and `GoldLayerDataset` to have `feedsSemanticModel someValuesFrom SemanticModel`. **(new in v2.0.0)** | Turns "raw traces to a source, silver traces to raw, gold feeds the semantic layer" from documentation prose into logical facts a reasoner can check — directly answering the review's critique that medallion-layer distinctions were asserted only in comments. |
| Use `owl:FunctionalProperty` for `hasCertificationStatus` and for `hasObservationStatus`. | A definition or observation should have exactly one current status at a time. |
| Use `owl:equivalentClass`, e.g. `CertifiedDefinition ≡ KPIDefinition ⊓ (hasCertificationStatus value Certified)`. | Lets a reasoner *infer* certification membership rather than requiring manual re-typing every time status changes. |
| Use `owl:inverseOf` pairs, e.g. `hasDefinition`/`isDefinitionOf`, `feedsSemanticModel`/`isFedBy`. | Enables bidirectional graph traversal/querying without duplicating assertions. |
| Introduce a small **property hierarchy** via `rdfs:subPropertyOf`: `hasSpecificationElement` over the KPI-spec properties, `hasGovernanceRecord` over the governance properties, `hasSemanticComponent` over the semantic-model composition properties. **(new in v2.0.0)** | Lets a query ask "give me everything that specifies this KPI" without listing seven narrow predicate names — the property-level analogue of a class hierarchy. |
| Prefer `owl:ObjectProperty`s reusing `prov:wasDerivedFrom`/`prov:wasGeneratedBy` over inventing unrelated lineage predicates. | Keeps the ontology interoperable with existing PROV-aware tooling (lineage visualizers, catalogs). |
| Keep cardinality restrictions light: do **not** hard-cap `implementedBy` at 1 per `KPIFormula`. | KPIs legitimately have multiple calculation implementations (SQL vs DAX) that coexist; over-constraining would fight the real world. |
| Model `CertificationStatus`, `Criticality`, `ThresholdSeverity`, and `AggregationType` as controlled **enumerations of named individuals** (`owl:oneOf`) rather than free text. **(three of these four are new in v2.0.0 — see the review's finding that they were previously loose `xsd:string` fields)** | Guarantees only valid states are used — supports governance dashboards, validation, and cross-team consistency. |
| Use SKOS (`skos:Concept`, `skos:altLabel`, `skos:prefLabel`) for `BusinessTerm`, not a parallel `Synonym` OWL class. | SKOS is purpose-built for controlled vocabularies and term relationships; a second class doing the same job is redundant (see §1a). |
| Keep the lineage chain as **instance-level graph traversal** (`wasDerivedFrom` chains) rather than encoding each hop as a distinct OWL property. | Keeps the class model stable even as new layers/pipelines are added; only new *individuals*, not new *schema*, are needed as the data estate grows. |
| Reserve `owl:disjointWith` for genuinely mutually-exclusive class pairs: `RawLayerDataset`, `SilverLayerDataset`, and `GoldLayerDataset` are pairwise disjoint. | Catches data-entry errors (a dataset mistakenly typed as both raw and gold) via reasoning. |
| Document — rather than model as a class — the relationship between `stewardedBy` (a denormalized "current steward" shortcut) and `StewardshipAssignment` (the authoritative, time-bound record). **(new in v2.0.0)** | Both edges are useful and neither is redundant: `stewardedBy` answers "who do I ask right now" in one hop; `hasStewardshipAssignment` answers "who was steward, and for how long" for audit purposes. Collapsing them into one property would lose the time-bound history. |

## 7. Recommended namespace / IRI strategy

- **Custom enterprise namespace (core ontology):** `https://ontology.enterprise.example.com/kpi-store/core#` — prefix `ekpi:`. **This is currently the only schema namespace in use** — the Turtle file is monolithic.
- **Module sub-namespaces (reserved for a future physical split, not yet in use):**
  - `https://ontology.enterprise.example.com/kpi-store/business-architecture#` → `ba:`
  - `https://ontology.enterprise.example.com/kpi-store/kpi-model#` → `kpim:`
  - `https://ontology.enterprise.example.com/kpi-store/semantic-model#` → `sem:`
  - `https://ontology.enterprise.example.com/kpi-store/lineage#` → `lin:`
  - `https://ontology.enterprise.example.com/kpi-store/consumption#` → `cons:`
  - `https://ontology.enterprise.example.com/kpi-store/governance#` → `gov:`
- **Instance/individual namespace** (kept separate from schema so data can be swapped/reloaded without touching the ontology): `https://data.enterprise.example.com/kpi-store/` → `data:`
- **Reused standard vocabularies:** `rdf:`, `rdfs:`, `owl:`, `xsd:`, `dcterms:`, `dc:`, `foaf:`, `skos:`, `prov:`, `schema:`
- **Versioning convention:** `owl:versionInfo "2.0.0"` and `owl:versionIRI` point at a dated snapshot (`.../core/2026-08-02#`), with `owl:priorVersion` linking back to `2026-08-01#` (the v1.0.0 snapshot). This mirrors W3C ontology-versioning best practice and keeps the "current" IRI resolvable while historical versions remain addressable for audit.
- **Slash vs hash:** `#` (hash IRIs) for ontology terms (classes/properties) for fast, single-request dereferencing; `/` (slash IRIs) for individuals, since instance data is large and benefits from server-side content negotiation/pagination.

## 8. Recommended modular structure (future-state roadmap)

The Stage 2 Turtle file today is a **single monolithic file** (`stage2_enterprise_kpi_ontology.ttl`) under one `ekpi:` namespace. The following split remains the recommended target once the ontology needs independent module versioning or a real triple store deployment — it is not yet implemented:

1. `core.ttl` — top-level metadata, `owl:imports` for all modules, shared genuine abstractions (`PerformanceIndicator`, `Dataset`, `ConsumptionAsset`), and the module `skos:Collection` individuals.
2. `business-architecture.ttl`
3. `kpi-model.ttl` (including the new observation/fact-layer classes)
4. `semantic-model.ttl`
5. `lineage.ttl`
6. `consumption.ttl`
7. `governance.ttl`

Each module would `owl:imports` `core.ttl` only (not each other) to avoid circular imports; cross-module *properties* (e.g., `realizesKPI` linking `sem:SemanticMeasure` to `kpim:KPI`) would be declared in `core.ttl` since they bridge two modules.

## 9. How the ontology supports an enterprise KPI store

- **Single trusted catalog:** Every KPI is a `kpim:KPI` individual with exactly one `hasDefinition` (a `CertifiedDefinition` once approved) and, by restriction, a required `BusinessOwner` — giving the KPI store one authoritative, accountable row per indicator instead of divergent per-dashboard formulas.
- **Traceable trust:** Because `hasCertificationStatus`, `ownedBy`, `stewardedBy`, `approvedBy`, and `auditedBy` are first-class graph edges (not spreadsheet columns), a KPI store UI can render trust badges and drill into who approved what and when, directly from SPARQL queries over the graph.
- **Actual performance, not just definitions:** The new `KPIObservation` fact layer means the KPI store can answer "what was Rack Price Capture Rate at Beaumont Terminal 1 for RBOB on 2026-07-31, and was it in breach?" — not only "how is Rack Price Capture Rate defined." This was the single biggest capability gap the v1.0.0 model had (definitions and lineage only, no facts).
- **Impact analysis:** Because lineage is modeled as an explicit, traversable chain (`SourceField → Raw → Silver → Gold → SemanticModel → SemanticMeasure → KPI → Dashboard`), the KPI store can answer "if this source field changes, which dashboards break?" via graph queries instead of tribal knowledge — and the new medallion restrictions (§6) let a reasoner flag a Gold dataset that was never actually connected to a SemanticModel.
- **Reuse over duplication:** The semantic model layer means a Measure is defined once (`SemanticMeasure`) and consumed by many KPIs/reports (`consumedBy`), avoiding the "50 slightly different revenue definitions" problem — demonstrated in §10, where the same `PercentUnit` individual and the same `KPICertificationPolicy` governance chain are reused rather than re-created.
- **Extensibility:** New business domains, KPIs, or data sources are added as new *individuals* against a stable *schema*, so the KPI store's ontology doesn't need to be redesigned as the enterprise grows — only extended.
- **Cross-tool interoperability:** Reuse of `prov:`, `skos:`, `dcterms:`, and `foaf:` means the KPI store's graph can interoperate with existing data-catalog, lineage-visualization, and glossary tools that already speak these vocabularies, instead of requiring bespoke integration.

## 10. Worked example: "Rack Price Capture Rate %" (Downstream Oil & Gas Commercial)

**Business context.** Within the **Downstream Commercial** business domain, the **Pricing & Margin Management** business function owns the **Rack Price Management & Publication** capability. Its core business process, **Rack Price Setting**, runs four steps: ingest the OPIS rack benchmark → apply zone/freight differential → publish the rack price sheet → reconcile realized vs. published price. This process sits inside the broader **Downstream Commercial Value Stream**, which runs Market & Strategy Formation → Execution & Operations → Risk, Performance & Control (looping back to Stage 1).

**KPI:** *Rack Price Capture Rate %* = (Realized Rack Revenue per Gallon ÷ Published OPIS Rack Benchmark per Gallon) × 100, computed per terminal, per product, per day. It is aligned to the strategic objective "Improve Rack Price Capture Rate to 99% by Q4 FY26," which narrows the business goal "Protect and Grow Commercial Margin."

**Graph walk (conceptual — matches the Stage 2 Turtle individuals exactly):**

1. `RackPriceCaptureRateKPI` (a `KPI`) — `alignsToObjective` → `ImproveRackCapture99pctQ4FY26` (a `StrategicObjective`, `narrowsGoal` → `ProtectGrowCommercialMarginGoal`).
2. `RackPriceCaptureRateKPI` — `supportsCapability` → `RackPriceManagementCapability`, `MarginPerformanceManagementCapability`; `supportsValueStream` → `DownstreamCommercialValueStream`; `belongsToDomain` → `DownstreamCommercialDomain`; `measuresProcess` → `RackPriceSettingProcess` (which `hasProcessStep` → the four steps above).
3. `RackPriceCaptureRateKPI` — `hasDefinition` → `RackPriceCaptureRateDefinition_v1` (a `CertifiedDefinition`), which `hasFormula` → `RackPriceCaptureRateFormula` ("Rack Price Capture Rate % = Realized Rack Revenue per Gallon / Published OPIS Rack Benchmark per Gallon × 100"), `implementedBy` → `RackCaptureCalcLogic_SQL` (carrying the actual SQL in `ekpi:logicExpression`).
4. `RackPriceCaptureRateKPI` — `hasAggregationRule` → `AvgOverTerminalDayRule` (`aggregationType` → `AggType_AVG`); `hasUnitOfMeasure` → `PercentUnit`; `hasTarget` → `Target_99pct_Q4FY26` (`targetValue` 99.0, `targetPeriod` → `FY26_Q4`); `hasThreshold` → `RedThreshold_97pct` (`thresholdSeverity` → `Severity_Red`); `slicedByDimension` → `TerminalDimension`, `ProductDimension`; `hasGrain` → `PerTerminalPerProductPerDayGrain`.
5. `RackPriceCaptureRateKPI` — `derivedFromMeasure` → `RealizedRackRevenueMeasure`, `PublishedRackBenchmarkMeasure` — **two independent lineage chains feeding one KPI**, demonstrating the medallion pattern with a real cross-system join:
   - `RealizedRackRevenueMeasure` → `derivedFromDataset` → `RackLiftings_GoldDataset` → `wasDerivedFrom` → `RackLiftings_SilverDataset` → `wasDerivedFrom` → `RackLiftings_RawDataset` → `wasDerivedFrom` → `NetPricePerGalField` (`SourceField` "NET_PRICE_PER_GAL" on `SourceTable` "TERMINAL_LIFTING_TXN" in `SourceApplication` "RightAngle Terminal Billing", `originatesIn` → `RightAngleCTRM`). The full pipeline (`RackLiftingsPipeline`, two `TransformationStep`s, and a `ProvenanceEvent` for the 2026-07-31 load run) is modeled explicitly.
   - `PublishedRackBenchmarkMeasure` → `derivedFromDataset` → `OPISBenchmark_GoldDataset` → (Silver → Raw →) `RackPriceUSDGalField` (`SourceField` "RACK_PRICE_USD_GAL" on `SourceTable` "OPIS_RACK_PRICE_DAILY" in `SourceApplication` "OPIS Rack Price Feed", `originatesIn` → `OPISMarketDataService`). This chain intentionally omits separate pipeline/transformation-step individuals, as a documented scope choice (not every chain needs identical depth).
   - Both Gold datasets `feedsSemanticModel` → `CommercialPricingSemanticModel`, and `OPISBenchmark_GoldDataset` is also wrapped by `RackPriceSheetDataProduct` (`wrapsDataset`).
6. `CommercialPricingSemanticModel` — `hasSemanticEntity` → `RackLoadingTransactionEntity`, `TerminalEntity`, `ProductEntity`; `hasSemanticRelationship` → `RackLoading_OccursAt_Terminal`, `RackLoading_For_Product`; `hasSemanticMeasure` → `RackPriceCaptureSemanticMeasure`, which `mapsToBusinessTerm` → `RackPriceCaptureBusinessTerm` (`skos:prefLabel` "Rack Price Capture Rate", `skos:altLabel` "Rack Margin Capture", "Price Realization Rate") and `realizesKPI` → `RackPriceCaptureRateKPI`.
7. `RackPriceCaptureSemanticMeasure` — `consumedBy` → `CommercialPricingDashboard` (`Dashboard`), `CommercialMarginScorecard` (`Scorecard`), `DailyRackReconciliationReport` (`Report`), and `RackPriceLeakageForecastModel` (`AnalyticalModel`) — all four `usedInUseCase` → `DailyCommercialPricingReview` (`ConsumerUseCase`).
8. **Observations (the new fact layer):** three `KPIObservation` individuals record actual readings — Houston Terminal 3 / ULSD on 2026-06-30 at 99.6% (`ObsStatus_OnTarget`), the same terminal/product on 2026-07-31 at 98.4% (`ObsStatus_Watch`), and Beaumont Terminal 1 / RBOB on 2026-07-31 at 96.2% (`ObsStatus_Breach`, below the 97% red threshold) — each `measuresKPI` → `RackPriceCaptureRateKPI`, `observedForPeriod` → the relevant day, `observedForDimensionValue` → the relevant terminal and product, and `computedAgainstTarget`/`computedAgainstThreshold` → the shared Target/Threshold individuals.
9. Governance: `RackPriceCaptureRateKPI` — `ownedBy` → `CommercialPricingManager` (`BusinessOwner`, `belongsToUnit` → `CommercialPricingDistributionTeam`); `stewardedBy` → `CommercialDataSteward`, backed by `CommercialPricingStewardshipAssignment` (`assignmentSteward`, `assignmentStartDate` 2026-07-15, open-ended); `governedByPolicy` → `KPICertificationPolicy` (reused from the enterprise-wide governance chain — `implementsStandard` → `KPINamingStandard` → `enforcedByControl` → `KPICodeUniquenessControl`); `RackPriceCaptureRateDefinition_v1` — `hasCertificationStatus` → `Status_Certified`, `hasVersion` → `RackCaptureDef_Version1` (`versionNumber` "1", `approvedBy` → `ApprovalEvent_20260715`), `auditedBy` → `AuditEvent_20260715`.

This is exactly the chain rendered as Turtle individuals in Stage 2, end-to-end from `SourceField` to `Dashboard` to `KPIObservation`.

---

## 11. Competency questions

A competency question is a natural-language question the ontology should be able to answer via a graph query once populated. These were used to validate the v2.0.0 design and double as a starting SPARQL test suite:

1. Which KPIs support the "Rack Price Management & Publication" capability?
2. What is the certified definition and formula for "Rack Price Capture Rate %," and who approved it?
3. Which source systems and fields ultimately feed a given KPI's Gold dataset?
4. If `NET_PRICE_PER_GAL` in RightAngle changes format, which dashboards or scorecards are at risk?
5. Who is the current data steward for a given KPI, and since when have they held that assignment?
6. Which KPIs have no `BusinessOwner` asserted? *(should return zero once the KPI-ownership restriction in §6 is enforced)*
7. Which Gold datasets do not yet feed any SemanticModel? *(should return zero once the medallion restriction in §6 is enforced)*
8. What was the observed Rack Price Capture Rate for Houston Terminal 3 / ULSD on a given day, and was it on target?
9. Which terminal/product combinations breached their threshold in the last reporting period?
10. Which business terms have alternate labels ("synonyms"), and what are they?
11. Which consumption assets (dashboards, reports, scorecards, models) would be affected if a specific SemanticMeasure were deprecated?
12. What is the full chain of custody — from source field to dashboard — for a specific KPI value shown to an executive?
13. Which KPIs are measured against the same underlying Measure (candidates for consolidation)?
14. Which policies, standards, and controls govern a given KPI, and is the enforcing control automated or procedural?
15. Which strategic objectives currently have no KPI tracking progress against them? *(a coverage-gap query, not yet enforced by a restriction — a candidate for future governance tightening)*

---

## Design answers to the two key questions

### Why the semantic model must be a first-class ontology citizen, not side documentation

If the semantic model is left as a spreadsheet or a BI tool's proprietary metadata, it becomes an *opaque translation step* between governed KPI definitions and physical gold data — invisible to lineage tools, invisible to the governance graph, and not queryable alongside the rest of the enterprise's semantic assets. By modeling `SemanticModel`, `SemanticEntity`, `SemanticMeasure`, `SemanticRelationship`, `MappingRule`, and `BusinessTerm` as OWL classes with explicit object properties (`feedsSemanticModel`, `mapsToBusinessTerm`, `realizesKPI`, `hasSemanticRelationship`), the semantic layer becomes:

- **Traceable**: `SemanticMeasure` sits exactly on the path between `GoldLayerDataset` and `KPI`, so lineage tools can traverse *through* it rather than around it.
- **Governable**: because it's made of RDF individuals, `CertificationStatus`, `ownedBy`, and `Version` can attach directly to `SemanticModel`/`SemanticMeasure`, giving the semantic layer the same trust machinery as KPIs.
- **Queryable**: SPARQL can answer "which business terms map to which physical columns" or "which KPIs would break if this semantic measure changes" — questions that are hard to answer when the mapping lives in tool-specific config files.
- **Vendor-neutral**: the same semantic model graph can describe measures whether they're implemented in a BI tool's semantic layer, a metrics-layer framework (e.g., dbt/Cube-style), or a warehouse view — because the ontology captures *meaning and mapping*, not vendor syntax.

### How governance relates to trust, lineage, certification, and change management

Governance is modeled as the layer that **attaches accountability and state to every other module's assets**, rather than as a separate silo:

- **Trust** is represented as a `CertificationStatus` individual attached via `hasCertificationStatus` to a `KPIDefinition` or `SemanticModel` — so "is this trustworthy" is a graph fact, not tribal knowledge.
- **Lineage** feeds governance: `DataQualityRule` results and `ProvenanceEvent`s attach to the same `Dataset`/`SourceField` nodes that lineage traverses, and — new in v2.0.0 — the medallion `owl:Restriction`s in §6 mean a reasoner can actually flag a Gold dataset that skipped the required Silver step, rather than trusting a human to have followed the convention.
- **Certification** is a *state machine* realized through `CertificationStatus` individuals (Draft → InReview → Certified → Deprecated) plus `ApprovalEvent`s that record who moved the state and when — giving certification an audit trail, not just a boolean flag.
- **Change management** is captured through `Version` individuals (one per `KPIDefinition`/`SemanticModel` revision) linked to `ApprovalEvent`s and `AuditEvent`s, so the ontology preserves *history*: a dashboard consuming `RackPriceCaptureRateDefinition_v1` today can be distinguished from a future `v2`, and an auditor can reconstruct exactly when/why the formula changed.
- **Observed performance is now part of the trust picture too**: because `KPIObservation` individuals carry `computedAgainstTarget`/`computedAgainstThreshold` and a functional `hasObservationStatus`, governance isn't only "is the definition certified" — it's also "is the KPI currently performing within its governed bounds," queryable directly from the same graph.

Together, this means governance isn't a checklist bolted onto the KPI store — it's the set of predicates that make every other module's assets **accountable, versioned, and auditable** within the same graph.
