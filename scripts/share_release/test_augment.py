"""The augment folder (augment.py; EPM-DEC-001-0113), tested with the logical-model module's made-up example as the
folder: without --augment nothing changes; with it the models are staged through the rules (the module's own IRIs move
to w3id.org/mpc, ER Studio's namespace is untouched and passes the gate), the package is built, registered and counted,
its manifest and release.json hold the outside files' hashes, and --augment without the decision owner's approval is
refused before anything is removed."""
import ast
import hashlib
import html
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
    for unrelated in ("go ahead", "yes to all", "approve 1.0.0", "do not approve logical-model 1.0.0 yet"):
        epm, path = answers(tmp_path, "Block 1:\n\n> " + unrelated + "\n")
        with pytest.raises(SystemExit, match="do not approve logical-model 1.0.0 by name"):
            augment.approval(epm, path, unrelated)  # words in the file that approve something else, or refuse
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
    before = {p: (rel / p).read_text(encoding="utf-8") for p, _ in augment.REGISTRATION}
    places = augment.apply(str(rel), augment.REGISTRATION, ctx)
    assert len(places) == len(augment.REGISTRATION)
    unchanged = [p for p in before if (rel / p).read_text(encoding="utf-8") == before[p]]
    assert unchanged == [], unchanged  # Codex's round 1: every registration place is written, not only called
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
    # Figured: the catalog is rebuilt, and every figure of the pages comes from the tree (Codex's review of #474).
    r = run(["build_catalog.py", "--write"], f"{ONT}/release")
    assert r.returncode == 0, r.stdout + r.stderr
    main, fig = augment.release_figures(ROOT), augment.release_figures(str(rel))
    package_files = sum(len(f) for _, _, f in os.walk(rel / ONT / "releases" / augment.MODULE))
    assert (fig["modules"], fig["catalog"], fig["versions"]) == (main["modules"] + 1, main["catalog"] + 1, main["versions"] + 1)
    assert fig["files"] == main["files"] + package_files and fig["graphs"] == main["graphs"] + fig["graphs_per_module"]
    assert fig["quads"] > main["quads"] and fig["total"] >= main["total"] and fig["triples"] == m["triples"]
    ctx.update(fig, requires=", ".join(f"{d} {v}" for d, v in fig["requires"].items()))
    assert augment.apply(str(rel), augment.FIGURES, ctx) == [p for p, _ in augment.FIGURES]
    guide = visible((rel / ONT / "epm-ontology-guide.html").read_text())
    walk = visible((rel / ONT / "epm-walkthrough.html").read_text())
    assert f"logical-model 1.0.0 {m['triples']} triples" in guide and f"Modules {fig['modules']} each released" in guide
    assert f"Triples {fig['total']:,} in the {augment.number_word(fig['modules'])} newest releases" in guide
    assert f"{fig['modules']} modules · {fig['versions']} versions · {fig['files']} files" in guide
    assert f"catalog of all {fig['catalog']} released packages in this release" in guide
    assert f"Expect {fig['graphs']} graphs and {fig['quads']:,} triples on these releases" in walk
    assert f"The catalog lists {fig['catalog']} releases in this release" in walk


def test_a_missing_anchor_stops_the_registration():
    with pytest.raises(SystemExit, match="pipeline.py PACKAGES"):
        augment.patch_pipeline("PACKAGES = []\n", {})
    with pytest.raises(SystemExit, match="the walkthrough, the overview's modules: the anchor"):
        augment.patch_walkthrough("no count here", dict(MADE_UP, slugs=[SLUG]))


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


def test_the_rebuilds_release_marker_lists_the_augment_folders_files(tmp_path, folder):
    # Codex's round 1: the marker the cut writes, not one built by hand, carries the outside files and their hashes.
    rel = tmp_path / "release"
    rel.mkdir()
    rebuild.Rebuild(str(rel), str(tmp_path), augment_folder=str(folder), approval=("a.md", WORDS)).release_marker()
    marker = json.loads((rel / "release.json").read_text())
    expected = {"module": augment.MODULE, "version": augment.VERSION, "files": augment.inputs(str(folder))}
    assert marker == manifest.marker(marker["built"], expected)
    rebuild.Rebuild(str(rel), str(tmp_path)).release_marker()
    marker = json.loads((rel / "release.json").read_text())
    assert marker == manifest.marker(marker["built"])


# ---- Every figure of the guide and the walkthrough that could name the release set, classified ----

def visible(page):
    """The text a reader sees, aria-labels included, on one line."""
    page = re.sub(r"<(style|script)\b.*?</\1>", " ", page, flags=re.S)
    page = re.sub(r'src="data:[^"]*"', "", page)
    page = re.sub(r'aria-label="([^"]*)"', r"> \1 <", page)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page)))


# A made-up augmented release: every figure differs from main's, so a figure the patches miss still reads main's.
MADE_UP = {"modules": len(manifest.MODULES) + 1, "total": 12345, "triples": 99, "catalog": 61, "versions": 60, "files": 400,
           "mb": 70, "graphs_per_module": 3, "graphs": 45, "quads": 54321,
           "requires": "data-product 1.2.0, party 2.1.0, system 1.5.0"}

# What could state the release set: a count of modules, releases, packages, versions, files, triples, quads, graphs or
# rows, at least as large as the smallest module count the pages give (eleven), a stat of the guide, or one of main's
# own figures written anywhere. Each hit must lie inside a pattern of FIGURE_CLASSES.
UNITS = r"(?:newest |released |earlier |versioned, checked )?(?:modules?|releases?|packages?|versions?|version folders|release files|release records|files|triples|quads|named graphs|graphs|rows)\b"

# (class, pattern before, pattern after). The patterns are on the visible text after the rewrite rules, formatted with
# main's figures (m_*, from the tree) and the made-up release's (a_*). "present" states the release set as it is: the
# patch rewrites it, so the before pattern is gone and the after pattern is there as often. Every other class stays as
# it is: "history" is dated, "stores" is what a store held at its last load (the next reload holds the release's
# figure), "other" counts something the release set does not change.
FIGURE_CLASSES = {
    "epm-ontology-guide.html": [
        ("present", r"split into {m_w} modules", r"split into {a_w} modules"),
        ("history", r"of the {m_w1} earlier modules\.", None),
        ("present", r"Modules {m_n} each released", r"Modules {a_n} each released"),
        ("present", r"Triples {m_total} in the {m_w} newest releases together", r"Triples {a_total} in the {a_w} newest releases together"),
        ("present", r"It is {m_w} modules because", r"It is {a_w} modules because"),
        ("present", r"It runs over the {m_w} newest releases loaded together, {m_total} triples since technical-graph 1\.0\.0 \(",
         r"It runs over the {a_w} newest releases loaded together, {a_total} triples since logical-model 1\.0\.0, in this release "
         r"\({m_total} since technical-graph 1\.0\.0, 2026-11-02; 36,951 since kpi 1\.3\.0 before it\)"),
        ("history", r"over 36,901 triples, after that day's releases", None),
        ("present", r"which prints {m_total} triples and 14 rows \(36,951 before",
         r"which prints {a_total} triples and 14 rows in this release \({m_total} before logical-model 1\.0\.0; 36,951 before"),
        # The query reads no statement of logical-model's vocabulary, so its output keeps its 14 rows.
        ("other", r"MPR 14 rows\. The Gulf Coast filter", None),
        # Each module card's own count; the patch adds logical-model's card (ADDED).
        ("other", r"\b(?:core|kpi|market-data|data-product|system|organization|value-stream|party|ref-mpc|lane|integration|technical-graph) \d+\.\d+\.\d+ [\d,]+ triples Holds", None),
        ("other", r"569,976 rows, refreshed", None),
        ("other", r"142 and 540 rows", None),
        ("present", r"as Turtle: {m_w} modules since technical-graph 1\.0\.0 \(2026-11-02\)",
         r"as Turtle: {a_w} modules since logical-model 1\.0\.0, in this release \({m_w} since technical-graph 1\.0\.0, 2026-11-02\)"),
        ("stores", r"over 36,951 triples Two loads", None),
        ("stores", r"loaded from 1 Module ;", None),  # a Neo4j table: one Module node per store marker
        ("stores", r"40,169 quads in 33 graphs", None),
        ("stores", r"40,169 rows in 33 named graphs", None),
        ("stores", r"11 Module and 11 ModuleRelease nodes", None),
        ("stores", r"33 named graphs, three per module, 40,169 quads", None),
        ("present", r"In all: {m_all} files and three links\. That is {m_files} release files",
         r"In all: {a_all} files and three links\. That is {a_files} release files"),
        ("present", r"the releases folder with {m_w} modules", r"the releases folder with {a_w} modules"),
        ("present", r"releases/ {m_n} modules · {m_versions} versions · {m_files} files", r"releases/ {a_n} modules · {a_versions} versions · {a_files} files"),
        ("present", r"releases/ : {m_n} modules, {m_versions} version folders and {m_files} files, about {m_mb} MB \(since technical-graph",
         r"releases/ : {a_n} modules, {a_versions} version folders and {a_files} files, about {a_mb} MB, in this release "
         r"\({m_n} modules, {m_versions} version folders and {m_files} files on main since technical-graph"),
        ("present", r"catalog of all {m_catalog} released packages:", r"catalog of all {a_catalog} released packages in this release:"),
        ("present", r"for the whole ontology \({m_total} triples\)", r"for the whole ontology \({a_total} triples\)"),
    ],
    "epm-walkthrough.html": [
        ("stores", r"loaded from 1 Module ;", None),  # a Neo4j table: one Module node per store marker
        ("other", r"Step 4 Release Checklist", None),  # a document title, not a count
        ("present", r"L0 to L6 {m_n} modules Turtle in git", r"L0 to L6 {a_n} modules Turtle in git"),
        ("present", r"Turtle in git {m_catalog} releases one DCAT catalog", r"Turtle in git {a_catalog} releases one DCAT catalog"),
        ("stores", r"Delta, 40,169 rows", None),
        ("history", r"ended as 50 versioned, checked releases \({m_catalog} since technical-graph 1\.0\.0, 2026-11-02\)", None),
        ("history", r"first catalog of 19 releases on 2026-10-22", None),
        ("history", r"kpi 1\.3\.0 and 50 releases on 2026-10-28", None),
        ("history", r"10-28 kpi 1\.3\.0; 50 releases", None),
        ("present", r"checks the same {m_w} packages in CI \(eleven until technical-graph",
         r"checks the same {a_w} packages in CI in this release, with logical-model 1\.0\.0 \({m_w} on main; eleven until technical-graph"),
        ("stores", r"from {m_total} triples and 2 inferred, every check passing", None),
        ("stores", r"epm_triples at 40,169 quads", None),
        ("present", r"printed, 4,234 and 22,302 on these releases, and {m_n} release records",
         r"printed \(4,234 and 22,302 on main's {m_w} modules, before logical-model 1\.0\.0 was added in this release\), and {a_n} release records"),
        ("present", r"Expect {m_graphs} graphs and {m_quads} triples on these releases: three graphs for each of {m_n} modules \(33 and 40,169 for the eleven before",
         r"Expect {a_graphs} graphs and {a_quads} triples on these releases: three graphs for each of {a_n} modules \({m_graphs} and {m_quads} "
         r"for the {m_w} before logical-model 1\.0\.0, added in this release; 33 and 40,169 for the eleven before"),
        ("present", r"this returns {m_quads_plain} and {m_graphs} for these releases \(40169 and 33",
         r"this returns {a_quads_plain} and {a_graphs} for these releases \({m_quads_plain} and {m_graphs} before logical-model 1\.0\.0, added in this release; 40169 and 33"),
        ("other", r"returns two rows|it returned 11 rows|this returned 11 rows|the walk 11 rows|Expect 11 rows", None),
        ("other", r"up to 500 rows as whole JSON, up from a cut at 20 rows", None),
        ("stores", r"over 36,951 triples Two loads", None),
        ("stores", r"40,169 quads in 33 graphs", None),
        ("stores", r"40,169 rows in 33 named graphs", None),
        ("stores", r"11 Module and 11 ModuleRelease nodes", None),
        ("stores", r"33 named graphs, three per module, 40,169 quads", None),
        ("other", r"142 and 540 rows", None),
        ("other", r"91 rows \(90 until 2026-11-02", None),
        ("other", r"569,976 rows, refreshed", None),
        ("other", r"steps 7-12 Modules steps 13-20", None),
        ("other", r"707 concepts, 14,659 triples", None),
        ("other", r"Expect 33 rows", None),
        ("present", r"The catalog lists {m_catalog} releases \(50 until technical-graph 1\.0\.0, 2026-11-02;",
         r"The catalog lists {a_catalog} releases in this release \(on main, {m_catalog} since technical-graph 1\.0\.0, 2026-11-02, and 50 until then;"),
        ("present", r"Expect {m_w} modules, newest core 2\.4\.0 and kpi 1\.3\.0 \(eleven until",
         r"Expect {a_w} modules, newest core 2\.4\.0 and kpi 1\.3\.0 \({m_w} until logical-model 1\.0\.0, added in this release; eleven until"),
        ("present", r"after a record, 4,234 nodes, 22,302 relationships, {m_total} triples and 2 inferred",
         r"after a record on this release, the run's nodes, relationships and inferences over {a_total} triples \(on main since "
         r"technical-graph 1\.0\.0, 2026-11-02: 4,234 nodes, 22,302 relationships, {m_total} triples and 2 inferred\)"),
        ("stores", r"epm_triples 40,169 quads, hash equal; 14 walks equal; the Jena walk store 37,089 quads", None),
        ("other", r"crack-spread gold table of 108,204 rows", None),
        # The file map's rows: each folder's own files, and each module's own packages, which the release set does not change.
        ("other", r"\(\d+ files(?:: Turtle, JSON-LD, shapes, DCAT record, manifest)?\)|\(109 files,", None),
    ],
}


# What the patches add for the module: its card, its row of the newest versions and of the module table, and a word
# where a map does not draw it.
ADDED = {
    "epm-ontology-guide.html": [r"logical-model 1\.0\.0 {a_triples} triples Holds", r"logical-model 1\.0\.0 {a_requires}",
                                r"In this release they also count logical-model 1\.0\.0",
                                r"logical-model 1\.0\.0, added in this release, is not drawn; it requires {a_requires}\.",
                                r"every one except ref-mpc , technical-graph and logical-model ;"],
    "epm-walkthrough.html": [r"logical-model 1\.0\.0, added in this release, is drawn in neither map\.",
                             r"Every module folder but technical-graph and logical-model has the same shape",
                             r"logical-model Logical data models exported from ER Studio Data Architect"],
}


def figure_values(fig, prefix):
    out = {f"{prefix}_{k}": v for k, v in fig.items() if isinstance(v, int)}
    out.update({f"{prefix}_n": fig["modules"], f"{prefix}_w": augment.number_word(fig["modules"]),
                f"{prefix}_w1": augment.number_word(fig["modules"] - 1), f"{prefix}_total": f"{fig['total']:,}",
                f"{prefix}_quads": f"{fig['quads']:,}", f"{prefix}_quads_plain": str(fig["quads"])})
    return out


def test_every_figure_of_the_pages_is_classified_and_an_augmented_release_rewrites_the_present_ones():
    """The real guide and walkthrough, as the cut has them (after the rewrite rules), patched for a made-up augmented
    release: each figure that states the release set reads the release's figure, no present figure keeps main's, and
    every other figure stays. A figure added to a page later fails here until it is classified."""
    main = augment.release_figures(ROOT)
    dates = export.record_dates(ROOT)
    with open(os.path.join(ROOT, ONT, "epm-ontology-guide.html"), encoding="utf-8") as f:
        guide = rules.apply(f.read(), f"{ONT}/epm-ontology-guide.html", dates)[0]
    copy = re.search(r"In all: (\d+) files and three links\. That is (\d+) release files", visible(guide))
    others = int(copy.group(1)) - int(copy.group(2))  # the pages and the files for using it, which the release set does not change
    values = figure_values(main, "m") | figure_values(MADE_UP, "a")
    values.update(m_all=main["files"] + others, a_all=MADE_UP["files"] + others, a_requires=re.escape(MADE_UP["requires"]))
    ctx = dict(MADE_UP, slugs=[SLUG])
    big = [augment.number_word(n) for n in range(main["modules"] - 1, len(augment.WORDS))]
    own = sorted({f"{main[k]:,}" for k in ("total", "quads", "files")} | {str(main["quads"]), str(main["total"]), str(values["m_all"])}, key=len, reverse=True)
    detect = re.compile(rf"(?<![\w.,-])(\d[\d,]*|{'|'.join(big)}) {UNITS}|\b(?:Modules|Triples) \d[\d,]*|(?<![\d,])(?:{'|'.join(map(re.escape, own))})(?![\d,])", re.I)
    for name, fn in (("epm-ontology-guide.html", augment.patch_guide), ("epm-walkthrough.html", augment.patch_walkthrough)):
        path = f"{ONT}/{name}"
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            page = rules.apply(f.read(), path, dates)[0]
        before, after = visible(page), visible(fn(page, ctx))
        classes = [(cls, b.format(**values), a and a.format(**values)) for cls, b, a in FIGURE_CLASSES[name]]
        spans = [m.span() for _, b, _ in classes for m in re.finditer(b, before)]
        loose = []
        for m in detect.finditer(before):
            unit = m.group(0).rsplit(" ", 1)[-1].lower()
            if m.group(1) and m.group(1)[0].isdigit() and int(m.group(1).replace(",", "")) < main["modules"] - 1 \
                    and unit.rstrip("s") in ("file", "triple", "quad", "row"):
                continue  # a small count of files, triples or rows; a count of modules, releases, packages, versions or graphs is always checked (Codex)
            if not any(s <= m.start() and m.end() <= e for s, e in spans):
                loose.append(f"{m.group(0)!r} in {before[max(0, m.start() - 80):m.end() + 40]!r}")
        assert not loose, f"{name}: figures no class in FIGURE_CLASSES covers:\n" + "\n".join(map(repr, loose))
        for added in ADDED[name]:
            assert len(re.findall(added.format(**values), after)) == 1, f"{name}: the augmented release does not say {added!r}"
        for cls, b, a in classes:
            found = len(re.findall(b, before))
            assert found, f"{name}: the {cls} figure {b!r} is not on the page; update FIGURE_CLASSES"
            if cls == "present":
                assert not re.search(b, after), f"{name}: {b!r} still states main's figure in an augmented release"
                assert len(re.findall(a, after)) == found, f"{name}: the augmented release does not say {a!r}"
            else:
                assert len(re.findall(b, after)) == found, f"{name}: the {cls} figure {b!r} changed"
