"""validate.py's rows and comparison fail on what they find, its commands exit nonzero on a failure, and its one
table of skill checks is what the release's check.sh runs."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate  # noqa: E402

NS = validate.MODULES_NS


def test_a_pin_move_is_explained_only_when_the_same_dependencies_move_to_the_newest_versions():
    from rdflib import URIRef
    req = URIRef("http://purl.org/dc/terms/requires")
    kpi = URIRef(NS + "kpi")
    newest = {"core": "2.4.0", "organization": "2.2.0", "kpi": "1.3.0"}
    moved = ([(kpi, req, URIRef(NS + "core/2.3.0"))], [(kpi, req, URIRef(NS + "core/2.4.0"))])
    assert validate.explained_by_pin_move(*moved, "kpi", newest) is True
    assert validate.explained_by_pin_move([], [], "kpi", newest) is True
    assert validate.explained_by_pin_move(moved[0], [(kpi, req, URIRef(NS + "core/2.2.0"))], "kpi", newest) is False  # not the newest
    assert validate.explained_by_pin_move(moved[0], [], "kpi", newest) is False  # a dependency dropped
    assert validate.explained_by_pin_move(moved[0], moved[1] + [(kpi, req, URIRef(NS + "organization/2.2.0"))], "kpi", newest) is False  # one added
    assert validate.explained_by_pin_move(moved[0], [(URIRef(NS + "lane"), req, URIRef(NS + "core/2.4.0"))], "kpi", newest) is False  # another subject
    assert validate.explained_by_pin_move([(kpi, URIRef("http://purl.org/dc/terms/title"), URIRef(NS + "x"))], [], "kpi", newest) is False


def fake_trees(tmp_path, release_deps, catalog_versions, main_deps=None):
    main, release = tmp_path / "main", tmp_path / "release"
    newest = {m: f"{i + 1}.0.0" for i, m in enumerate(validate.MODULES)}
    for m in validate.MODULES:
        for tree, deps in ((main, main_deps or release_deps), (release, release_deps)):
            folder = tree / validate.ONT / "releases" / m / newest[m]
            folder.mkdir(parents=True)
            (folder / "manifest.json").write_text(json.dumps({"depends_on": deps.get(m, {})}))
    catalog = "".join(f"<{NS}{m}/{v}> a dcat:Dataset ;\n    owl:versionInfo \"{v}\" .\n" for m, v in catalog_versions.items())
    (release / validate.ONT / "releases" / "catalog.ttl").write_text(catalog)
    return str(main), str(release), newest


def test_latest_links_reject_an_older_pin_a_changed_dependency_set_and_a_stale_catalog(tmp_path):
    deps = {"kpi": {"core": "1.0.0", "organization": "7.0.0"}, "lane": {"core": "1.0.0"}}
    main, release, newest = fake_trees(tmp_path, deps, newest_of := {m: f"{i + 1}.0.0" for i, m in enumerate(validate.MODULES)})
    assert validate.latest_links(main, release, newest) == []
    main, release, newest = fake_trees(tmp_path / "a", {**deps, "kpi": {"core": "0.9.0", "organization": "7.0.0"}}, newest_of)
    assert validate.latest_links(main, release, newest) == ["kpi 4.0.0 requires core 0.9.0, newest is 1.0.0"]
    main, release, newest = fake_trees(tmp_path / "b", {**deps, "kpi": {"core": "1.0.0"}}, newest_of, main_deps=deps)
    assert validate.latest_links(main, release, newest) == ["kpi 4.0.0 requires ['core'] in the release and ['core', 'organization'] on main"]
    main, release, newest = fake_trees(tmp_path / "c", deps, {**newest_of, "kpi": "3.9.0"})
    assert validate.latest_links(main, release, newest) == ["the catalog lists [('kpi', '3.9.0')] that are not newest and misses [('kpi', '4.0.0')]"]
    main, release, newest = fake_trees(tmp_path / "d", deps, newest_of)
    os.remove(os.path.join(main, validate.ONT, "releases", "kpi", newest["kpi"], "manifest.json"))
    assert validate.latest_links(main, release, newest) == ["kpi 4.0.0 has no manifest on main to compare with"]  # no baseline, no pass


def test_the_newest_version_is_chosen_by_number_everywhere(tmp_path):
    import manifest
    assert manifest.newest_version(["1.9.0", "1.10.0", "1.2.0"]) == "1.10.0"
    for v in ("1.9.0", "1.10.0"):
        folder = tmp_path / validate.ONT / "releases" / "kpi" / v
        folder.mkdir(parents=True); (folder / "manifest.json").write_text("{}")
    assert manifest.newest_on_disk(str(tmp_path), "kpi") == "1.10.0"
    assert sorted(["1.9.0", "1.10.0"])[-1] == "1.9.0"  # what text order would have chosen


def test_the_skills_tests_row_fails_when_a_test_command_ran_no_test(tmp_path, monkeypatch):
    (tmp_path / "release.json").write_text('{"release": "EPM 1.0", "mode": "share release"}\n')
    tails = {"tests": "Ran 12 tests in 0.1s\n\nOK\n", "check": "ok\n"}
    kinds = {" ".join(cmd): kind for _, _, cmd, kind in validate.SKILL_CHECKS}
    monkeypatch.setattr(validate, "sh", lambda cmd, cwd, **kw: {"command": " ".join(cmd), "cwd": cwd, "returncode": 0, "seconds": 0,
                                                                 "tail": tails[kinds[" ".join(cmd)]], "pytest_summary": None})
    row = validate.row_skills_tests(str(tmp_path), {})
    assert row["ok"] is True and row["passed"] == 48 and set(row["runs"]) == {"ontology", "ontology:check_sssom.py", "ontology-to-lpg", "rdf-store", "skills:test_playbook_html.py"}
    assert row["runs"]["skills:test_playbook_html.py"]["kind"] == "tests"  # a unittest suite: zero tests is a failure there too
    tails["tests"] = "Ran 0 tests in 0.0s\n\nOK\n"
    row = validate.row_skills_tests(str(tmp_path), {})
    assert row["ok"] is False and all(not r["ok"] for r in row["runs"].values() if r["kind"] == "tests") and row["runs"]["ontology:check_sssom.py"]["ok"]
    assert row["runs"]["skills:test_playbook_html.py"]["ok"] is False
    assert validate.row_skills_tests(str(tmp_path / "main"), {})["ok"] is None  # main without SKILLS_REPO: not run, with its reason


def test_the_skill_checks_table_renders_the_release_check_script():
    import skill_checks
    rendered = skill_checks.render()
    with open(os.path.join(HERE, "templates", "check.sh")) as f:
        template = f.read()
    assert "{{SKILL_CHECKS}}" in template and "run_tests()" in template
    assert rendered.count("\n") + 1 == len(validate.SKILL_CHECKS)
    for skill, folder, cmd, kind in validate.SKILL_CHECKS:
        assert cmd[-1] in rendered and ("run_tests " if kind == "tests" else "run ") in rendered
    assert "check_sssom.py" in rendered and "test_playbook_html.py" in rendered  # the two checks the old row left out


def test_the_iri_base_row_fails_on_the_release_and_measures_on_main(tmp_path):
    (tmp_path / "doc.md").write_text("<https://w3id.org/lsc/ontology/> and LSC\n")
    assert validate.row_iri_base(str(tmp_path), {}) == {"files": 1, "places": 2, "samples": [("doc.md", 2)], "unreadable": [], "ok": True}
    (tmp_path / "release.json").write_text('{"release": "EPM 1.0", "mode": "share release"}\n')
    assert validate.row_iri_base(str(tmp_path), {})["ok"] is False
    (tmp_path / "doc.md").write_text("<https://w3id.org/mpc/ontology/>\n")
    assert validate.row_iri_base(str(tmp_path), {})["ok"] is True
    (tmp_path / "locked.md").write_text("LSC\n")
    os.chmod(str(tmp_path / "locked.md"), 0)
    try:
        if os.access(str(tmp_path / "locked.md"), os.R_OK):
            import pytest
            pytest.skip("this user reads every file (root), so an unreadable file cannot be planted")
        row = validate.row_iri_base(str(tmp_path), {})
        assert row["ok"] is False and row["unreadable"] and "locked.md" in row["unreadable"][0]  # a file not read proves nothing
    finally:
        os.chmod(str(tmp_path / "locked.md"), 0o644)


def test_the_report_returns_the_failures_and_lists_the_figures_to_explain(tmp_path):
    base = {"tree": "main", "commit": "abc", "rows": {"regression": {"ok": True, "answerable": 40}, "checks": {"ok": True, "passed": 900},
                                                       "sync": {"ok": True}, "gate": {"ok": None, "reason": "the gate runs on the release only"}}}
    rel = {"tree": "rel", "rows": {"regression": {"ok": True, "answerable": 40}, "checks": {"ok": True, "passed": 700},
                                   "sync": {"ok": None, "reason": "needs Databricks"}, "gate": {"ok": True, "leaks": 0}}}
    cmp = {"rows": {"ontology-content": {"ok": True}, "latest-links": {"ok": False}}}
    for name, data in (("b.json", base), ("r.json", rel), ("c.json", cmp)):
        (tmp_path / name).write_text(json.dumps(data))
    failures = validate.report(str(tmp_path / "b.json"), str(tmp_path / "r.json"), str(tmp_path / "c.json"), str(tmp_path / "out.md"))
    assert failures == ["sync ran on main and not on the release", "latest-links (comparison) failed"]
    text = (tmp_path / "out.md").read_text()
    assert "Figures that differ, to explain in the cut's notes: checks." in text and "FAILED: sync ran on main" in text
    rel["rows"]["sync"] = {"ok": False}; cmp["rows"]["latest-links"] = {"ok": True}
    (tmp_path / "r.json").write_text(json.dumps(rel)); (tmp_path / "c.json").write_text(json.dumps(cmp))
    assert validate.report(str(tmp_path / "b.json"), str(tmp_path / "r.json"), str(tmp_path / "c.json"), str(tmp_path / "out.md")) == ["sync failed on the release"]
    rel["rows"]["sync"] = {"ok": True}
    (tmp_path / "r.json").write_text(json.dumps(rel))
    assert validate.report(str(tmp_path / "b.json"), str(tmp_path / "r.json"), str(tmp_path / "c.json"), str(tmp_path / "out.md")) == []


def test_the_commands_exit_nonzero_on_a_failed_row(tmp_path):
    (tmp_path / "release.json").write_text('{"release": "EPM 1.0", "mode": "share release"}\n')
    (tmp_path / "doc.md").write_text("LSC\n")
    cmd = [sys.executable, os.path.join(HERE, "validate.py"), "run", "--tree", str(tmp_path), "--out", str(tmp_path / "out.json"), "--rows", "iri-base"]
    r = subprocess.run(cmd[:-1] + [""], capture_output=True, text=True)  # no row asked for: not a validation
    assert r.returncode != 0 and "no row" in r.stderr and not (tmp_path / "out.json").exists()
    r = subprocess.run(cmd[:-1] + ["iri-base,nonsuch"], capture_output=True, text=True)
    assert r.returncode != 0 and "unknown row" in r.stderr
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 1 and json.load(open(str(tmp_path / "out.json")))["rows"]["iri-base"]["ok"] is False
    (tmp_path / "doc.md").write_text("MPC\n")
    assert subprocess.run(cmd, capture_output=True, text=True).returncode == 0
    cmd = [sys.executable, os.path.join(HERE, "validate.py"), "run", "--tree", str(tmp_path), "--out", str(tmp_path / "out.json"), "--rows", "gate"]
    r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "EPM_RELEASE_OWNER_NAMES": "Ada Lovelace"})
    assert r.returncode == 1  # the gate row: the README's namespace note is missing
