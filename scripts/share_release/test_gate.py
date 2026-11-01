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
    for value, reason in ((b"Author: Valero\0", "a peer named"), (b"Comment: skos__Concept\0", "the graph's double-underscore separator"),
                          (b"Title: PSX\0", "a peer's ticker"), (b"Keywords: #231\0", "an issue or pull request number")):
        (tmp_path / "img.png").write_bytes(b"\x89PNG\0\0" + value)  # one-value metadata, no second space
        assert [h["reason"] for h in gate.scan(str(tmp_path))] == [reason], value
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


def test_a_pdfs_compressed_streams_are_inflated_and_scanned(tmp_path):
    import zlib
    clean(tmp_path)

    def pdf(dictionary, payload):
        return b"%PDF-1.4\n1 0 obj\n<< /Length 5 " + dictionary + b" >>\nstream\n" + payload + b"\nendstream\nendobj\n%%EOF\n"
    (tmp_path / "doc.pdf").write_bytes(pdf(b"/Filter /FlateDecode", zlib.compress(b"BT (Prepared by Ada Lovelace for Valero) Tj ET")))
    assert {h["reason"] for h in gate.scan(str(tmp_path))} == {"the owner's name or handle", "a peer named"}
    assert gate.strings_of(zlib.compress(b"Ada Lovelace")).count("Ada") == 0  # the raw bytes hold no name: only inflation finds it
    (tmp_path / "doc.pdf").write_bytes(pdf(b"/Filter /FlateDecode", zlib.compress(b"BT (nothing private) Tj ET")) + b"<< /Author (Ada Lovelace) >>\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]  # metadata outside the streams
    (tmp_path / "doc.pdf").write_bytes(pdf(b"/Filter /FlateDecode", b"not zlib at all"))
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a PDF stream could not be inflated"]
    (tmp_path / "doc.pdf").write_bytes(pdf(b"/Filter /LZWDecode", b"\x80\x0b\x60\x50\x22\x0c\x0c\x85\x01"))
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a PDF stream uses a filter the gate cannot read"]
    (tmp_path / "doc.pdf").write_bytes(pdf(b"/Filter /DCTDecode /Subtype /Image", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"))
    assert gate.scan(str(tmp_path)) == []  # an image stream is not inflated and raises no problem
    (tmp_path / "doc.pdf").write_bytes(pdf(b"/Filter /DCTDecode /Subtype /Image", b"\xff\xd8\xff\xe0 jpeg comment: Ada Lovelace"))
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]  # but its printable text is still read
    (tmp_path / "doc.pdf").write_bytes(pdf(b"", b"BT (plain, under EPM-DEC-001-0001) Tj ET"))
    assert {h["reason"] for h in gate.scan(str(tmp_path))} == {"a decision record number"}  # an unfiltered stream is read as it is


def test_data_urls_in_every_valid_spelling_are_decoded_and_a_broken_one_fails(tmp_path):
    import base64
    clean(tmp_path)
    payload = base64.b64encode(b"\x89PNG\0\0Drawn by Ada Lovelace\0").decode()
    for head in ("data:image/png;base64,", "data:;base64,", "data:image/png;BASE64,", "data:text/plain;charset=utf-8;base64,", "DATA:;Base64,"):
        (tmp_path / "page.html").write_text(f'<img src="{head}{payload}">\n')
        assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"], head
    (tmp_path / "page.html").write_text('<a href="data:text/plain,Written%20by%20Ada%20Lovelace">x</a>\n')  # percent-encoded, not base64
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,AAAAAAAAAAAAAAAAA">\n')  # base64-shaped, wrong padding
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a data URI's base64 payload could not be decoded"]
    (tmp_path / "page.html").write_text('a[key].startswith("data:image/png;base64,abc") and f"data:image/png;base64,{b64}"\n')  # a fixture and a template, read as text
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "page.html").write_text('f"data:text/plain;base64,{b64}" about Ada Lovelace\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,' + base64.b64encode(b"\x89PNG\0\0" + bytes(range(256))).decode() + '">\n')
    assert gate.scan(str(tmp_path)) == []


def test_colours_are_masked_only_in_css_and_prose_issue_numbers_after_a_colon_fail(tmp_path):
    clean(tmp_path)
    (tmp_path / "page.html").write_text('<style>a{color: #455; --text: #111}</style><div style="color: #455">x</div>\n')
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "page.html").write_text("<p>Issue: #455 remains open</p>\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["an issue or pull request number"]
    (tmp_path / "page.html").unlink()
    (tmp_path / "s.css").write_text("a { color: #455 }\n")
    assert gate.scan(str(tmp_path)) == []


def test_a_python_name_exempts_only_its_own_word(tmp_path):
    clean(tmp_path)
    (tmp_path / "a.py").write_text("x = __init__ and core__Process\n")  # the allowed neighbour does not cover the graph name
    assert [h["match"] for h in gate.scan(str(tmp_path))] == ["core__P"]
    (tmp_path / "a.py").write_text("mf --group-by metric_time__day; __init__.py; __main__\n")
    assert gate.scan(str(tmp_path)) == []


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
    for text in ("Delek (DK)", "DK and MPC", "MPLX/DK", "DK, VLO", "the decision of 2026-10-05 to 0043", "amending 0021", "amends 0021", "supersedes 0021",
                 "https://www.sec.gov/Archives/edgar/data/999/000/vlo-20251231.htm", "https://www.sec.gov/Archives/edgar/data/0001035002/000162828026011499/a10k.htm",
                 "https://www.sec.gov/Archives/edgar/data/1376139/x/a.htm", "business_architecture/ontology/lpg-projection/README.md", "guideline in ../lpg-projection/ (v2.2)"):
        (tmp_path / "doc.md").write_text(text + "\n")
        assert gate.scan(str(tmp_path)) != [], text
    passes = ("the DK stays; psx in lower case; a DINOSAUR; MPC and MPLX", "https://www.sec.gov/Archives/edgar/data/1510295/mpc-20251231.htm", "https://www.sec.gov/Archives/edgar/data/0001510295/x/mpc-20251231.htm",
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


def test_the_fixture_files_may_describe_n10s_names_from_a_closed_list_and_nothing_else(tmp_path):
    clean(tmp_path)
    lpg = tmp_path / "skills" / "ontology-to-lpg" / "scripts"
    lpg.mkdir(parents=True)
    (lpg / "test_modeling.py").write_text('row("lib__Copy", "lib__barcode", "n4sch__Entity", "skos__Concept", "rdf__type")\n')  # n10s's schema names in the library fixture
    assert gate.scan(str(tmp_path)) == []
    (lpg / "load_verify.py").write_text('# always prefix__local\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the graph's double-underscore separator"]
    (lpg / "load_verify.py").unlink()
    for planted in ("vs__Stage", "core__Process", "prov__since", "owl__Class", "sh__path"):  # this ontology's prefixes and schema prefixes outside the list
        (lpg / "test_modeling.py").write_text(f'row("lib__Copy", "{planted}")\n')
        assert [h["match"] for h in gate.scan(str(tmp_path))] == [planted[:planted.index("__") + 3]], planted
    (lpg / "test_modeling.py").unlink()
    proj = tmp_path / "business_architecture" / "ontology" / "projection"
    proj.mkdir(parents=True)
    (proj / "test_pipeline.py").write_text('assert names == ["rdfs__label", "org__isA", "dcterms__issued"]\n')  # the pipeline's own rename test
    assert gate.scan(str(tmp_path)) == []
    (proj / "test_pipeline.py").write_text('assert names == ["kpi__Measure"]\n')
    assert [h["match"] for h in gate.scan(str(tmp_path))] == ["kpi__M"]
    (proj / "test_pipeline.py").unlink()
    other = tmp_path / "skills" / "ontology" / "scripts"
    other.mkdir(parents=True)
    (other / "test_docs.py").write_text('expected = "lib__Forbidden"\n')  # another skill's test is not a fixture of n10s, whatever the prefix
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the graph's double-underscore separator"]


def test_what_the_rules_leave_as_a_near_miss_fails_the_gate_on_purpose(tmp_path):
    """The rules rewrite only the short numbers the record-dates map knows and keep every other four-digit number;
    the gate still fails on a parenthesised short number or one chained to a rewritten date, so a cut stops there
    and a person decides whether the number is a record the map did not hold or a plain number. That stop is wanted."""
    import rules
    clean(tmp_path)
    for src in ("(0042) is unknown here", "see EPM-DEC-001-0044, 0999"):
        out, _ = rules.apply(src, "doc.md", {"EPM-DEC-001-0044": "2026-10-18"})
        (tmp_path / "doc.md").write_text(out + "\n")
        assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a decision record's short number"], out
    out, _ = rules.apply("Catalogue record 0042, field 700; W-0042", "doc.md", {"EPM-DEC-001-0042": "2026-10-16"})
    (tmp_path / "doc.md").write_text(out + "\n")
    assert gate.scan(str(tmp_path)) == []  # a number outside a citation's forms is left alone by both
