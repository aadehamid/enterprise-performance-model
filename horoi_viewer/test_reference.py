"""Fail-closed source binding, semantic fidelity, and additive-release checks."""

import hashlib
import json
from pathlib import Path

import pytest

from horoi_viewer import build as b
from horoi_viewer import release as r


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
    data = {"sourceCommit": b.CONFIG["source_commit"], "inputs": [], "pilotTerms": ["urn:term"],
            "triples": 1, "nodes": [{"id": "urn:term", "values": [{"p": "urn:definition", "v": "A definition", "literal": True}]}]}
    monkeypatch.setattr(b, "payload", lambda source: data)
    return data


def make_docs(path, data):
    path.mkdir()
    for name in r.DOC_FILES:
        (path / name).write_text("document\n")
    html = '<script id="ontology-data" type="application/json">' + b.script_json(data) + '</script>'
    (path / "index.html").write_text(html)
    (path / "build.json").write_text(json.dumps({"source_commit": b.CONFIG["source_commit"],
        "index_sha256": hashlib.sha256(html.encode()).hexdigest(), "inputs": data["inputs"]}))
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
    assert payload["pilotTerms"] == ["urn:Party", "urn:Stage"]
    assert [m["id"] for m in payload["moduleInfo"]] == ["urn:party"]
    assert len(payload["nodes"]) == 5


def test_stage_preserves_every_original_file(source, tmp_path, sample_data):
    docs = make_docs(tmp_path / "docs", sample_data)
    output = tmp_path / "release"
    result = r.stage(source, docs, output)
    assert result["unchanged_files"] == 2
    assert (output / "README.md").read_bytes() == b"Original release\n"
    assert (output / "script.sh").stat().st_mode & 0o100
    assert result["added_files"] == sorted("horoi_viewer/" + n for n in r.DOC_FILES)


@pytest.mark.parametrize("mutation", ["change", "delete", "mode", "extra", "symlink"])
def test_release_guard_rejects_changes(source, tmp_path, sample_data, mutation):
    output = tmp_path / "release"
    r.stage(source, make_docs(tmp_path / "docs", sample_data), output)
    if mutation == "change":
        (output / "README.md").write_text("Changed")
    elif mutation == "delete":
        (output / "README.md").unlink()
    elif mutation == "mode":
        (output / "script.sh").chmod(0o644)
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
