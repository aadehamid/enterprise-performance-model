# Store tests, steps 3 to 5, run on 2026-10-25

The record of the store tests on the released ontology: the projection into local Neo4j (step 3), the copy to Aura (step 4), and both rebuilt from the Databricks copy (step 5), each checked for no data loss, with every node tagged by its module and walked across modules in Neo4j and in Jena. Steps 2a and 2b, the round trips through Jena Fuseki and the Databricks Delta table, ran earlier the same night with the `rdf-store` skill (personal-agent-skills #55). The scripts are in this folder (README.md); the skill's add-on F (`module_tags.py`, `explore.py`, `queries/`) is personal-agent-skills #65.

Inputs: the newest release of each of the 11 modules (`inputs.py data`), 34,058 triples, and the 13 shape files (`inputs.py shapes`). Tools: Neo4j 2025.06.2 with the skill's pinned n10s, ROBOT 1.9.10 (ELK), Jena Fuseki 6.2.0, Aura Free, Databricks Free Edition (one serverless SQL warehouse).

## Step 3: local Neo4j

| Check | Result |
|---|---|
| `run.sh` (rules, SHACL, reasoning, serialisation, manifest) | passed; `loadable.nt` 34,058 triples, `inferred.nt` 2 |
| `load.sh` (`load_verify.py`, then `build.py check-report`) | passed: 598 compiled shape rows, 0 violations in the graph, 1 on the mutant, round trip 0 lost and 0 added, sorted and shuffled loads both hash `5929fa670a00755d1578df27119afbd4fa48ff50ebeec2e7681520f00ed177bb`; 3,971 nodes, 20,176 relationships |
| `tags.sh` (`module_tags.py tag`, `check`, `modules`) | every node and relationship carries exactly one module tag, equal to its package; 19,845 distinct triples plus the 331 n10s schema relationships (`n4sch__DOMAIN`, `RANGE`, `SCO`), which repeat `rdfs:` triples |
| The module graph against the release manifests | 11 modules, 21 requirements; 7 pins name an older release than the one loaded: lane and system pin core 2.2.0, organization pins core 2.1.0, market-data pins kpi 1.0.1, ref-mpc pins party 1.0.0, value-stream pins data-product 1.0.0 and kpi 1.1.0 |
| `model_review.py` | 0 errors, 34 warnings, all supernode candidates: code-list values, sources and RACI levels kept as nodes on purpose; no node near the 100,000-relationship limit |

Before the tags, the projection already held each package's `owl:Ontology` header node and its `dcterms:requires` links, but those point at bare version-IRI nodes, not at the loaded modules; the `:Module` graph joins them.

## Step 4: Aura

`copy_graph.py` copied 3,971 nodes and 20,176 relationships in 11 seconds. The target's hash equalled the source's and the report's (`5929fa67…`): the module tags are left out of the hash, so the tagged graph still matched the report, and the tags travelled with the copy. `tags.sh --env` then passed on Aura: every tag correct, and the module graph rebuilt there (11 modules, 21 requirements).

## The walk across modules, Neo4j against Jena

`explore.sh` loads the inputs and `inferred.nt` into Jena (one named graph per package, hash-checked) and runs every walk in `queries.json` in both stores. Every walk below gave the same edges, nodes, predicates and module tags from Neo4j and from Jena, on the repository build (local and Aura) and again on the build from Databricks (local and Aura). The module map agreed too (21 rows each side).

| Walk | Hops | Edges | Nodes | Modules reached |
|---|---|---|---|---|
| process across modules (`CM-1-1-5-8`) | 2 | 2,327 | 1,398 | 10 |
| value stream end to end (Order to Cash) | 3 | 905 | 555 | 11 |
| measure back to its processes | 2 | 1,506 | 1,277 | 10 |
| a process (core) | 2 | 2,181 | 1,307 | 10 |
| a role (organization) | 2 | 1,114 | 1,049 | 5 |
| a measure (kpi) | 2 | 1,483 | 1,271 | 10 |
| a data product (data-product) | 2 | 1,517 | 1,253 | 10 |
| a value-stream step (value-stream) | 2 | 227 | 164 | 4 |
| a system (system) | 2 | 2,484 | 2,251 | 10 |
| a lane (lane) | 2 | 1,294 | 1,255 | 10 |
| a customer-lifecycle stage (party) | 2 | 1,384 | 1,282 | 10 |
| a market-data series (market-data) | 2 | 1,393 | 1,268 | 10 |
| an MPC fact (ref-mpc) | 2 | 135 | 91 | 5 |
| an integration rule (integration) | 2 | 32 | 25 | 3 |

Two hops from most nodes reach a class node such as `skos:Concept` and through it every node of that class, which is why many walks reach ten modules; the tags say where each edge came from. The paste-able forms in the skill's `queries/` (Neo4j Browser and Fuseki) returned the same 2,181 edges as `explore.py` for `CM-1-2-1`.

## Step 5: rebuilt from Databricks

The local Neo4j was removed (`docker compose down -v`) and every node on Aura deleted: 3,982 nodes (the 3,971 copied plus the 11 `:Module` nodes) and their relationships, all loaded by this run; Aura held nothing before it. `rebuild.sh` then:

1. exported the table `workspace.epm_ontology.epm_triples` (36,575 quads in 33 graphs: the 11 modules with their shapes and catalogs) in 19 seconds, and its RDFC-1.0 hash equalled the release files' (`7c46658b4ab99315487003ee8869f04809db07ac43ee50f3d399091b5b7b979b`);
2. took the projection's data and release shapes from that export; the two whole-graph shape files (`step4/scoped-sequence/shapes.ttl`, `provenance/run-shapes.ttl`) were never loaded into the table, so they came from the repository;
3. ran `run.sh` and `load.sh` on them: `loadable.nt` and `inferred.nt` held the same 34,058 and 2 triples as the repository build, and both load hashes equalled the repository build's (`5929fa67…`), so Neo4j held the same graph;
4. tagged, copied to Aura (target hash `5929fa67…`) and checked the tags there.

The rebuilt `loadable.nt` is not byte-identical to the repository build's: the Databricks export writes the 1,520 literals typed `xsd:string` as plain literals, which RDF 1.1 defines as the same term, and n10s stores them alike, as the equal graph hashes show. `rebuild.sh` therefore compares triples as RDF 1.1 terms and requires the graph hashes to match. Free Edition limits were not reached.

## What remains in the stores

- **Aura:** the projection rebuilt from Databricks (3,971 nodes, 20,176 relationships, tagged) and the module graph (11 `:Module`, 21 `REQUIRES`).
- **Databricks:** the table `workspace.epm_ontology.epm_triples` (36,575 rows), nothing else; every staging table was dropped.
- **Local:** no container is left running; Fuseki is removed after each `explore.sh`.
