#!/usr/bin/env python3
"""02_load.py — CREATE SCHEMA + load data/*.csv into raw_* tables.

Shortcut that skips Act 0 Lakebase. Idempotent CREATE OR REPLACE + VALUES.
Prefer 00_lakebase_ods.py → 00b_land_replica.py when using dataexpert-day1.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (  # noqa: E402
    DATA_DIR,
    EXPECTED_RAW,
    TABLES,
    connect,
    run_statement,
    settings,
    values_as_select,
)


def main() -> None:
    cfg = settings()
    print(f"Load CSVs from {DATA_DIR} → {cfg.fq}.raw_*  (CREATE OR REPLACE, idempotent)")
    print("Shortcut: skips Lakebase. Act 0 path is 00 → 00b → 03.")

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            run_statement(
                cur,
                f"CREATE SCHEMA IF NOT EXISTS {cfg.fq}\n"
                "COMMENT 'O2C Unbilled USD demo 2 — Databricks Free. "
                "Not the Track A DuckDB pack.'",
                fetch=False,
            )
            for csv_name, _ops, raw_table, cols in TABLES:
                path = DATA_DIR / csv_name
                with path.open(newline="", encoding="utf-8") as fh:
                    rows = list(csv.DictReader(fh))
                fq = f"{cfg.catalog}.{cfg.schema}.{raw_table}"
                run_statement(cur, values_as_select(fq, cols, rows), fetch=False)

            sanity = (
                " UNION ALL ".join(
                    f"SELECT '{raw}' AS tbl, COUNT(*) AS n "
                    f"FROM {cfg.catalog}.{cfg.schema}.{raw}"
                    for _c, _o, raw, _cols in TABLES
                )
                + " ORDER BY 1"
            )
            rows = run_statement(cur, sanity)

    got = {str(r[0]): int(r[1]) for r in rows}
    bad = [t for t, n in EXPECTED_RAW.items() if got.get(t) != n]
    if bad:
        print(f"\nRow-count mismatch: {bad}. Expected {EXPECTED_RAW}.", file=sys.stderr)
        raise SystemExit(1)
    print("\nLoad ok (8 / 10 / 3 / 3 / 19 / 6 / 6). Next: uv run python scripts/03_facts.py")


if __name__ == "__main__":
    main()
