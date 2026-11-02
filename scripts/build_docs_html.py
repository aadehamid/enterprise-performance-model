#!/usr/bin/env python3
"""Build the HTML pages of the ontology's reading documents from their Markdown.

Run from the repository root:
  python3 scripts/build_docs_html.py            write every page
  python3 scripts/build_docs_html.py --check    exit 1 when a committed page differs from a fresh build

The Markdown is the master copy. Each page is generated from it through scripts/docs_template.html, sits
next to its Markdown with the same base name, and is never edited by hand. The decision records are one
page, business_architecture/domain/decisions/decisions.html, with an index and an anchor per record
(#EPM-DEC-001-0099). scripts/test_docs_html.py runs --check, so a Markdown change that is not rebuilt
fails scripts/check.sh.

Links: a relative link to a Markdown file that has a page here goes to that page; a link to a decision
record goes to its anchor on decisions.html; a decision ID in running text (EPM-DEC-001-0099) becomes a
link to its anchor; any other relative link stays a relative path. Standard library only. The renderer
covers the Markdown these files use: ATX headings, paragraphs, thematic breaks (dropped), HTML comments
(dropped), fenced code (also inside list items), tables, nested ordered and unordered lists, block quotes,
`code`, **bold**, *italic*, ~~strikethrough~~, [links](...), bare https URLs, and an escaped pipe in a table
cell. Markdown it does not cover stops the build with its file and line, so a source edit cannot lose
structure silently: an image, inline HTML (also across lines), a comment inside a line, a + or 1) list item,
a reference-style link, a link with a title, a backslash escape, a code span opened with two backticks, a
nested block quote, a tilde fence, a fence never closed, an indented code block and a Setext heading
(unsupported()). The renderer started as
personal-agent-skills' scripts/build_playbook_html.py; the look is the stores runbook's (framed-sheet).
"""
import glob
import html
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "scripts", "docs_template.html")
# Every generated page carries this mark; the template takes it from here, and scripts/epm_facts.py reads it.
GENERATOR = "scripts/build_docs_html.py"
MARK = f'<meta name="generator" content="{GENERATOR}">'

# The share release (EPM-DEC-001-0110) carries no decision records and leaves some documents out: in release mode
# (EPM_SHARE_RELEASE, or release.json at the tree's root) a page whose source is not here is not built, and nothing
# links to the decisions page. On main every source must be here, as before.
SHARE_RELEASE = bool(os.environ.get("EPM_SHARE_RELEASE")) or os.path.isfile(os.path.join(ROOT, "release.json"))

GUIDE = "business_architecture/ontology/epm-ontology-guide.html"
ONT = "business_architecture/ontology"
DECISIONS_DIR = "business_architecture/domain/decisions"
DECISIONS_PAGE = f"{DECISIONS_DIR}/decisions.html"
DEC_FILE = re.compile(r"EPM-DEC-001-(\d{4})-[\w-]+\.md$")
DEC_ID = re.compile(r"(?<![\w/#-])EPM-DEC-001-(\d{4})(?![\w-])")

# The folders the twelve released packages are built from, each documented by its README; technical-graph joined
# them with its 1.0.0 on 2026-11-02 (EPM-DEC-001-0112). core is built
# from the process map and release/; its changelog is its own document.
MODULE_READMES = ["kpi", "lane", "market-data", "organization", "party", "ref-mpc", "system", "value-stream",
                  "data-product", "consumer", "authority", "placement", "population", "provenance", "validation",
                  "regression", "apqc", "technical-graph"]


def single(src, lead, scope="EPM ontology"):
    """A page for one Markdown source; its title is the source's own H1, word for word."""
    # In release mode a source that is not in this tree makes no page: pages() drops it. On main it is read as always.
    title = None if SHARE_RELEASE and not os.path.exists(os.path.join(ROOT, src)) else source_title(src)
    return {"out": src[:-3] + ".html", "title": title, "scope": scope, "lead": lead, "sources": [src]}


def source_title(rel):
    """The Markdown text of a source's H1 (outside fenced code); a source without one cannot be a page."""
    titles = [ln[2:].strip() for ln in outside_fences(read_lines(rel)) if ln.startswith("# ")]
    if not titles:
        raise ValueError(f"{rel}: no H1 to title its page")
    return titles[0]


def read_lines(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read().split("\n")


def outside_fences(lines):
    """The lines that are not inside fenced code or an HTML comment block."""
    out, fenced, comment = [], False, False
    for line in lines:
        if not fenced and line.strip().startswith("<!--"):
            comment = "-->" not in line
            continue
        if comment:
            comment = "-->" not in line
            continue
        if re.match(r"^ *```", line):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


def drop_title(lines):
    """The lines without the H1 that titles the page (the first "# " line outside fenced code); a "# "
    line inside a fence, such as a shell comment, stays."""
    fenced = False
    for i, line in enumerate(lines):
        if re.match(r"^ *```", line):
            fenced = not fenced
        elif not fenced and line.startswith("# "):
            return lines[:i] + lines[i + 1:]
    return lines


def record_meta(rel, lines):
    """A decision record's displayed H1, Status and Date, read outside fenced code and comments. A record
    must have exactly one of each, so an example in a fence can never stand in for the record."""
    shown = outside_fences(lines)
    h1 = [ln[2:].strip() for ln in shown if ln.startswith("# ")]
    rows = {name: [m.group(1).strip() for ln in shown for m in [re.match(rf"^\|\s*{name}\s*\|(.*)\|\s*$", ln)] if m]
            for name in ("Status", "Date")}
    problems = [f"{rel}: {len(v)} {k} rows, not one" for k, v in (("H1", h1), *rows.items()) if len(v) != 1]
    if problems:
        raise ValueError("; ".join(problems))
    return h1[0], rows["Status"][0], rows["Date"][0]


def all_pages():
    """Every page: its output, its title, one sentence on what it is, and its sources."""
    out = [
        single(f"{ONT}/README.md",
               "Where the ontology build stands, what each part of this folder holds, and where to start."),
        single(f"{ONT}/MODULES.md",
               "Each module of the ontology: what it holds, how it links to the others, and an example quoted "
               "from its release."),
        single(f"{ONT}/competency-questions.md",
               "The questions the ontology must answer, which decide what it holds."),
        single(f"{ONT}/OPEN-ITEMS.md",
               "What stays open on the ontology, who answers each item, and the record that holds it."),
        single(f"{ONT}/business-closeout.md",
               "The points about the ontology that only the business can settle, and the record each answer goes to."),
        single(f"{ONT}/release/CHANGELOG.md",
               "What each release of the core module changed, and why."),
        single(f"{ONT}/projection/README.md",
               "How the released packages are projected into a Neo4j property graph and checked."),
        single(f"{ONT}/projection/LOCAL-STORES.md",
               "Where each store that holds the ontology or the demo data lives, and how to refresh it."),
        single(f"{ONT}/projection/STORE-INVENTORY.md",
               "What each store holds now, what should not be in it, and how to check it yourself."),
        single(f"{ONT}/projection/skill-run/README.md",
               "How the ontology-to-lpg skill's driver runs on these releases, with every store and check."),
        single("business_architecture/domain/business-glossary.md",
               "The business terms the ontology and its documents use, each defined once."),
    ]
    for m in MODULE_READMES:
        src = f"{ONT}/{m}/README.md"
        out.append(single(src, f"The {m} folder of the ontology build: what it holds, "
                          "how it is built and checked, and its releases.", scope="Module"))
    for path in sorted(glob.glob(os.path.join(ROOT, "business_architecture/business_process/proposals/*.md"))):
        rel = os.path.relpath(path, ROOT)
        out.append(single(rel, "A proposed change to the process map. A proposal is not applied until it is accepted.",
                          scope="Process-map proposal"))
    records = sorted(glob.glob(os.path.join(ROOT, DECISIONS_DIR, "EPM-DEC-001-*.md")))
    if SHARE_RELEASE and not (records and os.path.exists(os.path.join(ROOT, DECISIONS_DIR, "README.md"))):
        return out  # the share release carries no decision records (EPM-DEC-001-0110): no decisions page
    if not records:
        raise ValueError(f"no decision records under {DECISIONS_DIR}; the decisions page cannot be built from none")
    numbers = [record_id(p) for p in records]
    twice = sorted({n for n in numbers if numbers.count(n) > 1})
    if twice:
        raise ValueError(f"two records share a number: {', '.join(twice)}")
    out.append({"out": DECISIONS_PAGE, "title": source_title(f"{DECISIONS_DIR}/README.md"), "scope": "EPM-DEC-001",
                "lead": "Every decision behind the ontology and its build: context, decision, alternatives, the "
                        "decision owner's recorded words, evidence, status and date.",
                "sources": [os.path.relpath(p, ROOT) for p in records], "intro": f"{DECISIONS_DIR}/README.md",
                "decisions": True})
    return out


LIST_ITEM = re.compile(r"^( *)([-*]|\d+\.) (.*)$")
FENCE = re.compile(r"^( *)```(\S*)\s*$")
HEADING = re.compile(r"^(#{1,6}) (.+?)\s*#*\s*$")


UNSUPPORTED = [
    (re.compile(r"!\[[^\]]*\]\("), "an image (embed pictures in the page instead)"),
    # The start of any HTML tag, closing tag, declaration or autolink, also one that runs onto the next line
    # (the skills builder's pattern); a comment is left to the next rule.
    (re.compile(r"<(?:[A-Za-z][A-Za-z0-9-]*(?=[\s/>]|$)|/[A-Za-z]|!(?!--)|[A-Za-z][A-Za-z0-9+.-]*:)"),
     "inline HTML or an autolink (the page would show it as text)"),
    (re.compile(r"\S\s*<!--|<!--.*-->\s*\S"), "an HTML comment inside a line (only a comment on its own lines is dropped)"),
    (re.compile(r"^ *\+ "), "a list item marked with +"),
    (re.compile(r"^ *\d+\) "), "a list item numbered with a parenthesis"),
    (re.compile(r"^\s*\[[^\]]+\]:"), "a reference-style link definition"),
    (re.compile(r"\]\([^)\s]+\s+[\"'(]"), "a link with a title"),
    (re.compile(r"\\[\\`*_{}\[\]()#+.!>~-]"), "a backslash escape"),
    (re.compile(r"^\s*>\s*>"), "a nested block quote"),
    (re.compile(r"^\s*~~~"), "a tilde code fence (use backticks)"),
    (re.compile(r"^\s*=+\s*$"), "a Setext heading underline (use # headings)"),
]


def unsupported(rel, lines):
    """Each line of a source that holds Markdown the renderer does not cover, as "path:line: what", so a
    source edit cannot lose structure without the build saying so. Fenced code, comment blocks and code spans
    are skipped; an escaped pipe in a table row is covered."""
    problems, fenced, opened, comment, prev, in_list = [], False, 0, False, "", False
    for n, line in enumerate(lines, 1):
        if not fenced and not comment and line.strip().startswith("<!--"):
            comment = "-->" not in line
            if comment or line.strip().endswith("-->"):
                prev = ""
                continue
        if comment:
            comment = "-->" not in line
            continue
        if FENCE.match(line):
            fenced, opened, prev = not fenced, n, ""
            continue
        if fenced:
            continue
        if re.search(r"`{2,}", line):
            problems.append(f"{rel}:{n}: a code span opened with more than one backtick")
        text = re.sub(r"`[^`]*`", "", line)
        if text.lstrip().startswith("|"):
            text = text.replace("\\|", "")
        for pattern, what in UNSUPPORTED:
            if pattern.search(text):
                problems.append(f"{rel}:{n}: {what}")
        if LIST_ITEM.match(line):
            in_list = True
        elif line.strip() and not line.startswith(" "):
            in_list = False
        if not in_list and not prev.strip() and re.match(r"^ {4,}\S", line):
            problems.append(f"{rel}:{n}: an indented code block (use a fence)")
        if re.fullmatch(r" {0,3}-+\s*", line) and prev.strip() \
                and not prev.lstrip().startswith(("|", "#")) and not LIST_ITEM.match(prev):
            problems.append(f"{rel}:{n}: a Setext heading (use # headings)")
        prev = line
    if fenced:
        problems.append(f"{rel}:{opened}: a code fence that is never closed")
    return problems


def slug(text):
    """A heading's anchor: lower case, words joined by hyphens, punctuation dropped."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


def record_id(path):
    m = DEC_FILE.search(path)
    return f"EPM-DEC-001-{m.group(1)}" if m else None


class Page:
    """Renders the sources of one page; knows where every other generated page and record lives."""

    def __init__(self, spec, generated, decisions_page=True):
        self.spec = spec
        self.out = os.path.join(ROOT, spec["out"])
        self.out_dir = os.path.dirname(self.out)
        self.generated = generated     # normalised Markdown path -> its page's path
        self.decisions = spec.get("decisions", False)
        self.decisions_page = decisions_page  # whether decisions.html is built in this run; if not, nothing links to it
        self.toc, self.used = [], set()

    # ---- anchors and links

    def prefix(self, src):
        return (record_id(src) or "") if self.decisions else ""

    def anchor(self, src, text):
        base = slug(text)
        pre = self.prefix(src)
        a = f"{pre}--{base}" if pre else base
        n, cand = 2, a
        while cand in self.used:
            cand, n = f"{a}-{n}", n + 1
        self.used.add(cand)
        return cand

    def to(self, page):
        """A path from this page to another generated file, or "" when it is this page."""
        target = os.path.join(ROOT, page)
        if os.path.normpath(target) == os.path.normpath(self.out):
            return ""
        return os.path.relpath(target, self.out_dir)

    def record_link(self, src, url):
        """Whether a relative Markdown link names a decision record's file."""
        if re.match(r"^[a-z]+:", url) or url.startswith("#"):
            return False
        path = url.partition("#")[0]
        return bool(record_id(os.path.normpath(os.path.join(os.path.dirname(src), path))))

    def link(self, src, url):
        """Where a Markdown link points on the generated pages."""
        if re.match(r"^[a-z]+:", url):
            return url
        if url.startswith("#"):
            pre = self.prefix(src)
            return f"#{pre}--{url[1:]}" if pre else url
        path, _, frag = url.partition("#")
        target = os.path.normpath(os.path.join(os.path.dirname(src), path))
        rid = record_id(target)
        if rid:
            return f"{self.to(DECISIONS_PAGE)}#{rid}--{frag}" if frag else f"{self.to(DECISIONS_PAGE)}#{rid}"
        if target in self.generated:
            page = self.to(self.generated[target])
            return page + (f"#{frag}" if frag else ("" if page else "#top"))
        return os.path.relpath(target, self.out_dir) + (f"#{frag}" if frag else "")

    # ---- inline

    def inline(self, src, text):
        # Code spans become placeholders first, so bold, italics and links may hold code.
        codes = []

        def keep(m):
            codes.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
            return f"\x00{len(codes) - 1}\x00"
        s = re.sub(r"`([^`]*)`", keep, text)
        s = html.escape(s, quote=False)
        links = []

        def hold(markup):
            # A finished link is set aside, so the bare-URL and decision-ID passes do not touch its text.
            links.append(markup)
            return f"\x01{len(links) - 1}\x01"

        def a(m):
            url = re.sub(r"\x00(\d+)\x00", lambda c: re.sub(r"<[^>]+>", "", codes[int(c.group(1))]), m.group(2))
            if not self.decisions_page and self.record_link(src, html.unescape(url)):
                return hold(m.group(1))  # a link to a record, with no decisions page to take it: the text alone
            return hold(f'<a href="{html.escape(self.link(src, html.unescape(url)))}">{m.group(1)}</a>')
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", a, s)
        s = re.sub(r'(?<![="\w/>])(https?://[^\s<)\x00]*[^\s<).,;:\x00])',
                   lambda m: hold(f'<a href="{m.group(1)}">{m.group(1)}</a>'), s)
        page = self.to(DECISIONS_PAGE)
        if self.decisions_page:
            s = DEC_ID.sub(lambda m: hold(f'<a href="{page}#EPM-DEC-001-{m.group(1)}">{m.group(0)}</a>'), s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        s = re.sub(r"~~(.+?)~~", r"<del>\1</del>", s)
        s = re.sub(r"\x01(\d+)\x01", lambda m: links[int(m.group(1))], s)
        return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)

    # ---- blocks

    def blocks(self, src, lines, depth=0):
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            if not line.strip() or re.fullmatch(r" {0,3}(-{3,}|\*{3,})\s*", line):
                # A thematic break adds nothing the next heading does not already show.
                i += 1
                continue
            if line.strip().startswith("<!--"):
                # A comment marks the Markdown for a test (MODULES.md's module tags); readers do not see it.
                while i < len(lines) and "-->" not in lines[i]:
                    i += 1
                i += 1
                continue
            m = FENCE.match(line)
            if m:
                indent, lang = len(m.group(1)), m.group(2)
                body, i = [], i + 1
                while i < len(lines) and not FENCE.match(lines[i]):
                    body.append(lines[i][indent:] if lines[i][:indent].strip() == "" else lines[i])
                    i += 1
                i += 1
                cls = f' class="lang-{html.escape(lang)}"' if lang else ""
                out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body), quote=False)}</code></pre>")
                continue
            m = HEADING.match(line)
            if m and depth == 0:
                level, text = len(m.group(1)), m.group(2)
                aid = self.anchor(src, text)
                level_out = min(level + (1 if self.decisions else 0), 6)
                if level_out <= 3 and not self.decisions:
                    self.toc.append((level_out, aid, text))
                out.append(f'<h{level_out} id="{aid}">{self.inline(src, text)}'
                           f'<a class="hl" href="#{aid}" aria-label="Link to this section">#</a></h{level_out}>')
                i += 1
                continue
            if line.lstrip().startswith(">"):
                quoted = []
                while i < len(lines) and lines[i].lstrip().startswith(">"):
                    quoted.append(re.sub(r"^\s*> ?", "", lines[i]))
                    i += 1
                out.append(f"<blockquote>{self.blocks(src, quoted, depth + 1)}</blockquote>")
                continue
            if line.lstrip().startswith("|"):
                rows = []
                while i < len(lines) and lines[i].lstrip().startswith("|"):
                    rows.append(lines[i].strip())
                    i += 1
                out.append(self.table(src, rows))
                continue
            if LIST_ITEM.match(line):
                html_list, i = self.list_block(src, lines, i, depth)
                out.append(html_list)
                continue
            para = [line.strip()]
            i += 1
            while (i < len(lines) and lines[i].strip() and not FENCE.match(lines[i])
                   and not HEADING.match(lines[i]) and not lines[i].lstrip().startswith("|")
                   and not lines[i].lstrip().startswith(">") and not LIST_ITEM.match(lines[i])):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{self.inline(src, ' '.join(para))}</p>")
        return "\n".join(out)

    def table(self, src, rows):
        def cells(row):
            row = row.strip()
            if row.startswith("|"):
                row = row[1:]
            if row.endswith("|") and not row.endswith("\\|"):
                row = row[:-1]
            parts, cur, code, k = [], "", False, 0
            while k < len(row):
                ch = row[k]
                if ch == "\\" and row[k + 1:k + 2] == "|":
                    cur += "|"        # an escaped pipe is a pipe in the cell, as GitHub shows it
                    k += 2
                    continue
                if ch == "`":
                    code = not code
                if ch == "|" and not code:
                    parts.append(cur)
                    cur = ""
                else:
                    cur += ch
                k += 1
            parts.append(cur)
            return [p.strip() for p in parts]
        head = cells(rows[0])
        body = [cells(r) for r in rows[2:]] if len(rows) > 1 and re.match(r"^\|?[\s:|-]+\|?$", rows[1]) else \
            [cells(r) for r in rows[1:]]
        # A column whose every body cell is a figure is right-aligned (tabular figures come from the CSS).
        numeric = [bool(body) and all(re.fullmatch(r"[-+]?[\d.,]+%?", (r[k] if k < len(r) else "").strip())
                                      for r in body) for k in range(len(head))]
        cls = lambda k: ' class="num"' if k < len(numeric) and numeric[k] else ""
        th = "".join(f"<th{cls(k)}>{self.inline(src, c)}</th>" for k, c in enumerate(head))
        trs = "".join("<tr>" + "".join(f"<td{cls(k)}>{self.inline(src, c)}</td>" for k, c in enumerate(r)) + "</tr>"
                      for r in body)
        return f'<div class="tblwrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

    def list_block(self, src, lines, i, depth):
        m = LIST_ITEM.match(lines[i])
        base = len(m.group(1))
        ordered = m.group(2)[0].isdigit()
        start = int(m.group(2)[:-1]) if ordered else 1
        items = []
        while i < len(lines):
            m = LIST_ITEM.match(lines[i])
            if not m or len(m.group(1)) != base or m.group(2)[0].isdigit() != ordered:
                break
            content_col = base + len(m.group(2)) + 1
            body = [m.group(3)]
            i += 1
            while i < len(lines):
                ln = lines[i]
                if not ln.strip():
                    nxt = next((x for x in lines[i + 1:] if x.strip()), None)
                    if nxt is not None and len(nxt) - len(nxt.lstrip()) > base:
                        body.append("")
                        i += 1
                        continue
                    break
                ind = len(ln) - len(ln.lstrip())
                if ind <= base and (LIST_ITEM.match(ln) or HEADING.match(ln) or ln.lstrip().startswith("|")):
                    break
                if ind <= base and not body[-1].strip():
                    break
                cut = min(ind, content_col)
                body.append(ln[cut:])
                i += 1
            items.append(body)
        lis = []
        for body in items:
            first, rest = [], []
            for k, ln in enumerate(body):
                if k == 0 or (not rest and ln.strip() and not LIST_ITEM.match(ln) and not FENCE.match(ln)
                              and not ln.startswith(" ") and not ln.lstrip().startswith(">")):
                    first.append(ln.strip())
                else:
                    rest = body[k:]
                    break
            inner = self.inline(src, " ".join(first))
            if rest:
                inner += "\n" + self.blocks(src, rest, depth + 1)
            lis.append(f"<li>{inner}</li>")
        tag = "ol" if ordered else "ul"
        attr = f' start="{start}"' if ordered and start != 1 else ""
        return f"<{tag}{attr}>{''.join(lis)}</{tag}>", i

    # ---- the page

    @staticmethod
    def read(rel):
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            return f.read().split("\n")

    def render_decisions(self):
        intro = self.spec["intro"]
        src_intro = os.path.normpath(os.path.join(ROOT, intro))
        # The intro is the folder README without its title and its table: the index below replaces the table.
        lines = [x for x in drop_title(self.read(intro)) if not x.lstrip().startswith("|")]
        parts = [self.blocks(src_intro, lines)]
        rows, sections = [], []
        for rel in self.spec["sources"]:
            src = os.path.normpath(os.path.join(ROOT, rel))
            rid = record_id(rel)
            lines = self.read(rel)
            h1, status, date = record_meta(rel, lines)
            title = h1.split(":", 1)[1].strip() if ":" in h1 else h1
            self.used.add(rid)
            body = drop_title(lines)
            num = rid[-4:]
            rows.append(f'<tr><td class="num"><a href="#{rid}">{num}</a></td><td>{self.inline(src, title)}</td>'
                        f'<td>{self.inline(src, status)}</td><td class="num">{self.inline(src, date)}</td></tr>')
            self.toc.append((3, rid, f"{num} {title}"))
            sections.append(f'<section class="rec" id="{rid}"><h2>{html.escape(rid)}: {self.inline(src, title)}'
                            f'<a class="hl" href="#{rid}" aria-label="Link to this record">#</a></h2>\n'
                            f'<p class="from">From <code>{html.escape(os.path.basename(rel))}</code></p>\n'
                            + self.blocks(src, body) + "</section>")
        self.used.add("index")
        self.toc.insert(0, (2, "index", "Index"))
        index = ('<h2 id="index">Index<a class="hl" href="#index" aria-label="Link to this section">#</a></h2>'
                 f'<p>{len(rows)} records. Each number links to its record below.</p>'
                 '<div class="tblwrap"><table class="index"><thead><tr><th class="num">Record</th><th>Decision</th>'
                 '<th>Status</th><th class="num">Date</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
        return "\n".join(parts + [index] + sections)

    def render(self):
        if self.decisions:
            body = self.render_decisions()
            sources = (f"<code>{html.escape(os.path.basename(self.spec['intro']))}</code> and the "
                       f"{len(self.spec['sources'])} records <code>EPM-DEC-001-*.md</code> in this folder")
        else:
            rel = self.spec["sources"][0]
            src = os.path.normpath(os.path.join(ROOT, rel))
            body = self.blocks(src, drop_title(self.read(rel)))
            sources = f"<code>{html.escape(os.path.basename(rel))}</code>"
        toc = "\n".join(f'<li class="l{lvl}"><a href="#{aid}">{self.inline_plain(text)}</a></li>'
                        for lvl, aid, text in self.toc)
        with open(TEMPLATE, encoding="utf-8") as f:
            page = f.read()
        if not self.decisions_page:  # no decisions page in this run (the share release): no link to it in the navigation
            page = page.replace('    <a href="{{DECISIONS}}">Decisions</a>\n', "")
        values = {
            "{{GENERATOR}}": GENERATOR,
            "{{TITLE}}": self.inline_plain(self.spec["title"]),
            "{{H1}}": self.inline(self.spec["sources"][0], self.spec["title"]),
            "{{SCOPE}}": html.escape(self.spec["scope"]),
            "{{LEAD}}": html.escape(self.spec["lead"]),
            "{{SOURCES}}": sources,
            "{{GUIDE}}": html.escape(self.to(GUIDE)),
            "{{DECISIONS}}": html.escape(self.to(DECISIONS_PAGE) or "#top"),
            "{{TOC}}": toc,
            "{{BODY}}": body,
        }
        for k, v in values.items():
            page = page.replace(k, v)
        return page

    @staticmethod
    def inline_plain(text):
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = text.replace("`", "").replace("**", "")
        return html.escape(text, quote=False)


def generated_map(specs):
    """Each Markdown source that has its own page -> that page's path."""
    return {os.path.normpath(os.path.join(ROOT, s["sources"][0])): s["out"] for s in specs if not s.get("decisions")}


def pages():
    """Every page on main. In release mode, all_pages() minus those with a source that is not here: the share release
    carries no decision records and leaves some documents out (EPM-DEC-001-0110)."""
    specs = all_pages()
    if not SHARE_RELEASE:
        return specs
    # The share release's own guide has its page there; on main it is a template in scripts/share_release/.
    if os.path.exists(os.path.join(ROOT, "HOW-TO-UPDATE.md")):
        specs = specs + [single("HOW-TO-UPDATE.md", "How to change what you received: a definition, a concept, a process or a module.", "This release")]
    return [s for s in specs if all(os.path.exists(os.path.join(ROOT, rel)) for rel in s["sources"] + ([s["intro"]] if "intro" in s else []))]


def build_all():
    """Every page's path -> its HTML. Refuses (ValueError) when a source holds Markdown the renderer does not cover."""
    specs = pages()
    problems = []
    for spec in specs:
        for rel in spec["sources"] + ([spec["intro"]] if "intro" in spec else []):
            problems += unsupported(rel, Page.read(rel))
    if problems:
        raise ValueError("Markdown the renderer does not cover:\n  " + "\n  ".join(problems))
    gen = generated_map(specs)
    decisions_page = any(s.get("decisions") for s in specs)  # absent in the share release: then nothing links to it
    return {s["out"]: Page(s, gen, decisions_page).render() for s in specs}


def marked_pages(root=ROOT):
    """Every tracked .html file that carries the generator's mark, as a path from the repository root."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    if os.path.exists(os.path.join(root, ".git")):
        names = subprocess.check_output(["git", "-C", root, "ls-files", "-z", "*.html"], env=env).decode().split("\0")
    else:  # a tree without Git, such as the share release: every .html file in it
        names = [os.path.relpath(os.path.join(r, f), root) for r, ds, fs in os.walk(root) for f in fs
                 if f.endswith(".html") and "__pycache__" not in r]
    marked = []
    for name in filter(None, names):
        try:
            with open(os.path.join(root, name), encoding="utf-8") as f:
                head = f.read(4096)
        except (OSError, UnicodeDecodeError):
            continue
        if MARK in head:
            marked.append(name)
    return sorted(marked)


def orphans(built, marked):
    """Marked pages the builder no longer makes: no source keeps them fresh, so they must be removed by hand."""
    return sorted(set(marked) - set(built))


def main(argv, out_root=ROOT):
    """Write every page under out_root, or with --check compare them; --check also fails on an orphan page."""
    check = "--check" in argv
    stale = []
    built = build_all()
    for out, page in built.items():
        path = os.path.join(out_root, out)
        if check:
            try:
                with open(path, encoding="utf-8") as f:
                    current = f.read()
            except FileNotFoundError:
                current = None
            if current != page:
                stale.append(out)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(page)
            print(f"wrote {out}")
    lost = orphans(built, marked_pages(out_root)) if check else []
    for s in stale:
        print(f"FAIL {s} differs from a fresh build of its Markdown: run python3 scripts/build_docs_html.py")
    for s in lost:
        print(f"FAIL {s} carries the generator's mark but no source builds it: remove it, or add its source")
    if stale or lost:
        return 1
    if check:
        print("ok  every generated page matches its Markdown")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
