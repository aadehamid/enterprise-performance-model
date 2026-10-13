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
SWEEP_FIELDS = ("verdict", "verb", "target_slug", "direction", "stored_fact", "condition", "scope_note_sentence",
                "reason")
SWEEP_DECISION = "APPROVE: approved in the Phase 1 register (Hamid 2026-10-12, #207 comment 6133390674)"
SWEEP_HELD_OUTCOME = "Held: no relationship; question closed"
# Issues whose register rows are adopted into Step 4. Each has
# review-evidence/phase1-sweep/<issue>-review.csv covering exactly its register rows.
SWEEP_ADOPTED = ("206", "203", "210", "202")
# No-relationship rows the approved register keeps as duplicate provenance on a fact
# another row carries (mapping_v2.DUPLICATE_PROVENANCE_ATTACH). Each may sit on that
# fact only. REL-00436: "REL-00436 stays attached to that fact as duplicate provenance"
# (register reason); the fact stands through REL-00447.
SWEEP_PROVENANCE = {"REL-00436": ("CM-1-2-5-2-3", "core:dependsOnOutputOf", "CM-1-2-5-1-4")}


def sweep_files_problems(found):
    """Problems with the sweep review file names found: exactly <issue>-review.csv per adopted issue."""
    expected = {f"{i}-review.csv" for i in SWEEP_ADOPTED}
    problems = [f"{name} is missing for an adopted issue" for name in sorted(expected - set(found))]
    problems += [f"{name} is not the review file of an issue in SWEEP_ADOPTED" for name in sorted(set(found) - expected)]
    return problems


def scope_notes(taxonomy, slug):
    """The skos:scopeNote literals of proc:<slug> in Turtle text, whitespace-collapsed."""
    return [" ".join(t.split()) for t in literals(taxonomy, slug, "skos:scopeNote")]


def related_segments(taxonomy, slug):
    """proc:<slug>'s intake:relatedConcepts as (verb, target) pairs, read exactly as classify_v2.py reads them.

    The same per-line regexes and the same split: a relationship classify_v2 cannot
    see is not seen here either.
    """
    pairs, current = [], None
    for line in taxonomy.splitlines():
        m = re.match(r"proc:([A-Za-z]+-\d[\d-]*)\s+a\s+skos:Concept", line)
        if m:
            current = m.group(1)
            continue
        m = re.search(r'intake:relatedConcepts\s+"([^"]*)"', line)
        if m and current == slug:
            for part in m.group(1).split("|"):
                part = part.strip()
                if part and ":" in part:
                    verb, target = part.split(":", 1)
                    pairs.append((verb.strip(), target.strip()))
    return pairs


# Raw verbs a reversed register row is written with (EPM-DEC-001-0027).
MIRROR_VERBS = {"uses-input": "provides-input-to", "governed-by": "governs"}


def literals(taxonomy, slug, predicate):
    """The literals of one predicate of proc:<slug> in Turtle text.

    Reads only that subject's statement: it starts at "proc:<slug> a" (at any
    indentation), skips comments outside strings, and ends at the statement's
    closing "." outside strings. So a sentence in a comment or in another
    concept's statement does not count.
    """
    start = re.search(r"(?m)^[ \t]*proc:" + re.escape(slug) + r"[ \t]+a[ \t]", taxonomy)
    if not start:
        return []
    i, n, out = start.start(), len(taxonomy), []
    while i < n:
        if taxonomy.startswith('"""', i):
            j = taxonomy.index('"""', i + 3)
            out.append(("lit", taxonomy[i + 3:j])); i = j + 3
        elif taxonomy[i] == '"':
            j = i + 1
            while taxonomy[j] != '"':
                j += 2 if taxonomy[j] == "\\" else 1
            out.append(("lit", taxonomy[i + 1:j])); i = j + 1
        elif taxonomy[i] == "#":
            i = taxonomy.find("\n", i)
            i = n if i < 0 else i
        elif taxonomy[i] == "." and (i + 1 == n or taxonomy[i + 1].isspace()) and taxonomy[i - 1].isspace():
            break
        else:
            j = i
            while j < n and not taxonomy[j].isspace() and taxonomy[j] not in '"#':
                j += 1
            if j > i:
                out.append(("tok", taxonomy[i:j])); i = j
            else:
                i += 1
    found, pred = [], None
    for kind, text in out:
        if kind == "tok" and text not in (",", "@en") and not text.startswith("@") and not text.startswith("^^"):
            pred = None if text == ";" else (text if pred is None else pred)
        elif kind == "lit" and pred == predicate:
            found.append(text)
    return found


def sweep_batch_problems(issue, rows, register, approval_text, v2, facts, taxonomy=None):
    """Problems with one issue's sweep review rows, checked against the approved register.

    issue: the issue number as a string. rows: the batch review CSV as dicts.
    register: row ID -> register.csv row. v2: row ID -> target-dispositions-v2 row.
    facts: (s, p, o) -> list of row IDs. taxonomy: the pinned baseline taxonomy text; when
    given, each emitting row's sentence must appear in its scope-note concept's block.
    The review covers exactly the issue's register rows. Each row repeats its
    register row's decided values, Hamid's approval and the outcome they imply;
    an emitting row is on its stored fact, and a no-relationship row is on no fact.
    """
    problems = []
    if SWEEP_APPROVAL not in approval_text:
        problems.append("the saved approval does not contain Hamid's approval words")
    expected = {rid for rid, reg in register.items() if reg["issue"] == issue}
    got = {r["row_id"] for r in rows}
    for rid in sorted(expected - got):
        problems.append(f"{rid}: #{issue} register row has no review row")
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
        if reg["issue"] != issue or r["issue"] != issue:
            problems.append(f"{rid}: belongs to #{reg['issue']}, not #{issue}")
            continue
        for field in SWEEP_FIELDS:
            if r[field] != reg[field]:
                problems.append(f"{rid}: {field} differs from the approved register")
        if r["Hamid_decision"] != SWEEP_DECISION:
            problems.append(f"{rid}: Hamid_decision must be {SWEEP_DECISION!r}")
        outcome = (SWEEP_HELD_OUTCOME if reg["verdict"] == "no-relationship"
                   else f"Emitted as {reg['stored_fact'].split()[1]}" if reg["stored_fact"] else None)
        if r["outcome"] != outcome:
            problems.append(f"{rid}: outcome must be {outcome!r}")
        if r["source_slug"] != v2[rid]["source_slug"]:
            problems.append(f"{rid}: source_slug must be {v2[rid]['source_slug']}")
        carried = [k for k, ids in facts.items() if rid in ids]
        if reg["verdict"] == "no-relationship":
            allowed = [SWEEP_PROVENANCE[rid]] if rid in SWEEP_PROVENANCE else []
            if r["fresh_verdict"] != "HOLD" or carried != allowed:
                problems.append(f"{rid}: a no-relationship row stays HOLD and carries no fact"
                                + (f" except its provenance on {' '.join(allowed[0])}" if allowed else ""))
            continue
        if r["fresh_verdict"] != "APPROVE":
            problems.append(f"{rid}: fresh_verdict must be APPROVE")
        if r["scope_note_slug"] != r["source_slug"]:
            problems.append(f"{rid}: the sentence goes in the source's scope note")
        if taxonomy is not None:
            # The published relationship itself, as classify_v2 will read it.
            verb = MIRROR_VERBS.get(reg["verb"], reg["verb"]) if reg["direction"] == "reversed" else reg["verb"]
            segment = (verb, v2[rid]["raw_target"])
            if v2[rid]["verb"] != verb:
                problems.append(f"{rid}: the dispositions carry verb {v2[rid]['verb']!r}, not {verb!r}")
            pairs = related_segments(taxonomy, r["source_slug"])
            if pairs.count(segment) != 1:
                problems.append(f"{rid}: '{verb}: {segment[1]}' is not exactly once in "
                                f"{r['source_slug']}'s published relatedConcepts")
            # Another verb to the same target, such as the uncorrected enables left beside it.
            others = [v for v, t in pairs if t == segment[1] and v != verb]
            if others:
                problems.append(f"{rid}: {r['source_slug']}'s relatedConcepts also has {others} to {segment[1]}")
        sentence = " ".join(r["scope_note_sentence"].split())
        if taxonomy is not None and not any(sentence in note for note in scope_notes(taxonomy, r["scope_note_slug"])):
            problems.append(f"{rid}: the approved sentence is not in {r['scope_note_slug']}'s published scope note")
        fact = tuple(reg["stored_fact"].split())
        if carried != [fact]:
            problems.append(f"{rid}: carried by {carried}, expected only {' '.join(fact)}")
    return problems
