"""EPM-DEC-001-0027: the mirror raw verbs behave like the verbs they mirror.

They map to the same stored form, structural nearness never promotes governs,
and enables grouping sees a provides-input-to dependency. mapping_v2.py,
evidence-gate.py and context_pass.py run as scripts, so this test lifts each
function out of its source and calls it on stub data.

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


    def test_structural_nearness_never_counts_for_governs(self):
        real = function(os.path.join("target-report", "context_pass.py"), "_real", {})
        for verb in ("governed-by", "governs"):
            self.assertEqual(real({"verb": verb}, ["B:structural-nearness"]), [], verb)
        self.assertEqual(real({"verb": "uses-input"}, ["B:structural-nearness"]), ["B:structural-nearness"])

    def test_enables_grouping_sees_the_mirror_dependency(self):
        graph = {}
        env = {"imap": {"S": {"parent_slug": "P1"}, "T": {"parent_slug": "P2"}}, "graph": graph}
        group = function("mapping_v2.py", "enables_group", env)
        row = {"source_slug": "S"}
        self.assertEqual(group(row, "T"), "G3-genuine-enablement")
        graph[("T", "S")] = {"uses-input"}
        self.assertEqual(group(row, "T"), "G1-redundant-output-dep")
        graph.clear()
        graph[("S", "T")] = {"provides-input-to"}
        self.assertEqual(group(row, "T"), "G1-redundant-output-dep")


if __name__ == "__main__":
    unittest.main()
