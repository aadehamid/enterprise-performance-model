#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the enterprise-performance-model repo.
#
# All runnable code lives under demos/:
#   Track A  demos/o2c-unbilled-semantic-layer            (local: DuckDB + dbt + MetricFlow, no secrets)
#   Track B  demos/.../o2c-unbilled-databricks-free       (cloud: needs Databricks Free secrets to run)
#
# This script prepares both Python environments. Track A is fully runnable offline;
# Track B installs its deps so scripts import, but running it end-to-end needs
# DATABRICKS_* / LAKEBASE_* secrets supplied via the dashboard.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- uv (pinned Python + fast installs) -------------------------------------
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

# --- Track A: local semantic-layer demo (dbt + MetricFlow over DuckDB) ------
TRACK_A="$REPO_ROOT/demos/o2c-unbilled-semantic-layer"
echo "==> Track A: $TRACK_A"
cd "$TRACK_A"
[ -d .venv ] || uv venv --python 3.12
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -r requirements.txt
chmod +x scripts/demo.sh
dbt --version
mf --version || true
deactivate

# --- Track B: Databricks Free demo (deps only; run needs cloud secrets) -----
TRACK_B="$REPO_ROOT/demos/o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free"
echo "==> Track B: $TRACK_B"
cd "$TRACK_B"
uv sync

echo "==> Install complete. Run the Track A demo with:"
echo "    cd demos/o2c-unbilled-semantic-layer && source .venv/bin/activate && ./scripts/demo.sh"
