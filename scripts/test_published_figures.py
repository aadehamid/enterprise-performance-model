"""Check that figures stated in governed documents match epm-facts.

Each test reads a sentence or table from a document and compares it with what
`scripts/epm_facts.py` computes from the source files. A failure means the
document has drifted: update the document (or, if the source changed on
purpose, both the document and the pinned values in test_epm_facts.py).

Run: uv run --with pytest --with rdflib python -m pytest -q scripts/test_published_figures.py
"""
import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import epm_facts  # noqa: E402

STEP4_README = os.path.join(ROOT, "business_architecture", "ontology", "step4", "README.md")
ONTOLOGY_README = os.path.join(ROOT, "business_architecture", "ontology", "README.md")
DEC_0025 = os.path.join(ROOT, "business_architecture", "domain", "decisions", "EPM-DEC-001-0025-phase1-scope.md")


@pytest.fixture(scope="module")
def facts():
    out = subprocess.check_output([sys.executable, os.path.join(HERE, "epm_facts.py"), "--json", "counts"], text=True)
    return json.loads(out)


def flat(path):
    """The document's text with all whitespace runs collapsed, so wrapped sentences match."""
    with open(path) as f:
        return re.sub(r"\s+", " ", f.read())


def num(s):
    return int(s.replace(",", ""))


def test_step4_readme_ledger_and_gate(facts):
    text = flat(STEP4_README)
    m = re.search(r"([\d,]+) emitting / ([\d,]+) held / ([\d,]+) deferred / ([\d,]+) external governance / "
                  r"([\d,]+) structured flow = ([\d,]+); ([\d,]+) canonical facts \(`canonical-facts.csv`, ([\d,]+) rows\)", text)
    assert m, "ledger sentence not found in step4/README.md"
    led = facts["ledger"]
    assert tuple(num(g) for g in m.groups()) == (
        led["emitting"], led["held"], led["deferred"], led["external_governance"], led["structured_flow"],
        facts["conservation"], facts["canonical_facts_file"], facts["canonical_facts_file"])
    m = re.search(r"promoted ([\d,]+) / held ([\d,]+), plus the same ([\d,]+) / ([\d,]+) / ([\d,]+) = ([\d,]+); "
                  r"([\d,]+) PASS / ([\d,]+) FAIL", text)
    assert m, "gate sentence not found in step4/README.md"
    gate = facts["evidence_gate"]
    total = gate["promoted"] + gate["held"] + led["deferred"] + led["external_governance"] + led["structured_flow"]
    assert tuple(num(g) for g in m.groups()) == (
        gate["promoted"], gate["held"], led["deferred"], led["external_governance"], led["structured_flow"],
        total, gate["pass_checks"], gate["fail_checks"])
    assert total == led["mentions"]


def test_ontology_readme_taxonomy(facts):
    tax = facts["taxonomy"]
    if "triples" not in tax:
        pytest.skip("rdflib not installed")
    m = re.search(r"([\d,]+) triples, ([\d,]+) `skos:Concept`, ([\d,]+) `skos:broader` links, "
                  r"([\d,]+) concepts with `skos:definition`", flat(ONTOLOGY_README))
    assert m, "taxonomy sentence not found in ontology/README.md"
    assert tuple(num(g) for g in m.groups()) == (
        tax["triples"], tax["concepts"], tax["broader_links"], tax["concepts_with_definition"])


# Backlog index row label -> (issue, heading prefix of the section it counts).
INDEX_SECTIONS = {
    "G3 Section B": ("#201", "G3 Section B"),
    "G1b rows held for a verb correction": ("#202", "G1b rows held for a verb correction"),
    "Supply & Trading": ("#203", "Supply & Trading recommend/advise rows"),
    "Triggers": ("#204", "Triggers pass"),
    "Precedes/follows": ("#205", "Precedes/follows holds"),
    "Governed-by": ("#206", None),
    "G3 Section A": ("#209", "G3 Section A"),
    "Other verb-review holds": ("#210", "Other verb-review holds"),
}


def test_backlog_index_matches_sections():
    rows = epm_facts.phase1_rows()
    by_section = {}
    for _, (issue, section) in rows.items():
        by_section[section] = by_section.get(section, 0) + 1
    with open(epm_facts.BACKLOG) as f:
        text = f.read()
    seen = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or not cells[1].startswith("#"):
            continue
        label, issue, stated = cells
        key = next((k for k in INDEX_SECTIONS if label.startswith(k)), None)
        assert key, f"unknown backlog index row: {label!r}"
        seen.append(key)
        assert issue == INDEX_SECTIONS[key][0], f"{label}: index says {issue}, expected {INDEX_SECTIONS[key][0]}"
        if key == "Governed-by":
            m = re.match(r"(\d+) superseded approvals, (\d+) pass-backlog rows, (\d+) rows from the verb reviews", stated)
            assert m, f"governed-by index row unreadable: {stated!r}"
            expected = [sum(n for s, n in by_section.items() if s.startswith(p)) for p in (
                "Governed-by superseded approvals", "Governed-by pass backlog", "Governed-by rows held in the verb reviews")]
            assert [int(g) for g in m.groups()] == expected
            continue
        prefix = INDEX_SECTIONS[key][1]
        actual = sum(n for s, n in by_section.items() if s.startswith(prefix))
        assert int(re.match(r"\d+", stated).group()) == actual, f"{label}: index says {stated}, section has {actual}"
    assert sorted(seen) == sorted(INDEX_SECTIONS), f"index rows {seen} must list each section exactly once"


def test_decision_0025_figures(facts):
    text = flat(DEC_0025)
    p1 = facts["phase1"]
    m = re.search(r"list (\d+) rows.*?(\d+) of the (\d+) are held.*?(\d+) held mentions are not Phase 1 rows", text)
    assert m, "0025 summary sentence not found"
    assert tuple(int(g) for g in m.groups()) == (p1["rows"], p1["held"], p1["rows"], p1["held_outside"])
    table = dict(re.findall(r"\| ([^|]+?) \| (\d+) \|", text))
    reason = p1["held_outside_by_reason"]
    pairs = {
        "Context-pass holds": "context-pass HOLD",
        "`uses-input` pass holds": "USES_INPUT_20260926_HOLDS",
        "`informed-by` pass holds": "INFORMEDBY_20260926_HOLDS",
        "`enables` mentions held with their removed `uses-input` supporter": "USES_INPUT_G1A_20260926_HOLDS",
        "`governed-by` pass holds": "GOVERNEDBY_20260926_HOLDS",
        "Property-rule hold": "PROPERTY_RULE_HOLDS",
    }
    for label, key in pairs.items():
        row = next(int(v) for k, v in table.items() if k.startswith(label))
        assert row == reason[key], f"0025 table {label!r}: {row} vs {reason[key]}"
