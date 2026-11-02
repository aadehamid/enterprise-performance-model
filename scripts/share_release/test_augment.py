"""The augment folder (augment.py; EPM-DEC-001-0113), tested with the logical-model module's made-up example as the
folder: without --augment nothing changes; with it the models are staged through the rules (the module's own IRIs move
to w3id.org/mpc, ER Studio's namespace is untouched and passes the gate), the package is built, registered and counted,
its manifest and release.json hold the outside files' hashes, and --augment without the decision owner's approval is
refused before anything is removed."""
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

os.environ.setdefault("EPM_RELEASE_OWNER_NAMES", "Ada Lovelace")  # a stand-in: no test names a person
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import augment  # noqa: E402
import export  # noqa: E402
import gate  # noqa: E402
import manifest  # noqa: E402
import rebuild  # noqa: E402
import rules  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ONT = augment.ONT
LM = os.path.join(ROOT, ONT, "logical-model")
SLUG = "example-logical-model"
WORDS = "I approve logical-model 1.0.0."


@pytest.fixture
def folder(tmp_path):
    """The made-up example as an augment folder: <slug>.ttl and <slug>.links.csv, and a file the cut ignores."""
    f = tmp_path / "augment"
    f.mkdir()
    shutil.copy(os.path.join(LM, "example", "example-export.ttl"), f / f"{SLUG}.ttl")
    shutil.copy(os.path.join(LM, "example", "example-links.csv"), f / f"{SLUG}.links.csv")
    (f / "notes.md").write_text("not read\n")
    return f


def answers(tmp_path, body):
    folder = tmp_path / "epm" / ONT / augment.ANSWERS
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "answers-2026-11-03-logical-model-release.md").write_text(body)
    return str(tmp_path / "epm"), str(folder / "answers-2026-11-03-logical-model-release.md")


def test_the_folder_names_each_model_and_hashes_each_file(folder):
    assert augment.models(str(folder)) == [(SLUG, str(folder / f"{SLUG}.ttl"), str(folder / f"{SLUG}.links.csv"))]
    files = augment.inputs(str(folder))
    assert [f["path"] for f in files] == [f"{SLUG}.ttl", f"{SLUG}.links.csv"]
    assert files[0]["sha256"] == hashlib.sha256((folder / f"{SLUG}.ttl").read_bytes()).hexdigest()
    (folder / f"{SLUG}.links.csv").unlink()
    with pytest.raises(SystemExit, match="has no example-logical-model.links.csv"):
        augment.models(str(folder))


def test_augment_without_the_decision_owners_approval_is_refused(tmp_path):
    epm, path = answers(tmp_path, "<!-- context: I approve logical-model 1.0.0. -->\nOther answers.\n")
    for args in ((epm, "", ""), (epm, path, "")):
        with pytest.raises(SystemExit, match="waits for the decision owner's approval"):
            augment.approval(*args)
    with pytest.raises(SystemExit, match="are not in the body"):  # words in a comment are context, not the approval
        augment.approval(epm, path, WORDS)
    elsewhere = tmp_path / "approval.md"
    elsewhere.write_text(WORDS + "\n")
    with pytest.raises(SystemExit, match="not a file of the answers folder"):
        augment.approval(epm, str(elsewhere), WORDS)
    epm, path = answers(tmp_path, "Block 1:\n\n> " + WORDS + "\n")
    assert augment.approval(epm, path, WORDS) == (f"{augment.ANSWERS}/answers-2026-11-03-logical-model-release.md", WORDS)


def test_cut_refuses_augment_without_the_approval_before_anything_is_removed(tmp_path, folder):
    out = tmp_path / "out"
    out.mkdir()
    (out / "release.json").write_text(json.dumps(manifest.marker("2026-11-01")))
    (out / "keep").write_text("x")
    (tmp_path / "epm").mkdir(); (tmp_path / "skills").mkdir()
    (tmp_path / "stores.env").write_text("LEDGER_FILE=" + str(tmp_path / "ledger.jsonl") + "\n")
    r = subprocess.run(["bash", os.path.join(HERE, "cut.sh"), "--epm", str(tmp_path / "epm"), "--skills", str(tmp_path / "skills"),
                        "--out", str(out), "--env", str(tmp_path / "stores.env"), "--no-cleanroom", "--replace", "--augment", str(folder)],
                       env={**os.environ, "EPM_RELEASE_OWNER_NAMES": "Ada Lovelace"}, capture_output=True, text=True, timeout=120)
    assert r.returncode == 2 and "waits for the decision owner's approval" in r.stderr and "=== export" not in r.stdout
    assert (out / "keep").exists()


def test_the_rules_leave_er_studios_namespace_and_move_the_modules_own(folder, tmp_path):
    line = ("<https://www.erstudio.com/semanticmodel/x_Account_Dim> "
            "<https://w3id.org/lsc/ontology/modules/logical-model/sourceSystem> <https://w3id.org/lsc/ontology/modules/system/system/sap> .\n")
    new, _ = rules.apply(line, f"{augment.MODELS}/x.layer.ttl", {})
    assert new == line.replace("w3id.org/lsc/", "w3id.org/mpc/") and new.count(augment.ER_STUDIO) == 1
    release = tmp_path / "rel"
    staged = augment.stage(str(release), str(folder), {"EPM-DEC-001-0113": "2026-11-02"})
    links = (release / augment.MODELS / f"{SLUG}.links.csv").read_text()
    export_copy = (release / augment.MODELS / f"{SLUG}.erstudio.ttl").read_text()
    assert "w3id.org/lsc" not in links and links.count("https://w3id.org/mpc/ontology/modules/") == 6
    assert export_copy.count(augment.ER_STUDIO) == (folder / f"{SLUG}.ttl").read_text().count(augment.ER_STUDIO) > 0
    assert staged[f"{augment.MODELS}/{SLUG}.links.csv"] == {"source": f"{SLUG}.links.csv", "rules": {"iri": 6}}
    (release / "README.md").write_text("The namespaces will be reviewed and approved by the Data, Analytics and Insight team.\n")
    assert gate.scan(str(release)) == []  # erstudio.com is not a host of the build


def test_the_export_stages_the_models_only_with_augment(tmp_path, folder):
    epm = tmp_path / "epm"
    (epm / ONT / "logical-model").mkdir(parents=True)
    (epm / ONT / "logical-model" / "README.md").write_text("The module.\n")
    plain = export.export(str(epm), "", str(tmp_path / "plain"))
    assert "augment" not in plain and not (tmp_path / "plain" / augment.MODELS).exists()
    with_it = export.export(str(epm), "", str(tmp_path / "with"), augment_folder=str(folder))
    assert with_it["augment"]["files"] == augment.inputs(str(folder))
    assert sorted(os.listdir(tmp_path / "with" / augment.MODELS)) == [f"{SLUG}.erstudio.ttl", f"{SLUG}.links.csv"]
    assert {k: v for k, v in with_it.items() if k != "augment"}["files"] == plain["files"]


def test_without_augment_the_release_marker_check_script_and_documents_are_as_before(tmp_path):
    rb = rebuild.Rebuild(str(tmp_path / "rel"), str(tmp_path))
    os.makedirs(str(tmp_path / "rel"))
    rb.release_marker()
    assert "augment" not in json.load(open(str(tmp_path / "rel" / "release.json")))
    rb.check_script()
    assert "logical-model" not in (tmp_path / "rel" / "scripts" / "check.sh").read_text()
    for name in ("README.md", "HOW-TO-UPDATE.md", "walkthrough-change.html"):
        with open(os.path.join(HERE, "templates", name)) as f:
            text = f.read()
        assert "<!-- augment -->" in text, name
        plain = rb.augment_blocks(text)
        assert "augment -->" not in plain and "logical model" not in plain.lower(), name
        assert plain == re.sub(r"<!-- augment -->\n.*?<!-- /augment -->\n", "", text, flags=re.S)


def test_the_marker_holds_the_outside_files_and_nothing_else(tmp_path, folder):
    files = {"module": augment.MODULE, "version": augment.VERSION, "files": augment.inputs(str(folder))}
    path = tmp_path / "release.json"
    path.write_text(json.dumps(manifest.marker("2026-11-02", files)))
    assert manifest.is_tool_marker(str(path))
    for bad in ({**files, "folder": "/Users/x"}, {**files, "files": []}, {**files, "files": [{"path": "a", "sha256": "no"}]}, None):
        path.write_text(json.dumps({**manifest.marker("2026-11-02"), "augment": bad}))
        assert not manifest.is_tool_marker(str(path)), bad


def copy_tree(tmp_path):
    """The release's files the build and the registration touch, copied from this checkout (lsc IRIs throughout, so
    the staged example links resolve without the rules), with release.json so the builders run in release mode."""
    rel = tmp_path / "rel"
    shutil.copytree(os.path.join(ROOT, ONT), rel / ONT, ignore=shutil.ignore_patterns("step4", "__pycache__", "*.html"))
    for name in ("epm-walkthrough.html", "epm-ontology-guide.html"):
        shutil.copy(os.path.join(ROOT, ONT, name), rel / ONT / name)
    (rel / "scripts").mkdir()
    for name in ("epm_facts.py", "test_epm_facts.py"):
        shutil.copy(os.path.join(ROOT, "scripts", name), rel / "scripts" / name)
    shutil.copy(os.path.join(HERE, "templates", "check.sh"), rel / "scripts" / "check.sh")
    return rel


def test_the_package_is_built_registered_and_counted(tmp_path, folder):
    rel = copy_tree(tmp_path)
    models = rel / augment.MODELS
    models.mkdir()
    shutil.copy(folder / f"{SLUG}.ttl", models / f"{SLUG}.erstudio.ttl")
    shutil.copy(folder / f"{SLUG}.links.csv", models / f"{SLUG}.links.csv")
    run = lambda args, cwd: subprocess.run([sys.executable, *args], cwd=str(rel / cwd), capture_output=True, text=True, timeout=900,
                                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    r = run(augment.builder_args([SLUG], "--write"), f"{ONT}/logical-model")
    assert r.returncode == 0, r.stdout + r.stderr
    approved = (f"{augment.ANSWERS}/answers-2026-11-03-logical-model-release.md", WORDS)
    ctx = augment.context(str(rel), str(tmp_path), approved, str(folder), {"EPM-DEC-001-0113": "2026-11-02"}, issued="2026-11-03")
    augment.write_changelog(str(rel), ctx, {})
    places = augment.apply(str(rel), augment.REGISTRATION, ctx)
    assert len(places) == len(augment.REGISTRATION)
    (rel / "release.json").write_text(json.dumps(manifest.marker("2026-11-03")))  # release mode, as the cut's rebuild runs it
    r = run(["build_module.py", augment.MODULE, "--write"], f"{ONT}/release")
    assert r.returncode == 0, r.stdout + r.stderr
    r = run(["build_module.py", augment.MODULE, "--verify"], f"{ONT}/release")
    assert r.returncode == 0 and "release package is current" in r.stdout, r.stdout + r.stderr
    package = rel / ONT / "releases" / augment.MODULE / augment.VERSION
    m = json.loads((package / "manifest.json").read_text())
    assert m["augment"] == augment.inputs(str(folder)) and m["approved_by"]["words"] == WORDS
    for kind in ("erstudio", "layer"):  # each model's two graphs ship as the builder wrote them
        assert (package / f"{SLUG}.{kind}.ttl").read_bytes() == (models / f"{SLUG}.{kind}.ttl").read_bytes()
        assert f"{SLUG}.{kind}.ttl" in m["files"]
    assert set(m["depends_on"]) == {"party", "system", "data-product"}
    # Registered: the builder's table, the projection, the module list and the check script name it.
    tree = ast.parse((rel / ONT / "release" / "build_module.py").read_text())
    table = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "MODULES")
    assert table[augment.MODULE]["graphs"] == [f"logical-model/models/{SLUG}.erstudio.ttl", f"logical-model/models/{SLUG}.layer.ttl"]
    assert '("logical-model", "1.0.0")]\nINPUTS' in (rel / ONT / "projection" / "pipeline.py").read_text()
    assert json.loads((rel / ONT / "projection" / "skill-run" / "epm-config.json").read_text())["packages"][augment.MODULE] == augment.VERSION
    assert '"lane", "logical-model", "market-data"' in (rel / "scripts" / "test_epm_facts.py").read_text()
    check = augment.patch_check_sh((rel / "scripts" / "check.sh").read_text(), ctx)
    assert "build_module.py logical-model --verify" in check and f"--model {SLUG}" in check
    # Counted: the module map reads one more module than main's, and the guide's figures follow the packages.
    sys.path.insert(0, str(rel / "scripts"))
    try:
        import importlib
        facts = importlib.import_module("epm_facts")
        mods = facts.module_releases(str(rel / ONT / "releases"), str(rel / ONT / "release" / "build_module.py"))
    finally:
        sys.path.remove(str(rel / "scripts"))
        sys.modules.pop("epm_facts", None)
    assert augment.MODULE in [x["module"] for x in mods]
    assert ctx["count_release"] == len(manifest.MODULES) + 1
    ctx.update(total=12345, triples=m["triples"], requires="party 2.1.0, system 1.5.0, data-product 1.2.0")
    augment.apply(str(rel), augment.FIGURES, ctx)
    guide = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", (rel / ONT / "epm-ontology-guide.html").read_text()))
    assert f"logical-model 1.0.0 {m['triples']} triples" in guide
    assert f"Modules {ctx['count_release']} each released" in guide and "Triples 12,345 in the" in guide
    assert f"{augment.number_word(ctx['count_release'])} newest releases" in guide


def test_a_missing_anchor_stops_the_registration():
    with pytest.raises(SystemExit, match="pipeline.py PACKAGES"):
        augment.patch_pipeline("PACKAGES = []\n", {})
    with pytest.raises(SystemExit, match="the walkthrough states no module count"):
        augment.patch_walkthrough("no count here", {"count_main": 11, "count_release": 12})


def small_release(tmp_path, folder):
    """A release tree as a cut with --augment leaves it, as far as the validation reads it: the staged models,
    release.json and the package's manifest with the outside files, and a check script that passes."""
    rel = tmp_path / "small"
    augment.stage(str(rel), str(folder), {})
    files = augment.inputs(str(folder))
    (rel / "release.json").write_text(json.dumps(manifest.marker("2026-11-03", {"module": augment.MODULE, "version": augment.VERSION, "files": files})))
    package = rel / ONT / "releases" / augment.MODULE / augment.VERSION
    package.mkdir(parents=True)
    (package / "manifest.json").write_text(json.dumps({"augment": files}))
    (rel / "scripts").mkdir()
    (rel / "scripts" / "check.sh").write_text("echo all checks passed\n")
    return rel


def test_the_comparison_and_the_clones_check_take_the_augment_folder_and_say_so(tmp_path, folder):
    import clonecheck
    import validate
    rel = small_release(tmp_path, folder)
    row = validate.augment_row(str(rel), str(folder), {})
    assert row["ok"] and row["files"] == [f"{SLUG}.ttl", f"{SLUG}.links.csv"]
    assert not validate.augment_row(str(rel), None, {})["ok"]  # a release cut with the folder, compared without it
    log = tmp_path / "clone.log"
    assert clonecheck.run(str(rel), str(log), 60, str(folder)) == 0
    assert log.read_text().splitlines()[-1].startswith("with the augment folder: logical-model 1.0.0, 2 outside files")
    assert clonecheck.run(str(rel), str(log), 60) == 1 and "pass --augment" in log.read_text()
    (folder / f"{SLUG}.links.csv").write_text((folder / f"{SLUG}.links.csv").read_text() + "\n")  # the folder moved on
    assert not validate.augment_row(str(rel), str(folder), {})["ok"]
    assert clonecheck.run(str(rel), str(log), 60, str(folder)) == 1 and "differ" in log.read_text()


def test_a_rule_that_touched_er_studios_namespace_would_stop_the_stage(tmp_path, folder, monkeypatch):
    monkeypatch.setattr(rules, "apply", lambda text, path, dates: (text.replace("www.erstudio.com", "example.org"), {}))
    with pytest.raises(SystemExit, match="ER Studio's namespace"):
        augment.stage(str(tmp_path / "rel"), str(folder), {})
