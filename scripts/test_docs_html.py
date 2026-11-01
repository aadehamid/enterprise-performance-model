"""The generated HTML pages match a fresh build of their Markdown, the --check command says so, every link
on them resolves, they load nothing from the network, and the renderer handles what the documents use and
refuses what it does not.

Run: uv run --with pytest python -m pytest -q scripts/test_docs_html.py
"""
import html
import html.parser as html_parser
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


# The network checks, the visible-text reader and the credential scan come from personal-agent-skills'
# scripts/test_playbook_html.py (round 2 of its review), so both builders' pages are held to one standard.
REMOTE_CSS = re.compile(r"url\s*\(|@import", re.I)
REMOTE_JS = re.compile(r"\bfetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|\bimport\s*\(|importScripts"
                       r"|new\s+(?:Image|Worker|SharedWorker)\b|\.src\s*=|\.href\s*=|location\s*=|window\.open", re.I)
LOADING_RELS = {"stylesheet", "preload", "prefetch", "preconnect", "dns-prefetch", "icon", "modulepreload",
                "manifest", "apple-touch-icon", "prerender"}


class Resources(html_parser.HTMLParser):
    """What a page would fetch: any src, srcset, data, poster or background attribute other than an embedded
    PNG; a link whose rel holds a loading token; a frame or media element; a style attribute or <style> block
    with url() or @import (any case); and inline script that opens a request."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.fetched, self.images, self._in = [], [], None
        self._script, self._style = [], []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "img":
            self.images.append(a.get("src", ""))
        for key in ("src", "srcset", "data", "poster", "background", "lowsrc", "dynsrc"):
            if key in a and not (tag == "img" and key == "src" and a[key].startswith("data:image/png;base64,")):
                self.fetched.append(f"{tag} {key}={a[key][:60]}")
        if tag == "link" and set(a.get("rel", "").lower().split()) & LOADING_RELS:
            self.fetched.append(f"link rel={a.get('rel')} href={a.get('href')}")
        if tag in ("iframe", "frame", "embed", "object", "video", "audio", "source", "track", "base"):
            self.fetched.append(tag)
        if REMOTE_CSS.search(a.get("style", "")):
            self.fetched.append(f"{tag} style={a['style'][:60]}")
        if tag in ("script", "style"):
            self._in = tag

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._in == "script":
            self._script.append(data)
        elif self._in == "style":
            self._style.append(data)

    def close(self):
        super().close()
        if REMOTE_CSS.search("".join(self._style)):
            self.fetched.append("style block with url() or @import")
        for m in REMOTE_JS.finditer("".join(self._script)):
            self.fetched.append(f"script {m.group(0)}")


def network_loads(text):
    p = Resources()
    p.feed(text)
    p.close()
    return p.fetched


@pytest.mark.parametrize("out", sorted(PAGES))
def test_a_page_loads_nothing_from_the_network_or_another_file(out):
    assert network_loads(PAGES[out]) == [], out


@pytest.mark.parametrize("canary", [
    '<img src="data:image/png;base64,AA" srcset="https://example.invalid/a.png 2x">',
    '<link rel="alternate stylesheet" href="https://example.invalid/a.css">',
    '<link rel="StyleSheet" href="a.css">',
    '<style>body { background: URL(https://example.invalid/a.png) }</style>',
    '<style>@IMPORT "https://example.invalid/a.css";</style>',
    '<p style="background-image:url(https://example.invalid/a.png)">x</p>',
    '<script>fetch("https://example.invalid/data")</script>',
    '<script>new XMLHttpRequest()</script>',
    '<script>navigator.sendBeacon("https://example.invalid")</script>',
    '<script>var i = new Image(); i.src = "https://example.invalid/p.png"</script>',
    '<script src="https://example.invalid/a.js"></script>',
    "<script src='https://example.invalid/a.js'></script>",
    "<script src=https://example.invalid/a.js></script>",
    '<video poster="https://example.invalid/p.png"></video>',
])
def test_each_kind_of_network_load_is_caught(canary):
    assert network_loads(f"<html><body>{canary}</body></html>") != []


def test_an_embedded_png_and_a_plain_link_are_not_loads():
    assert network_loads('<img src="data:image/png;base64,AA"><a href="https://example.org">x</a>') == []


INLINE = {"a", "abbr", "b", "code", "em", "i", "kbd", "mark", "q", "s", "small", "span", "strong", "sub", "sup",
          "u", "del"}


class Visible(html_parser.HTMLParser):
    """The text a reader sees: no script or style, inline tags joined without a gap (so Mar<b>athon</b> reads
    Marathon), block tags separated by a line break."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag not in INLINE:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        elif tag not in INLINE:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def visible_text(text):
    p = Visible()
    p.feed(text)
    p.close()
    return "".join(p.parts)


CREDENTIALS = [
    ("a Databricks token", r"\bdapi[0-9a-f]{20,}"),
    ("an OpenAI-style key", r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}"),
    ("a GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{22,}"),
    ("a Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    ("an AWS access key ID", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("an AWS secret access key", r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}"),
    ("a private key", r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----"),
    ("a Google API key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("a credential assignment", r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|token)"
                                r"\b\s*[=:]\s*['\"]?(?=[^\s'\"<>]*[0-9])[^\s'\"<>{}$%]{12,}"),
]


def credentials(text):
    """(kind, matched text) for each credential-shaped string in text."""
    return [(kind, m.group(0)) for kind, pattern in CREDENTIALS for m in re.finditer(pattern, text)]


@pytest.mark.parametrize("spec", b.pages(), ids=lambda s: s["out"])
def test_no_page_or_source_holds_a_credential(spec):
    page = PAGES[spec["out"]]
    texts = {spec["out"]: page, spec["out"] + " (visible)": visible_text(page)}
    for src in spec["sources"] + ([spec["intro"]] if "intro" in spec else []):
        with open(os.path.join(b.ROOT, src), encoding="utf-8") as f:
            texts[src] = f.read()
    assert {name: credentials(text) for name, text in texts.items() if credentials(text)} == {}


@pytest.mark.parametrize("canary", [
    "dapi" + "0123456789abcdef0123456789abcdef", "sk-" + "A1b2C3d4E5f6G7h8I9j0K1l2",
    "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2", "github_pat_" + "11ABCDEFG0123456789_abcdefghijklmnop",
    "xoxb-" + "1234567890-abcdefghij", "AKIA" + "ABCDEFGHIJKLMNOP",
    "aws_secret_access_key = " + "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "-----BEGIN RSA " + "PRIVATE KEY-----", "AIza" + "SyA1234567890abcdefghijklmnopqrstuv",
    "password=" + "Hunter2!Hunter2!9", "api_key: " + "'x9.y8-z7_w6@v5u4'",
])
def test_each_credential_shape_is_caught(canary):
    assert credentials(canary) != []


@pytest.mark.parametrize("text", ["the password is in ~/epm-lpg/run.env", "--password <password>",
                                  "NEO4J_PASSWORD=%s", "token: see the env file", "a skill-version"])
def test_prose_and_placeholders_are_not_credentials(text):
    assert credentials(text) == []


def test_visible_text_joins_inline_tags_and_drops_scripts():
    assert visible_text("<p>Mar<b>athon</b></p><script>x()</script><p>next</p>").split() == ["Marathon", "next"]


def test_unsupported_markdown_stops_the_build_with_its_line():
    lines = ["Title", "=====", "", "![a picture](x.png)", "<div>raw</div>", "+ item", "1) item", "[ref]: https://x.test/",
             "```", "<kept> in code ![x](y)", "```", "`<kept>` in a code span"]
    problems = b.unsupported("doc.md", lines)
    assert problems == ["doc.md:2: a Setext heading underline (use # headings)",
                        "doc.md:4: an image (embed pictures in the page instead)",
                        "doc.md:5: inline HTML or an autolink (the page would show it as text)",
                        "doc.md:6: a list item marked with +",
                        "doc.md:7: a list item numbered with a parenthesis",
                        "doc.md:8: a reference-style link definition"]


@pytest.mark.parametrize("lines, what", [
    (["~~~", "code", "~~~"], "a tilde code fence"),
    (["```", "never closed"], "a code fence that is never closed"),
    (["Text.", "", "    indented code"], "an indented code block"),
    (["[x](https://x.test/ \"a title\")"], "a link with a title"),
    (["\\*not emphasis\\*"], "a backslash escape"),
    (["``code with ` inside``"], "a code span opened with more than one backtick"),
    (["Text <!-- a note --> more."], "an HTML comment inside a line"),
    (["> > nested"], "a nested block quote"),
    (["<div class=\"x\"", "id=\"y\">"], "inline HTML or an autolink"),
    (["[ref]:https://x.test/"], "a reference-style link definition"),
    (["  [ref]: https://x.test/"], "a reference-style link definition"),
    (["    ~~~"], "a tilde code fence"),
    (["Title", "  ===="], "a Setext heading underline"),
    (["see <https://x.test/>"], "inline HTML or an autolink"),
])
def test_each_construct_the_renderer_would_lose_stops_the_build(lines, what):
    assert any(what in p for p in b.unsupported("doc.md", lines)), b.unsupported("doc.md", lines)


def test_what_the_renderer_covers_passes_the_gate():
    lines = ["<!-- module: core -->", "<!--", "a <b>comment</b> block", "-->", "- item", "", "    continued item",
             "| `a \\| b` | split on \\| |", "> one quote", "```", "<raw> \\* ~~~", "```"]
    assert b.unsupported("doc.md", lines) == []


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


@pytest.mark.inputs("records")
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


def test_every_marked_page_in_the_repository_is_one_the_builder_makes():
    assert b.marked_pages() == sorted(PAGES), "an orphan page, or a built page not yet committed"


def test_the_check_command_fails_on_an_orphan_page(monkeypatch, capsys):
    monkeypatch.setattr(b, "marked_pages", lambda root=b.ROOT: sorted(PAGES) + ["business_architecture/old.html"])
    assert b.main(["--check"]) == 1
    assert "FAIL business_architecture/old.html carries the generator's mark" in capsys.readouterr().out


def test_every_page_carries_the_mark_and_the_template_takes_it_from_the_builder():
    assert all(b.MARK in page for page in PAGES.values())
    with open(b.TEMPLATE, encoding="utf-8") as f:
        assert b.MARK not in f.read(), "the template must take the mark from the builder, so it stays searchable"


def test_the_builder_writes_every_page_under_another_root(tmp_path):
    assert b.main([], out_root=str(tmp_path)) == 0
    for out, page in PAGES.items():
        assert (tmp_path / out).read_text(encoding="utf-8") == page


def test_every_source_exists():
    for spec in b.pages():
        for src in spec["sources"] + ([spec["intro"]] if "intro" in spec else []):
            assert os.path.isfile(os.path.join(b.ROOT, src)), src


@pytest.mark.inputs("records")
def test_every_decision_record_has_its_anchor_and_index_row():
    page = PAGES[b.DECISIONS_PAGE]
    records = [f for f in os.listdir(os.path.join(b.ROOT, b.DECISIONS_DIR)) if b.DEC_FILE.search(f)]
    assert records
    for f in records:
        rid = b.record_id(f)
        assert f'<section class="rec" id="{rid}">' in page, rid
        assert f'<td class="num"><a href="#{rid}">{rid[-4:]}</a></td>' in page, rid


def test_every_link_on_every_page_resolves():
    """A relative link names a file that exists, and an anchor on a linked HTML page exists there."""
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
            if not os.path.exists(target):
                problems.append(f"{out}: {href}: no such file")
                continue
            if target.endswith(".html") and target not in ids:
                # A hand-written page (the guide, the runbook): its anchors are its id and name attributes.
                with open(target, encoding="utf-8") as f:
                    ids[target] = set(re.findall(r'\b(?:id|name)="([^"]+)"', f.read()))
            if frag and frag != "top" and target in ids and frag not in ids[target]:
                problems.append(f"{out}: {href}: no such anchor")
    assert not problems, "\n".join(problems[:20])


def test_without_a_decisions_page_nothing_links_to_it(monkeypatch):
    # The share release's tree (EPM-DEC-001-0110): the decisions page is not built, so the navigation has no link
    # to it, a record ID in text stays text, a Markdown link to a record keeps its text alone, and every link that
    # is generated resolves.
    reduced = [s for s in b.all_pages() if not s.get("decisions")]
    monkeypatch.setattr(b, "pages", lambda: reduced)
    built = b.build_all()
    assert b.DECISIONS_PAGE not in built
    for out, page in built.items():
        assert not re.search(r'href="[^"]*decisions\.html', page), out
        assert 'href="{{DECISIONS}}"' not in page and ">Decisions</a>" not in page, out
        here = os.path.normpath(os.path.join(b.ROOT, out))
        for href in re.findall(r'href="([^"]+)"', page):
            path = html.unescape(href).partition("#")[0]
            if path and not re.match(r"^[a-z]+:", path):
                assert os.path.exists(os.path.normpath(os.path.join(os.path.dirname(here), path))), (out, href)
    spec = next(s for s in reduced if s["out"] == "business_architecture/ontology/README.html")
    p = b.Page(spec, b.generated_map(reduced), decisions_page=False)
    assert p.inline(SRC, "see EPM-DEC-001-0040.") == "see EPM-DEC-001-0040."
    assert p.inline(SRC, "[0099](../domain/decisions/EPM-DEC-001-0099-item-g.md)") == "0099"
    assert 'href="MODULES.html"' in p.inline(SRC, "[guide](MODULES.md)")  # other links are unchanged


def test_on_main_a_missing_source_still_stops_the_build(monkeypatch):
    # Release mode off: single() reads the source's title as it always did, so a source that is not here raises.
    monkeypatch.setattr(b, "SHARE_RELEASE", False)
    with pytest.raises(FileNotFoundError):
        b.single("business_architecture/ontology/no-such-document.md", "lead")
    monkeypatch.setattr(b, "SHARE_RELEASE", True)
    assert b.single("business_architecture/ontology/no-such-document.md", "lead")["title"] is None


def page(spec_out="business_architecture/ontology/README.html"):
    specs = b.pages()
    spec = next(s for s in specs if s["out"] == spec_out)
    return b.Page(spec, b.generated_map(specs))


SRC = os.path.normpath(os.path.join(b.ROOT, "business_architecture/ontology/README.md"))


def test_a_link_to_a_generated_document_goes_to_its_page():
    assert 'href="MODULES.html"' in page().inline(SRC, "[guide](MODULES.md)")
    assert 'href="kpi/README.html#releases"' in page().inline(SRC, "[kpi](kpi/README.md#releases)")


@pytest.mark.inputs("records")
def test_a_link_to_a_decision_record_goes_to_its_anchor():
    out = page().inline(SRC, "[0099](../domain/decisions/EPM-DEC-001-0099-item-g.md)")
    assert 'href="../domain/decisions/decisions.html#EPM-DEC-001-0099"' in out


@pytest.mark.inputs("records")
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
