# The EPM ontology and pricing demo, release EPM 1.0

This folder holds a business ontology for downstream oil and gas, the scripts that build and check it, the stores it is projected into, and a pricing demo that uses it. Everything here can be rebuilt and checked from this folder alone. It was prepared for colleagues who did not take part in the build, so nothing in it assumes you have seen it before.

Start with `business_architecture/ontology/epm-ontology-guide.html` in a browser. It explains what the ontology is for, why it is split into modules, what each module holds, and follows one pricing measure from the business to the stores. Then `business_architecture/ontology/epm-walkthrough.html` tells the whole story and, in its second part, rebuilds it step by step.

## What is here

| Folder | What it holds |
|---|---|
| `business_architecture/business_process/` | The process authority: the downstream process map, the two value streams, the office lanes and the data-product portfolio, as JSON, with their schemas and tests |
| `business_architecture/ontology/` | The ontology: each module's sources and builder, the released packages (`releases/`, the newest set, and `releases/previous/`, the release before each), the projection into Neo4j, the competency-question regression, the validation shapes, and the documents |
| `business_architecture/reference/` | The evidence behind the definitions: MPC's public filings, the industry view (analysis of publicly available filings from U.S. refining peers), the APQC framework, vendor descriptions |
| `business_architecture/domain/` | The business glossary, the data domains, the problem statement, and the decision packages |
| `demos/downstream-pricing-databricks-free/` | The pricing demo: synthetic pricing data in Databricks Free Edition, metric views bound to the ontology's measures, Genie agents, a technical graph and the acceptance tests |
| `skills/` | The four agent skills used to build this: `ontology` (the method), `ontology-to-lpg` (the projection into a property graph), `rdf-store` (triple stores) and `clear-writing` |
| `scripts/` | `check.sh`, the one command that runs every check; `epm_facts.py`, which reports figures from the sources; the page builder |
| `best-practices/` | General guides on production-ready ontologies and enterprise KPIs |
| `KNOWN-OPEN-ITEMS.md` | What is open, and what was not run on this release |

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

It verifies that every released package equals a fresh build from its sources, runs the competency-question regression, every test file, and the page check. The script's header says which four checks of the original build are not here and why.

## Rebuild, load and query

- **Rebuild a module:** from `business_architecture/ontology/`, `uv run --no-project --with rdflib --with pyshacl python3 -B <module>/build_<module>.py --write`, then `uv run --no-project --with rdflib --with pyshacl python3 -B release/build_module.py <module> --write`; `MODULES.md` and each module's README say what each holds. The builders read `release.json` at this folder's root and build against the newest package of each module.
- **Project into Neo4j:** `business_architecture/ontology/projection/README.md`, and `projection/ontology-stores-runbook.html` for every store, hands on.
- **Ask a competency question:** from `business_architecture/ontology/regression/`, `uv run --no-project --with rdflib python3 -B ask.py <question-id>`, and `../competency-questions.md` for the list.
- **Run the pricing demo:** `demos/downstream-pricing-databricks-free/README.md`.
- **Add a module:** `skills/ontology/references/new-module.md`, and the walkthrough's "How to change the ontology".

## Names, namespaces and terms

- The ontology's IRIs begin with `https://w3id.org/mpc/ontology/`. They identify terms and resolve nowhere. They are not issued by Marathon Petroleum, and nothing here is Marathon's own or endorsed by it. The namespaces will be reviewed and approved by the Data, Analytics and Insight team; until then they are working names.
- In the Neo4j graphs every label, relationship type and property is `prefix_name`, with one underscore (`skos_prefLabel`, `vs_Stage`).
- "Decision owner" in the documents and the sources means the subject matter expert who reviewed the documents and recorded each decision. Quotes attributed to "a subject matter expert reviewing the documents" are that person's words.
- Claims that rest on the industry view are presented as "Industry standard, and analysis of publicly available filings from peers (U.S. refiners)"; no peer is named.

## Licences and sources

The APQC Process Classification Framework for Downstream Petroleum is used with attribution under the APQC/IBM licence; its notice is in `business_architecture/reference/README.md` and travels with every copy. EIA data is a U.S. federal government work. Every other fact cites its source where it is used.

## Who to ask

Contact: (to be filled in by whoever shares this release).
