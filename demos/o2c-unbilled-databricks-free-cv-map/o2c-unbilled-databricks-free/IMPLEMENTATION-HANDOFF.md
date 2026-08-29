# Customer/O2C Role-Aware Unbilled Reference Implementation — Implementation Handoff

**Artifact ID:** EPM-RI-CUST-O2C-UNBILLED-001  
**Version:** 0.1  
**Status:** Draft  
**Owner:** Enterprise Performance Model initiative  
**Last updated:** 2026-08-29  
**Workstream:** KPI Store and Enterprise Performance Management, with Domain Modeling, System Integration, and Data Governance dependencies  
**Target artifact:** Customer/O2C runnable reference implementation  
**Objective:** Build and validate an end-to-end, synthetic-data implementation that demonstrates role-aware Customer/O2C traceability, governed unbilled-exposure measurement, and evidence-backed investigation.

## 1. Purpose and relationship

This document is the detailed execution specification for the Customer/O2C role-aware unbilled reference implementation.

It must be used with:

- [`README.md`](README.md) for navigation, scope, operating rules, and quick orientation.
- [`THE-PROBLEM.md`](THE-PROBLEM.md) for the business problem the implementation proves.
- [`../../../business_architecture/business_process/`](../../../business_architecture/business_process/) and [`../../../business_architecture/schema/`](../../../business_architecture/schema/) for process authority (order-to-cash included).
- [`../../../business_architecture/domain/customer_domain_problem_statement_v0.1.md`](../../../business_architecture/domain/customer_domain_problem_statement_v0.1.md) for Customer-domain context. Draft. Not process authority.
- [`../../../EPM_Homelab/`](../../../EPM_Homelab/) for the shared reference architecture, decisions, standards, and reusable patterns.

### Architectural relationship

```text
EPM_Homelab/
  = reference architecture and reusable enterprise patterns

This directory
  = reference implementation that executes, tests, and provides evidence for
    those patterns using the Customer/O2C role-aware unbilled use case
```

The reference implementation **implements** the shared architecture. It may reveal a reusable improvement, ambiguity, or gap, but it must not silently change an architecture decision, a model standard, a source-of-truth boundary, or a KPI definition.

### Change-routing rule

| Proposed change | Primary location | Required action |
|---|---|---|
| Reusable architecture principle, tool boundary, standard, or enterprise pattern | `EPM_Homelab/` | Propose/update the Homelab artifact and record a decision where material; assess impact on this and other demos |
| Customer/O2C source fixture, role mapping, data transformation, dashboard, test, or implementation-specific integration | This implementation directory | Change the implementation and its evidence; promote only proven reusable patterns to Homelab |
| Process meaning | Files under `business_architecture/business_process/` and `business_architecture/schema/` | Update the governing process or schema file before changing semantic interpretation |
| Customer business definition, role catalog, or source-system variant | Files under `business_architecture/domain/` | Draft Customer-domain context. Not process authority. Update that draft before changing Customer-domain interpretation |
| Metric/KPI definition, threshold, ownership, or approval status | KPI Store artifacts | Classify and govern the change; do not treat report logic as authoritative without validation |

## 2. Scope, baseline, and boundaries

### In scope

- Preserve and verify the existing Databricks Free / Unity Catalog / Contextual Views unbilled demonstration.
- Build deterministic synthetic Customer/O2C source records and cross-source identity/role scenarios.
- Represent Customer and O2C structures in Sirius Web at conceptual, logical, and physical levels.
- Publish controlled model exports and map them to semantic and technical assets.
- Load synthetic source records to Lakebase Postgres and represent them in Databricks Bronze.
- Create role-aware Silver structures and a Gold unbilled exposure fact.
- Implement reusable measures through Databricks Metric Views.
- Implement a minimum viable KPI Store pattern for candidate/approved KPI governance and published KPI snapshots.
- Publish semantic mappings and SHACL validation in Fuseki.
- Publish a serving/query context graph in Neo4j Community.
- Record technical catalog, ownership, lineage, quality, and glossary context through Unity Catalog and OpenMetadata, within available platform capabilities.
- Deliver a Plotly Dash operational control-tower dashboard.
- Deliver constrained FastAPI/MCP/agent tools that retrieve governed evidence rather than inventing calculations.
- Implement automated unit, integration, contract, semantic, lineage, and end-to-end acceptance tests.

### Explicitly out of scope

- Production MDM or customer-master replacement.
- Production integration with SAP, Salesforce, RightAngle, terminal automation, tax engines, banks, or collections platforms.
- Production financial close, invoicing, tax reporting, revenue recognition, credit decisioning, or collections workflow execution.
- Automatic promotion of an operational metric into an approved KPI.
- Enterprise-wide rollout of the model, ontology, graph, catalog, or KPI Store.
- Building or recreating Power BI reports unless separately approved.
- Treating historical Tableau calculations or current report logic as an approved KPI definition without governance validation.

### Current baseline

Known baseline:

- A Databricks unbilled demonstration already exists in this repository.
- The implementation is expected to use Databricks Free, Unity Catalog, Contextual Views, Lakebase Postgres (ODS), Sirius Web, Neo4j Community (meaning expose), OpenMetadata, Plotly Dash, Python, FastAPI, MCP, and Dagster where feasible.
- **Meaning path:** Turtle in git is SoT. Load published Turtle into Neo4j. Apache Jena Fuseki is optional **lab SPARQL classroom** only — keep it if you are learning SPARQL; it is not a client or demo-SoT runtime. Target picture: [`architecture/EPM-ARCH-MEANING-vs-COMPUTE.jpg`](../../../architecture/EPM-ARCH-MEANING-vs-COMPUTE.jpg). ADR-HL-021 / ADR-HL-022.
- Lakebase is the operational store, not a triple store. OntoBricks may draft OWL from UC tables; review, rewrite, and commit Turtle before any Neo4j load. dbxmetagen may draft comments/tags; do not auto-apply Metric Views.
- This is synthetic-data, homelab evidence—not a production design commitment.

Baseline uncertainty to resolve in Phase 0:

- Exact currently runnable scripts, schemas, catalog names, and execution commands.
- Which Databricks Free features are presently available in the target workspace.
- Exact version, API, export, authentication, and automation approach for Sirius Web.
- Whether OpenMetadata, Neo4j, Dash, Dagster, FastAPI, and MCP are locally containerized, remotely hosted, or not yet present. Fuseki is optional lab SPARQL only.
- Existing naming conventions, source-file formats, and test coverage.

No baseline behavior may be removed or refactored until it has a reproducible execution record and regression test evidence.

## 3. Business and measurement framing

### Customer/O2C problem

Customer-related identities and roles vary across commercial systems. A single legal party can be the bill-to party in one source, consignee in another, credit counterparty in a third, and corporate parent for reporting. Multiple parties can participate in one order, contract, delivery, custody, invoice, payment, or dispute chain.

The implementation must demonstrate that a simple global `customer_id` is insufficient for trusted O2C measurement. It must retain source identity, party identity, role context, effective dates, relationship evidence, and confidence/resolution status.

### Initial measurement classification

| Artifact | Initial classification | Governance status |
|---|---|---|
| Source-record amounts and dates | Raw measure / technical fields | Source-context evidence |
| Delivered quantity/value | Business or derived measure | Subject to validated calculation definition |
| Invoiced quantity/value | Business or derived measure | Subject to validated calculation definition |
| Unbilled exposure | Operational metric | Candidate for KPI evaluation; not approved automatically |
| Unbilled aging / exception count | Diagnostic/analytical metric | Used for investigation and control |
| Role-resolution coverage | Data-quality or operational metric | Used to measure harmonization quality |
| Customer O2C performance KPI | Candidate KPI only if ownership, objective, target, thresholds, cadence, and actions are defined | Requires formal KPI governance approval |

### Initial unbilled definition

The implementation must not claim this is an approved enterprise formula. It is a **candidate operational calculation** to validate with finance, commercial operations, billing, and the Customer-domain owner.

At a defined as-of timestamp and appropriate O2C grain:

\[
\text{Unbilled Exposure} = \text{Eligible Delivered Value} - \text{Eligible Invoiced Value}
\]

The detailed inclusion/exclusion rules, currency treatment, credit/rebill treatment, provisional pricing, tax handling, title-transfer point, and invoice finality must be represented as versioned calculation parameters and test scenarios—not embedded only in a dashboard query.

### Required KPI/metric metadata

Every reusable measurement must have, at minimum:

- Unique identifier and name.
- Classification: measure, metric, candidate KPI, approved KPI, technical calculation, or other taxonomy value.
- Business objective and business description.
- Formula version and effective dates.
- Time grain and business grain.
- Dimensional slicing rules, including permitted Customer role perspectives.
- Source systems, physical fields, lineage, and transformation dependencies.
- Accountable owner, technical owner, steward, and review cadence.
- Data-quality expectations, completeness rules, freshness expectation, and exceptions.
- Target, threshold/evaluation logic, and required action only when considered as a KPI.
- Publication/approval status.

## 4. Target architecture and source-of-truth boundaries

```text
                        ┌───────────────────────────────────┐
                        │ Customer/O2C business architecture │
                        │ party, role, process, measure      │
                        └─────────────────┬─────────────────┘
                                          │
                        ┌─────────────────▼─────────────────┐
                        │ ER/Studio models (production)      │
                        │ Sirius Web demo stand-in           │
                        │ conceptual / logical / physical    │
                        └───────┬──────────────┬─────────────┘
                                │              │ approved export
                     model context│              ▼
                                │   ┌─────────────────────────────┐
                                │   │ Fuseki demo runtime         │
                                │   │ SPARQL/SHACL from git Turtle│
                                │   └──────────────┬──────────────┘
                                │                  │ controlled projection
                                ▼                  ▼
                  ┌──────────────────┐    ┌───────────────────────┐
                  │ Unity Catalog    │    │ Neo4j context graph   │
                  │ native technical │    │ investigation/impact  │
                  │ governance       │    │ serving/query         │
                  └────────┬─────────┘    └──────────┬────────────┘
                           │                         │
 ┌───────────────────┐     ▼                         ▼
 │ Lakebase Postgres │ → Bronze → Silver → Gold → Metric Views → KPI Store → Dash / APIs / agents
 │ synthetic sources │      Databricks Delta / governed transformations
 └───────────────────┘
                           │
                           ▼
              ┌────────────────────┐    ┌────────────────────┐
              │ Purview catalog    │    │ Bigeye             │
              │ OM demo stand-in   │    │ observed lineage   │
              │ enterprise catalog │    │ and data quality   │
              └────────────────────┘    └────────────────────┘
                                          no OSS stand-in
```

### Mandatory boundaries

| Concern | System of record / authoritative boundary | Not authoritative for this concern |
|---|---|---|
| Downstream process meaning | Files under `business_architecture/business_process/` and `business_architecture/schema/` | Optional companions; demo-local process lists; files under `business_architecture/domain/` |
| Conceptual/logical/physical data-model structure | ER/Studio (production). Sirius Web is the demo stand-in | Hand-authored graph nodes, dashboard fields, agent prose; Sirius as a second model SoT |
| Formal semantic definitions and mapping assertions | Turtle in git (OWL/SKOS/SHACL). Fuseki loads those files as the demo SPARQL/SHACL runtime | Neo4j serving projection; Fuseki as a second ontology SoT |
| Operational source context | Lakebase source schemas and captured source extracts | Silver/Gold reinterpretation without retained source lineage |
| Lakehouse technical assets and native Databricks lineage | Unity Catalog | OpenMetadata copy/projection |
| Enterprise catalog | Purview (production). OpenMetadata is the demo stand-in | OpenMetadata as a second enterprise catalog |
| Cross-platform lineage and data quality | Bigeye (production) | no OSS stand-in; do not map OpenMetadata to Bigeye |
| Governed reusable analytical measures | Databricks Metric Views and versioned calculation specifications | Dashboard SQL, ad hoc notebook formulas, agent calculation logic |
| KPI approval, thresholding, ownership, and published value history | KPI Store governance artifacts and Gold-published KPI snapshots | Tableau logic, report calculations, or a Metric View alone |
| Graph investigation and impact traversal | Neo4j projection derived from approved sources | Uncontrolled semantic redefinition |
| Presentation | Plotly Dash | Independent calculation layer |

### Process authority and demo stand-ins

The files under `business_architecture/business_process/` and `business_architecture/schema/` are the Downstream oil and gas process set, including order-to-cash (O2C). Those two folders are process authority. Files under `business_architecture/domain/` are draft context, not process authority.

Current files on `main`:

- `business_architecture/business_process/downstream_process_map.json`
- `business_architecture/business_process/value_stream_order_to_cash.json`
- `business_architecture/business_process/value_stream_commercial_lifecycle.json`
- `business_architecture/business_process/data_product_portfolio.json`
- `business_architecture/business_process/office_lanes.json`
- `business_architecture/schema/data_product_portfolio.schema.json`
- `business_architecture/schema/value_stream.schema.json`

This implementation may use the open-source tools in the table below. The production system of authority is unchanged. A demo tool is not a second system of authority.

| Demo tool | Production seat | Concern |
|---|---|---|
| Sirius Web | ER/Studio | Models |
| OpenMetadata | Purview | Enterprise catalog |
| Neo4j Community | Neo4j | Serving graph |
| Apache Jena Fuseki | none (demo runtime only) | SPARQL and SHACL loaded from git Turtle |

Formal ontology source of truth stays Turtle in git. The serving graph stays Neo4j. Production seats stay ER/Studio, Purview, Unity Catalog, Bigeye, and Databricks Metric Views.

## 5. Core data-model requirements

### 5.1 Customer/party model

The implementation must distinguish at least these concepts:

| Concept | Required meaning |
|---|---|
| Party | A person, organization, legal entity, operating entity, or other commercial counterparty capable of participating in O2C relationships |
| Party identity | A stable internal/canonical identifier representing a resolved party where resolution is sufficiently supported |
| Source party record | A source-specific record and key preserved with source-system provenance |
| Party relationship | A dated relationship between parties, such as parent/subsidiary, guarantor/guaranteed party, franchisee/franchisor, or buying-group membership |
| Customer role | The role a party performs within a defined business context; never infer a single universal customer role |
| Role assignment | A dated association among party, role, O2C business object/context, source evidence, and resolution state |
| Corporate hierarchy | A dated party-to-party structure used for consolidated analysis; it is not a substitute for transaction-level role assignment |
| Resolution assertion | An evidence-backed claim that source records refer to the same, related, or distinct parties |
| Resolution status | Proposed, verified, rejected, unresolved, or conflicting, with confidence and evidence |

### 5.2 Minimum Customer role catalogue

The initial model must support, as applicable to synthetic scenarios:

- Sold-to party.
- Ship-to party.
- Consignee.
- Bill-to party.
- Payer.
- Contract party.
- Pricing party.
- Credit counterparty.
- Title-transfer party.
- Tax-liable party.
- Guarantor.
- Carrier/hauler.
- Corporate parent.
- Buying group or group-account relationship.

Each role must have a definition, allowed O2C business-object contexts, cardinality rules, effective dates, and source evidence. The model must support multiple roles per party and multiple parties per O2C object.

### 5.3 O2C chain

The first scenario must model enough structure to trace:

```text
commercial agreement / contract
  → order or nomination
  → allocation / lifting / delivery / custody release
  → billable event
  → invoice or invoice line
  → receivable / payment / adjustment / dispute
```

Required technical/business entities are expected to include:

- Commercial agreement/contract.
- Contract line or pricing term.
- Sales order, nomination, or equivalent commitment.
- Product and location/terminal context.
- Delivery, lifting, custody release, or billable event.
- Invoice and invoice line.
- Credit memo, rebill, adjustment, or dispute where needed for test cases.
- Currency, quantity, unit of measure, price, tax status, and as-of/effective timestamps.
- Customer role assignment at the correct transaction/process context.

### 5.4 Required keys and audit fields

All core structures require durable identifiers, source record identifiers where applicable, record source, load timestamp, effective-from/to timestamps where applicable, version or change sequence, and test scenario/fixture provenance for synthetic records.

No Silver/Gold entity may discard the source keys needed to trace it to its Bronze and Lakebase predecessors.

## 6. Data products and processing design

### 6.1 Lakebase source simulation

Create source-specific schemas/tables that emulate different system semantics. Use representative names only; do not misrepresent them as real production extracts.

| Synthetic source context | Example responsibility | Required customer semantics |
|---|---|---|
| CRM | Account/account hierarchy and commercial contacts | CRM account identifier, parent account, sales ownership, potential sold-to relationship |
| ERP billing/AR | Bill-to, payer, invoice, receivable, payment | Bill-to and payer can differ; invoice finality and adjustments must be represented |
| CTRM/commercial | Contract, nomination, pricing, counterparty | Contract party, pricing party, title-transfer and credit context |
| Terminal automation | Lifting, custody release, delivery endpoint | Consignee, carrier, ship-to/location context, physical event evidence |
| Tax/exemption | Tax registration, exemption, tax-liable party | Tax-liable party can differ from bill-to/payer |
| Collections/credit | Credit case, guarantor, parent/group view | Credit counterparty, guarantor, risk hierarchy context |

Use a deterministic seed and store it in the release manifest. Each fixture must identify its scenario and expected result.

### 6.2 Bronze

Bronze must preserve source representation with minimal transformation:

- One or more Bronze tables per source object.
- Source system, source table/object, source key, ingestion timestamp, extract batch, and raw/normalized payload representation.
- Reconciliation counts against Lakebase fixtures.
- Data-quality checks for key presence, uniqueness expectations, type conformance, and referential assumptions where source semantics allow.

### 6.3 Silver

Silver must harmonize without erasing role/source context.

Minimum Silver products:

| Silver product | Purpose |
|---|---|
| `party` | Canonical/resolved party representation with stable party identifier |
| `party_source_xref` | Source record to party mapping with evidence, confidence, effective dates, and resolution status |
| `party_relationship` | Dated parent/child, guarantor, group, and other relevant relationships |
| `party_role_assignment` | Party role in O2C object context, with role validity and source evidence |
| `commercial_agreement` | Contract/agreement context and relevant party-role relationships |
| `o2c_fulfillment_event` | Order, nomination, delivery, custody release, or billable event at chosen grain |
| `invoice_line` | Invoice line, finality, adjustment, and party-role linkage |
| `resolution_exception` | Unresolved/conflicting identity or role assertions affecting downstream measurement |

Silver behavior requirements:

- Preserve one-to-many and many-to-many role relationships.
- Do not choose a party or role silently when source evidence conflicts.
- Surface unresolved/conflicting resolution as explicit records and quality signals.
- Permit valid historical/as-of analysis through effective dating.
- Retain source lineage and transformation identifiers.

### 6.4 Gold

Create a Gold fact at a declared business grain. The recommended initial grain is **billable delivery/custody-release event and related contract/invoice allocation as of a specified reporting timestamp**.

Minimum Gold products:

| Gold product | Purpose |
|---|---|
| `fact_unbilled_exposure` | Role-aware delivery-to-invoice exposure, amounts, status, aging, and traceability keys |
| `dim_party_role_perspective` | Controlled analytical role perspective and relationship to party/context |
| `dim_o2c_status` | Billable, invoiced, partially invoiced, disputed, excluded, unresolved, or other governed status |
| `fact_customer_resolution_quality` | Resolution coverage and exception metrics by source/system/role/time |
| `kpi_value_snapshot` | Published snapshot of governed KPI values only after corresponding approval/publishing rules exist |

Required `fact_unbilled_exposure` attributes include:

- Business/as-of date and ingestion/publication timestamp.
- Delivery/custody/billable-event identifier and source identifiers.
- Contract/agreement, order/nomination, invoice-line, and adjustment identifiers where applicable.
- Party identifiers by role perspective—not only a generic customer key.
- Corporate-parent perspective where valid and dated.
- Eligible delivered amount, eligible invoiced amount, unbilled amount, currency, quantity, UOM, price and tax status as needed.
- Unbilled status, aging bucket, resolution status, data-quality status, and exclusion reason.
- Formula version, semantic version, transformation run identifier, source lineage keys, and test-scenario identifier.

### 6.5 Metric Views and KPI Store

Metric Views must expose reusable governed measurements such as eligible delivered value, eligible invoiced value, unbilled exposure, unbilled aging, and resolution coverage. Their formulas must refer to the governed Gold products and calculation specification version.

The KPI Store minimum viable pattern must separate:

```text
Calculation inventory / evidence
  → measurement catalog
  → candidate KPI register
  → KPI definition/version/threshold/ownership governance
  → approved calculation specification
  → published Gold KPI value snapshot
  → semantic/API/dashboard/agent consumption
```

For this demo, **unbilled exposure remains an operational metric unless formal governance explicitly approves it as a KPI**.

## 7. Semantic, graph, catalog, and model implementation

### 7.1 Sirius model repository

Create or extend a Sirius Web model that contains:

- Customer/party conceptual model.
- Customer role catalogue and role-assignment associations.
- O2C conceptual process/entity model.
- Logical data model for party, cross-reference, relationship, role assignment, contract, fulfillment, invoice, and exposure structures.
- Physical model mapping for Lakebase/Bronze/Silver/Gold products.
- Model-to-technical-asset mapping placeholders or controlled references.
- Version/release information and model validation results.

Python automation may submit only allow-listed model changes, such as create/update controlled elements, add approved attributes, create relationships, export a model release, or execute validation. Every automated change must retain a request/correlation ID, actor, timestamp, model version, and result.

### 7.2 Fuseki ontology and SHACL

Create modular RDF artifacts, for example:

```text
ontology/
├── customer-party.ttl
├── customer-roles.ttl
├── o2c-events.ttl
├── measurement-kpi.ttl
├── technical-mapping.ttl
├── provenance.ttl
├── shapes/
│   ├── customer-party.shacl.ttl
│   ├── customer-role-assignment.shacl.ttl
│   ├── o2c-event.shacl.ttl
│   └── measurement-kpi.shacl.ttl
└── mappings/
    ├── sirius-model-to-ontology.ttl
    ├── unity-catalog-to-ontology.ttl
    └── gold-metric-to-ontology.ttl
```

Required semantic concepts include Party, PartyRole, PartyRoleAssignment, PartyRelationship, SourcePartyRecord, ResolutionAssertion, CommercialAgreement, FulfillmentEvent, InvoiceLine, Measure, Metric, CandidateKPI, ApprovedKPI, DataProduct, PhysicalField, QualityRule, and LineageRelationship.

SHACL must validate at least:

- A role assignment identifies party, role, context, evidence/source, and validity where required.
- Unbilled fact semantic assertions contain traceability to delivery and applicable invoice/contract context.
- Candidate/approved KPI objects meet the required governance metadata appropriate to their classification.
- A metric is not asserted as an approved KPI without approval status, accountable owner, formula version, time grain, threshold/evaluation logic, and review cadence.

### 7.3 Neo4j serving graph

Neo4j must be a controlled projection from approved model/semantic/catalog/lineage/measurement artifacts. It supports contextual queries, impact analysis, and agent retrieval.

Minimum node labels:

```text
Party, PartyRole, PartyRoleAssignment, SourceRecord,
CommercialAgreement, FulfillmentEvent, InvoiceLine,
DataProduct, Table, Column, Metric, CandidateKPI, ApprovedKPI,
QualityRule, ModelElement, OntologyConcept, DashboardComponent,
TestCase, Release
```

Minimum relationship types:

```text
RESOLVES_TO, HAS_ROLE, PARTICIPATES_IN, RELATED_TO,
GOVERNS, REPRESENTS, SOURCED_FROM, TRANSFORMS_TO,
CALCULATES, PUBLISHED_AS, VALIDATED_BY, IMPLEMENTS,
MAPS_TO, DEPENDS_ON, IMPACTS, DISPLAYED_BY, TESTED_BY
```

The graph must retain provenance/source-system and version identifiers. It must not become a second calculation engine or semantic-authoring source.

### 7.4 Unity Catalog and OpenMetadata

Unity Catalog requirements:

- Register/catalog Lakebase-connected or ingested objects where capability permits.
- Govern Databricks tables/views, Metric Views, notebooks/jobs/pipelines as available, and access boundaries.
- Maintain technical ownership, descriptions, classifications/tags, and native lineage.

OpenMetadata requirements:

- Ingest or register Databricks/Unity Catalog metadata plus local/other platform assets where feasible.
- Represent ownership/stewardship, glossary associations, data-product context, cross-platform lineage, quality-test references, and documentation links.
- Be treated as an observability/discovery plane—not the authoritative origin of Databricks technical lineage.

## 8. Dashboard, APIs, and agents

### 8.1 Plotly Dash control tower

The dashboard must consume Gold tables, Metric Views, KPI Store published outputs, and traceability APIs only. It must not calculate unbilled exposure independently.

Initial dashboard capabilities:

- Aggregate unbilled exposure by selected Customer role perspective.
- Compare bill-to, consignee, credit-counterparty, and corporate-parent views, where defined.
- Filter by as-of date, business date, product, terminal/location, status, aging bucket, source/resolution status, and scenario.
- Drill from aggregate metric to governed Gold fact rows and evidence chain.
- Display formula version, publication timestamp, data-quality status, classification, and KPI status.
- Surface unresolved/conflicting Customer identity/role exceptions and affected exposure.
- Present a clear disclaimer when a metric is not an approved KPI.

### 8.2 FastAPI/MCP/agent controls

Expose narrow, read-only, evidence-backed tools. Suggested initial tools:

- `get_unbilled_exposure_summary(as_of_date, role_perspective, filters)`.
- `explain_unbilled_event(event_id, as_of_date)`.
- `get_party_role_context(party_id_or_source_key, context_id)`.
- `get_metric_definition(metric_id, version)`.
- `get_metric_lineage(metric_id_or_gold_field)`.
- `get_resolution_exceptions(filters)`.
- `get_model_impact(model_element_id)`.

Agent requirements:

- Retrieve only from approved/queryable sources.
- Return evidence IDs, formula/version, publication timestamp, and limitations.
- State when the requested output is an operational metric versus an approved KPI.
- Never invent entity matches, role assignments, calculation definitions, thresholds, or source lineage.
- Do not write to Sirius, Fuseki, Neo4j, Lakebase, Databricks, or catalog tools unless a separately approved controlled-write workflow is implemented.

## 9. Test strategy and acceptance gates

### 9.1 Test layers

| Test layer | Required evidence |
|---|---|
| Baseline/regression | Existing demo runs reproducibly before modification; expected outputs recorded |
| Unit | Transformation functions, status classification, role mapping, calculation parameters, API behavior |
| Source contract | Lakebase schema, key, data-type, required-field, and scenario fixture tests |
| Bronze reconciliation | Source-to-Bronze counts and source-key preservation |
| Silver harmonization | Party/role relationships, effective dates, conflict handling, xref coverage, lineage preservation |
| Gold calculation | Deterministic unbilled calculation, allocation, status, aging, and exclusion outcomes |
| Metric View/KPI Store | Metric definitions use governed Gold fields; classification and required metadata controls |
| Semantic | RDF syntax, ontology consistency where supported, SHACL validation, mapping completeness |
| Graph | Expected node/edge counts, provenance, no orphan critical nodes, competency queries |
| Catalog/lineage | Critical path is represented: source → Bronze → Silver → Gold → Metric → dashboard/API/agent |
| Dashboard | Dashboard renders governed outputs; filters/drill-through retain formula/version/evidence context |
| API/agent | Read-only authorization, schema validation, evidence grounding, error/uncertainty behavior |
| End-to-end | Scenario passes from synthetic source through dashboard and evidence explanation |

### 9.2 Minimum deterministic scenarios

Implement at least these scenarios, each with fixtures and expected outputs:

| Scenario | Required behavior |
|---|---|
| Same party, multiple source identifiers | CRM, ERP, and CTRM records resolve to one party with retained source references |
| One party, multiple transaction roles | Same party is sold-to and bill-to but a different party is consignee or payer |
| Parent/child hierarchy | Corporate-parent rollup is valid for reporting but does not overwrite transaction role |
| Delivered, not invoiced | Eligible delivery appears as unbilled at the declared as-of timestamp |
| Partially invoiced | Only remaining eligible amount is unbilled |
| Invoice posted after as-of date | Exposure is correct for historical as-of date and changes only in later snapshot |
| Credit/rebill or adjustment | Formula behavior follows explicit, versioned inclusion/exclusion rule |
| Tax-liable party differs from bill-to | Role-specific analysis remains accurate |
| Unresolved identity | Exposure is surfaced with unresolved/conflicting status and included/excluded per governed rule |
| Conflicting roles | No silent resolution; exception appears with lineage/evidence |
| Data-quality failure | Failed check changes quality status and dashboard/agent explanation reflects it |

### 9.3 Acceptance criteria

The release is acceptable only when:

1. The baseline demonstration executes and its behavior is captured.
2. The full synthetic scenario suite is reproducible from a clean environment with documented prerequisites.
3. Source-to-Bronze and Bronze-to-Silver reconciliation tests pass.
4. Silver retains role-aware, dated, and source-traceable party context.
5. Gold unbilled results match scenario expected outputs and formula version.
6. Metric View definitions and KPI metadata do not misclassify an operational metric as an approved KPI.
7. SHACL validation and graph competency queries pass.
8. Critical lineage is available across source, data products, measurement, dashboard, and API/agent outputs.
9. Dashboard drill-down reaches fact-level evidence and displays quality/formula/version status.
10. Agent/API answers return grounded evidence or explicitly state that evidence is unavailable.
11. A release manifest records versions, run IDs, input fixture seed/hash, test results, model/ontology release identifiers, and known limitations.

## 10. Delivery phases

### Phase 0 — Baseline and controls

**Objective:** Establish a reproducible, protected starting point.

Deliverables:

- Runbook for current demonstration.
- Environment/prerequisite inventory and tool-version matrix.
- Baseline release manifest and captured expected outputs.
- Repository inventory and naming-standard decision.
- Initial architecture conformance matrix.
- Risk and assumption register.

Exit gate: Existing demo is runnable from documented commands, with no unrecorded manual steps required for the baseline path.

### Phase 1 — Business, model, and scenario design

**Objective:** Define the Customer/O2C meaning and deterministic proof cases before implementing harmonization.

Deliverables:

- Validated initial party/role catalogue and O2C business grain.
- Sirius conceptual/logical model version.
- Initial RDF/OWL/SKOS concepts and SHACL shapes.
- Synthetic scenario catalogue, expected results, and seed policy.
- Draft calculation specification for unbilled exposure.
- Measurement classification records and candidate KPI assessment.

Exit gate: Domain owner/steward and implementation owner can explain how role-aware scenarios differ from a generic customer key and agree on testable expected results.

### Phase 2 — Source, Bronze, and Silver implementation

**Objective:** Build source-context preservation and role-aware harmonization.

Deliverables:

- Lakebase source schemas, fixtures, and deterministic generator.
- Bronze ingestion and reconciliation tests.
- Silver party, xref, relationship, role-assignment, O2C event, and exception products.
- Model-to-data mapping references.
- Silver quality tests and resolution exception outputs.

Exit gate: Each source scenario is traceable through Bronze and Silver without losing source key, role context, dates, or evidence.

### Phase 3 — Gold, Metric Views, and KPI Store minimum viable pattern

**Objective:** Produce governed, explainable unbilled metric outputs.

Deliverables:

- Gold unbilled exposure fact and supporting dimensions.
- Calculation specification/version table and test fixtures.
- Metric Views for reusable measures.
- Candidate KPI register entry and measurement catalog entry.
- KPI Store schema/components sufficient to separate catalog, calculation, governance, and published snapshots.
- Gold/Metric/KPI governance tests.

Exit gate: Unbilled exposure is reproducible at declared grain/as-of time and clearly labeled as an operational metric unless separately approved.

### Phase 4 — Semantic, graph, catalog, and lineage integration

**Objective:** Make model, semantic, technical, and measurement dependencies queryable and validated.

Deliverables:

- Sirius approved export and release record.
- Fuseki ontology/mapping load and SHACL test results.
- Neo4j controlled projection, constraints, indexes, and competency queries.
- Unity Catalog and OpenMetadata registration/lineage evidence.
- Cross-layer traceability queries.

Exit gate: A user can trace a metric output to Gold/Silver/Bronze/source records and see connected model, semantic, and quality context.

### Phase 5 — Consumption, controls, and release evidence

**Objective:** Deliver operational consumption without recreating calculation logic.

Deliverables:

- Plotly Dash control tower with drill-through/evidence behavior.
- FastAPI/MCP read-only evidence tools.
- Agent test suite and grounded-answer behavior.
- End-to-end scenario demonstrations.
- Release manifest, known-limitations statement, and architecture conformance assessment.

Exit gate: A business/technical reviewer can ask the defined questions, obtain governed results and evidence, and distinguish metric, candidate KPI, and approved KPI status.

## 11. Implementation backlog

| ID | Priority | Backlog item | Dependency | Done when |
|---|---:|---|---|---|
| RI-001 | P0 | Inventory and run existing demo | Existing repository/environment | Baseline manifest and regression output exist |
| RI-002 | P0 | Define repository conventions, environment file, and release manifest | RI-001 | Reproducible local/workspace setup documented |
| RI-003 | P0 | Define Customer/O2C scenario catalogue and expected results | Domain artifact review | Scenarios have deterministic fixtures and assertions |
| RI-004 | P0 | Build Sirius conceptual/logical Customer/O2C model | RI-003 | Versioned model export passes validation |
| RI-005 | P0 | Create Lakebase synthetic source schemas and seeded fixtures | RI-003 | Source contract tests pass |
| RI-006 | P0 | Implement Bronze ingestion and reconciliation | RI-005 | Source keys/counts reconcile |
| RI-007 | P0 | Implement Silver party/xref/role/relationship structures | RI-004, RI-006 | Role-aware scenario tests pass |
| RI-008 | P0 | Implement Gold unbilled exposure fact and calculation version | RI-007 | Gold expected-output tests pass |
| RI-009 | P0 | Implement measurement catalog and candidate KPI register records | RI-008 | Classification/governance tests pass |
| RI-010 | P1 | Implement Databricks Metric Views | RI-008 | Reusable measure outputs reconcile to Gold |
| RI-011 | P1 | Implement ontology modules and SHACL validation | RI-004, RI-009 | Semantic tests pass |
| RI-012 | P1 | Project approved semantic/model/catalog context to Neo4j | RI-011 | Competency queries and provenance tests pass |
| RI-013 | P1 | Register/catalog assets and lineage in Unity Catalog/OpenMetadata | RI-006 through RI-010 | Critical path is discoverable |
| RI-014 | P1 | Implement Plotly Dash dashboard | RI-008 through RI-010 | Dashboard tests prove governed consumption |
| RI-015 | P2 | Implement FastAPI/MCP evidence tools | RI-012 through RI-014 | API/agent ground-truth tests pass |
| RI-016 | P2 | Execute full end-to-end release test and evidence package | All preceding | Release acceptance criteria pass |

## 12. Risks, assumptions, and decisions required

### Assumptions

- Synthetic data can represent the required role/identity/fulfillment/invoicing edge cases without exposing actual customer data.
- A suitable as-of reporting model can be implemented in Databricks Free within available feature limits.
- Sirius Web supports the selected modeling and export workflow, or a documented controlled alternative is approved.
- Cross-platform catalog/lineage integrations may be partially simulated where local tooling limitations prevent full native ingestion.
- The initial use case can use a limited product/location/currency scope while retaining extensible modeling patterns.

### Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Ambiguous unbilled definition | Incorrect metric interpretation | Versioned calculation specification, owner validation, scenario tests, visible status disclaimer |
| Role simplification into one customer key | False attribution and misleading aggregation | Mandatory role-assignment model and scenario tests |
| Tool capability limits in free/local environment | Delayed or incomplete integrations | Phase 0 capability assessment; document substitutes and deviations |
| Semantic/graph duplication | Conflicting definitions | Enforce Turtle in git as the source, and the Neo4j projection boundary |
| Dashboard or agent formula reimplementation | Governed-result drift | Only consume Gold/Metric/KPI outputs; test response provenance |
| Overly broad scope | Unfinished proof | Use phased exit gates and maintain strict non-goals |
| Historical report logic treated as truth | Unvalidated KPI definitions | Classify as evidence; route to KPI governance validation |

### Open decisions

- What is the authoritative initial business grain for the unbilled fact: custody release, delivery, billable event, allocation, invoice-line pairing, or a combination with bridge tables?
- Which amount is used in the first scope: estimated, provisional, final, net of tax, gross, functional currency, transaction currency, or dual-currency representation?
- Which delivery/completion event makes a transaction eligible for billing in the synthetic use case?
- How are partial invoices, credit/rebills, reversals, disputes, and late adjustments treated in Version 0.1?
- What confidence/evidence threshold allows a source-party mapping to be used in standard aggregation rather than held as unresolved?
- Which Homelab artifact is the approved source for repo naming, model naming, ontology namespace, and release-version conventions?
- Which actual Databricks workspace and service deployment approach is available?

## 13. Artifact update block

### Conclusions

- The Customer/O2C role-aware unbilled demonstration is a reference implementation, not a competing reference architecture.
- Customer identity, hierarchy, and transaction role must be represented separately to support trustworthy O2C measurement.
- Unbilled exposure is initially an operational metric/candidate KPI consideration, not an automatically approved KPI.
- Meaning, compute, and consume must remain separated: Turtle in git defines formal semantic and mapping assertions only, not all meaning (ER/Studio production / Sirius Web demo stand-in model structure); FOUND-003 stays the human-readable semantic model; FOUND-004 stays the ontology design and uses conceptual names; exact IRIs, axioms, constraints, and individuals belong to Turtle in git; Databricks computes; Dash/APIs/agents consume governed outputs; Neo4j serves context.

### Decisions and status

- **Draft decision:** `EPM_Homelab/` governs reusable patterns; this directory contains implementation-specific executable evidence.
- **Draft decision:** Turtle in git is the formal semantic and mapping source, not all meaning. FOUND-003 stays the human-readable semantic model. FOUND-004 stays the ontology design and uses conceptual names; exact IRIs, axioms, constraints, and individuals belong to that Turtle. Fuseki loads that release as the demo SPARQL/SHACL runtime. Neo4j is a controlled projection for investigation and impact analysis.
- **Draft decision:** Dashboard and agent layers may not recreate governed metric/KPI formulas.
- **Pending decision:** Initial unbilled calculation scope, financial treatment, business grain, and operational owner validation.

### Definitions added or changed

- Party, source party record, party identity, party relationship, customer role, role assignment, resolution assertion, and resolution status are distinguished.
- Unbilled exposure is classified as an operational metric pending formal KPI governance.

### Assumptions

- All proof data is synthetic and deterministic.
- Existing demonstration logic is baseline evidence, not automatically an approved formula or KPI definition.
- Tool integrations may be incrementally implemented based on available homelab capabilities.

### Open questions and conflicts

- Resolve the detailed unbilled formula, grain, timing, currency, tax, adjustment, and status rules before asserting a governed metric release.
- Validate the role catalogue and source variants against the governing Customer-domain artifact.
- Confirm tool capabilities and deployment paths in Phase 0.

### Source evidence

- Existing implementation files and executable Databricks baseline, to be inventoried in Phase 0.
- `README.md` and `THE-PROBLEM.md` in this directory.
- Customer-domain problem statement in the business architecture repository.
- EPM Homelab reference architecture, ADR, data strategy, ontology-pilot, and repo/build artifacts.

### Artifacts to create or update

- This implementation README and handoff document.
- Baseline release manifest and environment/tool matrix.
- Customer/O2C Sirius model and controlled exports.
- Synthetic fixture catalogue and data contracts.
- Bronze/Silver/Gold design and SQL assets.
- Measurement Catalog and Candidate KPI Register entries.
- KPI Store technical-design artifacts for the pilot pattern.
- Ontology, SHACL, graph projection, catalog/lineage, dashboard, API/agent, and test artifacts.
- Architecture Decision Log entries for material reusable choices.

### Suggested version/status changes

- `IMPLEMENTATION-HANDOFF.md`: Version 0.1, **Draft**.
- `README.md`: Version 0.1, **Draft**.
- Promote relevant Homelab artifacts only after explicit review of reusable lessons from the implementation.

### Next action

Execute Phase 0: inventory the existing demo, document exact run commands and capability constraints, capture a baseline release manifest, and create regression tests before adding Customer-role extensions.
