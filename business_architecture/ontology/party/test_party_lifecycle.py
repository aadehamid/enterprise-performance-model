"""Tests for the customer lifecycle (EPM-DEC-001-0070): the two lifecycles, their links to core
processes and customer systems, and how they correspond. Expected values are written out by hand.

Run: python3 -m pytest test_party_lifecycle.py (needs rdflib, pyshacl).
"""
import os
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_party  # noqa: E402
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
            # CM 1.3.7.1.7 since 2026-10-23 (MPC-P10.1, EPM-DEC-001-0087, 0092).
            "onboarding": {"CM-1-3-7-4-6", "CM-1-3-7-4-2", "CM-1-3-7-1-1", "CM-1-3-7-2-1", "CM-1-3-7-1-7"},
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

    def conforms(self, extra="", remove=()):
        g = parse("vocabulary.ttl", "code-lists.ttl", "systems.ttl", "lifecycle.ttl", extra=extra)
        for triple in remove:
            g.remove(triple)
        ok, _, text = validate(g, shacl_graph=self.SHAPES, advanced=True)
        return ok, text

    def violates(self, focus, message, extra="", remove=()):
        """The graph fails, and one result is a violation on this focus node with this message."""
        g = parse("vocabulary.ttl", "code-lists.ttl", "systems.ttl", "lifecycle.ttl", extra=extra)
        for triple in remove:
            g.remove(triple)
        ok, results, _ = validate(g, shacl_graph=self.SHAPES, advanced=True)
        self.assertFalse(ok)
        found = {(r.focus, str(r.message)) for r in results.query(
            "PREFIX sh: <http://www.w3.org/ns/shacl#> SELECT ?focus ?message WHERE { "
            "?r a sh:ValidationResult ; sh:focusNode ?focus ; sh:resultMessage ?message ; sh:resultSeverity sh:Violation }")}
        self.assertIn((focus, message), found)

    def test_the_lifecycle_conforms(self):
        ok, text = self.conforms()
        self.assertTrue(ok, text[:3000])

    def test_a_system_stage_done_by_a_process(self):
        self.violates(CUST["system-stage/master"], "Only a business lifecycle stage is done by processes.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/system-stage/master> party:stageProcess "
                            "<https://w3id.org/lsc/ontology/process/CM-1-3-7-1-1> .")

    def test_a_business_stage_held_by_a_system(self):
        self.violates(CUST["lifecycle-stage/onboarding"], "Only a system stage is held by systems.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/onboarding> party:stageSystem "
                            "<https://w3id.org/lsc/ontology/modules/party/system/sap-mdg> .")

    def test_a_system_stage_that_corresponds(self):
        self.violates(CUST["system-stage/master"], "Only a business lifecycle stage corresponds to a system stage.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/system-stage/master> party:correspondsTo "
                            "<https://w3id.org/lsc/ontology/modules/party/system-stage/record> .")

    def test_a_correspondence_to_a_business_stage(self):
        self.violates(CUST["lifecycle-stage/offboarding"], "A business lifecycle stage corresponds only to a system stage.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/offboarding> party:correspondsTo "
                            "<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/prospect> .")

    # EPM-DEC-001-0070 decides each stage's links: a real target on the wrong stage fails, and so does a missing one.
    def test_a_real_system_on_the_wrong_stage(self):
        master = CUST["system-stage/master"]
        self.violates(master, "system-stage/master has exactly the systems EPM-DEC-001-0070 decides.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/system-stage/master> party:stageSystem "
                            "<https://w3id.org/lsc/ontology/modules/party/system/salesforce> .",
                      remove=[(master, CUST.stageSystem, CUST["system/sap-mdg"])])

    def test_a_real_process_on_the_wrong_stage(self):
        prospect = CUST["lifecycle-stage/prospect"]
        self.violates(prospect, "lifecycle-stage/prospect has exactly the processes EPM-DEC-001-0070 decides.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/prospect> party:stageProcess "
                            "<https://w3id.org/lsc/ontology/process/CM-1-3-8-2-1> .",
                      remove=[(prospect, CUST.stageProcess, PROC["CM-1-3-6-2-1"])])

    def test_a_correspondence_the_record_does_not_grant(self):
        self.violates(CUST["lifecycle-stage/offboarding"],
                      "lifecycle-stage/offboarding corresponds to no system stage (EPM-DEC-001-0070, item 4).",
                      extra="<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/offboarding> party:correspondsTo "
                            "<https://w3id.org/lsc/ontology/modules/party/system-stage/settle> .")

    def test_a_process_that_does_not_exist(self):
        self.violates(CUST["lifecycle-stage/risk-management"],
                      "lifecycle-stage/risk-management has exactly the processes EPM-DEC-001-0070 decides.",
                      extra="<https://w3id.org/lsc/ontology/modules/party/lifecycle-stage/risk-management> party:stageProcess "
                            "<https://w3id.org/lsc/ontology/process/DOES-NOT-EXIST> .")


class Build(unittest.TestCase):
    """The build rejects a link from the wrong kind of stage before lifecycle.ttl exists."""

    def fails(self, extra_row=None, drop=None):
        real = build_party.read

        def read(name):
            rows = real(name)
            if name != "lifecycle.csv":
                return rows
            return [r for r in rows if (r["stage"], r["link"], r["target"]) != drop] + ([extra_row] if extra_row else [])
        build_party.read = read
        try:
            rows = build_party.load()
            with self.assertRaises(SystemExit) as caught:
                build_party.load_lifecycle(rows, build_party.load_systems(rows)[0])
        finally:
            build_party.read = real
        return str(caught.exception)

    def test_a_system_stage_with_a_process(self):
        row = {"stage": "system-stage/master", "link": "process", "target": "CM 1.3.7.1.1", "note": "x"}
        self.assertIn("only a lifecycle-stage has a process link", self.fails(row))

    def test_a_business_stage_with_a_system(self):
        row = {"stage": "lifecycle-stage/onboarding", "link": "system", "target": "sap-mdg", "note": "x"}
        self.assertIn("only a system-stage has a system link", self.fails(row))

    def test_a_system_stage_that_corresponds(self):
        row = {"stage": "system-stage/master", "link": "stage", "target": "system-stage/record", "note": "x"}
        self.assertIn("only a lifecycle-stage has a stage link", self.fails(row))

    def test_a_real_system_on_the_wrong_stage(self):
        row = {"stage": "system-stage/master", "link": "system", "target": "salesforce", "note": ""}
        self.assertIn("system-stage/master system links ['salesforce'], not the decided ['sap-mdg']",
                      self.fails(row, drop=("system-stage/master", "system", "sap-mdg")))

    def test_a_real_process_on_the_wrong_stage(self):
        row = {"stage": "lifecycle-stage/prospect", "link": "process", "target": "CM 1.3.8.2.1", "note": "x"}
        self.assertIn("lifecycle-stage/prospect process links ['CM 1.3.6.6.1', 'CM 1.3.7.4.2', 'CM 1.3.8.2.1'], "
                      "not the decided ['CM 1.3.6.2.1', 'CM 1.3.6.6.1', 'CM 1.3.7.4.2']",
                      self.fails(row, drop=("lifecycle-stage/prospect", "process", "CM 1.3.6.2.1")))

    def test_a_correspondence_the_record_does_not_grant(self):
        row = {"stage": "lifecycle-stage/offboarding", "link": "stage", "target": "system-stage/settle", "note": ""}
        self.assertIn("lifecycle-stage/offboarding stage links ['system-stage/settle'], not the decided []", self.fails(row))

    def test_a_stage_with_every_link_removed(self):
        # The shapes do not target a stage with no lifecycle link, so the build must reject it.
        self.assertIn("system-stage/master has no link", self.fails(drop=("system-stage/master", "system", "sap-mdg")))


if __name__ == "__main__":
    unittest.main()
