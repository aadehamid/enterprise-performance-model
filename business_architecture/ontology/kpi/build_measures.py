"""Build the kpi module's measures (Step 7; EPM-DEC-001-0042, EPM-DEC-001-0043).

    python3 build_measures.py            # check the tables and print the figures
    python3 build_measures.py --write    # also write measures.ttl
    python3 build_measures.py --verify   # fail unless measures.ttl equals a fresh build

measure-classification.csv holds each measure's kind and why; measure-details.csv its
definition, grain, basis, aliases and the processes it informs; personas.csv the planning
roles; measure-identifiers.csv each measure's KPI or OPM identifier (kpi 1.3.0, EPM-DEC-001-0109).
The build fails unless both measure tables list the same measures once each, every
kind is on the measure-kind list, every persona and process named exists, every
"not to be confused with" names another measure, and every identifier follows its kind, is used once,
keeps the KPI-0001 exception and sits in its prefix's run in the classification table's order with no gap.
"""
import argparse
import csv
import os
import re
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLASSIFICATION = os.path.join(HERE, "measure-classification.csv")
DETAILS = os.path.join(HERE, "measure-details.csv")
PERSONAS = os.path.join(HERE, "personas.csv")
IDENTIFIER_TABLE = os.path.join(HERE, "measure-identifiers.csv")
CORE = os.path.join(HERE, "..", "releases", "core", "2.4.0", "core.ttl")
OUTPUT = os.path.join(HERE, "measures.ttl")

KPI = Namespace("https://w3id.org/lsc/ontology/modules/kpi/")
KIND = Namespace("https://w3id.org/lsc/ontology/modules/kpi/measure-kind/")
MEASURE = Namespace("https://w3id.org/lsc/ontology/modules/kpi/measure/")
PERSONA = Namespace("https://w3id.org/lsc/ontology/modules/kpi/persona/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
ORG = Namespace("http://www.w3.org/ns/org#")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
KINDS = ("kpi", "operational-metric", "plan-variance-diagnostic", "market-indicator",
         "decision-support-indicator", "tracker-or-report", "alert", "not-a-measure")
SOURCES = {  # where a measure comes from -> the source it cites
    "planner list": SRC["planner-measure-list-2026-10-18"],
    "MPC": SRC["mpc-performance-measures-evidence"],
    "industry": SRC["kpi-classification-evidence"],
}
SOURCE_TITLES = {
    SOURCES["planner list"]: "Value Chain Optimization Decision Support and Visualization (VCO DSV): the planning team's measure list, as the decision owner sent it on 2026-10-18; held outside the repository (EPM-DEC-001-0040)",
    SOURCES["MPC"]: "MPC performance measures, business_architecture/reference/mpc/mpc-performance-measures-evidence.md",
    SOURCES["industry"]: "KPI or operational metric, business_architecture/reference/downstream-peers/kpi-classification-evidence.md",
}
# Every measure also cites the classification evidence, which holds the rule it was sorted by.
CLASSIFIED_BY = SOURCES["industry"]
# The note on an identifier the decision owner's assets give a measure (EPM-DEC-001-0097, item 3). Every other
# measure's identifier follows the rule in EPM-DEC-001-0109 and carries no note.
IDENTIFIER_NOTES = {
    "crack-spreads": "KPI-0001 is the crack-spread Genie agent's identifier for this measure. The gold table "
                     "behind its metric view holds the constant KPI_ID value 'KPI Crack Spread 3-2-1' on every "
                     "one of its 127 series and all 1,090,423 rows of the gold table alike, so the identifier names the measure, "
                     "not a series "
                     "(EPM-DEC-001-0097, item 3). It keeps KPI-0001 although the module classes it as a market indicator, "
                     "because the pricing assets already use it (kpi 1.3.0, EPM-DEC-001-0109).",
}
# Which identifier prefix each kind takes (EPM-DEC-001-0109); a kind not listed takes none.
PREFIX = {"kpi": "KPI", "operational-metric": "OPM", "market-indicator": "OPM", "plan-variance-diagnostic": "OPM",
          "decision-support-indicator": "OPM", "alert": "OPM"}
# The one measure whose identifier does not follow its kind: the pricing assets' KPI-0001 (EPM-DEC-001-0097).
PREFIX_EXCEPTIONS = {"crack-spreads": "KPI-0001"}
# What changed in a measure since an earlier release, kept on the measure (kpi 1.2.0).
CHANGES = {
    "additional-market-prices": "kpi 1.2.0 (2026-10-25): narrowed to renewables and NGLs; the planner list's name was "
                                "'Additional Market Prices (Benchmark, Crude, Renewables, NGLs)'. Benchmark and crude "
                                "prices are Crude Market Pricing's (EPM-DEC-001-0097, item 4).",
}


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def process_index():
    """Process notation (or slug) -> IRI, from the core release."""
    g = Graph().parse(CORE)
    index = {str(n): s for s, n in g.subject_objects(SKOS.notation) if str(s).startswith(str(PROC))}
    index.update({str(s)[len(str(PROC)):]: s for s in g.subjects(RDF.type, SKOS.Concept) if str(s).startswith(str(PROC))})
    return index


def load():
    rows, details, personas = read_csv(CLASSIFICATION), read_csv(DETAILS), read_csv(PERSONAS)
    problems = []
    ids = Counter(r["measure_id"] for r in rows)
    problems += [f"classification lists {m!r} {n} times" for m, n in ids.items() if n > 1]
    detail_ids = Counter(d["measure_id"] for d in details)
    problems += [f"details list {m!r} {n} times" for m, n in detail_ids.items() if n > 1]
    problems += [f"{m!r} has no details row" for m in ids if m not in detail_ids]
    problems += [f"details row {m!r} has no classification" for m in detail_ids if m not in ids]
    labels = {p["label"]: p["slug"] for p in personas}
    by_detail = {d["measure_id"]: d for d in details}
    procs = process_index()
    identifiers = {i["measure_id"]: i["identifier"] for i in read_csv(IDENTIFIER_TABLE)}
    problems += [f"identifier {v!r} is used {n} times" for v, n in Counter(identifiers.values()).items() if n > 1]
    problems += [f"identifier row {m!r} has no classification" for m in identifiers if m not in ids]
    for r in rows:
        m, ident, prefix = r["measure_id"], identifiers.get(r["measure_id"], ""), PREFIX.get(r["class"])
        if m in PREFIX_EXCEPTIONS:
            if ident != PREFIX_EXCEPTIONS[m]:
                problems.append(f"{m}: its identifier must stay {PREFIX_EXCEPTIONS[m]}")
        elif prefix is None and ident:
            problems.append(f"{m}: a {r['class']} has no identifier")
        elif prefix and not re.fullmatch(prefix + r"-\d{4}", ident):
            problems.append(f"{m}: a {r['class']} needs a {prefix}-nnnn identifier, not {ident!r}")
        r["identifier"] = ident
    # Each prefix numbers its measures from 1 in the classification table's order, with no gap (EPM-DEC-001-0109);
    # KPI-0001 is the pricing assets' identifier, so the KPI run continues from it.
    for prefix, start in (("KPI", 1), ("OPM", 1)):
        run = [r for r in rows if r.get("identifier", "").startswith(prefix + "-")]
        if prefix == "KPI":
            run = [r for r in run if r["measure_id"] not in PREFIX_EXCEPTIONS]
            start = 1 + sum(1 for v in PREFIX_EXCEPTIONS.values() if v.startswith("KPI-"))
        for i, r in enumerate(run, start):
            if r["identifier"] != f"{prefix}-{i:04d}":
                problems.append(f"{r['measure_id']}: {r['identifier']} breaks the {prefix} run, which needs {prefix}-{i:04d} "
                                "here (in the classification table's order, no gap)")
    for r in rows:
        m = r["measure_id"]
        if r["class"] not in KINDS:
            problems.append(f"{m}: kind {r['class']!r} is not on the measure-kind list")
        if r["kpi_candidate"] not in ("yes", "no"):
            problems.append(f"{m}: kpi_candidate must be yes or no")
        if r["kpi_candidate"] == "yes" and r["class"] != "operational-metric":
            problems.append(f"{m}: only an operational metric can be a KPI candidate")
        if r["name"] in split(by_detail.get(m, {}).get("aliases", "")):
            problems.append(f"{m}: an alias repeats the measure's name, which SKOS forbids (S13; EPM-DEC-001-0098)")
        if r["source"] not in SOURCES:
            problems.append(f"{m}: unknown source {r['source']!r}")
        if not r["rule_test"].isdigit() or not 1 <= int(r["rule_test"]) <= 5:
            problems.append(f"{m}: rule_test must be 1 to 5")
        problems += [f"{m}: unknown persona {p!r}" for p in split(r["personas"]) if p not in labels]
    for d in details:
        m = d["measure_id"]
        if not d["definition"]:
            problems.append(f"{m}: no definition")
        problems += [f"{m}: process {p!r} is not in core 2.4.0" for p in split(d["informs_process"]) if p not in procs]
        problems += [f"{m}: confused-with {o!r} is not a measure" for o in split(d["not_to_be_confused_with"])
                     if o not in ids or o == m]
        if bool(d["not_to_be_confused_with"]) != bool(d["not_note"]) and d["not_to_be_confused_with"]:
            problems.append(f"{m}: a confused-with link needs a note saying how they differ")
    if problems:
        sys.exit("kpi tables do not reconcile:\n  " + "\n  ".join(problems))
    return rows, {d["measure_id"]: d for d in details}, personas, labels, procs


def split(text):
    return [t.strip() for t in text.split(";") if t.strip()]


def build(rows, details, personas, labels, procs):
    g = Graph()
    for prefix, ns in (("kpi", KPI), ("kind", KIND), ("measure", MEASURE), ("persona", PERSONA),
                       ("proc", PROC), ("org", ORG), ("src", SRC), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    for iri, title in SOURCE_TITLES.items():
        g.add((iri, RDF.type, DCTERMS.BibliographicResource))
        g.add((iri, DCTERMS.title, Literal(title, lang="en")))
    # The planner list's short name, as the decision owner gave it (answers-2026-10-19-vco-dsv.md).
    g.add((SOURCES["planner list"], DCTERMS.alternative, Literal("VCO DSV", lang="en")))
    for p in personas:
        iri = PERSONA[p["slug"]]
        g.add((iri, RDF.type, ORG.Role))
        g.add((iri, SKOS.prefLabel, Literal(p["label"], lang="en")))
        g.add((iri, SKOS.definition, Literal(p["definition"], lang="en")))
        g.add((iri, KPI.planType, Literal(p["plan_type"], datatype=XSD.string)))
        g.add((iri, KPI.planHorizon, Literal(p["horizon"], datatype=XSD.string)))
        g.add((iri, DCTERMS.source, SOURCES["planner list"]))
    for r in rows:
        m, d = r["measure_id"], details[r["measure_id"]]
        iri = MEASURE[m]
        g.add((iri, RDF.type, KPI.MeasureDefinition))
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, KPI.Measures))
        g.add((iri, SKOS.topConceptOf, KPI.Measures))  # a flat scheme, stated both ways (EPM-DEC-001-0098, item 5)
        g.add((KPI.Measures, SKOS.hasTopConcept, iri))
        g.add((iri, SKOS.prefLabel, Literal(r["name"], lang="en")))
        g.add((iri, SKOS.notation, Literal(m, datatype=XSD.string)))
        g.add((iri, SKOS.definition, Literal(d["definition"], lang="en")))
        g.add((iri, KPI.measureKind, KIND[r["class"]]))
        g.add((iri, KPI.kpiCandidate, Literal(r["kpi_candidate"] == "yes")))
        g.add((iri, KPI.classificationTest, Literal(int(r["rule_test"]))))
        g.add((iri, KPI.classificationReason, Literal(r["reason"], datatype=XSD.string)))
        for alias in split(d["aliases"]):
            g.add((iri, SKOS.altLabel, Literal(alias, lang="en")))
        for p in split(r["personas"]):
            g.add((iri, KPI.usedBy, PERSONA[labels[p]]))
        for p in split(d["informs_process"]):
            g.add((iri, KPI.informsProcess, procs[p]))
        for o in split(d["not_to_be_confused_with"]):
            g.add((iri, KPI.notToBeConfusedWith, MEASURE[o]))
        if d["not_note"]:
            g.add((iri, SKOS.scopeNote, Literal(d["not_note"], lang="en")))
        for prop, value in ((KPI.comparedAgainst, r["compared_against"]), (KPI.grain, d["grain"]),
                            (KPI.basis, d["basis"]), (KPI.publicCounterpart, r["mpc_counterpart"])):
            if value:
                g.add((iri, prop, Literal(value, datatype=XSD.string)))
        if r["identifier"]:
            g.add((iri, DCTERMS.identifier, Literal(r["identifier"], datatype=XSD.string)))
        if m in IDENTIFIER_NOTES:
            g.add((iri, SKOS.note, Literal(IDENTIFIER_NOTES[m], lang="en")))
        if m in CHANGES:
            g.add((iri, SKOS.changeNote, Literal(CHANGES[m], lang="en")))
        g.add((iri, DCTERMS.source, SOURCES[r["source"]]))
        g.add((iri, DCTERMS.source, CLASSIFIED_BY))
        if r["evidence"]:
            g.add((iri, DCTERMS.bibliographicCitation, Literal(r["evidence"], datatype=XSD.string)))
    return g


def figures(rows, details, personas):
    kinds = Counter(r["class"] for r in rows)
    sources = Counter(r["source"] for r in rows)
    return {
        "measures": len(rows),
        **{f"from {k}": v for k, v in sorted(sources.items())},
        **{k: kinds[k] for k in KINDS},
        "KPI candidates": sum(r["kpi_candidate"] == "yes" for r in rows),
        "KPI identifiers": sum(r["identifier"].startswith("KPI-") for r in rows),
        "OPM identifiers": sum(r["identifier"].startswith("OPM-") for r in rows),
        "personas": len(personas),
        "process links": sum(len(split(d["informs_process"])) for d in details.values()),
        "measures without a process link": sum(1 for d in details.values() if not d["informs_process"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    rows, details, personas, labels, procs = load()
    text = ("# Measures of the kpi module (Step 7; EPM-DEC-001-0042, EPM-DEC-001-0043).\n"
            "# Built by build_measures.py from measure-classification.csv, measure-details.csv and\n"
            "# personas.csv. Do not edit by hand.\n"
            + build(rows, details, personas, labels, procs).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(rows, details, personas).items()))
    if args.verify:
        current = os.path.exists(OUTPUT) and open(OUTPUT).read() == text
        if not current:
            sys.exit("measures.ttl is not current: run build_measures.py --write")
        print("measures.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
