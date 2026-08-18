#!/usr/bin/env python3
"""00b_land_replica.py — copy Lakebase ODS → Databricks raw_* (no federated join).

Read o2c_unbilled ops tables from existing Lakebase project dataexpert-day1.
Write workspace.o2c_unbilled.raw_* via the Databricks SQL connector.
Python is the pipe. Do not query Lakebase from Databricks.
Then facts + metric view stay scripts/03 and 04.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (  # noqa: E402
    ALLOWED_LAKEBASE_SCHEMA,
    EXPECTED_RAW,
    TABLES,
    connect,
    lakebase_connect,
    lakebase_settings,
    run_statement,
    settings,
    values_as_select,
)
from psycopg import sql


def main() -> None:
    lb = lakebase_settings()
    cfg = settings()
    if lb.schema != ALLOWED_LAKEBASE_SCHEMA:
        raise SystemExit("refusing: only schema o2c_unbilled")

    print("Act 0b land replica  (Lakebase → Databricks raw_*; no federated join)")
    print(f"  lakebase  = {lb.host} / {lb.database}.{lb.schema}")
    print(f"  warehouse = {cfg.server_hostname} / {cfg.fq}.raw_*")
    print("  token/password = (set, not printed)")

    pulled: dict[str, list] = {}
    with lakebase_connect(lb) as pg:
        with pg.cursor() as cur:
            for _csv, ops_table, raw_table, cols in TABLES:
                names = [c[0] for c in cols]
                q = sql.SQL("SELECT {} FROM {}").format(
                    sql.SQL(", ").join(sql.Identifier(n) for n in names),
                    sql.SQL(".").join(sql.Identifier(p) for p in (lb.schema, ops_table)),
                )
                print()
                print(f"── Lakebase read {lb.schema}.{ops_table} → {raw_table}")
                print(q.as_string(pg))
                cur.execute(q)
                rows = cur.fetchall()
                print(f"  ({len(rows)} rows)")
                pulled[raw_table] = rows

    with connect(cfg) as conn:
        with conn.cursor() as cur:
            run_statement(
                cur,
                f"CREATE SCHEMA IF NOT EXISTS {cfg.fq}\n"
                "COMMENT 'O2C Unbilled USD demo 2 — Databricks Free. "
                "Not the Track A DuckDB pack.'",
                fetch=False,
            )
            for _csv, _ops, raw_table, cols in TABLES:
                fq = f"{cfg.catalog}.{cfg.schema}.{raw_table}"
                stmt = values_as_select(fq, cols, pulled[raw_table])
                run_statement(cur, stmt, fetch=False)

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
    print("\nReplica ok (8 / 10 / 3 / 3 / 19 / 6 / 6). Skip 02_load.py.")
    print("Next: uv run python scripts/03_facts.py")


if __name__ == "__main__":
    main()
