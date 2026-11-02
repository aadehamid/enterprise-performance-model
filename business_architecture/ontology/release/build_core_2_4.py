"""Build core 2.4.0 from the released core 2.3.0 (EPM-DEC-001-0105).

    python3 build_core_2_4.py            # build, validate, print the figures
    python3 build_core_2_4.py --write    # write releases/core/2.4.0/
    python3 build_core_2_4.py --verify   # fail unless the written package equals a fresh build

core 2.3.0 stays as it was released (build_core_2_3.py). This builder starts from that graph and
applies three changes, none of which adds or removes an IRI:

1. MPC-P12 (EPM-DEC-001-0105): the 25 processes that shared one of seven names in the process map
   take the names the map now gives them, read from the map at a pinned commit. The old name stays
   as core:priorPreferredLabel. Any other map change since 2.3.0 stops the build, except to the
   `systems` field, which core does not read.
2. EPM-DEC-001-0098, item 2: the four alternative labels in core that equal another concept's
   preferred label move to core:priorPreferredLabel.
3. EPM-DEC-001-0098, item 5: each of core's eleven flat code lists states every member as a top
   concept, both ways (skos:topConceptOf and skos:hasTopConcept).

It changes labels and adds statements, and removes no IRI, so it is a minor release. Claude approved
it under the decision owner's delegation (APPROVAL below; EPM-DEC-001-0028, 0105).
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

import build_core_2_3 as prev
import build_module as bm  # release mode, and where an approval is recorded
import frozen_sources
import newest

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
BASE = frozen_sources.package_dir(ONTOLOGY, "core", "2.3.0")  # or the share release's history folder
SOURCE_PATH = prev.SOURCE_PATH
# The map as 2.3.0 was built from it, and the map as 2.4.0 is built from it: the commit that applied
# MPC-P12, the last change to the map's names before this release.
EARLIER_COMMIT = prev.SOURCE_COMMIT
SOURCE_COMMIT = "4906666a06507d9c7d996d83df7b24ab824038d7"
CHANGELOG = os.path.join(ONTOLOGY, "releases", "core", "CHANGELOG-2.4.0.md")
VERSION, ISSUED = "2.4.0", "2026-10-26"
APPROVER = "Claude, under the decision owner's delegation (EPM-DEC-001-0028, amendment of 2026-10-25, evening)"
# Where the delegation is recorded: (saved file, the decision owner's words in its body).
APPROVAL = ("step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md",
            "Yes, delegate as described (Recommended)")
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", VERSION)

CORE, PROC, ONTOLOGY_IRI, SCHEME = prev.CORE, prev.PROC, prev.ONTOLOGY_IRI, prev.SCHEME

# MPC-P12, as the decision owner accepted it: slug -> (name in 2.3.0, name in 2.4.0).
_ANALYSES = {"1": ("Market", "Market Analysis"), "2": ("Company", "Company Analysis"),
             "3": ("Consumer", "Consumer Analysis"), "4": ("Customer and Marketer", "Customer And Marketer Analysis"),
             "5": ("Competitor", "Competitor Analysis")}
RENAMES = {}
for _n, (_subject, _parent) in _ANALYSES.items():
    RENAMES[f"CM-1-3-1-{_n}-1"] = ("Source & Collect Information", f"Source & Collect Information for {_parent}")
    RENAMES[f"CM-1-3-1-{_n}-2"] = ("Define Analysis Objectives & Scope", f"Define Analysis Objectives & Scope for {_parent}")
    RENAMES[f"CM-1-3-1-{_n}-3"] = ("Analyze Data", f"Analyze {_subject} Data")
    RENAMES[f"CM-1-3-1-{_n}-4"] = ("Document Findings", f"Document Findings of {_parent}")
RENAMES.update({
    "CM-1-3-8-1-3": ("Determine Taxability", "Determine Invoice Taxability"),
    "CM-1-3-8-4-5": ("Determine Taxability", "Determine Taxability for Reporting"),
    "CM-1-1-2-6-1": ("Obtain latest XPIMS MOP model", "Obtain latest XPIMS MOP model for Crude Oil Evaluation"),
    "CM-1-1-2-7-1": ("Obtain latest XPIMS MOP model", "Obtain latest XPIMS MOP model for Product Evaluation"),
    "CM-1-2-3-1": ("Actualizations", "Perform Actualizations"),
})
# Map fields core does not read: a change to one of them is not a change to core.
UNREAD_FIELDS = {"systems"}
# EPM-DEC-001-0098, item 2: slug -> the alternative label that equals another concept's preferred label.
MOVED_ALT_LABELS = {
    "CM-1-3-2-3-1": "Test Customer value proposition",
    "CM-1-3-2-3-2": "Formulate and Evaluate Strategic Operating Alternatives (CVP)",
    "CM-1-3-2-3-3": "Establish CVP principles and objectives",
    "CM-1-3-2-3-4": "Develop/Update Strategy (CVP)",
}
# EPM-DEC-001-0098, item 5: core's flat code lists.
CODE_LISTS = ["ApqcMappingDecision", "BusinessDomain", "Cadence", "ConceptKind", "EvidenceBases", "GovernanceStatus",
              "HoldStatus", "LifecycleStatus", "OperatingMode", "PlanningLevel", "ScopeUnits"]


def en(text):
    return Literal(text, lang="en")


def renames(earlier=None, current=None):
    """The map's changes since 2.3.0: slug -> (old name, new name). Anything other than an approved rename stops."""
    earlier = earlier if earlier is not None else prev.prev.map_nodes(EARLIER_COMMIT)
    current = current if current is not None else prev.prev.map_nodes(SOURCE_COMMIT)
    if set(earlier) != set(current):
        sys.exit(f"the map added or removed nodes since 2.3.0: added {sorted(set(current) - set(earlier))}, "
                 f"removed {sorted(set(earlier) - set(current))}")
    found = {}
    for slug, (node, parent) in current.items():
        old, old_parent = earlier[slug]
        if parent != old_parent:
            sys.exit(f"{slug} moved from {old_parent} to {parent}; a move is not a minor change")
        changed = {k for k in set(old) | set(node) if old.get(k) != node.get(k)} - UNREAD_FIELDS
        if not changed:
            continue
        if changed != {"name"} or slug not in RENAMES or (old["name"], node["name"]) != RENAMES[slug]:
            sys.exit(f"{slug}: map fields {sorted(changed)} changed beyond MPC-P12: {old.get('name')!r} -> {node.get('name')!r}")
        found[slug] = (old["name"], node["name"])
    if set(found) != set(RENAMES):
        sys.exit(f"MPC-P12 renames missing from the map: {sorted(set(RENAMES) - set(found))}")
    return found


def build():
    g = Graph()
    g.parse(os.path.join(BASE, "core.ttl"))
    for slug, (old, new) in sorted(renames().items()):
        s = URIRef(PROC + slug)
        if g.value(s, SKOS.prefLabel) != en(old) or len(list(g.objects(s, SKOS.prefLabel))) != 1:
            sys.exit(f"{slug}: its 2.3.0 preferred label is not {old!r}")
        g.remove((s, SKOS.prefLabel, None))
        g.add((s, SKOS.prefLabel, en(new)))
        g.add((s, CORE.priorPreferredLabel, en(old)))
        g.add((s, SKOS.changeNote, en(
            f"core {VERSION} ({ISSUED}): renamed from '{old}' to '{new}', the name the process map gives it from "
            f"commit {SOURCE_COMMIT[:7]}, by MPC-P12 (EPM-DEC-001-0105). The old name, which other processes shared, "
            "is kept as the prior preferred label.")))
    for slug, label in sorted(MOVED_ALT_LABELS.items()):
        s = URIRef(PROC + slug)
        if (s, SKOS.altLabel, en(label)) not in g:
            sys.exit(f"{slug}: {label!r} is not a 2.3.0 alternative label")
        g.remove((s, SKOS.altLabel, en(label)))
        g.add((s, CORE.priorPreferredLabel, en(label)))
        g.add((s, SKOS.changeNote, en(
            f"core {VERSION} ({ISSUED}): '{label}' moved from alternative label to prior preferred label, because "
            "another process has it as its preferred label (EPM-DEC-001-0098, item 2; EPM-DEC-001-0105).")))
    tops = 0
    for name in CODE_LISTS:
        scheme = CORE[name]
        if (scheme, RDF.type, SKOS.ConceptScheme) not in g:
            sys.exit(f"core:{name} is not a concept scheme")
        members = sorted(s for s in g.subjects(SKOS.inScheme, scheme) if (s, RDF.type, SKOS.Concept) in g)
        if not members:
            sys.exit(f"core:{name} has no members")
        for s in members:
            if any(g.value(p, SKOS.inScheme) == scheme for p in g.objects(s, SKOS.broader)):
                sys.exit(f"{s}: it has a parent in core:{name}, which is not a flat code list")
            g.add((s, SKOS.topConceptOf, scheme))
            g.add((scheme, SKOS.hasTopConcept, s))
            tops += 1
    for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion):
        g.remove((ONTOLOGY_IRI, p, None))
    g.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(VERSION)))
    g.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{VERSION}")))
    g.add((ONTOLOGY_IRI, OWL.priorVersion, URIRef(f"{ONTOLOGY_IRI}/2.3.0")))
    g.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    with open(os.path.join(BASE, "counts.json")) as f:
        counts = Counter(json.load(f))
    del counts["new concepts"]  # 2.3.0's change; this release adds no concept
    counts["process concepts"] = sum(1 for s in g.subjects(RDF.type, SKOS.Concept) if str(s).startswith(PROC))
    counts["renamed concepts"] = len(RENAMES)
    counts["alternative labels moved"] = len(MOVED_ALT_LABELS)
    counts["code-list top concepts"] = tops
    return g, counts


def catalog():
    base = f"{ONTOLOGY_IRI}/releases/{VERSION}"
    dcat = prev.prev.prev.prev.DCAT
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
    g.add((dataset, DCTERMS.rights, en(prev.prev.prev.RIGHTS)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"), ("shapes.ttl", "text/turtle"),
                        ("canonical-facts.csv", "text/csv")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, dcat.distribution, dist))
        g.add((dist, RDF.type, dcat.Distribution))
        g.add((dist, dcat.downloadURL, dist))
        g.add((dist, dcat.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(g, counts):
    """2.3.0's shapes and canonical-fact mapping unchanged; the graph, catalog, counts and changelog new."""
    with open(os.path.join(BASE, "shapes.ttl")) as f:
        shapes_text = f.read()
    with open(os.path.join(BASE, "canonical-facts.csv")) as f:
        mapping_text = f.read()
    files = {"core.ttl": g.serialize(format="turtle"), "core.jsonld": prev.prev.prev.prev.jsonld(g),
             "shapes.ttl": shapes_text, "catalog.ttl": catalog(), "canonical-facts.csv": mapping_text,
             "counts.json": json.dumps(dict(sorted(counts.items())), indent=2) + "\n"}
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(os.path.join(BASE, "manifest.json")) as f:
        base_manifest = f.read()
    files["manifest.json"] = json.dumps({
        "module": "core", "version": VERSION, "release_candidate": False,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{VERSION}",
        "built_from": {"core 2.3.0 manifest": hashlib.sha256(base_manifest.encode()).hexdigest(),
                       "process map": f"{SOURCE_PATH} at {SOURCE_COMMIT}"},
        "decisions": ["EPM-DEC-001-0028", "EPM-DEC-001-0098", "EPM-DEC-001-0105"],
        "approval": {"who": APPROVER, **({"file": where} if (where := bm.recorded_where(APPROVAL[0])) else {}), "words": APPROVAL[1]},
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
          f"renamed {counts['renamed concepts']}, alternative labels moved {counts['alternative labels moved']}, "
          f"code-list top concepts {counts['code-list top concepts']}")
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
