# Data Lineage Knowledge Graph

A Neo4j-based knowledge graph that models the **medallion architecture data lineage** for the Lagos Refining & Supply Company (LSC) data platform. It traces data flow from operational source systems through Replica, Silver, Gold, and Semantic layers — at both the table level and the column level — connecting tables to the Power BI reports that consume them and mapping master data domains to their physical realizations.

## Graph Schema

```
Server -[:HOSTS]-> DataSystem -[:CONTAINS]-> Schema -[:CONTAINS]-> Table
Server -[:HOSTS]-> FlatFile   -[:CONTAINS]-> Table   (flat-file source -> operational table)
Table  -[:HAS_COLUMN]-> Column                (table contains column)
Table  -[:DERIVED_FROM]-> Table               (table-level lineage between layers)
Column -[:DERIVED_FROM]-> Column              (column-level lineage)
Table  -[:REPLICATED_TO]-> Table              (operational -> replica)
Table  -[:MIGRATED_TO]-> DataSystem           (gold -> Alteryx sandbox)
Report -[:CONSUMES]-> Table                   (report -> semantic view)
Report -[:BELONGS_TO]-> CapabilityDataDomain  (report ownership)
DataProduct -[:BELONGS_TO]-> CapabilityDataDomain (product -> domain ownership)
DataProduct -[:REALIZED_BY]-> Table           (product -> semantic view)
MasterDataDomain -[:REALIZED_IN]-> Table      (business concept -> physical table)
Table  -[:REFACTORED_TO]-> Table              (legacy persistence -> IDP equivalent)
```

### Node Labels

| Label | Key Property | Description |
|-------|-------------|-------------|
| Server | serverName | Physical database server (e.g., `HELIOS.prod.db.lsc.internal`) |
| DataSystem | name | Logical database (e.g., `Helios`, `Atlas`, `RightAngle`) |
| Schema | qualifiedName | Schema within a DataSystem (e.g., `wholesale_core`, `replica_helios`) |
| Table | qualifiedName | `schema.TableName` (e.g., `wholesale_core.Margin_Fact`) |
| Column | qualifiedName | `schema.TableName.ColumnName` (e.g., `udm_core.Helios_Margin_Fact.Margin_Amount`) |
| Report | name | Power BI report name |
| MasterDataDomain | name | Abstract business entity (e.g., `Location`, `Product`, `Business Associate`) |
| BusinessArea | name | Organizational area (e.g., `Wholesale Marketing`, `Refining & Planning`) |
| CapabilityDataDomain | name | Report ownership domain |
| DataProduct | name | Logical grouping of semantic views within a domain |
| DataModel | name | Data model artifact name (e.g., `Helios_Conceptual_Data_Model_v2`) |
| FlatFile | name | Flat-file data source (e.g., Excel/CSV commercial files) |

### Table Properties

- **qualifiedName** -- `schema.TableName` (unique constraint)
- **name** -- table name without schema prefix
- **layer** -- `Operational`, `Replica`, `Silver`, `Gold`, `Semantic`
- **objectType** -- `Fact`, `Dim`, `View`, `Table`
- **sourceFile** -- STTM file that defined this table

### Column Properties

- **qualifiedName** -- `schema.TableName.ColumnName` (unique constraint)
- **name** -- column name
- **dataType** -- SQL data type
- **keyType** -- `PK`, `FK`, `BK`, or blank
- **definition** -- business definition from STTM
- **transformation** -- transformation logic from STTM

## Loading Phases

Run scripts in order. Each phase is idempotent (safe to re-run). These loaders read the original project's source workbooks, which do not ship. The shareable copy loads the synthetic catalog instead (see [Shareable copy](#shareable-copy-synthetic-lsc-catalog)).

| Phase | Script | What It Creates |
|-------|--------|----------------|
| 1 | `src/load_schemas.py` | Schemas, replica links, DataSystem nodes |
| 2 | `src/load_tables.py` | Core Table nodes under their Schemas |
| 3 | `src/load_lineage.py` | Table-level DERIVED_FROM edges, Alteryx provenance graph |
| 4 | `src/load_reports.py` | Reports, CONSUMES and BELONGS_TO edges |
| 4.1 | `src/load_phase4_metadata.py` | Master metadata mapping: conformed Tables and Columns |
| 5 | `src/load_sttm.py --all` | Column nodes, column DERIVED_FROM and HAS_COLUMN edges |
| 6 | `src/load_master_data.py` | MasterDataDomain nodes, REALIZED_IN and REFACTORED_TO edges |
| 7 | `src/load_semantic_views.py` | Semantic View Table nodes + DERIVED_FROM edges to Silver/Gold |
| 7a | `src/load_retail_payments_views.py` | One-off semantic views with SQL-parsed lineage |
| 8 | `src/load_data_products.py` | DataProduct nodes, BELONGS_TO + REALIZED_BY edges |
| 9 | `src/backfill_replicated_to.py --load` | Operational Table nodes + REPLICATED_TO edges, missing DataSystems and FlatFiles, duplicate DataSystem merges |
| 10 | `src/load_legacy_tables.py --load` | Legacy Table and Schema nodes, REFACTORED_TO edges, layer fixes, missing legacy views + DERIVED_FROM |
| 11 | `src/load_report_to_view.py --load` | Report nodes and CONSUMES edges (Report → Semantic View) from the legacy decommissioning mapping |
| 12 | `src/load_data_models.py` | DataModel nodes, MODELS edges (DataModel → CDD), BELONGS_TO edges (DataModel → DataSystem), new CDDs and DataSystems |

### Phase 3 Details (load_lineage.py)

This is the most complex phase. It processes two data sources:

1. **Master mapping Excel** (`Data/Phase 3 Reports Full Data Mapping.xlsx`) -- initial cross-product lineage pairs
2. **STTM files** (`Data/sttms/`) -- ground-truth overrides from two formats:
   - **Standard DD & STTM** sheets (most files)
   - **Alteryx Table Mapping** sheets

#### Alteryx Provenance Model

For Alteryx-originated STTMs, the script creates a full provenance graph:

- **Server nodes** mapped to DataSystems via `ALTERYX_DS_NAME_MAP`
- **Operational source Tables** (normalized -- raw DB names like `Helios-Prod(Helios-Reporting-Proxy)` mapped to `Helios`)
- **REPLICATED_TO edges** (operational -> replica)
- **Sandbox DataSystems** (platform=Alteryx Sandbox, status=sunsetting)
- **MIGRATED_TO edges** (gold table -> sandbox)
- **Report CONSUMES edges** from Alteryx STTMs

#### Key Configuration Maps

- **ALTERYX_DS_NAME_MAP** -- maps raw Database column values to canonical DataSystem names
- **ALTERYX_SANDBOX_NAME_MAP** -- normalizes sandbox names (e.g., `BusinessOperations` -> `Business_Operations`)
- **STTM_NAME_CORRECTIONS** -- fixes known QN mismatches across STTMs
- **STTM_COLUMN_ALIASES** -- handles variant column headers (Gold Layer, newline-separated names)

### Phase 4.1 Details (load_phase4_metadata.py)

This script processes the master metadata mapping workbook (`Data/Phase4_Entities_with_UDM_Naming_Convention.xlsx`, sheet `"Entities with UDM column names"`) using conformed openpyxl logic:

- **Strike-through Font Skipping**: Skips cells with Excel strike-through formatting (`cell.font.strike`) and empty physical table rows.
- **`dbo` Schema Exclusion**: Safely skips generating `Replica` layer schema elements for rows where `"Source" = "dbo"`.
- **Data Portfolio Cleanups**:
  - Splits multi-line portfolio fields by newline (`\n`) to assign conformed tables to multiple `CapabilityDataDomain` nodes dynamically.
  - Bypasses CapabilityDataDomain links for a configured list of non-domain portfolios while preserving their structural columns and lineages.
  - Strips organization prefixes from portfolio names and ignores non-portfolio categories (migration projects, `"nan"` placeholders).
  - Conforms spelling variants of one portfolio (e.g., `"Terminals Ops"`, `"Terminal Operations"`) to a single base domain.

### Phase 5 Details (load_sttm.py)

Processes every STTM Excel file to extract column-level lineage:

- Parses `DD & STTM` sheets (supports variant names like `DD & STTM - <suffix>`)
- Creates Column nodes for both target (Silver/Gold) and source (Replica) fields
- Wires `(Table)-[:HAS_COLUMN]->(Column)` and `(Column)-[:DERIVED_FROM]->(Column)`
- Post-processing: links orphan Tables to their parent Schema, creates Operational source Tables with table-level REPLICATED_TO
- Skips non-table sources: `ETL Generated`, `NA`, `config`, blank

### Phase 6 Details (load_master_data.py)

Loads master data domain mappings from the master data workbook (`Data/new data system files to process/`, path in the script):

- Creates MasterDataDomain nodes (Location, Product, Business Associate, etc.)
- Wires `(MasterDataDomain)-[:REALIZED_IN]->(Table)` for both IDP and operational tables
- Wires `(Table)-[:REFACTORED_TO]->(Table)` for legacy persistence-to-IDP migrations
- Creates operational Table nodes and Server->DataSystem->Table wiring for non-IDP tables
- Applies server name canonicalization and QA-to-PROD server mapping

## Current Graph Counts

*Synthetic LSC catalog, seed 26, from `synthetic_data/manifest.json`. `src/load_synthetic_catalog.py` asserts these after a load.*

| Metric | Count |
|--------|------:|
| Column nodes | 31,417 |
| Table nodes | 7,405 |
| Report nodes | 2,628 |
| RoleAssignment nodes | 2,314 |
| View nodes | 2,300 |
| DataSystem nodes | 407 |
| Person nodes | 291 |
| Schema nodes | 257 |
| Server nodes | 212 |
| Message nodes | 200 |
| Legacy nodes (Table) | 115 |
| Dimension nodes | 98 |
| Fact nodes | 60 |
| Session nodes | 50 |
| DataModel nodes | 42 |
| CapabilityDataDomain nodes | 30 |
| BusinessArea nodes | 13 |
| BusinessProcess nodes | 12 |
| DataProduct nodes | 12 |
| MasterDataDomain nodes | 11 |
| DataPipeline nodes | 7 |
| DataProductLine nodes | 4 |
| ValueStreamStage nodes | 3 |
| Policy nodes | 2 |
| FlatFile nodes | 1 |
| HAS_COLUMN edges | 31,417 |
| DERIVED_FROM edges | 15,021 |
| CONSUMES edges | 13,115 |
| CONTAINS edges | 9,555 |
| HAS_ROLE edges | 2,420 |
| APPLIES_TO edges | 2,314 |
| REPLICATED_TO edges | 1,728 |
| BELONGS_TO edges | 688 |
| HOSTS edges | 608 |
| REALIZED_BY edges | 353 |
| HAS_MESSAGE edges | 200 |
| REALIZED_IN edges | 161 |
| NEXT edges | 150 |
| MIGRATED_TO edges | 110 |
| REFACTORED_TO edges | 89 |
| LAST_MESSAGE edges | 50 |
| SUPPORTS edges | 46 |
| MODELS edges | 38 |
| READS edges | 27 |
| OWNS edges | 17 |
| SUBJECT_TO edges | 15 |
| BELONGS_TO_STAGE edges | 12 |
| MIGRATED_FROM edges | 9 |
| LOADS edges | 9 |
| HAS_PRODUCT_LINE edges | 4 |
| HAS_STAGE edges | 3 |
| NEXT_STAGE edges | 2 |
| LOOPS_BACK_TO edges | 1 |
| INFORMS edges | 1 |


## Data Quality / Canonicalization

To prevent duplicate nodes from inconsistent casing in source data, all load scripts
apply **case-insensitive canonicalization** before creating nodes:

- **Server names** -- explicit mapping for known servers + generic fallback (lowercase wins)
- **DataSystem names** -- explicit mapping (e.g., `HELIOS` -> `Helios`)
- **Table qualifiedNames** -- `neo4j_loader.build_table_qn_lookup()` fetches all existing Table nodes and reuses their casing for any new qualifiedName that matches case-insensitively

- **JSON-Safe Float Sanitization (NaN Handling)** -- to guarantee seamless web portal performance, all ETL loaders must clean numerical fields to replace pandas/numpy `NaN` or `Infinity` float values with standard Python `None` before running Cypher writes. While Neo4j permits writing raw `NaN` values to node properties, standard JSON web serializers (such as FastAPI/Starlette) will fail to encode them, leading to API gateway crashes.

This logic lives in `neo4j_loader.py` (shared utility) and is called by `load_master_data.py`, `load_lineage.py`, and `load_sttm.py`.

Three shared modules own the rules every loader applies. Change a rule there, never in a loader:

- **`src/medallion.py`** holds the AGENTS.md layer and `:Legacy` rules as one ordered rule table. `schema_layer()`, `is_legacy()` and `is_idp_schema()` answer in Python, and `cypher_schema_layer()` / `cypher_is_legacy_schema()` render the same table as a Cypher `CASE`, so Python and Cypher cannot drift. A test checks both against every schema in the live graph.
- **`src/excel_cells.py`** holds the Excel cleaning rules. `clean_cell()` strips invisible Unicode and NBSP, `split_multivalue()` splits on newlines and commas and drops `NA`, `pair_positional()` pairs two multi-value cells and warns on a count mismatch, and `readable_copy()` copies a workbook Excel has locked.
- **`Neo4jLoader.write_batches(query, rows, **params)`** is the one write path. It runs an `UNWIND $rows` query in 500-row transactions.

## Project Structure

```
KG_Data_Lineage_Oct2026/                     # Project root (any checkout location)
  .venv/                                     # Project Python environment
  .agents/skills/                            # Agent skills shipped with the repo (see below)
  Data/                                      # Source workbooks for src/load_*.py (not shipped)
    schemas.csv                              # Schema definitions
    tables.csv                               # Table definitions (core tables)
    reports.csv                              # Report definitions + CDD associations
    Phase 3 Reports Full Data Mapping.xlsx   # Master lineage mapping
    Phase 3 Unique Master Data.xlsx          # Master data domain mappings
    sttms/                                   # STTM Excel files (column-level lineage)
    semantic_views/                           # Semantic view Excel files per CapabilityDataDomain
    legacy_systems.xlsx                      # Legacy schema tables
    new data system files to process/        # Additional legacy schema tables
    Data_Models/                              # ER Studio data model approval tracking
  synthetic/                                 # LSC graph data model, ingest Cypher, competency questions
  src/
    neo4j_loader.py          # Neo4j connection helper, write_batches, canonicalization utilities
    medallion.py             # Layer + :Legacy rules (Python and Cypher CASE from one table)
    excel_cells.py           # Excel cell cleaning, multi-value splitting, locked-file copy
    load_datasystems.py      # Phase 0: DataSystem nodes from CSV
    load_schemas.py          # Phase 1: Schemas + DataSystems
    load_tables.py           # Phase 2: Tables (Fact, Dimension, View)
    load_lineage.py          # Phase 3: Table-level DERIVED_FROM + Alteryx provenance
    load_reports.py          # Phase 4: Reports + CONSUMES + BELONGS_TO
    load_sttm.py             # Phase 5: Column-level lineage from STTM files
    load_master_data.py      # Phase 6: MasterDataDomain + REALIZED_IN + REFACTORED_TO
    load_semantic_views.py   # Phase 7: Semantic View Table nodes from Excel
    load_retail_payments_views.py # Phase 7a: one-off semantic views (SQL-parsed)
    load_data_products.py    # Phase 8: DataProduct nodes + BELONGS_TO + REALIZED_BY
    backfill_replicated_to.py # Phase 9: Backfill Operational nodes + REPLICATED_TO
    load_legacy_tables.py    # Phase 10: Legacy schema tables + REFACTORED_TO
    load_report_to_view.py   # Phase 11: Report-to-View CONSUMES from legacy decommissioning
    load_data_models.py      # Phase 12: ER Studio DataModel nodes + BELONGS_TO + MODELS
    generate_shareable_catalog.py # Synthetic LSC catalog generator
    load_synthetic_catalog.py # Loads the synthetic catalog and asserts manifest counts
    verify_synthetic_catalog.py # Scale, leak, count and competency checks for the catalog
    export_shareable_zip.py  # Builds and scans the shareable zip
    audit_sttm_sheets.py     # Utility: audit STTM sheet structures
    _audit_skipped_columns.py # Utility: find STTM columns skipped during load
  tests/                     # pytest: rule modules, loader parsing, EXPLAIN gate on every loader query
  db_connect/                                # SQL Server / Synapse connection package (used by load_powerbi_lineage.py)
  neo4j_text2cypher_fullstack/               # Web portal: FastAPI backend + React frontend
  cypher-query-generator-workspace/          # Eval output from run_evals.py (only README.md is tracked)
  docs/
    medallion_architecture_graph_design.md   # Full graph design document
    SHAREABLE.md                             # Setup guide for the shareable LSC copy
  neo4j_instance_credentials.env            # Connection config (not committed)
  AGENTS.md                                 # AI pair-programming guidance
  pyproject.toml
```

## Prerequisites

- Python 3.11+ (managed via `uv` — see `.python-version` and `pyproject.toml`)
- Neo4j instance (connection details in `neo4j_instance_credentials.env`)
- Python packages: `neo4j`, `pandas`, `python-dotenv`, `openpyxl`

## Usage

```bash
# Full load (run in order — each phase is idempotent)
python src/load_schemas.py
python src/load_tables.py
python src/load_lineage.py
python src/load_reports.py
python src/load_sttm.py --all        # Column-level lineage (every STTM file)
python src/load_master_data.py       # Master data domains
python src/load_semantic_views.py    # Semantic View Table nodes
python src/load_retail_payments_views.py # One-off semantic views (SQL-parsed)
python src/load_data_products.py     # DataProduct nodes
python src/backfill_replicated_to.py --load # Backfill Operational nodes + REPLICATED_TO
python src/load_legacy_tables.py --load    # Legacy tables + REFACTORED_TO
python src/load_report_to_view.py --load  # Report-to-View CONSUMES
python src/load_powerbi_lineage.py     # Power BI Report and conformed dataset lineage (SQL extraction + Neo4j)
python src/load_data_models.py         # ER Studio data model artifacts

# Single STTM file (for testing)
python src/load_sttm.py --file "MyTable - Silver Data Dictionary and STTM.xlsx"
```

**Order matters after `load_lineage.py`.** It deletes each STTM target's outgoing `DERIVED_FROM` edges before re-adding them from the STTM files, so edges later phases added to those tables go with them. After re-running `load_lineage.py`, re-run every phase after it in the order above.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest -q
```

- `tests/test_medallion.py` pins the AGENTS.md layer table and checks the Cypher `CASE` against Python for every schema in the graph.
- `tests/test_excel_cells.py`, `tests/test_lineage_parsing.py` and `tests/test_write_batches.py` cover cleaning, multi-value pairing and batching without a database.
- `tests/test_loader_queries.py` runs `EXPLAIN` on every module-level Cypher constant in `src/load_*.py`, so a broken f-string query fails before it writes anything.
- Tests marked `integration` need `neo4j_instance_credentials.env` and skip without it.

Portal tests live with the portal (see [Running the Web Portal](#running-the-web-portal)).

## Shareable copy (synthetic LSC catalog)

The `shareable-snapshot` branch packages the project for colleagues with no real data and no keys. They generate a catalog for the fictional Lagos Refining & Supply Company (LSC) and load it into their own Neo4j. [docs/SHAREABLE.md](docs/SHAREABLE.md) is the setup guide, and [docs/adr/0001-shareable-synthetic-catalog.md](docs/adr/0001-shareable-synthetic-catalog.md) records the decision.

| Script | What it does |
|---|---|
| `synthetic/build_model_artifacts.py` | Builds `ingest.cypher` and the Arrows JSON from `synthetic/lsc_data_model.json` with `mcp-neo4j-data-modeling` |
| `src/generate_shareable_catalog.py` | Writes the deterministic catalog to `synthetic_data/` (gitignored) |
| `src/load_synthetic_catalog.py --database lsc` | Runs `ingest.cypher` over it and asserts the manifest counts. It refuses a database holding other data |
| `src/verify_synthetic_catalog.py` | Checks scale against the production profile, name leaks, database counts (`--database`), the 15 competency answers, and name overlap with production (`--against-live governancemetadata`, read only) |
| `src/load_powerbi_lineage.py --database lsc --source duckdb:///synthetic_data/source.duckdb` | Runs the real Power BI loader over the generated `source.duckdb` export. `--source` takes any SQLAlchemy URL (DuckDB, SQLite, Postgres, SQL Server) through `db_connect`'s `query_database` |
| `frontend/tests/competency.e2e.ts` | Asks each question in `synthetic/competency_questions.json` in the chat window and checks the answer against the manifest. `E2E_BASE_URL` picks the frontend port |
| `src/export_shareable_zip.py` | `git archive` of a ref into `dist/`, scanned for data paths, secret-shaped strings and local credential values |

## Skills shipped with the repo

Everything an agent needs lives in `.agents/skills/`, so a fresh clone has it without any user-profile install:

| Skill | Used by | Purpose |
|---|---|---|
| `cypher-query-generator/` | Portal backend at runtime, and coding agents | Project skill: graph schema, lineage query patterns, gotchas, `scripts/validate_cypher.py` (EXPLAIN-based label/relationship check) and evals. The `Agent` puts `SKILL.md` and its `references/` (including `cypher_syntax_traps.md`) in every Cypher prompt. |
| `neo4j-cypher-skill/` | Coding agents only | Vendored upstream [neo4j-contrib/neo4j-skills](https://github.com/neo4j-contrib/neo4j-skills/tree/main/neo4j-cypher-skill) v1.0.30 (MIT). General Cypher 25 guidance for writing loader and fix Cypher. Not loaded by the portal. |
`references/cypher_syntax_traps.md` in the project skill is an adapted subset of the upstream `syntax-traps.md`: write-clause rows dropped (the portal is read-only), Cypher 25-only rows (`LET`, `FILTER`, `coll.*`) rewritten for this database's Cypher 5 default, and the project's `DERIVED_FROM*1..5` rule kept over the upstream QPE preference.

To update the vendored skill, follow `.agents/skills/neo4j-cypher-skill/VENDORED.md` (shallow clone, replace the folder, record the new commit), then carry relevant `syntax-traps.md` changes into `cypher_syntax_traps.md`.

## Known Gaps

- **Documented lineage gaps.** `_KNOWN_LINEAGE_GAPS` in `neo4j_text2cypher_fullstack/backend/app/generation/agent.py` lists semantic views whose source STTMs document no upstream. The portal's `Agent` answers questions about them as documented gaps instead of running a lineage query.

## Phase 9 Details (backfill_replicated_to.py)

Reverse-engineers missing `REPLICATED_TO` and `DataSystem CONTAINS` relationships from Replica table naming conventions.

- Parses `replica_<prefix>.<tableName>` to infer the upstream DataSystem and Operational table
- Uses an explicit alias map in the script for cases where the replica prefix differs from the DataSystem name
  - `files_commercial` maps to a FlatFile, not a DataSystem
- Merges duplicate DataSystem nodes whose names differ only in spacing
- Creates DataSystems and the FlatFile the alias map names when they are missing

## Phase 10 Details (load_legacy_tables.py)

Loads legacy schema tables from two sources and creates `REFACTORED_TO` edges to their IDP replacements.

**Data sources:**
- `Data/legacy_systems.xlsx` (sheet "Unique tables") — tables across the legacy schemas
- A legacy-vs-UDM counts workbook in `Data/new data system files to process/` (path in the script) — additional legacy tables

**Legacy Schemas** are pre-standard schemas such as `dwh`, `dwh_core`, `persistence` and `staging`. In the LSC catalog they are `dwh`, `dwh_core`, `dwh_refining`, `dwh_finance`, `dwh_quality`, `persistence` and `staging`.

**Actions:**
- Legacy Table nodes created with `:Legacy` label (layer set to correct medallion value: Silver or Semantic)
- `REFACTORED_TO` edges (legacy → IDP target in `udm_core`, `mdm_core`, `sem_<business_area>` or `replica_*`)
- Views in the pre-standard semantic schema carry the `:Legacy` label with `layer=Semantic`
- Creates missing legacy semantic views with `DERIVED_FROM` to legacy sources
- Merges duplicate views (case-insensitive name collisions: `_VW` vs `_vw`)

## Phase 11 Details (load_report_to_view.py)

Loads Report-to-View consumption mappings from the legacy decommissioning tracker.

**Data source:**
- The decommissioning workbook in `Data/new data system files to process/` (sheet "Report to View", path in the script)

**Actions:**
- Creates Report nodes the earlier phases did not load
- Wires CONSUMES edges (Report → Semantic View)
- Applies view name canonicalizations (casing `_vw` → `_VW`, known typos, malformed double prefixes)

## Running the Web Portal

To run the Conversational Search & Semantic Portal locally (both the FastAPI backend gateway and the Vite React frontend):

### 1. Start the Backend Server (FastAPI)

Open a terminal and execute the following:

```bash
# 1. Activate the Python virtual environment at the project root
#    (<project root>\.venv)
source .venv/bin/activate             # On macOS/Linux
.venv\Scripts\Activate.ps1           # On Windows PowerShell

# 2. Navigate to the backend directory
cd neo4j_text2cypher_fullstack/backend

# 3. Start the FastAPI backend server
python -m app.main
```

The API server runs at `http://localhost:8000`.

### 2. Start the Frontend Server (Vite React)

Open a second terminal and execute the following:

```bash
# Navigate to the frontend directory
cd neo4j_text2cypher_fullstack/frontend

# Install dependencies if running for the first time (pnpm-lock.yaml is the tracked lockfile)
pnpm install
# On Windows, if installs fail on long paths, point the store at a short folder: pnpm install --store-dir C:\fe\pnpm-store

# Start the Vite development server
pnpm dev
```

The web portal opens in your browser at `http://localhost:5173/`, conformed for both dark and light modes!

### 3. Portal tests

```powershell
# Backend: Agent.ask / expand and the HTTP routes against a fake LLM and fake Neo4j driver
cd neo4j_text2cypher_fullstack/backend
..\..\.venv\Scripts\python.exe -m pytest -q

# Frontend: type check, then e2e against the running dev server (localhost:5173) and backend (:8000)
cd neo4j_text2cypher_fullstack/frontend
npx tsc --noEmit
pnpm test:e2e
```

The e2e suite (`tests/portal.e2e.ts`, config in `e2e.config.ts`) asks real questions, so it needs the backend and Neo4j up. It attaches to a running dev server or starts `pnpm dev` itself. `tests/screenshots.e2e.ts` saves dark and light graph screenshots; set `KG_SHOTS_LABEL` to name the folder.

The backend's `Agent` reads the `cypher-query-generator` skill (`.agents/skills/cypher-query-generator/`) on every question for both generation and self-heal, and refuses to start without it. Before generation, an intent gate in `Agent.ask` answers bare greetings/thanks from a regex (no LLM call) and sends everything else through one LLM router call (`lineage_question` / `small_talk` / `off_topic`). Small talk gets a short friendly reply and off-topic questions get a one-line refusal, both with empty Cypher and an empty dashboard. The router leans toward `lineage_question` and falls back to the pipeline on any error. Chat-history/feedback questions skip the router. `validate_cypher.py` in that skill checks labels and relationship types through the planner's `EXPLAIN` warnings, so it always matches the live schema.

### Frontend theming notes (Needle v5)

- Use Needle v5 tokens only: classes `bg-neutral-bg-weak`, `text-neutral-text-default`, `border-neutral-border-weak`, etc., and CSS variables `var(--theme-color-*)` (hex values — do not wrap in `rgb()`). The v2 names `n-bg-palette-*` / `--theme-palette-*` no longer exist and silently render transparent.
- Theme-aware overlays for inline styles (`--app-overlay*`, `--app-border*`, `--app-text-muted`, `--app-accent-text`) are defined in `frontend/src/index.css` for light and `.ndl-theme-dark`.
- Needle's unlayered reset (`* { border-width: 0 }`) overrides Tailwind's layered utilities, so border **width** utilities need the important suffix: `border!`, `border-b-2!`, `border-r!`.
- The Cypher console, Table Grid, graph legend, and metadata modal are intentionally always-dark panels.

### Frontend performance notes

- `RetrievalInformation` (NVL graph, TanStack table) is `React.lazy`-loaded and preloaded when the question box gets focus or a question is submitted. This keeps the initial JS chunk at ~612 kB (192 kB gzip) instead of ~1.96 MB. Keep heavy viewers out of `Chatbot.tsx`'s static imports.
- `Chatbot` keys the dashboard on `result.id` (one per answer), so `RetrievalInformation` seeds its graph and default tab from props once at mount. Don't add effects that copy props into state.
- The reply types out every 3 ms, so message bodies render through the memoized `Markdown` component and the question box (`ChatInput`) owns its own state. Keystrokes and typing ticks don't re-parse earlier messages.
