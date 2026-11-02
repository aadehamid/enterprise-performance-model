"""Step 9 (EPM-DEC-001-0081): every release package on disk conforms to its own shapes.ttl, run over
the package with the released packages it requires loaded (its closure, read from the manifests). The
whole-graph gate (test_all_module_shapes.py) runs the source files; this test runs what was shipped.

Run: python3 -m pytest test_release_package_shapes.py (needs rdflib, pyshacl).
"""
import glob
import importlib
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ONTOLOGY, "release"))
import build_module  # noqa: E402
import newest  # noqa: E402
core = importlib.import_module(newest.core_builder())  # the newest core builder: its version and the version it builds from

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
    folder = build_module.package_folder(name, version)  # releases/<name>/<version>/, or the share release's history folder
    return os.path.join(folder or os.path.join(ONTOLOGY, "releases", name, version), fname)


def packages_on_disk(ontology=ONTOLOGY):
    """(module, version) for every package folder, the share release's releases/previous/ included."""
    found = set()
    for pattern in (os.path.join(ontology, "releases", "*", "*", ""), os.path.join(ontology, "releases", "previous", "*", "*", "")):
        for p in glob.glob(pattern):
            name, version = p.rstrip(os.sep).split(os.sep)[-2:]
            if name != "previous" and version[0].isdigit():
                found.add((name, version))
    return found


def previous_version(name, newest, ontology=ONTOLOGY):
    """The version before `newest`, read from the newest package's own CHANGELOG.md (its second heading), not from
    the folders on disk; None when the changelog names no earlier version."""
    with open(os.path.join(ontology, "releases", name, newest, "CHANGELOG.md")) as f:
        versions = re.findall(r"^## (\d+\.\d+\.\d+)", f.read(), re.M)
    return versions[1] if versions[:1] == [newest] and len(versions) > 1 else None


def expected_release_packages(ontology=ONTOLOGY):
    """The packages the share release must hold (EPM-DEC-001-0110): each module's newest version, from the builders'
    own tables, and the one before it, from each newest package's changelog (core's from its builder's base). Nothing
    here is read from the list of folders, so a package the export left out is missed by the disk, not by this."""
    newest = {(m, build_module.label(build_module.MODULES[m])) for m in build_module.MODULES} | {("core", core.VERSION)}
    previous = {("core", os.path.basename(core.BASE))}
    for name, version in newest - {("core", core.VERSION)}:
        before = previous_version(name, version, ontology)
        if before:
            previous.add((name, before))
    return newest | previous


# The share release ships only each module's newest and previous package (EPM-DEC-001-0110), so in release mode (the
# environment variable, or release.json at the tree's root) the list is what the builders and changelogs say must be
# there; on main it is the pinned list above, checked against the disk.
if build_module.SHARE_RELEASE:
    PACKAGES = sorted(expected_release_packages())


def package_graph(name, version):
    return Graph().parse(package_file(name, version, f"{name}.ttl"))


def with_closure(name, version, g, tc=None):
    data = Graph()
    data += g
    try:
        closure = build_module.closure(build_module.released_requires(name, version))
    except FileNotFoundError as e:
        # Only a package of the share release's history folder may lack its closure: its pins may name versions the
        # release does not ship (EPM-DEC-001-0110). A newest package's closure must be on disk, there and on main.
        previous = os.path.isdir(os.path.join(ONTOLOGY, "releases", "previous", name, version))
        if tc is None or not (build_module.SHARE_RELEASE and previous):
            raise
        tc.skipTest(f"{e}: {name} {version} is history only (releases/previous/), and the release does not ship its closure")
    for dep, dep_version in sorted(closure.items()):
        data.parse(package_file(dep, dep_version, f"{dep}.ttl"))
    return data


def conforms(name, version, data):
    ok, _, text = validate(data, shacl_graph=Graph().parse(package_file(name, version, "shapes.ttl")), advanced=True)
    return ok, text


class ReleasePackages(unittest.TestCase):
    def test_every_package_is_listed(self):
        # Keyed on folders, not manifests, so a package written without its manifest is not missed.
        on_disk = packages_on_disk()
        if not build_module.SHARE_RELEASE:
            self.assertEqual(on_disk, set(PACKAGES))
            return
        # A release keeps every earlier package under releases/previous/, however many a recipient's changes retire;
        # outside it, a module's folder holds only its newest package.
        self.assertEqual(set(PACKAGES) - on_disk, set())
        for name, version in on_disk - set(PACKAGES):
            self.assertTrue(os.path.isdir(os.path.join(ONTOLOGY, "releases", "previous", name, version)),
                            f"{name} {version} is neither the newest nor in releases/previous/")

    def test_the_closure_is_loaded(self):
        # value-stream 1.0.0 links to data products and measures in other packages; alone, its shapes fail.
        if build_module.SHARE_RELEASE and build_module.package_folder("value-stream", "1.0.0") is None:
            self.skipTest("value-stream 1.0.0 did not ship (the share release holds the newest and previous packages only)")
        self.assertEqual(build_module.closure(build_module.released_requires("value-stream", "1.0.0")),
                         {"core": "2.2.0", "data-product": "1.0.0", "kpi": "1.0.1"})
        ok, text = conforms("value-stream", "1.0.0", package_graph("value-stream", "1.0.0"))
        self.assertFalse(ok)
        self.assertIn("A measure link names exactly one measure of the kpi module.", text)

    def test_a_broken_package_fails(self):
        # An office lane without its notation breaks the lane package's own shapes.
        lane = Namespace("https://w3id.org/lsc/ontology/modules/lane/lane/")
        # lane 1.0.0 on main, as always; in the share release, where 1.0.0 may be history, the newest lane package.
        version = build_module.label(build_module.MODULES["lane"]) if build_module.SHARE_RELEASE else "1.0.0"
        g = package_graph("lane", version)
        g.remove((lane["front-office"], SKOS.notation, None))
        ok, text = conforms("lane", version, with_closure("lane", version, g, self))
        self.assertFalse(ok)
        self.assertIn("front-office", text)


class ReleaseInventory(unittest.TestCase):
    """The share release's package list comes from the builders and the changelogs, never from the folders it is
    checked against, so a package the export left out fails test_every_package_is_listed instead of vanishing."""

    def test_the_previous_version_comes_from_the_newest_packages_changelog(self):
        self.assertEqual(previous_version("kpi", "1.3.0"), "1.2.0")
        self.assertEqual(previous_version("lane", "1.1.0"), "1.0.0")
        with tempfile.TemporaryDirectory() as tmp:
            folder = os.path.join(tmp, "releases", "x", "1.0.0")
            os.makedirs(folder)
            with open(os.path.join(folder, "CHANGELOG.md"), "w") as f:
                f.write("# x\n\n## 1.0.0 (2026-10-01)\n\nFirst.\n")
            self.assertIsNone(previous_version("x", "1.0.0", tmp))

    def test_the_expected_set_is_each_newest_package_and_the_one_before(self):
        expected = expected_release_packages()
        newest = {(m, build_module.label(build_module.MODULES[m])) for m in build_module.MODULES} | {("core", core.VERSION)}
        self.assertTrue(newest <= expected)
        self.assertIn(("core", "2.3.0"), expected)
        self.assertIn(("kpi", "1.2.0"), expected)
        self.assertEqual(len(expected), 2 * len(newest))  # every module has a version before its newest
        self.assertTrue(expected <= packages_on_disk())  # main holds every version, so it holds these

    def test_a_tree_missing_a_previous_package_is_found_out(self):
        # The negative fixture: every newest package's changelog, and no history folder. The expectation still
        # names each previous version, so the disk fails to match it.
        newest = {(m, build_module.label(build_module.MODULES[m])) for m in build_module.MODULES} | {("core", core.VERSION)}
        with tempfile.TemporaryDirectory() as tmp:
            for name, version in newest:  # the previous versions are left out of the fixture on purpose
                folder = os.path.join(tmp, "releases", name, version)
                os.makedirs(folder)
                shutil.copy(os.path.join(ONTOLOGY, "releases", name, version, "CHANGELOG.md"), folder)
            self.assertEqual(packages_on_disk(tmp) - expected_release_packages(tmp), set())
            missing = expected_release_packages(tmp) - packages_on_disk(tmp)
            self.assertIn(("kpi", "1.2.0"), missing)
            self.assertIn(("core", "2.3.0"), missing)

    def test_a_newest_package_without_its_closure_fails_and_only_history_skips(self):
        # with_closure turns a missing closure into a skip only for a package of releases/previous/ in release mode.
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "releases", "previous", "kpi", "0.9.0"))
            os.makedirs(os.path.join(tmp, "releases", "kpi", "1.0.0"))

            def gone(name, version):
                raise FileNotFoundError(f"{name} {version} is not on disk")
            with mock.patch.object(build_module, "released_requires", gone), \
                    mock.patch.object(sys.modules[__name__], "ONTOLOGY", tmp):
                for share in (False, True):
                    with mock.patch.object(build_module, "SHARE_RELEASE", share):
                        with self.assertRaises(FileNotFoundError):
                            with_closure("kpi", "1.0.0", Graph(), self)  # a newest package, in either mode
                        with self.assertRaises(FileNotFoundError):
                            with_closure("kpi", "0.9.0", Graph())  # no test case to skip
                        if share:
                            with self.assertRaises(unittest.SkipTest):
                                with_closure("kpi", "0.9.0", Graph(), self)  # history, in release mode only
                        else:
                            with self.assertRaises(FileNotFoundError):
                                with_closure("kpi", "0.9.0", Graph(), self)


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
