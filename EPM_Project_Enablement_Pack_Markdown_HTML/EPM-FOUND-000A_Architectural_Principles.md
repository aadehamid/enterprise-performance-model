# EPM Architectural Principles
**Artifact:** EPM-FOUND-000A_Architectural_Principles  
**Version:** 1.0 Draft  
**Status:** Working Baseline  
**Updated:** August 4, 2026  

*The constitutional principles governing the Enterprise Performance Model*

## Purpose
These principles govern the design and evolution of the Enterprise Performance Model (EPM), KPI Store, Measurement Catalog, domain models, ontology, data products, semantic layer, Power BI models, reports, APIs, automation, and AI applications.

They are intentionally stable. Detailed designs may evolve, but changes should remain consistent with these principles unless a formal exception is approved.

## Principle 1 — Business meaning is defined once
A business concept should have one authoritative meaning for a given scope and effective period.

Different tools may represent the concept, but they must not independently redefine it.

Examples of implementation tools include:

- Markdown architecture artifacts
- Purview business glossary
- RDF/OWL ontology
- Knowledge graph
- SQL semantic views
- Power BI semantic models
- YAML or JSON metadata
- KPI Store tables
- APIs and AI context services

The governing definition belongs to the Enterprise Performance Semantic Model.

## Principle 2 — Strategy and objectives precede KPIs
A KPI exists because the enterprise needs to evaluate progress toward a defined objective or critical outcome.

Every approved KPI must therefore trace to at least one:

- strategic objective;
- business outcome;
- value-stream outcome;
- capability outcome; or
- critical process objective.

A measure without a meaningful objective may still be a valuable metric, but it should not be promoted automatically into the enterprise KPI set.

## Principle 3 — KPIs are selected, not discovered automatically
Tableau calculations, Power BI measures, SQL expressions, spreadsheet formulas, and report fields are evidence of measurement logic. They are not automatically KPIs.

KPI status requires governance, including:

- business ownership;
- objective alignment;
- approved definition;
- calculation logic;
- dimensional scope;
- target or evaluation rule;
- thresholds where appropriate;
- review cadence;
- decision or response;
- data quality and timeliness.

## Principle 4 — Metrics and KPIs are distinct
Measurements describe observed or calculated values.

Metrics standardize those values for monitoring, comparison, or diagnosis.

KPIs are the small governed subset of metrics used to evaluate critical outcomes and trigger accountability.

The Measurement Catalog may contain thousands of items. The KPI Store should remain intentionally selective.

## Principle 5 — Value streams and capabilities are modeled separately
A value stream describes how value flows from a trigger to an outcome.

A capability describes what the organization must be able to do.

Value-stream stages use capabilities. Capabilities are realized through processes. Processes contain activities. Activities support decisions.

Capabilities must not be treated as though they were simply sequential process steps.

## Principle 6 — Reusable logic is implemented once
Reusable business logic should be implemented at the lowest sensible governed layer.

- Source-specific cleansing belongs in Silver.
- Reusable cross-source business logic belongs in Gold data products.
- Official KPI values and status belong in the KPI Store.
- Stable consumer contracts belong in SQL semantic views.
- Dynamic analytical behavior belongs in Power BI semantic models.
- Visual-only logic belongs in reports.

This prevents the Tableau inconsistency problem from being recreated in Power BI.

## Principle 7 — Consumers access governed interfaces only
Consumers should access only approved semantic or consumption interfaces.

Raw, Silver, and Gold implementation details should remain insulated from consumers unless a formally governed exception exists.

Consumer contracts should be stable, documented, secure, and versioned.

## Principle 8 — Data products are designed for reuse
A data product is not merely a table or view. It is a managed product with:

- business purpose;
- ownership;
- consumers;
- contract;
- quality expectations;
- service levels;
- lineage;
- security;
- lifecycle;
- and adoption measures.

Foundational products represent reusable business facts. Derived products combine those facts into decision-ready insights.

## Principle 9 — The KPI Store records official performance, not all analytical detail
The KPI Store persists governed KPI identity, values, targets, thresholds, status, versions, dimensional context, effective dates, and lineage.

Detailed diagnostic records remain in the relevant derived data products and semantic models.

The KPI Store answers: **What happened against expectation?**

Derived data products and analytical models answer: **Why did it happen?**

## Principle 10 — The semantic model precedes the ontology
The Enterprise Performance Semantic Model is the authoritative human-readable system of business meaning.

The ontology formalizes approved semantics for machine use.

The ontology must not introduce unapproved definitions, relationships, or constraints.

## Principle 11 — Ontology and knowledge graph are different
The ontology defines classes, properties, constraints, and permitted relationships.

The knowledge graph contains actual enterprise instances and connections governed by that ontology.

The ontology is the schema of meaning. The knowledge graph is the populated network of meaning.

## Principle 12 — Governance is cross-cutting
Governance applies across business architecture, performance architecture, semantic architecture, data products, and consumption.

Governance includes:

- definition;
- ownership;
- stewardship;
- quality;
- lineage;
- security;
- certification;
- issue resolution;
- versioning;
- approval;
- and retirement.

## Principle 13 — Traceability is end to end
Every approved KPI should be traceable backward and forward.

Backward trace:

```text
KPI
→ Objective
→ Value stream, capability, process, and decision
→ Supporting metrics
→ Data products
→ Source data
```

Forward trace:

```text
KPI
→ Semantic views
→ Power BI semantic models
→ Reports, APIs, automation, and AI
→ Management decisions and actions
```

## Principle 14 — Historical report logic is evidence, not authority
The reports have already been migrated from Tableau to Power BI.

Tableau XML therefore represents historical implementation evidence. It must be reconciled with:

- current Power BI logic;
- current business practice;
- current source systems;
- approved definitions;
- and business-owner decisions.

No historical calculation should be adopted solely because it existed in Tableau.

## Principle 15 — AI and BI share the same semantic foundation
AI applications, agents, analytics, reports, and APIs must use the same governed definitions, relationships, KPI identities, and data-product contracts.

AI should not create a parallel and conflicting model of the enterprise.

## Principle 16 — Model iteratively, govern deliberately
The EPM should grow through focused pilots rather than a multi-year attempt to model the entire enterprise at once.

Each pilot should prove:

- business value;
- semantic clarity;
- governance workflow;
- technical pattern;
- data quality;
- traceability;
- and reuse.

The preferred first pilot remains Commercial Netback because its data, thresholds, dimensions, and KPI Store patterns are relatively mature.

## Exception management
An exception to these principles should document:

- the principle affected;
- business reason;
- scope;
- risk;
- temporary or permanent nature;
- accountable approver;
- remediation or review date;
- and affected artifacts and implementations.
