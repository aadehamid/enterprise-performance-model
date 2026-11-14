# Shareable copy: Lagos Refining & Supply Company (LSC)

This zip is the Data Lineage Knowledge Graph project and its text2cypher portal with no real data and no keys. You generate a synthetic catalog for a fictional downstream oil and gas company, Lagos Refining & Supply Company (LSC), load it into Neo4j, and ask the portal lineage questions in plain English.

For a one-page walkthrough with copyable commands, open `docs/guide/setup-guide.html` in a browser.

LSC runs two refineries, marine, rack and crude terminals, and inland depots across Nigeria, plus trading desks in Rotterdam and Houston. Its business areas are refining and planning, supply and trading, pipelines and terminals, wholesale marketing, renewable fuels, and regulatory compliance (RINs and low-carbon fuel credits). Reports carry the names a downstream analyst expects, such as "3-2-1 Crack Spread Dashboard", "Terminal Throughput Dashboard", "RIN Obligation Tracker" and "Lifting vs Contract Entitlement".

The synthetic catalog is close to production scale: about 45,400 nodes and 77,900 relationships across 21 node labels and 40 relationship patterns. It includes 50 chat sessions with 200 messages and feedback. Every report consumes at least one Semantic view whose lineage reaches an Operational source table. Public products and data sources keep their names (RightAngle, SAP, Salesforce, IBM Maximo, AVEVA PI, Toptech TMS, LabWare LIMS, Aspen PIMS, Allegro, Platts, OPIS, Argus, DTN, Profisee, Alteryx, Power BI). Everything else is fictional.

## What is in the zip

| Path | What it is |
|---|---|
| `synthetic/lsc_data_model.json` | The graph data model, validated with the `mcp-neo4j-data-modeling` server |
| `synthetic/lsc_data_model.arrows.json` | The same model for [arrows.app](https://arrows.app) (File, Import, paste the JSON) |
| `synthetic/ingest.cypher` | Constraint and `UNWIND $rows` ingest queries, generated from the model by the MCP server |
| `synthetic/build_model_artifacts.py` | Rebuilds the two files above from the model |
| `synthetic/competency_questions.json` | The 15 questions below, each with a check query |
| `src/generate_shareable_catalog.py` | Writes the synthetic catalog (deterministic for a given seed) |
| `src/load_synthetic_catalog.py` | Runs `ingest.cypher` over the catalog and checks the counts |
| `src/verify_synthetic_catalog.py` | Checks scale, name leaks, database counts and the 15 answers |
| `src/load_*.py` | The real ingestion scripts, kept as examples for loading your own sources (Excel STTMs, CSV, Power BI, Purview) |
| `neo4j_text2cypher_fullstack/` | The portal: FastAPI backend and Vite React frontend |
| `.agents/skills/cypher-query-generator/` | The skill the backend puts in every Cypher-generation prompt, written for the LSC graph |
| `neo4j_instance_credentials.env.example` | Placeholder settings for Neo4j and every LLM provider |

## Prerequisites

- Neo4j 5.x or 2025.x. Neo4j Desktop or Enterprise can host a separate `lsc` database. Community and Aura have one database, `neo4j`; use that name wherever this guide says `lsc`. On Community and Aura the loader swaps `NODE KEY` constraints for `UNIQUE` ones.
- Aura: set `NEO4J_URL=neo4j+s://<id>.databases.neo4j.io` and the password from the credentials file Aura gave you. The catalog fits Aura Free's limits (200,000 nodes, 400,000 relationships) with room for your own questions.
- Python 3.12 and [uv](https://docs.astral.sh/uv/).
- Node.js 20 or later and pnpm (`npm install -g pnpm`).
- An API key for one LLM provider (see step 2).

## Steps

Run these from the unzipped folder in PowerShell. On macOS or Linux, use `.venv/bin/python` and forward slashes.

### 1. Install

```powershell
uv sync
cd neo4j_text2cypher_fullstack\frontend
pnpm install
cd ..\..
```

`uv sync` creates `.venv` with the loader, backend and test dependencies, including the Azure OpenAI, OpenAI, Anthropic and Vertex AI clients.

### 2. Add your keys

```powershell
Copy-Item neo4j_instance_credentials.env.example neo4j_instance_credentials.env
```

Edit `neo4j_instance_credentials.env`. Fill in the Neo4j block, then set `LLM_PROVIDER`, `LLM_MODEL` and that provider's key.

| `LLM_PROVIDER` | Settings | Notes |
|---|---|---|
| `openai` | `OPENAI_API_KEY` | Also any OpenAI-compatible service: uncomment `OPENAI_BASE_URL` (OpenRouter, Groq, Together, Mistral, DeepSeek, xAI, a local Ollama or LM Studio) |
| `azure` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_API_VERSION`, `AZURE_DEPLOYMENT_NAME` | |
| `anthropic` | `ANTHROPIC_API_KEY` | |
| `google` | `GOOGLE_PROJECT`, `GOOGLE_LOCATION` | Vertex AI. Run `gcloud auth application-default login` or set `GOOGLE_APPLICATION_CREDENTIALS` |

Never commit or zip this file. `.gitignore` already excludes it.

### 3. Create the database

In Neo4j Browser, connected to the `system` database:

```cypher
CREATE DATABASE lsc IF NOT EXISTS WAIT;
```

Skip this on Community or Aura Free and set `NEO4J_DATABASE=neo4j`.

### 4. Generate the synthetic catalog

```powershell
.venv\Scripts\python.exe src\generate_shareable_catalog.py
.venv\Scripts\python.exe src\verify_synthetic_catalog.py
```

The generator writes `synthetic_data/` (gitignored): `nodes/*.jsonl`, `labels/*.jsonl`, `rels/*.jsonl` and `manifest.json` with counts and the expected answers. The same seed always writes the same files. Chat timestamps are placed in the last 21 days, so generate shortly before you load. The portal archives messages older than 30 days.

The verify step must print `[ok] profile`, `[ok] leaks` and `[ok] report lineage`. The default seed (26) is the tested one. Another seed (`--seed N`) writes a different catalog that can drift outside the ±10% profile tolerance, and the expected answers below change with it.

It also writes `synthetic_data/source.duckdb`, a DuckDB copy of the Power BI export tables a real loader reads in step 6.

### 5. Load it into Neo4j

```powershell
.venv\Scripts\python.exe src\load_synthetic_catalog.py --database lsc
.venv\Scripts\python.exe src\verify_synthetic_catalog.py --database lsc
```

The load takes about two minutes and ends with `Database 'lsc' matches manifest: 45426 nodes, 77946 relationships`. It is idempotent, so a rerun gives the same counts. It refuses a database that holds other data. The verify step adds `[ok] database`, `[ok] competency`, which runs each question's check query, and `[ok] database report lineage`, which checks that every report reaches an Operational table through a Semantic view.

### 6. Run a real loader over the source database (optional)

Step 5 loads the catalog directly. This step shows the project's real ingestion path: `load_powerbi_lineage.py` reads the Power BI export tables from a SQL source and merges reports, datasets and `CONSUMES` edges into the graph, then prunes Power BI reports it did not see.

```powershell
.venv\Scripts\python.exe src\load_powerbi_lineage.py --database lsc --source duckdb:///synthetic_data/source.duckdb
.venv\Scripts\python.exe src\verify_synthetic_catalog.py --database lsc
```

The catalog already matches what the loader writes, so the counts do not change and every verify check still prints `[ok]`.

`--source` (or `SOURCE_DB_URL` in the env file) takes any SQLAlchemy URL. `db_connect/src/connect/query_database.py` runs the read queries for every loader, so you can copy the tables to another engine and point at it:

| Engine | URL | Driver | Tested |
|---|---|---|---|
| DuckDB | `duckdb:///synthetic_data/source.duckdb` | `duckdb-engine` (installed) | Yes |
| SQLite | `sqlite:///source.db` | built in | Yes |
| PostgreSQL | `postgresql+psycopg://postgres:<password>@localhost:5432/lsc_source` | `psycopg` (installed) | No |
| SQL Server Express or Developer | `mssql+pyodbc://localhost\SQLEXPRESS/lsc_source?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes` | `pyodbc` (installed) plus Microsoft ODBC Driver 18 | No |

The tables live in schema `sem_internal_x`. On SQLite, which has no schemas, attach the file under that name or drop the prefix from the loader's queries. For the older SQL Server helpers in `db_connect`, set `SQLSERVER_ODBC_DRIVER` if your ODBC driver is not version 17.

### 7. Start the portal

Terminal 1, the backend on port 8000:

```powershell
cd neo4j_text2cypher_fullstack\backend
..\..\.venv\Scripts\python.exe -m app.main
```

Terminal 2, the frontend on port 5173:

```powershell
cd neo4j_text2cypher_fullstack\frontend
pnpm dev
```

Open http://localhost:5173 and ask the questions below.

To run beside another copy of the portal, pick other ports. Set `PORT` for the backend and `VITE_BACKEND_URL` for the frontend, and add the frontend's origin to `ALLOWED_ORIGINS` if you changed that setting:

```powershell
$env:PORT = "8001"; ..\..\.venv\Scripts\python.exe -m app.main
$env:VITE_BACKEND_URL = "http://localhost:8001/ask"; pnpm dev --port 5174 --strictPort
```

### 8. Run the tests (optional)

```powershell
.venv\Scripts\python.exe -m pytest -q
cd neo4j_text2cypher_fullstack\backend; ..\..\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend; npx tsc --noEmit; pnpm test:e2e
```

The root suite's `EXPLAIN` gate plans every loader query against the database in your env file. The e2e suite needs the backend and frontend running, and it calls your LLM. `tests/competency.e2e.ts` asks every competency question in the chat window and checks the answer against `synthetic_data/manifest.json`. To run only it, or against other ports:

```powershell
$env:E2E_BASE_URL = "http://localhost:5174"; npx e2e run tests/competency.e2e.ts
```

LLM answers vary from run to run. A failure prints the page text the test saw. Ask the question again in the portal before you treat it as a bug.

## Competency questions

With the default seed, the portal should answer these as follows. `manifest.json` holds the same expectations for your run.

| # | Question | Expected answer |
|---|---|---|
| 1 | How many Gold tables are there? | 43 |
| 2 | Show the tables in the wholesale_core schema | 13 tables, including `Margin_Fact`, `Product_Dim`, `Price_Batch_Dim` |
| 3 | Trace wholesale_core.Margin_Fact back to its replica source | `replica_helios.Margin_Detail` (through `udm_core.Helios_Margin_Fact`) |
| 4 | Which source column is wholesale_core.Margin_Fact.Margin_Amount derived from? | `udm_core.Helios_Margin_Fact.Margin_Amount`, from `replica_helios.Margin_Detail.MRGN_AMT` |
| 5 | Which report consumes sem_wholesale.Margin_vw? | Rack Margin Dashboard, Customer Profitability Scorecard |
| 6 | Which master data domain is realized in wholesale_core.Product_Dim? | Product |
| 7 | Which legacy table refactors to wholesale_core.Product_Dim? | `dwh.LSC_Product_Master` |
| 8 | Which data product is realized by sem_wholesale.Margin_vw, and which capability domain owns that product? | Rack Margin Analytics, in Wholesale Marketing |
| 9 | Which pipeline reads the replica margin table and loads wholesale_core.Margin_Fact? | `PL_Wholesale_Margin` |
| 10 | hey | A greeting, with no Cypher run |
| 11 | Can you show the graph of all the data models that cover the Helios data system? | `Helios_Conceptual_Data_Model_v2`, `Helios_Logical_Data_Model_v3` |
| 12 | Can you show all the feedback in the database in a graph? | 30 rated messages (10 poor, 20 good) with their sessions |
| 13 | Show me poor feedbacks? | 10 messages rated poor |
| 14a | We plan to move the source of mdm_core.RightAngle_Transaction_Type_Dim from RightAngle to Profisee. Which BI reports use sem_masterdata.TransactionType_vw? | Trading Deal Activity, Transaction Type Reference |
| 14b | Is the Timestamp column of sem_masterdata.TransactionType_vw used in any report? | Yes, Trading Deal Activity |
| 15 | How is sem_wholesale.Price_Batch_Dim_vw loaded? Which table and pipeline feed it? | `wholesale_core.Price_Batch_Dim`, loaded by `PL_Wholesale_Price_Batch` |

Questions 12 and 13 count the generated chat history. Your own questions add sessions, and any you rate add to those counts.

Ad hoc questions work too, for example "Which tables in refining_core have no lineage?", "Who is the data analyst for Rack Margin Dashboard?" or "Which systems replicate into replica_rightangle?".

## MCP servers (optional)

The app does not need MCP. These servers help you explore the graph and change the model from Cursor or Claude Desktop. Add them to `~/.cursor/mcp.json` (or `claude_desktop_config.json`) and restart the client.

```json
{
  "mcpServers": {
    "mcp-neo4j-cypher": {
      "command": "uvx",
      "args": ["mcp-neo4j-cypher", "--transport", "stdio"],
      "env": {
        "NEO4J_URI": "neo4j://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "<your-neo4j-password>",
        "NEO4J_DATABASE": "lsc"
      }
    },
    "mcp-neo4j-data-modeling": {
      "command": "uvx",
      "args": ["mcp-neo4j-data-modeling", "--transport", "stdio"]
    }
  }
}
```

- `mcp-neo4j-cypher` reads the schema (`get_neo4j_schema`) and runs read queries (`read_neo4j_cypher`) against `lsc`.
- `mcp-neo4j-data-modeling` validates a model and generates ingest Cypher and Arrows JSON. Use it to change `synthetic/lsc_data_model.json`.

## Changing the model

1. Edit `synthetic/lsc_data_model.json`, or import `lsc_data_model.arrows.json` into arrows.app, edit it and convert back with the MCP server's `load_from_arrows_json`.
2. Rebuild the artifacts with the same library the MCP server runs:

   ```powershell
   uvx --from mcp-neo4j-data-modeling==0.8.2 python synthetic/build_model_artifacts.py
   ```

   The script patches four gaps in the generated Cypher: it binds `$rows` instead of `$records` to match `Neo4jLoader.write_batches`, it writes relationship properties onto the relationship instead of the end node, it wraps `DATETIME` properties in `datetime()`, and it matches `RoleAssignment` on its composite key.
3. Teach `src/generate_shareable_catalog.py` to write the new label or relationship, then rerun steps 4 and 5. `tests/test_synthetic_catalog.py` fails if the model has a pattern that `ingest.cypher` does not cover.
4. Update `.agents/skills/cypher-query-generator/references/graph_schema.md` and `llm_graph_cypher_query_generation_context.md` so the portal's prompts know about the change.

## Loading your own sources

`src/load_*.py` are the loaders the original project ran against Excel STTM workbooks, CSV exports, Power BI and Purview metadata. They keep their original source-specific names and paths. Copy one as a starting point. Each reads a file, cleans cells with `src/excel_cells.py`, assigns layers with `src/medallion.py`, and writes through `Neo4jLoader.write_batches` with idempotent `MERGE` queries. `README.md` describes each phase and the order they run in.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Refusing to load: database ... holds N nodes and no LSC catalog` | Point `--database` at an empty database |
| `Database does not match manifest` | A previous partial load or other data is present. Drop and recreate the database, then reload |
| The portal answers about the wrong database | Set `NEO4J_DATABASE` in `neo4j_instance_credentials.env` and restart the backend |
| `LLM_PROVIDER=... but ... is empty` | The key for the chosen provider is missing from the env file |
| OpenAI calls fail with a URL error | `OPENAI_BASE_URL` is set to an empty value. Comment the line out |
| Questions 12 and 13 show no feedback | The catalog was generated more than 30 days ago and the portal archived the messages. Regenerate and reload |
| e2e reports port 5173 already in use, or tests run against the wrong portal | Another portal holds the port. Stop it, or start the servers on other ports (step 7) and set `E2E_BASE_URL` |
| `pnpm install` fails on long paths (Windows) | `pnpm install --store-dir C:\pnpm-store` |
