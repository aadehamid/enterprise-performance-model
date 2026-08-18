# EPM Chat Migration Playbook and Templates
**Artifact:** EPM-PROJ-006_Chat_Migration_Playbook_and_Templates
**Version:** 1.0 Draft
**Status:** Draft (working baseline)
**Updated:** 2026-08-05

*Routing, closeout, migration procedure, and control-log templates for turning chat work into governed artifacts*

**Project pack:** [EPM-FOUND-000A](EPM-FOUND-000A_Architectural_Principles.html) | [EPM-PROJ-001](EPM-PROJ-001_Project_Instructions.html) | [EPM-PROJ-002](EPM-PROJ-002_Project_Operating_Model.html) | [EPM-PROJ-003](EPM-PROJ-003_Project_Onboarding_Guide.html) | [EPM-PROJ-004](EPM-PROJ-004_Artifact_and_Chat_Map.html) | [EPM-PROJ-005](EPM-PROJ-005_Migration_Checklist.html) | [EPM-PROJ-006](EPM-PROJ-006_Chat_Migration_Playbook_and_Templates.html)

> **Provenance.** This artifact preserves the *Chat-to-Artifact Migration Playbook* half of the superseded Register (formerly EPM-FOUND-002 / the "Canonical Artifact Register and Chat Migration Playbook"). The Register's *inventory* half now lives in the Master Index (EPM-FOUND-000). The lighter onboarding and checklist material lives in EPM-PROJ-003 and EPM-PROJ-005. This document carries the operational method those two do not: the routing matrix, the conversation closeout template, the step-by-step migration procedure, and the control-log templates. See EPM-FOUND-000 §"Major decisions" (D-15) and §"Conflicts" (C-10).

## Purpose
Chats are working spaces. This playbook defines how durable knowledge produced in a chat becomes governed artifact content — and how prior or outside-project conversations are migrated in without losing traceability. The governing rule throughout: **moving a chat into the project is not the same as migrating it.** Migration is complete only when durable content is reflected in the appropriate canonical artifacts and recorded in the Source and Traceability Register.

## Chat-to-artifact routing matrix
When a chat produces a durable conclusion, route it to the correct canonical artifact.

| Chat outcome | Target artifact |
|---|---|
| New project scope or priority | Project Instructions / Operating Model (PROJ-001 / PROJ-002) |
| New definition or terminology | Business Glossary (GLOS-001) |
| New measurement class or classification rule | Enterprise Measurement and KPI Model (FOUND-005) |
| Extracted Tableau calculation | Tableau Calculation Inventory (XML-001) |
| Reusable normalized metric | Enterprise Measurement Catalog (MEAS-002) |
| Candidate KPI | Candidate KPI Register (KPI-001) |
| Approved KPI | Enterprise KPI Catalog (KPI-002) |
| KPI driver or supporting-measure relationship | KPI Dependency and Driver Model (KPI-003) |
| New KPI approval requirement | KPI Governance and Approval Standard (KPI-004) |
| New database or metadata design | KPI Store Logical/Physical Design or Metadata Schema (KPI-011/012/013) |
| New threshold or status rule | Target, Threshold, and Status Standard (KPI-015) |
| New restatement policy | Versioning and Restatement Standard (KPI-016) |
| New data-quality rule | KPI Data-Quality Framework (KPI-017) |
| New domain, capability, process, or activity | Business Architecture (FOUND-001 / BUS-001..004) |
| New data product | Data Product Portfolio (DP-001) |
| New semantic modeling rule | Semantic Model Standards (SEM-001) |
| New conceptual/logical model | Domain Model Repository (MOD-004) |
| KPI mapped to entity or attribute | KPI-to-Domain Traceability Model (MOD-005) |
| New tool responsibility | Tool Responsibility Matrix (INT-002) |
| New metadata flow | Metadata Flow and Sequence Diagrams (INT-004) |
| New payload | Payload and Contract Specifications (INT-005) |
| Material choice between alternatives | Architecture Decision Log (DEC-001) |
| Unresolved conflict or assumption | Open Issues and Assumptions Log (ISS-001) |
| External chat, file, or research used | Source and Traceability Register (SRC-001) |
| New delivery action or dependency | Delivery Backlog and Roadmap (DEL-001) |
| Validation evidence | Validation and Reconciliation Register (VAL-001) |

## Conversation closeout template
Use this at the end of a substantial project chat. It is the operational form of the "Artifact Update Block."

```text
Conversation Closeout

Chat title:
Date:
Workstream: KPI Store / Domain Modeling / System Integration / Governance / Other
Primary artifact being advanced:

1. Purpose        — What question or problem did the chat address?
2. Baseline used  — Which approved artifacts, prior chats, files, or implementations were the starting point?
3. Conclusions    — What durable understanding was reached?
4. Decisions      — What was decided? Mark each as proposed, candidate, or approved.
5. Definitions    — Which terms were added, clarified, or changed?
6. Assumptions    — Which assumptions remain, and what evidence is needed?
7. Open questions — What is unresolved?
8. Conflicts      — Which sources, definitions, formulas, or designs disagree?
9. Artifact updates — Per affected artifact: ID and title, section, proposed change, suggested version, suggested status.
10. Source traceability — Chats, files, reports, workbooks, systems, or research used.
11. Validation    — Who must validate, and what evidence is required?
12. Next action   — What happens next, by whom, in which workstream?
```

## Previous-chat migration procedure
A seven-step procedure for bringing prior or outside-project conversations into the governed baseline.

**Step 1 — Inventory prior chats.** List prior conversations by theme: KPI Store architecture; Tableau XML extraction; Power BI semantic models; downstream business architecture; Commercial, Refining, Midstream, Corporate; data portfolios and products; governance; Purview; Domain Modeling; System Integration; AI opportunities.

**Step 2 — Prioritize.**

- *Priority A — move or summarize immediately:* approved architecture, table designs, final business definitions, explicit stakeholder decisions, KPI formulas, governance decisions, scope commitments, important constraints.
- *Priority B — migrate during the relevant workstream:* detailed domain research, process and capability models, supporting-metric inventories, alternative designs, implementation examples.
- *Priority C — retain as reference only:* general learning, early brainstorming, superseded ideas, context that affects no canonical artifact.

**Step 3 — Extract durable content.** For each chat, identify final decisions, candidate decisions, definitions, formulas, data models, constraints, assumptions, open questions, stakeholders, sources, and superseded content.

**Step 4 — Reconcile.** Compare extracted content with approved artifacts, current implementation, newer decisions, and other prior chats. **Do not merge contradictions silently.**

**Step 5 — Promote.** Update the appropriate canonical artifacts. A prior chat is not migrated merely because it was moved into the project; migration is complete only when its durable content is reflected in the artifacts and the source register.

**Step 6 — Record provenance.** Add an entry to the Source and Traceability Register: source title, type, date, original location, topics, reliability/status, artifacts updated, decisions extracted, conflicts, migration date.

**Step 7 — Close.** Mark the source as fully migrated, partially migrated, reference only, superseded, or requires validation.

## Control-log templates
Concrete schemas for the three control logs that are still to be created (SRC-001, DEC-001, ISS-001). Statuses below use the canonical vocabularies reconciled in EPM-FOUND-000.

### Source and Traceability Register (SRC-001)
| Source ID | Source title | Type | Date | Topic | Status/reliability | Key conclusions | Decisions found | Conflicts | Artifacts affected | Migration status |
|---|---|---|---|---|---|---|---|---|---|---|

Source types: project chat; outside-project chat; uploaded file; business workshop; Tableau workbook; Power BI model; source-system analysis; approved specification; technical implementation; external research; architecture inference.

### Architecture Decision Log (DEC-001)
| Decision ID | Date | Title | Status | Context | Options | Decision | Rationale | Consequences | Owner | Affected artifacts | Review trigger |
|---|---|---|---|---|---|---|---|---|---|---|---|

**Decision statuses** (distinct from the artifact lifecycle): Proposed → Candidate → Approved → Implemented → Superseded → Rejected.

### Open Issues and Assumptions Log (ISS-001)
| Item ID | Type | Description | Impact | Evidence needed | Owner | Due/review date | Status | Affected artifacts |
|---|---|---|---|---|---|---|---|---|

Item types: open question; assumption; conflict; dependency; risk; constraint.

## Practical operating rules
1. Start each major chat by naming the workstream and target artifact.
2. Retrieve baseline context before producing a new design.
3. Keep exploration in the chat.
4. Record durable conclusions in the closeout.
5. Update canonical artifacts at defined milestones.
6. Record material decisions separately (DEC-001).
7. Record unresolved uncertainty separately (ISS-001).
8. Preserve the origin of every important definition or design (SRC-001).
9. Do not assume moving a chat equals migrating its content.
10. Before sharing or isolating the project, consolidate all Priority A external chats.
11. Review the artifact register monthly.
12. Review the decision log and open issues at every governance checkpoint.
13. Update the Master Index whenever an artifact is added, superseded, or approved.
14. Use catalogs for structured records and narrative documents for standards, rationale, and architecture.
15. Keep the KPI Store as the first delivery priority while designing it for later Domain Modeling and System Integration enrichment.

## Initial project source package
The minimum first package for a stable baseline:

1. Project Instructions (PROJ-001)
2. Project Operating Model (PROJ-002)
3. This Migration Playbook and Templates (PROJ-006)
4. Master Index (FOUND-000)
5. Architectural Principles (FOUND-000A)
6. Architecture foundation set (FOUND-001 to 006)
7. Decision Log (DEC-001) — to be created
8. Source and Traceability Register (SRC-001) — to be created
9. Open Issues and Assumptions Log (ISS-001) — to be created
10. Business Glossary and Measurement Taxonomy (GLOS-001)
11. Existing KPI Store Technical Design — to be located
12. Current Downstream business architecture — to be located
13. Current Tableau extraction results or inventory — to be located
14. Domain Modeling and System Integration scope materials — to be located

---
*Part of the Enterprise Performance Model project pack. Preserves migration method from the superseded Register.*
