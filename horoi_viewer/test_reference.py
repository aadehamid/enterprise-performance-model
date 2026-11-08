"""Fail-closed source binding, semantic fidelity, and additive-release checks."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from horoi_viewer import build as b
from horoi_viewer import release as r


def test_explorer_model_counterexamples():
    """Run the same assertion index used by the browser on adversarial graphs."""
    subprocess.run(["node", str(Path(__file__).with_name("test_explorer_model.cjs"))],
                   check=True, capture_output=True, text=True, timeout=30)


def git(path, *args):
    return b.git(path, *args).decode().strip()


@pytest.fixture
def source(tmp_path, monkeypatch):
    root = tmp_path / "source"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    (root / "README.md").write_text("Original release\n")
    (root / "script.sh").write_text("#!/bin/sh\nexit 0\n")
    (root / "script.sh").chmod(0o755)
    git(root, "add", ".")
    git(root, "commit", "-qm", "Fixture")
    config = dict(b.CONFIG, source_commit=git(root, "rev-parse", "HEAD"))
    monkeypatch.setattr(b, "CONFIG", config)
    return root


@pytest.fixture
def sample_data(monkeypatch):
    data = {"sourceCommit": b.CONFIG["source_commit"], "inputs": [], "referenceTerms": ["urn:term"], "referenceModules": ["party"],
            "triples": 1, "nodes": [{"id": "urn:term", "values": [{"p": "urn:definition", "v": "A definition", "literal": True}]}]}
    monkeypatch.setattr(b, "payload", lambda source: data)
    return data


def make_docs(path, data):
    path.mkdir()
    for name, content in b.render_files(data).items():
        (path / name).write_bytes(content)
    return path


def test_pin_rejects_another_commit(source, monkeypatch):
    monkeypatch.setitem(b.CONFIG, "source_commit", "0" * 40)
    with pytest.raises(ValueError, match="Expected release"):
        b.verify_source(source)


def test_local_source_change_is_refused(source):
    (source / "README.md").write_text("Changed\n")
    with pytest.raises(ValueError, match="clean checkout"):
        b.verify_source(source)


def test_assume_unchanged_does_not_hide_source_change(source):
    git(source, "update-index", "--assume-unchanged", "README.md")
    (source / "README.md").write_text("Changed\n")
    with pytest.raises(ValueError, match="pinned commit"):
        b.verify_source(source)


def test_script_json_cannot_close_its_element():
    value = {"definition": '</script><script>alert("x")</script> & <tag>', "lang": "fr"}
    encoded = b.script_json(value)
    assert "<" not in encoded
    assert json.loads(encoded) == value


def test_payload_round_trip_keeps_layers_and_one_header_per_module(source, monkeypatch):
    manifest = source / "manifest.json"
    manifest.write_text(json.dumps({"ontology_iri": "urn:party", "version": "1.0"}))
    git(source, "add", "manifest.json")
    modules = [{"name": "party"}]
    def node(identifier, kind):
        return {"id": identifier, "kind": kind, "label": identifier,
                "modules": modules, "values": []}
    raw = {"nodes": [node("urn:party", "Metadata"), node("urn:imported", "Metadata"),
                     node("urn:Party", "Class"), node("urn:Stage", "Concept"),
                     node("_:shape", "Shape")], "inputs": [], "supportingKinds": ("Shape",)}
    monkeypatch.setitem(b.CONFIG, "modules", ["party"])
    monkeypatch.setattr(b.reader, "build_data", lambda root: raw)
    monkeypatch.setattr(b.reader, "release_files", lambda root: [(source / "ontology.ttl", "party", "1.0")])
    monkeypatch.setattr(b.reader, "SUPPORTING_KINDS", ("Shape",))
    payload = b.payload(source)
    assert json.loads(b.script_json(payload)) == payload
    assert payload["referenceTerms"] == ["urn:Party", "urn:Stage"]
    assert [m["id"] for m in payload["moduleInfo"]] == ["urn:party"]
    assert len(payload["nodes"]) == 5


def test_all_modules_are_discovered_from_the_release_manifests(source, monkeypatch):
    raw_nodes, files = [], []
    for module in ["party", "new-module"]:
        folder = source / module
        folder.mkdir()
        (folder / "manifest.json").write_text(json.dumps({"ontology_iri": "urn:" + module, "version": "1.0"}))
        files.append((folder / "ontology.ttl", module, "1.0"))
        for suffix, kind in [("", "Metadata"), ("/Term", "Class"), ("/Rule", "Shape")]:
            raw_nodes.append({"id": "urn:" + module + suffix, "kind": kind, "label": module + suffix,
                              "modules": [{"name": module}], "values": []})
    git(source, "add", ".")
    monkeypatch.setitem(b.CONFIG, "modules", "all")
    monkeypatch.setattr(b.reader, "release_files", lambda root: files)
    monkeypatch.setattr(b.reader, "build_data", lambda root: {"nodes": raw_nodes, "inputs": [], "supportingKinds": ["Shape"]})
    monkeypatch.setattr(b.reader, "SUPPORTING_KINDS", ("Shape",))
    before = json.dumps(raw_nodes, sort_keys=True)
    data = b.payload(source)
    assert data["referenceModules"] == ["new-module", "party"]
    assert set(data["referenceTerms"]) == {"urn:party/Term", "urn:new-module/Term"}
    assert json.dumps(data["nodes"], sort_keys=True) == before
    monkeypatch.setitem(b.CONFIG, "modules", ["party", "absent"])
    with pytest.raises(ValueError, match="release module"):
        b.payload(source)


def test_stage_preserves_every_original_file(source, tmp_path, sample_data):
    docs = make_docs(tmp_path / "docs", sample_data)
    output = tmp_path / "release"
    result = r.stage(source, docs, output)
    assert result["unchanged_files"] == 2
    assert (output / "README.md").read_bytes() == b"Original release\n"
    assert (output / "script.sh").stat().st_mode & 0o100
    assert result["added_files"] == sorted("horoi_viewer/" + n for n in r.DOC_FILES)


@pytest.mark.parametrize("mutation", ["change", "delete", "mode", "read_mode", "nested_git", "root_git_file", "root_git_directory", "extra", "symlink"])
def test_release_guard_rejects_changes(source, tmp_path, sample_data, mutation):
    output = tmp_path / "release"
    r.stage(source, make_docs(tmp_path / "docs", sample_data), output)
    if mutation == "change":
        (output / "README.md").write_text("Changed")
    elif mutation == "delete":
        (output / "README.md").unlink()
    elif mutation == "read_mode":
        (output / "script.sh").chmod(0o555)
    elif mutation == "mode":
        (output / "script.sh").chmod(0o644)
    elif mutation == "nested_git":
        hidden = output / "horoi_viewer/.git"
        hidden.mkdir()
        (hidden / "extra.ttl").write_text("extra data")
    elif mutation == "root_git_file":
        (output / ".git").write_text("not git metadata")
    elif mutation == "root_git_directory":
        (output / ".git").mkdir()
        (output / ".git/payload").write_text("extra data")
    elif mutation == "extra":
        (output / "extra.ttl").write_text("extra data")
    else:
        (output / "extra-link").symlink_to(source / "README.md")
    with pytest.raises(ValueError):
        r.verify(source, output)


def test_changed_data_fails_even_when_html_hash_is_updated(source, tmp_path, sample_data):
    output = tmp_path / "release"
    r.stage(source, make_docs(tmp_path / "docs", sample_data), output)
    index = output / "horoi_viewer/index.html"
    index.write_text(index.read_text().replace("A definition", "Invented definition"))
    report_path = output / "horoi_viewer/build.json"
    report = json.loads(report_path.read_text())
    report["index_sha256"] = hashlib.sha256(index.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="data differs"):
        r.verify(source, output)


def test_stage_never_overwrites_a_folder(source, tmp_path, sample_data):
    output = tmp_path / "existing"
    output.mkdir()
    (output / "precious").write_text("keep me")
    with pytest.raises(ValueError, match="existing folders"):
        r.stage(source, make_docs(tmp_path / "docs", sample_data), output)
    assert (output / "precious").read_text() == "keep me"


def test_build_refuses_to_write_inside_source(source, sample_data):
    with pytest.raises(ValueError, match="outside the source"):
        b.build(source, source / "docs")


def test_existing_output_is_never_replaced(source, tmp_path, sample_data):
    output = tmp_path / "existing"
    output.mkdir()
    (output / "precious").write_text("keep me")
    with pytest.raises(ValueError, match="never replaced"):
        b.build(source, output)
    assert (output / "precious").read_text() == "keep me"


def test_vendor_matches_recorded_upstream_bytes():
    lock = json.loads((b.HERE / "vendor/upstream.json").read_text())
    assert lock["commit"] == b.CONFIG["horoi_commit"]
    for name, expected in lock["files"].items():
        assert hashlib.sha256((b.HERE / "vendor" / name).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize("mutation", ["javascript", "license", "notice", "metadata"])
def test_generated_files_must_match_the_builder(source, tmp_path, sample_data, mutation):
    docs = tmp_path / "docs"
    b.build(source, docs)
    output = tmp_path / "release"
    r.stage(source, docs, output)
    generated = output / "horoi_viewer"
    if mutation == "javascript":
        index = generated / "index.html"
        index.write_text(index.read_text().replace("</body>", "<script>window.changed=true</script></body>"))
        record = json.loads((generated / "build.json").read_text())
        record["index_sha256"] = hashlib.sha256(index.read_bytes()).hexdigest()
        (generated / "build.json").write_text(json.dumps(record))
    elif mutation == "metadata":
        record = json.loads((generated / "build.json").read_text())
        record["reference_terms"] = 99999
        (generated / "build.json").write_text(json.dumps(record))
    else:
        name = "LICENSE.txt" if mutation == "license" else "NOTICE.txt"
        (generated / name).write_text("Replaced notices")
    with pytest.raises(ValueError, match="generated documentation"):
        r.verify(source, output)


@pytest.mark.parametrize("target", ["source-new", "source-existing", "git-config", "docs", "existing-report", "missing-parent"])
def test_report_never_changes_inputs_or_existing_files(source, tmp_path, sample_data, monkeypatch, target):
    docs = tmp_path / "docs"
    b.build(source, docs)
    report = {"source-new": source / "audit.json", "source-existing": source / "README.md",
              "git-config": source / ".git/config", "docs": docs / "NOTICE.txt",
              "existing-report": tmp_path / "audit.json",
              "missing-parent": tmp_path / "missing/audit.json"}[target]
    if target == "existing-report":
        report.write_text("Keep this evidence")
    before = report.read_bytes() if report.exists() else None
    output = tmp_path / "release"
    monkeypatch.setattr(sys, "argv", ["release", "stage", "--source", str(source),
        "--docs", str(docs), "--out", str(output), "--report", str(report)])
    with pytest.raises(SystemExit) as exc:
        r.main()
    assert exc.value.code == 2
    assert not output.exists()
    assert (report.read_bytes() if report.exists() else None) == before


def test_real_payload_and_embedded_rdf_match_raw_packages(source, tmp_path, monkeypatch):
    import importlib.util
    import rdflib

    spec = importlib.util.spec_from_file_location(
        "reference_roundtrip_tests", b.HERE.parent / "business_architecture/ontology/viewer/test_viewer.py"
    )
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    for module in ("core", "party"):
        ontology = f"https://example.test/{module}"
        ttl = helpers.TTL + f'\n<{ontology}> a owl:Ontology; rdfs:label "{module}" .\n'
        ttl += f'<{ontology}/Shape> <urn:path> _:detail .\n_:detail <urn:code> "01"^^<http://www.w3.org/2001/XMLSchema#integer> .\n'
        path = helpers.package(source, module=module, ttl=ttl)
        manifest_path = path / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["ontology_iri"] = ontology
        manifest_path.write_text(json.dumps(manifest))
    git(source, "add", ".")
    git(source, "commit", "-qm", "Add nested RDF packages")
    monkeypatch.setitem(b.CONFIG, "source_commit", git(source, "rev-parse", "HEAD"))
    data = b.payload(source)
    output = tmp_path / "built"
    b.build(source, output)
    embedded = json.loads((output / "index.html").read_text().split(
        '<script id="ontology-data" type="application/json">', 1)[1].split("</script>", 1)[0])
    monkeypatch.setattr(rdflib, "NORMALIZE_LITERALS", False)
    helpers.assert_roundtrip(source, data)
    helpers.assert_roundtrip(source, embedded)
    assert embedded == data
