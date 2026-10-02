#!/usr/bin/env python3
"""Regenerate the self-contained HTML reading copies from their Markdown sources.

The Markdown file is the maintenance source (see EPM-FOUND-000). Edit the Markdown,
then run this script from anywhere:

    python3 scripts/build_reading_copies.py

Standard library only. It reproduces the page template used by the existing
EPM_Foundation_v2_Markdown_HTML/*.html files. It handles the Markdown subset used in
these documents: headings, paragraphs, nested lists, tables, fenced code, block
quotes, images, links, bold, italics, and inline code.
"""
import html
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOUND = "EPM_Foundation_v2_Markdown_HTML"

CSS = """
:root{
  --bg:#f4f7fb; --paper:#ffffff; --ink:#182230; --muted:#5f6b7a;
  --navy:#17365d; --blue:#2368a2; --line:#dfe6ee; --soft:#eef4fa;
  --accent:#0f766e; --warn:#fff8e6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif;line-height:1.62}
.shell{display:grid;grid-template-columns:280px minmax(0,1fr);min-height:100vh}
aside{background:#102a43;color:#e8f1f8;padding:28px 22px;position:sticky;top:0;height:100vh;overflow:auto}
aside h2{font-size:18px;margin:0 0 6px}
aside p{color:#b9c9d8;font-size:13px}
aside a{display:block;color:#dbeafe;text-decoration:none;padding:8px 10px;border-radius:7px;margin:3px 0;font-size:14px}
aside a:hover{background:#1f4568}
main{padding:36px}
.article{max-width:1060px;margin:0 auto;background:var(--paper);padding:48px 58px;border-radius:16px;box-shadow:0 12px 35px rgba(16,42,67,.08)}
.eyebrow{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--blue);font-weight:700}
h1{color:var(--navy);font-size:38px;line-height:1.15;margin:8px 0}
.subtitle{font-size:18px;color:var(--muted);margin-bottom:28px}
.meta{font-size:13px;color:var(--muted);margin:0 0 6px}
h2{color:var(--navy);margin-top:38px;border-bottom:2px solid var(--soft);padding-bottom:8px}
h3{color:#204a75;margin-top:26px}
p,li{font-size:16px}
blockquote{margin:22px 0;padding:18px 22px;background:var(--soft);border-left:5px solid var(--blue);border-radius:8px}
blockquote p{margin:0 0 10px}
pre{background:#0f2233;color:#e8f1f8;padding:20px;border-radius:10px;overflow:auto;line-height:1.45}
code{font-family:SFMono-Regular,Consolas,monospace}
p code,li code,td code,blockquote code{background:var(--soft);padding:1px 5px;border-radius:4px;font-size:.92em}
img{max-width:100%;height:auto}
table{width:100%;border-collapse:collapse;margin:22px 0;font-size:14px}
th{background:#17365d;color:#fff;text-align:left;padding:10px}
td{border:1px solid var(--line);padding:10px;vertical-align:top}
tr:nth-child(even) td{background:#f8fafc}
.footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
@media(max-width:900px){.shell{display:block}aside{position:relative;height:auto}.article{padding:28px 22px;border-radius:0}main{padding:0}h1{font-size:31px}}
"""

HR = '<hr style="border-color:#31516e">'
FOUND_IDS = ["000", "001", "002", "003", "004", "005", "006"]


def foundation_target(n):
    # 000 is the root Master Index; 001 to 006 live beside this file.
    nav = [("EPM-FOUND-%s" % i, ("../EPM-FOUND-000.html" if i == "000" else "EPM-FOUND-%s.html" % i)) for i in FOUND_IDS]
    return {
        "md": "%s/EPM-FOUND-%s.md" % (FOUND, n),
        "aside_title": "EPM Foundation v2",
        "home": ("Foundation home", "index.html"),
        "nav": nav,
    }


TARGETS = [foundation_target(n) for n in FOUND_IDS[1:]] + [
    {
        "md": "EPM-FOUND-000.md",
        "aside_title": "EPM Master Index",
        "home": None,
        "nav": [("EPM-FOUND-%s" % i, "%s/EPM-FOUND-%s.html" % (FOUND, i)) for i in FOUND_IDS[1:]],
    }
]

GENERATED = {os.path.join(ROOT, t["md"][:-3] + ".html") for t in TARGETS}


def fix_link(href, md_dir):
    if re.match(r"^(https?:|mailto:|#)", href):
        return href
    path, sep, frag = href.partition("#")
    if path.endswith(".md"):
        target = os.path.normpath(os.path.join(md_dir, urllib.parse.unquote(path)))
        html_target = target[:-3] + ".html"
        if html_target in GENERATED or os.path.exists(html_target):
            return path[:-3] + ".html" + sep + frag
    return href


def inline(text, md_dir):
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)\)",
        lambda m: '<img alt="%s" src="%s">' % (html.escape(m.group(1)), m.group(2)),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: '<a href="%s">%s</a>' % (fix_link(m.group(2), md_dir), m.group(1)),
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(
        r"\x00(\d+)\x00",
        lambda m: "<code>%s</code>" % html.escape(codes[int(m.group(1))], quote=False),
        text,
    )
    return text


LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def is_special(line):
    return (
        line.startswith("```")
        or re.match(r"^#{1,4}\s", line)
        or re.match(r"^-{3,}\s*$", line)
        or line.startswith(">")
        or line.startswith("|")
        or LIST_RE.match(line)
    )


def parse_blocks(lines):
    blocks, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(buf)))
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            blocks.append(("h", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        if re.match(r"^-{3,}\s*$", line):
            blocks.append(("hr",))
            i += 1
            continue
        if line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            blocks.append(("quote", buf))
            continue
        if line.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].startswith("|"):
                buf.append(lines[i])
                i += 1
            blocks.append(("table", buf))
            continue
        if LIST_RE.match(line):
            buf = []
            while i < len(lines):
                cur = lines[i]
                if LIST_RE.match(cur):
                    buf.append(cur)
                    i += 1
                elif cur.strip() and cur.startswith((" ", "\t")):
                    buf.append(cur)
                    i += 1
                elif not cur.strip() and i + 1 < len(lines) and LIST_RE.match(lines[i + 1]):
                    i += 1
                else:
                    break
            blocks.append(("list", buf))
            continue
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not is_special(lines[i]):
            buf.append(lines[i])
            i += 1
        blocks.append(("p", buf))
    return blocks


def render_list(buf, md_dir):
    items = []
    for line in buf:
        m = LIST_RE.match(line)
        if m:
            items.append([len(m.group(1)), "ol" if m.group(2)[0].isdigit() else "ul", m.group(3)])
        else:
            items[-1][2] += " " + line.strip()
    out, stack = [], []
    for indent, tag, text in items:
        body = inline(text, md_dir)
        if not stack:
            out.append("<%s>\n<li>%s" % (tag, body))
            stack.append((indent, tag))
        elif indent > stack[-1][0]:
            out.append("\n<%s>\n<li>%s" % (tag, body))
            stack.append((indent, tag))
        else:
            while len(stack) > 1 and indent < stack[-1][0]:
                out.append("</li>\n</%s>" % stack.pop()[1])
            out.append("</li>\n<li>%s" % body)
    while stack:
        out.append("</li>\n</%s>" % stack.pop()[1])
    return "".join(out)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def render_table(buf, md_dir):
    rows = [split_row(r) for r in buf]
    head = rows[0]
    body = [r for r in rows[2:]] if len(rows) > 1 and re.match(r"^[\s:|-]+$", buf[1]) else rows[1:]
    width = len(head)
    out = ["<table><thead><tr>%s</tr></thead><tbody>" % "".join("<th>%s</th>" % inline(c, md_dir) for c in head)]
    for r in body:
        r = (r + [""] * width)[:width]
        out.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, md_dir) for c in r))
    out.append("</tbody></table>")
    return "\n".join(out)


def render_block(block, md_dir):
    kind = block[0]
    if kind == "code":
        return "<pre><code>%s</code></pre>" % html.escape(block[1], quote=False)
    if kind == "list":
        return render_list(block[1], md_dir)
    if kind == "table":
        return render_table(block[1], md_dir)
    if kind == "quote":
        paras, cur = [], []
        for line in block[1]:
            if line.strip():
                cur.append(line.strip())
            elif cur:
                paras.append(cur)
                cur = []
        if cur:
            paras.append(cur)
        inner = "\n".join("<p>%s</p>" % inline(" ".join(p), md_dir) for p in paras)
        return "<blockquote>%s</blockquote>" % inner
    if kind == "p":
        return "<p>%s</p>" % inline("\n".join(l.rstrip() for l in block[1]), md_dir)
    if kind == "h":
        return "<h%d>%s</h%d>" % (block[1], inline(block[2], md_dir), block[1])
    return ""


def slug(text, seen):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    base, n = s, 2
    while s in seen:
        s = "%s-%d" % (base, n)
        n += 1
    seen.add(s)
    return s


def build(target):
    md_path = os.path.join(ROOT, target["md"])
    md_dir = os.path.dirname(md_path)
    out_path = md_path[:-3] + ".html"
    with open(md_path, encoding="utf-8") as fh:
        blocks = parse_blocks(fh.read().splitlines())

    title = None
    meta = {}
    subtitle = ""
    body_blocks = []
    for idx, b in enumerate(blocks):
        if b[0] == "h" and b[1] == 1 and title is None:
            title = re.sub(r"^EPM-[A-Z0-9-]+\s+\W\s+", "", b[2])
            continue
        if b[0] == "p" and b[1][0].startswith("**Artifact ID:**"):
            for line in b[1]:
                m = re.match(r"^\*\*(.+?):\*\*\s*(.*?)\s*$", line)
                if m:
                    meta[m.group(1)] = m.group(2)
            continue
        if b[0] == "p" and b[1][0].startswith("**Foundation navigation:**"):
            continue
        if (
            not subtitle
            and b[0] == "p"
            and len(b[1]) == 1
            and re.match(r"^\*[^*].*[^*]\*$", b[1][0].strip())
            and not body_blocks
        ):
            subtitle = b[1][0].strip()[1:-1]
            continue
        if b[0] == "hr":
            continue
        if b[0] == "p" and b[1][0].startswith("*Part of the Enterprise Performance Model"):
            continue
        if b[0] == "p" and b[1][0].startswith("Part of the Enterprise Performance Model"):
            continue
        body_blocks.append(b)

    art_id = meta.get("Artifact ID", "")
    seen, anchors = set(), []
    parts, open_section = [], False
    for b in body_blocks:
        if b[0] == "h" and b[1] == 2:
            if open_section:
                parts.append("</section>")
            sid = slug(b[2], seen)
            anchors.append((sid, re.sub(r"[*`]", "", b[2])))
            parts.append('<section id="%s"><h2>%s</h2>' % (sid, inline(b[2], md_dir)))
            open_section = True
        else:
            parts.append(render_block(b, md_dir))
    if open_section:
        parts.append("</section>")

    aside = ["<h2>%s</h2><p>%s</p>" % (target["aside_title"], html.escape(art_id))]
    if target["home"]:
        aside.append('<a href="%s">%s</a>' % (target["home"][1], target["home"][0]))
        aside.append(HR)
    aside.append(" ".join('<a href="%s">%s</a>' % (href, label) for label, href in target["nav"]))
    aside.append(HR)
    aside.extend('<a href="#%s">%s</a>' % (sid, html.escape(label, quote=False)) for sid, label in anchors)

    extra = [
        "%s: %s" % (k, v)
        for k, v in meta.items()
        if k not in ("Artifact ID", "Version")
    ]
    meta_html = ""
    if extra:
        meta_html = '<div class="meta">%s</div>\n' % html.escape(" \u00b7 ".join(extra).replace("`", ""), quote=False)

    footer = "Enterprise Performance Model Foundation \u00b7 %s \u00b7 Updated %s" % (
        meta.get("Status", ""),
        meta.get("Last updated", ""),
    )

    doc = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        "<title>%s \u2014 %s</title><style>%s</style></head>\n"
        '<body><div class="shell"><aside>\n%s\n</aside><main><article class="article">\n'
        '<div class="eyebrow">%s \u00b7 Version %s</div>\n<h1>%s</h1>\n'
        '<div class="subtitle">%s</div>\n%s%s\n'
        '<div class="footer">%s</div>\n</article></main></div></body></html>\n'
    ) % (
        html.escape(art_id),
        html.escape(title or "", quote=False),
        CSS,
        "\n".join(aside),
        html.escape(art_id),
        html.escape(meta.get("Version", ""), quote=False),
        html.escape(title or "", quote=False),
        inline(subtitle, md_dir),
        meta_html,
        "\n".join(parts),
        html.escape(footer, quote=False),
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return os.path.relpath(out_path, ROOT)


def main():
    for target in TARGETS:
        print("wrote", build(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
