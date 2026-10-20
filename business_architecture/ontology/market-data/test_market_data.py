"""Tests for the market-data module (Step 7; EPM-DEC-001-0057, EPM-DEC-001-0066): the build is
current, each series' recipe matches MPC Economics', MPC's and CME's wording, a series with a different region, legs or RIN
treatment is a different series, and SHACL accepts the module and rejects broken series.

Run: python3 -m pytest test_market_data.py (needs rdflib, pyshacl).
"""
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_market_data as bm  # noqa: E402

MKT, SERIES, BENCH, REGION, LEG, MEASURE = bm.MKT, bm.SERIES, bm.BENCH, bm.REGION, bm.LEG, bm.MEASURE
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
DATA = Graph().parse(os.path.join(HERE, "market-data.ttl"))
CONTEXT = Graph().parse(bm.MEASURES).parse(os.path.join(HERE, "..", "kpi", "vocabulary.ttl"))


def recipe(series):
    return {(str(DATA.value(l, MKT.benchmark))[len(str(BENCH)):], int(DATA.value(l, MKT.barrels)))
            for l in DATA.objects(SERIES[series], MKT.leg)}


def conforms(g):
    return validate(g + VOCAB + CONTEXT, shacl_graph=SHAPES, advanced=True)[0]


class Build(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_market_data.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_figures(self):
        # Counted by hand from the three tables.
        self.assertEqual(bm.figures(*bm.load()), {"regions": 9, "market regions": 6, "benchmarks": 24, "crude markers": 7,
                                                  "price master ids": 21, "series": 13, "legs": 28})

    def test_recipes(self):
        # MPC FY2025 Form 10-K, Item 7: "three barrels of MEH crude producing two barrels of USGC CBOB gasoline
        # and one barrel of USGC ULSD", and the same pattern for the other regions; CME for the NYMEX spread.
        self.assertEqual(recipe("crack-gulf-coast-3-2-1"), {("meh", 3), ("usgc-cbob", 2), ("usgc-ulsd", 1)})
        self.assertEqual(recipe("crack-mid-continent-3-2-1"), {("wti", 3), ("chicago-cbob", 2), ("chicago-ulsd", 1)})
        self.assertEqual(recipe("crack-west-coast-3-2-1"), {("ans", 3), ("la-carbob", 2), ("la-carb-diesel", 1)})
        self.assertEqual(recipe("crack-nymex-3-2-1"), {("nymex-wti", 3), ("nymex-rbob", 2), ("nymex-ny-harbor-ulsd", 1)})
        # MPC Economics' definition, sections 4.1 and 4.2: each ex-RIN crack deducts the RVO (MPR 13056) from every product barrel.
        self.assertEqual(recipe("crack-mpr-43870"), {("mpr-14133", 3), ("mpr-11926", 2), ("mpr-12838", 1), ("mpr-13056", 3)})
        self.assertEqual(recipe("crack-mpr-37438"), {("mpr-747", 3), ("mpr-16475", 2), ("mpr-16477", 1), ("mpr-13056", 3)})
        self.assertEqual(recipe("crack-mpr-37439"), {("mpr-747", 3), ("mpr-13076", 2), ("mpr-9408", 1), ("mpr-13056", 3)})
        self.assertEqual(recipe("crack-mpr-36855"), {("mpr-4055", 3), ("mpr-9660", 2), ("mpr-9657", 1), ("mpr-13056", 3)})

    def test_legs_unstated(self):
        # The definition names the PNW and SLC series but does not list their input legs (section 4.2, note).
        for series in ("crack-mpr-37443", "crack-mpr-37471"):
            self.assertEqual(DATA.value(SERIES[series], MKT.legsUnstated), Literal(True))
            self.assertEqual(recipe(series), set())

    def test_price_master_ids(self):
        ids = {str(DATA.value(SERIES[s], MKT.priceMasterId)) for s in
               ("crack-mpr-43870", "crack-mpr-37438", "crack-mpr-37439", "crack-mpr-36855", "crack-mpr-37443", "crack-mpr-37471")}
        self.assertEqual(ids, {"43870", "37438", "37439", "36855", "37443", "37471"})
        self.assertEqual(str(DATA.value(SERIES["crack-nymex-3-2-1"], MKT.priceMasterId)), "39998")

    def test_economics_blend(self):
        for blend in ("crack-mpr-37464", "crack-mpr-42023"):
            self.assertEqual(set(DATA.objects(SERIES[blend], MKT.blendOf)),
                             {SERIES["crack-mpr-43870"], SERIES["crack-mpr-37438"], SERIES["crack-mpr-36855"]})
            self.assertIn("before 5 May 2024", str(DATA.value(SERIES[blend], SKOS.scopeNote)))

    def test_blend(self):
        self.assertEqual(set(DATA.objects(SERIES["crack-blended-3-2-1"], MKT.blendOf)),
                         {SERIES["crack-gulf-coast-3-2-1"], SERIES["crack-mid-continent-3-2-1"], SERIES["crack-west-coast-3-2-1"]})
        self.assertFalse(list(DATA.objects(SERIES["crack-blended-3-2-1"], MKT.leg)))

    def test_same_measure_different_series(self):
        series = set(DATA.subjects(MKT.seriesOf, MEASURE["crack-spreads"]))
        self.assertEqual(len(series), 13)
        # MPC's 10-K cracks do not reflect RIN costs; MPC Economics' ex-RIN cracks deduct them (EPM-DEC-001-0066);
        # the exchange spread states nothing about RINs.
        self.assertEqual(DATA.value(SERIES["crack-gulf-coast-3-2-1"], MKT.excludesRINCost), Literal(True))
        for s in ("crack-mpr-43870", "crack-mpr-37438", "crack-mpr-37439", "crack-mpr-36855", "crack-mpr-37443", "crack-mpr-37471",
                  "crack-mpr-37464", "crack-mpr-42023"):
            self.assertEqual(DATA.value(SERIES[s], MKT.excludesRINCost), Literal(False), s)
        for s in ("crack-mid-continent-3-2-1", "crack-west-coast-3-2-1", "crack-blended-3-2-1"):
            self.assertEqual(DATA.value(SERIES[s], MKT.excludesRINCost), Literal(True), s)
        self.assertIsNone(DATA.value(SERIES["crack-nymex-3-2-1"], MKT.excludesRINCost))
        # Same crude and product markets, opposite RIN treatment: two series.
        self.assertNotEqual(SERIES["crack-gulf-coast-3-2-1"], SERIES["crack-mpr-43870"])

    def test_planner_names_resolve(self):
        # The planner list's crack names (kpi measure crack-spreads, classification reason) are MPC Economics'
        # published ex-RIN series, not MPC's 10-K cracks (EPM-DEC-001-0066).
        self.assertEqual(set(DATA.subjects(SKOS.altLabel, Literal("USGC 3-2-1 MEH ex-RIN", lang="en"))), {SERIES["crack-mpr-43870"]})
        self.assertEqual(set(DATA.subjects(SKOS.altLabel, Literal("Chicago WTI 3-2-1 ex-RIN", lang="en"))), {SERIES["crack-mpr-37438"]})
        self.assertEqual(set(DATA.subjects(SKOS.altLabel, Literal("NYMEX 3-2-1", lang="en"))), {SERIES["crack-nymex-3-2-1"]})


class Shapes(unittest.TestCase):
    def test_module_conforms(self):
        self.assertTrue(conforms(DATA))

    def broken(self, edit):
        g = Graph()
        for t in DATA:
            g.add(t)
        edit(g)
        return conforms(g)

    def test_rejects_legs_and_blend(self):
        self.assertFalse(self.broken(lambda g: g.add((SERIES["crack-blended-3-2-1"], MKT.leg, LEG["crack-gulf-coast-3-2-1--meh"]))))

    def test_rejects_a_price(self):
        self.assertFalse(self.broken(lambda g: g.add((BENCH["wti"], MKT.price, Literal(65.5)))))

    def test_rejects_a_price_on_a_leg(self):
        self.assertFalse(self.broken(lambda g: g.add((LEG["crack-gulf-coast-3-2-1--meh"], MKT.price, Literal(65.5)))))

    def test_shared_source_keeps_one_title(self):
        # src:mpc-performance-measures-evidence is also declared by the kpi module (Pi round 1).
        kpi = Graph().parse(bm.MEASURES)
        src = bm.SOURCES["MPC-S01"][0]
        both = set(DATA.objects(src, URIRef("http://purl.org/dc/terms/title"))) | set(kpi.objects(src, URIRef("http://purl.org/dc/terms/title")))
        self.assertEqual(len(both), 1, both)

    def test_rejects_a_value_on_a_region(self):
        self.assertFalse(self.broken(lambda g: g.add((REGION["gulf-coast"], MKT.price, Literal(65.5)))))

    def test_rejects_a_series_of_no_measure(self):
        self.assertFalse(self.broken(lambda g: g.remove((SERIES["crack-west-coast-3-2-1"], MKT.seriesOf, None))))

    def test_rejects_unstated_legs_beside_legs(self):
        self.assertFalse(self.broken(lambda g: g.add((SERIES["crack-mpr-43870"], MKT.legsUnstated, Literal(True)))))

    def test_rejects_a_value_on_a_market_region(self):
        self.assertFalse(self.broken(lambda g: g.add((REGION["pnw"], MKT.price, Literal(65.5)))))

    def test_rejects_a_region_off_the_list(self):
        self.assertFalse(self.broken(lambda g: g.add((SERIES["crack-nymex-3-2-1"], MKT.region, BENCH["wti"]))))


if __name__ == "__main__":
    unittest.main()
