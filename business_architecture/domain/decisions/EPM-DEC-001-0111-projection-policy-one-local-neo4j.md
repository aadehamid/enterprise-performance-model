# EPM-DEC-001-0111: What each store holds of a module: all three graphs in Jena and Delta, all content and one release record in Neo4j and Aura, with one local Neo4j and a standing Jena

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-11-01, for the policy, the release record and the one local Neo4j plus Jena; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-11-01 |
| Questions | Claude asked the decision owner three questions about the projection from Turtle to the property graph: one release record per module; keep all module content in Neo4j; one standard store form |
| Source | Claude Code session of 2026-11-01; `answers-2026-11-01-projection.md`, blocks 1 to 5 |

## Context

Each module package holds three graphs: `<module>.ttl` (the content), `shapes.ttl` (the rules) and `catalog.ttl` (the DCAT release record). Two local Neo4j stores held different forms of the same releases: `epm-lpg` from `pipeline.py` (guideline v2.2, no schema nodes, no `graph` property, 21,767 relationships) and `lpg-local` from the `ontology-to-lpg` skill's driver (v2.3, `n4sch__` schema nodes and a `graph` property giving the version IRI, 22,142 relationships). A third, Jena, had no standing form: the driver's Fuseki was removed after each run, and one had been started by hand.

## Decision

**The decision owner's decisions:**

1. **Triple stores and Delta hold everything:** "Triple stres and delta tables hold all three graphs for each module fully". Jena and `epm_triples` keep `<module>.ttl`, `shapes.ttl` and `catalog.ttl` in full.
2. **One release record per module in Neo4j:** to the question of one release record per module, "1. yes". A release's catalog metadata is not projected in full.
3. **All module content in Neo4j:** to the question of keeping all module content in Neo4j, "I will follow your recommendation". All of `<module>.ttl` is projected, with no selective projection, so the round trip keeps proving 0 lost and 0 added. Shapes validate the release (pySHACL before the load, n10s in the graph at the load) and are not projected as nodes.
4. **One local Neo4j and Jena, and Aura the same:** "there should be a local Neo4j and Jena. This same approach should apply to Aura as well."
5. **The documents say so:** "Let us add these details in the documents, guide, wlakthtough and so on of the release."
6. **The walkthrough gives colleagues all they need to connect:** "I want my colleagues to be able to take the walk through and create the same thing we have in QA/Prod enviroment following the walkthrough without missing any information." It covers "URL, keys, personal token, and so on", and "the path ot the scripts used for all of this must also be provided, including the validation scripts etc."
7. **The technical graph and the link to Databricks get the same detail:** the build "must alos have the same detailed information", and a section describes how Databricks objects are linked "to the ontology and how the ontology contextualize the objects in Databricks."
8. **The technical graph goes in Jena, and one plan keeps every store in step:** "Should Jena also load the update tech graph since the original ontology have changed", with "a clear plan on what that should look like in the walkthrough".
9. **Fully automated:** "We should be able to describe what we did in a way that is reproducible by anyone or an agent. It must be automated fully for this to scale".
10. **The lineage refreshes with the release:** "Let us refresh the linege once we relases the cust and uploda the fresh data."

**Delegated under EPM-DEC-001-0028**, with reasons:

11. **The driver's form is the standard, and the driver is the one loader.** It carries the checks the older loader lacks (every compiled shape tested, the module tags, the rebuild from a store), and Aura already copies it. `pipeline.py load-verify`, `pipeline.py reason` and `run_local.sh` go, so no second form can come back.
12. **`pipeline.py` keeps `build` and the input lists, and gains `record`.** `build --verify` runs the rule checks and the shapes in CI, which has neither Docker nor Java, and `skill-run/inputs.py` reads its lists. `record --run <driver out>` takes a driver run's `inferred.nt` and a summary of its report into the repository, refusing a run that read other inputs or did not pass. The committed `projection-report.json` stays small: the driver's full report runs to some 800 KB.
13. **The committed figures are now the driver's:** `epm_facts.py projection` prints them. The 21,767 stays only where a dated record says what the older loader held. The reasoner's two inferences join `inferred.nt`, because the driver reasons with `--include-indirect`, where the older loader found none.
14. **The release record:** one node labelled `ModuleRelease` per module, in the skill as `release_record.py`, with a `DESCRIBES` link to the module's `owl:Ontology` node. Like `EpmStoreMarker` it has no `Resource` label, and the link starts outside `Resource`, so the hash, the counts, the tags and the round trip read neither; the script stops if the hash moves. Its load time enters no hash.
15. **Jena stands and has no marker.** The run configuration's `keep_jena` leaves the Fuseki of the `jena` step running, on the port and project the hand-started one used. Its named graphs are version IRIs, so the drift check compares its graph names and each graph's triple count with the release files. That needs nothing written beside the release graphs for the drift check's sake.
16. **Jena stays in memory.** A restart empties it, and the drift check then reads `empty`; `sync_stores.py sync` reloads it with the driver's `jena` step alone. A persistent dataset would be a second store form to prove, for a store rebuilt in about a minute.
17. **The duplicate labels stay, documented.** A class is one node with both `owl__Class` (from its own triple) and `n4sch__Class` (from n10s's ontology import). Dropping either touches the round trip or the schema relationships the skill's checks read, so it is not simple, and the guide explains them instead.

18. **Another environment needs no code change.** A copy of the run configuration names its stores, ports and login files, and `EPM_STORES_JSON` points `sync_stores.py` and `tech_graph.py` at them, now with the run configuration, the output folder and the triple table's name too. What stays fixed in the demo is stated on the page.

19. **One command, one environment file.** `rebuild_stores.py --env <file>` runs preflight, empty, load, record, the demo's build, `collect`, the technical graph's build, its structure check, the lineage check, its load, the Delta copy, mark and check, and stops at the first failure with the step named. It has no prompt, it takes every name and login from the file, and `--store` chooses the targets. It writes a report and a log per step. It refuses a store that holds data without `--empty`. `empty_stores.py` drops only this tool's two tables in Databricks, so the demo's and anyone else's in the schema stay. *2026-11-02, delegated under EPM-DEC-001-0028:* with AuraDB and Databricks both chosen, an `aura-test` step runs `pricing_demo.aura_test` before `collect`, with the AuraDB login file the environment file names (`EPM_AURA_ENV`), because the shipped technical graph holds the check `databricks-reaches-auradb` that `collect` records only from that probe's result; without it the structure check failed on a fresh copy.
20. **The technical graph in Jena is two named graphs beside the release's.** Their names keep them out of the release's comparison, and the drift check judges them against their files. `epm_triples` does not take them: the decision owner's call on the planned module is still open.
21. **A refresh writes outside what ships.** `build` writes `out/tech/graph/`, which Git ignores, and `load` prefers it. `compare` leaves out a named list of volatile values and the host and fails on any other difference from `graph/*.ttl`, so row counts and refresh times may move and objects, edges and stable values may not. `build --to-repo` is the deliberate way to change what ships.
22. **The expected lineage differences are written down.** `graph/lineage-known.json` holds the 5 designed-only edges and the 9 that touch tables the demo does not build, derived from the release's design against the demo's SQL. `tech_graph lineage` fails on anything else. `collect --lineage-wait` reads Unity Catalog again while a built table has no event yet, so a lag does not read as a difference, for a bounded time.
23. **A dangling edge stays a failure.** `tech_graph load` stops when an edge's ontology target is missing, in Neo4j, AuraDB and Jena.

## Alternatives considered

- **Project only part of a module.** Rejected: the round trip's proof depends on the whole file.
- **Keep the older loader beside the driver as a check.** Rejected: two forms give two sets of figures, which is the confusion this decision removes.
- **Remove `pipeline.py` entirely.** Rejected: CI would lose the rule check and the shapes check on the release set, and the skills are not in this repository's tree.

## The decision owner's recorded words

> This only affects projection from turttle to lpg in Neo4j. Triple stres and delta tables hold all three graphs for each module fully

> 1. Should Jena also load the update tech graph since the original ontology have changed. This tie back to keeping the ontology in sync everywher they are used once a change happen. This will be crucial going forward and we have to have a clear plan on what that should look like in the walkthrough 2. We should be able to describe what we did in a way that is reproducible by anyone or an agent. It must be automated fully for this to scale 3. Let us refresh the linege once we relases the cust and uploda the fresh data.

> Also the how to create technical graph from databricks as source and its projection to ontology and dusbsequent projection to Neo4J /Aura must alos have the same detailed information. There should aslo be a section that deribes the link between Databricks objects such as Metric View, its mesaure/metrics/KPI, the underlyitng tables and its lineage is linked to the ontology and how the ontology contextualize the objects in Databricks.

> In the walkthrough, please, can you add a session on what is needed to be able to project to either Neo4j , Aura, and Databricks. This must include any required information that is needed such as URL, keys, personal token, and so on to be able to make the connection. I want my colleagues to be able to take the walk through and create the same thing we have in QA/Prod enviroment following the walkthrough without missing any information. It should be straight forward. This means the path ot the scripts used for all of this must also be provided, including the validation scripts etc.

> 1. yes 2. I will follow your recommendation 3. there should be one local store. why did we have two? Are we referring to jena and local neo4j? there should be a local Neo4j and Jena. This same approach should apply to Aura as well. basically projection from tripples to lpg should follow the approach here. I am aligned with your other recommendations. Let us add these details in the documents, guide, wlakthtough and so on of the release.

## Evidence

- `python3 scripts/epm_facts.py find "21,767"`, before this change: 16 hits.
- A driver run on main at `769345e0`, on test containers: 4,193 nodes and 22,142 relationships, of which 373 schema relationships and 2 from the reasoner's inferences, leaving the older count of 21,767; 762 in-graph constraints; 0 lost and 0 added; equal hashes; a rebuild from Jena with equal hashes.
- personal-agent-skills' `ontology-to-lpg`, `references/multi-store.md`, "What each store holds"; `references/add-ons.md`, add-on M.

## Consequences

- The stores change at the next reload, from the next release: it empties and removes `epm-lpg`, reloads the local Neo4j, Jena, Aura and Databricks, writes the release records and marks the stores. Until then the running stores read as behind.
- `sync_stores.py` and `tech_graph.py` no longer know a `pipeline` store.
- This supersedes EPM-DEC-001-0095's item 5, which kept `pipeline.py` on v2.2 as the committed pipeline, for the load and the reasoner. It amends EPM-DEC-001-0036's loader.
