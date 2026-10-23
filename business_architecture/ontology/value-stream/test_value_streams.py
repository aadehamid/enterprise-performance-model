"""Tests for the value-stream module (Step 7; EPM-DEC-001-0054): the vocabulary is well formed,
the build reconciles with the two value-stream files and is current, each link keeps the
source's target and relationship, and SHACL accepts the module and rejects broken items.

Run: python3 -m pytest test_value_streams.py (needs rdflib, pyshacl).
"""
import json
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_value_streams as bv  # noqa: E402

VS, REL, STREAM, STAGE, CAP, VSP, MLINK, PROC, MEASURE = (
    bv.VS, bv.REL, bv.STREAM, bv.STAGE, bv.CAPABILITY, bv.VSPROCESS, bv.MLINK, bv.PROC, bv.MEASURE)
DPROD = URIRef("https://w3id.org/lsc/ontology/modules/data-product/product/")
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
STREAMS = Graph().parse(os.path.join(HERE, "value-streams.ttl"))
CONTEXT = Graph().parse(bv.DATA_PRODUCTS).parse(bv.MEASURES) \
    .parse(os.path.join(HERE, "..", "data-product", "vocabulary.ttl")).parse(os.path.join(HERE, "..", "kpi", "vocabulary.ttl"))
SOURCES = {}
for path in bv.STREAMS:
    with open(path) as f:
        SOURCES[os.path.basename(path)] = json.load(f)


def product(slug):
    return URIRef(str(DPROD) + slug)


def conforms(data):
    ok, _, report = validate(data + VOCAB + CONTEXT, shacl_graph=SHAPES, advanced=True)
    return ok, report


class Vocabulary(unittest.TestCase):
    def test_produces_and_consumes_range_over_skos_concept(self):
        # EPM-DEC-001-0090, item 3: both take rdfs:range skos:Concept, not dp:DataProduct, because a data product
        # line is an allowed value. Checked in the source and in the released 1.1.0 package.
        released = Graph().parse(os.path.join(HERE, "..", "releases", "value-stream", "1.1.0", "value-stream.ttl"))
        for g in (VOCAB, released):
            for p in (VS.produces, VS.consumes):
                self.assertEqual(set(g.objects(p, RDFS.range)), {SKOS.Concept}, p)
        # A line is a real object of vs:consumes, and both kinds are SKOS concepts in the pinned data-product package.
        dp = Graph().parse(os.path.join(HERE, "..", "releases", "data-product", "1.0.0", "data-product.ttl"))
        line = URIRef("https://w3id.org/lsc/ontology/modules/data-product/line/planning-optimization")
        self.assertIn(line, set(STREAMS.objects(None, VS.consumes)))
        for o in set(STREAMS.objects(None, VS.produces)) | set(STREAMS.objects(None, VS.consumes)):
            self.assertIn((o, RDF.type, SKOS.Concept), dp, o)

    def test_every_term_is_defined_and_cited(self):
        kinds = (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty)
        terms = {t for k in kinds for t in VOCAB.subjects(RDF.type, k)}
        self.assertEqual(len(terms), 23)  # 5 classes, 18 properties, counted by hand
        for t in terms:
            self.assertIsNotNone(VOCAB.value(t, SKOS.definition), t)
            self.assertIsNotNone(VOCAB.value(t, URIRef("http://purl.org/dc/terms/bibliographicCitation")), t)

    def test_relationship_list_matches_the_schema(self):
        notations = {str(n) for s in VOCAB.subjects(SKOS.inScheme, VS.MeasureRelationship) for n in VOCAB.objects(s, SKOS.notation)}
        self.assertEqual(notations, {"informs", "benchmarks", "measures-performance"})


class Build(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_value_streams.py"), "--verify"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_figures(self):
        # Pinned on 2026-10-19. Streams, stages, capabilities, processes, flows and gap notes were
        # counted by hand in the two files; the link counts are the build's.
        # 2026-10-23: MPC-P10.2 linked Review Credit Limit & Risk Code to CM 1.3.7.4.2 and removed its gap
        # note (EPM-DEC-001-0087): one more core link, no process without one, one gap note fewer.
        streams, *_ = bv.load()
        self.assertEqual(bv.figures(streams), {
            "value streams": 2, "stages": 12, "capabilities": 21, "value-stream processes": 58,
            "links to core processes": 73, "processes with no core link": 0, "produces links": 9,
            "consumes links": 37, "measure links": 7, "flows": 4, "gap notes (no nodes)": 8})

    def test_stage_order(self):
        stages = sorted((int(STREAMS.value(s, VS.sequence)), s) for s in STREAMS.objects(STREAM["order-to-cash"], VS.hasStage))
        self.assertEqual([s for _, s in stages][:3], [STAGE["otc-master-data"], STAGE["otc-quote-sale"], STAGE["otc-credit-risk"]])
        self.assertEqual(len(stages), 9)

    def test_links_keep_their_targets(self):
        procs = bv.indexes()[0]
        for d in SOURCES.values():
            for s in d["stages"]:
                for p in s["processes"]:
                    node = bv.iri(p["id"])
                    self.assertEqual(STREAMS.value(node, VS.usesCapability), bv.iri(p["capabilityId"]), p["id"])
                    self.assertEqual(set(STREAMS.objects(node, VS.realizes)),
                                     {next(iter(procs[x])) for x in p["linkedProcessIds"]}, p["id"])
                    for m in p.get("measures", []):
                        link = MLINK[f"{p['id'][2:]}--{m['measureId']}"]
                        self.assertEqual(STREAMS.value(link, VS.relationship), REL[m["relationship"]], link)
                        self.assertEqual(STREAMS.value(link, VS.measure), MEASURE[m["measureId"]], link)

    def test_data_product_links_keep_their_targets(self):
        items = bv.indexes()[1]
        for d in SOURCES.values():
            for s in d["stages"]:
                for p in s["processes"]:
                    node = bv.iri(p["id"])
                    self.assertEqual(set(STREAMS.objects(node, VS.produces)), {items[x] for x in p["produces"]}, p["id"])
                    self.assertEqual(set(STREAMS.objects(node, VS.consumes)), {items[x] for x in p["consumes"]}, p["id"])

    def test_pinned_examples(self):
        # Pinned by hand from value_stream_commercial_lifecycle.json.
        node = VSP["deal-negotiation-capture"]
        self.assertEqual(set(STREAMS.objects(node, VS.realizes)), {PROC["CM-1-2-1-3"], PROC["CM-1-2-1-2"]})
        self.assertEqual(set(STREAMS.objects(node, VS.produces)), {product("physical-trading")})
        self.assertEqual(set(STREAMS.objects(node, VS.consumes)), {product("commercial-risk"), product("master-pricing")})
        self.assertIn((VSP["settlement-post-trade-reconciliation"], VS.loopsTo, VSP["market-intelligence-planning"]), STREAMS)
        link = MLINK["performance-tracking-analysis--rm-margin-per-barrel"]
        self.assertEqual(STREAMS.value(link, VS.relationship), REL["measures-performance"])
        self.assertEqual(STREAMS.value(STREAM["commercial-hydrocarbon-lifecycle"], VS.sourceDomain),
                         Literal("Commercial", datatype=XSD.string))
        # The one value-stream process the source linked to no map node; since MPC-P10.2 it realizes
        # CM 1.3.7.4.2 (EPM-DEC-001-0087, 0090).
        self.assertEqual(list(STREAMS.objects(VSP["otc-review-credit-limit-risk-code"], VS.realizes)), [PROC["CM-1-3-7-4-2"]])

    def test_gap_analysis_creates_nothing(self):
        # Every node with a notation comes from an id in the source files, never from gapAnalysis.
        ids = set()
        for d in SOURCES.values():
            ids |= {d["id"]} | {c["id"] for c in d["capabilities"]}
            for s in d["stages"]:
                ids |= {s["id"]} | {p["id"] for p in s["processes"]}
        self.assertEqual({str(n) for n in STREAMS.objects(None, SKOS.notation)}, ids)


class Shapes(unittest.TestCase):
    def test_module_conforms(self):
        ok, report = conforms(STREAMS)
        self.assertTrue(ok, report)

    def broken(self, edit):
        g = Graph()
        for t in STREAMS:
            g.add(t)
        edit(g)
        return conforms(g)[0]

    def test_rejects_a_process_with_two_capabilities(self):
        self.assertFalse(self.broken(lambda g: g.add((VSP["deal-negotiation-capture"], VS.usesCapability, CAP["price-management"]))))

    def test_rejects_a_produced_item_that_is_not_a_data_product(self):
        self.assertFalse(self.broken(lambda g: g.add((VSP["deal-negotiation-capture"], VS.produces, PROC["CM-1-2-1-3"]))))

    def test_rejects_more_than_four_consumed(self):
        def edit(g):
            for slug in ("loss-control", "gis", "hr", "it", "legal"):
                g.add((VSP["otc-manage-returns"], VS.consumes, product(slug)))
        self.assertFalse(self.broken(edit))

    def test_rejects_a_link_to_an_unknown_measure(self):
        link = MLINK["performance-tracking-analysis--rm-margin-per-barrel"]
        def edit(g):
            g.remove((link, VS.measure, None))
            g.add((link, VS.measure, MEASURE["no-such-measure"]))
        self.assertFalse(self.broken(edit))

    def test_rejects_a_relationship_off_the_list(self):
        link = MLINK["performance-tracking-analysis--rm-margin-per-barrel"]
        def edit(g):
            g.remove((link, VS.relationship, None))
            g.add((link, VS.relationship, REL["certifies"]))
        self.assertFalse(self.broken(edit))

    def test_rejects_a_kind_on_a_link(self):
        link = MLINK["performance-tracking-analysis--rm-margin-per-barrel"]
        kind = URIRef("https://w3id.org/lsc/ontology/modules/kpi/measure-kind/kpi")
        self.assertFalse(self.broken(lambda g: g.add((link, URIRef("https://w3id.org/lsc/ontology/modules/kpi/measureKind"), kind))))

    def test_rejects_a_stage_in_two_streams(self):
        self.assertFalse(self.broken(lambda g: g.add((STREAM["order-to-cash"], VS.hasStage, STAGE["market-strategy-formation"]))))


if __name__ == "__main__":
    unittest.main()
