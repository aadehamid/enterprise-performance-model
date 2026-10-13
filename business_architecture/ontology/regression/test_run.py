"""Tests for run.py: expected.csv covers the 44 locked questions, every query file is
used, the release passes, and a broken graph fails."""
import os
import re
import sys
import unittest

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run  # noqa: E402

GRAPH = run.load(run.RELEASE)
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
        self.assertEqual((statuses["answerable"], statuses["partial"], statuses["waits"]), (8, 5, 31))

    def test_an_orphan_fails_q2(self):
        g = Graph()
        g += GRAPH
        g.add((URIRef("https://example.org/orphan"), SKOS.inScheme, MOD))
        failures, _ = run.check(g, run.load_expected())
        self.assertTrue(any(f.startswith("Q2 q02a") for f in failures), failures)

    def test_an_empty_graph_fails_every_query(self):
        failures, _ = run.check(Graph(), run.load_expected())
        self.assertEqual(len([f for f in failures if "no rows" in f]), 11)

    def mutated(self, change):
        g = Graph()
        g += GRAPH
        change(g)
        return run.check(g, run.load_expected())[0]

    def test_losing_the_planned_child_notes_fails_q2(self):
        note = URIRef("https://w3id.org/lsc/ontology/modules/core/plannedChildNote")
        failures = self.mutated(lambda g: g.remove((None, note, None)))
        self.assertTrue(any(f.startswith("Q2 q02b") for f in failures), failures)

    def test_references_to_a_non_apqc_source_fail_q11(self):
        def rewrite(g):
            other = URIRef("https://w3id.org/lsc/ontology/source/src-api-mpms-001")
            for s, o in list(g.subject_objects(DCTERMS.references)):
                g.remove((s, DCTERMS.references, o))
                g.add((s, DCTERMS.references, other))
        self.assertTrue(any(f.startswith("Q11") for f in self.mutated(rewrite)))

    def test_a_lost_definition_fails_q40(self):
        concept = URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-1")
        failures = self.mutated(lambda g: g.remove((concept, SKOS.definition, None)))
        self.assertTrue(any(f.startswith("Q40") for f in failures), failures)

    def test_a_second_definition_fails_q43(self):
        concept = URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-1")
        failures = self.mutated(lambda g: g.add((concept, SKOS.definition, Literal("A copy.", lang="en"))))
        self.assertTrue(any(f.startswith("Q43") for f in failures), failures)

    def test_a_raci_process_without_an_accountable_role_fails_q4(self):
        orgm = "https://w3id.org/lsc/ontology/modules/organization/"
        accountable = URIRef(orgm + "raci-level/accountable")
        process = URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-2-1")

        def drop(g):
            for a in list(g.subjects(URIRef(orgm + "forProcess"), process)):
                if (a, URIRef(orgm + "raciLevel"), accountable) in g:
                    g.remove((a, None, None))
        failures = self.mutated(drop)
        self.assertTrue(any(f.startswith("Q4 q04b") for f in failures), failures)

    def test_an_assignment_to_a_process_outside_core_fails_q3(self):
        orgm = "https://w3id.org/lsc/ontology/modules/organization/"
        a = next(GRAPH.subjects(URIRef(orgm + "forProcess"), None))
        failures = self.mutated(lambda g: g.set((a, URIRef(orgm + "forProcess"), URIRef("https://example.org/nowhere"))))
        self.assertTrue(any(f.startswith("Q3 q03b") for f in failures), failures)

    def test_an_assignment_on_a_structural_anchor_fails_q3(self):
        orgm = "https://w3id.org/lsc/ontology/modules/organization/"
        kind = URIRef("https://w3id.org/lsc/ontology/modules/core/conceptKind")
        anchor = next(GRAPH.subjects(kind, URIRef("https://w3id.org/lsc/ontology/modules/core/concept-kind/structural-anchor")))
        a = next(GRAPH.subjects(URIRef(orgm + "forProcess"), None))
        failures = self.mutated(lambda g: g.set((a, URIRef(orgm + "forProcess"), anchor)))
        self.assertTrue(any(f.startswith("Q3 q03b") for f in failures), failures)

    def test_a_waiting_question_with_a_query_fails(self):
        rows = run.load_expected()
        rows[5] = dict(rows[5], queries="q01a-children.rq")
        failures, _ = run.check(GRAPH, rows)
        self.assertIn("Q6: waits but lists queries", failures)


if __name__ == "__main__":
    unittest.main()
