#!/usr/bin/env python3
"""Step 3 — Build the SKOS taxonomy for the core module.

Reads the Step 2 identity map (slugs, parents, levels, names, notations)
plus process descriptions from downstream_process_map.json, and emits
one Turtle file. Optional overlays, in precedence order:

  --workbook   Step 3c definition workbook: approved rows contribute
               definitions, scope notes (with in/out-of-scope boundaries),
               altLabels, APQC references, and provisional intake:
               annotations (Phase-1 capture, verbatim, promoted to real
               properties in Step 4). Blocked rows stay definition-less;
               retired rows are marked owl:deprecated.
  --authored   step3c-authored-definitions.json (14 human-authored L1–L3)
  --adoptions  step3b-adoptions.json (triangulated APQC/EIA definitions)

  - the core module namespace URI doubles as the skos:ConceptScheme
    (https://w3id.org/lsc/ontology/modules/core)
  - one skos:Concept per node, in stable document order
  - per concept: skos:inScheme, skos:prefLabel (exactly one, @en),
    skos:notation (where the repo has an ID), skos:definition (where the
    repo has a description), skos:broader (all but the two L0 roots)
  - the two L0 roots as skos:topConceptOf / skos:hasTopConcept

Language policy: every literal carries @en. Definitions are emitted only
where the repo provides them; the 505 gaps are reported, not
invented — authoring them (or a SHACL shape flagging them) is later work.

Validates with rdflib: parses clean, then runs structural checks
(concept count, one prefLabel each, broader integrity, top concepts,
workbook overlay integrity: every approved row defined, blocked rows
definition-less, retired rows deprecated).
"""
import argparse
import json
import re
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

HOME = Path.home()
IDENTITY_MAP = HOME / "workspace" / "ontology-build" / "step2-identity-map.json"
SRC = (HOME / "workspace" / "enterprise-performance-model" / "business_architecture"
       / "business_process" / "downstream_process_map.json")
OUT_DIR = HOME / "workspace" / "ontology-build"

BASE = "https://w3id.org/lsc/ontology/"
PROC = Namespace(BASE + "process/")
MOD = Namespace(BASE + "modules/")
SRCNS = Namespace(BASE + "source/")
# Provisional intake annotations: workbook Phase-1 fields carried as literals
# until Step 4 promotes them to real properties between concept URIs.
# Anything under intake/ is explicitly NOT the Step 4 model — it is the
# reviewer's captured text, preserved verbatim in the graph so nothing is
# lost between the workbook and the ontology.
INTAKE = Namespace(BASE + "intake/")
SCHEME = MOD["core"]
EN = "en"

SRC_APQC = SRCNS["apqc-pcf-7.2.2"]
SRC_EIA = SRCNS["eia-glossary"]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def descriptions_by_id(src_path):
    """Map repo node id (or name for stubs) -> description."""
    data = json.loads(Path(src_path).read_text(encoding="utf-8"))
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


def split_pipe(text):
    return [p.strip() for p in str(text or "").split("|") if p.strip()]


def read_workbook(path):
    """Read the Step 3c definition workbook.

    Returns {slug: dict} for rows with status approved/blocked/retired.
    Pending rows add nothing beyond the base tree, so they are skipped.
    Raises on an approved row without a definition (the gate should have
    caught it, but the taxonomy build must not silently emit one either).
    """
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["Review & authoring"]
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    rows = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        status = (r[idx["status"]] or "").strip()
        if status not in ("approved", "blocked", "retired"):
            continue
        slug = (r[idx["slug"]] or "").strip()
        if not slug:
            continue
        defi = (r[idx["definition"]] or "").strip()
        if status == "approved" and not defi:
            raise ValueError(f"approved row {slug} has no definition")
        rows[slug] = {
            "status": status,
            "definition": defi,
            "scope_note": (r[idx["scope_note"]] or "").strip(),
            "in_scope": (r[idx["in_scope"]] or "").strip(),
            "out_of_scope": (r[idx["out_of_scope"]] or "").strip(),
            "alt_labels": split_pipe(r[idx["alt_labels"]]),
            "apqc_id": (r[idx["apqc_id"]] or "").strip(),
            "apqc_decision": (r[idx["apqc_decision"]] or "").strip(),
            "key_inputs": (r[idx["key_inputs"]] or "").strip(),
            "primary_output": (r[idx["primary_output"]] or "").strip(),
            "related_concepts": (r[idx["related_concepts"]] or "").strip(),
            "responsible_domain": (r[idx["responsible_domain"]] or "").strip(),
            "process_horizon": (r[idx["process_horizon"]] or "").strip(),
            "primary_purpose": (r[idx["primary_purpose"]] or "").strip(),
            "reference_sources": (r[idx["reference_sources"]] or "").strip(),
            "terminology_notes": (r[idx["terminology_notes"]] or "").strip(),
            "concept_type_check": (r[idx["concept_type_check"]] or "").strip(),
            "parked_children": (r[idx["parked_children"]] or "").strip(),
        }
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--adoptions', default=None,
                    help='step3b-adoptions.json: slug -> adopted definition '
                         '+ provenance (triangulated APQC/EIA definitions)')
    ap.add_argument('--authored', default=None,
                    help='step3c-authored-definitions.json: slug -> human-'
                         'authored definition + scope note (approved by Hamid)')
    ap.add_argument('--workbook', default=None,
                    help='step3c-definition-authoring-workbook.xlsx: approved '
                         'rows overlay the taxonomy (definitions, scope notes, '
                         'altLabels, APQC refs, intake annotations); blocked '
                         'rows stay definition-less; retired rows are marked '
                         'owl:deprecated')
    ap.add_argument('--identity-map', default=str(IDENTITY_MAP))
    ap.add_argument('--src', default=str(SRC))
    ap.add_argument('--out-dir', default=str(OUT_DIR))
    args = ap.parse_args()
    adoptions = {}
    if args.adoptions:
        adoptions = json.loads(Path(args.adoptions).read_text(encoding='utf-8'))
    authored = {}
    if args.authored:
        for d in json.loads(Path(args.authored).read_text(encoding='utf-8')):
            if d.get("status") == "approved":
                authored[d["slug"]] = d
    wb_rows = {}
    if args.workbook:
        wb_rows = read_workbook(args.workbook)

    rows = json.loads(Path(args.identity_map).read_text(encoding="utf-8"))
    n_rows = len(rows)
    assert n_rows > 0, "identity map is empty"
    # broader links == parented rows (every concept except the L0 roots).
    # Derived, not hardcoded: R1 added one concept (683) and one broader link.
    n_broader_expected = sum(1 for r in rows if r["parent_slug"] is not None)
    descs = descriptions_by_id(args.src)

    g = Graph()
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)
    g.bind("proc", PROC)
    g.bind("mod", MOD)
    g.bind("src", SRCNS)
    g.bind("intake", INTAKE)

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
    workbook_count = 0
    workbook_altlabels = 0
    workbook_apqc_refs = 0
    n_deprecated = 0
    n_blocked = 0

    # Every approved/blocked/retired workbook row must name a real concept.
    unknown = [s for s in wb_rows if s not in by_slug]
    assert not unknown, f"workbook rows with unknown slugs: {unknown[:5]}"

    def prov_source(concept, title):
        b = BNode()
        g.add((b, RDF.type, DCTERMS.BibliographicResource))
        g.add((b, DCTERMS.title, Literal(title, lang=EN)))
        g.add((concept, DCTERMS.source, b))
        return b

    def apqc_ref(concept, apqc_id, link=DCTERMS.references, name=""):
        # Reference to an APQC PCF element, with the element id queryable.
        # link is dcterms:references for a mapping, dcterms:source when the
        # APQC text is the definition's provenance (step3b adoptions).
        b = BNode()
        g.add((b, RDF.type, DCTERMS.BibliographicResource))
        title = (f"APQC Downstream Petroleum PCF v7.2.2, element {apqc_id}"
                 + (f" '{name}'" if name else ""))
        g.add((b, DCTERMS.title, Literal(title, lang=EN)))
        g.add((b, DCTERMS.identifier, Literal(apqc_id)))
        g.add((b, DCTERMS.isPartOf, SRC_APQC))
        g.add((concept, link, b))
        return b

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
        slug = r["slug"]
        c = PROC[slug]
        g.add((c, RDF.type, SKOS.Concept))
        g.add((c, SKOS.inScheme, SCHEME))
        g.add((c, SKOS.prefLabel, Literal(r["name"], lang=EN)))
        if r["skos_notation"]:
            g.add((c, SKOS.notation, Literal(r["skos_notation"])))
        # L0–L6 level: locked taxonomy structure (Step 2/3), carried as an
        # intake annotation until Step 4 decides its permanent predicate.
        g.add((c, INTAKE["level"], Literal(f"L{r['level']}", lang=EN)))
        key = r["skos_notation"] or ("L%d %s" % (r["level"], r["name"]))

        w = wb_rows.get(slug)
        w_status = w["status"] if w else None

        # --- definition precedence: workbook approved > authored >
        # --- step3b adoption > repo description. A retired or blocked row
        # --- never carries a definition, even if the repo described it:
        # --- retired nodes are deprecated tombstones (kept for lineage,
        # --- excluded from active navigation), blocked nodes are parked.
        defined = False
        if w_status == "approved":
            g.add((c, SKOS.definition, Literal(w["definition"], lang=EN)))
            defined = True
            workbook_count += 1
            prov_source(c, "Step 3c definition workbook, approved row")
            scope_parts = [w["scope_note"]]
            if w["in_scope"]:
                scope_parts.append("In scope: " + w["in_scope"])
            if w["out_of_scope"]:
                scope_parts.append("Out of scope: " + w["out_of_scope"])
            scope_text = "\n".join(p for p in scope_parts if p).strip()
            if scope_text:
                g.add((c, SKOS.scopeNote, Literal(scope_text, lang=EN)))
            for alt in w["alt_labels"]:
                g.add((c, SKOS.altLabel, Literal(alt, lang=EN)))
                workbook_altlabels += 1
            if w["apqc_id"]:
                apqc_ref(c, w["apqc_id"])
                workbook_apqc_refs += 1
            # The APQC mapping decision (REVIEW LINK / ADOPTED / REJECTED /
            # NO CANDIDATE / NO SOURCE) is ontology-relevant provenance:
            # REJECTED rows are deliberate divergences (competency Q12).
            if w["apqc_decision"]:
                g.add((c, INTAKE["apqcDecision"],
                       Literal(w["apqc_decision"], lang=EN)))
            # Provisional intake annotations — verbatim reviewer capture,
            # to be promoted to real Step 4 properties between concept URIs.
            for col, pred in (
                ("key_inputs", "keyInputs"),
                ("primary_output", "primaryOutput"),
                ("related_concepts", "relatedConcepts"),
                ("responsible_domain", "responsibleDomain"),
                ("process_horizon", "processHorizon"),
                ("primary_purpose", "primaryPurpose"),
                ("reference_sources", "referenceSources"),
                ("terminology_notes", "terminologyNotes"),
                ("concept_type_check", "conceptTypeCheck"),
                ("parked_children", "parkedChildren"),
            ):
                if w[col]:
                    g.add((c, INTAKE[pred], Literal(w[col], lang=EN)))
        elif w_status in ("blocked", "retired"):
            n_blocked += 1 if w_status == "blocked" else 0
            g.add((c, INTAKE["status"], Literal(w_status, lang=EN)))
            if w["terminology_notes"]:
                g.add((c, INTAKE["terminologyNotes"],
                       Literal(w["terminology_notes"], lang=EN)))
            if w_status == "retired":
                # Deprecate, don't delete (version policy). No
                # dcterms:isReplacedBy yet — destinations are undecided
                # until the Step 3d tree pass closes the PTC entry.
                g.add((c, OWL.deprecated, Literal(True)))
                n_deprecated += 1
        elif slug in authored:
            d = authored[slug]
            g.add((c, SKOS.definition, Literal(d["definition"], lang=EN)))
            defined = True
            authored_count += 1
            if d.get("scope_note"):
                g.add((c, SKOS.scopeNote,
                       Literal(d["scope_note"], lang=EN)))
            # provenance: human-authored, approved by the domain owner
            prov_source(c, f"Human-authored definition, approved by Hamid "
                           f"({d.get('date', '')})")
        elif slug in adoptions:
            a = adoptions[slug]
            apqc = a.get("apqc", {})
            g.add((c, SKOS.definition, Literal(a["definition"], lang=EN)))
            defined = True
            adopted += 1
            # provenance: APQC element + each independent validator
            apqc_ref(c, apqc.get("id", ""), link=DCTERMS.source,
                     name=apqc.get("name", ""))
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
        elif key in descs:
            g.add((c, SKOS.definition, Literal(descs[key], lang=EN)))
            defined = True
        if defined:
            with_definition += 1
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
    assert n_concepts == n_rows, f"concepts: {n_concepts} != identity rows {n_rows}"
    multi_label = q(
        "SELECT ?c WHERE { ?c skos:prefLabel ?l1, ?l2 . FILTER(?l1 != ?l2) }")
    assert not multi_label, f"concepts with !=1 prefLabel: {len(multi_label)}"
    no_scheme = q(
        "SELECT ?c WHERE { ?c a skos:Concept . FILTER NOT EXISTS "
        "{ ?c skos:inScheme ?s } }")
    assert not no_scheme, "concepts missing inScheme"
    n_broader = len(q("SELECT ?c WHERE { ?c skos:broader ?p }"))
    assert n_broader == n_broader_expected, \
        f"broader links: {n_broader} != parented rows {n_broader_expected}"
    dangling = q(
        "SELECT ?c ?p WHERE { ?c skos:broader ?p . "
        "FILTER NOT EXISTS { ?p a skos:Concept } }")
    assert not dangling, "dangling broader targets"
    self_ref = q(
        "SELECT ?c WHERE { ?c skos:broader ?c }")
    assert not self_ref, "self broader"
    tops = q("SELECT ?c WHERE { ?c skos:topConceptOf ?s }")
    assert len(tops) == 2, f"top concepts: {len(tops)}"
    # workbook overlay integrity
    appr_slugs = [s for s, w in wb_rows.items() if w["status"] == "approved"]
    missing_def = q(
        "SELECT ?c WHERE { ?c a skos:Concept . FILTER NOT EXISTS "
        "{ ?c skos:definition ?d } }")
    missing_slugs = {str(c).rsplit("/", 1)[-1] for c in
                     [r[0] for r in missing_def]}
    undef_approved = [s for s in appr_slugs if s in missing_slugs]
    assert not undef_approved, \
        f"approved workbook rows without definition: {undef_approved[:5]}"
    blocked_with_def = q(
        "SELECT ?c WHERE { ?c <" + str(INTAKE["status"]) + "> \"blocked\"@en . "
        "?c skos:definition ?d }")
    assert not blocked_with_def, "blocked rows must not carry a definition"
    retired = q("SELECT ?c WHERE { ?c <" + str(OWL.deprecated) + "> true }")
    assert len(retired) == n_deprecated, "deprecated count mismatch"
    # every natural-language literal tagged @en
    # (skos:notation is a code, not prose — correctly untagged)
    lang_props = {SKOS.prefLabel, SKOS.altLabel, SKOS.definition,
                  SKOS.scopeNote, DCTERMS.title, DCTERMS.description,
                  INTAKE.keyInputs, INTAKE.primaryOutput,
                  INTAKE.relatedConcepts, INTAKE.responsibleDomain,
                  INTAKE.processHorizon, INTAKE.primaryPurpose,
                  INTAKE.referenceSources, INTAKE.terminologyNotes,
                  INTAKE.conceptTypeCheck, INTAKE.parkedChildren,
                  INTAKE.status, INTAKE.level, INTAKE.apqcDecision}
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

    out_path = Path(args.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "step3-taxonomy.ttl").write_text(ttl, encoding="utf-8")

    n_triples = len(g)
    wb_bits = ""
    if wb_rows:
        wb_bits = (f"\n- Workbook overlay: {workbook_count} approved rows "
                   f"(definitions, scope notes, {workbook_altlabels} "
                   f"altLabels, {workbook_apqc_refs} APQC references, "
                   f"intake annotations); {n_blocked} blocked rows "
                   f"(definition-less, parked); {n_deprecated} retired "
                   f"row(s) marked owl:deprecated")
    report = f"""# Step 3 — SKOS taxonomy report

- Concepts: {n_rows} (one per process-map node, stable document order)
- Triples: {n_triples}
- `skos:broader` links: {n_broader} (every concept except the two L0 roots)
- Top concepts: `L0-downstream-operations`, `L0-enabling-functions`
- `skos:notation` present: 669 (every ID'd node; original codes preserved)
- `skos:definition` present: {with_definition} of {n_rows}{f" ({adopted} triangulated APQC/EIA, {authored_count} human-authored L1-L3, {workbook_count} workbook-approved)" if (adopted or authored_count or workbook_count) else ""}{wb_bits}
- Untagged literals: 0 (language policy holds)

## ConceptScheme
The core module namespace URI
`https://w3id.org/lsc/ontology/modules/core`
doubles as the `skos:ConceptScheme`. Rationale: the module's entire
current content *is* the taxonomy; one URI, one thing.

## Workbook overlay (Step 3c)
Approved workbook rows overlay the taxonomy with definition precedence
workbook > human-authored L1–L3 > step3b adoption > repo description.
Each approved row contributes: `skos:definition`, `skos:scopeNote`
(scope note with in/out-of-scope boundaries folded in),
`skos:altLabel`s, a `dcterms:references` link to the APQC PCF element,
`dcterms:source` provenance, and verbatim Phase-1 capture under the
provisional `intake:` namespace
(`https://w3id.org/lsc/ontology/intake/` — level, keyInputs,
primaryOutput, relatedConcepts, responsibleDomain, processHorizon,
primaryPurpose, referenceSources, terminologyNotes, conceptTypeCheck,
parkedChildren, apqcDecision, status).
These annotations are explicitly NOT the Step 4 model: they preserve the
reviewer's text in the graph so nothing is lost, and Step 4 promotes them
to real properties between concept URIs. `intake:level` carries the locked
L0–L6 taxonomy level; `intake:apqcDecision` records the mapping call
(REVIEW LINK / ADOPTED / REJECTED / NO CANDIDATE / NO SOURCE) — REJECTED
rows are the deliberate APQC divergences (competency Q12).
Blocked rows appear with `intake:status "blocked"` and no definition
(the locked rule: a parked row must not carry one). Retired rows are
`owl:deprecated` (not deleted, per version policy); `dcterms:isReplacedBy`
is left for the Step 3d tree pass, when destinations are decided.

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
Parsed clean; {n_concepts} concepts; exactly one `@en` prefLabel per concept;
every concept in scheme; {n_broader} broader links, no dangling targets, no
self-references; 2 top concepts; zero untagged literals; Turtle
round-trip lossless.
"""
    (out_path / "step3-taxonomy-report.md").write_text(report, encoding="utf-8")
    print(f"OK: {n_rows} concepts, {n_triples} triples, "
          f"{with_definition}/{n_rows} definitions ({adopted} triangulated, "
          f"{authored_count} human-authored, {workbook_count} workbook).")


if __name__ == "__main__":
    main()
