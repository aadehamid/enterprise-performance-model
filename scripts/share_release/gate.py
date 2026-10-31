#!/usr/bin/env python3
"""The leak gate: fail on any name, handle, repository, host, peer, record number or issue number in the
release, and on the graph's double-underscore separator (plan step 5; EPM-DEC-001-0110 and its amendment).

    python3 scripts/share_release/gate.py <release folder> [--json]

It reads every file: text files as text; XLSX, DOCX and PPTX as the XML inside them; PDFs as their raw bytes
(metadata and uncompressed streams); other binaries as bytes decoded loosely. Base64 image data inside a
page (data: URIs) is skipped, since it is not text. Exit 1 with one line per hit.
"""
import argparse
import json
import os
import re
import sys
import zipfile

# Each pattern with its reason. The owner's name and handle are built from fragments so this file does not match itself.
OWNER = "|".join(["ha" + "mid", "ade" + "sokan", "aade" + "ha" + "mid"])
PEERS = r"valero|phillips\s?66|\bpbf\b|hf\s?sinclair|hollyfrontier|par\s+pacific|\bdelek\b|\bcvr\b|chevron|exxon"
PATTERNS = [
    ("the owner's name or handle", re.compile(OWNER, re.I)),
    ("this account's repositories", re.compile(r"enterprise-performance-model|personal-agent-skills", re.I)),
    ("a decision record number", re.compile(r"EPM-DEC-001")),
    ("the saved answers folder", re.compile(r"decision-owner-answers|answers-20\d\d-\d\d-\d\d")),
    ("the old IRI base or company name", re.compile(r"w3id\\*\.org/lsc|\bLSC\b|Lagos Specialty", re.I)),
    ("a host of the build", re.compile(r"exe\.dev|exe\.xyz|spacesheep\.dev|app\.eraser\.io", re.I)),
    ("a path on the owner's machine", re.compile(r"(?<!/Workspace)/Users/|Dropbox|~/\.claude/handoffs|~/\.claude/plugins|~/\.agents/skills")),
    ("a peer named", re.compile(PEERS, re.I)),
    ("an issue or pull request number", re.compile(r"\b(?:PRs?|pull requests?|issues?)\s+#\d+|(?<![&\w-])#\d{3}\b(?![\da-fA-F])")),
    ("the graph's double-underscore separator", re.compile(r"\b[a-z][a-z0-9]*__[A-Za-z]")),
    ("the namespace note is missing", None),  # checked once, below
]
# Third-party syntax that carries two underscores and is not a graph name (the owner's rule names the graph's separator).
ALLOWED_DOUBLE = re.compile(r"metric_time__day|__init__|__main__|__pycache__|__file__|__name__|__doc__")
# The skill's own test fixtures describe what n10s writes before the rename step; they are a third-party tool's format,
# not a name in any graph, query, document or page of the release (the night log of 2026-11-01, 00:45).
ALLOWED_FILES_DOUBLE = re.compile(r"^skills/[^/]+/scripts/test_[^/]+\.py$")
TEXT_EXT = {".md", ".html", ".ttl", ".jsonld", ".json", ".csv", ".py", ".rq", ".sql", ".sh", ".yml", ".yaml", ".txt",
            ".nt", ".toml", ".example", ".cypher", ".jsonl", ".css", ".svg", ".cfg", ".ini", ".lock"}
OFFICE_EXT = {".xlsx", ".docx", ".pptx"}
DATA_URI = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=\s]+")
CSS_COLOUR = re.compile(r"(?<=[:\s(,])#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b(?=[;\s)}\],!])")
SHORT_PATTERNS = ("a peer named", "an issue or pull request number", "the graph's double-underscore separator")
NAMESPACE_NOTE = "Data, Analytics and Insight"


def texts(path):
    """(label, text) pairs to scan for one file."""
    ext = os.path.splitext(path)[1].lower()
    if ext in OFFICE_EXT:
        try:
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    if name.endswith((".xml", ".rels", ".txt")):
                        yield f"{path}:{name}", z.read(name).decode("utf-8", "replace")
        except zipfile.BadZipFile:
            with open(path, "rb") as f:
                yield path, f.read().decode("latin-1")
        return
    with open(path, "rb") as f:
        data = f.read()
    if ext in TEXT_EXT or b"\0" not in data[:4096]:
        text = data.decode("utf-8", "replace")
        if ext in (".html", ".css", ".svg"):
            text = CSS_COLOUR.sub("#colour", text)  # #fff, #111 and #1a2b3c are colours, not numbers
        yield path, DATA_URI.sub("data:image-removed", text)
    else:
        # Bytes decoded loosely hold every three-letter word by chance, so only the long patterns run on them.
        yield path + " (binary)", data.decode("latin-1")


def scan(release):
    hits = []
    note_found = False
    for root, dirs, files in os.walk(release):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "__pycache__"))
        for f in sorted(files):
            path = os.path.join(root, f)
            rel = os.path.relpath(path, release)
            for reason, pattern in PATTERNS:
                if pattern and pattern.search(rel):
                    hits.append({"file": rel, "reason": reason, "where": "the path"})
            for label, text in texts(path):
                if NAMESPACE_NOTE in text and rel == "README.md":
                    note_found = True
                for reason, pattern in PATTERNS:
                    if pattern is None or (label.endswith(" (binary)") and reason in SHORT_PATTERNS):
                        continue
                    for m in pattern.finditer(text):
                        if reason.startswith("the graph's") and (ALLOWED_DOUBLE.search(text[max(0, m.start() - 12):m.end() + 12])
                                                                 or ALLOWED_FILES_DOUBLE.match(rel)):
                            continue
                        line = text.count("\n", 0, m.start()) + 1
                        shown = label.replace(" (binary)", "")
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
