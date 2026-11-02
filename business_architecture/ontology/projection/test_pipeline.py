"""Tests for the Step 12 projection's checks and record (EPM-DEC-001-0036, 0111). They need no Neo4j: they check the
rules (Step 1), the build and its manifest (Step 3), that a driver run's result is taken in only when it read this
tree's inputs and passed, and that the committed report describes the current inputs and passed.

Run: python3 -m pytest test_pipeline.py (needs rdflib, pyshacl).
"""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

import pipeline as pl

DATA = pl.graph(pl.INPUTS)
SHAPES = pl.graph(pl.SHAPES)
CORE = "https://w3id.org/lsc/ontology/modules/core/"


def rule_problems(change):
    g = Graph()
    g += DATA
    change(g)
    return [p for p in pl.check_rules(g, SHAPES) if p not in pl.RELEASE_EXCEPTIONS]


class Rules(unittest.TestCase):
    def test_the_inputs_pass_the_rules_except_the_listed_release_gaps(self):
        self.assertEqual(sorted(pl.check_rules(DATA, SHAPES)), sorted(pl.RELEASE_EXCEPTIONS))

    def test_an_untyped_own_property_fails_rule_1(self):
        p = URIRef(CORE + "precedes")
        problems = rule_problems(lambda g: g.remove((p, RDF.type, OWL.ObjectProperty)))
        self.assertTrue(any(x.startswith("Rule 1") and "precedes" in x for x in problems), problems)

    def test_a_property_without_cardinality_fails_rule_2(self):
        p = URIRef(CORE + "unshapedProperty")
        def change(g):
            g.add((p, RDF.type, OWL.DatatypeProperty))
            g.add((p, RDFS.range, XSD.string))
            g.add((URIRef(CORE + "x"), p, Literal("v")))
        problems = rule_problems(change)
        self.assertTrue(any(x.startswith("Rule 2") and "unshapedProperty" in x for x in problems), problems)

    def test_a_literal_range_fails_rule_1(self):
        p = URIRef(CORE + "taxonomyLevel")
        def change(g):
            g.remove((p, RDFS.range, None))
            g.add((p, RDFS.range, RDFS.Literal))
        problems = rule_problems(change)
        self.assertTrue(any(x.startswith("Rule 1") and "taxonomyLevel" in x for x in problems), problems)

    def test_a_blank_node_fails_rule_3(self):
        problems = rule_problems(lambda g: g.add((BNode(), RDF.type, OWL.Class)))
        self.assertIn("Rule 3: the data holds a blank node", problems)

    def test_an_unprefixed_namespace_fails_rule_3(self):
        problems = rule_problems(lambda g: g.add((URIRef(CORE + "x"), URIRef("https://example.org/p"), Literal("v"))))
        self.assertTrue(any(x.startswith("Rule 3: no fixed prefix") for x in problems), problems)

    def test_a_qualified_relation_with_two_ends_fails_rule_4a(self):
        a = next(DATA.subjects(RDF.type, URIRef(pl.OWN[1] + "ResponsibilityAssignment")))
        problems = rule_problems(lambda g: g.add((a, URIRef(pl.OWN[1] + "forProcess"), URIRef(CORE + "other"))))
        self.assertTrue(any(x.startswith("Rule 4a") for x in problems), problems)

    def test_a_scoped_sequence_with_two_earlier_processes_fails_rule_4a(self):
        seq = next(DATA.subjects(RDF.type, URIRef(CORE + "ScopedSequence")))
        problems = rule_problems(lambda g: g.add((seq, URIRef(CORE + "earlierProcess"), URIRef(CORE + "other"))))
        self.assertTrue(any(x.startswith("Rule 4a") and str(seq) in x for x in problems), problems)

    def test_a_measure_link_with_two_processes_fails_rule_4a(self):
        # The process end points to the link (vs:measureLink), as prov:qualifiedAssociation does.
        vs = "https://w3id.org/lsc/ontology/modules/value-stream/"
        link = next(DATA.subjects(RDF.type, URIRef(vs + "MeasureLink")))
        problems = rule_problems(lambda g: g.add((URIRef(vs + "process/other"), URIRef(vs + "measureLink"), link)))
        self.assertTrue(any(x.startswith("Rule 4a") and str(link) in x and "measureLink" in x for x in problems),
                        problems)

    def test_a_data_flow_with_two_sources_fails_rule_4a(self):
        party = "https://w3id.org/lsc/ontology/modules/party/"
        flow = next(DATA.subjects(RDF.type, URIRef(party + "DataFlow")))
        problems = rule_problems(lambda g: g.add((flow, URIRef(party + "fromSystem"), URIRef(party + "system/other"))))
        self.assertTrue(any(x.startswith("Rule 4a") and str(flow) in x for x in problems), problems)

    def test_lpg_names_carry_their_prefix_for_rule_5(self):
        # In SHORTEN mode the prefix keeps org:identifier and dcterms:identifier apart; a term whose
        # local part has a slash gets no name, and check_rules reports it.
        self.assertIsNone(pl.lpg_name("https://w3id.org/lsc/ontology/modules/core/a/b"))
        self.assertEqual(pl.lpg_name(str(RDFS.label), sep="__"), "rdfs__label")
        self.assertEqual(pl.lpg_name("http://www.w3.org/ns/org#identifier", sep="__"), "org__identifier")
        self.assertEqual(pl.lpg_name("http://purl.org/dc/terms/identifier", sep="__"), "dcterms__identifier")
        self.assertEqual(pl.lpg_name(str(RDFS.label), sep="_"), "rdfs_label")

    def test_the_separator_is_n10s_two_underscores_on_main_and_one_in_the_share_release(self):
        # Read from the two inputs themselves, so a wrong separator on main fails here (EPM-DEC-001-0110).
        marker = os.path.isfile(os.path.join(pl.ONTOLOGY, "..", "..", "release.json"))
        variable = bool(os.environ.get("EPM_SHARE_RELEASE"))
        self.assertEqual(pl.N10S_SEP, "__")
        self.assertEqual(pl.SHARE_RELEASE, marker or variable)
        self.assertEqual(pl.SEP, "_" if marker or variable else "__")
        if not (marker or variable):
            self.assertEqual(pl.lpg_name(str(RDFS.label)), "rdfs__label")

    def test_a_term_without_an_lpg_name_fails_rule_5(self):
        # In the core namespace (so Rule 3 passes) but with a slash in the local part, so SHORTEN
        # cannot name it.
        problems = rule_problems(lambda g: g.add((URIRef(CORE + "x"), URIRef(CORE + "a/b"), Literal("v"))))
        self.assertTrue(any(x.startswith("Rule 5: no LPG name") for x in problems), problems)

    def test_step_1_validates_the_inferred_triples_too(self):
        # An inferred type that breaks a shape must stop the build, as an asserted one would.
        from unittest import mock
        role = next(DATA.subjects(RDF.type, URIRef("http://www.w3.org/ns/org#Role")))
        bad = f"<{role}> <{RDF.type}> <{pl.OWN[1]}ResponsibilityAssignment> .\n"
        real_open = open
        def fake_open(path, *a, **k):
            if path == pl.INFERRED:
                import io
                return io.StringIO(bad)
            return real_open(path, *a, **k)
        with mock.patch("builtins.open", fake_open), mock.patch("os.path.exists", lambda p: True):
            with self.assertRaises(SystemExit):
                pl.build()

    def test_step_1_runs_the_sparql_targeted_process_shape(self):
        # Only core's ProcessConcept shape, whose target is a SPARQL query, limits a process to one
        # parent. Without SHACL-AF (advanced=True) it would not run and this would pass.
        g = Graph()
        g += DATA
        proc = URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-2-1")
        g.add((proc, URIRef("http://www.w3.org/2004/02/skos/core#broader"), URIRef("https://w3id.org/lsc/ontology/process/CM-1-1-3")))
        problems = pl.check(g, SHAPES)
        self.assertTrue(any(x.startswith("SHACL") and "broader" in x for x in problems), problems)

    def test_a_listed_release_gap_that_no_longer_occurs_fails_the_build(self):
        # core 2.0.0 closed core's two gaps; list one that does not occur.
        gap = f"Rule 1: {CORE}earlierProcess has no single concrete range"
        with mock.patch.dict(pl.RELEASE_EXCEPTIONS, {gap: "closed by core 2.0.0"}):
            problems = pl.check(DATA, SHAPES)
        self.assertTrue(any(x.startswith("listed release exception no longer occurs") for x in problems), problems)

    def test_a_property_without_its_range_fails_rule_1(self):
        problems = rule_problems(lambda g: g.remove((URIRef(CORE + "earlierProcess"), RDFS.range, None)))
        self.assertIn(f"Rule 1: {CORE}earlierProcess has no single concrete range", problems)


class Build(unittest.TestCase):
    def test_the_inputs_are_every_released_module_at_its_newest_version(self):
        # Pinned by hand (EPM-DEC-001-0036, amendment of 2026-10-22); a new release must be added here.
        self.assertEqual(pl.PACKAGES, [
            ("core", "2.4.0"), ("organization", "2.2.0"), ("ref-mpc", "1.3.0"), ("kpi", "1.3.0"), ("party", "2.1.0"),
            ("data-product", "1.2.0"), ("value-stream", "1.2.0"), ("system", "1.5.0"), ("lane", "1.1.0"),
            ("market-data", "1.1.0"), ("integration", "2.5.0"), ("technical-graph", "1.0.0")])
        import glob, os
        newest = {}
        for d in glob.glob(os.path.join(pl.ONTOLOGY, "releases", "*", "*", "")):
            module, version = d.rstrip(os.sep).split(os.sep)[-2:]
            if module == "previous":
                continue  # the share release keeps each module's previous package here; nothing loads it
            if module not in newest or tuple(map(int, version.split("."))) > tuple(map(int, newest[module].split("."))):
                newest[module] = version
        self.assertEqual(dict(pl.PACKAGES), newest)

    def test_the_manifest_is_current(self):
        _, _, manifest = pl.build()
        with open(pl.MANIFEST) as f:
            self.assertEqual(f.read(), manifest)

    def test_loadable_is_sorted_and_without_duplicates(self):
        loadable, _, _ = pl.build()
        lines = loadable.splitlines()
        self.assertEqual(lines, sorted(set(lines)))
        self.assertEqual(len(lines), len(DATA))

    def test_inferred_holds_only_iri_type_and_subclass_triples_outside_owl_and_rdfs(self):
        g = Graph().parse(pl.INFERRED, format="nt")
        for s, p, o in g:
            self.assertIn(p, (RDF.type, RDFS.subClassOf))
            self.assertIsInstance(o, URIRef)
            self.assertFalse(str(o).startswith((str(OWL), str(RDFS))))


class Report(unittest.TestCase):
    def test_a_shape_change_makes_the_report_stale(self):
        from unittest import mock
        real_open = open
        def edited(path, *a, **k):
            f = real_open(path, *a, **k)
            if str(path).endswith("releases/organization/2.2.0/shapes.ttl"):
                import io
                return io.StringIO(f.read() + "\n# edited\n")
            return f
        with mock.patch("builtins.open", edited):
            changed = pl.shapes_fingerprint()
        with real_open(pl.REPORT) as f:
            self.assertNotEqual(json.load(f)["shapes_fingerprint"], changed)

    def test_the_step_5_report_describes_the_current_inputs_and_passed(self):
        with open(pl.REPORT) as f:
            report = json.load(f)
        loadable, inferred, _ = pl.build()
        self.assertEqual(report["input_fingerprint"], pl.sha(loadable, inferred),
                         "projection-report.json is stale: run the driver, then pipeline.py record")
        self.assertEqual(report["shapes_fingerprint"], pl.shapes_fingerprint(),
                         "a shape file changed since the last load: run the driver, then pipeline.py record")
        self.assertEqual(report["shacl_violations_in_graph"], 0)
        self.assertGreater(report["in_graph_mutant_violations"], 0)
        self.assertEqual((report["roundtrip_lost"], report["roundtrip_added"]), (0, 0))
        self.assertEqual(report["determinism_hash_sorted"], report["determinism_hash_shuffled"])
        self.assertIs(report["rename_lossless"], True)
        self.assertEqual(report["separator"], pl.SEP)
        if not pl.SHARE_RELEASE:
            self.assertEqual((report["separator"], report["renamed"]), ("__", {}))  # main keeps the n10s names


class Record(unittest.TestCase):
    """pipeline.py record takes a driver run's result into this folder only when the run read this tree's inputs and
    its report passed. A stand-in run folder, with this folder's paths pointed at a temporary copy."""

    REPORT_OK = {"passed": True, "shacl_violations_in_graph": 0, "in_graph_shape_constraints": 7, "in_graph_mutant_violations": 1,
                 "roundtrip_lost": 0, "roundtrip_added": 0, "determinism_hash_sorted": "h", "determinism_hash_shuffled": "h",
                 "nodes": 3, "relationships": 2, "schema_relationships": 1, "export_rows": 5, "schema_rows_skipped": 1,
                 "separator": pl.SEP, "renamed": {}, "rename_lossless": True, "versions": {"method": "m"},
                 "compiled": ["left in the driver's folder"]}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = os.path.join(self.tmp.name, "run")
        os.makedirs(self.run_dir)
        for name in ("INFERRED", "MANIFEST", "REPORT"):
            patcher = mock.patch.object(pl, name, os.path.join(self.tmp.name, name.lower()))
            patcher.start()
            self.addCleanup(patcher.stop)
        files = [{"sha256": pl.sha(open(os.path.join(pl.ONTOLOGY, p)).read())} for p in pl.INPUTS + pl.SHAPES]
        self.write_run(files, self.REPORT_OK, pl.sorted_nt(pl.graph(pl.INPUTS)))

    def write_run(self, files, report, loaded):
        for name, text in (("run-manifest.json", json.dumps({"data": files[:1], "shapes": files[1:]})),
                           ("projection-report.json", json.dumps(report)), ("inferred.nt", ""), ("loadable.nt", loaded)):
            with open(os.path.join(self.run_dir, name), "w") as f:
                f.write(text)

    def test_a_run_of_this_tree_writes_the_three_files_and_only_the_summary(self):
        with mock.patch("sys.stdout", new_callable=lambda: __import__("io").StringIO()):
            pl.record(self.run_dir)
        with open(pl.REPORT) as f:
            report = json.load(f)
        loadable, inferred, manifest = pl.build()
        self.assertEqual(report["input_fingerprint"], pl.sha(loadable, inferred))
        self.assertEqual(report["shapes_fingerprint"], pl.shapes_fingerprint())
        self.assertEqual((report["nodes"], report["relationships"]), (3, 2))
        self.assertNotIn("compiled", report)
        with open(pl.MANIFEST) as f:
            self.assertEqual(f.read(), manifest)

    def test_a_run_of_other_inputs_is_refused_and_writes_nothing(self):
        with open(os.path.join(self.run_dir, "run-manifest.json"), "w") as f:
            json.dump({"data": [{"sha256": "other"}], "shapes": []}, f)
        with self.assertRaisesRegex(SystemExit, "other inputs"):
            pl.record(self.run_dir)
        self.assertFalse(os.path.exists(pl.REPORT))

    def test_a_run_that_loaded_other_triples_is_refused(self):
        with open(os.path.join(self.run_dir, "loadable.nt"), "w") as f:
            f.write("<urn:a> <urn:b> <urn:c> .\n")
        with self.assertRaisesRegex(SystemExit, "other triples"):
            pl.record(self.run_dir)

    def test_each_failed_check_stops_the_record(self):
        for change in ({"passed": False}, {"shacl_violations_in_graph": 1}, {"in_graph_mutant_violations": 0},
                       {"roundtrip_lost": 1}, {"roundtrip_added": 1}, {"determinism_hash_shuffled": "other"},
                       {"rename_lossless": False}):
            with self.subTest(change=change):
                with open(os.path.join(self.run_dir, "projection-report.json"), "w") as f:
                    json.dump({**self.REPORT_OK, **change}, f)
                with self.assertRaisesRegex(SystemExit, "cannot stand"):
                    pl.record(self.run_dir)
                self.assertFalse(os.path.exists(pl.REPORT))


if __name__ == "__main__":
    unittest.main()
