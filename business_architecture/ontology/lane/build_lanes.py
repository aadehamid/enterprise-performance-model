"""Build the lane module (Step 7; EPM-DEC-001-0056).

    python3 build_lanes.py            # check the sources and print the figures
    python3 build_lanes.py --write    # also write lanes.ttl
    python3 build_lanes.py --verify   # fail unless lanes.ttl equals a fresh build

The four lanes come from business_process/office_lanes.json; each node's officeLane in the
process map places it in one. The build fails unless every officeLane value is a lane in
office_lanes.json and every node with a lane is in core 2.1.0. Nothing is inherited from a
parent.
"""
import argparse
import json
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BP = os.path.join(REPO, "business_architecture", "business_process")
LANES = os.path.join(BP, "office_lanes.json")
MAP = os.path.join(BP, "downstream_process_map.json")
CORE = os.path.join(HERE, "..", "releases", "core", "2.1.0", "core.ttl")
OUTPUT = os.path.join(HERE, "lanes.ttl")

LANE = Namespace("https://w3id.org/lsc/ontology/modules/lane/")
LANEV = Namespace("https://w3id.org/lsc/ontology/modules/lane/lane/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")


def placements():
    with open(MAP) as f:
        roots = json.load(f)
    found = []

    def walk(node):
        if "officeLane" in node:
            found.append((node["id"], node["officeLane"]))
        for child in node.get("children") or []:
            walk(child)
    for r in roots:
        walk(r)
    return found


def load():
    with open(LANES) as f:
        lanes = json.load(f)
    g = Graph().parse(CORE)
    procs = {str(n): s for s, n in g.subject_objects(SKOS.notation) if str(s).startswith(str(PROC))}
    placed = placements()
    problems = [f"{pid}: lane {lane!r} is not in office_lanes.json" for pid, lane in placed if lane not in lanes]
    problems += [f"{pid}: not in core 2.1.0" for pid, _ in placed if pid not in procs]
    if problems:
        sys.exit("lane sources do not reconcile:\n  " + "\n  ".join(problems))
    return lanes, placed, procs


def slug(key):
    return key.replace("_", "-")


def build(lanes, placed, procs):
    g = Graph()
    for prefix, ns in (("lane", LANE), ("lanev", LANEV), ("proc", PROC), ("src", SRC), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    src = SRC["office-lanes"]
    g.add((src, RDF.type, DCTERMS.BibliographicResource))
    g.add((src, DCTERMS.title, Literal("Office lanes, business_architecture/business_process/office_lanes.json", lang="en")))
    for key, lane in lanes.items():
        iri = LANEV[slug(key)]
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, LANE.OfficeLanes))
        g.add((iri, SKOS.prefLabel, Literal(lane["name"], lang="en")))
        g.add((iri, SKOS.notation, Literal(key, datatype=XSD.string)))
        g.add((iri, SKOS.definition, Literal(lane["description"], lang="en")))
        g.add((iri, DCTERMS.source, src))
    for pid, lane in placed:
        g.add((procs[pid], LANE.officeLane, LANEV[slug(lane)]))
    return g


def figures(lanes, placed):
    per = Counter(lane for _, lane in placed)
    return {"lanes": len(lanes), "placed processes": len(placed), **{k: per[k] for k in lanes}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    lanes, placed, procs = load()
    text = ("# Office lanes of the lane module (Step 7; EPM-DEC-001-0056).\n"
            "# Built by build_lanes.py from office_lanes.json and the process map. Do not edit by hand.\n"
            + build(lanes, placed, procs).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(lanes, placed).items()))
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("lanes.ttl is not current: run build_lanes.py --write")
        print("lanes.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
