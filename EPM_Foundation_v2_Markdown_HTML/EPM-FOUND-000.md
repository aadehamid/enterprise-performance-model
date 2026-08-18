# Enterprise Performance Model Master Index
**Artifact ID:** EPM-FOUND-000  
**Version:** 2.0 Draft  
**Status:** Working baseline  
**Last updated:** August 4, 2026  

*Repository home, architecture map, artifact directory, and delivery guide*

**Foundation navigation:** [EPM-FOUND-000](EPM-FOUND-000.md) | [EPM-FOUND-001](EPM-FOUND-001.md) | [EPM-FOUND-002](EPM-FOUND-002.md) | [EPM-FOUND-003](EPM-FOUND-003.md) | [EPM-FOUND-004](EPM-FOUND-004.md) | [EPM-FOUND-005](EPM-FOUND-005.md) | [EPM-FOUND-006](EPM-FOUND-006.md)

## Executive orientation
The **Enterprise Performance Model (EPM)** is the shared architecture that connects:

- how the downstream enterprise creates and delivers value;
- how business performance is observed, explained, and governed;
- how trusted data is organized into reusable products;
- how KPIs are defined, calculated, stored, and consumed; and
- how Power BI, APIs, automation, analytics, AI, and future agents use consistent business context.

The EPM is the conceptual umbrella. The KPI Store, ontology, knowledge graph, SQL consumption views, Power BI semantic models, reports, APIs, and AI agents are implementations or consumers of parts of that architecture.

> **Current program context:** Most in-scope Tableau reports have already been migrated to Power BI. During migration, KPI definitions, ownership, targets, thresholds, lineage, and standardization were not systematically captured. Tableau XML is now being parsed retrospectively to inventory calculations. Extracted calculations are historical evidence—not approved KPIs.

## Primary architecture chain
```text
Enterprise strategy and objectives
        ↓
Business domains
        ↓
Value streams and value-stream stages
        ↕ use
Capabilities and sub-capabilities
        ↓ realized through
Business processes
        ↓ decomposed into
Business activities
        ↓ support or produce
Business decisions
        ↓ observed through
Measurements and metrics
        ↓ governed as
KPIs and performance outcomes
        ↓ supplied by
Foundational and derived data products
        ↓ exposed through
KPI Store, semantic views, Power BI semantic models, APIs
        ↓ consumed by
Reports, analytics, automation, AI, and management processes
```

## Architecture families
| Architecture | Primary question | Core concepts | Canonical artifact |
|---|---|---|---|
| Business architecture | How does the enterprise create and deliver value? | Domain, value stream, stage, capability, process, activity, decision | EPM-FOUND-001 |
| Performance architecture | How is performance observed, explained, and governed? | Measurement, metric, indicator, KPI, objective, target, threshold | EPM-FOUND-002 and EPM-FOUND-005 |
| Semantic architecture | What do the concepts mean and how are they related? | Definitions, relationships, rules, constraints, classifications | EPM-FOUND-003 |
| Ontology architecture | How is the semantic model formalized for machines? | Classes, properties, cardinality, inheritance, axioms | EPM-FOUND-004 |
| Data-product architecture | How is trusted data packaged and delivered? | Foundational product, derived product, KPI Store, semantic view | EPM-FOUND-006 |
| Consumption architecture | How do people and systems use governed meaning and data? | SQL views, Power BI models, APIs, reports, agents | EPM-FOUND-006 |

## Workstreams and current sequence
| Workstream | Purpose | Priority | Current emphasis |
|---|---|---|---|
| KPI Store and Enterprise Performance Management | Govern metrics and KPIs; persist approved values, targets, status, versions, and lineage | Immediate | Measurement classification, pilot KPIs, tall fact, threshold model |
| Domain Modeling | Formalize business concepts and conceptual/logical models | Follow-on and iterative | Reconnect KPIs and data products to domains, concepts, entities, and fields |
| System Integration | Connect metadata, models, catalog, quality, and consumption tooling | Follow-on | Targeted proofs of value and tool-responsibility boundaries |
| Cross-cutting Data Governance | Govern definitions, ownership, quality, lineage, security, certification, and lifecycle | Continuous | Promotion rules, stewardship, certification, issue resolution |

Approved working sequence:

1. Define the KPI Store and measurement architecture.
2. Inventory and classify Tableau calculations.
3. Establish KPI governance and implement pilot KPIs.
4. Formalize domain modeling and reconnect models to the KPI Store.
5. Define and prove system-integration patterns.
6. Scale, automate, and operationalize.

## Canonical foundation artifacts
| ID | Title | Purpose |
|---|---|---|
| EPM-FOUND-000 | Enterprise Performance Model Master Index | Navigation, scope, architecture map, artifact register, and delivery sequence |
| EPM-FOUND-001 | Enterprise Business Architecture | Defines domains, value streams, stages, capabilities, processes, activities, and decisions |
| EPM-FOUND-002 | Enterprise Performance and Data Architecture | Connects objectives, measurements, metrics, KPIs, data products, KPI Store, and consumption |
| EPM-FOUND-003 | Enterprise Performance Semantic Model | Human-readable authoritative description of concepts, relationships, rules, and constraints |
| EPM-FOUND-004 | Enterprise Performance Ontology Design | Machine-formal design derived from the semantic model |
| EPM-FOUND-005 | Enterprise Measurement and KPI Model | Detailed classification and promotion model for measurements, metrics, indicators, and KPIs |
| EPM-FOUND-006 | Enterprise Data Product and Consumption Model | Defines foundational/derived products and alignment with Raw, Silver, Gold, and semantic consumption |

## Authoritative baseline
### Working baseline

- The EPM is the conceptual umbrella.
- The KPI Store is the first implementation priority.
- Extracted Tableau calculations are candidate measurements, not approved KPIs.
- Power BI is the current primary validation and consumption environment.
- Reusable business logic should be implemented at the lowest sensible governed layer.
- Consumers access only the semantic/consumption layer.
- The semantic model is the authoritative system of business meaning.
- The ontology is the formal machine-readable implementation of that semantic model.
- SQL semantic views, Power BI semantic models, Purview glossary terms, knowledge graphs, APIs, and AI context are implementations or consumers of shared semantics.

### Items requiring confirmation

- Final canonical downstream domain and value-stream map.
- Final capability decomposition and ownership.
- KPI promotion and approval decision rights.
- Where measurement metadata is mastered across Purview, YAML, database metadata, and project artifacts.
- The first end-to-end ontology and knowledge-graph pilot.

## How to use the repository
Use chats for exploration, clarification, challenge, and decision development. Use these artifacts as the maintained baseline.

When a conversation changes an accepted definition, relationship, modeling rule, or implementation decision:

1. Record the decision and rationale.
2. Update the relevant canonical artifact.
3. Update the Master Index status or dependency if required.
4. Reflect the change in metadata, ontology, code, views, and Power BI models only after governance acceptance.

---
Part of the Enterprise Performance Model Foundation Version 2.