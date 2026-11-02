#!/usr/bin/env bash
# The one command that cuts the share release from a main checkout (plan steps 3 to 7, and step 10's zip):
#
#   scripts/share_release/cut.sh --epm <main checkout> --skills <skills checkout> --out <folder> \
#       --env <stores env> [--baseline <main's validate json>] [--store-rows <rows>|all] [--no-cleanroom] [--replace]
#
# In order: export (the allowlist and the rewrite rules); rebuild inside the release; the leak gate; the store
# rows on the test stores named in --env (the release's own rebuild_stores.py writes its report and
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
#   the cut, and the stores are emptied and reloaded from the release (the release's rebuild_stores.py --empty; the owner's instruction of 2026-11-01).
# - Step 10, the orphan branch and the shared zip, waits for the owner: publish.py branch, then --push.
# The final line says what remains.
#
# --out is written afresh. It is refused when it is "/", the home folder, the checkout or the skills checkout or
# a parent of either, or a file. An existing folder that is not empty is removed only with --replace, and only
# when its release.json is exactly the marker this tool writes (manifest.is_tool_marker: the fixed keys, the
# release name, the mode text, a date; nothing else is accepted). The owner's names are checked before anything
# is removed, so a cut that would refuse removes nothing.
#
# Deadlines: every step (the export, the rebuild, each validation run, the release's check.sh, the comparison, the
# snippets, both gates, the zip, the report and the clean room) runs under cleanroom.py's deadline (STEP_TIMEOUT seconds
# each, default 7200; the whole process group is killed on expiry and the clean room removes its container), so
# a stalled download, store or daemon is a failed step, never a hung cut.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
EPM=""; SKILLS=""; OUT=""; ENVF=""; BASELINE=""; CLEANROOM=1; REPLACE=0; STEP_TIMEOUT="${STEP_TIMEOUT:-7200}"; STORE_ROWS="projection-pipeline,underscores,demo-offline,store-map"
ALL_STORE_ROWS="projection-pipeline,underscores,projection-driver,demo-offline,demo-live,tech-graph,sync,store-map"
while [ $# -gt 0 ]; do
  case "$1" in
    --epm) EPM="$2"; shift 2;; --skills) SKILLS="$2"; shift 2;; --out) OUT="$2"; shift 2;;
    --env) ENVF="$2"; shift 2;; --baseline) BASELINE="$2"; shift 2;; --no-cleanroom) CLEANROOM=0; shift;;
    --store-rows) STORE_ROWS="$2"; shift 2;; --replace) REPLACE=1; shift;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[ -n "$EPM" ] && [ -n "$SKILLS" ] && [ -n "$OUT" ] && [ -n "$ENVF" ] || { sed -n '2,12p' "$0"; exit 2; }
[ "$STORE_ROWS" = all ] && STORE_ROWS="$ALL_STORE_ROWS"
[ -n "$STORE_ROWS" ] || { echo "--store-rows names no row; a cut with no store row is not a cut" >&2; exit 2; }
EPM="$(cd "$EPM" && pwd -P)"; SKILLS="$(cd "$SKILLS" && pwd -P)"; OUT="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$OUT")"
ENVF="$(cd "$(dirname "$ENVF")" && pwd -P)/$(basename "$ENVF")"
export PYTHONDONTWRITEBYTECODE=1
unset GIT_DIR GIT_INDEX_FILE GIT_WORK_TREE

# The output folder: never a folder that holds something else.
refuse() { echo "refusing --out $OUT: $1" >&2; exit 2; }
HOMEDIR="$(python3 -c 'import os; print(os.path.realpath(os.path.expanduser("~")))')"
[ "$OUT" = "/" ] && refuse "it is the root"
[ "$OUT" = "$HOMEDIR" ] && refuse "it is the home folder"
for tree in "$EPM" "$SKILLS" "$HERE"; do
  case "$tree/" in "$OUT/"*) refuse "it is the checkout $tree or a parent of it";; esac
done
if [ -e "$OUT" ]; then
  [ -d "$OUT" ] || refuse "it is a file"
  if [ -n "$(ls -A "$OUT")" ]; then
    [ "$REPLACE" = 1 ] || refuse "it is not empty; --replace removes an earlier release of this tool"
    python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import manifest; sys.exit(0 if manifest.is_tool_marker(sys.argv[2]) else 1)' "$HERE" "$OUT/release.json" \
      || refuse "its release.json is not exactly the marker this tool writes"
  fi
fi
python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import owner; owner.owner_names()' "$HERE" || exit 2  # the names, before anything is removed
LEDGER="$(grep -E '^LEDGER_FILE=' "$ENVF" | tail -1 | cut -d= -f2- || true)"; LEDGER="${LEDGER:-validate-ledger.jsonl}"

uvpy() { uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$@"; }
within() { python3 "$HERE/cleanroom.py" run --timeout "$STEP_TIMEOUT" --log "$1" -- "${@:2}"; }  # one step under the deadline; its output in the log
step() { echo "=== $1 ($(date -u +%H:%M:%S))"; }
rows_ok() {  # every row in a validate json must be ok, and there must be rows; prints the rows
python3 - "$1" "$2" <<'PY'
import json, sys
rows = json.load(open(sys.argv[1]))["rows"]
print(f"{sys.argv[2]}:", ", ".join(f"{k} {'ok' if v.get('ok') else 'FAILED'}" for k, v in rows.items()) or "no rows ran")
sys.exit(1 if not rows or any(not v.get("ok") for v in rows.values()) else 0)
PY
}

step "export"; rm -rf "$OUT"; within "$OUT-export.log" python3 -I "$HERE/export.py" --epm "$EPM" --skills "$SKILLS" --out "$OUT" > /dev/null || { tail -20 "$OUT-export.log"; exit 1; }; tail -1 "$OUT-export.log"
step "rebuild"; within "$OUT-rebuild.log" uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$HERE/rebuild.py" --release "$OUT" --epm "$EPM" > /dev/null || { tail -20 "$OUT-rebuild.log"; exit 1; }; tail -1 "$OUT-rebuild.log"
step "gate"; within "$OUT-gate.log" python3 -I "$HERE/gate.py" "$OUT" > /dev/null || { tail -20 "$OUT-gate.log"; exit 1; }; tail -1 "$OUT-gate.log"
step "store rows ($STORE_ROWS)"; within "$OUT-stores.log" uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$HERE/validate.py" run --tree "$OUT" --out "$OUT-stores.json" --env "$ENVF" \
  --rows "$STORE_ROWS" > /dev/null || { tail -20 "$OUT-stores.log"; exit 1; }
rows_ok "$OUT-stores.json" "store rows"
step "check.sh"; (cd "$OUT" && within "$OUT-check.log" bash scripts/check.sh > /dev/null) || { tail -30 "$OUT-check.log"; exit 1; }; tail -1 "$OUT-check.log"
step "check.sh from a Git clone"; (within "$OUT-clone.log" python3 "$HERE/clonecheck.py" --release "$OUT" --log "$OUT-clone-check.log" --timeout "$STEP_TIMEOUT" > /dev/null) || { tail -30 "$OUT-clone-check.log"; exit 1; }; tail -1 "$OUT-clone-check.log"
step "tree rows"; within "$OUT-tree.log" uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$HERE/validate.py" run --tree "$OUT" --out "$OUT-tree.json" --env "$ENVF" \
  --rows regression,docs-links,skills-tests,iri-base,gate > /dev/null || { tail -20 "$OUT-tree.log"; exit 1; }
rows_ok "$OUT-tree.json" "tree rows"
step "compare"; within "$OUT-compare.log" uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$HERE/validate.py" compare --main "$EPM" --release "$OUT" --out "$OUT-compare.json" > /dev/null || { tail -20 "$OUT-compare.log"; exit 1; }
rows_ok "$OUT-compare.json" "comparison"
step "snippets"; within "$OUT-snippets.log" uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$HERE/snippets.py" --tree "$OUT" --out "$OUT-snippets.json" --env "$ENVF" > /dev/null || { tail -20 "$OUT-snippets.log"; exit 1; }; head -1 "$OUT-snippets.log"
step "gate again"; find "$OUT" -type d \( -name __pycache__ -o -name .pytest_cache -o -name .venv \) -prune -exec rm -rf {} +; within "$OUT-gate2.log" python3 -I "$HERE/gate.py" "$OUT" > /dev/null || { tail -20 "$OUT-gate2.log"; exit 1; }; tail -1 "$OUT-gate2.log"
step "zip"; within "$OUT-zip.log" python3 -I "$HERE/publish.py" zip --release "$OUT" --out "$OUT.zip" > /dev/null || { tail -20 "$OUT-zip.log"; exit 1; }; tail -1 "$OUT-zip.log"
if [ "$CLEANROOM" = 1 ]; then step "clean room"; python3 "$HERE/cleanroom.py" "$OUT.zip" --log "$OUT-cleanroom.log" --timeout "$STEP_TIMEOUT" > /dev/null || { tail -20 "$OUT-cleanroom.log"; exit 1; }; tail -2 "$OUT-cleanroom.log"; fi
if [ -n "$BASELINE" ]; then
  step "report"; python3 - "$OUT-tree.json" "$OUT-stores.json" "$OUT-release.json" "$OUT-check.log" <<'PY'
import json, sys
t, s = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
t["rows"].update(s["rows"])
# The release's own check.sh ran as a step of the cut, not as a validate row: its result is the "checks" row here,
# so the report compares it with main's checks row instead of reporting it as not run on the release.
log = open(sys.argv[4], encoding="utf-8", errors="replace").read().splitlines()  # the last line exactly, trailing blanks included
last = log[-1] if log else ""
t["rows"]["checks"] = {"ok": last == "all checks passed", "command": "bash scripts/check.sh (the release's own, run by the cut)",
                       "tail": "\n".join(log[-20:])}
json.dump(t, open(sys.argv[3], "w"), indent=1)
PY
  within "$OUT-report.log" uv run -q --no-project --with rdflib --with pyshacl --with neo4j --with "markdown-it-py>=4,<5" python3 "$HERE/validate.py" report "$BASELINE" "$OUT-release.json" "$OUT-compare.json" --out "$OUT-VALIDATION.md" > /dev/null || { tail -20 "$OUT-report.log"; exit 1; }; tail -1 "$OUT-report.log"
fi
NOT_RUN="$(python3 -c 'import sys; a=set(sys.argv[1].split(",")); print(", ".join(r for r in sys.argv[2].split(",") if r not in a) or "none")' "$STORE_ROWS" "$ALL_STORE_ROWS")"
step "done"; echo "release: $OUT; zip: $OUT.zip; store rows not run: $NOT_RUN (--store-rows all runs them when Databricks is reachable); remaining: step 9, $HERE/cleanup.py --ledger $LEDGER --env $ENVF --tree $OUT --yes, then, from the release's root, python3 business_architecture/ontology/projection/rebuild_stores.py --env <file> --empty; step 10, $HERE/publish.py branch --zip $OUT.zip --repo $EPM, then --push, the owner's decision"
