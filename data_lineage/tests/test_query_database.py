import sqlite3
import sys
from pathlib import Path

import duckdb
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "db_connect" / "src"))
from connect import query_database  # noqa: E402


def test_reads_sqlite_with_bound_parameters(tmp_path):
    path = tmp_path / "source.db"
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE reports (name TEXT, views INTEGER)")
        con.executemany("INSERT INTO reports VALUES (?, ?)", [("Margin", 3), ("Freight", 1)])
    df = query_database("SELECT name FROM reports WHERE views > :n", f"sqlite:///{path}", n=2)
    assert df["name"].tolist() == ["Margin"]


def test_reads_duckdb_schemas(tmp_path):
    path = tmp_path / "source.duckdb"
    with duckdb.connect(str(path)) as con:
        con.execute("CREATE SCHEMA sem_internal_x")
        con.execute("CREATE TABLE sem_internal_x.t AS SELECT 'sem_wholesale' AS Schema_Name")
    df = query_database('SELECT Schema_Name AS "Database" FROM sem_internal_x.t', f"duckdb:///{path}")
    assert df.to_dict("records") == [{"Database": "sem_wholesale"}]


def test_falls_back_to_source_db_url(tmp_path, monkeypatch):
    path = tmp_path / "env.db"
    sqlite3.connect(path).close()
    monkeypatch.setenv("SOURCE_DB_URL", f"sqlite:///{path}")
    assert query_database("SELECT 7 AS n")["n"].tolist() == [7]


def test_refuses_without_a_url(monkeypatch):
    monkeypatch.delenv("SOURCE_DB_URL", raising=False)
    with pytest.raises(ValueError, match="SOURCE_DB_URL"):
        query_database("SELECT 1")
