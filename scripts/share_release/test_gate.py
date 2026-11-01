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


def test_base64_page_data_is_not_scanned(tmp_path):
    clean(tmp_path)
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,UEJGVmFsZXJvQ1ZS\n">\n')
    assert gate.scan(str(tmp_path)) == []


def test_the_namespace_note_must_be_in_the_readme(tmp_path):
    (tmp_path / "README.md").write_text("no note\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the namespace note is missing"]


def test_colours_in_a_page_and_short_words_in_a_binary_are_not_leaks(tmp_path):
    clean(tmp_path)
    (tmp_path / "page.html").write_text("<style>a{color:#111;background:#fff} b{border:1px solid #1a2b3c}</style>\n")
    (tmp_path / "img.png").write_bytes(b"\x89PNG\r\n\x1a\n\0\0pbf cvr #123 skos__x\0\0")
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "img.png").write_bytes(b"\x89PNG\0\0EPM-DEC-001-0001\0")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a decision record number"]


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


def test_the_skills_test_fixtures_may_describe_n10s_names(tmp_path):
    clean(tmp_path)
    (tmp_path / "skills" / "ontology-to-lpg" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "ontology-to-lpg" / "scripts" / "test_modeling.py").write_text('row("lib__Copy", "lib__barcode")\n')
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "skills" / "ontology-to-lpg" / "scripts" / "load_verify.py").write_text('# always prefix__local\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the graph's double-underscore separator"]
