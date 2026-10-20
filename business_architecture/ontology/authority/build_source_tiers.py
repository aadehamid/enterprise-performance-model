"""Build the source tiers (Step 9; EPM-DEC-001-0059).

    python3 build_source_tiers.py            # check the table and print the figures
    python3 build_source_tiers.py --write    # also write source-tiers.ttl
    python3 build_source_tiers.py --verify   # fail unless source-tiers.ttl equals a fresh build

source-tiers.csv gives each source the modules cite a tier from 1 to 5. The build fails unless
every tier is 1 to 5 and each source is listed once. test_source_tiers.py checks that every
source the released and module graphs cite is in the table.
"""
import argparse
import csv
import os
import sys
from collections import Counter

from rdflib import Graph, Namespace, URIRef

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "source-tiers.csv")
OUTPUT = os.path.join(HERE, "source-tiers.ttl")
AUTH = Namespace("https://w3id.org/lsc/ontology/modules/authority/")
TIER = Namespace("https://w3id.org/lsc/ontology/modules/authority/tier/")
TIERS = {1: "process-authority", 2: "mpc", 3: "peers", 4: "industry", 5: "framework"}


def load():
    with open(TABLE, newline="") as f:
        rows = list(csv.DictReader(f))
    problems = [f"{s} is listed {n} times" for s, n in Counter(r["source"] for r in rows).items() if n > 1]
    problems += [f"{r['source']}: tier {r['tier']!r} is not 1 to 5" for r in rows if r["tier"] not in {str(k) for k in TIERS}]
    if problems:
        sys.exit("source-tiers.csv does not reconcile:\n  " + "\n  ".join(problems))
    return rows


def build(rows):
    g = Graph()
    g.bind("auth", AUTH)
    g.bind("tier", TIER)
    for r in rows:
        g.add((URIRef(r["source"]), AUTH.evidenceTier, TIER[TIERS[int(r["tier"])]]))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows = load()
    text = ("# Evidence tiers of the cited sources (Step 9; EPM-DEC-001-0059).\n"
            "# Built by build_source_tiers.py from source-tiers.csv. Do not edit by hand.\n"
            + build(rows).serialize(format="turtle"))
    counts = Counter(int(r["tier"]) for r in rows)
    print("sources %d; " % len(rows) + "; ".join(f"tier {k} {counts[k]}" for k in TIERS))
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("source-tiers.ttl is not current: run build_source_tiers.py --write")
        print("source-tiers.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
