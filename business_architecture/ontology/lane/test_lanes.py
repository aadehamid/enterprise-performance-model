"""Tests for the lane module (Step 7; EPM-DEC-001-0056): the build is current, each placement
matches the process map, nothing is inherited, and SHACL accepts the module and rejects a
process in two lanes or a lane off the list.

Run: python3 -m pytest test_lanes.py (needs rdflib, pyshacl).
"""
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_lanes as bl  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "release"))
import build_module as bm  # noqa: E402  (release mode, and where a released package sits in either layout)


def released(tc, module, version, fname):
    """A file of a released package, in either layout. In the share release a package that did not ship skips the
    test; on main every package is on disk, so a missing one fails."""
    folder = bm.package_folder(module, version)
    if folder is None and bm.SHARE_RELEASE:
        tc.skipTest(f"{module} {version} did not ship (the share release holds the newest and previous packages only)")
    tc.assertIsNotNone(folder, f"{module} {version} is not on disk under releases/")
    return os.path.join(folder, fname)

LANE, LANEV, PROC = bl.LANE, bl.LANEV, bl.PROC
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
LANES = Graph().parse(os.path.join(HERE, "lanes.ttl"))


def conforms(data):
    return validate(data + VOCAB, shacl_graph=SHAPES, advanced=True)[0]


class Build(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_lanes.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_placements(self):
        # Pinned by hand from the process map: the seven nodes with an officeLane.
        self.assertEqual({(str(s)[len(str(PROC)):], str(o)[len(str(LANEV)):]) for s, o in LANES.subject_objects(LANE.officeLane)}, {
            ("CM-1-2-1", "front-office"), ("CM-1-2-2", "middle-office"), ("CM-1-2-3", "operations"),
            ("CM-1-2-4", "back-office"), ("CM-1-2-5", "operations"), ("CM-1-2-6", "operations"),
            ("CM-1-2-7", "operations")})

    def test_every_lane_is_a_top_concept_both_ways(self):
        # A flat code list states each member as a top concept, both ways (EPM-DEC-001-0098, item 5; 0106).
        lanes = {LANEV[k] for k in ("front-office", "middle-office", "back-office", "operations")}
        self.assertEqual(len(set(LANES.subjects(SKOS.inScheme, LANE.OfficeLanes))), 4)  # counted by hand
        self.assertEqual(set(LANES.subjects(SKOS.inScheme, LANE.OfficeLanes)), lanes)
        self.assertEqual(set(LANES.subjects(SKOS.topConceptOf, LANE.OfficeLanes)), lanes)
        self.assertEqual(set(LANES.objects(LANE.OfficeLanes, SKOS.hasTopConcept)), lanes)

    def test_no_message_holds_an_apostrophe(self):
        # n10s writes sh:message into Cypher unescaped, so a single quote breaks its validator (ontology skill,
        # SHACL rule 19; EPM-DEC-001-0106).
        self.assertEqual([str(m) for m in SHAPES.objects(None, URIRef("http://www.w3.org/ns/shacl#message")) if "'" in str(m)], [])

    def test_no_iri_changed_since_1_0_0(self):
        # A minor release removes no IRI: every subject of the 1.0.0 package, the ontology header aside, is still a
        # subject of 1.1.0, and nothing is newly deprecated (EPM-DEC-001-0106).
        releases = os.path.join(HERE, "..", "releases", "lane")
        header = URIRef("https://w3id.org/lsc/ontology/modules/lane")
        old = Graph().parse(released(self, "lane", "1.0.0", "lane.ttl"))
        new = Graph().parse(released(self, "lane", "1.1.0", "lane.ttl"))
        self.assertEqual({s for s in old.subjects() if s != header} - set(new.subjects()), set())
        deprecated = URIRef("http://www.w3.org/2002/07/owl#deprecated")
        self.assertEqual(set(new.subjects(deprecated, None)), set(old.subjects(deprecated, None)))

    def test_nothing_is_inherited(self):
        self.assertIsNone(LANES.value(PROC["CM-1-2-1-3"], LANE.officeLane))


class Shapes(unittest.TestCase):
    def test_module_conforms(self):
        self.assertTrue(conforms(LANES))

    def test_rejects_two_lanes(self):
        g = Graph()
        for t in LANES:
            g.add(t)
        g.add((PROC["CM-1-2-1"], LANE.officeLane, LANEV["back-office"]))
        self.assertFalse(conforms(g))

    def test_leaves_other_concepts_alone(self):
        # The lane shapes target lanes only: a concept of another scheme needs no notation here.
        g = Graph()
        for t in LANES:
            g.add(t)
        g.add((URIRef("https://example.org/other"), URIRef("http://www.w3.org/2004/02/skos/core#inScheme"), URIRef("https://example.org/scheme")))
        self.assertTrue(conforms(g))

    def test_rejects_a_lane_off_the_list(self):
        g = Graph()
        for t in LANES:
            g.add(t)
        fifth = URIRef(str(LANEV) + "shared-services")
        g.add((PROC["CM-1-3-1"], LANE.officeLane, fifth))
        self.assertFalse(conforms(g))
        # Typed and fully described, but not one of the four: still rejected (Pi round 1).
        for p, o in ((RDF.type, LANE.OfficeLane), (SKOS.prefLabel, Literal("Shared Services", lang="en")),
                     (SKOS.notation, Literal("shared_services", datatype=XSD.string)),
                     (SKOS.definition, Literal("Not one of the four.", lang="en")),
                     (SKOS.inScheme, URIRef("https://example.org/other-scheme"))):
            g.add((fifth, p, o))
        self.assertFalse(conforms(g))


if __name__ == "__main__":
    unittest.main()
