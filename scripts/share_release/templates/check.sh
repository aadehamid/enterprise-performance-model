#!/usr/bin/env bash
# The release's automated checks: every builder's --verify, the projection manifest, the competency regression,
# every test file, the module map and the coverage counts, and the generated pages. Run it from the release root
# before you change anything, and again after.
#
# Needs python3 and uv (https://docs.astral.sh/uv/) for the test dependencies.
#
# Compared with the repository this release was cut from, four checks are not here, because what they read did
# not ship: the Step 4 evidence gate and its tests (the review evidence of the process-map mapping), the Step 4
# pin check (Git history), the decision-record, quote, citation and name checks (the decision records and the
# saved review comments), and the pre-push hook test (no pull requests here). Every content check runs.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
while IFS= read -r var; do unset "$var"; done < <(compgen -e | grep '^GIT_' || true)
export PYTHONDONTWRITEBYTECODE=1
export EPM_SHARE_RELEASE=1   # the builders and tests read the release's layout: the newest set, and releases/previous/
run() { echo "--- $*"; "$@"; }
with_deps() { uv run -q --no-project --with pytest --with pytest-xdist --with rdflib --with pyshacl --with openpyxl --with jsonschema --with "markdown-it-py>=4,<5" "$@"; }

# Snapshot the tree, so a check that writes a file is caught.
snapshot() {
  python3 - <<'PY'
import hashlib, os
h = hashlib.sha256()
for root, dirs, files in os.walk("."):
    dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__", ".venv", ".pytest_cache"))
    for f in sorted(files):
        p = os.path.join(root, f)
        h.update(p.encode() + b"\0")
        with open(p, "rb") as fh:
            h.update(hashlib.sha256(fh.read()).digest())
print(h.hexdigest())
PY
}
before="$(snapshot)"

ONT=business_architecture/ontology
# The core package and each module's package must equal a fresh build (the newest set, EPM 1.0).
(cd $ONT/release && run with_deps python build_core_2_4.py --verify)
(cd $ONT/release && run with_deps python build_module.py organization --verify)
(cd $ONT/release && run with_deps python build_module.py kpi --verify)
(cd $ONT/release && run with_deps python build_module.py system --verify)
(cd $ONT/release && run with_deps python build_module.py party --verify)
(cd $ONT/release && run with_deps python build_module.py ref-mpc --verify)
(cd $ONT/release && run with_deps python build_module.py data-product --verify)
(cd $ONT/release && run with_deps python build_module.py value-stream --verify)
(cd $ONT/release && run with_deps python build_module.py lane --verify)
(cd $ONT/release && run with_deps python build_module.py market-data --verify)
(cd $ONT/release && run with_deps python build_module.py integration --verify)
(cd $ONT/release && run with_deps python build_catalog.py --verify)
# The competency questions the release can answer must still answer.
(cd $ONT/regression && run with_deps python run.py)
# Each module's source Turtle must equal a fresh build from its tables.
(cd $ONT/organization && run with_deps python build_roles.py --verify)
(cd $ONT/organization && run with_deps python build_assignments.py --verify)
(cd $ONT/kpi && run with_deps python build_measures.py --verify)
(cd $ONT/data-product && run with_deps python build_data_products.py --verify)
(cd $ONT/data-product && run with_deps python build_pricing.py --verify)
(cd $ONT/value-stream && run with_deps python build_value_streams.py --verify)
(cd $ONT/system && run with_deps python build_systems.py --verify)
(cd $ONT/lane && run with_deps python build_lanes.py --verify)
(cd $ONT/market-data && run with_deps python build_market_data.py --verify)
(cd $ONT/authority && run with_deps python build_source_tiers.py --verify)
(cd $ONT/apqc && run with_deps python build_apqc_elements.py --verify)
(cd $ONT/population && run with_deps python build_population.py --verify)
(cd $ONT/party && run with_deps python build_party.py --verify)
# The projection's checked, serialised inputs must match the manifest.
(cd $ONT/projection && run with_deps python pipeline.py build --verify)
# Every test file of the ontology, the demo and the scripts, in parallel (the list is written at the cut;
# test_check_script.py checks it is complete).
run with_deps python -m pytest -q -p no:cacheprovider -n "${CHECK_WORKERS:-auto}" --maxprocesses=8 --dist load \
{{TEST_FILES}}
# The four skills' own tests, each with the dependencies its own check names.
(cd skills/ontology/scripts && run uv run -q --no-project --with rdflib --with pyyaml --with pyshacl python3 -m unittest discover -q -p "test_*.py")
(cd skills/ontology && run uv run -q --no-project --with pyyaml python3 scripts/check_sssom.py templates/mappings.sssom.tsv)
(cd skills/ontology-to-lpg/scripts && run uv run -q --no-project --with rdflib --with pyshacl --with mcp-neo4j-data-modeling==0.8.2 python3 -m unittest -q test_projection test_engine_gate test_modeling test_explore test_run_projection)
(cd skills/rdf-store/scripts && run uv run -q --no-project --with pyoxigraph python3 -m unittest -q test_rdf_store)
(cd skills && run uv run -q --no-project --with "markdown-it-py>=4,<5" python3 scripts/test_playbook_html.py)
# The module map and the coverage counts run from the release folders.
run with_deps python scripts/epm_facts.py modules >/dev/null
run with_deps python scripts/epm_facts.py coverage >/dev/null
# The generated pages must equal a fresh build of their Markdown.
run with_deps python scripts/build_docs_html.py --check

after="$(snapshot)"
if [ "$before" != "$after" ]; then
  echo "the checks changed the tree; they must only read it" >&2
  exit 1
fi
echo "all checks passed"
