#!/usr/bin/env bash
# Add-on J of the ontology-to-lpg skill: start Jena Fuseki through the skill's compose file (profile
# fuseki), load the inputs and run.sh's inferred.nt with triplestore.py, one named graph per file, and
# check the per-graph, per-predicate and three-way counts against load.sh's projection-report.json.
# Removes Fuseki (down -v) at the end, pass or fail. Writes $LPG_OUT/triplestore-report.json.
# Needs ONTOLOGY_TO_LPG, LPG_OUT, Docker and uv; run run.sh and load.sh first.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for f in inferred.nt projection-report.json; do
  [ -f "$LPG_OUT/$f" ] || { echo "no $LPG_OUT/$f: run run.sh and load.sh first" >&2; exit 2; }
done
PROJECT=epm-lpg-fuseki
PORT="${LPG_FUSEKI_PORT:-13030}"
compose() { LPG_FUSEKI_PORT="$PORT" docker compose -f "$COMPOSE" -p "$PROJECT" "$@" < /dev/null; }
trap 'compose --profile fuseki down -v > /dev/null 2>&1 || true' EXIT
compose --profile fuseki down -v > /dev/null 2>&1 || true
compose --profile fuseki up -d --build
up=no
for _ in $(seq 1 60); do
  curl -fsS "http://127.0.0.1:$PORT/\$/ping" > /dev/null 2>&1 && { up=yes; break; }
  sleep 2
done
[ $up = yes ] || { compose logs fuseki 2>&1 | tail -20; echo "Fuseki did not start" >&2; exit 1; }
cd "$SK"
py triplestore.py --gsp "http://127.0.0.1:$PORT/ds" --query "http://127.0.0.1:$PORT/ds/query" \
  --inferred "$LPG_OUT/inferred.nt" --projection-report "$LPG_OUT/projection-report.json" \
  --report "$LPG_OUT/triplestore-report.json" "${DATA[@]}"
echo "triplestore.sh passed; report in $LPG_OUT/triplestore-report.json"
