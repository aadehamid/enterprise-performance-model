#!/usr/bin/env bash
# Run the repo's automated checks: the Step 4 evidence gate, every test script,
# epm-facts counts, and the decision-record check. CI and the pre-push hook run
# this file; run it yourself before opening a pull request.
#
# Needs python3 and uv (https://docs.astral.sh/uv/) for the test dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
run() { echo "--- $*"; "$@"; }
with_deps() { uv run -q --with pytest --with rdflib --with openpyxl "$@"; }

# Snapshot the tree: status lines plus the content of every modified or untracked
# file, so a check that rewrites a file that was already modified is caught too.
# Python, so that any git or read error raises and stops this script.
snapshot() {
  python3 - <<'PY'
import hashlib, os, subprocess
h = hashlib.sha256()
h.update(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"]))
names = subprocess.check_output(["git", "ls-files", "-z", "-m", "-o", "--exclude-standard"]).split(b"\0")
for name in sorted(n for n in names if n):
    h.update(name + b"\0")
    path = os.fsdecode(name)
    if os.path.lexists(path):
        with open(path, "rb") as f:
            h.update(hashlib.sha256(f.read()).digest())
    else:
        h.update(b"deleted")
print(h.hexdigest())
PY
}
before="$(snapshot)"

step4="business_architecture/ontology/step4"
(cd "$step4" && run python3 evidence-gate.py | tail -1)
for t in "$step4/test_mapping_v2_regression.py" "$step4/test_ledger_v2_census.py" \
         "$step4/test_script_portability.py" "$step4/target-report/test_context_pass.py" \
         "business_architecture/ontology/build/scripts/test_step3c_workbook_validate.py"; do
  (cd "$(dirname "$t")" && echo "--- $t" && with_deps python "$(basename "$t")" >/dev/null)
done
run with_deps python -m pytest -q -p no:cacheprovider scripts/test_epm_facts.py
run python3 scripts/epm_facts.py decisions
run with_deps python scripts/epm_facts.py counts >/dev/null

after="$(snapshot)"  # a standalone assignment, so a failing snapshot stops the script
if [ "$before" != "$after" ]; then
  echo "the checks changed the working tree; they must only read it:" >&2
  git status --short >&2
  exit 1
fi
echo "all checks passed"
