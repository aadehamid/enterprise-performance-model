#!/usr/bin/env python3
"""The leak gate: fail on any name, handle, repository, host, peer, record number or issue number in the
release, and on the graph's double-underscore separator (plan step 5; EPM-DEC-001-0110 and its amendment).

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

# Each pattern with its reason. The owner's names and handle come from owner.py's configuration, never from this file.
# A name matches as a whole word only ("Ada" is a hit; "Adam", "metadata" and "adapt" are not); a handle may hold
# punctuation, so the boundary is "no letter, digit or underscore on either side" rather than \b.
OWNER = r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(n) for n in _owner.owner_names()) + r")(?![A-Za-z0-9_])"
PEERS = r"valero|phillips\s?66|\bpbf\b|hf\s?sinclair|hollyfrontier|par\s+pacific|\bdelek\b|\bcvr\b|chevron|exxon"
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
    ("a document the release leaves out", re.compile(r"LOCAL-STORES\.(?:md|html)|STORE-INVENTORY\.(?:md|html)|business_architecture/ontology/lpg-projection|\.\./lpg-projection/|`lpg-projection/`|\(lpg-projection/")),
    ("an issue or pull request number", re.compile(r"\b(?:PRs?|pull requests?|issues?)\s+#\d+|(?<![&\w-])#\d{3}\b(?![\da-fA-F])")),
    ("the graph's double-underscore separator", re.compile(r"\b[a-z][a-z0-9]*__[A-Za-z]")),
    ("the namespace note is missing", None),  # checked once, below
]
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
# A data: URL (RFC 2397, "The 'data' URL scheme", August 1998, read 2026-11-01): an optional media type with
# parameters, an optional ";base64" in any case, a comma, the payload. A base64 payload may be wrapped over lines
# (line breaks only; a space ends it).
DATA_URL = re.compile(r"data:((?:[^,;\"'\s<>()]*)(?:;[^,;\"'\s<>()]*)*;base64),([A-Za-z0-9+/=\r\n]*)|data:([^,\"'\s<>()]*),([^\"'\s<>()]*)", re.I)
CSS_COLOUR = re.compile(r"(?<=[:\s(,])#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b(?=[;\s)}\],!\"'])")
STYLE_SPAN = re.compile(r"<style\b[^>]*>.*?</style>|\bstyle\s*=\s*\"[^\"]*\"|\bstyle\s*=\s*'[^']*'", re.S | re.I)
PRINTABLE_RUN = re.compile(rb"[\x20-\x7e\t]{6,}")
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
    """Decoded bytes as the text to scan: the whole text when it is text (UTF-8 without a NUL), else its printable
    runs. A short payload ("CVR") is text in full, never lost to the run length."""
    if b"\0" not in raw:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            pass
    return strings_of(raw)


def decoded_data_urls(text):
    """Each data: URL in a page, decoded: (label suffix, text) for a payload read, or a problem when it cannot be.
    Every base64 payload that is valid base64 is decoded, whatever its length ("Q1ZS" is "CVR"), with missing
    padding supplied as a browser does; a payload that is base64-shaped but does not decode fails the file; a
    payload that is not base64-shaped at all (a code template's "{b64}") is read as the text it is, since the scan of
    the file's text covers it."""
    for i, m in enumerate(DATA_URL.finditer(text), 1):
        if m.group(1) is not None:
            payload = re.sub(r"\s", "", m.group(2))
            if not BASE64_SHAPED.match(payload):
                yield f"data URI {i}", payload
                continue
            try:
                raw = base64.b64decode(payload.rstrip("=") + "=" * (-len(payload.rstrip("=")) % 4), validate=True)
            except (binascii.Error, ValueError):
                yield f"{PROBLEM}a data URI's base64 payload could not be decoded", f"data URI {i}"
                continue
            yield f"data URI {i}", readable(raw)
        else:
            yield f"data URI {i}", urllib.parse.unquote(m.group(4))


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
        if ext in (".html", ".css", ".svg", ".md"):
            text = mask_colours(text, ext)
        for label, decoded in decoded_data_urls(text):
            yield (label, decoded) if label.startswith(PROBLEM) else (f"{path} ({label}) (binary)", decoded)
        yield path, DATA_URL.sub("data:removed", text)
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


def scan(release):
    hits = []
    note_found = False
    for root, dirs, files in os.walk(release):
        # A virtual environment or a cache inside the tree is a validation artefact, never a shipped file (publish.py
        # leaves them out of the zip and the branch).
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__", ".pytest_cache", ".venv"))
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
                    for m in pattern.finditer(text):
                        if reason.startswith("the graph's") and allowed_double(rel, text, m):
                            continue
                        line = text.count("\n", 0, m.start()) + 1
                        shown = re.sub(r"( \([^()]*\))? \(binary\)$", "", label)
                        hits.append({"file": os.path.relpath(shown, release) if shown.startswith(release) else shown,
                                     "line": line, "reason": reason, "match": m.group(0)[:60]})
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
