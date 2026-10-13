"""Build the organization module's roles (Step 5, slice 2; EPM-DEC-001-0031) from the role register.

    python3 build_roles.py            # check the register against the source and print the figures
    python3 build_roles.py --write    # also write roles.ttl
    python3 build_roles.py --verify   # fail unless roles.ttl equals a fresh build

The register (role-register.csv) maps every role string in the process map's `raci` lists to
one or more roles in roles.csv. The build fails unless the register holds each distinct source
string exactly once, names only roles that roles.csv defines, and uses every role it defines.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SOURCE = os.path.join(REPO, "business_architecture", "business_process", "downstream_process_map.json")
REGISTER = os.path.join(HERE, "role-register.csv")
ROLES = os.path.join(HERE, "roles.csv")
OUTPUT = os.path.join(HERE, "roles.ttl")

ORG = Namespace("http://www.w3.org/ns/org#")
ORGM = Namespace("https://w3id.org/lsc/ontology/modules/organization/")
ROLE = Namespace("https://w3id.org/lsc/ontology/modules/organization/role/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
PROCESS_MAP = SRC["downstream-process-map"]
LEVELS = ("responsible", "accountable", "consulted", "informed")
RULES = {"exact", "case", "plural", "punctuation", "ampersand", "qualifier", "compound", "team"}
KINDS = {"position", "team"}
TEAM_NOTE = ("The source names a team here, not a position. The role stands for the team "
             "acting as one party in a RACI chart.")


def raci_entries(node, out):
    """Collect (process id, level, role string) for every RACI entry in the process map."""
    if isinstance(node, dict):
        raci = node.get("raci")
        if isinstance(raci, dict):
            unknown = set(raci) - set(LEVELS)
            if unknown:
                sys.exit(f"process {node.get('id')} has RACI keys outside the four levels: {sorted(unknown)}")
            for level in LEVELS:
                for text in raci.get(level, []):
                    out.append((node.get("id"), level, text))
        for value in node.values():
            raci_entries(value, out)
    elif isinstance(node, list):
        for value in node:
            raci_entries(value, out)
    return out


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load():
    """Return the register rows and roles, keyed, after checking each against the source."""
    with open(SOURCE) as f:
        entries = raci_entries(json.load(f), [])
    source_texts = Counter(text for _, _, text in entries)
    register, roles = read_csv(REGISTER), read_csv(ROLES)
    problems = []

    texts = Counter(r["source_text"] for r in register)
    problems += [f"register lists {t!r} {n} times" for t, n in texts.items() if n > 1]
    problems += [f"source string {t!r} is not in the register" for t in source_texts if t not in texts]
    problems += [f"register row {t!r} is not in the source" for t in texts if t not in source_texts]

    slugs = Counter(r["slug"] for r in roles)
    problems += [f"roles.csv lists {s!r} {n} times" for s, n in slugs.items() if n > 1]
    labels = Counter(r["label"] for r in roles)
    problems += [f"two roles share the label {lab!r}" for lab, n in labels.items() if n > 1]
    problems += [f"role {r['slug']!r} has kind {r['kind']!r}" for r in roles if r["kind"] not in KINDS]

    used = set()
    for row in register:
        names = row["roles"].split(";")
        used.update(names)
        problems += [f"{row['source_text']!r} names unknown role {n!r}" for n in names if n not in slugs]
        steps = set(row["rule"].split("+"))
        problems += [f"{row['source_text']!r} has unknown rule {s!r}" for s in steps - RULES]
        if ("compound" in steps) != (len(names) > 1):
            problems.append(f"{row['source_text']!r}: rule 'compound' must go with two or more roles")
        if ("qualifier" in steps) != bool(row["qualifier"]):
            problems.append(f"{row['source_text']!r}: rule 'qualifier' must go with a qualifier")
        # The cheap half of the surface-only rule: an exact row is spelt like its role's label, and a
        # case row differs from it in case alone.
        label = {r["slug"]: r["label"] for r in roles}.get(names[0], "")
        if steps == {"exact"} and row["source_text"] != label:
            problems.append(f"{row['source_text']!r}: rule 'exact' but the label is {label!r}")
        if steps == {"case"} and row["source_text"].lower() != label.lower():
            problems.append(f"{row['source_text']!r}: rule 'case' but the label is {label!r}")
        if "team" in steps and any(r["kind"] != "team" for r in roles if r["slug"] in names):
            problems.append(f"{row['source_text']!r}: rule 'team' must map to a team")
    problems += [f"role {s!r} is not used by the register" for s in slugs if s not in used]

    if problems:
        sys.exit("role register does not reconcile:\n  " + "\n  ".join(problems))
    return entries, register, roles


def build(register, roles):
    g = Graph()
    for prefix, ns in (("org", ORG), ("orgm", ORGM), ("role", ROLE), ("src", SRC), ("skos", SKOS),
                       ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    g.add((PROCESS_MAP, RDF.type, DCTERMS.BibliographicResource))
    g.add((PROCESS_MAP, DCTERMS.title, Literal(
        "Downstream process map, business_architecture/business_process/downstream_process_map.json", lang="en")))
    for role in roles:
        iri = ROLE[role["slug"]]
        g.add((iri, RDF.type, ORG.Role))
        g.add((iri, SKOS.prefLabel, Literal(role["label"], lang="en")))
        g.add((iri, DCTERMS.source, PROCESS_MAP))
        if role["kind"] == "team":
            g.add((iri, SKOS.scopeNote, Literal(TEAM_NOTE, lang="en")))
    # A source string that names one role without a qualifier, spelt differently from its
    # label, is an alternative label. A qualified string names the role in one setting only.
    for row in register:
        names = row["roles"].split(";")
        if len(names) == 1 and not row["qualifier"]:
            label = next(r["label"] for r in roles if r["slug"] == names[0])
            if row["source_text"] != label:
                g.add((ROLE[names[0]], SKOS.altLabel, Literal(row["source_text"], lang="en")))
    return g


def figures(entries, register, roles):
    per_text = {r["source_text"]: len(r["roles"].split(";")) for r in register}
    kinds = Counter(r["kind"] for r in roles)
    return {
        "processes with RACI": len({p for p, _, _ in entries}),
        "RACI entries": len(entries),
        "distinct source strings": len(register),
        "roles": len(roles),
        "positions": kinds["position"],
        "teams": kinds["team"],
        "compound strings": sum(1 for n in per_text.values() if n > 1),
        "role references after splitting": sum(per_text[t] for _, _, t in entries),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    entries, register, roles = load()
    text = ("# Roles of the organization module (Step 5, slice 2; EPM-DEC-001-0031).\n"
            "# Built by build_roles.py from role-register.csv and roles.csv. Do not edit by hand.\n"
            + build(register, roles).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(entries, register, roles).items()))
    if args.verify:
        current = os.path.exists(OUTPUT) and open(OUTPUT).read() == text
        if not current:
            sys.exit("roles.ttl is not current: run build_roles.py --write")
        print("roles.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
