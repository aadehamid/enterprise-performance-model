"""Integrity tests for the process authority (`business_process/` and `../schema/`): each file
with a schema validates against it, process-map node ids and data product and line ids are unique, and these
references resolve: a value stream's linkedProcessIds and gapAnalysis closestProcessIds to
process-map nodes, its produces and consumes to data products or lines, its capabilityId to a
capability and its flows to processes in the same file, and each process-map officeLane to a
lane in office_lanes.json.

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
LANES = os.path.join(HERE, "office_lanes.json")


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

    def test_gap_analysis_closest_process_ids_resolve_to_process_map_nodes(self):
        nodes = set(map_ids())
        for name, vs in value_streams().items():
            for gap in vs.get("gapAnalysis", []):
                for ref in gap.get("closestProcessIds", []):
                    with self.subTest(f=name, item=gap["item"], ref=ref):
                        self.assertIn(ref, nodes)

    def test_flows_resolve_to_processes_in_the_same_file(self):
        for name, vs in value_streams().items():
            own = {p["id"] for stage in vs["stages"] for p in stage["processes"]}
            for flow in vs.get("flows", []):
                for end in ("from", "to"):
                    with self.subTest(f=name, end=end, ref=flow[end]):
                        self.assertIn(flow[end], own)

    def test_office_lanes_resolve_to_lanes(self):
        lanes = set(load(LANES))
        self.assertTrue(lanes)
        used = []

        def walk(node):
            if isinstance(node, dict):
                if "officeLane" in node:
                    used.append(node["officeLane"])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(load(MAP))
        self.assertTrue(used)
        for lane in used:
            with self.subTest(lane=lane):
                self.assertIn(lane, lanes)


if __name__ == "__main__":
    unittest.main()
