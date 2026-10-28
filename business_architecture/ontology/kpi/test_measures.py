"""Tests for the kpi module (Step 7; EPM-DEC-001-0042, EPM-DEC-001-0043): the vocabulary's
properties are well formed, the build reconciles and is current, SHACL accepts the module
and rejects broken measures, and no person's name enters the module.

Run: python3 -m pytest test_measures.py (needs rdflib, pyshacl).
"""
import csv
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
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
# The decision owner's measure list, so this test can check for them without the repo holding them.
NAME_HASHES = {"db42328112177c2d", "326b6af3d84957a1", "6bf3d7f77d878d88", "d095241715e0e35b",
               "4d9cb7a511c6f91c", "431964611ee7be5d", "e1608f75c5d7813f", "0488d02ebacb6b22",
               "c35d6aaf3b3885df"}


POPULATION = Graph()
for _name in ("vocabulary.ttl", "population.ttl"):
    POPULATION.parse(os.path.join(HERE, "..", "population", _name))


def module_graph():
    # Since 1.1.0 the package carries the measure populations too (EPM-DEC-001-0079).
    g = Graph()
    g += VOCAB
    g += MEASURES
    g += POPULATION
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
    def test_the_planner_list_source_is_named_vco_dsv(self):
        # The decision owner named the list's source (answers-2026-10-19-vco-dsv.md); the source keeps its IRI.
        from rdflib.namespace import DCTERMS
        g = Graph().parse(os.path.join(HERE, "measures.ttl"))
        src = bm.SOURCES["planner list"]
        self.assertEqual(str(src), "https://w3id.org/lsc/ontology/source/planner-measure-list-2026-10-18")
        self.assertIn("Value Chain Optimization Decision Support and Visualization (VCO DSV)", str(g.value(src, DCTERMS.title)))
        self.assertEqual(g.value(src, DCTERMS.alternative), Literal("VCO DSV", lang="en"))

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


class Release120(unittest.TestCase):
    # kpi 1.2.0 (EPM-DEC-001-0097, items 3 and 4; EPM-DEC-001-0098, items 3 and 5). Values written out by hand.
    DCT = Namespace("http://purl.org/dc/terms/")

    def test_crack_spreads_carries_kpi_0001(self):
        self.assertEqual(str(MEASURES.value(MEASURE["crack-spreads"], self.DCT.identifier)), "KPI-0001")
        self.assertIn("KPI Crack Spread 3-2-1", str(MEASURES.value(MEASURE["crack-spreads"], SKOS.note)))
        # Since kpi 1.3.0 every measure but the trackers, reports and non-measures carries one (Release130).
        self.assertEqual(len(set(MEASURES.subjects(self.DCT.identifier, None))), 33)

    def test_additional_market_prices_is_narrowed_to_renewables_and_ngls(self):
        m = MEASURE["additional-market-prices"]
        self.assertEqual(MEASURES.value(m, SKOS.prefLabel), Literal("Additional Market Prices (Renewables, NGLs)", lang="en"))
        self.assertNotIn("benchmark", str(MEASURES.value(m, SKOS.definition)).lower())
        self.assertIn("Benchmark, Crude, Renewables, NGLs", str(MEASURES.value(m, SKOS.changeNote)))

    def test_no_alias_repeats_its_measures_name(self):
        for m in MEASURES.subjects(RDF.type, KPI.MeasureDefinition):
            self.assertNotIn(MEASURES.value(m, SKOS.prefLabel), set(MEASURES.objects(m, SKOS.altLabel)), m)

    def test_both_schemes_state_their_top_concepts_both_ways(self):
        for g, scheme, n in ((MEASURES, KPI.Measures, 41), (VOCAB, KPI.MeasureKind, 8)):
            tops = set(g.objects(scheme, SKOS.hasTopConcept))
            self.assertEqual(len(tops), n)
            self.assertEqual(tops, set(g.subjects(SKOS.topConceptOf, scheme)))


class Release130(unittest.TestCase):
    # kpi 1.3.0: the KPI and OPM identifiers (EPM-DEC-001-0109). Values written out by hand.
    DCT = Namespace("http://purl.org/dc/terms/")

    def ident(self, m):
        v = MEASURES.value(MEASURE[m], self.DCT.identifier)
        return str(v) if v is not None else None

    def test_the_counts_by_prefix(self):
        values = [str(o) for o in MEASURES.objects(None, self.DCT.identifier)]
        self.assertEqual(sum(v.startswith("KPI-") for v in values), 3)
        self.assertEqual(sum(v.startswith("OPM-") for v in values), 30)
        self.assertEqual(len(values), len(set(values)))

    def test_the_kpis_and_the_ends_of_the_opm_run(self):
        self.assertEqual(self.ident("crack-spreads"), "KPI-0001")
        self.assertEqual(self.ident("relative-refining-margin-by-region"), "KPI-0002")
        self.assertEqual(self.ident("relative-adjusted-ebitda-per-barrel"), "KPI-0003")
        self.assertEqual(self.ident("unit-utilization"), "OPM-0001")
        self.assertEqual(self.ident("crude-utilization"), "OPM-0002")
        self.assertEqual(self.ident("gasoline-prices"), "OPM-0017")
        self.assertEqual(self.ident("turnaround-lost-margin"), "OPM-0030")

    def test_trackers_reports_and_non_measures_have_none(self):
        for m in ("plan-overview-key-changes", "tar-activities-tracker", "sales-purchase-status",
                  "capital-project-evaluations", "mtp-submission-tracker", "key-activity-tracker",
                  "regional-site-monitoring", "ad-hoc-plan-trends"):
            self.assertIsNone(self.ident(m), m)

    def test_a_crack_spreads_note_says_why_it_keeps_kpi_0001(self):
        self.assertIn("market indicator", str(MEASURES.value(MEASURE["crack-spreads"], SKOS.note)))

    def test_the_build_rejects_an_identifier_off_its_kind(self):
        import tempfile
        from unittest import mock
        with open(bm.IDENTIFIER_TABLE, newline="") as f:
            table = list(csv.DictReader(f))
        cases = (("crude-utilization", "KPI-0099", "needs a OPM-nnnn identifier"),  # a KPI ID on an operational metric
                 ("crack-spreads", "OPM-0099", "must stay KPI-0001"),                # the shared asset's ID changed
                 ("tar-activities-tracker", "OPM-0099", "has no identifier"))          # an ID on a tracker
        for measure, bad, message in cases:
            rows = [dict(r) for r in table if r["measure_id"] != measure] + [{"measure_id": measure, "identifier": bad}]
            with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as t:
                w = csv.DictWriter(t, fieldnames=list(table[0].keys()))
                w.writeheader()
                w.writerows([{k: r.get(k, "") for k in table[0].keys()} for r in rows])
            try:
                with mock.patch.object(bm, "IDENTIFIER_TABLE", t.name), self.assertRaises(SystemExit) as caught:
                    bm.load()
                self.assertIn(message, str(caught.exception), measure)
            finally:
                os.unlink(t.name)


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

    def test_a_tracker_with_a_grain_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((MEASURE["tar-activities-tracker"], KPI.grain,
                                                      Literal("daily")))))

    def test_an_identifier_off_the_pattern_fails(self):
        dct = URIRef("http://purl.org/dc/terms/identifier")
        def edit(g):
            g.remove((MEASURE["margin-capture"], dct, None))
            g.add((MEASURE["margin-capture"], dct, Literal("OPM-25")))
        self.assertFalse(self.broken(edit))

    def test_a_tracker_with_an_identifier_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((MEASURE["tar-activities-tracker"],
                                                      URIRef("http://purl.org/dc/terms/identifier"), Literal("OPM-0099")))))

    def test_an_operational_metric_without_an_identifier_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MEASURE["margin-capture"],
                                                         URIRef("http://purl.org/dc/terms/identifier"), None))))

    def test_a_kpi_with_an_opm_identifier_fails(self):
        dct = URIRef("http://purl.org/dc/terms/identifier")
        def edit(g):
            g.remove((MEASURE["relative-refining-margin-by-region"], dct, None))
            g.add((MEASURE["relative-refining-margin-by-region"], dct, Literal("OPM-0099")))
        self.assertFalse(self.broken(edit))

    def test_a_measure_without_a_definition_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MEASURE["margin-capture"], SKOS.definition, None))))

    def test_a_value_on_a_measure_fails(self):
        # The closed measure shape (EPM-DEC-001-0079): a target or an actual cannot hang off a definition.
        self.assertFalse(self.broken(lambda g: g.add((MEASURE["margin-capture"], URIRef("https://example.org/actual"),
                                                      Literal(0.94)))))
        self.assertFalse(self.broken(lambda g: g.add((MEASURE["margin-capture"], RDF.value, Literal(0.94)))))

    def test_the_populations_conform_and_a_second_one_fails(self):
        pop = Namespace("https://w3id.org/lsc/ontology/modules/population/")
        self.assertIsNotNone(module_graph().value(MEASURE["crack-spreads"], pop.excludes))
        self.assertFalse(self.broken(lambda g: g.add((MEASURE["crack-spreads"], pop.excludes,
                                                      Literal("A second exclusion.", lang="en")))))


def name_tokens(text):
    """Lower-case word tokens, with accents removed and CamelCase split, so a name written
    "Name", "NAME", "name-surname", "NameSurname" or with an accent still matches."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    return set(re.findall(r"[a-z]+", text.lower()))


class Privacy(unittest.TestCase):
    def test_no_person_name_from_the_measure_list_is_in_the_repo(self):
        # EPM-DEC-001-0040: personas stay, the people's names do not. Every tracked file is
        # read, whatever its extension, and so is every file in this folder before it is
        # committed. A file holding a NUL byte is binary and skipped.
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=bm.REPO, capture_output=True, check=True).stdout
        paths = {os.path.join(bm.REPO, os.fsdecode(n)) for n in tracked.split(b"\0") if n}
        paths |= {p for p in glob.glob(os.path.join(HERE, "*")) if os.path.isfile(p)}
        checked = 0
        for path in sorted(p for p in paths if os.path.isfile(p)):
            with open(path, "rb") as f:
                data = f.read()
            if b"\0" in data:
                continue
            checked += 1
            hits = {t for t in name_tokens(data.decode("utf-8", errors="replace"))
                    if hashlib.sha256(t.encode()).hexdigest()[:16] in NAME_HASHES}
            self.assertEqual(hits, set(), os.path.relpath(path, bm.REPO))
        self.assertGreater(checked, 600)

    def test_the_matcher_catches_case_hyphen_camel_case_and_accents(self):
        # A stand-in name, so the test shows the matcher works without naming anyone.
        target = hashlib.sha256(b"placeholder").hexdigest()[:16]
        for text in ("Placeholder", "PLACEHOLDER", "placeholder-person", "PlaceholderPerson", "Pl\u00e1ceholder"):
            with self.subTest(text=text):
                self.assertIn(target, {hashlib.sha256(t.encode()).hexdigest()[:16] for t in name_tokens(text)})


class ValueStreamLinks(unittest.TestCase):
    """MPC-P09: value-stream processes name kpi measures, each with a relationship (EPM-DEC-001-0047)."""

    BP = os.path.join(HERE, "..", "..", "business_process")

    def value_streams(self):
        return {f: json.load(open(f)) for f in sorted(glob.glob(os.path.join(self.BP, "value_stream_*.json")))}

    def links(self):
        for f, vs in self.value_streams().items():
            for stage in vs["stages"]:
                for p in stage["processes"]:
                    for m in p.get("measures", []):
                        yield os.path.basename(f), p["id"], m

    def test_every_linked_measure_is_defined(self):
        ids = {r["measure_id"] for r in rows()}
        for f, process, m in self.links():
            with self.subTest(f=f, process=process, measure=m["measureId"]):
                self.assertIn(m["measureId"], ids)

    def test_p09_links_are_present(self):
        links = [(process, m["measureId"], m["relationship"]) for _, process, m in self.links()]
        got = set(links)
        self.assertEqual(len(links), len(got), "a measure link is listed twice")
        price, perf = "p-market-price-calculation-validation", "p-performance-tracking-analysis"
        self.assertEqual(got, {
            (price, "crack-spreads", "benchmarks"), (price, "rm-margin-per-barrel", "informs"),
            (perf, "rm-margin-per-barrel", "measures-performance"), (perf, "crack-spreads", "benchmarks"),
            (perf, "refining-opex-per-barrel", "measures-performance"),
            (perf, "distribution-cost-per-barrel", "measures-performance"),
            (perf, "turnaround-cost-per-barrel", "measures-performance")})


if __name__ == "__main__":
    unittest.main()
