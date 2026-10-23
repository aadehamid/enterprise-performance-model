"""Tests for the Step 12 projection pipeline (EPM-DEC-001-0036). They need no Neo4j: they check the
rules (Step 1), the build and its manifest (Step 3), the comparison rules of the round trip, and that
the committed Step 5 report describes the current inputs and passed.

Run: python3 -m pytest test_pipeline.py (needs rdflib, pyshacl).
"""
import json
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
        self.assertEqual(pl.lpg_name(str(RDFS.label)), "rdfs__label")
        self.assertEqual(pl.lpg_name("http://www.w3.org/ns/org#identifier"), "org__identifier")
        self.assertEqual(pl.lpg_name("http://purl.org/dc/terms/identifier"), "dcterms__identifier")

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
            ("core", "2.3.0"), ("organization", "2.0.0"), ("ref-mpc", "1.2.0"), ("kpi", "1.1.1"), ("party", "1.1.0"),
            ("data-product", "1.1.0"), ("value-stream", "1.1.0"), ("system", "1.0.0"), ("lane", "1.0.0"),
            ("market-data", "1.0.0"), ("integration", "1.0.1")])
        import glob, os
        newest = {}
        for d in glob.glob(os.path.join(pl.ONTOLOGY, "releases", "*", "*", "")):
            module, version = d.rstrip(os.sep).split(os.sep)[-2:]
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


class RoundTripRules(unittest.TestCase):
    def test_a_plain_and_an_xsd_string_literal_compare_equal(self):
        self.assertEqual(pl.canonical(Literal("a")), pl.canonical(Literal("a", datatype=XSD.string)))

    def test_integer_and_long_compare_equal(self):
        self.assertEqual(pl.canonical(Literal("5", datatype=XSD.integer)), pl.canonical(Literal("5", datatype=XSD.long)))

    def test_decimal_and_double_compare_by_value(self):
        self.assertEqual(pl.canonical(Literal("0.64", datatype=XSD.decimal)), pl.canonical(Literal("0.64", datatype=XSD.double)))
        self.assertNotEqual(pl.canonical(Literal("0.64", datatype=XSD.decimal)), pl.canonical(Literal("0.65", datatype=XSD.double)))

    def test_a_language_tag_is_kept(self):
        self.assertNotEqual(pl.canonical(Literal("a", lang="en")), pl.canonical(Literal("a")))
        self.assertEqual(pl.LANG_SUFFIX.match("Refinery Scheduler@en").groups(), ("Refinery Scheduler", "en"))

    def test_in_graph_shapes_drop_what_n10s_cannot_check(self):
        g = pl.in_graph_shapes(SHAPES)
        self.assertNotIn((None, pl.SH.datatype, RDF.langString), g)
        for p in pl.N10S_UNSUPPORTED:
            self.assertNotIn((None, p, None), g)
        self.assertTrue(set(g.subjects(pl.SH.targetClass, None)))

    def test_in_graph_shapes_drop_a_literal_list_but_keep_an_iri_list(self):
        # market-data's sh:in (true) on mkt:legsUnstated goes; party's list of entity classes stays.
        g = pl.in_graph_shapes(SHAPES)
        lists = [pl.Collection(g, o) for o in g.objects(None, pl.SH["in"])]
        self.assertTrue(lists)
        self.assertFalse(any(isinstance(m, Literal) for c in lists for m in c))
        party = URIRef("https://w3id.org/lsc/ontology/modules/party/Party")
        self.assertTrue(any(party in list(c) for c in lists))


class Report(unittest.TestCase):
    def test_a_shape_change_makes_the_report_stale(self):
        from unittest import mock
        real_open = open
        def edited(path, *a, **k):
            f = real_open(path, *a, **k)
            if str(path).endswith("releases/organization/2.0.0/shapes.ttl"):
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
                         "projection-report.json is stale: rerun pipeline.py load-verify")
        self.assertEqual(report["shapes_fingerprint"], pl.shapes_fingerprint(),
                         "a shape file changed since the last Step 5 run: rerun pipeline.py load-verify")
        self.assertEqual(report["shacl_violations_in_graph"], 0)
        self.assertGreater(report["in_graph_mutant_violations"], 0)
        self.assertEqual((report["roundtrip_lost"], report["roundtrip_added"]), (0, 0))
        self.assertEqual(report["determinism_hash_sorted"], report["determinism_hash_shuffled"])


if __name__ == "__main__":
    unittest.main()
