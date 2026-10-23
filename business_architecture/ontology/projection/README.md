# Property-graph projection (Step 12)

Projects the ontology into a Neo4j labelled property graph, following the guideline in `../lpg-projection/` (v2.2) with Rule 4a, qualified-relation nodes. Turtle stays the master copy; the graph can be rebuilt from it at any time. The design is EPM-DEC-001-0036. Since 2026-10-22 it projects every released package under `../releases/`, each at its newest version, with each package's own shapes (EPM-DEC-001-0036, amendment of 2026-10-22).

| File | What it is |
|---|---|
| `pipeline.py` | The five steps: `build` (check the rules, validate, serialise), `reason` (ELK through ROBOT), `load-verify` (load with n10s, then SHACL in the graph, round trip, determinism) |
| `inferred.nt` | The reasoner's inferences about the domain (empty today: the ontology is SKOS-first) |
| `projection-manifest.json` | Input and shape hashes, triple counts, the input fingerprint, the pinned versions, the listed release gaps (none from core 2.0.0 to 2026-10-21; since 2026-10-22, 16 in value-stream, kpi, party and integration, each with its fix) |
| `projection-report.json` | The last Step 5 result for the fingerprint it names |
| `test_pipeline.py` | The rule checks, the build, the round-trip comparison rules, and that the report is current and passed |

`scripts/check.sh` runs `pipeline.py build --verify` and the tests. Step 2 needs Java, and Steps 4 and 5 need a Neo4j container in Docker, so they run on a workstation, not in CI.

## Rerun the whole pipeline

Rerun it after any input or shape changes. You need Java 11 or later ([ROBOT's Getting Started](https://robot.obolibrary.org/): "make sure you have Java 11 or later installed"), Docker, and [uv](https://docs.astral.sh/uv/). Run the commands from this folder.

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

The last run, on every released package (2026-10-22): 3,925 nodes and 19,692 relationships from 33,742 triples, no SHACL violation in the graph (588 in-graph constraints, and the deliberate mutant still caught), an empty round-trip diff, and equal hashes for the sorted and shuffled loads. `sh:pattern`, and an `sh:in` list of literals, are left to Step 1's pySHACL check, since n10s matches a pattern against the whole string. *Earlier:* on core 2.2.0 with organization 2.0.0 (2026-10-22): 2,834 nodes and 14,934 relationships, no SHACL violation in the graph (133 in-graph constraints, and the deliberate mutant still caught), an empty round-trip diff, and equal hashes for the sorted and shuffled loads. core 2.2.0 adds 23 process concepts and IDs on four stubs (EPM-DEC-001-0076). *Earlier:* The last run, on core 2.1.0 with organization 2.0.0 (2026-10-19): 2,811 nodes and 14,865 relationships (organization 2.0.0 adds the three `dcterms:isReplacedBy` links of its deprecated roles), no SHACL violation in the graph, an empty round-trip diff, and equal hashes for the sorted and shuffled loads.
