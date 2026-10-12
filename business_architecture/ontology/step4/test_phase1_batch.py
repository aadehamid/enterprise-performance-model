"""Tests for phase1_batch.py: re-pin and adopt, each against a temporary copy of Step 4.

Run: python3 test_phase1_batch.py
"""
import ast
import contextlib
import csv
import io
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase1_batch  # noqa: E402

NEW = "0123456789abcdef0123456789abcdef01234567"


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = fn(*args, **kwargs)
    return result, out.getvalue()


class Step4Copy(unittest.TestCase):
    """A disposable copy of Step 4 and of build/output, so the tests can write."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-phase1-batch-")
        self.step4 = os.path.join(self.tmp, "step4")
        shutil.copytree(HERE, self.step4, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
        self.output = os.path.join(self.tmp, "output")
        os.makedirs(self.output)
        for name in ("step3-taxonomy.ttl", "step2-identity-map.json"):
            with open(os.path.join(self.output, name), "w") as f:
                f.write(f"rebuilt {name}\n")
        with open(os.path.join(self.step4, "PINNED_SHA.txt")) as f:
            self.old = f.read().strip()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self, name):
        with open(os.path.join(self.step4, name)) as f:
            return f.read()


class Repin(Step4Copy):
    def test_dry_run_counts_rows_and_writes_nothing(self):
        before = {n: self.read(n) for n in phase1_batch.SHA_FILES + ["PINNED_SHA.txt", "release-checklist.md"]}
        total, out = quiet(phase1_batch.repin, self.step4, self.output, NEW, "test", write=False)
        self.assertGreater(total, 0)
        self.assertIn(f"{total:,} rows in 7 CSVs", out)
        self.assertEqual(before, {n: self.read(n) for n in before})

    def test_write_restamps_only_the_sha_column(self):
        before = {n: self.read(n) for n in phase1_batch.SHA_FILES}
        total, _ = quiet(phase1_batch.repin, self.step4, self.output, NEW, "test batch", write=True, today="2026-10-12")
        stamped = 0
        for name in phase1_batch.SHA_FILES:
            after = self.read(name)
            self.assertEqual(after, before[name].replace(self.old, NEW))
            stamped += sum(1 for r in csv.DictReader(io.StringIO(after)) if r["baseline_sha"] == NEW)
        self.assertEqual(stamped, total)
        self.assertEqual(self.read("PINNED_SHA.txt"), NEW + "\n")
        self.assertEqual(self.read("baseline/step3-taxonomy.ttl"), "rebuilt step3-taxonomy.ttl\n")
        self.assertEqual(self.read("baseline/step2-identity-map.json"), "rebuilt step2-identity-map.json\n")
        self.assertIn(f"- **PINNED_SHA:** `{NEW}` (re-pinned 2026-10-12 for test batch, from `{self.old}`",
                      self.read("release-checklist.md"))
        self.assertIn(f"**Baseline:** `{NEW}` (re-pinned 2026-10-12 for test batch; was `{self.old}`).",
                      self.read("verb-predicate-mapping-v2.md"))

    def test_write_keeps_the_previous_pin_statements_word_for_word(self):
        checklist_pin = phase1_batch.CHECKLIST_PIN.search(self.read("release-checklist.md")).group(0)
        mapping_pin = phase1_batch.MAPPING_PIN.search(self.read("verb-predicate-mapping-v2.md")).group(0)
        quiet(phase1_batch.repin, self.step4, self.output, NEW, "test", write=True)
        self.assertIn("  - Previous pin: " + checklist_pin.replace("- **PINNED_SHA:** ", "", 1),
                      self.read("release-checklist.md"))
        self.assertIn("*Previous baseline:* " + mapping_pin.replace("**Baseline:** ", "", 1),
                      self.read("verb-predicate-mapping-v2.md"))

    def test_missing_build_output_stops_before_any_write(self):
        os.remove(os.path.join(self.output, "step2-identity-map.json"))
        before = {n: self.read(n) for n in phase1_batch.SHA_FILES + ["PINNED_SHA.txt"]}
        with self.assertRaises(FileNotFoundError):
            quiet(phase1_batch.repin, self.step4, self.output, NEW, "test", write=True)
        self.assertEqual(before, {n: self.read(n) for n in before})

    def test_sha_files_match_the_evidence_gate(self):
        tree = ast.parse(self.read("evidence-gate.py"))
        gate = next(ast.literal_eval(n.value) for n in ast.walk(tree)
                    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "sha_files")
        self.assertEqual(gate, phase1_batch.SHA_FILES)

    def test_refuses_a_row_stamped_with_another_pin(self):
        path = os.path.join(self.step4, phase1_batch.SHA_FILES[0])
        with open(path) as f:
            raw = f.read()
        with open(path, "w") as f:
            f.write(raw.replace(self.old, "f" * 40, 1))
        with self.assertRaises(SystemExit) as stop:
            quiet(phase1_batch.repin, self.step4, self.output, NEW, "test", write=True)
        self.assertIn("not stamped", str(stop.exception))
        self.assertEqual(self.read("PINNED_SHA.txt").strip(), self.old)

    def test_refuses_the_old_pin_outside_the_sha_column(self):
        path = os.path.join(self.step4, phase1_batch.SHA_FILES[0])
        with open(path) as f:
            rows = list(csv.reader(f))
        rows[1][0] = rows[1][0] + " " + self.old
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows(rows)
        with self.assertRaises(SystemExit) as stop:
            quiet(phase1_batch.repin, self.step4, self.output, NEW, "test", write=True)
        self.assertIn("outside the baseline_sha column", str(stop.exception))

    def test_refuses_a_short_or_unchanged_sha(self):
        for bad in ("abc123", self.old):
            with self.assertRaises(SystemExit):
                quiet(phase1_batch.repin, self.step4, self.output, bad, "test", write=False)


class Adopt(Step4Copy):
    def edit_governed_fact(self, row_id):
        """Change the governed canonical-facts.csv row carrying row_id, so the re-run differs from it."""
        path = os.path.join(self.step4, "canonical-facts.csv")
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        target = next(r for r in rows if row_id in r["row_ids"].split(";"))
        rows.remove(target)
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return target

    def first_fact_row(self):
        with open(os.path.join(self.step4, "canonical-facts.csv"), newline="") as f:
            return next(csv.DictReader(f))["row_ids"].split(";")[0]

    def set_contributors(self, row_ids_before, row_ids_after):
        """Rewrite the governed fact carrying exactly row_ids_before so it carries row_ids_after."""
        path = os.path.join(self.step4, "canonical-facts.csv")
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        target = next(r for r in rows if r["row_ids"] == row_ids_before)
        target["row_ids"] = row_ids_after
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def shared_fact(self):
        with open(os.path.join(self.step4, "canonical-facts.csv"), newline="") as f:
            return next(r["row_ids"] for r in csv.DictReader(f) if r["row_ids"].count(";") >= 1)

    def test_the_pipeline_reproduces_the_governed_files_byte_for_byte(self):
        tmp = tempfile.mkdtemp(dir=self.tmp)
        new_ctx, new_facts = phase1_batch._proposals(self.step4, tmp)
        for new, governed in ((new_ctx, "target-report/context-pass.csv"), (new_facts, "canonical-facts.csv")):
            with open(new, "rb") as a, open(os.path.join(self.step4, governed), "rb") as b:
                self.assertEqual(a.read(), b.read(), governed)
        status, out = quiet(phase1_batch.adopt, self.step4, set(), write=False)
        self.assertEqual(status, 0, out)
        self.assertIn("facts added: 0, removed: 0, changed: 0", out)

    def test_stops_when_a_shared_fact_gains_a_row_outside_the_batch(self):
        ids = self.shared_fact()
        first, rest = ids.split(";", 1)
        self.set_contributors(ids, first)  # the re-run restores `rest`, which is not in the batch
        status, out = quiet(phase1_batch.adopt, self.step4, {first}, write=True)
        self.assertEqual(status, 1, out)
        self.assertIn("rows outside the batch gained or lost", out)

    def test_stops_when_a_shared_fact_loses_a_row_outside_the_batch(self):
        ids = self.shared_fact()
        self.set_contributors(ids, ids + ";REL-99999")  # the re-run drops REL-99999
        status, out = quiet(phase1_batch.adopt, self.step4, {ids.split(";")[0]}, write=False)
        self.assertEqual(status, 1, out)
        self.assertIn("REL-99999", out)

    def test_accepts_a_shared_fact_whose_changed_rows_are_all_in_the_batch(self):
        ids = self.shared_fact()
        first, rest = ids.split(";", 1)
        self.set_contributors(ids, first)
        status, out = quiet(phase1_batch.adopt, self.step4, set(rest.split(";")), write=False)
        self.assertEqual(status, 0, out)

    def test_an_inherited_step4_override_cannot_redirect_the_context_pass(self):
        other = os.path.join(self.tmp, "other-step4")
        shutil.copytree(self.step4, other, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
        saved = os.environ.get("EPM_STEP4_DIR")
        os.environ["EPM_STEP4_DIR"] = other
        try:
            status, out = quiet(phase1_batch.adopt, self.step4, set(), write=False)
        finally:
            if saved is None:
                del os.environ["EPM_STEP4_DIR"]
            else:
                os.environ["EPM_STEP4_DIR"] = saved
        self.assertEqual(status, 0, out)
        self.assertFalse(os.path.exists(os.path.join(other, "proposal")))

    def test_stops_on_a_fact_outside_the_batch(self):
        self.edit_governed_fact(self.first_fact_row())
        before = self.read("canonical-facts.csv")
        status, out = quiet(phase1_batch.adopt, self.step4, {"REL-99999"}, write=True)
        self.assertEqual(status, 1)
        self.assertIn("STOP fact", out)
        self.assertEqual(self.read("canonical-facts.csv"), before)

    def test_writes_when_every_change_is_in_the_batch(self):
        removed = self.edit_governed_fact(self.first_fact_row())
        status, out = quiet(phase1_batch.adopt, self.step4, set(removed["row_ids"].split(";")), write=True)
        self.assertEqual(status, 0, out)
        self.assertIn("facts added: 1", out)
        status, out = quiet(phase1_batch.adopt, self.step4, set(), write=False)
        self.assertIn("facts added: 0, removed: 0, changed: 0", out)


if __name__ == "__main__":
    unittest.main()
