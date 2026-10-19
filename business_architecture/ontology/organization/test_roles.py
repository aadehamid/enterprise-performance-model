"""Tests for the role register and roles.ttl (Step 5, slice 2; EPM-DEC-001-0031): the register
reconciles with the process map's RACI strings, each broken register fails the build, and the
built roles conform to the organization shapes.

Run: python3 -m pytest test_roles.py (needs rdflib, pyshacl).
"""
import csv
import os
import shutil
import tempfile
import unittest
from unittest import mock

from pyshacl import validate
from rdflib import Graph
from rdflib.namespace import OWL, RDF, SKOS

import build_roles as br

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class RegisterReconciles(unittest.TestCase):
    def test_every_source_string_is_in_the_register_once(self):
        entries, register, roles = br.load()
        self.assertEqual({t for _, _, t in entries}, {r["source_text"] for r in register})
        self.assertEqual(len(register), len({r["source_text"] for r in register}))

    def test_the_figures_match_the_source(self):
        entries, register, roles = br.load()
        f = br.figures(entries, register, roles)
        self.assertEqual(f["processes with RACI"], len({p for p, _, _ in entries}))
        self.assertEqual(f["RACI entries"], len(entries))
        self.assertEqual(f["roles"], f["positions"] + f["teams"])
        # Splitting a compound adds one reference per extra role it names.
        extra = sum(len(r["roles"].split(";")) - 1 for r in register for _, _, t in entries if t == r["source_text"])
        self.assertEqual(f["role references after splitting"], f["RACI entries"] + extra)

    def test_the_figures_match_the_decision_record(self):
        # EPM-DEC-001-0031 states these; a register change that moves them must amend the record too.
        f = br.figures(*br.load())
        self.assertEqual((f["processes with RACI"], f["RACI entries"], f["distinct source strings"], f["roles"],
                          f["positions"], f["teams"], f["compound strings"], f["role references after splitting"]),
                         (153, 913, 91, 60, 54, 6, 11, 940))
        # EPM-DEC-001-0045: Hamid's three merges deprecate three roles; none is deleted.
        self.assertEqual((f["deprecated roles"], f["live roles"]), (3, 57))

    def test_roles_ttl_is_current(self):
        with open(br.OUTPUT) as f:
            written = f.read()
        _, register, roles = br.load()
        self.assertIn(br.build(register, roles).serialize(format="turtle"), written)


class BrokenRegisterFails(unittest.TestCase):
    """Each mutant of the register or the role list must stop the build."""

    def run_mutant(self, register_edit=None, roles_edit=None):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        paths = {}
        for name, source, edit in (("register", br.REGISTER, register_edit), ("roles", br.ROLES, roles_edit)):
            data = rows(source)
            if edit:
                data = edit(data)
            paths[name] = os.path.join(tmp, os.path.basename(source))
            with open(paths[name], "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows(source)[0].keys()))
                w.writeheader()
                w.writerows(data)
        with mock.patch.object(br, "REGISTER", paths["register"]), mock.patch.object(br, "ROLES", paths["roles"]):
            with self.assertRaises(SystemExit):
                br.load()

    def test_unchanged_copies_pass(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        reg, rol = shutil.copy(br.REGISTER, tmp), shutil.copy(br.ROLES, tmp)
        with mock.patch.object(br, "REGISTER", reg), mock.patch.object(br, "ROLES", rol):
            br.load()

    def test_a_missing_source_string_fails(self):
        self.run_mutant(register_edit=lambda d: d[1:])

    def test_a_duplicate_source_string_fails(self):
        self.run_mutant(register_edit=lambda d: d + [d[0]])

    def test_a_string_not_in_the_source_fails(self):
        self.run_mutant(register_edit=lambda d: d + [dict(d[0], source_text="Chief Everything Officer")])

    def test_an_unknown_role_fails(self):
        self.run_mutant(register_edit=lambda d: [dict(d[0], roles="no-such-role")] + d[1:])

    def test_an_unused_role_fails(self):
        self.run_mutant(roles_edit=lambda d: d + [dict(d[0], slug="spare-role", label="Spare Role")])

    def test_a_duplicate_role_label_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(d[0], label=d[1]["label"])] + d[1:])

    def test_a_compound_with_one_role_fails(self):
        def edit(d):
            return [dict(r, roles=r["roles"].split(";")[0]) if "compound" in r["rule"] else r for r in d]
        self.run_mutant(register_edit=edit)

    def test_a_qualifier_rule_without_its_qualifier_fails(self):
        self.run_mutant(register_edit=lambda d: [dict(r, qualifier="") for r in d])

    def test_an_exact_rule_that_differs_from_the_label_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(r, label="GFVC Manager") if r["slug"] == "gfvc-manager" else r for r in d])

    def test_a_case_rule_that_changes_more_than_case_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(r, label="Black Oils Manager") if r["slug"] == "black-oil-manager" else r for r in d])

    def test_an_unknown_raci_key_fails(self):
        with mock.patch.object(br, "LEVELS", ("responsible", "accountable", "consulted")):
            with self.assertRaises(SystemExit):
                br.load()

    def test_a_successor_that_is_not_a_role_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(r, replaced_by="no-such-role") if r["replaced_by"] else r for r in d])

    def test_a_successor_that_is_itself_deprecated_fails(self):
        def edit(d):
            return [dict(r, replaced_by="rcvo-advisor", replaced_label_kind="alt") if r["slug"] == "vp-rvco" else r for r in d]
        self.run_mutant(roles_edit=edit)

    def test_a_merge_without_a_label_kind_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(r, replaced_label_kind="") for r in d])

    def test_two_live_roles_showing_one_name_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(r, preferred_label="Trader") if r["slug"] == "crude-oil-trader" else r for r in d])

    def test_a_team_rule_mapped_to_a_position_fails(self):
        self.run_mutant(roles_edit=lambda d: [dict(r, kind="position") for r in d])


class RolesConform(unittest.TestCase):
    def test_roles_conform_to_the_organization_shapes(self):
        data = Graph().parse(br.OUTPUT)
        conforms, _, text = validate(data, shacl_graph=Graph().parse(os.path.join(HERE, "shapes.ttl")))
        self.assertTrue(conforms, text)

    def test_every_role_has_one_english_name_and_cites_the_process_map(self):
        data = Graph().parse(br.OUTPUT)
        roles = set(data.subjects(RDF.type, br.ORG.Role))
        self.assertEqual(len(roles), len(rows(br.ROLES)))
        for role in roles:
            self.assertEqual(len(list(data.objects(role, SKOS.prefLabel))), 1, role)
            self.assertIn((role, br.DCTERMS.source, br.PROCESS_MAP), data)

    def test_the_misspelling_is_a_hidden_label_and_the_acronym_an_alternative(self):
        data = Graph().parse(br.OUTPUT)
        rvco = br.ROLE["rvco-advisor"]
        self.assertEqual(str(data.value(rvco, SKOS.prefLabel)), "Refinery Value Chain Optimization Advisor")
        self.assertIn("RVCO Advisor", {str(x) for x in data.objects(rvco, SKOS.altLabel)})
        self.assertEqual({str(x) for x in data.objects(rvco, SKOS.hiddenLabel)}, {"RCVO Advisor"})

    def test_every_deprecation_is_true_and_matches_roles_csv(self):
        # The shape checks a boolean only; this pins the value and the set (EPM-DEC-001-0045).
        data = Graph().parse(br.OUTPUT)
        values = list(data.subject_objects(OWL.deprecated))
        self.assertTrue(all(v.toPython() is True for _, v in values))
        self.assertEqual({s for s, _ in values}, {br.ROLE[r["slug"]] for r in rows(br.ROLES) if r["replaced_by"]})

    def test_the_answers_point_the_right_way(self):
        # Hamid's answers 1, 3 and 4 (EPM-DEC-001-0045): which role survives each merge.
        replaced = {r["slug"]: r["replaced_by"] for r in rows(br.ROLES) if r["replaced_by"]}
        self.assertEqual(replaced, {
            "rcvo-advisor": "rvco-advisor",
            "refinery-technical-service-representative": "refinery-technical-representative",
            "vp-clean-products-crude-trading-ngls-asphalt-petchem": "vp-clean-products-rvco-crude-trading-ngls-asphalt-petchem"})
        kept = {r["slug"] for r in rows(br.ROLES) if not r["replaced_by"]}
        self.assertTrue({"forecaster", "local-refinery-forecaster", "crude-rfc", "vp-rvco"} <= kept)

    def test_ten_roles_take_an_expanded_name(self):
        self.assertEqual(sum(1 for r in rows(br.ROLES) if r["preferred_label"]), 10)

    def test_teams_carry_the_team_note_and_positions_do_not(self):
        data = Graph().parse(br.OUTPUT)
        for r in rows(br.ROLES):
            notes = list(data.objects(br.ROLE[r["slug"]], SKOS.scopeNote))
            self.assertEqual(len(notes), 1 if r["kind"] == "team" else 0, r["slug"])


if __name__ == "__main__":
    unittest.main()
