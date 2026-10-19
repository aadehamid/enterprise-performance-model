"""Build the release package of a module other than core (Step 10; EPM-DEC-001-0018, EPM-DEC-001-0037).

    python3 build_module.py organization            # build, validate, print the figures
    python3 build_module.py organization --write    # write releases/organization/<version>/
    python3 build_module.py organization --verify   # fail unless the written package equals a fresh build

The package holds the module's Turtle and JSON-LD, its shapes, a DCAT record, its changelog and a
manifest with each file's SHA-256, the shape of the core 1.0.0 package (EPM-DEC-001-0029). A release
candidate (a stage such as "rc.1") carries no issued date: a module's first release is a major, and
a major needs Hamid's approval (module policy, 2026-09-18). An issued release names where his
approval is recorded; the tests check that the words are there.
"""
import argparse
import hashlib
import json
import os
import sys

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
MODULES_NS = "https://w3id.org/lsc/ontology/modules/"
DCAT = Namespace("http://www.w3.org/ns/dcat#")

# One entry per module. Paths are relative to business_architecture/ontology/.
MODULES = {
    "organization": {
        "title": "LSC Organization Module",
        "description": "Roles, RACI responsibility assignments and control between legal entities (Step 5).",
        # 2.0.0 carries Hamid's role answers: three roles deprecated, their assignments moved
        # (EPM-DEC-001-0045). 1.0.0 stays on disk as released; test_build_module.py checks it is untouched.
        "version": "2.0.0", "stage": None, "issued": "2026-10-18",
        "approval": ("step4/review-evidence/hamid-answers/answers-2026-10-18-night.md", "Yes, approve 2.0.0 (Recommended)"),
        "parts": ["organization/vocabulary.ttl", "organization/roles.ttl", "organization/assignments.ttl"],
        "shapes": ["organization/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.0.0"},
        "decisions": ["EPM-DEC-001-0030", "EPM-DEC-001-0031", "EPM-DEC-001-0032", "EPM-DEC-001-0045"],
    },
    "ref-mpc": {
        "title": "LSC Reference Instances: Marathon Petroleum Corporation",
        "description": "Public reference facts about MPC and MPLX, each with a source and an as-of date (Step 5).",
        "version": "1.0.0", "stage": None, "issued": "2026-10-13",
        "approval": ("step4/review-evidence/hamid-answers/answers-2026-10-13-session2.md", "aprove now"),
        "parts": ["ref-mpc/ref-mpc.ttl"],
        "shapes": ["ref-mpc/shapes.ttl", "organization/shapes.ttl"],
        "depends_on": ["organization"],
        # ref-mpc 1.0.0 was released against organization 1.0.0 and is not re-released: organization
        # 2.0.0 deprecates three roles and changes nothing ref-mpc uses (EPM-DEC-001-0045).
        "pins": {"organization": "1.0.0"},
        "decisions": ["EPM-DEC-001-0015", "EPM-DEC-001-0033"],
    },
}


RELEASED = {"core": "1.0.0"}  # released modules this builder does not build


def label(m):
    return m["version"] if m["stage"] is None else f"{m['version']}-{m['stage']}"


def dependencies(name):
    """Each dependency with the version this package is built against: a released version, or the
    dependency's own current candidate, so a candidate never names a release that does not exist."""
    pins = MODULES[name].get("pins", {})
    return {d: pins.get(d) or RELEASED.get(d) or label(MODULES[d]) for d in MODULES[name]["depends_on"]}


def parse(paths):
    g = Graph()
    for p in paths:
        g.parse(os.path.join(ONTOLOGY, p))
    return g


def build(name):
    m = MODULES[name]
    iri, lab = URIRef(MODULES_NS + name), label(m)
    g = parse(m["parts"])
    for prefix, ns in (("dcterms", DCTERMS), ("owl", OWL)):
        g.bind(prefix, ns)
    # The ontology header names the version; the module refers to others by IRI and imports none.
    g.remove((iri, None, None))
    g.add((iri, RDF.type, OWL.Ontology))
    g.add((iri, DCTERMS.title, Literal(m["title"], lang="en")))
    g.add((iri, DCTERMS.description, Literal(m["description"], lang="en")))
    g.add((iri, OWL.versionInfo, Literal(lab)))
    g.add((iri, OWL.versionIRI, URIRef(f"{iri}/{lab}")))
    for dep, version in sorted(dependencies(name).items()):
        g.add((iri, DCTERMS.requires, URIRef(f"{MODULES_NS}{dep}/{version}")))
    if m["issued"]:
        # Issued and modified dates on every release, both the issue date at the cut (playbook
        # Step 10; build_core.py does the same for core).
        g.add((iri, DCTERMS.issued, Literal(m["issued"], datatype=XSD.date)))
        g.add((iri, DCTERMS.modified, Literal(m["issued"], datatype=XSD.date)))
    return g


def check(name, g):
    """The module's shapes over the module, with the released packages it depends on loaded: core for
    the concepts organization refers to, and the pinned organization release for ref-mpc."""
    m = MODULES[name]
    data = Graph()
    data += g
    deps = dependencies(name)
    if "core" in deps:
        data.parse(os.path.join(ONTOLOGY, "releases", "core", deps["core"], "core.ttl"))
    if "organization" in deps:
        data.parse(os.path.join(ONTOLOGY, "releases", "organization", deps["organization"], "organization.ttl"))
        data.parse(os.path.join(ONTOLOGY, "releases", "core", "1.0.0", "core.ttl"))
    conforms, _, text = validate(data, shacl_graph=parse(m["shapes"]))
    return conforms, text


def jsonld(g):
    """JSON-LD with nodes, keys and values in a fixed order, so a rebuild is byte-identical (as for core)."""
    data = json.loads(g.serialize(format="json-ld"))
    nodes = data if isinstance(data, list) else data.get("@graph", [data])
    for node in nodes:
        for key, value in node.items():
            if isinstance(value, list):
                node[key] = sorted(value, key=lambda v: json.dumps(v, sort_keys=True))
    nodes.sort(key=lambda n: n.get("@id", ""))
    return json.dumps(nodes, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def catalog(name):
    m = MODULES[name]
    iri, lab = MODULES_NS + name, label(m)
    base = f"{iri}/releases/{lab}"
    g = Graph()
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{iri}/{lab}")
    g.add((cat, RDF.type, DCAT.Catalog))
    g.add((cat, DCAT.dataset, dataset))
    g.add((dataset, RDF.type, DCAT.Dataset))
    g.add((dataset, DCTERMS.title, Literal(f"{m['title']} {lab}", lang="en")))
    g.add((dataset, DCTERMS.isVersionOf, URIRef(iri)))
    g.add((dataset, OWL.versionInfo, Literal(lab)))
    if m["issued"]:
        g.add((dataset, DCTERMS.issued, Literal(m["issued"], datatype=XSD.date)))
    for fname, media in ((f"{name}.ttl", "text/turtle"), (f"{name}.jsonld", "application/ld+json"),
                         ("shapes.ttl", "text/turtle")):
        dist = URIRef(f"{base}/{fname}")
        g.add((dataset, DCAT.distribution, dist))
        g.add((dist, RDF.type, DCAT.Distribution))
        g.add((dist, DCAT.downloadURL, dist))
        g.add((dist, DCAT.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(name, g):
    m = MODULES[name]
    lab = label(m)
    shapes = parse(m["shapes"][:1])
    files = {f"{name}.ttl": g.serialize(format="turtle"), f"{name}.jsonld": jsonld(g),
             "shapes.ttl": shapes.serialize(format="turtle"), "catalog.ttl": catalog(name)}
    with open(os.path.join(ONTOLOGY, "releases", name, "CHANGELOG.md")) as f:
        files["CHANGELOG.md"] = f.read()
    files["manifest.json"] = json.dumps({
        "module": name, "version": lab, "release_candidate": m["stage"] is not None,
        "ontology_iri": MODULES_NS + name, "version_iri": f"{MODULES_NS}{name}/{lab}",
        "depends_on": dependencies(name), "decisions": m["decisions"], "triples": len(g),
        "approved_by": None if m["stage"] else {"who": "Hamid", "recorded_in": m["approval"][0]},
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def release_dir(name):
    return os.path.join(ONTOLOGY, "releases", name, label(MODULES[name]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module", choices=sorted(MODULES))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    g = build(args.module)
    conforms, text = check(args.module, g)
    if not conforms:
        sys.exit(f"{args.module}: the shapes fail:\n{text}")
    files = package(args.module, g)
    out = release_dir(args.module)
    print(f"{args.module} {label(MODULES[args.module])}: {len(g)} triples; shapes conform")
    if args.verify:
        stale = [n for n, t in files.items()
                 if not os.path.exists(os.path.join(out, n)) or open(os.path.join(out, n)).read() != t]
        if stale:
            sys.exit(f"{args.module} release package is not current: {stale}")
        print("release package is current")
    if args.write:
        os.makedirs(out, exist_ok=True)
        for n, t in files.items():
            with open(os.path.join(out, n), "w") as f:
                f.write(t)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
