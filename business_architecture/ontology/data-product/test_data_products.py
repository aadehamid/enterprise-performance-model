"""Tests for the data-product module (Step 7; EPM-DEC-001-0053): the vocabulary is well formed,
the build reconciles with the portfolio and is current, each item keeps the portfolio's status
and place, SHACL accepts the module and rejects broken items.

Run: python3 -m pytest test_data_products.py (needs rdflib, pyshacl).
"""
import json
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_data_products as bd  # noqa: E402

DP, STATUS, PRODUCT, LINE, SEGMENT, PROC = bd.DP, bd.STATUS, bd.PRODUCT, bd.LINE, bd.SEGMENT, bd.PROC
DCAT = Namespace("http://www.w3.org/ns/dcat#")
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
PRODUCTS = Graph().parse(os.path.join(HERE, "data-products.ttl"))
with open(bd.PORTFOLIO) as f:
    PORTFOLIO = json.load(f)


def conforms(data):
    ok, _, report = validate(data + VOCAB, shacl_graph=SHAPES, advanced=True)
    return ok, report


class Vocabulary(unittest.TestCase):
    def test_every_term_is_defined_and_cited(self):
        terms = set(VOCAB.subjects(RDF.type, OWL.Class)) | set(VOCAB.subjects(RDF.type, OWL.ObjectProperty))
        self.assertEqual(len(terms), 7)
        for t in terms:
            self.assertIsNotNone(VOCAB.value(t, SKOS.definition), t)
            self.assertIsNotNone(VOCAB.value(t, URIRef("http://purl.org/dc/terms/bibliographicCitation")), t)

    def test_dcat_is_mapped_not_imported(self):
        self.assertIn((DP.DataProduct, SKOS.closeMatch, DCAT.Dataset), VOCAB)
        self.assertFalse(list(VOCAB.subjects(OWL.imports, None)))
        self.assertFalse(list(VOCAB.subjects(RDFS.subClassOf, DCAT.Dataset)))

    def test_status_code_list_matches_the_schema(self):
        notations = {str(n) for s in VOCAB.subjects(SKOS.inScheme, DP.PortfolioStatus) for n in VOCAB.objects(s, SKOS.notation)}
        self.assertEqual(notations, {"active", "defined_only", "open_decision"})


class Build(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_data_products.py"), "--verify"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_figures(self):
        # Counted by hand from data_product_portfolio.json on 2026-10-19; Loss Control's link is
        # emitted since core 2.2.0 (2026-10-22, EPM-DEC-001-0076).
        portfolio, links, *_ = bd.load()
        self.assertEqual(bd.figures(portfolio, links), {
            "segments": 3, "lines": 19, "data products": 48, "active products": 15,
            "defined_only products": 33, "open_decision products": 0, "parked without a description": 33,
            "process links": 1, "links waiting for a core release": 0})
        self.assertEqual(len(set(PRODUCTS.subjects(RDF.type, DP.DataProduct))), 48)
        self.assertEqual(len(set(PRODUCTS.subjects(RDF.type, DP.DataProductLine))), 19)

    def test_segment_anchors(self):
        # Pinned by hand: the portfolio's processDomainRef for each segment.
        self.assertEqual({s: PRODUCTS.value(s, DP.anchoredIn) for s in PRODUCTS.subjects(RDF.type, DP.PortfolioSegment)}, {
            SEGMENT["commercial"]: PROC["CM-1"],
            SEGMENT["midstream"]: PROC["L1-midstream"],
            SEGMENT["corporate"]: PROC["L0-enabling-functions"]})

    def test_each_item_keeps_its_status_and_place(self):
        for seg in PORTFOLIO["segments"]:
            for line in seg["productLines"]:
                l = LINE[line["id"][4:]]
                self.assertEqual(PRODUCTS.value(l, SKOS.broader), SEGMENT[seg["id"][4:]])
                self.assertEqual(PRODUCTS.value(l, DP.portfolioStatus), STATUS[bd.STATUSES[line["status"]]])
                for p in line["portfolios"]:
                    iri = PRODUCT[p["id"][3:]]
                    self.assertEqual(PRODUCTS.value(iri, SKOS.broader), l, p["id"])
                    self.assertEqual(PRODUCTS.value(iri, DP.portfolioStatus), STATUS[bd.STATUSES[p["status"]]], p["id"])
                    self.assertEqual(str(PRODUCTS.value(iri, SKOS.notation)), p["id"])

    def test_loss_control_is_produced_by_its_process(self):
        # CM 1.1.3.7.13 produces Loss Control (EPM-DEC-001-0048). It waited for core 2.2.0, which
        # added the process (EPM-DEC-001-0076), so the link is now emitted.
        self.assertEqual(PRODUCTS.value(PRODUCT["loss-control"], DP.producedBy),
                         URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-3-7-13"))
        _, links, by_key, _ = bd.load()
        self.assertEqual([(r["data_product"], r["process"], r["waits_for"]) for r in links],
                         [("dp-loss-control", "CM 1.1.3.7.13", "")])
        self.assertIn("CM 1.1.3.7.13", by_key)

    def test_aliases(self):
        self.assertIn((PRODUCT["commercial-risk"], SKOS.altLabel, Literal("Risk", lang="en")), PRODUCTS)
        self.assertIn((LINE["planning-optimization"], SKOS.altLabel, Literal("P&O", lang="en")), PRODUCTS)
        # "Master & Rack Pricing" names two data products, so it labels neither.
        self.assertFalse(list(PRODUCTS.subjects(SKOS.altLabel, Literal("Master & Rack Pricing", lang="en"))))
        # "ES&S" is already the data product's name.
        self.assertFalse(list(PRODUCTS.objects(PRODUCT["ess"], SKOS.altLabel)))


class Gates(unittest.TestCase):
    """The build's own checks, run on doctored copies of its inputs (Pi round 2 suggestion)."""

    def fails(self, edit_portfolio=None, links=None):
        import copy
        portfolio = copy.deepcopy(PORTFOLIO)
        if edit_portfolio:
            edit_portfolio(portfolio)
        real_open = open

        def fake_open(path, *a, **k):
            import io
            if path == bd.PORTFOLIO:
                return io.StringIO(json.dumps(portfolio))
            if path == bd.LINKS and links is not None:
                return io.StringIO(links)
            return real_open(path, *a, **k)
        import builtins
        builtins.open = fake_open
        try:
            with self.assertRaises(SystemExit) as cm:
                bd.load()
            return str(cm.exception)
        finally:
            builtins.open = real_open

    def test_a_missing_status_fails(self):
        def edit(p):
            del p["segments"][0]["productLines"][0]["portfolios"][0]["status"]
        self.assertIn("is not on the code list", self.fails(edit))

    def test_a_segment_without_a_description_fails(self):
        def edit(p):
            p["segments"][1]["description"] = None
        self.assertIn("needs a description", self.fails(edit))

    def test_a_spent_waits_for_fails(self):
        rows = "data_product,relation,process,source,waits_for\ndp-commercial-risk,produced-by,CM 1.2.2,test,core 2.9.9\n"
        self.assertIn("is in core now", self.fails(links=rows))


class Shapes(unittest.TestCase):
    def test_module_conforms(self):
        ok, report = conforms(PRODUCTS)
        self.assertTrue(ok, report)

    def broken(self, edit):
        g = Graph()
        for t in PRODUCTS:
            g.add(t)
        edit(g)
        ok, _ = conforms(g)
        return ok

    def test_rejects_defined_and_parked(self):
        self.assertFalse(self.broken(lambda g: g.add((PRODUCT["loss-control"], SKOS.editorialNote, Literal("parked", lang="en")))))

    def test_rejects_neither_defined_nor_parked(self):
        self.assertFalse(self.broken(lambda g: g.remove((PRODUCT["ess"], SKOS.editorialNote, None))))

    def test_rejects_active_without_definition(self):
        def edit(g):
            g.remove((PRODUCT["ess"], DP.portfolioStatus, None))
            g.add((PRODUCT["ess"], DP.portfolioStatus, STATUS["active"]))
        self.assertFalse(self.broken(edit))

    def test_rejects_a_value_on_a_product(self):
        self.assertFalse(self.broken(lambda g: g.add((PRODUCT["loss-control"], DP.recordCount, Literal(42)))))

    def test_rejects_a_product_in_two_lines(self):
        self.assertFalse(self.broken(lambda g: g.add((PRODUCT["loss-control"], SKOS.broader, LINE["marketing-sales"]))))

    def test_rejects_a_segment_without_an_anchor(self):
        self.assertFalse(self.broken(lambda g: g.remove((SEGMENT["corporate"], DP.anchoredIn, None))))

    def test_rejects_a_status_off_the_list(self):
        def edit(g):
            g.remove((PRODUCT["gis"], DP.portfolioStatus, None))
            g.add((PRODUCT["gis"], DP.portfolioStatus, STATUS["retired"]))
        self.assertFalse(self.broken(edit))


if __name__ == "__main__":
    unittest.main()
