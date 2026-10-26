#!/usr/bin/env bash
# Steps 4 to 7 of README.md ("Rerun the whole pipeline") in one command: build, reason with ROBOT, load and verify in a
# Neo4j container, rewrite the manifest. Run it after any release changes the projection's inputs, then commit
# inferred.nt, projection-manifest.json and projection-report.json together.
#
#   business_architecture/ontology/projection/run_local.sh [--keep]
#
# --keep leaves the Neo4j container (epm-lpg, Bolt on localhost:17687) running; its password is in
# ~/epm-lpg/run.env (mode 600). Without it the container is removed at the end, as README.md step 7 does.
# Needs Docker, uv, Java 11+, ROBOT at ~/epm-lpg/robot.jar, and ~/epm-lpg/import and ~/epm-lpg/plugins (n10s).
# The password is random and is never printed.
set -euo pipefail
keep=false
[ "${1:-}" = "--keep" ] && keep=true
here="$(cd "$(dirname "$0")" && pwd)"
robot=~/epm-lpg/robot.jar import=~/epm-lpg/import plugins=~/epm-lpg/plugins
pw=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
cd "$here"
uv run -q --with rdflib --with pyshacl python pipeline.py build
uv run -q --with rdflib --with pyshacl python pipeline.py reason --robot "$robot"
docker rm -f epm-lpg >/dev/null 2>&1 || true
docker run -d --name epm-lpg -p 127.0.0.1:17687:7687 -p 127.0.0.1:17474:7474 -e NEO4J_AUTH="neo4j/$pw" \
  -e NEO4J_PLUGINS='["apoc"]' -e NEO4J_dbms_security_procedures_unrestricted='apoc.*,n10s.*' \
  -v "$import":/import -v "$plugins":/plugins neo4j:2025.06.2 >/dev/null
for _ in $(seq 1 120); do docker logs epm-lpg 2>&1 | grep -q "Started." && break; sleep 5; done
if ! docker logs epm-lpg 2>&1 | grep -q "Started."; then
  echo "Neo4j did not start; see: docker logs epm-lpg (a full Docker disk is the usual cause)" >&2; exit 1
fi
uv run -q --with rdflib --with pyshacl --with neo4j python pipeline.py load-verify \
  --bolt bolt://localhost:17687 --password "$pw" --import-dir "$import"
uv run -q --with rdflib --with pyshacl python pipeline.py build
if $keep; then
  umask 077; printf 'NEO4J_URI=bolt://localhost:17687\nNEO4J_USERNAME=neo4j\nNEO4J_PASSWORD=%s\n' "$pw" > ~/epm-lpg/run.env
  echo "kept: epm-lpg on bolt://localhost:17687 (browser http://localhost:17474); login in ~/epm-lpg/run.env"
else
  docker rm -f epm-lpg >/dev/null
fi
echo "projection done"
