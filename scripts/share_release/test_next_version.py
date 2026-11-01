"""The release's next_version.py on planted text, and on main's real table: it changes one entry and nothing else."""
import ast
import importlib.util
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("next_version", os.path.join(HERE, "templates", "next_version.py"))
nv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nv)
BUILD_MODULE = os.path.join(HERE, "..", "..", "business_architecture", "ontology", "release", "build_module.py")


def modules_of(text):
    """The MODULES literal of build_module.py's text, as data."""
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "MODULES":
            return ast.literal_eval(node.value)
    raise AssertionError("no MODULES")


@pytest.mark.parametrize("module", ["kpi", "data-product", "market-data", "ref-mpc", "lane", "organization", "party", "system", "value-stream", "integration"])
def test_it_changes_one_real_entry_and_keeps_the_rest(module):
    with open(BUILD_MODULE, encoding="utf-8") as f:
        text = f.read()
    before = modules_of(text)
    after = modules_of(nv.set_entry(text, module, "9.9.9", "2026-11-01", 'the "owner"', "approvals/a.md", "Approved."))
    m = after[module]
    assert (m["version"], m["issued"], m["approver"], m["approval"]) == ("9.9.9", "2026-11-01", 'the "owner"', ("approvals/a.md", "Approved."))
    for key in before[module]:
        if key not in ("version", "issued", "approver", "approval"):
            assert m[key] == before[module][key], key
    assert {k: v for k, v in after.items() if k != module} == {k: v for k, v in before.items() if k != module}


def test_an_unknown_module_stops():
    with pytest.raises(SystemExit):
        nv.set_entry('MODULES = {\n    "a": {\n        "version": "1.0.0",\n    },\n}\n', "b", "2.0.0", "d", "w", "w", "w")


def test_the_changelog_keeps_its_title_and_carries_open_gaps():
    log = "# kpi changelog\n\n## 1.3.0 (2026-10-28)\n\nA minor.\n\n### Known gaps\n\n- One gap.\n  Reason: x\n\n## 1.2.0 (2026-10-25)\n\n### Known gaps\n\nNone.\n"
    out = nv.add_section(log, "1.3.1", "2026-11-01", "patch", "Reworded.", "kpi")
    assert out.startswith("# kpi changelog\n\n## 1.3.1 (2026-11-01)\n\nA patch release. Reworded.\n\n- [patch] Reworded.\n\n### Known gaps\n\n- One gap.\n  Reason: x\n\n## 1.3.0")


def test_a_first_changelog_gets_a_title():
    out = nv.add_section("", "1.0.0", "2026-11-01", "major", "First release.", "document")
    assert out.startswith("# document changelog\n\n## 1.0.0 (2026-11-01)") and "None." in out


def test_the_lists_change_one_module_or_stop():
    p, c = nv.set_lists('[("kpi", "1.3.0"), ("lane", "1.3.0")]', '{"kpi": "1.3.0", "lane": "1.3.0"}', "kpi", "1.3.0", "1.3.1")
    assert p == '[("kpi", "1.3.1"), ("lane", "1.3.0")]' and c == '{"kpi": "1.3.1", "lane": "1.3.0"}'
    with pytest.raises(SystemExit):
        nv.set_lists('[("kpi", "1.2.0")]', '{"kpi": "1.3.0"}', "kpi", "1.3.0", "1.3.1")


def test_finish_moves_the_old_package_and_refuses_the_newest(tmp_path):
    ont = tmp_path
    for v in ("1.3.0", "1.3.1"):
        (ont / "releases" / "kpi" / v).mkdir(parents=True)
    (ont / "projection" / "skill-run").mkdir(parents=True)
    (ont / "projection" / "pipeline.py").write_text('("kpi", "1.3.0")')
    (ont / "projection" / "skill-run" / "epm-config.json").write_text('"kpi": "1.3.0"')
    args = type("A", (), {"module": "kpi", "old": "1.3.1"})
    with pytest.raises(SystemExit):
        nv.finish(args, str(ont))
    args.old = "1.3.0"
    nv.finish(args, str(ont))
    assert (ont / "releases" / "previous" / "kpi" / "1.3.0").is_dir() and not (ont / "releases" / "kpi" / "1.3.0").exists()
    assert '"1.3.1"' in (ont / "projection" / "pipeline.py").read_text()


def test_finish_changes_nothing_when_a_list_lacks_the_version(tmp_path):
    ont = tmp_path
    for v in ("1.3.0", "1.3.1"):
        (ont / "releases" / "kpi" / v).mkdir(parents=True)
    (ont / "projection" / "skill-run").mkdir(parents=True)
    (ont / "projection" / "pipeline.py").write_text('("kpi", "1.2.0")')
    (ont / "projection" / "skill-run" / "epm-config.json").write_text('"kpi": "1.3.0"')
    with pytest.raises(SystemExit):
        nv.finish(type("A", (), {"module": "kpi", "old": "1.3.0"}), str(ont))
    assert (ont / "releases" / "kpi" / "1.3.0").is_dir() and not (ont / "releases" / "previous").exists()


def test_finish_moves_nothing_when_a_write_fails(tmp_path, monkeypatch):
    ont = tmp_path
    for v in ("1.3.0", "1.3.1"):
        (ont / "releases" / "kpi" / v).mkdir(parents=True)
    (ont / "projection" / "skill-run").mkdir(parents=True)
    (ont / "projection" / "pipeline.py").write_text('("kpi", "1.3.0")')
    (ont / "projection" / "skill-run" / "epm-config.json").write_text('"kpi": "1.3.0"')

    def full_disk(path, text):
        raise OSError("disk full")
    monkeypatch.setattr(nv, "write", full_disk)
    with pytest.raises(OSError):
        nv.finish(type("A", (), {"module": "kpi", "old": "1.3.0"}), str(ont))
    assert (ont / "releases" / "kpi" / "1.3.0").is_dir() and (ont / "projection" / "pipeline.py").read_text() == '("kpi", "1.3.0")'
