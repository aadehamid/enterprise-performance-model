#!/usr/bin/env bash
# Step 5 of the store tests: rebuild the projection from the Databricks copy and prove it equals the one
# built from the repository. Run it after run.sh, load.sh and aura-copy.sh have built and copied the
# repository's projection into $BASELINE_OUT, and after the local Neo4j and Aura were emptied.
#  1. export everything the Databricks table holds (the rdf-store skill's rdfstore.py export), and
#     compare it with the release files by RDFC-1.0 hash (rdfstore.py compare);
#  2. map the exported graphs to the projection's inputs (rebuild_inputs.py; the two whole-graph shape
#     files are not in the table, so they come from the repository);
#  3. run run.sh and load.sh on those inputs into $LPG_OUT, then require loadable.nt and inferred.nt to
#     hold the baseline's triples (as RDF 1.1 terms: the export writes "x"^^xsd:string as "x") and the
#     report's graph hashes to equal the baseline report's, the proof that Neo4j holds the same graph;
#  4. tag (tags.sh), copy to the target env file (copy_graph.py, as aura-copy.sh), check the tags there.
# Usage: rebuild.sh <databricks.env> <table> <target.env>
# Needs ONTOLOGY_TO_LPG, RDF_STORE, LPG_OUT (new, for the rebuild), BASELINE_OUT, ROBOT_JAR, Docker, uv.
set -euo pipefail
[ $# -eq 3 ] || { echo "usage: $0 <databricks.env> <table> <target.env>" >&2; exit 2; }
DBX_ENV=$1 TABLE=$2 TARGET_ENV=$3
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${RDF_STORE:?set RDF_STORE to the rdf-store skill folder}" "${BASELINE_OUT:?set BASELINE_OUT}"
. "$HERE/common.sh"
DBX_ENV="$(abs_path "$DBX_ENV")" TARGET_ENV="$(abs_path "$TARGET_ENV")"   # rs and copy_graph run elsewhere
EXPORT="$LPG_OUT/databricks-export"
rm -rf "$EXPORT"; mkdir -p "$EXPORT"
RS="$RDF_STORE/scripts"
rs() { ( cd "$RS" && uv run -q --no-project --with pyoxigraph --with databricks-sql-connector python3 rdfstore.py "$@" < /dev/null ); }
echo "== 1. export from Databricks and compare with the release"
rs export --store databricks --env "$DBX_ENV" --table "$TABLE" --out "$EXPORT/table.nq" --ttl-dir "$EXPORT/ttl"
PACK=()
for f in "${DATA[@]}"; do
  d=$(dirname "$f"); v=$(basename "$d"); m=$(basename "$(dirname "$d")")
  PACK+=("$f")
  for k in shapes catalog; do PACK+=(--graph "$d/$k.ttl=https://w3id.org/lsc/ontology/modules/$m/$v/$k" "$d/$k.ttl"); done
done
rs pack --out "$EXPORT/release.nq" "${PACK[@]}"
rs compare "$EXPORT/release.nq" "$EXPORT/table.nq" > "$EXPORT/compare.json"
echo "the Databricks copy has the release's RDFC-1.0 hash"
echo "== 2. inputs from the export"
py "$HERE/rebuild_inputs.py" "$EXPORT/ttl" > "$EXPORT/input-list.tsv"
echo "== 3. project the export"
INPUT_LIST="$EXPORT/input-list.tsv" bash "$HERE/run.sh"
INPUT_LIST="$EXPORT/input-list.tsv" bash "$HERE/load.sh"
py "$HERE/rebuild_inputs.py" compare-triples "$LPG_OUT" "$BASELINE_OUT"
py "$HERE/rebuild_inputs.py" compare-reports "$LPG_OUT/projection-report.json" "$BASELINE_OUT/projection-report.json"
echo "== 4. tag, copy and check on the target"
INPUT_LIST="$EXPORT/input-list.tsv" bash "$HERE/tags.sh"
. "$LPG_OUT/neo4j-run/run.env"
( cd "$SK" && NEO4J_PASSWORD="$PASSWORD" uv run -q --no-project --with rdflib --with neo4j python3 copy_graph.py \
    --source "bolt://127.0.0.1:$PORT" --target-env "$TARGET_ENV" --report "$LPG_OUT/projection-report.json" < /dev/null )
INPUT_LIST="$EXPORT/input-list.tsv" bash "$HERE/tags.sh" --env "$TARGET_ENV"
echo "rebuild.sh passed: the projection rebuilt from Databricks equals the repository's, locally and on the target"
