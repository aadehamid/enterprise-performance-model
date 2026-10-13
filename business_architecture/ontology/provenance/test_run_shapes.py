"""Tests for the definition-to-run pattern (Step 6; EPM-DEC-001-0034): no core definition is a
run, the example run conforms, and broken runs fail.

Run: python3 -m pytest test_run_shapes.py (needs rdflib, pyshacl).
"""
import os
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, PROV, RDF, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = Graph().parse(os.path.join(HERE, "..", "releases", "core", "1.0.0", "core.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "run-shapes.ttl"))
EXAMPLE = Graph().parse(os.path.join(HERE, "example-run.ttl"))
EX = Namespace("https://example.org/consumer/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")
CORE_NS = Namespace("https://w3id.org/lsc/ontology/modules/core/")
KIND = Namespace("https://w3id.org/lsc/ontology/modules/core/concept-kind/")
RUN, ASSOCIATION = EX["run-2026-10-01-001"], EX["run-2026-10-01-001-association"]


def conforms(*graphs):
    data = Graph()
    for g in graphs:
        data += g
    return validate(data, shacl_graph=SHAPES)[0]


def with_example(change):
    g = Graph()
    g += EXAMPLE
    change(g)
    return conforms(CORE, g)


class Definitions(unittest.TestCase):
    def test_the_core_release_holds_no_runs(self):
        self.assertEqual(list(CORE.subjects(RDF.type, PROV.Activity)), [])
        self.assertTrue(conforms(CORE))

    def test_a_definition_typed_as_a_run_fails(self):
        g = Graph()
        g.add((PROC["CM-1-1-2-1"], RDF.type, PROV.Activity))
        self.assertFalse(conforms(CORE, g))


class Runs(unittest.TestCase):
    def test_the_example_run_conforms(self):
        self.assertTrue(conforms(CORE, EXAMPLE))

    def test_a_run_without_a_definition_fails(self):
        self.assertFalse(with_example(lambda g: g.remove((ASSOCIATION, PROV.hadPlan, None))))

    def test_a_run_following_two_definitions_fails(self):
        self.assertFalse(with_example(lambda g: g.add((ASSOCIATION, PROV.hadPlan, PROC["CM-1-1-2"]))))

    def test_a_run_following_something_outside_the_scheme_fails(self):
        def change(g):
            g.set((ASSOCIATION, PROV.hadPlan, URIRef("https://example.org/not-a-process")))
        self.assertFalse(with_example(change))

    def test_a_run_following_a_retired_definition_fails(self):
        retired = next(CORE.subjects(OWL.deprecated, Literal(True)))
        self.assertFalse(with_example(lambda g: g.set((ASSOCIATION, PROV.hadPlan, retired))))

    def test_a_run_following_a_structural_anchor_fails(self):
        anchor = next(CORE.subjects(CORE_NS.conceptKind, KIND["structural-anchor"]))
        self.assertFalse(with_example(lambda g: g.set((ASSOCIATION, PROV.hadPlan, anchor))))

    def test_a_run_without_a_start_fails(self):
        self.assertFalse(with_example(lambda g: g.remove((RUN, PROV.startedAtTime, None))))

    def test_a_run_with_two_associations_fails(self):
        def change(g):
            g.add((RUN, PROV.qualifiedAssociation, EX.second))
            g.add((EX.second, PROV.hadPlan, PROC["CM-1-1-2"]))
        self.assertFalse(with_example(change))

    def test_a_start_that_is_not_a_timestamp_fails(self):
        self.assertFalse(with_example(lambda g: g.set((RUN, PROV.startedAtTime, Literal("2026-10-01", datatype=XSD.date)))))


if __name__ == "__main__":
    unittest.main()
