"""The leak gate fails on each kind of planted leak, in text, in a page's data, in an XLSX and in a path."""
import os

os.environ["EPM_RELEASE_OWNER_NAMES"] = "Ada Lovelace,Ada,adalove"  # a stand-in: no test names a person
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gate  # noqa: E402

PLANTS = {
    "the owner's name or handle": "written by Ada Lovelace",
    "this account's repositories": "see enterprise-performance-model on GitHub",
    "a decision record number": "approved under EPM-DEC-001-0044",
    "the saved answers folder": "recorded in answers-2026-10-18-night.md",
    "the old IRI base or company name": "<https://w3id.org/lsc/ontology/modules/core/>",
    "a host of the build": "runs on the exe.dev VM",
    "a path on the owner's machine": "/Users/someone/Dropbox/project",
    "a peer named": "compared with Valero and Phillips 66",
    "an issue or pull request number": "fixed in PR #231",
    "the graph's double-underscore separator": "MATCH (c:skos__Concept)",
}


def clean(tmp_path):
    (tmp_path / "README.md").write_text("The namespaces will be reviewed and approved by the Data, Analytics and Insight team.\n")


def test_a_clean_release_passes(tmp_path):
    clean(tmp_path)
    (tmp_path / "doc.md").write_text("MPC's processes; skos_Concept; mf --group-by metric_time__day; __init__.py; color #fff\n")
    assert gate.scan(str(tmp_path)) == []


def test_each_planted_leak_fails(tmp_path):
    clean(tmp_path)
    for reason, text in PLANTS.items():
        (tmp_path / "doc.md").write_text(text + "\n")
        hits = gate.scan(str(tmp_path))
        assert any(h["reason"] == reason for h in hits), (reason, hits)


def test_a_leak_in_a_workbook_and_in_a_path_fails(tmp_path):
    clean(tmp_path)
    with zipfile.ZipFile(tmp_path / "book.xlsx", "w") as z:
        z.writestr("xl/sharedStrings.xml", "<sst><si><t>EPM-DEC-001-0001</t></si></sst>")
    hits = gate.scan(str(tmp_path))
    assert any(h["reason"] == "a decision record number" and "book.xlsx" in h["file"] for h in hits)
    (tmp_path / "book.xlsx").unlink()
    (tmp_path / "downstream-peers").mkdir()
    (tmp_path / "downstream-peers" / "x.md").write_text("fine\n")
    assert gate.scan(str(tmp_path)) == []  # the folder name itself is not a leak pattern
    (tmp_path / "answers-2026-10-18.md").write_text("fine\n")
    assert any(h["reason"] == "the saved answers folder" and h.get("where") == "the path" for h in gate.scan(str(tmp_path)))


def test_base64_page_data_is_decoded_and_scanned(tmp_path):
    import base64
    clean(tmp_path)
    png = b"\x89PNG\r\n\x1a\n" + bytes(range(256)) * 4
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,' + base64.b64encode(png).decode() + '\n">\n')
    assert gate.scan(str(tmp_path)) == []
    for planted, reason in ((b"\x89PNG\0\0Written by Ada Lovelace, 2026\0", "the owner's name or handle"),
                            (b"\x89PNG\0\0see EPM-DEC-001-0001 here\0", "a decision record number"),
                            (b"\x89PNG\0\0compared with Valero and Phillips 66\0", "a peer named")):
        (tmp_path / "page.html").write_text('<img src="data:image/png;base64,' + base64.b64encode(planted).decode() + '">\n')
        assert {h["reason"] for h in gate.scan(str(tmp_path))} == {reason}, reason


def test_the_namespace_note_must_be_in_the_readme(tmp_path):
    (tmp_path / "README.md").write_text("no note\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the namespace note is missing"]


def test_colours_in_a_page_and_random_bytes_in_a_binary_are_not_leaks_but_planted_words_are(tmp_path):
    clean(tmp_path)
    (tmp_path / "page.html").write_text("<style>a{color:#111;background:#fff} b{border:1px solid #1a2b3c}</style>\n")
    (tmp_path / "img.png").write_bytes(b"\x89PNG\r\n\x1a\n" + bytes(range(256)) * 3 + b"h4i__z\0\0")  # a printable run by chance
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "img.png").write_bytes(b"\x89PNG\0\0Comment: see pbf and cvr in #123 and skos__x here\0\0")
    reasons = {h["reason"] for h in gate.scan(str(tmp_path))}
    assert reasons == {"a peer named", "an issue or pull request number", "the graph's double-underscore separator"}
    (tmp_path / "img.png").write_bytes(b"\x89PNG\0\0EPM-DEC-001-0001\0")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a decision record number"]
    (tmp_path / "img.png").unlink()
    with zipfile.ZipFile(tmp_path / "book.xlsx", "w") as z:  # an Office part that is not XML is read as a binary
        z.writestr("xl/sharedStrings.xml", "<sst/>")
        z.writestr("xl/media/image1.png", b"\x89PNG\0\0Author: Ada Lovelace, draft\0")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]


def test_the_owners_name_matches_whole_words_only(tmp_path):
    clean(tmp_path)
    (tmp_path / "doc.md").write_text("Adam adapted the metadata; ADAPT and adalovelace2 stay.\n")
    assert gate.scan(str(tmp_path)) == []
    for planted in ("by Ada.", "by Ada Lovelace", "(adalove)", "ada's note"):
        (tmp_path / "doc.md").write_text(planted + "\n")
        assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"], planted


def test_each_new_pattern_fails_and_its_near_misses_pass(tmp_path):
    clean(tmp_path)
    fails = {
        "this account's repositories": "lived in the enterprise-people-graph repository",
        "a peer's ticker": "Puts PSX, VLO and MPC in Focus",
        "a peer's filing on EDGAR": "https://www.sec.gov/Archives/edgar/data/1035002/000162828026011499/vlo-20251231.htm",
        "a decision record's short number": "(the decision of 2026-10-05, 0021)",
        "a document the release leaves out": "see `LOCAL-STORES.md` for the ports",
    }
    for reason, text in fails.items():
        (tmp_path / "doc.md").write_text(text + "\n")
        assert {h["reason"] for h in gate.scan(str(tmp_path))} == {reason}, (reason, text)
    for text in ("Delek (DK)", "the decision of 2026-10-05 to 0043", "amending 0021", "https://www.sec.gov/Archives/edgar/data/999/000/vlo-20251231.htm",
                 "business_architecture/ontology/lpg-projection/README.md", "guideline in ../lpg-projection/ (v2.2)"):
        (tmp_path / "doc.md").write_text(text + "\n")
        assert gate.scan(str(tmp_path)) != [], text
    passes = ("the DK stays; psx in lower case; a DINOSAUR", "https://www.sec.gov/Archives/edgar/data/1510295/mpc-20251231.htm",
              "https://www.sec.gov/Archives/edgar/data/67646/000119312503054119/dex991.htm", "Catalogue record 0042, field 700 (W-0042)",
              "read references/lpg-projection.md; the container lpg-projection; urn:lpg-projection:graph:", "the decision of 2026-10-05, amended on 2026-10-07")
    for text in passes:
        (tmp_path / "doc.md").write_text(text + "\n")
        assert gate.scan(str(tmp_path)) == [], text


def test_the_gate_and_the_export_refuse_to_run_without_the_owners_names(tmp_path):
    import subprocess
    rel = tmp_path / "rel"; rel.mkdir()
    clean(rel)
    env = {k: v for k, v in os.environ.items() if k != "EPM_RELEASE_OWNER_NAMES"}
    env["HOME"] = str(tmp_path / "home"); (tmp_path / "home").mkdir()
    r = subprocess.run([sys.executable, os.path.join(HERE, "gate.py"), str(rel)], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "not configured" in r.stderr
    r = subprocess.run([sys.executable, os.path.join(HERE, "export.py"), "--epm", str(rel), "--out", str(tmp_path / "out")], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "not configured" in r.stderr and not (tmp_path / "out").exists()
    (tmp_path / "home" / ".config" / "epm").mkdir(parents=True)
    (tmp_path / "home" / ".config" / "epm" / "owner-names.txt").write_text("Ada Lovelace\n")  # the file-based configuration
    r = subprocess.run([sys.executable, os.path.join(HERE, "gate.py"), str(rel)], env=env, capture_output=True, text=True)
    assert r.returncode == 0 and "no leaks" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, os.path.join(HERE, "export.py"), "--epm", str(rel), "--out", str(tmp_path / "out")], env=env, capture_output=True, text=True)
    assert r.returncode == 0 and (tmp_path / "out-report.json").exists(), r.stdout + r.stderr  # an empty tree ships nothing, but the export ran


def test_an_office_file_is_rewritten_by_the_export(tmp_path):
    import zipfile
    import export
    epm = tmp_path / "epm"
    (epm / "business_architecture" / "reference").mkdir(parents=True)
    with zipfile.ZipFile(epm / "business_architecture" / "reference" / "book.xlsx", "w") as z:
        z.writestr("xl/sharedStrings.xml", "<sst><si><t>LSC Core (EPM-DEC-001-0001)</t></si></sst>")
        z.writestr("xl/media/image1.png", b"\x89PNG\0\0")
    out = tmp_path / "rel"
    export.export(str(epm), "", str(out))
    with zipfile.ZipFile(out / "business_architecture" / "reference" / "book.xlsx") as z:
        assert z.read("xl/sharedStrings.xml") == b"<sst><si><t>MPC Core (the decision of an earlier date)</t></si></sst>"
        assert z.read("xl/media/image1.png") == b"\x89PNG\0\0"


def test_a_databricks_workspace_path_is_not_the_owners_machine(tmp_path):
    clean(tmp_path)
    (tmp_path / "a.py").write_text('folder = f"/Workspace/Users/{name}/pricing-demo"\n')
    assert gate.scan(str(tmp_path)) == []


def test_the_lpg_skills_test_fixtures_may_describe_n10s_names_but_nothing_else_may(tmp_path):
    clean(tmp_path)
    lpg = tmp_path / "skills" / "ontology-to-lpg" / "scripts"
    lpg.mkdir(parents=True)
    (lpg / "test_modeling.py").write_text('row("lib__Copy", "lib__barcode", "n4sch__Entity")\n')
    assert gate.scan(str(tmp_path)) == []
    (lpg / "load_verify.py").write_text('# always prefix__local\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the graph's double-underscore separator"]
    (lpg / "load_verify.py").unlink()
    (lpg / "test_modeling.py").write_text('row("lib__Copy", "vs__Stage")\n')  # a prefix of this ontology's graph, even in a fixture
    assert [h["match"] for h in gate.scan(str(tmp_path))] == ["vs__S"]
    (lpg / "test_modeling.py").unlink()
    other = tmp_path / "skills" / "ontology" / "scripts"
    other.mkdir(parents=True)
    (other / "test_docs.py").write_text('expected = "core__Forbidden"\n')  # another skill's test is not a fixture of n10s
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the graph's double-underscore separator"]


def test_the_pipelines_own_tests_may_name_n10s_fixtures_but_not_the_ontologys_prefixes(tmp_path):
    clean(tmp_path)
    rel = tmp_path / "business_architecture/ontology/projection/test_pipeline.py"
    rel.parent.mkdir(parents=True)
    rel.write_text('assert lpg_name(x, sep="__") == "rdfs__label"; nodes = [{"l": ["lib__Thing"]}]\n')
    assert [h for h in gate.scan(str(tmp_path)) if "double-underscore" in h["reason"]] == []
    rel.write_text('nodes = [{"l": ["kpi__MeasureDefinition"]}]\n')
    assert any("double-underscore" in h["reason"] for h in gate.scan(str(tmp_path)))
    other = tmp_path / "business_architecture/ontology/projection/test_sync_stores.py"
    other.write_text('x = "rdfs__label"\n')
    assert any("double-underscore" in h["reason"] and "test_sync_stores" in h["file"] for h in gate.scan(str(tmp_path)))
