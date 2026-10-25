#!/usr/bin/env bash
# Add-on F of the ontology-to-lpg skill on the local Neo4j that load.sh left running, or on a copy:
#   tags.sh                  tag every node and relationship with its package (module_tags.py tag), check
#                            the tags, and build the module graph, on the local Neo4j
#   tags.sh --env <file>     check the tags and build the module graph on the Neo4j the env file names
#                            (a copy from aura-copy.sh carries the tags; :Module nodes are not copied)
# The tags never change the graph hash (the skill's load_verify.graph_hash leaves `graph` out).
# Needs ONTOLOGY_TO_LPG, LPG_OUT, uv; run load.sh first.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/common.sh"
TARGET=()
if [ "${1:-}" = "--env" ]; then
  [ $# -eq 2 ] || { echo "usage: $0 [--env <target.env>]" >&2; exit 2; }
  TARGET=(--env "$(abs_path "$2")")   # the scripts may run from another folder
else
  [ $# -eq 0 ] || { echo "usage: $0 [--env <target.env>]" >&2; exit 2; }
  . "$LPG_OUT/neo4j-run/run.env"
  export NEO4J_PASSWORD="$PASSWORD"
  TARGET=(--uri "bolt://127.0.0.1:$PORT")
fi
cd "$SK"
if [ ${#TARGET[@]} -eq 2 ] && [ "${TARGET[0]}" = --uri ]; then
  py module_tags.py tag --config "$CONFIG" --inferred "$LPG_OUT/inferred.nt" "${TARGET[@]}" "${DATA[@]}"
fi
py module_tags.py check --config "$CONFIG" --inferred "$LPG_OUT/inferred.nt" "${TARGET[@]}" "${DATA[@]}"
py module_tags.py modules "${TARGET[@]}" "${DATA[@]}"
echo "tags.sh passed"
