# Downstream O&G Knowledge Homelab — Tool Selection and ADRs

**Title:** Tool Selection and Architecture Decision Records  
**Purpose:** Record the rationale, boundaries, and trade-offs behind the tool choices in `01-Reference-Architecture.md`. These ADRs provide a compact decision trail for a personal, open-source, single-machine learning stack.  
**Status:** Draft (personal homelab, not an EPM governed artifact)  
**Owner:** Hamid Adesokan  
**Last updated:** 2026-08-29

This document records the “why” behind each reference-architecture tool choice using a lightweight Architecture Decision Record (ADR) format. It is adapted from the enterprise EPM Architecture Decision Log pattern, but is intentionally scoped to the **Downstream O&G Knowledge Homelab**: an educational sandbox that may take practical shortcuts and is not part of the governed Enterprise Performance Model (EPM) artifact set.

## ADR-HL-001 — Use Apache Jena Fuseki as the homelab SPARQL classroom

**Status:** Accepted (for a personal homelab). Enterprise serve path is ADR-HL-021.

**Context.** The homelab needs a self-hosted RDF store and SPARQL endpoint so the owner can learn SPARQL, named graphs, and SHACL-on-a-server. Apache Jena provides a full RDF framework and Fuseki server under Apache-2.0, with current releases and maintained documentation. ([Apache Jena downloads](https://jena.apache.org/download/index.cgi)) ([Apache Jena Fuseki documentation](https://jena.apache.org/documentation/fuseki2/))

The enterprise client has no triple store and will not be sold one. Their unused Neo4j is the expose path (ADR-HL-021). Fuseki stays in the lab so SPARQL can be learned. It is not the transfer artifact.

**Decision.** Use **Apache Jena Fuseki** as the default **lab** SPARQL endpoint for Modules 05–07. Use **Oxigraph** only as an optional lightweight or embedded comparison companion, not as the primary replacement. ([Oxigraph](https://github.com/oxigraph/oxigraph)) Do not treat Fuseki as a client or production seat. The published Turtle still loads into Neo4j via n10s as the serve path that transfers.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| GraphDB Free, Stardog Free, AllegroGraph Free, Amazon Neptune | Proprietary or managed-commercial offerings rather than self-hostable open source; their free tiers have legal or functional constraints. ([GraphDB licensing](https://graphdb.ontotext.com/documentation/11.4/licensing.html)) ([Stardog Free license](https://www.stardog.com/legal/stardog-free/)) ([AllegroGraph editions](https://allegrograph.com/allegrograph-editions/)) ([Amazon Neptune](https://aws.amazon.com/neptune/)) |
| Blazegraph | GPLv2 and genuinely open source, but the repository is archived and upstream development is abandoned. ([Blazegraph releases](https://github.com/blazegraph/database/releases)) |
| D2RQ | An Apache-2.0 relational mapping tool, not a primary triple store, and archived since 2021. ([D2RQ repository](https://github.com/d2rq/d2rq)) |
| Oxigraph | Apache-2.0/MIT dual-licensed and actively developed, but selected as an optional embeddable/no-server exploration path rather than the teaching-oriented default endpoint. ([Oxigraph](https://github.com/oxigraph/oxigraph)) |

**Consequences.**
- SPARQL and RDF/OWL learning use a mainstream server endpoint with a clear operational boundary. Curriculum Modules 05–07 still run against Fuseki.
- Curated materialized facts can be loaded into Fuseki for those exercises; operational facts remain in Postgres and are exposed virtually where feasible.
- The stack avoids a dependency on free-tier terms or abandoned upstream projects.
- The client demo and transfer story load the same git Turtle into Neo4j. Fuseki is omitted from that story.

## ADR-HL-002 — Prefer Ontop virtual RDF; materialize with Morph-KGC only when needed

**Status:** Accepted (for a personal homelab)

**Context.** Order-to-cash and measurement facts belong in PostgreSQL rather than in duplicated graph copies. Ontop exposes relational data as a live RDF/SPARQL graph by translating SPARQL to SQL without materialization; Morph-KGC materializes knowledge graphs from R2RML/RML mappings. ([Ontop VKG guide](https://ontop-vkg.org/guide/)) ([Morph-KGC documentation](https://morph-kgc.readthedocs.io/en/latest/why-morph-kgc/))

**Decision.** Use **Ontop** as the default relational-to-RDF approach. Use **Morph-KGC** when stable, curated facts need to be materialized for Fuseki or Neo4j.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| D2RQ | Apache-2.0 but effectively abandoned; its repository has been archived since January 2021. ([D2RQ repository](https://github.com/d2rq/d2rq)) |
| Always materialize | Introduces copy/refresh responsibility where Ontop can preserve PostgreSQL as the live operational source of truth. ([Ontop VKG guide](https://ontop-vkg.org/guide/)) |
| RML Mapper/RMLStreamer | Maintained tools for heterogeneous or streaming sources, but not the simplest default for Postgres-first mapping. ([RMLStreamer](https://github.com/RMLio/RMLStreamer)) |

**Consequences.**
- Mapping files become governed learning artifacts and keep semantic interpretation close to the relational source.
- Materialization is an explicit pipeline decision, with refresh and provenance requirements.
- The architecture follows “virtual RDF/OBDA first; materialize stable facts only.”

## ADR-HL-003 — Use pySHACL for RDF validation

**Status:** Accepted (for a personal homelab)

**Context.** The homelab needs executable quality checks for ontology-driven facts, KPI definitions, and mappings. pySHACL is Apache-2.0, actively maintained under the RDFLib organization, and validates RDF data against SHACL shapes in Python pipelines. ([pySHACL repository](https://github.com/rdflib/pyshacl))

**Decision.** Use **pySHACL** with RDFLib and run validation as a pipeline/CI gate.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| TopBraid SHACL API | Apache-2.0 and maintained, but Java/Jena-oriented; it adds a second implementation ecosystem to a Python-first homelab. ([TopBraid SHACL API](https://github.com/topquadrant/shacl)) |
| No formal validation | Would leave semantic and mapping errors to ad hoc review rather than repeatable tests. |

**Consequences.**
- Shapes become testable data-quality contracts for RDF outputs.
- Python jobs can fail fast before loading invalid graph data.

## ADR-HL-004 — Use Protégé Desktop for ontology authoring

**Status:** Accepted (for a personal homelab)

**Context.** Ontology work needs a visual OWL/RDFS editor alongside version-controlled source files. Protégé Desktop is actively released and supports OWL ontology editing; the reviewed release page describes its historical free/open-source distribution but does not explicitly state a license identifier, so that license detail should be rechecked at installation. ([Protégé Desktop releases](https://github.com/protegeproject/protege-distribution/releases))

**Decision.** Use **Protégé Desktop** as the primary authoring tool. **WebProtégé** is optional only if collaboration, browser editing, or revision history is needed. ([WebProtégé repository](https://github.com/protegeproject/webprotege))

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| WebProtégé | Free/open source and collaborative, but its active development is moving through an architectural migration; collaboration is not a core need for one user. ([WebProtégé repository](https://github.com/protegeproject/webprotege)) |
| Code-only ontology authoring | Reproducible but less suitable for visually learning classes, properties, restrictions, and imports. |

**Consequences.**
- Keep Turtle/OWL and SHACL files in version control; use the desktop editor as an authoring aid, not the system of record.
- Reassess the exact Protégé distribution terms whenever the installed version changes.

## ADR-HL-005 — Standardize the Python RDF stack on RDFLib and Owlready2

**Status:** Accepted (for a personal homelab)

**Context.** The pipeline needs general RDF parsing, serialization, graph handling, SPARQL, and optional OWL reasoning in Python. RDFLib is BSD-3-Clause and actively maintained; Owlready2 is LGPLv3 and supports ontology-oriented programming and reasoning. ([RDFLib repository](https://github.com/rdflib/rdflib)) ([Owlready2 on PyPI](https://pypi.org/project/owlready2/))

**Decision.** Use **RDFLib** as the core Python RDF library and **Owlready2** only where OWL reasoning or Python-object ontology access is valuable. Add **oxrdflib** optionally when a faster PyOxigraph-backed RDFLib store is needed. ([oxrdflib repository](https://github.com/oxigraph/oxrdflib))

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| RDFLib alone for all needs | It is sufficient for many tasks, but does not provide Owlready2’s ontology-as-objects and reasoning focus. ([Owlready2 on PyPI](https://pypi.org/project/owlready2/)) |
| oxrdflib everywhere | BSD-3-Clause and maintained, but an optimization path rather than a prerequisite for small local datasets. ([oxrdflib repository](https://github.com/oxigraph/oxrdflib)) |

**Consequences.**
- Python remains the common implementation language from mappings through validation and agents.
- LGPL obligations for Owlready2 must be understood before redistributing packaged derivatives.

## ADR-HL-006 — Use neosemantics (n10s) for self-hosted Neo4j RDF integration

**Status:** Accepted (for a personal homelab)

**Context.** Neo4j is the serving/query layer for the property graph, not an independent RDF source of truth. n10s imports/exports RDF including OWL, RDFS, and SKOS, supports SHACL validation, and is available for self-hosted Neo4j but not Aura; the reviewed sources describe it as a Labs plugin without explicitly classifying its license as OSS. ([Neo4j Labs neosemantics](https://neo4j.com/labs/neosemantics/))

**Decision.** Use **neosemantics (n10s)** for RDF interoperability in self-hosted Neo4j. Keep **rdflib-neo4j** as the future option if an Aura-compatible bridge becomes necessary. ([Neo4j rdflib-neo4j overview](https://neo4j.com/blog/developer/rdflib-neo4j-rdf-integration-neo4j/))

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| rdflib-neo4j | Open source per Neo4j’s description and Aura-compatible, but early access and a less direct fit than n10s for the self-hosted default. ([Neo4j rdflib-neo4j overview](https://neo4j.com/blog/developer/rdflib-neo4j-rdf-integration-neo4j/)) |
| Native LPG only | Avoids mapping trade-offs but loses RDF/OWL/SKOS import-export interoperability; RDF and LPG models do not map one-to-one. ([Neo4j Labs neosemantics](https://neo4j.com/labs/neosemantics/)) |

**Consequences.**
- RDF mappings must state how predicates, multi-valued properties, and reification are handled before loading Neo4j.
- Neo4j remains downstream of the RDF meaning layer, reducing competing-source-of-truth risk.

## ADR-HL-007 — Use LangGraph for agent orchestration and graph-grounded retrieval components

**Status:** Accepted (for a personal homelab)

**Context.** The agent must execute controlled, stateful tool flows across the knowledge graph and KPI data. LangGraph is MIT-licensed open source and is designed for stateful, multi-step agent workflows. ([LangGraph license](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)) ([LangGraph product page](https://www.langchain.com/langgraph))

**Decision.** Use **LangGraph** as the agent framework. Use **LlamaIndex Property Graph Index** and/or **neo4j-graphrag-python** as retrieval/graph-grounding components rather than as replacements for orchestration. ([LlamaIndex Property Graph documentation](https://developers.llamaindex.ai/python/framework-api-reference/indices/property_graph/)) ([Neo4j GraphRAG Python guide](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html))

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| CrewAI | MIT-licensed open source and appropriate for role-based multi-agent teams, but the homelab prioritizes explicit state and controllable graph workflows. ([CrewAI license](https://github.com/crewAIInc/crewAI/blob/main/LICENSE)) |
| LlamaIndex Property Graph Index | MIT-licensed and useful for property-graph retrieval, but it is a retrieval/index capability rather than the selected workflow controller. ([LlamaIndex license](https://github.com/run-llama/llama_index/blob/main/LICENSE)) |

**Consequences.**
- Tools must return traceable evidence and respect the distinction between raw measures, metrics, and approved KPI definitions.
- The agent design stays modular: orchestrator, retriever, model server, and graph/database tools can evolve independently.

## ADR-HL-008 — Use Ollama and Apache-2.0 local models by default

**Status:** Accepted (for a personal homelab)

**Context.** The homelab needs a reproducible local model server with an agent-friendly API. Ollama provides local model serving through a CLI/REST interface and an OpenAI-compatible API; vLLM is the scale-up inference option for GPU throughput. ([Ollama comparison](https://dev.to/synsun/running-local-llms-in-2026-ollama-lm-studio-and-jan-compared-121c)) ([vLLM documentation](https://docs.vllm.ai/en/latest/))

**Decision.** Use **Ollama** as the default local LLM runtime. Prefer **Qwen3.6-27B**, **Qwen3.6-35B-A3B**, or **Mistral Small 3.2 24B**, each Apache-2.0; adopt **vLLM** only for GPU-driven scale-up. ([Local-model comparison](https://runaihome.com/blog/llama-33-vs-qwen3-vs-mistral-local-ai-2026/))

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| vLLM | Open source and suited to high-throughput GPU serving, but adds complexity beyond the default single-user setup. ([vLLM documentation](https://docs.vllm.ai/en/latest/)) |
| LM Studio | Free but proprietary/closed source; it is not the reproducible, scriptable runtime baseline. ([LM Studio documentation](https://lmstudio.ai/docs/app)) |
| Llama 3.3 | Source-available community license with usage restrictions, rather than an OSI-approved open-source license. ([Local-model comparison](https://runaihome.com/blog/llama-33-vs-qwen3-vs-mistral-local-ai-2026/)) |

**Consequences.**
- Model and prompt configuration can be versioned and run offline after model acquisition.
- Hardware limits will shape quantization, context, and latency; no model is treated as an authoritative source.

## ADR-HL-009 — Use Dagster Core for orchestration

**Status:** Accepted (for a personal homelab)

**Context.** The stack needs to make raw tables, mappings, RDF outputs, validation, graph loads, and lineage visible as repeatable assets. Dagster Core is the open-source product and its Python asset model maps directly to this pipeline shape. ([Dagster repository](https://github.com/dagster-io/dagster))

**Decision.** Use **Dagster Core/OSS** as the default orchestrator.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Prefect | Apache-2.0, self-hostable, and lightweight for annotated Python functions; retain as an alternative if minimal setup outweighs asset lineage. ([Prefect open source](https://www.prefect.io/prefect/open-source)) |
| Apache Airflow | Apache-2.0 and strong for transferable industry skill, but has a heavier local operational model and a more rigid DAG/operator approach. ([Airflow release notes](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html)) |

**Consequences.**
- Each dataset, RDF graph, shape-validation result, and graph load can be represented as an asset with observable dependencies.
- The selected tool teaches asset lineage concepts parallel to, but not integrated with, enterprise governance tooling.

## ADR-HL-010 — Use DuckDB as the primary analytical database

**Status:** Accepted (for a personal homelab)

**Context.** Analytical exploration of market, terminal, and KPI-supporting data should be local and low-operations. DuckDB is an actively developed, MIT-licensed in-process columnar SQL engine that can query local files and Postgres-connected data without a server. ([DuckDB](https://duckdb.org/)) ([DuckDB license](https://github.com/duckdb/duckdb/blob/main/LICENSE))

**Decision.** Use **DuckDB** as the primary OLAP engine, including notebook-oriented analysis.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| ClickHouse | Apache-2.0 and actively maintained; reserve for a later persistent, multi-service or real-time scale-up need. ([ClickHouse repository](https://github.com/clickhouse/clickhouse)) |
| Apache Druid | Apache-2.0 and maintained, but designed for large-scale streaming/event OLAP and therefore overkill for the stated scope. ([Apache Druid licensing](https://druid.apache.org/licensing/)) |

**Consequences.**
- Small analytical workloads need no separate server lifecycle.
- A future move to ClickHouse is an explicit scale-up ADR, not an assumed requirement.

## ADR-HL-011 — Use PostgreSQL 18 with pgvector and optional Apache AGE

**Status:** Accepted (for a personal homelab)

**Context.** PostgreSQL is the operational source of truth for simplified order-to-cash entities and transactional facts. PostgreSQL 18 uses the liberal PostgreSQL License; pgvector adds open-source vector similarity search, and Apache AGE is Apache-2.0 graph/Cypher capability inside Postgres. ([PostgreSQL 18 announcement](https://www.postgresql.org/about/news/postgresql-18-released-3142/)) ([pgvector repository](https://github.com/pgvector/pgvector)) ([Apache AGE overview](https://age.apache.org/overview/))

**Decision.** Use **PostgreSQL 18** as the OLTP backbone, **pgvector** for embeddings, and **Apache AGE** only as an optional graph-in-RDBMS experiment.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Separate vector database | Adds a service boundary before Postgres-integrated vector search has been explored. ([pgvector repository](https://github.com/pgvector/pgvector)) |
| TimescaleDB packaged distribution | Advanced features are source-available under the Timescale License rather than fully open source; use plain Postgres partitioning or DuckDB unless that trade-off is explicitly accepted. ([Timescale licensing](https://www.tigerdata.com/legal/licenses)) |

**Consequences.**
- Transactional facts remain in a familiar relational system with ACID behavior.
- Apache AGE experiments must not blur the responsibility boundary with Neo4j.

## ADR-HL-012 — Use OpenLineage and Marquez for lineage and observability

**Status:** Accepted (for a personal homelab)

**Context.** Pipeline lineage should connect source datasets, mapping runs, RDF outputs, and graph loads. OpenLineage is an Apache-2.0 open standard for job/dataset/run metadata, and Marquez is its Apache-2.0 reference collection and visualization implementation. ([OpenLineage repository](https://github.com/OpenLineage/openlineage)) ([Marquez repository](https://github.com/MarquezProject/marquez))

**Decision.** Emit **OpenLineage** events and use **Marquez** as the local lineage backend/UI.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Logs only | Useful for debugging but not sufficient for navigable dependency and run lineage. |
| Enterprise catalog/lineage products | Outside the personal, open-source, single-machine scope. |

**Consequences.**
- Dagster assets and lineage events can explain how a graph or KPI-supporting dataset was produced.
- PROV-O remains the semantic provenance vocabulary; OpenLineage/Marquez handles operational pipeline observability.

## ADR-HL-013 — Use SKOS and PROV-O as metadata standards

**Status:** Accepted (for a personal homelab)

**Context.** The homelab needs durable semantic standards for a business glossary/taxonomy and provenance. SKOS and PROV-O are mature W3C Recommendations; SKOS models concepts and hierarchical labels, while PROV-O represents entities, activities, agents, and derivation relationships. ([W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)) ([W3C PROV-O](https://www.w3.org/TR/prov-o/))

**Decision.** Use **SKOS** for glossary/taxonomy concepts and **PROV-O** for semantic provenance. Treat Google’s **Open Knowledge Format (OKF)** as a specification to watch, not a dependency.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Google Open Knowledge Format | Publicly readable and vendor-originated, but no clear open-source license was identified and no formal standards-body ratification is documented; it remains early-stage. ([Google Cloud OKF overview](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)) ([OKF repository](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md)) |
| Tool-specific glossary/lineage schemas | Reduce portability and obscure the distinction between semantic provenance and operational lineage. |

**Consequences.**
- Terms such as refining margin, netback, BOL, and custody event can be represented as reusable governed concepts.
- Semantic provenance can link mappings, data products, and graph assertions without depending on a vendor format.

## ADR-HL-014 — Use ERPNext with light custom Frappe workflows as the SAP-analog O2C system of record

**Status:** Accepted (for a personal homelab)

**Context.** The homelab needs a self-hosted ERP covering all ten Order-to-Cash process groups (downstream O&G redline, approved 2026-08-09) in the Deloitte-style taxonomy. ERPNext is GPL-3.0 software built on the Frappe framework and natively supports the Quotation → Sales Order → Delivery Note → Sales Invoice → Payment Entry flow for Master Data Mgmt, Quote & Sale, Order & Fulfillment, Billing, and Receipt. It was already proven for O2C in the owner’s own `scada_harmonization` repository. ([ERPNext repository](https://github.com/frappe/erpnext)) ([scada_harmonization PR #18](https://github.com/aadehamid/scada_harmonization/pull/18)) ERPNext has no native DocType for Credit & Risk, Collection, Dispute, Close, or Measure & Custody Transfer (a new Level 1 group added 2026-08-09 for custody-transfer/quantity-quality determination, mirroring the EPM blueprint's separate Measure/Title chevron).

**Decision.** Use **ERPNext** for the five natively supported groups. Add light custom Frappe DocTypes—**Credit Limit Review**, **Collection Case**, **Dispute Case**, **AR Sub-Ledger Close Task**, and **Custody Transfer Ticket**—with minimal state-transition workflows for the remaining five groups, rather than treating them as data-only simulation or describe-only. This is an explicit scoping decision confirmed on 2026-08-09.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Odoo | A viable GPL/LGPL open-core ERP, but it has not been previously proven in the owner’s own work. |
| Pure synthetic-data-only simulation of the five gap groups | Would lose realistic state-transition and workflow learning value. |
| Full custom-built ERP module | Excessive scope for a personal homelab. |

**Consequences.**
- ERPNext becomes the single relational system of record for all ten process groups.
- The five custom DocTypes must be documented as homelab-specific extensions, not standard ERPNext functionality.

## ADR-HL-015 — Use trycompai/crm as the Salesforce-analog external CRM source system

**Status:** Accepted (for a personal homelab)

**Context.** The owner’s Customer Data Dictionary Template models canonical customer/party data across a Salesforce-analog CRM and a SAP-analog ERP. trycompai/crm is a real, actively maintained, MIT-licensed, self-hostable CRM built with TypeScript, Bun, Next.js, NestJS, Prisma, and PostgreSQL; it runs through Docker Compose and Bun. ([trycompai/crm repository](https://github.com/trycompai/crm))

**Decision.** Use **trycompai/crm** as the external CRM/Salesforce-analog source system for Account, Contact, and party master data, integrated into Master Data Mgmt rather than as core pipeline code. It is an external system being harmonized, not a replacement for the Python-first pipeline.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| SuiteCRM | PHP-based with an older architecture and less active modernization. |
| Build customer master directly in ERPNext only | Would lose the two-source MDM harmonization scenario that the Customer Data Dictionary Template is designed to teach. |

**Consequences.**
- A second relational source system requires an explicit customer-entity harmonization and matching step before knowledge-graph load.
- This added step is intentional because MDM and matching are core learning goals.

## ADR-HL-016 — Use semantica-agi/semantica for unstructured+structured knowledge-graph fusion

**Status:** Accepted (for a personal homelab)

**Context.** The homelab needs to fuse unstructured artifacts—SOPs, emails, invoice PDFs, and Buzz team-channel messages—with relational ERPNext/PostgreSQL data into one graph. semantica-agi/semantica is MIT-licensed, active, and has 3,412+ stars; it supports both Neo4j property graphs and RDF stores including Oxigraph, Blazegraph, Jena, and RDF4J through one API, with SHACL/OWL governance, PROV-O provenance, and native ingestion connectors for files (PDF, DOCX, PPTX, HTML, TXT, CSV, JSON, XML, and Excel), email (IMAP/POP3), and message streams (Kafka, RabbitMQ, Kinesis, and Pulsar). ([semantica repository](https://github.com/semantica-agi/semantica))

**Decision.** Adopt **semantica** as the ingestion and fusion layer sitting atop the already chosen Ontop/Morph-KGC/Fuseki/Neo4j stack (ADR-HL-001, ADR-HL-002, and ADR-HL-006), specifically for the unstructured corpus. Keep Ontop and Morph-KGC as the relational-to-RDF path for structured ERPNext/PostgreSQL data.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Custom Python ingestion scripts per document type | More maintenance and no built-in entity resolution or conflict detection; retain only where a small adapter is necessary. |
| LlamaIndex/LangChain document loaders alone | Viable for chunking, but lack semantica’s native RDF, SHACL, and PROV-O governance integration. |

**Consequences.**
- Entity-linking IDs—`customer_id`, `order_id`, `invoice_id`, and `dispute_id`—must be consistently embedded in every generated unstructured artifact.
- These identifiers enable semantica entity extraction to resolve artifacts against the same graph nodes populated from the relational side.

## ADR-HL-017 — Use block/buzz as the team-channel simulation and agent-participation layer

**Status:** Accepted (for a personal homelab)

**Context.** The homelab needs to simulate unstructured team-channel discussion, such as dispute and exception threads, that is entity-linked to relational O2C data. block/buzz is an actively maintained Apache-2.0 Rust project with 25,700+ stars: a self-hostable, Nostr-relay-based workspace in which humans and AI agents are first-class channel members with their own signing keys and an audit trail. It ships `buzz-cli`, described as JSON-in/JSON-out and designed for LLM tool calls. ([block/buzz repository](https://github.com/block/buzz))

**Decision.** Self-host **Buzz** through its production Docker Compose bundle in `deploy/compose/`, including PostgreSQL, Redis, and MinIO. Use `buzz-cli` to let a scripted process or the capstone AI agent itself generate realistic dispute and exception discussion threads that reference real order, invoice, and dispute IDs. Export the underlying Nostr event log as structured JSON for semantica ingestion.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Mattermost | Open source, but heavier, not agent-native, and without a first-class agent identity model. |
| Purely LLM-generated flat-text chat transcripts | Would lose the agent-as-participant capstone learning opportunity and would not provide a realistic event-log export format. |

**Consequences.**
- Buzz becomes an additional self-hosted service in the Docker Compose stack documented in Document 06.
- Its Nostr event export format requires a small adapter script before semantica ingestion.

## ADR-HL-018 — Add an MCP server as an agent-agnostic serving component

**Status:** Accepted (for a personal homelab)

**Context.** AWS's Context Ontology Accelerator (COA), a GA open-source accelerator announced 2026-07-31, serves its knowledge graph to agents through a standalone MCP server, separate from any single application's own agent, explicitly to be "agent-agnostic" ([COA docs](https://aws.github.io/context-ontology-accelerator/); [COA GitHub repo](https://github.com/aws/context-ontology-accelerator)). The homelab's current design (ADR-HL-007) only exposes the Neo4j/DuckDB knowledge graph through the homelab's own LangGraph agent's tool calls, which means no other agent or client (Claude Desktop, Cursor, etc.) can query the homelab's graph without going through that one app.

**Decision.** Add a small MCP server, built on the official `modelcontextprotocol/python-sdk`, as a new Consumption-layer component alongside FastAPI (Document 01). Expose a minimal, read-only tool set: a KPI Store lookup tool (queries the DuckDB fact table), a Cypher query tool (queries Neo4j read-only), and a SPARQL query tool (queries Fuseki). This runs alongside, not instead of, the existing LangGraph agent and FastAPI backend.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Only expose the graph through FastAPI REST endpoints | Works for the homelab's own UI/agent but is not directly consumable by MCP-native clients like Claude Desktop or Cursor without a custom adapter |
| Only expose the graph through the LangGraph agent's own tools | Ties graph access to one specific agent framework, defeating the "any agent can consume it" learning objective this ADR is meant to demonstrate |

**Consequences.**
- A new `mcp-server` service/process is added to Document 06's repository structure and Docker Compose skeleton.
- The MCP server is read-only and bound to `127.0.0.1` by default, consistent with the homelab's local-only security posture (Document 01, Non-functional considerations) — it is not exposed to the public internet.
- Tool schemas for the MCP server should mirror the KPI Store/graph query surface already defined for FastAPI, avoiding duplicated business logic.

## ADR-HL-019 — Add an Owlready2/HermiT reasoning gate before ontology materialization

**Status:** Accepted (for a personal homelab)

**Context.** AWS's Context Ontology Accelerator's ontology-engine package runs ontology induction and reasoning (HermiT/ELK) as an explicit step of its Model stage, before an ontology proposal is published to the knowledge graph ([COA GitHub repo](https://github.com/aws/context-ontology-accelerator)). The homelab already selected Owlready2 for "reasoning and OWL-as-Python-classes when needed" (ADR-HL-005) but had not made reasoning an explicit, required pipeline step. Owlready2 ships a modified HermiT reasoner and runs it via a single `sync_reasoner()` call, which performs consistency checking and automatically reclassifies individuals and classes based on their asserted relations ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html)).

**Decision.** Add a new Dagster asset that loads the current T-Box (Document 05) into Owlready2 and calls `sync_reasoner()` (HermiT, the Owlready2 default) to check consistency and reclassify instances/classes. This asset gates the existing Morph-KGC materialization asset (ADR-HL-002): materialization only proceeds if the reasoner reports the ontology as consistent. Inferred facts are written to a separate inference ontology rather than merged silently into the asserted T-Box, so the distinction between asserted and inferred knowledge stays visible.

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Pellet via `sync_reasoner_pellet()` | Also bundled with Owlready2 and supports data-property inference, but is AGPL-licensed versus HermiT's LGPL, and HermiT is Owlready2's default; keep Pellet as a documented optional alternative for when data-property inference is specifically needed ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html)) |
| No reasoning gate; rely only on pySHACL (ADR-HL-003) | SHACL validates instance-level shape constraints but does not perform OWL consistency checking or classification — the two techniques are complementary, not substitutes |

**Consequences.**
- A Java Virtual Machine is required in the Dagster/pipeline environment, since HermiT and Pellet are both Java-based ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html)).
- Document 06's phased build backlog gains an explicit reasoning-gate task under the domain modeling/ontology phase.
- Document 01's data-flow narrative gains an explicit ontology-validation step between "Expose virtual meaning" and "Materialize the stable semantic subset."

## ADR-HL-020 — Formalize a tiered governed-metric resolution model with a visible resolution trace

**Status:** Accepted (for a personal homelab)

**Context.** AWS's Context Ontology Accelerator's Serve stage names three explicit resolution tiers for answering an agent's question — a governed metric (pre-computed, deterministic, 0 LLM calls), a structured ontology query over a virtual knowledge graph, and an agentic fallback with knowledge synthesis — and returns a visible resolution trace showing which tier answered the question and its provenance ([COA docs](https://aws.github.io/context-ontology-accelerator/)). The homelab's Document 01 step "Answer with an accountable path" already does something functionally similar (FastAPI checks the KPI Store fact table, then Neo4j, then the LangGraph agent synthesizes), but the tiers were not explicitly named, ordered, or surfaced to the caller.

**Decision.** Formalize the existing answer path into three explicitly named tiers, applied consistently in both the FastAPI backend and the new MCP server (ADR-HL-018):
- **Tier 0 — Governed metric.** A pre-computed KPI Store fact-table value (DuckDB). Deterministic, 0 LLM calls.
- **Tier 1 — Structured graph query.** A Cypher query against Neo4j or a SPARQL query against Fuseki/Ontop for concepts, topology, or facts not pre-computed as a KPI.
- **Tier 2 — Agentic fallback.** The LangGraph agent synthesizes an answer using Ollama and KG-grounded retrieval when Tiers 0–1 cannot resolve the question.

Every answer returned by FastAPI or the MCP server includes a resolution trace: which tier answered, the source table/query, and (where applicable) the Dagster run id or materialization identifier from OpenLineage/Marquez (ADR-HL-012).

**Alternatives considered.**

| Alternative | Why not selected as the baseline |
|---|---|
| Leave the existing fact-table-then-graph-then-agent order implicit, undocumented | Misses the teaching opportunity and the direct parallel to the enterprise EPM KPI Store's governance/auditability goals |
| Route every question through the LangGraph agent, letting it decide internally which tool to call | Loses the deterministic, 0-LLM-call fast path for pre-computed KPIs and makes the resolution path opaque to the caller |

**Consequences.**
- Document 01's "Answer with an accountable path" narrative is rewritten to name the three tiers explicitly.
- FastAPI and MCP server responses gain a small, consistent resolution-trace payload shape.
- This pattern is a direct, demonstrable parallel to the enterprise EPM project's KPI Store consumption/governance goals, useful for portfolio and learning-transfer purposes.

## ADR-HL-021 — No enterprise triple store; Turtle in git, expose through Neo4j

**Status:** Accepted (lab transfer rule and intended enterprise landing)

**Context.** The target band split is [MEANING vs COMPUTE](../architecture/EPM-ARCH-MEANING-vs-COMPUTE.jpg): meaning does not compute; the only join is one ontology IRI to one certified catalog row to one semantic-layer object. The intended enterprise landscape is ER/Studio, Databricks (Unity Catalog, Lakebase, Metric Views), BigEye, and Purview. That estate has **no triple store**. It already has **Neo4j**, unused. Introducing Fuseki, Neptune, GraphDB, or a Lakebase SPO table as a second meaning store would be a second program.

Machine ontology SoT is already Turtle in git ([EPM-FOUND-000](../EPM-FOUND-000.md); [metadata integration spec](../metadata%20Integration/enterprise-metadata-integration-architecture-specification.md)). Fuseki is listed there as demo runtime only.

**Decision.**
- Do not add a client triple store.
- Store published meaning as Turtle in git. That file is the store of triples, not a triple-store product.
- Load the published Turtle into **Neo4j** (n10s or an equivalent RDF import) and expose it there (Browser, Bloom, Cypher, MCP). Reload from git. Do not edit meaning in Neo4j.
- That graph is the **graph of meaning**: concepts, named KPIs, IRIs, process, catalog bindings. It is not a node per Databricks table and not an A-Box of Silver facts.
- **Apache Jena Fuseki remains in the homelab** so SPARQL and server-side SHACL can be learned (ADR-HL-001). It does not transfer.
- Lakebase stays the **ODS** (ops ingredients). A Lakebase SPO table is a fallback meaning runtime only if Neo4j stays dark. It is not SoT.

**Alternatives considered.**

| Alternative | Why not selected |
|---|---|
| Fuseki or another SPARQL server in the client estate | No triple-store seat; procurement and ops for a product they do not have |
| Lakebase SPO (OntoBricks default) as the primary meaning store | Databricks-native, but fights the unused-Neo4j serve seat and invites an A-Box of Silver |
| Purview / UC as the only meaning graph | Catalog is the certified-row seat, not a traversable graph of meaning |
| Neo4j as SoT | Edits would fork from git Turtle |

**Consequences.**
- Transfer rehearsal is: write Turtle → validate (pySHACL / HermiT) → commit → n10s load → Cypher competency questions → catalog row with IRI → Metric View compile.
- Agent contract on both lab and client: Cypher “which KPI” → catalog lookup → submit the certified measure. No formula authorship in the graph.

## ADR-HL-022 — OntoBricks drafts Turtle; dbxmetagen drafts catalog metadata

**Status:** Accepted (optional Databricks-workspace tools; not homelab core)

**Context.** The client will have many Unity Catalog tables with no Turtle. [OntoBricks](https://github.com/databrickslabs/ontobricks) can LLM-generate OWL from UC metadata, export Turtle/R2RML, and optionally materialize triples. [dbxmetagen](https://github.com/databricks-industry-solutions/dbxmetagen) can generate UC comments, tags, domain class, a catalog-metadata graph, and (if allowed) Metric Views and Genie spaces. Both are Databricks License: use only with Databricks Services. Neither is an OSI-open homelab core dependency. The 1:1 gate still holds: a table-induced `Customer` class is not a KPI.

**Decision.**

| Tool | Allowed seat | Forbidden seat |
|---|---|---|
| OntoBricks | **Draft factory** for one bounded domain/Gold mart. Export OWL. Steward reviews, rewrites, and **commits Turtle to git**. Neo4j serves that file. | SoT. Wizard-on-the-whole-catalog. Materialized Lakebase/Delta triples as the graph of meaning. KPI compile. |
| dbxmetagen | **Catalog assistant** on the PREPARE band: comments, tags, domain labels, steward review (`apply_ddl=false`). `customer_context` may carry ubiquitous language and IRIs. | Ontology SoT. Auto-applied Metric Views or Genie-written SQL. A second compiler. |

Industry bundles shipped with these tools (FIBO, FHIR, OMOP, Schema.org, Dublin Core) are hints, not EPM modules.

**Alternatives considered.**

| Alternative | Why not selected |
|---|---|
| Make OntoBricks the enterprise ontology workbench and skip git | Violates Turtle-in-git SoT and the unused-Neo4j serve path |
| Use dbxmetagen Metric View generation as the compiler | Second formula path; conflicts with the MEANING vs COMPUTE compile band |
| Reject both tools entirely | Leaves no bootstrap for hundreds of undocumented UC tables |

**Consequences.**
- Homelab core stack is unchanged (Protégé, RDFLib, Fuseki classroom, Neo4j serve, Ontop/Morph-KGC).
- A later Databricks workspace may run OntoBricks or dbxmetagen as optional assistants. Published meaning still leaves those apps as Turtle in git.
- Databricks License tools stay off the “prefer genuinely open” core list (see license risk summary).

## License risk summary

The baseline favors genuinely open-source software and open W3C standards. The following tools or specifications require an explicit exception, a future recheck, or avoidance because their free availability does not make them open source, or because they are abandoned.

| Tool or specification | Actual license or maintenance status | Homelab treatment |
|---|---|---|
| AllegroGraph | Proprietary EULA; Free edition capped at 5M triples. ([AllegroGraph editions](https://allegrograph.com/allegrograph-editions/)) | Reject as a core dependency |
| Amazon Neptune | Proprietary managed AWS service; no self-hostable open-source version. ([Amazon Neptune](https://aws.amazon.com/neptune/)) | Reject as a core dependency |
| Stardog Free | Proprietary, revocable evaluation-only license. ([Stardog Free license](https://www.stardog.com/legal/stardog-free/)) | Reject as a core dependency |
| Ontotext GraphDB Free | Proprietary/free-to-use, license-key requirement, source not published, capped concurrency. ([GraphDB licensing](https://graphdb.ontotext.com/documentation/11.4/licensing.html)) | Reject as a core dependency |
| LM Studio | Free desktop application but closed source. ([LM Studio documentation](https://lmstudio.ai/docs/app)) | Reject; use Ollama or vLLM |
| TimescaleDB packaged distribution | Source-available Timescale License for advanced/packaged capability, not fully open source. ([Timescale licensing](https://www.tigerdata.com/legal/licenses)) | Avoid unless exception is documented |
| Llama 3.3 models | Source-available community license with usage restrictions, not OSI-approved open source. ([Local-model comparison](https://runaihome.com/blog/llama-33-vs-qwen3-vs-mistral-local-ai-2026/)) | Prefer Apache-2.0 Qwen3.6 or Mistral Small |
| Google Open Knowledge Format | Public specification with no stated open-source license and no standards-body ratification. ([Google Cloud OKF overview](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)) | Watch; do not build on it |
| Blazegraph | GPLv2 open source, but formally archived and abandoned. ([Blazegraph releases](https://github.com/blazegraph/database/releases)) | Avoid for new builds |
| D2RQ | Apache-2.0 open source, but archived and effectively abandoned. ([D2RQ repository](https://github.com/d2rq/d2rq)) | Avoid for new builds |
| Databricks Labs OntoBricks | Databricks License; use only with Databricks Services. Labs AS-IS, no SLA. ([OntoBricks](https://github.com/databrickslabs/ontobricks)) | Optional enterprise draft factory (ADR-HL-022). Not a homelab core dependency |
| dbxmetagen | Databricks License; use only with Databricks Services. ([dbxmetagen](https://github.com/databricks-industry-solutions/dbxmetagen)) | Optional enterprise catalog assistant (ADR-HL-022). Not a homelab core dependency |

## Related homelab documents

- `00-Homelab-Charter-and-Roadmap.md`
- `01-Reference-Architecture.md`
- `03-Curriculum-and-Learning-Modules.md`
- `04-Data-Strategy-and-Datasets.md`
- `05-Domain-Model-and-Ontology-Pilot.md`
- `06-Repo-Structure-and-Build-Plan.md`

**See also (enterprise EPM parallel):** Architecture Decision Log. This is a conceptual parallel for learning and traceability only, not a governed EPM decision record.
