"""Coverage, provenance and safe offline serialization of the release viewer."""

import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    "viewer_builder", Path(__file__).with_name("build.py")
)
viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)

TTL = """@prefix x: <https://example.test/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
x:Thing a owl:Class; rdfs:label "A term"@en; rdfs:subClassOf [ a owl:Restriction; owl:onProperty x:has; owl:someValuesFrom x:Other ] .
x:has a owl:ObjectProperty .
x:Other a owl:Class .
x:Concept a skos:Concept; skos:prefLabel "A concept"@en .
x:individual a x:Thing; rdfs:label "A designed individual" .
"""


def package(root, module="core", version="1.0.0", ttl=TTL):
    p = root / viewer.ONTOLOGY / "releases" / module / version
    p.mkdir(parents=True)
    (p / (module + ".ttl")).write_text(ttl)
    (p / "manifest.json").write_text(
        json.dumps(
            {
                "module": module,
                "version": version,
                "release_candidate": False,
                "files": {module + ".ttl": hashlib.sha256(ttl.encode()).hexdigest()},
            }
        )
    )
    return p


def test_named_terms_and_anonymous_constraints_remain_reachable(tmp_path):
    package(tmp_path)
    data = viewer.build_data(tmp_path)
    nodes = {n["id"]: n for n in data["nodes"]}
    assert data["terms"] == 5
    assert nodes["https://example.test/Thing"]["label"] == "A term"
    restriction = next(n for n in nodes.values() if n["kind"] == "Anonymous node")
    assert any(v["v"] == "https://example.test/Other" for v in restriction["values"])
    assert restriction["id"] in nodes["https://example.test/Thing"]["parents"]
    assert data["triples"] == sum(len(n["values"]) for n in nodes.values())


def test_history_examples_and_live_graph_are_not_inputs(tmp_path):
    package(tmp_path, version="1.0.0", ttl=TTL + "\nx:Old a owl:Class .")
    package(tmp_path, version="2.0.0")
    for extra in [
        "releases/previous/core/0.1.0/old.ttl",
        "technical-graph/example/graph.ttl",
        "projection/out/graph.ttl",
    ]:
        p = tmp_path / viewer.ONTOLOGY / extra
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("invalid RDF must never be read")
    data = viewer.build_data(tmp_path)
    assert not any(n["id"].endswith("/Old") for n in data["nodes"])
    assert len(data["inputs"]) == 1


def test_changed_or_missing_package_fails(tmp_path):
    p = package(tmp_path)
    (p / "core.ttl").write_text(TTL + "\nx:Invented a owl:Class .")
    with pytest.raises(ValueError, match="hash mismatch"):
        viewer.build_data(tmp_path)
    (p / "core.ttl").unlink()
    with pytest.raises(FileNotFoundError):
        viewer.build_data(tmp_path)


def test_customer_schema_and_technical_vocabulary_are_included(tmp_path):
    package(tmp_path, "logical-model", ttl=TTL.replace("x:Thing", "x:CustomerEntity"))
    package(tmp_path, "technical-graph", ttl=TTL.replace("x:Thing", "x:Pipeline"))
    data = viewer.build_data(tmp_path)
    assert {n["id"] for n in data["nodes"]} >= {
        "https://example.test/CustomerEntity",
        "https://example.test/Pipeline",
    }
    blank = [n for n in data["nodes"] if n["kind"] == "Anonymous node"]
    assert len(blank) == 2  # identical blank nodes in different files are distinct


def test_embed_is_script_safe_and_needs_no_network(tmp_path):
    label = "</script><script>alert(1)</script> /* EMBEDDED_FONTS */ FONT_LICENSE_TEXT"
    package(
        tmp_path,
        ttl=TTL + '\nx:attack rdfs:label ' + json.dumps(label) + ' .',
    )
    out = tmp_path / "viewer/index.html"
    viewer.build(tmp_path, out, require_pin=False)
    text = out.read_text()
    payload = text.split('<script id="ontology-data" type="application/json">')[
        1
    ].split("</script>")[0]
    assert "</script>" not in payload
    assert any(
        n["label"] == label
        for n in json.loads(payload)["nodes"]
    )
    assert "data:font/woff2;base64," in text
    assert 'src="http' not in text and 'href="https://fonts' not in text


def test_cut_must_equal_source_packages(tmp_path):
    source = tmp_path / "source"
    cut = tmp_path / "cut"
    package(source)
    package(cut, ttl=TTL + "\nx:Changed a owl:Class .")
    out = tmp_path / "index.html"
    with pytest.raises(ValueError, match="differ"):
        viewer.build(source, out, compare=cut, require_pin=False)
    assert not out.exists()


def test_cut_emits_the_neutral_source_title_and_actual_file_hashes(tmp_path):
    from epm_source_descriptions import OLD_TITLE, NEW_TITLE

    source, cut = tmp_path / "source", tmp_path / "cut"
    ttl = TTL + f'\nx:source <http://purl.org/dc/terms/title> "{OLD_TITLE}"@en .\n'
    package(source, ttl=ttl)
    current = package(cut, ttl=ttl.replace(OLD_TITLE, NEW_TITLE))
    output = tmp_path / "index.html"
    viewer.build(source, output, compare=cut, require_pin=False)
    payload = output.read_text().split('<script id="ontology-data" type="application/json">')[1].split("</script>")[0]
    data = json.loads(payload)
    assert OLD_TITLE not in payload
    assert NEW_TITLE in payload
    assert data["inputs"][0]["sha256"] == hashlib.sha256((current / "core.ttl").read_bytes()).hexdigest()
    assert_roundtrip(cut, data)


@pytest.mark.parametrize("defect", ["unrewritten", "other-title", "meaning", "newline"])
def test_source_title_permission_rejects_every_other_cut_change(tmp_path, defect):
    from epm_source_descriptions import OLD_TITLE, NEW_TITLE

    source, cut = tmp_path / "source", tmp_path / "cut"
    ttl = TTL + f'\nx:source <http://purl.org/dc/terms/title> "{OLD_TITLE}"@en .\n'
    package(source, ttl=ttl)
    updated = ttl.replace(OLD_TITLE, NEW_TITLE)
    bad = {
        "unrewritten": ttl,
        "other-title": updated.replace("A term", "An altered term"),
        "meaning": updated + "\nx:Added a owl:Class .\n",
        "newline": updated.replace("\n", "\r\n"),
    }[defect]
    package(cut, ttl=bad)
    output = tmp_path / "index.html"
    with pytest.raises(ValueError, match="differ"):
        viewer.build(source, output, compare=cut, require_pin=False)
    assert not output.exists()


def test_no_package_is_an_error(tmp_path):
    (tmp_path / viewer.ONTOLOGY / "releases").mkdir(parents=True)
    with pytest.raises(ValueError, match="No released"):
        viewer.build_data(tmp_path)


def test_source_pin_rejects_another_commit_and_local_package_changes(tmp_path, monkeypatch):
    import os
    import subprocess

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for key in list(os.environ):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key)
    package(tmp_path)

    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args], env=env, text=True).strip()

    git("init", "-q")
    git("add", ".")
    git("-c", "user.name=Test fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture")
    with pytest.raises(ValueError, match="Expected source release"):
        viewer.pinned_source(tmp_path)
    monkeypatch.setattr(viewer, "SOURCE_COMMIT", git("rev-parse", "HEAD"))
    viewer.pinned_source(tmp_path)
    manifest = next((tmp_path / viewer.ONTOLOGY / "releases").glob("*/*/manifest.json"))
    manifest.write_text(manifest.read_text() + "\n")
    with pytest.raises(ValueError, match="local changes"):
        viewer.pinned_source(tmp_path)


def assert_roundtrip(root, data=None):
    from rdflib import Graph, URIRef, BNode, Literal
    from rdflib.compare import isomorphic

    expected = Graph()
    # Parse independently and include each current manifest-listed Turtle file.
    for path, _, _ in viewer.release_files(root):
        expected += Graph().parse(path, format="turtle")
    data = viewer.build_data(root) if data is None else data
    actual = Graph()

    def resource(value):
        return BNode(value[2:]) if value.startswith("_:") else URIRef(value)

    for node in data["nodes"]:
        for value in node["values"]:
            obj = (
                Literal(
                    value["v"],
                    lang=value["lang"],
                    datatype=URIRef(value["datatype"]) if value["datatype"] else None,
                )
                if value["literal"]
                else resource(value["v"])
            )
            actual.add((resource(node["id"]), URIRef(value["p"]), obj))
    assert isomorphic(actual, expected)
    assert len(actual) == data["triples"]
    assert len(set(actual.subjects())) == len(data["nodes"])
    assert sum(data["counts"].values()) == len(data["nodes"])


def test_payload_preserves_every_rdf_triple(tmp_path):
    package(tmp_path)
    assert_roundtrip(tmp_path)


def test_pinned_release_roundtrip_when_supplied(tmp_path):
    import os

    root = os.environ.get("EPM_VIEWER_RELEASE_SOURCE")
    if not root:
        pytest.skip(
            "Set EPM_VIEWER_RELEASE_SOURCE for the private release acceptance check"
        )
    viewer.pinned_source(root)
    output = tmp_path / "index.html"
    compared = os.environ.get("EPM_VIEWER_RELEASE_COMPARE")
    viewer.build(root, output, compare=compared)
    payload = output.read_text().split('<script id="ontology-data" type="application/json">')[1].split("</script>")[0]
    assert_roundtrip(Path(compared or root), json.loads(payload))
    if compared:
        assert output.read_bytes() == (Path(compared) / "viewer/index.html").read_bytes()


@pytest.mark.parametrize("defect", ["identity", "candidate", "escape", "missing-newest"])
def test_invalid_package_cannot_be_viewed(tmp_path, defect):
    p = package(tmp_path)
    manifest = json.loads((p / "manifest.json").read_text())
    if defect == "identity":
        manifest["module"] = "other"
    elif defect == "candidate":
        manifest["release_candidate"] = True
    elif defect == "escape":
        (p.parent / "escape.ttl").write_text(TTL)
        manifest["files"] = {"../escape.ttl": hashlib.sha256(TTL.encode()).hexdigest()}
    else:
        (p.parent / "2.0.0").mkdir()
    (p / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises((ValueError, FileNotFoundError)):
        viewer.build_data(tmp_path)


def test_catalog_metadata_is_preserved_but_not_counted_as_terms(tmp_path):
    package(tmp_path, ttl=TTL + '\nx:file a <http://www.w3.org/ns/dcat#Distribution> .')
    catalog = tmp_path / viewer.ONTOLOGY / "releases/catalog.ttl"
    catalog.write_text('@prefix dcat: <http://www.w3.org/ns/dcat#> . <https://example.test/catalog> a dcat:Catalog; <http://purl.org/dc/terms/title> "Whole release catalog" .')
    data = viewer.build_data(tmp_path)
    assert data["terms"] == 5
    assert data["counts"]["Metadata"] == 2
    assert any(n["label"] == "Whole release catalog" and n["modules"] for n in data["nodes"])
    assert_roundtrip(tmp_path, data)


def test_non_semver_directories_are_not_release_inputs(tmp_path):
    package(tmp_path)
    package(tmp_path, version="2.0.0-candidate", ttl="invalid RDF")
    assert viewer.build_data(tmp_path)["terms"] == 5
