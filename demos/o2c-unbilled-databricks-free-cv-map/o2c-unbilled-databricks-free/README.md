# Customer O2C Unbilled Reference Implementation

**Status:** Draft implementation expansion  
**Current baseline:** Existing Databricks Free / Unity Catalog / Contextual Views map demonstration  
**Primary domain:** Downstream Oil & Gas Customer domain  
**Primary value stream:** Order to Cash (O2C)  
**First operational use case:** Role-aware unbilled exposure  
**Implementation type:** Synthetic-data, test-first, enterprise-pattern homelab reference implementation

## Start here

This directory is the executable **Customer/O2C reference implementation** of the Enterprise Performance Model Homelab reference architecture.

It demonstrates how fragmented customer-like records across CRM, ERP, CTRM, terminal automation, accounts receivable, tax/exemption, and collections contexts can be modeled, harmonized, validated, traced, measured, and investigated without treating distinct party roles as one interchangeable `customer_id`.

Read the documents in this order:

1. [`THE-PROBLEM.md`](THE-PROBLEM.md) — the unbilled O2C business problem and its Customer-domain cause.
2. [`IMPLEMENTATION-HANDOFF.md`](IMPLEMENTATION-HANDOFF.md) — the detailed build specification, delivery sequence, test strategy, and acceptance criteria.
3. [`../../../business_architecture/domain/customer_domain_problem_statement_v0.1.md`](../../../business_architecture/domain/customer_domain_problem_statement_v0.1.md) — the parent Customer-domain problem, source-system variants, and role catalogue.
4. The shared EPM Homelab reference architecture listed below.

## Reference implementation relationship

> **Reference implementation:** This directory is the runnable, testable Customer/O2C implementation of the shared EPM Homelab reference architecture. It implements and validates shared patterns; it does not silently override shared source-of-truth boundaries or approved architecture decisions.

> **Reference architecture:** The reusable architecture, standards, tool decisions, and cross-cutting controls live in [`../../../EPM_Homelab/`](../../../EPM_Homelab/). Changes to a shared principle, tool boundary, standard, or pattern must be assessed against the Homelab artifacts before being treated as reusable baseline.

### Governing shared references

| Shared artifact | Why it matters to this implementation |
|---|---|
| [`00-Homelab-Charter-and-Roadmap.md`](../../../EPM_Homelab/00-Homelab-Charter-and-Roadmap.md) | Defines homelab mission, scope boundaries, delivery priority, and end-to-end demonstration intent |
| [`01-Reference-Architecture.md`](../../../EPM_Homelab/01-Reference-Architecture.md) | Defines cross-layer architecture, source-of-truth boundaries, and information flows |
| [`02-Tool-Selection-and-ADRs.md`](../../../EPM_Homelab/02-Tool-Selection-and-ADRs.md) | Records selected open-source tools, alternatives, licensing, and architecture decisions |
| [`04-Data-Strategy-and-Datasets.md`](../../../EPM_Homelab/04-Data-Strategy-and-Datasets.md) | Defines public-data anchors, synthetic-data boundaries, and source-to-data-product guidance |
| [`05-Domain-Model-and-Ontology-Pilot.md`](../../../EPM_Homelab/05-Domain-Model-and-Ontology-Pilot.md) | Defines ontology, RDF/OWL, SHACL, KPI, and graph-pilot patterns |
| [`06-Repo-Structure-and-Build-Plan.md`](../../../EPM_Homelab/06-Repo-Structure-and-Build-Plan.md) | Defines reproducibility, repository, testing, pipeline, and delivery conventions |

## Business problem

A Downstream Oil & Gas enterprise represents commercial parties differently across Salesforce CRM, SAP/ERP, RightAngle/CTRM, terminal automation, billing, accounts receivable, tax/exemption, collections, and supporting systems.

The same underlying party may act as a sold-to party, ship-to, consignee, bill-to party, payer, contract party, pricing party, credit counterparty, title-transfer party, tax-liable party, guarantor, or carrier. Conversely, different parties in a corporate hierarchy can perform these roles in one O2C transaction.

The resulting identity and role fragmentation makes customer-level O2C analysis unreliable. It can break order-to-contract-to-delivery-to-invoice linkage, distort unbilled exposure, weaken quality controls, and prevent trusted metric/KPI explanation.

The first proof is **role-aware unbilled exposure**. It is initially an operational metric, not automatically an approved KPI.

```text
Fragmented customer-like source objects
  → uncertain identity, hierarchy, and role
  → incomplete O2C event association
  → unreliable delivery-to-contract-to-invoice linkage
  → uncertain unbilled exposure and customer performance measures
```

## Meaning, compute, and consume

The implementation follows the Enterprise Performance Model separation of concerns.

```text
MEANING — no KPI computation
  Customer domain and O2C process architecture
  → Sirius conceptual, logical, and physical model
  → RDF/OWL/SKOS/SHACL ontology modules
  → graph of meaning and named KPI context

COMPUTE
  Lakebase synthetic operational records
  → Databricks Bronze source representations
  → Silver role-aware harmonization
  → Gold unbilled exposure fact
  → Metric Views and governed calculation processes
  → KPI Store candidate/approved KPI governance and published snapshots

CONSUME
  Plotly Dash operational control tower
  → BI and Databricks consumers
  → FastAPI/MCP/agent tools
  → Neo4j/Fuseki contextual investigation
```

A domain concept, a measure, a Metric View, an operational metric, a candidate KPI, and an approved KPI are distinct artifacts. No consumer, graph, dashboard, or agent may recreate an authoritative formula independently.

## Confirmed stack

| Layer | Tool or platform | Responsibility |
|---|---|---|
| Data modeling | Sirius Web | Conceptual, logical, and physical Customer/O2C data model; ERDs; versioned model releases |
| Operational source simulation | Databricks Lakebase Postgres | Synthetic source-specific O2C operational records |
| Lakehouse | Databricks and Delta | Bronze, Silver, and Gold data products and transformations |
| Technical catalog and lineage | Unity Catalog | Asset governance, technical metadata, access, and native Databricks lineage |
| Observability/catalog | OpenMetadata | Open-source discovery, cross-platform lineage, ownership, glossary, and quality context |
| Ontology/triple store | Apache Jena Fuseki | RDF/OWL/SKOS/SHACL, mapping assertions, provenance, and SPARQL |
| Knowledge graph | Neo4j Community | Customer/O2C/model/KPI context graph, impact analysis, Cypher, and agent-serving layer |
| Metric layer | Databricks Metric Views | Reusable governed analytical measure and dimension definitions |
| KPI governance | Enterprise KPI Store pattern | Candidate Register, Cataloging Store, Semantic Layer, Compiler, Gold published snapshots, and KPI governance |
| Dashboard | Plotly Dash | Operational control-tower dashboard consuming governed outputs only |
| Integration and agents | Python, FastAPI, MCP, Dagster | Controlled model generation, data generation, pipelines, validation, exports, APIs, and evidence-backed agent tools |

## Delivery scope

The first implementation increment will:

1. Preserve and baseline-test the current Databricks unbilled demonstration.
2. Add deterministic, synthetic source-system Customer variants.
3. Add role-aware Customer cross-reference and identity-resolution staging structures.
4. Extend Bronze, Silver, and Gold structures without breaking the existing unbilled path.
5. Model Customer/O2C structure in Sirius and export approved model releases through Python.
6. Link model elements to RDF/OWL, Neo4j, Unity Catalog, OpenMetadata, quality tests, Metric Views, and KPI dependencies.
7. Deliver a Plotly Dash operational dashboard and controlled agent questions.
8. Verify every layer through automated tests, release manifests, lineage checks, and end-to-end acceptance scenarios.

## Repository map

```text
.
├── README.md                         # You are here
├── THE-PROBLEM.md                    # Business/use-case problem
├── IMPLEMENTATION-HANDOFF.md         # Detailed implementation specification
├── WALKTHROUGH.md                    # Current demonstration walkthrough
├── sql/                              # Lakebase, Bronze/Silver/Gold, Metric View, Store SQL
├── scripts/                          # Python automation, Contextual Views, Genie, integration scripts
├── data/                             # Synthetic data and deterministic test fixtures
├── ontology/                         # Demo-specific RDF/OWL/SHACL and mapping artifacts
├── osi/                              # Open Semantic Interchange / semantic artifacts
├── tests/                            # To be added: unit, integration, semantic, and end-to-end tests
└── dashboards/                       # To be added: Plotly Dash application and dashboard tests
```

## Operating rules

- **Sirius owns model structure.** Coding agents may create proposed model changes through allow-listed Python tools; only validated and approved model releases are exported.
- **Fuseki owns formal semantic meaning and mapping assertions.** Neo4j is a serving/query projection, not a competing semantic source.
- **Lakebase preserves operational/source context.** Bronze preserves source semantics; Silver harmonizes role-aware structures; Gold publishes derived facts.
- **Unity Catalog owns native Databricks lineage.** OpenMetadata provides a cross-platform observability and catalog view.
- **Databricks quality capabilities execute data-quality controls.** The data model supplies reviewed quality intent, not autonomous production rules.
- **Metric Views calculate reusable measures.** The KPI Store governs whether a measure becomes a candidate or approved KPI.
- **Plotly Dash and agents consume governed outputs.** They do not independently recreate governed formulas.
- **Every increment must be tested.** Use deterministic source scenarios, repeatable data-generation seeds, contract tests, semantic tests, lineage checks, and end-to-end evidence.

## First questions to demonstrate

- What is unbilled exposure this week by bill-to, consignee, credit-counterparty, and corporate-parent perspective?
- Why is a specific custody release unbilled, and which source records, role mappings, contract, title, tax, invoice, and quality checks support the answer?
- Which Customer-domain source records are unresolved or conflicting, and which Gold facts, metrics, or KPIs are affected?
- Which Sirius model elements, Unity Catalog columns, quality rules, Metric Views, and graph relationships are impacted if a bill-to or title-transfer relationship changes?

## Status and limitations

- The current Databricks demo is the baseline implementation and must be tested before refactoring.
- Customer role variants, Sirius, Fuseki, Neo4j, OpenMetadata, Plotly Dash, agent tools, and comprehensive test suites are planned implementation extensions.
- All commercial-party and O2C records are synthetic. The demonstration does not implement production MDM, SAP MDG, CRM, ERP, CTRM, terminal automation, financial close, tax reporting, or automatic KPI approval.

## Next step

Read [`IMPLEMENTATION-HANDOFF.md`](IMPLEMENTATION-HANDOFF.md) and execute its phases in order. Do not introduce a new source-system variant, role, metric, or platform integration without adding corresponding data contracts, tests, lineage/semantic mappings where applicable, and acceptance evidence.
