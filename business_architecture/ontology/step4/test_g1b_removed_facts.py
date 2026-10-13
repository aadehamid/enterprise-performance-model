"""The G1b removed-fact rule (evidence-gate.py): a dependsOnOutputOf fact removed on
2026-09-26 may return only when every row carrying it is an adopted Phase 1 register
row whose approved stored fact is that fact. Each test plants a carrier in a copy of
Step 4 and runs the real gate.

Run: python3 test_g1b_removed_facts.py
"""
import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(os.path.dirname(HERE), "build", "output")
FACT = ("CM-1-1-7-3-1", "core:dependsOnOutputOf", "CM-1-1-7-3-3")  # first fact in the rule's list


class RemovedFactRule(unittest.TestCase):
    def gate(self, carriers):
        tmp = tempfile.mkdtemp(prefix="g1b-")
        try:
            step4 = os.path.join(tmp, "step4")
            shutil.copytree(HERE, step4, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
            os.makedirs(os.path.join(tmp, "build", "output"))
            shutil.copyfile(os.path.join(OUTPUT, "step3-taxonomy.ttl"),
                            os.path.join(tmp, "build", "output", "step3-taxonomy.ttl"))
            path = os.path.join(step4, "canonical-facts.csv")
            with open(path, newline="") as f:
                reader = csv.DictReader(f)
                fields, rows = reader.fieldnames, list(reader)
            rows = [r for r in rows if (r["subject"], r["predicate"], r["object"]) != FACT]
            rows.append({"subject": FACT[0], "predicate": FACT[1], "object": FACT[2],
                         "mention_count": str(len(carriers)), "row_ids": ";".join(carriers),
                         "raw_verbs": ";".join("enables" for _ in carriers), "notes": "planted"})
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            out = subprocess.run([sys.executable, "evidence-gate.py"], cwd=step4, capture_output=True, text=True)
            return out.stdout
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def failed(self, stdout):
        return any(line.startswith("FAIL G1b removed fact absent " + FACT[0]) for line in stdout.splitlines())

    def test_a_carrier_outside_the_register_fails(self):
        self.assertTrue(self.failed(self.gate(["REL-00001"])))

    def test_a_register_row_with_a_different_approved_fact_fails(self):
        with open(os.path.join(HERE, "review-evidence", "phase1-sweep", "register.csv"), newline="") as f:
            other = next(r["row_id"] for r in csv.DictReader(f)
                         if r["stored_fact"] and r["stored_fact"].split() != list(FACT))
        self.assertTrue(self.failed(self.gate([other])))


if __name__ == "__main__":
    unittest.main()
