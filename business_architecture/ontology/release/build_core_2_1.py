"""Build core 2.1.0 from the released core 2.0.0 (EPM-DEC-001-0044).

    python3 build_core_2_1.py            # build, validate, print the figures
    python3 build_core_2_1.py --write    # write releases/core/2.1.0/
    python3 build_core_2_1.py --verify   # fail unless the written package equals a fresh build

core 2.0.0 stays as it was released (build_core_next.py). This builder starts from that graph and
applies the decision owner's Step 9 answer of 2026-10-18, "1a, 2a":

1. The eleven controlled-value shapes of validation/controlled-values.ttl join the release shapes.
   They check scheme membership: each value of a code-list property carries skos:inScheme with its
   list. The 2.0.0 shapes stay as they were; these supplement them.
2. One evidence node per canonical fact, keeping the direct triple. Each core:CanonicalFact names
   exactly one subject, predicate and object, and carries every REL row that supports the fact in
   core:evidenceRow. The direct triples and the nodes come from one mapping, the canonical-fact
   mapping of core 1.0.0, which this package carries as canonical-facts.csv.
3. The dangling dcterms:license IRI gives way to a dcterms:rights statement: proprietary, all rights
   reserved (EPM-DEC-001-0041), with APQC's attribution.

It only adds terms and shapes, so it is a minor release; the decision owner approved cutting it (APPROVAL below).
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

import build_core_next as prev

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
BASE = os.path.join(ONTOLOGY, "releases", "core", "2.0.0")
MAPPING = os.path.join(ONTOLOGY, "releases", "core", "1.0.0", "canonical-facts.csv")
CONTROLLED = os.path.join(ONTOLOGY, "validation", "controlled-values.ttl")
CHANGELOG = os.path.join(ONTOLOGY, "releases", "core", "CHANGELOG-2.1.0.md")
VERSION, ISSUED = "2.1.0", "2026-10-18"
# The sentence that approved cutting the release: (saved file, the decision owner's words in its body).
APPROVAL = ("step4/review-evidence/decision-owner-answers/answers-2026-10-18-night.md", "Yes, cut 2.1.0 (Recommended)")
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", VERSION)

CORE = prev.CORE
PROC = prev.PROC
FACT = Namespace("https://w3id.org/lsc/ontology/fact/")
ONTOLOGY_IRI = prev.ONTOLOGY_IRI
DECIDED = "EPM-DEC-001-0044; the decision owner's words in step4/review-evidence/decision-owner-answers/answers-2026-10-18.md"
REL_ID = re.compile(r"^REL-[0-9]{5}$")
RIGHTS = ("© LSC. All rights reserved. Proprietary (EPM-DEC-001-0041). "
          "This work is based in part on an Industry Process Classification Framework (\"PCF\"), an open standard "
          "developed by APQC and IBM to promote benchmarking and best practices worldwide. The PCF is intended to "
          "facilitate organizational improvement through process management and benchmarking, regardless of industry, "
          "size, or geography. To download the full PCF or other industry-specific versions of the PCF, as well as "
          "associated measures and benchmarking, please visit www.apqc.org/pcf. "
          "©2025 APQC and IBM. The PCF is licensed perpetually, worldwide, royalty-free for use, copying, publication, "
          "modification, and derivative works, provided this notice and the attribution above travel with all copies.")


def en(text):
    return Literal(text, lang="en")


def mapping(path=MAPPING):
    """The canonical-fact mapping: one row per fact, (subject IRI, predicate IRI, object IRI, REL IDs)."""
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            ids = r["row_ids"].split(";")
            if not ids or any(not REL_ID.match(i) for i in ids) or len(set(ids)) != len(ids):
                sys.exit(f"canonical-facts.csv: bad row IDs {r['row_ids']!r}")
            prefix, local = r["predicate"].split(":")
            if prefix != "core":
                sys.exit(f"canonical-facts.csv: predicate {r['predicate']!r} is not a core term")
            rows.append((URIRef(PROC + r["subject"]), CORE[local], URIRef(PROC + r["object"]), ids))
    return rows


def predicates(rows):
    return sorted({p for _, p, _, _ in rows})


def fact_iri(s, p, o):
    return FACT[f"{str(s)[len(PROC):]}--{str(p)[len(str(CORE)):]}--{str(o)[len(PROC):]}"]


def vocabulary(g, preds):
    c = CORE.CanonicalFact
    g.add((c, RDF.type, OWL.Class))
    g.add((c, RDFS.label, en("canonical fact")))
    g.add((c, SKOS.definition, en("One relationship fact between two processes, as a node that names its subject, "
                                  "predicate and object and carries the workbook rows that support it. The direct "
                                  "triple stays; the node is its evidence record.")))
    g.add((c, DCTERMS.bibliographicCitation, en(DECIDED)))
    for name, label, rng, definition in (
            ("factSubject", "fact subject", SKOS.Concept, "The process the fact is about: the subject of its direct triple."),
            ("factPredicate", "fact predicate", RDF.Property, "The relationship the fact states: the predicate of its direct triple, one of the nine canonical relationship predicates."),
            ("factObject", "fact object", SKOS.Concept, "The process at the other end: the object of its direct triple.")):
        q = CORE[name]
        g.add((q, RDF.type, OWL.ObjectProperty))
        g.add((q, RDFS.label, en(label)))
        g.add((q, RDFS.domain, c))
        g.add((q, RDFS.range, rng))
        g.add((q, SKOS.definition, en(definition)))
        g.add((q, DCTERMS.bibliographicCitation, en(DECIDED)))
    q = CORE.evidenceRow
    g.add((q, RDF.type, OWL.DatatypeProperty))
    g.add((q, RDFS.label, en("evidence row")))
    g.add((q, RDFS.domain, c))
    g.add((q, RDFS.range, XSD.string))
    g.add((q, SKOS.definition, en("A relationship-workbook row (REL ID) that supports the fact. A fact carries every "
                                  "distinct row that supports it. Not core:sourceRow, whose domain is the scoped sequence.")))
    g.add((q, DCTERMS.bibliographicCitation, en(DECIDED)))


def build(rows=None):
    rows = mapping() if rows is None else rows
    g = Graph()
    g.parse(os.path.join(BASE, "core.ttl"))
    preds = predicates(rows)
    # The mapping and the released direct triples must be the same set before any node is added.
    direct = {(s, p, o) for p in preds for s, o in g.subject_objects(p)}
    mapped = {(s, p, o) for s, p, o, _ in rows}
    if direct != mapped or len(mapped) != len(rows):
        sys.exit(f"core 2.0.0 and the mapping differ: {len(direct - mapped)} triples unmapped, "
                 f"{len(mapped - direct)} mapped triples missing, {len(rows) - len(mapped)} duplicate rows")
    vocabulary(g, preds)
    for s, p, o, ids in rows:
        f = fact_iri(s, p, o)
        g.add((f, RDF.type, CORE.CanonicalFact))
        g.add((f, CORE.factSubject, s))
        g.add((f, CORE.factPredicate, p))
        g.add((f, CORE.factObject, o))
        for i in ids:
            g.add((f, CORE.evidenceRow, Literal(i)))
    # Rights: the 2.0.0 header names a licence IRI that no file describes.
    g.remove((ONTOLOGY_IRI, DCTERMS.license, None))
    g.add((ONTOLOGY_IRI, DCTERMS.rights, en(RIGHTS)))
    for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion):
        g.remove((ONTOLOGY_IRI, p, None))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(VERSION)))
    g.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{VERSION}")))
    g.add((ONTOLOGY_IRI, OWL.priorVersion, URIRef(f"{ONTOLOGY_IRI}/2.0.0")))
    g.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    counts = Counter({"canonical facts": len(rows), "evidence rows": sum(len(r[3]) for r in rows),
                      "facts with two or more rows": sum(len(r[3]) > 1 for r in rows)})
    for _, p, _, _ in rows:
        counts[f"facts {str(p)[len(str(CORE)):]}"] += 1
    return g, counts


def evidence_problems(g, rows):
    """Each fact node's rows must equal the mapping's rows for that exact fact, and every node must be
    one of the mapping's facts. A well-formed REL ID on the wrong fact is a problem."""
    want = {fact_iri(s, p, o): ((s, p, o), set(ids)) for s, p, o, ids in rows}
    problems = []
    for f in sorted(g.subjects(RDF.type, CORE.CanonicalFact)):
        if f not in want:
            problems.append(f"{f}: not a fact of the mapping")
            continue
        (s, p, o), ids = want[f]
        if (g.value(f, CORE.factSubject), g.value(f, CORE.factPredicate), g.value(f, CORE.factObject)) != (s, p, o):
            problems.append(f"{f}: its ends differ from the mapping")
        got = {str(i) for i in g.objects(f, CORE.evidenceRow)}
        if got != ids:
            problems.append(f"{f}: evidence rows {sorted(got)} != mapping {sorted(ids)}")
    problems += [f"{f}: no node" for f in sorted(set(want) - set(g.subjects(RDF.type, CORE.CanonicalFact)))]
    return problems


def fact_shapes(preds):
    """The canonical-fact shapes, as fixed text so the file is the same on every build."""
    values = ", ".join(f"<{p}>" for p in preds)
    inlist = " ".join(f"core:{str(p)[len(str(CORE)):]}" for p in preds)
    return f"""
# ---- Added in 2.1.0: evidence on canonical facts (EPM-DEC-001-0044) ----
# The decision owner's seven checks: fact structure, predicate scope, triple to node, node to triple, evidence
# presence, evidence correctness and reproducibility. The shapes cover the first five; evidence
# correctness against the mapping and reproducibility are build checks (build_core_2_1.py,
# evidence_problems and --verify) and tests (test_build_core_2_1.py).
@prefix core: <https://w3id.org/lsc/ontology/modules/core/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix shp: <https://w3id.org/lsc/ontology/modules/core/shapes/> .

shp:CanonicalFact a sh:NodeShape ;
    sh:targetClass core:CanonicalFact ;
    sh:nodeKind sh:IRI ;
    sh:property shp:CanonicalFact-factSubject, shp:CanonicalFact-factPredicate, shp:CanonicalFact-factObject,
        shp:CanonicalFact-evidenceRow ;
    sh:sparql shp:CanonicalFact-hasDirectTriple .

shp:CanonicalFact-factSubject sh:path core:factSubject ; sh:minCount 1 ; sh:maxCount 1 ; sh:class skos:Concept ;
    sh:message "A canonical fact names exactly one subject, a concept." .
shp:CanonicalFact-factPredicate sh:path core:factPredicate ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:in ( {inlist} ) ;
    sh:message "A canonical fact names exactly one of the canonical relationship predicates." .
shp:CanonicalFact-factObject sh:path core:factObject ; sh:minCount 1 ; sh:maxCount 1 ; sh:class skos:Concept ;
    sh:message "A canonical fact names exactly one object, a concept." .
shp:CanonicalFact-evidenceRow sh:path core:evidenceRow ; sh:minCount 1 ; sh:datatype xsd:string ;
    sh:pattern "^REL-[0-9]{{5}}$" ;
    sh:message "A canonical fact carries at least one workbook row ID (REL-nnnnn)." .

shp:CanonicalFact-hasDirectTriple a sh:SPARQLConstraint ;
    sh:message "A canonical fact describes a direct triple that the graph holds." ;
    sh:select \"\"\"
        SELECT $this WHERE {{
            $this <{CORE}factSubject> ?s ; <{CORE}factPredicate> ?p ; <{CORE}factObject> ?o .
            FILTER NOT EXISTS {{ ?s ?p ?o }}
        }}\"\"\" .

shp:CanonicalTriple a sh:NodeShape ;
    sh:targetSubjectsOf {", ".join(f"core:{str(p)[len(str(CORE)):]}" for p in preds)} ;
    sh:sparql shp:CanonicalTriple-hasOneFact, shp:CanonicalTriple-noSecondFact .

shp:CanonicalTriple-hasOneFact a sh:SPARQLConstraint ;
    sh:message "Every canonical relationship triple has a canonical fact node." ;
    sh:select \"\"\"
        SELECT $this ?value WHERE {{
            $this ?p ?value .
            FILTER (?p IN ({values}))
            FILTER NOT EXISTS {{
                ?f a <{CORE}CanonicalFact> ; <{CORE}factSubject> $this ; <{CORE}factPredicate> ?p ; <{CORE}factObject> ?value .
            }}
        }}\"\"\" .

shp:CanonicalTriple-noSecondFact a sh:SPARQLConstraint ;
    sh:message "A canonical relationship triple has exactly one canonical fact node." ;
    sh:select \"\"\"
        SELECT $this ?value WHERE {{
            $this ?p ?value .
            FILTER (?p IN ({values}))
            ?f1 <{CORE}factSubject> $this ; <{CORE}factPredicate> ?p ; <{CORE}factObject> ?value .
            ?f2 <{CORE}factSubject> $this ; <{CORE}factPredicate> ?p ; <{CORE}factObject> ?value .
            FILTER (?f1 != ?f2)
        }}\"\"\" .
"""


def shapes_text(preds):
    """2.0.0's shapes file unchanged, then the controlled-value shapes as approved, then the fact shapes."""
    with open(os.path.join(BASE, "shapes.ttl")) as f:
        base = f.read()
    with open(CONTROLLED) as f:
        controlled = f.read()
    return (base + "\n# ---- Added in 2.1.0: the controlled-value shapes (EPM-DEC-001-0035, 0044), as the decision owner approved them ----\n"
            + controlled + fact_shapes(preds))


def shapes(preds):
    return Graph().parse(data=shapes_text(preds), format="turtle")


def catalog():
    base = f"{ONTOLOGY_IRI}/releases/{VERSION}"
    g = Graph()
    g.bind("dcat", prev.DCAT)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{ONTOLOGY_IRI}/{VERSION}")
    g.add((cat, RDF.type, prev.DCAT.Catalog))
    g.add((cat, prev.DCAT.dataset, dataset))
    g.add((dataset, RDF.type, prev.DCAT.Dataset))
    g.add((dataset, DCTERMS.title, en(f"LSC Core Process Ontology {VERSION}")))
    g.add((dataset, DCTERMS.isVersionOf, ONTOLOGY_IRI))
    g.add((dataset, OWL.versionInfo, Literal(VERSION)))
    g.add((dataset, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((dataset, DCTERMS.rights, en(RIGHTS)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"), ("shapes.ttl", "text/turtle"),
                        ("canonical-facts.csv", "text/csv")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, prev.DCAT.distribution, dist))
        g.add((dist, RDF.type, prev.DCAT.Distribution))
        g.add((dist, prev.DCAT.downloadURL, dist))
        g.add((dist, prev.DCAT.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(g, preds, counts):
    with open(MAPPING) as f:
        mapping_text = f.read()
    files = {"core.ttl": g.serialize(format="turtle"), "core.jsonld": prev.jsonld(g), "shapes.ttl": shapes_text(preds),
             "catalog.ttl": catalog(), "canonical-facts.csv": mapping_text,
             "counts.json": json.dumps(dict(sorted(counts.items())), indent=2) + "\n"}
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(os.path.join(BASE, "manifest.json")) as f:
        base_manifest = f.read()
    files["manifest.json"] = json.dumps({
        "module": "core", "version": VERSION, "release_candidate": False,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{VERSION}",
        "built_from": {"core 2.0.0 manifest": hashlib.sha256(base_manifest.encode()).hexdigest(),
                       "canonical-fact mapping (core 1.0.0)": hashlib.sha256(mapping_text.encode()).hexdigest(),
                       "controlled-value shapes": hashlib.sha256(open(CONTROLLED, "rb").read()).hexdigest()},
        "decisions": ["EPM-DEC-001-0035", "EPM-DEC-001-0041", "EPM-DEC-001-0044"],
        "approval": {"file": APPROVAL[0], "words": APPROVAL[1]},
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows = mapping()
    g, counts = build(rows)
    problems = evidence_problems(g, rows)
    if problems:
        sys.exit("evidence does not match the mapping:\n  " + "\n  ".join(problems[:20]))
    preds = predicates(rows)
    conforms, _, text = validate(g, shacl_graph=shapes(preds), advanced=True)
    if not conforms:
        sys.exit(f"core {VERSION} fails its shapes:\n" + text)
    files = package(g, preds, counts)
    print(f"core {VERSION}: {len(g)} triples; shapes conform; evidence matches the mapping; "
          + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if args.verify:
        stale = [n for n, t in files.items() if not os.path.exists(os.path.join(RELEASE_DIR, n))
                 or open(os.path.join(RELEASE_DIR, n)).read() != t]
        if stale:
            sys.exit(f"core {VERSION} package is not current: {stale}")
        print("release package is current")
    if args.write:
        os.makedirs(RELEASE_DIR, exist_ok=True)
        for n, t in files.items():
            with open(os.path.join(RELEASE_DIR, n), "w") as f:
                f.write(t)
        print(f"wrote {RELEASE_DIR}")


if __name__ == "__main__":
    main()
