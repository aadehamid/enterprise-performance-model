#!/usr/bin/env python3
"""The leak gate: fail on any name, handle, repository, host, peer, record number or issue number in the
release, on a statement that the build kept something out of the repository, and on the graph's double-underscore
separator (plan step 5; EPM-DEC-001-0110 and its amendment).
A peer named in market news (vocabulary.MARKET_NEWS: the demo's cached Parallel search results and SCENARIO.md)
is not a failure in the file's text (EPM-DEC-001-0112, point 7); a file name that names a peer still fails, every other
check still runs on those files, and a peer anywhere else fails.

    python3 scripts/share_release/gate.py <release folder> [--json]

It reads every file: text files as text; XLSX, DOCX and PPTX as the XML inside them, their other parts as
binaries; a PDF as its raw bytes plus every FlateDecode stream inflated (the text operators and metadata are in
them), failing on a stream it cannot read; other binaries as the runs of printable text inside them (what
`strings` shows), so a name in a PDF's metadata or an image's comment is found. Data in a page (data: URIs, base64
or percent-encoded) is decoded and scanned the same way, and a payload that cannot be decoded is a failure.
Exit 1 with one line per hit. The leak vocabulary it shares with the rewrite rules is in vocabulary.py.
"""
import argparse
import base64
import binascii
import html
import json
import os
import re
import sys
import urllib.parse
import zipfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import owner as _owner  # noqa: E402
import vocabulary as V  # noqa: E402

# Agents and review tools the build used, and the words for what they did (the decision's amendment of 2026-11-01).
# "Delegation" stays where it is a business term: the delegation of authority, the documented delegation.
# The boundary is "no letter or digit", not \b, because an underscore is a word character: test_bugbot_380 must fail.
AGENT_NAMES = (r"(?<![A-Za-z0-9])(?:claude|codex|bugbot|kimi|anthropic|chatgpt|herdr|openai|copilot|gemini|gpt[-_ ]\d[\w.-]*|pi[-_ ]review|rex[-_ ]review)(?![A-Za-z0-9])"
               r"|\bAGENTS\.md\b|\bPi,? round\b|\bPi review")
AGENT_WORK = (r"\bretro of \d{4}|\bnight[ _]brief\b|\b[Ii]ndependent review|\b[Rr]eview rounds?\b|\b[Rr]ound \d+,? (?:on|finding)|\(findings? \d+|\bPR verdict|\bapproval agent\b"
              r"|\b[Uu]nder the delegation\b(?! of\b)|\b[Uu]nder their (?:recorded )?delegation\b|\b(?:expert|owner)'s delegation\b"
              r"|\b[Dd]elegated under\b|\bdelegate as described\b|\bcoding agents?\b|(?<![A-Za-z0-9])(?i:kailey)(?![A-Za-z0-9])")
# What the build kept out of the repository: the release never says it (the decision owner's request of 2026-11-03,
# rule 17 of rules.py). It may say that an input is read from a folder outside the repository, and how to keep that
# pattern or move the files into the copy (the decision owner's refinement, the same day). KEPT_OUT is the withholding
# wording: kept out of the repository or main, staying, held or living outside it, not in the repository, a gitignored
# folder of ours, files kept apart from these sources, this run's files in no repository, and the same claim as what
# main lacks. The shipped skills are exempt from it, since their method text is generic (the decision owner, the same day). KEPT_OUT_CUSTOMER, the customer's
# files, inputs, data or model kept out, gitignored or in the augment folder, runs on every file, the skills included.
KEPT_OUT = (r"\bkept\s+(?:out\s+of|outside)\s+(?:the\s+|this\s+)?(?:repo|repository|(?:`|<code>)?main)\b"
            r"|\b(?:stays?|stayed|remains?|held|lives?)\s+(?:out\s+of|outside)\s+(?:the\s+|this\s+)?(?:repo|repository|(?:`|<code>)?main)\b"
            r"|\bnot\s+in\s+(?:this|the)\s+repository\b|\bgitignored\s+(?:folder|augment)"
            r"|\b(?:kept\s+(?:apart\s+from|outside)|from\s+outside)\s+(?:these|those)\s+sources\b"
            r"|\bdo\s+not\s+live\s+in\s+either\s+repository\b|\bOutside\s+the\s+repositories\b"
            # The same claim as where the logical model is not: never entering main, not released or no package in main,
            # main holding none, only in the release. The release is the reader's copy, and main is not theirs.
            r"|\b(?:never|not|ever)\s+enters?\s+(?:<code>|`)?main\b|\bnot\s+(?:released\s+)?in\s+(?:<code>|`)main\b"
            r"|\bnot\s+released\s+in\s+main\b|\bno\s+package\s+in\s+(?:<code>|`)?main\b"
            r"|\bmain(?:</code>|`)?\s+(?:has|holds)\s+no\s+(?:such\s+)?(?:package|module|logical-model)"
            r"|\bships\s+only\s+in\s+the\s+release\b|\bwants\s+only\s+in\s+the\s+release\b|\bonly\s+the\s+release\s+(?:may\s+)?holds?\b"
            r"|\bIn\s+(?:<code>|`)?main(?:</code>|`)?,?\s+(?:it|the\s+command)\s+(?:has\s+no|loads\s+nothing|says\s+there\s+is\s+nothing)"
            r"|\(never\s+in\s+(?:<code>|`)?main\b"
            r"|\bunreleased\s+in\s+(?:<code>|`)?main\b|\bmain(?:</code>|`)?\s+holds\s+none\b|\bnone\s+in\s+(?:<code>|`)?main\b"
            r"|\bmain:\s+no\s+package\b|,\s+as\s+in\s+(?:<code>|`)?main\b"
            r"|;\s+main(?:</code>|`)?\s+does\s+not\)|\bIn\s+(?:<code>|`)?main(?:</code>|`)?\s+there\s+is\s+no\b")
KEPT_OUT_CUSTOMER = (r"\b(?:the|expert's|owner's)\s+customer\s+(?:files|inputs|data|logical\s+model|model)\b[^.\n]{0,80}?"
                     r"(?:\b(?:out\s+of|outside|not\s+in|never\s+enters?)\s+(?:the\s+|this\s+)?(?:repo|repository|(?:`|<code>)?main)\b"
                     r"|gitignored|augment\s+folder)")
# The three peer checks, whose text scan market news (vocabulary.MARKET_NEWS) is exempt from; a file's name is still checked.
PEER_REASONS = ("a peer named", "a peer's ticker", "a peer's filing on EDGAR")
# Each pattern with its reason. The owner's names and handle come from owner.py's configuration, never from this file.
# A name matches when no letter or digit touches it ("Ada" and "by_Ada_here" are hits; "Adam", "metadata" and "adapt"
# are not). A handle may hold punctuation, and \b treats an underscore as a word character, so \b will not do.
OWNER = r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(n) for n in _owner.owner_names()) + r")(?![A-Za-z0-9])"
PEERS = (r"valero|phillips[-_\s]?66|\bphillips\b|(?<![A-Za-z0-9])pbf(?![A-Za-z0-9])|hf\s?sinclair|hollyfrontier|par\s+pacific"
         r"|(?<![A-Za-z0-9])delek(?![A-Za-z0-9])|(?<![A-Za-z0-9])cvr(?![A-Za-z0-9])|chevron|exxon")
TICK = "|".join(V.PEER_TICKERS)
LIST_TICK = TICK + "|" + "|".join(V.OWN_TICKERS)
SEP = r"(?:,\s*|/|\s+and\s+|\s+or\s+)"
# The peers' tickers are upper case; DK (Delek) counts in parentheses or beside another ticker, MPC and MPLX included.
TICKERS = rf"\b(?:{TICK})\b|\(DK\)|\bDK(?={SEP}(?:{LIST_TICK})\b)|\b(?:{LIST_TICK}){SEP}DK\b"
PATTERNS = [
    ("the owner's name or handle", re.compile(OWNER, re.I)),
    ("this account's repositories", re.compile("|".join(("enterprise-performance-model", "personal-agent-skills", *V.OTHER_REPOS)), re.I)),
    ("a decision record number", re.compile(r"EPM-DEC-001")),
    ("a decision record's short number", re.compile(r"the decisions? of \d{4}-\d{2}-\d{2}(?:, | and | or | to |; )0\d{3}\b|\(0\d{3}\)|\b(?:amending|amended by|amends|supersedes|superseded by) 0\d{3}\b")),
    ("the saved answers folder", re.compile(r"decision-owner-answers|answers-20\d\d-\d\d-\d\d")),
    ("the old IRI base or company name", re.compile(r"w3id\\*\.org/lsc|\bLSC\b|Lagos Specialty", re.I)),
    ("a host of the build", re.compile(r"exe\.dev|exe\.xyz|spacesheep\.dev|app\.eraser\.io", re.I)),
    ("a path on the owner's machine", re.compile(r"(?<!/Workspace)/Users/|Dropbox|~/\.claude/handoffs|~/\.claude/plugins|~/\.agents/skills")),
    ("a peer named", re.compile(PEERS, re.I)),
    ("a peer's ticker", re.compile(TICKERS)),
    # A filer's CIK may be written with leading zeroes (EDGAR accepts both); the list is vocabulary.PEER_CIKS, cited there.
    ("a peer's filing on EDGAR", re.compile(r"sec\.gov/Archives/edgar/data/0*(?:" + "|".join(V.PEER_CIKS) + r")/|edgar/data/\d+/\S*/(?:" + "|".join(V.PEER_SLUGS) + r")-\d{8}\.", re.I)),
    ("a document the release leaves out", re.compile(r"LOCAL-STORES\.(?:md|html)|STORE-INVENTORY\.(?:md|html)|ontology-worklog|pr-reviews-262-266-269|business_architecture/ontology/lpg-projection|\.\./lpg-projection/|`lpg-projection/`|\(lpg-projection/")),
    # An issue's number also hides in an IRI that names an issue comment (the rules keep the comment, urn:epm:comment:N).
    ("an issue or pull request number", re.compile(r"\b(?:PRs?|pull requests?|issues?)\s+#\d+|(?<![&\w-])#\d{3}\b(?![\da-fA-F])|urn:epm:(?:issue|pull):\d")),
    ("a skill the release leaves out", re.compile(r"way-of-working")),
    ("something kept out of the repository", re.compile(KEPT_OUT, re.I)),
    ("something kept out of the repository", re.compile(KEPT_OUT_CUSTOMER, re.I)),
    ("the graph's double-underscore separator", re.compile(r"\b[a-z][a-z0-9]*__[A-Za-z]")),
    ("an agent or review tool named", re.compile(AGENT_NAMES, re.I)),
    ("the agent called Cursor", re.compile(r"\bCursor\b|\bcursor/|/cursor\b|(?<![A-Za-z0-9])cursor[-_]agent(?![A-Za-z0-9])|\.cursor/")),
    ("a pull request of the build", re.compile(r"\bPRs\b|(?<!\.\d )(?<!\()\bPR\b(?! campaigns?\b| program\b| all\b|\)| strategy\b)|\b[Pp]ull requests?\b")),
    ("the work of an agent", re.compile(AGENT_WORK)),
    ("the agent, in a decision package", re.compile(r"\b[Tt]he agent\b")),
    ("the namespace note is missing", None),  # checked once, below
]
# The method's own words on delegation and on a remote's pull requests, in the skills that teach any project: the skill
# says what to do when a team delegates or uses pull requests, and names nothing of this build.
METHOD_FILES = re.compile(r"^skills/")
# In a binary's printable runs, the graph pattern needs a known prefix: random bytes form "h4i__z" by chance,
# never "skos__Concept".
GRAPH_IN_BINARY = re.compile(r"\b(?:" + "|".join(V.GRAPH_PREFIXES) + r")__[A-Za-z]")
# Third-party syntax that carries two underscores and is not a graph name (the owner's rule names the graph's separator):
# applied to the whole word around a match, never to a neighbour.
ALLOWED_DOUBLE = re.compile(r"metric_time__day|__init__|__main__|__pycache__|__file__|__name__|__doc__")
WORD = re.compile(r"[A-Za-z0-9_]+")
# The ontology-to-lpg skill's own tests, and the projection pipeline's test of the names it renames, describe what
# n10s writes before the rename step (lib__Work, my__node, n4sch__Entity, skos__Concept): a third-party tool's format
# on fixture names, not a name in any graph, query, document or page of the release (the night log of 2026-11-01,
# 00:45). The exemption covers those files only and only the closed list vocabulary.FIXTURE_PREFIXES, so a planted
# vs__Stage, core__Process or prov__since fails there too.
FIXTURE_FILES = re.compile(r"^(?:skills/ontology-to-lpg/scripts/test_[^/]+|business_architecture/ontology/projection/test_pipeline)\.py$")
TEXT_EXT = {".md", ".html", ".ttl", ".jsonld", ".json", ".csv", ".py", ".rq", ".sql", ".sh", ".yml", ".yaml", ".txt",
            ".nt", ".toml", ".example", ".cypher", ".jsonl", ".css", ".svg", ".cfg", ".ini", ".lock"}
OFFICE_EXT = {".xlsx", ".docx", ".pptx"}
# A data: URL: dataurl := "data:" [ mediatype ] [ ";base64" ] "," data, where ";base64" means the data is base64
# and otherwise octets outside the safe URL characters use "the standard %xx hex encoding of URLs" (RFC 2397, "The
# 'data' URL scheme", August 1998, section 3, read 2026-11-01). The URL runs to what delimits it where it stands: the
# quote that opened it, the ")" of a Markdown link, else the next whitespace, "<" or ">"; inside that run a "#"
# starts a fragment and ends the URL, and a base64 payload ends at the first character that is not base64, "=", "%"
# or whitespace (a Markdown link's title, for example). Before base64 decoding, "%XX" is percent-decoded (WHATWG URL
# Standard, section 1.3 "Percent-encoded bytes", "percent-decode", Living Standard as of 19 October 2026, read
# 2026-11-01) and ASCII whitespace is removed, as the forgiving-base64 decode a browser uses does (WHATWG Infra
# Standard, "forgiving-base64 decode", Living Standard as of 19 October 2026, read 2026-11-01: "Remove all ASCII
# whitespace from data").
DATA_URL = re.compile(r"(?P<open>[\"'(]?)data:(?P<head>[^,\"'\s<>()]*),", re.I)
CSS_COLOUR = re.compile(r"(?<=[:\s(,])#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b(?=[;\s)}\],!\"'])")
STYLE_SPAN = re.compile(r"<style\b[^>]*>.*?</style>|\bstyle\s*=\s*\"[^\"]*\"|\bstyle\s*=\s*'[^']*'", re.S | re.I)
PRINTABLE_RUN = re.compile(rb"[\x20-\x7e\t]{6,}")
# In a decoded binary payload a short string between NULs ("\0CVR\0", a C string) counts from three characters; a
# three-letter run with arbitrary bytes around it is what an image's bytes form by chance, so it does not.
NUL_STRING = re.compile(rb"(?:^|\x00)([\x20-\x7e\t]{3,5})(?=\x00|$)")
DATA_URL_DEPTH = 4  # a decoded payload is itself scanned for data: URLs, this many layers down
PDF_STREAM = re.compile(rb"stream(?:\r\n|\r|\n)(.*?)(?:\r\n|\r|\n)endstream", re.S)  # a stream ends with CR, LF or CRLF (PDF 32000-1:2008, 7.3.8)
INFLATE_CAP = 64 * 1024 * 1024  # bytes one stream or one Office part may inflate to; past it the file fails rather than exhaust memory
PDF_IMAGE_FILTERS = (b"/DCTDecode", b"/JPXDecode", b"/CCITTFaxDecode", b"/JBIG2Decode")
NAMESPACE_NOTE = "Data, Analytics and Insight"
PROBLEM = "PROBLEM:"  # a label prefix: the text could not be read, which is itself a failure


def strings_of(data):
    """The runs of printable text inside bytes (what `strings` prints), one per line: words in a PDF's metadata, an
    image's comment or a binary's strings are scanned; random bytes between them are not."""
    return "\n".join(m.group(0).decode("ascii") for m in PRINTABLE_RUN.finditer(data))


def mask_colours(text, ext):
    """CSS colours (#fff, #111, #1a2b3c) are not issue numbers: masked inside <style> blocks and style attributes of a
    page, and everywhere in a stylesheet; prose such as "Issue: #455" is left for the number pattern."""
    if ext in (".css",):
        return CSS_COLOUR.sub("#colour", text)
    return STYLE_SPAN.sub(lambda m: CSS_COLOUR.sub("#colour", m.group(0)), text)


BASE64_SHAPED = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")


def readable(raw):
    """A decoded payload as the text to scan: the whole text when it is mostly printable (UTF-8, nine in ten
    characters printable), else its printable runs of three characters or more, so a short name between NULs
    ("\0CVR\0") is not lost to the run length a binary file gets."""
    try:
        text = raw.decode("utf-8")
        if text and sum(c.isprintable() or c in "\n\r\t" for c in text) >= 0.9 * len(text):
            return text
    except UnicodeDecodeError:
        pass
    short = [m.group(1).decode("ascii") for m in NUL_STRING.finditer(raw)]
    return "\n".join([strings_of(raw)] + short).strip("\n")


def data_urls(text):
    """Each data: URL in the text: (start, end, head, payload), the payload read to the URL's own delimiter."""
    for m in DATA_URL.finditer(text):
        opener = m.group("open")
        closer = {'"': '"', "'": "'", "(": ")"}.get(opener)
        start = m.end()
        if closer:
            end = text.find(closer, start)
            end = len(text) if end < 0 else end
        else:
            n = re.search(r"[\s<>]", text[start:])
            end = start + n.start() if n else len(text)
        payload = text[start:end].split("#", 1)[0]  # a fragment is not part of the URL's data
        if re.search(r"(?:^|;)base64$", m.group("head"), re.I):
            payload = re.match(r"[A-Za-z0-9+/=%\s]*", payload).group(0)  # the payload ends where the base64 alphabet does
        yield m.start() + len(opener), start + len(payload), m.group("head"), payload  # the opener stays in the text


def decoded_data_urls(text, depth=1, prefix=""):
    """Each data: URL in a page, decoded: (label suffix, text) for a payload read, or a problem when it cannot be.
    A base64 payload is read to its delimiter, its whitespace stripped and percent-encoding decoded (the WHATWG URL
    and Infra Standards cited at DATA_URL), then decoded whatever its length ("Q1ZS" is "CVR"), with missing padding
    supplied (forgiving-base64 decode removes one or two trailing "=" and fails only on a length that leaves a
    remainder of 1 when divided by 4; Infra Standard, same section and date); a payload that is
    base64-shaped but does not decode fails the file; a payload that is not base64-shaped at all (a code template's
    "{b64}") is read as the text it is, since the scan of the file's text covers it. A decoded payload is itself a
    document (an iframe's HTML holding another data: URL), so it is unescaped and scanned the same way, down to
    DATA_URL_DEPTH layers."""
    for i, (start, end, head, payload) in enumerate(data_urls(text), 1):
        label = f"{prefix}data URI {i}"
        if re.search(r"(?:^|;)base64$", head, re.I):
            payload = re.sub(r"\s", "", urllib.parse.unquote(payload))
            if not BASE64_SHAPED.match(payload):
                decoded = payload  # not base64 at all (a template's "{b64}", or text): read through the same path as every payload
            else:
                decoded = None
            if decoded is None:
                try:
                    raw = base64.b64decode(payload.rstrip("=") + "=" * (-len(payload.rstrip("=")) % 4), validate=True)
                except (binascii.Error, ValueError):
                    yield f"{PROBLEM}a data URI's base64 payload could not be decoded", label
                    continue
                decoded = readable(raw)
        else:
            decoded = urllib.parse.unquote(payload)
        inner = html.unescape(decoded)  # a payload is a document too: its character references are decoded before it is read (the HTML Standard sections cited in texts())
        yield label, inner
        if depth < DATA_URL_DEPTH and "data:" in inner.lower():
            yield from decoded_data_urls(inner, depth + 1, label + " > ")


def without_data_urls(text):
    """The text with each data: URL's payload removed, so the encoded form is not scanned as prose."""
    out, pos = [], 0
    for start, end, head, payload in data_urls(text):
        out.append(text[pos:start]); out.append("data:removed"); pos = end
    out.append(text[pos:])
    return "".join(out)


def inflate(data, cap=None):
    """zlib-inflate data up to cap bytes; past the cap it raises zlib.error, so a small hostile stream cannot exhaust memory."""
    d = zlib.decompressobj()
    out = d.decompress(data, cap or INFLATE_CAP)
    if d.unconsumed_tail:
        raise zlib.error(f"inflates past {cap or INFLATE_CAP} bytes")
    return out


def pdf_texts(data):
    """A PDF's readable text: its raw printable runs (the metadata dictionaries), and every FlateDecode stream
    inflated. A stream with a filter this gate cannot inflate, other than an image's, is a problem. A stream's
    dictionary is everything from its object's "obj" keyword to "stream", however long."""
    yield "pdf", strings_of(data)
    for i, m in enumerate(PDF_STREAM.finditer(data), 1):
        obj = data.rfind(b" obj", 0, m.start())
        dictionary = data[obj if obj >= 0 else 0:m.start()]
        if b"/FlateDecode" in dictionary:
            try:
                yield f"pdf stream {i}", strings_of(inflate(m.group(1)))
            except zlib.error as exc:
                yield f"{PROBLEM}a PDF stream could not be inflated", f"pdf stream {i}: {exc}"
        elif any(f in dictionary for f in PDF_IMAGE_FILTERS):
            continue
        elif b"/Filter" in dictionary:
            yield f"{PROBLEM}a PDF stream uses a filter the gate cannot read", f"pdf stream {i}"
        else:
            yield f"pdf stream {i}", strings_of(m.group(1))


def texts(path):
    """(label, text) pairs to scan for one file; a label starting with PROBLEM: is a failure to read."""
    ext = os.path.splitext(path)[1].lower()
    if ext in OFFICE_EXT:
        try:
            with zipfile.ZipFile(path) as z:
                for info in z.infolist():
                    name = info.filename
                    if info.file_size > INFLATE_CAP:
                        yield f"{PROBLEM}an Office part inflates past the cap", f"{name}: {info.file_size} bytes"
                        continue
                    if name.endswith((".xml", ".rels", ".txt")):
                        yield f"{path}:{name}", z.read(name).decode("utf-8", "replace")
                    elif not name.endswith("/"):
                        yield f"{path}:{name} (binary)", strings_of(z.read(name))
        except zipfile.BadZipFile:
            with open(path, "rb") as f:
                yield path + " (binary)", strings_of(f.read())
        return
    with open(path, "rb") as f:
        data = f.read()
    if ext == ".pdf" or data.startswith(b"%PDF"):
        for label, text in pdf_texts(data):
            yield (label, text) if label.startswith(PROBLEM) else (f"{path} ({label}) (binary)", text)
        return
    if ext in TEXT_EXT or b"\0" not in data[:4096]:
        text = data.decode("utf-8", "replace")
        if ext in (".html", ".md", ".svg"):
            # The tokenizer decodes a character reference in an attribute value before the value is used ("&#44;" is ","):
            # WHATWG HTML Standard, sections 13.2.5.77 "Character reference state", 13.2.5.78 "Named character reference
            # state", 13.2.5.80 "Numeric character reference state" and 13.2.5.84 "Numeric character reference end state",
            # Living Standard as of 30 October 2026, read 2026-11-01. So the gate decodes them before it looks for a URL.
            text = html.unescape(text)
        if ext in (".html", ".css", ".svg", ".md"):
            text = mask_colours(text, ext)
        for label, decoded in decoded_data_urls(text):
            yield (label, decoded) if label.startswith(PROBLEM) else (f"{path} ({label}) (binary)", decoded)
        yield path, without_data_urls(text)
    else:
        yield path + " (binary)", strings_of(data)


def allowed_double(rel, text, m):
    """A double underscore that is not the graph's separator: language syntax in the matched word itself, or a
    fixture prefix in the n10s fixture files."""
    start = m.start()
    while start > 0 and WORD.match(text[start - 1]):
        start -= 1
    word = WORD.match(text, start).group(0)
    if ALLOWED_DOUBLE.fullmatch(word):  # the whole word, so core__Process__init__ is not excused by its tail
        return True
    return bool(FIXTURE_FILES.match(rel)) and m.group(0).split("__", 1)[0] in V.FIXTURE_PREFIXES


def code_cursor(rel, text, m):
    """A database cursor's test double in Python: `class Cursor` or a call `Cursor(`. Lower-case `cursor` in code and the
    CSS property `cursor:` never match the pattern; every other capital Cursor is the agent."""
    return rel.endswith(".py") and m.group(0) == "Cursor" and (text[max(0, m.start() - 6):m.start()] == "class " or text[m.end():m.end() + 1] == "(")


SKIP_DIRS = (".git", "__pycache__", ".pytest_cache", ".venv", "out")  # publish.SKIP_DIRS; a test keeps them equal


def scan(release):
    hits = []
    note_found = False
    for root, dirs, files in os.walk(release):
        # A virtual environment, a cache or a run's out/ folder inside the tree is a validation artefact, never a
        # shipped file: the gate skips exactly the folders publish.py leaves out of the zip and the branch.
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            path = os.path.join(root, f)
            rel = os.path.relpath(path, release)
            for reason, pattern in PATTERNS:
                if pattern and pattern.search(rel):
                    hits.append({"file": rel, "reason": reason, "where": "the path"})
            for label, text in texts(path):
                if label.startswith(PROBLEM):
                    hits.append({"file": rel, "reason": label[len(PROBLEM):], "match": text})
                    continue
                if NAMESPACE_NOTE in text and rel == "README.md":
                    note_found = True
                binary = label.endswith(" (binary)")
                for reason, pattern in PATTERNS:
                    if pattern is None:
                        continue
                    if binary and reason.startswith("the graph's"):
                        pattern = GRAPH_IN_BINARY
                    if binary and reason == "a pull request of the build":
                        continue  # two capital letters in a binary's bytes are chance
                    if reason in PEER_REASONS and V.MARKET_NEWS.match(rel):
                        continue  # market news keeps its peer names (EPM-DEC-001-0112, point 7)
                    for m in pattern.finditer(text):
                        if reason.startswith("the graph's") and allowed_double(rel, text, m):
                            continue
                        if reason == "the agent, in a decision package" and "decision-packages/" not in rel:
                            continue
                        if reason == "the agent called Cursor" and code_cursor(rel, text, m):
                            continue
                        if reason == "something kept out of the repository" and pattern.pattern == KEPT_OUT and METHOD_FILES.match(rel):
                            continue  # the skills' generic method text; KEPT_OUT_CUSTOMER still runs on them
                        if reason == "a pull request of the build" and METHOD_FILES.match(rel):
                            continue
                        if reason == "the work of an agent" and METHOD_FILES.match(rel) and "delegated under" in m.group(0).lower():
                            continue
                        line = text.count("\n", 0, m.start()) + 1
                        shown = re.sub(r"( \([^()]*(?:\([^()]*\)[^()]*)*\))? \(binary\)$", "", label)
                        hit = {"file": os.path.relpath(shown, release) if shown.startswith(release) else shown,
                               "line": line, "reason": reason, "match": m.group(0)[:60]}
                        if shown != label:
                            hit["where"] = label[len(shown) + 1:]  # which decoded payload or stream of the file
                        hits.append(hit)
                        if sum(1 for h in hits if h["file"] == rel and h["reason"] == reason) >= 5:
                            break
    if not note_found:
        hits.append({"file": "README.md", "reason": "the namespace note is missing",
                     "match": f"the README must say the namespaces will be reviewed and approved by the {NAMESPACE_NOTE} team"})
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("release")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    hits = scan(os.path.abspath(a.release))
    if a.json:
        print(json.dumps(hits, indent=1))
    else:
        for h in hits:
            print(f"{h['file']}:{h.get('line', '-')}: {h['reason']}: {h.get('match', h.get('where', ''))}")
        print(f"{len(hits)} leak(s)" if hits else "no leaks")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
