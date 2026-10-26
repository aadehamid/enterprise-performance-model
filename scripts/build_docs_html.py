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
`code`, **bold**, *italic*, ~~strikethrough~~, [links](...) and bare https URLs. Markdown it does not cover
(an image, inline HTML, a + or 1) list item, a reference-style link, a Setext heading) stops the build with
its file and line, so a source edit cannot lose structure silently. The renderer started as
personal-agent-skills' scripts/build_playbook_html.py; the look is the stores runbook's (framed-sheet).
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "scripts", "docs_template.html")
GUIDE = "business_architecture/ontology/ontology-guide.html"
ONT = "business_architecture/ontology"
DECISIONS_DIR = "business_architecture/domain/decisions"
DECISIONS_PAGE = f"{DECISIONS_DIR}/decisions.html"
DEC_FILE = re.compile(r"EPM-DEC-001-(\d{4})-[\w-]+\.md$")
DEC_ID = re.compile(r"(?<![\w/#-])EPM-DEC-001-(\d{4})(?![\w-])")

# The folders the eleven released packages are built from, each documented by its README. core is built
# from the process map and release/; its changelog is its own document.
MODULE_READMES = ["kpi", "lane", "market-data", "organization", "party", "ref-mpc", "system", "value-stream",
                  "data-product", "consumer", "authority", "placement", "population", "provenance", "validation",
                  "regression", "apqc"]


def single(src, title, lead, scope="EPM ontology"):
    return {"out": src[:-3] + ".html", "title": title, "scope": scope, "lead": lead, "sources": [src]}


def first_heading(rel, fallback):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        first = next((ln for ln in f if ln.startswith("# ")), f"# {fallback}")
    return first[2:].strip().replace("`", "")


def pages():
    """Every page: its output, its title, one sentence on what it is, and its sources."""
    out = [
        single(f"{ONT}/README.md", "The ontology build",
               "Where the ontology build stands, what each part of this folder holds, and where to start."),
        single(f"{ONT}/MODULES.md", "Module guide",
               "Each module of the ontology: what it holds, how it links to the others, and an example quoted "
               "from its release."),
        single(f"{ONT}/competency-questions.md", "Competency questions",
               "The questions the ontology must answer, which decide what it holds."),
        single(f"{ONT}/business-closeout.md", "Business close-out",
               "The points about the ontology that only the business can settle, and the record each answer goes to."),
        single(f"{ONT}/release/CHANGELOG.md", "core changelog",
               "What each release of the core module changed, and why."),
        single(f"{ONT}/projection/README.md", "Property-graph projection",
               "How the released packages are projected into a Neo4j property graph and checked."),
        single(f"{ONT}/projection/LOCAL-STORES.md", "The stores kept for exploration",
               "Where each store that holds the ontology or the demo data lives, and how to refresh it."),
        single(f"{ONT}/projection/skill-run/README.md", "Running the projection skill",
               "How the ontology-to-lpg skill's driver runs on these releases, with every store and check."),
        single("business_architecture/domain/business-glossary.md", "Business glossary",
               "The business terms the ontology and its documents use, each defined once."),
    ]
    for m in MODULE_READMES:
        src = f"{ONT}/{m}/README.md"
        out.append(single(src, first_heading(src, m), f"The {m} folder of the ontology build: what it holds, "
                          "how it is built and checked, and its releases.", scope="Module"))
    for path in sorted(glob.glob(os.path.join(ROOT, "business_architecture/business_process/proposals/*.md"))):
        rel = os.path.relpath(path, ROOT)
        out.append(single(rel, first_heading(rel, os.path.basename(rel)),
                          "A proposed change to the process map. A proposal is not applied until it is accepted.",
                          scope="Process-map proposal"))
    records = sorted(glob.glob(os.path.join(ROOT, DECISIONS_DIR, "EPM-DEC-001-*.md")))
    out.append({"out": DECISIONS_PAGE, "title": "Decision records", "scope": "EPM-DEC-001",
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
    (re.compile(r"<(?!!--)[A-Za-z/][^>]*>"), "inline HTML (the page would show it as text)"),
    (re.compile(r"^ *\+ "), "a list item marked with +"),
    (re.compile(r"^ *\d+\) "), "a list item numbered with a parenthesis"),
    (re.compile(r"^ {0,3}\[[^\]]+\]: "), "a reference-style link definition"),
]


def unsupported(rel, lines):
    """Each line of a source that holds Markdown the renderer does not cover, as "path:line: what", so a
    source edit cannot lose structure without the build saying so. Fenced code and code spans are skipped."""
    problems, fenced, prev = [], False, ""
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            fenced, prev = not fenced, ""
            continue
        if fenced:
            continue
        text = re.sub(r"`[^`]*`", "", line)
        for pattern, what in UNSUPPORTED:
            if pattern.search(text):
                problems.append(f"{rel}:{n}: {what}")
        if (re.fullmatch(r" {0,3}=+\s*", line) or re.fullmatch(r" {0,3}-+\s*", line)) and prev.strip() \
                and not prev.lstrip().startswith(("|", "#")) and not LIST_ITEM.match(prev):
            problems.append(f"{rel}:{n}: a Setext heading (use # headings)")
        prev = line
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


def is_title(line):
    return line.startswith("# ")


class Page:
    """Renders the sources of one page; knows where every other generated page and record lives."""

    def __init__(self, spec, generated):
        self.spec = spec
        self.out = os.path.join(ROOT, spec["out"])
        self.out_dir = os.path.dirname(self.out)
        self.generated = generated     # normalised Markdown path -> its page's path
        self.decisions = spec.get("decisions", False)
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
            return hold(f'<a href="{html.escape(self.link(src, html.unescape(url)))}">{m.group(1)}</a>')
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", a, s)
        s = re.sub(r'(?<![="\w/>])(https?://[^\s<)\x00]*[^\s<).,;:\x00])',
                   lambda m: hold(f'<a href="{m.group(1)}">{m.group(1)}</a>'), s)
        page = self.to(DECISIONS_PAGE)
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

    @staticmethod
    def field(lines, name):
        """A record's value from its Field | Value table."""
        for ln in lines:
            m = re.match(rf"^\|\s*{name}\s*\|(.*)\|\s*$", ln)
            if m:
                return m.group(1).strip()
        return ""

    def render_decisions(self):
        intro = self.spec["intro"]
        src_intro = os.path.normpath(os.path.join(ROOT, intro))
        # The intro is the folder README without its title and its table: the index below replaces the table.
        lines = [x for x in self.read(intro) if not x.lstrip().startswith("|") and not is_title(x)]
        parts = [self.blocks(src_intro, lines)]
        rows, sections = [], []
        for rel in self.spec["sources"]:
            src = os.path.normpath(os.path.join(ROOT, rel))
            rid = record_id(rel)
            lines = self.read(rel)
            h1 = next((HEADING.match(x).group(2) for x in lines if is_title(x)), rid)
            title = h1.split(":", 1)[1].strip() if ":" in h1 else h1
            status, date = self.field(lines, "Status"), self.field(lines, "Date")
            short = re.split(r"\s*[(;]", status, maxsplit=1)[0].strip() or status
            self.used.add(rid)
            body = [x for x in lines if not is_title(x)]
            num = rid[-4:]
            rows.append(f'<tr><td class="num"><a href="#{rid}">{num}</a></td><td>{self.inline(src, title)}</td>'
                        f'<td>{self.inline(src, short)}</td><td class="num">{html.escape(date)}</td></tr>')
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
            body = self.blocks(src, [x for x in self.read(rel) if not is_title(x)])
            sources = f"<code>{html.escape(os.path.basename(rel))}</code>"
        toc = "\n".join(f'<li class="l{lvl}"><a href="#{aid}">{self.inline_plain(text)}</a></li>'
                        for lvl, aid, text in self.toc)
        with open(TEMPLATE, encoding="utf-8") as f:
            page = f.read()
        values = {
            "{{GENERATOR}}": "scripts/build_docs_html.py",
            "{{TITLE}}": html.escape(self.spec["title"]),
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
    return {s["out"]: Page(s, gen).render() for s in specs}


def main(argv):
    check = "--check" in argv
    stale = []
    for out, page in build_all().items():
        path = os.path.join(ROOT, out)
        if check:
            try:
                with open(path, encoding="utf-8") as f:
                    current = f.read()
            except FileNotFoundError:
                current = None
            if current != page:
                stale.append(out)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(page)
            print(f"wrote {out}")
    if stale:
        for s in stale:
            print(f"FAIL {s} differs from a fresh build of its Markdown: run python3 scripts/build_docs_html.py")
        return 1
    if check:
        print("ok  every generated page matches its Markdown")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
