"""Tests for how classify_v2.py reads intake:relatedConcepts (issue #240): a target holding an
escaped quote or backslash is read whole and decoded, and the row count and the positional
REL IDs of every other row stay the same.

Run: python3 test_classify_v2.py
"""
import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
STEP4 = os.path.dirname(HERE)
sys.path.insert(0, STEP4)
from batch_checks import related_mentions, related_segments, turtle_unescape  # noqa: E402

TTL = os.path.join(STEP4, "baseline", "step3-taxonomy.ttl")


def classify(step4_dir):
    """Run classify_v2.py on a Step 4 directory; return its rows."""
    subprocess.run([sys.executable, os.path.join(HERE, "classify_v2.py")], check=True,
                   env=dict(os.environ, EPM_STEP4_DIR=step4_dir), cwd=HERE,
                   stdout=subprocess.DEVNULL)
    with open(os.path.join(step4_dir, "proposal", "target-report", "target-dispositions-v2.csv"), newline="") as f:
        return list(csv.DictReader(f))


def copy_step4(dest, taxonomy_text):
    os.makedirs(os.path.join(dest, "baseline"))
    shutil.copyfile(os.path.join(STEP4, "PINNED_SHA.txt"), os.path.join(dest, "PINNED_SHA.txt"))
    shutil.copyfile(os.path.join(STEP4, "baseline", "step2-identity-map.json"),
                    os.path.join(dest, "baseline", "step2-identity-map.json"))
    with open(os.path.join(dest, "baseline", "step3-taxonomy.ttl"), "w") as f:
        f.write(taxonomy_text)


class Reader(unittest.TestCase):
    def test_escapes_are_decoded(self):
        self.assertEqual(turtle_unescape(r'Trade \"Capture\" a\\b'), 'Trade "Capture" a\\b')
        bs = chr(92)  # a backslash, built so no editor turns the escapes below into characters
        self.assertEqual(turtle_unescape('caf' + bs + 'u00E9 ' + bs + 'U0001F600'), 'caf' + chr(0xE9) + ' ' + chr(0x1F600))

    def test_a_quoted_target_is_read_whole(self):
        text = ('proc:CM-1-1 a skos:Concept ;\n'
                '    intake:relatedConcepts "enables: Trade \\"Capture\\" (CM-1-2-1-3) | precedes: Next Step"@en .\n'
                'proc:CM-1-2 a skos:Concept ;\n'
                '    intake:relatedConcepts "follows: CM 1.1"@en .\n')
        self.assertEqual(related_mentions(text), [
            ("CM-1-1", "enables", 'Trade "Capture" (CM-1-2-1-3)'),
            ("CM-1-1", "precedes", "Next Step"),
            ("CM-1-2", "follows", "CM 1.1")])
        self.assertEqual(related_segments(text, "CM-1-2"), [("follows", "CM 1.1")])


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(TTL) as f:
            cls.text = f.read()
        cls.tmp = tempfile.mkdtemp()
        copy_step4(os.path.join(cls.tmp, "base"), cls.text)
        cls.base = classify(os.path.join(cls.tmp, "base"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_a_quoted_target_keeps_every_row_and_id(self):
        # The issue's case: give a target of CM-1-1-3-7-9, which has three mentions, a quote
        # and a backslash. Before the fix the cell was cut at the quote.
        rows = [r for r in self.base if r["source_slug"] == "CM-1-1-3-7-9"]
        self.assertEqual(len(rows), 3)
        target = rows[0]["raw_target"]
        start = self.text.index("proc:CM-1-1-3-7-9 a skos:Concept")
        at = self.text.index(target, self.text.index("intake:relatedConcepts", start))
        changed = self.text[:at] + target + r' \"Desk\" a\\b' + self.text[at + len(target):]
        copy_step4(os.path.join(self.tmp, "quoted"), changed)
        out = classify(os.path.join(self.tmp, "quoted"))
        self.assertEqual(len(out), len(self.base))
        self.assertEqual([(r["row_id"], r["source_slug"], r["verb"]) for r in out],
                         [(r["row_id"], r["source_slug"], r["verb"]) for r in self.base])
        moved = [i for i, (a, b) in enumerate(zip(self.base, out)) if a["raw_target"] != b["raw_target"]]
        self.assertEqual(moved, [self.base.index(rows[0])])
        self.assertEqual(out[moved[0]]["raw_target"], target + ' "Desk" a\\b')


if __name__ == "__main__":
    unittest.main()
