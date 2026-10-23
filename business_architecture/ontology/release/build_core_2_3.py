"""Build core 2.3.0 from the released core 2.2.0 (EPM-DEC-001-0089).

    python3 build_core_2_3.py            # build, validate, print the figures
    python3 build_core_2_3.py --write    # write releases/core/2.3.0/
    python3 build_core_2_3.py --verify   # fail unless the written package equals a fresh build

core 2.2.0 stays as it was released (build_core_2_2.py). This builder starts from that graph and
applies the one process-map change merged since 2.2.0 was built: MPC-P10.1, CM 1.3.7.1.7 Coordinate
Customer Onboarding (EPM-DEC-001-0087), read from the map at a pinned commit. The new concept is
shaped as 2.2.0's new concepts are (build_core_2_2.py, item 1). Any other map change since 2.2.0
stops the build.

It adds a concept and removes no IRI, so it is a minor release; the decision owner approved it
(APPROVAL below; EPM-DEC-001-0088).
"""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS, XSD

import build_core_2_2 as prev

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
BASE = os.path.join(ONTOLOGY, "releases", "core", "2.2.0")
SOURCE_PATH = prev.SOURCE_PATH
# The map as 2.2.0 was built from it, and the map as 2.3.0 is built from it: the merge of the pull
# request that added CM 1.3.7.1.7, the last change to the map on main before this release.
EARLIER_COMMIT = prev.SOURCE_COMMIT
SOURCE_COMMIT = "c351ef0ecb1e3cbe6af38f46f66065499c73442f"
CHANGELOG = os.path.join(ONTOLOGY, "releases", "core", "CHANGELOG-2.3.0.md")
VERSION, ISSUED = "2.3.0", "2026-10-23"
# The sentence that approved the release: (saved file, the decision owner's words in its body).
APPROVAL = ("step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md", "Approve all six (Recommended)")
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", VERSION)

CORE, PROC, ONTOLOGY_IRI, SCHEME = prev.CORE, prev.PROC, prev.ONTOLOGY_IRI, prev.SCHEME
# The one node this release adds, and the record that added it.
ADDED_BY = {"CM 1.3.7.1.7": "EPM-DEC-001-0087 (MPC-P10.1, customer onboarding)"}


def en(text):
    return Literal(text, lang="en")


def build():
    g = Graph()
    g.parse(os.path.join(BASE, "core.ttl"))
    new, ids, descriptions = prev.changes(base=g, earlier=prev.map_nodes(EARLIER_COMMIT),
                                          current=prev.map_nodes(SOURCE_COMMIT))
    if ids or descriptions or sorted(node["id"] for _, node, _ in new) != sorted(ADDED_BY):
        sys.exit(f"the map changed more than MPC-P10.1 since 2.2.0: new {[n['id'] for _, n, _ in new]}, "
                 f"IDs {ids}, descriptions {[d[0] for d in descriptions]}")
    for slug, node, parent in new:
        s = URIRef(PROC + slug)
        if node.get("sioc"):
            sys.exit(f"{node['id']}: a SIPOC field on a new node needs the 2.0.0 planned-flow mapping")
        if (URIRef(PROC + parent), RDF.type, SKOS.Concept) not in g:
            sys.exit(f"{slug}: its parent {parent} is not a concept")
        definition, scope = prev.split_description(node["description"])
        g.add((s, RDF.type, SKOS.Concept))
        g.add((s, SKOS.prefLabel, en(node["name"])))
        g.add((s, SKOS.notation, Literal(node["id"])))
        g.add((s, SKOS.definition, en(definition)))
        if scope:
            g.add((s, SKOS.scopeNote, en(scope)))
        g.add((s, SKOS.broader, URIRef(PROC + parent)))
        g.add((s, SKOS.inScheme, SCHEME))
        g.add((s, CORE.taxonomyLevel, Literal(node["level"])))
        g.add((s, DCTERMS.provenance, en(
            f"Added in core 2.3.0 from the process map at commit {SOURCE_COMMIT[:7]}, by {ADDED_BY[node['id']]}; "
            "definition and scope note from the map's description (EPM-DEC-001-0089).")))
    for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion):
        g.remove((ONTOLOGY_IRI, p, None))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(VERSION)))
    g.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{VERSION}")))
    g.add((ONTOLOGY_IRI, OWL.priorVersion, URIRef(f"{ONTOLOGY_IRI}/2.2.0")))
    g.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    with open(os.path.join(BASE, "counts.json")) as f:
        counts = Counter(json.load(f))
    counts["process concepts"] = sum(1 for s in g.subjects(RDF.type, SKOS.Concept) if str(s).startswith(PROC))
    counts["new concepts"] = len(new)
    for k in ("IDs on stubs", "changed descriptions", "19948 references rejected", "19948 references confirmed"):
        del counts[k]  # 2.2.0's changes; this release makes none of them
    return g, counts


def catalog():
    base = f"{ONTOLOGY_IRI}/releases/{VERSION}"
    dcat = prev.prev.prev.DCAT
    g = Graph()
    g.bind("dcat", dcat)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{ONTOLOGY_IRI}/{VERSION}")
    g.add((cat, RDF.type, dcat.Catalog))
    g.add((cat, dcat.dataset, dataset))
    g.add((dataset, RDF.type, dcat.Dataset))
    g.add((dataset, DCTERMS.title, en(f"LSC Core Process Ontology {VERSION}")))
    g.add((dataset, DCTERMS.isVersionOf, ONTOLOGY_IRI))
    g.add((dataset, OWL.versionInfo, Literal(VERSION)))
    g.add((dataset, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((dataset, DCTERMS.rights, en(prev.prev.RIGHTS)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"), ("shapes.ttl", "text/turtle"),
                        ("canonical-facts.csv", "text/csv")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, dcat.distribution, dist))
        g.add((dist, RDF.type, dcat.Distribution))
        g.add((dist, dcat.downloadURL, dist))
        g.add((dist, dcat.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(g, counts):
    """2.2.0's shapes and canonical-fact mapping unchanged; the graph, catalog, counts and changelog new."""
    with open(os.path.join(BASE, "shapes.ttl")) as f:
        shapes_text = f.read()
    with open(os.path.join(BASE, "canonical-facts.csv")) as f:
        mapping_text = f.read()
    files = {"core.ttl": g.serialize(format="turtle"), "core.jsonld": prev.prev.prev.jsonld(g), "shapes.ttl": shapes_text,
             "catalog.ttl": catalog(), "canonical-facts.csv": mapping_text,
             "counts.json": json.dumps(dict(sorted(counts.items())), indent=2) + "\n"}
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(os.path.join(BASE, "manifest.json")) as f:
        base_manifest = f.read()
    files["manifest.json"] = json.dumps({
        "module": "core", "version": VERSION, "release_candidate": False,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{VERSION}",
        "built_from": {"core 2.2.0 manifest": hashlib.sha256(base_manifest.encode()).hexdigest(),
                       "process map": f"{SOURCE_PATH} at {SOURCE_COMMIT}"},
        "decisions": ["EPM-DEC-001-0087", "EPM-DEC-001-0088", "EPM-DEC-001-0089"],
        "approval": {"file": APPROVAL[0], "words": APPROVAL[1]},
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    g, counts = build()
    conforms, _, text = validate(g, shacl_graph=Graph().parse(os.path.join(BASE, "shapes.ttl")), advanced=True)
    if not conforms:
        sys.exit(f"core {VERSION} fails its shapes:\n" + text)
    files = package(g, counts)
    print(f"core {VERSION}: {len(g)} triples; shapes conform; process concepts {counts['process concepts']}, "
          f"new concepts {counts['new concepts']}")
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
