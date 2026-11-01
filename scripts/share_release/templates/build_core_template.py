"""Build the next core release: one or more added processes. Copy this file to build_core_<major>_<minor>.py and fill in
the block marked FILL IN. It follows build_core_2_3.py, the builder that added a node. For a change to an existing
node's ID or description, read build_core_2_2.py, which applies those; this file stops on them.

    python3 build_core_<major>_<minor>.py --write    # write releases/core/<version>/
    python3 build_core_<major>_<minor>.py --verify   # fail unless the written package equals a fresh build
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

import build_core_2_1 as b21
import build_core_2_2 as maps
import build_core_next as first
import frozen_sources
import newest

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)

# --- FILL IN ---------------------------------------------------------------------------------------------------------
VERSION, ISSUED = "X.Y.Z", "YYYY-MM-DD"
BASE_VERSION = "X.Y.Z"  # the core release this one starts from
# The two copies of the process map to compare, each named by the commit that holds it (or any label of 12 or more
# letters and digits in a plain folder). Each has a file in release/frozen/: <first 12 characters>-downstream_process_map.json
EARLIER_COMMIT = "the-commit-you-started-from"
SOURCE_COMMIT = "the-commit-that-changed-the-map"
APPROVAL = ("where the approval is recorded", "the sentence that approved this release")
DECISIONS = ["your decision record"]
# Each added node: its ID -> (its fields in the map beyond the description, its parent's slug).
APPROVED_NODE = {"CM 9.9.9": ({"id": "CM 9.9.9", "level": 3, "name": "The process's name"}, "CM-9-9")}
# ---------------------------------------------------------------------------------------------------------------------

BASE = frozen_sources.package_dir(ONTOLOGY, "core", BASE_VERSION)
CHANGELOG = os.path.join(ONTOLOGY, "releases", "core", f"CHANGELOG-{VERSION}.md")
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", VERSION)
CORE, PROC, ONTOLOGY_IRI, SCHEME = maps.CORE, maps.PROC, maps.ONTOLOGY_IRI, maps.SCHEME
# What an earlier core release counted of its own changes; this release does not repeat them.
EARLIER_COUNTS = ("renamed concepts", "alternative labels moved", "code-list top concepts", "IDs on stubs",
                  "changed descriptions", "19948 references rejected", "19948 references confirmed")


def en(text):
    return Literal(text, lang="en")


def build():
    g = Graph()
    g.parse(os.path.join(BASE, "core.ttl"))
    new, ids, descriptions = maps.changes(base=g, earlier=maps.map_nodes(EARLIER_COMMIT), current=maps.map_nodes(SOURCE_COMMIT))
    if ids or descriptions or sorted(node["id"] for _, node, _ in new) != sorted(APPROVED_NODE):
        sys.exit(f"the map changed more than APPROVED_NODE says: new {[n['id'] for _, n, _ in new]}, IDs {ids}, "
                 f"descriptions {[d[0] for d in descriptions]}")
    for slug, node, parent in new:
        s = URIRef(PROC + slug)
        fields, approved_parent = APPROVED_NODE[node["id"]]
        if {k: v for k, v in node.items() if k != "description"} != fields or parent != approved_parent \
                or not node.get("description"):
            sys.exit(f"{node['id']}: its map fields or parent differ from APPROVED_NODE: {node}, parent {parent}")
        if (URIRef(PROC + parent), RDF.type, SKOS.Concept) not in g:
            sys.exit(f"{slug}: its parent {parent} is not a concept")
        definition, scope = maps.split_description(node["description"])
        g.add((s, RDF.type, SKOS.Concept))
        g.add((s, SKOS.prefLabel, en(node["name"])))
        g.add((s, SKOS.notation, Literal(node["id"])))
        g.add((s, SKOS.definition, en(definition)))
        if scope:
            g.add((s, SKOS.scopeNote, en(scope)))
        g.add((s, SKOS.broader, URIRef(PROC + parent)))
        g.add((s, SKOS.inScheme, SCHEME))
        g.add((s, CORE.taxonomyLevel, Literal(node["level"])))
        g.add((s, DCTERMS.provenance, en(f"Added in core {VERSION} from the process map; definition and scope note from the map's description.")))
    for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion):
        g.remove((ONTOLOGY_IRI, p, None))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(VERSION)))
    g.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{VERSION}")))
    g.add((ONTOLOGY_IRI, OWL.priorVersion, URIRef(f"{ONTOLOGY_IRI}/{BASE_VERSION}")))
    g.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    with open(os.path.join(BASE, "counts.json")) as f:
        counts = Counter(json.load(f))
    counts["process concepts"] = sum(1 for s in g.subjects(RDF.type, SKOS.Concept) if str(s).startswith(PROC))
    counts["new concepts"] = len(new)
    for key in EARLIER_COUNTS:
        counts.pop(key, None)
    return g, counts


def catalog():
    base = f"{ONTOLOGY_IRI}/releases/{VERSION}"
    dcat = first.DCAT
    g = Graph()
    g.bind("dcat", dcat)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef(str(ONTOLOGY_IRI).split("/modules/")[0] + "/catalog"), URIRef(f"{ONTOLOGY_IRI}/{VERSION}")
    g.add((cat, RDF.type, dcat.Catalog))
    g.add((cat, dcat.dataset, dataset))
    g.add((dataset, RDF.type, dcat.Dataset))
    g.add((dataset, DCTERMS.title, en(f"Core Process Ontology {VERSION}")))
    g.add((dataset, DCTERMS.isVersionOf, ONTOLOGY_IRI))
    g.add((dataset, OWL.versionInfo, Literal(VERSION)))
    g.add((dataset, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((dataset, DCTERMS.rights, en(b21.RIGHTS)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"), ("shapes.ttl", "text/turtle"),
                        ("canonical-facts.csv", "text/csv")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, dcat.distribution, dist))
        g.add((dist, RDF.type, dcat.Distribution))
        g.add((dist, dcat.downloadURL, dist))
        g.add((dist, dcat.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(g, counts):
    """The earlier release's shapes and canonical-fact mapping unchanged; the graph, catalog, counts and changelog new."""
    with open(os.path.join(BASE, "shapes.ttl")) as f:
        shapes_text = f.read()
    with open(os.path.join(BASE, "canonical-facts.csv")) as f:
        mapping_text = f.read()
    files = {"core.ttl": g.serialize(format="turtle"), "core.jsonld": first.jsonld(g), "shapes.ttl": shapes_text,
             "catalog.ttl": catalog(), "canonical-facts.csv": mapping_text,
             "counts.json": json.dumps(dict(sorted(counts.items())), indent=2) + "\n"}
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(os.path.join(BASE, "manifest.json")) as f:
        base_manifest = f.read()
    files["manifest.json"] = json.dumps({
        "module": "core", "version": VERSION, "release_candidate": False,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{VERSION}",
        "built_from": {f"core {BASE_VERSION} manifest": hashlib.sha256(base_manifest.encode()).hexdigest(),
                       "process map": f"{maps.SOURCE_PATH} at {SOURCE_COMMIT}"},
        "decisions": DECISIONS,
        "approval": {"file": APPROVAL[0], "words": APPROVAL[1]},
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--rebuild-released", action="store_true", help="overwrite a released package: a rebuild of the whole set")
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
        newest.refuse_overwrite(RELEASE_DIR, files, f"core {VERSION}", args.rebuild_released)
        os.makedirs(RELEASE_DIR, exist_ok=True)
        for n, t in files.items():
            with open(os.path.join(RELEASE_DIR, n), "w") as f:
                f.write(t)
        print(f"wrote {RELEASE_DIR}")


if __name__ == "__main__":
    main()
