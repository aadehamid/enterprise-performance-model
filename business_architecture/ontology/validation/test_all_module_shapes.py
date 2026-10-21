"""Step 9 gate (EPM-DEC-001-0065): every shape file of the release and the modules, run together
on the whole graph the regression loads, finds zero violations. A broken link across modules,
which one module's own test cannot see, fails here.

Run: python3 -m pytest test_all_module_shapes.py (needs rdflib, pyshacl).
"""
import os
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ONTOLOGY, "regression"))
import run  # noqa: E402

SHAPE_FILES = [
    "releases/core/2.1.0/shapes.ttl", "organization/shapes.ttl", "ref-mpc/shapes.ttl", "kpi/shapes.ttl",
    "data-product/shapes.ttl", "value-stream/shapes.ttl", "system/shapes.ttl", "lane/shapes.ttl",
    "market-data/shapes.ttl", "consumer/shapes.ttl", "customer/shapes.ttl", "validation/controlled-values.ttl",
]
GRAPH = run.load(run.RELEASE)
VS = Namespace("https://w3id.org/lsc/ontology/modules/value-stream/")


def shapes():
    g = Graph()
    for path in SHAPE_FILES:
        g.parse(os.path.join(ONTOLOGY, path))
    return g


SHAPES = shapes()


def report(data):
    ok, _, text = validate(data, shacl_graph=SHAPES, advanced=True)
    return ok, text


class AllModules(unittest.TestCase):
    def test_every_shape_file_exists(self):
        for path in SHAPE_FILES:
            self.assertTrue(os.path.exists(os.path.join(ONTOLOGY, path)), path)

    def test_every_module_shape_file_is_listed(self):
        # A module that gains a shapes.ttl must join the gate (Pi round 1 suggestion). The core 1.0.0
        # slice (release/shapes.ttl) is part of core 2.1.0's shapes; the scoped-sequence shapes run in
        # their own build check.
        import glob
        found = {os.path.relpath(p, ONTOLOGY) for p in glob.glob(os.path.join(ONTOLOGY, "*", "shapes.ttl"))}
        self.assertEqual(found - set(SHAPE_FILES), {"release/shapes.ttl"})

    def test_the_whole_graph_conforms(self):
        ok, text = report(GRAPH)
        self.assertTrue(ok, text[:3000])

    def test_a_cross_module_break_fails(self):
        # A value-stream process that produces something the data-product module does not define.
        g = Graph()
        g += GRAPH
        g.add((URIRef(str(VS) + "process/deal-negotiation-capture"), VS.produces,
               URIRef("https://w3id.org/lsc/ontology/modules/data-product/product/no-such-product")))
        self.assertFalse(report(g)[0])


if __name__ == "__main__":
    unittest.main()
