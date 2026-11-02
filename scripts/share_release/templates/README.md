# The EPM ontology and pricing demo, release {{RELEASE_NAME}}

This folder holds a business ontology for downstream oil and gas, the scripts that build and check it, the stores it is projected into, and a pricing demo that uses it. Everything here can be rebuilt and checked from this folder alone. It is a base for you to build on, and nothing in it assumes you have seen it before.

**To change it, read [`HOW-TO-UPDATE.md`](HOW-TO-UPDATE.md) first:** how to change a definition, add a concept, change a process and add a module, and who decides each.

To understand it, start with `business_architecture/ontology/epm-ontology-guide.html` in a browser. It explains what the ontology is for, why it is split into modules, what each module holds, and follows one pricing measure from the business to the stores. Then `business_architecture/ontology/epm-walkthrough.html` tells the whole story and, in its second part, rebuilds it step by step.

## What is here

| Folder | What it holds |
|---|---|
| `business_architecture/business_process/` | The process authority: the downstream process map, the two value streams, the office lanes and the data-product portfolio, as JSON, with their schemas and tests |
| `business_architecture/ontology/` | The ontology: each module's sources and builder, the released packages (`releases/`, the newest set, and `releases/previous/`, the release before each, where a module has one), the projection into Neo4j, the competency-question regression, the validation shapes, and the documents |
| `business_architecture/reference/` | The evidence behind the definitions: MPC's public filings, the industry view (analysis of publicly available filings from U.S. refining peers), the APQC framework, vendor descriptions |
| `business_architecture/domain/` | The business glossary, the data domains, the problem statement, and the decision packages |
| `demos/downstream-pricing-databricks-free/` | The pricing demo: synthetic pricing data in Databricks Free Edition, metric views bound to the ontology's measures, Genie agents, a technical graph and the acceptance tests |
| `skills/` | The four skills that hold the method: `ontology` (the method), `ontology-to-lpg` (the projection into a property graph), `rdf-store` (triple stores) and `clear-writing` |
| `scripts/` | `check.sh`, the one command that proves your copy is valid; `check-pinned.sh`, the optional check that it still equals this release; `epm_facts.py`, which reports figures from the sources; the page builder |
| `best-practices/` | General guides on production-ready ontologies and enterprise KPIs |
| `HOW-TO-UPDATE.md` | How to change what you received, with worked commands |
| `KNOWN-OPEN-ITEMS.md` | What is open, and what was not run on this release |

<!-- augment -->
## One module from outside these sources

Everything here was built from one set of sources, except one module. `logical-model 1.0.0` holds logical data models exported from ER Studio Data Architect. Their files were kept apart from those sources and added when this release was cut. Each model's export and links file are in `business_architecture/ontology/logical-model/models/`, beside the two graphs built from them: `<model>.erstudio.ttl`, ER Studio's export in ER Studio's own namespace, and `<model>.layer.ttl`, the annotations that link its entities to `party`, `system` and `data-product`. The package is in `business_architecture/ontology/releases/logical-model/1.0.0/`. Its `manifest.json` and `release.json`, at the top of this folder, list each original file under `augment`, with its SHA-256. The ontology's rewrite of its own IRIs applied to the links file; ER Studio's namespace, `https://www.erstudio.com/semanticmodel/`, is ER Studio's and was not changed. The made-up model in `logical-model/example/` is test data. To add a model, see "Add a logical model" in `HOW-TO-UPDATE.md`.

<!-- /augment -->
## Before you run anything

- Python 3.12 and [uv](https://docs.astral.sh/uv/) run every script and test with their dependencies.
- Docker runs the local Neo4j (with the n10s and APOC plugins) and the demo's Postgres.
- Java 11 or later and ROBOT 1.9.10 reason over the ontology before the projection; the projection README says where to put the jar.
- A Databricks Free Edition workspace with a personal access token, your own, for the demo and the ontology's Delta table; an EIA API key only to refresh the public data (the cached data is enough to run the demo); a Neo4j AuraDB login only if you want the cloud copy.

Logins go in `~/.config/databricks/epm.env`, `~/.config/neo4j/aura.env` and the demo's `.env` (copy `.env.example`). Nothing here holds a login.

## Run the checks

```sh
bash scripts/check.sh
```

It verifies that every released package equals a fresh build from its sources, runs the competency-question regression, the test files and the page check. It passes from a Git clone and from a plain folder. `bash scripts/check-pinned.sh` is separate and optional: it asks whether your copy still equals this release as shipped, and after your first change its failures mean only that your copy has moved on. Both scripts' headers say more.

## Rebuild, load and query

- **Rebuild a module:** each module's source has its own builder in its folder, and `scripts/check.sh` lists them all. For `lane`, from `business_architecture/ontology/lane/`, `uv run --no-project --with rdflib --with pyshacl python3 -B build_lanes.py --verify`; for `kpi`, `build_measures.py`. `release/build_module.py <module> --verify` checks the package. Add `--write` only with a new version: `HOW-TO-UPDATE.md` says how.
- **Project into Neo4j:** `business_architecture/ontology/projection/README.md`, and `projection/ontology-stores-runbook.html` for every store, hands on.
- **Connect and load every store:** `business_architecture/ontology/epm-walkthrough.html#connect`, the walkthrough's section of that name.
- **Ask a competency question:** from `business_architecture/ontology/regression/`, `uv run --no-project --with rdflib python3 -B ask.py <question-id>`, and `../competency-questions.md` for the list.
- **Run the pricing demo:** `demos/downstream-pricing-databricks-free/README.md`.
- **Add a module, or change anything else:** `HOW-TO-UPDATE.md`.

## Names, namespaces and terms

- The ontology's IRIs begin with `https://w3id.org/mpc/ontology/`. They identify terms and resolve nowhere. They are not issued by Marathon Petroleum, and nothing here is Marathon's own or endorsed by it. The namespaces will be reviewed and approved by the Data, Analytics and Insight team; until then they are working names.
- In the Neo4j graphs every label, relationship type and property is `prefix_name`, with one underscore (`skos_prefLabel`, `vs_Stage`).
- "Decision owner" in the documents and the sources means the subject matter expert who reviewed the documents and recorded each decision. Every decision in this release is theirs. Quotes attributed to "a subject matter expert reviewing the documents" are their words. For your own changes, your ontology owner holds this role.
- Peers are named only in market news: the pricing demo's cached search results (`demos/downstream-pricing-databricks-free/data/parallel/`) and the scenario's briefings (`demos/downstream-pricing-databricks-free/SCENARIO.md`). Every other claim that rests on peers reads as the industry view: "Industry standard, and analysis of publicly available filings from peers (U.S. refiners)".

## Licences and sources

The APQC Process Classification Framework for Downstream Petroleum is used with attribution under the APQC/IBM licence; its notice is in `business_architecture/reference/README.md` and travels with every copy. EIA data is a U.S. federal government work. Every other fact cites its source where it is used.

## Who to ask

Contact: (to be filled in by whoever shares this release).
