# Enterprise Performance Model Master Index
**Artifact ID:** EPM-FOUND-000  
**Version:** 0.1  
**Status:** Draft  
**Owner:** Enterprise Performance Model Lead  
**Steward / maintainer:** To be confirmed  
**Last updated:** July 28, 2026  
**Review trigger:** Creation, approval, supersession, retirement, or material change of a major project artifact.
> This is the maintainable source companion to the self-contained HTML project-facing artifact.
## 1. Executive Orientation

The Enterprise Performance Model connects **business objectives → value streams → domains and capabilities → processes and activities → measurements → KPIs → data products → domain models → technical assets → reporting, analytics, automation, and AI**.

The Tableau reports in scope have already been migrated to Power BI. KPI definitions, ownership, targets, thresholds, lineage, and standardization were not systematically captured during migration. Tableau XML is now parsed retrospectively; extracted calculations are historical evidence, not approved KPIs. Power BI reports and semantic models are current validation and consumption sources. The KPI Store is the first delivery priority; Domain Modeling and System Integration are connected follow-on workstreams; Data Governance is cross-cutting.
## 2. Project Scope and Boundaries

- **KPI Store and EPM:** measurement taxonomy, inventory, catalogs, governance, metadata, calculation/value/consumption layers, quality, lineage, and pilots. Excludes treating every report calculation as a KPI or rebuilding all reports.
- **Domain Modeling:** tool-agnostic playbook, reference architecture, standards, lifecycle, and targeted proofs of value. Excludes broad physicalization and production build-out.
- **System Integration:** responsibilities, flows, patterns, payloads, constraints, and targeted proofs across ER/Studio, Purview, Unity Catalog, and BigEye. Excludes broad production integration.
- **Data Governance:** ownership, semantics, metadata, lineage, quality, security, compliance, reuse, adoption, and value across all workstreams.

Detailed authority: **EPM-FOUND-001 — Project Charter and Operating Model, Version 2.0, Candidate.**
## 3. Enterprise Performance Model Architecture

Governance spans every layer: ownership, metadata, lineage, quality, security, lifecycle, and change control. Governed consumers include Power BI, analytics, applications, automation and alerts, and AI/agents.
## 4. Workstream Overview

| Workstream | Priority | Status | Next milestone |
|---|---|---|---|
| KPI Store and Enterprise Performance Management | First | In progress | Confirm measurement and conceptual architecture; select first pilot |
| Domain Modeling | Follow-on and iterative | Exploratory | Locate scope materials; define proof-of-value domain |
| System Integration | Follow-on | Exploratory | Confirm proof scope; create tool responsibility matrix |
| Cross-cutting Data Governance | All phases | In progress | Create decision, source, and issue registers |
## 5. Current Delivery Sequence

1. Define the KPI Store and measurement architecture.
2. Inventory and classify Tableau calculations.
3. Establish KPI governance and pilot KPIs.
4. Formalize Domain Modeling and reconnect models to the KPI Store.
5. Define and prove System Integration patterns.
6. Scale and operationalize.
## 6. Canonical Artifact Directory

> Appearance in the register means planned in the minimum controlled set; it does not prove that a file exists.

| ID | Artifact | Family | Purpose | Owner | Version | Status | Role | Dependencies | Location | Next action |
|---|---|---|---|---|---|---|---|---|---|---|
| EPM-FOUND-000 | Enterprise Performance Model Master Index | Foundation and Navigation | Navigation and current-state overview | Enterprise Performance Model Lead | 0.1 | Draft | Navigation and control | EPM-FOUND-001; EPM-FOUND-002; all major artifact status updates | This document | Validate Version 0.1; add project links; update after control artifacts are created |
| EPM-FOUND-001 | Project Charter and Operating Model | Foundation and Navigation | Defines scope, workstreams, roles, lifecycle, and cadence | Enterprise Performance Model Lead | 2.0 | Candidate | Authoritative scope and operating model when approved | Executive and governance validation | Reviewed source; project source link to be added | Governance review and decision on approval baseline |
| EPM-FOUND-002 | Artifact Register and Chat Migration Playbook | Foundation and Navigation | Controls knowledge capture | To be confirmed | 1.0 | Candidate | Authoritative artifact and knowledge-control model when approved | Agreement on artifact controls and migration method | Reviewed source; project source link to be added | Confirm owner; governance review; approve or revise |
| EPM-GLOS-001 | Business Glossary | Foundation and Navigation | Establishes shared business meaning | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Approved priorities; stakeholder capacity; validation evidence | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-MEAS-001 | Enterprise Measurement Taxonomy | Measurement and KPI | Defines measurement classes and rules | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Measurement taxonomy; source evidence; business ownership; validation | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-SRC-001 | Source and Traceability Register | Foundation and Navigation | Records where knowledge originated | To be confirmed | To be confirmed | Not started | Authoritative provenance record when established | Project control setup; owners and review cadence | Project source link to be added | Create and populate immediately as a Phase 1 control |
| EPM-DEC-001 | Architecture Decision Log | Foundation and Navigation | Records material decisions | To be confirmed | To be confirmed | Not started | Authoritative decision record when established | Project control setup; owners and review cadence | Project source link to be added | Create and populate immediately as a Phase 1 control |
| EPM-ISS-001 | Open Issues and Assumptions Log | Foundation and Navigation | Prevents hidden uncertainty | To be confirmed | To be confirmed | Not started | Authoritative uncertainty record when established | Project control setup; owners and review cadence | Project source link to be added | Create and populate immediately as a Phase 1 control |
| EPM-BUS-001 | Downstream Value Stream Model | Business Architecture | Defines enterprise value creation | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | Existing Downstream architecture sources; process-owner validation | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-BUS-002 | Business Capability Map | Business Architecture | Organizes business responsibilities | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | Existing Downstream architecture sources; process-owner validation | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-BUS-003 | Business Process and Activity Model | Business Architecture | Provides process context | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | Existing Downstream architecture sources; process-owner validation | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-BUS-004 | Business Objective and Decision Model | Business Architecture | Links strategy to decisions | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | Existing Downstream architecture sources; process-owner validation | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-XML-001 | Tableau Calculation Inventory | Measurement and KPI | Preserves extracted legacy logic | To be confirmed | To be confirmed | In progress | Supporting evidence inventory | Tableau XML parser outputs; normalization rules; Power BI comparison | Current extraction output location to be confirmed | Locate current outputs; define inventory schema; classify first calculation cohort |
| EPM-MEAS-002 | Enterprise Measurement Catalog | Measurement and KPI | Governs reusable non-KPI measures | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Measurement taxonomy; source evidence; business ownership; validation | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-KPI-001 | Candidate KPI Register | Measurement and KPI | Manages KPI review pipeline | To be confirmed | To be confirmed | Not started | Governance workflow record | Measurement taxonomy; source evidence; business ownership; validation | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-KPI-002 | Enterprise KPI Catalog | Measurement and KPI | System of record for approved KPI definitions | To be confirmed | To be confirmed | Not started | Authoritative approved KPI system of record | Measurement taxonomy; source evidence; business ownership; validation | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-KPI-003 | KPI Dependency and Driver Model | Measurement and KPI | Shows how KPIs are formed and explained | To be confirmed | To be confirmed | Not started | Supporting explanatory model | Measurement taxonomy; source evidence; business ownership; validation | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-KPI-004 | KPI Governance and Approval Standard | Measurement and KPI | Defines governance workflow | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Measurement taxonomy; source evidence; business ownership; validation | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-KPI-010 | KPI Store Conceptual Architecture | KPI Store Technical Architecture | Explains what the store is and is not | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-011 | KPI Store Logical Data Model | KPI Store Technical Architecture | Defines logical structures and relationships | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-012 | KPI Store Physical Design | KPI Store Technical Architecture | Defines implementation schemas | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-013 | KPI Metadata Schema | KPI Store Technical Architecture | Defines required KPI metadata | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-014 | KPI Calculation and Load Framework | KPI Store Technical Architecture | Defines computation and ingestion | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-015 | Target, Threshold, and Status Standard | KPI Store Technical Architecture | Standardizes performance evaluation | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-016 | Versioning and Restatement Standard | KPI Store Technical Architecture | Controls changes over time | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-017 | KPI Data-Quality Framework | KPI Store Technical Architecture | Defines quality controls | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-018 | KPI Security and Consumption Standard | KPI Store Technical Architecture | Defines governed access and reuse | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-KPI-019 | KPI Pilot Specification Package | KPI Store Technical Architecture | Provides implementable KPI designs | To be confirmed | To be confirmed | Not started | Implementation specification package | KPI scope decision; resolved storage-pattern conflict; pilot requirements | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-DP-001 | Data Product Portfolio | Data Products and Semantic Models | Catalogs governed products | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | Current data-product portfolio; Power BI implementation evidence; owners | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-DP-002 | Data Product Standard and Contract Template | Data Products and Semantic Models | Defines what qualifies as a product | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Current data-product portfolio; Power BI implementation evidence; owners | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-SEM-001 | Semantic Model Standards | Data Products and Semantic Models | Controls reusable semantic logic | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Current data-product portfolio; Power BI implementation evidence; owners | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-SEM-002 | Power BI Consumption and Certification Standard | Data Products and Semantic Models | Governs report consumption | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Current data-product portfolio; Power BI implementation evidence; owners | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-MOD-001 | Domain Modeling Playbook | Domain Modeling | Defines repeatable modeling method | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI metadata requirements; selected proof-of-value domain; core tool constraints | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-MOD-002 | Domain Modeling Reference Architecture | Domain Modeling | Shows modeling ecosystem | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | KPI metadata requirements; selected proof-of-value domain; core tool constraints | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-MOD-003 | Modeling Standards and Conventions | Domain Modeling | Standardizes models | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | KPI metadata requirements; selected proof-of-value domain; core tool constraints | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-MOD-004 | Domain Model Repository | Domain Modeling | Stores approved conceptual/logical models | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | KPI metadata requirements; selected proof-of-value domain; core tool constraints | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-MOD-005 | KPI-to-Domain Traceability Model | Domain Modeling | Connects KPIs to formal domain models | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | KPI metadata requirements; selected proof-of-value domain; core tool constraints | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-INT-001 | System Integration Reference Architecture | System Integration | Defines the connected ecosystem | To be confirmed | To be confirmed | To be located | Authoritative within its subject area when approved | Tool responsibility decisions; representative payloads; proof-of-value scope | Prior source or artifact to be located | Locate prior artifact/evidence; assess currency; assign canonical ID and status |
| EPM-INT-002 | Tool Responsibility Matrix | System Integration | Prevents overlapping ownership | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Tool responsibility decisions; representative payloads; proof-of-value scope | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-INT-003 | Integration Pattern Catalog | System Integration | Defines reusable technical patterns | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Tool responsibility decisions; representative payloads; proof-of-value scope | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-INT-004 | Metadata Flow and Sequence Diagrams | System Integration | Shows propagation across systems | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Tool responsibility decisions; representative payloads; proof-of-value scope | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-INT-005 | Payload and Contract Specifications | System Integration | Defines exchange structures | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Tool responsibility decisions; representative payloads; proof-of-value scope | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-INT-006 | Tool Constraints and Risk Register | System Integration | Records limitations | To be confirmed | To be confirmed | Not started | Authoritative within its subject area when approved | Tool responsibility decisions; representative payloads; proof-of-value scope | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-DEL-001 | Delivery Backlog and Roadmap | Delivery and Adoption | Controls sequencing | To be confirmed | To be confirmed | Not started | Delivery control | Approved priorities; stakeholder capacity; validation evidence | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-VAL-001 | Validation and Reconciliation Register | Delivery and Adoption | Preserves validation evidence | To be confirmed | To be confirmed | Not started | Supporting validation evidence | Approved priorities; stakeholder capacity; validation evidence | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-CHG-001 | Training and Change Plan | Delivery and Adoption | Supports adoption | To be confirmed | To be confirmed | Not started | Adoption support | Approved priorities; stakeholder capacity; validation evidence | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |
| EPM-VALUE-001 | Adoption and Value Scorecard | Delivery and Adoption | Measures outcomes | To be confirmed | To be confirmed | Not started | Outcome measurement | Approved priorities; stakeholder capacity; validation evidence | Project source link to be added | Confirm owner and sequence; create initial Draft when dependency is available |

## 7. Authoritative Baseline

- **Candidate canonical artifacts:** EPM-FOUND-001 v2.0 and EPM-FOUND-002 v1.0.
- **Current implementation / user-stated baseline:** Power BI migration complete; Power BI current validation and consumption environment.
- **Working baseline:** XML extraction is evidence only; KPI Store first under the EPM umbrella.
- **Candidate architecture:** Domain Modeling and System Integration follow-on scope.
- **Items requiring confirmation:** technical KPI Store pattern, artifact owners, source links, current implementation evidence, business architecture, data products, and pilot scope.
## 8. Major Decisions

No reviewed Architecture Decision Log exists; therefore, no item is labeled Approved solely from Candidate artifacts or chats. Working baselines include the EPM umbrella, KPI Store priority, completed Power BI migration, retrospective XML treatment, and Power BI validation role. Candidate positions include progressive domain-model enrichment, targeted integration proofs, and cross-cutting governance.
## 9. Current Priorities and Active Work

Current work is project control, XML calculation discovery, KPI Store architecture reconciliation, source location, owner confirmation, and first-pilot selection. Broad report rebuilding, enterprise physicalization, and broad production integration are deferred.
## 10. Open Issues, Assumptions, and Conflicts

**Material conflict:** prior KPI Store work alternates between a persisted tall KPI value fact and a semantic-view/no-central-value-store model. Resolve through current implementation evidence and an Architecture Decision Log entry. Other issues include missing ownership, missing source links, unvalidated formulas, absent control registers, and unconfirmed modeling/integration proof scope.
## 11. Source and Traceability Overview

Source precedence: (1) approved canonical artifact, (2) approved decision-log entry, (3) approved specification, (4) current validated implementation, (5) Candidate artifact, (6) working project chat, (7) prior/outside-project chat, (8) unvalidated Tableau XML/report logic, (9) general industry assumption.
## 12. Governance and Ownership Overview

The Charter defines responsibilities for executive leadership, global process owners, Enterprise Data Governance, the EPM Lead, Domain Data Owners, Business KPI Owners, Data Product Owners, Data Stewards, Semantic Model Owners, and digital/engineering teams.
## 13. Artifact Status Dashboard

| Area | Status | Basis |
|---|---|---|
| Foundation and navigation | Draft | Master Index Draft; Charter and Register Candidate |
| Business architecture | To be confirmed | Prior materials not located |
| Measurement taxonomy and catalog | Exploratory | Seed taxonomy exists; catalog not started |
| Tableau calculation inventory | Exploratory | Parsing active; controlled artifact not reviewed |
| Candidate KPI governance | Not started | Register and standard not located |
| Enterprise KPI catalog | Not started | No approved catalog reviewed |
| KPI Store conceptual architecture | Exploratory | Competing historical patterns |
| KPI Store technical design | To be confirmed | Conflict unresolved; current implementation not reviewed |
| Data-product architecture | To be confirmed | Prior sources not located |
| Semantic-model standards | Not started | No governed standard located |
| Domain Modeling | Exploratory | Candidate scope only |
| System Integration | Exploratory | Candidate scope only |
| Delivery and adoption | Not started | Roadmap and registers not located |
## 14. How to Use This Index

Use the directory to find authority, EPM-DEC-001 for decisions, EPM-ISS-001 for uncertainty, EPM-SRC-001 for evidence, EPM-FOUND-002 for chat-to-artifact routing, and EPM-DEL-001 for sequencing once established.
## 15. Immediate Next Actions

1. Validate Version 0.1 and confirm maintainer.
2. Create/populate EPM-DEC-001, EPM-SRC-001, and EPM-ISS-001.
3. Locate prior KPI Store, business architecture, data-product, semantic, modeling, and integration artifacts.
4. Migrate Priority A KPI Store chats.
5. Resolve the persisted-store vs semantic-view conflict.
6. Confirm owners, versions, statuses, and links.
7. Locate and profile the Tableau inventory.
8. Advance EPM-MEAS-001 and EPM-KPI-010.
9. Select the first pilot KPI family.
10. Update this index after major artifact changes.
## Artifact Update Block

- **Conclusions:** Master Index created; strongest reviewed baseline is Candidate foundation artifacts plus current-state context.
- **Decisions and status:** No new approved decisions; working and Candidate baselines recorded.
- **Definitions added or changed:** Planned-register inclusion does not prove artifact existence.
- **Assumptions:** Prior sources exist but require location and classification.
- **Open questions and conflicts:** KPI value-store vs semantic-view pattern; ownership; approval; source links; inventory schema; pilot.
- **Source evidence:** Active project instructions; EPM-FOUND-001 v2.0 Candidate; EPM-FOUND-002 v1.0 Candidate; creation brief; accessible prior chats and KPI Store summaries.
- **Artifacts created or requiring updates:** EPM-FOUND-000 created; control registers required; major subject artifacts to locate/reconcile.
- **Suggested version and status:** 0.1 Draft.
- **Next validation or implementation action:** Create control registers and conduct the KPI Store architecture decision session.
