# lane: the office lanes

The `lane` module holds the four office lanes of the trading organization (`../../business_process/office_lanes.json`) as a SKOS code list, and places each process the process map gives an `officeLane` (competency question 9). Its namespace is `https://w3id.org/lsc/ontology/modules/lane/`; it depends on `core` 2.2.0 for process IRIs (2.1.0 until 2026-10-22, EPM-DEC-001-0076). EPM-DEC-001-0056 records the design.

| File | What |
|---|---|
| `vocabulary.ttl`, `shapes.ttl` | The lane scheme, the `officeLane` property, and shapes: a process sits in at most one lane, and a lane is one of the four |
| `build_lanes.py`, `lanes.ttl` | The build: 4 lanes and 7 placed processes (CM 1.2.1 to CM 1.2.7). `--verify` fails unless `lanes.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_lanes.py` | Tests: the build is current, the seven placements pinned by hand, nothing inherited, and SHACL rejecting two lanes or a lane off the list |

The module is not released yet. A release needs the decision owner's approval.
