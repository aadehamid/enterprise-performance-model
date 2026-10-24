#!/usr/bin/env bash
# Steps 5 and 6 of the ontology-to-lpg skill: start Neo4j with n10s through the skill's compose file
# (profile neo4j), run load_verify.py on run.sh's outputs, then build.py check-report.
# Validation path V6 to V12 (references/multi-store.md in the skill). On success Neo4j stays up for
# aura-copy.sh, with its settings in $LPG_OUT/neo4j-run/run.env; on failure it is removed (down -v).
# Needs ONTOLOGY_TO_LPG, LPG_OUT, Docker and uv; run run.sh first.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for f in merged.ttl loadable.nt inferred.nt projection-manifest.json; do
  [ -f "$LPG_OUT/$f" ] || { echo "no $LPG_OUT/$f: run run.sh first" >&2; exit 2; }
done
PROJECT=epm-lpg-local
RUN="$LPG_OUT/neo4j-run"
compose() { docker compose -f "$COMPOSE" -p "$PROJECT" "$@" < /dev/null; }
down() { LPG_RUN="$RUN" NEO4J_PASSWORD=unused compose --profile neo4j --profile fuseki down -v > /dev/null 2>&1 || true; }
down
rm -rf "$RUN"; mkdir -p "$RUN"; chmod 711 "$RUN"; mkdir -m 755 "$RUN/plugins" "$RUN/import"
( umask 077; printf 'PROJECT=%q\nPORT=%q\nPASSWORD=%q\nRUN=%q\n' "$PROJECT" "${LPG_BOLT_PORT:-17711}" "$(openssl rand -hex 12)" "$RUN" > "$RUN/run.env" )
. "$RUN/run.env"
export LPG_RUN="$RUN" NEO4J_PASSWORD="$PASSWORD" LPG_BOLT_PORT="$PORT"
fail() { echo "$1" >&2; down; rm -rf "$RUN"; exit 1; }
compose --profile neo4j up -d || fail "docker compose up failed"
started=no
for _ in $(seq 1 100); do
  compose logs neo4j 2>&1 | grep -q 'Started\.' && { started=yes; break; }
  sleep 3
done
[ $started = yes ] || { compose logs neo4j 2>&1 | tail -20; fail "Neo4j did not start"; }
sleep 5
cd "$SK"
rc=0
py load_verify.py --config "$CONFIG" "${SHAPE_ARGS[@]}" --bolt "bolt://127.0.0.1:$PORT" \
  --import-dir "$RUN/import" --plugins-dir "$RUN/plugins" --container "$PROJECT" \
  --merged "$LPG_OUT/merged.ttl" --loadable "$LPG_OUT/loadable.nt" --inferred "$LPG_OUT/inferred.nt" \
  --report "$LPG_OUT/projection-report.json" ${MANUAL_CASES:+--manual-cases "$MANUAL_CASES"} "${DATA[@]}" || rc=$?
[ $rc -eq 0 ] || fail "load_verify.py exited $rc; no report"
py build.py check-report --manifest "$LPG_OUT/projection-manifest.json" --report "$LPG_OUT/projection-report.json" \
  || fail "check-report failed"
echo "load.sh passed; Neo4j is up on 127.0.0.1:$PORT for aura-copy.sh (settings in $RUN/run.env)"
echo "remove it with: LPG_RUN=$(printf %q "$RUN") NEO4J_PASSWORD=unused docker compose -f $(printf %q "$COMPOSE") -p $PROJECT --profile neo4j --profile fuseki down -v"
