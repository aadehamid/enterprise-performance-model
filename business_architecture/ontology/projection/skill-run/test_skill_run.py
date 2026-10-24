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


if __name__ == "__main__":
    unittest.main()
