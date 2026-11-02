"""Tests for the logical-model module (EPM-DEC-001-0113): the vocabulary, its shapes, the builder and the made-up example.

Every export here is made up. The customer model never enters `main` (EPM-DEC-001-0113, decision 2).

Run: python3 -m pytest test_logical_model.py
"""
import csv
import io
import os
import shutil
import sys
import tempfile
import unittest

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_logical_model as blm  # noqa: E402

ONTOLOGY = os.path.join(HERE, "..")
LM, ER = blm.LM, blm.ER
SH = Namespace("http://www.w3.org/ns/shacl#")
EXAMPLE = os.path.join(HERE, "example")
EXPORT = os.path.join(EXAMPLE, "example-export.ttl")
LINKS = os.path.join(EXAMPLE, "example-links.csv")
SLUG, TITLE = "example-logical-model", "An example logical model"
VOCAB = Graph().parse(os.path.join(HERE, "vocabulary.ttl"))
SHAPES = Graph().parse(os.path.join(HERE, "shapes.ttl"))
LINKED = blm.releases()
EXPORT_GRAPH = Graph().parse(EXPORT)
LAYER = Graph().parse(os.path.join(EXAMPLE, f"{SLUG}.layer.ttl"))
ACCOUNT = ER["example_core_Example_Account_Dim"]
CONTACT = ER["example_core_Example_Contact_Dim"]
REGION = ER["example_core_Example_Region_Ref"]
MODEL = LM["model/" + SLUG]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def conforms(layer, export=EXPORT_GRAPH):
    ok, _, text = validate(VOCAB + LINKED + export + layer, shacl_graph=SHAPES, inference="none")
    return ok, text


class Build(unittest.TestCase):
    """The builder, run on made-up exports and links files in a temporary folder."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def links(self, change=None, slug=SLUG):
        rows = list(csv.DictReader(io.StringIO(read(LINKS))))
        for r in rows:
            r["model"] = slug
        if change:
            change(rows)
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=blm.COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        return out.getvalue()

    def build(self, export_text=None, links_text=None, slug=SLUG):
        export = self.write(f"{slug}-export.ttl", export_text if export_text is not None else read(EXPORT))
        links = self.write(f"{slug}-links.csv", links_text if links_text is not None else self.links(slug=slug))
        return blm.build([(export, links, slug, TITLE)], os.path.join(self.tmp, "out"))

    def layer_of(self, files, slug=SLUG):
        return Graph().parse(data=files[f"{slug}.layer.ttl"].decode("utf-8"), format="turtle")

    def test_a_renamed_entity_keeps_its_annotations(self):
        # The layer is keyed on ER Studio's identifier, not the IRI it builds from the name (decision 5).
        renamed = read(EXPORT).replace("Example_Account_Dim", "Example_Client_Account_Dim")
        files, _ = self.build(renamed)
        layer = self.layer_of(files)
        new = ER["example_core_Example_Client_Account_Dim"]
        self.assertIn((new, LM.describes, URIRef("https://w3id.org/lsc/ontology/modules/party/CustomerAccount")), layer)
        self.assertNotIn((ACCOUNT, LM.inModel, MODEL), layer)

    def test_a_removed_entity_fails(self):
        text = read(EXPORT).replace('dcterms:identifier "102"', 'dcterms:identifier "999"')
        with self.assertRaises(blm.BuildError) as e:
            self.build(text)
        self.assertIn("identifier 102", str(e.exception))

    def test_an_entity_is_found_by_a_class_not_by_an_attribute_sharing_its_number(self):
        # Entities and attributes share one identifier space: attribute Account_Region_Code is also 103.
        self.assertIn((ER["Attribute_example_core_Example_Account_Dim_Account_Region_Code"], DCTERMS.identifier,
                       Literal("103")), EXPORT_GRAPH)
        files, _ = self.build(links_text=self.links(lambda rows: rows[2].update(status="asserted")))
        layer = self.layer_of(files)
        self.assertIn((REGION, LM.sourceSystem, URIRef("https://w3id.org/lsc/ontology/modules/system/system/mips")), layer)
        self.assertEqual(len(list(layer.subjects(LM.sourceSystem, None))), 3)

    def test_two_entities_with_one_identifier_fail(self):
        text = read(EXPORT).replace('dcterms:identifier "102"', 'dcterms:identifier "101"')
        with self.assertRaises(blm.BuildError):
            self.build(text)

    def test_a_bad_link_target_fails(self):
        for column, value in (("source_system", "https://w3id.org/lsc/ontology/modules/system/system/no-such-system"),
                              ("source_system", "https://w3id.org/lsc/ontology/modules/party/CustomerAccount"),
                              ("describes", "https://w3id.org/lsc/ontology/modules/system/system/profisee"),
                              ("describes", "https://w3id.org/lsc/ontology/modules/party/NoSuchClass"),
                              ("implemented_by", "https://w3id.org/lsc/ontology/modules/data-product/product/no-such-product"),
                              ("implemented_by", "https://w3id.org/lsc/ontology/modules/party/CustomerAccount")):
            with self.subTest(column=column, value=value):
                with self.assertRaises(blm.BuildError):
                    self.build(links_text=self.links(lambda rows: rows[0].update({column: value})))

    def test_an_empty_source_system_fails(self):
        # Codex's quick check: an empty column could be a mistake, so the row must say which case it is.
        with self.assertRaises(blm.BuildError):
            self.build(links_text=self.links(lambda rows: rows[0].update(source_system="")))

    def test_an_asserted_row_may_say_no_module_holds_its_system(self):
        # Decided under EPM-DEC-001-0028: when neither module holds the entity's system, its other links still count.
        files, _ = self.build(links_text=self.links(lambda rows: rows[0].update(source_system=blm.NO_SYSTEM)))
        layer = self.layer_of(files)
        entity = next(iter(layer.subjects(LM.describes, None)))
        self.assertIsNone(layer.value(entity, LM.sourceSystem))
        self.assertIsNotNone(layer.value(entity, LM.describes))

    def test_a_system_of_either_module_is_accepted(self):
        files, _ = self.build()
        layer = self.layer_of(files)
        self.assertIn((ACCOUNT, LM.sourceSystem, URIRef("https://w3id.org/lsc/ontology/modules/system/system/profisee")), layer)
        self.assertIn((CONTACT, LM.sourceSystem, URIRef("https://w3id.org/lsc/ontology/modules/party/system/gravitate")), layer)

    def test_doubtful_rows_produce_no_triples(self):
        files, report = self.build()
        layer = self.layer_of(files)
        self.assertEqual(set(layer.predicate_objects(REGION)), {(LM.inModel, MODEL)})
        self.assertTrue(any("doubtful" in line and "103" in line for line in report))

    def test_a_bad_status_or_a_repeated_row_fails(self):
        with self.assertRaises(blm.BuildError):
            self.build(links_text=self.links(lambda rows: rows[0].update(status="maybe")))
        with self.assertRaises(blm.BuildError):
            self.build(links_text=self.links(lambda rows: rows.append(dict(rows[0]))))

    def test_an_entity_with_no_description_and_no_key_builds(self):
        self.assertIsNone(EXPORT_GRAPH.value(REGION, DCTERMS.description))
        self.assertFalse(list(EXPORT_GRAPH.subjects(SH.targetClass, REGION)))
        files, _ = self.build()
        self.assertIn((REGION, LM.inModel, MODEL), self.layer_of(files))

    def test_a_key_shape_on_an_attribute_of_another_entity_fails(self):
        text = read(EXPORT).replace("sh:path :example_core_Example_Contact_Dim_Contact_Id",
                                    "sh:path :example_core_Example_Account_Dim_Account_Id")
        with self.assertRaises(blm.BuildError):
            self.build(text)

    def test_a_second_ontology_header_fails(self):
        with self.assertRaises(blm.BuildError):
            self.build(read(EXPORT) + "\n<urn:example:another-header> a owl:Ontology .\n")

    def test_two_models_sharing_only_ER_Studios_vocabulary_and_header_build(self):
        # Every export declares :Ontology, the vocabulary and the glossary; none of them is a collision.
        other = read(EXPORT).replace("example_core_", "other_core_").replace("2026-01-01", "2026-02-01")
        first = self.write("first.ttl", read(EXPORT))
        second = self.write("second.ttl", other)
        files, _ = blm.build([(first, self.write("a.csv", self.links()), SLUG, TITLE),
                              (second, self.write("b.csv", self.links(slug="other-model")), "other-model", "Another")],
                             os.path.join(self.tmp, "out"))
        self.assertEqual(sorted(files), ["example-logical-model.erstudio.ttl", "example-logical-model.layer.ttl",
                                         "other-model.erstudio.ttl", "other-model.layer.ttl"])
        # Each model's header time lands on its own model individual, not on a merged header.
        self.assertEqual(len(list(self.layer_of(files, "other-model").objects(LM["model/other-model"], DCTERMS.created))), 1)

    def test_two_models_defining_one_entity_fail(self):
        first = self.write("first.ttl", read(EXPORT))
        second = self.write("second.ttl", read(EXPORT).replace("example_core_Example_Account_Dim", "other_core_Example_Account_Dim"))
        with self.assertRaises(blm.BuildError) as e:
            blm.build([(first, self.write("a.csv", self.links()), SLUG, TITLE),
                       (second, self.write("b.csv", self.links(slug="other-model")), "other-model", "Another")],
                      os.path.join(self.tmp, "out"))
        self.assertIn("both define", str(e.exception))

    def test_a_model_already_in_the_folder_takes_part_in_the_collision_check(self):
        out = os.path.join(self.tmp, "out")
        os.makedirs(out)
        shutil.copy(EXPORT, os.path.join(out, "earlier-model.erstudio.ttl"))
        with self.assertRaises(blm.BuildError):
            self.build()

    def test_a_glossary_term_described_differently_by_two_models_fails(self):
        first = self.write("first.ttl", read(EXPORT))
        other = read(EXPORT).replace("example_core_", "other_core_").replace('"Example Account Name"', '"Account title"')
        with self.assertRaises(blm.BuildError):
            blm.build([(first, self.write("a.csv", self.links()), SLUG, TITLE),
                       (self.write("second.ttl", other), self.write("b.csv", self.links(slug="other-model")), "other-model", "x")],
                      os.path.join(self.tmp, "out"))


class Example(unittest.TestCase):
    def test_the_example_is_current(self):
        files, _ = blm.build([(EXPORT, LINKS, SLUG, TITLE)], EXAMPLE)
        for name, data in files.items():
            with open(os.path.join(EXAMPLE, name), "rb") as f:
                self.assertEqual(f.read(), data, f"{name}: run build_logical_model.py --write (scripts/check.sh has the line)")

    def test_the_export_is_kept_byte_for_byte(self):
        with open(EXPORT, "rb") as a, open(os.path.join(EXAMPLE, f"{SLUG}.erstudio.ttl"), "rb") as b:
            self.assertEqual(a.read(), b.read())

    def test_the_example_conforms(self):
        ok, text = conforms(LAYER)
        self.assertTrue(ok, text)

    def test_every_entity_is_in_the_model(self):
        entities = {c for c in EXPORT_GRAPH.subjects(RDF.type, OWL.Class) if (c, DCTERMS.identifier, None) in EXPORT_GRAPH}
        self.assertEqual(set(LAYER.subjects(LM.inModel, MODEL)), entities)

    def test_the_layer_uses_only_the_vocabulary(self):
        used = {p for p in LAYER.predicates() if str(p).startswith(str(LM))}
        used |= {o for o in LAYER.objects(None, RDF.type) if str(o).startswith(str(LM))}
        self.assertEqual(used - set(VOCAB.subjects()), set())


class Vocabulary(unittest.TestCase):
    def test_every_term_has_a_label_a_definition_and_a_citation(self):
        terms = {s for s in VOCAB.subjects(RDF.type, None) if str(s).startswith(str(LM))}
        self.assertEqual(terms, {LM.LogicalModel, LM.inModel, LM.sourceSystem, LM.describes, LM.implementedBy})
        for term in terms:
            self.assertEqual(len(list(VOCAB.objects(term, RDFS.label))), 1, term)
            self.assertEqual(len(list(VOCAB.objects(term, SKOS.definition))), 1, term)
            self.assertIn("EPM-DEC-001-0113", str(VOCAB.value(term, DCTERMS.bibliographicCitation)), term)

    def test_the_links_are_annotation_properties(self):
        # So ER Studio's classes stay plain classes when the layer is loaded with the export (decision 4).
        for p in (LM.inModel, LM.sourceSystem, LM.describes, LM.implementedBy):
            self.assertEqual(set(VOCAB.objects(p, RDF.type)), {OWL.AnnotationProperty}, p)

    def test_no_shape_message_has_an_apostrophe(self):
        for msg in SHAPES.objects(None, SH.message):
            self.assertNotIn("'", str(msg))


class Questions(unittest.TestCase):
    GRAPH = VOCAB + EXPORT_GRAPH + LAYER

    def rows(self, name):
        with open(os.path.join(ONTOLOGY, "regression", "queries", name)) as f:
            return list(self.GRAPH.query(f.read()))

    def test_q53_lists_the_primary_and_the_alternate_key(self):
        keys = {(str(r.keyType), str(r.attribute).rsplit("_", 2)[-2] + "_" + str(r.attribute).rsplit("_", 1)[-1])
                for r in self.rows("q53-customer-keys.rq") if r.entity == ACCOUNT}
        self.assertEqual(keys, {(str(ER.PrimaryKey), "Account_Id"), (str(ER.AlternateKey), "Account_Number")})

    def test_q54_splits_attributes_with_and_without_a_term(self):
        with_term = {str(r.attribute) for r in self.rows("q54-business-term.rq")}
        without = {str(r.attribute): r.linkMissing for r in self.rows("q54b-no-business-term.rq")}
        self.assertEqual(with_term, {str(ER["Attribute_example_core_Example_Account_Dim_Account_Name"])})
        self.assertFalse(with_term & set(without))
        self.assertTrue(all(flag == Literal(True) for flag in without.values()))

    def test_q55_lists_the_entities_with_no_implementation(self):
        self.assertEqual({r.entity for r in self.rows("q55b-not-implemented.rq")}, {CONTACT, REGION})


class Shapes(unittest.TestCase):
    """Each shape rejects what it forbids (the ontology skill's negative tests)."""

    def broken(self, change, export=EXPORT_GRAPH):
        g = Graph()
        g += LAYER
        change(g)
        return conforms(g, export)[0]

    def test_a_model_with_no_title_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MODEL, RDFS.label, None))))

    def test_a_model_with_no_slug_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((MODEL, DCTERMS.identifier, None))))

    def test_an_entity_in_two_models_fails(self):
        other = LM["model/other"]
        self.assertFalse(self.broken(lambda g: (g.add((other, RDF.type, LM.LogicalModel)),
                                                g.add((other, RDFS.label, Literal("Other", lang="en"))),
                                                g.add((other, DCTERMS.identifier, Literal("other"))),
                                                g.add((ACCOUNT, LM.inModel, other)))))

    def test_an_annotated_entity_in_no_model_fails(self):
        self.assertFalse(self.broken(lambda g: g.remove((ACCOUNT, LM.inModel, None))))

    def test_a_model_that_is_not_a_logical_model_fails(self):
        self.assertFalse(self.broken(lambda g: (g.remove((ACCOUNT, LM.inModel, None)),
                                                g.add((ACCOUNT, LM.inModel, URIRef("urn:example:not-a-model"))))))

    def test_annotating_something_that_is_not_an_entity_fails(self):
        attribute = ER["Attribute_example_core_Example_Account_Dim_Account_Id"]
        self.assertFalse(self.broken(lambda g: g.add((attribute, LM.inModel, MODEL))))

    def test_an_entity_with_no_identifier_fails(self):
        export = Graph()
        export += EXPORT_GRAPH
        export.remove((ACCOUNT, DCTERMS.identifier, None))
        self.assertFalse(self.broken(lambda g: None, export))

    def test_a_source_system_that_is_not_a_system_fails(self):
        self.assertFalse(self.broken(lambda g: (g.remove((ACCOUNT, LM.sourceSystem, None)),
                                                g.add((ACCOUNT, LM.sourceSystem, URIRef("https://w3id.org/lsc/ontology/modules/party/CustomerAccount"))))))

    def test_two_source_systems_fail(self):
        self.assertFalse(self.broken(lambda g: g.add((ACCOUNT, LM.sourceSystem, URIRef("https://w3id.org/lsc/ontology/modules/system/system/mips")))))

    def test_describing_something_outside_party_fails(self):
        self.assertFalse(self.broken(lambda g: (g.remove((ACCOUNT, LM.describes, None)),
                                                g.add((ACCOUNT, LM.describes, URIRef("https://w3id.org/lsc/ontology/modules/system/system/mips"))))))

    def test_describing_two_concepts_fails(self):
        self.assertFalse(self.broken(lambda g: g.add((ACCOUNT, LM.describes, URIRef("https://w3id.org/lsc/ontology/modules/party/Party")))))

    def test_an_implementation_outside_data_product_fails(self):
        self.assertFalse(self.broken(lambda g: (g.remove((ACCOUNT, LM.implementedBy, None)),
                                                g.add((ACCOUNT, LM.implementedBy, URIRef("https://w3id.org/lsc/ontology/modules/party/CustomerAccount"))))))

    def test_two_implementations_fail(self):
        self.assertFalse(self.broken(lambda g: g.add((ACCOUNT, LM.implementedBy, URIRef(
            "https://w3id.org/lsc/ontology/modules/data-product/table/gold-mips-mpr-executive-summary-fact")))))


if __name__ == "__main__":
    unittest.main()
