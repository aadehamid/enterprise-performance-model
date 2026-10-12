"""Phase 1 batch checks: each row's review record must match the source author's saved answer.

REVIEW_STANDARDS rule 8: a check of decided values compares each value with the
record that decided it. For a batch, that record is the saved answer
(`review-evidence/hamid-answers/<issue>-<batch>.md`), one numbered line per
question: `N: a — “sentence”` or `N: b — “sentence”`. Standard library only, so
evidence-gate.py can call it.
"""
import re

ANSWER_LINE = re.compile(r"(\d+): ([abc]) — “(.+)”")
NUMBERED_LINE = re.compile(r"^\s*\d")   # any line whose first non-space character is a digit

# #204 batch 1: question number -> row ID, as posted on #204 (comment 6130189084).
TRIGGERS_BATCH1_QUESTIONS = {
    1: "REL-00049", 2: "REL-00291", 3: "REL-00892", 4: "REL-00163", 5: "REL-00169", 6: "REL-00170",
    7: "REL-00252", 8: "REL-00396", 9: "REL-00398", 10: "REL-00400", 11: "REL-00403",
}


def answers(text):
    """(question number -> (answer letter, quoted sentence), problems) from a saved answer file.

    Every line that starts with a number is an answer and must parse; a number
    answered twice is reported rather than letting the later line win.
    """
    found, problems = {}, []
    for line in text.splitlines():
        if not NUMBERED_LINE.match(line):
            continue
        m = ANSWER_LINE.fullmatch(line.strip())
        if not m:
            problems.append(f"numbered answer line cannot be read: {line.strip()[:60]!r}")
            continue
        number = int(m.group(1))
        if number in found:
            problems.append(f"question {number} is answered more than once")
            continue
        found[number] = (m.group(2), m.group(3))
    return found, problems


def triggers_batch_problems(rows, answer_text, questions, v2, facts):
    """Problems with a triggers batch's review rows, checked against the saved answer.

    rows: the review CSV as dicts. questions: question number -> row ID.
    v2: row ID -> target-dispositions-v2 row. facts: (s, p, o) -> list of row IDs.
    Every answer here is (a) or (b); both emit target core:triggeredBy source.
    """
    saved, problems = answers(answer_text)
    if sorted(saved) != sorted(questions):
        problems.append(f"saved answer has questions {sorted(saved)}, expected {sorted(questions)}")
    by_id = {r["row_id"]: r for r in rows}
    if len(rows) != len(by_id) or set(by_id) != set(questions.values()):
        problems.append(f"review rows {sorted(by_id)} are not exactly the batch's {sorted(questions.values())}")
    for number, row_id in sorted(questions.items()):
        r, answer = by_id.get(row_id), saved.get(number)
        if r is None or answer is None:
            continue
        letter, sentence = answer
        where = f"question {number} ({row_id})"
        if r["question"] != str(number):
            problems.append(f"{where}: question is {r['question']}")
        if r["hamid_answer"] != letter:
            problems.append(f"{where}: hamid_answer {r['hamid_answer']} but the saved answer is {letter}")
        if r["hamid_words"] != sentence:
            problems.append(f"{where}: hamid_words differ from the saved answer's sentence")
        if r["scope_note_sentence"] != sentence:
            problems.append(f"{where}: scope_note_sentence differs from the saved answer's sentence")
        source = v2[row_id]["source_slug"]
        target = v2[row_id]["candidate_slugs"]
        if (r["source_slug"], r["target_slug"], r["scope_note_slug"]) != (source, target, source):
            problems.append(f"{where}: source/target/scope-note slug must be {source}, {target}, {source}")
        if letter not in "ab":
            problems.append(f"{where}: answer {letter} is not a trigger, but the row is recorded as one")
            continue
        if r["fresh_verdict"] != "APPROVE" or r["outcome"] != "Emitted as core:triggeredBy":
            problems.append(f"{where}: fresh_verdict/outcome must be APPROVE / Emitted as core:triggeredBy")
        # A (b) answer is a conditional trigger. Its condition is Hamid's whole sentence,
        # which states both what invokes the target and what does not.
        if letter == "b" and r["condition"] != sentence:
            problems.append(f"{where}: a conditional trigger's condition must be the answer's full sentence")
        if letter == "a" and r["condition"]:
            problems.append(f"{where}: an unconditional trigger has no condition")
        if row_id not in facts.get((target, "core:triggeredBy", source), []):
            problems.append(f"{where}: no stored fact {target} core:triggeredBy {source} carrying the row")
    return problems
