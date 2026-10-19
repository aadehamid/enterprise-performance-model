#!/usr/bin/env python3
"""Build the core 1.0.0 release from the pinned Step 4 baseline (EPM-DEC-001-0029).

    python3 build_core.py            # build in memory, check, report; write nothing
    python3 build_core.py --write    # also write releases/core/<version>/
    python3 build_core.py --verify   # the written package equals a fresh build

Inputs: the pinned taxonomy (step4/baseline/step3-taxonomy.ttl), the canonical
facts (step4/canonical-facts.csv), the scoped sequences, the approved label report,
the workbook's reference register, and core-vocabulary.ttl. Every intake: triple
of the baseline goes to the target EPM-DEC-001-0029 names; conservation.csv records
each one, and the build stops if any intake: triple or blank node remains.
Needs rdflib and openpyxl.
"""
import argparse
import hashlib
import csv
import io
import json
import os
import re
import sys

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.dirname(HERE)
STEP4 = os.path.join(ONTOLOGY, "step4")
TAXONOMY = os.path.join(STEP4, "baseline", "step3-taxonomy.ttl")
FACTS = os.path.join(STEP4, "canonical-facts.csv")
SEQ_DIR = os.path.join(STEP4, "scoped-sequence")
LABELS = os.path.join(STEP4, "label-report", "label-dispositions-v1.2.csv")
WORKBOOK = os.path.join(ONTOLOGY, "build", "output", "step3c-definition-authoring-workbook.xlsx")
VOCABULARY = os.path.join(HERE, "core-vocabulary.ttl")
SHAPES = os.path.join(HERE, "shapes.ttl")
CHANGELOG = os.path.join(HERE, "CHANGELOG.md")
PINNED = os.path.join(STEP4, "PINNED_SHA.txt")
VERSION = "1.0.0"
# A package built before the decision owner approves a release is a release candidate (STAGE set,
# no issued date). The decision owner approved core 1.0.0 on 2026-10-13.
STAGE = None
ISSUED = "2026-10-13"
LABEL = VERSION if STAGE is None else f"{VERSION}-{STAGE}"
RELEASE_DIR = os.path.join(ONTOLOGY, "releases", "core", VERSION)

CORE = Namespace("https://w3id.org/lsc/ontology/modules/core/")
INTAKE = Namespace("https://w3id.org/lsc/ontology/intake/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
ONTOLOGY_IRI = URIRef("https://w3id.org/lsc/ontology/modules/core")
CODE = {name: Namespace(f"https://w3id.org/lsc/ontology/modules/core/{name}/") for name in (
    "concept-kind", "apqc-mapping-decision", "operating-mode", "cadence", "planning-level",
    "lifecycle-status", "governance-status", "hold-status")}
PREFIXES = {"core": CORE, "proc": PROC, "src": SRC, "mod": Namespace("https://w3id.org/lsc/ontology/modules/"),
            "seq": Namespace("https://w3id.org/lsc/ontology/sequence/"), "skos": SKOS, "dcterms": DCTERMS,
            "owl": OWL, "xsd": XSD, **{k.replace("-", "_"): v for k, v in CODE.items()},
            "scope": Namespace("https://w3id.org/lsc/ontology/modules/core/scope-unit/"),
            "evb": Namespace("https://w3id.org/lsc/ontology/modules/core/evidence-basis/")}

# Terminology notes (Q10; ledger-v2.md, terminologyNotes): a migration event goes to
# dcterms:provenance; everything else, decision-record pointers included, to
# skos:editorialNote. A note that is both is filed under provenance.
MIGRATION_EVENT = re.compile(r"renam|prior name|formerly|previously (named|labell?ed)|was (named|labell?ed)|"
                             r"tombstone|re-anchor|label[- ]change|relabel|R1 reclassif|reclassif", re.I)
DECISION_POINTER = re.compile(r"decision recorded on|per the decision owner's decision \(|the decision owner accepted Option|"
                              r"PTC-001 \(step3c-parked-tree-changes\.md\)", re.I)
HORIZON = {"event-driven": [("operating-mode", "event-driven")], "continuous": [("operating-mode", "continuous")],
           "periodic": [("operating-mode", "periodic")],
           "daily": [("operating-mode", "periodic"), ("cadence", "daily")],
           "weekly": [("operating-mode", "periodic"), ("cadence", "weekly")],
           "monthly": [("operating-mode", "periodic"), ("cadence", "monthly")],
           "tactical": [("planning-level", "tactical")], "strategic": [("planning-level", "strategic")]}
HORIZON_PROPERTY = {"operating-mode": CORE.operatingMode, "cadence": CORE.cadence, "planning-level": CORE.planningLevel}
KIND = {"process": "process", "capability": "capability", "not-process": "structural-anchor"}
APQC = {"REVIEW LINK": "review-link", "NO SOURCE": "no-source", "NO CANDIDATE": "no-candidate",
        "REJECTED": "rejected", "ADOPTED": "adopted"}


def en(text):
    return Literal(" ".join(str(text).split()), lang="en")


def note_kind(text):
    event, pointer = bool(MIGRATION_EVENT.search(text)), bool(DECISION_POINTER.search(text))
    return ("dual-aspect" if event and pointer else "provenance" if event else
            "decision-pointer" if pointer else "editorial")


def source_tokens(cell):
    """(source ID, annotation) pairs from a reference_sources cell. Segments split on "|";
    a segment without an annotation may hold several IDs split on ";". An annotation
    follows " — " and may itself contain ";"."""
    for segment in cell.split("|"):
        segment = segment.strip()
        m = re.match(r"(SRC-[A-Z0-9-]+)\s+—\s+(.+)", segment)
        if m:
            yield m.group(1), m.group(2).strip()
            continue
        for token in segment.split(";"):
            if token.strip():
                yield token.strip(), ""


def reference_register(path=WORKBOOK):
    from openpyxl import load_workbook
    rows = [r for r in load_workbook(path, read_only=True)["Reference register"].iter_rows(values_only=True) if any(r)]
    header = next(i for i, r in enumerate(rows) if r and r[0] == "source_id")
    fields = rows[header]
    return {r[0]: dict(zip(fields, r)) for r in rows[header + 1:] if r[0]}


def build():
    """Return (graph, conservation rows, counters)."""
    base = Graph()
    base.parse(TAXONOMY)
    out = Graph()
    for k, v in PREFIXES.items():
        out.bind(k, v)
    counts = {}

    def tally(key, n=1):
        counts[key] = counts.get(key, 0) + n

    # 1. Copy every non-intake triple; blank-node resources become IRIs.
    def resolve(node):
        if not isinstance(node, BNode):
            return node
        ident = base.value(node, DCTERMS.identifier)
        part = base.value(node, DCTERMS.isPartOf)
        if ident is not None and part is not None:
            iri = URIRef(f"{part}/element/{ident}")
        elif str(base.value(node, DCTERMS.title)) == "Step 3c definition workbook, approved row":
            iri = SRC["step3c-definition-workbook"]
        else:
            raise SystemExit(f"unexpected blank node: {list(base.predicate_objects(node))}")
        for p, o in base.predicate_objects(node):
            out.add((iri, p, o))
        return iri

    for s, p, o in base:
        if isinstance(s, BNode) or str(p).startswith(str(INTAKE)):
            continue
        out.add((s, p, resolve(o)))
        if isinstance(o, BNode):
            tally("blank nodes resolved")

    # 2. Migrate intake: per EPM-DEC-001-0029.
    register = reference_register()
    for s, p, o in base.triples((None, None, None)):
        if not str(p).startswith(str(INTAKE)):
            continue
        name, value = str(p)[len(str(INTAKE)):], str(o)
        tally(f"source:{name}")
        if name == "level":
            out.add((s, CORE.taxonomyLevel, Literal(int(value.lstrip("L")), datatype=XSD.integer)))
            tally(f"emitted:{name}")
        elif name == "apqcDecision":
            out.add((s, CORE.apqcMappingDecision, CODE["apqc-mapping-decision"][APQC[value]]))
            tally(f"emitted:{name}")
        elif name == "terminologyNotes":
            kind = note_kind(value)
            tally(f"note:{kind}")
            prop = DCTERMS.provenance if kind in ("provenance", "dual-aspect") else SKOS.editorialNote
            out.add((s, prop, en(value)))
            tally(f"emitted:{name}")
        elif name == "referenceSources":
            for ident, annotation in source_tokens(value):
                if ident not in register:
                    raise SystemExit(f"{s}: source {ident!r} is not in the reference register")
                out.add((s, DCTERMS.source, SRC[ident.lower()]))
                tally("source links")
                if annotation:
                    out.add((s, SKOS.editorialNote, en(f"Source note ({ident}): {annotation.strip()}")))
                    tally("source annotations")
            tally(f"emitted:{name}")
        elif name == "primaryPurpose":
            out.add((s, CORE.primaryPurpose, en(value)))
            tally(f"emitted:{name}")
        elif name == "conceptTypeCheck":
            out.add((s, CORE.conceptKind, CODE["concept-kind"][KIND[value]]))
            tally(f"emitted:{name}")
        elif name == "relatedConcepts":
            tally(f"replaced:{name}")  # the canonical facts and scoped sequences, added below
        elif name == "responsibleDomain":
            if value.startswith("Cross-functional"):
                out.add((s, CORE.responsibleDomain, en("Cross-functional")))
                out.add((s, SKOS.note, en(f"Responsible domain detail: {value}")))
                tally("cross-functional normalized")
            else:
                out.add((s, CORE.responsibleDomain, en(value)))
            tally(f"emitted:{name}")
        elif name == "processHorizon":
            for code, member in HORIZON[value]:
                out.add((s, HORIZON_PROPERTY[code], CODE[code][member]))
                tally("horizon facet assignments")
            tally(f"emitted:{name}")
        elif name == "primaryOutput":
            out.add((s, CORE.primaryOutputFlow, en(value)))
            tally(f"emitted:{name}")
        elif name == "keyInputs":
            for flow in value.split("|"):
                if flow.strip():
                    out.add((s, CORE.keyInputFlow, en(flow)))
                    tally("key input flows")
            tally(f"emitted:{name}")
        elif name == "parkedChildren":
            for child in value.split("|"):
                if child.strip():
                    out.add((s, CORE.plannedChildNote, en(child)))
            tally(f"emitted:{name}")
        elif name == "status":
            if value == "retired":
                out.add((s, CORE.lifecycleStatus, CODE["lifecycle-status"]["retired"]))
                out.add((s, OWL.deprecated, Literal(True)))
            elif value == "blocked":
                out.add((s, CORE.holdStatus, CODE["hold-status"]["implementation-hold"]))
                reason = base.value(s, INTAKE.terminologyNotes)
                out.add((s, CORE.holdReason, en(reason if reason is not None else "Blocked in the Step 3c workbook.")))
            else:
                raise SystemExit(f"{s}: unknown status {value!r}")
            tally(f"emitted:{name}")
        else:
            raise SystemExit(f"{s}: no target for intake:{name}")

    # 3. Sources cited by reference_sources, from the workbook register.
    for ident, row in register.items():
        iri = SRC[ident.lower()]
        if (None, DCTERMS.source, iri) not in out:
            continue
        out.add((iri, RDF.type, DCTERMS.BibliographicResource))
        out.add((iri, DCTERMS.identifier, Literal(ident)))
        out.add((iri, DCTERMS.title, en(row["title"])))
        for field, prop in (("organization", DCTERMS.publisher), ("version_or_date", DCTERMS.hasVersion),
                            ("url_or_identifier", DCTERMS.bibliographicCitation), ("permitted_use", DCTERMS.rights)):
            if row.get(field):
                out.add((iri, prop, en(row[field])))

    # 4. Former names: the approved label report (Q10).
    with open(LABELS, newline="") as f:
        for row in csv.DictReader(f):
            s, label = PROC[row["concept_slug"]], en(row["historical_label"])
            disposition = row["proposed_disposition"]
            if row["label_kind"] == "prior_name" and disposition in ("AddAsAltLabel", "RetainAsAltLabel"):
                out.add((s, SKOS.altLabel, label))
                tally(f"label:{disposition}")
            else:
                out.remove((s, SKOS.altLabel, label))
                out.add((s, CORE.priorPreferredLabel, label))
                tally(f"label:{disposition if row['label_kind'] == 'prior_name' else 'scoped alias'}")

    # 5. Canonical facts, the scoped sequences and the core vocabulary.
    with open(FACTS, newline="") as f:
        for row in csv.DictReader(f):
            out.add((PROC[row["subject"]], CORE[row["predicate"].split(":", 1)[1]], PROC[row["object"]]))
            tally("canonical facts")
    for path in (VOCABULARY, os.path.join(SEQ_DIR, "vocabulary.ttl"), os.path.join(SEQ_DIR, "scoped-sequences.ttl")):
        out.parse(path)

    # The scoped sequences cite the source author's answers as GitHub issue comments, named by
    # URN (EPM-DEC-001-0049); describe each so every dcterms:source resolves to a described resource.
    for page in set(out.objects(None, DCTERMS.source)):
        m = re.match(r"urn:epm:issue:(\d+):comment:(\d+)$", str(page))
        if m and (page, RDF.type, None) not in out:
            out.add((page, RDF.type, DCTERMS.BibliographicResource))
            out.add((page, DCTERMS.title, en(f"Source-author answer, GitHub issue #{m.group(1)}, comment {m.group(2)}")))
            tally("answer pages described")

    # 6. Ontology header (ontology-playbook.md, worked example).
    out.add((ONTOLOGY_IRI, RDF.type, OWL.Ontology))
    # The taxonomy names its concept scheme on the same IRI; the ontology header replaces that.
    out.remove((ONTOLOGY_IRI, DCTERMS.title, None))
    out.remove((ONTOLOGY_IRI, DCTERMS.description, None))
    out.add((ONTOLOGY_IRI, DCTERMS.title, en("LSC Core Process Ontology")))
    out.add((ONTOLOGY_IRI, DCTERMS.description, en(
        "Governed definitions of LSC's business processes: identity, hierarchy, relationships, and lifecycle.")))
    out.add((ONTOLOGY_IRI, OWL.versionIRI, URIRef(f"{ONTOLOGY_IRI}/{LABEL}")))
    out.add((ONTOLOGY_IRI, OWL.versionInfo, Literal(LABEL)))
    out.add((ONTOLOGY_IRI, DCTERMS.creator, Literal("The decision owner")))
    if ISSUED:
        out.add((ONTOLOGY_IRI, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
        out.add((ONTOLOGY_IRI, DCTERMS.modified, Literal(ISSUED, datatype=XSD.date)))
    out.add((ONTOLOGY_IRI, DCTERMS.license, URIRef(f"{ONTOLOGY_IRI}/license")))

    # 7. Nothing intake:, no blank nodes.
    leftovers = [t for t in out if any(str(x).startswith(str(INTAKE)) for x in t)]
    blanks = [t for t in out if any(isinstance(x, BNode) for x in t)]
    if leftovers or blanks:
        raise SystemExit(f"{len(leftovers)} intake: triples and {len(blanks)} blank-node triples remain")
    return out, counts


def conservation(counts):
    """The after half of the ledger: each intake: predicate's source count and destination."""
    target = {"level": "core:taxonomyLevel", "apqcDecision": "core:apqcMappingDecision",
              "terminologyNotes": "dcterms:provenance / skos:editorialNote",
              "referenceSources": "dcterms:source (src:)", "primaryPurpose": "core:primaryPurpose",
              "conceptTypeCheck": "core:conceptKind", "relatedConcepts": "canonical facts and scoped sequences",
              "responsibleDomain": "core:responsibleDomain", "processHorizon": "core:operatingMode / cadence / planningLevel",
              "primaryOutput": "core:primaryOutputFlow", "keyInputs": "core:keyInputFlow",
              "parkedChildren": "core:plannedChildNote", "status": "core:lifecycleStatus / core:holdStatus"}
    rows = []
    for name in sorted(target):
        src = counts.get(f"source:{name}", 0)
        done = counts.get(f"emitted:{name}", 0) + counts.get(f"replaced:{name}", 0)
        rows.append({"intake_predicate": name, "source_triples": src, "migrated": done, "target": target[name]})
        if done != src:
            raise SystemExit(f"intake:{name}: {src} source triples, {done} migrated")
    return rows


def shacl_report(graph):
    """(conforms, report text) for the release slice (EPM-DEC-001-0014)."""
    from pyshacl import validate
    shapes = Graph()
    shapes.parse(SHAPES)
    conforms, _, text = validate(graph, shacl_graph=shapes, advanced=True, inference="none")
    return conforms, text


def jsonld(graph):
    """JSON-LD with nodes, keys and values in a fixed order, so a rebuild is byte-identical."""
    data = json.loads(graph.serialize(format="json-ld"))
    nodes = data if isinstance(data, list) else data.get("@graph", [data])
    for node in nodes:
        for key, value in node.items():
            if isinstance(value, list):
                node[key] = sorted(value, key=lambda v: json.dumps(v, sort_keys=True))
    nodes.sort(key=lambda n: n.get("@id", ""))
    return json.dumps(nodes, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def serialize(graph):
    return graph.serialize(format="turtle")


def catalog():
    """The DCAT record of this release: one dataset version with its distributions."""
    dcat = Namespace("http://www.w3.org/ns/dcat#")
    base = f"{ONTOLOGY_IRI}/releases/{LABEL}"
    g = Graph()
    g.bind("dcat", dcat)
    g.bind("dcterms", DCTERMS)
    catalog_iri, dataset = URIRef("https://w3id.org/lsc/ontology/catalog"), URIRef(f"{ONTOLOGY_IRI}/{LABEL}")
    g.add((catalog_iri, RDF.type, dcat.Catalog))
    g.add((catalog_iri, dcat.dataset, dataset))
    g.add((dataset, RDF.type, dcat.Dataset))
    g.add((dataset, DCTERMS.title, en(f"LSC Core Process Ontology {LABEL}")))
    g.add((dataset, DCTERMS.isVersionOf, ONTOLOGY_IRI))
    if ISSUED:
        g.add((dataset, DCTERMS.issued, Literal(ISSUED, datatype=XSD.date)))
    g.add((dataset, OWL.versionInfo, Literal(LABEL)))
    for name, media in (("core.ttl", "text/turtle"), ("core.jsonld", "application/ld+json"),
                        ("shapes.ttl", "text/turtle"), ("canonical-facts.csv", "text/csv")):
        dist = URIRef(f"{base}/{name}")
        g.add((dataset, dcat.distribution, dist))
        g.add((dist, RDF.type, dcat.Distribution))
        g.add((dist, dcat.downloadURL, dist))
        g.add((dist, dcat.mediaType, Literal(media)))
    return g.serialize(format="turtle")


def package(graph, counts, rows):
    files = {"core.ttl": serialize(graph), "core.jsonld": jsonld(graph)}
    with open(SHAPES) as f:
        files["shapes.ttl"] = f.read()
    files["catalog.ttl"] = catalog()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    files["conservation.csv"] = buf.getvalue()
    with open(FACTS, newline="") as f:
        files["canonical-facts.csv"] = f.read()
    with open(LABELS, newline="") as f:
        files["label-dispositions.csv"] = f.read()
    files["counts.json"] = json.dumps(dict(sorted(counts.items())), indent=2) + "\n"
    with open(CHANGELOG) as f:
        files["CHANGELOG.md"] = f.read()
    with open(PINNED) as f:
        pin = f.read().strip()
    # The manifest names the evidence commit the package was built from, and each file's SHA-256.
    files["manifest.json"] = json.dumps({
        "module": "core", "version": LABEL, "release_candidate": STAGE is not None,
        "ontology_iri": str(ONTOLOGY_IRI), "version_iri": f"{ONTOLOGY_IRI}/{LABEL}", "built_from_pin": pin,
        "files": {n: hashlib.sha256(t.encode()).hexdigest() for n, t in sorted(files.items())}}, indent=2) + "\n"
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    graph, counts = build()
    rows = conservation(counts)
    conforms, report = shacl_report(graph)
    if not conforms:
        sys.exit("SHACL release slice fails:\n" + report)
    files = package(graph, counts, rows)
    print(f"core {LABEL}: {len(graph)} triples; SHACL slice conforms; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if args.verify:
        def current(n, text):
            path = os.path.join(RELEASE_DIR, n)
            if not os.path.exists(path):
                return False
            with open(path, newline="") as f:  # byte-for-byte: the CSVs keep their CRLF line ends
                return f.read() == text
        stale = [n for n, text in files.items() if not current(n, text)]
        if stale:
            sys.exit(f"release package is not current: {stale}")
        print("release package is current")
    if args.write:
        os.makedirs(RELEASE_DIR, exist_ok=True)
        for n, text in files.items():
            with open(os.path.join(RELEASE_DIR, n), "w", newline="") as f:
                f.write(text)
        print(f"wrote {RELEASE_DIR}")


if __name__ == "__main__":
    main()
