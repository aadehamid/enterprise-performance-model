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
import manifest  # noqa: E402
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
    assert template == expected - {"build_core_2_4.py"}, (template ^ expected)  # the template reads the newest core builder
    assert 'python "$CORE_BUILDER.py" --verify' in open(os.path.join(HERE, "templates", "check.sh")).read()
    assert expected <= main, expected - main  # main also verifies the earlier core builders, which the release leaves out


TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(rebuild.__file__)), "templates")
REPO = os.path.join(os.path.dirname(os.path.abspath(rebuild.__file__)), "..", "..")


def test_each_pinned_test_exists_on_main():
    with open(os.path.join(TEMPLATES, "pinned-tests.txt")) as f:
        lines = [x.strip() for x in f if x.strip() and not x.startswith("#")]
    assert lines
    for line in lines:
        path, name = line.split("::")
        with open(os.path.join(REPO, path), encoding="utf-8") as f:
            assert f"def {name}(" in f.read(), line


def test_every_template_has_a_place():
    placed = {name for name, dest in rebuild.TEMPLATES} | {"check.sh", "walkthrough-change.html"}
    assert placed == set(os.listdir(TEMPLATES)) - {"__pycache__"}


def test_the_guide_has_every_section_and_no_unfilled_fact():
    with open(os.path.join(TEMPLATES, "HOW-TO-UPDATE.md")) as f:
        text = manifest.fill(f.read())
    assert "{{" not in text
    for heading in ("Start here", "Patch, minor or major", "Change a concept's definition", "Add a concept or property", "Change a process",
                    "Add a module", "The cascade", "Keep the catalog, regression and projection current", "Project into Neo4j and Jena",
                    "The optional check against this release", "The namespace", "What you can ignore"):
        assert f"## {heading}" in text, heading


def test_the_file_map_keeps_only_what_is_in_the_tree(tmp_path):
    (tmp_path / "here.md").write_text("x")
    (tmp_path / "folder").mkdir()
    page = ('<tr><td><code>outside.md</code></td><td>o</td></tr>\n<section id="file-map">'
            "<tr><td><code>here.md</code></td><td>a</td></tr>\n<tr><td><code>gone.md</code></td><td>b</td></tr>\n"
            "<tr><td><code>folder/*</code></td><td>c</td></tr>\n<tr><td><code>none/*</code></td><td>d</td></tr>\n</section>")
    out = rebuild.prune_file_map(page, str(tmp_path))
    assert "here.md" in out and "folder/*" in out and "outside.md" in out and "gone.md" not in out and "none/*" not in out


def test_one_cut_is_one_place():
    assert manifest.fill("{{RELEASE_NAME}}") == manifest.RELEASE_NAME
    import publish
    parser_default = manifest.RELEASE_BRANCH
    assert parser_default.startswith("share/") and publish.manifest is manifest
