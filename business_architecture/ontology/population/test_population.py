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

    def test_no_planner_measure_has_an_invented_population(self):
        self.assertIsNone(DATA.value(bp.MEASURE["unit-utilization"], bp.POP.includes))


if __name__ == "__main__":
    unittest.main()
