"""Step 9 (EPM-DEC-001-0081): every release package on disk conforms to its own shapes.ttl, run over
the package with the released packages it requires loaded (its closure, read from the manifests). The
whole-graph gate (test_all_module_shapes.py) runs the source files; this test runs what was shipped.

Run: python3 -m pytest test_release_package_shapes.py (needs rdflib, pyshacl).
"""
import glob
import os
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ONTOLOGY, "release"))
import build_module  # noqa: E402

# Pinned by hand: a new release must join this list, so its package is checked here.
PACKAGES = [
    ("core", "1.0.0"), ("core", "2.0.0"), ("core", "2.1.0"), ("core", "2.2.0"), ("core", "2.3.0"),
    ("data-product", "1.0.0"), ("data-product", "1.1.0"), ("integration", "1.0.0"),
    ("kpi", "1.0.0"), ("kpi", "1.0.1"), ("kpi", "1.1.0"),
    ("lane", "1.0.0"), ("market-data", "1.0.0"),
    ("organization", "1.0.0"), ("organization", "2.0.0"), ("party", "1.0.0"),
    ("ref-mpc", "1.0.0"), ("ref-mpc", "1.1.0"), ("ref-mpc", "1.2.0"),
    ("system", "1.0.0"), ("value-stream", "1.0.0"), ("value-stream", "1.1.0"),
]


def package_file(name, version, fname):
    return os.path.join(ONTOLOGY, "releases", name, version, fname)


def package_graph(name, version):
    return Graph().parse(package_file(name, version, f"{name}.ttl"))


def with_closure(name, version, g):
    data = Graph()
    data += g
    for dep, dep_version in sorted(build_module.closure(build_module.released_requires(name, version)).items()):
        data.parse(package_file(dep, dep_version, f"{dep}.ttl"))
    return data


def conforms(name, version, data):
    ok, _, text = validate(data, shacl_graph=Graph().parse(package_file(name, version, "shapes.ttl")), advanced=True)
    return ok, text


class ReleasePackages(unittest.TestCase):
    def test_every_package_is_listed(self):
        # Keyed on folders, not manifests, so a package written without its manifest is not missed.
        found = {tuple(p.rstrip(os.sep).split(os.sep)[-2:]) for p in glob.glob(package_file("*", "*", ""))}
        self.assertEqual(found, set(PACKAGES))

    def test_the_closure_is_loaded(self):
        # value-stream 1.0.0 links to data products and measures in other packages; alone, its shapes fail.
        self.assertEqual(build_module.closure(build_module.released_requires("value-stream", "1.0.0")),
                         {"core": "2.2.0", "data-product": "1.0.0", "kpi": "1.0.1"})
        ok, text = conforms("value-stream", "1.0.0", package_graph("value-stream", "1.0.0"))
        self.assertFalse(ok)
        self.assertIn("A measure link names exactly one measure of the kpi module.", text)

    def test_a_broken_package_fails(self):
        # An office lane without its notation breaks the lane package's own shapes.
        lane = Namespace("https://w3id.org/lsc/ontology/modules/lane/lane/")
        g = package_graph("lane", "1.0.0")
        g.remove((lane["front-office"], SKOS.notation, None))
        ok, text = conforms("lane", "1.0.0", with_closure("lane", "1.0.0", g))
        self.assertFalse(ok)
        self.assertIn("front-office", text)


def _package_test(name, version):
    def test(self):
        ok, text = conforms(name, version, with_closure(name, version, package_graph(name, version)))
        self.assertTrue(ok, text[:3000])
    return test


for _name, _version in PACKAGES:
    setattr(ReleasePackages, f"test_{_name.replace('-', '_')}_{_version.replace('.', '_')}_conforms",
            _package_test(_name, _version))


if __name__ == "__main__":
    unittest.main()
