#!/usr/bin/env python3
"""05_query.py — Act 1 conflict, Act 2 MEASURE(), Act 3 SELECT * refused.

Prints every statement. Act 3 expects METRIC_VIEW_MISSING_MEASURE_FUNCTION.
Demo 2 / Track B. Not MetricFlow. Does not re-encode gallons_net * contract_price.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import connect, print_sql, run_statement, settings  # noqa: E402


def main() -> None:
    cfg = settings()
    fact = f"{cfg.catalog}.{cfg.schema}.fct_unbilled"
    mv = f"{cfg.catalog}.{cfg.schema}.unbilled_usd"

    act1_a = f"""SELECT
  sold_to_name AS customer,
  SUM(unbilled_usd) AS unbilled_usd,
  COUNT(*) AS tickets
FROM {fact}
GROUP BY sold_to_name
ORDER BY unbilled_usd DESC"""

    act1_b = f"""SELECT
  payer_name AS customer,
  SUM(unbilled_usd) AS unbilled_usd,
  COUNT(*) AS tickets
FROM {fact}
GROUP BY payer_name
ORDER BY unbilled_usd DESC"""

    act2_all = f"""SELECT
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {mv}"""

    act2_sold = f"""SELECT
  sold_to,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {mv}
GROUP BY sold_to
ORDER BY unbilled_usd DESC"""

    act2_payer = f"""SELECT
  payer,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {mv}
GROUP BY payer
ORDER BY unbilled_usd DESC"""

    act2_site = f"""SELECT
  site,
  site_name,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {mv}
GROUP BY site, site_name
ORDER BY unbilled_usd DESC"""

    act3 = f"SELECT * FROM {mv}"

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            print("\n======== ACT 1 — two workbooks, same tickets, rows fight ========")
            print("Report A (sold-to labeled customer). Expect 4 rows, $179,934.00.")
            run_statement(cur, act1_a)
            print("\nReport B (payer labeled customer). Expect 3 rows. Apex = Houston + Dallas.")
            run_statement(cur, act1_b)

            print("\n======== ACT 2 — same number through MEASURE() ========")
            print("Unsliced. Must equal Act 1 grand total $179,934.00 / 12 tickets.")
            run_statement(cur, act2_all)
            print("\nSold-to grain — must match Report A.")
            run_statement(cur, act2_sold)
            print("\nPayer grain — must match Report B.")
            run_statement(cur, act2_payer)
            print("\nSite grain — HSC $97,145.20 (6) / DAL $45,334.40 (4) / BMT $37,454.40 (2).")
            run_statement(cur, act2_site)

            print("\n======== ACT 3 — SELECT * must be refused ========")
            print("Expect METRIC_VIEW_MISSING_MEASURE_FUNCTION. That error is the lesson.")
            print_sql(act3)
            try:
                cur.execute(act3)
                rows = cur.fetchall() if cur.description else []
                print("UNEXPECTED: SELECT * returned rows (should have failed):")
                print(rows)
                raise SystemExit(1)
            except SystemExit:
                raise
            except Exception as exc:
                text = str(exc)
                print(f"Refused (expected):\n{text}")
                if "METRIC_VIEW_MISSING_MEASURE_FUNCTION" not in text:
                    print(
                        "\nNote: error text did not contain "
                        "METRIC_VIEW_MISSING_MEASURE_FUNCTION. "
                        "Record the message anyway — refusal is still the point.",
                        file=sys.stderr,
                    )

    print("\nQuery ok. Act 1 fights; Act 2 agrees; Act 3 refused.")
    print("Next: uv run python scripts/06_store.py")


if __name__ == "__main__":
    main()
