"""Tests for build_catalog.py (Step 10; EPM-DEC-001-0082): the written catalog equals a fresh build, it
lists one dataset per release package, every distribution names a file in that package, and it says
nothing about a release that the package's own catalog record does not.

Run: python3 -m pytest test_build_catalog.py (needs rdflib).
"""
import glob
import os
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, RDF

import build_catalog as bc

MODULES_NS = "https://w3id.org/lsc/ontology/modules/"


def package_folders():
    return {tuple(p.rstrip(os.sep).split(os.sep)[-2:]) for p in glob.glob(os.path.join(bc.RELEASES, "*", "*", ""))}


class Catalog(unittest.TestCase):
    def setUp(self):
        self.g = bc.build()

    def test_the_written_catalog_is_current(self):
        with open(bc.OUT) as f:
            self.assertEqual(f.read(), self.g.serialize(format="turtle"))

    def test_one_dataset_per_release_package(self):
        datasets = {str(d)[len(MODULES_NS):] for d in self.g.objects(bc.CATALOG, bc.DCAT.dataset)}
        self.assertEqual(len(datasets), 19)
        self.assertEqual({tuple(d.split("/")) for d in datasets}, package_folders())
        for d in self.g.objects(bc.CATALOG, bc.DCAT.dataset):
            self.assertIn((d, RDF.type, bc.DCAT.Dataset), self.g)

    def test_every_distribution_is_a_file_in_its_package(self):
        count = 0
        for dist in self.g.subjects(RDF.type, bc.DCAT.Distribution):
            module, rest = str(dist)[len(MODULES_NS):].split("/releases/")
            version, fname = rest.split("/")
            self.assertTrue(os.path.exists(os.path.join(bc.RELEASES, module, version, fname)), dist)
            self.assertEqual(self.g.value(dist, bc.DCAT.downloadURL), dist)
            count += 1
        self.assertGreater(count, 0)

    def test_the_catalog_adds_only_its_own_title_and_description(self):
        union = Graph()
        for path in bc.package_catalogs():
            union.parse(path)
        extra = set(self.g) - set(union)
        self.assertEqual({(s, p) for s, p, _ in extra}, {(bc.CATALOG, DCTERMS.title), (bc.CATALOG, DCTERMS.description)})
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
