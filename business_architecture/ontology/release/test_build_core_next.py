"""Tests for the core 2.0.0 candidate (EPM-DEC-001-0038): it is core 1.0.0 plus exactly the changes
Hamid decided, the split follows his rule, the SIPOC lists arrive whole, and the package is current.

Run: python3 -m pytest test_build_core_next.py (needs rdflib, pyshacl).
"""
import os
import unittest

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDFS, SKOS

import build_core_next as b

G, COUNTS = b.build()
BASE = Graph().parse(os.path.join(b.BASE, "core.ttl"))


class Candidate(unittest.TestCase):
    def test_every_1_0_0_triple_is_kept_except_the_version_header(self):
        header = {(b.ONTOLOGY_IRI, p, o) for p, o in BASE.predicate_objects(b.ONTOLOGY_IRI)
                  if p in (OWL.versionInfo, OWL.versionIRI, b.DCTERMS.issued, OWL.priorVersion)}
        changed = {(b.CORE.responsibleDomain, SKOS.definition, o) for o in BASE.objects(b.CORE.responsibleDomain, SKOS.definition)}
        missing = set(BASE) - set(G) - header - changed
        self.assertEqual(missing, set())

    def test_commercial_and_marketing_splits_by_branch(self):
        expected = {"CM-1-1": b.DOMAIN.commercial, "CM-1-2": b.DOMAIN.commercial, "CM-1-3": b.DOMAIN.marketing}
        for s, o in BASE.subject_objects(b.CORE.responsibleDomain):
            if str(o) == "Commercial & Marketing":
                self.assertEqual(G.value(s, b.CORE.businessDomain), expected[b.branch(s)], s)

    def test_every_process_with_a_domain_gets_exactly_one_business_domain(self):
        for s in BASE.subjects(b.CORE.responsibleDomain):
            self.assertEqual(len(list(G.objects(s, b.CORE.businessDomain))), 1, s)
        self.assertEqual(sum(v for k, v in COUNTS.items() if k.startswith("business domain")),
                         len(set(BASE.subjects(b.CORE.responsibleDomain))))

    def test_the_figures(self):
        # Pinned from the 2026-10-13 build; a source change must update them deliberately.
        self.assertEqual({k: v for k, v in COUNTS.items()}, {
            "business domain commercial": 205, "business domain marketing": 251,
            "business domain finance-enabled-supply-and-trading": 13, "business domain cross-functional": 12,
            "business domain finance": 2, "business domain refining": 2,
            "processes with planned inputs and outputs": 153, "planned inputs": 362, "planned outputs": 219})
        self.assertEqual(sorted(b.DOMAINS), ["commercial", "cross-functional", "finance",
                                             "finance-enabled-supply-and-trading", "it-services", "marketing", "refining"])

    def test_planned_inputs_and_outputs_arrive_whole(self):
        for process, inputs, outputs in b.sipoc():
            self.assertEqual({str(o) for o in G.objects(process, b.CORE.plannedInput)}, set(inputs), process)
            self.assertEqual({str(o) for o in G.objects(process, b.CORE.plannedOutput)}, set(outputs), process)

    def test_responsible_domain_is_deprecated_and_ranges_are_set(self):
        self.assertIn((b.CORE.responsibleDomain, OWL.deprecated, b.Literal(True)), G)
        for p in (b.CORE.earlierProcess, b.CORE.laterProcess):
            self.assertEqual(G.value(p, RDFS.range), SKOS.Concept)

    def test_the_candidate_has_no_issued_date(self):
        self.assertIsNotNone(b.STAGE, "2.0.0 is a major; it is issued only when Hamid approves it")
        self.assertNotIn((b.ONTOLOGY_IRI, b.DCTERMS.issued, None), G)

    def test_a_domain_outside_the_list_fails_the_shapes(self):
        g = Graph()
        g += G
        s = next(g.subjects(b.CORE.businessDomain, None))
        g.set((s, b.CORE.businessDomain, URIRef("https://w3id.org/lsc/ontology/modules/core/cadence/monthly")))
        self.assertFalse(b.validate(g, shacl_graph=b.shapes(), advanced=True)[0])

    def test_the_package_is_current(self):
        files = b.package(G, b.shapes(), COUNTS)
        for name, text in files.items():
            with open(os.path.join(b.RELEASE_DIR, name)) as f:
                self.assertEqual(f.read(), text, name)


if __name__ == "__main__":
    unittest.main()
