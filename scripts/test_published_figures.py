"""Check that figures stated in governed documents match epm-facts.

Each test reads a sentence or table from a document and compares it with what
`scripts/epm_facts.py` computes from the source files. A failure means the
document has drifted: update the document (or, if the source changed on
purpose, both the document and the pinned values in test_epm_facts.py).

Run: uv run --with pytest --with rdflib python -m pytest -q scripts/test_published_figures.py

Checked: every total and summary figure these documents state about Step 4
data, and that step4/README.md states no live ledger or gate figures at all. Deliberately not checked, because they are not data totals this tool
computes:
- step4/README.md's "16/16 sections": signed-off sections of the mapping document.
- The backlog's "All 96 Section B rows": the historic Section B population,
  explained by the index note "Section B is 96 rows plus 6".
- Subgroup breakdowns inside backlog section intros (for example "5 rows of the
  REL-00445 pattern"): they split rows whose section totals are checked here.
"""
import csv
import json
import os
import re
import shutil
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


@pytest.fixture(scope="module")
def facts_0025(tmp_path_factory):
    """Counts on the commit EPM-DEC-001-0025 cites, not today's.

    A decision record states its figures as of the commit it names ("run on
    commit `1179405`"), so its figures are history and stay as recorded while
    later batches move the live counts. Today's epm_facts.py runs on that
    commit's tree, so the counting logic is the same one checked everywhere else.
    """
    sha = re.search(r"run on commit `([0-9a-f]+)`", flat(DEC_0025)).group(1)
    tree = tmp_path_factory.mktemp("dec0025")
    archive = subprocess.run(["git", "-C", ROOT, "archive", sha], capture_output=True)
    assert archive.returncode == 0, (
        f"commit {sha} is not in this clone; a shallow clone needs `git fetch --unshallow` "
        f"(CI checks out full history): {archive.stderr.decode().strip()}")
    archive = archive.stdout
    subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, check=True)
    os.makedirs(tree / "scripts", exist_ok=True)
    shutil.copy(os.path.join(HERE, "epm_facts.py"), tree / "scripts" / "epm_facts.py")
    out = subprocess.check_output([sys.executable, str(tree / "scripts" / "epm_facts.py"), "--json", "counts"],
                                  text=True, stderr=subprocess.DEVNULL)
    result = json.loads(out)
    result["backlog"] = str(tree / os.path.relpath(epm_facts.BACKLOG, ROOT))
    return result


def flat(path):
    """The document's text with all whitespace runs collapsed, so wrapped sentences match."""
    with open(path) as f:
        return re.sub(r"\s+", " ", f.read())


def num(s):
    return int(s.replace(",", ""))


def pairs_table(backlog=None):
    """(G1b row, reverse row) pairs from the backlog's "G1b pairs held on both sides" table."""
    with open(backlog or epm_facts.BACKLOG) as f:
        text = f.read()
    section = text.split("## G1b pairs held on both sides", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^\|\s*(REL-\d{5})\s*\|\s*(REL-\d{5})\s*\|", section, re.M)


# Numbers step4/README.md may state because they are not live figures. Anything
# else numeric is a figure, however it is worded or emphasised.
README_NON_FIGURES = [
    # Fixed figures, each matched only in its own sentence; removed before the file-name rule splits them.
    r"conserving to all 1,318 mentions: the ledger",
    r"All 10 boxes in release-checklist\.md are complete",
    r"document, 16/16 sections\)",
    r"\d{4}-\d{2}-\d{2}",                           # dates
    r"#\d+\b",                                       # PR and issue numbers
    r"\b\d+\.\d+\.\d+\b",                           # release versions
    r"\b(?:REL-\d{5}|EPM-[A-Z]+-\d{3}(?:-\d{4})?|CM(?:-\d+)+|MPC-S\d+)\b",  # the project's ID namespaces
    r"[\w./-]+\.(?:md|py|csv|ttl|json|jsonl|sh|txt|html)\b",  # file names
    r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b",          # commit SHAs
    r"\bstep\d\b|\bStep \d+\b|\bQ\d+\b|\bpython3\b",   # step names, decision numbers, the command
]


def readme_figures(text):
    """Numbers left in the text once markup and the allowed non-figures are removed."""
    text = re.sub(r"[*_`]", "", text)
    for pattern in README_NON_FIGURES:
        text = re.sub(pattern, " ", text)
    return re.findall(r"\d[\d,]*", text)


def test_step4_readme_states_no_live_figures():
    # Live figures live in epm_facts.py counts only, so no batch edits figure prose
    # (retro on #235: restated figures were the most frequent review finding).
    text = flat(STEP4_README)
    assert "python3 scripts/epm_facts.py counts" in text
    assert readme_figures(text) == [], "step4/README.md states a figure; point to epm_facts.py counts instead"


@pytest.mark.parametrize("line", [
    "Current ledger: 999 emitting, 999 held.",
    "Canonical facts: 999.",
    "Evidence gate: promoted 999 / held 999.",
    "Evidence gate: **999 PASS** / **999 FAIL**.",
    "Ledger: **999 emitting** / **999 held**.",
    "`999` facts",
    "Current gate: 999-PASS / 9-FAIL.",
    "The canonical store is a 999-fact store.",
    "Live ledger: emitting/999 held/888.",
    "Current ledger: 1,318 mentions held.",
    "The current emitting population is a 628-row subset of the ledger.",
    "The evidence gate has a 237-row held population.",
    "All 10 boxes are 999 facts.",
    "Current gate: PASS-999 / FAIL-9.",
    "Current ledger: EMITTING-999 / HELD-888.",
    "Current canonical facts: FACTS-999.",
    "Current gate: **PASS-999** / **FAIL-9**.",
])
def test_readme_guard_catches_restated_figures(line):
    assert readme_figures(flat(STEP4_README) + " " + line)


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


def test_decision_0025_figures(facts_0025):
    facts = facts_0025
    text = flat(DEC_0025)
    p1 = facts["phase1"]
    reverse = len(pairs_table(facts["backlog"]))
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


def batch_rows(n):
    """Rows in the #205 batch n review file."""
    path = os.path.join(epm_facts.REVIEWS, f"precedes-follows-batch{n}-review.csv")
    with open(path, newline="") as f:
        return sum(1 for r in csv.DictReader(f) if r["row_id"].startswith("REL-"))


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
        (r"(\d+) rows were held\. Each needed an affirmative sequence citation", section_count("Precedes/follows holds")),
        (r"Batch 1 \((\d+) rows\) and batch 2", batch_rows(1)),
        (r"batch 2 \((\d+) rows\) have fresh verdicts", batch_rows(2)),
        (r"holds 96 \+ 6 = (\d+) rows", section_count("G3 Section B")),
    ]
    for pattern, expected in checks:
        m = re.search(pattern, text)
        assert m, f"backlog sentence not found: {pattern}"
        assert int(m.group(1)) == expected, f"{pattern}: states {m.group(1)}, actual {expected}"


def test_decision_0025_every_figure(facts_0025):
    facts = facts_0025
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
    m = re.search(r"Roughly ([\d.]+) times the Phase 1 work", text)
    assert m, "0025 workload multiplier not found"
    assert float(m.group(1)) == round(led["held"] / p1["rows"], 1), f"multiplier {m.group(1)} vs {led['held']}/{p1['rows']}"
