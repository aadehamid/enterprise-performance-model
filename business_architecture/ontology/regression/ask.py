"""Ask the ontology one competency question, with the regression's queries and the same graph.

Run from this folder:
    python3 ask.py                     # list the queries, each named for its question
    python3 ask.py q36-the-crack       # run one, showing each IRI's label
    python3 ask.py q06a-systems-for-process --limit 5
"""
import argparse
import glob
import os
import sys

from rdflib import URIRef
from rdflib.namespace import RDFS, SKOS

import run


def label(graph, value):
    """A term's preferred label or label if it has one, else the value as written; an unbound value shows as a dash."""
    if value is None:
        return "-"
    if isinstance(value, URIRef):
        return str(graph.value(value, SKOS.prefLabel) or graph.value(value, RDFS.label) or value)
    return str(value)


def questions():
    return {os.path.basename(p)[:-3]: p for p in sorted(glob.glob(os.path.join(run.HERE, "queries", "*.rq")))}


def ask(graph, path, limit=20):
    """The query's first line, its row count, and up to `limit` rows with labels."""
    with open(path) as f:
        text = f.read()
    rows = list(graph.query(text))
    return text.splitlines()[0].lstrip("# "), len(rows), [[label(graph, v) for v in r] for r in rows[:limit]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()
    known = questions()
    if not args.question:
        for name, path in known.items():
            with open(path) as f:
                print(f"{name}: {f.readline().lstrip('# ').strip()}")
        return
    if args.question not in known:
        sys.exit(f"no question {args.question}; run with no argument to list them")
    question, count, rows = ask(run.load(run.RELEASE), known[args.question], args.limit)
    print(f"{question}\n{count} row(s)")
    for r in rows:
        print("  " + " | ".join(r))


if __name__ == "__main__":
    main()
