# What each store holds now

This page lists what each store held when it was last audited, what should not be in it, and the commands to check it yourself. `LOCAL-STORES.md` says where each store lives and how to refresh it, and `../../../demos/downstream-pricing-databricks-free/DATA.md` says how the demo's tables are generated. This page answers a different question: is the data in each store the latest, and is anything old left beside it?

**Last audit: 2026-10-29, at main `0b5d6051`.** It was read-only: nothing was changed or deleted. `sync_stores.py check` read all four ontology stores as current, each marked at 2026-10-29T14:23:14Z from the release set at commit `4d1e675b`.

## Local Neo4j, from the pipeline (container `epm-lpg`)

| What | Count | Where it comes from |
|---|---|---|
| Nodes labelled `Resource` (the ontology) | 4,193 | `pipeline.py`, on every released package |
| Relationships between `Resource` nodes | 21,767 | The same load |
| Nodes labelled `Tech` (the technical graph and decision trail) | 142, each with its own `uri` | `pricing_demo.tech_graph load` |
| `EpmStoreMarker` | 1 (`store: pipeline`) | `sync_stores.py mark` |
| n10s configuration nodes (`_GraphConfig`, `_NsPrefDef`, `_n10sValidatorConfig`) | 1 each | The n10s load |
| All nodes, all relationships | 4,339, 22,307 | |

Should not be there: nodes from an earlier release beside the current ones, a second copy of the Tech graph (two `Tech` nodes with the same `uri`), or any label not listed above.

## Local Neo4j, from the driver (container `lpg-local-neo4j-1`)

| What | Count | Where it comes from |
|---|---|---|
| Nodes labelled `Resource` | 4,193 | The driver's `rebuild` step, from `epm_triples` |
| Relationships between `Resource` nodes | 22,142 | The same load; the driver counts more relationships than the pipeline from the same releases (see `ontology-stores-runbook.html`, Stores) |
| Nodes labelled `Tech` | 142, each with its own `uri` | `pricing_demo.tech_graph load` |
| Nodes labelled `Module` | 11 | The driver's module tags |
| `EpmStoreMarker` | 1 (`store: driver`) | `sync_stores.py mark` |
| n10s configuration nodes | 1 each | The n10s load |
| All nodes, all relationships | 4,350, 22,706 | |

## Neo4j AuraDB

AuraDB holds a copy of the driver's graph, in one database. Its counts match the driver's, without the n10s configuration nodes:

- 4,193 `Resource` nodes, with 22,142 relationships between them;
- 142 `Tech` nodes, each with its own `uri`;
- 11 `Module` nodes;
- one `EpmStoreMarker` (`store: aura`);
- 4,347 nodes and 22,706 relationships in all.

## Local Postgres (container `pricing-demo-sources`) and the exe.dev VM

Both hold the same eight databases, with the same tables and row counts. These match `DATA.md`:

| Database | Tables (rows) |
|---|---|
| `price_assessment` | `mips_priceassessment` (266,288), `mips_pricebatch` (748), `mips_priceassessmentgroup` (188), `mips_pricegroup` (66), `mips_pricesheet` (7), `mips_unitofmeasure` (6), `mips_currency` (1) |
| `price_reference` | `pricedetail` (599,148), `pricemaster` (132) |
| `reference_data_hub` | `external_citation` (1,360), `external_event` (344), `forward_scan` (45), `holidaycalendar` (30), `market_event` (9), `deliveryperiodcategory` (3), `priceservice` (2) |
| `rightangle` | `deal` (2,673), `movement` (2,673), `freight_rate` (1,496) |
| `aspen_pims` | `plan_target` (481), `plan_version` (455), `decision_evidence` (22), `decision_log` (10) |
| `production_accounting` | `unit_daily` (76,296), `refinery_daily` (9,724), `refinery` (13) |
| `eia_weekly` | `weekly_value` (8,792), `series` (28) |
| `decision_truth` | `decision_dossier` (10); hidden, never replicated |

Should not be there: databases under the source names used before 2026-10-28. None was found.

**Databases on the VM that the demo did not create.** The VM's Postgres also holds two databases owned by other logins, which the demo never reads: "Enterprise Performance Model" (owner `epm_owner`, no tables) and `exedev` (no tables; the default database of the VM's own `exedev` login, so `psql` for that login connects to it). Both are kept at the decision owner's choice. A third, `sales` (a small sample schema owned by `sales`), was dropped on 2026-10-29 at the decision owner's word (`../step4/review-evidence/decision-owner-answers/answers-2026-10-29-store-cleanup.md`).


## Docker on this Mac

Three containers are in use: `epm-lpg`, `lpg-local-neo4j-1` and `pricing-demo-sources`, each with its data volume. `lpg-local-n10s-jar-1` is stopped, as it should be: at the driver's start it downloads the n10s plugin into the plugins folder and checks its checksum. The images `lpg-fuseki:6.2.0` and `rdf-store-fuseki:6.2.0` serve the driver's transient Jena store, whose container is removed after each run; a driver run rebuilds them if they are missing.

Should not be there: an unnamed volume attached to no container, or a container no store uses. On 2026-10-29, at the decision owner's word (the same answers file), 14 such volumes (about 3.8 GB, the data of Neo4j containers that later runs replaced, and their log volumes) and two unused containers (`practical_edison`, Docker's tutorial, and `pgadmin4_container`, never started) were removed. To check that none has come back:

```bash
docker volume ls -q --filter dangling=true                    # should print nothing
docker ps -a --format '{{.Names}} {{.Status}}'                # the three stores and lpg-local-n10s-jar-1
```

## Check it yourself

From this folder, with the logins `LOCAL-STORES.md` names:

```bash
uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with databricks-sql-connector python sync_stores.py check
```

Each Neo4j store: the counts above (the pipeline store shown; for the driver, use `lpg-local-neo4j-1` and its `run.env` as `ontology-stores-runbook.html`, Check, says):

```bash
set -a; . ~/epm-lpg/run.env; set +a
docker exec -e NEO4J_PASSWORD epm-lpg cypher-shell -u neo4j \
  "MATCH (n) UNWIND labels(n) AS l RETURN l, count(*) ORDER BY count(*) DESC; MATCH (t:Tech) RETURN count(t), count(DISTINCT t.uri);"
```

Postgres: the row-count loop in `ontology-stores-runbook.html`, Check. Databricks: `uv run python -m pricing_demo.databricks counts` from the demo's folder.
