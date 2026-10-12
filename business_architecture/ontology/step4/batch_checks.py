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
        # recorded verbatim so no paraphrase can narrow or widen it.
        if letter == "b" and r["condition"] != sentence:
            problems.append(f"{where}: a conditional trigger's condition must be the answer's full sentence")
        if letter == "a" and r["condition"]:
            problems.append(f"{where}: an unconditional trigger has no condition")
        if row_id not in facts.get((target, "core:triggeredBy", source), []):
            problems.append(f"{where}: no stored fact {target} core:triggeredBy {source} carrying the row")
    return problems


# Phase 1 sweep (Hamid 2026-10-12, #207 comment 6133390674): the decided record is
# the approved register, review-evidence/phase1-sweep/register.csv, approved as a
# whole in review-evidence/hamid-answers/phase1-sweep.md.
SWEEP_APPROVAL = "approve register, Q1 yes, Q2 yes, Q3 yes, flagged: yes to all."
SWEEP_FIELDS = ("verdict", "verb", "target_slug", "stored_fact", "condition", "scope_note_sentence")


def sweep_batch_problems(rows, register, approval_text, v2, facts):
    """Problems with one issue's sweep review rows, checked against the approved register.

    rows: the batch review CSV as dicts. register: row ID -> register.csv row.
    v2: row ID -> target-dispositions-v2 row. facts: (s, p, o) -> list of row IDs.
    Each review row repeats its register row's decided values; an emitting row is
    on its stored fact, and a no-relationship row is on no fact.
    """
    problems = []
    if SWEEP_APPROVAL not in approval_text:
        problems.append("the saved approval does not contain Hamid's approval words")
    seen = set()
    for r in rows:
        rid = r["row_id"]
        if rid in seen:
            problems.append(f"{rid}: reviewed more than once")
        seen.add(rid)
        reg = register.get(rid)
        if reg is None:
            problems.append(f"{rid}: not in the approved register")
            continue
        for field in SWEEP_FIELDS:
            if r[field] != reg[field]:
                problems.append(f"{rid}: {field} differs from the approved register")
        if r["source_slug"] != v2[rid]["source_slug"]:
            problems.append(f"{rid}: source_slug must be {v2[rid]['source_slug']}")
        carried = [k for k, ids in facts.items() if rid in ids]
        if reg["verdict"] == "no-relationship":
            if r["fresh_verdict"] != "HOLD" or carried:
                problems.append(f"{rid}: a no-relationship row stays HOLD and carries no fact")
            continue
        if r["fresh_verdict"] != "APPROVE":
            problems.append(f"{rid}: fresh_verdict must be APPROVE")
        if r["scope_note_slug"] != r["source_slug"]:
            problems.append(f"{rid}: the sentence goes in the source's scope note")
        fact = tuple(reg["stored_fact"].split())
        if carried != [fact]:
            problems.append(f"{rid}: carried by {carried}, expected only {' '.join(fact)}")
    return problems
