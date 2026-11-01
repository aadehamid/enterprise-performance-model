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
    ("core", "1.0.0"), ("core", "2.0.0"), ("core", "2.1.0"), ("core", "2.2.0"), ("core", "2.3.0"), ("core", "2.4.0"),
    ("data-product", "1.0.0"), ("data-product", "1.1.0"), ("data-product", "1.2.0"), ("integration", "1.0.0"), ("integration", "2.0.0"), ("integration", "2.1.0"), ("integration", "2.2.0"), ("integration", "2.3.0"), ("integration", "2.4.0"), ("integration", "2.5.0"),
    ("kpi", "1.0.0"), ("kpi", "1.0.1"), ("kpi", "1.1.0"), ("kpi", "1.1.1"), ("kpi", "1.2.0"), ("kpi", "1.3.0"),
    ("lane", "1.0.0"), ("lane", "1.1.0"), ("market-data", "1.0.0"), ("market-data", "1.1.0"),
    ("organization", "1.0.0"), ("organization", "2.0.0"), ("organization", "2.1.0"), ("organization", "2.2.0"), ("party", "1.0.0"), ("party", "1.1.0"), ("party", "1.2.0"), ("party", "1.3.0"), ("party", "1.4.0"), ("party", "2.0.0"), ("party", "2.1.0"),
    ("ref-mpc", "1.0.0"), ("ref-mpc", "1.1.0"), ("ref-mpc", "1.2.0"), ("ref-mpc", "1.3.0"),
    ("system", "1.0.0"), ("system", "1.1.0"), ("system", "1.2.0"), ("system", "1.3.0"), ("system", "1.4.0"), ("system", "1.5.0"), ("value-stream", "1.0.0"), ("value-stream", "1.1.0"), ("value-stream", "1.2.0"),
]


def package_file(name, version, fname):
    folder = os.path.join(ONTOLOGY, "releases", name, version)
    if not os.path.isdir(folder) and os.path.isdir(os.path.join(ONTOLOGY, "releases", "previous", name, version)):
        folder = os.path.join(ONTOLOGY, "releases", "previous", name, version)  # the share release's history folder
    return os.path.join(folder, fname)


def packages_on_disk():
    """(module, version) for every package folder, the share release's releases/previous/ included."""
    found = set()
    for pattern in (os.path.join(ONTOLOGY, "releases", "*", "*", ""), os.path.join(ONTOLOGY, "releases", "previous", "*", "*", "")):
        for p in glob.glob(pattern):
            name, version = p.rstrip(os.sep).split(os.sep)[-2:]
            if name != "previous" and version[0].isdigit():
                found.add((name, version))
    return found


# The share release ships only each module's newest and previous package (EPM-DEC-001-0110), so with
# EPM_SHARE_RELEASE set the list is what is on disk; on main it is the pinned list above, checked against the disk.
if build_module.SHARE_RELEASE:  # the environment variable, or release.json at the tree's root
    PACKAGES = sorted(packages_on_disk())


def package_graph(name, version):
    return Graph().parse(package_file(name, version, f"{name}.ttl"))


def with_closure(name, version, g, tc=None):
    data = Graph()
    data += g
    try:
        closure = build_module.closure(build_module.released_requires(name, version))
    except FileNotFoundError as e:
        if tc is None:
            raise
        tc.skipTest(f"{e}: the share release holds each module's newest and previous packages only")
    for dep, dep_version in sorted(closure.items()):
        data.parse(package_file(dep, dep_version, f"{dep}.ttl"))
    return data


def conforms(name, version, data):
    ok, _, text = validate(data, shacl_graph=Graph().parse(package_file(name, version, "shapes.ttl")), advanced=True)
    return ok, text


class ReleasePackages(unittest.TestCase):
    def test_every_package_is_listed(self):
        # Keyed on folders, not manifests, so a package written without its manifest is not missed.
        self.assertEqual(packages_on_disk(), set(PACKAGES))

    def test_the_closure_is_loaded(self):
        # value-stream 1.0.0 links to data products and measures in other packages; alone, its shapes fail.
        if build_module.package_folder("value-stream", "1.0.0") is None or build_module.package_folder("core", "2.2.0") is None:
            self.skipTest("value-stream 1.0.0 or its closure did not ship (the share release holds the newest and previous packages only)")
        self.assertEqual(build_module.closure(build_module.released_requires("value-stream", "1.0.0")),
                         {"core": "2.2.0", "data-product": "1.0.0", "kpi": "1.0.1"})
        ok, text = conforms("value-stream", "1.0.0", package_graph("value-stream", "1.0.0"))
        self.assertFalse(ok)
        self.assertIn("A measure link names exactly one measure of the kpi module.", text)

    def test_a_broken_package_fails(self):
        # An office lane without its notation breaks the lane package's own shapes.
        lane = Namespace("https://w3id.org/lsc/ontology/modules/lane/lane/")
        version = max((v for m, v in packages_on_disk() if m == "lane"), key=lambda v: tuple(int(x) for x in v.split(".")))
        g = package_graph("lane", version)
        g.remove((lane["front-office"], SKOS.notation, None))
        ok, text = conforms("lane", version, with_closure("lane", version, g, self))
        self.assertFalse(ok)
        self.assertIn("front-office", text)


def _package_test(name, version):
    def test(self):
        ok, text = conforms(name, version, with_closure(name, version, package_graph(name, version), self))
        self.assertTrue(ok, text[:3000])
    return test


for _name, _version in PACKAGES:
    setattr(ReleasePackages, f"test_{_name.replace('-', '_')}_{_version.replace('.', '_')}_conforms",
            _package_test(_name, _version))


if __name__ == "__main__":
    unittest.main()
