"""Tests for core 2.3.0 (EPM-DEC-001-0089): it is core 2.2.0 plus CM 1.3.7.1.7 Coordinate Customer Onboarding
(MPC-P10.1, EPM-DEC-001-0087), with no IRI removed; any other map change since 2.2.0 stops the build; and the
package is the approved, current release. Expected values are written out by hand.

Run: python3 -m pytest test_build_core_2_3.py (needs rdflib, pyshacl).
"""
import hashlib
import json
import os
import re
import unittest
from unittest import mock

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

import build_core_2_3 as b

G, COUNTS = b.build()
BASE = Graph().parse(os.path.join(b.BASE, "core.ttl"))
P = b.PROC
NEW = URIRef(P + "CM-1-3-7-1-7")
HEADER = (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion)


class Release(unittest.TestCase):
    def test_every_2_2_0_triple_is_kept_except_the_header(self):
        header = {(b.ONTOLOGY_IRI, p, o) for p, o in BASE.predicate_objects(b.ONTOLOGY_IRI) if p in HEADER}
        self.assertEqual(set(BASE) - set(G), header)

    def test_no_iri_is_removed(self):
        self.assertEqual(set(BASE.subjects()) - set(G.subjects()), set())

    def test_the_one_new_concept(self):
        added = {s for s in G.subjects(RDF.type, SKOS.Concept)} - {s for s in BASE.subjects(RDF.type, SKOS.Concept)}
        self.assertEqual(added, {NEW})
        self.assertEqual(G.value(NEW, SKOS.prefLabel), Literal("Coordinate Customer Onboarding", lang="en"))
        self.assertEqual(G.value(NEW, SKOS.notation), Literal("CM 1.3.7.1.7"))
        self.assertEqual(G.value(NEW, SKOS.broader), URIRef(P + "CM-1-3-7-1"))
        self.assertEqual(G.value(NEW, b.CORE.taxonomyLevel), Literal(5))
        self.assertEqual(G.value(NEW, SKOS.inScheme), b.SCHEME)
        self.assertEqual(G.value(NEW, SKOS.definition), Literal(
            "Coordinate the onboarding of a new customer of any type, from the setup request to a customer that is "
            "set up in every system that uses it.", lang="en"))
        scope = str(G.value(NEW, SKOS.scopeNote))
        self.assertTrue(scope.startswith("It captures the setup request, starts the credit, KYC and contract checks"), scope)
        self.assertTrue(scope.endswith("MPC-P10.1 (EPM-DEC-001-0087)."), scope)
        self.assertIn("EPM-DEC-001-0087", str(G.value(NEW, DCTERMS.provenance)))

    def test_the_new_concept_gains_nothing_the_map_does_not_give(self):
        self.assertEqual({p for p, _ in G.predicate_objects(NEW)},
                         {RDF.type, SKOS.prefLabel, SKOS.notation, SKOS.definition, SKOS.scopeNote, SKOS.broader,
                          SKOS.inScheme, b.CORE.taxonomyLevel, DCTERMS.provenance})

    def test_the_figures(self):
        self.assertEqual(len(G), 19819)
        self.assertEqual((COUNTS["process concepts"], COUNTS["new concepts"], COUNTS["canonical facts"]), (707, 1, 640))
        for key in ("IDs on stubs", "changed descriptions", "19948 references rejected", "19948 references confirmed"):
            self.assertNotIn(key, COUNTS)

    def test_the_header(self):
        self.assertEqual(str(G.value(b.ONTOLOGY_IRI, OWL.versionInfo)), "2.3.0")
        self.assertEqual(G.value(b.ONTOLOGY_IRI, OWL.priorVersion), URIRef(f"{b.ONTOLOGY_IRI}/2.2.0"))
        self.assertEqual(G.value(b.ONTOLOGY_IRI, DCTERMS.issued), G.value(b.ONTOLOGY_IRI, DCTERMS.modified))


class Package(unittest.TestCase):
    FILES = b.package(G, COUNTS)

    def test_the_written_package_equals_a_fresh_build(self):
        for name, text in self.FILES.items():
            with open(os.path.join(b.RELEASE_DIR, name)) as f:
                self.assertEqual(f.read(), text, name)

    def test_the_approval_is_the_decision_owners_words_in_the_saved_file(self):
        path, words = b.APPROVAL
        self.assertEqual(words, "Approve all six (Recommended)")
        with open(os.path.join(b.ONTOLOGY, path)) as f:
            body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
        self.assertIn(words, body)
        manifest = json.loads(self.FILES["manifest.json"])
        self.assertEqual(manifest["approval"], {"file": path, "words": words})
        self.assertFalse(manifest["release_candidate"])

    def test_shapes_and_mapping_are_2_2_0s(self):
        for name in ("shapes.ttl", "canonical-facts.csv"):
            with open(os.path.join(b.BASE, name)) as f:
                self.assertEqual(self.FILES[name], f.read(), name)

    def test_the_map_is_read_at_its_pinned_commit(self):
        self.assertEqual(b.EARLIER_COMMIT, "82593547cc1672cbcf35e13d54244830671dd009")
        self.assertRegex(b.SOURCE_COMMIT, r"^[0-9a-f]{40}$")
        manifest = json.loads(self.FILES["manifest.json"])
        self.assertEqual(manifest["built_from"]["process map"], f"{b.SOURCE_PATH} at {b.SOURCE_COMMIT}")


class EarlierRelease(unittest.TestCase):
    def test_2_2_0_is_untouched(self):
        with open(os.path.join(b.BASE, "manifest.json")) as f:
            manifest = json.load(f)
        for name, digest in manifest["files"].items():
            with open(os.path.join(b.BASE, name), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest, name)


class Guards(unittest.TestCase):
    def test_a_second_new_node_stops_the_build(self):
        current = b.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-3-7-1-7"]
        extra = dict(current, **{"CM-1-3-7-1-8": (dict(node, id="CM 1.3.7.1.8"), parent)})
        real = b.prev.map_nodes
        with mock.patch.object(b.prev, "map_nodes", lambda commit: extra if commit == b.SOURCE_COMMIT else real(commit)):
            with self.assertRaises(SystemExit):
                b.build()

    def test_a_changed_description_stops_the_build(self):
        current = b.prev.map_nodes(b.SOURCE_COMMIT)
        node, parent = current["CM-1-1-7"]
        changed = dict(current, **{"CM-1-1-7": (dict(node, description=node.get("description", "") + " More."), parent)})
        real = b.prev.map_nodes
        with mock.patch.object(b.prev, "map_nodes", lambda commit: changed if commit == b.SOURCE_COMMIT else real(commit)):
            with self.assertRaises(SystemExit):
                b.build()


if __name__ == "__main__":
    unittest.main()
