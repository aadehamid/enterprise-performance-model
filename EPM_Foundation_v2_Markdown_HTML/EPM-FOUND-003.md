# Enterprise Performance Semantic Model
**Artifact ID:** EPM-FOUND-003  
**Version:** 2.0 Draft  
**Status:** Working baseline  
**Last updated:** August 4, 2026  

*Human-readable authoritative description of business meaning*

**Foundation navigation:** [EPM-FOUND-000](EPM-FOUND-000.md) | [EPM-FOUND-001](EPM-FOUND-001.md) | [EPM-FOUND-002](EPM-FOUND-002.md) | [EPM-FOUND-003](EPM-FOUND-003.md) | [EPM-FOUND-004](EPM-FOUND-004.md) | [EPM-FOUND-005](EPM-FOUND-005.md) | [EPM-FOUND-006](EPM-FOUND-006.md)

## Definition
The **Enterprise Performance Semantic Model** is the governed system of meaning for the Enterprise Performance Model.

It defines:

- the concepts the enterprise uses;
- what each concept means;
- how concepts relate;
- which classifications are allowed;
- which rules and constraints apply;
- how concepts should be interpreted consistently by people and systems.

The written specification is the human-readable expression of the semantic model. Ontologies, knowledge graphs, metadata structures, SQL views, Power BI models, and AI context layers are formal or technical representations, implementations, or consumers of that meaning.

## Semantic model versus implementation
| Item | What it is |
|---|---|
| Semantic model | The organized system of concepts, definitions, relationships, rules, constraints, and classifications |
| Human-readable specification | The authoritative written expression used for business review and governance |
| Ontology | Formal machine-readable representation of the semantic model |
| Knowledge graph | Instances of concepts and relationships, usually governed by an ontology |
| SQL semantic view | A consumer-facing data interface implementing selected semantics |
| Power BI semantic model | An analytical implementation containing tables, relationships, measures, hierarchies, and security |
| Purview glossary | A governance implementation for terms, definitions, owners, and lineage |
| YAML/JSON metadata | A portable implementation format for automation and configuration |

## Core concept taxonomy
### Business context

- Enterprise
- Business Domain
- Strategic Objective
- Value Stream
- Value-Stream Stage
- Business Outcome

### Operating architecture

- Capability
- Sub-capability
- Business Process
- Business Activity
- Business Event
- Business Decision
- Role
- Organization

### Performance architecture

- Measurement
- Raw Measurement
- Derived Measurement
- Metric
- Operational Metric
- Diagnostic Metric
- Performance Indicator
- Candidate KPI
- Enterprise KPI
- Target
- Threshold
- Status
- Performance Driver
- Performance Outcome

### Data and consumption architecture

- Source System
- Data Asset
- Foundational Data Product
- Derived Data Product
- KPI Store
- Semantic Layer
- Semantic View
- Power BI Semantic Model
- Report
- API
- Analytical Model
- AI Application
- Automation Workflow

## Core relationship taxonomy
| Relationship | Domain and range | Meaning |
|---|---|---|
| contains | Domain → Capability; Process → Activity | Parent concept includes child concept |
| decomposes into | Capability → Sub-capability | Broader ability is divided into component abilities |
| uses | Value-Stream Stage → Capability | Stage requires the capability |
| is realized through | Capability → Process | Ability is operationalized through repeatable work |
| supports | Activity → Decision; KPI → Objective | Enables or contributes to another concept |
| generates | Process/Activity/Event → Measurement | Produces an observed or calculated value |
| calculates | Metric/KPI/Data Product → Measurement or Metric | Derives a value using governed logic |
| measures | KPI/Metric → Objective, Outcome, Stage, Capability, Process | Quantifies performance of the target concept |
| explains variance in | Metric/Driver → KPI | Helps explain why KPI performance changed |
| influences | Event/Decision/Driver → Outcome or KPI | Changes likelihood, direction, or magnitude |
| causes | Event/Condition → Effect | Stronger causal assertion supported by evidence |
| constrains | Condition/Policy/Capacity → Decision or Process | Restricts available options |
| supplies | Data Product → Metric/KPI/Semantic View | Provides required trusted data |
| persists | KPI Store → KPI Value | Stores governed time-series results |
| exposes | Semantic View/Model → Consumer | Makes governed data available |
| consumes | Report/API/AI → Semantic View/Model | Uses an approved interface |
| owned by | Governed Concept → Role/Organization | Assigns accountability |
| governed by | Concept → Policy/Standard/Decision | Identifies governing authority |

## Rules and constraints
- Every enterprise KPI must evaluate at least one objective or critical outcome.
- Every approved KPI must have an accountable business owner.
- Every approved KPI must have a governed definition, calculation, grain, unit, dimensional scope, target or expected condition, and review cadence.
- A metric may explain multiple KPIs.
- A KPI may depend on multiple data products.
- A data product may support multiple metrics and KPIs.
- A value-stream stage may use many capabilities.
- A capability may support many value streams and stages.
- A process must realize at least one capability.
- An activity must belong to at least one process.
- A semantic view must have an identified source data product and consumer contract.
- The ontology must not introduce meanings that have not been defined or approved in the semantic specification.

## Example semantic chain
```text
Commercial Margin Optimization
    is a Strategic Objective

Gasoline Netback CPG
    is an Enterprise KPI
    evaluates Commercial Margin Optimization
    is explained by Transportation Cost per Gallon
    is explained by Product Cost Variance
    is explained by RIN Cost Variance

Commercial Margin Data Product
    supplies Gasoline Netback CPG
    supplies Transportation Cost per Gallon

CONSUMPTION.v_kpi_values
    exposes Gasoline Netback CPG

Commercial Performance Power BI Semantic Model
    consumes CONSUMPTION.v_kpi_values

Executive Commercial Scorecard
    consumes Commercial Performance Power BI Semantic Model
```

## Governance of meaning
The semantic model is authoritative only when:

- definitions are structured and internally consistent;
- relationships are explicit;
- modeling rules are documented;
- ownership and approval are recorded;
- changes are versioned;
- conflicts are surfaced rather than silently resolved;
- implementations can be traced back to the governing concept and definition.

---
Part of the Enterprise Performance Model Foundation Version 2.