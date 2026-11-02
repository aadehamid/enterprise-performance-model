"""Tests for build_catalog.py (Step 10; EPM-DEC-001-0082): the written catalog equals a fresh build, it
lists one dataset per release package, every distribution a dataset links to is described and names a
file in that package, and it says nothing about a release that the package's own catalog record does not.

Run: python3 -m pytest test_build_catalog.py (needs rdflib).
"""
import glob
import importlib
import os
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF

import build_catalog as bc
import build_module
import newest

core = importlib.import_module(newest.core_builder())  # the newest core builder: its version

MODULES_NS = "https://w3id.org/lsc/ontology/modules/"


def package_folders():
    found = {tuple(p.rstrip(os.sep).split(os.sep)[-2:]) for p in glob.glob(os.path.join(bc.RELEASES, "*", "*", ""))}
    return {(m, v) for m, v in found if m != "previous"}  # the share release's history folder is not a package


def newest_set():
    """The share release's packages, from the builders' own tables (never from the folders the catalog is checked
    against): each module's newest version and the newest core."""
    return {(m, build_module.label(build_module.MODULES[m])) for m in build_module.MODULES} | {("core", core.VERSION)}


def distributions_of(packages):
    """How many distributions these packages describe in their own catalog.ttl files."""
    n = 0
    for m, v in packages:
        g = Graph().parse(os.path.join(bc.RELEASES, m, v, "catalog.ttl"))
        n += len(set(g.subjects(RDF.type, bc.DCAT.Distribution)))
    return n


class Catalog(unittest.TestCase):
    def setUp(self):
        self.g = bc.build()

    def test_the_written_catalog_is_current(self):
        with open(bc.OUT) as f:
            self.assertEqual(f.read(), self.g.serialize(format="turtle"))

    def test_one_dataset_per_release_package(self):
        datasets = {str(d)[len(MODULES_NS):] for d in self.g.objects(bc.CATALOG, bc.DCAT.dataset)}
        # The share release's catalog lists its newest set only (EPM-DEC-001-0110): one dataset per package on disk.
        self.assertEqual(len(datasets), len(newest_set()) if build_module.SHARE_RELEASE else 51)  # then technical-graph 1.0.0 (EPM-DEC-001-0112):  # 50, then kpi 1.3.0 (EPM-DEC-001-0109):  # 49, then party 2.1.0 and integration 2.5.0 (EPM-DEC-001-0099, amendment of 2026-10-28):  # 47, then organization 2.2.0 (EPM-DEC-001-0045, amendment of 2026-10-28):  # 46, then ref-mpc 1.3.0 (EPM-DEC-001-0108, amendment of 2026-10-27):  # 45, then party 2.0.0, system 1.5.0 and integration 2.4.0 (EPM-DEC-001-0108):  # 42, then system 1.4.0 and party 1.4.0 (EPM-DEC-001-0104):  # 40, then core 2.4.0 (EPM-DEC-001-0105):  # 39, then three more (EPM-DEC-001-0103):  # 25, then item G's three (EPM-DEC-001-0099) and item F's five (0100)
        self.assertEqual({tuple(d.split("/")) for d in datasets}, newest_set() if build_module.SHARE_RELEASE else package_folders())
        for d in self.g.objects(bc.CATALOG, bc.DCAT.dataset):
            self.assertIn((d, RDF.type, bc.DCAT.Dataset), self.g)

    def test_every_distribution_is_a_file_in_its_package(self):
        # Read from each dataset's dcat:distribution links, so a link to an undescribed distribution fails.
        linked = set(self.g.objects(None, bc.DCAT.distribution))
        self.assertEqual(len(linked), distributions_of(newest_set()) if build_module.SHARE_RELEASE else 158)  # then technical-graph 1.0.0's three (0112):  # 155, then kpi 1.3.0's three (0109):  # 152, then party 2.1.0's and integration 2.5.0's three each (0099, amendment of 2026-10-28):  # 146, then organization 2.2.0's three (0045, amendment of 2026-10-28):  # 143, then ref-mpc 1.3.0's three (0108, amendment):  # 140, then nine more, three packages of three (0108):  # 131, then six more (0104):  # 125, then core 2.4.0's four:  # 121, then nine more:  # 79, then eight packages of three distributions
        for dist in linked:
            self.assertIn((dist, RDF.type, bc.DCAT.Distribution), self.g)
            self.assertEqual(list(self.g.objects(dist, bc.DCAT.downloadURL)), [dist])
            module, rest = str(dist)[len(MODULES_NS):].split("/releases/")
            version, fname = rest.split("/")
            self.assertTrue(os.path.exists(os.path.join(bc.RELEASES, module, version, fname)), dist)
        # And every described distribution is linked, only from a dataset.
        self.assertEqual(set(self.g.subjects(RDF.type, bc.DCAT.Distribution)), linked)
        for d in self.g.subjects(bc.DCAT.distribution, None):
            self.assertIn((d, RDF.type, bc.DCAT.Dataset), self.g)

    def test_a_link_to_an_undescribed_distribution_fails(self):
        dataset = sorted(self.g.objects(bc.CATALOG, bc.DCAT.dataset))[0]  # any package of the catalog
        dist = next(self.g.objects(dataset, bc.DCAT.distribution))
        self.g.remove((dist, None, None))
        with self.assertRaises(AssertionError):
            self.test_every_distribution_is_a_file_in_its_package()

    def test_the_catalog_adds_only_its_own_title_and_description(self):
        union = Graph()
        for path in bc.package_catalogs():
            union.parse(path)
        extra = set(self.g) - set(union)
        self.assertEqual(extra, {(bc.CATALOG, DCTERMS.title, bc.TITLE), (bc.CATALOG, DCTERMS.description, bc.DESCRIPTION)})
        self.assertEqual(set(union) - set(self.g), set())

    def test_a_package_left_out_makes_the_catalog_stale(self):
        real = bc.package_catalogs
        bc.package_catalogs = lambda: [p for p in real() if os.sep + "lane" + os.sep not in p]
        try:
            stale = bc.build()
        finally:
            bc.package_catalogs = real
        self.assertNotIn(URIRef(MODULES_NS + "lane/1.0.0"), set(stale.objects(bc.CATALOG, bc.DCAT.dataset)))
        with open(bc.OUT) as f:
            self.assertNotEqual(f.read(), stale.serialize(format="turtle"))


if __name__ == "__main__":
    unittest.main()
