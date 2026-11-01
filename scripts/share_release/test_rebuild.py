"""The rebuild's release-specific steps on a small tree: the marker names no folder of this machine, the history
folder's manifests lose their provenance fields, the generated check script is complete, and the three builder
lists agree."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rebuild  # noqa: E402
import validate  # noqa: E402

ONT = rebuild.ONT


def test_the_release_marker_names_no_folder_of_the_machine(tmp_path):
    epm = tmp_path / "Enterprise Performance Model"; epm.mkdir()
    rb = rebuild.Rebuild(str(tmp_path / "rel"), str(epm))
    os.makedirs(str(tmp_path / "rel"))
    rb.release_marker()
    marker = json.load(open(str(tmp_path / "rel" / "release.json")))
    assert set(marker) == {"release", "built", "mode"} and "Enterprise" not in json.dumps(marker)
    import manifest
    assert manifest.is_tool_marker(str(tmp_path / "rel" / "release.json")) and marker == manifest.marker(marker["built"])
    for bad in ({"release": "EPM 1.0", "mode": "share release"}, {**marker, "mode": "other"}, {**marker, "extra": 1}, {**marker, "built": "today"}, [], "x"):
        (tmp_path / "rel" / "release.json").write_text(json.dumps(bad))
        assert not manifest.is_tool_marker(str(tmp_path / "rel" / "release.json")), bad
    (tmp_path / "rel" / "release.json").write_text("not json")
    assert not manifest.is_tool_marker(str(tmp_path / "rel" / "release.json"))


def test_the_history_folders_manifests_lose_their_provenance_and_name_the_rewritten_hashes(tmp_path):
    folder = tmp_path / "rel" / ONT / "releases" / "previous" / "kpi" / "1.2.0"
    folder.mkdir(parents=True)
    (folder / "kpi.ttl").write_text("rewritten\n")
    manifest = {"module": "kpi", "version": "1.2.0", "files": {"kpi.ttl": "0" * 64}, "decisions": ["the decision of 2026-10-18"],
                "approved_by": {"who": "the decision owner", "recorded_in": "(the review comments)", "words": "Yes"},
                "approval": {"who": "x", "file": "answers.md", "words": "Yes"}, "depends_on": {"core": "2.3.0"}}
    (folder / "manifest.json").write_text(json.dumps(manifest))
    rb = rebuild.Rebuild(str(tmp_path / "rel"), str(tmp_path))
    rb.previous_hashes()
    out = json.load(open(str(folder / "manifest.json")))
    assert out["files"]["kpi.ttl"] == hashlib.sha256(b"rewritten\n").hexdigest()
    assert "decisions" not in out and out["approved_by"] == {"who": rebuild.SME, "words": "Yes"} and out["approval"] == {"who": rebuild.SME, "words": "Yes"}
    assert out["depends_on"] == {"core": "2.3.0"} and rb.steps[-1]["packages"] == ["kpi/1.2.0"]


def test_the_generated_check_script_lists_every_test_file_and_the_skill_checks(tmp_path):
    rel = tmp_path / "rel"
    for p in ("a/test_a.py", "b/c/test_b.py", "skills/x/scripts/test_skill.py", "a/__pycache__/test_cached.py", "a/helper.py", "odd name/test_$(id).py"):
        (rel / p).parent.mkdir(parents=True, exist_ok=True); (rel / p).write_text("")
    rb = rebuild.Rebuild(str(rel), str(tmp_path))
    rb.check_script()
    text = (rel / "scripts" / "check.sh").read_text()
    assert "{{" not in text and os.access(str(rel / "scripts" / "check.sh"), os.X_OK)
    assert "  a/test_a.py \\\n  b/c/test_b.py" in text and "test_skill.py" not in text.split("--dist load")[1].split("\n(cd")[0] and "test_cached" not in text
    import skill_checks
    assert skill_checks.render() in text and rb.steps[-1]["tests"] == 3
    assert "'odd name/test_$(id).py'" in text and "  odd name/test_$(id).py" not in text  # quoted: no word splitting, no substitution


def verifies(path):
    with open(path) as f:
        text = "\n".join(re.sub(r"(^|[\s;&|()<>])#.*$", r"\1", l) for l in f.read().split("\n"))
    return set(re.findall(r"python (build_[a-z_0-9]+\.py(?: [a-z-]+)?) --verify", text))


def test_the_three_builder_lists_agree():
    """scripts/check.sh on main, the release's check.sh template, and rebuild.py's builders verify the same population."""
    expected = {f"{script}" for folder, script in rebuild.SOURCE_BUILDERS} | {"build_core_2_4.py", "build_catalog.py"} | {f"build_module.py {m}" for m in rebuild.MODULE_ORDER}
    template = verifies(os.path.join(HERE, "templates", "check.sh"))
    main = verifies(os.path.join(HERE, "..", "check.sh"))
    assert template == expected, (template ^ expected)
    assert expected <= main, expected - main  # main also verifies the earlier core builders, which the release leaves out
