"""Build the RACI assignments (Step 5, slice 3; EPM-DEC-001-0032) from the process map and the role register.

    python3 build_assignments.py            # build, check SHACL and the ledger, print the figures
    python3 build_assignments.py --write    # also write assignments.ttl and raci-conservation.csv
    python3 build_assignments.py --verify   # fail unless both files equal a fresh build

One assignment per RACI entry and role: an entry that names two roles (a compound string)
gives two assignments. Nothing is inferred from the hierarchy: a process without a `raci`
object in the source gets no assignment. The ledger (raci-conservation.csv) reconciles
entries in with assignments out.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

import build_roles as br

HERE = br.HERE
IDENTITY = os.path.join(HERE, "..", "build", "output", "step2-identity-map.json")
OUTPUT = os.path.join(HERE, "assignments.ttl")
LEDGER = os.path.join(HERE, "raci-conservation.csv")
ASSIGNMENT = Namespace("https://w3id.org/lsc/ontology/modules/organization/assignment/")
RACI = Namespace("https://w3id.org/lsc/ontology/modules/organization/raci-level/")


def process_iris():
    """Map each process map ID (the concept's skos:notation) to its IRI from the Step 2 identity map."""
    with open(IDENTITY) as f:
        return {row["skos_notation"]: URIRef(row["uri"]) for row in json.load(f) if row["skos_notation"]}


def assignment_iri(process_iri, level, role, text):
    """Stable under reordering of the source lists: the IRI hashes the source string, not its position."""
    digest = hashlib.sha256(text.encode()).hexdigest()[:8]
    return ASSIGNMENT[f"{str(process_iri).rsplit('/', 1)[1]}--{level}--{role}--{digest}"]


def build():
    entries, register, roles = br.load()
    roles_of = {r["source_text"]: r["roles"].split(";") for r in register}
    iris = process_iris()
    missing = sorted({p for p, _, _ in entries if p not in iris})
    if missing:
        sys.exit(f"processes with RACI have no IRI in the identity map: {missing}")
    g = Graph()
    for prefix, ns in (("orgm", br.ORGM), ("role", br.ROLE), ("raci", RACI), ("asg", ASSIGNMENT),
                       ("src", br.SRC), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    for process, level, text in entries:
        for role in roles_of[text]:
            a = assignment_iri(iris[process], level, role, text)
            if (a, RDF.type, br.ORGM.ResponsibilityAssignment) in g:
                sys.exit(f"two assignments share the IRI {a}: the same string twice in one list of {process}")
            g.add((a, RDF.type, br.ORGM.ResponsibilityAssignment))
            g.add((a, br.ORGM.forProcess, iris[process]))
            g.add((a, br.ORGM.assignedRole, br.ROLE[role]))
            g.add((a, br.ORGM.raciLevel, RACI[level]))
            g.add((a, br.ORGM.sourceRoleText, Literal(text, datatype=XSD.string)))
            g.add((a, DCTERMS.source, br.PROCESS_MAP))
    return entries, register, g


def ledger(entries, register, g):
    """Rows of (measure, value). Entries in, plus the extra roles of compound strings, equal assignments out."""
    width = {r["source_text"]: len(r["roles"].split(";")) for r in register}
    out = Counter(str(o).rsplit("/", 1)[1] for o in g.objects(None, br.ORGM.raciLevel))
    rows = [("processes with RACI in the source", len({p for p, _, _ in entries})),
            ("RACI entries in the source", len(entries)),
            ("extra roles from compound strings", sum(width[t] - 1 for _, _, t in entries)),
            ("assignments emitted", len(set(g.subjects(RDF.type, br.ORGM.ResponsibilityAssignment))))]
    rows += [(f"assignments at level {lvl}", out[lvl]) for lvl in br.LEVELS]
    rows += [(f"entries at level {lvl}", sum(1 for _, lv, _ in entries if lv == lvl)) for lvl in br.LEVELS]
    values = dict(rows)
    if values["RACI entries in the source"] + values["extra roles from compound strings"] != values["assignments emitted"]:
        sys.exit("RACI ledger does not reconcile: entries + extra roles != assignments")
    return rows


def shacl(g):
    data = Graph()
    for part in ("vocabulary.ttl", "roles.ttl"):
        data.parse(os.path.join(HERE, part))
    data += g
    # The process concepts live in core; type the ones assignments point at so sh:class checks resolve.
    for p in set(g.objects(None, br.ORGM.forProcess)):
        data.add((p, RDF.type, SKOS.Concept))
    conforms, _, text = validate(data, shacl_graph=Graph().parse(os.path.join(HERE, "shapes.ttl")))
    if not conforms:
        sys.exit("assignments fail the organization shapes:\n" + text)


def render(entries, register, g):
    ttl = ("# RACI assignments of the organization module (Step 5, slice 3; EPM-DEC-001-0032).\n"
           "# Built by build_assignments.py from the process map and the role register. Do not edit by hand.\n"
           + g.serialize(format="turtle"))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["measure", "value"])
    w.writerows(ledger(entries, register, g))
    return {OUTPUT: ttl, LEDGER: buf.getvalue()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    entries, register, g = build()
    shacl(g)
    files = render(entries, register, g)
    print("; ".join(f"{k} {v}" for k, v in ledger(entries, register, g)) + "; SHACL conforms")
    if args.verify:
        stale = [os.path.basename(p) for p, text in files.items()
                 if not os.path.exists(p) or open(p).read() != text]
        if stale:
            sys.exit(f"not current: {stale}; run build_assignments.py --write")
        print("assignments.ttl and raci-conservation.csv are current")
    if args.write:
        for p, text in files.items():
            with open(p, "w") as f:
                f.write(text)
        print("wrote assignments.ttl and raci-conservation.csv")


if __name__ == "__main__":
    main()
