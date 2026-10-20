"""Tests for the system module (Step 7; EPM-DEC-001-0055): the register covers every string in
the process map, the merges and splits are the ones recorded, the build is current, the links
match the map, and SHACL accepts the module and rejects broken systems.

Run: python3 -m pytest test_systems.py (needs rdflib, pyshacl).
"""
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal
from rdflib.namespace import RDF, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_systems as bs  # noqa: E402

SYS, KIND, SYSTEM, PROC = bs.SYS, bs.KIND, bs.SYSTEM, bs.PROC
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
SYSTEMS = Graph().parse(os.path.join(HERE, "systems.ttl"))


def conforms(data):
    return validate(data + VOCAB, shacl_graph=SHAPES, advanced=True)[0]


class Build(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_systems.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_figures(self):
        # Pinned on 2026-10-19. The string, system and kind counts were checked by hand against
        # register.csv and systems.csv; the link count is the build's, over 153 processes.
        self.assertEqual(bs.figures(*bs.load()), {
            "map strings": 37, "systems": 32, "application": 23, "office-tool": 4, "document": 5,
            "no-system strings": 4, "processes naming a system": 153, "links": 285,
            "links waiting for a core release": 0})

    def test_spelling_merge(self):
        self.assertIn((SYSTEM["rightangle"], SKOS.altLabel, Literal("Right Angle", lang="en")), SYSTEMS)
        self.assertEqual(len(set(SYSTEMS.subjects(SKOS.prefLabel, Literal("RightAngle", lang="en")))), 1)

    def test_split(self):
        # CM 1.1.5.1.2.3 names "PI" and "SAP/ Hyperion".
        process = PROC["CM-1-1-5-1-2-3"]
        self.assertEqual(set(SYSTEMS.subjects(SYS.supports, process)), {SYSTEM["pi"], SYSTEM["sap"], SYSTEM["hyperion"]})

    def test_manual_is_not_a_system(self):
        # CM 1.1.2.2.3.4 names "MPR" and "Manual".
        self.assertEqual(set(SYSTEMS.subjects(SYS.supports, PROC["CM-1-1-2-2-3-4"])), {SYSTEM["mpr"]})
        labels = {str(o) for o in SYSTEMS.objects(None, SKOS.prefLabel)}
        for text in ("Manual", "TBD", "To be incorporated in regional Premise solution"):
            self.assertNotIn(text, labels)

    def test_kinds(self):
        self.assertEqual(SYSTEMS.value(SYSTEM["ms-outlook"], SYS.systemKind), KIND["office-tool"])
        self.assertEqual(SYSTEMS.value(SYSTEM["refinery-premise-document"], SYS.systemKind), KIND["document"])
        self.assertEqual(SYSTEMS.value(SYSTEM["xpims"], SYS.systemKind), KIND["application"])

    def test_profisee_links(self):
        self.assertEqual(set(SYSTEMS.objects(SYSTEM["profisee"], SYS.supports)),
                         {PROC["CM-1-1-2-1"], PROC["CM-1-1-2-1-8"], PROC["CM-1-1-2-2"]})


class Shapes(unittest.TestCase):
    def test_module_conforms(self):
        self.assertTrue(conforms(SYSTEMS))

    def broken(self, edit):
        g = Graph()
        for t in SYSTEMS:
            g.add(t)
        edit(g)
        return conforms(g)

    def test_rejects_an_invented_definition(self):
        self.assertFalse(self.broken(lambda g: g.add((SYSTEM["xpims"], SKOS.definition, Literal("A planning tool.", lang="en")))))

    def test_rejects_two_kinds(self):
        self.assertFalse(self.broken(lambda g: g.add((SYSTEM["xpims"], SYS.systemKind, KIND["document"]))))

    def test_rejects_a_kind_off_the_list(self):
        def edit(g):
            g.remove((SYSTEM["xpims"], SYS.systemKind, None))
            g.add((SYSTEM["xpims"], SYS.systemKind, KIND["manual"]))
        self.assertFalse(self.broken(edit))

    def test_rejects_a_system_without_its_note(self):
        self.assertFalse(self.broken(lambda g: g.remove((SYSTEM["dpo"], SKOS.editorialNote, None))))


if __name__ == "__main__":
    unittest.main()
