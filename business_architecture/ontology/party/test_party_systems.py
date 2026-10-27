"""Tests for the customer systems, data flows, sourcings and attributes (EPM-DEC-001-0069). Expected
values are written out by hand from the decision owner's inputs as EPM-DEC-001-0069 records them.

Run: python3 -m pytest test_party_systems.py (needs rdflib, pyshacl).
"""
import os
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_party  # noqa: E402
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
        # 42 systems, 35 flows and 24 sourcings until 2.0.0, which adds the inputs of 2026-10-27: 8 systems (PRM, station
        # point-of-sale systems, the street price aggregator, Credit Card Summary, the Enterprise Data Lake, MSMIS, MCS and
        # Terminaling Throughputs), 13 flows and 1 sourcing, the ship-to stations' origin (EPM-DEC-001-0108).
        self.assertEqual(len(set(G.subjects(RDF.type, CUST.CustomerSystem))), 42 + 8)
        self.assertEqual(len(set(G.subjects(RDF.type, CUST.DataFlow))), 35 + 13)
        self.assertEqual(len(set(G.subjects(RDF.type, CUST.CustomerSourcing))), 24 + 1)

    def test_systems_per_tier(self):
        def tier(t):
            return slugs(G.subjects(CUST.systemTier, CUST[f"system-tier/{t}"]))
        self.assertEqual(tier("integration"), {"magic"})
        self.assertEqual(tier("enrich"), {"tax-image-silo", "sirion", "terminal-upload", "xref", "information-steward"})
        # 22 downstream until 2.0.0, which adds PRM, the street price aggregator, Credit Card Summary and the
        # Enterprise Data Lake, and four landscape sources (EPM-DEC-001-0108).
        self.assertEqual(len(tier("downstream")), 22 + 4)
        self.assertEqual(tier("landscape"), {"terminal-audit-system", "flowcal", "eis", "asphalt-marketing-system",
                                             "brand-credit-card-system", "terminal-margin-ranking-system",
                                             "corp-vetting", "lenel-onguard",
                                             "station-pos", "msmis", "mcs", "terminaling-throughputs"})

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

    def test_49_attributes_carry_a_shared_attribute(self):
        # 48 until 2.0.0, which adds Salesforce's Financial Statement, a credit attribute (EPM-DEC-001-0108, question 13).
        self.assertEqual(len(set(G.subjects(CUST.sharedAttribute, None))), 49)

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

    def test_twenty_systems_match_the_system_module(self):
        # Three share a slug with the system module; the Terminal Margin Ranking System is its TMR (EPM-DEC-001-0072);
        # SAP S/4HANA is the process map's "SAP", by the decision owner's answer of 2026-10-25 (EPM-DEC-001-0099).
        # Since party 1.4.0 the seven systems the system module gains with MPC-P11 match too (EPM-DEC-001-0104).
        # Only the customer systems' matches: the dealer classes' matches are within the module (EPM-DEC-001-0108).
        pairs = {(str(s).rsplit("/", 1)[1], str(o).rsplit("/", 1)[1]) for s, o in G.subject_objects(SKOS.exactMatch)
                 if str(s).startswith(str(S))}
        self.assertEqual(pairs, {("rightangle", "rightangle"), ("kittyhawk", "kittyhawk"), ("profisee", "profisee"),
                                 ("terminal-margin-ranking-system", "tmr"), ("sap-s4hana", "sap"),
                                 ("sap-mdg", "sap-mdg"), ("salesforce", "salesforce"), ("magic", "magic"),
                                 ("bridger-insight", "bridger-insight"), ("information-steward", "information-steward"),
                                 ("sirion", "sirion"), ("customer-portal", "customer-portal"),
                                 # Since 2.0.0 the eight systems the system module gains in 1.5.0 (EPM-DEC-001-0108).
                                 ("prm", "prm"), ("station-pos", "station-pos"),
                                 ("street-price-aggregator", "street-price-aggregator"),
                                 ("credit-card-summary", "credit-card-summary"),
                                 ("enterprise-data-lake", "enterprise-data-lake"), ("msmis", "msmis"), ("mcs", "mcs"),
                                 ("terminaling-throughputs", "terminaling-throughputs")})
        self.assertEqual(len(pairs), 20)
        self.assertIn((S.rightangle, SKOS.exactMatch, SYSTEM.rightangle), G)
        self.assertIn((S["terminal-margin-ranking-system"], SKOS.exactMatch, SYSTEM.tmr), G)
        self.assertIn((S["sap-mdg"], SKOS.exactMatch, SYSTEM["sap-mdg"]), G)
        self.assertIn((S["customer-portal"], SKOS.exactMatch, SYSTEM["customer-portal"]), G)
        # The weak MPC-P11 candidates are not in the system module, so they match nothing.
        for slug in ("allocation-manager", "data-products-idp"):
            self.assertIsNone(G.value(S[slug], SKOS.exactMatch), slug)

    def test_no_shape_message_holds_an_apostrophe(self):
        # The ontology skill's SHACL rule 19: n10s writes sh:message into Cypher unescaped, so a quote breaks
        # validation in Neo4j. party 1.4.0 rewords the one message that held one (EPM-DEC-001-0104).
        from rdflib.namespace import SH
        shapes = Graph().parse(os.path.join(HERE, "shapes.ttl"))
        messages = [str(m) for m in shapes.objects(None, SH.message)]
        self.assertEqual(len(messages), 40)
        self.assertEqual([m for m in messages if "'" in m or "\u2019" in m], [])
        self.assertIn("The definition of a customer system cites its source.", messages)

    def test_definitions(self):
        # Item G (EPM-DEC-001-0099), checked by hand against definitions.csv on 2026-10-25: 18 customer systems are
        # defined, each citing its source; the four the decision owner's customer-data owner is asked about are not.
        systems = set(G.subjects(RDF.type, CUST.CustomerSystem))
        defined = slugs(s for s in G.subjects(SKOS.definition, None) if s in systems)
        # 18 in 1.2.0 (EPM-DEC-001-0099), then the 20 internal systems drafted from the repository in 1.3.0
        # (EPM-DEC-001-0103): every customer system but the four the customer-data owner is asked about.
        # 46 since 2.0.0: the eight systems of 2026-10-27 are defined too (EPM-DEC-001-0108).
        self.assertEqual(len(defined), 38 + 8)
        self.assertEqual(slugs(systems) - defined, {"drop-tank", "gas-buddy", "dtn-file-server", "federal-health"})
        for slug in ("drop-tank", "gas-buddy", "dtn-file-server", "federal-health"):
            self.assertIsNone(G.value(S[slug], SKOS.definition))
        src = Namespace("https://w3id.org/lsc/ontology/source/")
        self.assertEqual(set(G.objects(S.polaris, DCTERMS.source)), {src["phmsa-marathon-pipeline-noa-2024-09-26"]})
        self.assertIn("Terminal Upload", str(G.value(S.kittyhawk, SKOS.editorialNote)))
        for s in systems:
            if G.value(s, SKOS.definition) is not None:
                self.assertIsNotNone(G.value(s, DCTERMS.source), s)

    def test_the_origin_patterns(self):
        def origin(concept):
            return {str(G.value(n, CUST.sourcingSystem)).rsplit("/", 1)[1]
                    for n in G.subjects(CUST.sourcedConcept, CUST[concept])
                    if (n, CUST.sourcingKind, CUST["sourcing-kind/origin"]) in G}
        self.assertEqual(origin("party-role/sold-to"), {"salesforce"})
        # The jobber's origin in Dealer Master is deprecated in 2.0.0, its triples kept, and replaced by the ship-to
        # stations' origin there (EPM-DEC-001-0108).
        self.assertEqual(origin("party-role/jobber"), {"dealer-master"})
        old = CUST["sourcing/dealer-master--origin--party-role--jobber"]
        new = CUST["sourcing/dealer-master--origin--site-type--station"]
        from rdflib.namespace import OWL
        self.assertIn((old, OWL.deprecated, Literal(True)), G)
        self.assertIn((old, DCTERMS.isReplacedBy, new), G)
        self.assertEqual(origin("site-type/station"), {"dealer-master"})
        self.assertIsNone(G.value(new, OWL.deprecated))
        self.assertEqual(origin("customer-class/direct-dealer"), {"sap-mdg"})
        self.assertIn("replicated to Dealer Master",
                      str(G.value(CUST["sourcing/sap-mdg--origin--customer-class--direct-dealer"], RDFS.comment)))

    def test_key_flows(self):
        for a, b in [("salesforce", "sap-mdg"), ("dealer-master", "sap-mdg"), ("sap-mdg", "dealer-master"),
                     ("sap-mdg", "sap-s4hana"), ("sap-mdg", "rightangle"), ("rightangle", "sap-mdg"),
                     ("magic", "salesforce"), ("sap-mdg", "polaris"), ("polaris", "sap-s4hana")]:
            self.assertIn((S[a], CUST.feeds, S[b]), G, f"{a} -> {b}")
        # Input 2's uncertain edges were not taken (EPM-DEC-001-0069); input 8 shows both, and the decision owner
        # confirmed its arrows, so 2.0.0 takes them (EPM-DEC-001-0108).
        self.assertIn((S["sap-s4hana"], CUST.feeds, S["bridger-insight"]), G)
        self.assertIn((S["rightangle"], CUST.feeds, S["tfr"]), G)
        # The corrected flows carry ship-to stations and replicated sold-tos, not jobbers or direct dealers.
        self.assertIn("Ship-to stations", str(G.value(CUST["flow/dealer-master--sap-mdg"], CUST.carries)))
        self.assertIn("sold-to", str(G.value(CUST["flow/sap-mdg--dealer-master"], CUST.carries)))
        for f in ("flow/dealer-master--sap-mdg", "flow/sap-mdg--dealer-master"):
            self.assertIsNotNone(G.value(CUST[f], SKOS.changeNote), f)
        # The Dealer Master loop with RightAngle, and the flows to PRM, written out by hand.
        for a, b in [("rightangle", "dealer-master"), ("dealer-master", "rightangle"), ("dealer-master", "prm"),
                     ("station-pos", "dealer-master"), ("station-pos", "street-price-aggregator"),
                     ("street-price-aggregator", "prm"), ("dealer-master", "credit-card-summary"),
                     ("rightangle", "gravitate"), ("rightangle", "terminal-download"), ("kittyhawk", "rcms"),
                     ("fuelfacs", "tasdm")]:
            self.assertIn((S[a], CUST.feeds, S[b]), G, f"{a} -> {b}")

    def test_dealer_master_after_the_correction(self):
        # EPM-DEC-001-0108: Dealer Master is not built on Salesforce, jobbers do not start there, and it is the system
        # of record for the ship-to stations and the link from each jobber to its stations.
        for p in (CUST.customerRole, SKOS.definition):
            text = str(G.value(S["dealer-master"], p))
            self.assertNotIn("built on Salesforce", text, p)
            self.assertNotIn("Jobbers start here", text, p)
            self.assertIn("ship-to stations", text, p)
        self.assertEqual(set(G.objects(S["dealer-master"], CUST.systemOfRecordFor)), {CUST.Site, CUST.PartyRelationship})
        self.assertIsNotNone(G.value(S["dealer-master"], SKOS.changeNote))
        self.assertIn("Brand Credit Card Master database",
                      {str(a) for a in G.objects(S["brand-credit-card-system"], SKOS.altLabel)})
        self.assertIn("MDG.BP.I.1001", str(G.value(S["bridger-insight"], CUST.customerRole)))
        self.assertIn("authoritative source", str(G.value(S["terminal-margin-ranking-system"], SKOS.editorialNote)))


class Attributes(unittest.TestCase):
    def attrs(self, **where):
        out = set(G.subjects(RDF.type, CUST.SystemAttribute))
        for p, o in where.items():
            out = {a for a in out if (a, CUST[p], o) in G}
        return out

    def test_counts_by_category(self):
        # 275 and 43 until 2.0.0, which adds Salesforce's Financial Statement (EPM-DEC-001-0108, question 13).
        self.assertEqual(len(self.attrs()), 276)
        self.assertEqual(len(self.attrs(attributeCategory=CUST["attribute-category/create"])), 44)
        self.assertEqual(len(self.attrs(attributeCategory=CUST["attribute-category/enrich"])), 232)

    def test_counts_by_system_and_category(self):
        expected = {"salesforce": (10, 44), "sap-mdg": (9, 26), "rightangle": (9, 123),
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


class SameSystem(unittest.TestCase):
    """The build rejects a hand-held match to the system module that does not hold (EPM-DEC-001-0072)."""

    def fails(self, same):
        real = build_party.SAME_SYSTEM
        build_party.SAME_SYSTEM = same
        try:
            with self.assertRaises(SystemExit) as caught:
                build_party.load_systems(build_party.load())
        finally:
            build_party.SAME_SYSTEM = real
        return str(caught.exception)

    def test_a_node_the_system_module_lacks(self):
        self.assertIn("terminal-margin-ranking-system: not a listed customer system, or no-such-node not in the system module",
                      self.fails({"terminal-margin-ranking-system": "no-such-node"}))

    def test_a_node_with_another_label(self):
        self.assertIn("terminal-margin-ranking-system: the system module calls sap 'SAP S/4HANA', which is not one of its labels",
                      self.fails({"terminal-margin-ranking-system": "sap"}))


class DecisionOwnerAnswers(unittest.TestCase):
    def test_the_cbs_sourcing_cites_the_decision_owner(self):
        # The decision owner assumes input 6's CBS is FuelFacs (EPM-DEC-001-0072), so the sourcing says so.
        note = str(G.value(CUST["sourcing/fuelfacs--source--customer-class--terminal-rack-customer"], RDFS.comment))
        self.assertEqual(note, "Terminal customers, from input 6's CBS, which the decision owner assumes, for this model, "
                               "is FuelFacs (EPM-DEC-001-0072).")


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
        self.assertIn("from the inputs 1 to 11", text)

    def test_a_sourcing_of_something_that_is_not_a_kind_of_customer(self):
        ok, text = self.conforms('party:n a party:CustomerSourcing ; party:sourcingSystem s:salesforce ; '
                                 'party:sourcingKind <https://w3id.org/lsc/ontology/modules/party/sourcing-kind/origin> ; '
                                 'party:sourcedConcept <https://w3id.org/lsc/ontology/modules/party/transaction-kind/invoice> ; '
                                 '<http://www.w3.org/2000/01/rdf-schema#comment> "x"@en ; party:evidenceInput "2" .')
        self.assertFalse(ok)
        self.assertIn("names a party role, a customer class", text)

    def test_a_definition_without_its_source(self):
        ok, text = self.conforms('s:drop-tank <http://www.w3.org/2004/02/skos/core#definition> "A system."@en .')
        self.assertFalse(ok)
        self.assertIn("cites its source", text)

    def test_two_definitions(self):
        ok, _ = self.conforms('s:salesforce <http://www.w3.org/2004/02/skos/core#definition> "Another."@en .')
        self.assertFalse(ok)

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
