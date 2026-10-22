"""Tests for the source tiers (Step 9; EPM-DEC-001-0059): the build is current, every source the
release and the module graphs cite has a tier, and the tiers of sample sources are the ones the
record decided.

Run: python3 -m pytest test_source_tiers.py (needs rdflib).
"""
import os
import subprocess
import sys
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "regression"))
import build_source_tiers as bt  # noqa: E402
import run  # noqa: E402

TIERS = Graph().parse(os.path.join(HERE, "source-tiers.ttl"))
GRAPH = run.load(run.RELEASE)
GRAPH.parse(os.path.join(HERE, "..", "ref-mpc", "ref-mpc.ttl"))  # ref-mpc cites MPC's 10-K and GLEIF (Pi round 1)
SRC = "https://w3id.org/lsc/ontology/source/"


def tier(name):
    iri = URIRef(name if name.startswith("urn:") else SRC + name)
    return str(TIERS.value(iri, bt.AUTH.evidenceTier)).split("/")[-1]


class Tiers(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_source_tiers.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_cited_source_has_a_tier(self):
        cited = set(GRAPH.objects(None, DCTERMS.source))
        missing = {s for s in cited if TIERS.value(s, bt.AUTH.evidenceTier) is None}
        self.assertEqual(missing, set())

    def test_decided_tiers(self):
        # EPM-DEC-001-0059, items 2 to 6, one example per tier.
        self.assertEqual(tier("downstream-process-map"), "process-authority")
        self.assertEqual(tier("mpc-economics-crack-spread-kpi-definition"), "process-authority")  # EPM-DEC-001-0066
        self.assertEqual(tier("step3c-definition-workbook"), "process-authority")
        self.assertEqual(tier("urn:epm:issue:205:comment:6115309253"), "process-authority")
        self.assertEqual(tier("mpc-performance-measures-evidence"), "mpc")
        self.assertEqual(tier("kpi-classification-evidence"), "peers")
        self.assertEqual(tier("src-api-mpms-001"), "industry")
        self.assertEqual(tier("cme-trading-crack-spreads-2024"), "industry")
        self.assertEqual(tier("src-apqc-pcf-001"), "framework")
        self.assertEqual(tier("src-ascm-cscp-001"), "framework")
        self.assertEqual(tier("mpc-s01"), "mpc")
        self.assertEqual(tier("mplx-s01"), "mpc")  # EPM-DEC-001-0071
        self.assertEqual(tier("gleif-lei"), "industry")


if __name__ == "__main__":
    unittest.main()
