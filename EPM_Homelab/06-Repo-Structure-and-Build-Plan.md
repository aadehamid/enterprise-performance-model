# Downstream O&G Knowledge Homelab — Repository Structure and Build Plan

**Title:** Downstream O&G Knowledge Homelab — Repository Structure and Build Plan  
**Purpose:** Provide a practical, reproducible implementation plan for the personal Downstream O&G Knowledge Homelab, from local prerequisites through the capstone vertical slice.  
**Status:** Draft (personal homelab, not an EPM governed artifact)  
**Owner:** Hamid Adesokan  
**Last updated:** 2026-08-10  

## Prerequisites

Complete this short local checklist before creating the repository:

- [ ] Docker and Docker Compose are installed and can run a basic container.
- [ ] Python 3.12+ and a virtual-environment tool are installed: `uv` or `venv`.
- [ ] Git is installed and configured with a name and email.
- [ ] Plan for at least 16 GB RAM. Ollama local model serving is the most memory-hungry component; begin with a smaller quantized model when RAM is constrained, then move toward the recommended Apache-2.0 models, such as Qwen3.6-27B or Mistral Small 3.2 24B, as hardware permits ([local-model comparison](https://runaihome.com/blog/llama-33-vs-qwen3-vs-mistral-local-ai-2026/)).
- [ ] Reserve a few GB for Docker images and persistent volumes, plus additional disk capacity as public extracts, generated O2C data, RDF exports, and Ollama models grow.

The baseline remains local-first and single-machine: PostgreSQL 18 for operational facts, DuckDB for in-process analytics, Apache Jena Fuseki for RDF/SPARQL, Neo4j Community Edition as the graph serving layer, and Dagster Core for Python-native asset orchestration ([PostgreSQL 18](https://www.postgresql.org/about/news/postgresql-18-released-3142/), [DuckDB](https://duckdb.org/), [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/), [Dagster](https://github.com/dagster-io/dagster)).

## Repository folder structure

Use one Git monorepo. Keep operational and analytical facts in their appropriate stores; treat ontology, mappings, graph-load artifacts, and validation rules as versioned source code.

```text
downstream-og-homelab/
├── docker-compose.yml                 # local services and persistent volumes
├── .env.example                       # safe variable names and defaults only
├── README.md                          # quick start, architecture picture, run commands
├── pyproject.toml                     # shared Python tooling and dependency groups
├── uv.lock                            # reproducible Python environment, if using uv
├── .gitignore                         # excludes .env, data outputs, model caches, local DB files
├── docs/                              # the 00–06 homelab document set
│   ├── 00-Homelab-Charter-and-Roadmap.md
│   └── ...
├── adr/                               # lightweight architecture decision records
├── ontology/
│   ├── tbox/                          # OWL/RDFS classes and properties in Turtle
│   ├── abox/                          # hand-authored or generated RDF instance exports
│   ├── shapes/                        # SHACL shape files
│   ├── glossary/                      # SKOS concept schemes and terms
│   ├── mappings/                      # R2RML/Ontop and Morph-KGC mapping files
│   ├── queries/                       # SPARQL competency-question examples
│   └── config/                        # Ontop connection and mapping configuration templates
├── data/
│   ├── raw/
│   │   └── eia/                       # immutable EIA API/download landing files
│   ├── synthetic/                     # generated O2C, ticket, and SCADA-style data
│   ├── seeds/                         # small reviewed reference/seed tables for SDV
│   ├── curated/                       # reproducible derived files, if retained locally
│   └── duckdb/                        # local DuckDB database files, normally ignored by Git
├── pipelines/                         # Dagster project
│   ├── definitions.py                 # asset, job, schedule, and resource registration
│   ├── assets/                        # ingestion, transformation, RDF, validation, graph assets
│   ├── resources/                     # Postgres, DuckDB, Fuseki, Neo4j, and OpenLineage resources
│   ├── jobs/                          # named materialization selections
│   └── tests/                         # Dagster asset and integration tests
├── generators/                        # Python generation scripts
│   ├── o2c/                           # Faker/Mimesis order, contract, BOL, and invoice generation
│   ├── scada/                         # TimeSynth-style historian/tag signals
│   ├── sdv/                           # SDV training, sampling, and quality checks
│   └── reference/                     # controlled product, terminal, and customer reference data
├── erpnext/                           # custom Frappe app and fixtures for light O2C workflows
│   ├── apps/                           # custom application source and ERPNext hooks
│   ├── doctypes/                       # Credit Limit Review, Collection Case, Dispute Case, AR Sub-Ledger Close Task, Custody Transfer Ticket
│   └── fixtures/                       # roles, workflows, states, and seed configuration
├── crm-integration/                    # trycompai/crm checkout/configuration and master-data harmonization
│   ├── harmonize_customer_master.py    # map CRM Account/Contact parties to ERPNext Customer records
│   └── tests/                          # matching, survivorship, and reconciliation tests
├── unstructured-data/                  # entity-linked artifacts generated from the same O2C identifiers
│   ├── sops/                           # one process SOP per Level 2 O2C taxonomy box
│   ├── invoices/                       # rendered invoice and receipt PDFs from ERPNext rows
│   ├── emails/                         # dispute, credit, collection, and remittance threads
│   └── team-channel/                   # exported Buzz Nostr events and seed-message definitions
├── semantica-ingestion/                # Semantica connector configuration and Dagster-facing scripts
│   ├── configs/                        # files, IMAP/POP3, and message-stream connector configuration
│   ├── scripts/                        # corpus registration, entity-linking, and provenance helpers
│   └── tests/                          # connector and graph-ingestion checks
├── warehouse/
│   ├── sql/                           # Postgres DDL, views, and KPI Store SQL
│   ├── duckdb/                        # DuckDB analytical queries and model builders
│   └── contracts/                     # data-product schemas and grain/quality notes
├── scripts/
│   ├── bootstrap/                     # initial schemas, extensions, and local setup helpers
│   ├── ontology/                      # Turtle load and pySHACL validation scripts
│   ├── graph/                         # n10s configuration/import and Cypher query scripts
│   └── smoke_tests/                   # end-to-end API, SPARQL, Cypher, and agent checks
├── backend/                           # FastAPI application
│   ├── app/                           # routes, KPI service, schemas, dependencies
│   ├── tests/
│   └── Dockerfile
├── agent/                             # LangGraph workflow, tools, prompts, evaluation cases
│   ├── graph.py
│   ├── tools/                         # FastAPI/KPI Store, Neo4j, and SPARQL tool adapters
│   ├── prompts/
│   └── tests/
├── mcp-server/                        # agent-agnostic MCP server (ADR-HL-018)
│   ├── server.py                      # official modelcontextprotocol/python-sdk server entrypoint
│   ├── tools/                         # get_kpi, run_cypher, run_sparql tool implementations
│   ├── tests/
│   └── Dockerfile
├── notebooks/                         # exploratory Jupyter or marimo notebooks
├── lineage/                           # OpenLineage event/configuration and Marquez notes
├── tests/                             # cross-component pytest and pySHACL CI checks
└── ci/                                # simple local or hosted CI check definitions
```

`ontology/tbox` is the semantic source of truth for terms and relationships; `ontology/abox` is a generated or curated view of instances. Ontop should expose PostgreSQL facts virtually where possible, while Morph-KGC should materialize only stable curated facts that must be loaded into Fuseki or Neo4j ([Ontop VKG guide](https://ontop-vkg.org/guide/), [Morph-KGC documentation](https://morph-kgc.readthedocs.io/)).

The `erpnext/`, `crm-integration/`, `unstructured-data/`, and `semantica-ingestion/` directories make the light O2C application workflows and their entity-linked corpus first-class, versioned build assets. ERPNext supplies the native O2C path plus the custom Frappe workflows; [trycompai/crm](https://github.com/trycompai/crm) remains the external Account/Contact source; [block/buzz](https://github.com/block/buzz) supplies the team-channel simulator; and [semantica-agi/semantica](https://github.com/semantica-agi/semantica) is invoked by the Dagster pipeline to fuse the corpus with relational facts.

The `mcp-server/` directory is a thin, agent-agnostic serving layer built on the official [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk); it exposes the same read-only KPI Store, Cypher, and SPARQL tools already implemented for the FastAPI/LangGraph agent under `agent/tools/`, so both surfaces share one tool implementation rather than diverging (ADR-HL-018). The Owlready2/HermiT reasoning-gate check (ADR-HL-019) lives as a Dagster asset under `pipelines/assets/`, adjacent to the existing pySHACL validation asset, and its inference output is written to a separate `ontology/abox/inferred/` export rather than merged into the hand-authored T-Box.

## Docker Compose skeleton

The following skeleton intentionally uses named volumes and one internal network. Neo4j Community is the graph serving/query layer, with its self-hosted n10s plugin enabled; Fuseki persists its TDB2 dataset; and Marquez has a small dedicated metadata database. The image tags should be pinned after the first verified local run rather than treated as a production deployment standard ([neosemantics](https://neo4j.com/labs/neosemantics/), [OpenLineage](https://github.com/OpenLineage/OpenLineage), [Marquez](https://github.com/MarquezProject/marquez)).

The O2C extension adds [ERPNext](https://github.com/frappe/erpnext), a Postgres-backed [trycompai/crm](https://github.com/trycompai/crm) instance, and the [block/buzz](https://github.com/block/buzz) production-bundle pattern: a relay with Postgres, Redis, and MinIO. Semantica is a Python-library dependency in the Dagster/ingestion image, not a separate service; its file, IMAP/POP3 email, and Buzz-event ingestion is configured under `semantica-ingestion/` ([semantica-agi/semantica](https://github.com/semantica-agi/semantica)).

```yaml
services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks: [homelab]

  erpnext:
    image: frappe/erpnext:latest
    env_file: .env
    environment:
      DB_HOST: postgres
      DB_PORT: "5432"
      DB_NAME: ${ERPNext_DB_NAME}
      DB_USER: ${ERPNext_DB_USER}
      DB_PASSWORD: ${ERPNext_DB_PASSWORD}
    ports:
      - "8080:8080"
    volumes:
      - ./erpnext:/workspace/erpnext
      - erpnext_sites:/home/frappe/frappe-bench/sites
    depends_on:
      - postgres
    networks: [homelab]

  crm_db:
    image: postgres:18
    environment:
      POSTGRES_USER: ${CRM_DB_USER}
      POSTGRES_PASSWORD: ${CRM_DB_PASSWORD}
      POSTGRES_DB: ${CRM_DB_NAME}
    volumes:
      - crm_db_data:/var/lib/postgresql/data
    networks: [homelab]

  trycompai-crm:
    build:
      context: ./crm-integration/trycompai-crm
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${CRM_DB_USER}:${CRM_DB_PASSWORD}@crm_db:5432/${CRM_DB_NAME}
    ports:
      - "3001:3000"
    depends_on:
      - crm_db
    networks: [homelab]

  buzz_db:
    image: postgres:18
    environment:
      POSTGRES_USER: ${BUZZ_DB_USER}
      POSTGRES_PASSWORD: ${BUZZ_DB_PASSWORD}
      POSTGRES_DB: ${BUZZ_DB_NAME}
    volumes:
      - buzz_db_data:/var/lib/postgresql/data
    networks: [homelab]

  buzz_redis:
    image: redis:7-alpine
    volumes:
      - buzz_redis_data:/data
    networks: [homelab]

  buzz_minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: ${BUZZ_MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${BUZZ_MINIO_ROOT_PASSWORD}
    command: server /data --console-address ":9001"
    volumes:
      - buzz_minio_data:/data
    ports:
      - "9001:9001"
    networks: [homelab]

  buzz:
    build:
      context: ./crm-integration/buzz
      dockerfile: deploy/compose/Dockerfile
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${BUZZ_DB_USER}:${BUZZ_DB_PASSWORD}@buzz_db:5432/${BUZZ_DB_NAME}
      REDIS_URL: redis://buzz_redis:6379/0
      S3_ENDPOINT: http://buzz_minio:9000
    depends_on:
      - buzz_db
      - buzz_redis
      - buzz_minio
    networks: [homelab]

  fuseki:
    image: stain/jena-fuseki:latest
    environment:
      ADMIN_PASSWORD: ${FUSEKI_ADMIN_PASSWORD}
      FUSEKI_DATASET_1: ${FUSEKI_DATASET_NAME}
    ports:
      - "3030:3030"
    volumes:
      - fuseki_data:/fuseki
    networks: [homelab]

  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: ${NEO4J_AUTH}
      NEO4J_PLUGINS: '["n10s"]'
      NEO4J_dbms_security_procedures_unrestricted: "n10s.*"
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks: [homelab]

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    networks: [homelab]

  dagster:
    build:
      context: ./pipelines
    env_file: .env
    command: ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
    ports:
      - "3000:3000"
    volumes:
      - ./pipelines:/app
      - ./data:/workspace/data
      - ./ontology:/workspace/ontology
    depends_on:
      - postgres
      - erpnext
      - trycompai-crm
      - buzz
      - fuseki
      - neo4j
      - marquez
    networks: [homelab]

  marquez_db:
    image: postgres:18
    environment:
      POSTGRES_USER: ${MARQUEZ_DB_USER}
      POSTGRES_PASSWORD: ${MARQUEZ_DB_PASSWORD}
      POSTGRES_DB: ${MARQUEZ_DB_NAME}
    volumes:
      - marquez_db_data:/var/lib/postgresql/data
    networks: [homelab]

  marquez:
    image: marquezproject/marquez:latest
    environment:
      MARQUEZ_DB_HOST: marquez_db
      MARQUEZ_DB_PORT: "5432"
      MARQUEZ_DB_USER: ${MARQUEZ_DB_USER}
      MARQUEZ_DB_PASSWORD: ${MARQUEZ_DB_PASSWORD}
      MARQUEZ_DB: ${MARQUEZ_DB_NAME}
    ports:
      - "5000:5000"
    depends_on:
      - marquez_db
    networks: [homelab]

  backend:
    build:
      context: ./backend
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./agent:/workspace/agent
      - ./ontology:/workspace/ontology:ro
    depends_on:
      - postgres
      - fuseki
      - neo4j
      - ollama
    networks: [homelab]

  mcp-server:
    build:
      context: ./mcp-server
    env_file: .env
    environment:
      MCP_SERVER_HOST: 127.0.0.1
      MCP_SERVER_PORT: ${MCP_SERVER_PORT}
    ports:
      - "127.0.0.1:8001:8001"
    volumes:
      - ./mcp-server:/app
      - ./ontology:/workspace/ontology:ro
    depends_on:
      - postgres
      - fuseki
      - neo4j
    networks: [homelab]

networks:
  homelab:
    name: downstream-og-homelab

volumes:
  postgres_data:
  erpnext_sites:
  crm_db_data:
  buzz_db_data:
  buzz_redis_data:
  buzz_minio_data:
  fuseki_data:
  neo4j_data:
  neo4j_logs:
  ollama_models:
  marquez_db_data:
```

## Environment variables

Commit `.env.example`, never `.env`. Replace all placeholder secrets locally.

```bash
# PostgreSQL operational/KPI Store database
POSTGRES_USER=homelab
POSTGRES_PASSWORD=change-me
POSTGRES_DB=downstream_og
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# ERPNext and custom Frappe O2C workflows
ERPNext_DB_NAME=erpnext
ERPNext_DB_USER=erpnext
ERPNext_DB_PASSWORD=change-me

# trycompai/crm and customer-master harmonization
CRM_DB_USER=crm
CRM_DB_PASSWORD=change-me
CRM_DB_NAME=crm

# Buzz relay production-bundle dependencies
BUZZ_DB_USER=buzz
BUZZ_DB_PASSWORD=change-me
BUZZ_DB_NAME=buzz
BUZZ_MINIO_ROOT_USER=buzz-minio
BUZZ_MINIO_ROOT_PASSWORD=change-me

# Apache Jena Fuseki
FUSEKI_DATASET_NAME=downstream
FUSEKI_ADMIN_PASSWORD=change-me
FUSEKI_BASE_URL=http://fuseki:3030

# Neo4j Community + n10s
NEO4J_AUTH=neo4j/change-me
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me

# Ollama and the capstone agent
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen3.6:27b

# FastAPI and lineage
BACKEND_PORT=8000
MARQUEZ_URL=http://marquez:5000
MARQUEZ_DB_USER=marquez
MARQUEZ_DB_PASSWORD=change-me
MARQUEZ_DB_NAME=marquez

# MCP server (ADR-HL-018), bound to loopback only
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8001

# Public-data ingestion
EIA_API_KEY=replace-with-your-eia-api-key
```

## Bootstrap sequence

1. Create and clone the repository, then enter it:
   ```bash
   git clone <your-repository-url> downstream-og-homelab
   cd downstream-og-homelab
   ```
2. Create the local configuration and Python environment:
   ```bash
   cp .env.example .env
   uv venv && source .venv/bin/activate
   uv sync
   ```
3. Start the stateful foundation services and the O2C application dependencies:
   ```bash
   docker compose up -d postgres erpnext crm_db trycompai-crm buzz_db buzz_redis buzz_minio buzz neo4j fuseki ollama
   ```
4. Pull the selected local model. The default is the fully open Qwen3.6-27B; substitute the documented Mistral Small 3.2 24B only if that is the chosen local model ([local-model comparison](https://runaihome.com/blog/llama-33-vs-qwen3-vs-mistral-local-ai-2026/)):
   ```bash
   docker compose exec ollama ollama pull qwen3.6:27b
   ```
5. Confirm the service endpoints: PostgreSQL on `5432`, Fuseki on `http://localhost:3030`, Neo4j Browser on `http://localhost:7474`, and Ollama on `http://localhost:11434`.
6. Run the Dagster ingestion asset selection. It should fetch EIA inputs, land immutable raw files in `data/raw/eia/`, generate synthetic O2C/custody data, and load reviewed relational tables into PostgreSQL and analytical outputs into DuckDB. The EIA API returns JSON and requires a registered API key; Dagster’s asset model is the organizing unit for this sequence ([EIA Open Data API](https://www.eia.gov/opendata/), [Dagster](https://github.com/dagster-io/dagster)).
   ```bash
   docker compose exec dagster dagster asset materialize -m definitions \
     -s eia_spot_prices,normalized_spot_prices,synthetic_o2c,weekly_gasoline_netback_cpg
   ```
7. Run the ontology loader, which parses Turtle with RDFLib, validates the intended A-Box with pySHACL, and pushes the approved graph to the Fuseki dataset:
   ```bash
   python scripts/ontology/load_fuseki.py
   ```
8. Run the n10s import script. It configures the Neo4j RDF mapping convention, imports the curated RDF export, and executes a small verification Cypher query. n10s is for self-hosted Neo4j, not Aura ([neosemantics](https://neo4j.com/labs/neosemantics/)).
   ```bash
   python scripts/graph/import_n10s.py
   ```
9. Start the application and observability surfaces, including the MCP server bound to loopback only:
   ```bash
   docker compose up -d backend mcp-server dagster marquez
   ```
10. Run the smoke test query, which must return the latest weekly Gasoline Netback / Refining Margin CPG KPI, its principal drivers, the underlying SPARQL or Cypher evidence path, and the resolution tier (ADR-HL-020) that answered it:
   ```bash
   python scripts/smoke_tests/agent_netback.py
   ```
11. Run the same smoke-test prompts against the MCP server on `127.0.0.1:8001` and confirm its `get_kpi`/`run_cypher`/`run_sparql` tools return evidence equivalent to the FastAPI response (ADR-HL-018).
12. Materialize the unstructured-corpus ingestion assets after the ERPNext transactions, generated documents, emails, and Buzz event export exist. The Semantica library runs inside the Dagster ingestion environment and sends governed, provenance-bearing graph facts into the existing Ontop/Morph-KGC/Fuseki/Neo4j path ([semantica-agi/semantica](https://github.com/semantica-agi/semantica)).

## Phased build backlog

### Phase 0 — Environment and repository setup

- [ ] Create the monorepo, `.gitignore`, `.env.example`, Python `pyproject.toml`, and a concise `README.md`.
- [ ] Add the Compose skeleton and verify persistent PostgreSQL, Fuseki, Neo4j, Ollama, Dagster, Marquez, FastAPI, and MCP server containers start independently, with the MCP server bound to `127.0.0.1:8001` (ADR-HL-018).
- [ ] Add the ERPNext, trycompai/crm, and Buzz Compose services/dependencies; add Semantica to the Dagster Python dependency group rather than creating a standalone Semantica container.
- [ ] Create Postgres schemas for `raw`, `core`, `kpi_store`, and `audit`; add a DuckDB connection convention.
- [ ] Add a minimal Dagster project with `definitions.py`, one test asset, and `dagster dev` instructions.
- [ ] Add pytest, RDFLib, pySHACL, DuckDB, PostgreSQL, Neo4j, FastAPI, LangGraph, and OpenLineage dependencies to the Python environment.
- [ ] Create an ADR template recording decision, context, alternatives, and consequences.

**Phase is done when:**

- The repository clones cleanly, `.env` is local-only, and `docker compose up -d` brings up the base stack.
- A developer can connect to PostgreSQL, Fuseki, Neo4j, and Ollama through the documented local ports.
- A basic Dagster asset and pytest test run successfully.

### Phase 1 — Data foundation

- [ ] Write Dagster asset `eia_spot_prices` that calls the EIA Open Data API and lands raw JSON in `data/raw/eia/`.
- [ ] Write a normalization asset that produces a dated EIA spot-price table with product, market, unit, source URL, and load timestamp.
- [ ] Define PostgreSQL tables for terminal, product, customer, contract, custody ticket/BOL, order, invoice, and invoice line.
- [ ] Build Faker/Mimesis generators for plausible terminals, products, customers, contracts, orders, BOLs, and invoices.
- [ ] Use SDV only where an existing seed table warrants a learned synthetic sample; record input and output provenance.
- [ ] Generate TimeSynth-style tag series only for the small SCADA/historian learning scenario, not as a substitute for custody facts.
- [ ] Create a data dictionary stating grain, keys, units, quality rules, and whether each dataset is public or synthetic.

**Phase is done when:**

- Re-running the asset selection refreshes raw EIA inputs and deterministically loads a usable small O2C/custody dataset.
- Tables have declared keys, units, dates, and source/provenance fields.
- A DuckDB query can join prices to the synthetic commercial context without copying source-of-truth assumptions into the graph.

### Phase 1A — O2C applications, customer-master harmonization, and unstructured corpus

- [ ] Configure [ERPNext](https://github.com/frappe/erpnext) for the native Quotation → Sales Order → Delivery Note → Sales Invoice → Payment Entry path and install the versioned custom Frappe app.
- [ ] Implement the five light custom Frappe DocTypes with real minimal state transitions and approvals: `Credit Limit Review` (Credit & Risk), `Collection Case` (Collection), `Dispute Case` (Dispute), `AR Sub-Ledger Close Task` (Close), and `Custody Transfer Ticket` (Measure & Custody Transfer).
- [ ] Set up the Postgres-backed [trycompai/crm](https://github.com/trycompai/crm) service as the external Account/Contact source, then build and test the customer-master harmonization step into ERPNext Customer records.
- [ ] Configure [block/buzz](https://github.com/block/buzz) from its `deploy/compose/` production bundle and seed entity-linked team-channel messages for disputes, credit holds, collections, remittance, and exceptions; export its Nostr event log as structured JSON.
- [ ] Generate entity-linked `unstructured-data/` artifacts for the full Level 2 O2C taxonomy: SOPs, ERPNext-derived invoice/receipt PDFs, email threads, and Buzz messages. Every artifact must retain the relevant `customer_id`, `order_id`, `invoice_id`, `dispute_id`, or `collection_case_id`.
- [ ] Add [semantica-agi/semantica](https://github.com/semantica-agi/semantica) connector configurations and Dagster assets for files, email via IMAP/POP3, and the Buzz exported event log as a message stream.
- [ ] Wire the Semantica outputs, entity links, and PROV-O provenance into the established Ontop/Morph-KGC/Fuseki/Neo4j pipeline without creating a graph-side transactional source of truth.

**Phase is done when:**

- ERPNext contains a believable, linked O2C flow and each of the five custom workflows can reach a completed state through its documented approval/state transition.
- CRM Account/Contact records reconcile to the intended ERPNext Customer master records, with unmatched or ambiguous cases visible to the harmonization tests.
- The seeded corpus is linked to the same synthetic identifiers as ERPNext/Postgres, and Semantica ingestion makes its file, email, and Buzz-derived facts queryable with source provenance.

### Phase 2 — Domain modeling and ontology

- [ ] Draft the pilot competency questions, including “What is our netback this week and why?”
- [ ] Create T-Box classes for KPI, Measure, Product, Terminal, CustodyTicket, Contract, Invoice, DataProduct, and LineageActivity.
- [ ] Define key object and data properties, URI conventions, labels, units, time grain, and controlled values.
- [ ] Create a SKOS concept scheme for downstream commercial, custody-transfer, and KPI terms.
- [ ] Add PROV-O-aligned entities and activities for EIA ingestion, synthetic generation, KPI calculation, and graph load.
- [ ] Create SHACL shapes for required custody ticket, KPI definition, KPI result, and lineage fields.
- [ ] Build RDFLib/Owlready2 tests and a pySHACL report with at least one deliberate failure fixture.
- [ ] Add a Dagster asset that runs Owlready2's `sync_reasoner()` (HermiT) against the T-Box before Morph-KGC materialization, writes inferred output to `ontology/abox/inferred/`, and blocks the downstream materialization asset on a reported inconsistency (ADR-HL-019).

**Phase is done when:**

- Turtle parses, SHACL validation passes for the approved example data, and a broken fixture fails predictably.
- Protégé Desktop can open the T-Box and a reader can answer each competency question from a SPARQL example or modeled path.
- The HermiT reasoning-gate asset passes on the approved T-Box and reliably fails on a deliberately introduced inconsistency, and Morph-KGC materialization does not run when the gate fails.

### Phase 3 — KPI Store and semantic/query layer

- [ ] Write the documented Gasoline Netback / Refining Margin CPG KPI definition: objective, formula, unit, grain, dimensions, drivers, thresholds, and refresh logic.
- [ ] Create `kpi_store.kpi_definition`, `kpi_store.kpi_result`, and calculation-audit tables in PostgreSQL.
- [ ] Implement Dagster asset `weekly_gasoline_netback_cpg` using normalized EIA price inputs and defined synthetic commercial adjustments.
- [ ] Create DuckDB analytical queries for driver decomposition and weekly comparison.
- [ ] Write R2RML/Ontop mappings for selected relational facts, KPI definitions, and KPI results.
- [ ] Add SPARQL examples that answer KPI definition, current value, source, and driver questions through the virtual RDF surface.
- [ ] Materialize only the stable RDF subset required for Fuseki using Morph-KGC.

**Phase is done when:**

- The weekly KPI can be recalculated repeatably, persisted, and reconciled to a documented SQL/DuckDB query.
- A SPARQL query exposes the intended relational facts virtually through Ontop, and a separate curated RDF export loads into Fuseki.

### Phase 4 — Neo4j serving graph

- [ ] Document the RDF-to-LPG mapping choices, including URI handling, labels, relationship types, and multi-valued predicates.
- [ ] Configure n10s once through a repeatable script and assert its procedures are available.
- [ ] Build a Morph-KGC export restricted to curated terms, KPI definitions/results, and stable business relationships.
- [ ] Write the n10s import script with idempotent cleanup or a named graph-load version convention.
- [ ] Add Cypher queries for KPI-to-measure, KPI-to-data-product, ticket-to-invoice, and lineage paths.
- [ ] Compare a selected SPARQL result to its intended Cypher result and record any semantic-mapping limitation.

**Phase is done when:**

- A clean Neo4j volume can be repopulated from versioned RDF artifacts with one documented command.
- Cypher returns the required capstone evidence path without Neo4j becoming an independent source of truth.

### Phase 5 — AI agent, FastAPI, and MCP server capstone

- [ ] Implement FastAPI endpoints for current KPI value, KPI definition, KPI drivers, SPARQL evidence, and Cypher evidence.
- [ ] Create LangGraph state, routing, tool contracts, and prompts for a controlled KPI question-answering flow.
- [ ] Implement tools for the KPI Store, Neo4j, and Fuseki; restrict each tool to read-only parameterized queries.
- [ ] Connect the agent to Ollama using `OLLAMA_MODEL` and log selected tool calls.
- [ ] Use neo4j-graphrag-python and/or LlamaIndex Property Graph Index only as the KG-grounded retrieval layer required by the agent design.
- [ ] Formalize the tiered resolution model (ADR-HL-020): Tier 0 governed KPI Store lookup, Tier 1 structured Cypher/SPARQL query, Tier 2 agentic LangGraph/Ollama fallback; every answer must report which tier resolved it plus a resolution trace (tier, source query, Dagster run id).
- [ ] Build the `mcp-server/` service with the official `modelcontextprotocol/python-sdk`, exposing `get_kpi`, `run_cypher`, and `run_sparql` tools that call the same underlying implementations as `agent/tools/`; bind it to `127.0.0.1:8001` only (ADR-HL-018).
- [ ] Add positive, ambiguous, and unsupported-question test cases with expected evidence behavior, run against both `POST /netback/explain` and the MCP server.

**Phase is done when:**

- `What is our netback this week and why?` returns a bounded answer with KPI value, unit, period, drivers, evidence references, and the resolution tier that answered it.
- The agent does not invent a KPI result when tools return no evidence.
- The MCP server returns an equivalent, tier-labeled answer to the same three acceptance prompts as the FastAPI endpoint.

### Phase 6 — Governance polish, lineage, and walkthrough

- [ ] Emit OpenLineage events from the documented pipeline boundary and verify their visibility in Marquez.
- [ ] Document data-product owners, source/provenance, refresh expectations, and quality checks for every capstone asset.
- [ ] Add pySHACL validation and pytest to a pre-commit hook or simple CI script.
- [ ] Add a clean-machine bootstrap runbook and screenshots or short walkthrough notes for each UI.
- [ ] Review all ADRs, licenses, and “not core dependency” exclusions against the stack decisions.
- [ ] Record limitations: public/synthetic data, single-machine capacity, model variability, and non-production controls.

**Phase is done when:**

- A new reader can reproduce the vertical slice, inspect its lineage, rerun SHACL checks, and follow the evidence from objective to API response.
- The repository clearly distinguishes personal educational artifacts from the enterprise EPM program.

## Local development tips

- Use `dagster dev` for rapid asset iteration before containerizing a change. Dagster Core is designed around Python-defined assets, which fits the raw-to-RDF-to-graph flow ([Dagster](https://github.com/dagster-io/dagster)).
- Diagnose services with `docker compose logs -f <service>` and check readiness before treating an import failure as a data problem.
- Keep Turtle, SHACL, SKOS, R2RML/Ontop, Morph-KGC, Cypher, and SPARQL files under Git version control. Treat them as source code, not editable runtime configuration.
- Run pySHACL as a pre-commit hook or simple CI script; it is Python-native and integrates with RDFLib validation flows ([pySHACL](https://github.com/rdflib/pyshacl)).
- Begin with a smaller quantized Ollama model to preserve RAM. Only move to the recommended Qwen3.6 or Mistral Small model after the data, semantic, and evidence paths already work.

## Troubleshooting notes

| Symptom | Likely cause | Practical fix |
|---|---|---|
| n10s procedures are missing | Plugin was not installed, Neo4j did not restart, or procedure restrictions block it. | Confirm `NEO4J_PLUGINS` is valid JSON, restart Neo4j, inspect logs, and run the documented `CALL n10s...` availability check. |
| Fuseki loses data after a restart | The TDB2 path is not mounted to the named `fuseki_data` volume, or a different dataset name is being queried. | Keep `/fuseki` mounted, use one `FUSEKI_DATASET_NAME`, and verify the dataset URL before loading. |
| Ollama fails, swaps heavily, or returns slowly | The model quantization or context setting exceeds available RAM. | Stop unused containers, select a smaller quantized model, and defer the larger Qwen3.6/Mistral Small model until hardware allows it. |
| A host port is already in use | Another local database, Neo4j, API, or development tool uses 5432, 7474, 7687, 8000, 8001, or 11434. | Identify the local process or change only the host-side port mapping in Compose, then update the matching local URL. |
| MCP server tools return stale or diverging evidence versus FastAPI | The two surfaces drifted onto separate tool implementations instead of sharing `agent/tools/`. | Confirm `mcp-server/tools/` imports the same read-only query functions as `agent/tools/` rather than duplicating query logic (ADR-HL-018). |
| Fuseki and Neo4j disagree on a relationship | The RDF-to-LPG mapping flattened a predicate or used a different URI/label convention. | Compare the Turtle triple, n10s configuration, imported node/relationship shape, and SPARQL/Cypher verification queries before changing source semantics. |
| Graph import duplicates nodes | The script is not idempotent or stable URIs are absent. | Use stable entity URIs, a versioned load convention, and explicit cleanup/merge behavior in the n10s import workflow. |

## Related homelab documents

- `00-Homelab-Charter-and-Roadmap.md`
- `01-Reference-Architecture.md`
- `02-Tool-Selection-and-ADRs.md`
- `03-Curriculum-and-Learning-Modules.md`
- `04-Data-Strategy-and-Datasets.md`
- `05-Domain-Model-and-Ontology-Pilot.md`

## See also (enterprise EPM parallel)

For learning-transfer context only, this practical build plan loosely parallels the enterprise EPM **Delivery Backlog and Roadmap** artifact. It is not a governed EPM artifact and makes no claim of formal linkage or approval.
