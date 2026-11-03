"""The leak gate fails on each kind of planted leak, in text, in a page's data, in an XLSX and in a path."""
import pytest
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
    "a skill the release leaves out": "follow the `way-of-working` skill",
    "something kept out of the repository": "The customer files themselves stay out of the repository.",
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


def test_short_and_wrapped_base64_payloads_are_decoded(tmp_path):
    import base64
    clean(tmp_path)
    (tmp_path / "page.html").write_text('<img alt="data:image/png;base64,Q1ZS">\n')  # "CVR" in four characters
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    wrapped = base64.b64encode(b"\x89PNG\0\0Drawn by Ada Lovelace\0").decode()
    wrapped = wrapped[:12] + "\n" + wrapped[12:24] + "\r\n" + wrapped[24:]
    (tmp_path / "page.html").write_text(f'<img src="data:image/png;base64,{wrapped}">\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,QUJD"> and Valero\n')  # "ABC"; the payload ends at the quote and the text after it is scanned as text
    assert {h["reason"] for h in gate.scan(str(tmp_path))} == {"a peer named"}
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,QWRhIExvdmVsYWNl">\n')  # unpadded: forgiving-base64 decode accepts it (WHATWG Infra Standard, Living Standard as of 19 October 2026, read 2026-11-01)
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]


def test_pdf_streams_with_long_dictionaries_cr_endings_and_a_size_cap(tmp_path, monkeypatch):
    import zlib
    clean(tmp_path)
    payload = zlib.compress(b"BT (Prepared by Ada Lovelace) Tj ET")
    long_dict = b"<< /Length 5 /Junk (" + b"x" * 900 + b") /Filter /FlateDecode >>"
    (tmp_path / "doc.pdf").write_bytes(b"%PDF-1.4\n1 0 obj\n" + long_dict + b"\nstream\n" + payload + b"\nendstream\nendobj\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]  # the whole dictionary is read
    (tmp_path / "doc.pdf").write_bytes(b"%PDF-1.4\r1 0 obj\r<< /Length 5 /Filter /FlateDecode >>\rstream\r" + payload + b"\rendstream\rendobj\r")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]  # CR-only line ends
    (tmp_path / "doc.pdf").write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Filter /FlateDecode >>\nstream\n" + zlib.compress(b"\0" * 200000) + b"\nendstream\n")
    monkeypatch.setattr(gate, "INFLATE_CAP", 10000)
    hits = gate.scan(str(tmp_path))
    assert [h["reason"] for h in hits] == ["a PDF stream could not be inflated"] and "past 10000" in hits[0]["match"]
    (tmp_path / "doc.pdf").unlink()
    with zipfile.ZipFile(tmp_path / "book.xlsx", "w") as z:
        z.writestr("xl/sharedStrings.xml", "<sst/>" + " " * 20000)
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["an Office part inflates past the cap"]


def test_a_graph_name_is_not_excused_by_a_python_name_inside_the_same_word(tmp_path):
    clean(tmp_path)
    (tmp_path / "a.py").write_text("x = core__Process__init__\n")
    assert [h["match"] for h in gate.scan(str(tmp_path))] == ["core__P"]
    (tmp_path / "a.py").write_text("metric_time__day __init__.py __main__\n")
    assert gate.scan(str(tmp_path)) == []


def test_a_base64_payload_hides_nothing_after_a_space_or_percent_encoding(tmp_path):
    clean(tmp_path)
    chevron = "Q2hldnJvbg=="  # "Chevron"
    for spelt in (chevron[:4] + " " + chevron[4:], chevron[:4] + "%64" + chevron[5:], chevron[:3] + "%20" + chevron[3:], chevron[:6] + "\n   " + chevron[6:]):
        (tmp_path / "page.html").write_text(f'<img src="data:image/png;base64,{spelt}">\n')
        assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"], spelt
        (tmp_path / "page.md").write_text(f"![x](data:image/png;base64,{spelt}) text\n")  # a Markdown link: the payload ends at ")"
        (tmp_path / "page.html").unlink()
        assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"], spelt
        (tmp_path / "page.md").unlink()
    (tmp_path / "page.html").write_text(f'<img src="data:image/png;base64,{chevron}" alt="Exxon">\n')  # the payload ends at its quote; the alt is prose
    assert sorted(h["reason"] for h in gate.scan(str(tmp_path))) == ["a peer named", "a peer named"]


def test_a_base64_payload_ends_at_a_fragment_or_a_markdown_title_and_is_still_decoded(tmp_path):
    clean(tmp_path)
    chevron = "Q2hldnJvbg=="  # "Chevron"
    (tmp_path / "page.md").write_text(f'![x](data:image/png;base64,{chevron} "a title")\n')  # the title is not the payload
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    (tmp_path / "page.md").write_text(f"see data:image/png;base64,{chevron}#fragment here\n")  # a fragment is not the payload
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    (tmp_path / "page.md").write_text(f'<a href="data:image/png;base64,{chevron}#x">x</a>\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    (tmp_path / "page.md").write_text(f'![x](data:image/png;base64,{chevron} "Exxon")\n')  # and the title is scanned as prose
    assert sorted(h["reason"] for h in gate.scan(str(tmp_path))) == ["a peer named", "a peer named"]


def test_html_character_references_nested_payloads_and_nul_delimited_names_are_found(tmp_path):
    import base64
    clean(tmp_path)
    inner = base64.b64encode(b"<p>compared with Chevron</p>").decode()
    (tmp_path / "page.html").write_text(f'<iframe src="data:text/html;base64&#44;{inner}"></iframe>\n')  # &#44; is the comma
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    (tmp_path / "page.html").write_text(f'<iframe src="data&#58;text/html;base64,{inner}"></iframe>\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    outer = base64.b64encode(f'<iframe src="data:text/html;base64,{inner}"></iframe>'.encode()).decode()  # a data URL inside a data URL
    (tmp_path / "page.html").write_text(f'<iframe src="data:text/html;base64,{outer}"></iframe>\n')
    hits = gate.scan(str(tmp_path))
    assert [h["reason"] for h in hits] == ["a peer named"] and "data URI 1 > data URI 1" in hits[0]["where"]
    layer = inner
    for _ in range(gate.DATA_URL_DEPTH + 2):  # deeper than the cap: the gate stops at the cap and does not loop
        layer = base64.b64encode(f'<iframe src="data:text/html;base64,{layer}"></iframe>'.encode()).decode()
    (tmp_path / "page.html").write_text(f'<iframe src="data:text/html;base64,{layer}"></iframe>\n')
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "page.html").write_text('<img src="data:image/png;base64,' + base64.b64encode(b"\0\0CVR\0\0").decode() + '">\n')  # NUL-delimited, shorter than a binary's run
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    assert gate.readable(b"\0\0CVR\0\0") == "CVR" and gate.readable(b"plain text with Valero in it") == "plain text with Valero in it"
    assert "CVI" not in gate.readable(b"\xff\xd8\xff\xe0\x10CVI\x12\x9a")  # three letters between arbitrary bytes are an image's chance, not a string


def test_entity_encoded_text_inside_a_decoded_payload_is_scanned_at_every_depth(tmp_path):
    import base64
    clean(tmp_path)
    inner = base64.b64encode(b"<p>compared with &#67;hevron</p>").decode()  # "C" as a numeric character reference
    (tmp_path / "page.html").write_text(f'<iframe src="data:text/html;base64,{inner}"></iframe>\n')
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    (tmp_path / "page.html").write_text('<iframe src="data:text/html,%3Cp%3Eby%20&#65;da%20Lovelace%3C/p%3E"></iframe>\n')  # percent-encoded payload, entity inside
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the owner's name or handle"]
    outer = base64.b64encode(f'<iframe src="data:text/html;base64,{inner}"></iframe>'.encode()).decode()
    (tmp_path / "page.html").write_text(f'<iframe src="data:text/html;base64,{outer}"></iframe>\n')  # two layers down
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]


def test_a_percent_encoded_entity_in_a_non_base64_payload_is_decoded_at_every_depth(tmp_path):
    import base64
    clean(tmp_path)
    (tmp_path / "page.html").write_text('<iframe src="data:text/html;base64,%26%2367%3Bhevron"></iframe>\n')  # not base64-shaped: percent-decodes to &#67;hevron
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    outer = base64.b64encode(b'<iframe src="data:text/html;base64,%26%2367%3Bhevron"></iframe>').decode()
    (tmp_path / "page.html").write_text(f'<iframe src="data:text/html;base64,{outer}"></iframe>\n')  # the same, nested
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]
    (tmp_path / "page.html").write_text('<a href="data:text/html,%26%2367%3Bhevron">x</a>\n')  # the plain data URL form too
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a peer named"]


@pytest.mark.parametrize("name,planted", [
    ("claude", "Drafted by Claude."), ("claude.ai", "see claude.ai"), ("CLAUDE.md", "Read CLAUDE.md"), ("codex", "Codex said"),
    ("bugbot", "Bugbot found it"), ("kimi", "Kimi round 1"), ("anthropic", "from Anthropic"), ("chatgpt", "ChatGPT wrote"),
    ("herdr", "a herdr pane"), ("openai", "OpenAI key"), ("gpt", "gpt-6-luna"), ("rex-review", "rex-review.sh"), ("pi-review", "pi-review.sh"),
    ("agents.md", "see AGENTS.md"), ("cursor", "the Cursor bot"), ("cursor folder", "app/cursor merged"),
    ("independent review", "the independent reviewer"), ("review round", "review round 2"), ("finding", "(finding 11)"),
    ("verdict", "the PR verdict"), ("delegation", "Approved under the delegation"), ("delegated under", "delegated under a record"),
    ("delegate", "Yes, delegate as described"), ("first name", "Kailey said"), ("pull request", "ship in one pull request"), ("pr", "the batch 08 PR"),
])
def test_an_agent_name_or_agent_work_fails(tmp_path, name, planted):
    f = tmp_path / "notes.md"
    f.write_text(planted + "\n")
    assert any(h["file"] == "notes.md" and h["reason"] != "the namespace note is missing" for h in gate.scan(str(tmp_path))), name


@pytest.mark.parametrize("fname,kept", [
    ("db.py", "cur = conn.cursor()\n"), ("db.py", "class Cursor:\n    pass\nc = Cursor(1)\n"), ("page.css", "td { cursor: pointer; }\n"),
    ("a.md", "the delegation of authority\n"), ("a.md", "public relations (PR) strategy\n"), ("a.md", "prov:SoftwareAgent and Genie agents\n"),
    ("a.md", "`evidence.md`, finding 3\n"),
])
def test_what_is_not_the_build_passes(tmp_path, fname, kept):
    (tmp_path / fname).write_text(kept)
    assert [h for h in gate.scan(str(tmp_path)) if h["file"] == fname] == []


def test_a_name_in_an_office_part_fails(tmp_path):
    import zipfile
    with zipfile.ZipFile(tmp_path / "book.xlsx", "w") as z:
        z.writestr("xl/sharedStrings.xml", "<t>Drafted by Claude</t>")
    assert any(h["reason"] == "an agent or review tool named" for h in gate.scan(str(tmp_path)))


def test_an_agent_in_a_path_fails(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("x\n")
    assert any(h["reason"] == "an agent or review tool named" and h.get("where") == "the path" for h in gate.scan(str(tmp_path)))


def test_the_skills_may_teach_pull_requests_and_delegation(tmp_path):
    folder = tmp_path / "skills" / "ontology"
    folder.mkdir(parents=True)
    (folder / "guide.md").write_text("Through a pull request. Decided (delegated under <record>).\n")
    assert [h for h in gate.scan(str(tmp_path)) if h["file"].startswith("skills/")] == []


def test_a_left_out_document_fails(tmp_path):
    (tmp_path / "a.md").write_text("see step4/playbook/ontology-worklog.md and pr-reviews-262-266-269.md\n")
    assert any(h["reason"] == "a document the release leaves out" for h in gate.scan(str(tmp_path)))


def test_the_agent_fails_only_in_a_decision_package(tmp_path):
    clean(tmp_path)
    (tmp_path / "other.md").write_text("the agent's filters name the price\n")
    assert gate.scan(str(tmp_path)) == []
    folder = tmp_path / "business_architecture" / "domain" / "decision-packages"
    folder.mkdir(parents=True)
    (folder / "x.md").write_text("You ask the agent to draft it.\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["the agent, in a decision package"]


@pytest.mark.parametrize("text", ["def test_bugbot_380_x(): pass", "each_edge_codex_found", "built_by_Ada_Lovelace_here", "pbf_margin",
                                  "Phillips-66-Market-Indicators.pdf", "a U.S. refining peer, Phillips", "test_pi_review.py",
                                  "scripts/test_rex_review.py", "gpt_4_eval", "cursor_agent_380", "kailey_plan"])
def test_a_name_joined_by_an_underscore_or_a_hyphen_fails(tmp_path, text):
    clean(tmp_path)
    (tmp_path / "doc.md").write_text(text + "\n")
    assert gate.scan(str(tmp_path))


MARKET_NEWS = ("demos/downstream-pricing-databricks-free/data/parallel/monthly-west-coast-2024-02.json",
               "demos/downstream-pricing-databricks-free/SCENARIO.md")
PEER_LINE = "Valero and Chevron cut runs; PSX, VLO and MPC in Focus; https://www.sec.gov/Archives/edgar/data/1035002/000162828026011499/vlo-20251231.htm\n"


def plant(tmp_path, rel, text):
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_a_peer_in_market_news_passes(tmp_path):
    # EPM-DEC-001-0112, point 7: peer names, tickers and filings in the cached Parallel search results and in
    # SCENARIO.md stay in the release.
    clean(tmp_path)
    for rel in MARKET_NEWS:
        plant(tmp_path, rel, PEER_LINE)
    assert gate.scan(str(tmp_path)) == []


def test_a_peer_outside_market_news_still_fails(tmp_path):
    # A planted leak: the same line in an ontology module, another demo file, a look-alike path or a page of the
    # parallel folder that is not a cached result fails on each peer check.
    for rel in ("business_architecture/ontology/modules/kpi/kpi.ttl", "demos/downstream-pricing-databricks-free/README.md",
                "demos/downstream-pricing-databricks-free/data/acceptance/run-1.json",
                "demos/downstream-pricing-databricks-free/data/parallel/notes.md",
                "demos/other/SCENARIO.md", "x/demos/downstream-pricing-databricks-free/SCENARIO.md"):
        clean(tmp_path)
        path = plant(tmp_path, rel, PEER_LINE)
        reasons = {h["reason"] for h in gate.scan(str(tmp_path))}
        assert reasons == {"a peer named", "a peer's ticker", "a peer's filing on EDGAR"}, rel
        path.unlink()


def test_market_news_still_fails_on_every_other_check(tmp_path):
    # Only the peer checks skip market news: an owner's name, a host or an issue number there still fails.
    for rel in MARKET_NEWS:
        clean(tmp_path)
        path = plant(tmp_path, rel, PEER_LINE + "written by Ada Lovelace on the exe.dev VM, fixed in issue #231\n")
        reasons = {h["reason"] for h in gate.scan(str(tmp_path))}
        assert reasons == {"the owner's name or handle", "a host of the build", "an issue or pull request number"}, (rel, reasons)
        path.unlink()


def test_a_market_news_file_named_for_a_peer_still_fails(tmp_path):
    # Only the text scan skips market news: a cached result whose file name names a peer still fails on the path.
    clean(tmp_path)
    path = plant(tmp_path, "demos/downstream-pricing-databricks-free/data/parallel/valero.json", "{}\n")
    hits = gate.scan(str(tmp_path))
    assert [(h["reason"], h.get("where")) for h in hits if h["reason"] == "a peer named"], hits
    path.unlink()


def test_an_issue_number_in_an_answer_iri_fails_and_the_comment_alone_passes(tmp_path):
    clean(tmp_path)
    (tmp_path / "seq.csv").write_text("REL-00008,urn:epm:issue:205:comment:6116668059\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["an issue or pull request number"]
    (tmp_path / "seq.csv").write_text("REL-00008,urn:epm:comment:6116668059\n")
    assert gate.scan(str(tmp_path)) == []


def test_a_shipped_skill_naming_a_left_out_skill_fails(tmp_path):
    clean(tmp_path)
    plant(tmp_path, "skills/ontology/references/governance.md", "Where the `way-of-working` skill is installed, follow it.\n")
    assert [h["reason"] for h in gate.scan(str(tmp_path))] == ["a skill the release leaves out"]


def test_the_gate_skips_what_the_zip_skips_and_scans_the_rest(tmp_path):
    # A run's out/ folder (the demo's replica, written by the store rows) never ships, so its copies of market news
    # are not leaks; the same text in a shipped folder is.
    import publish
    assert set(gate.SKIP_DIRS) == set(publish.SKIP_DIRS)
    clean(tmp_path)
    (tmp_path / "demos" / "d" / "out" / "replica").mkdir(parents=True)
    (tmp_path / "demos" / "d" / "out" / "replica" / "citation.txt").write_text("Valero raised runs\n")
    assert gate.scan(str(tmp_path)) == []
    (tmp_path / "demos" / "d" / "notes.txt").write_text("Valero raised runs\n")
    assert any(h["reason"] == "a peer named" for h in gate.scan(str(tmp_path)))


# Each withholding wording the build used, and variants a later document might use.
KEPT_OUT_PLANTS = [
    "The customer files themselves stay out of the repository.",
    "the subject matter expert's customer inputs (seven files, kept out of the repository by the decision of 2026-10-21)",
    "shared on 2026-10-25 and held outside the repository (the decision of 2026-10-25)",
    "as the subject matter expert sent it on 2026-10-18, which stays outside the repository (the decision of 2026-10-18)",
    "the decision owner's customer data is not in the\n  repository (the decision of 2026-10-21)",
    "The decision owner's model and other inputs are not in this repository.",
    "the customer logical model, is kept out of `main` and joins the release",
    "The customer model never enters `main`.",
    "Its export lives in the gitignored folder `release-cut/augment/logical-model/`.",
    "<h3>A confidential export stays outside the repository</h3>",
    "## One module from outside these sources",
    "Their files were kept apart from those sources and added when this release was cut.",
    "every check passed; the reload's log is kept outside the repository.",
    "The planning workbook stays outside the repo.",
    "Tools and working files this run used that do not live in either repository.",
]


@pytest.mark.parametrize("text", KEPT_OUT_PLANTS)
def test_a_statement_that_the_build_kept_something_out_of_the_repository_fails(tmp_path, text):
    clean(tmp_path)
    (tmp_path / "doc.md").write_text(text + "\n")
    hits = gate.scan(str(tmp_path))
    assert hits and {h["reason"] for h in hits} == {"something kept out of the repository"}, hits


# The option wording (an input read from outside the repository, and the two ways to work with it) and generic text,
# copied from the release's templates, main's pages and the skills: none says the build kept something out.
GENERIC_TEXT = {
    "skills/ontology/references/release.md": "## Inputs kept outside Git\n\nSome releases read files that may never enter the repository, such as an export a client keeps private, read through a release option from a folder git ignores (`logical-model.md`, rule 12). That content, and anything built from it, never enters the main branch.\n",
    "skills/ontology-to-lpg/references/multi-store.md": "### Files a release reads from outside Git\n\nA file kept outside Git, such as an export a client keeps private, has no store marker.\n",
    "skills/ontology/references/governance.md": "24. **Keep customer inputs (files, images, transcripts) out of the repository.** Store them outside it and refer to them neutrally.\n",
    "skills/ontology/references/logical-model.md": "12. **Where the export is confidential, keep it outside the repository and let the release build read it from a folder git ignores** (an augment folder). A confidential export stays outside the repository with its hash in the release's input record.\n",
    "skills/ontology-to-lpg/references/running.md": "Keep `loadable.nt`, `merged.ttl` and the downloads out of the repository; they are rebuilt from the Turtle files.\n",
    "skills/rdf-store/SKILL.md": "Store credentials live in an env file outside the repository; the script reads them.\n",
    "HOW-TO-UPDATE.md": (
        "## Inputs from outside the repository\n\nA build can read an input from a folder outside the repository instead of from your copy.\n\n"
        "This release's logical models were built that way. When the release was made, the build read each model's ER Studio export and links file from a folder outside the repository, `release-cut/augment/logical-model/`, and copied them into `$ONT/logical-model/models/`.\n"
        "- **Keep the files outside the repository.** Save the export and the links file in a folder of your own, outside your copy.\n"
        "- **Move the files into the repository.** Save them in `$ONT/logical-model/models/`.\n"),
    "business_architecture/ontology/epm-ontology-guide.html": (
        "<p>Three kinds of copy can fall behind Git: the ontology's triples, the graphs loaded beside them, and the files a release reads from outside Git.</p>\n"
        "<h3>A confidential export, read from outside the repository</h3>\n<p>A model the decision owner wants only in the release never enters <code>main</code>. Its export and links file sit in <code>release-cut/augment/logical-model/</code>, a folder Git ignores.</p>\n"
        "<h3>Files read from outside Git</h3>\n<p>A logical model that only the release may hold has its export and links file in the augment folder, <code>release-cut/augment/logical-model/</code>, which Git ignores, so neither ever enters <code>main</code>.</p>\n"
        "<li>Keep the cleaned file beside the original, outside the repository, and record each change.</li>\n"),
    "business_architecture/ontology/release/build_module.py": "# Added by the share release's cut from files read from outside the repository; \"augment\": the files from outside the repository the package was built from\n",
    "business_architecture/ontology/projection/skill-run/README.md": "Outputs go to `~/lpg-out/`, outside the repository. Copy it outside the repository; it must be outside the repository.\n",
    "demos/downstream-pricing-databricks-free/README.md": "`build` writes `out/tech/graph/`, which Git ignores. The demo's .env (gitignored) is not in git. Records stay out of the ontology.\n",
}


def test_the_option_wording_and_generic_text_pass(tmp_path):
    clean(tmp_path)
    for rel, text in GENERIC_TEXT.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    assert gate.scan(str(tmp_path)) == []
    for text in ("The customer files themselves stay out of the repository.", "The customer model's export lives in the augment folder."):
        (tmp_path / "skills/ontology/references/release.md").write_text(text + "\n")
        hits = gate.scan(str(tmp_path))
        assert hits and {h["reason"] for h in hits} == {"something kept out of the repository"}, (text, hits)
