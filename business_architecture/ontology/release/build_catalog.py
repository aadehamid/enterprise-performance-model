"""Build releases/catalog.ttl, one DCAT catalog of every release (Step 10; EPM-DEC-001-0082).

    python3 build_catalog.py            # build and print the figures
    python3 build_catalog.py --write    # write releases/catalog.ttl
    python3 build_catalog.py --verify   # fail unless the written catalog equals a fresh build

Each release package carries its own catalog.ttl, a record of that one release in the catalog
<https://w3id.org/lsc/ontology/catalog>. This catalog is their union, read from the packages on disk,
plus the catalog's own title and description. It adds nothing about a release that its package does
not say. The namespace is not hosted (EPM-DEC-001-0039), so the catalog's IRIs do not resolve yet.
"""
import argparse
import glob
import os
import sys

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF

HERE = os.path.dirname(os.path.abspath(__file__))
RELEASES = os.path.join(HERE, "..", "releases")
OUT = os.path.join(RELEASES, "catalog.ttl")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
CATALOG = URIRef("https://w3id.org/lsc/ontology/catalog")


def package_catalogs():
    return sorted(glob.glob(os.path.join(RELEASES, "*", "*", "catalog.ttl")))


def build():
    g = Graph()
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    for path in package_catalogs():
        g.parse(path)
    g.add((CATALOG, RDF.type, DCAT.Catalog))
    g.add((CATALOG, DCTERMS.title, Literal("LSC Ontology Release Catalog", lang="en")))
    g.add((CATALOG, DCTERMS.description, Literal(
        "Every release of the LSC ontology modules, one dataset per release, read from each package's own "
        "catalog record.", lang="en")))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    g = build()
    text = g.serialize(format="turtle")
    print(f"catalog: {len(set(g.objects(CATALOG, DCAT.dataset)))} releases from {len(package_catalogs())} packages")
    if args.verify:
        if not os.path.exists(OUT) or open(OUT).read() != text:
            sys.exit("releases/catalog.ttl is not current: run build_catalog.py --write")
        print("releases/catalog.ttl is current")
    if args.write:
        with open(OUT, "w") as f:
            f.write(text)
        print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
