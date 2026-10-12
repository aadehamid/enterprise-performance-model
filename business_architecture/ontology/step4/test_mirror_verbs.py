"""EPM-DEC-001-0027: the mirror raw verbs map to the stored form of the verb they mirror.

mapping_v2.py and evidence-gate.py run as scripts, so this test lifts the two
mapping functions out of their source and calls them on a stub row.

Run: python3 test_mirror_verbs.py
"""
import ast
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = {  # raw verb -> (subject, predicate, object) for row S -> T
    "provides-input-to": ("T", "core:dependsOnOutputOf", "S"),
    "governs": ("T", "core:governedBy", "S"),
    "uses-input": ("S", "core:dependsOnOutputOf", "T"),
    "governed-by": ("S", "core:governedBy", "T"),
}


def function(filename, name, env):
    with open(os.path.join(HERE, filename)) as f:
        tree = ast.parse(f.read())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, "exec"), env)
    return env[name]


class MirrorVerbs(unittest.TestCase):
    def test_mapping_stored_fact(self):
        stored_fact = function("mapping_v2.py", "stored_fact", {})
        for verb, want in CASES.items():
            got = stored_fact({"source_slug": "S", "verb": verb, "row_id": "REL-99999"}, "T")[:3]
            self.assertEqual(got, want, verb)

    def test_gate_expectation(self):
        env = {"v2d": {}, "_tgt": lambda rid: "T"}
        stored = function("evidence-gate.py", "_stored", env)
        for verb, want in CASES.items():
            env["v2d"]["REL-99999"] = {"source_slug": "S", "verb": verb}
            self.assertEqual(stored("REL-99999"), want, verb)


if __name__ == "__main__":
    unittest.main()
