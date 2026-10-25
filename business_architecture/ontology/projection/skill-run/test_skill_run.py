"""The skill-run scripts read the same inputs as ../pipeline.py: inputs.py lists exactly its INPUTS and
SHAPES, each file exists, and epm-config.json pins the same packages.

Run: python3 -m pytest test_skill_run.py (needs rdflib, pyshacl).
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(HERE, ".."))
import pipeline  # noqa: E402

ONTOLOGY = os.path.realpath(pipeline.ONTOLOGY)


def listed(kind):
    out = subprocess.run([sys.executable, os.path.join(HERE, "inputs.py"), kind], check=True,
                         capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return out.stdout.splitlines()


class Inputs(unittest.TestCase):
    def test_data_is_pipeline_inputs(self):
        self.assertEqual(listed("data"), [os.path.join(ONTOLOGY, p) for p in pipeline.INPUTS])

    def test_shapes_are_pipeline_shapes(self):
        self.assertEqual(listed("shapes"), [os.path.join(ONTOLOGY, p) for p in pipeline.SHAPES])

    def test_every_listed_file_exists_and_is_absolute(self):
        for path in listed("data") + listed("shapes"):
            self.assertTrue(os.path.isabs(path), path)
            self.assertTrue(os.path.isfile(path), path)
        self.assertTrue(os.path.isdir(listed("releases")[0]))

    def test_the_config_pins_the_pipeline_packages(self):
        with open(os.path.join(HERE, "epm-config.json")) as f:
            config = json.load(f)
        self.assertEqual(config["packages"], dict(pipeline.PACKAGES))

    def test_a_bad_argument_exits_2(self):
        result = subprocess.run([sys.executable, os.path.join(HERE, "inputs.py"), "other"], capture_output=True)
        self.assertEqual(result.returncode, 2)


class Paths(unittest.TestCase):
    def test_relative_paths_become_absolute_before_any_cd(self):
        """common.sh turns relative ONTOLOGY_TO_LPG, ROBOT_JAR and MANUAL_CASES into absolute paths,
        because run.sh, load.sh and aura-copy.sh change directory into the skill before using them."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "skill", "scripts"))
            open(os.path.join(tmp, "skill", "scripts", "build.py"), "w").close()
            script = ('. "$1"; printf "%s\\n" "$ONTOLOGY_TO_LPG" "$ROBOT_JAR" "$MANUAL_CASES" "$SK" "$COMPOSE"')
            env = {**os.environ, "ONTOLOGY_TO_LPG": "skill", "ROBOT_JAR": "robot.jar",
                   "MANUAL_CASES": "cases.json", "LPG_OUT": "out"}
            out = subprocess.run(["bash", "-c", script, "bash", os.path.join(HERE, "common.sh")], cwd=tmp,
                                 env=env, capture_output=True, text=True, check=True).stdout.splitlines()
            real = os.path.realpath(tmp)
            self.assertEqual(out, [os.path.join(real, "skill"), os.path.join(real, "robot.jar"),
                                   os.path.join(real, "cases.json"), os.path.join(real, "skill", "scripts"),
                                   os.path.join(real, "skill", "docker", "compose.yaml")])


class Rebuild(unittest.TestCase):
    """rebuild_inputs.py: the export's graphs map to inputs.py's order, and the two comparisons find a
    planted difference (rebuild.sh step 3)."""

    def setUp(self):
        import tempfile
        sys.path.insert(0, HERE)
        import rebuild_inputs
        self.ri = rebuild_inputs
        self.tmp = tempfile.mkdtemp()

    def write(self, name, text):
        path = os.path.join(self.tmp, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_the_export_maps_to_the_inputs_and_whole_graph_shapes_come_from_the_repository(self):
        head = ("<https://x.org/m> a <http://www.w3.org/2002/07/owl#Ontology> ; "
                "<http://www.w3.org/2002/07/owl#versionIRI> <https://x.org/m/1.0.0> .\n")
        data = self.write("releases/m/1.0.0/m.ttl", head)
        shapes = self.write("releases/m/1.0.0/shapes.ttl", "")
        extra = self.write("other/shapes.ttl", "")
        self.write("export/graphs.tsv", "graph-1.ttl\thttps://x.org/m/1.0.0\ngraph-2.ttl\thttps://x.org/m/1.0.0/shapes\n")
        rows = self.ri.input_list(os.path.join(self.tmp, "export"), [data], [shapes, extra])
        self.assertEqual(rows, [("data", os.path.join(self.tmp, "export", "graph-1.ttl")),
                                ("shapes", os.path.join(self.tmp, "export", "graph-2.ttl")),
                                ("shapes", os.path.abspath(extra), "repository")])

    def test_triples_compare_as_rdf_terms_and_a_changed_value_differs(self):
        xs = "<http://www.w3.org/2001/XMLSchema#string>"
        for side, text in (("a", f'<https://x.org/s> <https://x.org/p> "v"^^{xs} .\n'),
                           ("b", '<https://x.org/s> <https://x.org/p> "v" .\n'),
                           ("c", '<https://x.org/s> <https://x.org/p> "w" .\n')):
            self.write(f"{side}/loadable.nt", text)
            self.write(f"{side}/inferred.nt", "")
        self.assertEqual(self.ri.compare_triples(os.path.join(self.tmp, "b"), os.path.join(self.tmp, "a")), [])
        self.assertEqual(len(self.ri.compare_triples(os.path.join(self.tmp, "c"), os.path.join(self.tmp, "a"))), 1)

    def test_reports_must_carry_equal_hashes(self):
        import json
        a = self.write("a.json", json.dumps({"determinism_hash_sorted": "h", "nodes": 1}))
        b = self.write("b.json", json.dumps({"determinism_hash_sorted": "h", "nodes": 2}))
        c = self.write("c.json", json.dumps({"determinism_hash_sorted": "g"}))
        d = self.write("d.json", json.dumps({"nodes": 1}))
        self.assertEqual(self.ri.compare_reports(b, a), [])
        self.assertEqual(len(self.ri.compare_reports(c, a)), 1)
        self.assertEqual(len(self.ri.compare_reports(d, a)), 1)
        self.assertEqual(len(self.ri.compare_reports(a, d)), 1)


if __name__ == "__main__":
    unittest.main()
