# Enterprise Metadata Integration Architecture Specification

**ID:** EPM-ARCH-META-001  
**Title:** Enterprise Metadata Integration Architecture: Ontology, DCAT, PROV-O, Purview, Unity Catalog, Bigeye, Semantic Layer, and KPI Store  
**Version:** 0.1  
**Status:** Draft — Candidate Architecture  
**Owner:** Enterprise Data Architecture / Data Governance  
**Last Updated:** 2026-08-23  
**Scope:** Enterprise Performance Model (EPM), initial Downstream Oil & Gas Commercial / Order-to-Cash pilot  
**Primary Objective:** Define a governed, interoperable metadata integration architecture that makes approved business, KPI, data-product, semantic, catalog, lineage, quality, and stewardship context available to downstream consumers without replacing Purview, Unity Catalog, Bigeye, or the semantic layer.

---

## 1. Executive Design Decision

The enterprise will implement a **federated, ontology-linked metadata knowledge graph**.

It will not bulk-import all catalog objects into the domain ontology. Instead, it will selectively project governed metadata from operational systems of authority into a canonical metadata graph. The graph will link:

- domain ontology and business glossary semantics;
- approved KPI and measurement definitions;
- semantic-layer metrics and services;
- Purview enterprise catalog metadata and stewardship;
- Unity Catalog physical assets and enforcement references;
- Bigeye lineage and observability evidence;
- DCAT data-product, distribution, and service metadata; and
- PROV-O provenance and lineage assertions.

The resulting graph becomes the **integration and context plane**. It supports governed discovery, cross-platform impact analysis, data-product publication, KPI traceability, policy-filtered AI grounding, and interoperability. It does not replace the user interfaces, runtime controls, or detailed operational functions of the source platforms.

### 1.1 Core principle

> Keep each metadata fact in its operational system of authority. Publish a validated, selective, identity-resolved projection for enterprise integration and downstream consumption.

Process and domain authority for this scope is the files under `business_architecture/`. Demo tools may stand in for a production system of authority. A demo tool is not a second system of authority.

---

## 2. Scope and Non-Goals

### 2.1 In scope

- Medallion-aligned datasets and data products: Bronze, Silver, and Gold.
- Domain ontology and enterprise glossary alignment.
- KPI Store and enterprise measurement architecture.
- Semantic-layer metric and service metadata.
- Microsoft Purview enterprise discovery, glossary associations, classifications, stewardship, and governance context.
- Databricks Unity Catalog physical asset identity, technical metadata, and enforcement references.
- Bigeye cross-platform lineage and data-observability evidence.
- DCAT 3 catalog/data-product/service projection.
- PROV-O representation of lineage, derivation, activities, agents, and evidence.
- SHACL validation and metadata publication gates.
- Policy-filtered views for business users, engineers, architects, BI tools, APIs, and AI agents.

### 2.2 Out of scope

- Replacing Purview, Unity Catalog, Bigeye, the semantic platform, or source system metadata stores.
- Full replication of every table, field, tag, pipeline run, query plan, log, or ACL into RDF.
- Runtime authorization enforcement through DCAT, RDF, or the knowledge graph.
- Treating legacy Tableau calculations or report logic as approved KPI definitions.
- Broad production integration without a targeted pilot and validation gates.
- Rebuilding reports or migrating BI assets.

---

## 3. Architecture Drivers

| Driver | Architectural response |
|---|---|
| Business terms and KPIs need enterprise meaning | Domain ontology, SKOS glossary, and KPI Store provide stable semantics and governance |
| Metrics must be calculated consistently | Semantic layer remains the executable authority for governed calculations |
| Technical assets live across platforms | Purview supplies enterprise discovery; Unity Catalog governs Databricks assets |
| Lineage and quality evidence are fragmented | Bigeye, Unity Catalog, pipelines, and Purview contribute evidence normalized through PROV-O |
| Consumers need different levels of technical detail | Publish policy-filtered consumer views over a shared canonical graph |
| Catalog interchange needs to be portable | DCAT represents datasets, distributions, services, publisher/contact, access, and interoperability metadata |
| Auditability is required for KPIs | Versioned definitions, qualified provenance, quality evidence, lineage validation, and stable IDs are required |
| The platform estate evolves | Source authorities remain decoupled from the canonical projection through adapters and mapping contracts |

---

## 4. Architecture Overview

```text
+----------------------------------------------------------------------------------+
|                              DOWNSTREAM CONSUMERS                                |
|----------------------------------------------------------------------------------|
| Business users | BI developers | Engineers | Architects | Auditors | AI agents   |
+----------------------+---------------------+----------------------+-------------+
                       |                     |                      |
                       v                     v                      v
+----------------------------------------------------------------------------------+
|                    CONSUMPTION / EXPERIENCE LAYER                                |
|----------------------------------------------------------------------------------|
| Purview discovery UI | Data-product portal | Semantic APIs | Context API | SPARQL|
| Policy-filtered search, lineage views, access-request routes, AI retrieval       |
+-----------------------------------+----------------------------------------------+
                                    |
                                    v
+----------------------------------------------------------------------------------+
|             ENTERPRISE METADATA KNOWLEDGE GRAPH / CONTEXT PLANE                  |
|----------------------------------------------------------------------------------|
| Canonical metadata instances + relationship graph                                |
| DCAT 3 | PROV-O | SKOS | OWL/RDFS | SHACL | Enterprise EPM vocabulary            |
|                                                                              |
| Dataset/DataProduct --supports--> KPI --implementedBy--> SemanticMetric          |
|          |                            |                                         |
|          +--hasDistribution--> PhysicalAsset --wasDerivedFrom--> SourceAsset      |
|          +--servedBy--> SemanticService --enforces--> PolicyReference             |
|          +--hasConcept--> DomainOntologyConcept                                 |
+-----------------------------------+----------------------------------------------+
                                    |
                                    v
+----------------------------------------------------------------------------------+
|                METADATA INTEGRATION AND GOVERNANCE SERVICES                     |
|----------------------------------------------------------------------------------|
| Extract | Normalize | Identity resolve | Map | Reconcile | Validate | Publish     |
| Adapters: Purview | Unity enrichment | Bigeye | Semantic layer | KPI Store | MDM  |
| Controls: mapping registry | SHACL | approval gate | audit log | drift detection  |
+-----------------------------------+----------------------------------------------+
                                    |
                                    v
+----------------------------------------------------------------------------------+
|                  OPERATIONAL SYSTEMS OF AUTHORITY                                |
|----------------------------------------------------------------------------------|
| Domain Ontology | KPI Store | Semantic Layer | Purview | Unity Catalog | Bigeye |
| Source systems / pipelines / Medallion data products / Power BI                   |
+----------------------------------------------------------------------------------+
```

---

## 5. System Responsibilities and Authority

### 5.1 Systems of authority

| Metadata category | System of authority | Canonical graph treatment |
|---|---|---|
| Business concept definition and relationships | Domain ontology / business glossary governance | Link by stable URI; do not duplicate definition authority |
| KPI identity, approval, owner, thresholds, review cadence | Enterprise KPI Store / KPI Catalog | Project approved KPI metadata and versions |
| Metric formula, dimensions, grain, calculation behavior | Semantic-layer repository/platform | Project metric descriptor and immutable implementation reference |
| Databricks physical object identity and permissions | Unity Catalog | Reference object IDs/names, tags, and enforcement-policy identifiers |
| Enterprise catalog discovery and business enrichment | Purview | Project asset identity, classifications, glossary links, stewardship, domains, and catalog context |
| Cross-platform lineage and quality evidence | Bigeye, with other lineage sources retained | Normalize as source-attributed lineage evidence |
| Pipeline transformation declarations | Transformation/orchestration platform, dbt, Databricks jobs | Map into PROV-O activities where available |
| Catalog interchange representation | Metadata integration service | Publish versioned DCAT/PROV-O/enterprise RDF projection |
| Runtime data access | Unity Catalog, semantic layer, API gateway, BI platform | Reference access policies only; never enforce from graph |

### 5.2 Non-negotiable authority rules

1. One authoritative system is declared for every material metadata field.
2. A projection may enrich or link source facts but must not silently overwrite source facts.
3. A catalog label is never used as the sole integration key; use stable GUIDs, platform object IDs, or canonical URIs.
4. An observed lineage edge is not automatically validated KPI lineage.
5. A Gold object is not automatically certified merely because it is in a Gold schema.
6. A widely used calculation is not automatically an approved KPI.
7. DCAT describes access and services; it does not execute permission enforcement.

### 5.3 Process authority and demo stand-ins

The files under `business_architecture/business_process/` and `business_architecture/schema/` are the Downstream oil and gas process set, including order-to-cash (O2C). Those two folders are process authority. Files under `business_architecture/domain/` are draft context, not process authority.

Current files on `main`:

- `business_architecture/business_process/downstream_process_map.json`
- `business_architecture/business_process/value_stream_order_to_cash.json`
- `business_architecture/business_process/value_stream_commercial_lifecycle.json`
- `business_architecture/business_process/data_product_portfolio.json`
- `business_architecture/business_process/office_lanes.json`
- `business_architecture/schema/data_product_portfolio.schema.json`
- `business_architecture/schema/value_stream.schema.json`

Demo and reference implementations may use the open-source tools in the table below. The production system of authority is unchanged. A demo tool is not a second system of authority.

| Demo tool | Production seat | Concern |
|---|---|---|
| Sirius Web | ER/Studio | Models |
| OpenMetadata | Purview | Enterprise catalog |
| Neo4j Community | Neo4j | Serving graph |
| Apache Jena Fuseki | none (demo runtime only) | SPARQL and SHACL loaded from git Turtle |

Formal ontology source of truth stays Turtle in git (the ontology file format). The serving graph stays Neo4j. Production seats stay ER/Studio, Purview, Unity Catalog, Bigeye, and Databricks Metric Views.

---

## 6. Vocabulary and Information Model

### 6.1 Standards and enterprise extensions

| Vocabulary | Role |
|---|---|
| DCAT 3 | Catalogs, datasets, distributions, data services, contacts, access, interoperability |
| PROV-O | Entities, activities, agents, derivation, attribution, qualified provenance |
| SKOS | Glossary terms, synonyms, preferred labels, broader/narrower relationships, controlled taxonomies |
| OWL/RDFS | Domain ontology classes, properties, semantic constraints, inference where appropriate |
| SHACL | Publication-profile validation and data-quality constraints for metadata graphs |
| Dublin Core Terms | Titles, descriptions, identifiers, subjects, rights, versions, temporal coverage |
| EPM vocabulary | KPI, metric, measure, data product, certification, Medallion role, semantic service, quality control, mapping status |

### 6.2 Core enterprise classes

```text
Business / domain layer
  BusinessCapability
  ValueStream
  Domain
  Process
  BusinessConcept
  KPI
  Metric
  SemanticMetric

Data product / catalog layer
  DataProduct
  PhysicalDataAsset
  DataService
  DataContract
  DataQualityProfile
  PolicyReference

Governance layer
  BusinessOwner
  DataProductOwner
  DataSteward
  TechnicalOwner
  SecurityOwner
  Classification
  CertificationStatus
  LifecycleStatus

Evidence / lineage layer
  LineageAssertion
  DataQualityIncident
  DataQualityRule
  TransformationActivity
  SourceSystem
  CatalogRecord
```

### 6.3 Required relationship patterns

```text
KPI --measures--> BusinessObjective / Capability / Process
KPI --isImplementedBy--> SemanticMetric
SemanticMetric --isServedBy--> SemanticService
SemanticMetric --isComputedFrom--> DataProduct
DataProduct --hasDistribution--> PhysicalDataAsset
DataService --dcat:servesDataset--> DataProduct
PhysicalDataAsset --prov:wasDerivedFrom--> PhysicalDataAsset
PhysicalDataAsset --representsConcept--> BusinessConcept
PhysicalDataAsset --hasCatalogRecord--> PurviewAsset
PhysicalDataAsset --hasPlatformObject--> UnityCatalogObject
DataProduct --supportsKPI--> KPI
DataProduct --hasDataSteward--> StewardGroup
DataProduct --hasClassification--> Classification
LineageAssertion --assertedBy--> EvidenceSource
LineageAssertion --hasValidationStatus--> LineageStatus
```

---

## 7. Detailed Logical Architecture

```text
                                     +---------------------------+
                                     | Domain Ontology Repository |
                                     | OWL/RDFS + SKOS            |
                                     | concepts / glossary / URI  |
                                     +-------------+-------------+
                                                   |
                           concept and KPI links   |
                                                   v
+----------------------+      +-------------------+--------------------+      +----------------------+
| Enterprise KPI Store |----->| Canonical Metadata / Knowledge Graph   |<-----| Semantic Layer        |
| definitions, owners, |      | DCAT + PROV-O + EPM extensions         |      | metrics, dimensions,  |
| versions, thresholds |      | graph data + versioned projections     |      | services, APIs         |
+----------------------+      +-------------------+--------------------+      +----------------------+
                                                   ^
                                                   |
                         mapped / validated metadata projections
                                                   |
+---------------------+      +---------------------+-------------------+      +----------------------+
| Microsoft Purview   |----->| Metadata Integration Service             |<-----| Bigeye               |
| catalog, glossary,  |      |                                           |      | lineage, incidents,   |
| classifications,    |      | - extract and delta capture              |      | observability         |
| stewardship         |      | - normalize and identity resolve          |      +----------------------+
+----------+----------+      | - map to canonical RDF                    |
           ^                 | - reconcile evidence                      |
           | scan             | - SHACL validate                          |
           |                  | - publish and audit                       |
+----------+----------+      +---------------------+-------------------+
| Unity Catalog       |--------------------------^                      
| technical objects,  |                                                 
| grants, tags, lineage|                                                
+---------------------+                                                 
```

---

## 8. Medallion Integration Pattern

### 8.1 Logical role of layers

| Layer | Operational purpose | Catalog / graph treatment | Default consumer posture |
|---|---|---|---|
| Bronze | Source-aligned ingestion, preservation of source context | Project selectively for source/lineage/controls; typically restricted | Engineering, lineage, audit |
| Silver | Conformance, standardization, reusable domain representations | Catalog reusable domain products and critical conformed entities | Engineering, analytics, modelers |
| Gold | Curated, purpose-oriented analytical products | Primary DCAT data-product publication and KPI links | BI, semantic layer, data science, controlled AI |
| Semantic layer | Governed analytical calculation and serving | Publish as `dcat:DataService`; link approved metrics | BI, applications, agents |

### 8.2 Example asset chain

```text
RightAngle commercial transactions                 OPIS market assessments
                 |                                          |
                 v                                          v
commercial.bronze.rightangle_transaction_raw      commercial.bronze.opis_assessment_raw
                 |                                          |
                 +-------------------+----------------------+ 
                                     v
commercial.silver.commercial_transaction_conformed
commercial.silver.market_price_assessment_conformed
                                     |
                                     v
commercial.gold.commercial_pricing_performance
                                     |
                                     v
Commercial Performance Semantic Service
                                     |
                                     v
Rack Price Capture Rate % / approved BI and agent consumers
```

### 8.3 Metadata representation by layer

```text
Gold logical product
  = dcat:Dataset + epm:DataProduct

Gold UC table/view
  = dcat:Distribution + epm:PhysicalDataAsset + prov:Entity

Semantic endpoint
  = dcat:DataService + epm:SemanticService

Transformation path
  = prov:Activity + prov:used + prov:wasGeneratedBy / prov:wasDerivedFrom

Business meaning
  = ontology concept URI links and SKOS glossary terms
```

---

## 9. Purview, Unity Catalog, and DCAT Integration

### 9.1 Standard flow for Databricks-managed assets

```text
+--------------------+        scheduled scan / incremental harvest       +------------------------+
| Unity Catalog      | ------------------------------------------------> | Microsoft Purview      |
|                    |                                                     |                        |
| catalogs/schemas   |                                                     | Data Map assets        |
| tables/views       |                                                     | glossary associations  |
| tags/comments      |                                                     | classifications        |
| grants/filters     |                                                     | stewardship            |
| native lineage     |                                                     | governance context     |
+--------------------+                                                     +-----------+------------+
                                                                                      |
                                                    approved data product / asset delta|
                                                                                      v
                                                                     +----------------+----------------+
                                                                     | Metadata Integration Service   |
                                                                     | Purview -> canonical -> DCAT   |
                                                                     +----------------+----------------+
                                                                                      |
                                                                                      v
                                                                     +----------------+----------------+
                                                                     | DCAT / PROV-O Graph Projection |
                                                                     +---------------------------------+
```

### 9.2 Division of responsibility

| Capability | Unity Catalog | Purview | DCAT / Metadata Graph |
|---|---|---|---|
| Databricks table and view registration | Owns | Ingests | References |
| Databricks runtime authorization | Enforces | Documents/contextualizes | References policy |
| Enterprise discovery across platforms | Local scope | Owns | Federation/search endpoint |
| Glossary association and business labels | Optional/local | Owns enterprise association | Links ontology URI |
| Classifications | Tags may exist | Owns enterprise classification model | Projects approved classification |
| Owners/stewards | Technical ownership | Owns business stewardship view | Publishes role references |
| Data-product record | Technical representation | Enterprise managed representation | DCAT logical dataset |
| Lineage | Native Databricks lineage | Catalog lineage view | PROV-O normalized evidence |

### 9.3 Purview mapping policy

The integration service reads from Purview only assets and data products that have an explicit publication status:

```text
Draft      : not published outside Purview
Publish    : may be emitted as a non-certified DCAT record
Certified  : eligible for broad enterprise/semantic/AI consumption
Withhold   : retained in Purview only; never emitted to open graph views
Retired    : emitted only with lifecycle status and replacement relation
```

---

## 10. Bigeye-to-PROV-O Lineage Integration

### 10.1 Purpose

Bigeye contributes cross-platform lineage and data-observability evidence. It enriches the enterprise lineage graph, especially where platform-native lineage is incomplete across warehouses, lakehouses, ETL, BI, and source systems.

### 10.2 Evidence model

```text
                  Bigeye observed relationship
     upstream node ---------------------------------> downstream node
                     |                                      |
                     +----------------+---------------------+
                                      v
                          Qualified lineage assertion
                          - Bigeye node IDs
                          - connector/source
                          - observation time
                          - confidence/evidence type
                          - reconciliation state
                          - quality incident references
```

### 10.3 PROV-O mapping

| Bigeye evidence | Canonical representation |
|---|---|
| Table/data node | `prov:Entity`, `epm:PhysicalDataAsset` |
| Column/data node | `prov:Entity`, `epm:PhysicalField` |
| Parent-child lineage | `prov:wasDerivedFrom` and qualified `prov:Derivation` |
| Transformation job, if exposed | `prov:Activity` |
| Bigeye connector/parser | `prov:SoftwareAgent` |
| Bigeye scan/observation | Source-attributed lineage assertion with timestamp |
| Quality monitor | `epm:DataQualityRule` |
| Incident/anomaly | `epm:DataQualityIncident` linked to entity/derivation |

### 10.4 Qualified derivation pattern

```turtle
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix epm:  <https://epm.example.org/id/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

epm:GoldCommercialPricing
    a prov:Entity, epm:PhysicalDataAsset ;
    prov:qualifiedDerivation epm:Derivation_GoldPricing_From_SilverTransaction .

epm:Derivation_GoldPricing_From_SilverTransaction
    a prov:Derivation, epm:ObservedLineageAssertion ;
    prov:entity epm:SilverCommercialTransaction ;
    prov:hadActivity epm:BuildGoldCommercialPricing_v17 ;
    prov:wasAttributedTo epm:BigeyeLineageConnector ;
    epm:sourceSystem "Bigeye" ;
    epm:bigeyeDataNodeId "123456" ;
    epm:observedAt "2026-08-23T19:15:00Z"^^xsd:dateTime ;
    epm:assertionStatus epm:ObservedCrossPlatform ;
    epm:reconciliationStatus epm:PendingValidation .
```

### 10.5 Lineage reconciliation policy

```text
Bigeye edge + Unity Catalog edge + declared pipeline edge agree
  -> status: Corroborated
  -> eligible for approved lineage review

Bigeye edge exists only
  -> status: ObservedCrossPlatform
  -> eligible for investigation; not KPI-validated

Declared pipeline edge exists but Bigeye disagrees
  -> status: Conflict
  -> steward/technical owner review required

KPI owner and data steward approve traceability chain
  -> status: ValidatedForKPI
```

---

## 11. Canonical Metadata Integration Service

### 11.1 Component design

```text
+----------------------------------------------------------------------------------+
|                     METADATA INTEGRATION SERVICE                                |
|----------------------------------------------------------------------------------|
| Ingress adapters                                                                 |
|  [Purview] [Unity enrichment] [Bigeye] [Semantic layer] [KPI Store] [Ontology]   |
|       |                                                                          |
|       v                                                                          |
| Canonicalization                                                                 |
|  - normalize identifiers, time, classification, owner/steward roles              |
|  - map source attributes to canonical metadata model                             |
|       |                                                                          |
|       v                                                                          |
| Identity and mapping registry                                                    |
|  - canonical URI allocation                                                      |
|  - Purview GUID <-> Unity object <-> Bigeye node <-> ontology URI               |
|       |                                                                          |
|       v                                                                          |
| Reconciliation and policy engine                                                 |
|  - source authority enforcement                                                  |
|  - lineage evidence comparison                                                   |
|  - publish eligibility / sensitivity filtering                                   |
|       |                                                                          |
|       v                                                                          |
| Validation                                                                       |
|  - SHACL profile validation                                                      |
|  - approval, contract, owner, quality, lineage completeness gates                |
|       |                                                                          |
|       v                                                                          |
| Publication and audit                                                            |
|  - RDF / JSON-LD graph publication                                               |
|  - versioned snapshot and delta events                                           |
|  - audit records, error queues, steward remediation                              |
+----------------------------------------------------------------------------------+
```

### 11.2 Service modules

| Module | Responsibilities |
|---|---|
| Purview extractor | Extract eligible assets, terms, classifications, business metadata, contacts, governance relationships, and lineage references |
| Unity enrichment adapter | Resolve durable UC object IDs, object location, current service endpoint, policy reference, and technical metadata missing from Purview |
| Bigeye adapter | Extract lineage nodes, relationships, monitors, incidents, source connector metadata, and observation times |
| Semantic adapter | Extract approved metrics, dimensions, time grains, service endpoints, version IDs, and model references |
| KPI Store adapter | Extract KPI identity, owner, purpose, thresholds, lifecycle, approval, and formula reference |
| Ontology linker | Resolve business concept/domain/process/capability URIs and verify semantic mapping state |
| Canonical mapper | Produce RDF/JSON-LD using DCAT, PROV-O, SKOS, and EPM terms |
| Mapping registry | Maintain stable cross-system identity mappings and mapping version history |
| Reconciliation engine | Detect identity conflicts, duplicate assets, competing lineage, stale mappings, and unapproved semantics |
| SHACL validator | Validate standard and enterprise-profile constraints before publication |
| Publisher | Publish graph snapshots/deltas, API records, and consumer indexes |
| Audit/remediation service | Store evidence, failures, approval actions, and steward work items |

---

## 12. Identity Resolution and Mapping Registry

### 12.1 Why it is required

The same thing can appear under different identifiers:

```text
Unity Catalog table:
  commercial.gold.commercial_pricing_performance

Purview asset:
  GUID 9e24... / qualifiedName databricks://...

Bigeye node:
  node 123456

Data product:
  DP-COMM-PRICING-001

Domain concept:
  https://epm.example.org/ontology/commercial#CommercialTransaction

DCAT dataset:
  https://epm.example.org/id/data-product/DP-COMM-PRICING-001
```

The mapping registry establishes which identifiers refer to the same logical asset, which refer to a physical implementation, and which are related but not equivalent.

### 12.2 Registry record

| Field | Example |
|---|---|
| Canonical URI | `https://epm.example.org/id/asset/commercial-pricing-gold-v1` |
| Resource type | `PhysicalDataAsset` |
| Unity Catalog object | `commercial.gold.commercial_pricing_performance` |
| Unity object ID | Platform-specific ID |
| Purview GUID | `9e24...` |
| Bigeye node ID | `123456` |
| Data product ID | `DP-COMM-PRICING-001` |
| Ontology concepts | CommercialTransaction, Terminal, Product, MarketPriceAssessment |
| Mapping method | Declared / reviewed / inferred |
| Mapping confidence | 1.0 / 0.95 / unknown |
| Mapping status | Approved / pending review / retired |
| Effective dates | Start/end validity |
| Mapping version | `1.0.0` |

### 12.3 Mapping rules

- Stable IDs, not names, are primary keys.
- Qualified names are useful secondary keys but can change.
- A logical data product is not the same resource as a physical table.
- A physical table can implement more than one logical data product only with explicit relationship and governance review.
- A glossary term link is not proof that an entire asset semantically represents that concept.
- Inferred mappings must be labelled `Candidate` and cannot support certified KPI lineage until reviewed.

---

## 13. DCAT Publication Model

### 13.1 DCAT resource patterns

```text
Enterprise catalog
  dcat:Catalog
      |
      +-- dcat:Dataset = logical governed DataProduct
              |
              +-- dcat:Distribution = physical table / view / file / secure share
              |
              +-- dcat:DataService = semantic layer analytical service
```

### 13.2 Core mapping

| Enterprise concept | DCAT representation |
|---|---|
| Enterprise data-product catalog | `dcat:Catalog` |
| Governed logical data product | `dcat:Dataset` |
| Physical Unity Catalog table/view or export | `dcat:Distribution` |
| Semantic-layer endpoint/API | `dcat:DataService` |
| Product owner | `dcterms:publisher` plus enterprise role relation |
| Steward/contact | `dcat:contactPoint` |
| Domain/business subject | `dcterms:subject` referencing ontology URI |
| Contract/profile | `dcterms:conformsTo` |
| Access posture | `dcterms:accessRights` and enterprise policy references |
| Source/provenance | PROV-O links; do not overload DCAT alone |

### 13.3 Example product projection

```turtle
@prefix dcat:    <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix epm:     <https://epm.example.org/id/> .

epm:DP-CommercialPricingPerformance
    a dcat:Dataset, epm:DataProduct ;
    dcterms:title "Commercial Pricing Performance" ;
    dcterms:description "Certified Gold data product for governed downstream commercial pricing performance analytics." ;
    dcterms:subject epm:CommercialPricing ;
    dcterms:publisher epm:CommercialDataProductsGroup ;
    dcat:contactPoint epm:CommercialDataStewardshipGroup ;
    epm:certificationStatus epm:Certified ;
    epm:medallionLayer epm:Gold ;
    epm:supportsKPI epm:RackPriceCaptureRate ;
    epm:representsConcept epm:CommercialTransaction , epm:Terminal , epm:Product , epm:MarketPriceAssessment ;
    dcat:distribution epm:DistCommercialPricingGoldTable , epm:DistCommercialPricingSecureView ;
    dcterms:conformsTo epm:CommercialPricingDataProductContractV1 ;
    prov:wasDerivedFrom epm:SilverCommercialTransaction , epm:SilverMarketPriceAssessment .

epm:CommercialPerformanceSemanticService
    a dcat:DataService, epm:SemanticService ;
    dcterms:title "Commercial Performance Semantic Service" ;
    dcat:servesDataset epm:DP-CommercialPricingPerformance ;
    epm:providesMetric epm:MetricRackPriceCaptureRatePct ;
    epm:enforcesPolicy epm:CommercialPricingAccessPolicy .
```

---

## 14. Semantic Layer and KPI Store Integration

### 14.1 Role boundary

```text
Domain ontology:
  What is a Terminal, Contract, Product, Market Price Assessment, KPI?

KPI Store:
  What is the approved KPI, why does it matter, who owns it,
  which threshold and review process apply?

Semantic layer:
  How is the metric actually calculated, filtered, joined, aggregated,
  secured, optimized, and served?

Metadata graph:
  How do those definitions connect to the data product, physical assets,
  lineage, quality evidence, reports, and consumers?
```

### 14.2 Required KPI traceability chain

```text
Business objective
      |
      v
Approved KPI
      |
      +-- approved definition / formula meaning / owner / thresholds
      |
      v
Semantic metric implementation version
      |
      +-- dimensions / time grain / aggregation / eligibility rules
      |
      v
Semantic service endpoint
      |
      v
Certified Gold data product
      |
      v
Silver conformed products
      |
      v
Bronze source-aligned assets and source systems
      |
      v
Data quality controls, freshness, and lineage evidence
```

### 14.3 KPI lineage state gate

A KPI may be published as `Approved KPI` only when its traceability chain has:

- approved KPI definition and ownership;
- approved semantic metric version;
- defined dimensions and time grain;
- known Gold data product;
- lineage to required sources;
- quality and freshness expectations;
- approved access posture;
- source evidence and validation status;
- a version/effective-date policy.

---

## 15. Consumer Views and Availability Model

### 15.1 Do not expose one raw graph to everyone

```text
Canonical graph
      |
      +-- Business discovery view
      +-- Technical engineering view
      +-- KPI governance/audit view
      +-- Semantic metric developer view
      +-- AI context view
      +-- Partner/federated DCAT exchange view
```

### 15.2 Consumer interfaces

| Consumer | Interface | Permitted context |
|---|---|---|
| Business user | Purview/data-product portal | Product meaning, steward, certification, glossary, access route, high-level lineage |
| BI developer | Semantic catalog/API | Approved metrics, dimensions, grain, service contract, usage guidance |
| Data engineer | Purview + Unity + technical lineage API | Schemas, quality rules, transformations, physical mappings, detailed lineage |
| Architect/modeler | Graph explorer / SPARQL / modeling repository | Ontology, mapping registry, provenance, dependency analysis |
| Auditor/controller | Evidence portal | KPI version, approvals, validated lineage, quality status, sources, review trail |
| AI agent | Policy-filtered context API + semantic tools | Approved concepts, metric/service contracts, quality/freshness, user-permitted paths |
| External partner | DCAT export/profile endpoint | Only externally shareable datasets/services and approved metadata |

### 15.3 AI query pattern

```text
User: Why did Rack Price Capture Rate decline in Houston last month?

1. Agent retrieves approved KPI context from metadata graph.
2. Agent verifies requester access, approved semantic metric, valid variants, and data freshness.
3. Agent invokes semantic service with approved metric, filters, and grouping dimensions.
4. Agent retrieves policy-permitted driver/lineage/quality context.
5. Agent returns answer with KPI version, freshness, and evidence references.

The agent must not invent a metric formula, source table, join path, or report logic.
```

---

## 16. Security, Privacy, and Policy Design

### 16.1 Separation of discovery and access

```text
Catalog / graph says:
  "This product exists; it is commercially sensitive; request access here."

Runtime platform says:
  "This identity can or cannot query this table/service at this moment."
```

### 16.2 Policy principles

- Unity Catalog and other runtime systems enforce grants, masks, row filters, and storage permissions.
- Purview manages discoverability, classification, governance context, and stewardship workflow.
- The canonical graph publishes policy references and access posture, not executable secrets or ACL payloads.
- DCAT output is filtered by audience; no sensitive technical metadata is automatically public.
- AI context APIs must apply the same identity, purpose, and sensitivity controls as data/service access.
- Bigeye incidents and detailed column lineage may be restricted to engineering and control personas.

### 16.3 Classification crosswalk

| Unity tag / technical tag | Purview classification | Canonical graph term | Consumer exposure |
|---|---|---|---|
| `pii=true` | `PersonalContactData` | `epm:PersonalContactData` | Restricted |
| `commercial_sensitivity=high` | `CommerciallySensitivePricing` | `epm:CommerciallySensitivePricing` | Restricted/need-to-know |
| `layer=gold` | none by itself | `epm:Gold` | Internal |
| `certified=true` only after governance approval | `CertifiedDataProduct` | `epm:Certified` | Broad enterprise discovery |
| `retention=7y` | `RecordsRetention` | `epm:RetentionPolicyRef` | Role-specific |

---

## 17. Validation and Quality Controls

### 17.1 Publication gates

```text
Source metadata change
      |
      v
Extract and normalize
      |
      v
Identity mapping resolved?
  no --> remediation queue
  yes
      |
      v
Authority and publication eligibility satisfied?
  no --> retain source metadata only
  yes
      |
      v
SHACL validation passed?
  no --> block publication and notify steward
  yes
      |
      v
Publish versioned graph projection and audit event
```

### 17.2 Minimum Certified Gold data-product requirements

- Stable data-product ID and canonical URI.
- Name, description, domain, lifecycle, and certification status.
- Business owner, data-product owner, and data steward group.
- At least one business-concept URI mapping.
- At least one approved access form: distribution and/or semantic service.
- Purview asset ID and platform-specific physical-object reference.
- Contract and quality profile reference.
- Data sensitivity/access posture.
- Freshness expectation and current quality status reference.
- Lineage reference to required upstream products/sources.
- Approved metric/KPI association where the product supports enterprise performance measurement.

### 17.3 Example SHACL pattern

```turtle
@prefix sh:      <http://www.w3.org/ns/shacl#> .
@prefix dcat:    <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix epm:     <https://epm.example.org/id/> .

epm:CertifiedGoldDataProductShape
    a sh:NodeShape ;
    sh:targetClass epm:CertifiedGoldDataProduct ;
    sh:property [ sh:path dcterms:title ; sh:minCount 1 ] ;
    sh:property [ sh:path dcterms:publisher ; sh:minCount 1 ] ;
    sh:property [ sh:path dcat:contactPoint ; sh:minCount 1 ] ;
    sh:property [ sh:path epm:representsConcept ; sh:minCount 1 ] ;
    sh:property [ sh:path dcat:distribution ; sh:minCount 1 ] ;
    sh:property [ sh:path epm:hasDataContract ; sh:minCount 1 ] ;
    sh:property [ sh:path epm:hasClassification ; sh:minCount 1 ] .
```

---

## 18. End-to-End Operational Flows

### 18.1 New Gold product publication

```text
1. Engineering creates Gold asset in Unity Catalog.
2. Unity Catalog scan makes technical metadata discoverable in Purview.
3. Steward assigns/validates glossary concepts, classification, ownership, contract, quality profile, and publish state in Purview.
4. Data-product owner approves certification after required quality and governance checks.
5. Metadata integration service extracts the eligible Purview record.
6. Identity resolver links UC object, Purview GUID, domain URIs, and product ID.
7. Bigeye lineage/quality adapter enriches source-to-product evidence.
8. Semantic adapter links the relevant semantic service/metrics, if any.
9. SHACL profile validates completeness.
10. Service publishes DCAT/PROV-O/ontology-linked projection.
11. Portal, graph API, and policy-filtered AI context index update.
12. Audit event records source versions, mapping version, approver, and publication timestamp.
```

### 18.2 Source-schema change and impact assessment

```text
Source change in RightAngle or OPIS
      |
      v
Bronze/Silver asset schema changes
      |
      v
Unity Catalog and/or Bigeye observe change
      |
      v
Purview metadata/lineage refresh
      |
      v
Integration service identifies affected canonical asset
      |
      v
Graph traversal finds:
  Silver product -> Gold product -> semantic metric -> KPI -> reports / agents
      |
      v
Create impact event for technical owner, steward, metric owner, KPI owner
      |
      v
Validate/release changed metric or mark dependent product/KPI degraded
```

### 18.3 Bigeye incident flow

```text
Bigeye detects freshness / volume / schema / quality incident
      |
      v
Incident linked to observed asset and lineage path
      |
      v
Canonical graph receives incident reference and impact context
      |
      v
Graph identifies affected Gold product, semantic metric, KPI, reports
      |
      v
Consumer view shows quality state:
  Healthy | Warning | Degraded | Unavailable
      |
      v
KPI owner decides whether to suppress, annotate, restate, or continue KPI publication
```

### 18.4 Ontology/KPI definition change

```text
Approved business change proposal
      |
      v
Ontology/KPI Store version created with effective date
      |
      v
Impact analysis over mapped data products, semantic metrics, reports, and agents
      |
      v
Required semantic model and catalog mapping updates implemented
      |
      v
Validation and owner approval
      |
      v
New version published; older version retained/referenced as superseded
```

---

## 19. Pilot Design: Commercial Pricing Performance

### 19.1 Pilot objective

Demonstrate one complete governed trace from Downstream Commercial business semantics through the Medallion platform, semantic layer, catalog, lineage/quality evidence, and downstream consumption.

### 19.2 Pilot KPI

**KPI:** Rack Price Capture Rate %  
**Purpose:** Measure realized net rack price relative to the applicable approved market benchmark price for a defined commercial scope.  
**Status:** Candidate until business formula, scope, thresholds, ownership, and data feasibility are approved.

### 19.3 Pilot product and assets

```text
Business concepts
  Terminal | Product | Customer | Contract | CommercialTransaction | MarketPriceAssessment

Sources
  RightAngle CTRM / commercial transactions
  OPIS market data assessments

Medallion products
  Bronze: rightangle_transaction_raw; opis_assessment_raw
  Silver: commercial_transaction_conformed; market_price_assessment_conformed
  Gold: commercial_pricing_performance

Semantic service
  Commercial Performance Semantic Service

Consumer products
  KPI Store view; Power BI validation report; controlled AI analytical tool
```

### 19.4 Pilot success criteria

- A user can discover the Gold product in Purview and the data-product portal.
- The product is linked to approved/candidate ontology concepts with stable URIs.
- The Gold product has mapped Unity Catalog object, Purview GUID, and Bigeye lineage node(s).
- The semantic metric version is linked to the KPI and product.
- The lineage path to RightAngle and OPIS is represented using PROV-O and has evidence status.
- Quality/freshness evidence is visible at the appropriate consumer level.
- The graph can answer: “Which semantic metric, data product, source systems, owners, and quality controls support this KPI?”
- A SHACL gate blocks publication if the owner, steward, classification, contract, or lineage reference is missing.

---

## 20. Delivery Roadmap

### Phase 0 — Foundation

- Approve metadata principles and system-of-authority matrix.
- Define EPM namespace, stable URI policy, and identifier strategy.
- Define KPI/metric/data-product vocabulary and classification taxonomy.
- Establish the mapping-registry schema.
- Choose RDF/graph store and API serving approach.

### Phase 1 — Pilot

- Configure Unity Catalog to Purview discovery for selected Commercial catalogs.
- Define Purview business metadata schema and publication states.
- Create ontology-to-glossary mapping registry for core Commercial concepts.
- Implement Purview extractor, Bigeye lineage adapter, canonical mapper, and SHACL validator.
- Publish DCAT/PROV-O projection for Commercial Pricing Performance.
- Validate one KPI traceability chain.

### Phase 2 — Operationalization

- Add incremental extraction and reconciliation.
- Integrate semantic-layer metadata/API contract.
- Add data-quality/freshness status references and incident propagation.
- Deliver data-product portal and architecture/lineage views.
- Establish steward remediation workflow and metadata SLOs.

### Phase 3 — Scale

- Add Customer, Supply, Terminal Operations, Finance, and O2C data products.
- Expand certified KPI catalog and semantic services.
- Add Power BI consumption/report lineage validation.
- Provide policy-filtered agent context API.
- Publish approved DCAT profiles for federation/partner exchange where needed.

---

## 21. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Full catalog replication creates an unusable graph | Noise, cost, poor trust | Project only governed, reusable, or KPI-relevant assets first |
| Multiple systems claim ownership of same metadata | Drift and conflicting facts | System-of-authority matrix; field-level ownership; source-attributed assertions |
| Labels are used as integration keys | Broken mappings and false matches | Stable URIs, GUIDs, and platform IDs; mapping registry |
| Bigeye lineage is treated as business-approved truth | Unsupported KPI traceability | Evidence status and KPI validation gate |
| Gold layer is confused with certification | Untrustworthy consumer products | Separate Medallion role from certification status |
| DCAT is asked to enforce access | Security design failure | Keep enforcement in Unity Catalog/API/BI controls; use DCAT as policy reference |
| Agents receive excessive technical/sensitive metadata | Security and hallucination risk | Policy-filtered context service and approved semantic tools |
| Mapping maintenance is manual and ungoverned | Stale metadata | CI/CD, mapping versioning, reconciliation, steward queues |
| Vendor APIs are incomplete or change | Integration fragility | Adapter isolation, contract tests, retained source evidence, fallbacks |

---

## 22. Architecture Decisions

### ADR-001 — Selective Metadata Projection

**Decision:** Project selected catalog and platform metadata into a canonical knowledge graph; do not bulk-ingest all catalog items into the domain ontology.  
**Status:** Candidate.  
**Rationale:** Preserves operational authority, controls graph volume, and delivers useful cross-domain context.

### ADR-002 — DCAT as Interoperability Envelope

**Decision:** Use DCAT 3 for data products, datasets, distributions, and data services.  
**Status:** Candidate.  
**Rationale:** Supports portable catalog metadata without substituting for ontology, semantic modeling, or platform catalog operations.

### ADR-003 — PROV-O for Normalized Lineage

**Decision:** Use PROV-O with enterprise extensions for cross-platform provenance, including Bigeye evidence.  
**Status:** Candidate.  
**Rationale:** Supports source attribution, qualified derivation, activity/agent representation, and interoperability.

### ADR-004 — Unity Catalog → Purview → Canonical Projection

**Decision:** For Databricks assets, use the supported Unity Catalog-to-Purview discovery path as the primary source for enterprise technical catalog enrichment, then project from Purview to the canonical graph.  
**Status:** Candidate.  
**Rationale:** Avoids duplicate technical metadata pipelines and keeps Purview as enterprise governance enrichment point.

### ADR-005 — Bigeye as Evidence Source

**Decision:** Treat Bigeye lineage and observability metadata as source-attributed evidence, not automatic approved lineage.  
**Status:** Candidate.  
**Rationale:** Enables cross-platform lineage while retaining review and reconciliation controls.

---

## 23. Open Questions

1. Which product will host the canonical RDF graph: dedicated triplestore, graph database projection, catalog-adjacent graph service, or managed cloud knowledge graph?
2. What is the authoritative enterprise data-product lifecycle registry: Purview, KPI Store, dedicated product registry, or a governed graph workflow?
3. Which Purview capability model is available: Data Map/Atlas, Unified Catalog, or both?
4. Is Unity Catalog running in Azure Databricks, and which lineage/tags/metadata capabilities are enabled?
5. Which Bigeye Lineage Plus connectors and APIs are licensed and available?
6. Which semantic layer platform is in scope, and can it export machine-readable metric definitions, dependency metadata, and service contracts?
7. Which classifications and lineage details can be exposed to AI agents and broad internal discovery?
8. What freshness and synchronization SLAs are required for each metadata category?
9. How will identifier changes, renames, mergers, and source migrations be managed over time?
10. Which governance forum approves mappings, validated KPI lineage, and data-product certification?

---

## 24. Artifact Update Block

### Conclusions

- The target architecture is a federated, ontology-linked metadata knowledge graph.
- Purview, Unity Catalog, Bigeye, the semantic layer, KPI Store, and domain ontology remain distinct systems with explicit authority boundaries.
- DCAT is used for portable data-product/service publication; PROV-O normalizes provenance and evidence; SHACL validates publication quality.
- Bigeye is integrated as a cross-platform lineage and observability evidence source.
- Downstream consumers receive policy-filtered views rather than unrestricted access to a raw enterprise graph.

### Decisions and status

- Architecture is **Draft / Candidate** pending platform capability validation and pilot outcomes.
- Recommended initial pattern: `Unity Catalog → Purview → Metadata Integration Service → DCAT/PROV-O Knowledge Graph`.
- Recommended pilot: Commercial Pricing Performance and Rack Price Capture Rate %.

### Definitions added or changed

- **Canonical metadata graph:** An integrated, versioned graph of selected metadata instances linked to ontology concepts.
- **DCAT projection:** The portable catalog/data-product/service representation emitted from canonical metadata.
- **Observed lineage assertion:** A source-attributed lineage statement not yet approved for KPI traceability.
- **Validated KPI lineage:** An approved, evidence-backed KPI traceability chain.

### Assumptions

- Purview can harvest selected Unity Catalog metadata.
- Bigeye APIs/exports provide usable lineage identifiers and observation context.
- A controlled graph store and identity/mapping registry can be operated.
- Data product, KPI, and semantic metric governance roles will be assigned.

### Source evidence

- W3C DCAT 3: catalog interoperability for datasets and data services.
- W3C PROV-O: interoperable provenance representation.
- Microsoft Purview/Unity Catalog integration guidance: Unity Catalog technical metadata is ingested into Purview through a scan-based, one-way pattern.
- Bigeye lineage documentation: lineage API and Lineage Plus provide table/column-level lineage capabilities, subject to enabled connectors.

### Artifacts to create or update

- Enterprise Metadata Knowledge Graph Reference Architecture.
- Enterprise DCAT Application Profile.
- PROV-O / Bigeye Mapping Specification.
- Purview-to-Canonical Metadata Mapping Specification.
- Unity Catalog-to-Purview Scan and Enrichment Runbook.
- Ontology/Glossary Mapping Registry Design.
- Metadata Integration Service Technical Design.
- Certified Data Product SHACL Shapes.
- KPI Store Technical Design.
- System Integration Reference Architecture.
- Architecture Decision Log and Delivery Backlog.

### Suggested version/status changes

- EPM-ARCH-META-001 v0.1: **Draft**.
- ADR-001 through ADR-005: **Candidate**.
- Commercial Pricing Performance pilot: **Candidate proof of value**.
- Enterprise DCAT Application Profile v0.1: **Draft**.
