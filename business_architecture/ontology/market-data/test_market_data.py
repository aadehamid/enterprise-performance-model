"""Tests for the market-data module (Step 7; EPM-DEC-001-0057): the build is current, each
series' recipe matches MPC's and CME's wording, a series with a different region, legs or RIN
treatment is a different series, and SHACL accepts the module and rejects broken series.

Run: python3 -m pytest test_market_data.py (needs rdflib, pyshacl).
"""
import os
import subprocess
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal
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
        self.assertEqual(bm.figures(*bm.load()), {"regions": 3, "benchmarks": 12, "crude markers": 4, "series": 5, "legs": 12})

    def test_recipes(self):
        # MPC FY2025 Form 10-K, Item 7: "three barrels of MEH crude producing two barrels of USGC CBOB gasoline
        # and one barrel of USGC ULSD", and the same pattern for the other regions; CME for the NYMEX spread.
        self.assertEqual(recipe("crack-gulf-coast-3-2-1"), {("meh", 3), ("usgc-cbob", 2), ("usgc-ulsd", 1)})
        self.assertEqual(recipe("crack-mid-continent-3-2-1"), {("wti", 3), ("chicago-cbob", 2), ("chicago-ulsd", 1)})
        self.assertEqual(recipe("crack-west-coast-3-2-1"), {("ans", 3), ("la-carbob", 2), ("la-carb-diesel", 1)})
        self.assertEqual(recipe("crack-nymex-3-2-1"), {("nymex-wti", 3), ("nymex-rbob", 2), ("nymex-ny-harbor-ulsd", 1)})

    def test_blend(self):
        self.assertEqual(set(DATA.objects(SERIES["crack-blended-3-2-1"], MKT.blendOf)),
                         {SERIES["crack-gulf-coast-3-2-1"], SERIES["crack-mid-continent-3-2-1"], SERIES["crack-west-coast-3-2-1"]})
        self.assertFalse(list(DATA.objects(SERIES["crack-blended-3-2-1"], MKT.leg)))

    def test_same_measure_different_series(self):
        series = set(DATA.subjects(MKT.seriesOf, MEASURE["crack-spreads"]))
        self.assertEqual(len(series), 5)
        # MPC's cracks exclude RIN costs; the exchange spread states nothing about RINs.
        self.assertEqual(DATA.value(SERIES["crack-gulf-coast-3-2-1"], MKT.excludesRINCost), Literal(True))
        self.assertIsNone(DATA.value(SERIES["crack-nymex-3-2-1"], MKT.excludesRINCost))

    def test_planner_names_resolve(self):
        # The planner list's crack names (kpi measure crack-spreads, classification reason).
        self.assertEqual(set(DATA.subjects(SKOS.altLabel, Literal("USGC 3-2-1 MEH ex-RIN", lang="en"))), {SERIES["crack-gulf-coast-3-2-1"]})
        self.assertEqual(set(DATA.subjects(SKOS.altLabel, Literal("Chicago WTI 3-2-1 ex-RIN", lang="en"))), {SERIES["crack-mid-continent-3-2-1"]})
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

    def test_rejects_a_series_of_no_measure(self):
        self.assertFalse(self.broken(lambda g: g.remove((SERIES["crack-west-coast-3-2-1"], MKT.seriesOf, None))))

    def test_rejects_a_region_off_the_list(self):
        self.assertFalse(self.broken(lambda g: g.add((SERIES["crack-nymex-3-2-1"], MKT.region, BENCH["wti"]))))


if __name__ == "__main__":
    unittest.main()
