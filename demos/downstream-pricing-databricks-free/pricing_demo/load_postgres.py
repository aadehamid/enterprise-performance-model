"""Load the generated source tables into Postgres, one database per source system.

    uv run python -m pricing_demo.load_postgres

Each database loads in one transaction: its tables are dropped, recreated and filled, and the row counts checked,
before the commit. A failure rolls the whole database back, so a reader never sees an empty or half-loaded table
(Kimi round 1, finding 20). SOURCE_PG_DSN names the server.
"""
import datetime as dt
import decimal

from . import generate
from .config import HIDDEN_SYSTEMS, SYSTEMS, source_dsn


def pg_type(values):
    sample = next((v for v in values if v is not None), None)
    if isinstance(sample, bool):
        return "boolean"
    if isinstance(sample, int):
        return "bigint"
    if isinstance(sample, (float, decimal.Decimal)) or sample is None:
        return "numeric(18,6)"  # an all-null column (the unused high and low prices) is numeric, as its source is
    if isinstance(sample, dt.datetime):
        return "timestamp"
    if isinstance(sample, dt.date):
        return "date"
    return "text"


def load_database(conn, system_tables):
    """Load one database's tables inside the caller's transaction, and check every count."""
    for name, table in system_tables.items():
        cols = ", ".join(f'"{c}" {pg_type([r[i] for r in table.rows])}' for i, c in enumerate(table.columns))
        conn.execute(f'DROP TABLE IF EXISTS "{name}"')
        conn.execute(f'CREATE TABLE "{name}" ({cols})')
        with conn.cursor().copy(f'COPY "{name}" ({", ".join(chr(34) + c + chr(34) for c in table.columns)}) FROM STDIN') as copy:
            for row in table.rows:
                copy.write_row(row)
        n = conn.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
        if n != len(table.rows):
            raise RuntimeError(f"{name}: loaded {n} rows of {len(table.rows)}")
        print(f"{name}: {n} rows")


def load(tables=None):
    import psycopg
    tables = tables or generate.build()
    base = source_dsn().rstrip("/")
    for system in list(SYSTEMS) + list(HIDDEN_SYSTEMS):  # the hidden ones too: loaded, never replicated
        with psycopg.connect(f"{base}/{system}") as conn:  # one transaction per database; an error rolls it back
            load_database(conn, tables[system])
            conn.commit()


if __name__ == "__main__":
    load()
