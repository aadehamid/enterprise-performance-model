#!/usr/bin/env python3
"""The leak gate: fail on any name, handle, repository, host, peer, record number or issue number in the
release, and on the graph's double-underscore separator (plan step 5; EPM-DEC-001-0110 and its amendment).

    python3 scripts/share_release/gate.py <release folder> [--json]

It reads every file: text files as text; XLSX, DOCX and PPTX as the XML inside them, their other parts as
binaries; PDFs and other binaries as the runs of printable text inside them (what `strings` shows), so a name
in a PDF's metadata or an image's comment is found and random bytes are not read as words. Base64 data inside
a page (data: URIs) is decoded and scanned the same way. Exit 1 with one line per hit.
"""
import argparse
import base64
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import owner as _owner  # noqa: E402

# Each pattern with its reason. The owner's names and handle come from owner.py's configuration, never from this file.
# A name matches as a whole word only ("Ada" is a hit; "Adam", "metadata" and "adapt" are not); a handle may hold
# punctuation, so the boundary is "no letter, digit or underscore on either side" rather than \b.
OWNER = r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(n) for n in _owner.owner_names()) + r")(?![A-Za-z0-9_])"
PEERS = r"valero|phillips\s?66|\bpbf\b|hf\s?sinclair|hollyfrontier|par\s+pacific|\bdelek\b|\bcvr\b|chevron|exxon"
# The peers' tickers are upper case; DK (Delek) counts only beside another ticker or in parentheses.
TICKERS = r"\b(?:VLO|PSX|PBF|DINO|PARR|CVI|CVX|XOM)\b|\(DK\)|\bDK, (?:VLO|PSX|PBF|DINO|PARR|CVI|CVX|XOM)\b"
# The peers' filers on EDGAR (their CIKs) and the ticker slugs their filings are named by; MPC's, MPLX's and an
# industry exhibit's filings are not peers' and stay.
PEER_CIKS = ("1035002", "1534701", "1534504", "1915657", "48039", "1694426", "1376339", "821483", "93410", "34088")
PEER_SLUGS = r"vlo|psx|pbf|dino|parr|dk|cvi|cvx|xom|hfc"
PATTERNS = [
    ("the owner's name or handle", re.compile(OWNER, re.I)),
    ("this account's repositories", re.compile(r"enterprise-performance-model|personal-agent-skills|enterprise-people-graph", re.I)),
    ("a decision record number", re.compile(r"EPM-DEC-001")),
    ("a decision record's short number", re.compile(r"the decisions? of \d{4}-\d{2}-\d{2}(?:, | and | or | to |; )0\d{3}\b|\(0\d{3}\)|\b(?:amending|amended by|supersedes|superseded by) 0\d{3}\b")),
    ("the saved answers folder", re.compile(r"decision-owner-answers|answers-20\d\d-\d\d-\d\d")),
    ("the old IRI base or company name", re.compile(r"w3id\\*\.org/lsc|\bLSC\b|Lagos Specialty", re.I)),
    ("a host of the build", re.compile(r"exe\.dev|exe\.xyz|spacesheep\.dev|app\.eraser\.io", re.I)),
    ("a path on the owner's machine", re.compile(r"(?<!/Workspace)/Users/|Dropbox|~/\.claude/handoffs|~/\.claude/plugins|~/\.agents/skills")),
    ("a peer named", re.compile(PEERS, re.I)),
    ("a peer's ticker", re.compile(TICKERS)),
    ("a peer's filing on EDGAR", re.compile(r"sec\.gov/Archives/edgar/data/(?:" + "|".join(PEER_CIKS) + r")/|edgar/data/\d+/\S*/(?:" + PEER_SLUGS + r")-\d{8}\.", re.I)),
    ("a document the release leaves out", re.compile(r"LOCAL-STORES\.(?:md|html)|STORE-INVENTORY\.(?:md|html)|business_architecture/ontology/lpg-projection|\.\./lpg-projection/|`lpg-projection/`|\(lpg-projection/")),
    ("an issue or pull request number", re.compile(r"\b(?:PRs?|pull requests?|issues?)\s+#\d+|(?<![&\w-])#\d{3}\b(?![\da-fA-F])")),
    ("the graph's double-underscore separator", re.compile(r"\b[a-z][a-z0-9]*__[A-Za-z]")),
    ("the namespace note is missing", None),  # checked once, below
]
# Third-party syntax that carries two underscores and is not a graph name (the owner's rule names the graph's separator).
ALLOWED_DOUBLE = re.compile(r"metric_time__day|__init__|__main__|__pycache__|__file__|__name__|__doc__")
# The ontology-to-lpg skill's own tests describe what n10s writes before the rename step, on its library example
# (lib__Work, my__node, n4sch__Entity): a third-party tool's format on fixture names, not a name in any graph, query,
# document or page of the release (the night log of 2026-11-01, 00:45). The exemption covers those test files only,
# and never a prefix of this ontology's graph, so a planted vs__Stage or core__Process fails there too.
# ... and the projection pipeline's own tests of the n10s names it renames (business_architecture/ontology/projection/test_pipeline.py).
FIXTURE_FILES = re.compile(r"^(?:skills/ontology-to-lpg/scripts/test_[^/]+|business_architecture/ontology/projection/test_pipeline)\.py$")
GRAPH_PREFIXES = ("core", "orgm", "kpi", "pop", "party", "dp", "vs", "sys", "lane", "mkt", "plc", "auth", "con", "tv", "tech", "oeo")
TEXT_EXT = {".md", ".html", ".ttl", ".jsonld", ".json", ".csv", ".py", ".rq", ".sql", ".sh", ".yml", ".yaml", ".txt",
            ".nt", ".toml", ".example", ".cypher", ".jsonl", ".css", ".svg", ".cfg", ".ini", ".lock"}
OFFICE_EXT = {".xlsx", ".docx", ".pptx"}
DATA_URI = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,([A-Za-z0-9+/=\s]+)")
CSS_COLOUR = re.compile(r"(?<=[:\s(,])#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b(?=[;\s)}\],!])")
PRINTABLE_RUN = re.compile(rb"[\x20-\x7e\t]{6,}")
# Inside a binary, a three-letter peer, "#123" or "x__y" is read only from runs that look like words (two spaces or
# more): an image's random bytes form "h4i__z" by chance, a planted "see pbf and skos__x" does not look like chance.
SHORT_PATTERNS = ("a peer named", "a peer's ticker", "an issue or pull request number", "the graph's double-underscore separator")
NAMESPACE_NOTE = "Data, Analytics and Insight"


def strings_of(data):
    """The runs of printable text inside bytes (what `strings` prints), one per line: words in a PDF's metadata, an
    image's comment or a binary's strings are scanned; random bytes between them are not."""
    return "\n".join(m.group(0).decode("ascii") for m in PRINTABLE_RUN.finditer(data))


def decoded_data_uris(text):
    """Each base64 payload of a data: URI in a page, decoded, as the printable text inside it."""
    for m in DATA_URI.finditer(text):
        try:
            raw = base64.b64decode(re.sub(r"\s", "", m.group(1)), validate=False)
        except (ValueError, Exception):
            continue
        yield strings_of(raw)


def texts(path):
    """(label, text) pairs to scan for one file."""
    ext = os.path.splitext(path)[1].lower()
    if ext in OFFICE_EXT:
        try:
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
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
    if ext in TEXT_EXT or b"\0" not in data[:4096]:
        text = data.decode("utf-8", "replace")
        if ext in (".html", ".css", ".svg"):
            text = CSS_COLOUR.sub("#colour", text)  # #fff, #111 and #1a2b3c are colours, not numbers
        for i, decoded in enumerate(decoded_data_uris(text)):
            yield f"{path} (data URI {i + 1})", decoded
        yield path, DATA_URI.sub("data:image-removed", text)
    else:
        yield path + " (binary)", strings_of(data)


def allowed_double(rel, text, m):
    """A double underscore that is not the graph's separator: language syntax, or a fixture name in the skill's tests."""
    if ALLOWED_DOUBLE.search(text[max(0, m.start() - 12):m.end() + 12]):
        return True
    prefix = m.group(0).split("__", 1)[0]
    return bool(FIXTURE_FILES.match(rel)) and prefix not in GRAPH_PREFIXES


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
                if NAMESPACE_NOTE in text and rel == "README.md":
                    note_found = True
                binary = label.endswith(" (binary)") or " (data URI " in label
                wordy = "\n".join(l for l in text.split("\n") if l.count(" ") >= 2) if binary else text
                for reason, pattern in PATTERNS:
                    if pattern is None:
                        continue
                    scanned = wordy if binary and reason in SHORT_PATTERNS else text
                    for m in pattern.finditer(scanned):
                        if reason.startswith("the graph's") and allowed_double(rel, scanned, m):
                            continue
                        line = scanned.count("\n", 0, m.start()) + 1
                        shown = re.sub(r" \((?:binary|data URI \d+)\)$", "", label)
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
