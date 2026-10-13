"""Tests for build_core.py: conservation, no intake:, no blank nodes, the SHACL slice,
the migration rules, and the vocabulary's one kind and one range per property.

Run: python3 -m pytest test_build_core.py (needs rdflib, openpyxl, pyshacl).
"""
import csv
import os
import re
import shutil
import sys
import tempfile
import unittest

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

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


class Destinations(unittest.TestCase):
    """Each intake: value is read from the source taxonomy here, independently of the
    builder, and must sit on its EPM-DEC-001-0029 predicate in the built graph. A swapped
    or reversed mapping fails these even when the conservation counts still balance."""

    @classmethod
    def setUpClass(cls):
        cls.g = BUILT[0]
        cls.base = Graph()
        cls.base.parse(b.TAXONOMY)

    def values(self, name):
        return list(self.base.subject_objects(b.INTAKE[name]))

    def norm(self, text):
        return Literal(" ".join(str(text).split()), lang="en")

    def test_literal_fields_land_on_their_own_predicates(self):
        for name, prop in (("primaryPurpose", b.CORE.primaryPurpose), ("primaryOutput", b.CORE.primaryOutputFlow)):
            for s, v in self.values(name):
                with self.subTest(field=name, concept=str(s)):
                    self.assertIn((s, prop, self.norm(v)), self.g)
        for s, v in self.values("responsibleDomain"):
            expected = "Cross-functional" if str(v).startswith("Cross-functional") else v
            self.assertIn((s, b.CORE.responsibleDomain, self.norm(expected)), self.g)
        for s, v in self.values("keyInputs"):
            for flow in str(v).split("|"):
                if flow.strip():
                    self.assertIn((s, b.CORE.keyInputFlow, self.norm(flow)), self.g)
        for s, v in self.values("parkedChildren"):
            for child in str(v).split("|"):
                if child.strip():
                    self.assertIn((s, b.CORE.plannedChildNote, self.norm(child)), self.g)
                    self.assertNotIn((s, b.CORE.keyInputFlow, self.norm(child)), self.g)

    def test_level_kind_apqc_horizon_and_status(self):
        kinds = {"process": "process", "capability": "capability", "not-process": "structural-anchor"}
        for s, v in self.values("level"):
            self.assertIn((s, b.CORE.taxonomyLevel, Literal(int(str(v)[1:]), datatype=XSD.integer)), self.g)
        for s, v in self.values("conceptTypeCheck"):
            self.assertIn((s, b.CORE.conceptKind, b.CODE["concept-kind"][kinds[str(v)]]), self.g)
        for s, v in self.values("apqcDecision"):
            member = self.g.value(s, b.CORE.apqcMappingDecision)
            self.assertEqual(str(self.g.value(member, SKOS.notation)), str(v))
        # Q6, written out here rather than read from build_core: each value's full set of facets.
        mode, cadence, level = b.CORE.operatingMode, b.CORE.cadence, b.CORE.planningLevel
        periodic = (mode, b.CODE["operating-mode"]["periodic"])
        horizon = {"daily": {periodic, (cadence, b.CODE["cadence"]["daily"])},
                   "weekly": {periodic, (cadence, b.CODE["cadence"]["weekly"])},
                   "monthly": {periodic, (cadence, b.CODE["cadence"]["monthly"])},
                   "periodic": {periodic},
                   "event-driven": {(mode, b.CODE["operating-mode"]["event-driven"])},
                   "continuous": {(mode, b.CODE["operating-mode"]["continuous"])},
                   "tactical": {(level, b.CODE["planning-level"]["tactical"])},
                   "strategic": {(level, b.CODE["planning-level"]["strategic"])}}
        by_concept = {}
        for s, v in self.values("processHorizon"):
            by_concept.setdefault(s, set()).update(horizon[str(v)])
        for s, expected in by_concept.items():
            with self.subTest(concept=str(s)):
                actual = {(p, o) for p in (mode, cadence, level) for o in self.g.objects(s, p)}
                self.assertEqual(actual, expected)
        status = dict((str(v), s) for s, v in self.values("status"))
        self.assertIn((status["retired"], b.CORE.lifecycleStatus, b.CODE["lifecycle-status"]["retired"]), self.g)
        self.assertIn((status["blocked"], b.CORE.holdStatus, b.CODE["hold-status"]["implementation-hold"]), self.g)

    def test_notes_and_sources(self):
        # Q10 split, measured on the baseline (ledger-v2.md status; counts.json): 97 provenance
        # and 3 dual-aspect notes are provenance; 385 editorial and 6 decision-pointer notes
        # are editorial notes. Routing every note one way fails the counts.
        prov = edit = 0
        for s, v in self.values("terminologyNotes"):
            text = self.norm(v)
            on_prov, on_edit = (s, DCTERMS.provenance, text) in self.g, (s, SKOS.editorialNote, text) in self.g
            self.assertTrue(on_prov != on_edit, str(s))
            prov, edit = prov + on_prov, edit + on_edit
            if re.search(r"renam", str(v), re.I):
                self.assertTrue(on_prov, f"{s}: a rename note is provenance")
        self.assertEqual((prov, edit), (100, 391))
        for s, v in self.values("referenceSources"):
            for ident in re.findall(r"SRC-[A-Z0-9-]+", str(v)):
                self.assertIn((s, DCTERMS.source, b.SRC[ident.lower()]), self.g)

    def test_former_names_follow_the_label_report(self):
        with open(b.LABELS, newline="") as f:
            for row in csv.DictReader(f):
                s, label = b.PROC[row["concept_slug"]], self.norm(row["historical_label"])
                searchable = row["label_kind"] == "prior_name" and row["proposed_disposition"] in (
                    "AddAsAltLabel", "RetainAsAltLabel")
                with self.subTest(concept=row["concept_slug"], label=str(label)):
                    self.assertEqual((s, SKOS.altLabel, label) in self.g, searchable)
                    self.assertEqual((s, b.CORE.priorPreferredLabel, label) in self.g, not searchable)

    def test_facts_keep_their_direction(self):
        with open(b.FACTS, newline="") as f:
            rows = list(csv.DictReader(f))
        stored = {(r["subject"], r["predicate"], r["object"]) for r in rows}
        for r in rows:
            p = b.CORE[r["predicate"].split(":", 1)[1]]
            self.assertIn((b.PROC[r["subject"]], p, b.PROC[r["object"]]), self.g)
            if (r["object"], r["predicate"], r["subject"]) not in stored:
                self.assertNotIn((b.PROC[r["object"]], p, b.PROC[r["subject"]]), self.g)

    def test_the_package_is_a_release_candidate_until_approved(self):
        g = self.g
        # Literal on purpose: at the cut, Hamid's approval changes this test with build_core.py.
        self.assertEqual(str(g.value(b.ONTOLOGY_IRI, OWL.versionInfo)), "1.0.0-rc.1")
        self.assertIsNone(g.value(b.ONTOLOGY_IRI, DCTERMS.issued))
        self.assertEqual(len(list(g.objects(b.ONTOLOGY_IRI, DCTERMS.title))), 1)


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

    def test_each_core_property_states_a_cardinality_in_the_slice(self):
        # EPM-DEC-001-0020 rule 2. Code-list and ontology-header properties describe
        # vocabulary terms, not concepts, so the concept slice does not cover them.
        vocab, shapes = Graph(), Graph()
        vocab.parse(b.VOCABULARY)
        shapes.parse(b.SHAPES)
        SH = URIRef("http://www.w3.org/ns/shacl#")
        stated = {shapes.value(n, URIRef(SH + "path")) for n in shapes.subjects(URIRef(SH + "path"), None)
                  if shapes.value(n, URIRef(SH + "maxCount")) is not None
                  or shapes.value(n, URIRef(SH + "minCount")) is not None}
        # A concept property is one the build uses on a process concept, or one whose
        # declared domain is skos:Concept (so an unused one, like governanceStatus, counts).
        concept_props = {p for k in (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
                         for p in vocab.subjects(RDF.type, k)
                         if (p, RDFS.domain, SKOS.Concept) in vocab
                         or any(str(s).startswith(str(b.PROC)) for s in BUILT[0].subjects(p, None))}
        self.assertIn(b.CORE.governanceStatus, concept_props)
        self.assertTrue(concept_props)
        self.assertEqual(sorted(map(str, concept_props - stated)), [])


if __name__ == "__main__":
    unittest.main()
