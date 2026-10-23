"""Tests for the Step 9 controlled-value shapes (EPM-DEC-001-0014, EPM-DEC-001-0035, EPM-DEC-001-0044):
the core release (2.2.0, which carries these shapes in its release shapes, as 2.1.0 did) and the organization module
conform, a value from the wrong list fails, and every code-list property of core has a shape.

Run: python3 -m pytest test_controlled_values.py (needs rdflib, pyshacl).
"""
import os
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
SHAPES = Graph().parse(os.path.join(HERE, "controlled-values.ttl"))
CORE = Namespace("https://w3id.org/lsc/ontology/modules/core/")
ORGM = Namespace("https://w3id.org/lsc/ontology/modules/organization/")
SH = Namespace("http://www.w3.org/ns/shacl#")

DATA = Graph()
RELEASE = os.path.join(ONTOLOGY, "releases", "core", "2.3.0")
DATA.parse(os.path.join(RELEASE, "core.ttl"))
DATA.parse(os.path.join(ONTOLOGY, "organization", "vocabulary.ttl"))
DATA.parse(os.path.join(ONTOLOGY, "organization", "assignments.ttl"))
CODED = [SHAPES.value(s, SH.targetObjectsOf) for s in SHAPES.subjects(RDF.type, SH.NodeShape)]
RELEASE_SHAPES = Graph().parse(os.path.join(RELEASE, "shapes.ttl"))


def membership_targets(shapes):
    """Properties whose values a shape checks for membership of a named list (skos:inScheme, sh:hasValue)."""
    out = set()
    for shape in shapes.subjects(RDF.type, SH.NodeShape):
        target = shapes.value(shape, SH.targetObjectsOf)
        for prop in shapes.objects(shape, SH.property):
            if shapes.value(prop, SH.path) == SKOS.inScheme and shapes.value(prop, SH.hasValue) is not None:
                out.add(target)
    return out


def conforms(g):
    return validate(g, shacl_graph=SHAPES)


def wrong_list(prop):
    """Point one use of prop at a concept from a different code list; return the mutated graph."""
    g = Graph()
    g += DATA
    s, o = next(iter(g.subject_objects(prop)), (URIRef("https://example.org/p"), None))
    scheme = DATA.value(o, SKOS.inScheme) if o is not None else None
    other = next(c for c, sch in DATA.subject_objects(SKOS.inScheme)
                 if sch != scheme and sch in {DATA.value(v, SKOS.inScheme) for v in DATA.objects(None, CORE.conceptKind)})
    if o is not None:
        g.remove((s, prop, o))
    g.add((s, prop, other))
    return g


class ControlledValues(unittest.TestCase):
    def test_the_core_release_conforms(self):
        ok, _, text = conforms(DATA)
        self.assertTrue(ok, text)

    def test_every_code_list_property_of_core_has_a_shape(self):
        # Every core property whose values sit in a core code list is covered. The process
        # scheme itself is not a code list: process-to-process relations are not coded values.
        schemes = set(DATA.subjects(RDF.type, SKOS.ConceptScheme)) - {URIRef("https://w3id.org/lsc/ontology/modules/core")}
        used = {p for s, p, o in DATA if str(p).startswith(str(CORE)) and DATA.value(o, SKOS.inScheme) in schemes}
        self.assertEqual(sorted(map(str, used - set(CODED))), [str(CORE.businessDomain)])
        # core:businessDomain has no shape here: the release shapes check it (shp:BusinessDomainValue,
        # added in core 2.0.0). Every coded property is covered by one or the other.
        self.assertEqual(sorted(map(str, used - membership_targets(RELEASE_SHAPES))), [])

    def test_the_release_shapes_carry_every_controlled_value_shape(self):
        self.assertTrue(set(CODED) <= membership_targets(RELEASE_SHAPES))

    def test_each_shape_names_the_list_its_property_uses(self):
        # Where the property has values, they sit in the scheme the shape names. Where it has none
        # yet (governance status), the property and the scheme carry the same label in their
        # vocabularies.
        vocab = Graph()
        vocab.parse(os.path.join(ONTOLOGY, "release", "core-vocabulary.ttl"))
        vocab.parse(os.path.join(ONTOLOGY, "organization", "vocabulary.ttl"))
        for shape in SHAPES.subjects(RDF.type, SH.NodeShape):
            prop = SHAPES.value(shape, SH.targetObjectsOf)
            named = SHAPES.value(SHAPES.value(shape, SH.property), SH.hasValue)
            with self.subTest(property=str(prop)):
                self.assertIn((named, RDF.type, SKOS.ConceptScheme), DATA)
                used = set(DATA.objects(None, prop))
                if used:
                    self.assertEqual({DATA.value(v, SKOS.inScheme) for v in used}, {named})
                else:
                    self.assertEqual(str(vocab.value(prop, RDFS.label)).lower(), str(vocab.value(named, RDFS.label)).lower())

    def test_a_value_from_the_wrong_list_fails(self):
        for prop in CODED:
            if prop == CORE.conceptKind:
                continue
            with self.subTest(property=str(prop)):
                self.assertFalse(conforms(wrong_list(prop))[0])

    def test_a_concept_kind_from_the_wrong_list_fails(self):
        g = Graph()
        g += DATA
        s, o = next(iter(g.subject_objects(CORE.conceptKind)))
        g.remove((s, CORE.conceptKind, o))
        g.add((s, CORE.conceptKind, next(DATA.subjects(SKOS.inScheme, CORE.Cadence))))
        self.assertFalse(conforms(g)[0])


if __name__ == "__main__":
    unittest.main()
