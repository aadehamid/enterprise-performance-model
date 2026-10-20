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
from rdflib import Graph, URIRef

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_lanes as bl  # noqa: E402

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

    def test_rejects_a_lane_off_the_list(self):
        g = Graph()
        for t in LANES:
            g.add(t)
        g.add((PROC["CM-1-3-1"], LANE.officeLane, URIRef(str(LANEV) + "shared-services")))
        self.assertFalse(conforms(g))


if __name__ == "__main__":
    unittest.main()
