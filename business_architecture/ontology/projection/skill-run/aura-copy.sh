#!/usr/bin/env bash
# Add-on I of the ontology-to-lpg skill: copy the verified graph from the local Neo4j that load.sh
# left running to the Neo4j named in an env file (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, optional
# NEO4J_DATABASE; the Aura credentials format), with copy_graph.py --report. copy_graph.py touches the
# target only when the report says passed with equal hashes and the local graph's hash equals the
# report's, and fails unless the target's hash then equals the local one. If load.sh's Neo4j is not up, it runs load.sh
# first. It removes the local Neo4j (down -v) and its run folder at the end, pass or fail.
# Usage: aura-copy.sh <target.env> [--replace]   (--replace deletes everything on the target first)
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: $0 <target.env> [--replace]" >&2; exit 2; }
TARGET_ENV=$1; shift
[ -f "$TARGET_ENV" ] || { echo "no file $TARGET_ENV" >&2; exit 2; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/common.sh"
RUN="$LPG_OUT/neo4j-run"
running() {
  [ -f "$RUN/run.env" ] && [ -f "$LPG_OUT/projection-report.json" ] || return 1
  . "$RUN/run.env"
  [ -n "$(LPG_RUN="$RUN" NEO4J_PASSWORD=unused docker compose -f "$COMPOSE" -p "$PROJECT" ps -q neo4j < /dev/null 2>/dev/null)" ]
}
running || bash "$HERE/load.sh"
. "$RUN/run.env"
rc=0
( cd "$SK" && NEO4J_PASSWORD="$PASSWORD" uv run -q --no-project --with rdflib --with neo4j python3 copy_graph.py \
    --source "bolt://127.0.0.1:$PORT" --target-env "$TARGET_ENV" --report "$LPG_OUT/projection-report.json" "$@" < /dev/null ) || rc=$?
LPG_RUN="$RUN" NEO4J_PASSWORD=unused docker compose -f "$COMPOSE" -p "$PROJECT" --profile neo4j --profile fuseki down -v < /dev/null > /dev/null 2>&1 || true
rm -rf "$RUN"
exit $rc
