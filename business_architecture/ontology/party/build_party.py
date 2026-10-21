"""Build the `party` module's code lists (Steps 5 to 7; EPM-DEC-001-0067, EPM-DEC-001-0068).

    python3 build_party.py            # check the table and print the figures
    python3 build_party.py --write    # also write code-lists.ttl
    python3 build_party.py --verify   # fail unless code-lists.ttl equals a fresh build

code-lists.csv holds every code list of the module, one row per value. The build fails unless
every row names a known scheme, has a definition, is unique in its scheme, and points its
broader value at a value of the same scheme; and unless the customer classes carry each of
MPC's classes C1 to C8 exactly once.
"""
import argparse
import csv
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, "code-lists.csv")
OUTPUT = os.path.join(HERE, "code-lists.ttl")
CUST = Namespace("https://w3id.org/lsc/ontology/modules/party/")
CITATION = "EPM-DEC-001-0067; EPM-DEC-001-0068"
MPC_CLASSES = {f"C{n}" for n in range(1, 9)}

# Each scheme's label and definition, in the order the module lists them.
SCHEMES = {
    "party-type": ("party types", "Person or organization: the two kinds of party."),
    "party-role": ("party roles", "The governed list of role types a party can hold. A new role type needs a governance decision."),
    "relationship-type": ("party relationship types", "The kinds of link from one party role to another."),
    "agreement-type": ("agreement types", "The types of agreement. They overlap: one agreement can have several."),
    "line-of-business": ("lines of business", "The governed categories of the company's business that a customer sits under."),
    "customer-class": ("customer classes", "The kinds of customer, grouped by value-chain role and brand attachment. Each class is assigned to a customer account with dates. Together with MPC's classification C1 to C8 they form the channel dimension of MPC-P06."),
    "site-type": ("site types", "The kinds of physical operating location."),
    "operating-model": ("site operating models", "Who owns and who operates a site."),
    "identifier-type": ("identifier types", "The kinds of external identifier of a party."),
    "address-usage": ("address usages", "How an address is used."),
    "contact-type": ("contact types", "The kinds of contact point."),
    "transaction-kind": ("transaction kinds", "The kinds of transaction a party or an account is associated with."),
}


def scheme_iri(scheme):
    return CUST[scheme]


def value_iri(scheme, notation):
    return CUST[f"{scheme}/{notation}"]


def load():
    with open(TABLE, newline="") as f:
        rows = list(csv.DictReader(f))
    problems = [f"{r['scheme']}/{r['notation']}: unknown scheme" for r in rows if r["scheme"] not in SCHEMES]
    problems += [f"{r['scheme']}/{r['notation']}: no definition" for r in rows if not r["definition"]]
    keys = Counter((r["scheme"], r["notation"]) for r in rows)
    problems += [f"{s}/{n} is listed {c} times" for (s, n), c in keys.items() if c > 1]
    problems += [f"{r['scheme']}/{r['notation']}: broader {r['broader']} is not in its scheme"
                 for r in rows if r["broader"] and (r["scheme"], r["broader"]) not in keys]
    mpc = Counter(r["mpc_class"] for r in rows if r["mpc_class"])
    problems += [f"MPC class {c} is used {n} times" for c, n in mpc.items() if n > 1]
    problems += [f"MPC class {c} is not one of C1 to C8" for c in mpc if c not in MPC_CLASSES]
    problems += [f"MPC class {c} has no customer class" for c in sorted(MPC_CLASSES - set(mpc))]
    problems += [f"{r['scheme']}/{r['notation']}: only customer classes carry an MPC class"
                 for r in rows if r["mpc_class"] and r["scheme"] != "customer-class"]
    problems += [f"{s}: no values" for s in SCHEMES if not any(r["scheme"] == s for r in rows)]
    if problems:
        sys.exit("code-lists.csv does not reconcile:\n  " + "\n  ".join(problems))
    return rows


def build(rows):
    g = Graph()
    g.bind("party", CUST)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    for scheme, (label, definition) in SCHEMES.items():
        s = scheme_iri(scheme)
        g.add((s, RDF.type, SKOS.ConceptScheme))
        g.add((s, RDFS.label, Literal(label, lang="en")))
        g.add((s, SKOS.definition, Literal(definition, lang="en")))
        g.add((s, DCTERMS.bibliographicCitation, Literal(CITATION, lang="en")))
    for r in rows:
        v = value_iri(r["scheme"], r["notation"])
        g.add((v, RDF.type, SKOS.Concept))
        if r["scheme"] == "line-of-business":
            g.add((v, RDF.type, CUST.LineOfBusiness))
        g.add((v, SKOS.inScheme, scheme_iri(r["scheme"])))
        g.add((v, SKOS.notation, Literal(r["notation"])))
        g.add((v, SKOS.prefLabel, Literal(r["label"], lang="en")))
        g.add((v, SKOS.definition, Literal(r["definition"], lang="en")))
        if r["broader"]:
            g.add((v, SKOS.broader, value_iri(r["scheme"], r["broader"])))
        else:
            g.add((v, SKOS.topConceptOf, scheme_iri(r["scheme"])))
        if r["mpc_class"]:
            g.add((v, CUST.mpcClassification, Literal(r["mpc_class"])))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows = load()
    text = ("# The `party` module's code lists (Steps 5 to 7; EPM-DEC-001-0067, EPM-DEC-001-0068).\n"
            "# Built by build_party.py from code-lists.csv. Do not edit by hand.\n"
            + build(rows).serialize(format="turtle"))
    counts = Counter(r["scheme"] for r in rows)
    print("code lists " + ", ".join(f"{s} {counts[s]}" for s in SCHEMES))
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("code-lists.ttl is not current: run build_party.py --write")
        print("code-lists.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
