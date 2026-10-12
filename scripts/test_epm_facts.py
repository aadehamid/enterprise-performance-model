"""Pin the figures epm-facts reports, so a change that moves one fails here first.

Run: uv run --with pytest python -m pytest -q scripts/test_epm_facts.py

When a figure changes on purpose (a Phase 1 batch merges, a release lands),
update the pinned value in the same pull request and say why in its body.
"""
import csv
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
    assert (led["emitting"], led["held"], led["deferred"], led["external_governance"], led["structured_flow"],
            led["scoped_sequence"]) == (617, 669, 12, 1, 2, 17)
    ss = c["scoped_sequences"]
    assert (ss["nodes"], ss["handoffs"], ss["problems"]) == (17, 16, [])
    assert c["conservation"] == led["mentions"] == 1318
    assert c["canonical_facts_file"] == led["canonical_facts_pipeline"] == 457
    assert c["evidence_gate"]["green"] is True
    assert (c["evidence_gate"]["promoted"], c["evidence_gate"]["held"]) == (1066, 237)


def test_phase1_scope_matches_decision_0025():
    p = run("counts")["phase1"]
    assert p["rows"] == 276 and p["held"] == 258
    # REL-00190 emits a core fact; the 17 #205 scoped rows emit scoped-sequence nodes (EPM-DEC-001-0026).
    assert p["not_held"] == sorted(["REL-00190"] + epm_facts.scoped_sequences()["rows"])
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
    # A date in parentheses neither ends the list nor counts as a record number.
    assert epm_facts._status_parts(
        "Decided; amended by EPM-DEC-001-0025 (2026-10-06) and EPM-DEC-001-0026 (2026-10-12)") == ("Decided", {"0025", "0026"})


def test_decisions_check_catches_a_second_amendment_target(tmp_path):
    folder = _decisions_copy(tmp_path)
    rec = next(folder.glob("EPM-DEC-001-0013-*.md"))
    rec.write_text(rec.read_text().replace("amended by EPM-DEC-001-0025", "amended by EPM-DEC-001-0025, EPM-DEC-001-0098", 1))
    problems = epm_facts.decision_problems(str(folder))
    assert "0013: amended by 0098, which does not exist" in problems
    assert any(p.startswith("0013: index status") for p in problems)


# ---------- quotes ----------

def _quote_fixture(tmp_path, reason="", hamid_words=None, block=None):
    """A copy of the batch 1 review file and the backlog, with one field changed."""
    reviews = tmp_path / "reviews"
    reviews.mkdir(parents=True)
    src = os.path.join(epm_facts.REVIEWS, "precedes-follows-batch1-review.csv")
    with open(src, newline="") as f:
        rows = list(csv.DictReader(f))
    if reason:
        rows[7]["semantic_reason"] = reason
    if hamid_words:
        rows[0]["hamid_words"] = hamid_words
    with open(reviews / "batch.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    backlog = tmp_path / "backlog.md"
    with open(epm_facts.BACKLOG) as f:
        text = f.read()
    if block:
        text += f"\n\n> {block}\n"
    backlog.write_text(text)
    return epm_facts.quote_problems(str(reviews), str(backlog), epm_facts.ANSWERS)


def test_quotes_pass_on_the_repo():
    assert epm_facts.quote_problems() == []


def test_quotes_catch_a_period_moved_inside_a_shortened_quote(tmp_path):
    # The #225 defect: Hamid's sentence continues after "activity".
    bad = 'it "does not require completion of all trade-capture activity." more'
    good = 'it "does not require completion of all trade-capture activity". more'
    assert any("semantic_reason" in p for p in _quote_fixture(tmp_path / "bad", reason=bad))
    assert _quote_fixture(tmp_path / "good", reason=good) == []


def test_quotes_catch_altered_answer_text_and_block_quotes(tmp_path):
    assert any("hamid_words" in p for p in _quote_fixture(tmp_path / "a", hamid_words="a, with my own wording."))
    assert any("block quote" in p for p in _quote_fixture(tmp_path / "b", block="Go ahead with the Batch 1 PR."))


def test_quotes_split_an_ellipsis_and_skip_short_terms(tmp_path):
    ok = 'He said "adopted reference-model positions … not verified MPC internal procedures" and "owned by".'
    assert _quote_fixture(tmp_path, reason=ok) == []


def test_quotes_catch_an_inserted_comma(tmp_path):
    bad = 'it "does not require completion of all trade-capture activity," more'
    assert any("semantic_reason" in p for p in _quote_fixture(tmp_path, reason=bad))


def test_quotes_read_indented_and_lazy_block_quotes(tmp_path):
    assert any("block quote" in p for p in _quote_fixture(
        tmp_path / "a", block="x\n\n  > Hamid approved all held relationships for immediate emission."))
    assert any("block quote" in p for p in _quote_fixture(
        tmp_path / "b", block="Take this as my authorization\nand emit all held rows now."))


def test_quotes_report_when_nothing_was_checked(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    backlog = tmp_path / "backlog.md"
    backlog.write_text("no quotes\n")
    problems = epm_facts.quote_problems(str(empty), str(backlog), str(empty))
    assert any("no saved answer text" in p for p in problems)
    assert any("no review file" in p for p in problems)


def test_quotes_follow_commonmark_block_structure(tmp_path):
    nested = "- Decision record\n\n    > Hamid approved all held relationships for immediate emission."
    assert any("block quote" in p for p in _quote_fixture(tmp_path / "a", block="x\n\n" + nested))
    heading = "Take this as my authorization\n## Unquoted heading"
    assert _quote_fixture(tmp_path / "b", block=heading) == []
    blank = "Take this as my authorization\n>\nUnquoted paragraph"
    assert _quote_fixture(tmp_path / "c", block=blank) == []


def test_quotes_reject_empty_answers_and_blank_rows(tmp_path):
    answers = tmp_path / "answers"
    answers.mkdir()
    (answers / "empty.md").write_text("<!-- source header only -->\n")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "batch.csv").write_text("row_id,hamid_words,scope_note_sentence,semantic_reason,Hamid_decision\nREL-00193,,,,\n")
    backlog = tmp_path / "backlog.md"
    backlog.write_text("")
    problems = epm_facts.quote_problems(str(reviews), str(backlog), str(answers))
    assert any("no saved answer text" in p for p in problems)
    assert any("hamid_words is blank" in p for p in problems)


def test_quotes_check_code_and_html_inside_block_quotes(tmp_path):
    fake = "Hamid approved all held relationships for immediate emission."
    for i, block in enumerate([f"```text\n> {fake}\n> ```", f"    {fake}", f"<p>{fake}</p>"]):
        assert any("block quote" in p for p in _quote_fixture(tmp_path / str(i), block=block)), block


def test_quotes_reject_a_repeated_column(tmp_path):
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "batch.csv").write_text(
        "row_id,hamid_words,hamid_words\nREL-00193,Hamid authorized immediate emission of every held row.,Take this as my authorization\n")
    backlog = tmp_path / "backlog.md"
    backlog.write_text("")
    problems = epm_facts.quote_problems(str(reviews), str(backlog), epm_facts.ANSWERS)
    assert any("repeated column" in p for p in problems)


def test_quotes_reject_a_header_only_review_file(tmp_path):
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "batch.csv").write_text("row_id,hamid_words\n")
    backlog = tmp_path / "backlog.md"
    backlog.write_text("")
    assert any("no rows" in p for p in epm_facts.quote_problems(str(reviews), str(backlog), epm_facts.ANSWERS))


def _decision_fixture(tmp_path, number, words, status="Decided"):
    """A decisions folder holding one record with the given 'Hamid's recorded words' section."""
    folder = tmp_path / "decisions"
    folder.mkdir(parents=True)
    (folder / f"EPM-DEC-001-{number:04d}-test.md").write_text(
        f"# EPM-DEC-001-{number:04d}: test\n\n| Field | Value |\n|---|---|\n| Status | {status} |\n\n"
        f"## Decision\n\nThe definition \"The source completes before the target begins\" stays.\n\n"
        f"## Hamid's recorded words\n\n{words}\n\n## Evidence\n\nNone.\n")
    reviews = os.path.dirname(epm_facts.REVIEWS + "/")
    return epm_facts.quote_problems(reviews, epm_facts.BACKLOG, epm_facts.ANSWERS, str(folder))


def test_quotes_catch_unsaved_words_in_a_decision_record(tmp_path):
    # The PR #231 defect: chat answers quoted in EPM-DEC-001-0026, never saved.
    problems = _decision_fixture(tmp_path, 26, 'Hamid answered "yes to all seven" in the session.')
    assert any("EPM-DEC-001-0026" in p and "yes to all seven" in p for p in problems)


def test_quotes_accept_saved_words_in_a_decision_record(tmp_path):
    words = 'He approved on #226: "Approved: Q1–Q18 as recommended in the comment above"'
    assert _decision_fixture(tmp_path, 26, words) == []


def test_quotes_check_only_the_recorded_words_section(tmp_path):
    # The Decision section quotes the predicate's definition, which is not Hamid's answer.
    assert _decision_fixture(tmp_path, 27, 'He said "Approved: Q1–Q18 as recommended in the comment above"') == []


def test_quotes_skip_records_before_0026(tmp_path):
    # Records 0001-0025 quote sessions that were never saved as answers.
    assert _decision_fixture(tmp_path, 25, 'Q12: "I agree with this."') == []


def test_quotes_require_a_checked_quote_in_a_decided_record(tmp_path):
    problems = _decision_fixture(tmp_path, 26, "Hamid agreed in the session.")
    assert any("EPM-DEC-001-0026" in p and "no quote" in p for p in problems)
    assert _decision_fixture(tmp_path / "p", 26, "Not yet decided.", status="Proposed") == []


def test_recorded_words_section_follows_markdown_headings(tmp_path):
    # A "## " line inside a code fence is not a heading: the quote after the fence is still checked.
    words = ('"Approved: Q1–Q18 as recommended in the comment above"\n\n```text\n## Example\n```\n\n'
             'Hamid also said "yes to all seven"')
    assert any("yes to all seven" in p for p in _decision_fixture(tmp_path / "a", 26, words))
    # A heading written with a tab ends the section, so the next section's quote does not count.
    folder = tmp_path / "b" / "decisions"
    folder.mkdir(parents=True)
    (folder / "EPM-DEC-001-0026-test.md").write_text(
        "# t\n\n| Status | Decided |\n\n## Hamid's recorded words\n\nHamid agreed.\n\n##\tEvidence\n\n"
        '"Approved: Q1–Q18 as recommended in the comment above"\n')
    problems = epm_facts.quote_problems(epm_facts.REVIEWS, epm_facts.BACKLOG, epm_facts.ANSWERS, str(folder))
    assert any("no quote" in p for p in problems)


def test_recorded_words_refuse_raw_html(tmp_path):
    # Raw HTML can hide a quote (a comment, an attribute) or show one the text reading misses
    # (an entity in an HTML block, words joined by <br>), so it is reported, not interpreted.
    cases = {
        "block_comment": 'Hamid agreed.\n\n<!-- "Approved: Q1–Q18 as recommended in the comment above" -->',
        "inline_comment": SAVED + ' <!-- "yes to all seven" -->',
        "attribute": "<div title='> \"Approved: Q1–Q18 as recommended in the comment above\"'>No quote</div>",
        "block_entity": SAVED + "\n\n<div>&quot;yes to all seven&quot;</div>",
        "inline_break": 'He said "Approved: Q1–Q18 as recommended<br>in the comment above"',
    }
    for name, words in cases.items():
        assert any("raw HTML" in p for p in _decision_fixture(tmp_path / name, 26, words)), name


def test_recorded_words_reject_a_repeated_section(tmp_path):
    words = ('"Approved: Q1–Q18 as recommended in the comment above"\n\n'
             "## Hamid's recorded words\n\nHamid also said \"yes to all seven\"")
    assert any("more than one" in p for p in _decision_fixture(tmp_path, 26, words))


SAVED = '"Approved: Q1–Q18 as recommended in the comment above"'


def test_recorded_words_read_displayed_text_not_raw_markdown(tmp_path):
    # Entity-encoded quote marks display as quote marks, so the unsaved words are checked.
    entity = SAVED + "\n\nHamid also said &quot;yes to all seven&quot;."
    assert any("yes to all seven" in p for p in _decision_fixture(tmp_path / "b", 26, entity))
    # Emphasis inside a quote displays the saved words.
    assert _decision_fixture(tmp_path / "c", 26, '"**Approved: Q1–Q18 as recommended in the comment above**"') == []


def test_recorded_words_recognise_a_formatted_heading(tmp_path):
    folder = tmp_path / "decisions"
    folder.mkdir()
    (folder / "EPM-DEC-001-0026-test.md").write_text(
        "# t\n\n| Status | Proposed |\n\n## **Hamid's recorded words**\n\nHe said \"yes to all seven\"\n")
    problems = epm_facts.quote_problems(epm_facts.REVIEWS, epm_facts.BACKLOG, epm_facts.ANSWERS, str(folder))
    assert any("yes to all seven" in p for p in problems)


def test_recorded_words_keep_comment_syntax_inside_code(tmp_path):
    fenced = SAVED + '\n\n```text\n<!-- "yes to all seven" -->\n```'
    assert any("yes to all seven" in p for p in _decision_fixture(tmp_path / "a", 26, fenced))
    inline = SAVED + '\n\nSee `<!-- "yes to all seven" -->`.'
    assert any("yes to all seven" in p for p in _decision_fixture(tmp_path / "b", 26, inline))


def test_recorded_words_continue_past_a_heading_nested_in_a_quote(tmp_path):
    words = SAVED + '\n\n> ## Example\n\nHamid also said "yes to all seven"'
    assert any("yes to all seven" in p for p in _decision_fixture(tmp_path, 26, words))


def test_recorded_words_match_a_saved_answer_with_formatting(tmp_path):
    # 205-batch1.md says "For each **a** response, ..."; both sides are compared as displayed text.
    assert _decision_fixture(tmp_path, 26, '"For each **a** response, use the revised wording below"') == []
