"""Tests for core 2.1.0 (EPM-DEC-001-0044): it is core 2.0.0 plus the Step 9 additions the decision owner approved,
each canonical fact has exactly one evidence node that matches the mapping, the shapes catch each
kind of drift, and the package is the approved, current release.

Run: python3 -m pytest test_build_core_2_1.py (needs rdflib, pyshacl).
"""
import json
import os
import re
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, SKOS

import build_core_2_1 as b

ROWS = b.mapping()
PREDS = b.predicates(ROWS)
G, COUNTS = b.build(ROWS)
BASE = Graph().parse(os.path.join(b.BASE, "core.ttl"))
# The fact shapes alone, so each drift test validates in seconds; build_core_2_1.py --verify runs
# the full release shapes on the release graph.
FACT_SHAPES = Graph().parse(data=b.fact_shapes(PREDS), format="turtle")
S, P, O, IDS = ROWS[0]
F = b.fact_iri(S, P, O)


# The part of the graph the fact shapes read: the fact nodes, the direct triples and the concept types.
SUB = Graph()
_FACTS = set(G.subjects(RDF.type, b.CORE.CanonicalFact))
for t in G:
    if t[0] in _FACTS or t[1] in PREDS or t[1:] == (RDF.type, SKOS.Concept):
        SUB.add(t)


def copy():
    g = Graph()
    g += SUB
    return g


def fact_shapes_hold(g):
    return validate(g, shacl_graph=FACT_SHAPES, advanced=True)[0]


class Release(unittest.TestCase):
    def test_every_2_0_0_triple_is_kept_except_the_header_and_the_licence(self):
        header = {(b.ONTOLOGY_IRI, p, o) for p, o in BASE.predicate_objects(b.ONTOLOGY_IRI)
                  if p in (OWL.versionInfo, OWL.versionIRI, b.DCTERMS.issued, b.DCTERMS.modified, OWL.priorVersion,
                           b.DCTERMS.license)}
        self.assertEqual(set(BASE) - set(G) - header, set())
        self.assertIsNone(G.value(b.ONTOLOGY_IRI, b.DCTERMS.license))
        rights = str(G.value(b.ONTOLOGY_IRI, b.DCTERMS.rights))
        self.assertIn("All rights reserved", rights)
        self.assertIn("APQC and IBM", rights)

    def test_the_figures(self):
        # Pinned from the 2026-10-18 build; they match the Step 9 walkthrough (640 facts, 812 rows, 172).
        self.assertEqual(dict(COUNTS), {
            "canonical facts": 640, "evidence rows": 812, "facts with two or more rows": 172,
            "facts assuredBy": 5, "facts constrainedBy": 11, "facts dependsOnOutputOf": 190, "facts enabledBy": 93,
            "facts governedBy": 35, "facts informedBy": 99, "facts precedes": 182, "facts requires": 5,
            "facts triggeredBy": 20})
        self.assertEqual(len(PREDS), 9)

    def test_one_node_per_fact_with_the_mappings_rows(self):
        self.assertEqual(b.evidence_problems(G, ROWS), [])
        self.assertEqual(len(set(G.subjects(RDF.type, b.CORE.CanonicalFact))), len(ROWS))
        self.assertEqual({str(i) for i in G.objects(F, b.CORE.evidenceRow)}, set(IDS))

    def test_the_new_property_is_not_source_row(self):
        self.assertEqual(list(G.objects(F, b.CORE.sourceRow)), [])
        self.assertEqual(G.value(b.CORE.evidenceRow, b.RDFS.domain), b.CORE.CanonicalFact)


class Drift(unittest.TestCase):
    """The decision owner's checks: each kind of drift between the triple, the node and the mapping fails."""

    def test_the_release_passes_the_fact_shapes(self):
        self.assertTrue(fact_shapes_hold(SUB))

    def test_a_triple_without_a_node_fails(self):
        g = copy()
        g.remove((F, None, None))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_second_node_for_one_triple_fails(self):
        g = copy()
        twin = URIRef(str(F) + "-twin")
        for p, o in G.predicate_objects(F):
            g.add((twin, p, o))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_node_without_its_triple_fails(self):
        g = copy()
        g.remove((S, P, O))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_node_with_two_subjects_fails(self):
        g = copy()
        g.add((F, b.CORE.factSubject, O))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_predicate_outside_the_nine_fails(self):
        g = copy()
        g.set((F, b.CORE.factPredicate, SKOS.broader))
        g.add((S, SKOS.broader, O))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_node_with_no_row_fails(self):
        g = copy()
        g.remove((F, b.CORE.evidenceRow, None))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_malformed_row_fails(self):
        g = copy()
        g.add((F, b.CORE.evidenceRow, Literal("REL-1")))
        self.assertFalse(fact_shapes_hold(g))

    def test_a_well_formed_row_on_the_wrong_fact_fails_the_mapping_check(self):
        # The shapes cannot know which row supports which fact; the mapping check does.
        g = copy()
        other = next(i for _, _, _, ids in ROWS[1:] for i in ids)
        g.remove((F, b.CORE.evidenceRow, None))
        g.add((F, b.CORE.evidenceRow, Literal(other)))
        self.assertTrue(fact_shapes_hold(g))
        self.assertTrue(b.evidence_problems(g, ROWS))

    def test_a_missing_row_fails_the_mapping_check(self):
        multi = next((s, p, o, ids) for s, p, o, ids in ROWS if len(ids) > 1)
        g = Graph()
        g += G
        g.remove((b.fact_iri(*multi[:3]), b.CORE.evidenceRow, Literal(multi[3][0])))
        self.assertTrue(b.evidence_problems(g, ROWS))

    def test_a_mapping_that_differs_from_the_triples_stops_the_build(self):
        with self.assertRaises(SystemExit):
            b.build(ROWS[1:])

    def test_the_build_is_reproducible(self):
        again, _ = b.build(ROWS)
        self.assertEqual(again.serialize(format="nt").splitlines().__len__(), len(G))
        self.assertEqual(set(again), set(G))


class ControlledValues(unittest.TestCase):
    def test_the_release_shapes_hold_the_eleven_controlled_value_shapes(self):
        controlled = Graph().parse(b.CONTROLLED)
        release = b.shapes(PREDS)
        for shape in controlled.subjects(RDF.type, b.prev.SH.NodeShape):
            with self.subTest(shape=str(shape)):
                self.assertEqual(release.value(shape, b.prev.SH.targetObjectsOf),
                                 controlled.value(shape, b.prev.SH.targetObjectsOf))
        self.assertEqual(len(set(controlled.subjects(RDF.type, b.prev.SH.NodeShape))), 11)

    def test_no_max_count_on_in_scheme(self):
        release = b.shapes(PREDS)
        for node in release.subjects(b.prev.SH.path, SKOS.inScheme):
            self.assertIsNone(release.value(node, b.prev.SH.maxCount), node)


class Package(unittest.TestCase):
    def test_the_package_is_the_approved_release(self):
        self.assertEqual(b.APPROVAL, ("step4/review-evidence/decision-owner-answers/answers-2026-10-18-night.md",
                                      "Yes, cut 2.1.0 (Recommended)"))
        with open(os.path.join(b.ONTOLOGY, b.APPROVAL[0])) as f:
            body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
        self.assertIn(b.APPROVAL[1], body)
        self.assertEqual(str(G.value(b.ONTOLOGY_IRI, OWL.versionInfo)), "2.1.0")
        self.assertEqual(G.value(b.ONTOLOGY_IRI, OWL.priorVersion), URIRef(f"{b.ONTOLOGY_IRI}/2.0.0"))
        with open(os.path.join(b.RELEASE_DIR, "manifest.json")) as f:
            manifest = json.load(f)
        self.assertFalse(manifest["release_candidate"])
        self.assertEqual(manifest["approval"], {"file": b.APPROVAL[0], "words": b.APPROVAL[1]})

    def test_the_mapping_travels_with_the_release(self):
        with open(os.path.join(b.RELEASE_DIR, "canonical-facts.csv")) as f, open(b.MAPPING) as g:
            self.assertEqual(f.read(), g.read())
        self.assertEqual(len(b.mapping(os.path.join(b.RELEASE_DIR, "canonical-facts.csv"))), 640)

    def test_the_package_is_current(self):
        files = b.package(G, PREDS, COUNTS)
        for name, text in files.items():
            with open(os.path.join(b.RELEASE_DIR, name)) as f:
                self.assertEqual(f.read(), text, name)


if __name__ == "__main__":
    unittest.main()
