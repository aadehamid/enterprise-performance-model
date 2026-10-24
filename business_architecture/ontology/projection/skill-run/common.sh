# Sourced by the skill-run scripts. Reads the environment, checks it, and loads the input lists.
# Works in bash 3.2 (macOS /bin/bash): no mapfile, no namerefs.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HERE/epm-config.json"
: "${ONTOLOGY_TO_LPG:?set ONTOLOGY_TO_LPG to the ontology-to-lpg skill folder}"
: "${LPG_OUT:?set LPG_OUT to an output folder outside the repository}"
# Make every path absolute before any script changes directory.
abs_path() { case "$1" in /*) printf '%s\n' "$1";; *) printf '%s/%s\n' "$(pwd -P)" "$1";; esac; }
ONTOLOGY_TO_LPG="$(abs_path "$ONTOLOGY_TO_LPG")"
[ -z "${ROBOT_JAR:-}" ] || ROBOT_JAR="$(abs_path "$ROBOT_JAR")"
[ -z "${MANUAL_CASES:-}" ] || MANUAL_CASES="$(abs_path "$MANUAL_CASES")"
SK="$ONTOLOGY_TO_LPG/scripts"
COMPOSE="$ONTOLOGY_TO_LPG/docker/compose.yaml"
[ -f "$SK/build.py" ] || { echo "no scripts/build.py under ONTOLOGY_TO_LPG=$ONTOLOGY_TO_LPG" >&2; exit 2; }
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
made=no; [ -d "$LPG_OUT" ] || { mkdir -p "$LPG_OUT"; made=yes; }
LPG_OUT="$(cd "$LPG_OUT" && pwd -P)"
case "$LPG_OUT/" in "$(cd "$REPO" && pwd -P)/"*)
  [ $made = no ] || rmdir "$LPG_OUT"
  echo "LPG_OUT must be outside the repository" >&2; exit 2;;
esac

py() { uv run -q --no-project --with rdflib --with pyshacl --with neo4j python3 "$@" < /dev/null; }

# DATA, SHAPES and SHAPE_ARGS (repeated --shapes) from inputs.py, one path per line, spaces kept.
DATA=(); SHAPES=(); SHAPE_ARGS=()
while IFS= read -r l; do [ -n "$l" ] && DATA+=("$l"); done < <(py "$HERE/inputs.py" data)
while IFS= read -r l; do [ -n "$l" ] && SHAPES+=("$l") && SHAPE_ARGS+=(--shapes "$l"); done < <(py "$HERE/inputs.py" shapes)
RELEASES="$(py "$HERE/inputs.py" releases)"
[ ${#DATA[@]} -gt 0 ] && [ ${#SHAPES[@]} -gt 0 ] || { echo "inputs.py listed no inputs" >&2; exit 1; }
