"""Tests for dependents.py: what a change re-releases, and in what order."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dependents as d  # noqa: E402

TABLE = {"a": {"depends_on": ["core"]}, "b": {"depends_on": ["a"]}, "c": {"depends_on": ["a", "b"]},
         "e": {"depends_on": ["core"]}}


class Dependents(unittest.TestCase):
    def test_a_module_comes_before_what_needs_it(self):
        self.assertEqual(d.dependents("a", TABLE), ["a", "b", "c"])

    def test_core_reaches_every_module_that_names_it(self):
        self.assertEqual(d.dependents("core", TABLE), ["a", "e", "b", "c"])

    def test_a_module_nothing_needs_is_alone(self):
        self.assertEqual(d.dependents("e", TABLE), ["e"])

    def test_a_cycle_stops(self):
        with self.assertRaises(SystemExit):
            d.dependents("a", {"a": {"depends_on": ["b"]}, "b": {"depends_on": ["a"]}})


if __name__ == "__main__":
    unittest.main()
