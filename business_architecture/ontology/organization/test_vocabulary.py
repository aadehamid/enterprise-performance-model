"""Tests for the organization vocabulary and shapes (Step 5; EPM-DEC-001-0030): one kind,
one range, a label and a definition per property; a stated cardinality on every property;
and SHACL that accepts a valid assignment and control relationship and rejects broken ones.

Run: python3 -m pytest test_vocabulary.py (needs rdflib, pyshacl).
"""
import os
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ORGM = Namespace("https://w3id.org/lsc/ontology/modules/organization/")
RACI = Namespace("https://w3id.org/lsc/ontology/modules/organization/raci-level/")
ORG = Namespace("http://www.w3.org/ns/org#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("https://example.org/")
SHP = Namespace("https://w3id.org/lsc/ontology/modules/organization/shapes/")

VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
KINDS = (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
TYPED = {p for k in KINDS for p in VOCAB.subjects(RDF.type, k)}
# A property is anything typed as one, or anything with a declared domain or range, so an
# untyped predicate cannot slip past the kind and cardinality checks.
PROPS = TYPED | set(VOCAB.subjects(RDFS.domain, None)) | set(VOCAB.subjects(RDFS.range, None))
EXACTLY_ONE = {  # EPM-DEC-001-0030: these paths carry exactly one value on their shape
    ORGM.forProcess, ORGM.assignedRole, ORGM.raciLevel, ORGM.sourceRoleText,
    ORGM.controllingEntity, ORGM.controlledEntity, ORGM.asOf, SKOS.prefLabel}
LEVELS = {RACI.responsible, RACI.accountable, RACI.consulted, RACI.informed}


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

    def test_an_untyped_property_is_caught(self):
        g = Graph()
        g += VOCAB
        g.remove((ORGM.forProcess, RDF.type, OWL.ObjectProperty))
        props = {p for k in KINDS for p in g.subjects(RDF.type, k)} | set(g.subjects(RDFS.range, None))
        self.assertIn(ORGM.forProcess, props)
        self.assertEqual(len([k for k in KINDS if (ORGM.forProcess, RDF.type, k) in g]), 0)

    def test_each_property_states_a_cardinality(self):
        stated = {SHAPES.value(n, SH.path) for n in SHAPES.subjects(SH.path, None)
                  if (n, SH.minCount, None) in SHAPES or (n, SH.maxCount, None) in SHAPES}
        self.assertEqual(sorted(map(str, PROPS - stated)), [])

    def test_exactly_one_paths_have_both_bounds(self):
        for n in SHAPES.subjects(SH.path, None):
            path = SHAPES.value(n, SH.path)
            if path in EXACTLY_ONE:
                with self.subTest(path=str(path)):
                    self.assertEqual(int(SHAPES.value(n, SH.minCount)), 1)
                    self.assertEqual(int(SHAPES.value(n, SH.maxCount)), 1)

    def test_both_shapes_require_a_source(self):
        for shape in (SHP.Assignment, SHP.Control):
            mins = [SHAPES.value(n, SH.minCount) for n in SHAPES.objects(shape, SH.property)
                    if SHAPES.value(n, SH.path) == DCTERMS.source]
            self.assertEqual([int(m) for m in mins], [1], str(shape))

    def test_the_raci_list_has_exactly_four_levels(self):
        members = set(VOCAB.subjects(SKOS.inScheme, ORGM.RaciLevel))
        self.assertEqual(members, LEVELS)
        self.assertEqual(sorted(str(VOCAB.value(m, SKOS.notation)) for m in members), ["A", "C", "I", "R"])

    def test_the_shape_allows_exactly_the_four_levels(self):
        node = [n for n in SHAPES.objects(SHP.Assignment, SH.property)
                if SHAPES.value(n, SH.path) == ORGM.raciLevel][0]
        self.assertEqual(set(Collection(SHAPES, SHAPES.value(node, SH["in"]))), LEVELS)


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

    def test_two_processes_fail(self):
        self.assertFalse(self.broken(lambda g: (g.add((EX.other, RDF.type, SKOS.Concept)),
                                                g.add((EX.assignment, ORGM.forProcess, EX.other)))))

    def test_two_roles_fail(self):
        def change(g):
            g.add((EX.role2, RDF.type, ORG.Role))
            g.add((EX.role2, SKOS.prefLabel, Literal("Planner", lang="en")))
            g.add((EX.assignment, ORGM.assignedRole, EX.role2))
        self.assertFalse(self.broken(change))

    def test_two_source_texts_fail(self):
        self.assertFalse(self.broken(lambda g: g.add((EX.assignment, ORGM.sourceRoleText,
                                                      Literal("Scheduler", datatype=XSD.string)))))

    def test_a_control_relationship_without_a_source_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((EX.control, DCTERMS.source, None))))

    def test_a_control_relationship_without_a_date_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((EX.control, ORGM.asOf, None))))

    def test_a_share_above_one_fails(self):
        def change(g):
            g.remove((EX.control, ORGM.ownershipShare, None))
            g.add((EX.control, ORGM.ownershipShare, Literal("64", datatype=XSD.decimal)))
        self.assertFalse(self.broken(change))


if __name__ == "__main__":
    unittest.main()
