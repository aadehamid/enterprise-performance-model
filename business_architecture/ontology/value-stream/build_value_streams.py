"""Build the value-stream module (Step 7; EPM-DEC-001-0054).

    python3 build_value_streams.py            # check the sources and print the figures
    python3 build_value_streams.py --write    # also write value-streams.ttl
    python3 build_value_streams.py --verify   # fail unless value-streams.ttl equals a fresh build

The two value streams in business_process/ give the stages, capabilities, value-stream
processes, flows and measure links. The build fails unless every id is unique across both
files, every linked process and process group is in core 2.2.0, every data product or line
is in the data-product module, every measure is in the kpi module, and every flow and
capability reference names something in the same file. gapAnalysis entries are
documentation only and create nothing (the schema's rule).
"""
import argparse
import json
import os
import sys
from collections import Counter

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STREAMS = [os.path.join(REPO, "business_architecture", "business_process", f)
           for f in ("value_stream_commercial_lifecycle.json", "value_stream_order_to_cash.json")]
CORE = os.path.join(HERE, "..", "releases", "core", "2.2.0", "core.ttl")
DATA_PRODUCTS = os.path.join(HERE, "..", "data-product", "data-products.ttl")
MEASURES = os.path.join(HERE, "..", "kpi", "measures.ttl")
OUTPUT = os.path.join(HERE, "value-streams.ttl")

VS = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/")
REL = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/measure-relationship/")
STREAM = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/stream/")
STAGE = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/stage/")
CAPABILITY = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/capability/")
VSPROCESS = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/process/")
MLINK = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/measure-link/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
MEASURE = Namespace("https://w3id.org/lsc/ontology/modules/kpi/measure/")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")
FLOWS = {"feeds": VS.feeds, "informs": VS.informs, "loops_to": VS.loopsTo}
RELATIONSHIPS = ("informs", "benchmarks", "measures-performance")
PREFIXES = {"vs-": STREAM, "stg-": STAGE, "cap-": CAPABILITY, "p-": VSPROCESS}


def iri(ident):
    """vs-order-to-cash -> stream/order-to-cash: the IRI drops the id's type prefix; skos:notation keeps it."""
    for prefix, ns in PREFIXES.items():
        if ident.startswith(prefix):
            return ns[ident[len(prefix):]]
    raise ValueError(f"unknown id prefix: {ident}")


def source(path):
    return SRC["value-stream-" + os.path.basename(path)[len("value_stream_"):-len(".json")].replace("_", "-")]


def indexes():
    core = Graph().parse(CORE)
    procs = {}
    for s, n in core.subject_objects(SKOS.notation):
        if str(s).startswith(str(PROC)):
            procs.setdefault(str(n), set()).add(s)
    dps = Graph().parse(DATA_PRODUCTS)
    items = {str(n): s for s, n in dps.subject_objects(SKOS.notation)}
    measures = {str(n) for n in Graph().parse(MEASURES).objects(None, SKOS.notation)}
    return procs, items, measures


def load():
    streams = []
    for path in STREAMS:
        with open(path) as f:
            streams.append((path, json.load(f)))
    procs, items, measures = indexes()
    problems, ids = [], Counter()
    for path, d in streams:
        name = os.path.basename(path)
        local = {d["id"]} | {c["id"] for c in d["capabilities"]}
        ids[d["id"]] += 1
        for c in d["capabilities"]:
            ids[c["id"]] += 1
            problems += [f"{name} {c['id']}: process group {p!r} is not in core 2.2.0"
                         for p in c.get("alignsToProcessGroups", []) if len(procs.get(p, ())) != 1]
        vsps = set()
        for s in d["stages"]:
            ids[s["id"]] += 1
            for p in s["processes"]:
                ids[p["id"]] += 1
                vsps.add(p["id"])
                if p["capabilityId"] not in local:
                    problems.append(f"{name} {p['id']}: capability {p['capabilityId']!r} is not in this value stream")
                problems += [f"{name} {p['id']}: process {x!r} is not in core 2.2.0"
                             for x in p["linkedProcessIds"] if len(procs.get(x, ())) != 1]
                problems += [f"{name} {p['id']}: {x!r} is not in the data-product module"
                             for x in p["produces"] + p["consumes"] if x not in items]
                problems += [f"{name} {p['id']}: measure {m['measureId']!r} is not in the kpi module"
                             for m in p.get("measures", []) if m["measureId"] not in measures]
                problems += [f"{name} {p['id']}: relationship {m['relationship']!r} is not on the list"
                             for m in p.get("measures", []) if m["relationship"] not in RELATIONSHIPS]
        for fl in d["flows"]:
            if fl["from"] not in vsps or fl["to"] not in vsps or fl["kind"] not in FLOWS:
                problems.append(f"{name}: flow {fl} names a process outside this value stream or an unknown kind")
    problems += [f"id {i!r} appears {n} times" for i, n in ids.items() if n > 1]
    if problems:
        sys.exit("value-stream sources do not reconcile:\n  " + "\n  ".join(problems))
    return streams, procs, items


def label(g, node, cls, item, src):
    g.add((node, RDF.type, cls))
    g.add((node, SKOS.prefLabel, Literal(item["name"], lang="en")))
    g.add((node, SKOS.notation, Literal(item["id"], datatype=XSD.string)))
    if item.get("description"):
        g.add((node, SKOS.definition, Literal(item["description"], lang="en")))
    g.add((node, DCTERMS.source, src))


def build(streams, procs, items):
    g = Graph()
    for prefix, ns in (("vs", VS), ("rel", REL), ("stream", STREAM), ("stage", STAGE), ("capability", CAPABILITY),
                       ("vsprocess", VSPROCESS), ("mlink", MLINK), ("proc", PROC), ("measure", MEASURE),
                       ("src", SRC), ("skos", SKOS), ("dcterms", DCTERMS)):
        g.bind(prefix, ns)
    for path, d in streams:
        src = source(path)
        g.add((src, RDF.type, DCTERMS.BibliographicResource))
        g.add((src, DCTERMS.title, Literal(
            f"Value stream {d['name']}, business_architecture/business_process/{os.path.basename(path)}, generated "
            + d["meta"]["generatedAt"] + ", from: " + "; ".join(d["meta"]["sources"]), lang="en")))
        stream = iri(d["id"])
        label(g, stream, VS.ValueStream, d, src)
        g.add((stream, VS.sourceDomain, Literal(d["domain"], datatype=XSD.string)))
        for prop, key in ((VS.trigger, "trigger"), (VS.outcome, "outcome")):
            if d.get(key):
                g.add((stream, prop, Literal(d[key], datatype=XSD.string)))
        for c in d["capabilities"]:
            cap = iri(c["id"])
            label(g, cap, VS.Capability, c, src)
            g.add((stream, VS.usesCapabilityInStream, cap))
            for p in c.get("alignsToProcessGroups", []):
                g.add((cap, VS.alignsToProcessGroup, next(iter(procs[p]))))
        for s in d["stages"]:
            stage = iri(s["id"])
            label(g, stage, VS.Stage, s, src)
            g.add((stream, VS.hasStage, stage))
            g.add((stage, VS.sequence, Literal(s["sequence"])))
            for p in s["processes"]:
                node = iri(p["id"])
                label(g, node, VS.ValueStreamProcess, p, src)
                g.add((stage, VS.hasProcess, node))
                g.add((node, VS.usesCapability, iri(p["capabilityId"])))
                if p.get("rationale"):
                    g.add((node, SKOS.scopeNote, Literal(p["rationale"], lang="en")))
                for x in p["linkedProcessIds"]:
                    g.add((node, VS.realizes, next(iter(procs[x]))))
                for x in p["produces"]:
                    g.add((node, VS.produces, items[x]))
                for x in p["consumes"]:
                    g.add((node, VS.consumes, items[x]))
                for m in p.get("measures", []):
                    link = MLINK[f"{p['id'][2:]}--{m['measureId']}"]
                    g.add((node, VS.measureLink, link))
                    g.add((link, RDF.type, VS.MeasureLink))
                    g.add((link, VS.measure, MEASURE[m["measureId"]]))
                    g.add((link, VS.relationship, REL[m["relationship"]]))
                    g.add((link, DCTERMS.bibliographicCitation, Literal(m["basis"], datatype=XSD.string)))
        for fl in d["flows"]:
            g.add((iri(fl["from"]), FLOWS[fl["kind"]], iri(fl["to"])))
    return g


def figures(streams):
    procs = [p for _, d in streams for s in d["stages"] for p in s["processes"]]
    return {
        "value streams": len(streams),
        "stages": sum(len(d["stages"]) for _, d in streams),
        "capabilities": sum(len(d["capabilities"]) for _, d in streams),
        "value-stream processes": len(procs),
        "links to core processes": sum(len(p["linkedProcessIds"]) for p in procs),
        "processes with no core link": sum(1 for p in procs if not p["linkedProcessIds"]),
        "produces links": sum(len(p["produces"]) for p in procs),
        "consumes links": sum(len(p["consumes"]) for p in procs),
        "measure links": sum(len(p.get("measures", [])) for p in procs),
        "flows": sum(len(d["flows"]) for _, d in streams),
        "gap notes (no nodes)": sum(len(d["gapAnalysis"]) for _, d in streams),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    streams, procs, items = load()
    text = ("# Value streams of the value-stream module (Step 7; EPM-DEC-001-0054).\n"
            "# Built by build_value_streams.py from business_process/value_stream_*.json. Do not edit by hand.\n"
            + build(streams, procs, items).serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(streams).items()))
    if args.verify:
        current = os.path.exists(OUTPUT) and open(OUTPUT).read() == text
        if not current:
            sys.exit("value-streams.ttl is not current: run build_value_streams.py --write")
        print("value-streams.ttl is current")
    if args.write:
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
