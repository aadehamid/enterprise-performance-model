# Property-graph projection (Step 12)

Projects the ontology into a Neo4j labelled property graph, following the guideline in `../lpg-projection/` (v2.2) with Rule 4a, qualified-relation nodes. *2026-10-23:* the guideline moved into the `ontology-to-lpg` skill in personal-agent-skills, version 2.3, and `../lpg-projection/` keeps the v2.2 copy as superseded evidence; this pipeline stays on v2.2, as the skill allows for a project pinned to an earlier version (EPM-DEC-001-0095). Turtle stays the master copy; the graph can be rebuilt from it at any time. The design is EPM-DEC-001-0036. Since 2026-10-22 it projects every released package under `../releases/`, each at its newest version, with each package's own shapes (EPM-DEC-001-0036, amendment of 2026-10-22).

| File | What it is |
|---|---|
| `pipeline.py` | The five steps: `build` (check the rules, validate, serialise), `reason` (ELK through ROBOT), `load-verify` (load with n10s, then SHACL in the graph, round trip, determinism) |
| `inferred.nt` | The reasoner's inferences about the domain (empty today: the ontology is SKOS-first) |
| `projection-manifest.json` | Input and shape hashes, triple counts, the input fingerprint, the pinned versions, the listed release gaps (none from core 2.0.0 to 2026-10-21; since 2026-10-22, 16 in value-stream, kpi, party and integration, each with its fix; *2026-10-23:* 14, in kpi, party and integration, since `value-stream` 1.1.0 closed two, EPM-DEC-001-0090; then 6, in kpi and integration, since `party` 1.1.0 closed eight, EPM-DEC-001-0092; then 5, in integration, since `kpi` 1.1.1 closed one, EPM-DEC-001-0093; none since `integration` 2.0.0, EPM-DEC-001-0094) |
| `projection-report.json` | The last Step 5 result for the fingerprint it names |
| `run_local.sh` | Steps 4 to 7 below in one command; `--keep` leaves the Neo4j container running |
| `LOCAL-STORES.md` | The stores kept loaded for exploration since 2026-10-26 (*2026-10-27:* the four ontology stores are empty since that day's purge and are reloaded at the start of Part 2; *2026-10-28:* reloaded, from that day's releases with `kpi` 1.3.0), how to refresh each, and where its login lives |
| `ontology-stores-runbook.html` | A standalone page for a person: the end-to-end workflow with diagrams, and how to check, stop, start, purge and reload each store |
| `test_pipeline.py` | The rule checks, the build, the round-trip comparison rules, that the report is current and passed, and (since 2026-10-29) that the counts, the hash and the round trip read only `:Resource` nodes and the edges between them |

`scripts/check.sh` runs `pipeline.py build --verify` and the tests. Step 2 needs Java, and Steps 4 and 5 need a Neo4j container in Docker, so they run on a workstation, not in CI.

## Rerun the whole pipeline

Rerun it after any input or shape changes. `run_local.sh` runs steps 4 to 7 in one command once steps 1 to 3 are done. You need Java 11 or later ([ROBOT's Getting Started](https://robot.obolibrary.org/): "make sure you have Java 11 or later installed"), Docker, and [uv](https://docs.astral.sh/uv/). Run the commands from this folder.

1. Make two empty folders outside the repo: one for the Neo4j plugins and one for the import files.

   ```bash
   PLUGINS=~/epm-lpg/plugins; IMPORT=~/epm-lpg/import; mkdir -p "$PLUGINS" "$IMPORT"
   ```

2. Download the pinned n10s (neosemantics) plugin into the plugins folder, and check its SHA-256. The jar comes from the [neosemantics 2025.06.1 release](https://github.com/neo4j-labs/neosemantics/releases/tag/2025.06.1), the version built for Neo4j 2025.06. If the checksum differs, stop: the file is not the one the last run used.

   ```bash
   curl -L -o "$PLUGINS/neosemantics-2025.06.1.jar" \
     https://github.com/neo4j-labs/neosemantics/releases/download/2025.06.1/neosemantics-2025.06.1.jar
   shasum -a 256 "$PLUGINS/neosemantics-2025.06.1.jar"
   # expect 4c461087e08405c7cb472ecfefc043e9e8ed93628ed74988e4fda1f1bac54b3e
   ```

3. Download ROBOT 1.9.10 (it runs the ELK reasoner), and check its SHA-256.

   ```bash
   ROBOT=~/epm-lpg/robot.jar
   curl -L -o "$ROBOT" https://github.com/ontodev/robot/releases/download/v1.9.10/robot.jar
   shasum -a 256 "$ROBOT"
   # expect 16a73c074f3df359a7338a84b4e0788785fe06117f931bb9796e9619ea776105
   ```

4. Reason. This rewrites `inferred.nt`, the reasoner's inferences, which the repo keeps.

   ```bash
   uv run --with rdflib --with pyshacl python pipeline.py reason --robot "$ROBOT"
   ```

5. Start Neo4j 2025.06.2 with the plugins folder mounted. The image downloads APOC itself (`NEO4J_PLUGINS`), and n10s loads from the mounted jar. Wait until `docker logs epm-lpg` prints `Started.`

   ```bash
   docker run -d --name epm-lpg -p 17687:7687 -e NEO4J_AUTH=neo4j/<password> -e NEO4J_PLUGINS='["apoc"]' \
     -e NEO4J_dbms_security_procedures_unrestricted='apoc.*,n10s.*' \
     -v "$IMPORT":/import -v "$PLUGINS":/plugins neo4j:2025.06.2
   ```

6. Load and verify. This step checks the rules and the shapes, writes the N-Triples and the in-graph shapes into the import folder, loads them, runs the three checks, and writes `projection-report.json`.

   ```bash
   uv run --with rdflib --with pyshacl --with neo4j python pipeline.py load-verify \
     --bolt bolt://localhost:17687 --password <password> --import-dir "$IMPORT"
   ```

7. Rewrite the manifest (`projection-manifest.json`), then remove the container. Commit `inferred.nt`, the manifest and the report together. The downloads stay in `~/epm-lpg/`, outside the repo.

   ```bash
   uv run --with rdflib --with pyshacl python pipeline.py build
   docker rm -f epm-lpg
   ```

The last run, on every released package with `kpi` 1.3.0 (2026-10-28): 4,193 nodes and 21,767 relationships from 36,951 triples, no SHACL violation in the graph over 766 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed (EPM-DEC-001-0109). *Earlier:* with `party` 2.1.0 and `integration` 2.5.0 (2026-10-28): 4,192 nodes and 21,767 relationships from 36,918 triples, no SHACL violation in the graph over 766 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed (EPM-DEC-001-0099, amendment of 2026-10-28). *Earlier:* with `organization` 2.2.0 (2026-10-28): 4,188 nodes and 21,758 relationships from 36,902 triples, no SHACL violation in the graph over 766 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed (EPM-DEC-001-0045, amendment of 2026-10-28). *Earlier:* with `ref-mpc` 1.3.0 (2026-10-27): 4,187 nodes and 21,758 relationships from 36,901 triples, no SHACL violation in the graph over 766 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed; the three brands are `party__Brand` nodes (EPM-DEC-001-0108, amendment of 2026-10-27). *Earlier:* with `party` 2.0.0, `system` 1.5.0 and `integration` 2.4.0 (2026-10-27): 4,186 nodes and 21,749 relationships from 36,883 triples, no SHACL violation in the graph over 758 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed (EPM-DEC-001-0108); with `system` 1.4.0 and `party` 1.4.0 (2026-10-26): 4,146 nodes and 21,503 relationships from 36,473 triples, no SHACL violation in the graph over 754 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed (EPM-DEC-001-0104). *Earlier:* with `core` 2.4.0 (2026-10-26): 4,137 nodes and 21,419 relationships from 36,363 triples, no SHACL violation in the graph over 754 in-graph constraints, the deliberate mutant still caught, an empty round-trip diff, equal hashes for the sorted and shuffled loads, and no release gap listed (EPM-DEC-001-0105); its 102 new relationships are the code lists' top-concept links. *Earlier:* with `lane` 1.1.0, `organization` 2.1.0 and `value-stream` 1.2.0 (2026-10-26): 4,137 nodes and 21,317 relationships from 36,207 triples, no SHACL violation in the graph over 754 in-graph constraints, every check passing, and no release gap listed; the 22 new relationships are the top-concept statements, both ways (EPM-DEC-001-0106). *Earlier:* with `system` 1.3.0, `party` 1.3.0 and `integration` 2.3.0 (2026-10-26): 4,137 nodes and 21,295 relationships from 36,185 triples, no SHACL violation in the graph over 754 in-graph constraints, every check passing, and no release gap listed (EPM-DEC-001-0103). *Earlier:* with item F's releases (`kpi` 1.2.0, `market-data` 1.1.0, `data-product` 1.2.0, `system` 1.2.0, `integration` 2.2.0; 2026-10-26): 4,135 nodes and 21,256 relationships from 36,090 triples, no SHACL violation in the graph over 754 in-graph constraints, every check passing, and no release gap listed (EPM-DEC-001-0100). *Earlier:* with `system` 1.1.0, `party` 1.2.0 and `integration` 2.1.0 (2026-10-25): 3,998 nodes and 20,223 relationships from 34,495 triples, no SHACL violation in the graph, every check passing as below, and no release gap listed (EPM-DEC-001-0099). *Earlier:* with `integration` 2.0.0 (2026-10-23): 3,971 nodes and 19,843 relationships from 34,058 triples, every check passing as below, and no release gap listed (EPM-DEC-001-0094). *Earlier:* with `kpi` 1.1.1 (2026-10-23): 3,972 nodes and 19,841 relationships from 34,055 triples, every check passing as below; kpi 1.1.1 closes one release gap (EPM-DEC-001-0093). *Earlier:* with `party` 1.1.0 (2026-10-23): 3,971 nodes and 19,840 relationships from 34,054 triples, no SHACL violation in the graph over 602 in-graph constraints, every other check passing; party 1.1.0 closes eight release gaps and adds the `oeo` prefix for its product mappings (EPM-DEC-001-0092). *Earlier:* with `data-product` 1.1.0 (2026-10-23): 3,930 nodes and 19,705 relationships from 33,766 triples, every check passing as below (EPM-DEC-001-0091). *Earlier:* with `value-stream` 1.1.0 (2026-10-23): 3,928 nodes and 19,698 relationships from 33,754 triples, every check passing; value-stream 1.1.0 closes two release gaps (EPM-DEC-001-0090). *Earlier:* with `core` 2.3.0 (2026-10-23): 3,927 nodes and 19,695 relationships from 33,751 triples, no SHACL violation in the graph (588 in-graph constraints, and the deliberate mutant still caught), an empty round-trip diff, and equal hashes for the sorted and shuffled loads. core 2.3.0 adds one process concept (EPM-DEC-001-0089). *Earlier:* on every released package (2026-10-22): 3,925 nodes and 19,692 relationships from 33,742 triples, no SHACL violation in the graph (588 in-graph constraints, and the deliberate mutant still caught), an empty round-trip diff, and equal hashes for the sorted and shuffled loads. `sh:pattern`, and an `sh:in` list of literals, are left to Step 1's pySHACL check, since n10s matches a pattern against the whole string. *Earlier:* on core 2.2.0 with organization 2.0.0 (2026-10-22): 2,834 nodes and 14,934 relationships, no SHACL violation in the graph (133 in-graph constraints, and the deliberate mutant still caught), an empty round-trip diff, and equal hashes for the sorted and shuffled loads. core 2.2.0 adds 23 process concepts and IDs on four stubs (EPM-DEC-001-0076). *Earlier:* The last run, on core 2.1.0 with organization 2.0.0 (2026-10-19): 2,811 nodes and 14,865 relationships (organization 2.0.0 adds the three `dcterms:isReplacedBy` links of its deprecated roles), no SHACL violation in the graph, an empty round-trip diff, and equal hashes for the sorted and shuffled loads.

*2026-10-29:* the pricing demo's technical graph and decision trail (E5) share this store, the driver's and AuraDB: 134 nodes labelled `Tech`, never `Resource`, with edges only from them to other `Tech` nodes or to ontology nodes. `graph_hash`, the counts and the round trip read only `:Resource` nodes and the edges between them, so they do not move: `graph_hash` gave the same value, 4,193 nodes and 21,767 relationships, before and after the demo loaded its graph here, and `test_pipeline.py` pins that every query but the load's wipe names the label. The wipe removes the `Tech` nodes too, so `run_local.sh` leaves them out until the demo's `tech_graph load` runs again (`demos/downstream-pricing-databricks-free/README.md`).
