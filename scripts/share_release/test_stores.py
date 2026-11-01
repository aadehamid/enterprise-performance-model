"""The store rows judge their own findings: a planted violation fails the row, a missing artefact fails it, and no
output file holds a password. The stores themselves are stubbed; nothing here needs Docker or a login."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stores  # noqa: E402


def release_tree(tmp_path):
    (tmp_path / "release.json").write_text('{"release": "EPM 1.0", "mode": "share release"}\n')
    return str(tmp_path)


def stub_cypher(answers):
    """A cypher() that answers each query from a table keyed by a word in it."""
    def cypher(bolt, pw, query):
        for key, value in answers.items():
            if key in query:
                return [{"l": value}]
        return [{"l": []}]
    return cypher


def test_no_record_holds_a_password():
    assert stores.redacted(["pipeline.py", "load-verify", "--password", "s3cret", "--import-dir", "/x"]) == "pipeline.py load-verify --password *** --import-dir /x"
    r = stores.sh(["echo", "--password", "s3cret", "--token=t0ken"], None)
    assert "s3cret" not in r["command"] and "t0ken" not in r["command"] and r["returncode"] == 0
    assert "s3cret" not in r["tail"] and "t0ken" not in r["tail"] and "***" in r["tail"]  # the echoed secret is scrubbed from the output too
    r = stores.sh(["sh", "-c", "echo $NEO4J_PASSWORD"], None, env={"NEO4J_PASSWORD": "fromenv1"})
    assert "fromenv1" not in r["tail"] and "***" in r["tail"]
    stores.SECRETS.add("generated9")
    try:
        r = stores.sh(["echo", "the generated9 one"], None)
        assert "generated9" not in r["tail"]
        r = stores.sh(["sh", "-c", "echo generated9; sleep 5"], None, timeout=1)
        assert r["returncode"] == -1 and "generated9" not in r["tail"]
    finally:
        stores.SECRETS.discard("generated9")


def test_the_projection_row_passes_the_password_through_the_environment(tmp_path, monkeypatch):
    tree = release_tree(tmp_path)
    (tmp_path / "business_architecture" / "ontology" / "projection").mkdir(parents=True)
    calls = []
    monkeypatch.setattr(stores, "uv", lambda args, cwd, env=None, **kw: (calls.append((args, env)), {"command": " ".join(args), "returncode": 1, "seconds": 0, "tail": ""})[1])
    monkeypatch.setattr(stores, "neo4j_up", lambda env: ("bolt://localhost:1", "pw-secret-1"))
    env = {"IMPORT_DIR": str(tmp_path / "import"), "ROBOT_JAR": "/r.jar", "LEDGER_FILE": str(tmp_path / "ledger.jsonl")}
    calls.clear()
    monkeypatch.setattr(stores, "uv", lambda args, cwd, env=None, **kw: (calls.append((args, env)), {"command": " ".join(args), "returncode": 0, "seconds": 0, "tail": ""})[1])
    stores.row_projection_pipeline(tree, env)
    args, e = calls[-1]
    assert args[:2] == ["pipeline.py", "load-verify"] and "--password" not in args and "pw-secret-1" not in " ".join(args)
    assert e["NEO4J_PASSWORD"] == "pw-secret-1"


def test_the_underscore_row_fails_on_a_planted_double_separator_anywhere(tmp_path, monkeypatch):
    tree = release_tree(tmp_path)
    env = {"TEST_NEO4J_PASSWORD": "x"}
    clean = {"labels(n)": ["skos_Concept", "Resource"], "type(r)": ["skos_broader"], "keys(n)": ["uri", "skos_prefLabel"], "keys(r)": ["since"]}
    monkeypatch.setattr(stores, "cypher", stub_cypher(clean))
    assert stores.row_underscores(tree, env)["ok"] is True
    for where, bad in (("labels(n)", ["skos__Concept"]), ("type(r)", ["skos__broader"]), ("keys(n)", ["skos__prefLabel"]), ("keys(r)", ["prov__since"])):
        monkeypatch.setattr(stores, "cypher", stub_cypher({**clean, where: bad}))
        row = stores.row_underscores(tree, env)
        assert row["ok"] is False and row["samples"] == bad, where
    monkeypatch.setattr(stores, "cypher", stub_cypher({}))  # an empty graph proves nothing
    assert stores.row_underscores(tree, env)["ok"] is False
    monkeypatch.setattr(stores, "cypher", stub_cypher({**clean, "labels(n)": ["skos__Concept"]}))
    assert stores.row_underscores(str(tmp_path / "main"), env)["ok"] is True  # on main the row measures n10s's names


def test_the_projection_row_needs_every_figure_present_and_right():
    base = {"steps": [{"returncode": 0}], "report": True, "determinism_hash_sorted": "abc", "determinism_hash_shuffled": "abc", "hashes_equal": True,
            "roundtrip_lost": 0, "roundtrip_added": 0, "shacl_violations_in_graph": 0, "in_graph_mutant_violations": 1,
            "separator": "_", "rename_lossless": True, "readme_note": {"written": True, "page_ok": True}}
    assert stores.projection_ok(base, release=True) is True
    assert stores.projection_ok({**base, "readme_note": None, "separator": "__", "rename_lossless": False}, release=False) is True
    for change in ({"steps": [{"returncode": 1}]}, {"report": False}, {"determinism_hash_shuffled": "abd"}, {"roundtrip_lost": 1}, {"roundtrip_added": 2},
                   {"shacl_violations_in_graph": 1}, {"in_graph_mutant_violations": 0}, {"separator": "__"}, {"rename_lossless": False},
                   {"readme_note": {"written": False, "page_ok": False}}, {"readme_note": {"written": True, "page_ok": False}},
                   {"roundtrip_lost": False}, {"in_graph_mutant_violations": True}):
        assert stores.projection_ok({**base, **change}, release=True) is False, change
    for missing in ("determinism_hash_sorted", "determinism_hash_shuffled", "roundtrip_lost", "roundtrip_added", "shacl_violations_in_graph", "in_graph_mutant_violations"):
        partial = {k: v for k, v in base.items() if k != missing}  # a report without the figure proves nothing
        assert stores.projection_ok(partial, release=True) is False, missing
        assert stores.projection_ok({**partial, missing: None}, release=True) is False, missing
    assert stores.projection_ok({**base, "determinism_hash_sorted": None, "determinism_hash_shuffled": None}, release=True) is False  # None == None is not equal hashes


def test_the_readme_note_reports_what_it_wrote_and_whether_the_page_rebuilt(tmp_path, monkeypatch):
    tree = release_tree(tmp_path)
    readme = tmp_path / "business_architecture" / "ontology" / "projection" / "README.md"
    readme.parent.mkdir(parents=True)
    rep = {"nodes": 10, "relationships": 20, "shacl_violations_in_graph": 0, "roundtrip_lost": 0, "roundtrip_added": 0, "renamed": {"labels": 3}}
    readme.write_text("Intro.\n\nThe last run, on every released package with 50 nodes.\n")
    monkeypatch.setattr(stores, "page_build", lambda tree: {"returncode": 0, "tail": ""})
    out = stores.note_projection_figures(tree, rep)
    assert out["written"] and out["page_ok"] and "10 nodes and 20 relationships" in readme.read_text()
    out = stores.note_projection_figures(tree, {**rep, "nodes": 11})  # a later run replaces the note: its figures are this report's
    assert out["written"] and out["page_ok"] and out["replaced"] and readme.read_text().count("This release's own run") == 1
    assert "11 nodes" in readme.read_text() and "10 nodes" not in readme.read_text() and readme.read_text().lower().count("the last run, on every released package with") == 1
    monkeypatch.setattr(stores, "page_build", lambda tree: {"returncode": 1, "tail": "boom"})
    assert stores.note_projection_figures(tree, rep)["page_ok"] is False
    readme.write_text("No run paragraph here.\n")
    out = stores.note_projection_figures(tree, rep)
    assert out == {"written": False, "page_ok": False, "note": "not written: the run paragraph was not found"}


def test_the_offline_demo_row_needs_every_run_paired_and_compared(tmp_path):
    fresh, recorded = tmp_path / "run-rejudged.json", tmp_path / "recorded-rejudged.json"
    assert stores.rejudge_pair(str(fresh), str(recorded)) == {"missing": "the tree holds no recorded re-judgement for this run"}
    recorded.write_text(json.dumps({"results": [{"n": 1, "passed": True}, {"n": 2, "passed": False}]}))
    assert stores.rejudge_pair(str(fresh), str(recorded)) == {"missing": "the re-judge wrote no result"}
    fresh.write_text(json.dumps({"results": [{"n": 1, "passed": True}, {"n": 2, "passed": True}]}))
    assert stores.rejudge_pair(str(fresh), str(recorded)) == {"cases": 2, "differences": ["2"]}
    good = {"returncode": 0, "cases": 2, "differences": []}
    assert stores.demo_offline_ok(0, [good]) is True
    assert stores.demo_offline_ok(0, []) is False  # no run re-judged proves nothing
    assert stores.demo_offline_ok(1, [good]) is False
    for bad in ({**good, "returncode": 1}, {**good, "differences": ["2"]}, {"returncode": 0, "missing": "x"}, {**good, "cases": 0}):
        assert stores.demo_offline_ok(0, [good, bad]) is False, bad


def test_the_sync_row_judges_the_two_test_stores_and_expects_the_drift_checks_exit_code():
    good = {"steps": [{"returncode": 0}, {"returncode": 0}, {"returncode": 1}], "removed": "urn:x", "drift_caught": True,
            "before": {"pipeline": "current", "driver": "current"}, "after": {"pipeline": "changed", "driver": "current"}}
    assert stores.sync_ok(good) is True
    assert stores.sync_ok({**good, "steps": [{"returncode": 1}, {"returncode": 0}, {"returncode": 1}]}) is False  # mark failed
    assert stores.sync_ok({**good, "steps": [{"returncode": 0}, {"returncode": 1}, {"returncode": 1}]}) is False  # not current before the drift
    assert stores.sync_ok({**good, "steps": [{"returncode": 0}, {"returncode": 0}, {"returncode": 0}]}) is False  # the drift check exits 1 when it sees the drift
    assert stores.sync_ok({**good, "after": {"pipeline": "current", "driver": "current"}}) is False
    assert stores.sync_ok({**good, "after": {"pipeline": "changed", "driver": "behind"}}) is False
    assert stores.sync_ok({**good, "before": {"pipeline": "current"}}) is False
    assert stores.sync_ok({**good, "removed": None}) is False
    assert stores.sync_ok({"steps": []}) is False


def test_the_sync_row_reads_only_the_test_stores_lines(tmp_path, monkeypatch):
    """The real check (rel15) printed aura unmarked and databricks behind beside the two current test stores; the row
    passes --store for the two, reads their lines only, and names the other two as outside the test."""
    tree = release_tree(tmp_path)
    (tmp_path / "business_architecture" / "ontology" / "projection").mkdir(parents=True)
    before = ("pipeline    current   marked 2026-11-01T04:44:59Z at commit unknown\ndriver      current   marked 2026-11-01T04:44:59Z at commit unknown\n"
              "aura        unmarked  no marker: mark it after a checked load, or sync it\ndatabricks  behind    marked 2026-10-29T14:23:14Z from another release set\n[WARN] pyarrow\n")
    after = before.replace("pipeline    current   marked 2026-11-01T04:44:59Z at commit unknown", "pipeline    changed   marked with [4189, 21767], now holds [4188, 21407]")
    calls = []

    def uv(args, cwd, env=None, **kw):
        calls.append(args)
        if args[1] == "mark":
            return {"command": " ".join(args), "returncode": 0, "seconds": 0, "tail": "pipeline: marked\ndriver: marked\n"}
        return {"command": " ".join(args), "returncode": 1, "seconds": 0, "tail": after if len(calls) > 2 else before}
    monkeypatch.setattr(stores, "uv", uv)
    monkeypatch.setattr(stores, "test_password", lambda env: "pw")
    monkeypatch.setattr(stores, "stores_json", lambda env: "{}")
    monkeypatch.setattr(stores, "cypher", lambda bolt, pw, q: [{"uri": "urn:victim"}] if "RETURN n.uri" in q else [])
    row = stores.row_sync(tree, {})
    assert all(a[1] != "check" or a[2:6] == ["--store", "pipeline", "--store", "driver"] for a in calls) and calls[0][1:6] == ["mark", "--store", "pipeline", "--store", "driver"]
    assert row["before"] == {"pipeline": "current", "driver": "current"} and row["after"] == {"pipeline": "changed", "driver": "current"}
    assert row["drift_caught"] and "aura" not in row["before"] and "aura and databricks" in row["outside_the_test"]
    assert row["ok"] is False  # the first check exited 1 as rel15's did when it read every store; with --store it exits 0
    calls.clear()
    seq = iter([(0, "pipeline: marked\n"), (0, before), (1, after)])
    monkeypatch.setattr(stores, "uv", lambda args, cwd, env=None, **kw: (lambda rc_tail: {"command": " ".join(args), "returncode": rc_tail[0], "seconds": 0, "tail": rc_tail[1]})(next(seq)))
    assert stores.row_sync(tree, {})["ok"] is True


def test_the_live_demo_row_writes_its_compose_override_outside_the_tree_and_ledgers_it(tmp_path, monkeypatch):
    tree = release_tree(tmp_path)
    scratch = tmp_path / "scratch"; scratch.mkdir()
    env = {"IMPORT_DIR": str(scratch), "LEDGER_FILE": str(scratch / "ledger.jsonl"), "DEMO_PROJECT": "pricing-validate", "DEMO_PG_PORT": "55433"}
    calls = []
    monkeypatch.setattr(stores, "sh", lambda args, cwd, **kw: (calls.append(args), {"command": " ".join(args), "returncode": 1, "seconds": 0, "tail": "down"})[1])
    row = stores.row_demo_live(tree, env)
    assert row["ok"] is False and calls[0][:2] == ["docker", "compose"]
    override = str(scratch / "compose.pricing-validate.yml")
    assert override in calls[0] and os.path.exists(override) and "pricing-validate-sources" in open(override).read()
    assert not os.path.exists(os.path.join(tree, "demos", "downstream-pricing-databricks-free", "docker", "compose.validate.yml"))
    ledger = [json.loads(l) for l in open(str(scratch / "ledger.jsonl"))]
    assert [(e["kind"], e["name"]) for e in ledger] == [("file", override), ("compose-project", "pricing-validate")]
