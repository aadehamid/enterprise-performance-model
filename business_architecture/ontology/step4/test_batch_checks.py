"""Tests for batch_checks.py: a batch's review records must match the saved answer, row by row.

Run: python3 test_batch_checks.py
"""
import copy
import csv
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import batch_checks  # noqa: E402

REVIEW = os.path.join(HERE, "review-evidence", "triggers-batch1-review.csv")
ANSWER = os.path.join(HERE, "review-evidence", "hamid-answers", "204-batch1.md")


def facts():
    with open(os.path.join(HERE, "canonical-facts.csv"), newline="") as f:
        return {(r["subject"], r["predicate"], r["object"]): r["row_ids"].split(";") for r in csv.DictReader(f)}


def v2():
    with open(os.path.join(HERE, "target-report", "target-dispositions-v2.csv"), newline="") as f:
        return {r["row_id"]: r for r in csv.DictReader(f)}


class TriggersBatch1(unittest.TestCase):
    def setUp(self):
        with open(REVIEW, newline="") as f:
            self.rows = list(csv.DictReader(f))
        with open(ANSWER) as f:
            self.answer = f.read()
        self.facts, self.v2 = facts(), v2()

    def problems(self, rows=None, answer=None, fact_rows=None):
        return batch_checks.triggers_batch_problems(
            rows if rows is not None else self.rows, answer if answer is not None else self.answer,
            batch_checks.TRIGGERS_BATCH1_QUESTIONS, self.v2, fact_rows if fact_rows is not None else self.facts)

    def changed(self, row_id, **fields):
        rows = copy.deepcopy(self.rows)
        for r in rows:
            if r["row_id"] == row_id:
                r.update(fields)
        return rows

    def test_the_committed_batch_passes(self):
        self.assertEqual(self.problems(), [])

    def test_a_hold_verdict_is_caught(self):
        self.assertTrue(any("fresh_verdict" in p for p in self.problems(self.changed("REL-00169", fresh_verdict="HOLD"))))

    def test_a_condition_not_in_the_answer_is_caught(self):
        rows = self.changed("REL-00169", condition="A corporate event alone is sufficient; no authorized instruction is required.")
        self.assertTrue(any("condition" in p for p in self.problems(rows)))

    def test_a_partial_condition_is_caught(self):
        # Exclusion-only or event-only fragments drop half of what Hamid decided.
        for fragment in ("a corporate event",
                         "A corporate event alone does not trigger termination or novation; applicable legal, "
                         "credit, and consent requirements remain in force."):
            self.assertTrue(any("condition" in p for p in self.problems(self.changed("REL-00169", condition=fragment))),
                            fragment)

    def test_a_duplicate_answer_number_is_caught(self):
        answer = self.answer.replace("1: b — ", "1: c — “This is not a trigger.”\n\n1: b — ", 1)
        self.assertTrue(any("more than once" in p for p in self.problems(answer=answer)))

    def test_a_malformed_numbered_answer_is_caught(self):
        for line in ("1: c - This is not a trigger.", "1 - c - This is not a trigger.", "  12 c “x y z”"):
            answer = self.answer + "\n" + line + "\n"
            self.assertTrue(any("cannot be read" in p for p in self.problems(answer=answer)), line)

    def test_a_missing_condition_on_a_conditional_row_is_caught(self):
        self.assertTrue(any("condition" in p for p in self.problems(self.changed("REL-00049", condition=""))))

    def test_a_condition_on_an_unconditional_row_is_caught(self):
        rows = self.changed("REL-00396", condition="Referral does not mean the violation has been substantiated.")
        self.assertTrue(any("condition" in p for p in self.problems(rows)))

    def test_answers_swapped_between_rows_are_caught(self):
        rows = copy.deepcopy(self.rows)
        a, b = rows[0], rows[1]
        for col in ("hamid_words", "scope_note_sentence"):
            a[col], b[col] = b[col], a[col]
        self.assertTrue(any("hamid_words" in p for p in self.problems(rows)))

    def test_a_wrong_answer_letter_is_caught(self):
        self.assertTrue(any("hamid_answer" in p for p in self.problems(self.changed("REL-00396", hamid_answer="b"))))

    def test_a_reversed_direction_is_caught(self):
        rows = self.changed("REL-00291", source_slug="CM-1-2-2-3-6", target_slug="CM-1-2-2-3-8")
        self.assertTrue(any("slug" in p for p in self.problems(rows)))

    def test_a_missing_fact_is_caught(self):
        fact_rows = {k: v for k, v in self.facts.items() if "REL-00252" not in v}
        self.assertTrue(any("REL-00252" in p and "fact" in p for p in self.problems(fact_rows=fact_rows)))

    def test_a_missing_or_extra_row_is_caught(self):
        self.assertTrue(any("rows" in p for p in self.problems(self.rows[:-1])))

    def test_an_edited_answer_file_is_caught(self):
        answer = self.answer.replace("Upper-limit breaches", "Lower-limit breaches")
        self.assertTrue(self.problems(answer=answer))


SWEEP = os.path.join(HERE, "review-evidence", "phase1-sweep")


class SweepBatch206(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(SWEEP, "206-review.csv"), newline="") as f:
            self.rows = list(csv.DictReader(f))
        with open(os.path.join(SWEEP, "register.csv"), newline="") as f:
            self.register = {r["row_id"]: r for r in csv.DictReader(f)}
        with open(os.path.join(HERE, "review-evidence", "hamid-answers", "phase1-sweep.md")) as f:
            self.approval = f.read()
        self.facts, self.v2 = facts(), v2()

    def problems(self, rows=None, approval=None, fact_rows=None):
        return batch_checks.sweep_batch_problems(
            "206", rows if rows is not None else self.rows, self.register,
            approval if approval is not None else self.approval, self.v2,
            fact_rows if fact_rows is not None else self.facts)

    def test_the_batch_matches_the_register(self):
        self.assertEqual(self.problems(), [])

    def test_a_changed_sentence_or_fact_is_caught(self):
        for field in ("scope_note_sentence", "stored_fact", "verdict"):
            rows = copy.deepcopy(self.rows)
            rows[0][field] += " (edited)"
            self.assertTrue(any(field in p for p in self.problems(rows=rows)), field)

    def test_a_no_relationship_row_must_stay_off_every_fact(self):
        held = next(r for r in self.rows if r["verdict"] == "no-relationship")
        fact_rows = copy.deepcopy(self.facts)
        fact_rows[("CM-0", "core:governedBy", "CM-1")] = [held["row_id"]]
        self.assertTrue(any(held["row_id"] in p for p in self.problems(fact_rows=fact_rows)))

    def test_an_emitting_row_must_be_on_its_fact(self):
        emit = next(r for r in self.rows if r["verdict"] != "no-relationship")
        fact = tuple(emit["stored_fact"].split())
        fact_rows = copy.deepcopy(self.facts)
        fact_rows[fact] = [x for x in fact_rows[fact] if x != emit["row_id"]]
        self.assertTrue(any(emit["row_id"] in p for p in self.problems(fact_rows=fact_rows)))

    def test_the_approval_words_must_be_saved(self):
        self.assertTrue(self.problems(approval="approved"))

    def test_a_missing_row_or_an_empty_file_is_caught(self):
        dropped = self.rows[0]["row_id"]
        self.assertTrue(any(dropped in p and "no review row" in p for p in self.problems(rows=self.rows[1:])))
        self.assertEqual(sum("no review row" in p for p in self.problems(rows=[])), len(self.rows))

    def test_a_row_from_another_issue_is_caught(self):
        other = next(r for r in self.register.values() if r["issue"] != "206")
        row = dict(self.rows[0], row_id=other["row_id"], issue="206")
        self.assertTrue(any("not #206" in p for p in self.problems(rows=self.rows + [row])))

    def test_a_contradictory_outcome_or_decision_is_caught(self):
        emit = next(i for i, r in enumerate(self.rows) if r["verdict"] != "no-relationship")
        held = next(i for i, r in enumerate(self.rows) if r["verdict"] == "no-relationship")
        for i, field, value in ((emit, "outcome", batch_checks.SWEEP_HELD_OUTCOME),
                                (held, "outcome", "Emitted as core:governedBy"),
                                (emit, "Hamid_decision", "Hamid refused this relationship")):
            rows = copy.deepcopy(self.rows)
            rows[i][field] = value
            self.assertTrue(any(field in p for p in self.problems(rows=rows)), (field, value))

    def test_review_files_match_the_adopted_issues(self):
        names = {f"{i}-review.csv" for i in batch_checks.SWEEP_ADOPTED}
        self.assertEqual(batch_checks.sweep_files_problems(names), [])
        self.assertTrue(batch_checks.sweep_files_problems(set()))
        for extra in ("999-review.csv", "206-copy-review.csv"):
            self.assertTrue(any(extra in p for p in batch_checks.sweep_files_problems(names | {extra})), extra)



class SweepBatch203(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(SWEEP, "203-review.csv"), newline="") as f:
            self.rows = list(csv.DictReader(f))
        with open(os.path.join(SWEEP, "register.csv"), newline="") as f:
            self.register = {r["row_id"]: r for r in csv.DictReader(f)}
        with open(os.path.join(HERE, "review-evidence", "hamid-answers", "phase1-sweep.md")) as f:
            self.approval = f.read()
        self.facts, self.v2 = facts(), v2()
        with open(os.path.join(HERE, "baseline", "step3-taxonomy.ttl")) as f:
            self.taxonomy = f.read()

    def problems(self, fact_rows, rows=None, taxonomy=None):
        return batch_checks.sweep_batch_problems("203", rows if rows is not None else self.rows, self.register,
                                                 self.approval, self.v2, fact_rows,
                                                 taxonomy=taxonomy if taxonomy is not None else self.taxonomy)

    def test_the_batch_matches_the_register(self):
        self.assertEqual(self.problems(self.facts), [])

    def test_a_changed_direction_or_reason_is_caught(self):
        for field, value in (("direction", "as-asserted"), ("reason", "edited")):
            rows = copy.deepcopy(self.rows)
            i = next(i for i, r in enumerate(rows) if r["direction"] == "reversed")
            rows[i][field] = value
            self.assertTrue(any(field in p for p in self.problems(self.facts, rows=rows)), field)

    def test_a_sentence_missing_from_the_published_scope_note_is_caught(self):
        row = next(r for r in self.rows if r["row_id"] == "REL-00263")
        sentence = " ".join(row["scope_note_sentence"].split())
        flat = " ".join(self.taxonomy.split())
        self.assertIn(sentence, flat)
        mutated = self.taxonomy.replace(row["scope_note_sentence"].split(",")[0], "Manage Risk Reporting always consumes", 1)
        self.assertNotEqual(mutated, self.taxonomy)
        self.assertTrue(any("REL-00263" in p and "published scope note" in p
                            for p in self.problems(self.facts, taxonomy=mutated)))

    def test_a_sentence_in_another_concept_or_a_comment_does_not_count(self):
        row = next(r for r in self.rows if r["row_id"] == "REL-00263")
        sentence = row["scope_note_sentence"]
        own = "proc:CM-1-2-2-3-12 a skos:Concept ;\n"
        self.assertIn(own, self.taxonomy)
        stripped = self.taxonomy.replace(sentence, "")
        # Moved into the next concept's statement, whose header is indented.
        moved = stripped.replace("proc:CM-1-2-2-3-13 a skos:Concept ;\n",
                                 f'  proc:CM-1-2-2-3-13 a skos:Concept ;\n    skos:scopeNote """{sentence}"""@en ;\n', 1)
        # Kept only as a comment inside its own statement.
        commented = stripped.replace(own, own + f"    # {sentence}\n", 1)
        for mutated in (moved, commented):
            self.assertNotEqual(mutated, stripped)
            self.assertTrue(any("REL-00263" in p and "published scope note" in p
                                for p in self.problems(self.facts, taxonomy=mutated)))

    def test_scope_notes_reads_only_the_named_subject(self):
        ttl = ('proc:A a skos:Concept ;\n  # skos:scopeNote "in a comment"\n  skos:prefLabel "A"@en ;\n'
               '  skos:scopeNote """one. two"""@en , "three"@en .\n'
               '  proc:B a skos:Concept ;\n  skos:scopeNote "B note"@en .\n')
        self.assertEqual(batch_checks.scope_notes(ttl, "A"), ["one. two", "three"])
        self.assertEqual(batch_checks.scope_notes(ttl, "B"), ["B note"])
        self.assertEqual(batch_checks.scope_notes(ttl, "C"), [])

    def test_a_reverted_relationship_in_the_published_taxonomy_is_caught(self):
        # REL-00263's corrected segment back to enables, with its sentence left in the scope note.
        reverted = self.taxonomy.replace("provides-input-to: Manage Risk Reporting", "enables: Manage Risk Reporting", 1)
        # The uncorrected segment appended beside the corrected one.
        appended = self.taxonomy.replace("provides-input-to: Manage Risk Reporting",
                                         "provides-input-to: Manage Risk Reporting | enables: Manage Risk Reporting", 1)
        for mutated in (reverted, appended):
            self.assertNotEqual(mutated, self.taxonomy)
            self.assertTrue(any("REL-00263" in p and "relatedConcepts" in p
                                for p in self.problems(self.facts, taxonomy=mutated)))

    def test_a_relationship_classify_cannot_read_does_not_count(self):
        # Moved into a triple-quoted literal: valid Turtle, but classify_v2 reads only one-line literals.
        line = next(l for l in self.taxonomy.splitlines()
                    if "provides-input-to: Manage Risk Reporting" in l)
        hidden = self.taxonomy.replace(line, line.replace('"', '"""', 1).replace('"@', '"""@', 1), 1)
        self.assertNotEqual(hidden, self.taxonomy)
        self.assertTrue(any("REL-00263" in p and "relatedConcepts" in p
                            for p in self.problems(self.facts, taxonomy=hidden)))

    def test_sweep_provenance_matches_the_mapping_attachments(self):
        import ast
        with open(os.path.join(HERE, "mapping_v2.py")) as f:
            tree = ast.parse(f.read())
        attach = next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                      and getattr(n.targets[0], "id", "") == "DUPLICATE_PROVENANCE_ATTACH")
        for rid, fact in batch_checks.SWEEP_PROVENANCE.items():
            self.assertEqual(attach.get(rid), fact, rid)

    def test_recorded_provenance_is_allowed_only_on_its_fact(self):
        fact = batch_checks.SWEEP_PROVENANCE["REL-00436"]
        self.assertIn("REL-00436", self.facts[fact])
        moved = copy.deepcopy(self.facts)
        moved[fact] = [x for x in moved[fact] if x != "REL-00436"]
        moved[("CM-0", "core:dependsOnOutputOf", "CM-1")] = ["REL-00436"]
        self.assertTrue(any("REL-00436" in p for p in self.problems(moved)))
        dropped = copy.deepcopy(self.facts)
        dropped[fact] = [x for x in dropped[fact] if x != "REL-00436"]
        self.assertTrue(any("REL-00436" in p for p in self.problems(dropped)))


class SweepBatchesAfter203(unittest.TestCase):
    """#210 and later batches: each matches the register and the published taxonomy, and a
    row on the wrong fact, or a no-relationship row on any fact, is caught."""

    def setUp(self):
        with open(os.path.join(SWEEP, "register.csv"), newline="") as f:
            self.register = {r["row_id"]: r for r in csv.DictReader(f)}
        with open(os.path.join(HERE, "review-evidence", "hamid-answers", "phase1-sweep.md")) as f:
            self.approval = f.read()
        with open(os.path.join(HERE, "baseline", "step3-taxonomy.ttl")) as f:
            self.taxonomy = f.read()
        self.facts, self.v2 = facts(), v2()
        self.issues = [i for i in batch_checks.SWEEP_ADOPTED if i not in ("206", "203")]

    def rows(self, issue):
        with open(os.path.join(SWEEP, f"{issue}-review.csv"), newline="") as f:
            return list(csv.DictReader(f))

    def problems(self, issue, fact_rows):
        return batch_checks.sweep_batch_problems(issue, self.rows(issue), self.register, self.approval, self.v2,
                                                 fact_rows, taxonomy=self.taxonomy)

    def test_each_batch_matches_the_register_and_the_published_taxonomy(self):
        for issue in self.issues:
            with self.subTest(issue=issue):
                self.assertEqual(self.problems(issue, self.facts), [])

    def test_an_emitting_row_on_another_rows_fact_is_caught(self):
        for issue in self.issues:
            emit = [r for r in self.rows(issue) if r["verdict"] != "no-relationship"]
            moved_row, other = emit[0], next(r for r in emit if r["stored_fact"] != emit[0]["stored_fact"])
            fact_rows = copy.deepcopy(self.facts)
            own, wrong = tuple(moved_row["stored_fact"].split()), tuple(other["stored_fact"].split())
            fact_rows[own] = [x for x in fact_rows[own] if x != moved_row["row_id"]]
            fact_rows[wrong] = fact_rows[wrong] + [moved_row["row_id"]]
            with self.subTest(issue=issue, row=moved_row["row_id"]):
                self.assertTrue(any(moved_row["row_id"] in p for p in self.problems(issue, fact_rows)))

    def test_a_no_relationship_row_on_a_fact_is_caught(self):
        for issue in self.issues:
            held = next(r for r in self.rows(issue) if r["verdict"] == "no-relationship")
            fact_rows = copy.deepcopy(self.facts)
            some = next(iter(fact_rows))
            fact_rows[some] = fact_rows[some] + [held["row_id"]]
            with self.subTest(issue=issue, row=held["row_id"]):
                self.assertTrue(any(held["row_id"] in p for p in self.problems(issue, fact_rows)))

if __name__ == "__main__":
    unittest.main()
