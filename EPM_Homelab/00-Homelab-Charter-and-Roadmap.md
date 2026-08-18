# Downstream O&G Knowledge Homelab — Charter and Roadmap

**Title:** Downstream O&G Knowledge Homelab — Charter and Roadmap  
**Purpose:** Establish the personal learning mission, architectural boundaries, capstone pilot, and delivery sequence for the homelab. This document is the master index for the six supporting homelab documents.  
**Status:** Draft (personal homelab, not an EPM governed artifact)  
**Owner:** Hamid Adesokan  
**Last updated:** 2026-08-10  

## Vision

The **Downstream O&G Knowledge Homelab** exists to deepen Hamid Adesokan's ontology, RDF/OWL, Neo4j, R2RML, AI-agent, and Python data-engineering skills through one realistic but self-contained Downstream Oil & Gas scenario. Rather than learning each technology in isolation, the homelab builds an end-to-end reference architecture around refining margin/netback, wholesale rack marketing, terminal custody transfer, retail fuel, and order-to-cash. The result should be a portfolio-worthy working system that demonstrates how business meaning, operational facts, governed KPIs, semantic models, knowledge graphs, and agentic consumption connect in practice.

## Learning objectives

The homelab is designed to build practical capability in:

- Conceptual modeling, including separation of **T-Box** terminology/model structure from **A-Box** instance facts.
- Controlled vocabularies and business glossary design with **SKOS**, including preferred labels, alternative labels, broader/narrower relationships, and concept schemes ([W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)).
- RDFS and OWL modeling, competency questions, URI design, and targeted reasoning.
- RDF serialization, graph handling, and SPARQL with **RDFLib** and **Apache Jena Fuseki** ([RDFLib](https://github.com/rdflib/rdflib), [Apache Jena Fuseki documentation](https://jena.apache.org/documentation/fuseki2/)).
- R2RML mapping and virtual RDF/OBDA through **Ontop**, with deliberate materialization only where it is useful ([Ontop VKG guide](https://ontop-vkg.org/guide/)).
- SHACL shape design, validation diagnostics, and validation in continuous integration using **pySHACL** ([RDFLib pySHACL](https://github.com/rdflib/pyshacl)).
- Neo4j property-graph design, Cypher, and RDF interchange using self-hosted **neosemantics (n10s)** ([Neo4j Labs neosemantics](https://neo4j.com/labs/neosemantics/)).
- KPI Store design: KPI versus metric versus measure; definitions, formulas, dimensions, thresholds, lineage, and governed query surfaces.
- Python data pipelines and asset-oriented orchestration with **Dagster**, spanning raw ingestion, relational loading, mapping, validation, and graph population ([Dagster](https://github.com/dagster-io/dagster)).
- AI-agent and GraphRAG patterns with **LangGraph**, local models served by **Ollama**, and graph/KPI-store tools exposed through **FastAPI** and an agent-agnostic **MCP server** ([LangGraph license](https://github.com/langchain-ai/langgraph/blob/main/LICENSE), [Ollama runtime overview](https://dev.to/synsun/running-local-llms-in-2026-ollama-lm-studio-and-jan-compared-121c), [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)).
- Ontology reasoning with **Owlready2/HermiT** and a tiered, traceable answer-resolution model — patterns adapted from AWS's Context Ontology Accelerator ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html), [AWS Context Ontology Accelerator docs](https://aws.github.io/context-ontology-accelerator/)); see ADR-HL-018 through ADR-HL-020 in `02-Tool-Selection-and-ADRs.md`.

## Scope and boundaries

| Boundary | In scope | Out of scope |
|---|---|---|
| Deployment | Single-machine or small home-server deployment, reproducible with Docker Compose. | Production hardening, high availability, multi-region deployment, and enterprise operations. |
| Domain | The full ten-group O2C process taxonomy: Master Data Mgmt, Quote & Sale, Credit & Risk, Order & Fulfillment, Measure & Custody Transfer, Billing, Receipt, Collection, Dispute, and Close. [ERPNext](https://github.com/frappe/erpnext) provides the core O2C flow; [trycompai/crm](https://github.com/trycompai/crm) supplies external party-master context; light custom Frappe workflows cover Credit & Risk, Measure & Custody Transfer, Collection, Dispute, and Close. Downstream O&G-specific process structure includes rack pricing, terminal lifting, product grade/BOL, PADD, and excise-tax status. | A complete refinery, terminal automation, ERP, retail, or channel operating model. |
| Data | Small public and synthetic datasets; EIA spot-price and petroleum-marketing inputs; synthetic tickets, orders, and invoices. EIA offers daily crude/refined-product spot prices for crack-spread and netback exercises ([EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)) and public wholesale/rack context ([EIA Petroleum Marketing Monthly](https://www.eia.gov/petroleum/marketing/monthly/)). The [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) is a realism-calibration reference for synthetic O2C volumes, cardinalities, and distributions, not the primary schema. | Enterprise-scale volumes, proprietary data, commercial OPIS/Platts feeds, PII, or production SCADA connectivity. |
| Unstructured enterprise context | Entity-linked SOPs, emails, invoice/receipt PDFs, and team-channel messages generated across all 64 Level 2 taxonomy processes. [block/buzz](https://github.com/block/buzz) provides the team-channel simulator; [semantica-agi/semantica](https://github.com/semantica-agi/semantica) ingests and fuses these artifacts with relational data in the knowledge graph. | An independently generated document corpus disconnected from O2C entities or production records-management implementation. |
| Governance | Git, semantic versioning, data contracts, SHACL checks, lineage notes, and ADRs. | Compliance certification, formal enterprise governance, multi-tenant security, approval workflow, or audited controls. |
| Purpose | A personal educational sandbox and portfolio reference architecture. | A governed enterprise asset or a substitute for professional EPM deliverables. |

This is plainly a personal sandbox, not part of the governed Enterprise Performance Model (EPM) artifact set. It intentionally parallels selected EPM structures so learning transfers, but it may make simplifications and shortcuts that a governed enterprise initiative cannot.

## Relationship to the professional EPM initiative

| Dimension | Enterprise Performance Model | Downstream O&G Knowledge Homelab |
|---|---|---|
| Operating context | Governed, multi-team enterprise performance architecture. | Personal, single-owner learning environment. |
| Delivery setting | Power BI reporting/semantic-model consumption following Tableau migration, with ten connected workstreams. | Fully open-source stack, local-first delivery, and one simplified pilot. |
| Primary objective | Govern and scale enterprise performance architecture, with KPI Store delivery first. | Learn the semantic-data-graph-agent path by building it. |
| Data and controls | Enterprise systems, governed definitions, ownership, access, quality, and lifecycle controls. | Public EIA data, synthetic data, lightweight conventions, and reproducible code. |
| Scope pattern | Multiple domains, artifacts, integrations, consumers, and rollout waves. | One vertical slice, deliberately narrow enough to finish and explain. |

The homelab deliberately mirrors these EPM concepts without claiming formal linkage:

- **KPI versus metric versus measure distinction:** a KPI is not merely a calculation; it requires an objective, definition, time grain, evaluation logic, and action context.
- **Measurement classification:** raw measure, business measure, derived measure, operational metric, diagnostic/analytical metric, performance indicator, candidate KPI, and approved KPI are distinct states.
- **KPI Store pattern:** persist the selected KPI result and governed context while retaining supporting facts in data products and analytical stores.
- **Downstream O2C custody-event-centric shape:** terminal, product, custody ticket/BOL, corrected quantity, pricing, tax, and invoice relationships are first-class concepts.
- **Ontology/virtual-RDF-first principle:** physical operational and analytical data remain in their appropriate stores; RDF/OWL supplies meaning and linked semantics.

## Guiding principles

1. **Define business meaning once.** Reuse a canonical KPI, metric, glossary, and domain-concept definition rather than rebuilding query, dashboard, or agent logic.
2. **Let strategy and objective precede the KPI.** Start with a commercial-margin objective, then define the KPI, drivers, and action questions.
3. **Keep facts in the right systems of record.** PostgreSQL holds operational/O2C facts and DuckDB local analytics; RDF/OWL holds definitions, relationships, mappings, and lineage meaning.
4. **Prefer virtual RDF before materialized RDF.** Use Ontop and R2RML to query relational facts as a live RDF graph before copying them; materialize stable curated facts with Morph-KGC only when the use case needs it ([Ontop VKG guide](https://ontop-vkg.org/guide/), [Morph-KGC documentation](https://morph-kgc.readthedocs.io/)).
5. **Treat Neo4j as a serving/query layer.** Populate Neo4j from the RDF layer using n10s or Morph-KGC; it is not an independent semantic source of truth.
6. **Use SHACL to validate and OWL to define meaning.** Shapes make closed-world data-quality expectations executable; OWL/RDFS expresses vocabulary, classification, and relationships.
7. **Version-control everything as code.** Ontologies, shapes, mappings, generators, pipeline assets, queries, API contracts, ADRs, and documentation belong in Git.
8. **Build one working vertical slice before broadening layers.** A proven end-to-end pilot is more valuable than seven partially connected technology demonstrations.
9. **Prefer genuinely open, actively maintained dependencies.** The baseline favors Apache-2.0, MIT, BSD-3-Clause, PostgreSQL, GPLv3, and W3C-standard components: for example, Ontop and Morph-KGC are Apache-2.0, RDFLib is BSD-3-Clause, DuckDB is MIT, and pySHACL is Apache-2.0 ([Ontop VKG guide](https://ontop-vkg.org/guide/), [Morph-KGC documentation](https://morph-kgc.readthedocs.io/), [RDFLib](https://github.com/rdflib/rdflib), [RDFLib pySHACL](https://github.com/rdflib/pyshacl)). Do not make proprietary free tiers or archived projects core dependencies.

## The one capstone pilot

The homelab first builds the full ten-group O2C process taxonomy through [ERPNext](https://github.com/frappe/erpnext): Master Data Mgmt, Quote & Sale, Credit & Risk, Order & Fulfillment, Measure & Custody Transfer, Billing, Receipt, Collection, Dispute, and Close. ERPNext provides the native O2C backbone, with light custom Frappe workflows for the five groups it does not natively support: Credit & Risk, Measure & Custody Transfer, Collection, Dispute, and Close. This horizontal process backbone sits above the existing Refining Margin / Gasoline Netback KPI vertical trace, which remains the capstone pilot.

The capstone is a simplified **Gasoline Netback / Refining Margin CPG** KPI. It traces a single, inspectable chain:

```text
Commercial-margin objective
  → Gasoline Netback / Refining Margin CPG KPI definition
  → supporting measures and metrics (EIA spot-price / crack-spread inputs)
  → Terminal, Product, Custody Ticket, Customer, Contract, and Invoice concepts
  → public EIA + synthetic O2C data products
  → KPI Store fact and semantic view
  → SPARQL and Cypher query surfaces
  → FastAPI endpoint + LangGraph agent response
```

The public foundation uses EIA daily crude and refined-product spot prices as inputs to a 3:2:1 crack-spread calculation ([EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)). Synthetic terminal tickets, contracts, orders, pricing differentials, invoices, and retail allocations supply a realistic but non-sensitive commercial context. The KPI Store records netback at its declared time grain and dimensions; PostgreSQL/DuckDB retain supporting facts; RDF/OWL defines meaning; Ontop exposes virtual RDF; and Neo4j provides an LPG query and GraphRAG serving surface.

The capstone endpoint answers: **“What is our netback this week and why?”** The answer must retrieve the weekly KPI, identify material drivers, and show the SPARQL and/or Cypher evidence path behind the response, naming which resolution tier answered it (Tier 0 governed KPI Store lookup, Tier 1 structured graph query, or Tier 2 agentic fallback — ADR-HL-020). It must be reachable equally through the FastAPI backend or the MCP server (ADR-HL-018), and the underlying T-Box must have passed the Owlready2/HermiT reasoning gate before its facts were materialized (ADR-HL-019). One narrow vertical slice is intentional. It follows the enterprise pilot rationale: validate that the connected structures work from objective through semantic and graph consumption before scaling into broad, disconnected layers.

## High-level roadmap / phases

| Phase | Objective | Key deliverable | Primary tools | Rough learning-time estimate |
|---|---|---|---|---|
| Phase 0: Environment & repo setup | Establish a reproducible local developer experience and repository conventions. | Docker Compose stack, Python environment, Git conventions, ADR template, CI checks. | Docker Compose, Git, Python, PostgreSQL 18, DuckDB. | 1–2 weekends |
| Phase 1: O2C taxonomy-to-ontology mapping | Map all ten Level 1 groups and 64 Level 2 processes (downstream O&G redline, approved 2026-08-09) to the ontology, including cross-cutting metadata, downstream O&G-specific process structure, competency questions, and KPI-candidate links. | O2C taxonomy map, process-node URI convention, ontology extensions, and initial glossary. | Protégé Desktop, RDFLib, SKOS, OWL, SHACL. | 2–3 weekends |
| Phase 2: Data foundation — ingest public data + design synthetic data | Ingest price inputs and create plausible O2C/custody datasets that preserve business rules. | EIA ingestion assets; synthetic terminal, product, custody-ticket, contract, order, and invoice tables; data dictionary. | Python, Dagster Core, PostgreSQL, DuckDB, EIA Open Data API, [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). | 2–3 weekends |
| Phase 3: ERPNext O2C plus custom workflow build | Implement the native O2C backbone and the minimal stateful workflows required for groups without native ERPNext support. | [ERPNext](https://github.com/frappe/erpnext) O2C configuration; custom Frappe DocTypes and approvals for Credit Limit Review, Custody Transfer Ticket, Collection Case, Dispute Case, and AR Sub-Ledger Close Task; CRM master-data feed from [trycompai/crm](https://github.com/trycompai/crm). | ERPNext, Frappe, trycompai/crm, PostgreSQL. | 3–4 weekends |
| Phase 4: Unstructured data generation, Buzz, and semantica ingestion | Generate entity-linked artifacts for all Level 2 processes and fuse them with relational facts in the knowledge graph. | SOP corpus; invoice/receipt PDFs; email threads; [block/buzz](https://github.com/block/buzz) channel exports; [semantica-agi/semantica](https://github.com/semantica-agi/semantica) ingestion and provenance configuration. | Python, ReportLab or WeasyPrint, block/buzz, semantica-agi/semantica, Neo4j, Apache Jena Fuseki. | 3–4 weekends |
| Phase 5: Domain modeling & ontology (RDF/OWL/SHACL) for the pilot | Model the pilot's terminology, classes, relationships, glossary, competency questions, and data-quality rules; gate materialization with an Owlready2/HermiT consistency check (ADR-HL-019). | Turtle ontology, SKOS glossary, SHACL shapes, examples, validation report, reasoning-gate Dagster asset. | Protégé Desktop, RDFLib, Owlready2, pySHACL, SKOS, PROV-O. | 3–4 weekends |
| Phase 6: KPI Store & semantic/query layer (Postgres/DuckDB + SPARQL) | Implement the pilot KPI’s definition, calculation, persistent result, governed dimensions, and virtual RDF query surface. | KPI definition and KPI Store tables; calculation assets; R2RML mappings; SPARQL examples. | PostgreSQL, DuckDB, Ontop, RDFLib, Apache Jena Fuseki. | 3–4 weekends |
| Phase 7: Neo4j knowledge graph population via n10s/Morph-KGC | Populate and query a Neo4j serving graph from curated RDF facts without separating semantic ownership. | Repeatable graph-load job, mapping convention, Cypher queries, SPARQL-to-Cypher comparison notes. | Neo4j Community Edition, n10s, Morph-KGC, RDFLib. | 2–3 weekends |
| Phase 8: AI agent, FastAPI, and MCP server capstone | Provide controlled question answering that retrieves KPI values and graph evidence through an explicit tiered resolution model, reachable from both FastAPI and an agent-agnostic MCP server. | FastAPI endpoints, MCP server tools, LangGraph workflow, local Ollama model integration, tiered answer/evidence contract with resolution trace. | FastAPI, LangGraph, Ollama, neo4j-graphrag-python and/or LlamaIndex Property Graph Index, `modelcontextprotocol/python-sdk` (ADR-HL-018, ADR-HL-020). | 3–4 weekends |
| Phase 9: Governance polish — lineage, SHACL CI, documentation | Make the pilot inspectable, reproducible, and portfolio-ready. | Lineage notes, SHACL CI gate, runbook, architecture diagrams, walkthrough. | OpenLineage, Marquez, Dagster, pySHACL, GitHub Actions or local CI. | 2–3 weekends |

## Artifact index

| Document | Purpose |
|---|---|
| `00-Homelab-Charter-and-Roadmap.md` | Defines mission, boundaries, principles, capstone pilot, roadmap, and master index. |
| `01-Reference-Architecture.md` | Describes the layered architecture, information flows, tool responsibilities, and source-of-truth boundaries. |
| `02-Tool-Selection-and-ADRs.md` | Records the open-source tool baseline, alternatives, rejected options, and architecture decisions. |
| `03-Curriculum-and-Learning-Modules.md` | Organizes the learning sequence, exercises, prerequisites, and evidence of skill development. |
| `04-Data-Strategy-and-Datasets.md` | Specifies public/synthetic data sources, schemas, provenance, generation strategy, and data-product boundaries. |
| `05-Domain-Model-and-Ontology-Pilot.md` | Defines the netback pilot’s domain concepts, ontology scope, competency questions, mappings, and SHACL checks. |
| `06-Repo-Structure-and-Build-Plan.md` | Defines repository layout, implementation increments, commands, tests, CI, and build acceptance criteria. |

## Success criteria

The capstone pilot is done when:

- [ ] A documented Gasoline Netback / Refining Margin CPG KPI has an objective, formula, unit, time grain, dimensions, supporting measures, and evaluation logic.
- [ ] Public EIA price inputs and synthetic O2C/custody data load repeatably into PostgreSQL and/or DuckDB through Python pipeline assets.
- [ ] The ontology, SKOS glossary, R2RML mappings, and SHACL shapes are versioned and a SHACL validation run passes in CI.
- [ ] Ontop exposes the defined relational facts through a working SPARQL query surface.
- [ ] Neo4j is populated reproducibly from RDF-derived content and returns the intended Cypher paths.
- [ ] The KPI Store returns the latest weekly netback and enough driver context to explain the result.
- [ ] A FastAPI-backed agent can answer a netback question by querying the KPI Store and citing the SPARQL/Cypher path it used.
- [ ] A new reader can clone the repository, follow the build plan, reproduce the pilot, and understand source-of-truth boundaries.

## Open Issues

- **Customer master governance layer:** No open-source analog has yet been identified for SAP MDG-style staging and approval or Profisee-style probabilistic matching and survivorship needed by the Customer Data Dictionary Template. A custom Python matching/survivorship implementation plus a Neo4j/Fuseki governance record is a candidate fallback, not an accepted decision.

## Related homelab documents

- `01-Reference-Architecture.md`
- `02-Tool-Selection-and-ADRs.md`
- `03-Curriculum-and-Learning-Modules.md`
- `04-Data-Strategy-and-Datasets.md`
- `05-Domain-Model-and-Ontology-Pilot.md`
- `06-Repo-Structure-and-Build-Plan.md`

## See also (enterprise EPM parallel)

For learning-transfer context only, this document loosely mirrors the EPM Project Charter and Operating Model, KPI Store, Commercial Margin / Gasoline Netback Pilot, and Downstream O2C Operational Blueprint. It is not a governed EPM artifact and makes no claim of formal linkage or approval.
