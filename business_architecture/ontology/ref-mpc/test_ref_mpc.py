"""Tests for the ref-mpc module (Step 5, slice 4; EPM-DEC-001-0033): every reference instance
cites a source and an as-of date, the facts match the FY2025 10-K as recorded in the fact sheet,
MPC's control of MPLX is a control relationship and not a sub-organization, and the module
defines no terms of its own; and MPC and MPLX described in the party module's terms, moved here
from party/ (EPM-DEC-001-0075).

Run: python3 -m pytest test_ref_mpc.py (needs rdflib, pyshacl).
"""
import os
import sys
import unittest
from decimal import Decimal

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
ORGANIZATION = os.path.join(HERE, "..", "organization")
sys.path.insert(0, os.path.join(HERE, "..", "release"))
import build_module as bm  # noqa: E402  (release mode, and where a released package sits in either layout)


def core_shapes_graph():
    """Core 1.0.0's shapes, which hold the source shape (EPM-DEC-001-0033). In the share release, which holds the
    newest and previous core only, the newest core's shapes carry the same shape; on main 1.0.0 is always on disk."""
    folder = bm.package_folder("core", "1.0.0")
    if folder is None and bm.SHARE_RELEASE:
        folder = os.path.join(bm.ONTOLOGY, "releases", "core", bm.newest_on_disk("core"))
    return Graph().parse(os.path.join(folder, "shapes.ttl"))

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
        core_shapes = core_shapes_graph()
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


class Brands(unittest.TestCase):
    """MPC's brands as party:Brand individuals: the decision owner confirmed on 2026-10-27 that Marathon, ARCO and
    Tesoro can be brand values (EPM-DEC-001-0108, amendment of 2026-10-27). Expected values are written by hand."""
    BRANDS = Graph().parse(os.path.join(HERE, "reference-brands.ttl"))
    BRAND = Namespace("https://w3id.org/lsc/ontology/modules/ref-mpc/brand/")
    EXPECTED = {"marathon": "Marathon", "arco": "ARCO", "tesoro": "Tesoro"}

    def test_three_brands_with_their_labels(self):
        found = {s: str(self.BRANDS.value(s, SKOS.prefLabel)) for s in self.BRANDS.subjects(RDF.type, CUST.Brand)}
        self.assertEqual(found, {self.BRAND[k]: v for k, v in self.EXPECTED.items()})

    def test_each_brand_is_in_this_modules_namespace(self):
        for s in self.BRANDS.subjects(RDF.type, CUST.Brand):
            self.assertTrue(str(s).startswith("https://w3id.org/lsc/ontology/modules/ref-mpc/brand/"), s)

    def test_each_brand_cites_the_customer_inputs_and_the_10k_and_holds_as_of_the_answer(self):
        sources = {SRC["decision-owner-customer-inputs-2026-10-27"], SRC["mpc-s01"]}
        for k in self.EXPECTED:
            self.assertEqual(set(self.BRANDS.objects(self.BRAND[k], DCTERMS.source)), sources, k)
            self.assertEqual(self.BRANDS.value(self.BRAND[k], DCTERMS.date), Literal("2026-10-27", datatype=XSD.date), k)
            self.assertEqual(self.BRANDS.value(self.BRAND[k], SKOS.definition).language, "en", k)

    def test_the_brands_conform_and_a_brand_without_a_definition_fails(self):
        ok, _, text = validate(self.BRANDS, shacl_graph=SHAPES)
        self.assertTrue(ok, text)
        g = Graph()
        g += self.BRANDS
        g.remove((self.BRAND.tesoro, SKOS.definition, None))
        self.assertFalse(validate(g, shacl_graph=SHAPES)[0])

    def test_the_brands_meet_the_core_source_shape(self):
        core_shapes = core_shapes_graph()
        ok, _, text = validate(self.BRANDS, shacl_graph=core_shapes)
        self.assertTrue(ok, text)

    def test_the_brands_are_released_in_ref_mpc_1_3_0(self):
        released = Graph().parse(os.path.join(HERE, "..", "releases", "ref-mpc", "1.3.0", "ref-mpc.ttl"))
        for k, label in self.EXPECTED.items():
            self.assertIn((self.BRAND[k], RDF.type, CUST.Brand), released, k)
            self.assertIn((self.BRAND[k], SKOS.prefLabel, Literal(label, lang="en")), released, k)

    def test_the_brands_are_not_in_the_party_module(self):
        for n in ("vocabulary.ttl", "code-lists.ttl", "systems.ttl", "lifecycle.ttl"):
            g = Graph().parse(os.path.join(PARTY, n))
            self.assertEqual(list(g.subjects(RDF.type, CUST.Brand)), [], n)


if __name__ == "__main__":
    unittest.main()
