"""The G1b removed-fact rule (evidence-gate.py): a dependsOnOutputOf fact removed on
2026-09-26 may return only when every row carrying it is an adopted Phase 1 register
row whose approved stored fact is that fact. Each test sets the carriers of one such
fact in a copy of Step 4 and runs the real gate.

Run: python3 test_g1b_removed_facts.py
"""
import csv
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(os.path.dirname(HERE), "build", "output")


def removed_facts():
    """The facts the gate's G1b removed-fact loop names."""
    with open(os.path.join(HERE, "evidence-gate.py")) as f:
        text = f.read()
    block = text[:text.index('check(f"G1b removed fact absent')]
    block = block[block.rindex("for fact in ("):]
    return re.findall(r'\("([^"]+)", "(core:dependsOnOutputOf)", "([^"]+)"\)', block)


def adopted_register():
    spec = importlib.util.spec_from_file_location("batch_checks_t", os.path.join(HERE, "batch_checks.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open(os.path.join(HERE, "review-evidence", "phase1-sweep", "register.csv"), newline="") as f:
        return {r["row_id"]: r for r in csv.DictReader(f) if r["issue"] in mod.SWEEP_ADOPTED}


def facts():
    with open(os.path.join(HERE, "canonical-facts.csv"), newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


# A removed fact the corrected source restored: carried today only by adopted register
# rows whose approved fact it is.
REGISTER = adopted_register()
_, ROWS = facts()
RESTORED = next((r["subject"], r["predicate"], r["object"]) for r in ROWS
                if (r["subject"], r["predicate"], r["object"]) in set(removed_facts()))
CARRIERS = next(r["row_ids"].split(";") for r in ROWS if (r["subject"], r["predicate"], r["object"]) == RESTORED)


class RemovedFactRule(unittest.TestCase):
    def gate(self, carriers):
        tmp = tempfile.mkdtemp(prefix="g1b-")
        try:
            step4 = os.path.join(tmp, "step4")
            shutil.copytree(HERE, step4, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
            os.makedirs(os.path.join(tmp, "build", "output"))
            shutil.copyfile(os.path.join(OUTPUT, "step3-taxonomy.ttl"),
                            os.path.join(tmp, "build", "output", "step3-taxonomy.ttl"))
            fields, rows = facts()
            for r in rows:
                if (r["subject"], r["predicate"], r["object"]) == RESTORED:
                    r["row_ids"], r["mention_count"] = ";".join(carriers), str(len(carriers))
            with open(os.path.join(step4, "canonical-facts.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            out = subprocess.run([sys.executable, "evidence-gate.py"], cwd=step4, capture_output=True, text=True)
            name = f"G1b removed fact absent {RESTORED[0]}->{RESTORED[2]}"
            return [line.split(" ", 1)[0] for line in out.stdout.splitlines()
                    if name in line and line.startswith(("PASS ", "FAIL "))]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_restored_fact_passes_with_its_approved_carriers(self):
        self.assertTrue(all(c in REGISTER and REGISTER[c]["stored_fact"].split() == list(RESTORED) for c in CARRIERS))
        self.assertEqual(self.gate(CARRIERS), ["PASS"])

    def test_an_extra_carrier_outside_the_register_fails(self):
        self.assertEqual(self.gate(CARRIERS + ["REL-00001"]), ["FAIL"])

    def test_an_adopted_row_whose_approved_fact_differs_fails(self):
        other = next(rid for rid, r in REGISTER.items()
                     if r["stored_fact"] and r["stored_fact"].split() != list(RESTORED))
        self.assertEqual(self.gate([other]), ["FAIL"])
        self.assertEqual(self.gate(CARRIERS + [other]), ["FAIL"])


if __name__ == "__main__":
    unittest.main()
