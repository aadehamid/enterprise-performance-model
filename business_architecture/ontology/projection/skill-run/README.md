# Running the ontology-to-lpg skill on the EPM inputs

These scripts run the `ontology-to-lpg` skill's own scripts (version 2.3) on the projection's inputs. They do not replace `../pipeline.py`: that pipeline (guideline v2.2) stays the committed CI pipeline, and its `inferred.nt`, manifest and report stay the committed result (EPM-DEC-001-0095, item 5). These scripts write nothing into the repository.

The input list has one source. `inputs.py` imports `PACKAGES`, `INPUTS` and `SHAPES` from `../pipeline.py` and prints them as absolute paths. Importing `pipeline.py` runs nothing: its `main()` runs only when the file is run as a script. `test_skill_run.py` checks that `inputs.py` lists exactly the pipeline's inputs and shapes, that each file exists, and that `epm-config.json` pins the same packages. `scripts/check.sh` runs it.

## Environment

| Variable | What it holds | Needed by |
|---|---|---|
| `ONTOLOGY_TO_LPG` | The skill folder, the one holding `scripts/` and `docker/compose.yaml` | every script |
| `LPG_OUT` | An output folder outside the repository; the scripts refuse a folder inside it | every script |
| `ROBOT_JAR` | ROBOT 1.9.10; `run.sh` checks its SHA-256 before it reasons | `run.sh` |

The scripts also need uv, Java 11 or later (for `run.sh`) and Docker (for the other three). Paths with spaces are safe: every list is a bash array.

## The scripts, in order

1. `run.sh` checks the rules and package pins (`check_projection_rules.py`), validates the inputs with every shape (`validate_data.py`), reasons with ELK through ROBOT, writes `loadable.nt` and `inferred.nt`, checks both (`build.py check-serialised`), validates them again, and writes the manifest. It ends with the advisory `in_graph_shapes.py` prediction.
2. `load.sh` starts Neo4j with n10s through the skill's `docker/compose.yaml` (profile `neo4j`, project `epm-lpg-local`, Bolt on `127.0.0.1:17711`, a fresh password in `$LPG_OUT/neo4j-run/run.env`). It runs `load_verify.py`, then `build.py check-report`. On success Neo4j stays up for the copy; on any failure the script removes it with `docker compose ... down -v`. Set `MANUAL_CASES` to pass `--manual-cases`.
3. `aura-copy.sh <target.env> [--replace]` copies the verified graph to the Neo4j that the env file names (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, optional `NEO4J_DATABASE`) with `copy_graph.py`. It fails unless the target's graph hash equals the local hash and the report's. If `load.sh`'s Neo4j is not up, it runs `load.sh` first. It removes the local Neo4j at the end. `--replace` deletes everything on the target first.
4. `triplestore.sh` starts Jena Fuseki through the compose file (profile `fuseki`), loads the inputs and `inferred.nt` with `triplestore.py`, one named graph per file, and checks the per-graph, per-predicate and three-way counts against `projection-report.json`. It removes Fuseki at the end.

`run.sh` covers checks V1 to V5 of the skill's validation path and `load.sh` covers V6 to V12; `aura-copy.sh` and `triplestore.sh` cover the remaining checks, up to V14. The `GRAPH TYPE` checks G1 to G4 have no script here: generate the statement with `build.py graph-type --config epm-config.json --shapes ...` and apply it to the target by hand. The skill's `references/multi-store.md` defines both lists.

`epm-config.json` is the skill's projection configuration for these inputs: Rule 4a, the module namespaces and prefixes, the qualified-relation classes, the package pins (equal to `PACKAGES`) and no release exceptions.
