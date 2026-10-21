"""Tests for the consumer rules (Step 7; EPM-DEC-001-0061): the rules conform, each relies on
its decided terms (pinned by hand) and on terms the graph defines, the rule counts are the decided ones, and the catalog binding accepts
a defined data product and measure and rejects an undefined end.

Run: python3 -m pytest test_consumer_rules.py (needs rdflib, pyshacl).
"""
import os
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "regression"))
import run  # noqa: E402

CON = Namespace("https://w3id.org/lsc/ontology/modules/consumer/")
RK = Namespace("https://w3id.org/lsc/ontology/modules/consumer/rule-kind/")
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
GRAPH = run.load(run.RELEASE)
PRODUCT = URIRef("https://w3id.org/lsc/ontology/modules/data-product/product/master-pricing")
MEASURE = URIRef("https://w3id.org/lsc/ontology/modules/kpi/measure/crack-spreads")


def conforms(extra=None):
    g = Graph()
    g += GRAPH
    if extra:
        g += extra
    return validate(g, shacl_graph=SHAPES, advanced=True)[0]


class Rules(unittest.TestCase):
    def test_counts(self):
        # EPM-DEC-001-0061: six things an agent may answer, five it must refuse; EPM-DEC-001-0062 adds a seventh.
        rules = set(VOCAB.subjects(RDF.type, CON.Rule))
        self.assertEqual(len([r for r in rules if (r, CON.ruleKind, RK["may-answer"]) in VOCAB]), 7)
        self.assertEqual(len([r for r in rules if (r, CON.ruleKind, RK["must-refuse"]) in VOCAB]), 5)

    def test_each_rule_relies_on_its_decided_terms(self):
        # Pinned by hand from EPM-DEC-001-0061: a term that exists but means something else fails.
        R = Namespace("https://w3id.org/lsc/ontology/modules/consumer/rule/")
        KPI = Namespace("https://w3id.org/lsc/ontology/modules/kpi/")
        MKT = Namespace("https://w3id.org/lsc/ontology/modules/market-data/")
        VS = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/")
        PLC = Namespace("https://w3id.org/lsc/ontology/modules/placement/")
        AUTH = Namespace("https://w3id.org/lsc/ontology/modules/authority/")
        ORGM = Namespace("https://w3id.org/lsc/ontology/modules/organization/")
        SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
        DCT = Namespace("http://purl.org/dc/terms/")
        POP = Namespace("https://w3id.org/lsc/ontology/modules/population/")
        expected = {
            "definitions": {SKOS.definition, SKOS.prefLabel, SKOS.altLabel, KPI.measureKind},
            "not-to-be-confused-with": {KPI.notToBeConfusedWith, MKT.seriesOf},
            "placement": {KPI.informsProcess, VS.measureLink, VS.produces, VS.consumes, PLC.placementKind},
            "recipe": {MKT.leg, MKT.barrels, MKT.region, MKT.excludesRINCost},
            "who-does-it": {ORGM.forProcess},
            "which-source": {DCT.source, AUTH.evidenceTier},
            "no-values": {KPI.basis},
            "no-crack-from-legs": {MKT.leg, MKT.seriesOf},
            "no-report-as-kpi": {KPI.measureKind, KPI.kpiCandidate},
            "no-customer-without-role": {URIRef("https://w3id.org/lsc/ontology/process/CM-1-3-7-1-1"),
                                         URIRef("https://w3id.org/lsc/ontology/modules/customer/roleType")},  # EPM-DEC-001-0068
            "no-context-as-ownership": {PLC.placementKind},
            "what-a-measure-counts": {POP.includes, POP.excludes, POP.populationEvidence},  # EPM-DEC-001-0062
        }
        rules = set(VOCAB.subjects(RDF.type, CON.Rule))
        self.assertEqual(rules, {R[k] for k in expected})
        for key, terms in expected.items():
            self.assertEqual(set(VOCAB.objects(R[key], CON.reliesOn)), terms, key)

    def test_rules_rely_on_defined_terms(self):
        for term in set(VOCAB.objects(None, CON.reliesOn)):
            if str(term).startswith("https://w3id.org/lsc/"):
                self.assertTrue(list(GRAPH.triples((term, None, None))), term)

    def test_rules_conform(self):
        self.assertTrue(conforms())


class Binding(unittest.TestCase):
    def test_a_defined_binding_conforms(self):
        g = Graph()
        g.add((PRODUCT, CON.publishesMeasure, MEASURE))
        self.assertTrue(conforms(g))

    def test_an_undefined_measure_fails(self):
        g = Graph()
        g.add((PRODUCT, CON.publishesMeasure, URIRef(str(MEASURE) + "-homemade")))
        self.assertFalse(conforms(g))

    def test_an_undefined_data_product_fails(self):
        g = Graph()
        g.add((URIRef(str(PRODUCT) + "-unknown"), CON.publishesMeasure, MEASURE))
        self.assertFalse(conforms(g))


if __name__ == "__main__":
    unittest.main()
