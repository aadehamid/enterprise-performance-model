# Enterprise KPI Store & Semantic Governance Architecture

## Master System Specification, Metadata Lifecycle & Data Contract Design

> **Status: working draft. The foundation files and Turtle SoT are authoritative until I-11 closes.**
>
> This file is a working draft under reconciliation. The foundation
> files (`EPM-FOUND-003`, `EPM-FOUND-004`, `EPM-FOUND-000`,
> `EPM-FOUND-002`, `EPM-FOUND-005`, `EPM-FOUND-006`, ADR-HL-021) and
> the Turtle SoT (`ontology/stage2_enterprise_kpi_ontology.ttl`) are
> authoritative. This file does not override them; conflicts are open
> items, not resolved positions. Inline `> ⚠️ I-11 conflict:`
> callouts mark specific lines where this draft diverges from the
> foundation; each callout cites the current seat.
>
> Tracked as Open Issue I-11 in `EPM-FOUND-000` and GitHub issue #18.

---

## 1. Executive Summary & Core Objectives

The enterprise is establishing a centralized **KPI Store** hosted on the **Databricks Lakehouse Platform** to serve as the single, authoritative source of truth for all enterprise key performance indicators (KPIs).

This architecture resolves a fundamental enterprise problem: client-side reporting solutions (e.g., Power BI), operational microservices, and AI query engines defining competing, divergent calculation logic for the exact same business metrics.

### Guiding Principles

- **Strict Decoupling of Meaning from Computation:** The conceptual identity, business definition, and operational context of a metric (**Meaning Plane**) are decoupled from the physical calculation engine, SQL pipelines, and storage tables (**Compute Plane**).
- **The 1:1 Governance Gate:** General domain concepts (e.g., `Customer`, `Refinery`, `Crude Barrel`) describe entities, not computable values. Only an unambiguous, measurable business indicator (e.g., `Crack Spread`, `Gross Refining Margin`) can pass the 1:1 governance gate to become a **Named KPI** and receive a permanent **Ontology IRI**.
- **Contract-Driven Delivery via ODPS:** Every gold-tier KPI dataset and semantic view is packaged as a formal **Data Product** governed by the **Open Data Product Specification (ODPS)**. The data contract defines semantic linkage, operational SLAs/SLOs, allowed vs. prohibited consumption contexts, and data quality thresholds.
- **Abstract Formula Pointers Over Hardcoded SQL:** Catalogs and data contracts never hardcode physical SQL or DAX strings. Instead, they store abstract, version-controlled **Formula Pointers** directing execution engines to certified measure objects inside a centralized **Semantic Layer**.
- **Controlled AI Agent Interaction:** AI agents (external and in-platform) are prevented from writing custom calculation logic or running unrestricted table scans over Silver or Gold datasets. Agents query the **Graph of Meaning** to locate the metric, resolve its **Catalog Record** and **Formula Pointer**, and submit the certified measure to the compiler engine. The compiled query serves as the immutable audit trail.
- **Single-Source-of-Truth Metadata Propagation:** Metadata is captured once at its natural point of origin (authoritative source) and propagated downstream across the architecture **by reference** (via URIs, IRIs, and foreign identifiers) rather than through manual copy-pasting.

---

## 2. End-to-End System Architecture

```text
========================================================================================================================
PLANE 1: MEANING (Semantic & Conceptual Governance - Zero Computation Here)
========================================================================================================================
[ Domain Understanding ] ────── formalize ─────▶ [ Ontology Modules ] ───────▶ [ Graph of Meaning ]
  (ER/Studio CDM & LDM;                            (Turtle in Git;               (Turtle in Git;
   Ubiquitous Language)                             Shared meaning & lineage)     Global Enterprise Graph)
          │                                                │                                ▲
          │ About this object                              ▼ Creates this named KPI         │ which KPI
          ▼                                         [ Named KPI ] ──────────────────────────┤
[ Process Architecture ] ──────── Used in ────────▶   (e.g., Crack Spread;                  │
  (Value Streams, Workflows,                           Has unique Ontology IRI;             │
   Business Processes; Turtle in Git)                  1:1 Governance Gate)                 │
          │                                                │                                │
===========================================================│================================│===========================
PLANE 2: COMPUTE (Execution, Preparation, Storage, Contracts & Observability)               │
===========================================================│================================│===========================
  PREPARE (Ingredients & Catalog)                          │                                │
  ┌───────────────────────────────────────────────────┐    │                                │
  │ [ Candidate KPI Register ]                        │    │                                │
  │   - Staging backlog (not warehouse table)         │    │                                │
  │   - Validates uniqueness before approval          │    │                                │
  │   - Process provides explanatory context          │    │                                │
  │                         │                         │    │                                │
  │                         ▼ promote via steward     │    │                                │
  │ [ Cataloging Tool (Purview / Unity Catalog) ] ────┼────┘ (Ontology IRI)                 │
  │   - Certified row: Name, Owner, Formula           │                                     │
  │     Pointer, Used In, Ontology IRI                │                                     │
  │   - 1:1 binding to Named KPI                      │                                     │
  │                         │                         │                                     │
  │                         ▼ one-way copy            │ Formula Pointer                     │
  │ [ Silver Layer (Databricks) ]                     │ (Lookup)                            │
  │   - Star schema: facts & dimensions (Ingredients) │                                     │
  │   - Read-only local copy of KPI metadata table    │                                     │
  │   - Governed by: Upstream Ingestion Contract      │                                     │

> ⚠️ **I-11 conflict:** Diagram presents the Purview/Unity Catalog "Certified row" as the 1:1 binding to a Named KPI. Current seat: `dim_kpi_metadata` owns identity, approval, status, and the formula pointer; Purview/UC are discover/govern tools over pointed-at assets, not the Store row. Tracked in GH #18.
  └─────────────────────────┬─────────────────────────┘                                     │
                            │ Ingredients                                                   │
                            ▼                                                               │
  COMPILE (Where the KPI is Compiled)                                                       │
  ┌───────────────────────────────────────────────────────────────────────────────────┐     │
  │ [ Semantic Layer (Metric Views / dbt MetricFlow / Cube / Power BI Model) ]        │     │
  │   - Certified measure object: Pointed to by catalog row                           │     │
  │   - Named object + measure name (Not raw SQL, not Gold, not Ontology IRI)         │     │
  │                                         │                                         │     │
  │                                         ▼ compiler runs this                      │     │
  │ [ Compiler Engine ] ──────────────────────────────────────────────────────────────┼─────┤
  │   - Compiles certified semantic object against Silver ingredients                 │     │
  │   - Materializes Gold cuts; computes dynamic ad-hoc slices                        │     │
  └─────────────────────────┬─────────────────────────────────────────────────────────┘     │
                            │ Published snapshot                                            │
                            ▼                                                               │
  CONSUME (Contracts, Observability & Consumers)                                            │
  ┌───────────────────────────────────────────────────────────────────────────────────┐     │
  │ [ Gold Layer (Databricks) ]                                                       │     │
  │   - Materialized cuts at agreed grains (No secondary client SUMs)                 │     │
  │                         │                                                         │     │
  │                         ▼ wrapped by                                              │     │
  │ ┌───────────────────────────────────────────────────────────────────────────────┐ │     │
  │ │               THE DOWNSTREAM DATA CONTRACT (ODPS / Data Product)              │ │     │
  │ ├───────────────────────────────────────────────────────────────────────────────┤ │     │
  │ │ - Semantic Linkage: Certified Ontology IRI from Meaning Plane                  │ │     │
  │ │ - Physical Output Ports: SQL Warehouse Endpoint, REST API, Semantic Views     │ │     │
  │ │ - SLA / SLO Commitments: Freshness, Latency, Grain guarantees                  │ │     │
  │ │ - Observability Rules: BigEye Quality Assertions & Anomaly Thresholds         │ │     │
  │ │ - Governance & Scope: Certified vs. Non-Certified Uses, Excluded Data          │ │     │
  │ │ - Ownership: Four-Tier Ownership Matrix                                       │ │     │
  │ └───────────────────────────────────────┬───────────────────────────────────────┘ │     │
  │                                         │                                         │     │
  │          ┌──────────────────────────────┴──────────────────────────────┐          │     │
  │          ▼                                                             ▼          │     │
  │ [ Consuming Applications & BI ]                              [ AI Agents ]        │     │
  │   - Power BI / Operational Apps                                - External Agent   │◀────┘
  │   - DirectQuery / SQL Access via Ports                         - In-Platform Agent│
  │                                                                - Submits certified│
  │                                                                  measure to       │
  │                                                                  Compiler only    │
  └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Metadata Lifecycle & Flow: Domain Analysis to Consumption

Metadata moves through a structured, multi-stage lifecycle. Each stage has a single Authoritative Source (System of Record). Downstream stages ingest or reference that metadata without redefining it.

```text
[ STAGE 1: DOMAIN ANALYSIS & MEANING ]
  Authoritative Source: ER/Studio (CDM/LDM) & Git Ontologies (Turtle)
  Metadata Collected: Business Terms, Taxonomies, Domain Context, Process Hierarchies, Named KPI IRIs.
           │
           ▼ (Reference via Ontology IRI)
[ STAGE 2: CANDIDATE REGISTRATION & CERTIFICATION ]
  Authoritative Source: Microsoft Purview / Databricks Unity Catalog
  Metadata Collected: Stewardship assignments, Lifecycle status (Proposed -> Certified), Formula Pointers.

> ⚠️ **I-11 conflict:** Stage 2 names Purview/Unity Catalog as the Authoritative Source for certification and lifecycle status. Current seat: `dim_kpi_metadata` is the KPI Store seat (identity, approval, status, formula pointer); Purview/UC discover/govern pointed-at assets. Current status set is `proposed | approved | drifted | archived` per `EPM-FOUND-000` §Meaning vs compute and ADR-HL-021, not `Proposed -> Certified`. Tracked in GH #18.
           │
           ▼ (Reference via Catalog ID & Sync Engine)
[ STAGE 3: DATA ASSET & INGREDIENT MODELING ]
  Authoritative Source: ER/Studio (PDM) & Databricks Silver Star Schema
  Metadata Collected: Table schemas, Column types, Grain keys, Foreign Keys, Dimensional hierarchies.
           │
           ▼ (Reference via Measure Object Name)
[ STAGE 4: METRIC COMPILATION & SEMANTIC MODELING ]
  Authoritative Source: Semantic Layer (Metric Views / dbt MetricFlow / Cube / Power BI)
  Metadata Collected: Aggregation functions, Dimensions available, Joins, Compile-time parameters.
           │
           ▼ (Aggregated Manifest via ODPS YAML/JSON)
[ STAGE 5: PRODUCTIZATION & CONTRACT DEFINITION ]
  Authoritative Source: Data Contract Manifest (ODPS)
  Metadata Collected: Output ports, Latency/Freshness SLAs, BigEye test assertions, Certified/Non-Certified uses.
           │
           ▼ (Operational Metric Validation)
[ STAGE 6: OBSERVABILITY & CONSUMPTION ]
  Authoritative Source: BigEye Observability Platform & Consuming Clients / Agents
  Metadata Collected: Quality run metrics, Test execution state, Consumer queries, Audit traces.
```

---

## 4. Metadata Mapping Matrix: Where It Lives vs. Where It Is Shared

This matrix establishes the definitive boundaries between where metadata originates and how other architectural components consume it.

| Metadata Category | Specific Metadata Attributes | Authoritative Source (System of Record) | Consumed By / Shared With | Sharing Mechanism (Protocol / Pattern) |
| --- | --- | --- | --- | --- |
| Domain & Concept | Domain Name, Domain Description, Ubiquitous Language definitions | ER/Studio (CDM) & Meaning Plane (Git) | Purview Catalog, ODPS Contract, External AI Agents | By Reference: linked via canonical `skos:Concept` or Domain URI (`ex:domain/Refining`). |

> ⚠️ **I-11 conflict:** Row uses a generic `ex:domain/Refining` example prefix. Current convention: domain identity routes through the human-readable semantic model (`EPM-FOUND-003`) and any formal URI is declared in the Turtle SoT (`ontology/stage2_enterprise_kpi_ontology.ttl`, prefixes `ekpi:` and `data:` only). `ex:` is illustrative here, not authoritative. Tracked in GH #18.
| Business Process | Value stream name, Process Step ID, Explanatory context | Meaning Plane (Git / RDF) | Candidate KPI Register, Purview Catalog, ODPS Contract | By Reference: linked via `dcterms:subject` or `ex:process/FluidCatalyticCracking`. Not used as a SQL join key. |

> ⚠️ **I-11 conflict:** Row names the Meaning Plane (Git / RDF) as the Authoritative Source for business process identity. Current seat: process authority is `business_architecture/business_process/` + `business_architecture/schema/` per `EPM-FOUND-000` §Process authority. Turtle may link process IDs but is not process SoT. Tracked in GH #18.
| Named KPI Identity | KPI Business Name, Certified Definition, 1:1 Gate status | Graph of Meaning (Git / RDF) | Purview Catalog, Silver KPI Metadata Table, ODPS Contract | By Reference: permanent URI / Ontology IRI (`ex:kpi/CrackSpread321`). |

> ⚠️ **I-11 conflict:** Row presents the Graph of Meaning as the Authoritative Source for "1:1 Gate status." Current seat: the only legal join is ontology IRI → `dim_kpi_metadata` row → Metric View compiled with `MEASURE()`; the Store row owns the gate. The Silver KPI Metadata Table is a read-only local copy used for joins, not the seat. Tracked in GH #18.
| Governance & Roles | Domain Data Owner, Product Owner, Data Steward, Technical Owner | Microsoft Purview / Unity Catalog | Candidate Register, Silver Metadata, ODPS Contract | By Identity URI / Email: synchronized into contract headers and graph agents (`foaf:Person`, `prov:wasAttributedTo`). |
| Physical Schema & Grain | Column names, Data types, Primary/Foreign keys, Grain/Dimensionality | ER/Studio (PDM) & Databricks Silver | Semantic Layer, BigEye, ODPS Contract | By Value & Schema Reference: PDM generates DDL; contract embeds schema specification directly; grain links to dimension keys. |
| Metric Logic & Math | Measure calculation object, Aggregation rules, Filter constraints | Semantic Layer (Metric Views / dbt / Cube) | Purview Catalog, Silver Metadata, ODPS Contract | By Formula Pointer: stored strictly as an abstract identifier (e.g., `metric_view_refining.crack_spread_321`). Never raw SQL/DAX. |
| Physical Endpoints | SQL Warehouse JDBC/ODBC, REST APIs, Semantic Model connections | Databricks Platform / Unity Catalog | ODPS Contract, Consuming Applications, BI Tools | By Value (Output Ports): ODPS manifest declares explicit connection strings (`dcat:endpointURL` / `dcat:accessURL`). |
| SLAs & Operational SLOs | Refresh schedule, Freshness window, Query latency, Availability rate | Databricks Orchestration & SRE Engine | ODPS Contract, BigEye Observability, BI Teams | By Value (Contract SLA): declared in ODPS YAML using ISO 8601 durations (`odps:freshnessTarget "PT6H"`). |
| Data Quality Assertions | Range bounds, Nullability thresholds, Anomaly bounds, Completeness % | BigEye Observability Engine | Databricks Pipelines, ODPS Contract, AI Agents | Bi-Directional API: declarative rules authored in ODPS contract; BigEye pulls rules via API, runs tests, and emits execution metrics. |
| Usage Boundaries | Certified Business Use Cases, Prohibited / Non-Certified Use Cases | Enterprise Data Governance Board | ODPS Contract, AI Agents, BI Dashboards | By Value (Contract Policy): textual rules enforced by AI agent system prompts and catalog validation flags. |
| Audit & Traceability | Upstream tables used, Pipeline Run IDs, Execution Timestamps, SQL executed | Databricks Execution Engine & Compiler | Enterprise Knowledge Graph, BigEye, Compliance Logs | Automated Generation: captured during runtime via PROV-O (`prov:wasGeneratedBy`, `prov:used`). |

---

## 5. The Four-Tier Ownership Matrix

To ensure clear operational accountability and eliminate bottlenecks during KPI promotion, the architecture institutes a four-tier ownership model across both the Meaning Plane and the Compute Plane.

```text
+──────────────────────────+───────────────────────────────────────────────────────────+
| Tier 1: Domain Data Owner| - Business Executive / Domain VP                          |
| (Strategic Authority)    | - Accountability: Business glossary, domain boundaries,   |
|                          |   approves Candidate KPI concepts and Certified Uses.     |
+──────────────────────────+───────────────────────────────────────────────────────────+
             │
             ▼
+──────────────────────────+───────────────────────────────────────────────────────────+
| Tier 2: Data Product     | - Lead Business Analyst / Metric Product Manager          |
|         Owner            | - Accountability: Lifecycle of the KPI Data Product,      |
| (Product Lifecycle)      |   authoring the ODPS Contract, setting SLAs and SLOs.     |
+──────────────────────────+───────────────────────────────────────────────────────────+
             │
             ▼
+──────────────────────────+───────────────────────────────────────────────────────────+
| Tier 3: Data Steward     | - Senior Data Governance Specialist / Subject Expert      |
| (Semantic Governance)    | - Accountability: 1:1 Gate verification, certifying the   |
|                          |   Ontology IRI, mapping ER/Studio models, Purview setup. |
+──────────────────────────+───────────────────────────────────────────────────────────+
             │
             ▼
+──────────────────────────+───────────────────────────────────────────────────────────+
| Tier 4: Technical Owner  | - Databricks Platform Engineer / Analytics Engineer       |
| (Compute & Pipeline)     | - Accountability: Silver star schema ETL, Semantic Layer  |
|                          |   compiler configuration, BigEye monitoring setup.       |
+──────────────────────────+───────────────────────────────────────────────────────────+
```

### Operational Roles in the Promotion Workflow

1. **Candidate Ingestion:** The Data Product Owner enters a new metric into the Candidate KPI Register, associating it with a proposed name and business process context.
2. **Semantic Verification:** The Data Steward vets the candidate against the Graph of Meaning. If unique, the Steward assigns a permanent Ontology IRI and secures approval from the Domain Data Owner.
3. **Physical Delivery:** The Technical Owner maps the Silver star schema ingredients (from ER/Studio PDM), builds the measure in the Semantic Layer, and defines the Formula Pointer.
4. **Contract Sign-Off:** The Data Product Owner and Technical Owner execute the Data Contract (ODPS), which registers the certified row in Microsoft Purview and schedules automated BigEye monitors.

---

## 6. Change Management & Schema Governance

Because multiple downstream applications and autonomous AI agents rely on the KPI Store, breaking changes must be prevented. The architecture enforces Semantic Versioning (MAJOR.MINOR.PATCH) across all metadata and data contracts.

```text
       [ Change Proposed in System of Record ]
                         │
                         ▼
        Is the change backwards-compatible?
        ├── YES (Field added, SLA improved, non-breaking logic adjustment)
        │     └── Apply MINOR or PATCH update.
        │         - Contract version increments (e.g., 2.1.0 -> 2.2.0).
        │         - BigEye thresholds and Purview catalog updated automatically.
        │         - No downstream consumer code changes required.
        │
        └── NO (Breaking Change)
              - Column deleted or renamed in Silver/Gold.
              - Underlying aggregation math or business logic fundamentally altered.
              - Grain altered (e.g., Daily aggregated to Monthly).
              - Deprecation of a certified output port.
                         │
                         ▼
              [ BREAKING CHANGE GOVERNANCE PROCESS ]
              1. Increment MAJOR contract version (e.g., 2.2.0 -> 3.0.0).
              2. Data Steward triggers architectural review with Domain Data Owner.
              3. Publish deprecation schedule via Purview (minimum 90-day grace).
              4. Maintain parallel Semantic Layer measure objects:
                 - metric_view_refining.crack_spread_v2 (Legacy)
                 - metric_view_refining.crack_spread_v3 (New)
              5. Deprecate legacy version once consumer migration is validated.
```

---

## 7. The Architectural Mechanism: How Metadata Is Shared

To eliminate manual configuration and prevent metadata drift, the architecture uses automated, decoupled sharing mechanisms.

```text
                                  METADATA SHARING TOPOLOGY

     [ Meaning Plane: Git ]           [ ER/Studio ]          [ Microsoft Purview ]
      (Ontology IRIs/Turtle)            (PDM Models)          (Certified Catalog)
                │                            │                          │
                │ Webhook                    │ Model Export             │ REST API
                ▼                            ▼                          ▼
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │               AUTOMATED METADATA COMPILER & INGESTION PIPELINE               │
   │      - Merges semantic IRIs, physical schemas, and catalog properties        │
   │      - Validates syntax and constraint completeness                          │
   └──────────────────────────────────────┬───────────────────────────────────────┘
                                          │
                                          ▼ Generates Declarative Contract
                           ┌──────────────────────────────┐
                           │   DATA CONTRACT (ODPS YAML)  │
                           │     Managed in Git Repo      │
                           └──────────────┬───────────────┘
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
   [ BigEye Observability Platform ]         [ Databricks Unity Catalog / Silver ]
   - Imports quality rules via API           - Syncs read-only Silver metadata table
   - Instantiates automated tests            - Configures Semantic Layer pointers
   - Emits health scores back to catalog     - Exposes Gold Output Ports to consumers
```

- **Meaning Plane to Catalog:** Git webhooks detect changes in RDF Turtle files, compiling new Named KPI IRIs and pushing them to Microsoft Purview as certified conceptual assets.
- **Catalog to Silver Metadata Table:** A scheduled, automated Databricks pipeline issues a read-only one-way sync from Purview into the Silver KPI Metadata Table. This ensures queries running inside Databricks can perform fast local joins against catalog metadata without external API round-trips.
- **Data Contract to BigEye (Observability as Code):** The Data Contract (ODPS YAML) is parsed by CI/CD deployment jobs. The quality section is compiled into API payloads sent to BigEye, automatically creating or updating monitoring metrics, freshness expectations, and anomaly detection rules.
- **Contract to Consuming AI Agents:** External agents send read requests to the contract API or Graph of Meaning. The agent parses the machine-readable contract to determine whether its intended analytical goal falls under Certified Uses before generating query executions.

---

## 8. Complete Concrete Data Contract Example (ODPS YAML)

Below is an enterprise-grade, production-ready Data Contract descriptor illustrating the Crack Spread KPI Data Product, incorporating all nine dimensions of the unified metadata framework.

```yaml
dataProductSpecificationVersion: "2.1.0"

# ==============================================================================
# 1. OVERVIEW
# ==============================================================================
info:
  id: "urn:dataproduct:refining:crack-spread-321"
  name: "Refinery 3:2:1 Crack Spread Margin"
  version: "2.1.0"
  status: "active"
  domain: "Downstream Refining & Trading"
  domainIRI: "https://metadata.enterprise.org/domains/Refining"

> ⚠️ **I-11 conflict:** `domainIRI` uses a host (`metadata.enterprise.org`) and path not declared in the Turtle SoT. Current Turtle SoT prefixes: `ekpi:` (`https://ontology.enterprise.example.com/kpi-store/core#`) and `data:` (`https://data.enterprise.example.com/kpi-store/`) only. This IRI is illustrative. Tracked in GH #18.
  purpose: >
    Provide an uncompromised, certified economic margin calculation representing
    the gross theoretical refining margin achieved by converting three barrels of
    crude oil into two barrels of gasoline and one barrel of distillate fuel.
  businessProblemSolved: >
    Eliminates competing crack spread calculations across regional trading desks,
    refinery operations dashboards, and corporate financial performance reviews.

# ==============================================================================
# 2. DETAILS (GRAIN, SLAS & CLASSIFICATION)
# ==============================================================================
details:
  grain: "Refinery Facility + Pricing Hub + Settlement Date"
  physicalKey: ["facility_id", "hub_code", "pricing_date"]
  refreshFrequency: "Daily by 04:00 UTC"
  expectedLatency: "15 minutes from raw pricing feed ingestion"
  availabilitySLA: "99.9% availability across business planning windows"
  dataClassification: "Confidential - Commercial Operational Data"

# ==============================================================================
# 3. WHAT'S IN THE DATA PRODUCT (SEMANTICS, FORMULA POINTER & EXCLUSIONS)
# ==============================================================================
productDefinition:
  keyBusinessDefinition: >
    The theoretical gross dollar margin per barrel produced by cracking 3 barrels
    of reference crude into 2 barrels of finished gasoline and 1 barrel of ultra-low
    sulfur diesel (ULSD).

  # Strict 1:1 Gate Linking to Meaning Plane
  ontologyIRI: "https://metadata.enterprise.org/kpis/CrackSpread321"

> ⚠️ **I-11 conflict:** `ontologyIRI` uses a host and path not declared in the Turtle SoT. Current Turtle SoT prefixes: `ekpi:` and `data:` only, on `ontology.enterprise.example.com` / `data.enterprise.example.com`. This IRI is illustrative. Tracked in GH #18.

  # Centralized Semantic Layer Formula Pointer (Never raw SQL)
  calculationModel:
    semanticLayerType: "Databricks Metric View"
    formulaPointer: "refining_semantic_catalog.refining_metrics.crack_spread_321"
    underlyingFormulaNotation: "((2 * Gasoline_Price) + (1 * Diesel_Price) - (3 * Crude_Price)) / 3"

  # Physical Schema Specification (Silver/Gold Interface)
  includedData:
    - name: "facility_id"
      type: "string"
      description: "Identifier for the operational refinery facility"
      isPrimaryKey: true
    - name: "hub_code"
      type: "string"
      description: "Regional pricing hub benchmark (e.g., US_GULF_COAST, ROTTERDAM)"
      isPrimaryKey: true
    - name: "pricing_date"
      type: "date"
      description: "Market settlement date"
      isPrimaryKey: true
    - name: "crack_spread_per_bbl"
      type: "decimal(10,4)"
      description: "Calculated certified 3:2:1 crack spread margin in USD per barrel"
      mapsToConcept: "https://metadata.enterprise.org/concepts/DollarPerBarrel"

> ⚠️ **I-11 conflict:** `mapsToConcept` uses a host and path not declared in the Turtle SoT. Current Turtle SoT prefixes: `ekpi:` and `data:` only. This IRI is illustrative. Tracked in GH #18.
    - name: "calculation_timestamp"
      type: "timestamp"
      description: "System execution timestamp emitted by the compiler"

  excludedData:
    - "Transportation freight differentials and regional pipeline tariffs"
    - "Secondary refinery chemical processing and catalyst operating costs"
    - "Refinery energy utility overhead (natural gas, grid electricity)"
    - "Corporate tax incentives and carbon compliance allowances"

# ==============================================================================
# 4. QUALITY & TRUST (BIGEYE OBSERVABILITY BRIDGE)
# ==============================================================================
qualityAndTrust:
  observabilityPlatform: "BigEye"
  testSuiteIdentifier: "bigeye_suite_refining_crack_spread_gold"

  rules:
    - field: "facility_id"
      assertion: "not_null"
    - field: "hub_code"
      assertion: "values_in_set"
      parameters: ["US_GULF_COAST", "US_MIDCONTINENT", "NEW_YORK_HARBOR", "ROTTERDAM"]
    - field: "crack_spread_per_bbl"
      assertion: "expected_range"
      parameters:
        min: -15.00
        max: 85.00
        actionOnBreach: "quarantine_and_alert"

  thresholds:
    completeness: ">= 99.5%"
    timeliness: ">= 98.0% of snapshots published within SLA window"
    consistencyWithIngredients: ">= 99.9% reconciliation against Silver pricing facts"
    duplicateRate: "0.0% (Zero duplicate key tolerances)"

# ==============================================================================
# 5. USE & CONSUMPTION (GUARDRAILS & PERMITTED SCOPE)
# ==============================================================================
useAndConsumption:
  primaryConsumers:
    - "Downstream Commercial Trading Desk"
    - "Refinery Operations Planning Systems"
    - "Corporate Executive Performance Management"
    - "Autonomous Market Analysis AI Agents"

  certifiedUses:
    - "Refinery economic optimization and crude run scheduling"
    - "Daily operational commercial performance tracking"
    - "Commercial trading margin benchmarking"
    - "Input to corporate financial planning models"

  nonCertifiedUses:
    - "Statutory audited financial reporting without reconciliation adjustments"
    - "Direct real-time algorithmic trade execution without human risk review"
    - "Taxation filing and asset depreciation schedules"

# ==============================================================================
# 6. OWNERSHIP & ROLES (FOUR-TIER MATRIX)
# ==============================================================================
ownership:
  domainDataOwner:
    name: "EVP Downstream Manufacturing & Trading"
    role: "Domain Executive"
    accountableEntity: "Downstream Commercial Operations Committee"

  dataProductOwner:
    name: "Sarah Jenkins"
    title: "Lead Commercial Analytics Product Manager"
    email: "sarah.jenkins@enterprise.org"

  dataSteward:
    name: "Marcus Vance"
    title: "Enterprise Refining Data Steward"
    email: "marcus.vance@enterprise.org"
    purviewStewardID: "usr-steward-refining-042"

  technicalOwner:
    name: "Data Platform Engineering Team"
    lead: "Alex Rostova"
    email: "dataplatform-refining@enterprise.org"

# ==============================================================================
# 7. DATA FLOW & INTEGRATION (PORTS & LINEAGE)
# ==============================================================================
dataFlowAndIntegration:
  upstreamLineage:
    sourceSystems:
      - "Operational Data Store: SAP ERP Plant Production Modules"
      - "Market Pricing Feeds: S&P Global Platts / Argus Media"
    rawLayer: "databricks_raw.market_pricing.settlements"
    silverIngredients:
      facts: "databricks_silver.fct_market_settlement_daily"
      dimensions:
        - "databricks_silver.dim_refinery_facility"
        - "databricks_silver.dim_pricing_hub"

  outputPorts:
    - id: "port-databricks-sql-warehouse"
      name: "Databricks Gold Serverless SQL Warehouse"
      type: "SQL/JDBC"
      endpointURL: "jdbc:spark://corp.cloud.databricks.com:443/default;transportMode=http;ssl=1;AuthMech=3;httpPath=/sql/1.0/endpoints/refining_gold_wh"
      databaseTable: "databricks_gold.refining_kpis.kpi_crack_spread_321_daily"

    - id: "port-powerbi-directlake"
      name: "Power BI Certified Direct Lake Endpoint"
      type: "PowerBI_SemanticModel"
      endpointURL: "powerbi://api.powerbi.com/v1.0/myorg/Downstream_Operations;dataset=CrackSpread_Certified_v2"

    - id: "port-rest-api"
      name: "Enterprise Data Fabric REST API"
      type: "REST"
      endpointURL: "https://api.enterprise.org/v2/refining/kpi/crack-spread"
      specificationFormat: "OpenAPI 3.1"

# ==============================================================================
# 8. OPERATIONS & SUPPORT
# ==============================================================================
operationsAndSupport:
  supportIntakeModel: "ServiceNow Queue: DATA-PLATFORM-REFINING"
  incidentEscalation:
    slaBreachWebhook: "https://alerts.enterprise.org/hooks/refining-data-sla"
    pagingThreshold: "Critical alert if Gold snapshot delayed > 60 minutes beyond SLA"

  changeManagement:
    policy: "Semantic Versioning (SemVer 2.0). Minimum 90-day deprecation for breaking changes."
    changeReviewBoard: "Refining Architecture Review Guild"

# ==============================================================================
# 9. SUCCESS METRICS
# ==============================================================================
successMetrics:
  - metric: "Consuming Report Consistency"
    target: "100% of internal reports consume this certified measure instead of custom formulas"
  - metric: "Reconciliation Defect Reduction"
    target: ">= 90% drop in month-end variance discrepancies between Trading and Accounting"
  - metric: "Query Response Performance"
    target: "95th percentile query latency < 1.5 seconds across all output ports"
```

---

## 9. Consumption Patterns: Autonomous AI Agents

To ensure strict governance and prevent metric corruption, autonomous AI agents (such as LangChain workflows, Semantic Kernel agents, or platform copilots) must interact with the KPI Store following an auditable sequence.

```text
               AI AGENT AUDITED ACCESS PATTERN

   [ AI Agent receives user prompt ]
                   │
                   ▼
   Step 1: QUERY MEANING FIRST
   - Agent queries Graph of Meaning (SPARQL/Turtle).
   - Discovers the certified Named KPI ("Crack Spread 3:2:1").
   - Verifies that the user prompt falls under Certified Uses.

> ⚠️ **I-11 conflict:** Step 1 says agents query the Graph of Meaning via SPARQL/Turtle. Current serve path: Neo4j/Cypher is the enterprise expose path; Fuseki/SPARQL is lab-only per ADR-HL-021. Tracked in GH #18.
                   │
                   ▼
   Step 2: RESOLVE CATALOG & CONTRACT
   - Agent reads Purview Catalog / ODPS Contract.
   - Resolves the Formula Pointer:
     refining_semantic_catalog.refining_metrics.crack_spread_321
   - Locates the approved Output Port.
                   │
                   ▼
   Step 3: SUBMIT TO COMPILER
   - Agent sends measure request to the Compiler:
     COMPILE MEASURE crack_spread_321 FOR facility='Refinery_A' AND date='2026-09-01'
   - Agent DOES NOT generate SQL or DAX calculation math.
                   │
                   ▼
   Step 4: COMPILER EXECUTES & AUDITS
   - Compiler validates permissions against Unity Catalog.
   - Compiler generates optimized SQL over Silver ingredients or reads Gold.
   - Emits compiled SQL into query execution logs as an immutable audit record.
   - Returns certified value to the AI Agent.
```

By enforcing this four-step sequence, the enterprise guarantees that whether a metric is queried by an executive dashboard, an ad-hoc analyst, or an autonomous LLM agent, the resulting calculation is certified, auditable, and identical across every interface.
