# Homelab Stack Decisions (shared reference for all homelab documents)

Use this EXACT terminology, tool set, and naming across every homelab document. Do not substitute alternative tools without flagging it as an "alternative/optional" callout. These are recommended defaults for a personal, single-user, single-machine (or small home server) learning homelab — not a production enterprise deployment.

## Project naming
- Project name: **Downstream O&G Knowledge Homelab** (a personal, educational sandbox inspired by and loosely parallel to the enterprise "Enterprise Performance Model" (EPM) initiative the owner works on professionally — but NOT part of the governed EPM artifact set, not subject to EPM approval workflow, and free to take shortcuts EPM cannot).
- Owner: Hamid Adesokan.
- Domain scenario: Downstream Oil & Gas — refining margin/netback, wholesale rack marketing, terminal custody transfer, retail fuel, order-to-cash — chosen because it mirrors the owner's professional domain (Downstream O&G, EPM/KPI Store work) so learning transfers directly.

## Layer-by-layer tool decisions (baseline / default path)

| Layer | Tool | License | Why (one line) |
|---|---|---|---|
| Containerization | Docker Compose | Apache-2.0 (Docker Compose itself) | Single-command local spin-up/tear-down of the whole stack |
| Operational database (OLTP) | PostgreSQL 18 | PostgreSQL License (OSI-approved, MIT/BSD-style) | Industry-standard, owner already knows SQL; source of truth for order-to-cash entities |
| OLTP extensions | pgvector (embeddings), Apache AGE (optional native graph/Cypher experiment) | Apache-2.0 (both) | Lets the agent do vector search directly in Postgres; AGE is optional exploration of graph-in-RDBMS vs. Neo4j |
| Analytical database (OLAP) | DuckDB (primary) | MIT | Zero-ops, in-process, perfect for a single-machine homelab; ClickHouse (Apache-2.0) is the noted scale-up alternative if the homelab grows to a multi-service/streaming setup |
| Orchestration | Dagster (Core/OSS) | Apache-style OSS | Python-native, asset-based mental model maps directly onto a KG pipeline (raw tables → RDF triples → graph loads); Prefect (Apache-2.0) is the noted lightweight alternative, Airflow (Apache-2.0) is the noted "industry-transferable-skill" alternative |
| Ontology authoring | Protégé Desktop | Free/open (Stanford) | Visual OWL/RDFS editor; WebProtégé noted as optional collaborative alternative |
| Python RDF library | RDFLib | BSD-3-Clause | Core Python RDF graph handling, Turtle/JSON-LD parsing, SPARQL |
| Python ontology-as-objects | Owlready2 | LGPL v3 | Reasoning and OWL-as-Python-classes when needed |
| Fast RDFLib store backend (optional) | oxrdflib (PyOxigraph-backed) | BSD-3-Clause | Drop-in faster store than RDFLib's default in-memory store |
| SHACL validation | pySHACL | Apache-2.0 | Python-native, integrates with RDFLib pipelines; run in CI |
| Relational→RDF mapping (virtual, default) | Ontop | Apache-2.0 | Exposes Postgres as a live virtual RDF/SPARQL graph with NO ETL/copy step — matches the "operational store stays source of truth" principle already discussed |
| Relational→RDF mapping (materialize, when needed) | Morph-KGC | Apache-2.0 | Python engine to materialize an actual RDF graph from R2RML/RML mappings when you want to load curated facts into a triple store or Neo4j |
| Triple store / SPARQL classroom (lab only) | Apache Jena Fuseki | Apache-2.0 | Homelab SPARQL/SHACL classroom (ADR-HL-001). Learns SPARQL. Does **not** transfer to the client. Enterprise has no triple store. |
| Meaning SoT | Turtle files in git | W3C RDF 1.1 Turtle | The triples live in git. Not a triple-store product. |
| Meaning expose / serving graph | Neo4j Community Edition + n10s | GPLv3 / Neo4j Labs | Load **published** git Turtle. Client already has unused Neo4j. This is the transfer seat (ADR-HL-021). |
| Lightweight/embedded triple store (optional exploration) | Oxigraph | Apache-2.0 / MIT dual | Optional no-server SPARQL comparison in the lab only |
| RDF ↔ Neo4j bridge | neosemantics (n10s) (self-hosted only, not Aura) | Neo4j Labs plugin | Imports/exports RDF (incl. OWL/RDFS/SKOS) into/out of Neo4j's LPG model, validates against SHACL; `rdflib-neo4j` is the noted alternative if ever moving to Neo4j Aura |
| AI agent orchestration | LangGraph | MIT | Stateful, controllable agent graphs; used to wire an LLM agent to the Neo4j knowledge graph and the KPI Store as tools |
| KG-grounded retrieval | neo4j-graphrag-python and/or LlamaIndex Property Graph Index | Open source (Neo4j Labs) / MIT | Purpose-built for grounding LLM answers in a Neo4j graph (GraphRAG pattern) |
| Local LLM serving | Ollama | Open-source runtime | Simple local model serving, OpenAI-compatible API, works with LangGraph out of the box |
| Recommended local models | Qwen3.6-27B or Qwen3.6-35B-A3B or Mistral Small 3.2 24B | Apache-2.0 (all three) | Fully open license, unlike Llama 3.3's restricted community license |
| Backend API | FastAPI | MIT | Python-native, owner's existing ecosystem; exposes KPI-on-demand and agent endpoints |
| Agent-agnostic serving | MCP server (official `modelcontextprotocol/python-sdk`) | MIT | Exposes KPI Store, graph, and SPARQL/Cypher query tools over the Model Context Protocol so ANY MCP-compatible client (Claude Desktop, Cursor, etc.), not only the homelab's own LangGraph agent, can consume the homelab's knowledge graph — pattern borrowed from AWS Context Ontology Accelerator's "Serve" stage ([python-sdk](https://github.com/modelcontextprotocol/python-sdk)) |
| Ontology reasoning gate | Owlready2's built-in HermiT reasoner (`sync_reasoner()`) | LGPL v3 (Owlready2); HermiT itself LGPL | Runs OWL consistency checking and automatic reclassification on the T-Box before any Turtle release is materialized or published — pattern borrowed from AWS Context Ontology Accelerator's ontology-engine reasoning step ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html)) |
| Data lineage/observability | OpenLineage + Marquez | Apache-2.0 (both) | Adds pipeline lineage visualization to the Dagster pipeline, teaching the same lineage concepts the enterprise EPM project cares about (Purview/PROV-O) |
| Metadata/glossary standard | SKOS (W3C Recommendation) | Open W3C standard | Models the homelab's business glossary/taxonomy layer |
| Provenance standard | PROV-O (W3C Recommendation) | Open W3C standard | Models lineage/provenance in the ontology itself |

## Explicit "do not use as core dependency" list (with reason)
- **GraphDB (Ontotext), Stardog, AllegroGraph, Amazon Neptune** — proprietary; free tiers are capped/evaluation-only, source not published. Fine to try once out of curiosity but not the homelab's dependency baseline.
- **Blazegraph** — genuinely open source (GPLv2) but formally archived March 2026; no active development.
- **D2RQ** — genuinely open source (Apache-2.0) but archived since January 2021.
- **LM Studio** — free but closed-source desktop app; use Ollama or vLLM instead for a reproducible, scriptable homelab.
- **TimescaleDB (packaged)** — source-available Timescale License, not fully open; if time-series-in-Postgres is wanted, note this caveat or prefer plain Postgres partitioning / DuckDB.
- **Llama 3.3 models** — source-available community license with usage restrictions; prefer Qwen3.6 or Mistral Small 3.2 (Apache-2.0) for a fully open homelab.
- **Google's Open Knowledge Format (OKF)** — an emerging Google-authored specification, publicly viewable on GitHub, but with no stated open-source license and no formal standards-body ratification as of research date. Treat as "watch, don't build on yet." Rely on SKOS/PROV-O/RDF/OWL/SHACL instead.
- **OPIS, S&P Global Platts** — paid commercial data services; use EIA Petroleum Marketing Monthly (rack prices) and EIA Spot Prices as the free substitutes.
- **OntoBricks and dbxmetagen** — Databricks License; not homelab core. Optional on a Databricks workspace as draft assistants only (ADR-HL-022).

## Lab vs enterprise transfer (ADR-HL-021 / ADR-HL-022)

Target picture: [MEANING vs COMPUTE](../architecture/EPM-ARCH-MEANING-vs-COMPUTE.jpg).

| Concern | Homelab (learn it) | Transfers to client |
|---|---|---|
| Meaning SoT | Turtle in git | Same |
| SPARQL classroom | Fuseki (ADR-HL-001) | No. Client has no triple store. |
| Expose / graph of meaning | Neo4j + n10s load of published Turtle | Same. Client already has unused Neo4j. |
| Ops facts | PostgreSQL 18 | Lakebase (Databricks Postgres) |
| Compile | DuckDB + MetricFlow in Track A; Metric Views in Track B | Databricks Metric Views only |
| KPI Store row (identity, approval, status, formula pointer, ontology IRI) | `dim_kpi_metadata` (`proposed \| approved \| drifted \| archived`) | Same Store seat. The Store owns this row. |
| Asset discovery / technical catalog | OpenMetadata (lab stand-in) | Purview (discovery/stewardship). Unity Catalog (tables, Metric Views, access). Not the Store door. |
| Data quality on Silver/Gold | dbt tests / SHACL on meaning | BigEye (SHACL is not BigEye) |
| Bootstrap Turtle from existing tables | Optional later; Protégé is the lab author | OntoBricks **draft** → review/rewrite → git Turtle → Neo4j |
| Bootstrap UC comments/tags | Not required in the lab | dbxmetagen **draft**; never auto-apply Metric Views |

Do not ontologize the whole lakehouse. Formal Turtle covers named KPIs and the concepts they bind.

## Architecture principle carried over from the enterprise EPM project
Operational and analytical data (Postgres, DuckDB) remain the systems of record for volume/transactional facts. The RDF/OWL ontology is the **meaning layer** — definitions, classes, relationships, KPI specs, lineage — accessed virtually via Ontop wherever possible rather than duplicated. Neo4j is a **serving/query layer** for the graph (populated from published git Turtle via n10s, and from Morph-KGC only for stable curated facts), not a second independent source of truth. This mirrors the "virtual RDF/OBDA first, materialize only stable facts" decision already explored for the enterprise EPM ontology work. The client landing is the same meaning file with no Fuseki: git Turtle → Neo4j.

## Source documents already produced (read these, cite from them, do not re-derive facts)
- [research_oss_tool_stack.md](../research_oss_tool_stack.md) — placeholder; the full tool license/maintenance research was not committed. Use this file and [02-Tool-Selection-and-ADRs.md](02-Tool-Selection-and-ADRs.md) as the in-repo authority.
- [research_public_datasets.md](../research_public_datasets.md) — placeholder; the full public-dataset research was not committed. Use [04-Data-Strategy-and-Datasets.md](04-Data-Strategy-and-Datasets.md) as the in-repo authority.

## Enterprise EPM context to reference (for continuity/flavor, NOT to duplicate verbatim)
- EPM chain: Enterprise Strategy & Objectives → Business Domains → Value Streams & Stages → Capabilities → Business Processes → Activities/Events/Decisions/Outcomes → Measurements & Metrics → governed Enterprise KPIs → Data Products → KPI Store/Semantic Views/Power BI → Reports/APIs/Analytics/Automation/AI.
- KPI Store = governed persistence/consumption layer for APPROVED KPIs only; measurement classification (raw measure → business measure → derived measure → operational metric → diagnostic/analytical metric → performance indicator → candidate KPI → approved KPI → technical calculation → presentation-only → duplicate/near-duplicate → obsolete/retired) gates entry.
- The enterprise's first pilot is "Commercial Margin / Gasoline Netback CPG" tracing objective → KPI → metrics/drivers → domain concepts → data products → KPI Store → semantic views → Power BI → lineage → ontology/graph links. The homelab should build a SIMPLIFIED, personal, open-source-only version of this exact same kind of vertical trace (a "Refining Margin / Crack Spread" or "Gasoline Netback" KPI) as its own capstone pilot, since the pattern is proven and the public EIA data (crack spread methodology, spot prices, PMM rack prices) directly supports it.
- Downstream O2C is custody-event-centric: GOV/GSV/NSV volume correction (API MPMS 11.1/ASTM D1250), BOL/ticket flow, formula/index pricing, excise tax status. The homelab's synthetic order-to-cash schema should mirror this shape at a simplified/personal scale.

## Formatting rules for every homelab document
- Markdown only. Use `##`/`###` headers, tables, and fenced code blocks (` ```turtle `, ` ```sparql `, ` ```yaml `, ` ```python `, ` ```mermaid ` or ASCII art for diagrams).
- Every external fact/tool/dataset claim must carry an inline markdown link citation, e.g. `([Apache Jena](https://jena.apache.org/download/index.cgi))`. Pull these URLs from the two research files above — do not invent URLs.
- Start each document with a short header block: Title, Purpose (1-2 lines), Status: Draft (personal homelab, not an EPM governed artifact), Owner: Hamid Adesokan, Last updated: 2026-08-09.
- End each document with a "Related homelab documents" list (the other 6 documents, by filename) and, where relevant, a "See also (enterprise EPM parallel)" line pointing to the conceptual EPM artifact it mirrors (e.g., "mirrors the EPM KPI Store" or "mirrors the EPM Downstream O2C Blueprint") — for flavor/context only, not as a claim of formal linkage.
- Do not use emojis. Do not use exclamation points. Keep prose concise; prefer tables and structured lists over long paragraphs.

## O2C Process Taxonomy v2 — Downstream O&G Redline — updated 2026-08-09 (supersedes v1 generic taxonomy)

STATUS: Approved by project owner 2026-08-09, supersedes the v1 generic Deloitte-style taxonomy previously recorded in stack_decisions.md. Source: `research_o2c_downstream_taxonomy.md` (106-citation research report) + owner decision to split custody/measurement into its own Level 1 group and to leave the 2 unconfirmed Credit & Risk candidates out.

**Level 0:** Order to Cash (Value Driver: Operational Finance)

**Level 1 groups: 10 (was 9).** New group inserted: "Measure & Custody Transfer" — sits between Order & Fulfillment and Billing, mirroring the EPM blueprint's (`EPM-BA-O2C-DS-001`) separate "Measure/Title" chevron.

**Full Level 1 → Level 2 table (64 Level 2 processes total, was 46):**

| # | Level 1 group | Level 2 processes | Build treatment |
|---|---|---|---|
| 1 | Master Data Mgmt | Maintain Customer Master; Maintain Price & Discount Master; Maintain Product Master (extended: dye status, API gravity/density, UoM conversion group, RIN D-code eligibility); Maintain Excise & Environmental Credit Master (renamed from *Maintain Tax Master*); Maintain Workflows; Maintain Terminal & Location Master (incl. TCN) [NEW]; Maintain Exchange Partner Master [NEW]; Maintain Quantity Conversion/UoM Rules [NEW] | Build fully — native to ERPNext + trycompai/crm |
| 2 | Quote & Sale | Maintain Commercial Policies; Establish Commercial Terms & Contracts; Define Financing & Payment Methods; Issue Quotes & Renewals; Develop & Monitor Revenue Plan; Analyze Customer Profitability; Establish & Manage Exchange Agreements [NEW]; Negotiate Channel-Specific Agreements (DODO/CODO/Jobber) [NEW] | Build fully — native to ERPNext (Quotation, Sales Order) |
| 3 | Credit & Risk | Maintain Credit Policies; Establish Credit Limit & Risk Code; Monitor Credit Against Limit; Review Credit Limit and Risk Code; Analyze Portfolio Credit Risk; Perform Customer Closure and Reinstatement; Issue & Manage Letters of Credit [NEW] | Light custom Frappe/ERPNext workflow (not native) — see ADR-HL-014 |
| 4 | Order & Fulfillment | Capture & Validate Nomination (renamed from *Capture & Validate Order*); Allocate & Release Order (extended: Stock Projection Worksheet, Location Balancing, Three-Way Pegging); Track & Forecast Order (extended: Worklist, Berth Planning Board); Change/Cancel Order; Manage Terminal Lifting & Gate Operations (renamed from *Manage Fulfillment*); Manage Returns (deprioritized — retained for lubricants channel only, low relevance for bulk fuel); Execute Exchange Lifting (Borrow/Loan) [NEW]; Authorize & Fulfill Into-Plane/Bunker Delivery [NEW] | Build fully — native to ERPNext (Sales Order → Delivery Note) |
| 5 | **Measure & Custody Transfer** [NEW GROUP] | Perform Custody Transfer & Quantity/Quality Determination (GOV/GSV/NSV conversion via QCI, API MPMS 11.1/ASTM D1250); Issue Custody Transfer Documentation (Bill of Lading / Bunker Delivery Note) | Light custom Frappe/ERPNext workflow (not native) — see ADR-HL-014 (extend ADR to cover this group) |
| 6 | Billing | Create & Distribute Bill; Perform Accounting for Self-Billing; Determine Excise/Motor Fuel Tax Liability & Dye Status (renamed from *Determine Taxability & Record Tax Liabilities*); Create Exception Invoice; Generate & Report RIN Credits [NEW]; File Federal & State Motor Fuel Excise Tax Returns (Form 720/State Equivalents) [NEW]; Bill Exchange Partner Netting (LIA/Borrow-Loan) [NEW] | Build fully — native to ERPNext (Sales Invoice) |
| 7 | Receipt | Receive Payments; Receive Remittance Advice; Apply Receipts; Manage Unapplied Receipts; Perform Reconciliations & Settlements; Reconcile Fuel/Fleet Card Transactions [NEW]; Process LC Document Presentation & Bank Payment [NEW] | Build fully — native to ERPNext (Payment Entry) |
| 8 | Collection | Establish Collection Targets; Analyze AR Aging; Execute Collections; Negotiate Settlements; Initiate Legal Action | Light custom Frappe/ERPNext workflow (not native) — see ADR-HL-014 (unchanged — no O&G-specific evidence found) |
| 9 | Dispute | Validate Deductions; Receive & Validate Queries; Create Credit Memo/Charge Back; Perform Appeasements; Develop Root Cause Analysis & Action Plan; Manage Quantity/Quality Claims (Custody Disputes) [NEW] | Light custom Frappe/ERPNext workflow (not native) — see ADR-HL-014 |
| 10 | Close | Perform Revenue Accounting (extended: two-step plant-to-plant transfer P&L postings, exchange-agreement accounting); Process Bad Debt; Close AR Sub Ledger; Reconcile Excise, Environmental Credit & Indirect Tax (renamed from *Reconcile Indirect Tax*); Reconcile Tank/Silo Book Stock to Physical Inventory [NEW]; Close Exchange Balance/Netting Position [NEW] | Light custom Frappe/ERPNext workflow (not native) — see ADR-HL-014 |

**Counts:** 10 Level 1 groups (was 9) · 64 Level 2 processes (was 46) · 4 renames · 19 additions (net of the 2 unconfirmed candidates, which were explicitly NOT adopted) · 1 process deprioritized (Manage Returns, retained not removed) · 1 new Level 1 group (Measure & Custody Transfer).

**Explicitly NOT adopted (owner decision 2026-08-09):** "Link Commodity Hedge Position to Credit Exposure" and "Establish Prepayment/COD Requirements for Bulk Shipments" — both flagged as research candidates under Credit & Risk but not independently confirmed by primary sources. Left out of the taxonomy; may be revisited later with a targeted follow-up against ISDA/EEI/NAESB documentation or 10-K risk-factor disclosures.

**Build treatment note:** Group 5 (Measure & Custody Transfer) is a NEW non-native group requiring the same "light custom Frappe/ERPNext workflow" treatment as Credit & Risk, Collection, Dispute, and Close — extending the owner's 2026-08-09 scoping decision ("light custom workflow for ERPNext gap groups") to this newly identified 5th gap group for consistency. This adds a 5th custom Frappe DocType: **Custody Transfer Ticket** (alongside Credit Limit Review, Collection Case, Dispute Case, AR Sub-Ledger Close Task).

**Downstream O&G overlay (superseded language):** the taxonomy is no longer generic-with-an-overlay; O&G specifics are now directly embedded in the Level 1/Level 2 structure itself (Measure & Custody Transfer group, exchange agreements, excise/RIN processes, channel-specific fulfillment). Retire the old "overlay" framing.

**Full source list:** see `research_o2c_downstream_taxonomy.md` Section 8 (29 URLs) for complete citations — key ones: [SAP TSW](https://help.sap.com/docs/SAP_ERP/3f42f39c7e59483b9095d75f5145ec23/5065702566b761fde10000000a421bc1.html), [SAP HPM](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/0f4ab800d01c4366b0c9aaff06a64320/23c9cc5340487214e10000000a174cb4.html), [SAP QCI Integration](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/0f4ab800d01c4366b0c9aaff06a64320/40ea5e9072ae42119c3425a9f9294d5f.html), [SAP Exchange Agreement](https://help.sap.com/docs/SAP_ERP/205f2566b44c4ea3a0bc331615641e72/4581cf535b804808e10000000a174cb4.html?version=6.03.latest), [IRS Form 720](https://www.irs.gov/pub/irs-pdf/f720.pdf), [EPA RINs](https://www.epa.gov/renewable-fuel-standard/renewable-identification-numbers-rins-under-renewable-fuel-standard-program), [APQC Downstream Petroleum PCF](https://www.apqc.org/resource-library/resource-listing/apqc-process-classification-framework-pcf-downstream-petroleum), [ExxonMobil BDN](https://www.exxonmobil.com/en/marine/technicalresource/marine-resources/bunker-delivery-notes), [Financely Group — LCs in O&G](https://www.financely-group.com/how-are-letters-of-credit-used-to-enable-oil-gas-purchases), [UK Defence Club — Bunker Disputes](https://www.ukdefence.com/fileadmin/uploads/uk-defence/Photos/Publications/Soundings/2011/UKDC_BunkerDisputes_web.pdf).

## Additional tool decisions — added 2026-08-09

| Layer | Tool | License | Why (one line) |
|---|---|---|---|
| ERP / SAP-analog | ERPNext (Frappe framework) | GPL-3.0 | Native Quotation → Sales Order → Delivery Note → Sales Invoice → Payment Entry O2C flow; already proven in the owner's own `scada_harmonization` repo (PR #18); custom Frappe DocTypes added for Credit & Risk/Collection/Dispute/Close |
| CRM / Salesforce-analog | trycompai/crm | MIT | External source system for Account/Contact/party master data feeding Master Data Mgmt; self-hosts via `docker compose up` + Bun |
| Team-channel simulator | block/buzz | Apache-2.0 | Self-hosted Nostr-relay-based workspace; humans and agents are first-class channel members with own keys; `buzz-cli` is JSON-in/JSON-out and designed for LLM tool calls, letting the capstone agent generate or participate in realistic dispute/exception discussion threads; production self-host via Docker Compose (`deploy/compose/`: Postgres, Redis, MinIO) |
| Unstructured+structured fusion / KG ingestion | semantica-agi/semantica | MIT | Sits atop the already-chosen Fuseki+Neo4j stack; native ingestion connectors for files (PDF/DOCX/PPTX/HTML/TXT/CSV/JSON/XML/Excel), email (IMAP/POP3), message streams (Kafka/RabbitMQ/Kinesis/Pulsar), supports both Neo4j (LPG) and RDF stores via one API with SHACL/OWL governance and PROV-O provenance — the mechanism that fuses the unstructured corpus (SOPs, emails, invoices, Buzz messages) with the ERPNext/Postgres relational data into one graph |

**Open gap (not yet resolved):** no open-source analog has been identified yet for SAP MDG (staging/approval workflow) or Profisee (probabilistic matching/survivorship) referenced in the owner's Customer Data Dictionary Template. Candidate fallback: custom Python matching/survivorship logic plus a Neo4j/Fuseki-based governance record, but this is not yet an accepted decision — flagged in the Open Issues section of Document 00.

## Additional dataset decision — added 2026-08-09

| Dataset | Role | License/access |
|---|---|---|
| Olist Brazilian E-Commerce dataset | Realism-calibration reference only (NOT the primary schema) — ~100K real orders/customers/payments/deliveries/reviews, 2016-2018, used to sanity-check that synthetic O2C record volumes, cardinalities, and distributions look like real transactional data | Public, [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), CC BY-NC-SA 4.0 |

Confirmed finding (unchanged from prior research): no public entity-level (customer/order/invoice) Downstream O&G O2C dataset exists. Downstream O&G remains the domain scenario; synthetic data generation (relational + unstructured) remains the primary data strategy, with EIA/World Bank/Kaggle-Timac providing only aggregate reference series (rack prices, fuel prices) already cited in Document 04.

## Unstructured data generation strategy — added 2026-08-09

**Core design principle: entity-linking, not independent generation.** Every unstructured artifact must reference the same synthetic IDs (customer_id, order_id, invoice_id, dispute_id, collection_case_id) as the relational/ERPNext data. This is what lets semantica's entity extraction and conflict-detection fuse structured and unstructured facts about the same real-world entity into one graph, rather than producing two disconnected corpora.

**Scoping decision (confirmed with owner 2026-08-09): full taxonomy coverage.** Generate unstructured artifacts for all 64 Level 2 taxonomy boxes (across 10 Level 1 groups — updated 2026-08-09 per the downstream O&G taxonomy redline, was ~40 boxes / 9 groups), not only the boxes with the deepest transactional build — documents are cheap to generate and give the knowledge graph full process coverage even where a process group's transactional depth is lighter.

| Artifact type | Generation approach | Entity-link mechanism |
|---|---|---|
| SOPs (64, one per Level 2 box) | LLM-authored Markdown/PDF, grounded in the ontology's definition for that process | Tagged with `process_id` matching the Document 05 T-Box process node |
| Invoices / Receipts | Rendered as real PDFs (ReportLab or WeasyPrint) templated directly from ERPNext Sales Invoice / Payment Entry rows | Same invoice_id/payment_id as the ERPNext record; amounts must match exactly |
| Emails | LLM-generated threads (dispute escalation, credit-hold notice, collections follow-up, remittance advice) | References specific order_id/invoice_id/dispute_id/collection_case_id in subject or body |
| Team channel messages | block/buzz, seeded with scripted and/or agent-authored messages (via `buzz-cli`) | Messages reference the same IDs; Buzz's Nostr event log is exported as structured JSON for ingestion |
| SOP-to-KPI traceability | Each SOP's process_id links to the KPI candidates seeded from that Level 2 box (see O2C Process Taxonomy table above) | Shared process_id namespace across Document 05 ontology and Document 04 data generation scripts |

**Ingestion mechanism:** semantica-agi/semantica's native connectors (files, email IMAP/POP3, message streams) pull this unstructured corpus alongside the ERPNext/Postgres structured data into the same knowledge graph, with entity-aware chunking and PROV-O provenance recording which source (structured row vs. unstructured document) contributed which fact.

## AWS Context Ontology Accelerator-inspired additions — added 2026-08-10

AWS announced **Context Ontology Accelerator (COA)** as a GA open-source (Apache-2.0) accelerator on 2026-07-31: a Scan → Model → Serve pipeline that AI-drafts an OWL/RDF/SHACL ontology from structured+unstructured sources with human review, publishes it to a customer-owned knowledge graph (Amazon Neptune), and serves it to any agent via an MCP server, REST, or SPARQL endpoint, with a tiered governed-metric resolution model ([AWS announcement](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-context--ontology-accelarator-generally-available/); [COA docs](https://aws.github.io/context-ontology-accelerator/); [COA GitHub repo](https://github.com/aws/context-ontology-accelerator)). The homelab's architecture had already independently converged on several of the same patterns (Ontop as virtual RDF, Owlready2 for OWL). Three additional patterns are adopted below, evaluated and approved by the owner on 2026-08-09/10; the enterprise-RBAC/namespace-isolation and control-plane/data-layer split patterns from COA were explicitly evaluated and rejected as out of scope for a single-owner, single-host learning homelab.

| Pattern borrowed from COA | Homelab adoption | Rationale |
|---|---|---|
| Ontology Engine reasoning gate (HermiT/ELK) before publishing to the graph | New Dagster asset runs Owlready2's `sync_reasoner()` (HermiT) for consistency checking and automatic reclassification on the T-Box, gating the existing Morph-KGC materialization step (ADR-HL-002) | Catches ontology errors before they reach Git or Neo4j; low-cost since Owlready2 was already the chosen OWL-as-Python-objects library ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html)) |
| Serve stage's agent-agnostic MCP server, separate from the app's own agent | New MCP server component (official `modelcontextprotocol/python-sdk`) alongside FastAPI, exposing read-only KPI Store, Cypher, and SPARQL query tools to any MCP client, not only the homelab's LangGraph agent | On-theme for the owner's agentic-AI learning interest; demonstrates the "agent-agnostic serving" principle without adding enterprise complexity ([python-sdk](https://github.com/modelcontextprotocol/python-sdk)) |
| Tiered governed-metric resolution model with a visible resolution trace | Formalize the existing FastAPI/LangGraph answer path (already fact-table-first, then graph, then agent synthesis) into 3 explicitly named tiers — Tier 0 pre-computed KPI Store value (deterministic, 0 LLM calls), Tier 1 structured Cypher/SPARQL query, Tier 2 agentic fallback with synthesis — and return which tier answered each question, with source/run-id provenance | Makes the homelab's "accountable path" concept concrete and demonstrable; directly relevant to the enterprise EPM project's KPI Store governance/auditability goals |

**Explicitly rejected COA patterns (with reason):**
- **Namespace isolation + RBAC roles** (`owner`/`maintainer`/`data-steward`/`data-analyst`, `platform-admin`/`platform-viewer`) — contradicts the homelab's own stated "one owner, one host, no enterprise IAM" simplification principle (Document 01, Non-functional considerations). May be referenced as a curriculum discussion topic only, never implemented.
- **Control-plane/data-layer API split with Smithy-generated contracts** — real engineering overhead (Java/Gradle toolchain, generated OpenAPI/TypeScript clients) with no external API consumers to justify it in a personal learning homelab. Not adopted.
