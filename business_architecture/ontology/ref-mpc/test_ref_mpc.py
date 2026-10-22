"""Tests for the ref-mpc module (Step 5, slice 4; EPM-DEC-001-0033): every reference instance
cites a source and an as-of date, the facts match the FY2025 10-K as recorded in the fact sheet,
MPC's control of MPLX is a control relationship and not a sub-organization, and the module
defines no terms of its own; and MPC and MPLX described in the party module's terms, moved here
from party/ (EPM-DEC-001-0075).

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

    def test_the_module_meets_the_core_source_shape(self):
        # Core requires every dcterms:source target to be a titled bibliographic resource. A source
        # node gives its URL as a citation, as core's own source nodes do (EPM-DEC-001-0033).
        core_shapes = Graph().parse(os.path.join(HERE, "..", "releases", "core", "1.0.0", "shapes.ttl"))
        ok, _, text = validate(MODULE, shacl_graph=core_shapes)
        self.assertTrue(ok, text)
        # The reference parties cite MPLX's 10-K, src:mplx-s01, which meets the same shape (Pi on #341).
        parties = Graph().parse(os.path.join(HERE, "reference-parties.ttl"))
        ok, _, text = validate(parties, shacl_graph=core_shapes)
        self.assertTrue(ok, text)
        self.assertIsNotNone(parties.value(SRC["mplx-s01"], DCTERMS.title))

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


PARTY = os.path.join(HERE, "..", "party")
CUST = Namespace("https://w3id.org/lsc/ontology/modules/party/")


class RealParties(unittest.TestCase):
    """MPC and MPLX in the party module's terms: section VII's done-when with real organisations, as
    the decision owner chose (EPM-DEC-001-0071), kept in this reference module since EPM-DEC-001-0075."""
    G = Graph()
    for n in ("vocabulary.ttl", "code-lists.ttl"):
        G.parse(os.path.join(PARTY, n))
    PARTIES = Graph().parse(os.path.join(HERE, "reference-parties.ttl"))
    G += PARTIES
    EXPECTED = {"mpc": {"throughput-holder", "payer"}, "mplx": {"carrier", "vendor"}}

    def test_party_to_roles(self):
        for party, roles in self.EXPECTED.items():
            found = {str(self.G.value(r, CUST.roleType)).rsplit("/", 1)[1] for r in self.G.objects(REF[party], CUST.plays)}
            self.assertEqual(found, roles, party)

    def test_role_to_party(self):
        for party in self.EXPECTED:
            for r in self.G.objects(REF[party], CUST.plays):
                self.assertEqual(set(self.G.subjects(CUST.plays, r)), {REF[party]}, r)

    def test_every_role_cites_the_mplx_filing(self):
        filing = SRC["mplx-s01"]
        self.assertEqual(str(self.G.value(filing, DCTERMS.identifier)), "0001552000-26-000009")
        for party in self.EXPECTED:
            for r in self.G.objects(REF[party], CUST.plays):
                self.assertEqual(set(self.G.objects(r, DCTERMS.source)), {filing}, r)

    def test_each_role_holds_from_the_first_agreements(self):
        # MPLX's FY2025 Form 10-K, exhibit index: the Omnibus Agreement (10.1) and the first Transportation
        # Services Agreement (10.2) are "dated as of October 31, 2012" (EPM-DEC-001-0071).
        for party in self.EXPECTED:
            for r in self.G.objects(REF[party], CUST.plays):
                self.assertEqual(str(self.G.value(r, CUST.validFrom)), "2012-10-31", r)
                self.assertIsNone(self.G.value(r, CUST.validTo), r)

    def test_every_node_described_here_is_in_this_modules_namespace_or_a_source(self):
        # EPM-DEC-001-0075: the roles and the agreement moved from the party namespace to ref-mpc's.
        for s in set(self.PARTIES.subjects()):
            self.assertTrue(str(s).startswith(str(REF)) or str(s).startswith(str(SRC)), s)
        described = set(self.PARTIES.subjects())
        for local in ("mpc-throughput-holder", "mpc-payer", "mplx-carrier", "mplx-vendor", "mplx-mpc-services"):
            self.assertIn(REF["party/" + local], described, local)

    def test_the_file_left_the_party_module(self):
        self.assertFalse(os.path.exists(os.path.join(PARTY, "reference-parties.ttl")))

    def test_they_conform_to_the_party_shapes(self):
        ok, _, text = validate(self.G, shacl_graph=Graph().parse(os.path.join(PARTY, "shapes.ttl")))
        self.assertTrue(ok, text[:3000])


if __name__ == "__main__":
    unittest.main()
