"""Tests for the technical-graph module (EPM-DEC-001-0112): the vocabulary, its shapes and the example graph.

Run: python3 -m pytest test_technical_graph.py
"""
import os
import sys
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "release"))
import build_example  # noqa: E402
import newest  # noqa: E402

TG = Namespace("https://w3id.org/lsc/ontology/modules/technical-graph/")
SH = Namespace("http://www.w3.org/ns/shacl#")
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
EXAMPLE = Graph().parse(build_example.OUTPUT)
ONTOLOGY = os.path.join(HERE, "..")
# The releases the module links to by IRI; a graph that uses the vocabulary is checked with them loaded.
LINKED = Graph()
for module in ("data-product", "kpi", "system"):
    LINKED.parse(os.path.join(ONTOLOGY, "releases", module, newest.newest_version(module, ONTOLOGY), f"{module}.ttl"))


def conforms(data):
    ok, _, text = validate(VOCAB + LINKED + data, shacl_graph=SHAPES, inference="none")
    return ok, text


class Vocabulary(unittest.TestCase):
    def test_every_term_has_a_label_a_definition_and_a_citation(self):
        terms = [s for s in set(VOCAB.subjects(RDF.type, None)) if str(s).startswith(str(TG))
                 and not str(s).startswith(str(TG) + "check-result/")]
        self.assertGreater(len(terms), 30)
        for term in terms:
            self.assertEqual(len(list(VOCAB.objects(term, SKOS.definition))), 1, term)
            self.assertTrue(list(VOCAB.objects(term, DCTERMS.bibliographicCitation)), term)

    def test_the_layer_list_is_data_products_not_a_new_one(self):
        # new-module.md, step 2: point to another module's terms by IRI; never redefine them.
        self.assertFalse(any("Layer" in str(s) for s in VOCAB.subjects(RDF.type, SKOS.ConceptScheme)))

    def test_no_owner_property(self):
        # EPM-DEC-001-0112, item 3: who answers for it is found through the data product, not a property here.
        props = {str(s) for s in VOCAB.subjects(RDF.type, OWL.ObjectProperty)} | {str(s) for s in VOCAB.subjects(RDF.type, OWL.DatatypeProperty)}
        self.assertFalse([p for p in props if "owner" in p.lower() or "accountab" in p.lower()])

    def test_every_check_result_is_a_top_concept_both_ways(self):
        for c in VOCAB.objects(TG.CheckResults, SKOS.hasTopConcept):
            self.assertIn((c, SKOS.topConceptOf, TG.CheckResults), VOCAB)

    def test_no_shape_message_has_an_apostrophe(self):
        # The ontology skill's SHACL rule 19: some stores mangle an apostrophe in a message.
        for msg in SHAPES.objects(None, SH.message):
            self.assertNotIn("'", str(msg))


class Example(unittest.TestCase):
    def test_the_example_is_current(self):
        text = ("# The technical-graph module's example graph: test data, not ontology content (EPM-DEC-001-0112, item 4).\n"
                "# Built by build_example.py from the pricing demo's technical graph. Do not edit by hand.\n"
                + build_example.build().serialize(format="turtle"))
        with open(build_example.OUTPUT) as f:
            self.assertEqual(f.read(), text, "run build_example.py --write")

    def test_the_example_uses_only_the_vocabulary(self):
        defined = set(VOCAB.subjects())
        used = {p for p in EXAMPLE.predicates() if str(p).startswith(str(TG))}
        used |= {o for o in EXAMPLE.objects(None, RDF.type) if str(o).startswith(str(TG))}
        self.assertEqual(used - defined, set())

    def test_the_example_conforms(self):
        ok, text = conforms(EXAMPLE)
        self.assertTrue(ok, text)

    def test_the_demos_graph_conforms_in_the_modules_terms(self):
        # The demo moves to the module's terms after its 1.0.0 (EPM-DEC-001-0112, item 4); its graph already fits.
        ok, text = conforms(build_example.to_module(Graph().parse(build_example.DEMO_GRAPH)))
        self.assertTrue(ok, text)


class Shapes(unittest.TestCase):
    """Each shape rejects what it forbids (the ontology skill's negative tests)."""

    def broken(self, change):
        g = Graph()
        g += EXAMPLE
        change(g)
        return conforms(g)[0]

    def first(self, cls):
        return sorted(EXAMPLE.subjects(RDF.type, cls))[0]

    def test_a_result_off_the_list_fails(self):
        check = self.first(TG.QualityCheck)
        self.assertFalse(self.broken(lambda g: (g.remove((check, TG.result, None)),
                                                g.add((check, TG.result, URIRef("urn:example:unknown"))))))

    def test_a_metric_view_computing_no_measure_fails(self):
        view = self.first(TG.MetricView)
        self.assertFalse(self.broken(lambda g: g.remove((view, TG.implements, None))))

    def test_a_layer_outside_data_products_list_fails(self):
        table = self.first(TG.Table)
        self.assertFalse(self.broken(lambda g: (g.remove((table, TG.layer, None)),
                                                g.add((table, TG.layer, URIRef("urn:example:bronze"))))))

    def test_two_layers_fail(self):
        table = next(t for t in sorted(EXAMPLE.subjects(RDF.type, TG.Table)) if (t, TG.layer, None) in EXAMPLE)
        layer = URIRef("https://w3id.org/lsc/ontology/modules/data-product/layer/gold")
        other = URIRef("https://w3id.org/lsc/ontology/modules/data-product/layer/silver")
        self.assertFalse(self.broken(lambda g: (g.add((table, TG.layer, layer)), g.add((table, TG.layer, other)))))

    def test_reading_from_something_not_a_data_object_fails(self):
        view = self.first(TG.MetricView)
        self.assertFalse(self.broken(lambda g: g.add((view, TG.readsFrom, self.first(TG.PipelineStep)))))

    def test_a_check_with_no_time_fails(self):
        check = self.first(TG.QualityCheck)
        self.assertFalse(self.broken(lambda g: g.remove((check, TG.checkedAt, None))))

    def test_a_step_with_no_order_fails(self):
        step = self.first(TG.PipelineStep)
        self.assertFalse(self.broken(lambda g: g.remove((step, TG.order, None))))

    def test_a_database_standing_for_a_non_system_fails(self):
        db = self.first(TG.SourceDatabase)
        self.assertFalse(self.broken(lambda g: (g.remove((db, TG.standsFor, None)),
                                                g.add((db, TG.standsFor, URIRef("urn:example:not-a-system"))))))

    def test_an_orchestrator_routing_nowhere_fails(self):
        orchestrator = self.first(TG.Orchestrator)
        self.assertFalse(self.broken(lambda g: g.remove((orchestrator, TG.routesTo, None))))

    def test_a_check_result_with_two_labels_fails(self):
        result = URIRef("https://w3id.org/lsc/ontology/modules/technical-graph/check-result/pass")
        self.assertFalse(self.broken(lambda g: g.add((result, SKOS.prefLabel, Literal("Passed", lang="en")))))

    def test_a_table_copying_two_databases_fails(self):
        table = next(t for t in sorted(EXAMPLE.subjects(TG.copies, None)))
        other = next(d for d in sorted(EXAMPLE.subjects(RDF.type, TG.SourceDatabase)) if (table, TG.copies, d) not in EXAMPLE)
        self.assertFalse(self.broken(lambda g: g.add((table, TG.copies, other))))

    def test_an_agent_bound_to_a_non_data_object_fails(self):
        agent = self.first(TG.Agent)
        self.assertFalse(self.broken(lambda g: g.add((agent, TG.binds, self.first(TG.PipelineStep)))))

    def test_two_producing_steps_fail(self):
        table = next(t for t in sorted(EXAMPLE.subjects(TG.producedBy, None)) if (t, RDF.type, TG.Table) in EXAMPLE)
        other = next(s for s in sorted(EXAMPLE.subjects(RDF.type, TG.PipelineStep)) if (table, TG.producedBy, s) not in EXAMPLE)
        self.assertFalse(self.broken(lambda g: g.add((table, TG.producedBy, other))))

    def test_a_design_that_is_neither_a_concept_nor_an_agent_fails(self):
        table = self.first(TG.Table)
        self.assertFalse(self.broken(lambda g: (g.remove((table, TG.designedAs, None)),
                                                g.add((table, TG.designedAs, URIRef("urn:example:not-a-design"))))))

    def test_a_check_testing_nothing_fails(self):
        check = self.first(TG.QualityCheck)
        self.assertFalse(self.broken(lambda g: g.remove((check, TG.checks, None))))

    def test_a_refresh_that_is_not_a_time_fails(self):
        table = next(t for t in sorted(EXAMPLE.subjects(TG.lastRefresh, None)))
        self.assertFalse(self.broken(lambda g: (g.remove((table, TG.lastRefresh, None)),
                                                g.add((table, TG.lastRefresh, Literal("yesterday"))))))

    def test_a_database_on_two_hosts_fails(self):
        db = next(d for d in sorted(EXAMPLE.subjects(TG.hostedOn, None)))
        self.assertFalse(self.broken(lambda g: g.add((db, TG.hostedOn, URIRef("urn:example:another-host")))))

    def test_a_name_in_two_forms_fails(self):
        table = self.first(TG.Table)
        self.assertFalse(self.broken(lambda g: g.add((table, TG.name, Literal("another name")))))


if __name__ == "__main__":
    unittest.main()
