# Running the ontology-to-lpg skill on the EPM inputs

These scripts run the `ontology-to-lpg` skill's own scripts (version 2.3) on the projection's inputs. They do not replace `../pipeline.py`: that pipeline (guideline v2.2) stays the committed CI pipeline, and its `inferred.nt`, manifest and report stay the committed result (EPM-DEC-001-0095, item 5). These scripts write nothing into the repository (`queries.json`, the saved walks, is an input).

The input list has one source. `inputs.py` imports `PACKAGES`, `INPUTS` and `SHAPES` from `../pipeline.py` and prints them as absolute paths. Importing `pipeline.py` runs nothing: its `main()` runs only when the file is run as a script. `test_skill_run.py` checks that `inputs.py` lists exactly the pipeline's inputs and shapes, that each file exists, and that `epm-config.json` pins the same packages. `scripts/check.sh` runs it.

## Environment

| Variable | What it holds | Needed by |
|---|---|---|
| `ONTOLOGY_TO_LPG` | The skill folder, the one holding `scripts/` and `docker/compose.yaml` | every script |
| `LPG_OUT` | An output folder outside the repository; the scripts refuse a folder inside it | every script |
| `ROBOT_JAR` | ROBOT 1.9.10; `run.sh` checks its SHA-256 before it reasons | `run.sh` |
| `RDF_STORE` | The `rdf-store` skill folder (its `scripts/rdfstore.py` and `docker/compose.yaml`) | `explore.sh`, `rebuild.sh` |
| `BASELINE_OUT` | The `LPG_OUT` of the build from the repository, to compare the rebuild with | `rebuild.sh` |
| `INPUT_LIST` | Optional: a file of `data<TAB>path` and `shapes<TAB>path` lines read instead of `inputs.py` (`rebuild.sh` writes it) | every script |

The scripts also need uv, Java 11 or later (for `run.sh`) and Docker (for `load.sh`, `aura-copy.sh` and `triplestore.sh`). Paths with spaces are safe: every list is a bash array.

## The scripts, in order

1. `run.sh` checks the rules and package pins (`check_projection_rules.py`), validates the inputs with every shape (`validate_data.py`), reasons with ELK through ROBOT, writes `loadable.nt` and `inferred.nt`, checks both (`build.py check-serialised`), validates them again, and writes the manifest. It ends with the advisory `in_graph_shapes.py` prediction.
2. `load.sh` starts Neo4j with n10s through the skill's `docker/compose.yaml` (profile `neo4j`, project `epm-lpg-local`, Bolt on `127.0.0.1:17711`, a fresh password in `$LPG_OUT/neo4j-run/run.env`). It runs `load_verify.py` with `--compose-project epm-lpg-local`, so the clean-up line it prints is the compose `down -v`, then `build.py check-report`. On success Neo4j stays up for the copy; on any failure the script removes it with `docker compose ... down -v`. Set `MANUAL_CASES` to pass `--manual-cases`.
3. `aura-copy.sh <target.env> [--replace]` copies the verified graph to the Neo4j that the env file names (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, optional `NEO4J_DATABASE`) with `copy_graph.py --report`. `copy_graph.py` touches the target only when the report's own evidence holds (compiled rows, a passing case for each, equal sorted and shuffled hashes) and the local graph's hash equals the report's, and it fails unless the target's hash then equals the local one. If `load.sh`'s Neo4j is not up, it runs `load.sh` first. It removes the local Neo4j at the end. `--replace` deletes everything on the target first.
4. `graph-type.sh` writes the Cypher 25 `GRAPH TYPE` statement for the current inputs and shapes to `$LPG_OUT/graph-type.cypher` with `build.py graph-type --output`. That command reads the data files too, so it types a property as a list exactly when the load stores it as an array. The script applies nothing: apply the statement to an Enterprise target, such as Aura, after `aura-copy.sh`, by hand.
5. `triplestore.sh` starts Jena Fuseki through the compose file (profile `fuseki`), loads the inputs and `inferred.nt` with `triplestore.py`, one named graph per file, and checks the per-graph, per-predicate and three-way counts against `projection-report.json`. `triplestore.py` writes its report only when every count matched, and needs a report from `load.sh` that says `passed: true`. It removes Fuseki at the end.

6. `tags.sh` (add-on F of the skill, personal-agent-skills #65) tags every node and relationship of the local Neo4j with its package (`module_tags.py tag`), checks the tags and builds the `:Module` graph; `tags.sh --env <file>` checks the tags and builds the module graph on a copy, such as Aura after `aura-copy.sh` (the tags travel with the copy; the hash leaves them out).
7. `explore.sh [--env <file>]` starts Jena Fuseki from the `rdf-store` skill's compose file, loads the inputs and `inferred.nt` (hash-checked), and runs `explore.py compare`: every walk in `queries.json` (one from each module's kind of node, plus a process across modules, a value stream end to end and a measure back to its processes) and the module map, Neo4j against Jena. It writes `$LPG_OUT/explore-report.json` and removes Fuseki.
8. `rebuild.sh <databricks.env> <table> <target.env>` is step 5 of the store tests: it exports the Databricks table (`rdfstore.py export`), compares it with the release files by hash, maps the exported graphs to the inputs (`rebuild_inputs.py`), runs `run.sh` and `load.sh` on them, requires the same triples (as RDF 1.1 terms) and the same graph hashes as `$BASELINE_OUT`, then tags, copies to the target and checks the tags there. Empty the local Neo4j and the target first.

The run of 2026-10-25, with every count and hash, is in `store-tests-2026-10-25.md`.

`run.sh` covers checks V1 to V5 of the skill's validation path and `load.sh` covers V6 to V12; `aura-copy.sh` and `triplestore.sh` cover the remaining checks, up to V14. For the `GRAPH TYPE` checks G1 to G4, `graph-type.sh` generates the statement; applying it, reading it back with `SHOW CURRENT GRAPH TYPE` and probing it with a write that breaks it are done by hand. The skill's `references/multi-store.md` defines both lists.

`epm-config.json` is the skill's projection configuration for these inputs: Rule 4a, the module namespaces and prefixes, the qualified-relation classes, the package pins (equal to `PACKAGES`) and no release exceptions.
