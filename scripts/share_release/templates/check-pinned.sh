#!/usr/bin/env bash
# Optional. Does this tree still equal {{RELEASE_NAME}} as it was shipped? It runs only the tests in scripts/pinned-tests.txt.
# On the release as shipped they pass. After your first change some are expected to fail, which says your copy has
# moved on and nothing more. Run scripts/check.sh to see whether your copy is valid.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
while IFS= read -r var; do unset "$var"; done < <(compgen -e | grep '^GIT_' || true)
export PYTHONDONTWRITEBYTECODE=1 EPM_SHARE_RELEASE=1 EPM_PINNED_ONLY=1
files="$(grep -v '^#' scripts/pinned-tests.txt | cut -d: -f1 | sort -u)"
# shellcheck disable=SC2086
uv run -q --no-project --with pytest --with rdflib --with pyshacl --with openpyxl --with jsonschema --with "markdown-it-py>=4,<5" \
  python -m pytest -q -p no:cacheprovider --rootdir "$ROOT" --confcutdir "$ROOT" $files
