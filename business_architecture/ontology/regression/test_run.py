"""Tests for run.py: expected.csv covers the 44 locked questions, every query file is
used, the release passes, and a broken graph fails."""
import os
import re
import sys
import unittest

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402

GRAPH = Graph()
GRAPH.parse(run.RELEASE)
MOD = URIRef("https://w3id.org/lsc/ontology/modules/core")


class Coverage(unittest.TestCase):
    def test_one_row_per_locked_question(self):
        with open(run.QUESTIONS) as f:
            numbers = [int(n) for n in re.findall(r"^(\d+)\. ", f.read(), re.M)]
        self.assertEqual(numbers, list(range(1, 45)))
        self.assertEqual([int(r["question"]) for r in run.load_expected()], numbers)

    def test_every_query_file_is_listed_once(self):
        listed = [q for r in run.load_expected() for q in r["queries"].split(";") if q]
        self.assertEqual(sorted(listed), sorted(os.listdir(os.path.join(HERE, "queries"))))
        self.assertEqual(len(listed), len(set(listed)))

    def test_each_waiting_question_names_what_it_waits_for(self):
        for r in run.load_expected():
            if r["status"] != "answerable":
                self.assertTrue(r["waits_for"], r["question"])


class Release(unittest.TestCase):
    def test_the_release_passes(self):
        failures, statuses = run.check(GRAPH, run.load_expected())
        self.assertEqual(failures, [])
        self.assertEqual((statuses["answerable"], statuses["partial"], statuses["waits"]), (5, 3, 36))

    def test_an_orphan_fails_q2(self):
        g = Graph()
        g += GRAPH
        g.add((URIRef("https://example.org/orphan"), SKOS.inScheme, MOD))
        failures, _ = run.check(g, run.load_expected())
        self.assertTrue(any(f.startswith("Q2 q02a") for f in failures), failures)

    def test_an_empty_graph_fails_every_query(self):
        failures, _ = run.check(Graph(), run.load_expected())
        self.assertEqual(len([f for f in failures if "no rows" in f]), 8)

    def test_a_waiting_question_with_a_query_fails(self):
        rows = run.load_expected()
        rows[2] = dict(rows[2], queries="q01a-children.rq")
        failures, _ = run.check(GRAPH, rows)
        self.assertIn("Q3: waits but lists queries", failures)


if __name__ == "__main__":
    unittest.main()
