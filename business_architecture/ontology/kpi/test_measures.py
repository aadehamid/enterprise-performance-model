"""Tests for the kpi module (Step 7; EPM-DEC-001-0042, EPM-DEC-001-0043): the vocabulary's
properties are well formed, the build reconciles and is current, SHACL accepts the module
and rejects broken measures, and no person's name enters the module.

Run: python3 -m pytest test_measures.py (needs rdflib, pyshacl).
"""
import csv
import glob
import hashlib
import os
import re
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_measures as bm  # noqa: E402

KPI = bm.KPI
KIND = bm.KIND
MEASURE = bm.MEASURE
SH = Namespace("http://www.w3.org/ns/shacl#")
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
MEASURES = Graph().parse(os.path.join(HERE, "measures.ttl"))
CORE = Graph().parse(bm.CORE)
KINDS = (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
PROPS = {p for k in KINDS for p in VOCAB.subjects(RDF.type, k)} | set(VOCAB.subjects(RDFS.domain, None))
# sha256 (first 16 hex digits) of the lower-cased given and family names of the people in
# Hamid's measure list, so this test can check for them without the repo holding them.
NAME_HASHES = {"db42328112177c2d", "326b6af3d84957a1", "6bf3d7f77d878d88", "d095241715e0e35b",
               "4d9cb7a511c6f91c", "431964611ee7be5d", "e1608f75c5d7813f", "0488d02ebacb6b22",
               "c35d6aaf3b3885df"}


def module_graph():
    g = Graph()
    g += VOCAB
    g += MEASURES
    g += CORE
    return g


def conforms(g):
    return validate(g, shacl_graph=SHAPES, advanced=True)[0]


def rows():
    with open(bm.CLASSIFICATION, newline="") as f:
        return list(csv.DictReader(f))


class Vocabulary(unittest.TestCase):
    def test_each_property_has_one_kind_one_range_a_label_and_a_definition(self):
        self.assertTrue(PROPS)
        for p in PROPS:
            with self.subTest(property=str(p)):
                self.assertEqual(len([k for k in KINDS if (p, RDF.type, k) in VOCAB]), 1)
                self.assertEqual(len(list(VOCAB.objects(p, RDFS.range))), 1)
                self.assertIsNotNone(VOCAB.value(p, RDFS.label))
                self.assertIsNotNone(VOCAB.value(p, SKOS.definition))

    def test_every_property_has_a_stated_cardinality(self):
        paths = {}
        for shape in SHAPES.objects(None, SH.property):
            paths.setdefault(SHAPES.value(shape, SH.path), []).append(shape)
        for p in PROPS:
            with self.subTest(property=str(p)):
                self.assertIn(p, paths)
                for shape in paths[p]:
                    self.assertIsNotNone(SHAPES.value(shape, SH.minCount))

    def test_the_measure_kind_list_has_the_eight_kinds_with_definitions(self):
        kinds = set(VOCAB.subjects(SKOS.inScheme, KPI.MeasureKind))
        self.assertEqual({str(k)[len(str(KIND)):] for k in kinds}, set(bm.KINDS))
        for k in kinds:
            self.assertIsNotNone(VOCAB.value(k, SKOS.definition), k)


class Build(unittest.TestCase):
    def test_measures_ttl_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_measures.py"), "--verify"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_row_becomes_one_measure(self):
        ids = [r["measure_id"] for r in rows()]
        built = set(MEASURES.subjects(RDF.type, KPI.MeasureDefinition))
        self.assertEqual(len(ids), 41)
        self.assertEqual(built, {MEASURE[i] for i in ids})

    def test_kinds_and_candidates_match_the_classification(self):
        for r in rows():
            iri = MEASURE[r["measure_id"]]
            self.assertEqual(MEASURES.value(iri, KPI.measureKind), KIND[r["class"]])
            self.assertEqual(MEASURES.value(iri, KPI.kpiCandidate).toPython(), r["kpi_candidate"] == "yes")

    def test_the_figures(self):
        _rows, details, personas, _labels, _procs = bm.load()
        f = bm.figures(_rows, details, personas)
        self.assertEqual((f["kpi"], f["operational-metric"], f["plan-variance-diagnostic"], f["market-indicator"],
                          f["decision-support-indicator"], f["tracker-or-report"], f["alert"], f["not-a-measure"]),
                         (2, 15, 6, 7, 1, 6, 2, 2))
        self.assertEqual(f["KPI candidates"], 6)

    def test_every_process_link_resolves_in_core(self):
        for p in MEASURES.objects(None, KPI.informsProcess):
            self.assertIn((p, RDF.type, SKOS.Concept), CORE, p)


class Shapes(unittest.TestCase):
    def test_the_module_conforms(self):
        self.assertTrue(conforms(module_graph()))

    def broken(self, edit):
        g = module_graph()
        edit(g)
        return conforms(g)

    def test_a_measure_without_a_kind_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MEASURE["crack-spreads"], KPI.measureKind, None))))

    def test_a_measure_with_two_kinds_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((MEASURE["crack-spreads"], KPI.measureKind, KIND.kpi))))

    def test_a_kind_off_the_list_fails(self):
        def edit(g):
            g.remove((MEASURE["crack-spreads"], KPI.measureKind, None))
            g.add((MEASURE["crack-spreads"], KPI.measureKind, URIRef(str(KIND) + "vanity-metric")))
        self.assertFalse(self.broken(edit))

    def test_a_market_indicator_cannot_be_a_kpi_candidate(self):
        def edit(g):
            g.remove((MEASURE["crack-spreads"], KPI.kpiCandidate, None))
            g.add((MEASURE["crack-spreads"], KPI.kpiCandidate, Literal(True)))
        self.assertFalse(self.broken(edit))

    def test_customer_cannot_be_classified_as_a_kpi(self):
        # Competency question 13: a domain concept cannot carry a measure kind.
        customer = URIRef("https://example.org/Customer")
        def edit(g):
            g.add((customer, RDF.type, SKOS.Concept))
            g.add((customer, KPI.measureKind, KIND.kpi))
        self.assertFalse(self.broken(edit))

    def test_a_measure_without_a_source_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MEASURE["margin-capture"], URIRef("http://purl.org/dc/terms/source"), None))))

    def test_a_measure_without_a_definition_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MEASURE["margin-capture"], SKOS.definition, None))))


class Privacy(unittest.TestCase):
    def test_no_person_name_from_the_measure_list_is_in_the_repo(self):
        # EPM-DEC-001-0040: personas stay, the people's names do not. Every tracked text file
        # is checked, plus this folder's files before they are committed.
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=bm.REPO, capture_output=True, check=True).stdout
        paths = {os.path.join(bm.REPO, os.fsdecode(n)) for n in tracked.split(b"\0") if n}
        paths |= {p for p in glob.glob(os.path.join(HERE, "*")) if os.path.isfile(p)}
        text_files = [p for p in paths if re.search(r"\.(md|csv|ttl|py|json|rq|txt|sh|yml)$", p) and os.path.isfile(p)]
        self.assertTrue(text_files)
        for path in sorted(text_files):
            with open(path, encoding="utf-8", errors="replace") as f:
                tokens = set(re.findall(r"[a-z]+", f.read().lower()))
            hits = {t for t in tokens if hashlib.sha256(t.encode()).hexdigest()[:16] in NAME_HASHES}
            self.assertEqual(hits, set(), os.path.relpath(path, bm.REPO))


if __name__ == "__main__":
    unittest.main()
