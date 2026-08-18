# Canonical Artifact Register and Chat-to-Artifact Migration Playbook

**Artifact ID:** EPM-FOUND-002  
**Status:** Candidate  
**Version:** 1.0  
**Purpose:** Define the canonical document set, explain how chats are used, and provide the method for migrating durable knowledge from previous and current conversations into governed artifacts.

---

# 1. Why this artifact exists

Chats are excellent for exploration, learning, clarification, alignment, analysis, and drafting. They are poor as the sole long-term system of record because:

- Decisions are distributed across messages.
- Later discussion can contradict earlier discussion.
- Definitions may evolve without an explicit version.
- Important conclusions may be hard to locate.
- A conversation may mix approved decisions with temporary hypotheses.
- Other contributors may not know which message is authoritative.

The project will therefore use:

- **Chats for working and reasoning.**
- **Canonical artifacts for durable knowledge.**
- **Decision logs for material choices.**
- **Source registers for traceability.**
- **Catalogs for structured inventories.**

---

# 2. Recommended project setup

## 2.1 Project Instructions

Place the compact “Enterprise Performance Model — Project Instructions” text in Project Settings.

Its job is to tell ChatGPT:

- The project mission.
- The current baseline.
- The priority sequence.
- How to use chats.
- How to use prior context.
- How to classify measurements.
- How to route conclusions into artifacts.
- How to handle conflicts and changes.

Do not place the full operating model in the instruction field unless there is no other option. The instruction field should govern behavior; project-source documents should carry detailed content.

## 2.2 Project sources

Add the following as project sources:

1. Project Charter and Operating Model.
2. Canonical Artifact Register and Chat Migration Playbook.
3. Enterprise Performance Model Master Index.
4. Architecture Decision Log.
5. Source and Traceability Register.
6. Business Glossary and Measurement Taxonomy.
7. Current KPI Store Technical Design.
8. Current business architecture and data-portfolio documents.
9. Domain Modeling scope and reference materials.
10. System Integration scope and reference materials.

## 2.3 Chats

Create focused chats rather than one endless thread.

Suggested prefixes:

- `KPI |`
- `XML |`
- `BUSINESS |`
- `MODEL |`
- `INTEGRATION |`
- `GOVERNANCE |`
- `DECISION |`
- `DELIVERABLE |`
- `RESEARCH |`
- `LEARNING |`

---

# 3. Canonical Artifact Register

The table below defines the minimum controlled artifact set.

| ID | Artifact | Purpose | Primary content | Updated when |
|---|---|---|---|---|
| EPM-FOUND-000 | Enterprise Performance Model Master Index | Navigation and current-state overview | Scope, architecture map, artifact links, maturity, priorities | Any major artifact is added, retired, or materially changed |
| EPM-FOUND-001 | Project Charter and Operating Model | Defines scope, workstreams, roles, lifecycle, and cadence | Mission, boundaries, governance, delivery sequence | Scope, roles, priority, or operating method changes |
| EPM-FOUND-002 | Artifact Register and Chat Migration Playbook | Controls knowledge capture | Artifact inventory, routing, migration method | Artifact set or knowledge-management method changes |
| EPM-GLOS-001 | Business Glossary | Establishes shared business meaning | Terms, definitions, synonyms, owners, status | A term is introduced, challenged, or approved |
| EPM-MEAS-001 | Enterprise Measurement Taxonomy | Defines measurement classes and rules | Taxonomy, classification tests, examples | Classification policy changes |
| EPM-SRC-001 | Source and Traceability Register | Records where knowledge originated | Chat/file/source, date, topic, reliability, affected artifacts | New source evidence is used |
| EPM-DEC-001 | Architecture Decision Log | Records material decisions | Context, options, decision, rationale, consequences | A material decision is made or superseded |
| EPM-ISS-001 | Open Issues and Assumptions Log | Prevents hidden uncertainty | Issue, assumption, owner, impact, due date, status | Uncertainty or conflict is identified |
| EPM-BUS-001 | Downstream Value Stream Model | Defines enterprise value creation | Value streams, stages, outcomes, interactions | Value-stream structure changes |
| EPM-BUS-002 | Business Capability Map | Organizes business responsibilities | Domains, capabilities, owners, dependencies | Capability scope changes |
| EPM-BUS-003 | Business Process and Activity Model | Provides process context | Processes, activities, decisions, controls | Process knowledge is added or corrected |
| EPM-BUS-004 | Business Objective and Decision Model | Links strategy to decisions | Objectives, outcomes, decisions, interventions | KPI purpose or management action changes |
| EPM-XML-001 | Tableau Calculation Inventory | Preserves extracted legacy logic | Workbook, view, calculation, formula, dependencies, use | New XML is parsed or normalized |
| EPM-MEAS-002 | Enterprise Measurement Catalog | Governs reusable non-KPI measures | Definition, formula, grain, dimensions, owner, lineage | A measure is approved, changed, or retired |
| EPM-KPI-001 | Candidate KPI Register | Manages KPI review pipeline | Candidate, rationale, owner, gaps, status | A candidate is identified or reviewed |
| EPM-KPI-002 | Enterprise KPI Catalog | System of record for approved KPI definitions | Definition, formula, target, thresholds, owner, dimensions, lineage | A KPI is approved, revised, or retired |
| EPM-KPI-003 | KPI Dependency and Driver Model | Shows how KPIs are formed and explained | Inputs, drivers, diagnostic metrics, causal hypotheses | KPI logic or drivers change |
| EPM-KPI-004 | KPI Governance and Approval Standard | Defines governance workflow | Roles, gates, required evidence, approval states | Governance process changes |
| EPM-KPI-010 | KPI Store Conceptual Architecture | Explains what the store is and is not | Components, boundaries, logical flow | Scope or architecture changes |
| EPM-KPI-011 | KPI Store Logical Data Model | Defines logical structures and relationships | Entities, keys, relationships, cardinality | Logical model changes |
| EPM-KPI-012 | KPI Store Physical Design | Defines implementation schemas | Tables, views, indexes, partitions, security | Physical implementation changes |
| EPM-KPI-013 | KPI Metadata Schema | Defines required KPI metadata | Fields, types, validations, provenance | Metadata requirements change |
| EPM-KPI-014 | KPI Calculation and Load Framework | Defines computation and ingestion | Configuration, orchestration, backfill, daily loads | Calculation/load patterns change |
| EPM-KPI-015 | Target, Threshold, and Status Standard | Standardizes performance evaluation | Targets, warnings, direction, effective dating | Evaluation rules change |
| EPM-KPI-016 | Versioning and Restatement Standard | Controls changes over time | Versions, corrections, current record, audit | Version/restatement policy changes |
| EPM-KPI-017 | KPI Data-Quality Framework | Defines quality controls | Rules, tolerances, monitoring, issue workflow | Quality requirements change |
| EPM-KPI-018 | KPI Security and Consumption Standard | Defines governed access and reuse | Views, RLS, APIs, semantic access, certification | Consumption or security changes |
| EPM-KPI-019 | KPI Pilot Specification Package | Provides implementable KPI designs | One specification per pilot KPI family | Pilot requirements or implementation change |
| EPM-DP-001 | Data Product Portfolio | Catalogs governed products | Purpose, owner, consumers, assets, quality, value | Product is created, changed, or retired |
| EPM-DP-002 | Data Product Standard and Contract Template | Defines what qualifies as a product | Required metadata, interfaces, SLAs, quality | Product standard changes |
| EPM-SEM-001 | Semantic Model Standards | Controls reusable semantic logic | Dimensions, measures, naming, security, testing | Semantic standards change |
| EPM-SEM-002 | Power BI Consumption and Certification Standard | Governs report consumption | Thin-report expectations, certification, local logic | Consumption policy changes |
| EPM-MOD-001 | Domain Modeling Playbook | Defines repeatable modeling method | Steps, roles, inputs, outputs, gates | Modeling method changes |
| EPM-MOD-002 | Domain Modeling Reference Architecture | Shows modeling ecosystem | Business concepts, catalog, models, fields | Reference architecture changes |
| EPM-MOD-003 | Modeling Standards and Conventions | Standardizes models | Naming, keys, relationships, levels, patterns | Modeling standards change |
| EPM-MOD-004 | Domain Model Repository | Stores approved conceptual/logical models | Entities, attributes, relationships, definitions | A model is created or changed |
| EPM-MOD-005 | KPI-to-Domain Traceability Model | Connects KPIs to formal domain models | KPI, measure, concept, entity, attribute, field | Domain re-drive adds or changes mappings |
| EPM-INT-001 | System Integration Reference Architecture | Defines the connected ecosystem | Systems, responsibilities, flows, boundaries | Integration architecture changes |
| EPM-INT-002 | Tool Responsibility Matrix | Prevents overlapping ownership | Purview, Unity Catalog, ER/Studio, BigEye responsibilities | Tool responsibilities change |
| EPM-INT-003 | Integration Pattern Catalog | Defines reusable technical patterns | Push, pull, event, batch, API, file, identifier patterns | A pattern is introduced or revised |
| EPM-INT-004 | Metadata Flow and Sequence Diagrams | Shows propagation across systems | Source, destination, payload, trigger, failure handling | Integration flow changes |
| EPM-INT-005 | Payload and Contract Specifications | Defines exchange structures | Schemas, fields, examples, versioning | Payload changes |
| EPM-INT-006 | Tool Constraints and Risk Register | Records limitations | Constraint, impact, mitigation, owner | A limitation is discovered or resolved |
| EPM-DEL-001 | Delivery Backlog and Roadmap | Controls sequencing | Epics, tasks, dependencies, milestones | Priorities or dates change |
| EPM-VAL-001 | Validation and Reconciliation Register | Preserves validation evidence | Test, expected, actual, result, approver | Validation is executed |
| EPM-CHG-001 | Training and Change Plan | Supports adoption | Audiences, learning, communications, reinforcement | Adoption plan changes |
| EPM-VALUE-001 | Adoption and Value Scorecard | Measures outcomes | Usage, quality, time saved, value, maturity | Reporting cycle completes |

---

# 4. Artifact Families and Boundaries

## 4.1 Foundation artifacts

These answer:
- What is the project?
- What is authoritative?
- What changed?
- What is unresolved?
- Where did the information come from?

## 4.2 Business architecture artifacts

These answer:
- How does the business create value?
- Which domain or capability owns the outcome?
- Which process and activity are being measured?
- Which decision is supported?

## 4.3 Measurement and KPI artifacts

These answer:
- What was calculated?
- What does it mean?
- Is it a measure, metric, indicator, or KPI?
- Is it governed?
- What feeds it?

## 4.4 Technical KPI Store artifacts

These answer:
- How is the KPI represented, calculated, stored, versioned, validated, secured, and consumed?

## 4.5 Data-product and semantic artifacts

These answer:
- Which reusable product supplies the data?
- Which semantic model owns the reusable measure?
- How should Power BI consume it?

## 4.6 Domain Modeling artifacts

These answer:
- Which business concepts, entities, attributes, and relationships represent the domain?
- How does the KPI map to those models?

## 4.7 System Integration artifacts

These answer:
- Which tool owns which metadata?
- How does metadata move?
- What payload and identifier patterns are used?
- What constraints exist?

## 4.8 Delivery and adoption artifacts

These answer:
- What happens next?
- What has been validated?
- Who needs to adopt it?
- What value is being realized?

---

# 5. Chat-to-Artifact Routing Matrix

| Chat outcome | Target artifact |
|---|---|
| New project scope or priority | Project Charter and Operating Model |
| New definition or terminology | Business Glossary |
| New measurement class or classification rule | Enterprise Measurement Taxonomy |
| Extracted Tableau calculation | Tableau Calculation Inventory |
| Reusable normalized metric | Enterprise Measurement Catalog |
| Candidate KPI | Candidate KPI Register |
| Approved KPI | Enterprise KPI Catalog |
| KPI driver or supporting measure relationship | KPI Dependency and Driver Model |
| New KPI approval requirement | KPI Governance and Approval Standard |
| New database or metadata design | KPI Store Logical/Physical Design or Metadata Schema |
| New threshold or status rule | Target, Threshold, and Status Standard |
| New restatement policy | Versioning and Restatement Standard |
| New data-quality rule | KPI Data-Quality Framework |
| New domain, capability, process, or activity | Business Architecture artifacts |
| New data product | Data Product Portfolio |
| New semantic modeling rule | Semantic Model Standards |
| New conceptual/logical model | Domain Model Repository |
| KPI mapped to entity or attribute | KPI-to-Domain Traceability Model |
| New tool responsibility | Tool Responsibility Matrix |
| New metadata flow | Metadata Flow and Sequence Diagrams |
| New payload | Payload and Contract Specifications |
| Material choice between alternatives | Architecture Decision Log |
| Unresolved conflict or assumption | Open Issues and Assumptions Log |
| External chat, file, or research used | Source and Traceability Register |
| New delivery action or dependency | Delivery Backlog and Roadmap |
| Validation evidence | Validation and Reconciliation Register |

---

# 6. Conversation Closeout Template

Use this at the end of a substantial project chat.

## Conversation Closeout

**Chat title:**  
**Date:**  
**Workstream:** KPI Store / Domain Modeling / System Integration / Governance / Other  
**Primary artifact being advanced:**  

### 1. Purpose
What question or problem did the chat address?

### 2. Baseline used
Which approved artifacts, prior chats, files, or implementations were treated as the starting point?

### 3. Conclusions
What durable understanding was reached?

### 4. Decisions
What was explicitly decided? Identify whether each decision is proposed, candidate, or approved.

### 5. Definitions
Which terms or definitions were added, clarified, or changed?

### 6. Assumptions
Which assumptions remain and what evidence is needed?

### 7. Open questions
What is unresolved?

### 8. Conflicts
Which sources, definitions, formulas, or designs disagree?

### 9. Artifact updates
For each affected artifact, specify:
- Artifact ID and title.
- Section to update.
- Proposed change.
- Suggested new version.
- Suggested status.

### 10. Source traceability
List the chats, files, reports, workbooks, systems, or research sources used.

### 11. Validation
Who must validate the conclusion and what evidence is required?

### 12. Next action
What should happen next, by whom, and in which workstream?

---

# 7. Previous-Chat Migration Procedure

## Step 1 — Inventory prior chats

Create an initial list of prior conversations by theme:

- KPI Store architecture.
- Tableau XML extraction.
- Power BI semantic models.
- Downstream business architecture.
- Commercial domains.
- Refining.
- Midstream.
- Corporate.
- Data portfolios.
- Data products.
- Governance.
- Purview.
- Domain Modeling.
- System Integration.
- AI opportunities.

## Step 2 — Prioritize

Use these priority levels:

### Priority A — Move or summarize immediately
Chats containing:
- Approved architecture.
- Table designs.
- Final business definitions.
- Explicit stakeholder decisions.
- KPI formulas.
- Governance decisions.
- Scope commitments.
- Important constraints.

### Priority B — Migrate during relevant workstream
Chats containing:
- Detailed domain research.
- Process and capability models.
- Supporting metric inventories.
- Alternative designs.
- Implementation examples.

### Priority C — Retain as reference only
Chats containing:
- General learning.
- Early brainstorming.
- Superseded ideas.
- Context that does not affect a canonical artifact.

## Step 3 — Extract durable content

For each chat, identify:

- Final decisions.
- Candidate decisions.
- Definitions.
- Formulas.
- Data models.
- Constraints.
- Assumptions.
- Open questions.
- Stakeholders.
- Sources.
- Superseded content.

## Step 4 — Reconcile

Compare the extracted content with:

- Approved artifacts.
- Current implementation.
- Newer decisions.
- Other prior chats.

Do not merge contradictions silently.

## Step 5 — Promote

Update the appropriate canonical artifacts.

A prior chat is not considered migrated merely because it was moved into the project. Migration is complete when its durable content is reflected in the appropriate artifacts and source register.

## Step 6 — Record provenance

Add an entry to the Source and Traceability Register:

- Source title.
- Source type.
- Date.
- Original location.
- Topics.
- Reliability or status.
- Artifacts updated.
- Decisions extracted.
- Conflicts.
- Migration date.

## Step 7 — Close

Mark the source as:
- Fully migrated.
- Partially migrated.
- Reference only.
- Superseded.
- Requires validation.

---

# 8. Source and Traceability Register Template

| Source ID | Source title | Type | Date | Topic | Status/reliability | Key conclusions | Decisions found | Conflicts | Artifacts affected | Migration status |
|---|---|---|---|---|---|---|---|---|---|---|

Suggested source types:
- Project chat.
- Outside-project chat.
- Uploaded file.
- Business workshop.
- Tableau workbook.
- Power BI model.
- Source-system analysis.
- Approved specification.
- Technical implementation.
- External research.
- Architecture inference.

---

# 9. Architecture Decision Log Template

| Decision ID | Date | Title | Status | Context | Options | Decision | Rationale | Consequences | Owner | Affected artifacts | Review trigger |
|---|---|---|---|---|---|---|---|---|---|---|---|

Decision statuses:
- Proposed.
- Candidate.
- Approved.
- Implemented.
- Superseded.
- Rejected.

---

# 10. Open Issues and Assumptions Template

| Item ID | Type | Description | Impact | Evidence needed | Owner | Due/review date | Status | Affected artifacts |
|---|---|---|---|---|---|---|---|---|

Types:
- Open question.
- Assumption.
- Conflict.
- Dependency.
- Risk.
- Constraint.

---

# 11. Practical Operating Rules

1. Start each major chat by naming the workstream and target artifact.
2. Retrieve baseline context before producing a new design.
3. Keep exploration in the chat.
4. Record durable conclusions in the closeout.
5. Update canonical artifacts at defined milestones.
6. Record material decisions separately.
7. Record unresolved uncertainty separately.
8. Preserve the origin of every important definition or design.
9. Do not assume moving a chat equals migrating its content.
10. Before sharing or isolating the project, consolidate all Priority A external chats.
11. Review the artifact register monthly.
12. Review the decision log and open issues at every governance checkpoint.
13. Update the Master Index whenever an artifact is added, superseded, or approved.
14. Use catalogs for structured records and narrative documents for standards, rationale, and architecture.
15. Keep the KPI Store as the first delivery priority while designing it for later Domain Modeling and System Integration enrichment.

---

# 12. Initial Project Source Package

The minimum first package should contain:

1. Project Instructions.
2. Project Charter and Operating Model.
3. This Artifact Register and Migration Playbook.
4. Master Index.
5. Decision Log.
6. Source and Traceability Register.
7. Open Issues and Assumptions Log.
8. Business Glossary and Measurement Taxonomy.
9. Existing KPI Store Technical Design.
10. Current Downstream business architecture.
11. Current Tableau extraction results or inventory.
12. Domain Modeling scope materials.
13. System Integration scope materials.

This package creates a stable baseline while allowing chats to remain flexible working spaces.