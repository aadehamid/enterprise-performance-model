#!/usr/bin/env bash
# End-to-end demo: generate seeds → dbt → conflicting reports → MetricFlow.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if ! command -v dbt >/dev/null 2>&1; then
  echo "dbt not found. Activate the venv:  source .venv/bin/activate" >&2
  exit 1
fi
if ! command -v mf >/dev/null 2>&1; then
  echo "mf not found. Activate the venv:  source .venv/bin/activate" >&2
  echo "which mf should be .venv/bin/mf" >&2
  exit 1
fi

export DBT_PROFILES_DIR="$ROOT"
export DBT_TARGET="${DBT_TARGET:-dev}"

echo "==> 1. Generate seed CSVs (deterministic seed=42)"
python scripts/generate_data.py

echo
echo "==> 2. dbt seed / run / parse"
dbt seed --target dev
dbt run --target dev
dbt parse --target dev

echo
echo "==> 3. Act 1 — three reports named Unbilled USD"
python scripts/act1_reports.py

echo
echo "==> 4. Act 2 — metadata 1 row, grain on the fact"
python scripts/act2_grain.py

echo
echo "==> 5. Act 3 — MetricFlow (one metric, many slices)"
echo "    Ignore any CLI nag to upgrade dbt-metricflow to 0.13.0."
echo "    0.13 is a different line and will break this project's YAML."
echo "    MetricFlow prefixes categorical dimensions with the primary entity,"
echo "    so group-by names are ticket__sold_to / ticket__payer / ticket__terminal."
echo "    ticket__ is compiler namespacing, not a claim that sold-to is a child of ticket."
echo
echo "--- mf list metrics ---"
mf list metrics

echo
echo "--- mf query --metrics unbilled_usd --explain ---"
mf query --metrics unbilled_usd --explain

echo
echo "--- mf query --metrics unbilled_usd --decimals 2 ---"
mf query --metrics unbilled_usd --decimals 2

echo
echo "--- mf query --metrics unbilled_usd --group-by ticket__sold_to --decimals 2 ---"
mf query --metrics unbilled_usd --group-by ticket__sold_to --decimals 2

echo
echo "--- mf query --metrics unbilled_usd --group-by ticket__payer --decimals 2 ---"
mf query --metrics unbilled_usd --group-by ticket__payer --decimals 2

echo
echo "--- mf query --metrics unbilled_usd --group-by ticket__sold_to,ticket__terminal,metric_time__day --decimals 2 ---"
mf query --metrics unbilled_usd --group-by ticket__sold_to,ticket__terminal,metric_time__day --decimals 2

echo
echo "Demo finished. Certified unbilled_usd is the same ticket set as Report A/B."
echo "Report C stays different because it never used fct_unbilled / the metric."
echo "Act 1 A/B already query the fact. Act 3 is the same number through mf query."
