"""Build the data-product module (Step 7, item 3 of EPM-DEC-001-0017; EPM-DEC-001-0053).

    python3 build_data_products.py            # check the sources and print the figures
    python3 build_data_products.py --write    # also write data-products.ttl
    python3 build_data_products.py --verify   # fail unless data-products.ttl equals a fresh build

The portfolio (business_process/data_product_portfolio.json) gives the segments, lines and
data products; links.csv gives the process links a recorded decision names. The build fails
unless every id is unique, every status is on the code list, every segment's process-domain
reference resolves to one core concept, every link names a data product, and every link's
process is in core 2.1.0 unless the row says which release it waits for.
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PORTFOLIO = os.path.join(REPO, "business_architecture", "business_process", "data_product_portfolio.json")
LINKS = os.path.join(HERE, "links.csv")
CORE = os.path.join(HERE, "..", "releases", "core", "2.1.0", "core.ttl")
OUTPUT = os.path.join(HERE, "data-products.ttl")

DP = Namespace("https://w3id.org/lsc/ontology/modules/data-product/")
STATUS = Namespace("https://w3id.org/lsc/ontology/modules/data-product/status/")
SEGMENT = Namespace("https://w3id.org/lsc/ontology/modules/data-product/segment/")
LINE = Namespace("https://w3id.org/lsc/ontology/modules/data-product/line/")
PRODUCT = Namespace("https://w3id.org/lsc/ontology/modules/data-product/product/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
STATUSES = {"active": "active", "defined_only": "defined-only", "open_decision": "open-decision"}
RELATIONS = {"produced-by": DP.producedBy, "consumed-by": DP.consumedBy}
PORTFOLIO_SOURCE = SRC["data-product-portfolio"]
PARKED = ("The portfolio names this {kind} but does not describe it (status defined_only). "
          "Its definition waits for its data owners (EPM-DEC-001-0053).")
# The portfolio's processDomainRef names a process by path and, where it has one, by ID in
# parentheses. MS 1's IRI keeps the slug it had before it was given an ID (EPM-DEC-001-0047).
SLUG_PINS = {"MS 1": "L1-midstream"}


def local(prefix, ident):
    """dp-loss-control -> loss-control: the IRI drops the id's type prefix; skos:notation keeps it."""
    return ident[len(prefix):]


def core_index():
    """Notation, slug and label -> core process IRIs, from the core release."""
    g = Graph().parse(CORE)
    concepts = [s for s in g.subjects(RDF.type, SKOS.Concept) if str(s).startswith(str(PROC))]
    by_key = {}
    for s in concepts:
        by_key.setdefault(str(s)[len(str(PROC)):], set()).add(s)
        for n in g.objects(s, SKOS.notation):
            by_key.setdefault(str(n), set()).add(s)
    by_label = {}
    for s in concepts:
        for label in g.objects(s, SKOS.prefLabel):
            by_label.setdefault(str(label), set()).add(s)
    return by_key, by_label


def resolve_domain(ref, by_key, by_label):
    """The core concept a processDomainRef names: its ID in parentheses, else the path's last name."""
    m = re.search(r"\(([A-Z]{2} [0-9.]+)\)\s*$", ref)
    if m:
        ident = m.group(1)
        hits = by_key.get(SLUG_PINS.get(ident, ident), set())
    else:
        hits = by_label.get(re.sub(r"\s*\([^)]*\)\s*$", "", ref).split(">")[-1].strip(), set())
    return next(iter(hits)) if len(hits) == 1 else None


def load():
    with open(PORTFOLIO) as f:
        portfolio = json.load(f)
    with open(LINKS, newline="") as f:
        links = list(csv.DictReader(f))
    by_key, by_label = core_index()
    problems = []
    ids = Counter()
    for seg in portfolio["segments"]:
        ids[seg["id"]] += 1
        if resolve_domain(seg.get("processDomainRef") or "", by_key, by_label) is None:
            problems.append(f"{seg['id']}: processDomainRef {seg.get('processDomainRef')!r} names no single core concept")
        for line in seg["productLines"]:
            items = [line] + line.get("portfolios", [])
            for item in items:
                ids[item["id"]] += 1
                if item.get("status", "active") not in STATUSES:
                    problems.append(f"{item['id']}: status {item.get('status')!r} is not on the code list")
    problems += [f"id {i!r} appears {n} times" for i, n in ids.items() if n > 1]
    products = {p["id"] for s in portfolio["segments"] for l in s["productLines"] for p in l.get("portfolios", [])}
    for row in links:
        if row["data_product"] not in products:
            problems.append(f"links.csv: {row['data_product']!r} is not a data product")
        if row["relation"] not in RELATIONS:
            problems.append(f"links.csv: relation {row['relation']!r} is not produced-by or consumed-by")
        if not row["source"]:
            problems.append(f"links.csv: {row['data_product']} -> {row['process']} cites no source")
        if not row["waits_for"] and len(by_key.get(row["process"], set())) != 1:
            problems.append(f"links.csv: process {row['process']!r} is not in core 2.1.0, and the row names no release it waits for")
    for alias, target in portfolio.get("aliases", {}).items():
        if "," not in target and target not in ids:
            problems.append(f"alias {alias!r} names {target!r}, which is not in the portfolio")
    if problems:
        sys.exit("data product sources do not reconcile:\n  " + "\n  ".join(problems))
    return portfolio, links, by_key, by_label


def build(portfolio, links, by_key, by_label):
    g = Graph()
    for prefix, ns in (("dp", DP), ("status", STATUS), ("segment", SEGMENT), ("line", LINE), ("product", PRODUCT),
                       ("proc", PROC), ("src", SRC), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    g.add((PORTFOLIO_SOURCE, RDF.type, DCTERMS.BibliographicResource))
    g.add((PORTFOLIO_SOURCE, DCTERMS.title, Literal(
        "Data product portfolio, business_architecture/business_process/data_product_portfolio.json, generated "
        + portfolio["meta"]["generatedAt"] + ", from: " + "; ".join(portfolio["meta"]["sources"]), lang="en")))
    # An alias that names one id is an alternative label; one that names two ids labels neither.
    aliases = {}
    for alias, target in portfolio.get("aliases", {}).items():
        if "," not in target:
            aliases.setdefault(target, []).append(alias)
    iris = {}

    def describe(iri, cls, item, broader, kind):
        iris[item["id"]] = iri
        g.add((iri, RDF.type, cls))
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, DP.DataProducts))
        g.add((iri, SKOS.prefLabel, Literal(item["name"], lang="en")))
        g.add((iri, SKOS.notation, Literal(item["id"], datatype=XSD.string)))
        if broader is not None:
            g.add((iri, SKOS.broader, broader))
        if cls != DP.PortfolioSegment:
            g.add((iri, DP.portfolioStatus, STATUS[STATUSES[item.get("status", "active")]]))
        if item.get("description"):
            g.add((iri, SKOS.definition, Literal(item["description"], lang="en")))
        else:
            g.add((iri, SKOS.editorialNote, Literal(PARKED.format(kind=kind), lang="en")))
        for alias in aliases.get(item["id"], []):
            if alias != item["name"]:
                g.add((iri, SKOS.altLabel, Literal(alias, lang="en")))
        for note in item.get("notes", []):
            g.add((iri, SKOS.scopeNote, Literal(note, lang="en")))
        g.add((iri, DCTERMS.source, PORTFOLIO_SOURCE))

    for seg in portfolio["segments"]:
        s = SEGMENT[local("seg-", seg["id"])]
        describe(s, DP.PortfolioSegment, seg, None, "segment")
        g.add((s, SKOS.topConceptOf, DP.DataProducts))
        g.add((s, DP.anchoredIn, resolve_domain(seg["processDomainRef"], by_key, by_label)))
        for line in seg["productLines"]:
            l = LINE[local("dpl-", line["id"])]
            describe(l, DP.DataProductLine, line, s, "data product line")
            for p in line.get("portfolios", []):
                describe(PRODUCT[local("dp-", p["id"])], DP.DataProduct, p, l, "data product")
    for row in links:
        if not row["waits_for"]:
            g.add((iris[row["data_product"]], RELATIONS[row["relation"]], next(iter(by_key[row["process"]]))))
    return g


def figures(portfolio, links):
    lines = [l for s in portfolio["segments"] for l in s["productLines"]]
    products = [p for l in lines for p in l.get("portfolios", [])]
    status = Counter(p.get("status", "active") for p in products)
    return {
        "segments": len(portfolio["segments"]),
        "lines": len(lines),
        "data products": len(products),
        **{f"{k} products": status[k] for k in STATUSES},
        "parked without a description": sum(1 for p in products if not p.get("description")),
        "process links": sum(1 for r in links if not r["waits_for"]),
        "links waiting for a core release": sum(1 for r in links if r["waits_for"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    portfolio, links, by_key, by_label = load()
    text = ("# Data products of the data-product module (Step 7; EPM-DEC-001-0053).\n"
            "# Built by build_data_products.py from business_process/data_product_portfolio.json and\n"
            "# links.csv. Do not edit by hand.\n"
            + build(portfolio, links, by_key, by_label).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(portfolio, links).items()))
    if args.verify:
        current = os.path.exists(OUTPUT) and open(OUTPUT).read() == text
        if not current:
            sys.exit("data-products.ttl is not current: run build_data_products.py --write")
        print("data-products.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
