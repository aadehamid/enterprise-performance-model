"""Check that figures stated in governed documents match epm-facts.

Each test reads a sentence or table from a document and compares it with what
`scripts/epm_facts.py` computes from the source files. A failure means the
document has drifted: update the document (or, if the source changed on
purpose, both the document and the pinned values in test_epm_facts.py).

Run: uv run --with pytest --with rdflib python -m pytest -q scripts/test_published_figures.py

Checked: every total and summary figure these documents state about Step 4
data. Deliberately not checked, because they are not data totals this tool
computes:
- step4/README.md's "16/16 sections": signed-off sections of the mapping document.
- The backlog's "All 96 Section B rows": the historic Section B population,
  explained by the index note "Section B is 96 rows plus 6".
- Subgroup breakdowns inside backlog section intros (for example "5 rows of the
  REL-00445 pattern"): they split rows whose section totals are checked here.
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


def pairs_table():
    """(G1b row, reverse row) pairs from the backlog's "G1b pairs held on both sides" table."""
    with open(epm_facts.BACKLOG) as f:
        text = f.read()
    section = text.split("## G1b pairs held on both sides", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^\|\s*(REL-\d{5})\s*\|\s*(REL-\d{5})\s*\|", section, re.M)


def test_step4_readme_ledger_and_gate(facts):
    text = flat(STEP4_README)
    m = re.search(r"both conserving to ([\d,]+) mentions", text)
    assert m and num(m.group(1)) == facts["ledger"]["mentions"]
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
        if key == "G1b rows held for a verb correction":
            g1b = {r for r, (_, s) in rows.items() if s.startswith(prefix)}
            overlap = sum(1 for left, _ in pairs_table() if left in g1b)
            m = re.search(r"\((\d+) of them also appear in the both-sides-held pairs table\)", stated)
            assert m and int(m.group(1)) == overlap, f"G1b overlap: index says {stated!r}, actual {overlap}"
    assert sorted(seen) == sorted(INDEX_SECTIONS), f"index rows {seen} must list each section exactly once"


def test_decision_0025_figures(facts):
    text = flat(DEC_0025)
    p1 = facts["phase1"]
    reverse = len(pairs_table())
    m = re.search(r"the pipeline holds (\d+) mentions.*?list (\d+) rows.*?They are the (\d+) rows in the eight issues' lists.*?"
                  r"plus the (\d+) reverse `informed-by` rows.*?(\d+) of the (\d+) are held.*?(\d+) held mentions are not Phase 1 rows",
                  text)
    assert m, "0025 summary sentences not found"
    assert tuple(int(g) for g in m.groups()) == (
        facts["ledger"]["held"], p1["rows"], p1["rows"] - reverse, reverse, p1["held"], p1["rows"], p1["held_outside"])
    m = re.search(r"Phase 1 covers all (\d+) held mentions", text)
    assert m and int(m.group(1)) == facts["ledger"]["held"]
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


def section_count(prefix):
    return sum(1 for _, (_, s) in epm_facts.phase1_rows().items() if s.startswith(prefix))


def test_backlog_section_totals():
    text = flat(epm_facts.BACKLOG)
    pairs = pairs_table()
    g1b = {r for r, (_, s) in epm_facts.phase1_rows().items() if s.startswith("G1b rows held for a verb correction")}
    checks = [
        (r"(\d+) pairs where the G1b `enables` row is held", len(pairs)),
        (r"The pairs table above lists (\d+) pairs", len(pairs)),
        (r"(\d+) of those pairs' G1b rows are in this table", sum(1 for left, _ in pairs if left in g1b)),
        (r"The (\d+) rows held in the Supply & Trading enables review", section_count("Supply & Trading")),
        (r"(\d+) `governed-by` rows, all held in the full governed-by review", section_count("Governed-by rows held in the verb reviews")),
        (r"(\d+) rows, each held in one of these review batches", section_count("Other verb-review holds")),
        (r"The following (\d+) RELs had 2026-09-25 row-level approvals", section_count("Governed-by superseded approvals")),
        (r"Triggers pass: (\d+) held rows", section_count("Triggers pass")),
        (r"(\d+) rows held — each needs an affirmative sequence citation", section_count("Precedes/follows holds")),
    ]
    for pattern, expected in checks:
        m = re.search(pattern, text)
        assert m, f"backlog sentence not found: {pattern}"
        assert int(m.group(1)) == expected, f"{pattern}: states {m.group(1)}, actual {expected}"


def test_decision_0025_every_figure(facts):
    text = flat(DEC_0025)
    led, p1 = facts["ledger"], facts["phase1"]
    reason = p1["held_outside_by_reason"]
    corrections = reason["USES_INPUT_20260926_HOLDS"] + reason["INFORMEDBY_20260926_HOLDS"] + reason["USES_INPUT_G1A_20260926_HOLDS"]
    checks = [
        (r"block the release until all (\d+) were corrected", led["held"]),
        (r"The (\d+) held mentions outside it stay held", p1["held_outside"]),
        (r"new issues for the (\d+) context-pass holds", reason["context-pass HOLD"]),
        (r"and the (\d+) `uses-input`, `informed-by` and dependent holds", corrections),
        (r"run on commit `[0-9a-f]+`: (\d+) held mentions", led["held"]),
        (r"held mentions, (\d+) emitting", led["emitting"]),
        (r"emitting, (\d+) facts", facts["canonical_facts_file"]),
    ]
    for pattern, expected in checks:
        m = re.search(pattern, text)
        assert m, f"0025 sentence not found: {pattern}"
        assert int(m.group(1)) == expected, f"{pattern}: states {m.group(1)}, actual {expected}"
