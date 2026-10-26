"""Load the generated source tables into Postgres, one database per source system.

    uv run python -m pricing_demo.load_postgres

Each table is dropped and recreated, so a rerun gives the same rows. SOURCE_PG_DSN names the server.
"""
import datetime as dt
import decimal

import psycopg

from . import generate
from .config import source_dsn


def pg_type(values):
    sample = next((v for v in values if v is not None), None)
    if isinstance(sample, bool):
        return "boolean"
    if isinstance(sample, int):
        return "bigint"
    if isinstance(sample, (float, decimal.Decimal)):
        return "numeric(18,6)"
    if isinstance(sample, dt.datetime):
        return "timestamp"
    if isinstance(sample, dt.date):
        return "date"
    return "text"


def load(tables=None):
    tables = tables or generate.build()
    base = source_dsn().rstrip("/")
    for system, system_tables in tables.items():
        with psycopg.connect(f"{base}/{system}", autocommit=True) as conn:
            for name, table in system_tables.items():
                cols = ", ".join(f'"{c}" {pg_type([r[i] for r in table.rows])}' for i, c in enumerate(table.columns))
                conn.execute(f'DROP TABLE IF EXISTS "{name}"')
                conn.execute(f'CREATE TABLE "{name}" ({cols})')
                with conn.cursor().copy(f'COPY "{name}" ({", ".join(chr(34) + c + chr(34) for c in table.columns)}) FROM STDIN') as copy:
                    for row in table.rows:
                        copy.write_row(row)
                print(f"{system}.{name}: {len(table.rows)} rows")


if __name__ == "__main__":
    load()
