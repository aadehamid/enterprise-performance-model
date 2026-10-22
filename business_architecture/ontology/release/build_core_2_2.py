"""Build core 2.2.0 from the released core 2.1.0 (EPM-DEC-001-0076).

    python3 build_core_2_2.py            # build, validate, print the figures
    python3 build_core_2_2.py --write    # write releases/core/2.2.0/
    python3 build_core_2_2.py --verify   # fail unless the written package equals a fresh build

core 2.1.0 stays as it was released (build_core_2_1.py). This builder starts from that graph and
applies the process-map changes merged since 2.0.0 was built (the ten PRs #288 to #296 and #301,
under EPM-DEC-001-0047, 0048 and 0051), read from the map at a pinned commit:

1. New concepts. Every map node with no concept in 2.1.0 becomes one, shaped as 2.1.0's map-sourced
   concepts are: prefLabel, notation, definition, broader, inScheme and taxonomy level. Its slug
   follows Step 2 (the ID with spaces and dots as hyphens). The definition is the first sentence of
   the map's description and the rest of the description is its scope note; provenance names the map
   commit and the record that added the node.
2. IDs on stubs. A 2.1.0 stub that the map now gives an ID keeps its IRI (the slug pins of
   build/step2-identity-map.py) and gains the ID as its skos:notation.
3. Changed descriptions. Where 2.1.0's definition is the map's earlier description and the new one
   extends it, the added text becomes a scope note; otherwise the map's new description is added as
   a scope note. Definitions from the definition workbook stay as approved.
4. Two checks from earlier records. The APQC element 19948 references (EPM-DEC-001-0060) and RF 1.2's
   Candidate status (EPM-DEC-001-0063), each settled in CHECKED below.

It adds concepts and notes and removes no IRI, so it is a minor release; the decision owner approved the
release plan (APPROVAL below).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS, XSD

import build_core_2_1 as prev

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ONTOLOGY))
BASE = os.path.join(ONTOLOGY, "releases", "core", "2.1.0")
SOURCE_PATH = "business_architecture/business_process/downstream_process_map.json"
# The map as 2.0.0 and 2.1.0 were built from it, and the map as 2.2.0 is built from it: the merge of
# #301, the last change to the map on main before this release. MPC-P10 is a proposal and not applied.
EARLIER_COMMIT = "b75fd991e243248e60ecc832b3ad2c4f5c91740a"
SOURCE_COMMIT = "82593547cc1672cbcf35e13d54244830671dd009"
CHANGELOG = os.path.join(ONTOLOGY, "releases", "core", "CHANGELOG-2.2.0.md")
VERSION, ISSUED = "2.2.0", "2026-10-22"
# The sentence that approved the release: (saved file, the decision owner's words in its body).
APPROVAL = ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved")
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", VERSION)

CORE = prev.CORE
PROC = prev.PROC
ONTOLOGY_IRI = prev.ONTOLOGY_IRI
SCHEME = URIRef("https://w3id.org/lsc/ontology/modules/core")
DECISION = Namespace(str(CORE) + "apqc-mapping-decision/")
ELEMENT_19948 = URIRef("https://w3id.org/lsc/ontology/source/apqc-pcf-7.2.2/element/19948")
# Step 2's slug pins: a stub first published under a minted slug keeps it when it gains an ID.
SLUG_PINS = {
    "RF 1": "L1-refining",
    "RF 1.1": "L2-refinery-performance-and-risk-coordination",
    "RF 1.2": "L2-refinery-asset-reliability-and-turnaround-coordination",
    "MS 1": "L1-midstream",
}
ID_RE = re.compile(r"^[A-Z]+ \d+(\.\d+)*$")

# The record behind each new node, by its ID's prefix; the map description names it too.
ADDED_BY = (
    ("CM 1.1.3.7.13", "EPM-DEC-001-0048 (process-map gap: movement losses and gains)"),
    ("CM 1.2.5.1.5", "EPM-DEC-001-0048 (process-map gap: renewable feedstock traceability)"),
    ("CM 1.2.4.3.8", "EPM-DEC-001-0047 (MPC-P05, environmental credits)"),
    ("RF 1.2.", "EPM-DEC-001-0047 (MPC-P02b, turnaround coordination)"),
    ("MS 1.", "EPM-DEC-001-0047 (MPC-P01, fuels logistics)"),
)

# The two checks folded in from earlier records (EPM-DEC-001-0076, What follows).
# EPM-DEC-001-0060: element 19948 is "Analyze internal operations" (APQC 1.1.3.2), a strategy
# element. Each of the 16 concepts that references it carries the element as its top-scoring step 3b
# candidate (step3b-definition-review.csv, apqc_id), as every concept with an APQC mapping decision
# does. The 14 marked "No candidate" are confirmed: the reference names the candidate compared, and
# the decision says it does not match. The two marked "Review link" are corrected to "Rejected".
REJECT_19948 = {
    "CM-1-2-6-3": "its own note says the APQC candidate is an unrelated internal-operations match",
    "L0-downstream-operations": "the scheme root is not an analysis of internal operations, and its definition review linked no element",
}
RF_1_2 = "L2-refinery-asset-reliability-and-turnaround-coordination"
CHANGE_NOTES = {
    "CM-1-2-6-3": "core 2.2.0 (2026-10-22): APQC mapping decision corrected from Review link to Rejected. Element 19948, "
                  "Analyze internal operations (APQC 1.1.3.2), was the top-scoring candidate; " + REJECT_19948["CM-1-2-6-3"]
                  + " (EPM-DEC-001-0060, 0076).",
    "L0-downstream-operations": "core 2.2.0 (2026-10-22): APQC mapping decision corrected from Review link to Rejected. Element "
                                "19948, Analyze internal operations (APQC 1.1.3.2), was the top-scoring candidate; "
                                + REJECT_19948["L0-downstream-operations"] + " (EPM-DEC-001-0060, 0076).",
    RF_1_2: "core 2.2.0 (2026-10-22): no longer a Candidate node. MPC-P02b populated it with RF 1.2.1 to RF 1.2.5 "
            "(EPM-DEC-001-0047), and EPM-DEC-001-0063, item 2, answered its ownership question for the map's scope: it owns "
            "the commercial and planning side of turnarounds; maintenance strategy, inspection and turnaround execution "
            "stay outside the map, with the refinery maintenance function (EPM-DEC-001-0076).",
}


def en(text):
    return Literal(text, lang="en")


def map_nodes(commit):
    """slug -> (node fields without children, parent slug), from the map at a commit."""
    data = json.loads(subprocess.check_output(["git", "show", f"{commit}:{SOURCE_PATH}"], cwd=REPO))
    out = {}

    def walk(node, parent):
        pid = node.get("id")
        if pid:
            if not ID_RE.match(pid):
                sys.exit(f"{pid!r} is not a process ID")
            slug = SLUG_PINS.get(pid) or pid.replace(" ", "-").replace(".", "-")
        else:
            slug = f"L{node['level']}-" + re.sub(r"[^a-z0-9]+", "-", node["name"].lower()).strip("-")
        if slug in out:
            sys.exit(f"two map nodes share the slug {slug}")
        out[slug] = ({k: v for k, v in node.items() if k != "children"}, parent)
        for child in node.get("children", []):
            walk(child, slug)

    for root in data:
        walk(root, None)
    return out


def split_description(text):
    """The first sentence, and the rest. A sentence ends at '. ' before a capital, outside brackets."""
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "." and depth == 0 and text[i + 1:i + 2] == " " and text[i + 2:i + 3].isupper():
            return text[:i + 1], text[i + 2:].strip()
    return text, ""


def added_by(pid):
    for prefix, record in ADDED_BY:
        if pid == prefix or pid.startswith(prefix):
            return record
    sys.exit(f"no record names why {pid} was added")


def changes(base=None, earlier=None, current=None):
    """What the map changed since 2.1.0: new nodes, IDs on stubs and changed descriptions."""
    base = base if base is not None else Graph().parse(os.path.join(BASE, "core.ttl"))
    earlier = earlier if earlier is not None else map_nodes(EARLIER_COMMIT)
    current = current if current is not None else map_nodes(SOURCE_COMMIT)
    if set(earlier) - set(current):
        sys.exit(f"the map removed nodes: {sorted(set(earlier) - set(current))}")
    new, ids, descriptions = [], [], []
    for slug, (node, parent) in current.items():
        if slug not in earlier:
            if (URIRef(PROC + slug), None, None) in base:
                sys.exit(f"{slug} is new in the map but already in core 2.1.0")
            new.append((slug, node, parent))
            continue
        old, old_parent = earlier[slug]
        if parent != old_parent:
            sys.exit(f"{slug} moved from {old_parent} to {parent}; a move is not a minor change")
        changed = {k for k in set(old) | set(node) if old.get(k) != node.get(k)}
        if changed - {"id", "description"}:
            sys.exit(f"{slug}: map fields {sorted(changed)} changed; this builder carries only IDs and descriptions")
        if "id" in changed:
            if old.get("id") or not node.get("id"):
                sys.exit(f"{slug}: its ID changed from {old.get('id')!r} to {node.get('id')!r}")
            ids.append((slug, node["id"]))
        if "description" in changed:
            if not node.get("description"):
                sys.exit(f"{slug}: the map dropped its description")
            descriptions.append((slug, old.get("description"), node["description"]))
    return sorted(new), sorted(ids), sorted(descriptions)


def build():
    g = Graph()
    g.parse(os.path.join(BASE, "core.ttl"))
    base_triples = len(g)
    new, ids, descriptions = changes(base=g)
    for slug, node, parent in new:
        s = URIRef(PROC + slug)
        if node.get("sioc"):
            sys.exit(f"{node['id']}: a SIPOC field on a new node needs the 2.0.0 planned-flow mapping")
        if (URIRef(PROC + parent), RDF.type, SKOS.Concept) not in g and parent not in {n[0] for n in new}:
            sys.exit(f"{slug}: its parent {parent} is not a concept")
        definition, scope = split_description(node["description"])
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
            f"Added in core 2.2.0 from the process map at commit {SOURCE_COMMIT[:7]}, by {added_by(node['id'])}; "
            "definition and scope note from the map's description (EPM-DEC-001-0076).")))
    for slug, pid in ids:
        s = URIRef(PROC + slug)
        if g.value(s, SKOS.notation) is not None:
            sys.exit(f"{slug} already has a notation")
        g.add((s, SKOS.notation, Literal(pid)))
    for slug, old, text in descriptions:
        s = URIRef(PROC + slug)
        definition = g.value(s, SKOS.definition)
        if old and definition is not None and str(definition) == old and text.startswith(old):
            # 2.1.0's definition is the map's earlier description: keep it, add what the map added.
            g.add((s, SKOS.scopeNote, en(text[len(old):].strip())))
        else:
            g.add((s, SKOS.scopeNote, en(text)))
    # EPM-DEC-001-0060: the 19948 references.
    for slug in REJECT_19948:
        s = URIRef(PROC + slug)
        if (s, CORE.apqcMappingDecision, DECISION["review-link"]) not in g or (s, DCTERMS.references, ELEMENT_19948) not in g:
            sys.exit(f"{slug} is not a 2.1.0 review link to element 19948")
        g.remove((s, CORE.apqcMappingDecision, None))
        g.add((s, CORE.apqcMappingDecision, DECISION["rejected"]))
    for slug, note in CHANGE_NOTES.items():
        g.add((URIRef(PROC + slug), SKOS.changeNote, en(note)))
    for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion):
        g.remove((ONTOLOGY_IRI, p, None))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(VERSION)))
    g.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{VERSION}")))
    g.add((ONTOLOGY_IRI, OWL.priorVersion, URIRef(f"{ONTOLOGY_IRI}/2.1.0")))
    g.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    concepts = [s for s in g.subjects(RDF.type, SKOS.Concept) if str(s).startswith(PROC)]
    counts = Counter({"process concepts": len(concepts), "new concepts": len(new), "IDs on stubs": len(ids),
                      "changed descriptions": len(descriptions), "19948 references rejected": len(REJECT_19948),
                      "19948 references confirmed": sum(1 for _ in g.subjects(DCTERMS.references, ELEMENT_19948)) - len(REJECT_19948)})
    with open(os.path.join(BASE, "counts.json")) as f:
        counts.update(json.load(f))
    return g, counts


def catalog():
    base = f"{ONTOLOGY_IRI}/releases/{VERSION}"
    g = Graph()
    g.bind("dcat", prev.prev.DCAT)
    g.bind("dcterms", DCTERMS)
    cat, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{ONTOLOGY_IRI}/{VERSION}")
    g.add((cat, RDF.type, prev.prev.DCAT.Catalog))
    g.add((cat, prev.prev.DCAT.dataset, dataset))
    g.add((dataset, RDF.type, prev.prev.DCAT.Dataset))
    g.add((dataset, DCTERMS.title, en(f"LSC Core Process Ontology {VERSION}")))
    g.add((dataset, DCTERMS.isVersionOf, ONTOLOGY_IRI))
    g.add((dataset, OWL.versionInfo, Literal(VERSION)))
    g.add((dataset, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((dataset, DCTERMS.rights, en(prev.RIGHTS)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"), ("shapes.ttl", "text/turtle"),
                        ("canonical-facts.csv", "text/csv")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, prev.prev.DCAT.distribution, dist))
        g.add((dist, RDF.type, prev.prev.DCAT.Distribution))
        g.add((dist, prev.prev.DCAT.downloadURL, dist))
        g.add((dist, prev.prev.DCAT.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(g, counts):
    """2.1.0's shapes and canonical-fact mapping unchanged; the graph, catalog, counts and changelog new."""
    with open(os.path.join(BASE, "shapes.ttl")) as f:
        shapes_text = f.read()
    with open(os.path.join(BASE, "canonical-facts.csv")) as f:
        mapping_text = f.read()
    files = {"core.ttl": g.serialize(format="turtle"), "core.jsonld": prev.prev.jsonld(g), "shapes.ttl": shapes_text,
             "catalog.ttl": catalog(), "canonical-facts.csv": mapping_text,
             "counts.json": json.dumps(dict(sorted(counts.items())), indent=2) + "\n"}
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(os.path.join(BASE, "manifest.json")) as f:
        base_manifest = f.read()
    files["manifest.json"] = json.dumps({
        "module": "core", "version": VERSION, "release_candidate": False,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{VERSION}",
        "built_from": {"core 2.1.0 manifest": hashlib.sha256(base_manifest.encode()).hexdigest(),
                       "process map": f"{SOURCE_PATH} at {SOURCE_COMMIT}"},
        "decisions": ["EPM-DEC-001-0047", "EPM-DEC-001-0048", "EPM-DEC-001-0051", "EPM-DEC-001-0060",
                      "EPM-DEC-001-0063", "EPM-DEC-001-0076"],
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
    print(f"core {VERSION}: {len(g)} triples; shapes conform; "
          + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()) if not k.startswith(("facts ", "evidence", "canonical"))))
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
