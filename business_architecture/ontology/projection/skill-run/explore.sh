#!/usr/bin/env bash
# Add-on F: start Jena Fuseki from the rdf-store skill's compose file, load the projection's inputs and
# inferred.nt (rdfstore.py roundtrip, one named graph per package, hash-checked), then run
# explore.py compare: every saved walk in queries.json and the module map, Neo4j against Jena. It
# writes $LPG_OUT/explore-report.json and removes Fuseki at the end, pass or fail.
#   explore.sh                 against the local Neo4j load.sh left running (after tags.sh)
#   explore.sh --env <file>    against the Neo4j the env file names (after tags.sh --env)
# Needs ONTOLOGY_TO_LPG, RDF_STORE (the rdf-store skill folder), LPG_OUT, Docker and uv.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/common.sh"
: "${RDF_STORE:?set RDF_STORE to the rdf-store skill folder}"
TARGET=()
if [ "${1:-}" = "--env" ]; then
  [ $# -eq 2 ] || { echo "usage: $0 [--env <target.env>]" >&2; exit 2; }
  TARGET=(--env "$2")
else
  . "$LPG_OUT/neo4j-run/run.env"
  export NEO4J_PASSWORD="$PASSWORD"
  TARGET=(--uri "bolt://127.0.0.1:$PORT")
fi
PORT_F="${RDF_FUSEKI_PORT:-13031}"
FCOMPOSE="$RDF_STORE/docker/compose.yaml"
fdown() { RDF_FUSEKI_PORT="$PORT_F" docker compose -f "$FCOMPOSE" -p epm-explore-fuseki down -v < /dev/null > /dev/null 2>&1 || true; }
trap fdown EXIT
fdown
RDF_FUSEKI_PORT="$PORT_F" docker compose -f "$FCOMPOSE" -p epm-explore-fuseki up -d --build < /dev/null
for _ in $(seq 1 60); do
  curl -sf -o /dev/null "http://127.0.0.1:$PORT_F/ds/query?query=ASK%7B%7D" < /dev/null && break
  sleep 2
done
( cd "$RDF_STORE/scripts" && uv run -q --no-project --with pyoxigraph python3 rdfstore.py roundtrip --store fuseki \
    --gsp "http://127.0.0.1:$PORT_F/ds/data" --query "http://127.0.0.1:$PORT_F/ds/query" \
    --update "http://127.0.0.1:$PORT_F/ds/update" --report "$LPG_OUT/jena-roundtrip.json" \
    --graph "$LPG_OUT/inferred.nt=urn:ontology-to-lpg:inferred" "${DATA[@]}" "$LPG_OUT/inferred.nt" < /dev/null )
cd "$SK"
py explore.py compare --config "$CONFIG" "${TARGET[@]}" --sparql "http://127.0.0.1:$PORT_F/ds/query" \
  --queries "$HERE/queries.json" --report "$LPG_OUT/explore-report.json"
echo "explore.sh passed; report in $LPG_OUT/explore-report.json"
