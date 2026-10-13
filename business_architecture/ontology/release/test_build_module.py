"""Tests for the module release builder (Step 10; EPM-DEC-001-0037): each written package equals a
fresh build, a release candidate carries no issued date, dependencies name versions that exist, and
the DCAT record and manifest describe the files.

Run: python3 -m pytest test_build_module.py (needs rdflib, pyshacl).
"""
import hashlib
import json
import os
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF

import build_module as bm

DCAT = bm.DCAT


class Packages(unittest.TestCase):
    def test_each_written_package_equals_a_fresh_build(self):
        for name in bm.MODULES:
            with self.subTest(module=name):
                g = bm.build(name)
                self.assertTrue(bm.check(name, g)[0])
                for fname, text in bm.package(name, g).items():
                    with open(os.path.join(bm.release_dir(name), fname)) as f:
                        self.assertEqual(f.read(), text, fname)

    def test_a_candidate_has_no_issued_date_and_says_it_is_a_candidate(self):
        for name, m in bm.MODULES.items():
            with self.subTest(module=name):
                self.assertIsNotNone(m["stage"], "a first release (a major) needs Hamid's approval")
                g = bm.build(name)
                self.assertNotIn((URIRef(bm.MODULES_NS + name), DCTERMS.issued, None), g)
                manifest = json.loads(bm.package(name, g)["manifest.json"])
                self.assertTrue(manifest["release_candidate"])
                self.assertNotIn("issued", Graph().parse(data=bm.catalog(name), format="turtle").serialize())

    def test_dependencies_name_versions_that_exist(self):
        for name in bm.MODULES:
            for dep, version in bm.dependencies(name).items():
                with self.subTest(module=name, dep=dep):
                    # The dependency's package must be on disk, not only in the builder's own table.
                    package = os.path.join(bm.ONTOLOGY, "releases", dep, version)
                    self.assertTrue(os.path.isfile(os.path.join(package, "manifest.json")), f"{name} names {dep} {version}")
                    with open(os.path.join(package, "manifest.json")) as f:
                        self.assertEqual(json.load(f)["version"], version)
                    self.assertIn((URIRef(bm.MODULES_NS + name), DCTERMS.requires,
                                   URIRef(f"{bm.MODULES_NS}{dep}/{version}")), bm.build(name))

    def test_ref_mpc_is_validated_with_the_control_relationship_shape(self):
        # ref-mpc's control relationship is checked by the organization module's shapes.
        shapes = bm.parse(bm.MODULES["ref-mpc"]["shapes"])
        sh = "http://www.w3.org/ns/shacl#"
        self.assertIn((None, URIRef(sh + "targetClass"), URIRef(bm.MODULES_NS + "organization/ControlRelationship")), shapes)

    def test_the_header_names_the_version(self):
        for name in bm.MODULES:
            g, iri = bm.build(name), URIRef(bm.MODULES_NS + name)
            self.assertIn((iri, RDF.type, OWL.Ontology), g)
            self.assertEqual(str(g.value(iri, OWL.versionIRI)), f"{iri}/{bm.label(bm.MODULES[name])}")

    def test_the_catalog_lists_the_three_distributions(self):
        for name in bm.MODULES:
            cat = Graph().parse(data=bm.catalog(name), format="turtle")
            dataset = next(cat.subjects(RDF.type, DCAT.Dataset))
            names = {str(d).rsplit("/", 1)[1] for d in cat.objects(dataset, DCAT.distribution)}
            self.assertEqual(names, {f"{name}.ttl", f"{name}.jsonld", "shapes.ttl"})

    def test_the_manifest_hashes_every_other_file(self):
        for name in bm.MODULES:
            files = bm.package(name, bm.build(name))
            manifest = json.loads(files["manifest.json"])
            self.assertEqual(set(manifest["files"]), set(files) - {"manifest.json"})
            for fname, digest in manifest["files"].items():
                self.assertEqual(hashlib.sha256(files[fname].encode()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
