"""Build core 2.0.0 from the released core 1.0.0 (EPM-DEC-001-0038).

    python3 build_core_next.py            # build, validate, print the figures
    python3 build_core_next.py --write    # write releases/core/2.0.0/
    python3 build_core_next.py --verify   # fail unless the written package equals a fresh build

core 1.0.0 stays as it was built from its pinned evidence (build_core.py). This builder starts from
that released graph and applies the changes the decision owner decided on 2026-10-13:

1. Business domains as a code list. A new object property core:businessDomain links each concept
   that carries a 1.0.0 core:responsibleDomain value (processes and capabilities) to a concept of
   the core:BusinessDomain list. "Commercial & Marketing" splits by branch:
   CM 1.3 is Marketing, CM 1.1 and CM 1.2 are Commercial, CM 1.4 is IT Services. The other values
   keep their own domain. core:responsibleDomain is deprecated (owl:deprecated true); its values stay.
2. Planned inputs and outputs from the process map's SIPOC field (`sioc`): core:plannedInput and
   core:plannedOutput, one governed literal per input or output (the 2026-09-22 flow decision).
3. core:earlierProcess and core:laterProcess get rdfs:range skos:Concept (guideline Rule 1).

Deprecating a property makes this a major: 2.0.0, which needs the decision owner's approval (module policy,
2026-09-18). It was built as the candidate 2.0.0-rc.1 with no issued date; the decision owner approved the
release on 2026-10-13 (APPROVAL below).
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
BASE = os.path.join(ONTOLOGY, "releases", "core", "1.0.0")
# The process map as 2.0.0 was built from it. A released package is fixed, so the build reads the
# map at the commit that last changed it before the release, not the working copy: later map
# changes go into a later core release. CI fetches full history, so the commit is always there.
SOURCE_PATH = "business_architecture/business_process/downstream_process_map.json"
SOURCE_COMMIT = "b75fd991e243248e60ecc832b3ad2c4f5c91740a"
IDENTITY = os.path.join(ONTOLOGY, "build", "output", "step2-identity-map.json")
CHANGELOG = os.path.join(ONTOLOGY, "releases", "core", "CHANGELOG-2.0.0.md")
VERSION, STAGE, ISSUED = "2.0.0", None, "2026-10-13"
# The sentence that approved the release: (saved file, the decision owner's words in its body).
APPROVAL = ("step4/review-evidence/decision-owner-answers/core-2-0-0-release.md", "I approve the core 2.0.0 releas")
LABEL = VERSION if STAGE is None else f"{VERSION}-{STAGE}"
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", LABEL)

CORE = Namespace("https://w3id.org/lsc/ontology/modules/core/")
DOMAIN = Namespace("https://w3id.org/lsc/ontology/modules/core/business-domain/")
PROC = "https://w3id.org/lsc/ontology/process/"
ONTOLOGY_IRI = URIRef("https://w3id.org/lsc/ontology/modules/core")
SH = Namespace("http://www.w3.org/ns/shacl#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DECIDED = "EPM-DEC-001-0038; the decision owner's words in step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md"

# The business domain list. Each 1.0.0 responsibleDomain value maps to one concept, except
# "Commercial & Marketing", which splits by the branch of CM 1 the process sits in.
DOMAINS = {
    "commercial": ("Commercial", "The commercial work of the downstream business: planning and scheduling, and supply and trading (CM 1.1, CM 1.2)."),
    "marketing": ("Marketing", "The marketing work of the downstream business (CM 1.3)."),
    "it-services": ("IT Services", "The IT services that support the commercial and marketing processes (CM 1.4)."),
    "finance-enabled-supply-and-trading": ("Finance-enabled Supply & Trading", "Supply and trading work that Finance enables."),
    "finance": ("Finance", "The finance domain."),
    "refining": ("Refining", "The refining domain."),
    "cross-functional": ("Cross-functional", "Shared by two or more domains; the process's note names them."),
}
SPLIT = {"CM-1-1": "commercial", "CM-1-2": "commercial", "CM-1-3": "marketing", "CM-1-4": "it-services"}
OTHER = {"Finance-enabled Supply & Trading": "finance-enabled-supply-and-trading", "Finance": "finance",
         "Refining": "refining", "Cross-functional": "cross-functional"}


def en(text):
    return Literal(text, lang="en")


def branch(process):
    """The CM 1 branch a process sits in ("CM-1-3" for CM-1-3-2-1), or None."""
    local = str(process)[len(PROC):]
    parts = local.split("-")
    return "-".join(parts[:3]) if local.startswith("CM-1-") and len(parts) >= 3 else None


def domain_of(process, value):
    if value == "Commercial & Marketing":
        key = SPLIT.get(branch(process))
        if key is None:
            sys.exit(f"{process}: Commercial & Marketing outside CM 1.1 to CM 1.4")
        return key
    if value not in OTHER:
        sys.exit(f"{process}: no business domain for {value!r}")
    return OTHER[value]


def source_map():
    """The bytes of the process map at SOURCE_COMMIT."""
    repo = os.path.dirname(os.path.dirname(ONTOLOGY))
    return subprocess.run(["git", "-C", repo, "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
                          check=True, capture_output=True, stdin=subprocess.DEVNULL).stdout


def sipoc():
    """(process IRI, inputs, outputs) for every process with a SIPOC field in the process map."""
    with open(IDENTITY) as f:
        iri = {row["skos_notation"]: URIRef(row["uri"]) for row in json.load(f) if row["skos_notation"]}
    data = json.loads(source_map())
    out = []

    def walk(node):
        if isinstance(node, dict):
            s = node.get("sioc")
            if isinstance(s, dict):
                if set(s) != {"suppliers", "inputs", "outputs", "customers"}:
                    sys.exit(f"{node.get('id')}: sioc keys {sorted(s)} are not the four SIPOC lists")
                out.append((iri[node["id"]], s["inputs"], s["outputs"]))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(data)
    return out


def vocabulary(g):
    """The new and changed terms."""
    g.add((CORE.BusinessDomain, RDF.type, SKOS.ConceptScheme))
    g.add((CORE.BusinessDomain, RDFS.label, en("Business domain")))
    g.add((CORE.BusinessDomain, SKOS.definition, en("The business domains that own processes and capabilities (the decision owner, 2026-10-13).")))
    for key, (label, definition) in DOMAINS.items():
        c = DOMAIN[key]
        g.add((c, RDF.type, SKOS.Concept))
        g.add((c, SKOS.inScheme, CORE.BusinessDomain))
        g.add((c, SKOS.prefLabel, en(label)))
        g.add((c, SKOS.definition, en(definition)))
    p = CORE.businessDomain
    g.add((p, RDF.type, OWL.ObjectProperty))
    g.add((p, RDFS.label, en("business domain")))
    g.add((p, RDFS.domain, SKOS.Concept))
    g.add((p, RDFS.range, SKOS.Concept))
    g.add((p, SKOS.definition, en("The business domain that owns the concept, a process or a capability: a concept of the business domain list.")))
    g.add((p, DCTERMS.bibliographicCitation, en(DECIDED)))
    for name, label, definition in (
            ("plannedInput", "planned input", "Something the process is designed to take in, as the process map's SIPOC inputs name it."),
            ("plannedOutput", "planned output", "Something the process is designed to produce, as the process map's SIPOC outputs name it.")):
        q = CORE[name]
        g.add((q, RDF.type, OWL.DatatypeProperty))
        g.add((q, RDFS.label, en(label)))
        g.add((q, RDFS.domain, SKOS.Concept))
        g.add((q, RDFS.range, RDF.langString))
        g.add((q, SKOS.definition, en(definition)))
        g.add((q, DCTERMS.bibliographicCitation, en(DECIDED)))
    rd = CORE.responsibleDomain
    g.add((rd, OWL.deprecated, Literal(True)))
    g.set((rd, SKOS.definition, en("Deprecated in 2.0.0: use core:businessDomain. The business domain responsible for the process, as a literal.")))
    for p in (CORE.earlierProcess, CORE.laterProcess):
        g.add((p, RDFS.range, SKOS.Concept))


def build():
    g = Graph()
    g.parse(os.path.join(BASE, "core.ttl"))
    counts = Counter()
    vocabulary(g)
    for s, o in list(g.subject_objects(CORE.responsibleDomain)):
        if (s, SKOS.inScheme, ONTOLOGY_IRI) not in g:
            continue
        key = domain_of(s, str(o))
        g.add((s, CORE.businessDomain, DOMAIN[key]))
        counts[f"business domain {key}"] += 1
    for process, inputs, outputs in sipoc():
        if (process, SKOS.inScheme, ONTOLOGY_IRI) not in g:
            sys.exit(f"{process}: has SIPOC lists but is not in core 1.0.0")
        for text in inputs:
            g.add((process, CORE.plannedInput, en(text)))
        for text in outputs:
            g.add((process, CORE.plannedOutput, en(text)))
        counts["processes with planned inputs and outputs"] += 1
        counts["planned inputs"] += len(inputs)
        counts["planned outputs"] += len(outputs)
    # The ontology header names the new version; it replaces 1.0.0's version triples.
    for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion):
        g.remove((ONTOLOGY_IRI, p, None))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(LABEL)))
    g.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{LABEL}")))
    g.add((ONTOLOGY_IRI, OWL.priorVersion, URIRef(f"{ONTOLOGY_IRI}/1.0.0")))
    if ISSUED:
        g.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
        g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    return g, counts


def shapes_text():
    """1.0.0's shapes file, unchanged, followed by the 2.0.0 additions. Kept as text so the inline
    blank nodes of 1.0.0's shapes are not re-serialized in a different order on each build."""
    with open(os.path.join(BASE, "shapes.ttl")) as f:
        base = f.read()
    return base + "\n# ---- Added in 2.0.0 (EPM-DEC-001-0038) ----\n" + additions().serialize(format="turtle")


def shapes():
    return Graph().parse(data=shapes_text(), format="turtle")


def additions():
    """A stated cardinality and list for each new property; IRI nodes only, so the text is stable."""
    s = Graph()
    shp = Namespace("https://w3id.org/lsc/ontology/modules/core/shapes/")
    s.bind("shp", shp)
    s.bind("core", CORE)
    s.bind("sh", SH)
    pc = shp.ProcessConcept
    for path, extra in ((CORE.businessDomain, [(SH.maxCount, Literal(1)), (SH["class"], SKOS.Concept)]),
                        (CORE.plannedInput, [(SH.minCount, Literal(0)), (SH.datatype, RDF.langString)]),
                        (CORE.plannedOutput, [(SH.minCount, Literal(0)), (SH.datatype, RDF.langString)])):
        node = URIRef(f"{shp}ProcessConcept-{str(path).rsplit('/', 1)[1]}")
        s.add((pc, SH.property, node))
        s.add((node, SH.path, path))
        for p, o in extra:
            s.add((node, p, o))
    dom = shp.BusinessDomainValue
    s.add((dom, RDF.type, SH.NodeShape))
    s.add((dom, SH.targetObjectsOf, CORE.businessDomain))
    node = URIRef(f"{shp}BusinessDomainValue-inScheme")
    s.add((dom, SH.property, node))
    s.add((node, SH.path, SKOS.inScheme))
    s.add((node, SH.hasValue, CORE.BusinessDomain))
    s.add((node, SH.message, en("A business domain comes from the business domain list.")))
    return s


def jsonld(g):
    data = json.loads(g.serialize(format="json-ld"))
    nodes = data if isinstance(data, list) else data.get("@graph", [data])
    for node in nodes:
        for key, value in node.items():
            if isinstance(value, list):
                node[key] = sorted(value, key=lambda v: json.dumps(v, sort_keys=True))
    nodes.sort(key=lambda n: n.get("@id", ""))
    return json.dumps(nodes, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def catalog():
    base = f"{ONTOLOGY_IRI}/releases/{LABEL}"
    g = Graph()
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{ONTOLOGY_IRI}/{LABEL}")
    g.add((cat, RDF.type, DCAT.Catalog))
    g.add((cat, DCAT.dataset, dataset))
    g.add((dataset, RDF.type, DCAT.Dataset))
    g.add((dataset, DCTERMS.title, en(f"LSC Core Process Ontology {LABEL}")))
    g.add((dataset, DCTERMS.isVersionOf, ONTOLOGY_IRI))
    g.add((dataset, OWL.versionInfo, Literal(LABEL)))
    if ISSUED:
        g.add((dataset, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"), ("shapes.ttl", "text/turtle")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, DCAT.distribution, dist))
        g.add((dist, RDF.type, DCAT.Distribution))
        g.add((dist, DCAT.downloadURL, dist))
        g.add((dist, DCAT.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(g, s, counts):
    files = {"core.ttl": g.serialize(format="turtle"), "core.jsonld": jsonld(g), "shapes.ttl": shapes_text(),
             "catalog.ttl": catalog(), "counts.json": json.dumps(dict(sorted(counts.items())), indent=2) + "\n"}
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(os.path.join(BASE, "manifest.json")) as f:
        base_manifest = f.read()
    files["manifest.json"] = json.dumps({
        "module": "core", "version": LABEL, "release_candidate": STAGE is not None,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{LABEL}",
        "built_from": {"core 1.0.0 manifest": hashlib.sha256(base_manifest.encode()).hexdigest(),
                       "process map": hashlib.sha256(source_map()).hexdigest()},
        "decisions": ["EPM-DEC-001-0038"],
        **({"approval": {"file": APPROVAL[0], "words": APPROVAL[1]}} if STAGE is None else {}),
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    g, counts = build()
    s = shapes()
    conforms, _, text = validate(g, shacl_graph=s, advanced=True)
    if not conforms:
        sys.exit("core " + LABEL + " fails its shapes:\n" + text)
    files = package(g, s, counts)
    print(f"core {LABEL}: {len(g)} triples; shapes conform; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if args.verify:
        stale = [n for n, t in files.items() if not os.path.exists(os.path.join(RELEASE_DIR, n))
                 or open(os.path.join(RELEASE_DIR, n)).read() != t]
        if stale:
            sys.exit(f"core {LABEL} package is not current: {stale}")
        print("release package is current")
    if args.write:
        os.makedirs(RELEASE_DIR, exist_ok=True)
        for n, t in files.items():
            with open(os.path.join(RELEASE_DIR, n), "w") as f:
                f.write(t)
        print(f"wrote {RELEASE_DIR}")


if __name__ == "__main__":
    main()
