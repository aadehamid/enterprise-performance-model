"""Tests for core 2.2.0 (EPM-DEC-001-0076): it is core 2.1.0 plus the process-map changes since 2.0.0, with no
IRI removed; the new concepts, IDs and scope notes are the ones the map holds; the APQC 19948 and RF 1.2
checks land as decided; and the package is the approved, current release. Expected values are written
out by hand.

Run: python3 -m pytest test_build_core_2_2.py (needs rdflib, pyshacl).
"""
import json
import os
import re
import unittest

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

import build_core_2_2 as b

G, COUNTS = b.build()
BASE = Graph().parse(os.path.join(b.BASE, "core.ttl"))
P = b.PROC


def c(slug):
    return URIRef(P + slug)


NEW = {
    "CM-1-1-3-7-13": ("CM 1.1.3.7.13", "CM-1-1-3-7", 5), "CM-1-2-4-3-8": ("CM 1.2.4.3.8", "CM-1-2-4-3", 5),
    "CM-1-2-4-3-8-1": ("CM 1.2.4.3.8.1", "CM-1-2-4-3-8", 6), "CM-1-2-4-3-8-2": ("CM 1.2.4.3.8.2", "CM-1-2-4-3-8", 6),
    "CM-1-2-5-1-5": ("CM 1.2.5.1.5", "CM-1-2-5-1", 5),
    **{f"RF-1-2-{i}": (f"RF 1.2.{i}", "L2-refinery-asset-reliability-and-turnaround-coordination", 3) for i in range(1, 6)},
    "MS-1-1": ("MS 1.1", "L1-midstream", 2), "MS-1-1-1": ("MS 1.1.1", "MS-1-1", 3), "MS-1-1-2": ("MS 1.1.2", "MS-1-1", 3),
    "MS-1-1-3": ("MS 1.1.3", "MS-1-1", 3), "MS-1-2": ("MS 1.2", "L1-midstream", 2), "MS-1-2-1": ("MS 1.2.1", "MS-1-2", 3),
    "MS-1-2-2": ("MS 1.2.2", "MS-1-2", 3), "MS-1-3": ("MS 1.3", "L1-midstream", 2), "MS-1-3-1": ("MS 1.3.1", "MS-1-3", 3),
    "MS-1-3-2": ("MS 1.3.2", "MS-1-3", 3), "MS-1-4": ("MS 1.4", "L1-midstream", 2), "MS-1-4-1": ("MS 1.4.1", "MS-1-4", 3),
    "MS-1-4-2": ("MS 1.4.2", "MS-1-4", 3),
}
STUB_IDS = {"L1-refining": "RF 1", "L2-refinery-performance-and-risk-coordination": "RF 1.1",
            "L2-refinery-asset-reliability-and-turnaround-coordination": "RF 1.2", "L1-midstream": "MS 1"}
CHANGED = {"CM-1-1-7", "CM-1-2-4-3-6", "CM-1-2-5", "CM-1-2-5-1", "CM-1-3-3-4", "CM-1-3-8-4-6", "L1-midstream",
           "L2-refinery-asset-reliability-and-turnaround-coordination"}
CONFIRMED_19948 = {"CM-1-2-4-1-10", "CM-1-2-4-1-18", "CM-1-2-4-1-19", "L1-midstream", "CM-1-2-4-1-15", "CM-1-2-4-1-7",
                   "CM-1-2-4-1-4", "CM-1-2-4-1-12", "CM-1-2-4-1-16", "CM-1-2-4-1-6", "L1-refining", "CM-1-2-7-2",
                   "CM-1-2-3-1", "CM-1-2-4-1"}
REJECTED_19948 = {"CM-1-2-6-3", "L0-downstream-operations"}


class Release(unittest.TestCase):
    def test_every_2_1_0_triple_is_kept_except_the_header_and_two_apqc_decisions(self):
        header = {(b.ONTOLOGY_IRI, p, o) for p, o in BASE.predicate_objects(b.ONTOLOGY_IRI)
                  if p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.issued, DCTERMS.modified, OWL.priorVersion)}
        review = URIRef(str(b.CORE) + "apqc-mapping-decision/review-link")
        corrected = {(c(s), b.CORE.apqcMappingDecision, review) for s in REJECTED_19948}
        self.assertEqual(set(BASE) - set(G), header | corrected)

    def test_no_iri_is_removed(self):
        self.assertEqual(set(BASE.subjects()) - set(G.subjects()), set())

    def test_the_new_concepts(self):
        concepts = {str(s)[len(P):] for s in G.subjects(RDF.type, SKOS.Concept) if str(s).startswith(P)}
        old = {str(s)[len(P):] for s in BASE.subjects(RDF.type, SKOS.Concept) if str(s).startswith(P)}
        self.assertEqual(concepts - old, set(NEW))
        self.assertEqual(len(concepts), 706)
        for slug, (notation, parent, level) in NEW.items():
            with self.subTest(slug):
                s = c(slug)
                self.assertEqual(str(G.value(s, SKOS.notation)), notation)
                self.assertEqual(G.value(s, SKOS.broader), c(parent))
                self.assertEqual(G.value(s, b.CORE.taxonomyLevel).toPython(), level)
                self.assertEqual(G.value(s, SKOS.inScheme), b.SCHEME)
                self.assertEqual(len(list(G.objects(s, SKOS.prefLabel))), 1)
                self.assertEqual(len(list(G.objects(s, SKOS.definition))), 1)
                self.assertIn("8259354", str(G.value(s, DCTERMS.provenance)))

    def test_a_new_definition_and_scope_note_split_the_map_description(self):
        s = c("CM-1-1-3-7-13")
        self.assertEqual(str(G.value(s, SKOS.prefLabel)), "Reconcile Movement Losses and Gains")
        self.assertTrue(str(G.value(s, SKOS.definition)).startswith("Compare the quantities measured at each end of a movement"))
        self.assertTrue(str(G.value(s, SKOS.definition)).endswith("including transfers of intermediates between refineries."))
        self.assertTrue(str(G.value(s, SKOS.scopeNote)).startswith("Gains and losses come from pressure and temperature changes"))
        self.assertIn("EPM-DEC-001-0048", str(G.value(s, DCTERMS.provenance)))
        # A one-sentence description gives no scope note.
        self.assertIsNone(G.value(c("MS-1-1-1"), SKOS.scopeNote))
        self.assertIn("MPC-P01", str(G.value(c("MS-1-1-1"), DCTERMS.provenance)))

    def test_the_split_keeps_bracketed_full_stops(self):
        self.assertEqual(b.split_description("Do A (see Item 1. Note 2). Then B."), ("Do A (see Item 1. Note 2).", "Then B."))
        self.assertEqual(b.split_description("One sentence only."), ("One sentence only.", ""))

    def test_the_stubs_keep_their_iris_and_gain_their_ids(self):
        for slug, pid in STUB_IDS.items():
            with self.subTest(slug):
                self.assertIsNone(BASE.value(c(slug), SKOS.notation))
                self.assertEqual(str(G.value(c(slug), SKOS.notation)), pid)

    def test_changed_descriptions_become_scope_notes_and_definitions_stay(self):
        for s in CHANGED:
            with self.subTest(s):
                self.assertEqual(G.value(c(s), SKOS.definition), BASE.value(c(s), SKOS.definition))
                added = set(G.objects(c(s), SKOS.scopeNote)) - set(BASE.objects(c(s), SKOS.scopeNote))
                self.assertEqual(len(added), 1)
        # CM 1.1.7's definition was the earlier description; only the added text is the note.
        note = {str(n) for n in G.objects(c("CM-1-1-7"), SKOS.scopeNote)}
        self.assertEqual(len(note), 1)
        self.assertTrue(next(iter(note)).startswith("Inter-refinery transfers of intermediate products (IRT)"))
        # CM 1.2.4.3.6's definition is the workbook's; the map's whole new description is the note.
        added = {str(n) for n in G.objects(c("CM-1-2-4-3-6"), SKOS.scopeNote)} - {str(n) for n in BASE.objects(c("CM-1-2-4-3-6"), SKOS.scopeNote)}
        self.assertEqual(added, {"Report RIN generation, transactions and retirements. A step of environmental compliance "
                                 "credit management (CM 1.2.4.3.8.1)."})

    def test_the_19948_references(self):
        element = b.ELEMENT_19948
        self.assertEqual({str(s)[len(P):] for s in G.subjects(DCTERMS.references, element)}, CONFIRMED_19948 | REJECTED_19948)
        no_candidate = URIRef(str(b.CORE) + "apqc-mapping-decision/no-candidate")
        rejected = URIRef(str(b.CORE) + "apqc-mapping-decision/rejected")
        for s in CONFIRMED_19948:
            self.assertEqual(G.value(c(s), b.CORE.apqcMappingDecision), no_candidate, s)
            self.assertIsNone(G.value(c(s), SKOS.changeNote), s)
        for s in REJECTED_19948:
            self.assertEqual(G.value(c(s), b.CORE.apqcMappingDecision), rejected, s)
            self.assertIn("19948", str(G.value(c(s), SKOS.changeNote)), s)

    def test_rf_1_2_is_no_longer_a_candidate_node(self):
        s = c(b.RF_1_2)
        note = str(G.value(s, SKOS.changeNote))
        self.assertIn("no longer a Candidate node", note)
        self.assertIn("EPM-DEC-001-0063", note)
        # The 2026-09-22 provenance stays as history.
        self.assertEqual(set(G.objects(s, DCTERMS.provenance)), set(BASE.objects(s, DCTERMS.provenance)))
        self.assertEqual({str(x)[len(P):] for x in G.subjects(SKOS.broader, s)}, {f"RF-1-2-{i}" for i in range(1, 6)})

    def test_the_figures(self):
        self.assertEqual(len(G), 19810)
        self.assertEqual({k: v for k, v in COUNTS.items() if not k.startswith(("facts ", "evidence", "canonical"))},
                         {"process concepts": 706, "new concepts": 23, "IDs on stubs": 4, "changed descriptions": 8,
                          "19948 references rejected": 2, "19948 references confirmed": 14})
        self.assertEqual(COUNTS["canonical facts"], 640)

    def test_the_header(self):
        self.assertEqual(str(G.value(b.ONTOLOGY_IRI, OWL.versionInfo)), "2.2.0")
        self.assertEqual(G.value(b.ONTOLOGY_IRI, OWL.priorVersion), URIRef(f"{b.ONTOLOGY_IRI}/2.1.0"))
        self.assertEqual(G.value(b.ONTOLOGY_IRI, DCTERMS.issued), G.value(b.ONTOLOGY_IRI, DCTERMS.modified))


class Package(unittest.TestCase):
    FILES = b.package(G, COUNTS)

    def test_the_written_package_equals_a_fresh_build(self):
        for name, text in self.FILES.items():
            with open(os.path.join(b.RELEASE_DIR, name)) as f:
                self.assertEqual(f.read(), text, name)

    def test_the_approval_is_the_decision_owners_words_in_the_saved_file(self):
        path, words = b.APPROVAL
        self.assertEqual(words, "release plan approved")
        with open(os.path.join(b.ONTOLOGY, path)) as f:
            body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
        self.assertIn(words, body)
        manifest = json.loads(self.FILES["manifest.json"])
        self.assertEqual(manifest["approval"], {"file": path, "words": words})
        self.assertFalse(manifest["release_candidate"])

    def test_shapes_and_mapping_are_2_1_0s(self):
        for name in ("shapes.ttl", "canonical-facts.csv"):
            with open(os.path.join(b.BASE, name)) as f:
                self.assertEqual(self.FILES[name], f.read(), name)

    def test_the_map_is_read_at_its_pinned_commit(self):
        manifest = json.loads(self.FILES["manifest.json"])
        self.assertEqual(manifest["built_from"]["process map"],
                         f"{b.SOURCE_PATH} at 82593547cc1672cbcf35e13d54244830671dd009")

    def test_the_catalog_lists_four_distributions(self):
        cat = Graph().parse(data=self.FILES["catalog.ttl"], format="turtle")
        names = {str(d).rsplit("/", 1)[1] for d in cat.objects(None, b.prev.prev.DCAT.distribution)}
        self.assertEqual(names, {"core.ttl", "core.jsonld", "shapes.ttl", "canonical-facts.csv"})


class EarlierRelease(unittest.TestCase):
    def test_2_1_0_is_untouched(self):
        import hashlib
        with open(os.path.join(b.BASE, "manifest.json")) as f:
            manifest = json.load(f)
        for name, digest in manifest["files"].items():
            with open(os.path.join(b.BASE, name), "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest, name)


class Guards(unittest.TestCase):
    def test_a_moved_node_stops_the_build(self):
        earlier = b.map_nodes(b.EARLIER_COMMIT)
        current = dict(earlier)
        node, _ = current["CM-1-1-7"]
        current["CM-1-1-7"] = (node, "CM-1-2")
        with self.assertRaises(SystemExit):
            b.changes(base=BASE, earlier=earlier, current=current)

    def test_a_removed_node_stops_the_build(self):
        earlier = b.map_nodes(b.EARLIER_COMMIT)
        current = {k: v for k, v in earlier.items() if k != "CM-1-1-7-1"}
        with self.assertRaises(SystemExit):
            b.changes(base=BASE, earlier=earlier, current=current)

    def test_a_changed_field_other_than_id_or_description_stops_the_build(self):
        earlier = b.map_nodes(b.EARLIER_COMMIT)
        current = dict(earlier)
        node, parent = current["CM-1-1-7"]
        current["CM-1-1-7"] = (dict(node, name="Renamed"), parent)
        with self.assertRaises(SystemExit):
            b.changes(base=BASE, earlier=earlier, current=current)


if __name__ == "__main__":
    unittest.main()
