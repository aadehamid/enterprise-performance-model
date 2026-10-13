"""Tests for the ref-mpc module (Step 5, slice 4; EPM-DEC-001-0033): every reference instance
cites a source and an as-of date, the facts match the FY2025 10-K as recorded in the fact sheet,
MPC's control of MPLX is a control relationship and not a sub-organization, and the module
defines no terms of its own.

Run: python3 -m pytest test_ref_mpc.py (needs rdflib, pyshacl).
"""
import os
import unittest
from decimal import Decimal

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ORGANIZATION = os.path.join(HERE, "..", "organization")
REF = Namespace("https://w3id.org/lsc/ontology/modules/ref-mpc/")
ORGM = Namespace("https://w3id.org/lsc/ontology/modules/organization/")
ORG = Namespace("http://www.w3.org/ns/org#")
SRC = Namespace("https://w3id.org/lsc/ontology/source/")

MODULE = Graph().parse(os.path.join(HERE, "ref-mpc.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
SHAPES += Graph().parse(os.path.join(ORGANIZATION, "shapes.ttl"))
VOCAB = Graph().parse(os.path.join(ORGANIZATION, "vocabulary.ttl"))
AS_OF = Literal("2025-12-31", datatype=XSD.date)


def conforms(g):
    data = Graph()
    data += VOCAB
    data += g
    return validate(data, shacl_graph=SHAPES)


class Facts(unittest.TestCase):
    def test_the_module_conforms(self):
        ok, _, text = conforms(MODULE)
        self.assertTrue(ok, text)

    def test_three_reportable_segments_of_mpc(self):
        # 10-K: "Our operations consist of three reportable operating segments: Refining &
        # Marketing, Midstream and Renewable Diesel."
        units = {str(MODULE.value(u, SKOS.prefLabel)) for u in MODULE.subjects(ORG.unitOf, REF.mpc)}
        self.assertEqual(units, {"Refining & Marketing", "Midstream", "Renewable Diesel"})

    def test_thirteen_refineries_of_mpc(self):
        self.assertEqual(len(set(MODULE.subjects(ORG.siteOf, REF.mpc))), 13)

    def test_mpc_controls_mplx_through_a_control_relationship(self):
        c = REF["mpc-controls-mplx"]
        self.assertEqual(MODULE.value(c, ORGM.controllingEntity), REF.mpc)
        self.assertEqual(MODULE.value(c, ORGM.controlledEntity), REF.mplx)
        self.assertEqual(MODULE.value(c, ORGM.ownershipShare).toPython(), Decimal("0.64"))
        self.assertEqual(MODULE.value(c, ORGM.asOf), AS_OF)
        self.assertEqual(MODULE.value(c, DCTERMS.source), SRC["mpc-s01"])
        self.assertIn("approximately 64 percent", str(MODULE.value(c, SKOS.note)))

    def test_mpc_and_mplx_carry_their_gleif_leis(self):
        # GLEIF API, queried 2026-10-13 (EPM-DEC-001-0023: GLEIF is mapped at Step 5).
        self.assertEqual(str(MODULE.value(REF.mpc, ORG.identifier)), "3BNYRYQHD39K4LCKQF12")
        self.assertEqual(str(MODULE.value(REF.mplx, ORG.identifier)), "5493000CZJ19CK4P3G36")
        for s in (REF.mpc, REF.mplx):
            self.assertIn((s, DCTERMS.source, SRC["gleif-lei"]), MODULE)

    def test_mplx_is_not_a_unit_of_mpc(self):
        self.assertNotIn((REF.mplx, ORG.subOrganizationOf, REF.mpc), MODULE)
        self.assertNotIn((REF.mplx, ORG.unitOf, REF.mpc), MODULE)

    def test_every_instance_holds_as_of_the_fiscal_year_end(self):
        for kind in (ORG.FormalOrganization, ORG.OrganizationalUnit, ORG.Site):
            for s in MODULE.subjects(RDF.type, kind):
                self.assertEqual(MODULE.value(s, DCTERMS.date), AS_OF, s)

    def test_the_module_defines_no_terms(self):
        # Company-neutral modules own the vocabulary; ref-mpc only uses it (EPM-DEC-001-0015).
        for kind in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, RDF.Property):
            self.assertEqual(list(MODULE.subjects(RDF.type, kind)), [], kind)
        self.assertEqual(list(MODULE.subjects(RDFS.domain, None)), [])


class BrokenInstancesFail(unittest.TestCase):
    def broken(self, change):
        g = Graph()
        g += MODULE
        change(g)
        return conforms(g)[0]

    def test_an_instance_without_a_source_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((REF["refinery-kenai"], DCTERMS.source, None))))

    def test_an_instance_without_a_date_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((REF.mplx, DCTERMS.date, None))))

    def test_a_source_without_an_issue_date_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((SRC["mpc-s01"], DCTERMS.issued, None))))

    def test_a_segment_without_its_company_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((REF["segment-midstream"], ORG.unitOf, None))))

    def test_a_control_relationship_without_a_date_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((REF["mpc-controls-mplx"], ORGM.asOf, None))))

    def test_a_second_name_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((REF.mpc, SKOS.prefLabel, Literal("Marathon", lang="en")))))


if __name__ == "__main__":
    unittest.main()
