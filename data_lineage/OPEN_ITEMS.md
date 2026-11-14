# Open items

These items were found while reconstructing this catalog and opening the pull request. They are still open. The reconstructed files were left as they are.

## The ontology check does not run this catalog's tests

`scripts/test_check_script.py` runs `test_every_tracked_test_file_is_run`. That test requires every tracked `test_*.py` path to appear in `scripts/check.sh`. Twelve test files under `data_lineage/` are tracked, and `scripts/check.sh` does not list them, so the test fails. Those files are this catalog's tests. `scripts/check.sh` was not edited.

## A lockfile hash matches a measure-list name token

`Privacy.test_no_person_name_from_the_measure_list_is_in_the_repo` in `business_architecture/ontology/kpi/test_measures.py` reads every tracked text file for name tokens from the measure list. It matches the letter run `tom` inside two pnpm integrity hashes in `data_lineage/neo4j_text2cypher_fullstack/frontend/pnpm-lock.yaml`. Both hashes belong to `es-object-atoms@1.1.2`, on lines 767 and 2594. The hashes were not edited.

## The portal accepts every origin and does not authenticate questions

`ALLOWED_ORIGINS` stays a JSON string in `data_lineage/neo4j_text2cypher_fullstack/backend/app/config.py`, `data_lineage/neo4j_text2cypher_fullstack/backend/app/main.py`, and `data_lineage/neo4j_text2cypher_fullstack/backend/app/api/routes.py`. CORS and the `/ask` referer check treat that string as characters, so a `*` allows every origin. `POST /ask` has no authentication.

## SQL Server connections trust the server certificate

`query_sql_server` in `data_lineage/db_connect/src/connect/query_sql_server.py` always sets `TrustServerCertificate=yes`.

## The read-only Cypher check is a keyword denylist

`assert_read_only` in `data_lineage/neo4j_text2cypher_fullstack/backend/app/generation/agent.py` is a keyword denylist. It misses Cypher 25 `INSERT`, `GRANT`, and write or load procedures.

## Two GitHub Actions jobs went red without logs

The GitHub Actions jobs `checks` and `lychee` failed in a couple of seconds, and their logs were not stored. Rerun them before treating that red result as a catalog failure.

## Three deadline tests fail in this environment

Three share-release deadline tests failed on this machine's argparse, which reports `unrecognized arguments: -- sleep 30`. The scripts are unchanged. They are not this catalog.

- `scripts/share_release/test_cut.py::test_a_hanging_export_is_stopped_by_the_deadline`
- `scripts/share_release/test_cut.py::test_a_hanging_zip_is_stopped_by_the_deadline`
- `scripts/share_release/test_publish.py::test_the_clean_room_stops_its_container_when_the_deadline_passes`
