#!/usr/bin/env bash
# Steps 2 to 4 of the ontology-to-lpg skill on the EPM inputs: check the rules, validate, reason with
# ELK through ROBOT, serialise, check the serialised files and write the manifest, all into $LPG_OUT.
# Validation path V1 to V5 (references/multi-store.md in the skill). Needs ONTOLOGY_TO_LPG, LPG_OUT,
# ROBOT_JAR, Java 11 or later and uv.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/common.sh"
: "${ROBOT_JAR:?set ROBOT_JAR to the ROBOT 1.9.10 jar}"
ROBOT_SHA256=16a73c074f3df359a7338a84b4e0788785fe06117f931bb9796e9619ea776105  # references/running.md, rule 2
echo "== ROBOT checksum"
echo "$ROBOT_SHA256  $ROBOT_JAR" | shasum -a 256 -c -
cd "$SK"
echo "== check: rules and pins"
py check_projection_rules.py --config "$CONFIG" "${SHAPE_ARGS[@]}" --releases "$RELEASES" "${DATA[@]}"
echo "== check: SHACL on the inputs"
py validate_data.py --config "$CONFIG" "${SHAPE_ARGS[@]}" "${DATA[@]}"
echo "== reason"
py build.py merge --output "$LPG_OUT/merged.ttl" "${DATA[@]}"
java -jar "$ROBOT_JAR" reason --reasoner ELK --input "$LPG_OUT/merged.ttl" --axiom-generators "SubClass ClassAssertion" \
  --include-indirect true --output "$LPG_OUT/reasoned.ttl" < /dev/null
py build.py inferred --input "$LPG_OUT/merged.ttl" --reasoned "$LPG_OUT/reasoned.ttl" --output "$LPG_OUT/inferred.nt"
echo "== serialise"
py build.py loadable --output "$LPG_OUT/loadable.nt" "${DATA[@]}"
py build.py check-serialised --loadable "$LPG_OUT/loadable.nt" --inferred "$LPG_OUT/inferred.nt"
py validate_data.py --config "$CONFIG" "${SHAPE_ARGS[@]}" "$LPG_OUT/loadable.nt" "$LPG_OUT/inferred.nt"
echo "== manifest"
py build.py manifest --config "$CONFIG" "${SHAPE_ARGS[@]}" --loadable "$LPG_OUT/loadable.nt" \
  --inferred "$LPG_OUT/inferred.nt" --output "$LPG_OUT/projection-manifest.json" "${DATA[@]}"
echo "== in_graph_shapes (advisory)"
py in_graph_shapes.py --output "$LPG_OUT/shapes-in-graph.ttl" "${SHAPES[@]}" | tail -3
echo "run.sh passed; outputs in $LPG_OUT"
