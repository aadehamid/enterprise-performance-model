"""Integrity tests for the process authority (`business_process/` and `../schema/`): each file
validates against its schema, process-map node ids are unique, and every reference a value
stream makes resolves (to a process-map node, a data product or line, or a capability in the
same file).

Run: python3 -m pytest test_business_process.py (needs jsonschema).
"""
import collections
import glob
import json
import os
import unittest

import jsonschema

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "..", "schema")
MAP = os.path.join(HERE, "downstream_process_map.json")
PORTFOLIO = os.path.join(HERE, "data_product_portfolio.json")


def load(path):
    with open(path) as f:
        return json.load(f)


def ids(node, keep):
    """Every string `id` in the tree for which keep(node, id) is true."""
    found = []
    if isinstance(node, dict):
        if isinstance(node.get("id"), str) and keep(node, node["id"]):
            found.append(node["id"])
        for value in node.values():
            found += ids(value, keep)
    elif isinstance(node, list):
        for value in node:
            found += ids(value, keep)
    return found


def map_ids():
    return ids(load(MAP), lambda node, _: "name" in node)


def product_ids():
    return ids(load(PORTFOLIO), lambda _, i: i.startswith(("dp-", "dpl-")))


def value_streams():
    return {os.path.basename(f): load(f) for f in sorted(glob.glob(os.path.join(HERE, "value_stream_*.json")))}


def processes():
    for name, vs in value_streams().items():
        for stage in vs["stages"]:
            for p in stage["processes"]:
                yield name, vs, p


def errors(schema_file, data):
    validator = jsonschema.Draft202012Validator(load(os.path.join(SCHEMA, schema_file)))
    return [f"{list(e.path)}: {e.message}" for e in validator.iter_errors(data)]


class Schemas(unittest.TestCase):
    def test_the_data_product_portfolio_validates_against_its_schema(self):
        self.assertEqual(errors("data_product_portfolio.schema.json", load(PORTFOLIO)), [])

    def test_every_value_stream_validates_against_its_schema(self):
        self.assertTrue(value_streams())
        for name, vs in value_streams().items():
            with self.subTest(f=name):
                self.assertEqual(errors("value_stream.schema.json", vs), [])


class Identity(unittest.TestCase):
    def test_process_map_node_ids_are_unique(self):
        counts = collections.Counter(map_ids())
        self.assertTrue(counts)
        self.assertEqual(sorted(i for i, n in counts.items() if n > 1), [])

    def test_data_product_ids_are_unique(self):
        counts = collections.Counter(product_ids())
        self.assertTrue(counts)
        self.assertEqual(sorted(i for i, n in counts.items() if n > 1), [])


class References(unittest.TestCase):
    """Every reference resolves today, so there are no known exceptions."""

    def test_linked_process_ids_resolve_to_process_map_nodes(self):
        nodes = set(map_ids())
        for name, _, p in processes():
            for ref in p.get("linkedProcessIds", []):
                with self.subTest(f=name, process=p["id"], ref=ref):
                    self.assertIn(ref, nodes)

    def test_produces_and_consumes_resolve_to_data_products(self):
        products = set(product_ids())
        for name, _, p in processes():
            for key in ("produces", "consumes"):
                for ref in p.get(key, []):
                    with self.subTest(f=name, process=p["id"], key=key, ref=ref):
                        self.assertIn(ref, products)

    def test_capability_ids_resolve_within_the_same_file(self):
        for name, vs, p in processes():
            with self.subTest(f=name, process=p["id"]):
                self.assertIn(p["capabilityId"], {c["id"] for c in vs.get("capabilities", [])})


if __name__ == "__main__":
    unittest.main()
