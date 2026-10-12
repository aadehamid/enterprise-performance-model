"""Tests for phase1_batch.py: re-pin and adopt, each against a temporary copy of Step 4.

Run: python3 test_phase1_batch.py
"""
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

    def test_the_pipeline_reproduces_the_governed_files(self):
        status, out = quiet(phase1_batch.adopt, self.step4, set(), write=False)
        self.assertEqual(status, 0, out)
        self.assertIn("facts added: 0, removed: 0, changed: 0", out)

    def test_stops_on_a_fact_outside_the_batch(self):
        self.edit_governed_fact(self.first_fact_row())
        before = self.read("canonical-facts.csv")
        status, out = quiet(phase1_batch.adopt, self.step4, {"REL-99999"}, write=True)
        self.assertEqual(status, 1)
        self.assertIn("STOP fact", out)
        self.assertEqual(self.read("canonical-facts.csv"), before)

    def test_writes_when_every_change_is_in_the_batch(self):
        row = self.first_fact_row()
        self.edit_governed_fact(row)
        status, out = quiet(phase1_batch.adopt, self.step4, {row}, write=True)
        self.assertEqual(status, 0, out)
        self.assertIn("facts added: 1", out)
        status, out = quiet(phase1_batch.adopt, self.step4, set(), write=False)
        self.assertIn("facts added: 0, removed: 0, changed: 0", out)


if __name__ == "__main__":
    unittest.main()
