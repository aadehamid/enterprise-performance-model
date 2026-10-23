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
    def test_q7_lists_loss_control_produced_by_its_process(self):
        # EPM-DEC-001-0048: CM 1.1.3.7.13 produces Loss Control, a link core 2.2.0 made possible (EPM-DEC-001-0076).
        with open(os.path.join(HERE, "queries", "q07a-produces-consumes.rq")) as f:
            rows = {(str(r.process), str(r.relation), str(r.item)) for r in GRAPH.query(f.read())}
        self.assertIn(("https://w3id.org/lsc/ontology/process/CM-1-1-3-7-13",
                       "https://w3id.org/lsc/ontology/modules/value-stream/produces",
                       "https://w3id.org/lsc/ontology/modules/data-product/product/loss-control"), rows)
        with open(os.path.join(HERE, "queries", "q07-no-owning-process.rq")) as f:
            orphans = {str(r.product).rsplit("/", 1)[1] for r in GRAPH.query(f.read())}
        self.assertNotIn("loss-control", orphans)

    def test_the_release_passes(self):
        failures, statuses = run.check(GRAPH, run.load_expected())
        self.assertEqual(failures, [])
        self.assertEqual((statuses["answerable"], statuses["partial"], statuses["waits"], statuses["parked"]), (43, 0, 0, 1))

    def test_q15b_reports_the_systems_in_two_modules_as_one(self):
        # EPM-DEC-001-0069 item 1: three party systems are the system module's nodes of the same name;
        # EPM-DEC-001-0072: the Terminal Margin Ranking System is its TMR, which the party node carries as an alternative label.
        with open(os.path.join(HERE, "queries", "q15b-same-word-linked.rq")) as f:
            rows = [r for r in GRAPH.query(f.read()) if r.link == SKOS.exactMatch]
        party, system = "https://w3id.org/lsc/ontology/modules/party/system/", "https://w3id.org/lsc/ontology/modules/system/system/"
        self.assertEqual({(str(r.a), str(r.b)) for r in rows},
                         {(party + "rightangle", system + "rightangle"), (party + "kittyhawk", system + "kittyhawk"),
                          (party + "profisee", system + "profisee"), (party + "terminal-margin-ranking-system", system + "tmr")})
        self.assertEqual({str(r.word) for r in rows if str(r.a) == party + "terminal-margin-ranking-system"}, {"TMR"})

    def test_an_orphan_fails_q2(self):
        g = Graph()
        g += GRAPH
        g.add((URIRef("https://example.org/orphan"), SKOS.inScheme, MOD))
        failures, _ = run.check(g, run.load_expected())
        self.assertTrue(any(f.startswith("Q2 q02a") for f in failures), failures)

    def test_q8_processes_carry_both_flows_or_neither(self):
        # The worklog's "504 have neither" depends on this: no process has inputs without outputs.
        core = "https://w3id.org/lsc/ontology/modules/core/"
        inputs = set(GRAPH.subjects(URIRef(core + "plannedInput"), None))
        outputs = set(GRAPH.subjects(URIRef(core + "plannedOutput"), None))
        self.assertEqual(inputs, outputs)
        self.assertEqual(len(inputs), 153)

    def test_a_crack_without_its_not_links_fails_q32_and_q36(self):
        g = Graph()
        g += GRAPH
        g.remove((URIRef("https://w3id.org/lsc/ontology/modules/kpi/measure/crack-spreads"),
                  URIRef("https://w3id.org/lsc/ontology/modules/kpi/notToBeConfusedWith"), None))
        failures, _ = run.check(g, run.load_expected())
        self.assertTrue(any(f.startswith("Q32") for f in failures), failures)
        self.assertTrue(any(f.startswith("Q36") for f in failures), failures)

    def test_each_source_has_one_title(self):
        # A source node shared by two modules must carry one title, not one per module.
        title = URIRef("http://purl.org/dc/terms/title")
        many = {s for s in set(GRAPH.subjects(title, None)) if len(set(GRAPH.objects(s, title))) > 1}
        self.assertEqual(many, set())

    def test_an_empty_graph_fails_every_query(self):
        failures, _ = run.check(Graph(), run.load_expected())
        self.assertEqual(len([f for f in failures if "no rows" in f]), 55)  # 45 before the `party` module, plus its 10 row-returning queries

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

    def test_a_ship_to_role_fails_q21(self):
        role = URIRef("https://w3id.org/lsc/ontology/modules/party/party-role/ship-to")
        failures = self.mutated(lambda g: (g.add((role, SKOS.inScheme, URIRef("https://w3id.org/lsc/ontology/modules/party/party-role"))),
                                           g.add((role, SKOS.prefLabel, Literal("Ship-To", lang="en")))))
        self.assertIn("Q21 q21c-no-ship-to-role.rq: 1 rows, expected none", failures)

    def test_a_customer_class_of_party_fails_q24(self):
        cust = "https://w3id.org/lsc/ontology/modules/party/"
        failures = self.mutated(lambda g: g.add((URIRef(cust + "Customer"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"), URIRef(cust + "Party"))))
        self.assertIn("Q24 q24b-no-customer-class.rq: 1 rows, expected none", failures)

    def test_the_role_labels_alone_fail_q24(self):
        # Q24 asks how one party holds several roles: keeping the three role labels but removing every
        # role a party plays must fail it (Codex HOLD on #333).
        plays = URIRef("https://w3id.org/lsc/ontology/modules/party/plays")
        failures = self.mutated(lambda g: g.remove((None, plays, None)))
        self.assertTrue(any(f.startswith("Q24 q24a-one-party-many-roles.rq") for f in failures), failures)

    def test_a_waiting_question_with_a_query_fails(self):
        rows = run.load_expected()
        rows[16] = dict(rows[16], status="waits:EPM-DEC-001-0045", queries="q01a-children.rq")
        failures, _ = run.check(GRAPH, rows)
        self.assertIn("Q17: waits but lists queries", failures)

    def test_a_parked_question_with_a_query_fails(self):
        rows = run.load_expected()
        self.assertEqual(rows[16]["status"], "parked:EPM-DEC-001-0086")  # Q17, parked by the decision owner
        rows[16] = dict(rows[16], queries="q01a-children.rq")
        failures, _ = run.check(GRAPH, rows)
        self.assertIn("Q17: parked but lists queries", failures)


if __name__ == "__main__":
    unittest.main()
