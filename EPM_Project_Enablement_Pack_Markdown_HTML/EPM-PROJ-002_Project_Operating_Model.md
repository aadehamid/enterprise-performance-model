# Enterprise Performance Project Operating Model
**Artifact:** EPM-PROJ-002_Project_Operating_Model  
**Version:** 1.0 Draft  
**Status:** Working Baseline  
**Updated:** August 4, 2026  

*How chats, artifacts, decisions, reviews, and implementation work together*

## Operating philosophy
The project should function like an architecture repository supported by working conversations.

- Chats are temporary workspaces for exploration.
- Canonical artifacts preserve approved knowledge.
- Implementation assets operationalize approved architecture.
- Decision records explain significant changes.
- The Master Index provides navigation and status.

## Project structure
```text
Enterprise Performance Project
├── Project Instructions
├── Foundation
│   ├── EPM-FOUND-000 Master Index
│   ├── EPM-FOUND-000A Architectural Principles
│   ├── EPM-FOUND-001 Business Architecture
│   ├── EPM-FOUND-002 Performance and Data Architecture
│   ├── EPM-FOUND-003 Semantic Model
│   ├── EPM-FOUND-004 Ontology Design
│   ├── EPM-FOUND-005 Measurement and KPI Model
│   └── EPM-FOUND-006 Data Product and Consumption Model
├── Domain Models
│   ├── Commercial
│   ├── Refining
│   ├── Midstream
│   └── Corporate
├── KPI and Measurement
│   ├── Measurement Catalog
│   ├── KPI Catalog
│   ├── KPI Specifications
│   └── Threshold Specifications
├── Data Products
│   ├── Foundational Products
│   ├── Derived Products
│   └── Consumer Contracts
├── Migration
│   ├── Tableau Inventory
│   ├── Classification Results
│   ├── Power BI Reconciliation
│   └── Retirement Decisions
├── Ontology and Knowledge Graph
├── Technical Design
├── Decision Records
├── Working Chats
└── Outputs and Readouts
```

## Recommended chat taxonomy
Use focused chats instead of one giant project conversation.

| Chat | Purpose |
|---|---|
| EPM Foundation Governance | Definitions, principles, cross-architecture decisions |
| KPI Store Design | Tables, thresholds, versioning, loads, DQ, semantic exposure |
| Measurement Classification | Tableau calculations, duplicates, metric/KPI decisions |
| Commercial Business Architecture | Value streams, capabilities, processes, decisions |
| Commercial Performance Model | Objectives, metrics, KPIs, causal relationships |
| Refining Performance Model | Refining capabilities, processes, metrics, KPIs |
| Midstream Performance Model | Pipelines, terminals, storage, logistics metrics |
| Domain Modeling | Conceptual and logical models |
| Ontology Design | Classes, properties, constraints, competency questions |
| Data Product Portfolio | Foundational and derived product definitions |
| Semantic and Consumption Layer | SQL semantic views and consumer contracts |
| Power BI Standards | Semantic-model design and report standards |
| System Integration | Purview, YAML, metadata, lineage, APIs, graph integration |
| Executive Readouts | CIO, CTO, governance council, and steering materials |

## Canonical artifact rule
A chat conclusion is not automatically an approved architecture decision.

A conclusion becomes canonical when:

1. The decision is clearly stated.
2. Assumptions and alternatives are recorded.
3. The responsible owner or governance forum accepts it.
4. The relevant artifact is updated.
5. Downstream implementation impacts are identified.
6. The Master Index or decision log is updated.

## Decision record template
```markdown
# EPM-ADR-### — Decision Title

## Status
Proposed | Accepted | Superseded | Retired

## Date

## Context

## Decision

## Rationale

## Alternatives considered

## Consequences

## Affected artifacts

## Affected implementations

## Owner and approvers
```

## Artifact lifecycle
| State | Meaning |
|---|---|
| Draft | Under development; not authoritative |
| Working Baseline | Used provisionally for active work |
| Proposed | Submitted for review |
| Approved | Authoritative within stated scope |
| Superseded | Replaced by a newer artifact or version |
| Retired | No longer valid or required |

Every artifact should have an ID, title, version, status, owner, date, scope, and dependencies.

## Review cadence
Recommended cadence:

- Weekly working review for active pilots
- Biweekly architecture and governance review
- Monthly program operating review
- Quarterly foundation and principles review
- Event-driven review when major business, platform, or governance changes occur

## Definition of done for an architecture artifact
An artifact is complete enough for approval when it has:

- clear purpose and scope;
- definitions and relationships;
- assumptions and exclusions;
- examples;
- decisions and open questions;
- ownership;
- dependencies;
- implementation implications;
- traceability;
- version and status;
- and identified review or approval forum.

## Definition of done for a KPI
A KPI is production-ready when:

- objective and owner are approved;
- definition and formula are approved;
- grain, dimensions, unit, and time behavior are defined;
- targets and thresholds are approved;
- source data and lineage are established;
- data quality controls pass;
- backfill and daily refresh are reconciled;
- KPI Store load is operational;
- semantic view is certified;
- Power BI consumption is validated;
- monitoring and issue ownership are assigned.
