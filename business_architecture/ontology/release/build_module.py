"""Build the release package of a module other than core (Step 10; EPM-DEC-001-0018, EPM-DEC-001-0037).

    python3 build_module.py organization            # build, validate, print the figures
    python3 build_module.py organization --write    # write releases/organization/<version>/
    python3 build_module.py organization --verify   # fail unless the written package equals a fresh build

The package holds the module's Turtle and JSON-LD, its shapes, a DCAT record, its changelog and a
manifest with each file's SHA-256, the shape of the core 1.0.0 package (EPM-DEC-001-0029). A release
candidate (a stage such as "rc.1") carries no issued date: a module's first release is a major, and
a major needs the decision owner's approval (module policy, 2026-09-18). An issued release names where their
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
        # 2.0.0 carries the decision owner's role answers: three roles deprecated, their assignments moved
        # (EPM-DEC-001-0045). Each earlier package stays on disk as released; test_build_module.py
        # checks it is untouched.
        "version": "2.0.0", "stage": None, "issued": "2026-10-18",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-18-night.md", "Yes, approve 2.0.0 (Recommended)"),
        "parts": ["organization/vocabulary.ttl", "organization/roles.ttl", "organization/assignments.ttl"],
        "shapes": ["organization/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.1.0"},
        "decisions": ["EPM-DEC-001-0030", "EPM-DEC-001-0031", "EPM-DEC-001-0032", "EPM-DEC-001-0045"],
    },
    "ref-mpc": {
        "title": "LSC Reference Instances: Marathon Petroleum Corporation",
        "description": "Public reference facts about MPC and MPLX, each with a source and an as-of date (Step 5).",
        # 1.1.0 requires organization 2.0.0; its own content is unchanged (EPM-DEC-001-0045).
        # 1.2.0 adds MPC and MPLX as parties in the party module's terms, moved from party/, and requires
        # party 1.0.0; the decision owner approved it on its own (EPM-DEC-001-0075, EPM-DEC-001-0080).
        "version": "1.2.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-ref-mpc-release.md", "Approve ref-mpc 1.2.0 (Recommended)"),
        "parts": ["ref-mpc/ref-mpc.ttl", "ref-mpc/reference-parties.ttl"],
        "shapes": ["ref-mpc/shapes.ttl", "organization/shapes.ttl", "party/shapes.ttl"],
        "depends_on": ["organization", "party"],
        "pins": {"organization": "2.0.0", "party": "1.0.0"},
        "decisions": ["EPM-DEC-001-0015", "EPM-DEC-001-0033", "EPM-DEC-001-0071", "EPM-DEC-001-0075", "EPM-DEC-001-0080"],
    },
    "kpi": {
        "title": "LSC KPI Module",
        "description": "Measure definitions, classified by kind, with the planning personas who use them and the core processes they inform (Step 7). Definitions only, never values.",
        # 1.0.0 was the module's first release, a major approved by the decision owner (EPM-DEC-001-0043).
        # 1.0.1 is a patch: the planner list's source names VCO DSV (EPM-DEC-001-0040).
        # 1.1.0 is a minor approved with the release plan: the eight measure populations join the package,
        # the measure shape is closed, and it requires core 2.2.0 (EPM-DEC-001-0079).
        "version": "1.1.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved"),
        "parts": ["kpi/vocabulary.ttl", "kpi/measures.ttl", "population/vocabulary.ttl", "population/population.ttl"],
        "shapes": ["kpi/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.2.0"},
        "decisions": ["EPM-DEC-001-0040", "EPM-DEC-001-0042", "EPM-DEC-001-0043", "EPM-DEC-001-0062", "EPM-DEC-001-0079"],
    },
    "party": {
        "title": "LSC Party Module",
        "description": "The Customer domain's concepts: parties, the roles they hold for a period, accounts, agreements and sites; the customer's systems, data flow and attributes; and the customer lifecycle linked to core processes (Steps 5 to 7). Definitions only, never records.",
        # 1.0.0 is the module's first release, a major approved by the decision owner (EPM-DEC-001-0074).
        # The reference parties are reference instances of real companies, which the playbook's module policy
        # puts in their own module, so they are not part of this package. Since 2026-10-22 they are in
        # ref-mpc/reference-parties.ttl (EPM-DEC-001-0075).
        "version": "1.0.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-21-release-playbook.md", "You have my permission to release the stable version when you are done."),
        "parts": ["party/vocabulary.ttl", "party/code-lists.ttl", "party/systems.ttl", "party/lifecycle.ttl"],
        "shapes": ["party/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.1.0"},
        "decisions": ["EPM-DEC-001-0067", "EPM-DEC-001-0068", "EPM-DEC-001-0069", "EPM-DEC-001-0070",
                      "EPM-DEC-001-0071", "EPM-DEC-001-0072", "EPM-DEC-001-0074"],
    },
    # The Step 7 modules' first releases, majors the decision owner approved with the release plan
    # (EPM-DEC-001-0077). Each requires core 2.2.0, the release that holds every process they link.
    "data-product": {
        "title": "LSC Data Product Module",
        "description": "The data products of the portfolio, the product lines and segments that group them, and the processes that produce them (Step 7). Definitions only, never data values; mapped to DCAT, not imported.",
        # 1.1.0 is a minor approved with the close-out releases: the Customer Master data product, produced by
        # CM 1.3.7.1.1 (MPC-P10.3); it requires core 2.3.0 (EPM-DEC-001-0087, 0088, 0091).
        "version": "1.1.0", "stage": None, "issued": "2026-10-23",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md", "Approve all six (Recommended)"),
        "parts": ["data-product/vocabulary.ttl", "data-product/data-products.ttl"],
        "shapes": ["data-product/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.3.0"},
        "decisions": ["EPM-DEC-001-0005", "EPM-DEC-001-0048", "EPM-DEC-001-0053", "EPM-DEC-001-0077", "EPM-DEC-001-0087",
                      "EPM-DEC-001-0088", "EPM-DEC-001-0091"],
    },
    "value-stream": {
        "title": "LSC Value Stream Module",
        "description": "The Commercial Hydrocarbon Lifecycle and Order to Cash value streams: their stages, capabilities and value-stream processes, which realize core processes, produce and consume data products and carry cited measure links (Step 7).",
        # 1.1.0 is a minor the decision owner approved with the close-out releases: the Order to Cash credit
        # review realizes CM 1.3.7.4.2 (MPC-P10.2), and vs:produces and vs:consumes gain rdfs:range skos:Concept;
        # it requires the current core, data-product and kpi releases (EPM-DEC-001-0087, 0088, 0090).
        "version": "1.1.0", "stage": None, "issued": "2026-10-23",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-23-closeout.md", "Approve all six (Recommended)"),
        "parts": ["value-stream/vocabulary.ttl", "value-stream/value-streams.ttl"],
        "shapes": ["value-stream/shapes.ttl"],
        "depends_on": ["core", "data-product", "kpi"],
        # Every dependency pinned: a later kpi or data-product release must not change this package.
        "pins": {"core": "2.3.0", "data-product": "1.0.0", "kpi": "1.1.0"},
        "decisions": ["EPM-DEC-001-0054", "EPM-DEC-001-0077", "EPM-DEC-001-0087", "EPM-DEC-001-0088", "EPM-DEC-001-0090"],
    },
    "system": {
        "title": "LSC System Module",
        "description": "The systems, office tools and working documents the process map names, with their kind and the processes that use them (Step 7).",
        "version": "1.0.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved"),
        "parts": ["system/vocabulary.ttl", "system/systems.ttl"],
        "shapes": ["system/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.2.0"},
        "decisions": ["EPM-DEC-001-0055", "EPM-DEC-001-0077"],
    },
    "lane": {
        "title": "LSC Lane Module",
        "description": "The four office lanes as a code list, and the processes the process map places in them (Step 7).",
        "version": "1.0.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved"),
        "parts": ["lane/vocabulary.ttl", "lane/lanes.ttl"],
        "shapes": ["lane/shapes.ttl"],
        "depends_on": ["core"],
        "pins": {"core": "2.2.0"},
        "decisions": ["EPM-DEC-001-0056", "EPM-DEC-001-0077"],
    },
    "market-data": {
        "title": "LSC Market Data Module",
        "description": "The published series of the crack-spreads measure, from MPC Economics' definition first, with their benchmarks, regions, legs and RIN treatment (Step 7). Definitions only, never prices.",
        "version": "1.0.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved"),
        "parts": ["market-data/vocabulary.ttl", "market-data/market-data.ttl"],
        "shapes": ["market-data/shapes.ttl"],
        "depends_on": ["kpi"],
        "pins": {"kpi": "1.0.1"},
        "decisions": ["EPM-DEC-001-0046", "EPM-DEC-001-0057", "EPM-DEC-001-0066", "EPM-DEC-001-0077"],
    },
    # The integration package's first release, a major the decision owner approved with the release plan
    # (EPM-DEC-001-0078). It packages three small vocabularies, each keeping its own namespace; the package
    # IRI names the release only. The population statements ship in kpi 1.1.0, and the APQC element list
    # stays a reference file (EPM-DEC-001-0078).
    "integration": {
        "title": "LSC Integration Vocabularies",
        "description": "The rules that tie the modules together: which placing properties certify and which give context (placement), the evidence tier of every cited source (authority), and what a consumer may bind, answer and must refuse (consumer). Each vocabulary keeps its own namespace (Steps 7, 9 and 11).",
        "version": "1.0.0", "stage": None, "issued": "2026-10-22",
        "approval": ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved"),
        "parts": ["placement/vocabulary.ttl", "authority/vocabulary.ttl", "authority/source-tiers.ttl",
                  "consumer/vocabulary.ttl"],
        "shapes": ["consumer/shapes.ttl"],
        "depends_on": ["core", "organization", "kpi", "data-product", "value-stream", "system", "lane", "market-data",
                       "party"],
        "pins": {"core": "2.2.0", "organization": "2.0.0", "kpi": "1.0.1", "data-product": "1.0.0", "value-stream": "1.0.0",
                 "system": "1.0.0", "lane": "1.0.0", "market-data": "1.0.0", "party": "1.0.0"},
        "decisions": ["EPM-DEC-001-0058", "EPM-DEC-001-0059", "EPM-DEC-001-0061", "EPM-DEC-001-0078"],
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


def released_requires(dep, version):
    """What a released package requires, read from its own manifest on disk, never from this builder's
    current table: a later release of that module must not change what an earlier package loads."""
    with open(os.path.join(ONTOLOGY, "releases", dep, version, "manifest.json")) as f:
        return json.load(f).get("depends_on") or {}


def released_closure(name):
    """Every released package this module's check loads: its dependencies at the versions it names,
    and theirs (from each selected release's manifest), down to core. Where two paths name different
    versions of one module, the highest is loaded, so a graph never holds two releases of one module."""
    return closure(dependencies(name))


def closure(depends_on):
    """The released packages that the given dependencies load, by the rule of released_closure. A
    written package's closure starts from its own manifest: closure(released_requires(name, version))."""
    found = {}
    todo = list(depends_on.items())
    while todo:
        dep, version = todo.pop()
        if dep in found and tuple(map(int, found[dep].split("."))) >= tuple(map(int, version.split("."))):
            continue
        found[dep] = version
        todo += list(released_requires(dep, version).items())
    return found


def validation_graph(name, g):
    """The data the module's shapes run over: the module, with the released packages of its closure."""
    data = Graph()
    data += g
    for dep, version in sorted(released_closure(name).items()):
        data.parse(os.path.join(ONTOLOGY, "releases", dep, version, f"{dep}.ttl"))
    return data


def check(name, g):
    """The module's shapes over the module, with the released packages it depends on loaded: core for
    the concepts a module refers to, the pinned organization release for ref-mpc, and the released
    data-product and kpi packages for value-stream and market-data."""
    conforms, _, text = validate(validation_graph(name, g), shacl_graph=parse(MODULES[name]["shapes"]))
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
        "approved_by": None if m["stage"] else {"who": "The decision owner", "recorded_in": m["approval"][0]},
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
