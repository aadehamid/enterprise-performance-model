"""Tests for the customer module (Steps 5 to 7; EPM-DEC-001-0067, EPM-DEC-001-0068): the build is
current, the code lists hold the decided values, the vocabulary holds the fifteen entities of the
decision owner's conceptual model, the five example organizations read both ways, and SHACL accepts
the examples and rejects each kind of break. Expected values are written out by hand.

Run: python3 -m pytest test_customer.py (needs rdflib, pyshacl).
"""
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
CUST = Namespace("https://w3id.org/lsc/ontology/modules/customer/")
EX = Namespace("https://w3id.org/lsc/ontology/modules/customer/example/")
ROLE = Namespace("https://w3id.org/lsc/ontology/modules/customer/party-role/")
CLS = Namespace("https://w3id.org/lsc/ontology/modules/customer/customer-class/")
AGT = Namespace("https://w3id.org/lsc/ontology/modules/customer/agreement-type/")


def parse(*names):
    g = Graph()
    for n in names:
        g.parse(os.path.join(HERE, n))
    return g


VOCAB = parse("vocabulary.ttl")
CODES = parse("code-lists.ttl")
SCHEMA = parse("vocabulary.ttl", "code-lists.ttl")
SHAPES = parse("shapes.ttl")


def data(extra=""):
    g = parse("vocabulary.ttl", "code-lists.ttl", "examples.ttl")
    if extra:
        g.parse(data="@prefix cust: <https://w3id.org/lsc/ontology/modules/customer/> .\n"
                     "@prefix ex: <https://w3id.org/lsc/ontology/modules/customer/example/> .\n"
                     "@prefix role: <https://w3id.org/lsc/ontology/modules/customer/party-role/> .\n"
                     "@prefix cls: <https://w3id.org/lsc/ontology/modules/customer/customer-class/> .\n"
                     "@prefix pt: <https://w3id.org/lsc/ontology/modules/customer/party-type/> .\n"
                     "@prefix agt: <https://w3id.org/lsc/ontology/modules/customer/agreement-type/> .\n"
                     "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                     "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" + extra, format="turtle")
    return g


def conforms(g):
    ok, _, text = validate(g, shacl_graph=SHAPES, advanced=True)
    return ok, text


def notations(scheme):
    return {str(n) for v in CODES.subjects(SKOS.inScheme, CUST[scheme]) for n in CODES.objects(v, SKOS.notation)}


class Build(unittest.TestCase):
    def test_code_lists_are_current(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        r = subprocess.run([sys.executable, "build_customer.py", "--verify"], cwd=HERE, env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class CodeLists(unittest.TestCase):
    def test_party_roles_are_the_twelve_plus_the_two_added(self):
        self.assertEqual(notations("party-role"), {
            "sold-to", "payer", "bill-to", "consignee", "jobber", "dealer", "exchange-counterparty",
            "throughput-holder", "carrier", "vendor", "surety", "supplier",
            "position-holder", "loading-authorized-party"})

    def test_relationship_and_agreement_types(self):
        self.assertEqual(notations("relationship-type"),
                         {"parent-of", "guarantor-of", "supplies", "credit-roll-up", "contact-for"})
        self.assertEqual(notations("agreement-type"), {
            "fuel-supply", "exchange-buy-sell", "throughput-storage", "brand-license",
            "consignment-commission", "fleet-card-program", "offtake"})

    def test_lines_of_business_keep_sdp_as_a_label(self):
        self.assertEqual(notations("line-of-business"), {
            "brand", "unbranded", "asphalt", "petrochemicals", "sdp", "renewable-fuels", "cardlock",
            "producers", "pipeline-ls", "misc"})
        sdp = CUST["line-of-business/sdp"]
        self.assertEqual(CODES.value(sdp, SKOS.prefLabel), Literal("SDP", lang="en"))
        self.assertIn((sdp, RDF.type, CUST.LineOfBusiness), CODES)

    def test_the_classes_by_group(self):
        def members(group):
            return {str(v).rsplit("/", 1)[1] for v in CODES.subjects(SKOS.broader, CLS[group])}
        self.assertEqual(members("brand-attached-resellers"), {"branded-jobber", "direct-dealer"})
        self.assertEqual(members("wholesale-unbranded"), {"wholesale-marketing", "independent-retailer", "unbranded-customer",
                                                          "export-customer", "terminal-rack-customer", "forecast-driven-customer"})
        self.assertEqual(members("end-users-specialty"), {"commercial-industrial-end-user", "asphalt-bitumen-buyer",
                                                          "pipeline-customer"})
        self.assertEqual(members("trading-counterparties"), {"exchange-trading-counterparty", "crude-oil-customer",
                                                             "spot-market-buyer"})

    def test_fourteen_classes_in_four_groups(self):
        groups = {"brand-attached-resellers", "wholesale-unbranded", "end-users-specialty", "trading-counterparties"}
        self.assertEqual(len(notations("customer-class")), 18)
        for g in groups:
            self.assertIn((CUST[f"customer-class/{g}"], SKOS.topConceptOf, CUST["customer-class"]), CODES)
        classes = {v for v in CODES.subjects(SKOS.inScheme, CUST["customer-class"]) if CODES.value(v, SKOS.broader)}
        self.assertEqual(len(classes), 14)

    def test_each_mpc_class_lands_on_the_decided_class(self):
        expected = {"branded-jobber": "C1", "direct-dealer": "C2", "wholesale-marketing": "C3",
                    "independent-retailer": "C4", "unbranded-customer": "C5", "spot-market-buyer": "C6",
                    "export-customer": "C7", "crude-oil-customer": "C8"}
        found = {str(v).rsplit("/", 1)[1]: str(c) for v, c in CODES.subject_objects(CUST.mpcClassification)}
        self.assertEqual(found, expected)

    def test_the_four_added_classes_sit_in_the_decided_groups(self):
        self.assertEqual(CODES.value(CLS["independent-retailer"], SKOS.broader), CLS["wholesale-unbranded"])
        self.assertEqual(CODES.value(CLS["unbranded-customer"], SKOS.broader), CLS["wholesale-unbranded"])
        self.assertEqual(CODES.value(CLS["spot-market-buyer"], SKOS.broader), CLS["trading-counterparties"])
        self.assertEqual(CODES.value(CLS["crude-oil-customer"], SKOS.broader), CLS["trading-counterparties"])

    def test_direct_dealers_sit_under_fuel_supply(self):
        # EPM-DEC-001-0067, What follows, item 1: a supply agreement, not a brand licence.
        text = str(CODES.value(CLS["direct-dealer"], SKOS.definition))
        self.assertIn("Fuel Supply agreement", text)
        self.assertNotIn("Brand License", text)

    def test_exchange_counterparty_stays_a_class(self):
        self.assertEqual(CODES.value(CLS["exchange-trading-counterparty"], SKOS.broader), CLS["trading-counterparties"])

    def test_site_lists(self):
        self.assertEqual(notations("operating-model"), {"coco", "codo", "dodo"})
        self.assertEqual(notations("site-type"), {"station", "bulk-plant", "cardlock", "terminal",
                                                  "airport-location", "pipeline-delivery-point"})


class Vocabulary(unittest.TestCase):
    ENTITIES = ["Party", "ExternalIdentifier", "Address", "ContactPoint", "PartyRole", "PartyRelationship",
                "CustomerAccount", "CustomerClass", "LineOfBusiness", "Brand", "Agreement", "SiteBrandAssignment",
                "PartyTransactionAssociation", "Product", "Site"]

    def test_the_fifteen_entities_are_classes(self):
        for name in self.ENTITIES:
            self.assertIn((CUST[name], RDF.type, URIRef("http://www.w3.org/2002/07/owl#Class")), VOCAB, name)

    def test_every_term_has_a_definition_and_a_citation(self):
        for term in set(VOCAB.subjects(RDFS.label, None)):
            self.assertIsNotNone(VOCAB.value(term, SKOS.definition), term)
            self.assertIsNotNone(VOCAB.value(term, URIRef("http://purl.org/dc/terms/bibliographicCitation")), term)

    def test_only_person_and_organization_are_kinds_of_party(self):
        self.assertEqual(set(VOCAB.subjects(RDFS.subClassOf, CUST.Party)), {CUST.Person, CUST.Organization})
        self.assertNotIn((CUST.Customer, None, None), VOCAB)

    def test_the_relationships_the_decision_owner_settled(self):
        self.assertEqual(VOCAB.value(CUST.scopedToProduct, RDFS.domain), CUST.Agreement)
        self.assertEqual(VOCAB.value(CUST.suppliedFrom, RDFS.domain), CUST.CustomerAccount)
        self.assertEqual(VOCAB.value(CUST.suppliedFrom, RDFS.range), CUST.Site)
        self.assertEqual(VOCAB.value(CUST.authorizesBrandAtSite, RDFS.range), CUST.SiteBrandAssignment)


class BothWays(unittest.TestCase):
    """Section VII's done-when: each organization, party to roles and role to party."""
    G = data()
    EXPECTED = {
        "jobber-co": {"jobber", "sold-to", "payer", "bill-to"},
        "trader-co": {"sold-to", "supplier", "exchange-counterparty"},
        "shipper-co": {"throughput-holder", "payer"},
        "rack-co": {"sold-to", "position-holder", "loading-authorized-party"},
        "carrier-co": {"carrier", "vendor", "surety"},
    }

    def roles_of(self, party):
        return {str(self.G.value(r, CUST.roleType)).rsplit("/", 1)[1] for r in self.G.objects(EX[party], CUST.plays)}

    def test_party_to_roles(self):
        for party, roles in self.EXPECTED.items():
            self.assertEqual(self.roles_of(party), roles, party)

    def test_role_to_party(self):
        for party in self.EXPECTED:
            for r in self.G.objects(EX[party], CUST.plays):
                self.assertEqual(set(self.G.subjects(CUST.plays, r)), {EX[party]}, r)

    def test_each_organization_holds_several_roles(self):
        for party in self.EXPECTED:
            self.assertGreaterEqual(len(self.roles_of(party)), 2, party)


class Shapes(unittest.TestCase):
    def test_the_examples_conform(self):
        ok, text = conforms(data())
        self.assertTrue(ok, text[:3000])

    def assertRejects(self, extra, message=None):
        ok, text = conforms(data(extra))
        self.assertFalse(ok, extra)
        if message:
            self.assertIn(message, text)

    def test_a_role_with_no_party(self):
        self.assertRejects('ex:orphan a cust:PartyRole ; cust:roleType role:payer ; cust:validFrom "2020-01-01"^^xsd:date .',
                           "held by exactly one party")

    def test_a_role_held_by_two_parties(self):
        self.assertRejects("ex:trader-co cust:plays ex:jobber-co-payer .", "held by exactly one party")

    def test_a_role_with_no_start_date(self):
        self.assertRejects("ex:p a cust:Organization ; cust:partyType pt:organization ; cust:legalName \"P\" ; "
                           "cust:plays ex:r . ex:r a cust:PartyRole ; cust:roleType role:payer .")

    def test_a_role_that_ends_before_it_starts(self):
        self.assertRejects('ex:jobber-co-payer cust:validTo "2019-01-01"^^xsd:date .')

    def test_a_role_type_off_the_role_list(self):
        self.assertRejects("ex:p a cust:Organization ; cust:partyType pt:organization ; cust:legalName \"P\" ; "
                           'cust:plays ex:r . ex:r a cust:PartyRole ; cust:roleType agt:fuel-supply ; '
                           'cust:validFrom "2020-01-01"^^xsd:date .')

    def test_a_class_assignment_with_no_date(self):
        self.assertRejects("ex:a a cust:CustomerAccount ; cust:classifiedAs ex:c . ex:jobber-co cust:transactsThrough ex:a . "
                           "ex:c a cust:CustomerClass ; cust:classValue cls:direct-dealer .",
                           "assigned from a start date")

    def test_a_group_assigned_as_a_class(self):
        # A fresh assignment with one value, a date and an account, so only the group rule can fire (Pi, PR 2 round 1).
        self.assertRejects('ex:a2 a cust:CustomerAccount ; cust:classifiedAs ex:c2 . ex:jobber-co cust:transactsThrough ex:a2 . '
                           'ex:c2 a cust:CustomerClass ; cust:classValue cls:brand-attached-resellers ; '
                           'cust:validFrom "2020-01-01"^^xsd:date .', "names one of the four groups")

    # Each off-list test uses a fresh node, so only the list's own shape can fire.
    def test_a_site_type_off_its_list(self):
        self.assertRejects('ex:s9 a cust:Site ; cust:siteType <https://w3id.org/lsc/ontology/modules/customer/operating-model/coco> .',
                           "InSiteType")

    def test_an_operating_model_off_its_list(self):
        self.assertRejects('ex:s9 a cust:Site ; cust:operatingModel <https://w3id.org/lsc/ontology/modules/customer/site-type/station> .',
                           "InOperatingModel")

    def test_a_transaction_kind_off_its_list(self):
        self.assertRejects('ex:t9 a cust:PartyTransactionAssociation ; cust:transactionKind agt:offtake ; '
                           'cust:transactionReference "X" ; cust:forAccount ex:shipper-co-account .', "InTransactionKind")

    def test_an_agreement_type_off_its_list(self):
        self.assertRejects("ex:g9 a cust:Agreement ; cust:agreementType role:carrier .", "InAgreementType")

    def test_a_party_that_is_both_person_and_organization(self):
        self.assertRejects("ex:jobber-co a cust:Person .")

    def test_customer_as_a_subclass_of_party(self):
        self.assertRejects("cust:Customer rdfs:subClassOf cust:Party .", "not a subclass of party")

    def test_a_site_brand_assignment_with_no_agreement(self):
        self.assertRejects('ex:sba a cust:SiteBrandAssignment ; cust:assignsBrand ex:brand-a ; cust:appliesTo ex:station-1 ; '
                           'cust:validFrom "2020-01-01"^^xsd:date .', "made under an agreement")

    def test_an_account_with_no_party(self):
        self.assertRejects("ex:lonely a cust:CustomerAccount .", "belongs to at least one party")


if __name__ == "__main__":
    unittest.main()
