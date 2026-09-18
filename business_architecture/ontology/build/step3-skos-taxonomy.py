#!/usr/bin/env python3
"""Step 3 — Build the SKOS taxonomy for the core module.

Reads the Step 2 identity map (slugs, parents, levels, names, notations)
plus process descriptions from downstream_process_map.json, and emits
one Turtle file:

  - the core module namespace URI doubles as the skos:ConceptScheme
    (https://w3id.org/lsc/ontology/modules/core)
  - 680 skos:Concepts, one per node, in stable document order
  - per concept: skos:inScheme, skos:prefLabel (exactly one, @en),
    skos:notation (where the repo has an ID), skos:definition (where the
    repo has a description), skos:broader (all but the two L0 roots)
  - the two L0 roots as skos:topConceptOf / skos:hasTopConcept

Language policy: every literal carries @en. Definitions are emitted only
where the repo provides them (177/680); the 503 gaps are reported, not
invented — authoring them (or a SHACL shape flagging them) is later work.

Validates with rdflib: parses clean, then runs structural checks
(concept count, one prefLabel each, broader integrity, top concepts).
"""
import argparse
import json
import re
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

HOME = Path.home()
IDENTITY_MAP = HOME / "workspace" / "ontology-build" / "step2-identity-map.json"
SRC = (HOME / "workspace" / "enterprise-performance-model" / "business_architecture"
       / "business_process" / "downstream_process_map.json")
OUT_DIR = HOME / "workspace" / "ontology-build"

BASE = "https://w3id.org/lsc/ontology/"
PROC = Namespace(BASE + "process/")
MOD = Namespace(BASE + "modules/")
SRCNS = Namespace(BASE + "source/")
SCHEME = MOD["core"]
EN = "en"

SRC_APQC = SRCNS["apqc-pcf-7.2.2"]
SRC_EIA = SRCNS["eia-glossary"]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def descriptions_by_id():
    """Map repo node id (or name for stubs) -> description."""
    data = json.loads(SRC.read_text(encoding="utf-8"))
    out = {}

    def walk(n):
        desc = (n.get("description") or "").strip()
        if desc:
            key = n.get("id") or ("L%d %s" % (n["level"], n["name"]))
            out[key] = clean(desc)
        for c in n.get("children", []):
            walk(c)

    for top in data:
        walk(top)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--adoptions', default=None,
                    help='step3b-adoptions.json: slug -> adopted definition '
                         '+ provenance (triangulated APQC/EIA definitions)')
    ap.add_argument('--authored', default=None,
                    help='step3c-authored-definitions.json: slug -> human-'
                         'authored definition + scope note (approved by Hamid)')
    args = ap.parse_args()
    adoptions = {}
    if args.adoptions:
        adoptions = json.loads(Path(args.adoptions).read_text(encoding='utf-8'))
    authored = {}
    if args.authored:
        for d in json.loads(Path(args.authored).read_text(encoding='utf-8')):
            if d.get("status") == "approved":
                authored[d["slug"]] = d

    rows = json.loads(IDENTITY_MAP.read_text(encoding="utf-8"))
    assert len(rows) == 680, f"expected 680 rows, got {len(rows)}"
    descs = descriptions_by_id()

    g = Graph()
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("proc", PROC)
    g.bind("mod", MOD)
    g.bind("src", SRCNS)

    # --- the scheme is the core module namespace ---
    g.add((SCHEME, RDF.type, SKOS.ConceptScheme))
    g.add((SCHEME, DCTERMS.title,
           Literal("LSC downstream process taxonomy", lang=EN)))
    g.add((SCHEME, DCTERMS.description, Literal(
        "SKOS taxonomy of Lagos Specialty Chemicals' downstream petroleum "
        "business processes (levels L0-L6), derived from "
        "business_architecture/business_process/downstream_process_map.json. "
        "The core module namespace serves as the ConceptScheme.",
        lang=EN)))

    by_slug = {r["slug"]: r for r in rows}
    with_definition = 0
    adopted = 0
    authored_count = 0

    if adoptions:
        # source registry: where adopted definitions come from
        g.add((SRC_APQC, RDF.type, DCTERMS.BibliographicResource))
        g.add((SRC_APQC, DCTERMS.title, Literal(
            "APQC Process Classification Framework (PCF) for Downstream "
            "Petroleum, version 7.2.2", lang=EN)))
        g.add((SRC_APQC, DCTERMS.publisher, Literal("APQC", lang=EN)))
        g.add((SRC_APQC, DCTERMS.issued, Literal("2025-05-30")))
        g.add((SRC_APQC, DCTERMS.rights, Literal(
            "Used with attribution per the APQC/IBM license.", lang=EN)))
        g.add((SRC_EIA, RDF.type, DCTERMS.BibliographicResource))
        g.add((SRC_EIA, DCTERMS.title, Literal(
            "U.S. Energy Information Administration (EIA) Glossary", lang=EN)))
        g.add((SRC_EIA, DCTERMS.publisher, Literal(
            "U.S. Energy Information Administration", lang=EN)))
        g.add((SRC_EIA, DCTERMS.rights, Literal(
            "U.S. federal government work; public domain.", lang=EN)))

    for r in rows:
        c = PROC[r["slug"]]
        g.add((c, RDF.type, SKOS.Concept))
        g.add((c, SKOS.inScheme, SCHEME))
        g.add((c, SKOS.prefLabel, Literal(r["name"], lang=EN)))
        if r["skos_notation"]:
            g.add((c, SKOS.notation, Literal(r["skos_notation"])))
        key = r["skos_notation"] or ("L%d %s" % (r["level"], r["name"]))
        if key in descs:
            g.add((c, SKOS.definition, Literal(descs[key], lang=EN)))
            with_definition += 1
        elif r["slug"] in adoptions:
            a = adoptions[r["slug"]]
            apqc = a.get("apqc", {})
            g.add((c, SKOS.definition, Literal(a["definition"], lang=EN)))
            with_definition += 1
            adopted += 1
            # provenance: APQC element + each independent validator
            b1 = BNode()
            g.add((b1, RDF.type, DCTERMS.BibliographicResource))
            g.add((b1, DCTERMS.title, Literal(
                f"APQC Downstream Petroleum PCF v7.2.2, element "
                f"{apqc.get('id')} '{apqc.get('name')}'", lang=EN)))
            g.add((b1, DCTERMS.identifier, Literal(apqc.get("id", ""))))
            g.add((b1, DCTERMS.isPartOf, SRC_APQC))
            g.add((c, DCTERMS.source, b1))
            for v in a.get("validators", []):
                bv = BNode()
                g.add((bv, RDF.type, DCTERMS.BibliographicResource))
                g.add((bv, DCTERMS.title, Literal(
                    f"Independent validator ({v.get('kind', 'web')}): "
                    f"{v.get('label', '')} "
                    f"(agreement {v.get('agreement', 0):.2f})", lang=EN)))
                if v.get("url"):
                    g.add((bv, DCTERMS.identifier, Literal(v["url"])))
                g.add((c, DCTERMS.source, bv))
        elif r["slug"] in authored:
            d = authored[r["slug"]]
            g.add((c, SKOS.definition, Literal(d["definition"], lang=EN)))
            with_definition += 1
            authored_count += 1
            if d.get("scope_note"):
                g.add((c, SKOS.scopeNote,
                       Literal(d["scope_note"], lang=EN)))
            # provenance: human-authored, approved by the domain owner
            ba = BNode()
            g.add((ba, RDF.type, DCTERMS.BibliographicResource))
            g.add((ba, DCTERMS.title, Literal(
                f"Human-authored definition, approved by Hamid "
                f"({d.get('date', '')})", lang=EN)))
            g.add((c, DCTERMS.source, ba))
        parent = r["parent_slug"]
        if parent is None:
            g.add((c, SKOS.topConceptOf, SCHEME))
            g.add((SCHEME, SKOS.hasTopConcept, c))
        else:
            assert parent in by_slug, f"unknown parent {parent}"
            g.add((c, SKOS.broader, PROC[parent]))

    # --- validation ---
    q = lambda s: list(g.query(s, initNs={"skos": SKOS}))
    n_concepts = len(q(
        "SELECT ?c WHERE { ?c a skos:Concept }"))
    assert n_concepts == 680, f"concepts: {n_concepts}"
    multi_label = q(
        "SELECT ?c WHERE { ?c skos:prefLabel ?l1, ?l2 . FILTER(?l1 != ?l2) }")
    assert not multi_label, f"concepts with !=1 prefLabel: {len(multi_label)}"
    no_scheme = q(
        "SELECT ?c WHERE { ?c a skos:Concept . FILTER NOT EXISTS "
        "{ ?c skos:inScheme ?s } }")
    assert not no_scheme, "concepts missing inScheme"
    n_broader = len(q("SELECT ?c WHERE { ?c skos:broader ?p }"))
    assert n_broader == 678, f"broader links: {n_broader}"
    dangling = q(
        "SELECT ?c ?p WHERE { ?c skos:broader ?p . "
        "FILTER NOT EXISTS { ?p a skos:Concept } }")
    assert not dangling, "dangling broader targets"
    self_ref = q(
        "SELECT ?c WHERE { ?c skos:broader ?c }")
    assert not self_ref, "self broader"
    tops = q("SELECT ?c WHERE { ?c skos:topConceptOf ?s }")
    assert len(tops) == 2, f"top concepts: {len(tops)}"
    # every natural-language literal tagged @en
    # (skos:notation is a code, not prose — correctly untagged)
    lang_props = {SKOS.prefLabel, SKOS.altLabel, SKOS.definition,
                  SKOS.scopeNote, DCTERMS.title, DCTERMS.description}
    untagged = [str(o) for s, p, o in g
                if isinstance(o, Literal) and o.language is None
                and isinstance(o.value, str) and p in lang_props]
    assert not untagged, f"untagged literals: {untagged[:3]}"

    ttl = g.serialize(format="turtle")
    # deterministic ordering: rdflib serializes in insertion-ish order;
    # re-parse to prove the file itself is valid Turtle
    g2 = Graph()
    g2.parse(data=ttl, format="turtle")
    assert len(g2) == len(g), "round-trip triple loss"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "step3-taxonomy.ttl").write_text(ttl, encoding="utf-8")

    n_triples = len(g)
    report = f"""# Step 3 — SKOS taxonomy report

- Concepts: 680 (one per process-map node, stable document order)
- Triples: {n_triples}
- `skos:broader` links: 678 (every concept except the two L0 roots)
- Top concepts: `L0-downstream-operations`, `L0-enabling-functions`
- `skos:notation` present: 669 (every ID'd node; original codes preserved)
- `skos:definition` present: {with_definition} of 680{f" ({adopted} triangulated APQC/EIA, {authored_count} human-authored)" if (adopted or authored_count) else ""}
- Untagged literals: 0 (language policy holds)

## ConceptScheme
The core module namespace URI
`https://w3id.org/lsc/ontology/modules/core`
doubles as the `skos:ConceptScheme`. Rationale: the module's entire
current content *is* the taxonomy; one URI, one thing.

## Known gaps (not invented here)
- **Concepts without `skos:definition`.** The repo describes only 177
  nodes. Step 3b triangulates APQC element descriptions against public
  industry definitions (EIA glossary): where the two sources agree and
  the APQC link is strong, the APQC text is adopted with full
  `dcterms:source` provenance. Everything else stays definition-less
  until authored or human-reviewed — see `step3b-definition-review.csv`.
- `skos:narrower` is not materialized: it is `owl:inverseOf`
  `skos:broader` in the SKOS ontology, so it is entailed, not stored.
- RACI, systems, lanes, and other node fields are **not** in this file —
  they belong to Steps 4/5. This file is the taxonomy, nothing more.

## Validation (rdflib, mechanical)
Parsed clean; 680 concepts; exactly one `@en` prefLabel per concept;
every concept in scheme; 678 broader links, no dangling targets, no
self-references; 2 top concepts; zero untagged literals; Turtle
round-trip lossless.
"""
    (OUT_DIR / "step3-taxonomy-report.md").write_text(report, encoding="utf-8")
    print(f"OK: 680 concepts, {n_triples} triples, "
          f"{with_definition}/680 definitions ({adopted} triangulated, {authored_count} human-authored).")


if __name__ == "__main__":
    main()
