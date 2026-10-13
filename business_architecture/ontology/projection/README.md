# Property-graph projection (Step 12)

Projects the ontology into a Neo4j labelled property graph, following the guideline in `../lpg-projection/` (v2.1) with Rule 4a, qualified-relation nodes. Turtle stays the master copy; the graph can be rebuilt from it at any time. The design is EPM-DEC-001-0036.

| File | What it is |
|---|---|
| `pipeline.py` | The five steps: `build` (check the rules, validate, serialise), `reason` (ELK through ROBOT), `load-verify` (load with n10s, then SHACL in the graph, round trip, determinism) |
| `inferred.nt` | The reasoner's inferences about the domain (empty today: the ontology is SKOS-first) |
| `projection-manifest.json` | Input and shape hashes, triple counts, the input fingerprint, the pinned versions, the listed release gaps |
| `projection-report.json` | The last Step 5 result for the fingerprint it names |
| `test_pipeline.py` | The rule checks, the build, the round-trip comparison rules, and that the report is current and passed |

`scripts/check.sh` runs `pipeline.py build --verify` and the tests. To rerun the whole pipeline after an input changes:

```bash
python3 pipeline.py reason --robot robot.jar          # ROBOT 1.9.10
docker run -d --name epm-lpg -p 17687:7687 -e NEO4J_AUTH=neo4j/<password> -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_dbms_security_procedures_unrestricted='apoc.*,n10s.*' \
  -v <import dir>:/import -v <plugins dir with neosemantics-2025.06.1.jar>:/plugins neo4j:2025.06.2
python3 pipeline.py load-verify --bolt bolt://localhost:17687 --password <password> --import-dir <import dir>
python3 pipeline.py build                              # rewrite the manifest
```

The last run: 2,154 nodes and 11,778 relationships, no SHACL violation in the graph, an empty round-trip diff, and equal hashes for the sorted and shuffled loads.
