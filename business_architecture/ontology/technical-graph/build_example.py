"""Build the technical-graph module's example graph (EPM-DEC-001-0112, item 4).

    python3 build_example.py            # build and print the figures
    python3 build_example.py --write    # also write example/example-graph.ttl
    python3 build_example.py --verify   # fail unless example/example-graph.ttl equals a fresh build

The example is test data, not ontology content: it never ships in the module's package. The regression
runs competency questions 45 to 50 on the module plus this example, and the same queries run on the
demo's live technical graph.

It is cut from the pricing demo's technical graph (demos/downstream-pricing-databricks-free/graph/
tech-graph.ttl): everything upstream of the metric views that compute the crack-spreads measure, the
agents bound to them and the orchestrator routing to those agents, the source databases and hosts they
copy from, the pipeline steps that produced them and the quality checks that test them. The demo's graph uses
the module's terms, so it is cut as it stands (demo_graph); until 2026-11-02 it used its own vocabulary
(urn:pricing-demo:tech-vocab#), which a mapping here translated. One design is added that
the demo lacks, so that question 49 (who answers for it) has an answer to find: a gold table designed as
an example data product, produced by a process that has an Accountable role in organization. In
the ontology today no path reaches an owner: the pricing data products record no producing process, and
the two data products that do record one (data-products.ttl) are produced by processes with no RACI
assignment.
"""
import argparse
import os
import sys

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEMO_GRAPH = os.path.join(REPO, "demos", "downstream-pricing-databricks-free", "graph", "tech-graph.ttl")
OUTPUT = os.path.join(HERE, "example", "example-graph.ttl")

TG = Namespace("https://w3id.org/lsc/ontology/modules/technical-graph/")
RESULT = Namespace("https://w3id.org/lsc/ontology/modules/technical-graph/check-result/")
LAYER = Namespace("https://w3id.org/lsc/ontology/modules/data-product/layer/")
DP = Namespace("https://w3id.org/lsc/ontology/modules/data-product/")
MEASURE = Namespace("https://w3id.org/lsc/ontology/modules/kpi/measure/")
TV = Namespace("urn:pricing-demo:tech-vocab#")  # the demo's old vocabulary, which demo_graph refuses
EX = Namespace("urn:example:technical-graph:")
LINE = Namespace("https://w3id.org/lsc/ontology/modules/data-product/line/")
STATUS = Namespace("https://w3id.org/lsc/ontology/modules/data-product/status/")
AUTH = Namespace("https://w3id.org/lsc/ontology/modules/authority/")
TIER = Namespace("https://w3id.org/lsc/ontology/modules/authority/tier/")

MEASURE_OF_EXAMPLE = MEASURE["crack-spreads"]
PRODUCING_PROCESS = URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-2-1")  # has an Accountable role (assignments.ttl)


def demo_graph(path=DEMO_GRAPH):
    """The demo's technical graph, which uses the module's terms since the demo moved onto them (EPM-DEC-001-0112,
    item 4). A term of the demo's old vocabulary (urn:pricing-demo:tech-vocab#) stops the build."""
    g = Graph().parse(path)
    old = sorted({str(t) for triple in g for t in triple if str(t).startswith(str(TV))})
    if old:
        sys.exit("the demo's graph still uses its old vocabulary:\n  " + "\n  ".join(old))
    return g


def cut(g):
    """The part of g upstream of the metric views computing the example's measure, and what tests and uses it."""
    def upstream(nodes):  # as-built lineage, then the source databases and hosts behind it
        found, frontier = set(nodes), list(nodes)
        while frontier:
            node = frontier.pop()
            for p in (TG.readsFrom, TG.copies, TG.hostedOn):
                for o in g.objects(node, p):
                    if o not in found:
                        found.add(o)
                        frontier.append(o)
        return found

    keep = upstream(g.subjects(TG.implements, MEASURE_OF_EXAMPLE))
    agents = {a for a in g.subjects(TG.binds, None) if set(g.objects(a, TG.binds)) & keep}
    keep |= agents
    keep = upstream(keep | {o for a in agents for o in g.objects(a, TG.binds)})
    keep |= {o for o in g.subjects(TG.routesTo, None) if set(g.objects(o, TG.routesTo)) & agents}
    checks = {c for c in g.subjects(RDF.type, TG.QualityCheck) if set(g.objects(c, TG.checks)) & keep}
    keep |= checks
    steps = {o for n in keep for o in g.objects(n, TG.producedBy)}
    keep |= steps
    out = Graph()
    for s, p, o in g:
        if s not in keep:
            continue
        if p in (TG.checks, TG.routesTo, TG.next) and o not in keep:
            continue  # a check, an orchestrator and a step keep only the links inside the example
        out.add((s, p, o))
    return out


def designed_example(g):
    """One design the demo lacks: the gold table the example's metric view reads, designed as an example data product
    produced by CM 1.1.2.1, a process with an Accountable role in organization. Test data only, written to meet
    data-product's and authority's shapes, so the whole-graph gate can load it beside the modules. A platform table
    cannot carry it: data-product's shapes make every non-replica platform table part of the master-pricing product,
    which records no producing process."""
    gold = sorted(o for v in g.subjects(TG.implements, MEASURE_OF_EXAMPLE) for o in g.objects(v, TG.readsFrom)
                  if (o, TG.layer, LAYER.gold) in g)[0]
    product, source = EX["product/example-data-product"], EX["source/example-graph"]
    g.remove((gold, TG.designedAs, None))
    g.add((gold, TG.designedAs, product))
    g.add((product, RDF.type, SKOS.Concept))
    g.add((product, RDF.type, DP.DataProduct))
    g.add((product, SKOS.prefLabel, Literal("An example data product", lang="en")))
    g.add((product, SKOS.inScheme, DP.DataProducts))
    g.add((product, SKOS.broader, LINE["marketing-sales"]))
    g.add((product, SKOS.notation, Literal("example-data-product", datatype=XSD.string)))
    g.add((product, SKOS.definition, Literal("A data product that exists only in this example, so that question 49 has an owner to find.", lang="en")))
    g.add((product, DP.portfolioStatus, STATUS.active))
    g.add((product, DP.producedBy, PRODUCING_PROCESS))
    g.add((product, DCTERMS.source, source))
    g.add((source, RDF.type, DCTERMS.BibliographicResource))
    g.add((source, DCTERMS.title, Literal("EPM-DEC-001-0112, item 4: the technical-graph module's example graph, test data", lang="en")))
    g.add((source, AUTH.evidenceTier, TIER["process-authority"]))
    return g


def build():
    g = designed_example(cut(demo_graph()))
    for prefix, ns in (("tg", TG), ("result", RESULT), ("layer", LAYER), ("dp", DP),
                       ("measure", MEASURE), ("ex", EX), ("skos", SKOS), ("dcterms", DCTERMS), ("rdfs", RDFS)):
        g.bind(prefix, ns)
    return g


def figures(g):
    kinds = {}
    for _, cls in g.subject_objects(RDF.type):
        if str(cls).startswith(str(TG)):
            kinds[str(cls)[len(str(TG)):]] = kinds.get(str(cls)[len(str(TG)):], 0) + 1
    return {"triples": len(g), **dict(sorted(kinds.items()))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    g = build()
    text = ("# The technical-graph module's example graph: test data, not ontology content (EPM-DEC-001-0112, item 4).\n"
            "# Built by build_example.py from the pricing demo's technical graph. Do not edit by hand.\n"
            + g.serialize(format="turtle"))
    print("; ".join(f"{k} {v}" for k, v in figures(g).items()))
    if args.verify:
        if not (os.path.exists(OUTPUT) and open(OUTPUT).read() == text):
            sys.exit("example/example-graph.ttl is not current: run build_example.py --write")
        print("example/example-graph.ttl is current")
    if args.write:
        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, "w") as f:
            f.write(text)
        print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
