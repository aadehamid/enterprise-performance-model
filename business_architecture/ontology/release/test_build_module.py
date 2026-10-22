"""Tests for the module release builder (Step 10; EPM-DEC-001-0037): each written package equals a
fresh build, a release candidate carries no issued date, dependencies name versions that exist, and
the DCAT record and manifest describe the files.

Run: python3 -m pytest test_build_module.py (needs rdflib, pyshacl).
"""
import hashlib
import re
import json
import os
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF

import build_module as bm

DCAT = bm.DCAT
# The sentence that approved each issued release (EPM-DEC-001-0037).
SESSION2 = "step4/review-evidence/decision-owner-answers/answers-2026-10-13-session2.md"
NIGHT = "step4/review-evidence/decision-owner-answers/answers-2026-10-18-night.md"
RELEASES = "step4/review-evidence/decision-owner-answers/answers-2026-10-19-ref-mpc.md"
APPROVALS = {"organization": (NIGHT, "Yes, approve 2.0.0 (Recommended)"),
             "ref-mpc": (RELEASES, "Approve the ref-mpc release too if needed"),
             "kpi": ("step4/review-evidence/decision-owner-answers/answers-2026-10-19-releases.md",
                     "You have my approval to keep going and release things as needed. while I am out"),
             "party": ("step4/review-evidence/decision-owner-answers/answers-2026-10-21-release-playbook.md",
                       "You have my permission to release the stable version when you are done.")}
# The Step 7 modules' first releases, approved with the release plan (EPM-DEC-001-0077).
PLAN = ("step4/review-evidence/decision-owner-answers/answers-2026-10-22-morning.md", "release plan approved")
STEP7 = ("data-product", "value-stream", "system", "lane", "market-data")
APPROVALS.update({name: PLAN for name in STEP7})


def approval_holds(name, m):
    """The release names the sentence the decision owner wrote for it, and that sentence is in the body of the
    saved file. Another sentence of the same file, an answer to another question, is not an approval."""
    path, words = m["approval"]
    if (path, words) != APPROVALS[name]:
        return False
    with open(os.path.join(bm.ONTOLOGY, path)) as f:
        # The decision owner's words sit in the body; Claude's context sits in HTML comments.
        body = re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)
    return words in body


class Packages(unittest.TestCase):
    def test_each_written_package_equals_a_fresh_build(self):
        for name in bm.MODULES:
            with self.subTest(module=name):
                g = bm.build(name)
                self.assertTrue(bm.check(name, g)[0])
                for fname, text in bm.package(name, g).items():
                    with open(os.path.join(bm.release_dir(name), fname)) as f:
                        self.assertEqual(f.read(), text, fname)

    def test_an_issued_release_carries_the_owners_recorded_approval_and_a_candidate_no_date(self):
        # A module's first release is a major, which needs the decision owner's approval (module policy).
        for name, m in bm.MODULES.items():
            with self.subTest(module=name):
                g = bm.build(name)
                manifest = json.loads(bm.package(name, g)["manifest.json"])
                issued = (URIRef(bm.MODULES_NS + name), DCTERMS.issued, None) in g
                if m["stage"] is None:
                    path, _ = m["approval"]
                    self.assertTrue(approval_holds(name, m))
                    self.assertTrue(issued)
                    iri = URIRef(bm.MODULES_NS + name)
                    self.assertEqual(g.value(iri, DCTERMS.modified), g.value(iri, DCTERMS.issued))
                    self.assertFalse(manifest["release_candidate"])
                    self.assertEqual(manifest["approved_by"]["recorded_in"], path)
                else:
                    self.assertFalse(issued)
                    self.assertTrue(manifest["release_candidate"])

    def test_another_sentence_of_the_answers_file_is_not_an_approval(self):
        wrong = dict(bm.MODULES["organization"], approval=(NIGHT, "Yes, cut 2.1.0 (Recommended)"))
        self.assertFalse(approval_holds("organization", wrong))
        self.assertTrue(approval_holds("organization", bm.MODULES["organization"]))

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


class EarlierReleases(unittest.TestCase):
    def test_earlier_packages_are_untouched(self):
        # The builder now builds organization 2.0.0 and ref-mpc 1.1.0; each released 1.0.0 package
        # must still match its own manifest.
        for name in ("organization", "ref-mpc", "kpi"):
            out = os.path.join(bm.ONTOLOGY, "releases", name, "1.0.0")
            with open(os.path.join(out, "manifest.json")) as f:
                manifest = json.load(f)
            self.assertEqual(manifest["version"], "1.0.0")
            for fname, digest in manifest["files"].items():
                with self.subTest(module=name, file=fname), open(os.path.join(out, fname), "rb") as f:
                    self.assertEqual(hashlib.sha256(f.read()).hexdigest(), digest)

    def test_party_holds_its_four_source_files_and_nothing_else(self):
        # EPM-DEC-001-0074, item 2: the vocabulary, code lists, systems and lifecycle, read here from the
        # source files rather than from the builder's list; the reference parties and examples stay out.
        released = Graph().parse(os.path.join(bm.ONTOLOGY, "releases", "party", "1.0.0", "party.ttl"))
        header = URIRef(bm.MODULES_NS + "party")
        released.remove((header, None, None))
        sources = Graph()
        for name in ("vocabulary.ttl", "code-lists.ttl", "systems.ttl", "lifecycle.ttl"):
            sources.parse(os.path.join(bm.ONTOLOGY, "party", name))
        sources.remove((header, None, None))
        self.assertEqual(set(released), set(sources))
        for path in ("ref-mpc/reference-parties.ttl", "party/examples.ttl"):
            outside = Graph().parse(os.path.join(bm.ONTOLOGY, path))
            self.assertFalse(set(outside) & set(released), path)

    def test_the_new_releases_require_the_current_ones(self):
        self.assertEqual(bm.dependencies("ref-mpc"), {"organization": "2.0.0"})
        self.assertEqual(bm.dependencies("organization"), {"core": "2.1.0"})
        self.assertEqual(bm.dependencies("kpi"), {"core": "2.1.0"})
        self.assertEqual(bm.dependencies("party"), {"core": "2.1.0"})
        # EPM-DEC-001-0077: the Step 7 modules require core 2.2.0, and the modules whose IRIs they use.
        self.assertEqual(bm.dependencies("data-product"), {"core": "2.2.0"})
        self.assertEqual(bm.dependencies("value-stream"), {"core": "2.2.0", "data-product": "1.0.0", "kpi": "1.0.1"})
        self.assertEqual(bm.dependencies("system"), {"core": "2.2.0"})
        self.assertEqual(bm.dependencies("lane"), {"core": "2.2.0"})
        self.assertEqual(bm.dependencies("market-data"), {"kpi": "1.0.1"})

    def test_a_check_loads_one_release_of_each_module(self):
        # value-stream reaches core twice: directly at 2.2.0 and through kpi 1.0.1 at 2.1.0. Only 2.2.0 loads.
        self.assertEqual(bm.released_closure("value-stream"), {"core": "2.2.0", "data-product": "1.0.0", "kpi": "1.0.1"})
        self.assertEqual(bm.released_closure("market-data"), {"kpi": "1.0.1", "core": "2.1.0"})
        self.assertEqual(bm.released_closure("ref-mpc"), {"organization": "2.0.0", "core": "2.1.0"})

    def test_the_validated_graph_holds_one_core_release(self):
        # Codex round 1 on EPM-DEC-001-0077, item 3: the graph the shapes see, not only the version table.
        core = URIRef(bm.MODULES_NS + "core")
        expected = {"value-stream": "2.2.0", "market-data": "2.1.0", "ref-mpc": "2.1.0"}
        for name, version in expected.items():
            with self.subTest(module=name):
                data = bm.validation_graph(name, bm.build(name))
                self.assertEqual({str(v) for v in data.objects(core, OWL.versionInfo)}, {version})
        # core 2.2.0 corrected two 19948 decisions; the superseded 2.1.0 triples must not come back.
        data = bm.validation_graph("value-stream", bm.build("value-stream"))
        review = URIRef(bm.MODULES_NS + "core/apqc-mapping-decision/review-link")
        decision = URIRef(bm.MODULES_NS + "core/apqcMappingDecision")
        for slug in ("CM-1-2-6-3", "L0-downstream-operations"):
            self.assertNotIn((URIRef("https://w3id.org/lsc/ontology/process/" + slug), decision, review), data)

    def test_a_later_dependency_release_leaves_the_released_packages_unchanged(self):
        # Codex round 1: kpi 1.1.0 and a later data-product must not change value-stream or market-data 1.0.0,
        # nor what their checks load (closures come from each selected release's own manifest).
        saved = {n: dict(bm.MODULES[n]) for n in ("kpi", "data-product")}
        try:
            bm.MODULES["kpi"].update(version="1.1.0", pins={"core": "2.2.0"})
            bm.MODULES["data-product"].update(version="1.1.0")
            self.assertEqual(bm.released_closure("value-stream"), {"core": "2.2.0", "data-product": "1.0.0", "kpi": "1.0.1"})
            self.assertEqual(bm.released_closure("market-data"), {"kpi": "1.0.1", "core": "2.1.0"})
            for name in ("value-stream", "market-data"):
                with self.subTest(module=name):
                    for fname, text in bm.package(name, bm.build(name)).items():
                        with open(os.path.join(bm.release_dir(name), fname)) as f:
                            self.assertEqual(f.read(), text, fname)
        finally:
            for n, m in saved.items():
                bm.MODULES[n].clear()
                bm.MODULES[n].update(m)

    def test_each_step7_package_holds_its_two_source_files(self):
        # EPM-DEC-001-0077: each package is its module's vocabulary and instance file, nothing else.
        files = {"data-product": "data-products.ttl", "value-stream": "value-streams.ttl", "system": "systems.ttl",
                 "lane": "lanes.ttl", "market-data": "market-data.ttl"}
        for name, instances in files.items():
            with self.subTest(module=name):
                released = Graph().parse(os.path.join(bm.ONTOLOGY, "releases", name, "1.0.0", f"{name}.ttl"))
                header = URIRef(bm.MODULES_NS + name)
                released.remove((header, None, None))
                sources = Graph()
                for part in ("vocabulary.ttl", instances):
                    sources.parse(os.path.join(bm.ONTOLOGY, name, part))
                sources.remove((header, None, None))
                self.assertEqual(set(released), set(sources))

    def test_the_step7_releases_carry_the_release_plan_approval(self):
        for name in STEP7:
            self.assertEqual(bm.MODULES[name]["approval"], PLAN)
            self.assertEqual((bm.MODULES[name]["version"], bm.MODULES[name]["stage"], bm.MODULES[name]["issued"]),
                             ("1.0.0", None, "2026-10-22"))


if __name__ == "__main__":
    unittest.main()
