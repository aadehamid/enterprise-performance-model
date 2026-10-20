"""Tests for the placement kinds (Step 7; EPM-DEC-001-0058): every property that places a
subject on a process has exactly one kind, the kinds are the ones the record decided, and every
annotated property is defined in its own module.

Run: python3 -m pytest test_placement.py (needs rdflib).
"""
import os
import unittest

from rdflib import Graph, Namespace

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

    def test_every_annotated_property_exists(self):
        for p in set(VOCAB.subjects(PLC.placementKind, None)):
            self.assertTrue(list(MODULES.triples((p, None, None))), p)


if __name__ == "__main__":
    unittest.main()
