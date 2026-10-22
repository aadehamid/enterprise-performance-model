"""Tests for the APQC element list (Step 7; EPM-DEC-001-0060): the build is current, the count
matches the workbook's Combined sheet, every element core 2.2.0 references is listed, and two
elements are pinned by hand.

Run: python3 -m pytest test_apqc_elements.py (needs rdflib, openpyxl).
"""
import os
import subprocess
import sys
import unittest

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDFS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_apqc_elements as ba  # noqa: E402

DATA = Graph().parse(os.path.join(HERE, "apqc-elements.ttl"))


class Elements(unittest.TestCase):
    def test_build_is_current(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "build_apqc_elements.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_count(self):
        # The Combined sheet has 2,013 rows: a header and 2,012 elements (counted in the workbook).
        self.assertEqual(len(set(DATA.subjects(DCTERMS.isPartOf, ba.PCF))), 2012)

    def test_core_references_are_listed(self):
        _, referenced = ba.load()
        self.assertEqual(len(referenced), 251)
        for e in referenced:
            self.assertIn((URIRef(e), DCTERMS.isPartOf, ba.PCF), DATA)

    def test_pinned_elements(self):
        e = URIRef(ba.ELEMENT + "10002")
        self.assertEqual(DATA.value(e, RDFS.label), Literal("Develop Vision and Strategy", lang="en"))
        self.assertEqual(DATA.value(e, SKOS.notation), Literal("1.0", datatype=XSD.string))
        # The title matches the triple core 2.2.0 already states for a referenced element.
        self.assertEqual(DATA.value(URIRef(ba.ELEMENT + "19948"), DCTERMS.title),
                         Literal("APQC Downstream Petroleum PCF v7.2.2, element 19948", lang="en"))


if __name__ == "__main__":
    unittest.main()
