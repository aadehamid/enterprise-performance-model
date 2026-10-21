"""Tests for the customer lifecycle (EPM-DEC-001-0070): the two lifecycles, their links to core
processes and customer systems, and how they correspond. Expected values are written out by hand.

Run: python3 -m pytest test_party_lifecycle.py (needs rdflib, pyshacl).
"""
import os
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
CUST = Namespace("https://w3id.org/lsc/ontology/modules/party/")
PROC = Namespace("https://w3id.org/lsc/ontology/process/")


def parse(*names, extra=""):
    g = Graph()
    for n in names:
        g.parse(os.path.join(HERE, n))
    if extra:
        g.parse(data="@prefix party: <https://w3id.org/lsc/ontology/modules/party/> .\n" + extra, format="turtle")
    return g


G = parse("vocabulary.ttl", "code-lists.ttl", "systems.ttl", "lifecycle.ttl")


def tail(iri):
    return str(iri).rsplit("/", 1)[1]


class Lifecycle(unittest.TestCase):
    def test_the_two_lifecycles(self):
        def stages(scheme):
            return {tail(v) for v in G.subjects(SKOS.inScheme, CUST[scheme])}
        self.assertEqual(stages("lifecycle-stage"), {"prospect", "onboarding", "payment-management", "risk-management",
                                                     "relationship-management", "offboarding"})
        self.assertEqual(stages("system-stage"), {"prospect", "master", "record", "execute", "settle"})

    def test_each_stage_and_its_processes(self):
        expected = {
            "prospect": {"CM-1-3-6-2-1", "CM-1-3-6-6-1", "CM-1-3-7-4-2"},
            "onboarding": {"CM-1-3-7-4-6", "CM-1-3-7-4-2", "CM-1-3-7-1-1", "CM-1-3-7-2-1"},
            "payment-management": {"CM-1-3-8-2-1", "CM-1-3-8-2-3", "CM-1-3-8-3-2"},
            "risk-management": {"CM-1-3-7-4-3", "CM-1-3-7-4-4"},
            "relationship-management": {"CM-1-3-6-2-2", "CM-1-3-7-5-5", "CM-1-3-7-2-6", "CM-1-3-7-4-2"},
            "offboarding": {"CM-1-3-7-4-5", "CM-1-3-7-1-1"},
        }
        for stage, procs in expected.items():
            found = {tail(p) for p in G.objects(CUST[f"lifecycle-stage/{stage}"], CUST.stageProcess)}
            self.assertEqual(found, procs, stage)

    def test_each_system_stage_and_its_systems(self):
        expected = {"prospect": {"salesforce"}, "master": {"sap-mdg"}, "record": {"sap-s4hana"},
                    "execute": {"rightangle", "polaris", "dealer-master", "terminal-download"},
                    "settle": {"sap-s4hana"}}
        for stage, systems in expected.items():
            found = {tail(s) for s in G.objects(CUST[f"system-stage/{stage}"], CUST.stageSystem)}
            self.assertEqual(found, systems, stage)

    def test_the_correspondences(self):
        found = {(tail(a), tail(b)) for a, b in G.subject_objects(CUST.correspondsTo)}
        self.assertEqual(found, {("prospect", "prospect"), ("onboarding", "master"), ("onboarding", "record"),
                                 ("payment-management", "settle")})


class Shapes(unittest.TestCase):
    SHAPES = parse("shapes.ttl")

    def conforms(self, extra=""):
        ok, _, text = validate(parse("vocabulary.ttl", "code-lists.ttl", "systems.ttl", "lifecycle.ttl", extra=extra),
                               shacl_graph=self.SHAPES, advanced=True)
        return ok, text

    def test_the_lifecycle_conforms(self):
        ok, text = self.conforms()
        self.assertTrue(ok, text[:3000])

    def test_a_system_stage_done_by_a_process(self):
        ok, text = self.conforms("<https://w3id.org/lsc/ontology/modules/party/system-stage/master> party:stageProcess "
                                 "<https://w3id.org/lsc/ontology/process/CM-1-3-7-1-1> .")
        self.assertFalse(ok)
        self.assertIn("Only a business lifecycle stage", text)

    def test_a_business_stage_held_by_a_system(self):
        ok, text = self.conforms("<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/onboarding> party:stageSystem "
                                 "<https://w3id.org/lsc/ontology/modules/party/system/sap-mdg> .")
        self.assertFalse(ok)
        self.assertIn("Only a system stage", text)


if __name__ == "__main__":
    unittest.main()
