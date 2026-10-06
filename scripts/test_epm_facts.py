"""Pin the figures epm-facts reports, so a change that moves one fails here first.

Run: uv run --with pytest python -m pytest -q scripts/test_epm_facts.py

When a figure changes on purpose (a Phase 1 batch merges, a release lands),
update the pinned value in the same pull request and say why in its body.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epm_facts  # noqa: E402


def run(*args):
    out = subprocess.check_output([sys.executable, os.path.join(HERE, "epm_facts.py"), "--json", *args], text=True)
    return json.loads(out)


def test_ledger_conserves_and_matches_governed_figures():
    c = run("counts")
    led = c["ledger"]
    assert (led["emitting"], led["held"], led["deferred"], led["external_governance"], led["structured_flow"]) == (617, 686, 12, 1, 2)
    assert c["conservation"] == led["mentions"] == 1318
    assert c["canonical_facts_file"] == led["canonical_facts_pipeline"] == 457
    assert c["evidence_gate"]["green"] is True
    assert (c["evidence_gate"]["promoted"], c["evidence_gate"]["held"]) == (1066, 237)


def test_phase1_scope_matches_decision_0025():
    p = run("counts")["phase1"]
    assert p["rows"] == 276 and p["held"] == 275
    assert p["not_held"] == ["REL-00190"]
    assert p["by_issue"] == {"201": 102, "202": 44, "203": 15, "204": 11, "205": 20, "206": 15, "209": 47, "210": 22}
    assert p["held_outside"] == 411


def test_citations_are_not_rows():
    rows = epm_facts.phase1_rows()
    assert "REL-00214" not in rows  # cited inside the REL-00152 rationale
    assert "REL-00366" not in rows  # cited as a Definitions precedent
    assert "REL-00215" in rows and rows["REL-00215"][0] == 206  # a listed governed-by row


def test_home_section_beats_pairs_table():
    rows = epm_facts.phase1_rows()
    assert rows["REL-00469"][0] == 203
    assert rows["REL-00489"][0] == 201
    assert rows["REL-01130"][0] == 202  # a reverse informed-by row, only in the pairs table


def test_review_holds_read_only_the_decision_column():
    per_file, _ = epm_facts.review_holds()
    # 22 rows in this file say "RECONCILED — already held" in review_section with a blank decision.
    assert per_file["enables-g3-genuine-enablement-review-batch.csv"] == 107
    assert per_file["enables-g3-section-b5-class-verdict.csv"] == 42


def test_row_reports_held_provenance():
    r = run("row", "REL-00436")
    assert r["status"] == "held"
    assert r["stored_facts"] == ["CM-1-2-5-2-3 core:dependsOnOutputOf CM-1-2-5-1-4"]
    assert r["phase1_issue"] == 203


def test_find_catches_text_split_across_lines():
    hits = run("find", "EPM-DEC-001-0024, decided")["hits"]
    assert any(h["kind"] == "split" for h in hits)


def _backlog():
    with open(epm_facts.BACKLOG) as f:
        return f.read()


def test_parser_ignores_table_padding():
    text = _backlog()
    squeezed = "\n".join(
        "|" + "|".join(c.strip() for c in line.strip().strip("|").split("|")) + "|"
        if line.strip().startswith("|") else line
        for line in text.split("\n")
    )
    assert epm_facts.phase1_rows(squeezed) == epm_facts.phase1_rows(text)


def test_parser_ignores_indentation_and_bullet_style():
    text = _backlog()
    reformatted = "\n".join(
        ("    " + line) if line.startswith("REL-") else line.replace("- REL", "* REL", 1)
        for line in text.split("\n")
    )
    assert epm_facts.phase1_rows(reformatted) == epm_facts.phase1_rows(text)


def test_sentences_starting_with_an_id_are_not_rows():
    text = _backlog() + "\n\nREL-00366 is a precedent, not a row requiring source correction.\n- REL-00214 explains why REL-00152 is held (citation).\n"
    rows = epm_facts.phase1_rows(text)
    assert "REL-00366" not in rows and "REL-00214" not in rows
    assert rows == epm_facts.phase1_rows()


def test_wrapped_lists_keep_every_row():
    text = _backlog()
    wrapped = text.replace("REL-01223, REL-01227, REL-01241, REL-01289, REL-01291, REL-01294.",
                           "REL-01223, REL-01227, REL-01241, REL-01289, REL-01291 and\nREL-01294.")
    assert wrapped != text
    assert epm_facts.phase1_rows(wrapped) == epm_facts.phase1_rows(text)


def test_gate_figures_survive_a_failing_gate(tmp_path):
    fake = tmp_path / "evidence-gate.py"
    fake.write_text("import sys\npromoted = 1066\nheld_ctx = 237\nprint('GATE FAILED: 1 check(s)')\nsys.exit(1)\n")
    ns, ok, out = epm_facts.run_keeping_globals(str(fake))
    assert ok is False and "GATE FAILED" in out
    assert (ns["promoted"], ns["held_ctx"]) == (1066, 237)


def _decisions_copy(tmp_path):
    import shutil
    folder = tmp_path / "decisions"
    shutil.copytree(epm_facts.DECISIONS, folder)
    return folder


def test_decision_records_are_consistent_today():
    assert epm_facts.decision_problems() == []


def test_decisions_check_catches_status_mismatch(tmp_path):
    folder = _decisions_copy(tmp_path)
    rec = next(folder.glob("EPM-DEC-001-0024-*.md"))
    rec.write_text(rec.read_text().replace("| Status | Decided |", "| Status | Proposed |", 1))
    assert any(p.startswith("0024: index status") for p in epm_facts.decision_problems(str(folder)))


def test_decisions_check_requires_a_quote_for_decided(tmp_path):
    folder = _decisions_copy(tmp_path)
    rec = next(folder.glob("EPM-DEC-001-0009-*.md"))
    text = rec.read_text()
    start = text.index("## Hamid's recorded words")
    end = text.index("## Evidence")
    rec.write_text(text[:start] + "## Hamid's recorded words\n\nAgreed in the session.\n\n" + text[end:])
    assert any(p.startswith("0009: Decided, but no quote") for p in epm_facts.decision_problems(str(folder)))


def test_decisions_check_catches_unindexed_record_and_bad_amendment(tmp_path):
    folder = _decisions_copy(tmp_path)
    (folder / "EPM-DEC-001-0099-new.md").write_text("# EPM-DEC-001-0099: new\n\n| Status | Decided; amended by EPM-DEC-001-0098 |\n")
    problems = epm_facts.decision_problems(str(folder))
    assert "0099: record not listed in the index" in problems
    assert "0099: amended by 0098, which does not exist" in problems


def test_status_parts_reads_every_amendment():
    assert epm_facts._status_parts("Decided; amended by 0024, 0098") == ("Decided", {"0024", "0098"})
    assert epm_facts._status_parts("Decided; amended by EPM-DEC-001-0024 and EPM-DEC-001-0025 (2026-10-06)") == ("Decided", {"0024", "0025"})


def test_decisions_check_catches_a_second_amendment_target(tmp_path):
    folder = _decisions_copy(tmp_path)
    rec = next(folder.glob("EPM-DEC-001-0013-*.md"))
    rec.write_text(rec.read_text().replace("amended by EPM-DEC-001-0025", "amended by EPM-DEC-001-0025, EPM-DEC-001-0098", 1))
    problems = epm_facts.decision_problems(str(folder))
    assert "0013: amended by 0098, which does not exist" in problems
    assert any(p.startswith("0013: index status") for p in problems)
