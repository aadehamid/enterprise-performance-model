"""The store rows judge their own findings: a planted violation fails the row, a missing artefact fails it, and no
output file holds a password. The stores themselves are stubbed; nothing here needs Docker or a login."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stores  # noqa: E402


def release_tree(tmp_path):
    (tmp_path / "KNOWN-OPEN-ITEMS.md").write_text("open\n")
    return str(tmp_path)


def stub_cypher(answers):
    """A cypher() that answers each query from a table keyed by a word in it."""
    def cypher(bolt, pw, query):
        for key, value in answers.items():
            if key in query:
                return [{"l": value}]
        return [{"l": []}]
    return cypher


def test_the_recorded_command_masks_a_password():
    assert stores.redacted(["pipeline.py", "load-verify", "--password", "s3cret", "--import-dir", "/x"]) == "pipeline.py load-verify --password *** --import-dir /x"
    r = stores.sh(["echo", "--password", "s3cret"], None)
    assert "s3cret" not in r["command"] and r["returncode"] == 0


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


def test_the_projection_row_needs_the_report_the_rename_evidence_and_the_readme_note():
    base = {"steps": [{"returncode": 0}], "report": True, "hashes_equal": True, "roundtrip_lost": 0, "roundtrip_added": 0,
            "shacl_violations_in_graph": 0, "separator": "_", "rename_lossless": True, "readme_note": {"written": True, "page_ok": True}}
    assert stores.projection_ok(base, release=True) is True
    assert stores.projection_ok({**base, "readme_note": None, "separator": "__", "rename_lossless": False}, release=False) is True
    for change in ({"steps": [{"returncode": 1}]}, {"report": False}, {"hashes_equal": False}, {"roundtrip_lost": 1}, {"roundtrip_added": 2},
                   {"shacl_violations_in_graph": 1}, {"separator": "__"}, {"rename_lossless": False}, {"readme_note": {"written": False, "page_ok": False}},
                   {"readme_note": {"written": True, "page_ok": False}}):
        assert stores.projection_ok({**base, **change}, release=True) is False, change


def test_the_readme_note_reports_what_it_wrote_and_whether_the_page_rebuilt(tmp_path, monkeypatch):
    tree = release_tree(tmp_path)
    readme = tmp_path / "business_architecture" / "ontology" / "projection" / "README.md"
    readme.parent.mkdir(parents=True)
    rep = {"nodes": 10, "relationships": 20, "shacl_violations_in_graph": 0, "roundtrip_lost": 0, "roundtrip_added": 0, "renamed": {"labels": 3}}
    readme.write_text("Intro.\n\nThe last run, on every released package with 50 nodes.\n")
    monkeypatch.setattr(stores, "page_build", lambda tree: {"returncode": 0, "tail": ""})
    out = stores.note_projection_figures(tree, rep)
    assert out["written"] and out["page_ok"] and "10 nodes and 20 relationships" in readme.read_text()
    out = stores.note_projection_figures(tree, rep)  # a second run writes no second note
    assert out["written"] and out["page_ok"] and readme.read_text().count("This release's own run") == 1
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


def test_the_sync_row_counts_every_step_and_the_drift():
    good = {"steps": [{"returncode": 0}, {"returncode": 0}, {"returncode": 0}], "removed": "urn:x", "drift_caught": True}
    assert stores.sync_ok(good) is True
    assert stores.sync_ok({**good, "steps": [{"returncode": 1}, {"returncode": 0}, {"returncode": 0}]}) is False  # mark failed
    assert stores.sync_ok({**good, "drift_caught": False}) is False
    assert stores.sync_ok({**good, "removed": None}) is False
    assert stores.sync_ok({"steps": []}) is False


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
