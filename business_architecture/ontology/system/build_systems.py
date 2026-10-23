"""Build the system module (Step 7; EPM-DEC-001-0055).

    python3 build_systems.py            # check the register and print the figures
    python3 build_systems.py --write    # also write systems.ttl
    python3 build_systems.py --verify   # fail unless systems.ttl equals a fresh build

register.csv maps every distinct string in the process map's `systems` fields to the systems
it names (merged on spelling, split on "/"), or to none ("no-system": Manual, TBD and plans).
systems.csv gives each system's name and kind. The build fails unless every string in the map
is in the register once, every system the register names is in systems.csv, and every system
in systems.csv is named. A link to a process not in core 2.3.0 is counted as waiting for the
next core release, not emitted.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAP = os.path.join(REPO, "business_architecture", "business_process", "downstream_process_map.json")
REGISTER = os.path.join(HERE, "register.csv")
SYSTEMS = os.path.join(HERE, "systems.csv")
CORE = os.path.join(HERE, "..", "releases", "core", "2.3.0", "core.ttl")
OUTPUT = os.path.join(HERE, "systems.ttl")

SYS = Namespace("https://w3id.org/lsc/ontology/modules/system/")
KIND = Namespace("https://w3id.org/lsc/ontology/modules/system/kind/")
SYSTEM = Namespace("https://w3id.org/lsc/ontology/modules/system/system/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
KINDS = ("application", "office-tool", "document")
RULES = ("exact", "spelling", "split", "no-system")
MAP_SOURCE = SRC["downstream-process-map"]
UNDEFINED = ("The process map names this system but no source in the repository says what it does. "
             "Its definition waits for its owners (EPM-DEC-001-0055).")


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def split(text):
    return [t for t in text.split(";") if t]


def map_uses():
    """(process id, system string) for every entry of every node's systems field."""
    with open(MAP) as f:
        roots = json.load(f)
    uses = []

    def walk(node):
        for s in node.get("systems") or []:
            uses.append((node.get("id"), s))
        for child in node.get("children") or []:
            walk(child)
    for r in roots:
        walk(r)
    return uses


def core_processes():
    g = Graph().parse(CORE)
    return {str(n): s for s, n in g.subject_objects(SKOS.notation) if str(s).startswith(str(PROC))}


def load():
    register, systems, uses = read_csv(REGISTER), read_csv(SYSTEMS), map_uses()
    problems = []
    counts = Counter(r["source_text"] for r in register)
    problems += [f"register lists {t!r} {n} times" for t, n in counts.items() if n > 1]
    in_map = {s for _, s in uses}
    problems += [f"map string {t!r} is not in the register" for t in sorted(in_map - set(counts))]
    problems += [f"register string {t!r} is not in the map" for t in sorted(set(counts) - in_map)]
    slugs = {s["slug"]: s for s in systems}
    problems += [f"systems.csv lists {s!r} twice" for s, n in Counter(x["slug"] for x in systems).items() if n > 1]
    named = set()
    for r in register:
        if r["rule"] not in RULES:
            problems.append(f"{r['source_text']!r}: rule {r['rule']!r} is not one of {RULES}")
        if (r["rule"] == "no-system") != (not r["systems"]):
            problems.append(f"{r['source_text']!r}: only a no-system row names no system")
        if r["rule"] == "split" and len(split(r["systems"])) < 2:
            problems.append(f"{r['source_text']!r}: a split names two or more systems")
        for s in split(r["systems"]):
            named.add(s)
            if s not in slugs:
                problems.append(f"{r['source_text']!r}: system {s!r} is not in systems.csv")
    problems += [f"system {s!r} is named by no register row" for s in sorted(set(slugs) - named)]
    problems += [f"{s['slug']}: kind {s['kind']!r} is not one of {KINDS}" for s in systems if s["kind"] not in KINDS]
    if problems:
        sys.exit("system sources do not reconcile:\n  " + "\n  ".join(problems))
    return {r["source_text"]: r for r in register}, slugs, uses, core_processes()


def links(register, uses, procs):
    """(system slug, process id) pairs, once each, and the ones waiting for a core release."""
    pairs = {(s, pid) for pid, text in uses for s in split(register[text]["systems"])}
    return sorted(p for p in pairs if p[1] in procs), sorted(p for p in pairs if p[1] not in procs)


def build(register, slugs, uses, procs):
    g = Graph()
    for prefix, ns in (("sys", SYS), ("kind", KIND), ("system", SYSTEM), ("proc", PROC), ("src", SRC),
                       ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    # The map's source node is declared by the organization module (roles.ttl); only referenced here.
    for slug, s in slugs.items():
        iri = SYSTEM[slug]
        g.add((iri, RDF.type, SYS.System))
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, SYS.Systems))
        g.add((iri, SKOS.prefLabel, Literal(s["label"], lang="en")))
        g.add((iri, SKOS.notation, Literal(slug, datatype=XSD.string)))
        g.add((iri, SKOS.editorialNote, Literal(UNDEFINED, lang="en")))
        g.add((iri, SYS.systemKind, KIND[s["kind"]]))
        g.add((iri, DCTERMS.source, MAP_SOURCE))
    for r in register.values():
        if r["rule"] == "spelling":
            g.add((SYSTEM[r["systems"]], SKOS.altLabel, Literal(r["source_text"], lang="en")))
    emitted, _ = links(register, uses, procs)
    for slug, pid in emitted:
        g.add((SYSTEM[slug], SYS.supports, procs[pid]))
    return g


def figures(register, slugs, uses, procs):
    emitted, waiting = links(register, uses, procs)
    kinds = Counter(s["kind"] for s in slugs.values())
    return {
        "map strings": len(register),
        "systems": len(slugs),
        **{k: kinds[k] for k in KINDS},
        "no-system strings": sum(1 for r in register.values() if r["rule"] == "no-system"),
        "processes with a systems field": len({pid for pid, _ in uses}),
        "processes with a link": len({pid for _, pid in emitted}),
        "links": len(emitted),
        "links waiting for a core release": len(waiting),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    register, slugs, uses, procs = load()
    text = ("# Systems of the system module (Step 7; EPM-DEC-001-0055).\n"
            "# Built by build_systems.py from the process map, register.csv and systems.csv. Do not edit by hand.\n"
            + build(register, slugs, uses, procs).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(register, slugs, uses, procs).items()))
    if args.verify:
        current = os.path.exists(OUTPUT) and open(OUTPUT).read() == text
        if not current:
            sys.exit("systems.ttl is not current: run build_systems.py --write")
        print("systems.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
