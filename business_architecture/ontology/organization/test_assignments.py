"""Tests for the RACI assignments (Step 5, slice 3; EPM-DEC-001-0032): one assignment per
source entry and role, nothing inferred from the hierarchy, a ledger that reconciles, and
SHACL that holds.

Run: python3 -m pytest test_assignments.py (needs rdflib, pyshacl).
"""
import json
import os
import unittest
from collections import Counter
from unittest import mock

from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, OWL, RDF

import build_assignments as ba
import build_roles as br

ENTRIES, REGISTER, GRAPH = ba.build()
ROLES_OF = {r["source_text"]: r["roles"].split(";") for r in REGISTER}
# Organization 2.0.0 (EPM-DEC-001-0045): a deprecated role hands its assignments to its successor.
LIVE = {r["slug"]: r["replaced_by"] or r["slug"] for r in br.read_csv(br.ROLES)}
IRIS = ba.process_iris()
O = br.ORGM


def emitted():
    """(process IRI, level, role slug, source text) for every assignment in the graph."""
    out = Counter()
    for a in GRAPH.subjects(RDF.type, O.ResponsibilityAssignment):
        out[(GRAPH.value(a, O.forProcess), str(GRAPH.value(a, O.raciLevel)).rsplit("/", 1)[1],
             str(GRAPH.value(a, O.assignedRole)).rsplit("/", 1)[1], str(GRAPH.value(a, O.sourceRoleText)))] += 1
    return out


class Assignments(unittest.TestCase):
    def test_each_source_entry_and_role_gives_exactly_one_assignment(self):
        expected = Counter((IRIS[p], lvl, LIVE[role], t) for p, lvl, t in ENTRIES for role in ROLES_OF[t])
        self.assertEqual(emitted(), expected)

    def test_only_processes_with_raci_in_the_source_get_assignments(self):
        # Nothing is inferred from the hierarchy: a parent's RACI does not reach its children.
        self.assertEqual(set(GRAPH.objects(None, O.forProcess)), {IRIS[p] for p, _, _ in ENTRIES})

    def test_the_ledger_reconciles(self):
        rows = dict(ba.ledger(ENTRIES, REGISTER, GRAPH))
        self.assertEqual(rows["RACI entries in the source"] + rows["extra roles from compound strings"],
                         rows["assignments emitted"])
        self.assertEqual(sum(rows[f"assignments at level {lvl}"] for lvl in br.LEVELS), rows["assignments emitted"])
        self.assertEqual(sum(rows[f"entries at level {lvl}"] for lvl in br.LEVELS), rows["RACI entries in the source"])

    def test_the_written_files_are_current(self):
        for path, text in ba.render(ENTRIES, REGISTER, GRAPH).items():
            with open(path) as f:
                self.assertEqual(f.read(), text, path)

    def test_the_assignments_conform(self):
        ba.shacl(GRAPH)  # exits on a violation

    def test_an_assignment_without_a_role_fails_shacl(self):
        g = Graph()
        g += GRAPH
        a = next(g.subjects(RDF.type, O.ResponsibilityAssignment))
        g.remove((a, O.assignedRole, None))
        with self.assertRaises(SystemExit):
            ba.shacl(g)

    def test_a_process_missing_from_the_identity_map_fails(self):
        with mock.patch.object(ba, "process_iris", lambda: {}):
            with self.assertRaises(SystemExit):
                ba.build()

    def test_a_ledger_that_does_not_reconcile_fails(self):
        g = Graph()
        g += GRAPH
        a = next(g.subjects(RDF.type, O.ResponsibilityAssignment))
        g.remove((a, None, None))
        with self.assertRaises(SystemExit):
            ba.ledger(ENTRIES, REGISTER, g)

    def test_iris_do_not_depend_on_list_order(self):
        # The IRI hashes the source string, so it is fixed whatever the entry's position.
        p = IRIS["CM 1.1.2.1"]
        self.assertEqual(str(ba.assignment_iri(p, "accountable", "trader", "Traders")),
                         "https://w3id.org/lsc/ontology/modules/organization/assignment/CM-1-1-2-1--accountable--trader--"
                         + __import__("hashlib").sha256(b"Traders").hexdigest()[:8])
        reversed_entries = list(reversed(ENTRIES))
        with mock.patch.object(br, "raci_entries", lambda node, out: out.extend(reversed_entries) or out):
            _, _, rebuilt = ba.build()
        self.assertEqual(set(rebuilt.subjects(RDF.type, O.ResponsibilityAssignment)),
                         set(GRAPH.subjects(RDF.type, O.ResponsibilityAssignment)))
        self.assertNotEqual(ba.assignment_iri(p, "accountable", "trader", "Traders"),
                            ba.assignment_iri(p, "accountable", "trader", "Supply Coordinators/Traders"))


class RoleMerges(unittest.TestCase):
    """Organization 2.0.0 (EPM-DEC-001-0045): Hamid's three merges deprecate, never delete."""

    RELEASED = os.path.join(br.HERE, "..", "releases", "organization", "1.0.0", "organization.ttl")

    def test_no_assignment_names_a_deprecated_role(self):
        roles = Graph().parse(br.OUTPUT)
        deprecated = {s for s in roles.subjects(OWL.deprecated, Literal(True))}
        self.assertEqual({br.ROLE[s] for s, r in LIVE.items() if r != s}, deprecated)
        self.assertFalse(set(GRAPH.objects(None, O.assignedRole)) & deprecated)

    def test_an_assignment_to_a_deprecated_role_fails_shacl(self):
        g = Graph()
        g += GRAPH
        a = next(g.subjects(O.assignedRole, br.ROLE["rvco-advisor"]))
        g.set((a, O.assignedRole, br.ROLE["rcvo-advisor"]))
        with self.assertRaises(SystemExit):
            ba.shacl(g)

    def test_the_merges_keep_every_released_iri(self):
        # The same assignment IRIs as 1.0.0, and every 1.0.0 role still present.
        released = Graph().parse(self.RELEASED)
        self.assertEqual(set(GRAPH.subjects(RDF.type, O.ResponsibilityAssignment)),
                         set(released.subjects(RDF.type, O.ResponsibilityAssignment)))
        roles = Graph().parse(br.OUTPUT)
        self.assertEqual(set(released.subjects(RDF.type, br.ORG.Role)), set(roles.subjects(RDF.type, br.ORG.Role)))

    def test_a_deprecated_role_keeps_its_triples_and_names_its_successor(self):
        released = Graph().parse(self.RELEASED)
        roles = Graph().parse(br.OUTPUT)
        for slug, successor in ((s, r) for s, r in LIVE.items() if r != s):
            with self.subTest(role=slug):
                for triple in released.triples((br.ROLE[slug], None, None)):
                    self.assertIn(triple, roles)
                self.assertEqual(roles.value(br.ROLE[slug], DCTERMS.isReplacedBy), br.ROLE[successor])

    def test_exactly_the_three_moved_assignments_changed_role(self):
        released = Graph().parse(self.RELEASED)
        moved = {a for a in GRAPH.subjects(RDF.type, O.ResponsibilityAssignment)
                 if GRAPH.value(a, O.assignedRole) != released.value(a, O.assignedRole)}
        self.assertEqual(len(moved), dict(ba.ledger(ENTRIES, REGISTER, GRAPH))["assignments moved to a successor role"])
        self.assertEqual(len(moved), 3)


if __name__ == "__main__":
    unittest.main()
