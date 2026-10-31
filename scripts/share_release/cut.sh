#!/usr/bin/env bash
# The one command that cuts the share release from a main checkout (plan step 3 to 7, 10's zip):
#
#   scripts/share_release/cut.sh --epm <main checkout> --skills <skills checkout> --out <folder> \
#       --env <stores env> [--baseline <main's validate json>] [--no-cleanroom]
#
# In order: export (the allowlist and the rewrite rules); rebuild inside the release; the leak gate; the store
# rows on the test stores named in --env (the projection's load-verify writes the release's own report and
# figures); the release's own check.sh; the tree rows; the comparison with main; every snippet; the gate again;
# the zip; the clean room on the zip; and, with --baseline, the validation report. Each step writes beside the
# output folder (<out>-<step>.json or .log). The first failing step stops the cut: a release with a failing
# check is not cut.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EPM=""; SKILLS=""; OUT=""; ENVF=""; BASELINE=""; CLEANROOM=1
while [ $# -gt 0 ]; do
  case "$1" in
    --epm) EPM="$2"; shift 2;; --skills) SKILLS="$2"; shift 2;; --out) OUT="$2"; shift 2;;
    --env) ENVF="$2"; shift 2;; --baseline) BASELINE="$2"; shift 2;; --no-cleanroom) CLEANROOM=0; shift;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[ -n "$EPM" ] && [ -n "$SKILLS" ] && [ -n "$OUT" ] && [ -n "$ENVF" ] || { sed -n '2,12p' "$0"; exit 2; }
EPM="$(cd "$EPM" && pwd)"; SKILLS="$(cd "$SKILLS" && pwd)"; OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
ENVF="$(cd "$(dirname "$ENVF")" && pwd)/$(basename "$ENVF")"
export PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE
uvpy() { uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$@"; }
step() { echo "=== $1 ($(date -u +%H:%M:%S))"; }

step "export"; rm -rf "$OUT"; python3 -I "$HERE/export.py" --epm "$EPM" --skills "$SKILLS" --out "$OUT" | tail -1
step "rebuild"; uvpy "$HERE/rebuild.py" --release "$OUT" --epm "$EPM" | tail -1
step "gate"; python3 -I "$HERE/gate.py" "$OUT" | tail -1
step "store rows"; uvpy "$HERE/validate.py" run --tree "$OUT" --out "$OUT-stores.json" --env "$ENVF" \
  --rows projection-pipeline,underscores,demo-offline,store-map > "$OUT-stores.log" 2>&1 || { tail -20 "$OUT-stores.log"; exit 1; }
python3 - "$OUT-stores.json" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1]))["rows"]
bad = [k for k, v in rows.items() if not v.get("ok")]
print("store rows:", ", ".join(f"{k} {'ok' if v.get('ok') else 'FAILED'}" for k, v in rows.items()))
sys.exit(1 if bad else 0)
PY
step "check.sh"; (cd "$OUT" && bash scripts/check.sh > "$OUT-check.log" 2>&1) || { tail -30 "$OUT-check.log"; exit 1; }; tail -1 "$OUT-check.log"
step "tree rows"; uvpy "$HERE/validate.py" run --tree "$OUT" --out "$OUT-tree.json" --env "$ENVF" \
  --rows regression,docs-links,skills-tests,iri-base,gate > "$OUT-tree.log" 2>&1 || { tail -20 "$OUT-tree.log"; exit 1; }
python3 - "$OUT-tree.json" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1]))["rows"]
print("tree rows:", ", ".join(f"{k} {'ok' if v.get('ok') else 'FAILED'}" for k, v in rows.items()))
sys.exit(1 if any(not v.get("ok") for v in rows.values()) else 0)
PY
step "compare"; uvpy "$HERE/validate.py" compare --main "$EPM" --release "$OUT" --out "$OUT-compare.json" > "$OUT-compare.log" 2>&1 || { tail -20 "$OUT-compare.log"; exit 1; }
python3 - "$OUT-compare.json" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1]))["rows"]
print("comparison:", ", ".join(f"{k} {'ok' if v.get('ok') else 'FAILED'}" for k, v in rows.items()))
sys.exit(1 if any(not v.get("ok") for v in rows.values()) else 0)
PY
step "snippets"; uvpy "$HERE/snippets.py" --tree "$OUT" --out "$OUT-snippets.json" --env "$ENVF" | head -1
step "gate again"; find "$OUT" -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +; python3 -I "$HERE/gate.py" "$OUT" | tail -1
step "zip"; python3 -I "$HERE/publish.py" zip --release "$OUT" --out "$OUT.zip" | tail -1
if [ "$CLEANROOM" = 1 ]; then step "clean room"; bash "$HERE/cleanroom.sh" "$OUT.zip" "$OUT-cleanroom.log" > /dev/null; tail -2 "$OUT-cleanroom.log"; fi
if [ -n "$BASELINE" ]; then
  step "report"; python3 - "$OUT-tree.json" "$OUT-stores.json" "$OUT-release.json" <<'PY'
import json, sys
t, s = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
t["rows"].update(s["rows"]); json.dump(t, open(sys.argv[3], "w"), indent=1)
PY
  uvpy "$HERE/validate.py" report "$BASELINE" "$OUT-release.json" "$OUT-compare.json" --out "$OUT-VALIDATION.md" | tail -1
fi
step "done"; echo "release: $OUT; zip: $OUT.zip"
