"""Tests for the measure populations (Step 7; EPM-DEC-001-0062): the build is current, the
counts, and pinned statements match MPC's wording in the evidence file.

Run: python3 -m pytest test_population.py (needs rdflib).
"""
import os
import subprocess
import sys
import unittest

from rdflib import Graph

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_population as bp  # noqa: E402

DATA = Graph().parse(os.path.join(HERE, "population.ttl"))


class Population(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_population.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_counts(self):
        rows, total = bp.load()
        # Eight MPC-defined measures; the kpi module has 41 measures.
        self.assertEqual((len(rows), total), (8, 41))

    def test_pinned_statements(self):
        # MPC FY2025 Form 10-K: "Refining operating costs exclude planned turnaround and depreciation and amortization expense."
        self.assertIn("Planned turnaround costs", str(DATA.value(bp.MEASURE["refining-opex-per-barrel"], bp.POP.excludes)))
        # The cracks "do not reflect the market cost of RINs".
        self.assertIn("market cost of RINs", str(DATA.value(bp.MEASURE["crack-spreads"], bp.POP.excludes)))
        # Regional per-barrel margin "excludes inter-refinery transfer volumes".
        self.assertIn("Inter-refinery transfer volumes", str(DATA.value(bp.MEASURE["rm-margin-per-barrel"], bp.POP.excludes)))

    def test_the_decided_eight_and_no_other(self):
        # EPM-DEC-001-0062, item 2: these eight measures, each from the MPC evidence row named here.
        decided = {
            "rm-margin-per-barrel": "row 7 and finding 5", "margin-capture": "row 8",
            "refining-opex-per-barrel": "row 14", "distribution-cost-per-barrel": "row 15",
            "turnaround-cost-per-barrel": "row 16", "crack-spreads": "row 10",
            "relative-refining-margin-by-region": "row 19", "relative-adjusted-ebitda-per-barrel": "row 20"}
        rows, _ = bp.load()
        self.assertEqual({r["measure_id"]: r["evidence"].split(", ", 1)[1] for r in rows}, decided)
        populated = {str(s)[len(str(bp.MEASURE)):] for s in DATA.subjects(bp.POP.includes, None)}
        self.assertEqual(populated, set(decided))

    def test_every_statement_starts_as_decided(self):
        # The opening words of each statement, copied by hand from population.csv as reviewed.
        starts = {
            "rm-margin-per-barrel": ("Sales revenue less the cost of refinery inputs", "Inter-refinery transfer volumes"),
            "margin-capture": ("The company's reported R&M margin", "Regional capture"),
            "refining-opex-per-barrel": ("Refining operating costs, driven mainly", "Planned turnaround costs"),
            "distribution-cost-per-barrel": ("Distribution costs, mainly the long-term agreements", "Depreciation and amortization."),
            "turnaround-cost-per-barrel": ("Planned turnaround and other major maintenance costs", None),
            "crack-spreads": ("The crude and product benchmarks", "The market cost of RINs"),
            "relative-refining-margin-by-region": ("Refining EBITDA per barrel of total throughput", None),
            "relative-adjusted-ebitda-per-barrel": ("ACB Adjusted EBITDA per barrel", None)}
        for m, (inc, exc) in starts.items():
            self.assertTrue(str(DATA.value(bp.MEASURE[m], bp.POP.includes)).startswith(inc), m)
            got = DATA.value(bp.MEASURE[m], bp.POP.excludes)
            self.assertEqual(got is None, exc is None, m)
            if exc:
                self.assertTrue(str(got).startswith(exc), m)


if __name__ == "__main__":
    unittest.main()
