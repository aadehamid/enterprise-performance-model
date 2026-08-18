# KPI Ontology Class Hierarchy (Quick Reference)

*Version 2.0.0 — corrected structure. Worked example: Downstream Oil & Gas Commercial — Rack Price Capture Rate %.*

*This is a navigation aid, not a substitute for the full design rationale in "Stage 1 — KPI Ontology Design Blueprint" or the formal definitions in "Stage 2 — Enterprise KPI Ontology (Turtle)." Regenerate this document any time the class tree changes.*

---

## What changed since v1.0.0 (read this first)

v1.0.0 organized classes under four abstract "bucket" superclasses (`BusinessArchitectureElement`, `SemanticAsset`, `LineageNode`, `GovernanceElement`) purely for documentation grouping — a modeling mistake caught by applying Casey Hart's "would you put a bedroom and a shoe in the same class because they're both things in a house?" test. **v2.0.0 removes all four.** Their former members are now flat under `owl:Thing`, each tagged with `dcterms:isPartOf` pointing at a `skos:Collection` module individual — a metadata grouping, not a taxonomy claim. Three superclasses that *do* pass the genuine-kind test were kept: `PerformanceIndicator`, `Dataset`, and `ConsumptionAsset`. v2.0.0 also adds a new observation/fact layer, closes several free-text fields into controlled vocabularies, adds a small property hierarchy, and backs key subclass distinctions with `owl:Restriction`s. See the "Ontology Best Practices" document for the full reasoning behind each change.

---

## Full class tree

```
owl:Thing
│
├─ ROLE / AGENT
│  └─ Role  (rdfs:subClassOf foaf:Agent)
│      ├─ BusinessOwner
│      └─ DataSteward
│
├─ PERFORMANCE INDICATOR  ── genuine superclass, kept
│  └─ PerformanceIndicator
│      ├─ Metric
│      │   └─ KPI   (⊑ Metric; restricted: requires hasDefinition + ownedBy)
│      └─ Measure
│
├─ KPI OBSERVATION / FACT LAYER  ── NEW in v2.0.0, module-tagged (KPIModelModule)
│  ├─ KPIObservation
│  ├─ DimensionValue
│  └─ ObservationStatus   (owl:oneOf: OnTarget, Watch, Breach)
│
├─ DATASET  ── genuine superclass, kept (enables disjointness)
│  └─ Dataset
│      ├─ RawLayerDataset      ⟂ disjoint with Silver, Gold
│      ├─ SilverLayerDataset   ⟂ disjoint with Raw, Gold
│      └─ GoldLayerDataset     ⟂ disjoint with Raw, Silver
│
├─ CONSUMPTION ASSET  ── genuine superclass, kept
│  └─ ConsumptionAsset
│      ├─ Report
│      ├─ Dashboard
│      ├─ Scorecard
│      └─ AnalyticalModel
│
├─ CONSUMER USE CASE  (standalone, module-tagged)
│  └─ ConsumerUseCase
│
├─ [BusinessArchitectureModule] ── module tag only, no shared superclass
│  ├─ BusinessCapability
│  ├─ ValueStream
│  ├─ BusinessDomain
│  ├─ BusinessFunction
│  ├─ BusinessProcess
│  │   └─ ProcessStep
│  ├─ BusinessGoal
│  │   └─ StrategicObjective   (⊑ BusinessGoal; narrowsGoal → BusinessGoal)
│  └─ OrganizationalUnit
│
├─ [KPIModelModule] ── module tag only, no shared superclass
│  ├─ KPIDefinition
│  │   └─ CertifiedDefinition  (≡ KPIDefinition ⊓ hasCertificationStatus value Certified)
│  ├─ KPIFormula
│  ├─ CalculationLogic
│  ├─ AggregationRule
│  ├─ UnitOfMeasure
│  ├─ Target
│  ├─ Threshold
│  ├─ Dimension
│  ├─ TimePeriod
│  └─ Grain
│
├─ [SemanticModelModule] ── module tag only, no shared superclass
│  ├─ SemanticLayer
│  ├─ SemanticModel
│  ├─ SemanticEntity
│  ├─ SemanticAttribute
│  ├─ SemanticMeasure
│  ├─ SemanticRelationship      (now instantiated — was orphan in v1.0.0)
│  ├─ BusinessTerm   (⊑ skos:Concept)
│  ├─ BusinessDefinition
│  │   └─ CertifiedDefinition   (also here, via owl:equivalentClass)
│  └─ MappingRule
│      [Synonym — REMOVED; superseded by skos:altLabel]
│
├─ [LineageModule] ── module tag only, no shared superclass
│  ├─ OperationalSystem
│  ├─ SourceApplication
│  ├─ SourceTable
│  ├─ SourceField
│  ├─ DataProduct               (now instantiated; wrapsDataset)
│  ├─ DataPipeline
│  │   └─ TransformationStep    (⊑ prov:Activity)
│  ├─ DataQualityRule
│  └─ ProvenanceEvent           (⊑ prov:Activity)
│      [LineageNode, LineageEdge — REMOVED bucket/orphan]
│      (Dataset and its three layers live under the genuine superclass above,
│       not under this module tag, but are also dcterms:isPartOf LineageModule)
│
└─ [GovernanceModule] ── module tag only, no shared superclass
   ├─ Policy
   ├─ Standard
   ├─ Control
   ├─ AccessRule                (now instantiated)
   ├─ CertificationStatus  (owl:oneOf: Draft, InReview, Certified, Deprecated)
   ├─ Version
   ├─ ApprovalEvent             (⊑ prov:Activity)
   ├─ AuditEvent                (⊑ prov:Activity)
   └─ StewardshipAssignment     (now carries real properties: assignmentSteward, assignmentStartDate, assignmentEndDate)
```

**Reading the notation:** `⊑` = `rdfs:subClassOf` (genuine subsumption). `≡` = `owl:equivalentClass` (reasoner-inferred membership). `⟂ disjoint with` = `owl:disjointWith` (mutually exclusive siblings). `[ModuleName]` = a grouping expressed only via `dcterms:isPartOf` → a `skos:Collection` individual, **not** a class and **not** a taxonomy claim — no `rdfs:subClassOf` edge exists to it.

---

## Genuine superclasses vs. module tags — the distinction that drives this whole tree

| Kind | Examples | Test it passes | Mechanism |
|---|---|---|---|
| **Genuine superclass** (real `rdfs:subClassOf`) | `PerformanceIndicator`, `Dataset`, `ConsumptionAsset`, `Role` | Every member is *always and necessarily* that kind of thing, in every context, with no exceptions. | `rdfs:subClassOf` |
| **Module tag** (metadata grouping only) | `BusinessArchitectureModule`, `KPIModelModule`, `SemanticModelModule`, `LineageModule`, `ConsumptionModule`, `GovernanceModule` | Members share a *topic* or *documentation section*, not an essential nature. | `dcterms:isPartOf` → `skos:Collection` individual |

Six `skos:Collection` module-tag individuals exist: `BusinessArchitectureModule`, `KPIModelModule`, `SemanticModelModule`, `LineageModule`, `ConsumptionModule`, `GovernanceModule`. Every class in the ontology carries exactly one `dcterms:isPartOf` edge to one of these six — including classes that also sit under a genuine superclass (e.g., `GoldLayerDataset` is both `rdfs:subClassOf Dataset` **and** `dcterms:isPartOf LineageModule` — the two facts serve different purposes and don't conflict).

---

## Property hierarchy (new in v2.0.0)

Object/datatype properties are also organized, via `rdfs:subPropertyOf`, into three super-properties — the property-level analogue of the class hierarchy above:

```
hasSpecificationElement   (parent — "give me everything that specifies this KPI")
├─ hasFormula
├─ hasAggregationRule
├─ hasUnitOfMeasure
├─ hasTarget
├─ hasThreshold
├─ hasTimePeriod  (was targetPeriod gap in v1.0.0 — now implemented)
└─ hasGrain

hasGovernanceRecord   (parent — "give me everything governing this asset")
├─ hasCertificationStatus  (owl:FunctionalProperty)
├─ hasVersion
├─ auditedBy
└─ restrictedBy

hasSemanticComponent   (parent — "give me everything composing this semantic model")
├─ hasSemanticEntity
├─ hasSemanticMeasure
└─ hasSemanticAttribute
```

Two properties are deliberately *not* collapsed into one another despite looking redundant — see the Best Practices document, §9, for why both are kept:

- `stewardedBy` — a denormalized "current steward, one hop" shortcut on the governed asset itself.
- `hasStewardshipAssignment` → `StewardshipAssignment` — the authoritative, time-bound record (`assignmentSteward`, `assignmentStartDate`, `assignmentEndDate`).

---

## Controlled vocabularies (`owl:oneOf` — closed enumerations)

| Class | Closed values | New in v2.0.0? |
|---|---|---|
| `CertificationStatus` | Draft, InReview, Certified, Deprecated | Pre-existing |
| `Criticality` | High, Medium, Low | **New** — was free `xsd:string` |
| `ThresholdSeverity` | Red, Yellow, Green | **New** — was free `xsd:string` |
| `AggregationType` | SUM, AVG, LAST, RATIO | **New** — was free `xsd:string` |
| `ObservationStatus` | OnTarget, Watch, Breach | **New** — supports the new observation layer |

---

## Restrictions that operationalize key distinctions (new in v2.0.0)

| Class | Restriction | What it formally guarantees |
|---|---|---|
| `KPI` | `hasDefinition someValuesFrom KPIDefinition` | No orphan KPIs without a documented definition. |
| `KPI` | `ownedBy someValuesFrom BusinessOwner` | The actual reasoner-checkable difference between a `KPI` and a plain `Metric` — a Metric has no owner requirement. |
| `RawLayerDataset` | `prov:wasDerivedFrom someValuesFrom SourceField` | Raw datasets must trace to a real source field. |
| `SilverLayerDataset` | `prov:wasDerivedFrom someValuesFrom RawLayerDataset` | Silver datasets must trace to a raw dataset — enforces medallion order. |
| `GoldLayerDataset` | `feedsSemanticModel someValuesFrom SemanticModel` | Gold datasets must actually feed a governed semantic model, not dead-end. |

---

## Worked example — Downstream O&G Commercial individuals mapped to the tree

| Class | Individual(s) in the worked example |
|---|---|
| `KPI` | `RackPriceCaptureRateKPI` |
| `KPIDefinition` / `CertifiedDefinition` | `RackPriceCaptureRateDefinition_v1` |
| `StrategicObjective` | `ImproveRackCapture99pctQ4FY26` |
| `BusinessGoal` | `ProtectGrowCommercialMarginGoal` |
| `BusinessCapability` | `RackPriceManagementCapability`, `MarginPerformanceManagementCapability` |
| `BusinessProcess` / `ProcessStep` | `RackPriceSettingProcess` (4 steps) |
| `ValueStream` | `DownstreamCommercialValueStream` |
| `OrganizationalUnit` | `CommercialPricingDistributionTeam` |
| `BusinessOwner` / `DataSteward` | `CommercialPricingManager`, `CommercialDataSteward` |
| `Dimension` / `DimensionValue` | `TerminalDimension` (→ `HoustonRackTerminal3`, `BeaumontRackTerminal1`), `ProductDimension` (→ `ULSDDieselProduct`, `RBOBGasolineProduct`) |
| `Target` / `Threshold` | `Target_99pct_Q4FY26`, `RedThreshold_97pct` |
| `RawLayerDataset` → `SilverLayerDataset` → `GoldLayerDataset` | `RackLiftings_*` chain (RightAngle CTRM) and parallel `OPISBenchmark_*` chain (OPIS Market Data Service) |
| `OperationalSystem` | `RightAngleCTRM`, `OPISMarketDataService` |
| `SemanticModel` | `CommercialPricingSemanticModel` (3 entities, 2 relationships, 1 measure) |
| `Dashboard` | `CommercialPricingDashboard` |
| `KPIObservation` | Three individuals: 2026-06-30 OnTarget, 2026-07-31 Watch, 2026-07-31 Breach (different terminal/product) |

For the full backward trace from `CommercialPricingDashboard` to source fields, see Part 6 of "Stage 3 — RDF/OWL Teaching Document."

---

## Change log vs. v1.0.0

- **Removed:** `BusinessArchitectureElement`, `SemanticAsset`, `LineageNode`, `GovernanceElement` bucket superclasses; `Synonym` class; `LineageEdge` class.
- **Kept as genuine superclasses:** `ConsumptionAsset`, `PerformanceIndicator`, `Dataset`.
- **Added:** module-tagging pattern (`dcterms:isPartOf` + 6 `skos:Collection` individuals); observation/fact layer (`KPIObservation`, `DimensionValue`, `ObservationStatus`); property hierarchy (`hasSpecificationElement`, `hasGovernanceRecord`, `hasSemanticComponent`); 3 new closed vocabularies (`Criticality`, `ThresholdSeverity`, `AggregationType`) plus `ObservationStatus`; 5 new `owl:Restriction`s; `Role rdfs:subClassOf foaf:Agent`.
- **Reconciled:** `targetPeriod` implemented and wired to real `TimePeriod` individuals; `SemanticRelationship`, `DataProduct`, `AccessRule` now instantiated; `StewardshipAssignment` now carries real properties instead of a bare label.
