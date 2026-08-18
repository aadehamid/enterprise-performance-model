# Enterprise Performance Model
## Project Charter, Operating Model, and Knowledge Management Framework

**Artifact ID:** EPM-FOUND-001  
**Status:** Candidate  
**Version:** 2.0  
**Primary owner:** Enterprise Performance Model Lead  
**Applies to:** KPI Store, Domain Modeling, System Integration, and cross-cutting Data Governance  
**Purpose:** Define how the project is organized, governed, executed, documented, and evolved.

---

# 1. Purpose

The Enterprise Performance Model initiative establishes a governed business, measurement, data, modeling, metadata, and technology architecture for Downstream Oil & Gas.

The architecture connects:

**Business objectives → value streams → domains and capabilities → processes and activities → measurements → KPIs → data products → domain models → technical data assets → reports, analytics, applications, automation, and AI**

The initiative is broader than a KPI database. It creates the context needed to understand why a KPI exists, how it is calculated, which business process it measures, which data products and models support it, where it is consumed, and who is accountable for its meaning and performance.

The Enterprise Performance Model is the conceptual umbrella. The KPI Store is the first implementation priority.

---

# 2. Current-State Baseline

## 2.1 Power BI migration status

The Tableau reports in scope have already been migrated to Power BI.

The completed migration focused on maintaining reporting capability and transitioning the visualization platform. It did not systematically capture or govern:

- KPI definitions.
- KPI ownership.
- KPI targets and thresholds.
- Reusable business measures.
- Formula differences across reports.
- Calculation lineage.
- Process and capability context.
- Data-product dependencies.
- Enterprise semantic standards.

The current initiative is therefore not a new Tableau-to-Power BI migration.

## 2.2 Retrospective Tableau XML discovery

Legacy Tableau XML is being parsed to recover calculations used in workbooks, dashboards, worksheets or views, and data sources.

The extracted content is an inventory of historical logic. It may include:

- Raw measures.
- Derived measures.
- Operational metrics.
- Diagnostic metrics.
- Candidate KPIs.
- Table calculations.
- Filters and parameters.
- Presentation calculations.
- Duplicate calculations.
- Obsolete calculations.
- Locally modified versions of similar concepts.

Extraction does not confer governance status.

## 2.3 Current Power BI role

Power BI reports and semantic models are used to:

- Identify what is currently consumed.
- Compare migrated calculations with legacy Tableau logic.
- Determine whether logic changed during migration.
- Identify duplicate or local measures.
- Validate proposed enterprise definitions.
- Trace which reports depend on a measure or KPI.

Report redevelopment is outside the current scope unless specifically authorized.

---

# 3. Strategic Objectives

The initiative will:

1. Define a common enterprise measurement and KPI architecture.
2. Establish the KPI Store end to end.
3. Recover and rationalize business logic from legacy Tableau content.
4. Standardize reusable metrics and enterprise KPIs.
5. Establish business ownership, stewardship, and decision rights.
6. Connect KPIs to objectives, processes, data products, models, and technical assets.
7. Develop a reusable Domain Modeling playbook and reference architecture.
8. Develop reusable System Integration patterns for the core metadata ecosystem.
9. Create traceability from business definitions to technical fields.
10. Provide trusted, reusable, and AI-ready business context.

---

# 4. Workstream Model

## 4.1 Workstream 1 — KPI Store and Enterprise Performance Management

**Priority:** First

### Scope

- Define the KPI Store and its boundaries.
- Establish the measurement taxonomy.
- Inventory Tableau calculations.
- Normalize calculations and identify duplicates.
- Classify measurements.
- Identify candidate enterprise KPIs.
- Establish KPI governance and approval.
- Define KPI metadata.
- Define targets, thresholds, and status evaluation.
- Define versioning, effective dating, and restatement.
- Define KPI calculation and loading patterns.
- Define data-quality controls.
- Define lineage.
- Define consumption patterns.
- Implement representative pilot KPIs.
- Scale by business capability and domain.

### Logical layers

1. Source Calculation Inventory.
2. Governed Enterprise Measurement Catalog.
3. Candidate KPI Register.
4. Approved Enterprise KPI Catalog.
5. KPI Calculation Layer.
6. KPI Values Store.
7. KPI Consumption Layer.

### Non-goals

- Storing every Tableau calculation as a KPI.
- Rebuilding all Power BI reports.
- Treating report popularity as KPI approval.
- Waiting for every domain model to be complete before beginning.
- Replacing foundational data products with the KPI Store.

---

## 4.2 Workstream 2 — Domain Modeling

**Priority:** Follow-on and iterative

### Purpose

Create a reusable, tool-agnostic playbook that defines how business concepts are represented in conceptual and logical models and how models connect to metadata, data products, and technical fields.

### In scope

- Domain Modeling playbook.
- Reference architecture.
- Modeling methodology.
- Modeling standards and conventions.
- Required inputs and outputs.
- Modeling lifecycle and governance.
- Technical considerations.
- Alignment with the enterprise data-product strategy.
- One or two representative proofs of value.
- Demonstration of how models can be physicalized later.
- Connection from business definition through catalog and model to technical field.
- Use of ER/Studio, Purview, Unity Catalog, and BigEye as the core stack.

### Out of scope

- Broad ETL or ELT development.
- Enterprise-wide physical data-model implementation.
- Database-ready physicalization of all domains.
- Heavy production execution.
- Comprehensive domain enrichment within the initial timeline.
- Deep validation of every domain.
- A broad enterprise roadmap unless separately authorized.

### KPI Store relationship

Domain Modeling must not delay the first KPI Store phase.

During the Domain Modeling re-drive or refinement stage, model outputs will enrich the KPI architecture by mapping:

- KPI to domain.
- KPI to capability.
- KPI to process and activity.
- KPI to business objective.
- KPI to supporting measurements.
- KPI to business concepts.
- KPI to conceptual and logical entities.
- KPI to model attributes.
- KPI to data products.
- KPI to source and technical fields.

The KPI Store must therefore support progressive metadata enrichment.

---

## 4.3 Workstream 3 — System Integration

**Priority:** Follow-on, coordinated with Domain Modeling

### Purpose

Define how modeling, catalog, technical governance, and data-quality tools operate as one metadata ecosystem.

### Core stack

- ER/Studio — data modeling.
- Microsoft Purview — enterprise governance, glossary, catalog, and lineage.
- Unity Catalog — Databricks governance and technical catalog.
- BigEye — data quality and observability.

### In scope

- Tool responsibility boundaries.
- Core connectivity design patterns.
- System flow maps.
- Metadata propagation patterns.
- Integration contracts.
- Payload structures.
- Interoperability constraints.
- Metadata synchronization risks.
- Proof-of-value integration.
- Illustrative actual payload exchange.

### Out of scope

- Production tool installation or configuration.
- Broad production implementation.
- Bulk glossary or schema migration.
- Enterprise-wide metadata migration.
- Production custom connector development.
- Broad custom APIs and pipeline development.
- Evaluation of unrelated tooling.

### KPI Store relationship

The KPI Store is a primary integration use case. The target traceability path is:

**Business KPI definition → Purview term and governance metadata → ER/Studio domain model → Unity Catalog technical assets → BigEye quality controls → KPI Store calculation and values → Power BI and other consumers**

The first KPI Store release must not depend on full production integration across all tools.

---

## 4.4 Cross-cutting Data Governance

Data Governance applies across all workstreams and lifecycle stages.

It establishes:

- Enterprise policies and standards.
- Roles and decision rights.
- Domain ownership.
- Business definitions and semantic consistency.
- Metadata and lineage.
- Data quality.
- Security, privacy, retention, and compliance.
- Data-product governance.
- Reuse and interoperability.
- Adoption and value realization.
- Maturity measures.

---

# 5. Governance Roles

## 5.1 Executive leadership

- Set strategic direction.
- Establish priorities.
- Allocate resources.
- Resolve material escalations.
- Monitor value and risk.
- Sponsor adoption.

## 5.2 Global process owners

- Own end-to-end processes.
- Establish process standards.
- Resolve cross-domain process decisions.
- Define required business outcomes.
- Validate process KPIs.
- Drive continuous improvement.

## 5.3 Enterprise Data Governance

- Establish policies and standards.
- Define governance roles.
- Operate enterprise governance forums.
- Resolve cross-domain semantic issues.
- Monitor governance maturity and adoption.
- Promote enterprise reuse.

## 5.4 Domain Data Owner

- Set domain strategy and objectives.
- Approve business semantics.
- Approve domain KPIs.
- Establish ownership and decision rights.
- Set data-quality expectations.
- Prioritize data products.
- Balance value, risk, and compliance.
- Sponsor adoption and value realization.

## 5.5 Business KPI Owner

- Own the business objective and intended outcome.
- Approve KPI definition and interpretation.
- Approve targets and thresholds.
- Define the management action triggered by the KPI.
- Participate in periodic KPI review.

## 5.6 Data Product Owner

- Define product purpose and consumers.
- Manage product lifecycle.
- Approve requirements and contracts.
- Establish service expectations.
- Monitor adoption, quality, performance, and value.
- Ensure fitness for purpose.

## 5.7 Data Steward

- Maintain glossary terms and definitions.
- Maintain business and technical metadata.
- Monitor data quality.
- Coordinate issue resolution.
- Support lineage and discoverability.
- Apply naming and classification standards.

## 5.8 Semantic Model Owner

- Own shared dimensions and measures.
- Implement approved reusable logic.
- Maintain security and certification.
- Support consuming reports.
- Manage compatibility and change.

## 5.9 Digital and engineering teams

- Provide architecture and platforms.
- Implement approved models and data solutions.
- Secure and operate technical components.
- Build pipelines and transformations where authorized.
- Implement monitoring and technical quality controls.
- Support metadata and lineage.

## 5.10 Enterprise Performance Model Lead

- Own overall project direction.
- Maintain architectural coherence.
- Prioritize workstreams.
- Accept candidate artifacts for formal review.
- Ensure durable decisions are promoted from chats.
- Coordinate stakeholder validation.
- Maintain the master index and decision log.

---

# 6. Guiding Principles

1. Business ownership is required.
2. The KPI Store is the first delivery priority.
3. The Enterprise Performance Model remains the conceptual umbrella.
4. Not every calculation is a metric, and not every metric is a KPI.
5. Legacy report logic is evidence, not authority.
6. Governance is embedded in delivery.
7. Shared semantics are mandatory.
8. Data products are governed, reusable assets.
9. Enterprise interoperability is required.
10. Metadata and lineage are mandatory.
11. Reuse is preferred over duplication.
12. Governance rigor is proportional to business value and risk.
13. Methods should remain tool-agnostic even when proved through the current core stack.
14. Design patterns should be validated through targeted proofs of value.
15. Domain models and KPI metadata must be progressively reconcilable.
16. Approved baselines cannot be changed silently.
17. Durable knowledge must be promoted from chats into controlled artifacts.

---

# 7. Measurement and KPI Governance

## 7.1 Measurement taxonomy

- Raw measure.
- Business measure.
- Derived measure.
- Operational metric.
- Diagnostic or analytical metric.
- Performance indicator.
- Candidate KPI.
- Approved enterprise KPI.
- Technical calculation.
- Presentation-only calculation.
- Duplicate or near-duplicate.
- Obsolete or retired.

## 7.2 KPI qualification criteria

A candidate KPI should normally have:

- A defined business objective.
- An accountable business owner.
- An approved definition.
- An approved calculation.
- Defined dimensions and time grain.
- A target or performance expectation.
- Thresholds or evaluation logic.
- A management review cadence.
- A defined action or decision when performance changes.
- Enterprise or cross-report significance.
- Feasible data quality and timeliness.

## 7.3 KPI lifecycle

1. Discovered.
2. Normalized.
3. Classified.
4. Candidate.
5. Under business review.
6. Under technical validation.
7. Approved.
8. Implemented.
9. Monitored.
10. Revised, superseded, or retired.

---

# 8. Delivery Lifecycle

## Stage 1 — Discover

Collect evidence from:

- Tableau XML.
- Power BI reports and semantic models.
- Existing definitions.
- Source schemas.
- Data products.
- Business workshops.
- Process documentation.
- Prior chats and project sources.
- Industry sources where authorized.

Discovery identifies what exists. It does not approve it.

## Stage 2 — Contextualize

Map the item to:

- Business area.
- Value-stream stage.
- Domain and capability.
- Process and activity.
- Business objective.
- Decision supported.
- User group.
- Data product.
- Model entity.
- Source system.
- Consumer.

## Stage 3 — Classify

Assign the measurement type and governance state.

## Stage 4 — Rationalize

Determine whether to:

- Standardize.
- Consolidate.
- Reuse.
- Retain locally.
- Recalculate centrally.
- Replace.
- Deprecate.
- Retire.

## Stage 5 — Govern

Approve meaning, formula, ownership, dimensions, grain, thresholds, quality expectations, and review cadence.

## Stage 6 — Design and Implement

Place logic at the lowest sensible reusable layer:

- Foundational data product.
- Derived data product.
- Semantic model.
- KPI calculation layer.
- KPI Store.
- Consumption view.
- Report, application, alert, or AI service.

## Stage 7 — Validate

Validate:

- Formula.
- Data.
- Dimensional behavior.
- Time behavior.
- Reconciliation.
- Quality.
- Freshness.
- Lineage.
- Performance.
- User acceptance.
- Management usefulness.

## Stage 8 — Promote and Evolve

Update canonical artifacts, decision records, lineage, statuses, and implementation documentation.

---

# 9. Chat and Knowledge Operating Model

## 9.1 Purpose of chats

Chats support:

- Exploration.
- Learning.
- Source review.
- Concept definition.
- Clarification.
- Alternative analysis.
- Design.
- Alignment.
- Validation.
- Drafting.
- Stakeholder preparation.

A chat is not the system of record.

## 9.2 Chat categories

Recommended chat naming:

- `KPI | <topic>`
- `XML | <workbook or calculation family>`
- `BUSINESS | <domain or process>`
- `MODEL | <domain or proof of value>`
- `INTEGRATION | <tool or pattern>`
- `GOVERNANCE | <policy or role>`
- `DECISION | <decision topic>`
- `DELIVERABLE | <artifact name>`
- `LEARNING | <concept>`
- `RESEARCH | <topic>`

## 9.3 Chat closeout

At the end of a substantial chat, produce:

- Summary of the question.
- Current baseline.
- Conclusions.
- Decisions.
- New or changed definitions.
- Assumptions.
- Open questions.
- Conflicts.
- Evidence used.
- Artifacts to create or update.
- Suggested status/version change.
- Next action.

## 9.4 Promotion rule

No durable conclusion is complete until it is transferred to a canonical artifact or recorded as an explicit pending update.

---

# 10. Use of Previous and Outside-Project Conversations

## 10.1 Retrieve before recreating

Before beginning a major artifact or reopening a major design question, review accessible prior context.

## 10.2 Treat previous chats as evidence

A previous chat may contain:

- Approved decisions.
- Candidate decisions.
- Working assumptions.
- Outdated information.
- Contradictory designs.
- Valuable domain knowledge.

Its content must be classified before incorporation.

## 10.3 Promotion workflow

For each relevant prior chat:

1. Identify the scope and major topics.
2. Extract durable conclusions.
3. Separate decisions from exploration.
4. Identify assumptions and unresolved questions.
5. Compare with the current baseline.
6. Record conflicts.
7. Map each conclusion to a canonical artifact.
8. Update the artifact.
9. Record material decisions.
10. Add the chat or summary to the Source and Traceability Register.

## 10.4 Outside-context availability

When outside-project context is accessible, use it as baseline evidence.

When it is not accessible:

- State the missing context.
- Ask for the chat to be moved, attached, or summarized.
- Do not reconstruct material decisions from vague memory.
- Continue only with clearly labeled assumptions where useful.

## 10.5 Sharing transition

Before the project is shared or otherwise isolated from outside context:

- Move the highest-value prior chats into the project where eligible.
- Create summaries for chats that cannot be moved.
- Promote durable content into canonical artifacts.
- Upload critical source documents.
- Create a consolidated Baseline Decision Register.
- Verify that no foundational decision exists only outside the project.

---

# 11. Canonical Artifact Architecture

Canonical artifacts are organized into eight families.

## Family A — Foundation and Navigation

- Enterprise Performance Model Master Index.
- Project Charter and Operating Model.
- Business Glossary.
- Source and Traceability Register.
- Architecture Decision Log.
- Open Issues and Assumptions Log.

## Family B — Business Architecture

- Downstream Value Stream Model.
- Business Capability Map.
- Business Process and Activity Model.
- Business Objective and Decision Model.
- Domain Ownership Register.

## Family C — Measurement and KPI

- Enterprise Measurement Taxonomy.
- Tableau Calculation Inventory.
- Enterprise Measurement Catalog.
- Candidate KPI Register.
- Enterprise KPI Catalog.
- KPI Dependency and Driver Model.
- KPI Governance and Approval Standard.

## Family D — KPI Store Technical Architecture

- KPI Store Conceptual Architecture.
- KPI Store Logical Data Model.
- KPI Store Physical Design.
- KPI Metadata Schema.
- KPI Calculation and Load Framework.
- Target and Threshold Standard.
- Versioning and Restatement Standard.
- KPI Data-Quality Framework.
- KPI Security and Consumption Standard.
- KPI Pilot Specifications.

## Family E — Data Products and Semantics

- Data Product Portfolio.
- Data Product Standard and Contract Template.
- Data Portfolio-to-Capability Map.
- Semantic Model Standards.
- Shared Dimensions and Reference Data Standard.
- Power BI Consumption and Certification Standard.

## Family F — Domain Modeling

- Domain Modeling Playbook.
- Domain Modeling Reference Architecture.
- Modeling Standards and Conventions.
- Modeling Input and Output Specification.
- Domain Model Repository.
- Proof-of-Value Model Packages.
- KPI-to-Domain Traceability Model.

## Family G — System Integration

- System Integration Reference Architecture.
- Tool Responsibility Matrix.
- Metadata Flow and Sequence Diagrams.
- Integration Pattern Catalog.
- Payload and Contract Specifications.
- Tool Constraints and Risk Register.
- System Integration Proof-of-Value Package.

## Family H — Delivery and Adoption

- Delivery Backlog and Roadmap.
- Validation and Reconciliation Register.
- Stakeholder Review Log.
- Training and Change Plan.
- Adoption and Value Scorecard.
- Maturity Assessment.
- Executive Readouts.

---

# 12. Artifact Lifecycle and Change Control

## 12.1 Statuses

- Exploratory.
- Draft.
- Candidate.
- Approved Baseline.
- Implemented.
- Superseded.
- Retired.

## 12.2 Required metadata

Every canonical artifact should display:

- Artifact ID.
- Title.
- Version.
- Status.
- Owner.
- Steward.
- Last updated.
- Purpose.
- Scope.
- Source references.
- Related decisions.
- Dependencies.
- Change summary.
- Open issues.
- Review trigger.

## 12.3 Change rules

- Minor editorial changes may increment a minor version.
- Material semantic, scope, model, or technical changes require a decision record.
- Changes to an approved baseline must identify affected artifacts.
- Superseded artifacts must point to their replacement.
- Implemented artifacts must identify the validating implementation or release.

---

# 13. Operating Cadence

## Event-based

Triggered by:

- Data-quality incidents.
- KPI definition conflicts.
- Cross-domain semantic conflicts.
- Material implementation issues.
- Regulatory or compliance requests.
- Upstream or downstream process impacts.

## Monthly

Review:

- KPI onboarding and implementation.
- Calculation-classification progress.
- Data quality and issue resolution.
- Data-product performance.
- Metadata and lineage completeness.
- Open decisions.
- Adoption and usage.
- Digital delivery progress.

## Quarterly

Review:

- Domain priorities.
- KPI portfolio.
- Cross-domain dependencies.
- Reuse.
- Governance maturity.
- Value realization.
- Domain Modeling progress.
- System Integration proof-of-value progress.
- Major architecture changes.

## Strategic planning

Decide:

- Which initiatives drive the highest enterprise value.
- Which domains and KPI families to prioritize.
- Where to invest.
- Which foundational gaps to close.
- Which data products to scale, consolidate, or retire.
- Which maturity targets to adopt.

---

# 14. Delivery Sequence

## Phase 1 — Establish project controls

- Approve this operating model.
- Create the Master Index.
- Establish the Artifact Register.
- Create the Decision Log.
- Create the Source Register.
- Consolidate prior baseline decisions.

## Phase 2 — Define the KPI Store

- Define scope and boundaries.
- Define the measurement taxonomy.
- Define KPI qualification criteria.
- Define governance workflow.
- Define metadata and logical architecture.

## Phase 3 — Inventory and classify calculations

- Parse Tableau XML.
- Normalize calculations.
- Identify dependencies and duplicates.
- Compare with Power BI.
- Populate the Measurement Catalog.
- Identify candidate KPIs.

## Phase 4 — Govern and pilot KPIs

- Select pilot KPI families.
- Assign owners and stewards.
- Approve definitions and formulas.
- Define targets and thresholds.
- Implement and validate.
- Publish governed consumption views.

## Phase 5 — Domain Modeling re-drive

- Formalize business concepts and logical models.
- Map KPI and measurement concepts to model entities and attributes.
- Refine data-product and technical lineage.
- Update KPI metadata and traceability.

## Phase 6 — System Integration proof of value

- Demonstrate tool responsibilities.
- Exchange representative payloads.
- Validate metadata propagation.
- Document constraints and production recommendations.

## Phase 7 — Scale and operationalize

- Expand KPI families and domains.
- Automate onboarding and controls.
- Embed governance cadence.
- Extend consumption to applications, alerts, AI, and agents.
- Track adoption and business value.

---

# 15. Definition of Success

The project succeeds when the organization can answer:

- What is an enterprise KPI?
- Which Tableau calculations are KPIs, metrics, or technical logic?
- Who owns each KPI and its outcome?
- Which business objective, capability, process, and decision does it support?
- What is the approved definition and formula?
- Which measures feed it?
- What dimensions, time grain, unit, targets, and thresholds apply?
- Which data products and models supply it?
- Which technical fields contribute to it?
- Which reports and applications consume it?
- Which version is effective?
- How is it validated and monitored?
- Which definitions or calculations conflict?
- Which assets should be reused, consolidated, or retired?
- How can the trusted context be consumed by analytics, automation, and AI?

The final outcome is not merely a KPI table. It is a governed enterprise performance architecture that connects strategy, operations, measurement, data, technology, and decision-making.