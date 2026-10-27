"""Tests for core 2.4.0 (EPM-DEC-001-0105): it is core 2.3.0 with the 25 MPC-P12 renames, the four alternative
labels of EPM-DEC-001-0098 item 2 moved to core:priorPreferredLabel, and core's eleven code lists stating their top
concepts (item 5), with no IRI added or removed; any other map change since 2.3.0 stops the build; and the package is
the approved, current release. Expected values are written out by hand.

Run: python3 -m pytest test_build_core_2_4.py (needs rdflib, pyshacl).
"""
import hashlib
import json
import os
import re
import unittest
from collections import Counter
from unittest import mock

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS, XSD

import build_core_2_4 as b

G, COUNTS = b.build()
BASE = Graph().parse(os.path.join(b.BASE, "core.ttl"))
P = b.PROC
HEADER = (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion)


def en(text):
    return Literal(text, lang="en")


def label(slug):
    return G.value(URIRef(P + slug), SKOS.prefLabel)


class Release(unittest.TestCase):
    def test_no_iri_is_added_or_removed(self):
        self.assertEqual(set(BASE.subjects()), set(G.subjects()))

    def test_only_the_header_labels_and_alternative_labels_are_removed(self):
        removed = set(BASE) - set(G)
        self.assertEqual(Counter(p for _, p, _ in removed),
                         Counter({SKOS.prefLabel: 25, SKOS.altLabel: 4, OWL.versionInfo: 1, OWL.versionIRI: 1,
                                  DCTERMS.issued: 1, DCTERMS.modified: 1, OWL.priorVersion: 1}))

    def test_the_added_statements(self):
        added = set(G) - set(BASE)
        self.assertEqual(Counter(p for _, p, _ in added),
                         Counter({SKOS.prefLabel: 25, b.CORE.priorPreferredLabel: 29, SKOS.changeNote: 29,
                                  SKOS.topConceptOf: 51, SKOS.hasTopConcept: 51, OWL.versionInfo: 1,
                                  OWL.versionIRI: 1, DCTERMS.issued: 1, DCTERMS.modified: 1, OWL.priorVersion: 1}))

    def test_the_mpc_p12_names(self):
        # Written out by hand from the accepted proposal (MPC-P12; EPM-DEC-001-0105).
        expected = {
            "CM-1-3-1-1-1": "Source & Collect Information for Market Analysis",
            "CM-1-3-1-1-2": "Define Analysis Objectives & Scope for Market Analysis",
            "CM-1-3-1-1-3": "Analyze Market Data",
            "CM-1-3-1-1-4": "Document Findings of Market Analysis",
            "CM-1-3-1-2-1": "Source & Collect Information for Company Analysis",
            "CM-1-3-1-2-2": "Define Analysis Objectives & Scope for Company Analysis",
            "CM-1-3-1-2-3": "Analyze Company Data",
            "CM-1-3-1-2-4": "Document Findings of Company Analysis",
            "CM-1-3-1-3-1": "Source & Collect Information for Consumer Analysis",
            "CM-1-3-1-3-2": "Define Analysis Objectives & Scope for Consumer Analysis",
            "CM-1-3-1-3-3": "Analyze Consumer Data",
            "CM-1-3-1-3-4": "Document Findings of Consumer Analysis",
            "CM-1-3-1-4-1": "Source & Collect Information for Customer And Marketer Analysis",
            "CM-1-3-1-4-2": "Define Analysis Objectives & Scope for Customer And Marketer Analysis",
            "CM-1-3-1-4-3": "Analyze Customer and Marketer Data",
            "CM-1-3-1-4-4": "Document Findings of Customer And Marketer Analysis",
            "CM-1-3-1-5-1": "Source & Collect Information for Competitor Analysis",
            "CM-1-3-1-5-2": "Define Analysis Objectives & Scope for Competitor Analysis",
            "CM-1-3-1-5-3": "Analyze Competitor Data",
            "CM-1-3-1-5-4": "Document Findings of Competitor Analysis",
            "CM-1-3-8-1-3": "Determine Invoice Taxability",
            "CM-1-3-8-4-5": "Determine Taxability for Reporting",
            "CM-1-1-2-6-1": "Obtain latest XPIMS MOP model for Crude Oil Evaluation",
            "CM-1-1-2-7-1": "Obtain latest XPIMS MOP model for Product Evaluation",
            "CM-1-2-3-1": "Perform Actualizations",
        }
        self.assertEqual({s: str(label(s)) for s in expected}, expected)
        self.assertEqual(G.value(URIRef(P + "CM-1-2-3-1"), b.CORE.priorPreferredLabel), en("Actualizations"))
        self.assertEqual(G.value(URIRef(P + "CM-1-3-1-4-3"), b.CORE.priorPreferredLabel), en("Analyze Data"))
        self.assertEqual(label("CM-1-2-3"), en("Actualizations"))

    def test_each_old_name_is_kept_as_the_prior_preferred_label(self):
        # Written out by hand: the name each process had in core 2.3.0 and the map before MPC-P12.
        old = {}
        for n in "12345":
            old.update({f"CM-1-3-1-{n}-1": "Source & Collect Information",
                        f"CM-1-3-1-{n}-2": "Define Analysis Objectives & Scope",
                        f"CM-1-3-1-{n}-3": "Analyze Data", f"CM-1-3-1-{n}-4": "Document Findings"})
        old.update({"CM-1-3-8-1-3": "Determine Taxability", "CM-1-3-8-4-5": "Determine Taxability",
                    "CM-1-1-2-6-1": "Obtain latest XPIMS MOP model", "CM-1-1-2-7-1": "Obtain latest XPIMS MOP model",
                    "CM-1-2-3-1": "Actualizations"})
        self.assertEqual(len(old), 25)
        for slug, name in old.items():
            s = URIRef(P + slug)
            self.assertEqual(BASE.value(s, SKOS.prefLabel), en(name), slug)
            self.assertEqual(set(G.objects(s, b.CORE.priorPreferredLabel)) - set(BASE.objects(s, b.CORE.priorPreferredLabel)),
                             {en(name)}, slug)
            self.assertNotIn(en(name), set(G.objects(s, SKOS.altLabel)), slug)
            self.assertIn("MPC-P12 (EPM-DEC-001-0105)", " ".join(str(n) for n in G.objects(s, SKOS.changeNote)), slug)

    def test_the_four_cvp_alternative_labels_move_to_history(self):
        moved = {"CM-1-3-2-3-1": "Test Customer value proposition",
                 "CM-1-3-2-3-2": "Formulate and Evaluate Strategic Operating Alternatives (CVP)",
                 "CM-1-3-2-3-3": "Establish CVP principles and objectives",
                 "CM-1-3-2-3-4": "Develop/Update Strategy (CVP)"}
        for slug, name in moved.items():
            s = URIRef(P + slug)
            self.assertIn((s, SKOS.altLabel, en(name)), BASE, slug)
            self.assertNotIn((s, SKOS.altLabel, en(name)), G, slug)
            self.assertIn((s, b.CORE.priorPreferredLabel, en(name)), G, slug)
            self.assertEqual(G.value(s, SKOS.prefLabel), BASE.value(s, SKOS.prefLabel), slug)

    def test_the_iris_equal_core_2_3_0s(self):
        iris = lambda g: {t for triple in g for t in triple if isinstance(t, URIRef)}
        # Only the header's version IRIs differ: 2.4.0 is new, and 2.2.0 is no longer the prior version.
        self.assertEqual(iris(G) - iris(BASE), {URIRef(f"{b.ONTOLOGY_IRI}/2.4.0")})
        self.assertEqual(iris(BASE) - iris(G), {URIRef(f"{b.ONTOLOGY_IRI}/2.2.0")})
        self.assertEqual(set(G.subjects(RDF.type, SKOS.Concept)), set(BASE.subjects(RDF.type, SKOS.Concept)))

    def test_no_two_processes_share_a_preferred_label(self):
        labels = Counter(str(l).lower() for s, l in G.subject_objects(SKOS.prefLabel)
                         if (s, SKOS.inScheme, b.SCHEME) in G)
        self.assertEqual([l for l, n in labels.items() if n > 1], [])

    def test_no_alternative_label_equals_another_concepts_preferred_label(self):
        pref = {str(l).lower(): s for s, l in G.subject_objects(SKOS.prefLabel)}
        clashes = [(s, l) for s, l in G.subject_objects(SKOS.altLabel) if pref.get(str(l).lower(), s) != s]
        self.assertEqual(clashes, [])
        self.assertIn(en("Test Customer value proposition"),
                      set(G.objects(URIRef(P + "CM-1-3-2-3-1"), b.CORE.priorPreferredLabel)))

    def test_every_code_list_member_is_a_top_concept_both_ways(self):
        self.assertEqual(sorted(b.CODE_LISTS), [
            "ApqcMappingDecision", "BusinessDomain", "Cadence", "ConceptKind", "EvidenceBases", "GovernanceStatus",
            "HoldStatus", "LifecycleStatus", "OperatingMode", "PlanningLevel", "ScopeUnits"])
        for name in b.CODE_LISTS:
            self.assertEqual(list(BASE.subjects(SKOS.topConceptOf, b.CORE[name])), [], name)
            scheme = b.CORE[name]
            members = {s for s in G.subjects(SKOS.inScheme, scheme)}
            self.assertTrue(members, name)
            self.assertEqual(set(G.subjects(SKOS.topConceptOf, scheme)), members, name)
            self.assertEqual(set(G.objects(scheme, SKOS.hasTopConcept)), members, name)

    def test_the_figures(self):
        self.assertEqual(len(G), 19975)
        self.assertEqual((COUNTS["process concepts"], COUNTS["renamed concepts"], COUNTS["alternative labels moved"],
                          COUNTS["code-list top concepts"], COUNTS["canonical facts"]), (707, 25, 4, 51, 640))
        self.assertNotIn("new concepts", COUNTS)

    def test_the_header(self):
        self.assertEqual(str(G.value(b.ONTOLOGY_IRI, OWL.versionInfo)), "2.4.0")
        self.assertEqual(G.value(b.ONTOLOGY_IRI, OWL.priorVersion), URIRef(f"{b.ONTOLOGY_IRI}/2.3.0"))
        self.assertEqual(G.value(b.ONTOLOGY_IRI, OWL.versionIRI), URIRef("https://w3id.org/lsc/ontology/modules/core/2.4.0"))
        for p in (DCTERMS.issued, DCTERMS.modified):
            self.assertEqual(G.value(b.ONTOLOGY_IRI, p), Literal("2026-10-26", datatype=XSD.date))


class Package(unittest.TestCase):
    FILES = b.package(G, COUNTS)

    def test_the_written_package_equals_a_fresh_build(self):
        for name, text in self.FILES.items():
            with open(os.path.join(b.RELEASE_DIR, name)) as f:
                self.assertEqual(f.read(), text, name)

    def test_the_approval_is_the_delegation_in_the_saved_file(self):
        path, words = b.APPROVAL
        self.assertEqual(words, "Yes, delegate as described (Recommended)")
        with open(os.path.join(b.ONTOLOGY, path)) as f:
            body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
        self.assertIn(words, body)
        manifest = json.loads(self.FILES["manifest.json"])
        self.assertEqual(manifest["approval"], {"who": b.APPROVER, "file": path, "words": words})
        self.assertFalse(manifest["release_candidate"])

    def test_the_proposal_acceptance_is_the_decision_owners_words(self):
        with open(os.path.join(b.ONTOLOGY, "step4/review-evidence/decision-owner-answers/answers-2026-10-26-night.md")) as f:
            body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
        self.assertIn("Rename by parent (Recommended)", body)

    def test_shapes_and_mapping_are_2_3_0s(self):
        for name in ("shapes.ttl", "canonical-facts.csv"):
            with open(os.path.join(b.BASE, name)) as f:
                self.assertEqual(self.FILES[name], f.read(), name)

    def test_the_map_is_read_at_its_pinned_commit(self):
        self.assertEqual(b.EARLIER_COMMIT, "c351ef0ecb1e3cbe6af38f46f66065499c73442f")
        # The commit that applied MPC-P12 to the map (EPM-DEC-001-0105).
        self.assertEqual(b.SOURCE_COMMIT, "4906666a06507d9c7d996d83df7b24ab824038d7")
        manifest = json.loads(self.FILES["manifest.json"])
        self.assertEqual(manifest["built_from"]["process map"], f"{b.SOURCE_PATH} at {b.SOURCE_COMMIT}")


class EarlierRelease(unittest.TestCase):
    def test_2_3_0_is_untouched(self):
        with open(os.path.join(b.BASE, "manifest.json")) as f:
            manifest = json.load(f)
        for name, digest in manifest["files"].items():
            with open(os.path.join(b.BASE, name), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest, name)


class Guards(unittest.TestCase):
    def patched(self, nodes):
        real = b.prev.prev.map_nodes
        return mock.patch.object(b.prev.prev, "map_nodes",
                                 lambda commit: nodes if commit == b.SOURCE_COMMIT else real(commit))

    def test_an_unapproved_rename_stops_the_build(self):
        current = b.prev.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-1-7"]
        with self.patched(dict(current, **{"CM-1-1-7": (dict(node, name="Something Else"), parent)})):
            with self.assertRaises(SystemExit):
                b.build()

    def test_a_different_new_name_stops_the_build(self):
        current = b.prev.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-2-3-1"]
        with self.patched(dict(current, **{"CM-1-2-3-1": (dict(node, name="Actualize Trades"), parent)})):
            with self.assertRaises(SystemExit):
                b.build()

    def test_a_changed_description_stops_the_build(self):
        current = b.prev.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-1-7"]
        changed = dict(current, **{"CM-1-1-7": (dict(node, description=node.get("description", "") + " More."), parent)})
        with self.patched(changed):
            with self.assertRaises(SystemExit):
                b.build()

    def test_a_new_node_stops_the_build(self):
        current = b.prev.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-2-3-1"]
        with self.patched(dict(current, **{"CM-1-2-3-2": (dict(node, id="CM 1.2.3.2"), parent)})):
            with self.assertRaises(SystemExit):
                b.build()

    def test_a_systems_change_does_not_stop_the_build(self):
        # Core does not read the map's systems field (MPC-P11 changes it in its own pull request).
        current = b.prev.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-3-8-2-1"]
        with self.patched(dict(current, **{"CM-1-3-8-2-1": (dict(node, systems=["SAP S/4HANA"]), parent)})):
            g, _ = b.build()
        self.assertEqual(len(g), 19975)


if __name__ == "__main__":
    unittest.main()
