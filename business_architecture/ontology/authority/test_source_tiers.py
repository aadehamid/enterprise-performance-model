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


class TierShapes(unittest.TestCase):
    """The integration 2.0.0 shapes on ranks and tiers (EPM-DEC-001-0094). Expected values are written out by hand."""
    AUTH = "https://w3id.org/lsc/ontology/modules/authority/"

    def graph(self):
        g = Graph()
        for part in ("vocabulary.ttl", "source-tiers.ttl"):
            g.parse(os.path.join(HERE, part))
        return g

    def results(self, g):
        from pyshacl import validate
        from rdflib import Namespace
        from rdflib.namespace import RDF
        SH = Namespace("http://www.w3.org/ns/shacl#")
        ok, report, _ = validate(g, shacl_graph=Graph().parse(os.path.join(HERE, "shapes.ttl")), advanced=True)
        return ok, {(report.value(r, SH.focusNode), report.value(r, SH.resultPath), report.value(r, SH.sourceConstraintComponent))
                    for r in report.subjects(RDF.type, SH.ValidationResult)}

    def test_the_ranks(self):
        rank = URIRef(self.AUTH + "rank")
        found = {str(s).rsplit("/", 1)[1]: int(o) for s, o in self.graph().subject_objects(rank)}
        self.assertEqual(found, {"process-authority": 1, "mpc": 2, "peers": 3, "industry": 4, "framework": 5})

    def test_the_tiers_conform(self):
        self.assertTrue(self.results(self.graph())[0])

    def test_a_tier_without_its_rank_fails(self):
        g = self.graph()
        mpc, rank = URIRef(self.AUTH + "tier/mpc"), URIRef(self.AUTH + "rank")
        g.remove((mpc, rank, None))
        ok, found = self.results(g)
        self.assertFalse(ok)
        self.assertIn((mpc, rank, URIRef("http://www.w3.org/ns/shacl#MinCountConstraintComponent")), found)

    def test_a_cited_source_without_its_tier_fails(self):
        # The full graph, which holds the dcterms:source citations the shape targets.
        g = Graph() + GRAPH + self.graph()
        self.assertTrue(self.results(g)[0])
        src, tier_p = URIRef("https://w3id.org/lsc/ontology/source/downstream-process-map"), URIRef(self.AUTH + "evidenceTier")
        self.assertIn(src, set(g.objects(None, DCTERMS.source)))
        g.remove((src, tier_p, None))
        ok, found = self.results(g)
        self.assertFalse(ok)
        self.assertIn((src, tier_p, URIRef("http://www.w3.org/ns/shacl#MinCountConstraintComponent")), found)


if __name__ == "__main__":
    unittest.main()
