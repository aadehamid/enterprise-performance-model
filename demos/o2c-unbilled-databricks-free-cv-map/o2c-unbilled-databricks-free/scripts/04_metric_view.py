#!/usr/bin/env python3
"""04_metric_view.py — runner of the live-proven YAML 0.1 Metric View.

Sends the same version 0.1 (fields + measures only) as sql/03_metric_view.sql.
Fails the job if 03 diverges from this 0.1 (no YAML 1.1 comment /
display_name / synonyms). Live-proven on Databricks Free 2026-08-14.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import PACK_ROOT, connect, run_statement, settings  # noqa: E402

FORBIDDEN_01 = ("comment:", "display_name:", "synonyms:", "version: 1.1")


def expected_yaml(catalog: str, schema: str) -> str:
    source = f"{catalog}.{schema}.fct_unbilled"
    return f"""version: 0.1
source: {source}
fields:
  - name: payer
    expr: source.payer_name
  - name: sold_to
    expr: source.sold_to_name
  - name: site
    expr: source.site_code
  - name: site_name
    expr: source.site_name
  - name: as_of
    expr: source.as_of_date
  - name: delivery_date
    expr: source.delivery_date
  - name: product
    expr: source.product_code
measures:
  - name: unbilled_usd
    expr: SUM(source.unbilled_usd)
  - name: unbilled_ticket_count
    expr: COUNT(1)
"""


def normalize_yaml(text: str) -> str:
    lines = [ln.rstrip() for ln in text.strip().splitlines()]
    return "\n".join(ln for ln in lines if ln.strip())


def extract_yaml_block(sql_text: str) -> str:
    match = re.search(r"AS\s+\$\$(.*?)\$\$", sql_text, flags=re.S | re.I)
    if not match:
        raise SystemExit("sql/03_metric_view.sql: missing AS $$ … $$ YAML block")
    return match.group(1)


def assert_dialect_01(yaml_text: str) -> None:
    low = yaml_text.lower()
    for token in FORBIDDEN_01:
        if token in low:
            raise SystemExit(
                f"sql/03_metric_view.sql is not live-proven 0.1: found {token!r}. "
                "fields + measures only; no YAML 1.1 agent metadata."
            )
    if "version: 0.1" not in yaml_text:
        raise SystemExit("sql/03_metric_view.sql must declare version: 0.1")


def metric_view_sql(catalog: str, schema: str) -> str:
    """CREATE statement from sql/03_metric_view.sql; fail if it is not 0.1."""
    path = PACK_ROOT / "sql" / "03_metric_view.sql"
    raw = path.read_text(encoding="utf-8")
    # Substitute only the two pack tokens — do not need a live Settings here.
    substituted = raw.replace("{{catalog}}", catalog).replace("{{schema}}", schema)
    authored = extract_yaml_block(substituted)
    assert_dialect_01(authored)
    expected = expected_yaml(catalog, schema)
    if normalize_yaml(authored) != normalize_yaml(expected):
        raise SystemExit(
            "sql/03_metric_view.sql YAML diverges from live-proven 0.1 in "
            "scripts/04_metric_view.py. One compile dialect only."
        )
    view = f"{catalog}.{schema}.unbilled_usd"
    return f"""CREATE OR REPLACE VIEW {view}
WITH METRICS
LANGUAGE YAML
AS $$
{expected.rstrip()}
$$"""


def main() -> None:
    cfg = settings()
    stmt = metric_view_sql(cfg.catalog, cfg.schema)
    if stmt.count("$$") != 2:
        raise SystemExit("Metric View YAML must be a single $$ … $$ block")
    print(f"Creating {cfg.fq}.unbilled_usd  (version 0.1, one statement)")
    print("Runner of sql/03_metric_view.sql — same 0.1 dialect.")

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            run_statement(cur, stmt, fetch=False)
            run_statement(cur, f"DESCRIBE TABLE EXTENDED {cfg.fq}.unbilled_usd")

    print("\nMetric View ok. Next: uv run python scripts/05_query.py")


if __name__ == "__main__":
    main()
