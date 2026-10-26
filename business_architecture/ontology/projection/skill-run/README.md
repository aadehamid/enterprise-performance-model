# Running the ontology-to-lpg skill on the EPM inputs

The `ontology-to-lpg` skill's `run_projection.py` (version 2.3 of its method, personal-agent-skills #67) runs the projection of the EPM release, every store and every check, from the run configuration in this folder. It does not replace `../pipeline.py`: that pipeline (guideline v2.2) stays the committed CI pipeline, and its `inferred.nt`, manifest and report stay the committed result (EPM-DEC-001-0095, item 5). The driver writes nothing into the repository.

## What is here

| File | What it is |
|---|---|
| `epm-run.json` | The run configuration: releases mode, the inputs from `inputs.py`, each release's `shapes` and `catalog` graphs, Aura as the copy target, the Databricks table `epm_triples`, the saved walks, and a rebuild from Databricks. Outputs go to `~/lpg-out/`, outside the repository. |
| `inputs.py` | The one input list. It imports `INPUTS`, `SHAPES` and `PACKAGES` from `../pipeline.py` and prints them as absolute paths (`data`, `shapes`, `releases`). Importing `pipeline.py` runs nothing: its `main()` runs only when the file is run as a script. |
| `epm-config.json` | The skill's projection configuration for these inputs: Rule 4a, the module namespaces and prefixes, the qualified-relation classes, the package pins (equal to `PACKAGES`) and no release exceptions. |
| `queries.json` | The 14 saved walks the explore step compares in Neo4j and Jena: one from each module's kind of node, plus a process across modules, a value stream end to end and a measure back to its processes. |
| `test_skill_run.py` | Checks that `inputs.py` lists exactly the pipeline's inputs and shapes, that each file exists, that `epm-config.json` pins the same packages, that `epm-run.json` names this folder's files (each must exist) and keeps outputs, ROBOT and the env files under the home folder, which CI cannot check, that every release has its `shapes` and `catalog` files, and that each saved walk is well formed. `scripts/check.sh` runs it. |
| `store-tests-2026-10-25.md` | The store tests' results, first with this folder's earlier scripts and then again through the driver. |

## Running it

With the skill folder in `$SKILLS` (personal-agent-skills' `skills/data`):

```
cd "$SKILLS/ontology-to-lpg/scripts"
uv run --no-project --with rdflib python3 run_projection.py --config <this folder>/epm-run.json --plan
uv run --no-project --with rdflib python3 run_projection.py --config <this folder>/epm-run.json --skip databricks
```

`--plan` lists the steps and why any is skipped. `--skip databricks` leaves the table as it is: the rebuild still exports it and checks its hash against the release files. The run needs uv, Docker and Java 11 or later, ROBOT 1.9.10 at `~/epm-lpg/robot.jar`, an Aura env file at `~/.config/neo4j/aura.env` (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`) and the Databricks env file at `~/.config/databricks/epm.env`. Change those paths in a copy of `epm-run.json` for another machine.

`replace_target` is on, so the copy and the rebuild's copy delete everything on Aura first. That Aura instance holds only these test runs.

`keep_neo4j` is on (since 2026-10-26), so the local Neo4j stays up after the run for exploration. `../LOCAL-STORES.md` lists every store kept loaded and how to refresh it.

The skill's `references/run-config.md` describes each step and the check it runs. Steps 2 to 4 cover checks V1 to V5 of the skill's validation path and the load covers V6 to V12. The copy, the triple-store counts and the round trips cover the rest, up to V14. For the `GRAPH TYPE` checks G1 to G4, the `graph-type` step writes the statement; applying it, reading it back with `SHOW CURRENT GRAPH TYPE` and probing it with a write that breaks it are done by hand.
