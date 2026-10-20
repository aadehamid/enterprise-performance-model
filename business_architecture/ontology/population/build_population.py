"""Build the measure populations (Step 7; EPM-DEC-001-0062).

    python3 build_population.py            # check the table and print the figures
    python3 build_population.py --write    # also write population.ttl
    python3 build_population.py --verify   # fail unless population.ttl equals a fresh build

population.csv states, for each measure whose public source says so, what it includes and
excludes. The build fails unless every measure is in the kpi module, is listed once, has an
includes statement and cites its evidence.
"""
import argparse
import csv
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "population.csv")
MEASURES = os.path.join(HERE, "..", "kpi", "measures.ttl")
OUTPUT = os.path.join(HERE, "population.ttl")
POP = Namespace("https://w3id.org/lsc/ontology/modules/population/")
MEASURE = Namespace("https://w3id.org/lsc/ontology/modules/kpi/measure/")


def load():
    with open(TABLE, newline="") as f:
        rows = list(csv.DictReader(f))
    measures = {str(n) for n in Graph().parse(MEASURES).objects(None, SKOS.notation)}
    problems = [f"{m} is listed {n} times" for m, n in Counter(r["measure_id"] for r in rows).items() if n > 1]
    problems += [f"{r['measure_id']} is not a measure of the kpi module" for r in rows if r["measure_id"] not in measures]
    problems += [f"{r['measure_id']}: no includes statement" for r in rows if not r["includes"]]
    problems += [f"{r['measure_id']}: no evidence" for r in rows if not r["evidence"]]
    if problems:
        sys.exit("population.csv does not reconcile:\n  " + "\n  ".join(problems))
    return rows, len(measures)


def build(rows):
    g = Graph()
    g.bind("pop", POP)
    g.bind("measure", MEASURE)
    for r in rows:
        m = MEASURE[r["measure_id"]]
        g.add((m, POP.includes, Literal(r["includes"], lang="en")))
        if r["excludes"]:
            g.add((m, POP.excludes, Literal(r["excludes"], lang="en")))
        g.add((m, POP.populationEvidence, Literal(r["evidence"], datatype=XSD.string)))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows, total = load()
    text = ("# Measure populations (Step 7; EPM-DEC-001-0062). Built by build_population.py from\n"
            "# population.csv. Do not edit by hand.\n" + build(rows).serialize(format="turtle"))
    print(f"measures with a population {len(rows)} of {total}; with an exclusion {sum(1 for r in rows if r['excludes'])}")
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("population.ttl is not current: run build_population.py --write")
        print("population.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
