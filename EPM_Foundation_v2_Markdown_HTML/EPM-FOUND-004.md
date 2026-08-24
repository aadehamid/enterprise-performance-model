# Enterprise Performance Ontology Design
**Artifact ID:** EPM-FOUND-004  
**Version:** 2.0 Draft  
**Status:** Working baseline  
**Last updated:** August 4, 2026  

*Formalization plan for machine-readable business context*

**Foundation navigation:** [EPM-FOUND-000](EPM-FOUND-000.md) | [EPM-FOUND-001](EPM-FOUND-001.md) | [EPM-FOUND-002](EPM-FOUND-002.md) | [EPM-FOUND-003](EPM-FOUND-003.md) | [EPM-FOUND-004](EPM-FOUND-004.md) | [EPM-FOUND-005](EPM-FOUND-005.md) | [EPM-FOUND-006](EPM-FOUND-006.md)

## Purpose
This file is the ontology design for the Enterprise Performance Semantic Model. It is not the machine ontology SoT.

FOUND-003 is the human-readable semantic model. Turtle in git defines formal semantic and mapping assertions only, not all meaning. This design uses conceptual names. Exact current IRIs, axioms, constraints, and individuals belong to the Turtle SoT.

Machine ontology SoT is Turtle in git ([`ontology/stage2_enterprise_kpi_ontology.ttl`](../ontology/stage2_enterprise_kpi_ontology.ttl)). Demo `o2c-meaning.ttl` is demo Turtle, not that SoT. Fuseki is a demo SPARQL/SHACL runtime loaded from git Turtle, not SoT. A named KPI is one individual, 1:1 with its catalog row. Do not add CandidateKPI or ApprovedKPI OWL classes. Process authority is not this file.

## Ontology layers
| Layer | Examples |
|---|---|
| Upper enterprise concepts | Enterprise, Domain, Objective, Outcome, Role |
| Business architecture | ValueStream, ValueStreamStage, Capability, Process, Activity, Decision |
| Performance architecture | Measurement, Metric, PerformanceIndicator, EnterpriseKPI, Target, Threshold |
| Data architecture | DataAsset, FoundationalDataProduct, DerivedDataProduct, KPIStore, SemanticView |
| Consumption architecture | PowerBISemanticModel, Report, API, AIApplication, Workflow |
| Governance | Owner, Steward, Policy, Standard, Approval, Version |

## Illustrative class hierarchy
```text
BusinessConcept
├── BusinessDomain
├── StrategicObjective
├── ValueStream
├── ValueStreamStage
├── Capability
│   └── SubCapability
├── BusinessProcess
├── BusinessActivity
├── BusinessDecision
└── BusinessOutcome

PerformanceConcept
├── Measurement
│   ├── RawMeasurement
│   └── DerivedMeasurement
├── Metric
│   ├── OperationalMetric
│   ├── DiagnosticMetric
│   └── PerformanceIndicator
└── EnterpriseKPI

DataConcept
├── DataAsset
├── DataProduct
│   ├── FoundationalDataProduct
│   └── DerivedDataProduct
├── KPIStore
├── SemanticView
└── PowerBISemanticModel
```

## Illustrative object properties
| Property | Domain | Range |
|---|---|---|
| hasStage | ValueStream | ValueStreamStage |
| usesCapability | ValueStreamStage | Capability |
| hasSubCapability | Capability | Capability |
| realizedThrough | Capability | BusinessProcess |
| containsActivity | BusinessProcess | BusinessActivity |
| supportsDecision | BusinessActivity | BusinessDecision |
| generatesMeasurement | BusinessProcess or Activity | Measurement |
| evaluatesObjective | EnterpriseKPI | StrategicObjective |
| measuresConcept | Metric or KPI | BusinessConcept |
| explainedBy | EnterpriseKPI | Metric |
| suppliedBy | Metric or KPI | DataProduct |
| exposedThrough | DataProduct or KPI | SemanticView |
| consumedBy | SemanticView or SemanticModel | Report, API, AIApplication |
| ownedBy | GovernedConcept | Role or Organization |

## Illustrative data properties
- preferredLabel
- definition
- identifier
- version
- status
- effectiveFrom
- effectiveTo
- unitOfMeasure
- timeGrain
- targetValue
- warningMinimum
- warningMaximum
- evaluationDirection
- calculationExpression
- sourceSystem
- refreshFrequency
- confidenceScore
- causalLag

## Cardinality and validation examples
- EnterpriseKPI **must have exactly one** accountable owner at a given effective date.
- EnterpriseKPI **must evaluate at least one** StrategicObjective or BusinessOutcome.
- EnterpriseKPI **must have at least one** source DataProduct.
- BusinessProcess **must realize at least one** Capability.
- ValueStreamStage **must use at least one** Capability.
- SemanticView **must expose at least one** DataProduct or KPI.
- Candidate KPI may omit target and thresholds; Approved Enterprise KPI may not.

## Ontology versus knowledge graph
The ontology defines what kinds of things and relationships are allowed.

The knowledge graph contains actual instances.

Example:

```text
Ontology statement:
EnterpriseKPI explainedBy Metric

Knowledge graph instances:
Gasoline Netback CPG explainedBy Transportation Cost per Gallon
Gasoline Netback CPG explainedBy RIN Cost Variance
```

## Recommended implementation path
1. Approve the human-readable semantic model.
2. Define stable identifiers and namespaces.
3. Formalize core classes and properties as Turtle in git (`ontology/stage2_enterprise_kpi_ontology.ttl`). This file is the design, not that SoT. Fuseki is a demo runtime, not SoT.
4. Add SHACL validation shapes for governance constraints.
5. Load a small Commercial pilot knowledge graph.
6. Connect ontology identifiers to Purview terms, KPI metadata, data products, SQL views, and Power BI models.
7. Validate competency questions such as:
   - Which KPIs measure Logistics Execution?
   - Which metrics explain Gasoline Netback CPG?
   - Which data products supply those metrics?
   - Which Power BI reports consume the KPI?
   - Which processes and decisions can change the KPI?

---
Part of the Enterprise Performance Model Foundation Version 2.