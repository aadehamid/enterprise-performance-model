# system: the systems the process map names

The `system` module holds the systems, office tools and working documents that the process map's `systems` fields name, and links each one to the processes that use it (competency question 6). Its namespace is `https://w3id.org/lsc/ontology/modules/system/`; its build reads `core` 2.3.0 for process IRIs (2.2.0 until 2026-10-23, EPM-DEC-001-0089; 2.1.0 until 2026-10-22, EPM-DEC-001-0076); its released 1.0.0 package requires `core` 2.2.0. EPM-DEC-001-0055 records the design.

| File | What |
|---|---|
| `register.csv` | Every distinct string in the map's `systems` fields (37), with the systems it names and the rule: `exact`, `spelling` (a merge on spelling only), `split` (a string that names several systems, split on "/"), or `no-system` (Manual, TBD and two plans to build something) |
| `systems.csv` | The 32 systems, each with its name and kind: application, office tool or working document |
| `vocabulary.ttl`, `shapes.ttl` | The class, the `supports` and `systemKind` properties, the system-kind code list, and the SHACL shapes |
| `build_systems.py`, `systems.ttl` | The build: 32 systems and 285 links to 150 processes. 153 processes have a `systems` field; three of them name only Manual, TBD or a plan. `--verify` fails unless `systems.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_systems.py` | Tests: the build is current, the figures, the spelling merge, a split, Manual creating no system, kinds, pinned links, and SHACL accepting the module and rejecting an invented definition, two kinds, a kind off the list and a missing note |

The module is not released yet. A release needs the decision owner's approval. *2026-10-22:* released as 1.0.0, with the decision owner's approval of the release plan (EPM-DEC-001-0077). The package is in `../releases/system/1.0.0/`.

No source in the repository says what each system does, so no system has a definition; each carries a note saying so. These are internal system names, which EPM-DEC-001-0040 item 3 allows in this repository.
