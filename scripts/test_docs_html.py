"""The generated HTML pages match a fresh build of their Markdown, the --check command says so, every link
on them resolves, they load nothing from the network, and the renderer handles what the documents use and
refuses what it does not.

Run: uv run --with pytest python -m pytest -q scripts/test_docs_html.py
"""
import html
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_docs_html as b  # noqa: E402

PAGES = b.build_all()


@pytest.mark.parametrize("out", sorted(PAGES))
def test_every_committed_page_matches_a_fresh_build(out):
    with open(os.path.join(b.ROOT, out), encoding="utf-8") as f:
        assert f.read() == PAGES[out], f"{out} is stale: run python3 scripts/build_docs_html.py"


def test_the_check_command_passes_on_the_committed_pages():
    r = subprocess.run([sys.executable, os.path.join(b.ROOT, "scripts", "build_docs_html.py"), "--check"],
                       cwd=b.ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_check_command_fails_on_a_stale_or_missing_page(monkeypatch, capsys):
    out = sorted(PAGES)[0]
    monkeypatch.setattr(b, "build_all", lambda: {out: PAGES[out] + "<!-- changed -->"})
    assert b.main(["--check"]) == 1
    assert f"FAIL {out} differs" in capsys.readouterr().out
    monkeypatch.setattr(b, "build_all", lambda: {"business_architecture/no-such-page.html": "x"})
    assert b.main(["--check"]) == 1


# A page loads a resource when a tag other than <a> names a URL, or its CSS does; a data: URI is embedded.
LOADS = re.compile(r"<(?!a\b)[a-z]+\b[^>]*\b(?:src|href|srcset|poster|data)\s*=\s*\"(?!data:|#)([^\"]+)\"", re.I)
CSS_LOADS = re.compile(r"@import|url\(\s*['\"]?(?!data:)", re.I)


@pytest.mark.parametrize("out", sorted(PAGES))
def test_a_page_loads_nothing_from_the_network_or_another_file(out):
    page = PAGES[out]
    assert LOADS.findall(page) == [], out
    styles = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", page, re.S))
    assert not CSS_LOADS.search(styles), out
    assert "<iframe" not in page and "<img" not in page, out


def test_unsupported_markdown_stops_the_build_with_its_line():
    lines = ["Title", "=====", "", "![a picture](x.png)", "<div>raw</div>", "+ item", "1) item", "[ref]: https://x.test/",
             "```", "<kept> in code ![x](y)", "```", "`<kept>` in a code span"]
    problems = b.unsupported("doc.md", lines)
    assert problems == ["doc.md:2: a Setext heading (use # headings)",
                        "doc.md:4: an image (embed pictures in the page instead)",
                        "doc.md:5: inline HTML (the page would show it as text)",
                        "doc.md:6: a list item marked with +",
                        "doc.md:7: a list item numbered with a parenthesis",
                        "doc.md:8: a reference-style link definition"]


def test_a_thematic_break_and_a_table_rule_are_not_setext_headings():
    assert b.unsupported("doc.md", ["Text.", "", "---", "", "| A |", "|---|", "- item", "---"]) == []


@pytest.mark.parametrize("spec", b.pages(), ids=lambda s: s["out"])
def test_a_page_shows_its_source_h1_word_for_word(spec):
    # An independent reading of the H1: the first "# " line of the source (the decisions page: its README).
    src = spec.get("intro", spec["sources"][0])
    with open(os.path.join(b.ROOT, src), encoding="utf-8") as f:
        h1 = next(line[2:].strip() for line in f if line.startswith("# "))
    shown = re.search(r"<h1>(.*?)</h1>", PAGES[spec["out"]], re.S).group(1)
    assert html.unescape(re.sub(r"<[^>]+>", "", shown)) == h1.replace("`", "")


def _shown_lines(path):
    """A record's lines outside fenced code, read independently of the builder."""
    out, fenced = [], False
    with open(path, encoding="utf-8") as f:
        for line in f.read().split("\n"):
            if line.lstrip().startswith("```"):
                fenced = not fenced
            elif not fenced:
                out.append(line)
    return out


def _text(cell):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", cell))).strip()


def test_every_index_row_shows_its_record_title_full_status_and_date():
    page = PAGES[b.DECISIONS_PAGE]
    rows = dict(re.findall(r'<tr><td class="num"><a href="#(EPM-DEC-001-\d{4})">\d{4}</a></td>(.*?)</tr>', page))
    folder = os.path.join(b.ROOT, b.DECISIONS_DIR)
    records = sorted(f for f in os.listdir(folder) if b.DEC_FILE.search(f))
    assert len(rows) == len(records)
    for f in records:
        lines = _shown_lines(os.path.join(folder, f))
        h1 = next(x[2:] for x in lines if x.startswith("# ")).split(":", 1)[1].strip()
        status = next(re.match(r"^\|\s*Status\s*\|(.*)\|\s*$", x).group(1) for x in lines if x.startswith("| Status |"))
        date = next(re.match(r"^\|\s*Date\s*\|(.*)\|\s*$", x).group(1) for x in lines if x.startswith("| Date |"))
        cells = [_text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", rows[b.record_id(f)], re.S)]
        # The displayed text: the Markdown without its code and emphasis marks.
        expect = [re.sub(r"\s+", " ", re.sub(r"[`*]|~~", "", v)).strip() for v in (h1, status, date)]
        assert cells == expect, f


def test_a_fenced_example_cannot_stand_in_for_a_record():
    lines = ["# EPM-DEC-001-9999: The real title", "", "```", "# EPM-DEC-001-9999: An example",
             "| Status | Proposed |", "| Date | 1900-01-01 |", "```", "", "| Field | Value |", "|---|---|",
             "| Status | Decided |", "| Date | 2026-10-26 |"]
    assert b.record_meta("x.md", lines) == ("EPM-DEC-001-9999: The real title", "Decided", "2026-10-26")
    with pytest.raises(ValueError, match="2 Status rows"):
        b.record_meta("x.md", lines + ["| Status | Proposed |"])


def test_a_shell_comment_in_a_fence_is_not_taken_for_the_title():
    lines = ["```sh", "# a comment", "```", "# Title", "text"]
    assert b.drop_title(lines) == ["```sh", "# a comment", "```", "text"]


def test_every_source_exists():
    for spec in b.pages():
        for src in spec["sources"] + ([spec["intro"]] if "intro" in spec else []):
            assert os.path.isfile(os.path.join(b.ROOT, src)), src


def test_every_decision_record_has_its_anchor_and_index_row():
    page = PAGES[b.DECISIONS_PAGE]
    records = [f for f in os.listdir(os.path.join(b.ROOT, b.DECISIONS_DIR)) if b.DEC_FILE.search(f)]
    assert records
    for f in records:
        rid = b.record_id(f)
        assert f'<section class="rec" id="{rid}">' in page, rid
        assert f'<td class="num"><a href="#{rid}">{rid[-4:]}</a></td>' in page, rid


def test_every_link_on_every_page_resolves():
    """A relative link names a file that exists, and an anchor on a generated page exists there. The
    ontology guide is the one target allowed to be absent: it lands in its own pull request."""
    ids = {os.path.normpath(os.path.join(b.ROOT, out)): set(re.findall(r'id="([^"]+)"', page))
           for out, page in PAGES.items()}
    problems = []
    for out, page in PAGES.items():
        here = os.path.normpath(os.path.join(b.ROOT, out))
        for href in re.findall(r'href="([^"]+)"', page):
            href = html.unescape(href)
            if re.match(r"^[a-z]+:", href):
                continue
            path, _, frag = href.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(here), path)) if path else here
            if path.endswith(os.path.basename(b.GUIDE)):
                continue
            if not os.path.exists(target):
                problems.append(f"{out}: {href}: no such file")
            elif frag and frag != "top" and target in ids and frag not in ids[target]:
                problems.append(f"{out}: {href}: no such anchor")
    assert not problems, "\n".join(problems[:20])


def page(spec_out="business_architecture/ontology/README.html"):
    specs = b.pages()
    spec = next(s for s in specs if s["out"] == spec_out)
    return b.Page(spec, b.generated_map(specs))


SRC = os.path.normpath(os.path.join(b.ROOT, "business_architecture/ontology/README.md"))


def test_a_link_to_a_generated_document_goes_to_its_page():
    assert 'href="MODULES.html"' in page().inline(SRC, "[guide](MODULES.md)")
    assert 'href="kpi/README.html#releases"' in page().inline(SRC, "[kpi](kpi/README.md#releases)")


def test_a_link_to_a_decision_record_goes_to_its_anchor():
    out = page().inline(SRC, "[0099](../domain/decisions/EPM-DEC-001-0099-item-g.md)")
    assert 'href="../domain/decisions/decisions.html#EPM-DEC-001-0099"' in out


def test_a_decision_id_in_text_becomes_a_link_but_not_inside_code_or_a_link():
    p = page()
    assert '<a href="../domain/decisions/decisions.html#EPM-DEC-001-0040">EPM-DEC-001-0040</a>' in \
        p.inline(SRC, "see EPM-DEC-001-0040.")
    assert p.inline(SRC, "`EPM-DEC-001-0040`") == "<code>EPM-DEC-001-0040</code>"
    assert p.inline(SRC, "[EPM-DEC-001-0040](https://x.test/)").count("<a ") == 1


def test_a_link_to_another_file_stays_relative():
    assert 'href="releases/catalog.ttl"' in page().inline(SRC, "[catalog](releases/catalog.ttl)")


def test_a_comment_is_dropped_and_a_block_quote_kept():
    out = page().blocks(SRC, ["<!-- module: core -->", "> quoted", "> lines"])
    assert "module: core" not in out
    assert out == "<blockquote><p>quoted lines</p></blockquote>"


def test_an_escaped_pipe_stays_in_its_cell_and_strikethrough_renders():
    out = page().table(SRC, ["| A | B |", "|---|---|", r"| split on `\|` | ~~old~~ new |"])
    assert "<td>split on <code>|</code></td>" in out
    assert "<del>old</del> new" in out
