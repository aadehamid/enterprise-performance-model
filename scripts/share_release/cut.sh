#!/usr/bin/env bash
# The one command that cuts the share release from a main checkout (plan steps 3 to 7, and step 10's zip):
#
#   scripts/share_release/cut.sh --epm <main checkout> --skills <skills checkout> --out <folder> \
#       --env <stores env> [--baseline <main's validate json>] [--store-rows <rows>|all] [--no-cleanroom]
#
# In order: export (the allowlist and the rewrite rules); rebuild inside the release; the leak gate; the store
# rows on the test stores named in --env (the projection's load-verify writes the release's own report and
# figures); the release's own check.sh; the tree rows; the comparison with main; every snippet; the gate again;
# the zip; the clean room on the zip; and, with --baseline, the validation report. Each step writes beside the
# output folder (<out>-<step>.json or .log). The first failing step stops the cut: a release with a failing
# check is not cut.
#
# What this command does not do, by the plan:
# - The store rows that need Databricks (projection-driver, demo-live, tech-graph, sync) run only when the
#   workspace is reachable: --store-rows all, or a list, runs them; the default runs the four offline rows
#   (projection-pipeline, underscores, demo-offline, store-map). The final line names the rows that did not run.
# - Step 9, deleting the test data, is cleanup.py --ledger <LEDGER_FILE of --env> --yes, run after the review of
#   the cut, and the AuraDB reload from main is the driver's step (the decision's amendment, item 12).
# - Step 10, the orphan branch and the shared zip, waits for the owner: publish.py branch, then --push.
# The final line says what remains.
#
# --out is removed and written afresh. It is refused when it is "/", the home folder, the checkout or the skills
# checkout or a parent of either, or an existing folder that is neither empty nor a release (no release.json).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EPM=""; SKILLS=""; OUT=""; ENVF=""; BASELINE=""; CLEANROOM=1; STORE_ROWS="projection-pipeline,underscores,demo-offline,store-map"
ALL_STORE_ROWS="projection-pipeline,underscores,projection-driver,demo-offline,demo-live,tech-graph,sync,store-map"
while [ $# -gt 0 ]; do
  case "$1" in
    --epm) EPM="$2"; shift 2;; --skills) SKILLS="$2"; shift 2;; --out) OUT="$2"; shift 2;;
    --env) ENVF="$2"; shift 2;; --baseline) BASELINE="$2"; shift 2;; --no-cleanroom) CLEANROOM=0; shift;;
    --store-rows) STORE_ROWS="$2"; shift 2;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[ -n "$EPM" ] && [ -n "$SKILLS" ] && [ -n "$OUT" ] && [ -n "$ENVF" ] || { sed -n '2,12p' "$0"; exit 2; }
[ "$STORE_ROWS" = all ] && STORE_ROWS="$ALL_STORE_ROWS"
EPM="$(cd "$EPM" && pwd -P)"; SKILLS="$(cd "$SKILLS" && pwd -P)"; OUT="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$OUT")"
ENVF="$(cd "$(dirname "$ENVF")" && pwd -P)/$(basename "$ENVF")"
export PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE

# The output folder: never a folder that holds something else.
refuse() { echo "refusing --out $OUT: $1" >&2; exit 2; }
HOMEDIR="$(cd ~ && pwd -P)"
[ "$OUT" = "/" ] && refuse "it is the root"
[ "$OUT" = "$HOMEDIR" ] && refuse "it is the home folder"
for tree in "$EPM" "$SKILLS" "$HERE"; do
  case "$tree/" in "$OUT/"*) refuse "it is the checkout $tree or a parent of it";; esac
done
if [ -e "$OUT" ]; then
  [ -d "$OUT" ] || refuse "it is a file"
  if [ -n "$(ls -A "$OUT")" ] && [ ! -f "$OUT/release.json" ]; then refuse "it is not empty and holds no release.json"; fi
fi
LEDGER="$(grep -E '^LEDGER_FILE=' "$ENVF" | tail -1 | cut -d= -f2- || true)"; LEDGER="${LEDGER:-validate-ledger.jsonl}"

uvpy() { uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$@"; }
step() { echo "=== $1 ($(date -u +%H:%M:%S))"; }
rows_ok() {  # every row in a validate json must be ok; prints the rows
python3 - "$1" "$2" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1]))["rows"]
print(f"{sys.argv[2]}:", ", ".join(f"{k} {'ok' if v.get('ok') else 'FAILED'}" for k, v in rows.items()))
sys.exit(1 if any(not v.get("ok") for v in rows.values()) else 0)
PY
}

step "export"; rm -rf "$OUT"; python3 -I "$HERE/export.py" --epm "$EPM" --skills "$SKILLS" --out "$OUT" | tail -1
step "rebuild"; uvpy "$HERE/rebuild.py" --release "$OUT" --epm "$EPM" | tail -1
step "gate"; python3 -I "$HERE/gate.py" "$OUT" | tail -1
step "store rows ($STORE_ROWS)"; uvpy "$HERE/validate.py" run --tree "$OUT" --out "$OUT-stores.json" --env "$ENVF" \
  --rows "$STORE_ROWS" > "$OUT-stores.log" 2>&1 || { tail -20 "$OUT-stores.log"; exit 1; }
rows_ok "$OUT-stores.json" "store rows"
step "check.sh"; (cd "$OUT" && bash scripts/check.sh > "$OUT-check.log" 2>&1) || { tail -30 "$OUT-check.log"; exit 1; }; tail -1 "$OUT-check.log"
step "tree rows"; uvpy "$HERE/validate.py" run --tree "$OUT" --out "$OUT-tree.json" --env "$ENVF" \
  --rows regression,docs-links,skills-tests,iri-base,gate > "$OUT-tree.log" 2>&1 || { tail -20 "$OUT-tree.log"; exit 1; }
rows_ok "$OUT-tree.json" "tree rows"
step "compare"; uvpy "$HERE/validate.py" compare --main "$EPM" --release "$OUT" --out "$OUT-compare.json" > "$OUT-compare.log" 2>&1 || { tail -20 "$OUT-compare.log"; exit 1; }
rows_ok "$OUT-compare.json" "comparison"
step "snippets"; uvpy "$HERE/snippets.py" --tree "$OUT" --out "$OUT-snippets.json" --env "$ENVF" | head -1
step "gate again"; find "$OUT" -type d \( -name __pycache__ -o -name .pytest_cache -o -name .venv \) -prune -exec rm -rf {} +; python3 -I "$HERE/gate.py" "$OUT" | tail -1
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
NOT_RUN="$(python3 -c 'import sys; a=set(sys.argv[1].split(",")); print(", ".join(r for r in sys.argv[2].split(",") if r not in a) or "none")' "$STORE_ROWS" "$ALL_STORE_ROWS")"
step "done"; echo "release: $OUT; zip: $OUT.zip; store rows not run: $NOT_RUN (--store-rows all runs them when Databricks is reachable); remaining: step 9, $HERE/cleanup.py --ledger $LEDGER --env $ENVF --tree $OUT --yes, and the AuraDB reload from main; step 10, $HERE/publish.py branch --release $OUT --repo $EPM, then --push, the owner's decision"
