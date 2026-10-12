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


if __name__ == "__main__":
    unittest.main()
