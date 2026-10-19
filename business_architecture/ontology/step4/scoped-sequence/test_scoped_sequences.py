"""Tests for build.py: the real table passes, and each broken input is caught.

Run: uv run --with pytest --with rdflib --with pyshacl python -m pytest -q test_scoped_sequences.py
"""
import copy
import os
import sys

import pytest
import rdflib
from rdflib.namespace import RDF, SH, SKOS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

CORE = rdflib.Namespace(build.CORE)
PROC = rdflib.Namespace(build.PROC)


@pytest.fixture(scope="module")
def table():
    return build.load()


@pytest.fixture(scope="module")
def built():
    return build.graph()


def rows_with(table, target, **changes):
    rows = copy.deepcopy(table[1])
    for r in rows:
        if r["row_id"] == target:
            r.update(changes)
    return rows


def test_real_table_passes(table):
    assert build.check(*table) == []
    c = build.counts(table[1])
    assert (c["nodes"], c["handoffs"]) == (17, 16)


def test_ttl_is_current_and_conforms(built):
    g, tax = built
    with open(build.OUTPUT) as f:
        assert f.read() == build.turtle(g)
    conforms, _, report = build.shacl(g, tax)
    assert conforms, report


def test_three_no_sequence_rows_are_absent(table):
    ids = {r["row_id"] for r in table[1]}
    assert not ids & {"REL-01227", "REL-00184", "REL-00149"}


@pytest.mark.parametrize("row_id, changes, expected", [
    ("REL-00319", {"earlier": "CM-1-2-4-1-11", "later": "CM-1-2-1-3-7",
                   "node_slug": "CM-1-2-4-1-11--CM-1-2-1-3-7--transaction"}, "earlier/later must be"),
    ("REL-00193", {"definition": "Capture Physical Trades precedes confirmation."}, "differs from the review CSV"),
    ("REL-00188", {"condition": "Where any power transaction exists"}, "condition is not words of the definition"),
    ("REL-00193", {"scope_unit": "trade", "node_slug": "CM-1-2-1-3-3--CM-1-2-2-2--trade"}, "not in the scope-unit list"),
    ("REL-00193", {"evidence_basis": "verified"}, "not in the evidence-basis list"),
    ("REL-00193", {"node_slug": "capture-to-confirmation"}, "node_slug must be"),
    ("REL-00193", {"answer": "https://example.org/not-saved"}, "not a saved answer"),
    ("REL-00193", {"source_verb": "follows"}, "but the review says precedes"),
    ("REL-00112", {"links_to_ancestor": "no"}, "the taxonomy says yes"),
    ("REL-00193", {"links_to_ancestor": "yes"}, "the taxonomy says no"),
    ("REL-00008", {"refines": "CM-1-1-3-7-9--CM-1-1-3-6--replenishment-requirement"}, "different later process or scope"),
    ("REL-00008", {"refines": "nowhere"}, "which is not a node"),
    ("REL-01223", {"refines": "CM-1-1-1-1-4--CM-1-1-2--forecast-version"}, "not an ancestor of its own"),
    ("REL-00193", {"earlier": "CM-9-9", "node_slug": "CM-9-9--CM-1-2-2-2--transaction"}, "not a concept in the pinned taxonomy"),
    # Valid values that differ from what was approved for the row.
    ("REL-00008", {"evidence_basis": "source-confirmed"}, "but Q13 gives reference-model-assumption"),
    ("REL-00188", {"evidence_basis": "source-confirmed"}, "but Q13 gives reference-model-assumption"),
    ("REL-00193", {"evidence_basis": "reference-model-assumption"}, "but Q13 gives source-confirmed"),
    ("REL-00193", {"answer": "urn:epm:issue:226:comment:6123946413"},
     "answer must be the batch's saved answer"),
    ("REL-00193", {"scope_unit": "forecast-version", "node_slug": "CM-1-2-1-3-3--CM-1-2-2-2--forecast-version"},
     "but Q9 approved transaction"),
    ("REL-01289", {"condition": ""}, "Q10 lists this row as conditional"),
    ("REL-00193", {"condition": "Capture Physical Trades"}, "Q10 does not list this row as conditional"),
    ("REL-00112", {"links_to_ancestor": "no"}, "shapes.ttl ApprovedAncestorLink lists"),
])
def test_broken_rows_are_caught(table, row_id, changes, expected):
    problems = build.check(table[0], rows_with(table, row_id, **changes))
    assert any(expected in p for p in problems), problems


def test_refinement_must_match_q12(table):
    rows = rows_with(table, "REL-00008", refines="")
    assert any("differ from Q12" in p for p in build.check(table[0], rows))


def test_ancestor_flag_needs_q6_approval(table, monkeypatch):
    real = build.approvals()
    monkeypatch.setattr(build, "approvals", lambda: {**real, "ancestor": set()})
    assert any("Q6 approves an ancestor link only" in p for p in build.check(*table))


def test_repeated_node_and_unknown_row_are_caught(table):
    rows = copy.deepcopy(table[1])
    rows.append(dict(rows[0]))
    assert any("node_slug repeated" in p for p in build.check(table[0], rows))
    rows = rows_with(table, "REL-00193", row_id="REL-99999")
    assert any("not in a precedes/follows review CSV" in p for p in build.check(table[0], rows))


def test_wrong_columns_and_empty_table_are_caught(table):
    assert build.check(table[0][:-1], table[1])
    assert build.check(table[0], []) == ["scoped-sequences.csv has no rows"]


def test_taxonomy_parents_match_rdflib(built):
    _, tax = built
    parents = build.taxonomy_parents()
    expected = {str(s).rsplit("/", 1)[1]: None for s in tax.subjects(RDF.type, SKOS.Concept)}
    for s, o in tax.subject_objects(SKOS.broader):
        expected[str(s).rsplit("/", 1)[1]] = str(o).rsplit("/", 1)[1]
    assert parents == expected


def test_code_lists_match_rdflib():
    vocab = rdflib.Graph().parse(build.VOCABULARY, format="turtle")
    for scheme in ("ScopeUnits", "EvidenceBases"):
        expected = {str(s).rsplit("/", 1)[1] for s in vocab.subjects(SKOS.inScheme, CORE[scheme])}
        assert build.code_list(scheme) == expected


def shacl_after(built, change):
    g, tax = built
    g = copy.deepcopy(g)
    change(g)
    conforms, _, report = build.shacl(g, tax)
    return conforms, report


def severities(built, change):
    g, tax = built
    g = copy.deepcopy(g)
    change(g)
    _, results, _ = build.shacl(g, tax)
    return set(results.objects(None, SH.resultSeverity))


def first_node(g):
    return next(g.subjects(RDF.type, CORE.ScopedSequence))


def test_shacl_catches_missing_evidence_basis(built):
    conforms, report = shacl_after(built, lambda g: g.remove((first_node(g), CORE.evidenceBasis, None)))
    assert not conforms and "evidenceBasis" in report


def test_shacl_catches_same_earlier_and_later(built):
    def change(g):
        n = first_node(g)
        g.set((n, CORE.laterProcess, g.value(n, CORE.earlierProcess)))
    assert not shacl_after(built, change)[0]


def test_shacl_catches_endpoint_that_is_not_a_process(built):
    conforms, _ = shacl_after(built, lambda g: g.set((first_node(g), CORE.earlierProcess, PROC["CM-9-9"])))
    assert not conforms


def test_shacl_warns_on_undeclared_ancestor_link(built):
    def change(g):
        n = next(s for s in g.subjects(RDF.type, CORE.ScopedSequence) if (s, CORE.linksToAncestor, None) in g)
        g.remove((n, CORE.linksToAncestor, None))
    assert severities(built, change) == {SH.Warning}


def test_shacl_rejects_an_unapproved_node_declaring_an_ancestor_link(built):
    def change(g):
        n = rdflib.URIRef(build.SEQ + "CM-1-2-1-3-3--CM-1-2-2-2--transaction")
        g.set((n, CORE.earlierProcess, PROC["CM-1-2-1-3-3"]))
        g.set((n, CORE.laterProcess, PROC["CM-1-2-1-3"]))  # its parent
        g.set((n, CORE.linksToAncestor, rdflib.Literal(True)))
    assert SH.Violation in severities(built, change)


def test_shacl_catches_scope_outside_the_list(built):
    conforms, _ = shacl_after(built, lambda g: g.set((first_node(g), CORE.sequenceScope, CORE["scope-unit/trade"])))
    assert not conforms
