"""Replicate every source table to Parquet with DuckDB, the way a replication job lands a full snapshot.

    uv run python -m pricing_demo.replicate

DuckDB's postgres extension reads each database named by SOURCE_PG_DSN and writes out/replica/<system>/<table>.parquet
with two columns added: _change_ts (the source row's updated_at) and _replicated_at. Every run is a full snapshot:
the downstream layers replace their contents from these files, so a partial (incremental) file would delete rows
(Kimi round 1, finding 7). The run writes into a staging folder, checks that every expected table is there and not
empty, writes manifest.json with each table's row count, and only then replaces out/replica (finding 5).
"""
import datetime as dt
import json
import os
import shutil

from . import generate
from .config import OUT, SYSTEMS, source_dsn

REPLICA = os.path.join(OUT, "replica")


def expected_tables():
    """{system: [table, ...]} from the generator, the one registry of source tables (finding 22)."""
    return {system: sorted(tables) for system, tables in generate.build().items()}


def replicate(replicated_at=None):
    replicated_at = replicated_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0, tzinfo=None)
    expected = expected_tables()
    import duckdb
    staging = REPLICA + ".staging"
    shutil.rmtree(staging, ignore_errors=True)
    con = duckdb.connect()
    con.execute("INSTALL postgres; LOAD postgres;")
    base = source_dsn().rstrip("/")
    manifest = {}
    for system in SYSTEMS:
        con.execute(f"ATTACH '{base}/{system}' AS {system} (TYPE postgres, READ_ONLY)")
        found = {r[0] for r in con.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_catalog = '{system}' AND table_schema = 'public'").fetchall()}
        missing = set(expected[system]) - found
        if missing:
            raise SystemExit(f"{system}: source tables missing: {sorted(missing)}; run load_postgres first")
        folder = os.path.join(staging, system)
        os.makedirs(folder, exist_ok=True)
        for table in expected[system]:
            path = os.path.join(folder, f"{table}.parquet")
            con.execute(f"""COPY (SELECT *, updated_at AS _change_ts, TIMESTAMP '{replicated_at}' AS _replicated_at
                            FROM {system}.public."{table}") TO '{path}' (FORMAT parquet)""")
            n = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
            if n == 0:
                raise SystemExit(f"{system}.{table}: the source table is empty; nothing replaced")
            manifest[f"{system}/{table}"] = n
            print(f"{system}.{table}: {n} rows")
        con.execute(f"DETACH {system}")
    with open(os.path.join(staging, "manifest.json"), "w") as f:
        json.dump({"replicated_at": replicated_at.isoformat(), "tables": manifest}, f, indent=1, sort_keys=True)
    shutil.rmtree(REPLICA, ignore_errors=True)
    os.replace(staging, REPLICA)
    return manifest


def parquet_rows(file):
    import pyarrow.parquet as pq
    return pq.ParquetFile(file).metadata.num_rows


def replicated_at(folder=REPLICA):
    """When the replica in `folder` was taken, as its manifest records it."""
    return json.load(open(os.path.join(folder, "manifest.json")))["replicated_at"]


def check_replica(folder=REPLICA, rows_of=parquet_rows):
    """The manifest of a complete replica: every expected table, each file present with the rows the manifest names.
    Raises SystemExit otherwise, so an empty or partial replica is never uploaded (finding 5)."""
    path = os.path.join(folder, "manifest.json")
    if not os.path.exists(path):
        raise SystemExit(f"no manifest in {folder}: run replicate first")
    manifest = json.load(open(path))["tables"]
    expected = {f"{s}/{t}" for s, ts in expected_tables().items() for t in ts}
    if set(manifest) != expected:
        raise SystemExit(f"the manifest's tables differ from the expected ones: missing {sorted(expected - set(manifest))}, "
                         f"extra {sorted(set(manifest) - expected)}")
    for key, rows in manifest.items():
        file = os.path.join(folder, f"{key}.parquet")
        if not os.path.exists(file):
            raise SystemExit(f"{key}.parquet is missing")
        n = rows_of(file)
        if n != rows or n == 0:
            raise SystemExit(f"{key}.parquet has {n} rows; the manifest says {rows}")
    return manifest


if __name__ == "__main__":
    replicate()
