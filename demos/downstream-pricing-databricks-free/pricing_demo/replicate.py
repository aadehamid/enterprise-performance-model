"""Replicate every source table to Parquet with DuckDB, the way a replication job lands a replica.

    uv run python -m pricing_demo.replicate [--since 2026-10-01T00:00:00]

DuckDB's postgres extension reads each database named by SOURCE_PG_DSN and writes out/replica/<system>/<table>.parquet
with two columns added: _change_ts (the source row's updated_at, the change timestamp) and _replicated_at. With
--since, only rows changed after that time are written, which is how an incremental run works.
"""
import argparse
import datetime as dt
import os

import duckdb

from .config import OUT, source_dsn

SYSTEMS = ("mips", "mpr", "kittyhawk", "ctrm", "planning", "prodacct")


def replicate(since=None, replicated_at=None):
    replicated_at = replicated_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0, tzinfo=None)
    con = duckdb.connect()
    con.execute("INSTALL postgres; LOAD postgres;")
    base = source_dsn().rstrip("/")
    written = {}
    for system in SYSTEMS:
        con.execute(f"ATTACH '{base}/{system}' AS {system} (TYPE postgres, READ_ONLY)")
        tables = [r[0] for r in con.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_catalog = '{system}' AND table_schema = 'public'").fetchall()]
        folder = os.path.join(OUT, "replica", system)
        os.makedirs(folder, exist_ok=True)
        for table in sorted(tables):
            where = f"WHERE updated_at > TIMESTAMP '{since}'" if since else ""
            path = os.path.join(folder, f"{table}.parquet")
            con.execute(f"""COPY (SELECT *, updated_at AS _change_ts, TIMESTAMP '{replicated_at}' AS _replicated_at
                            FROM {system}.public."{table}" {where}) TO '{path}' (FORMAT parquet)""")
            n = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
            written[f"{system}.{table}"] = n
            print(f"{system}.{table}: {n} rows -> {os.path.relpath(path, OUT)}")
        con.execute(f"DETACH {system}")
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    replicate(ap.parse_args().since)
