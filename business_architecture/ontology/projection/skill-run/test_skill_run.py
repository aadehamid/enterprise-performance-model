"""The ontology-to-lpg skill's run_projection.py reads the same inputs as ../pipeline.py: inputs.py lists
exactly its INPUTS and SHAPES, each file exists, and epm-config.json pins the same packages. epm-run.json,
the run configuration, names this folder's files, keeps every output outside the repository and names
each release's shapes and catalog, which sit beside every data file.

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


class RunConfig(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "epm-run.json")) as f:
            self.cfg = json.load(f)

    def path(self, value):
        return os.path.normpath(os.path.join(HERE, value))

    def test_it_projects_the_releases_this_folder_lists(self):
        self.assertEqual(self.cfg["mode"], "releases")
        self.assertEqual(self.path(self.cfg["inputs_script"]), os.path.join(HERE, "inputs.py"))
        self.assertEqual(self.path(self.cfg["projection_config"]), os.path.join(HERE, "epm-config.json"))
        self.assertEqual(self.path(self.cfg["queries"]), os.path.join(HERE, "queries.json"))
        self.assertEqual(os.path.realpath(self.path(self.cfg["releases"])), listed("releases")[0])
        for key in ("inputs_script", "projection_config", "queries"):
            self.assertTrue(os.path.isfile(self.path(self.cfg[key])), key)

    def test_outputs_and_credentials_live_outside_the_repository(self):
        # Machine paths (ROBOT, the env files, the outputs) cannot exist in CI, so they must sit under the
        # home folder, which the driver expands; the repository's own files are checked above.
        for key in ("out", "robot_jar", "target_env"):
            self.assertTrue(self.cfg[key].startswith("~/"), key)
        self.assertTrue(self.cfg["rebuild"]["out"].startswith("~/"))
        self.assertTrue(self.cfg["databricks"]["env"].startswith("~/"))

    def test_every_release_has_the_graphs_the_stores_hold(self):
        for data in listed("data"):
            for name in self.cfg["release_graphs"]:
                self.assertTrue(os.path.isfile(os.path.join(os.path.dirname(data), name + ".ttl")), (data, name))

    def test_every_saved_walk_names_a_start_and_hops(self):
        with open(os.path.join(HERE, "queries.json")) as f:
            queries = json.load(f)["queries"]
        self.assertEqual(len(queries), 14)
        for q in queries:
            self.assertTrue(q["name"] and q["iri"].startswith("https://") and int(q["hops"]) >= 1, q)


if __name__ == "__main__":
    unittest.main()
