"""Tests for the placement kinds (Step 7; EPM-DEC-001-0058): each annotated property has exactly
one kind, the kinds are the ones the record decided, every annotated property is defined in its
own module, and q38a sees a measure certified as an object.

Run: python3 -m pytest test_placement.py (needs rdflib).
"""
import os
import unittest

from rdflib import Graph, Namespace, URIRef

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
PLC = Namespace("https://w3id.org/lsc/ontology/modules/placement/")
KIND = Namespace("https://w3id.org/lsc/ontology/modules/placement/kind/")
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
MODULES = Graph()
for path in ("kpi/vocabulary.ttl", "value-stream/vocabulary.ttl", "data-product/vocabulary.ttl", "system/vocabulary.ttl",
             "lane/vocabulary.ttl", "market-data/vocabulary.ttl"):
    MODULES.parse(os.path.join(ONTOLOGY, path))


def short(iri):
    return str(iri).rstrip("/").split("/")[-1]


class Kinds(unittest.TestCase):
    def test_decided_kinds(self):
        # EPM-DEC-001-0058, item 2: only producing a data product certifies; everything else is context.
        kinds = {short(p): short(k) for p, k in VOCAB.subject_objects(PLC.placementKind)}
        self.assertEqual(kinds, {
            "informsProcess": "context", "measureLink": "context", "consumes": "context", "realizes": "context",
            "usesCapability": "context", "anchoredIn": "context", "consumedBy": "context", "supports": "context",
            "officeLane": "context", "region": "context", "produces": "certification", "producedBy": "certification"})

    def test_one_kind_each(self):
        for p in set(VOCAB.subjects(PLC.placementKind, None)):
            self.assertEqual(len(list(VOCAB.objects(p, PLC.placementKind))), 1, p)

    def test_q38a_sees_a_measure_certified_as_an_object(self):
        # A process that 'produces' a measure would certify it; q38a must list it (Pi round 1).
        import sys
        sys.path.insert(0, os.path.join(ONTOLOGY, "regression"))
        import run
        g = run.load(run.RELEASE)
        vs = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/")
        g.add((URIRef(str(vs) + "process/performance-tracking-analysis"), vs.produces,
               URIRef("https://w3id.org/lsc/ontology/modules/kpi/measure/crack-spreads")))
        with open(os.path.join(ONTOLOGY, "regression", "queries", "q38a-no-measure-certified.rq")) as f:
            self.assertEqual(len(list(g.query(f.read()))), 1)

    def test_every_annotated_property_exists(self):
        for p in set(VOCAB.subjects(PLC.placementKind, None)):
            self.assertTrue(list(MODULES.triples((p, None, None))), p)


if __name__ == "__main__":
    unittest.main()
