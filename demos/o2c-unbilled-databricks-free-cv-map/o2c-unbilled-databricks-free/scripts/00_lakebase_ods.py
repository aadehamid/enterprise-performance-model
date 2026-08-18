#!/usr/bin/env python3
"""00_lakebase_ods.py — Act 0 ODS on existing Lakebase project dataexpert-day1.

CREATE SCHEMA IF NOT EXISTS o2c_unbilled
Create ops tables; load data/*.csv via psycopg.
Refuse if LAKEBASE_PASSWORD is missing.
Never DROP other schemas. Never write into other day1 schemas.
Do not create a second Lakebase project.
Demo 2 / Track B. Not MetricFlow.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (  # noqa: E402
    ALLOWED_LAKEBASE_DATABASE,
    ALLOWED_LAKEBASE_PROJECT,
    ALLOWED_LAKEBASE_SCHEMA,
    DATA_DIR,
    EXPECTED_OPS,
    TABLES,
    lakebase_connect,
    lakebase_settings,
    pg_type,
    print_grid,
    print_sql,
)
from psycopg import sql


def _ident(*parts: str) -> sql.Composed:
    return sql.SQL(".").join(sql.Identifier(p) for p in parts)


def main() -> None:
    lb = lakebase_settings()
    if lb.schema != ALLOWED_LAKEBASE_SCHEMA or lb.database != ALLOWED_LAKEBASE_DATABASE:
        raise SystemExit("refusing: Act 0 is locked to dataexpert-day1 / databricks_postgres / o2c_unbilled")

    print("Act 0 Lakebase ODS")
    print(f"  project   = {ALLOWED_LAKEBASE_PROJECT}  (existing — do not create another)")
    print(f"  host      = {lb.host}")
    print(f"  database  = {lb.database}")
    print(f"  schema    = {lb.schema}  (only this schema; never DROP others)")
    print(f"  user      = {lb.user}")
    print("  password  = (set, not printed)")

    counts: dict[str, int] = {}
    with lakebase_connect(lb) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            create_schema = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                sql.Identifier(lb.schema)
            )
            print_sql(create_schema.as_string(conn))
            cur.execute(create_schema)

            for csv_name, ops_table, _raw, cols in TABLES:
                col_defs = sql.SQL(", ").join(
                    sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(pg_type(typ)))
                    for name, typ, _kind in cols
                )
                create_tbl = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                    _ident(lb.schema, ops_table),
                    col_defs,
                )
                print_sql(create_tbl.as_string(conn))
                cur.execute(create_tbl)

                # Reload this table only. Never DROP SCHEMA. Never touch other schemas.
                trunc = sql.SQL("TRUNCATE TABLE {}").format(_ident(lb.schema, ops_table))
                print_sql(trunc.as_string(conn))
                cur.execute(trunc)

                path = DATA_DIR / csv_name
                with path.open(newline="", encoding="utf-8") as fh:
                    rows = list(csv.DictReader(fh))
                names = [c[0] for c in cols]
                placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in names)
                insert = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    _ident(lb.schema, ops_table),
                    sql.SQL(", ").join(sql.Identifier(n) for n in names),
                    placeholders,
                )
                print_sql(insert.as_string(conn) + f"  -- {len(rows)} rows from {csv_name}")
                payload = [tuple(row[n] if row[n] != "" else None for n in names) for row in rows]
                cur.executemany(insert, payload)

                count_sql = sql.SQL("SELECT COUNT(*) FROM {}").format(_ident(lb.schema, ops_table))
                print_sql(count_sql.as_string(conn))
                cur.execute(count_sql)
                n = int(cur.fetchone()[0])
                counts[ops_table] = n
                print(f"  {lb.schema}.{ops_table} = {n}")

        conn.commit()

    print()
    print_grid(["ops_table", "n"], [(k, counts[k]) for k in sorted(counts)])
    bad = [t for t, n in EXPECTED_OPS.items() if counts.get(t) != n]
    if bad:
        print(f"\nRow-count mismatch: {bad}. Expected {EXPECTED_OPS}.", file=sys.stderr)
        raise SystemExit(1)
    print("\nAct 0 ODS ok (8 / 10 / 3 / 3 / 19 / 6 / 6) in o2c_unbilled only.")
    print("Next: uv run python scripts/00b_land_replica.py")


if __name__ == "__main__":
    main()
