"""The generated HTML pages match a fresh build of their Markdown, every link on them resolves, and the
renderer handles what the documents use.

Run: uv run --with pytest python -m pytest -q scripts/test_docs_html.py
"""
import html
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_docs_html as b  # noqa: E402

PAGES = b.build_all()


@pytest.mark.parametrize("out", sorted(PAGES))
def test_every_committed_page_matches_a_fresh_build(out):
    with open(os.path.join(b.ROOT, out), encoding="utf-8") as f:
        assert f.read() == PAGES[out], f"{out} is stale: run python3 scripts/build_docs_html.py"


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
