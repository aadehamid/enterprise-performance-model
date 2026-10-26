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
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

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
        # register.csv and systems.csv. The link count is the build's; 3 of the 153 processes with a
        # systems field name only Manual, TBD or a plan, so 150 receive a link.
        self.assertEqual(bs.figures(*bs.load()), {
            "map strings": 37, "systems": 34, "defined": 18, "application": 25, "office-tool": 4, "document": 5,
            "no-system strings": 4, "processes with a systems field": 153,
            "processes with a link": 150, "links": 285,
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


    def test_definitions(self):
        # Item G (EPM-DEC-001-0099), checked by hand against definitions.csv on 2026-10-25: 15 systems are
        # defined; full forms are preferred labels, with the process map's abbreviation as an alternative.
        defined = {s for s in SYSTEMS.subjects(SKOS.definition, None)}
        self.assertEqual(len(defined), 18)  # 15, then MIPS, MPR and Databricks in 1.2.0 (EPM-DEC-001-0100)
        for slug, label, alt in (("dpo", "Distribution Planning Optimizer", "DPO"), ("aps", "Aspen Petroleum Scheduler", "APS"),
                                 ("sap", "SAP S/4HANA", "SAP"), ("hyperion", "Oracle Hyperion Planning", "Hyperion"),
                                 ("pi", "AVEVA PI System", "PI")):
            self.assertEqual(SYSTEMS.value(SYSTEM[slug], SKOS.prefLabel), Literal(label, lang="en"))
            self.assertIn((SYSTEM[slug], SKOS.altLabel, Literal(alt, lang="en")), SYSTEMS)
        self.assertEqual(set(SYSTEMS.objects(SYSTEM["ms-excel"], DCTERMS.source)),
                         {bs.MAP_SOURCE, bs.SRC["vendor-microsoft-excel"]})
        self.assertIn((bs.SRC["vendor-microsoft-excel"], RDF.type, DCTERMS.BibliographicResource), SYSTEMS)
        self.assertIsNone(SYSTEMS.value(SYSTEM["ms-excel"], SKOS.editorialNote))
        # Hyperion is defined, and keeps a note saying its identification was a guess the owner accepted.
        self.assertIn("a guess", str(SYSTEMS.value(SYSTEM["hyperion"], SKOS.editorialNote)))
        # TopDay and VALT are MPC-built and still undefined.
        for slug in ("topday", "valt"):
            self.assertIsNone(SYSTEMS.value(SYSTEM[slug], SKOS.definition))
            self.assertTrue(str(SYSTEMS.value(SYSTEM[slug], SKOS.editorialNote)).startswith("MPC-built"))
        self.assertEqual(str(SYSTEMS.value(SYSTEM["trr"], SKOS.editorialNote)), bs.UNDEFINED)

    def test_systems_the_map_does_not_name(self):
        # Item F (EPM-DEC-001-0100): MIPS and Databricks, named by the decision owner's pricing assets.
        assets = bs.SRC["decision-owner-pricing-assets-2026-10-25"]
        for slug in ("mips", "databricks"):
            self.assertIn((SYSTEM[slug], DCTERMS.source, assets), SYSTEMS)
            self.assertNotIn((SYSTEM[slug], DCTERMS.source, bs.MAP_SOURCE), SYSTEMS)
            self.assertIsNone(SYSTEMS.value(SYSTEM[slug], SYS.supports))
        self.assertIn((SYSTEM["mips"], SKOS.altLabel, Literal("Market Information and Pricing System", lang="en")), SYSTEMS)
        self.assertIn("Master Price Record", str(SYSTEMS.value(SYSTEM["mpr"], SKOS.editorialNote)))

    def test_the_map_source_is_not_redeclared(self):
        # roles.ttl declares the process map's source node; this module only references it (Pi round 1).
        self.assertIsNone(SYSTEMS.value(bs.MAP_SOURCE, URIRef("http://purl.org/dc/terms/title")))


class Shapes(unittest.TestCase):
    def test_module_conforms(self):
        self.assertTrue(conforms(SYSTEMS))

    def broken(self, edit):
        g = Graph()
        for t in SYSTEMS:
            g.add(t)
        edit(g)
        return conforms(g)

    def test_rejects_a_definition_without_its_source(self):
        # TRR cites only the process map, which names systems but does not define them.
        self.assertFalse(self.broken(lambda g: g.add((SYSTEM["trr"], SKOS.definition, Literal("A planning tool.", lang="en")))))

    def test_rejects_a_defined_system_that_loses_the_process_map_source(self):
        # Kimi round 1, finding 20: two other sources must not stand in for the process map.
        def edit(g):
            g.remove((SYSTEM["xpims"], DCTERMS.source, bs.MAP_SOURCE))
        self.assertFalse(self.broken(edit))

    def test_rejects_a_defined_system_that_loses_its_source(self):
        self.assertFalse(self.broken(lambda g: g.remove((SYSTEM["ms-excel"], DCTERMS.source, bs.SRC["vendor-microsoft-excel"]))))

    def test_rejects_two_kinds(self):
        self.assertFalse(self.broken(lambda g: g.add((SYSTEM["xpims"], SYS.systemKind, KIND["document"]))))

    def test_rejects_a_kind_off_the_list(self):
        def edit(g):
            g.remove((SYSTEM["xpims"], SYS.systemKind, None))
            g.add((SYSTEM["xpims"], SYS.systemKind, KIND["manual"]))
        self.assertFalse(self.broken(edit))

    def test_rejects_an_undefined_system_another_source_names(self):
        self.assertFalse(self.broken(lambda g: g.remove((SYSTEM["mips"], SKOS.definition, None))))

    def test_rejects_a_system_without_its_note(self):
        self.assertFalse(self.broken(lambda g: g.remove((SYSTEM["trr"], SKOS.editorialNote, None))))


if __name__ == "__main__":
    unittest.main()
