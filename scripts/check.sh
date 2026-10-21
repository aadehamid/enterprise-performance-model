#!/usr/bin/env bash
# Run the repo's automated checks: the Step 4 evidence gate, the scoped-sequence
# build and SHACL check, the Step 11 competency regression, every test script, epm-facts counts, the decision-record
# and quote checks, the check that no tracked file names the decision owner, and the Step 4 pin check. CI and the pre-push hook run this
# file; run it yourself before opening a pull request.
#
# Needs python3 and uv (https://docs.astral.sh/uv/) for the test dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
run() { echo "--- $*"; "$@"; }
with_deps() { uv run -q --with pytest --with rdflib --with pyshacl --with openpyxl --with jsonschema --with "markdown-it-py>=4,<5" "$@"; }

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
for t in "$step4/test_mapping_v2_regression.py" "$step4/test_ledger_v2_census.py" "$step4/test_batch_checks.py" "$step4/test_phase1_batch.py" "$step4/test_mirror_verbs.py" \
         "$step4/test_g1b_removed_facts.py" \
         "$step4/test_script_portability.py" "$step4/target-report/test_context_pass.py" "$step4/target-report/test_classify_v2.py" \
         "business_architecture/ontology/build/scripts/test_step3c_workbook_validate.py" \
         "business_architecture/ontology/build/scripts/test_scope_note_append.py" \
         "business_architecture/ontology/build/scripts/test_relation_correct.py"; do
  (cd "$(dirname "$t")" && echo "--- $t" && with_deps python "$(basename "$t")" >/dev/null)
done
(cd "$step4/scoped-sequence" && run with_deps python build.py --verify)
# The core release package (EPM-DEC-001-0029) must equal a fresh build from the pinned evidence.
(cd business_architecture/ontology/release && run with_deps python build_core.py --verify)
# Step 10: the module release packages must equal a fresh build (EPM-DEC-001-0037).
(cd business_architecture/ontology/release && run with_deps python build_module.py organization --verify)
(cd business_architecture/ontology/release && run with_deps python build_module.py ref-mpc --verify)
(cd business_architecture/ontology/release && run with_deps python build_module.py kpi --verify)
# The core 2.0.0 release must equal a fresh build from core 1.0.0 (EPM-DEC-001-0038).
(cd business_architecture/ontology/release && run with_deps python build_core_next.py --verify)
# Step 9: core 2.1.0, with one evidence node per canonical fact, must equal a fresh build from 2.0.0 (EPM-DEC-001-0044).
(cd business_architecture/ontology/release && run with_deps python build_core_2_1.py --verify)
# Step 11: the competency questions the release can answer must still answer (EPM-DEC-001-0019).
(cd business_architecture/ontology/regression && run with_deps python run.py)
# Step 5: the role register must reconcile with the process map's RACI strings (EPM-DEC-001-0031).
(cd business_architecture/ontology/organization && run with_deps python build_roles.py --verify)
# Step 5: the RACI assignments must equal a fresh build, with a ledger that reconciles (EPM-DEC-001-0032).
(cd business_architecture/ontology/organization && run with_deps python build_assignments.py --verify)
# Step 7: the kpi module's measures must equal a fresh build from its tables (EPM-DEC-001-0043).
(cd business_architecture/ontology/kpi && run with_deps python build_measures.py --verify)
# Step 7: the data-product module must equal a fresh build from the portfolio (EPM-DEC-001-0053).
(cd business_architecture/ontology/data-product && run with_deps python build_data_products.py --verify)
# Step 7: the value-stream module must equal a fresh build from the two value streams (EPM-DEC-001-0054).
(cd business_architecture/ontology/value-stream && run with_deps python build_value_streams.py --verify)
# Step 7: the system module must equal a fresh build from the process map's systems fields (EPM-DEC-001-0055).
(cd business_architecture/ontology/system && run with_deps python build_systems.py --verify)
# Step 7: the lane module must equal a fresh build from office_lanes.json and the map (EPM-DEC-001-0056).
(cd business_architecture/ontology/lane && run with_deps python build_lanes.py --verify)
# Step 7: the market-data module must equal a fresh build from its tables (EPM-DEC-001-0057).
(cd business_architecture/ontology/market-data && run with_deps python build_market_data.py --verify)
# Step 9: the source tiers must equal a fresh build from their table (EPM-DEC-001-0059).
(cd business_architecture/ontology/authority && run with_deps python build_source_tiers.py --verify)
# Step 7: the APQC element list must equal a fresh build from the vendored workbook (EPM-DEC-001-0060).
(cd business_architecture/ontology/apqc && run with_deps python build_apqc_elements.py --verify)
# Step 7: the measure populations must equal a fresh build from their table (EPM-DEC-001-0062).
(cd business_architecture/ontology/population && run with_deps python build_population.py --verify)
# Steps 5 to 7: the `party` module's code lists must equal a fresh build from their table (EPM-DEC-001-0068).
(cd business_architecture/ontology/party && run with_deps python build_party.py --verify)
# Step 12: the projection's checked, serialised inputs must match the committed manifest (EPM-DEC-001-0036).
(cd business_architecture/ontology/projection && run with_deps python pipeline.py build --verify)
run with_deps python -m pytest -q -p no:cacheprovider scripts/test_epm_facts.py scripts/test_published_figures.py \
  "$step4/scoped-sequence/test_scoped_sequences.py" business_architecture/ontology/release/test_build_core.py \
  business_architecture/ontology/release/test_build_module.py \
  business_architecture/ontology/release/test_build_core_next.py \
  business_architecture/ontology/release/test_build_core_2_1.py \
  business_architecture/ontology/regression/test_run.py business_architecture/ontology/organization/test_vocabulary.py \
  business_architecture/ontology/organization/test_roles.py \
  business_architecture/ontology/organization/test_assignments.py \
  business_architecture/ontology/ref-mpc/test_ref_mpc.py \
  business_architecture/ontology/kpi/test_measures.py \
  business_architecture/ontology/data-product/test_data_products.py \
  business_architecture/ontology/value-stream/test_value_streams.py \
  business_architecture/ontology/system/test_systems.py \
  business_architecture/ontology/lane/test_lanes.py \
  business_architecture/ontology/market-data/test_market_data.py \
  business_architecture/ontology/placement/test_placement.py \
  business_architecture/ontology/authority/test_source_tiers.py \
  business_architecture/ontology/apqc/test_apqc_elements.py \
  business_architecture/ontology/consumer/test_consumer_rules.py \
  business_architecture/ontology/population/test_population.py \
  business_architecture/ontology/party/test_party.py \
  business_architecture/business_process/test_business_process.py \
  business_architecture/ontology/provenance/test_run_shapes.py \
  business_architecture/ontology/validation/test_controlled_values.py \
  business_architecture/ontology/validation/test_all_module_shapes.py \
  business_architecture/ontology/projection/test_pipeline.py
run python3 scripts/epm_facts.py decisions
run with_deps python scripts/epm_facts.py quotes
# EPM-DEC-001-0049: the repo names the decision owner by role, never by name or account.
run python3 scripts/epm_facts.py names
# The Step 4 pin must name a commit in this branch's history. A squash or rebase
# merge of the pinning PR leaves it off main (PR #225, re-pinned in #227).
pin="$(cat "$step4/PINNED_SHA.txt")"
echo "--- Step 4 pin $pin is in HEAD's history"
git merge-base --is-ancestor "$pin" HEAD || { echo "PINNED_SHA $pin is not an ancestor of HEAD; re-pin Step 4" >&2; exit 1; }
run with_deps python scripts/epm_facts.py counts >/dev/null

after="$(snapshot)"  # a standalone assignment, so a failing snapshot stops the script
if [ "$before" != "$after" ]; then
  echo "the checks changed the working tree; they must only read it:" >&2
  git status --short >&2
  exit 1
fi
echo "all checks passed"
