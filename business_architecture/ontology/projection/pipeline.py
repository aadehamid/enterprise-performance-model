"""Step 12's checks and committed record: the projection's inputs, checked with no database, and the result of the last load.

The one loader is the ontology-to-lpg skill's run_projection.py (skill-run/README.md). What stays here runs in CI and
needs neither Docker nor Java:

    python3 pipeline.py build                    # check the rules, validate, write projection-manifest.json
    python3 pipeline.py build --verify           # fail unless the manifest matches a fresh build
    python3 pipeline.py record --run ~/lpg-out/epm   # after a driver run on these inputs: take its inferred.nt and a summary
                                                 # of its report into this folder, then rewrite the manifest

Commit inferred.nt, projection-manifest.json and projection-report.json together. Turtle stays the master copy; Neo4j
is a projection that can be rebuilt from these files at any time.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict

from pyshacl import validate
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
# Every released module once, at its newest release (EPM-DEC-001-0036, amendment of 2026-10-22). So
# kpi is 1.1.1 (EPM-DEC-001-0093), though market-data and integration were released against 1.0.1 (as was value-stream 1.0.0;
# value-stream 1.1.0 requires kpi 1.1.0, EPM-DEC-001-0090; 1.2.0 requires kpi 1.2.0, EPM-DEC-001-0106); their own release
# checks still test those pinned versions. Since 2026-10-28 kpi is 1.3.0, with the KPI and OPM identifiers (EPM-DEC-001-0109),
# while data-product, value-stream, market-data and integration still require kpi 1.2.0.
PACKAGES = [("core", "2.4.0"), ("organization", "2.2.0"), ("ref-mpc", "1.3.0"), ("kpi", "1.3.0"), ("party", "2.1.0"),
            ("data-product", "1.2.0"), ("value-stream", "1.2.0"), ("system", "1.5.0"), ("lane", "1.1.0"),
            ("market-data", "1.1.0"), ("integration", "2.5.0")]
INPUTS = [f"releases/{m}/{v}/{m}.ttl" for m, v in PACKAGES]
# Each package's own shapes. core 2.4.0's, as 2.3.0's, 2.2.0's and 2.1.0's, carry the controlled-value shapes
# (EPM-DEC-001-0044), so validation/controlled-values.ttl is not listed again.
SHAPES = [f"releases/{m}/{v}/shapes.ttl" for m, v in PACKAGES] + ["step4/scoped-sequence/shapes.ttl",
                                                                    "provenance/run-shapes.ttl"]
LOADABLE = os.path.join(HERE, "loadable.nt")
INFERRED = os.path.join(HERE, "inferred.nt")
MANIFEST = os.path.join(HERE, "projection-manifest.json")
REPORT = os.path.join(HERE, "projection-report.json")
SH = Namespace("http://www.w3.org/ns/shacl#")
MODULES_NS = "https://w3id.org/lsc/ontology/modules/"
# Our own namespaces, one per module.
OWN = tuple(MODULES_NS + m + "/" for m in ("core", "organization", "kpi", "population", "party", "data-product",
                                           "value-stream", "system", "lane", "market-data", "placement",
                                           "authority", "consumer"))
# Fixed prefixes (Rule 3). n10s gets exactly these, in this order, so no ns0-style prefix is invented.
PREFIXES = {
    "core": "https://w3id.org/lsc/ontology/modules/core/",
    "orgm": "https://w3id.org/lsc/ontology/modules/organization/",
    "kpi": "https://w3id.org/lsc/ontology/modules/kpi/",
    "pop": "https://w3id.org/lsc/ontology/modules/population/",
    "party": "https://w3id.org/lsc/ontology/modules/party/",
    "dp": "https://w3id.org/lsc/ontology/modules/data-product/",
    "vs": "https://w3id.org/lsc/ontology/modules/value-stream/",
    "sys": "https://w3id.org/lsc/ontology/modules/system/",
    "lane": "https://w3id.org/lsc/ontology/modules/lane/",
    "mkt": "https://w3id.org/lsc/ontology/modules/market-data/",
    "plc": "https://w3id.org/lsc/ontology/modules/placement/",
    "auth": "https://w3id.org/lsc/ontology/modules/authority/",
    "con": "https://w3id.org/lsc/ontology/modules/consumer/",
    "skos": str(SKOS), "dcterms": "http://purl.org/dc/terms/", "org": "http://www.w3.org/ns/org#",
    "rdfs": str(RDFS), "owl": str(OWL), "rdf": str(RDF), "prov": "http://www.w3.org/ns/prov#",
    # The party products' SKOS mappings point to Open Energy Ontology classes (EPM-DEC-001-0092).
    "oeo": "https://openenergyplatform.org/ontology/oeo/",
}
# Rule 4a's qualified-relation classes: (class, ends the node points to, ends that point to the node).
# An end that points to the node is the inverse link the guideline allows, as prov:qualifiedAssociation.
QUALIFIED_RELATIONS = [
    ("core/ScopedSequence", ("core/earlierProcess", "core/laterProcess"), ()),  # EPM-DEC-001-0026
    ("core/CanonicalFact", ("core/factSubject", "core/factPredicate", "core/factObject"), ()),  # EPM-DEC-001-0044
    ("organization/ResponsibilityAssignment", ("organization/forProcess", "organization/assignedRole"), ()),
    ("organization/ControlRelationship", ("organization/controllingEntity", "organization/controlledEntity"), ()),
    ("value-stream/MeasureLink", ("value-stream/measure",), ("value-stream/measureLink",)),  # EPM-DEC-001-0054
    ("market-data/Leg", ("market-data/benchmark",), ("market-data/leg",)),  # EPM-DEC-001-0057, 0066
    ("party/PartyRole", ("party/roleType",), ("party/plays",)),  # EPM-DEC-001-0068
    ("party/DataFlow", ("party/fromSystem", "party/toSystem"), ()),  # EPM-DEC-001-0069
    ("party/CustomerSourcing", ("party/sourcingSystem", "party/sourcedConcept"), ()),  # EPM-DEC-001-0069
]
# Rule gaps in a released module, which only a new release of that module can close. Each is
# named here with its fix target; the build fails on any gap not listed, and on a listed gap
# that no longer occurs, so the list cannot go stale (EPM-DEC-001-0036).
RELEASE_EXCEPTIONS = {}  # every listed gap is closed by integration 2.0.0 (EPM-DEC-001-0094)
VERSIONS = {"neo4j": "2025.06.2", "n10s": "2025.06.1", "apoc": "bundled with neo4j:2025.06.2",
            "robot": "1.9.10", "reasoner": "ELK (through ROBOT)", "method": "ontology-to-lpg 2.3"}


def graph(paths):
    g = Graph()
    for p in paths:
        g.parse(os.path.join(ONTOLOGY, p))
    return g


def sorted_nt(g):
    """Sorted, de-duplicated N-Triples, one triple per line (guideline Step 3)."""
    lines = {line for line in g.serialize(format="nt").splitlines() if line.strip()}
    return "".join(line + "\n" for line in sorted(lines))


def sha(*texts):
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode())
    return h.hexdigest()


# n10s writes every label, relationship type and property key as the fixed prefix, two underscores and the local
# name (its SHORTEN setting). The graph keeps that on main. In the share release the separator is one underscore
# (EPM-DEC-001-0110): the driver renames each name after every check has passed on the n10s names (the run
# configuration's separator).
N10S_SEP = "_" * 2
SHARE_RELEASE = bool(os.environ.get("EPM_SHARE_RELEASE")) or os.path.isfile(os.path.join(ONTOLOGY, "..", "..", "release.json"))
SEP = "_" if SHARE_RELEASE else N10S_SEP


def lpg_name(iri, sep=None):
    """The name a term has in the graph: the fixed prefix, the separator, the local name."""
    sep = SEP if sep is None else sep
    s = str(iri)
    for prefix, ns in PREFIXES.items():
        if s.startswith(ns) and "/" not in s[len(ns):] and "#" not in s[len(ns):]:
            return f"{prefix}{sep}{s[len(ns):]}"
    return None


def shapes_fingerprint():
    """SHA-256 over every shape file, in order. The committed report records it, so a shape change makes
    the report stale even when the loaded triples do not change."""
    return sha(*(open(os.path.join(ONTOLOGY, p)).read() for p in SHAPES))


# ---------- Step 1: check the rules, then validate the data ----------

def check_rules(data, shapes):
    """Return a list of rule violations. Any violation stops the build (guideline Step 1)."""
    problems = []
    preds = set(data.predicates())
    own = {p for p in preds if str(p).startswith(OWN)}
    kinds = (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
    # Rule 1: every predicate of our own modules has one kind and one concrete range.
    for p in sorted(own):
        k = [k for k in kinds if (p, RDF.type, k) in data]
        r = list(data.objects(p, RDFS.range))
        if len(k) != 1:
            problems.append(f"Rule 1: {p} has {len(k)} kinds")
        # A concrete range: one IRI, and not rdfs:Literal or rdfs:Resource, which say nothing.
        if len(r) != 1 or isinstance(r[0], BNode) or r[0] in (RDFS.Literal, RDFS.Resource):
            problems.append(f"Rule 1: {p} has no single concrete range")
    # Rule 2: every own predicate has a shape that states its cardinality.
    stated = {shapes.value(n, SH.path) for n in shapes.subjects(SH.path, None)
              if (n, SH.minCount, None) in shapes or (n, SH.maxCount, None) in shapes}
    problems += [f"Rule 2: no cardinality stated for {p}" for p in sorted(own - stated)]
    # Rule 3: no blank nodes; every namespace in use has a fixed prefix.
    if any(isinstance(x, BNode) for t in data for x in t):
        problems.append("Rule 3: the data holds a blank node")
    for p in preds:
        if not any(str(p).startswith(ns) for ns in PREFIXES.values()):
            problems.append(f"Rule 3: no fixed prefix for {p}")
    # Rule 4a: every qualified-relation node has an IRI and one value for each end. These are the
    # qualified-relation classes the modules define; a new one must be added to QUALIFIED_RELATIONS.
    for cls, ends, inbound in QUALIFIED_RELATIONS:
        for node in data.subjects(RDF.type, URIRef(MODULES_NS + cls)):
            for end in ends:
                if len(list(data.objects(node, URIRef(MODULES_NS + end)))) != 1:
                    problems.append(f"Rule 4a: {node} has not exactly one {MODULES_NS + end}")
            for end in inbound:
                if len(list(data.subjects(URIRef(MODULES_NS + end), node))) != 1:
                    problems.append(f"Rule 4a: {node} is not the object of exactly one {MODULES_NS + end}")
    # Rule 5: every predicate and class gets a name in the graph, and no two share one. In n10s's
    # SHORTEN mode the name is the fixed prefix plus the local name (EPM-DEC-001-0036).
    used = defaultdict(set)
    for term in preds | set(data.objects(None, RDF.type)):
        name = lpg_name(term)
        if name is None:
            problems.append(f"Rule 5: no LPG name for {term}")
        else:
            used[name].add(str(term))
    problems += [f"Rule 5: the LPG name {n!r} is shared by {sorted(t)}" for n, t in used.items() if len(t) > 1]
    return problems


def check(data, shapes):
    found = check_rules(data, shapes)
    problems = [p for p in found if p not in RELEASE_EXCEPTIONS]
    problems += [f"listed release exception no longer occurs: {e}" for e in RELEASE_EXCEPTIONS if e not in found]
    # advanced=True runs the SHACL-AF parts: SPARQL targets (core's ProcessConcept) and SPARQL
    # constraints (the scoped-sequence ancestor check).
    conforms, _, text = validate(data, shacl_graph=shapes, advanced=True)
    if not conforms:
        problems.append("SHACL: the data does not conform:\n" + text)
    return problems


# ---------- Steps 1 and 3 ----------

def build():
    data, shapes = graph(INPUTS), graph(SHAPES)
    inferred = open(INFERRED).read() if os.path.exists(INFERRED) else ""
    # Step 1 checks every triple that is loaded: the asserted data and the inferred triples.
    checked = Graph()
    checked += data
    checked.parse(data=inferred, format="nt")
    problems = check(checked, shapes)
    if problems:
        sys.exit("Step 1 stops the build:\n  " + "\n  ".join(problems))
    loadable = sorted_nt(data)
    manifest = {
        "inputs": {p: sha(open(os.path.join(ONTOLOGY, p)).read()) for p in INPUTS},
        "shapes": {p: sha(open(os.path.join(ONTOLOGY, p)).read()) for p in SHAPES},
        "loadable_triples": loadable.count("\n"),
        "inferred_triples": inferred.count("\n"),
        "input_fingerprint": sha(loadable, inferred),
        "rule4": "4a: qualified-relation nodes (EPM-DEC-001-0020)",
        "release_exceptions": RELEASE_EXCEPTIONS,
        "versions": VERSIONS,
    }
    return loadable, inferred, json.dumps(manifest, indent=2, sort_keys=True) + "\n"


# ---------- the record of the last load ----------

# What the committed report keeps of the driver's. Its compiled rows and fail cases run to some 800 KB and stay in the
# driver's output folder.
REPORT_FIELDS = ("shacl_violations_in_graph", "in_graph_shape_constraints", "in_graph_mutant_violations", "roundtrip_lost",
                 "roundtrip_added", "determinism_hash_sorted", "determinism_hash_shuffled", "nodes", "relationships",
                 "schema_relationships", "export_rows", "schema_rows_skipped", "separator", "renamed", "rename_lossless")


def report_problems(report):
    """Why a load's report cannot stand as the record: every check the load must have passed."""
    checks = {"it does not say passed": report.get("passed") is True,
              "a SHACL violation in the graph": report.get("shacl_violations_in_graph") == 0,
              "the deliberate mutant was not caught": (report.get("in_graph_mutant_violations") or 0) > 0,
              "the round trip lost or added a triple": (report.get("roundtrip_lost"), report.get("roundtrip_added")) == (0, 0),
              "the two loads hash differently": bool(report.get("determinism_hash_sorted"))
              and report.get("determinism_hash_sorted") == report.get("determinism_hash_shuffled"),
              "the rename was not lossless": report.get("rename_lossless") is True}
    return [why for why, ok in checks.items() if not ok]


def record(run):
    """Takes a driver run's result into this folder, once its inputs are proven to be this tree's: every file its
    run-manifest.json lists has the SHA-256 of the file this tree projects, and it loaded the same triples."""
    with open(os.path.join(run, "run-manifest.json")) as f:
        ran = json.load(f)
    with open(os.path.join(run, "projection-report.json")) as f:
        report = json.load(f)
    with open(os.path.join(run, "inferred.nt")) as f:
        inferred = f.read()
    with open(os.path.join(run, "loadable.nt")) as f:
        loaded = f.read()
    tree = sorted(sha(open(os.path.join(ONTOLOGY, p)).read()) for p in INPUTS + SHAPES)
    if sorted(e["sha256"] for e in ran["data"] + ran["shapes"]) != tree:
        sys.exit("record: that run read other inputs than this tree's; run the driver on this tree")
    problems = report_problems(report)
    if problems:
        sys.exit("record: the run's report cannot stand: " + "; ".join(problems))
    if set(loaded.splitlines()) != set(sorted_nt(graph(INPUTS)).splitlines()):
        sys.exit("record: that run loaded other triples than this tree's")
    with open(INFERRED, "w") as f:
        f.write(inferred)
    loadable, inferred, manifest = build()  # Step 1 now covers the run's inferences too
    summary = {k: report[k] for k in REPORT_FIELDS}
    summary.update({"input_fingerprint": sha(loadable, inferred), "shapes_fingerprint": shapes_fingerprint(),
                    "versions": report["versions"]})
    with open(MANIFEST, "w") as f:
        f.write(manifest)
    with open(REPORT, "w") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"recorded: {summary['nodes']} nodes, {summary['relationships']} relationships, "
          f"{loadable.count(chr(10))} triples and {inferred.count(chr(10))} inferred")


def parser():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--verify", action="store_true")
    r = sub.add_parser("record")
    r.add_argument("--run", required=True, help="the driver's output folder (the run configuration's out)")
    return ap


def main():
    args = parser().parse_args()
    if args.cmd == "build":
        loadable, inferred, manifest = build()
        print(f"Step 1 passed; loadable.nt {loadable.count(chr(10))} triples, inferred.nt {inferred.count(chr(10))}")
        if args.verify:
            if not os.path.exists(MANIFEST) or open(MANIFEST).read() != manifest:
                sys.exit("projection-manifest.json is not current: run pipeline.py build")
            print("projection-manifest.json is current")
        else:
            with open(MANIFEST, "w") as f:
                f.write(manifest)
            print("wrote projection-manifest.json")
    else:
        record(os.path.expanduser(args.run))


if __name__ == "__main__":
    main()
