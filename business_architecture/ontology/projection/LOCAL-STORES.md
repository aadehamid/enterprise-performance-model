# The stores kept for exploration

Since 2026-10-26 the stores below stay loaded after a run, so the decision owner can explore the graph, the ontology and the Databricks data, as they asked that day (`../step4/review-evidence/decision-owner-answers/answers-2026-10-26-keep-stores.md`). Before that date each run removed its local containers. This page says where each store is, which command refreshes it and where its login lives. No password is written here: each one stays in its env file. The `run.env` files are written by the scripts with mode 600; the Aura and Databricks env files are yours, so set their mode yourself (`chmod 600`).

| Store | What it holds | Refresh it with | Login |
|---|---|---|---|
| Local Neo4j, from the driver | The projection of every released package, as the driver's last step (`rebuild`) loads it back from `epm_triples` | `uv run --no-project --with rdflib python3 run_projection.py --config <this folder>/skill-run/epm-run.json`, from the skill's `scripts/` folder (`skill-run/README.md`, "Running it"); `keep_neo4j` is on, so the container stays up | Bolt `localhost:17711`; `~/lpg-out/epm-rebuild/neo4j-run/run.env` after a full run, because the rebuild replaces the first container; `~/lpg-out/epm/neo4j-run/run.env` only when the rebuild is skipped |
| Local Neo4j, from the pipeline | The same projection, built by `pipeline.py` | `./run_local.sh --keep` from this folder | Bolt `localhost:17687`, browser `localhost:17474`; `~/epm-lpg/run.env` |
| Neo4j AuraDB | A copy of the driver's local graph | The same driver run (its copy step) | `~/.config/neo4j/aura.env` |
| Databricks Free Edition, `epm_triples` | The release triples as a Delta table | The same driver run (its `databricks` step) | `~/.config/databricks/epm.env` |
| Local Postgres, `pricing-demo-sources` | The pricing demo's six synthetic source databases | `docker compose -f docker/docker-compose.yml up -d`, then `uv run python -m pricing_demo.load_postgres`, from the demo's folder (`demos/downstream-pricing-databricks-free/README.md`, "Run it") | `127.0.0.1:55432`; the local demo login in `docker/docker-compose.yml` |
| Databricks Free Edition, catalog `idp_sbx` | The demo's replica, silver and gold tables, metric views and Genie agents | The demo's `replicate`, `databricks` and `genie` commands, in the README's order | `~/.config/databricks/epm.env` or the demo's `.env` |

The Postgres data sits in the named Docker volume `pricing-demo-pgdata`, so a reboot keeps it. The container has `restart: unless-stopped`; after a reboot, start all three local containers as `stores-runbook.html` says, whichever came back by itself. `replace_target` is on in `skill-run/epm-run.json`, so each driver run replaces what Aura holds.

`stores-runbook.html`, beside this page, explains the end-to-end workflow with diagrams, and gives the commands to check, stop, start, restart after a reboot, purge and reload each store. Open it in a browser.

The scripts that build and check these stores are in the repository: `pipeline.py`, `run_local.sh` and `skill-run/` here, and `pricing_demo/` and `tests/` in the demo.
