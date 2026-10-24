#!/usr/bin/env bash
# Add-on H of the ontology-to-lpg skill: write the Cypher 25 GRAPH TYPE statement for the current
# inputs and shapes to $LPG_OUT/graph-type.cypher with build.py graph-type, which reads the data files
# to type as LIST exactly the properties the load stores as arrays. It applies nothing: apply the
# statement to an Enterprise target (Aura included) after aura-copy.sh, by hand.
# Needs ONTOLOGY_TO_LPG, LPG_OUT and uv.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/common.sh"
cd "$SK"
py build.py graph-type --config "$CONFIG" "${SHAPE_ARGS[@]}" "${DATA[@]}" > "$LPG_OUT/graph-type.cypher"
nodes=$(grep -c '^  (:[^)]* => {' "$LPG_OUT/graph-type.cypher" || true)
rels=$(grep -c ')-\[:' "$LPG_OUT/graph-type.cypher" || true)
echo "wrote $LPG_OUT/graph-type.cypher: $nodes node and $rels relationship element types"
