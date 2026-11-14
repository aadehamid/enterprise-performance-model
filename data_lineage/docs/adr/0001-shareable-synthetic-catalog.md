# 0001. Share the project with a generated LSC catalog, not real data

Date: 2026-11-01. Status: accepted.

## Context

Colleagues need to run the lineage graph and the text2cypher portal on their own machines. The real catalog describes internal systems, hosts, plants and people, and the env file holds live keys. Neither can leave this machine. The portal only works if the skill and context files it puts in every prompt name tables that exist in the graph it queries.

## Decision

- Ship `git archive` of the `shareable-snapshot` branch, built and scanned by `src/export_shareable_zip.py`. No data folder, env file, database or dependency folder ships. The scan fails on secret-shaped strings and on any value from the local credentials file.
- Model the graph once in `synthetic/lsc_data_model.json`, validated by `mcp-neo4j-data-modeling`. Generate `ingest.cypher` and the Arrows JSON from it with the same library, patched where its output is wrong for this project.
- Generate a deterministic catalog for a fictional downstream oil and gas company, Lagos Refining & Supply Company, so the demo audience recognises the systems, entities and reports. It is sized to the production profile within 10 percent per label and per relationship pattern. Plant the paths the 15 competency questions need and record their answers in `manifest.json`.
- Rename every non-public system, host, plant and person. Public products keep their names, including widely used downstream products (IBM Maximo, AVEVA PI, Toptech TMS, LabWare LIMS, Aspen PIMS, Allegro, Platts, DTN). Non-public systems, refineries and terminals get fictional names, and the company is set in Nigeria so it reads as clearly not the source company.
- Every report consumes at least one Semantic view whose `DERIVED_FROM` and `REPLICATED_TO` path reaches an Operational table. Views without lineage stay in the catalog to match production's gap rate, but no report reads them. `verify_synthetic_catalog.py` checks this in the files and in the loaded database.
- Rewrite every runtime support file (the cypher-query-generator skill and its references, `llm_graph_cypher_query_generation_context.md`, the known lineage gaps in `agent.py`, and the tests that pin those names) to LSC on the branch. `src/load_*.py` keep their original names as examples of real ingestion.
- The branch is never merged to `main`.

## Consequences

- A colleague can rebuild the whole graph with three commands and check it with a fourth. The same seed gives the same answers, so the setup guide can state them.
- `main` and the branch diverge on runtime prompt files. A prompt or skill change on `main` must be ported to the branch by hand before the next export.
- Downstream vocabulary brings the catalog closer to production terms. Generic industry terms are expected; exact identifiers are not, and `--against-live` must pass before every export.
- The catalog matches production shape, not production content. Query performance and LLM behavior on it are a close guide, not a guarantee.
- `verify_synthetic_catalog.py --against-live` can prove no generated identifier equals a production one, but only on a machine that can reach production.
