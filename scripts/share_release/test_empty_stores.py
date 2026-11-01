"""empty_stores.py deletes only with --yes, only the stores named, and prints no login. Fakes stand in for every store."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import empty_stores as es  # noqa: E402


class FakeResult:
    def __init__(self, c):
        self.c = c

    def single(self):
        return {"c": self.c}


class FakeSession:
    """A graph of n nodes: a delete takes up to 5000."""
    def __init__(self, nodes):
        self.nodes, self.queries = nodes, []

    def run(self, query):
        self.queries.append(query)
        if "DETACH DELETE" in query:
            gone = min(self.nodes, 5000)
            self.nodes -= gone
            return FakeResult(gone)
        return FakeResult(self.nodes if "(n)" in query else 0)


class FakeCursor:
    def __init__(self, tables):
        self.tables, self.statements, self.last = list(tables), [], []

    def execute(self, sql):
        self.statements.append(sql)
        if sql.startswith("SHOW TABLES"):
            self.last = [("s", t) for t in self.tables]
        elif sql.startswith("SELECT count"):
            self.last = [(7,)]
        elif sql.startswith("DROP TABLE"):
            self.tables.remove(sql.rsplit(".", 1)[1])

    def fetchall(self):
        return self.last

    def fetchone(self):
        return self.last[0]


def test_without_yes_nothing_is_deleted():
    s = FakeSession(12000)
    out = es.empty_neo4j(s, yes=False)
    assert s.nodes == 12000 and out["deleted"] == 0 and out["after"] == out["before"]
    assert not any("DELETE" in q for q in s.queries)


def test_yes_deletes_in_batches_and_counts_after():
    s = FakeSession(12000)
    out = es.empty_neo4j(s, yes=True)
    assert s.nodes == 0 and out["deleted"] == 12000 and out["after"]["nodes"] == 0
    assert sum("DETACH DELETE" in q for q in s.queries) == 4  # three batches and the empty one that ends the loop


def test_databricks_without_yes_drops_nothing():
    c = FakeCursor(["epm_triples"])
    out = es.empty_databricks(c, "cat.sch", yes=False)
    assert out["counts_before"] == {"epm_triples": 7} and "tables_after" not in out
    assert not any(s.startswith("DROP") for s in c.statements)


def test_databricks_yes_drops_only_that_schema():
    c = FakeCursor(["a", "b"])
    out = es.empty_databricks(c, "cat.sch", yes=True)
    assert out["tables_after"] == []
    assert [s for s in c.statements if s.startswith("DROP")] == ["DROP TABLE IF EXISTS cat.sch.a", "DROP TABLE IF EXISTS cat.sch.b"]


def env_file(tmp_path, text="NEO4J_LOCAL=bolt://x|/nowhere\n"):
    p = tmp_path / "stores.env"
    p.write_text(text)
    return str(p)


def test_a_store_must_be_named(tmp_path):
    with pytest.raises(SystemExit):
        es.main(["--env", env_file(tmp_path)], runner=lambda *a: pytest.fail("ran with no store named"))


def test_a_store_the_env_does_not_list_cannot_run(tmp_path):
    with pytest.raises(SystemExit):
        es.main(["--env", env_file(tmp_path), "aura"], runner=lambda *a: pytest.fail("ran an unlisted store"))


def test_yes_reaches_only_the_named_store(tmp_path, capsys):
    calls = []
    code = es.main(["--env", env_file(tmp_path, "NEO4J_LOCAL=a|b\nNEO4J_AURA=c\n"), "--yes", "local"],
                   runner=lambda name, config, yes: calls.append((name, yes)) or {"deleted": 0})
    assert code == 0 and calls == [("local", True)]
    assert json.loads(capsys.readouterr().out)["store"] == "local"


def test_a_failure_is_reported_with_the_login_masked(tmp_path, capsys):
    login = tmp_path / "login.env"
    login.write_text("NEO4J_URI=bolt://x\nNEO4J_PASSWORD=hunter-two-secret\n")
    es.neo4j_login(str(login))

    def fails(name, config, yes):
        raise RuntimeError("auth failed for hunter-two-secret")
    code = es.main(["--env", env_file(tmp_path), "local"], runner=fails)
    out = capsys.readouterr().out
    assert code == 1 and "hunter-two-secret" not in out and "RuntimeError" in out
