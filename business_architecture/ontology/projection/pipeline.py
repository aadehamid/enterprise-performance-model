"""Step 12: project the ontology into a Neo4j labelled property graph (EPM-DEC-001-0020, 0021, 0036).

Follows the guideline in ../lpg-projection/ (v2.2) with Rule 4 set to 4a, qualified-relation nodes:

    python3 pipeline.py build                    # Steps 1 and 3: check the rules, validate, write the
                                                 # sorted N-Triples and the manifest (no tools beyond rdflib)
    python3 pipeline.py build --verify           # fail unless the manifest matches a fresh build
    python3 pipeline.py reason --robot robot.jar # Step 2: ELK through ROBOT; writes inferred.nt
    python3 pipeline.py load-verify --bolt bolt://localhost:17687 --password ... --import-dir DIR
                                                 # Steps 4 and 5 against a running Neo4j with n10s and APOC;
                                                 # writes projection-report.json

Turtle stays the master copy. Neo4j is a projection that can be rebuilt from these files at any time.
"""
import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
# Every released module once, at its newest release (EPM-DEC-001-0036, amendment of 2026-10-22). So
# kpi is 1.1.0, though value-stream, market-data and integration were released against 1.0.1; their own release
# checks still test those pinned versions.
PACKAGES = [("core", "2.3.0"), ("organization", "2.0.0"), ("ref-mpc", "1.2.0"), ("kpi", "1.1.0"), ("party", "1.0.0"),
            ("data-product", "1.0.0"), ("value-stream", "1.0.0"), ("system", "1.0.0"), ("lane", "1.0.0"),
            ("market-data", "1.0.0"), ("integration", "1.0.0")]
INPUTS = [f"releases/{m}/{v}/{m}.ttl" for m, v in PACKAGES]
# Each package's own shapes. core 2.3.0's, as 2.2.0's and 2.1.0's, carry the controlled-value shapes
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
RELEASE_EXCEPTIONS = {
    "Rule 1: https://w3id.org/lsc/ontology/modules/value-stream/produces has no single concrete range":
        "value-stream 1.0.0 declares no rdfs:range; the next value-stream release adds rdfs:range dp:DataProduct",
    "Rule 1: https://w3id.org/lsc/ontology/modules/value-stream/consumes has no single concrete range":
        "value-stream 1.0.0 declares no rdfs:range; the next value-stream release adds rdfs:range skos:Concept "
        "(it consumes data products and data product lines)",
    "Rule 1: https://w3id.org/lsc/ontology/modules/population/populationEvidence has no single concrete range":
        "kpi 1.1.0 declares no rdfs:range; the next kpi release adds rdfs:range xsd:string",
    "Rule 1: https://w3id.org/lsc/ontology/modules/placement/placementKind has no single concrete range":
        "integration 1.0.0 declares no rdfs:range; the next integration release adds rdfs:range skos:Concept",
    "Rule 1: https://w3id.org/lsc/ontology/modules/party/evidenceInput has no single concrete range":
        "party 1.0.0 declares no rdfs:range; the next party release adds rdfs:range xsd:string",
    "Rule 1: https://w3id.org/lsc/ontology/modules/party/customerRole has no single concrete range":
        "party 1.0.0 declares no rdfs:range; the next party release adds rdfs:range rdf:langString",
    "Rule 1: https://w3id.org/lsc/ontology/modules/party/carries has no single concrete range":
        "party 1.0.0 declares no rdfs:range; the next party release adds rdfs:range rdf:langString",
    "Rule 1: https://w3id.org/lsc/ontology/modules/consumer/reliesOn has no single concrete range":
        "integration 1.0.0 declares no rdfs:range; its objects are properties, a concept and other terms, so "
        "the next integration release gives it one concrete range",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/placement/placementKind":
        "integration 1.0.0 has no shape stating its cardinality; the next integration release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/party/plays":
        "party 1.0.0 has no shape stating its cardinality; the next party release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/party/mpcClassification":
        "party 1.0.0 has no shape stating its cardinality; the next party release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/party/implements":
        "party 1.0.0 has no shape stating its cardinality; the next party release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/party/governedBy":
        "party 1.0.0 has no shape stating its cardinality; the next party release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/party/feeds":
        "party 1.0.0 has no shape stating its cardinality; the next party release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/authority/rank":
        "integration 1.0.0 has no shape stating its cardinality; the next integration release adds one",
    "Rule 2: no cardinality stated for https://w3id.org/lsc/ontology/modules/authority/evidenceTier":
        "integration 1.0.0 has no shape stating its cardinality; the next integration release adds one",
}
VERSIONS = {"neo4j": "2025.06.2", "n10s": "2025.06.1", "apoc": "bundled with neo4j:2025.06.2",
            "robot": "1.9.10", "reasoner": "ELK (through ROBOT)", "guideline": "v2.2 (lpg-projection/, pin 8ce9ada)"}


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


def lpg_name(iri):
    """The name n10s gives a term in SHORTEN mode: the fixed prefix, two underscores, the local name."""
    s = str(iri)
    for prefix, ns in PREFIXES.items():
        if s.startswith(ns) and "/" not in s[len(ns):] and "#" not in s[len(ns):]:
            return f"{prefix}__{s[len(ns):]}"
    return None


def shapes_fingerprint():
    """SHA-256 over every shape file, in order. The Step 5 report records it, so a shape change makes
    the committed report stale even when the loaded triples do not change."""
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


# ---------- Step 2: reason once, upstream ----------

def reason(robot):
    with tempfile.TemporaryDirectory() as tmp:
        merged, reasoned = os.path.join(tmp, "merged.ttl"), os.path.join(tmp, "reasoned.ttl")
        data = graph(INPUTS)
        data.serialize(merged, format="turtle")
        subprocess.run(["java", "-jar", robot, "reason", "--reasoner", "ELK", "--input", merged,
                        "--axiom-generators", "SubClass ClassAssertion", "--output", reasoned], check=True)
        before = set(sorted_nt(data).splitlines())
        after = Graph().parse(reasoned)
    # inferred.nt: in the reasoner's output, not its input; rdf:type and rdfs:subClassOf only;
    # subject and object both IRIs (guideline Step 3).
    # Also drop triples whose object is an OWL or RDFS built-in (owl:NamedIndividual, owl:Class,
    # owl:Thing, owl:AnnotationProperty, rdfs:Datatype): the OWL API writes these declarations into
    # the reasoner's output; they are not inferences about the domain (EPM-DEC-001-0036).
    builtin = (str(OWL), str(RDFS))
    keep = Graph()
    for s, p, o in after:
        if p in (RDF.type, RDFS.subClassOf) and isinstance(s, URIRef) and isinstance(o, URIRef) \
                and not str(o).startswith(builtin):
            keep.add((s, p, o))
    lines = [line for line in sorted_nt(keep).splitlines() if line not in before]
    with open(INFERRED, "w") as f:
        f.write("".join(line + "\n" for line in lines))
    print(f"inferred.nt: {len(lines)} triples")


# ---------- Steps 4 and 5 ----------

def literal_multivalued(data, shapes):
    """Literal-valued predicates that may carry more than one value: n10s keeps them as arrays."""
    one = {shapes.value(n, SH.path) for n in shapes.subjects(SH.maxCount, Literal(1))}
    lit = {p for s, p, o in data if isinstance(o, Literal)}
    seen = Counter((s, p) for s, p, o in data if isinstance(o, Literal))
    many = {p for (s, p), n in seen.items() if n > 1}
    return sorted(str(p) for p in lit if p not in one or p in many)


# What n10s 2025.06.1 cannot validate in the graph. Step 1 has already validated every one of these
# with pySHACL on the exact triples that are loaded, and the round trip proves the graph holds those
# triples, so the full shapes hold in the graph (EPM-DEC-001-0036).
# sh:pattern is among them: n10s matches the pattern against the whole string, where SHACL searches
# it, so "\S" fails on every value longer than one character (EPM-DEC-001-0036, amendment of
# 2026-10-22). So is an sh:in list of literals: n10s does not match a loaded true to the list's true.
N10S_UNSUPPORTED = [SH["not"], SH.languageIn, SH.targetObjectsOf, SH.targetSubjectsOf, SH.node,
                    SH.message, SH.severity, SH.pattern]


def in_graph_shapes(shapes):
    """The subset of the shapes that n10s validates inside Neo4j: property shapes on target classes."""
    g = Graph()
    for s, p, o in shapes:
        if p in N10S_UNSUPPORTED:
            continue
        if p == SH.datatype and o == RDF.langString:
            continue
        if p == SH["in"] and any(isinstance(m, Literal) for m in Collection(shapes, o)):
            continue
        g.add((s, p, o))
    # Drop node shapes left with no target class: n10s validates only targeted shapes.
    for shape in set(g.subjects(RDF.type, SH.NodeShape)):
        if (shape, SH.targetClass, None) not in g:
            for prop in list(g.objects(shape, SH.property)):
                g.remove((prop, None, None))
            g.remove((shape, None, None))
    return g


def cypher_setup(data, shapes):
    """Generated, not handwritten (guideline anti-patterns): prefixes and config. SHORTEN, as guideline
    v2.2 says (v2.1's example used MAP): n10s validates SHACL only in a namespace-aware graph
    (EPM-DEC-001-0036)."""
    stmts = ["CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE"]
    multival = json.dumps(literal_multivalued(data, shapes))
    stmts.append("CALL n10s.graphconfig.init({handleVocabUris:'SHORTEN', handleRDFTypes:'LABELS_AND_NODES', "
                 f"handleMultival:'ARRAY', multivalPropList:{multival}, keepLangTag:true, keepCustomDataTypes:true}})")
    return stmts


def load(session, nt_name, setup):
    session.run("MATCH (n) DETACH DELETE n").consume()
    for drop in ("CALL n10s.graphconfig.drop()", "CALL n10s.nsprefixes.removeAll()", "CALL n10s.mapping.dropAll()"):
        try:
            session.run(drop).consume()
        except Exception:
            pass
    for stmt in setup:
        session.run(stmt).consume()
    # Fixed prefixes after the config, so n10s never invents an ns0-style prefix (Rule 3).
    for k, v in PREFIXES.items():
        session.run("CALL n10s.nsprefixes.add($k, $v)", k=k, v=v).consume()
    for name in (nt_name, "inferred.nt"):
        r = session.run(f"CALL n10s.rdf.import.fetch('file:///import/{name}','N-Triples')").single()
        if r["terminationStatus"] != "OK":
            raise RuntimeError(f"n10s import of {name}: {dict(r)}")
    # 4g: sort array properties so the graph does not depend on load order.
    keys = session.run("MATCH (n:Resource) UNWIND keys(n) AS k WITH n, k WHERE valueType(n[k]) STARTS WITH 'LIST' "
                       "RETURN DISTINCT k").value()
    for k in keys:
        session.run(f"MATCH (n:Resource) WHERE n.`{k}` IS NOT NULL SET n.`{k}` = apoc.coll.sort(n.`{k}`)").consume()


def graph_hash(session):
    nodes = session.run("MATCH (n:Resource) RETURN n.uri AS uri, labels(n) AS l, properties(n) AS p ORDER BY uri").data()
    edges = session.run("MATCH (a:Resource)-[r]->(b:Resource) RETURN a.uri AS s, type(r) AS t, b.uri AS o, "
                        "r.uri AS u ORDER BY s, t, o, u").data()
    canon = json.dumps({"nodes": [{**n, "l": sorted(n["l"])} for n in nodes], "edges": edges},
                       sort_keys=True, default=str)
    return sha(canon), len(nodes), len(edges)


LANG_SUFFIX = re.compile(r"^(.*)@([a-z]{2,3}(?:-[A-Za-z0-9]+)*)$", re.S)
INTEGERS = {XSD.integer, XSD.long, XSD.int, XSD.short, XSD.byte, XSD.nonNegativeInteger, XSD.positiveInteger}


def canonical(term):
    """One spelling per RDF literal, so the round trip compares values, not spellings: a plain
    literal and an xsd:string literal are the same (RDF 1.1); integer types load as INTEGER and come
    back as xsd:long (guideline section 8), so they compare as xsd:integer; xsd:decimal loads as FLOAT
    and comes back as xsd:double (section 8; Add-on C not adopted), so both compare by their value as a
    double, and the build refuses a decimal whose double does not print back to the same value."""
    if not isinstance(term, Literal) or term.language:
        return term
    if term.datatype in (None, XSD.string):
        return Literal(str(term))
    if term.datatype in INTEGERS:
        return Literal(int(term), datatype=XSD.integer)
    if term.datatype in (XSD.decimal, XSD.double, XSD.float):
        return Literal(repr(float(term)), datatype=XSD.double)
    return term


def canonical_graph(g):
    out = Graph()
    for s, p, o in g:
        out.add((s, p, canonical(o)))
    return out


def roundtrip(session):
    rows = session.run("CALL n10s.rdf.export.cypher('MATCH (n:Resource) OPTIONAL MATCH (n)-[r]->(m:Resource) "
                       "RETURN n, r, m') YIELD subject, predicate, object, isLiteral, literalType, literalLang "
                       "RETURN subject, predicate, object, isLiteral, literalType, literalLang").data()
    g = Graph()
    for r in rows:
        if r["isLiteral"]:
            m = LANG_SUFFIX.match(str(r["object"]))
            if r["literalLang"]:
                o = Literal(r["object"], lang=r["literalLang"])
            elif m and r["literalType"] in (None, str(XSD.string)):
                # keepLangTag stores "text@en" in the graph; the export hands it back untagged.
                o = Literal(m.group(1), lang=m.group(2))
            else:
                o = Literal(r["object"], datatype=URIRef(r["literalType"]) if r["literalType"] else None)
        else:
            o = URIRef(r["object"])
        g.add((URIRef(r["subject"]), URIRef(r["predicate"]), o))
    return g


def load_verify(bolt, password, import_dir):
    from neo4j import GraphDatabase
    from rdflib.compare import graph_diff, to_isomorphic

    data, shapes = graph(INPUTS), graph(SHAPES)
    loadable, inferred, _ = build()
    setup = cypher_setup(data, shapes)
    lines = loadable.splitlines()
    shuffled = lines[:]
    random.Random(12).shuffle(shuffled)
    for name, text in (("loadable.nt", loadable), ("inferred.nt", inferred),
                       ("shuffled.nt", "".join(x + "\n" for x in shuffled))):
        with open(os.path.join(import_dir, name), "w") as f:
            f.write(text)
    with open(os.path.join(import_dir, "shapes.ttl"), "w") as f:
        f.write(in_graph_shapes(shapes).serialize(format="turtle"))
    driver = GraphDatabase.driver(bolt, auth=("neo4j", password))
    with driver.session() as s:
        load(s, "shuffled.nt", setup)
        hash_shuffled = graph_hash(s)
        load(s, "loadable.nt", setup)
        hash_sorted = graph_hash(s)
        s.run("CALL n10s.validation.shacl.import.fetch('file:///import/shapes.ttl','Turtle')").consume()
        violations = s.run("CALL n10s.validation.shacl.validate() YIELD focusNode, propertyShape, resultMessage "
                           "RETURN focusNode, propertyShape, resultMessage").data()
        out = roundtrip(s)
        # The in-graph check must be able to fail: remove one role's name, which every role must
        # have exactly once (the organization package's shapes.ttl), and count the violations n10s reports.
        shapes_loaded = s.run("CALL n10s.validation.shacl.listShapes() YIELD target RETURN count(*) AS n").single()["n"]
        s.run("MATCH (r:org__Role) WITH r ORDER BY r.uri LIMIT 1 REMOVE r.skos__prefLabel").consume()
        caught = len(s.run("CALL n10s.validation.shacl.validate() YIELD focusNode RETURN focusNode").data())
    driver.close()
    src = Graph().parse(data=loadable + inferred, format="nt")
    inexact = [o for o in src.objects() if isinstance(o, Literal) and o.datatype == XSD.decimal
               and str(o.toPython()) != repr(float(o))]
    if inexact:
        sys.exit(f"a decimal does not survive as a FLOAT; adopt guideline Add-on C: {inexact[:3]}")
    clash = [o for o in src.objects() if isinstance(o, Literal) and not o.language and LANG_SUFFIX.match(str(o))]
    if clash:
        sys.exit(f"a source string ends like a language tag, so the round trip cannot tell them apart: {clash[:3]}")
    both, lost, added = graph_diff(to_isomorphic(canonical_graph(src)), to_isomorphic(canonical_graph(out)))
    report = {
        "input_fingerprint": sha(loadable, inferred),
        "shapes_fingerprint": shapes_fingerprint(),
        "shacl_violations_in_graph": len(violations),
        "in_graph_shape_constraints": shapes_loaded,
        "in_graph_mutant_violations": caught,
        "roundtrip_lost": len(lost), "roundtrip_added": len(added),
        "determinism_hash_sorted": hash_sorted[0], "determinism_hash_shuffled": hash_shuffled[0],
        "nodes": hash_sorted[1], "relationships": hash_sorted[2],
        "versions": VERSIONS,
        "samples": {"violations": violations[:5],
                    "lost": sorted(t.n3() for t in [x for x in lost][:0]) or [" ".join(x.n3() for x in t) for t in list(lost)[:10]],
                    "added": [" ".join(x.n3() for x in t) for t in list(added)[:10]]},
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--verify", action="store_true")
    r = sub.add_parser("reason")
    r.add_argument("--robot", required=True)
    lv = sub.add_parser("load-verify")
    lv.add_argument("--bolt", required=True)
    lv.add_argument("--password", required=True)
    lv.add_argument("--import-dir", required=True)
    args = ap.parse_args()
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
    elif args.cmd == "reason":
        reason(args.robot)
    else:
        report = load_verify(args.bolt, args.password, args.import_dir)
        with open(REPORT, "w") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
        ok = (report["shacl_violations_in_graph"] == 0 and report["in_graph_mutant_violations"] > 0
              and report["roundtrip_lost"] == 0 and report["roundtrip_added"] == 0
              and report["determinism_hash_sorted"] == report["determinism_hash_shuffled"])
        print(json.dumps({k: v for k, v in report.items() if k not in ("samples", "versions")}, indent=1))
        if not ok:
            sys.exit("Step 5 failed; see projection-report.json samples")


if __name__ == "__main__":
    main()
