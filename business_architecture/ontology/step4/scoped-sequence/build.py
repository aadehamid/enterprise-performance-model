#!/usr/bin/env python3
"""Scoped sequences (EPM-DEC-001-0026, #226): check the source table, build the
nodes, and validate them against the SHACL shapes.

scoped-sequences.csv is the governed source: one row per node, authored from the
#205 review CSVs and the #226 design decisions. This script never edits it.

    python3 build.py           # checks only (standard library)
    python3 build.py --verify  # checks, SHACL, and scoped-sequences.ttl is current (needs rdflib, pyshacl)
    python3 build.py --write   # checks, then rewrite scoped-sequences.ttl (needs rdflib)

check() and counts() use the standard library only, so the evidence gate and
epm_facts.py can call them without extra dependencies.
"""
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEP4 = os.path.dirname(HERE)
TABLE = os.path.join(HERE, "scoped-sequences.csv")
VOCABULARY = os.path.join(HERE, "vocabulary.ttl")
SHAPES = os.path.join(HERE, "shapes.ttl")
OUTPUT = os.path.join(HERE, "scoped-sequences.ttl")
TAXONOMY = os.path.join(STEP4, "baseline", "step3-taxonomy.ttl")
REVIEWS = [os.path.join(STEP4, "review-evidence", f"precedes-follows-batch{n}-review.csv") for n in (1, 2)]
ANSWERS = os.path.join(STEP4, "review-evidence", "hamid-answers")
# The #226 design summary Hamid approved (EPM-DEC-001-0026): per-row scope, conditions, refinement, ancestors.
DESIGN = os.path.join(STEP4, "review-evidence", "226-design-summary.md")
# The saved answer each review batch came from.
BATCH_ANSWER = {REVIEWS[0]: "205-batch1.md", REVIEWS[1]: "205-batch2.md"}

CORE = "https://w3id.org/lsc/ontology/modules/core/"
PROC = "https://w3id.org/lsc/ontology/process/"
SEQ = "https://w3id.org/lsc/ontology/sequence/"
COLUMNS = ["node_slug", "row_id", "source_verb", "earlier", "later", "scope_unit", "condition",
           "refines", "links_to_ancestor", "evidence_basis", "definition", "answer"]


def load(path=TABLE):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def taxonomy_parents(path=TAXONOMY):
    """slug -> parent slug (or None), read from the taxonomy's skos:broader lines."""
    parents, subject = {}, None
    with open(path) as f:
        for line in f:
            m = re.match(r"proc:(\S+) a skos:Concept", line)
            if m:
                subject = m.group(1)
                parents.setdefault(subject, None)
                continue
            m = re.match(r"\s+skos:broader proc:(\S+) [;.]", line)
            if m and subject:
                parents[subject] = m.group(1)
    return parents


def ancestors(slug, parents):
    seen = []
    while parents.get(slug):
        slug = parents[slug]
        seen.append(slug)
    return seen


def code_list(scheme, path=VOCABULARY):
    """Local names of the skos:Concepts in one scheme of vocabulary.ttl."""
    with open(path) as f:
        text = f.read()
    names = set()
    for block in text.split("\n\n"):
        m = re.match(r"\s*(?:#.*\n)*\s*\w+:([\w-]+) a skos:Concept", block)
        if m and f"skos:inScheme core:{scheme}" in block:
            names.add(m.group(1))
    return names


def saved_answer_urls(folder=ANSWERS):
    urls = set()
    for path in glob.glob(os.path.join(folder, "*.md")):
        with open(path) as f:
            urls.update(re.findall(r"verbatim from (\S+)", f.readline()))
    return urls


def scope_labels(path=VOCABULARY):
    """Scope-unit prefLabel (lower case) -> local name, from vocabulary.ttl."""
    with open(path) as f:
        text = f.read()
    return {label.lower(): name for name, label in
            re.findall(r'scope:([\w-]+) a skos:Concept ;[^.]*?skos:prefLabel "([^"]+)"@en', text, re.S)}


def approved_ancestor_nodes(path=SHAPES):
    """Node slugs listed in shape:ApprovedAncestorLink's sh:in."""
    with open(path) as f:
        m = re.search(r"shape:ApprovedAncestorLink a sh:NodeShape ;.*?sh:in \(([^)]*)\)", f.read(), re.S)
    return set(re.findall(r"seq:(\S+)", m.group(1))) if m else set()


def approvals():
    """What Hamid approved for each row, from the #226 summary and the #205 review batches.

    scope: row -> scope unit; conditional, refinement, ancestor: row sets named by Q10, Q12, Q6;
    answer: row -> saved answer URL; basis: row -> evidence basis (Q13).
    """
    with open(DESIGN) as f:
        text = f.read()
    labels = scope_labels()
    scope = {}
    q9 = text.split("**Q9.**", 1)[1].split("**Q10.**", 1)[0]
    for label, ids in re.findall(r"^\s*\| ([^|(]+?)\s*(?:\([^|]*\))? \| (REL-[^|]+) \|", q9, re.M):
        for rid in re.findall(r"REL-\d{5}", ids):
            scope[rid] = labels.get(label.lower(), f"unknown label {label!r}")

    def rows_in(question):
        line = re.search(rf"^- \*\*{question}\.\*\*.*$", text, re.M).group(0)
        return set(re.findall(r"REL-\d{5}", line))

    answer, basis = {}, {}
    for path in REVIEWS:
        with open(os.path.join(ANSWERS, BATCH_ANSWER[path])) as f:
            url = re.search(r"verbatim from (\S+)", f.readline()).group(1)
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                answer[r["row_id"]] = url
                # Q13: all of batch 2, and the batch 1 answers adopted as reference-model assumptions.
                assumption = path == REVIEWS[1] or "reference-model assumption" in r["hamid_words"]
                basis[r["row_id"]] = "reference-model-assumption" if assumption else "source-confirmed"
    return {"scope": scope, "conditional": rows_in("Q10"), "refinement": rows_in("Q12"),
            "ancestor": rows_in("Q6"), "answer": answer, "basis": basis}


def check(columns=None, rows=None):
    """Every rule SHACL cannot see: agreement with the review CSVs, the taxonomy and the decisions."""
    if rows is None:
        columns, rows = load()
    problems = []
    if columns != COLUMNS:
        return [f"columns are {columns}, expected {COLUMNS}"]
    if not rows:
        return ["scoped-sequences.csv has no rows"]
    parents = taxonomy_parents()
    scopes, bases = code_list("ScopeUnits"), code_list("EvidenceBases")
    answers = saved_answer_urls()
    reviewed = {}
    for path in REVIEWS:
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                reviewed[r["row_id"]] = r
    by_slug = {}
    for r in rows:
        rid, slug = r["row_id"], r["node_slug"]
        where = f"{rid} ({slug})"
        if slug in by_slug:
            problems.append(f"{where}: node_slug repeated")
        by_slug[slug] = r
        if slug != f"{r['earlier']}--{r['later']}--{r['scope_unit']}":
            problems.append(f"{where}: node_slug must be earlier--later--scope_unit")
        for col in ("earlier", "later"):
            if r[col] not in parents:
                problems.append(f"{where}: {col} {r[col]} is not a concept in the pinned taxonomy")
        if r["scope_unit"] not in scopes:
            problems.append(f"{where}: scope_unit {r['scope_unit']} is not in the scope-unit list")
        if r["evidence_basis"] not in bases:
            problems.append(f"{where}: evidence_basis {r['evidence_basis']} is not in the evidence-basis list")
        if r["answer"] not in answers:
            problems.append(f"{where}: answer {r['answer']} is not a saved answer in review-evidence/hamid-answers")
        if r["condition"] and r["condition"] not in r["definition"]:
            problems.append(f"{where}: condition is not words of the definition")
        # Q4 and Q11: direction and definition come from the reviewed row.
        src = reviewed.get(rid)
        if src is None:
            problems.append(f"{where}: row is not in a precedes/follows review CSV")
            continue
        if src["verb"] != r["source_verb"]:
            problems.append(f"{where}: source_verb {r['source_verb']} but the review says {src['verb']}")
        expected = (src["source_slug"], src["target_slug"]) if src["verb"] == "precedes" else (src["target_slug"], src["source_slug"])
        if (r["earlier"], r["later"]) != expected:
            problems.append(f"{where}: earlier/later must be {expected} for a '{src['verb']}' row")
        if r["definition"] != src["scope_note_sentence"]:
            problems.append(f"{where}: definition differs from the review CSV's scope_note_sentence")
        # Q6: a link to an ancestor is declared, and only declared when it is one.
        is_ancestor = r["later"] in ancestors(r["earlier"], parents) or r["earlier"] in ancestors(r["later"], parents)
        if r["links_to_ancestor"] not in ("yes", "no"):
            problems.append(f"{where}: links_to_ancestor must be yes or no")
        elif (r["links_to_ancestor"] == "yes") != is_ancestor:
            problems.append(f"{where}: links_to_ancestor is {r['links_to_ancestor']} but the taxonomy says {'yes' if is_ancestor else 'no'}")
    # Each row carries exactly what was approved for it (EPM-DEC-001-0026).
    approved = approvals()
    if {r["row_id"] for r in rows} != set(approved["scope"]):
        problems.append("rows differ from the rows in the approved Q9 table")
    for r in rows:
        rid = r["row_id"]
        where = f"{rid} ({r['node_slug']})"
        if rid in approved["scope"] and r["scope_unit"] != approved["scope"][rid]:
            problems.append(f"{where}: scope_unit {r['scope_unit']} but Q9 approved {approved['scope'][rid]}")
        if bool(r["condition"]) != (rid in approved["conditional"]):
            problems.append(f"{where}: Q10 {'lists' if rid in approved['conditional'] else 'does not list'} this row as conditional")
        if rid in approved["answer"] and r["answer"] != approved["answer"][rid]:
            problems.append(f"{where}: answer must be the batch's saved answer {approved['answer'][rid]}")
        if rid in approved["basis"] and r["evidence_basis"] != approved["basis"][rid]:
            problems.append(f"{where}: evidence_basis {r['evidence_basis']} but Q13 gives {approved['basis'][rid]}")
        if r["links_to_ancestor"] == "yes" and rid not in approved["ancestor"]:
            problems.append(f"{where}: links_to_ancestor yes, but Q6 approves an ancestor link only for {sorted(approved['ancestor'])}")
    in_refinement = {r["row_id"] for r in rows if r["refines"]}
    in_refinement |= {r["row_id"] for r in rows if any(o["refines"] == r["node_slug"] for o in rows)}
    if in_refinement != approved["refinement"]:
        problems.append(f"refinement rows {sorted(in_refinement)} differ from Q12 {sorted(approved['refinement'])}")
    flagged = {r["node_slug"] for r in rows if r["links_to_ancestor"] == "yes"}
    if approved_ancestor_nodes() != flagged:
        problems.append(f"shapes.ttl ApprovedAncestorLink lists {sorted(approved_ancestor_nodes())}, the table flags {sorted(flagged)}")
    # Q12: a refining node details a node one or more levels up, for the same later process and scope.
    for r in rows:
        if not r["refines"]:
            continue
        where = f"{r['row_id']} ({r['node_slug']})"
        target = by_slug.get(r["refines"])
        if target is None:
            problems.append(f"{where}: refines {r['refines']}, which is not a node")
        elif target is r:
            problems.append(f"{where}: refines itself")
        elif (target["later"], target["scope_unit"]) != (r["later"], r["scope_unit"]):
            problems.append(f"{where}: refines a node with a different later process or scope")
        elif target["earlier"] not in ancestors(r["earlier"], parents):
            problems.append(f"{where}: refines a node whose earlier process is not an ancestor of its own")
        elif target["refines"]:
            problems.append(f"{where}: refines a node that itself refines another")
    return problems


def counts(rows=None):
    if rows is None:
        _, rows = load()
    return {"nodes": len(rows), "handoffs": sum(1 for r in rows if not r["refines"]),
            "rows": sorted(r["row_id"] for r in rows)}


def graph(rows=None):
    import rdflib
    from rdflib.namespace import DCTERMS, RDF, SKOS, XSD
    if rows is None:
        _, rows = load()
    core = rdflib.Namespace(CORE)
    proc, seq = rdflib.Namespace(PROC), rdflib.Namespace(SEQ)
    scope = rdflib.Namespace(CORE + "scope-unit/")
    evb = rdflib.Namespace(CORE + "evidence-basis/")
    tax = rdflib.Graph().parse(TAXONOMY, format="turtle")
    scope_labels = {s: str(o) for s, o in rdflib.Graph().parse(VOCABULARY, format="turtle").subject_objects(SKOS.prefLabel)}

    def label(slug):
        return str(tax.value(proc[slug], SKOS.prefLabel))

    g = rdflib.Graph()
    for prefix, ns in (("core", core), ("proc", proc), ("seq", seq), ("scope", scope), ("evb", evb),
                       ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    for r in rows:
        node = seq[r["node_slug"]]
        g.add((node, RDF.type, core.ScopedSequence))
        g.add((node, core.earlierProcess, proc[r["earlier"]]))
        g.add((node, core.laterProcess, proc[r["later"]]))
        g.add((node, core.sequenceScope, scope[r["scope_unit"]]))
        if r["condition"]:
            g.add((node, core.sequenceCondition, rdflib.Literal(r["condition"], lang="en")))
        if r["refines"]:
            g.add((node, core.refinesSequence, seq[r["refines"]]))
        if r["links_to_ancestor"] == "yes":
            g.add((node, core.linksToAncestor, rdflib.Literal(True)))
        g.add((node, core.evidenceBasis, evb[r["evidence_basis"]]))
        g.add((node, SKOS.definition, rdflib.Literal(r["definition"], lang="en")))
        scope_label = scope_labels[scope[r["scope_unit"]]].lower()
        g.add((node, SKOS.prefLabel, rdflib.Literal(
            f"{label(r['earlier'])} before {label(r['later'])}, per {scope_label}", lang="en")))
        g.add((node, core.sourceRow, rdflib.Literal(r["row_id"], datatype=XSD.string)))
        g.add((node, DCTERMS.source, rdflib.URIRef(r["answer"])))
    return g, tax


def turtle(g):
    header = ("# Generated by build.py --write from scoped-sequences.csv. Do not edit by hand.\n"
              "# Scoped sequences: EPM-DEC-001-0026 (#226).\n")
    return header + g.serialize(format="turtle")


def shacl(g, tax):
    import pyshacl
    import rdflib
    data = rdflib.Graph()
    for part in (g, tax, rdflib.Graph().parse(VOCABULARY, format="turtle")):
        data += part
    shapes = rdflib.Graph().parse(SHAPES, format="turtle")
    conforms, results, text = pyshacl.validate(data, shacl_graph=shapes, advanced=True, allow_warnings=False)
    return conforms, results, text


def main(argv):
    if "--write" in argv and "--verify" in argv:
        print("use --write or --verify, not both")
        return 2
    problems = check()
    for p in problems:
        print("FAIL", p)
    if problems:
        return 1
    c = counts()
    print(f"scoped sequences: {c['nodes']} nodes, {c['handoffs']} handoffs; source table checks pass")
    if "--write" in argv or "--verify" in argv:
        g, tax = graph()
        text = turtle(g)
        if "--write" in argv:
            with open(OUTPUT, "w") as f:
                f.write(text)
            print(f"wrote {os.path.relpath(OUTPUT, STEP4)}")
        else:
            with open(OUTPUT) as f:
                if f.read() != text:
                    print("FAIL scoped-sequences.ttl is not current; run build.py --write")
                    return 1
            conforms, _, report = shacl(g, tax)
            if not conforms:
                print(report)
                return 1
            print("SHACL: conforms (no violations, no warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
