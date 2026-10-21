"""Tests for the customer systems, data flows, sourcings and attributes (EPM-DEC-001-0069). Expected
values are written out by hand from the decision owner's inputs as EPM-DEC-001-0069 records them.

Run: python3 -m pytest test_party_systems.py (needs rdflib, pyshacl).
"""
import os
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
CUST = Namespace("https://w3id.org/lsc/ontology/modules/party/")
S = Namespace("https://w3id.org/lsc/ontology/modules/party/system/")
SYSTEM = Namespace("https://w3id.org/lsc/ontology/modules/system/system/")


def parse(*names, extra=""):
    g = Graph()
    for n in names:
        g.parse(os.path.join(HERE, n))
    if extra:
        g.parse(data="@prefix party: <https://w3id.org/lsc/ontology/modules/party/> .\n"
                     "@prefix s: <https://w3id.org/lsc/ontology/modules/party/system/> .\n" + extra, format="turtle")
    return g


G = parse("vocabulary.ttl", "code-lists.ttl", "systems.ttl")
SHAPES = parse("shapes.ttl")


def slugs(subjects):
    return {str(s).rsplit("/", 1)[1] for s in subjects}


class Systems(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(set(G.subjects(RDF.type, CUST.CustomerSystem))), 42)
        self.assertEqual(len(set(G.subjects(RDF.type, CUST.DataFlow))), 35)
        self.assertEqual(len(set(G.subjects(RDF.type, CUST.CustomerSourcing))), 24)

    def test_systems_per_tier(self):
        def tier(t):
            return slugs(G.subjects(CUST.systemTier, CUST[f"system-tier/{t}"]))
        self.assertEqual(tier("integration"), {"magic"})
        self.assertEqual(tier("enrich"), {"tax-image-silo", "sirion", "terminal-upload", "xref", "information-steward"})
        self.assertEqual(len(tier("downstream")), 22)
        self.assertEqual(tier("landscape"), {"terminal-audit-system", "flowcal", "eis", "asphalt-marketing-system",
                                             "brand-credit-card-system", "terminal-margin-ranking-system",
                                             "corp-vetting", "lenel-onguard"})

    def test_nine_systems_below_magic_feed_profisee(self):
        self.assertEqual(slugs(G.subjects(CUST.feeds, S.profisee)),
                         {"tmt", "federal-health", "quorum", "kittyhawk", "gas-buddy", "drop-tank", "emk3",
                          "customer-portal", "dtn-file-server"})

    def test_the_four_system_code_lists_cite_their_record(self):
        from rdflib import URIRef
        cite = URIRef("http://purl.org/dc/terms/bibliographicCitation")
        for scheme in ("system-tier", "shared-attribute", "sourcing-kind"):
            self.assertEqual(str(G.value(CUST[scheme], cite)), "EPM-DEC-001-0069", scheme)
        self.assertEqual(str(G.value(CUST["attribute-category"], cite)), "EPM-DEC-001-0067; EPM-DEC-001-0069")

    def test_48_attributes_carry_a_shared_attribute(self):
        self.assertEqual(len(set(G.subjects(CUST.sharedAttribute, None))), 48)

    def test_the_six_core_systems_and_what_they_implement(self):
        expected = {
            "sap-mdg": {"Party", "ExternalIdentifier"},
            "sap-s4hana": {"Party", "PartyRole", "CustomerAccount"},
            "salesforce": {"Party", "ContactPoint", "Address"},
            "rightangle": {"Party", "PartyRole", "ContactPoint", "Agreement"},
            "polaris": {"CustomerAccount", "PartyTransactionAssociation", "Site"},
            "dealer-master": {"PartyRole", "Site", "SiteBrandAssignment", "Agreement"},
        }
        core = slugs(G.subjects(CUST.systemTier, CUST["system-tier/core"]))
        self.assertEqual(core, set(expected))
        for slug, entities in expected.items():
            self.assertEqual(slugs(G.objects(S[slug], CUST.implements)), entities, slug)

    def test_three_systems_match_the_system_module(self):
        matched = {str(o).rsplit("/", 1)[1] for o in G.objects(None, SKOS.exactMatch)}
        self.assertEqual(matched, {"rightangle", "kittyhawk", "profisee"})
        self.assertIn((S.rightangle, SKOS.exactMatch, SYSTEM.rightangle), G)

    def test_the_origin_patterns(self):
        def origin(concept):
            return {str(G.value(n, CUST.sourcingSystem)).rsplit("/", 1)[1]
                    for n in G.subjects(CUST.sourcedConcept, CUST[concept])
                    if (n, CUST.sourcingKind, CUST["sourcing-kind/origin"]) in G}
        self.assertEqual(origin("party-role/sold-to"), {"salesforce"})
        self.assertEqual(origin("party-role/jobber"), {"dealer-master"})
        self.assertEqual(origin("customer-class/direct-dealer"), {"sap-mdg"})

    def test_key_flows(self):
        for a, b in [("salesforce", "sap-mdg"), ("dealer-master", "sap-mdg"), ("sap-mdg", "dealer-master"),
                     ("sap-mdg", "sap-s4hana"), ("sap-mdg", "rightangle"), ("rightangle", "sap-mdg"),
                     ("magic", "salesforce"), ("sap-mdg", "polaris"), ("polaris", "sap-s4hana")]:
            self.assertIn((S[a], CUST.feeds, S[b]), G, f"{a} -> {b}")
        # Input 2's uncertain edges are not taken (EPM-DEC-001-0069).
        self.assertNotIn((S["sap-s4hana"], CUST.feeds, S["bridger-insight"]), G)
        self.assertNotIn((S["rightangle"], CUST.feeds, S["tfr"]), G)


class Attributes(unittest.TestCase):
    def attrs(self, **where):
        out = set(G.subjects(RDF.type, CUST.SystemAttribute))
        for p, o in where.items():
            out = {a for a in out if (a, CUST[p], o) in G}
        return out

    def test_counts_by_category(self):
        self.assertEqual(len(self.attrs()), 275)
        self.assertEqual(len(self.attrs(attributeCategory=CUST["attribute-category/create"])), 43)
        self.assertEqual(len(self.attrs(attributeCategory=CUST["attribute-category/enrich"])), 232)

    def test_counts_by_system_and_category(self):
        expected = {"salesforce": (9, 44), "sap-mdg": (9, 26), "rightangle": (9, 123),
                    "dealer-master": (2, 17), "sap-s4hana": (2, 9), "polaris": (12, 13)}
        for slug, (create, enrich) in expected.items():
            self.assertEqual(len(self.attrs(inSystem=S[slug], attributeCategory=CUST["attribute-category/create"])), create, slug)
            self.assertEqual(len(self.attrs(inSystem=S[slug], attributeCategory=CUST["attribute-category/enrich"])), enrich, slug)

    def test_shared_identifiers(self):
        def systems_of(shared):
            return {str(G.value(a, CUST.inSystem)).rsplit("/", 1)[1]
                    for a in self.attrs(sharedAttribute=CUST[f"shared-attribute/{shared}"])}
        self.assertEqual(systems_of("sap-customer-number"), {"sap-mdg", "rightangle", "dealer-master", "polaris"})
        self.assertEqual(systems_of("business-associate-id"), {"sap-mdg", "rightangle", "dealer-master"})
        self.assertEqual(systems_of("tax-id"), {"sap-mdg", "sap-s4hana", "rightangle", "dealer-master", "polaris"})

    def test_labels_are_corrected_and_deduplicated(self):
        labels = {str(G.value(a, SKOS.prefLabel)) for a in self.attrs()}
        for wrong in ("Sales Manaager", "Adress_Line_1", "Joint_Tarrif_Flag", "Broke Reconcile Method",
                      "SAP Net Our Profit Cntr", "Inactive_Indicator Flag"):
            self.assertNotIn(wrong, labels)
        for right in ("Sales Manager", "Address_Line_1", "Joint_Tariff_Flag", "Broker Reconcile Method",
                      "SAP Net Out Profit Cntr", "Inactive_Indicator_Flag"):
            self.assertIn(right, labels)

    def test_a_few_mappings(self):
        def describes(system, category, slug):
            return G.value(CUST[f"attribute/{system}/{category}/{slug}"], CUST.describes)
        self.assertEqual(describes("rightangle", "create", "fein"), CUST.ExternalIdentifier)
        self.assertEqual(describes("dealer-master", "create", "territory-manager"), CUST.CustomerAccount)
        self.assertEqual(describes("sap-mdg", "enrich", "authorization-group"), CUST.LineOfBusiness)
        self.assertEqual(describes("dealer-master", "enrich", "createdatetime"), CUST.SystemRecord)
        self.assertEqual(describes("salesforce", "enrich", "credit-parent-account"), CUST.PartyRelationship)


class OpenQuestions(unittest.TestCase):
    def test_the_cbs_sourcing_keeps_its_open_identity(self):
        # Whether input 6's CBS is FuelFacs is open (EPM-DEC-001-0069, item 2), so the sourcing says so.
        note = str(G.value(CUST["sourcing/fuelfacs--source--customer-class--terminal-rack-customer"], RDFS.comment))
        self.assertIn("is open", note)


class Shapes(unittest.TestCase):
    def conforms(self, extra=""):
        ok, _, text = validate(parse("vocabulary.ttl", "code-lists.ttl", "systems.ttl", extra=extra),
                               shacl_graph=SHAPES, advanced=True)
        return ok, text

    def test_the_module_conforms(self):
        ok, text = self.conforms()
        self.assertTrue(ok, text[:3000])

    def test_a_flow_with_no_target(self):
        ok, text = self.conforms('party:x a party:DataFlow ; party:fromSystem s:salesforce ; party:carries "x"@en ; party:evidenceInput "1" .')
        self.assertFalse(ok)
        self.assertIn("from one customer system to one other", text)

    def test_an_attribute_with_no_category(self):
        ok, text = self.conforms('party:a a party:SystemAttribute ; <http://www.w3.org/2004/02/skos/core#prefLabel> "A"@en ; '
                                 'party:inSystem s:salesforce ; party:describes party:Party .')
        self.assertFalse(ok)
        self.assertIn("Create or Enrich", text)

    def test_an_attribute_describing_a_non_entity(self):
        ok, text = self.conforms('party:a a party:SystemAttribute ; <http://www.w3.org/2004/02/skos/core#prefLabel> "A"@en ; '
                                 'party:inSystem s:salesforce ; party:attributeCategory <https://w3id.org/lsc/ontology/modules/party/attribute-category/create> ; '
                                 'party:describes party:DataFlow .')
        self.assertFalse(ok)
        self.assertIn("describes one entity", text)

    def test_a_system_with_two_roles(self):
        ok, text = self.conforms("s:salesforce party:customerRole \"Another role.\"@en .")
        self.assertFalse(ok)
        self.assertIn("says what it does", text)

    def test_a_flow_that_carries_nothing(self):
        ok, text = self.conforms('party:x a party:DataFlow ; party:fromSystem s:salesforce ; party:toSystem s:sap-mdg ; '
                                 'party:carries ""@en ; party:evidenceInput "3" .')
        self.assertFalse(ok)
        self.assertIn("says what it carries", text)

    def test_a_flow_citing_an_input_that_does_not_exist(self):
        ok, text = self.conforms('party:x a party:DataFlow ; party:fromSystem s:salesforce ; party:toSystem s:sap-mdg ; '
                                 'party:carries "x"@en ; party:evidenceInput "42" .')
        self.assertFalse(ok)
        self.assertIn("from the seven inputs", text)

    def test_a_sourcing_of_something_that_is_not_a_kind_of_customer(self):
        ok, text = self.conforms('party:n a party:CustomerSourcing ; party:sourcingSystem s:salesforce ; '
                                 'party:sourcingKind <https://w3id.org/lsc/ontology/modules/party/sourcing-kind/origin> ; '
                                 'party:sourcedConcept <https://w3id.org/lsc/ontology/modules/party/transaction-kind/invoice> ; '
                                 '<http://www.w3.org/2000/01/rdf-schema#comment> "x"@en ; party:evidenceInput "2" .')
        self.assertFalse(ok)
        self.assertIn("names a party role, a customer class", text)

    def test_a_system_whose_role_is_blank(self):
        ok, text = self.conforms('party:sx a party:CustomerSystem ; <http://www.w3.org/2004/02/skos/core#prefLabel> "X"@en ; '
                                 '<http://www.w3.org/2004/02/skos/core#inScheme> party:customer-systems ; '
                                 'party:systemTier <https://w3id.org/lsc/ontology/modules/party/system-tier/landscape> ; '
                                 'party:customerRole "   "@en .')
        self.assertFalse(ok)
        self.assertIn("says what it does", text)

    def test_a_flow_whose_carries_is_blank(self):
        ok, text = self.conforms('party:x a party:DataFlow ; party:fromSystem s:salesforce ; party:toSystem s:sap-mdg ; '
                                 'party:carries "   "@en ; party:evidenceInput "3" .')
        self.assertFalse(ok)
        self.assertIn("says what it carries", text)

    def test_a_sourcing_whose_note_is_blank(self):
        ok, text = self.conforms('party:n a party:CustomerSourcing ; party:sourcingSystem s:salesforce ; '
                                 'party:sourcingKind <https://w3id.org/lsc/ontology/modules/party/sourcing-kind/origin> ; '
                                 'party:sourcedConcept <https://w3id.org/lsc/ontology/modules/party/party-role/sold-to> ; '
                                 '<http://www.w3.org/2000/01/rdf-schema#comment> " "@en ; party:evidenceInput "2" .')
        self.assertFalse(ok)
        self.assertIn("has a note", text)

    def test_a_system_implementing_something_outside_the_model(self):
        for thing in ("SystemRecord", "DataFlow"):
            ok, text = self.conforms(f"s:salesforce party:implements party:{thing} .")
            self.assertFalse(ok, thing)
            self.assertIn("entities of the conceptual model only", text)


if __name__ == "__main__":
    unittest.main()
