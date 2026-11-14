# Project Guidance

This repository is for building a knowledge graph from data modeling artifacts, data engineering artifacts, business context, and related documentation.

## Before you begin

**Read the following files in full before starting any work.** This ensures you understand the graph schema, conventions, and the current state of the project.

| File | Purpose |
|---|---|
| `README.md` | Project overview, setup instructions, and current state of loaders/scripts |
| `AGENTS.md` | Working conventions, validation rules, and graph modelling patterns (this file) |
| `src/data_model_merge_template.cypher` | Canonical `MERGE` patterns for every node type and relationship in the graph |
| `llm_graph_cypher_query_generation_context.md` | Full graph schema — node labels, properties, relationships, layer rules, and Cypher query patterns |

**After reading all four files, you must:**
1. Provide a concise summary of the project — what we are building, the graph structure, the data layers, and the current state of the work.
2. Wait for the user to confirm that the summary is correct before starting any task.

Do not begin any task until the user has confirmed your understanding is correct.

## Working environment
- Project root: the folder containing this file, wherever it is checked out. All paths (data, scripts, credentials, skills) resolve relative to this folder — do not reference any older copy of the project elsewhere on disk. Code and committed config must not hardcode machine paths; derive them from `Path(__file__)` (see `src/load_powerbi_lineage.py`).
- **Shareable branch.** `shareable-snapshot` carries the synthetic Lagos Refining & Supply Company (LSC) copy described in `docs/SHAREABLE.md`. Its skill and context files describe the LSC graph, so never merge it into `main`. Load synthetic data only into a scratch database (`lsc`), never `governancemetadata`. Build the zip with `src/export_shareable_zip.py`, never by hand.
- Use the Python virtual environment at the project root: `.venv\Scripts\python.exe`
- Activate that environment before running Python, tests, linters, notebooks, or scripts.
- Do not use system Python unless explicitly approved.

## Core workflow
- For “grill me with docs” requests, use Matt’s shared `grill-with-docs` skill at `~/.agents/skills/grill-with-docs/SKILL.md`; it invokes `grilling` and `domain-modeling`. For grilling without docs, use the shared `grill-me` skill. Do not use a project-local copy.
- Treat all tasks as requiring validation, not just completion.
- Always validate work before reporting success.
- Prefer small, incremental changes with clear checkpoints.
- **Branch workflow**: commit work on a feature branch. When the branch is finished, merge it into `main`, restart the application (backend + frontend) from `main` and verify it works, then delete the feature branch.
- If unsure about a best practice, do a quick web search and confirm the current recommendation before proceeding.
- **When in doubt about Cypher syntax, schema design, or graph modelling patterns, browse the official Neo4j documentation at [neo4j.com/docs](https://neo4j.com/docs) before proceeding.**
- **Cypher skills shipped with the repo** (`.agents/skills/`, present on every clone):
 - `neo4j-cypher-skill/` — vendored upstream Neo4j guidance (MIT, see its `VENDORED.md`). Read its `SKILL.md` and `references/` (`syntax-traps.md`, `cypher-syntax.md`, `performance.md`) when writing or validating loader and graph-fix Cypher. Do not edit it; update it as `VENDORED.md` describes. The `governancemetadata` database runs Neo4j 2025.06 with default language **Cypher 5**, so its Cypher 25-only advice (`LET`, `FILTER`, `coll.*`, `CYPHER 25` prefix) does not apply unless a query opts in.
 - `cypher-query-generator/` — the portal's runtime skill. The backend `Agent` puts its `SKILL.md` and listed `references/` (including the adapted `cypher_syntax_traps.md`) in every generation and self-heal prompt. It never loads `neo4j-cypher-skill`.
- Be concise: avoid verbose explanations. Summarise what was done and why, not a line-by-line narration.

## Validation requirements
- Verify outputs with tests, assertions, schema checks, or spot checks appropriate to the task.
- **Always test the actual return value of code** — confirm it produces the expected result, not just that it ran without error.
- Re-run validation after any fix or refactor.
- Do not claim success until the work is validated.
- If validation fails, fix the issue and validate again.
- **Test suites** — run before every commit:
  - `.venv\Scripts\python.exe -m pytest -q` from the project root (rule modules, loader parsing, and an `EXPLAIN` gate that plans every Cypher constant in `src/load_*.py`).
  - `..\..\.venv\Scripts\python.exe -m pytest -q` from `neo4j_text2cypher_fullstack/backend` (portal `Agent` and routes with a fake LLM and driver).
  - `npx tsc --noEmit` and `pnpm test:e2e` from `neo4j_text2cypher_fullstack/frontend` (needs backend :8000 and Neo4j up).
- **Refactor pins** — for a behavior-preserving loader change, record the writes old and new code send (a fake `Neo4jLoader` whose `write_batches` and `driver.session().execute_write` append `(query, rows)`), run both versions from a `git worktree` of the old commit over the real `Data/` files, and diff. Nothing touches the database, and the diff is the proof.
- Live `/ask` calls write `Session` and `Message` nodes (`record_message`). Agent test calls must pass a `session_id` prefixed `test-` (for example `test-intentgate-hey`) so they can be removed with `MATCH (s:Session) WHERE s.id STARTS WITH 'test-'`. The e2e suite cannot set one: `useAsk` mints a random UUID per page load, so each test writes an untagged session. Note the time window of every e2e run you make. Clean up with the pre/post pattern: select sessions whose every `Message.question` is an e2e question (`fill(...)` in `frontend/tests/*.e2e.ts`, plus every question in `synthetic/competency_questions.json`, which `competency.e2e.ts` asks) and that fall inside a run window, and never delete a session holding any other question. The user also asks those questions by hand. Untagged sessions outside a run window stay (2026-10-31 cleanup kept `5fbe37e0…`, the user's own `hey`). Sessions with no messages are Neo4j shells whose messages `archive_old_messages` moved to `backend/app/database/chat_history.db`. They are not test debris.
- **Portal LLM prompts are told apart by their last line** in `tests/fakes.py` (`Answer:` = summary, `Intent JSON:` = intent router, anything else = Cypher generation/self-heal). A new `Agent` LLM call needs its own suffix and a `FakeLLM` branch, or it silently eats a scripted Cypher and shifts every test. Any non-Cypher `Agent` path (like the intent gate) should be asserted with `llm.cypher_prompts == []` and no non-`Session` Neo4j queries.
- **For graph data fixes, use the pre/post-fix validation pattern:** capture counts and state _before_ the fix, apply the fix, then assert the expected _after_ state (e.g., count of updated nodes matches expectation, no remaining violations). This makes regressions immediately visible.
- After task completion, share a Cypher query that can be run in Neo4j Browser (Graph view) to visually verify the results. This is in addition to the programmatic validation the agent performs.

## Temporary files and cleanup
- Only project files belong in this repo. Do not add unrelated files, personal scratch notebooks, one-off exploration scripts, agent audit logs, or exports. Generated output (e2e reports, eval results, caches, local DBs) must be gitignored.
- Clean up all temporary files, scratch scripts, exports, caches, and intermediate artifacts created during exploration or testing.
- Do not leave behind one-off files unless they are intentionally part of the solution.
- If a temporary file is needed, place it in a clearly disposable location and **remove it immediately when done** — do not leave stray files in the project directory.

## Documentation
- Once a solution is agreed to and working, document what was done.
- Record the final approach, key decisions, assumptions, validation steps, and any important operational notes.
- Update project documentation when the implementation changes workflow, architecture, or usage.
- **Schema changes require updating two files immediately:**
  - `src/data_model_merge_template.cypher` — add or revise `MERGE` patterns for any new node type or relationship.
  - `llm_graph_cypher_query_generation_context.md` — reflect any new nodes, relationships, properties, or constraints so the LLM query context stays accurate.
- **Keep `AGENTS.md` current.** When a practice proves to work well or poorly, update the relevant section. This file is a living document, not a one-time snapshot.
- **Keep `README.md` current.** Update it whenever new loaders, scripts, workflows, or significant changes are added — it should always reflect the current state of the project.

## Knowledge graph expectations
I will provide guidance as needed.
- Preserve source traceability for extracted facts and relationships.
- Prefer explicit mappings from source artifact to graph entity and relationship.
- Avoid silent transformations that make provenance unclear.
- When uncertain, ask for clarification rather than inventing structure.

## Neo4j tooling
- **`Neo4jLoader` is pre-installed** in the project virtual environment (`.venv`). No installation step is needed — import and use it directly in validation scripts.
- Load credentials from `neo4j_instance_credentials.env` via `python-dotenv` when instantiating `Neo4jLoader`.
- The target database is `governancemetadata`. Use `:use governancemetadata` **only when connecting programmatically** (e.g., specifying the database in `Neo4jLoader` config). Do **not** prepend it to Cypher queries shared with the user for Neo4j Browser — the user is already connected to the correct database.

## Secrets and credentials
- Never hardcode credentials in scripts.
- Load Neo4j connection details from `neo4j_instance_credentials.env` using `python-dotenv`.
- Do not commit `.env` files to version control.

## Idempotency
- All Cypher write operations must use `MERGE` (not `CREATE`) to be safely re-runnable.
- Use `ON CREATE SET` for initial property values and `ON MATCH SET` for updates.
- Every load script must be idempotent — running it twice must not duplicate nodes, relationships, or corrupt properties.

## Pilot-then-batch workflow
- Test every new load script or significant change on a small pilot set (e.g., 3 files) before running at scale.
- Validate pilot results with targeted queries before proceeding to full batch.
- After batch completion, run summary counts and spot-check queries to confirm integrity.

## Graph schema conventions
- `qualifiedName` is the merge key for Table, Column, and Schema nodes.
- `layer` is a property on Schema and Table nodes (Operational, Replica, Silver, Gold, Semantic), not a label.
- **Layer assignment rules** — always derive `layer` from the object's schema name or prefix:
  | Schema / Prefix | Layer |
  |---|---|
  | `udm_core.*`, `mdm_core.*` | `Silver` |
  | `replica*` | `Replica` |
  | `sem_<business_area>.*` (e.g. `sem_wholesale.*`, `sem_masterdata.*`) | `Semantic` |
  | `<business_area>_core.*` (e.g. `wholesale_core.*`) | `Gold` |
  | `dwh*` (e.g. `dwh_core.*`, `dwh_refining.*`, `dwh_finance.*`, `dwh_quality.*`), `persistence.*`, `staging.*`, and the other pre-standard Silver schemas in `src/medallion.py` | `Silver` (pre-standard schemas — also carry `:Legacy` label) |
  | The pre-standard semantic schema in `src/medallion.py` | `Semantic` (pre-standard schema — also carries `:Legacy` label) |
  - **Semantic — primary pattern**: schema is `sem_<business_area>` (e.g. `sem_wholesale`, `sem_masterdata`). `qualifiedName` follows `sem_<business_area>.<object_name>`.
  - **Gold pattern**: any schema matching `*_core` that is NOT `udm_core` or `mdm_core` is Gold.
  - `udm_core` and `mdm_core` are Silver (universal/master data cores), not Gold — do not apply the `_core` Gold rule to them.
  - When the `layer` property is set or updated, verify it matches these rules before committing.
 - **`src/medallion.py` is the only implementation of these rules.** Loaders call `schema_layer()` / `is_legacy()` in Python or embed `cypher_schema_layer()` / `cypher_is_legacy_schema()` in Cypher. Never re-implement the table in a loader; change `_LAYER_RULES` and `tests/test_medallion.py` together.
- **Legacy provenance** — objects from pre-standard schemas (e.g. `dwh`, `dwh_core`, `dwh_refining`, `dwh_finance`, `dwh_quality`, `persistence`, `staging`, and the pre-standard semantic schema; `src/medallion.py` holds the full list) carry a `:Legacy` label (not a layer value). Query them with `MATCH (t:Table:Legacy)` or `MATCH (s:Schema:Legacy)`. This follows the same multi-label pattern as `:Table:Fact`, `:Table:Dimension`, `:Table:View`.
  - **Union tables are Legacy**: Silver-layer tables with `union` (case-insensitive) in their name carry the `:Legacy` label. These are pre-standard dimension consolidation tables (e.g., `mdm_core.Currency_Union_Dim`).
- Dimensional roles use multi-labels: `:Table:Fact`, `:Table:Dimension`, `:Table:View`.
- Relationship types follow a fixed vocabulary: `HAS_COLUMN`, `DERIVED_FROM`, `CONTAINS`, `REPLICATED_TO`, `HOSTS`, `BELONGS_TO`, `MIGRATED_FROM`, `CONSUMES`, `REALIZED_IN`, `REALIZED_BY`, `REFACTORED_TO`, `READS`, `LOADS`, `MODELS`.
- Node types include: `DataSystem`, `Schema`, `Table`, `Column`, `Report`, `Server`, `BusinessArea`, `MasterDataDomain`, `Policy`, `ValueStreamStage`, `DataProductLine`, `CapabilityDataDomain`, `BusinessProcess`, `DataProduct`, `FlatFile`, `DataPipeline`, `DataModel`.
- **DataModel** represents an ER Studio data model artifact (merge key: `name`). Properties: `fileName`, `modelType` (`Conceptual` | `Logical`), `folderLink`, `sourceFile`. Relationships: `MODELS` (DataModel→CapabilityDataDomain) and `BELONGS_TO` (DataModel→DataSystem, when a specific system is known).
- **DataPipeline** represents a Synapse pipeline (merge key: `name`). Properties: `synapseDataflow`, `alteryxWorkflow`, `sourceFile`. Relationships: `READS` (DataPipeline→Table, for source/Replica tables read by the pipeline) and `LOADS` (DataPipeline→Table, for Gold tables written by the pipeline).
- **Semantic lineage rules** — Views/Semantic tables must not have `DERIVED_FROM` edges pointing directly to Replica tables. They must derive from Gold or Silver. All Semantic-layer tables should have at least one `DERIVED_FROM` relationship.
- New node types or relationship types require explicit approval before use.

## Post-processing and defensive patterns
- After loading, run post-processing queries to catch orphaned nodes (e.g., Tables without a parent Schema).
- Use `LINK_ORPHAN_TABLES_QUERY` pattern: find disconnected nodes, derive the expected parent from naming conventions, and wire them.
- Log counts for every write operation so discrepancies are immediately visible.
- **Dynamic Lookup-and-Link Rule (`MERGE` vs. `MATCH`)**: When connecting primary nodes (like Reports or Tables) to lookup nodes (like Schemas or CapabilityDataDomains), using `MATCH` on the lookup node will silently drop the entire relationship row if that lookup node is not already created. Always use `MERGE` on the lookup node (with `ON CREATE SET` for creation metadata) during bulk ETL linkages to automatically register new elements.
- **Bypassing Exclusive Windows File Locks**: Excel exclusively locks files on Windows, causing standard python `open()` or `shutil` calls to crash with a `PermissionError`. Always implement a defensive fallback using a subprocess call to PowerShell `Copy-Item` to copy locked files to a temporary location before loading, which utilizes native Windows API sharing permissions.

## Batch processing
- Write through `loader.write_batches(query, rows, **params)`. It runs an `UNWIND $rows` query in 500-row `execute_write` transactions. Do not open `loader.driver.session()` for batch writes.
- This prevents transaction timeouts and memory issues on large datasets.
- **Re-run order after `load_lineage.py`.** Its STTM override deletes each target's outgoing `DERIVED_FROM` edges, including ones later phases added. After re-running it, re-run every later phase in README order. Running a later phase first and then `load_lineage.py` silently loses edges (seen: 102 `DERIVED_FROM`).

## Data cleaning conventions
- **`src/excel_cells.py` implements these rules** (`clean_cell`, `split_multivalue`, `pair_positional`, `readable_copy`). Use it in every loader instead of local helpers. Multi-value cells that span schema, table and field (STTM Source columns) are split per cell and paired by position (`load_sttm.source_columns`). Skipping that produced comma-joined ghost Tables and Columns.
 - Exception: `load_sttm.cell_val` keeps plain `strip()`. A recorded-writes pin showed `clean_cell` would rename the loaded Column `mdm_core.IIR_Plants_Dim.SIC\xa0_Code_Name` (inner NBSP) and MERGE a duplicate. Switch only together with a migration of that node.
- Strip invisible Unicode characters (`\u200b` zero-width space, `\u200c`, `\u200d`, `\ufeff` BOM) from all Excel cell values before use. Normalize `\u00a0` (non-breaking space) to a regular space.
- **Strict float/NaN sanitation** — Never write raw `NaN` (Not a Number) or `Infinity` float values into Neo4j nodes or properties. Although Neo4j permits them, standard JSON serializers (e.g. Starlette/FastAPI) will crash when building RAG payload responses. Always run `.fillna(None)` or `.replace({float('nan'): None})` during the pandas/Excel ETL load phase to guarantee JSON-safe values.
- Filter out `"NA"` (case-insensitive) values from multi-value columns to prevent bogus graph nodes.
- Split multi-value cells on both newlines (`\n`) and commas (`,`) to handle all observed delimiter patterns.
- When two columns both contain multi-line values, pair them positionally (index 0 ↔ 0, 1 ↔ 1, etc.). Log a warning if counts don't match.
- Use `MERGE` (not `MATCH`) when creating `DERIVED_FROM` edges to upstream tables. `MATCH` silently drops rows when the target node doesn't exist yet; `MERGE` creates a stub node and wires it to its Schema.
- After fixing stale data from prior runs, always delete old edges before re-running the loader — `MERGE` only adds, it does not remove incorrect edges.

## Quality bar
- Follow current best practices for Python, data engineering, and knowledge-graph modeling.
- Favor readable, maintainable, and testable implementations.
- If a tradeoff is needed, explain it before proceeding.
