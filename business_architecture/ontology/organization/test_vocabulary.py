"""Tests for the organization vocabulary and shapes (Step 5; EPM-DEC-001-0030): one kind,
one range, a label and a definition per property; a stated cardinality on every property;
and SHACL that accepts a valid assignment and control relationship and rejects broken ones.

Run: python3 -m pytest test_vocabulary.py (needs rdflib, pyshacl).
"""
import os
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ORGM = Namespace("https://w3id.org/lsc/ontology/modules/organization/")
RACI = Namespace("https://w3id.org/lsc/ontology/modules/organization/raci-level/")
ORG = Namespace("http://www.w3.org/ns/org#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("https://example.org/")

VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
KINDS = (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
PROPS = {p for k in KINDS for p in VOCAB.subjects(RDF.type, k)}


def valid_graph():
    g = Graph()
    g += VOCAB
    g.add((EX.process, RDF.type, SKOS.Concept))
    g.add((EX.role, RDF.type, ORG.Role))
    g.add((EX.role, SKOS.prefLabel, Literal("Refinery Scheduler", lang="en")))
    a = EX.assignment
    g.add((a, RDF.type, ORGM.ResponsibilityAssignment))
    g.add((a, ORGM.forProcess, EX.process))
    g.add((a, ORGM.assignedRole, EX.role))
    g.add((a, ORGM.raciLevel, RACI.accountable))
    g.add((a, ORGM.sourceRoleText, Literal("Refinery scheduler", datatype=XSD.string)))
    g.add((a, DCTERMS.source, EX.processMap))
    for e in (EX.parent, EX.child):
        g.add((e, RDF.type, ORG.FormalOrganization))
    c = EX.control
    g.add((c, RDF.type, ORGM.ControlRelationship))
    g.add((c, ORGM.controllingEntity, EX.parent))
    g.add((c, ORGM.controlledEntity, EX.child))
    g.add((c, ORGM.ownershipShare, Literal("0.64", datatype=XSD.decimal)))
    g.add((c, ORGM.asOf, Literal("2025-12-31", datatype=XSD.date)))
    g.add((c, DCTERMS.source, EX.filing))
    return g


def conforms(g):
    return validate(g, shacl_graph=SHAPES, advanced=True)[0]


class Vocabulary(unittest.TestCase):
    def test_each_property_has_one_kind_one_range_a_label_and_a_definition(self):
        self.assertTrue(PROPS)
        for p in PROPS:
            with self.subTest(property=str(p)):
                self.assertEqual(len([k for k in KINDS if (p, RDF.type, k) in VOCAB]), 1)
                self.assertEqual(len(list(VOCAB.objects(p, RDFS.range))), 1)
                self.assertIsNotNone(VOCAB.value(p, RDFS.label))
                self.assertIsNotNone(VOCAB.value(p, SKOS.definition))

    def test_each_property_states_a_cardinality(self):
        stated = {SHAPES.value(n, SH.path) for n in SHAPES.subjects(SH.path, None)
                  if (n, SH.minCount, None) in SHAPES or (n, SH.maxCount, None) in SHAPES}
        self.assertEqual(sorted(map(str, PROPS - stated)), [])

    def test_the_raci_list_has_four_levels(self):
        self.assertEqual(sorted(str(n) for n in VOCAB.objects(None, SKOS.notation)), ["A", "C", "I", "R"])


class Shapes(unittest.TestCase):
    def test_a_valid_graph_conforms(self):
        self.assertTrue(conforms(valid_graph()))

    def broken(self, change):
        g = valid_graph()
        change(g)
        return conforms(g)

    def test_an_assignment_without_a_level_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((EX.assignment, ORGM.raciLevel, None))))

    def test_an_assignment_with_two_levels_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((EX.assignment, ORGM.raciLevel, RACI.informed))))

    def test_an_assignment_without_a_source_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((EX.assignment, DCTERMS.source, None))))

    def test_an_assignment_to_a_non_role_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((EX.role, RDF.type, ORG.Role))))

    def test_a_role_with_two_names_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((EX.role, SKOS.prefLabel, Literal("Scheduler", lang="en")))))

    def test_a_control_relationship_without_a_date_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((EX.control, ORGM.asOf, None))))

    def test_a_share_above_one_fails(self):
        def change(g):
            g.remove((EX.control, ORGM.ownershipShare, None))
            g.add((EX.control, ORGM.ownershipShare, Literal("64", datatype=XSD.decimal)))
        self.assertFalse(self.broken(change))


if __name__ == "__main__":
    unittest.main()
