"""Tests for build_core.py: conservation, no intake:, no blank nodes, the SHACL slice,
the migration rules, and the vocabulary's one kind and one range per property.

Run: python3 -m pytest test_build_core.py (needs rdflib, openpyxl, pyshacl).
"""
import os
import shutil
import sys
import tempfile
import unittest

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_core as b  # noqa: E402

BUILT = b.build()


class Build(unittest.TestCase):
    def test_every_intake_triple_is_migrated_and_none_remains(self):
        graph, counts = BUILT
        rows = b.conservation(counts)
        self.assertEqual(sum(r["source_triples"] for r in rows), 5571)
        self.assertTrue(all(r["source_triples"] == r["migrated"] for r in rows))
        self.assertFalse([t for t in graph if any(str(x).startswith(str(b.INTAKE)) for x in t)])
        self.assertFalse([t for t in graph if any(isinstance(x, BNode) for x in t)])

    def test_measured_figures(self):
        _, counts = BUILT
        self.assertEqual(counts["horizon facet assignments"], 577)       # ledger-v2.md, Q6
        self.assertEqual(counts["blank nodes resolved"], 1003)
        self.assertEqual(counts["cross-functional normalized"], 12)      # Q7
        self.assertEqual(sum(v for k, v in counts.items() if k.startswith("note:")), 491)
        self.assertEqual(sum(v for k, v in counts.items() if k.startswith("label:")), 104)

    def test_shacl_slice_conforms(self):
        conforms, report = b.shacl_report(BUILT[0])
        self.assertTrue(conforms, report)

    def test_canonical_facts_are_direct_triples(self):
        graph, counts = BUILT
        facts = [t for t in graph if str(t[1]).startswith(str(b.CORE)) and
                 str(t[1]).rsplit("/", 1)[1] in ("precedes", "dependsOnOutputOf", "informedBy", "enabledBy",
                                                 "governedBy", "triggeredBy", "constrainedBy", "requires", "assuredBy")
                 and str(t[0]).startswith(str(b.PROC))]
        self.assertEqual(len(facts), counts["canonical facts"])


class Rules(unittest.TestCase):
    def test_note_kinds(self):
        self.assertEqual(b.note_kind("Renamed 2026-09-21 from X."), "provenance")
        self.assertEqual(b.note_kind("Defined narrowly per Hamid's decision (2026-09-18, Option 1)."), "decision-pointer")
        self.assertEqual(b.note_kind("Parked by PTC-001 (step3c-parked-tree-changes.md). Renamed later."), "dual-aspect")
        self.assertEqual(b.note_kind("Batch 21 (2026-09-20). Shared lifecycle step."), "editorial")

    def test_source_tokens_keep_semicolons_inside_annotations(self):
        cell = "SRC-OSHA-PSM-001 — boundary: x; excludes y | SRC-APQC-PCF-001; SRC-FTC-RP-001"
        self.assertEqual(list(b.source_tokens(cell)), [("SRC-OSHA-PSM-001", "boundary: x; excludes y"),
                                                        ("SRC-APQC-PCF-001", ""), ("SRC-FTC-RP-001", "")])


class Negatives(unittest.TestCase):
    def test_two_preflabels_violate_the_slice(self):
        graph = Graph()
        graph += BUILT[0]
        concept = URIRef(str(b.PROC) + "CM-1-1-1")
        graph.add((concept, SKOS.prefLabel, Literal("A second label", lang="en")))
        self.assertFalse(b.shacl_report(graph)[0])

    def test_a_fact_to_a_non_concept_violates_the_slice(self):
        graph = Graph()
        graph += BUILT[0]
        graph.add((URIRef(str(b.PROC) + "CM-1-1-1"), b.CORE.informedBy, URIRef("https://example.org/not-a-concept")))
        self.assertFalse(b.shacl_report(graph)[0])

    def test_an_unmapped_intake_predicate_stops_the_build(self):
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "taxonomy.ttl")
            shutil.copyfile(b.TAXONOMY, path)
            with open(path, "a") as f:
                f.write('\n<https://w3id.org/lsc/ontology/process/CM-1-1-1> '
                        '<https://w3id.org/lsc/ontology/intake/newField> "x"@en .\n')
            saved, b.TAXONOMY = b.TAXONOMY, path
            try:
                with self.assertRaises(SystemExit) as stop:
                    b.build()
                self.assertIn("no target for intake:newField", str(stop.exception))
            finally:
                b.TAXONOMY = saved
        finally:
            shutil.rmtree(tmp)


class Vocabulary(unittest.TestCase):
    def test_each_core_property_has_one_kind_and_one_range(self):
        vocab = Graph()
        vocab.parse(b.VOCABULARY)
        kinds = (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
        props = {s for k in kinds for s in vocab.subjects(RDF.type, k)}
        self.assertTrue(props)
        for p in props:
            with self.subTest(property=str(p)):
                self.assertEqual(len([k for k in kinds if (p, RDF.type, k) in vocab]), 1)
                self.assertEqual(len(list(vocab.objects(p, RDFS.range))), 1)
                self.assertIsNotNone(vocab.value(p, SKOS.definition))
                self.assertIsNotNone(vocab.value(p, RDFS.label))


if __name__ == "__main__":
    unittest.main()
