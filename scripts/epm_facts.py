#!/usr/bin/env python3
"""epm-facts: the figures and row facts that agents quote, computed from source.

One place to get the numbers right, so no agent writes its own counting script.
Every answer names the files it read and the commit it read them at.

Usage (from anywhere in the repo):

    python3 scripts/epm_facts.py counts            # ledger, scoped sequences, gate, facts, Phase 1, reviews, taxonomy
    python3 scripts/epm_facts.py row REL-00436     # where one row stands
    python3 scripts/epm_facts.py section 201       # row IDs for one Phase 1 issue
    python3 scripts/epm_facts.py find "0024"       # repo-wide search, including text split across lines
    python3 scripts/epm_facts.py sweep main        # where wording this branch replaced or deleted still stands
    python3 scripts/epm_facts.py decisions         # check the EPM-DEC-001 records against their index
    python3 scripts/epm_facts.py names             # no tracked file names the decision owner (EPM-DEC-001-0049)
    add --json for machine-readable output

How it gets the numbers:

- Ledger and per-row status come from running the Step 4 pipeline
  (`mapping_v2.py`) and the evidence gate (`evidence-gate.py`) as they are, in a
  temporary copy of the step4 folder, so the repo is never written to and the
  counting logic is never duplicated.
- A Phase 1 row is a row of the source-correction backlog
  (`step4/source-workbook-backlog.md`): the first cell of a table row in a
  Phase 1 section, both cells of the #202 pairs table, and the IDs listed in
  the prose sections (the text before any parenthesis). An ID cited inside a
  rationale ("Precedent: REL-00366") is not a row. See EPM-DEC-001-0025.
- A review hold is a non-blank `owner_decision` cell that records a hold, in
  any wording ("HOLD ...", "Held for source correction", "Carry forward
  (remains held)"). Other columns are ignored (see test_review_holds_read_only_the_decision_column).

Standard library only, except taxonomy triple counts, which use rdflib when it
is installed, and the quotes command, which needs markdown-it-py (`uv run --with rdflib python3 scripts/epm_facts.py counts`).
"""
import argparse
import collections
import contextlib
import csv
import difflib
import glob
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEP4 = os.path.join(ROOT, "business_architecture", "ontology", "step4")
BACKLOG = os.path.join(STEP4, "source-workbook-backlog.md")
REVIEWS = os.path.join(STEP4, "review-evidence")
FACTS = os.path.join(STEP4, "canonical-facts.csv")
TAXONOMY = os.path.join(ROOT, "business_architecture", "ontology", "build", "output", "step3-taxonomy.ttl")
DECISIONS = os.path.join(ROOT, "business_architecture", "domain", "decisions")
ANSWERS = os.path.join(REVIEWS, "decision-owner-answers")
SCOPED = os.path.join(STEP4, "scoped-sequence")

NOT_HELD = {"AmbiguousDeferred", "ExternalGovernanceReference", "StructuredFlowValue"}
HOLD_WORD = re.compile(r"(?i)\bhold\b|\bheld\b")
REL = re.compile(r"REL-\d{5}")
# A list line: IDs separated by commas, semicolons or "and", ending with optional
# punctuation or with a separator when the list wraps onto the next line.
ID_LIST = re.compile(r"REL-\d{5}(?:\s*(?:,|;|and|,\s*and)\s*REL-\d{5})*\s*(?:,\s*and|and|[,.;:])?")

# Backlog section heading prefix -> Phase 1 issue. Sections not listed here
# (the index, Definitions, the identity-rule ruling) hold no Phase 1 rows.
SECTION_ISSUE = [
    ("G3 Section B", 201),
    ("G1b pairs held on both sides", 202),
    ("G1b rows held for a verb correction", 202),
    ("Supply & Trading recommend/advise rows", 203),
    ("Triggers pass", 204),
    ("Precedes/follows holds", 205),
    ("Governed-by rows held in the verb reviews", 206),
    ("Governed-by pass backlog", 206),
    ("Governed-by superseded approvals", 206),
    ("G3 Section A", 209),
    ("Other verb-review holds", 210),
]

# The pipeline's named hold sets, in the order used to explain a hold.
HOLD_SETS = [
    "USES_INPUT_20260926_HOLDS", "USES_INPUT_G1A_20260926_HOLDS", "INFORMEDBY_20260926_HOLDS",
    "GOVERNEDBY_20260926_HOLDS", "TRIGGERS_20260926_HOLDS", "PRECEDES_20260927_HOLDS",
]


def rel(path):
    return os.path.relpath(path, ROOT)


def commit():
    try:
        sha = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = subprocess.call(["git", "-C", ROOT, "diff", "--quiet", "HEAD", "--", rel(STEP4)]) != 0
        return sha + (" (step4 has uncommitted changes)" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


# ---------- pipeline ----------

def run_pipeline():
    """Run mapping_v2.py and evidence-gate.py in a temp copy; return their globals."""
    tmp = tempfile.mkdtemp(prefix="epm-facts-")
    try:
        work = os.path.join(tmp, "step4")
        shutil.copytree(STEP4, work, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
        # The gate compares the published taxonomy with the pinned baseline, at ../build/output.
        published = os.path.join(os.path.dirname(STEP4), "build", "output", "step3-taxonomy.ttl")
        os.makedirs(os.path.join(tmp, "build", "output"))
        shutil.copyfile(published, os.path.join(tmp, "build", "output", "step3-taxonomy.ttl"))
        cwd = os.getcwd()
        os.chdir(work)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mapping = runpy.run_path(os.path.join(work, "mapping_v2.py"), run_name="__main__")
            gate, gate_ok, gate_text = run_keeping_globals(os.path.join(work, "evidence-gate.py"))
        finally:
            os.chdir(cwd)
        return mapping, gate, gate_ok and "GATE GREEN" in gate_text, gate_text
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_keeping_globals(path):
    """Run a script as __main__ and keep its globals even if it calls sys.exit.

    The evidence gate exits non-zero when a check fails; the counts it computed
    before exiting are exactly what a caller needs to see in that case.
    Returns (globals, exited_cleanly, captured stdout).
    """
    namespace = {"__name__": "__main__", "__file__": path}
    out = io.StringIO()
    ok = True
    with open(path) as f:
        code = compile(f.read(), path, "exec")
    try:
        with contextlib.redirect_stdout(out):
            exec(code, namespace)
    except SystemExit as e:
        ok = e.code in (0, None)
    return namespace, ok, out.getvalue()


def scoped_rows(mapping):
    """Rows emitted as scoped sequences; empty on trees before EPM-DEC-001-0026."""
    return set(mapping.get("SCOPED_SEQUENCE_ROWS", ()))


def ledger(mapping):
    """Ledger categories. A scoped-sequence row (EPM-DEC-001-0026) emits a node, not a core fact."""
    v2 = mapping["v2"]
    emitting = set(mapping["emitting_ids"])
    scoped = scoped_rows(mapping)
    disp = collections.Counter(r["disposition"] for r in v2)
    held = {r["row_id"] for r in v2
            if r["row_id"] not in emitting and r["row_id"] not in scoped and r["disposition"] not in NOT_HELD}
    return {
        "mentions": len(v2),
        "emitting": len(emitting),
        "held": len(held),
        "deferred": disp["AmbiguousDeferred"],
        "external_governance": disp["ExternalGovernanceReference"],
        "structured_flow": disp["StructuredFlowValue"],
        "scoped_sequence": len(scoped),
        "canonical_facts_pipeline": len(mapping["facts"]),
    }, held, emitting


def hold_reason(mapping, row_id):
    for name in HOLD_SETS:
        if row_id in mapping[name]:
            return name
    if row_id in mapping["PROPERTY_RULE_HOLDS"]:
        return "PROPERTY_RULE_HOLDS"
    if mapping["ctx"].get(row_id) == "HOLD":
        return "context-pass HOLD"
    return "disposition"


# ---------- backlog ----------

def issue_for(heading):
    for prefix, issue in SECTION_ISSUE:
        if heading.startswith(prefix):
            return issue
    return None


def phase1_rows(text=None):
    """Map each Phase 1 row ID to (issue, section heading), from the backlog's structure.

    Formatting does not matter: table cells are read with their padding
    stripped, and list lines are read after stripping indentation, bullets and
    bold. A row's own section wins over the #202 pairs table, which repeats
    some rows held in other sections (REL-00469 in #203, REL-00489 in #201).
    An ID that is only cited inside a sentence or a parenthesis is not a row.
    """
    if text is None:
        with open(BACKLOG) as f:
            text = f.read()
    home, paired = {}, {}
    section = None
    for raw in text.split("\n"):
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        issue = issue_for(section or "")
        if issue is None or not line:
            continue
        if line.startswith("|"):
            cells = [c.strip().strip("*`").strip() for c in line.strip("|").split("|")]
            if not cells or not re.fullmatch(r"REL-\d{5}", cells[0]):
                continue
            if section.startswith("G1b pairs held on both sides"):
                for cell in cells[:2]:
                    if re.fullmatch(r"REL-\d{5}", cell):
                        paired.setdefault(cell, (issue, section))
            else:
                home.setdefault(cells[0], (issue, section))
            continue
        # A list line: "- REL-1 (note)", "- **REL-1** (...)", "REL-1, REL-2,", "* REL-1".
        item = re.sub(r"^([-*+]\s+)", "", line)
        prefix = item.split("(")[0].replace("*", "").replace("`", "").strip()
        if not ID_LIST.fullmatch(prefix):
            continue  # a sentence, not a list of row IDs
        for row_id in REL.findall(prefix):
            home.setdefault(row_id, (issue, section))
    rows = dict(paired)
    rows.update(home)
    return rows


# ---------- reviews ----------

def review_holds():
    """Per review file: rows whose owner_decision records a hold; and per row, its decisions."""
    per_file, per_row = {}, collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(REVIEWS, "*.csv"))):
        try:
            with open(path, newline="") as f:
                reader = list(csv.DictReader(f))
        except (csv.Error, UnicodeDecodeError):
            continue
        if not reader or "owner_decision" not in reader[0]:
            continue
        held = []
        for r in reader:
            decision = (r.get("owner_decision") or "").strip()
            row_id = (r.get("row_id") or "").strip()
            if not row_id.startswith("REL-") or not decision:
                continue
            per_row[row_id].append((os.path.basename(path), decision))
            if HOLD_WORD.search(decision):
                held.append(row_id)
        per_file[os.path.basename(path)] = len(set(held))
    return per_file, per_row


# ---------- facts ----------

def stored_facts():
    with open(FACTS, newline="") as f:
        return list(csv.DictReader(f))


# ---------- scoped sequences ----------

def scoped_sequences():
    """Nodes and handoffs from scoped-sequence/scoped-sequences.csv, with its check results."""
    # Load by path under its own name: the evidence gate loads a temporary copy of
    # the same file, and a cached plain "build" module would point at that copy.
    if not os.path.exists(os.path.join(SCOPED, "build.py")):
        return {"nodes": 0, "handoffs": 0, "rows": [], "problems": []}  # a tree before EPM-DEC-001-0026
    import importlib.util
    spec = importlib.util.spec_from_file_location("epm_scoped_sequence_build", os.path.join(SCOPED, "build.py"))
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    columns, rows = build.load()
    out = build.counts(rows)
    out["problems"] = build.check(columns, rows)
    return out


# ---------- taxonomy ----------

def taxonomy():
    try:
        import rdflib
    except ImportError:
        return {"note": "rdflib not installed; run with `uv run --with rdflib`"}
    g = rdflib.Graph().parse(TAXONOMY, format="turtle")
    skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    intake = "https://w3id.org/lsc/ontology/intake/"
    concepts = set(g.subjects(rdflib.RDF.type, skos.Concept))
    return {
        "triples": len(g),
        "concepts": len(concepts),
        "concepts_with_definition": len({s for s in concepts if (s, skos.definition, None) in g}),
        "broader_links": len(list(g.triples((None, skos.broader, None)))),
        "intake_triples": sum(1 for _, p, _ in g if str(p).startswith(intake)),
    }


# ---------- commands ----------

def cmd_counts(args):
    mapping, gate, gate_green, gate_text = run_pipeline()
    gate_lines = gate_text.splitlines()
    led, held, emitting = ledger(mapping)
    facts = stored_facts()
    p1 = phase1_rows()
    p1_ids = set(p1)
    by_issue = collections.Counter(issue for issue, _ in p1.values())
    outside = held - p1_ids
    per_file, _ = review_holds()
    out = {
        "commit": commit(),
        "ledger": led,
        "conservation": (led["emitting"] + led["held"] + led["deferred"] + led["external_governance"]
                         + led["structured_flow"] + led["scoped_sequence"]),
        "canonical_facts_file": len(facts),
        "evidence_gate": {
            "green": gate_green,
            "promoted": gate.get("promoted"),
            "held": gate.get("held_ctx"),
            "pass_checks": sum(1 for line in gate_lines if line.startswith("PASS")),
            "fail_checks": sum(1 for line in gate_lines if line.startswith("FAIL")),
        },
        "phase1": {
            "rows": len(p1_ids),
            "held": len(p1_ids & held),
            "not_held": sorted(p1_ids - held),
            "by_issue": dict(sorted(by_issue.items())),
            "held_outside": len(outside),
            "held_outside_by_reason": dict(collections.Counter(hold_reason(mapping, i) for i in outside).most_common()),
        },
        "review_holds_by_file": per_file,
        "emitting_by_verb": {f"{v} -> {p}": n for (v, p), n in sorted(mapping["perverb"].items())},
        "scoped_sequences": scoped_sequences(),
        "taxonomy": taxonomy(),
        "sources": [rel(os.path.join(STEP4, "mapping_v2.py")), rel(os.path.join(STEP4, "evidence-gate.py")),
                    rel(FACTS), rel(BACKLOG), rel(REVIEWS) + "/*.csv",
                    rel(os.path.join(SCOPED, "scoped-sequences.csv")), rel(TAXONOMY)],
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    led = out["ledger"]
    print(f"commit {out['commit']}")
    print(f"ledger: {led['emitting']} emitting / {led['held']} held / {led['deferred']} deferred / "
          f"{led['external_governance']} external governance / {led['structured_flow']} structured flow / "
          f"{led['scoped_sequence']} scoped sequence = {out['conservation']} (of {led['mentions']} mentions)")
    ss = out["scoped_sequences"]
    print(f"scoped sequences (EPM-DEC-001-0026): {ss['nodes']} nodes, {ss['handoffs']} handoffs; "
          f"source table: {len(ss['problems'])} problem(s)")
    print(f"canonical facts: {out['canonical_facts_file']} in canonical-facts.csv; pipeline builds {led['canonical_facts_pipeline']}")
    print("emitting by raw verb -> stored predicate: " + ", ".join(f"{k} {n}" for k, n in out["emitting_by_verb"].items()))
    eg = out["evidence_gate"]
    print(f"evidence gate: {'GREEN' if eg['green'] else 'NOT GREEN'}; promoted {eg['promoted']} / held {eg['held']}; "
          f"{eg['pass_checks']} PASS / {eg['fail_checks']} FAIL")
    ph = out["phase1"]
    print(f"Phase 1 (EPM-DEC-001-0025): {ph['rows']} rows, {ph['held']} held; not held: {', '.join(ph['not_held']) or 'none'}")
    print("  by issue: " + ", ".join(f"#{k} {v}" for k, v in ph["by_issue"].items()))
    print(f"  held outside Phase 1: {ph['held_outside']}: " + ", ".join(f"{k} {v}" for k, v in ph["held_outside_by_reason"].items()))
    print("review holds (owner_decision) by file:")
    for name, n in out["review_holds_by_file"].items():
        if n:
            print(f"  {n:4d}  {name}")
    print("taxonomy: " + ", ".join(f"{k} {v}" for k, v in out["taxonomy"].items()))
    print("sources: " + "; ".join(out["sources"]))
    return 0


def cmd_row(args):
    row_id = args.row_id.upper()
    mapping, _, _, _ = run_pipeline()
    _, held, emitting = ledger(mapping)
    scoped = scoped_rows(mapping)
    rec = next((r for r in mapping["v2"] if r["row_id"] == row_id), None)
    if rec is None:
        print(f"{row_id}: not in target-dispositions-v2.csv", file=sys.stderr)
        return 1
    facts = [f for f in stored_facts() if row_id in f["row_ids"].split(";")]
    p1 = phase1_rows()
    _, per_row = review_holds()
    status = ("emitting" if row_id in emitting else "scoped sequence" if row_id in scoped
              else "held" if row_id in held else rec["disposition"])
    out = {
        "commit": commit(),
        "row_id": row_id,
        "verb": rec["verb"],
        "source": rec["source_slug"],
        "candidate_targets": rec["candidate_slugs"],
        "disposition": rec["disposition"],
        "status": status,
        "hold_reason": hold_reason(mapping, row_id) if row_id in held else None,
        "stored_facts": [f"{f['subject']} {f['predicate']} {f['object']}" for f in facts],
        "review_decisions": per_row.get(row_id, []),
        "phase1_issue": p1[row_id][0] if row_id in p1 else None,
        "backlog_section": p1[row_id][1] if row_id in p1 else None,
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    print(f"commit {out['commit']}")
    print(f"{row_id}: {out['source']} {out['verb']} -> {out['candidate_targets'] or '?'}")
    print(f"  status: {status}" + (f" ({out['hold_reason']})" if out["hold_reason"] else "") + f"; disposition {out['disposition']}")
    print(f"  stored facts carrying it: {'; '.join(out['stored_facts']) or 'none'}")
    if out["phase1_issue"]:
        print(f"  Phase 1: issue #{out['phase1_issue']}, section \"{out['backlog_section']}\"")
    else:
        print("  Phase 1: not a backlog row")
    for name, decision in out["review_decisions"]:
        print(f"  review {name}: {decision[:120]}")
    return 0


def cmd_section(args):
    rows = phase1_rows()
    ids = sorted(r for r, (issue, _) in rows.items() if issue == args.issue)
    if args.json:
        print(json.dumps({"commit": commit(), "issue": args.issue, "rows": ids}, indent=2))
        return 0
    print(f"commit {commit()}")
    print(f"#{args.issue}: {len(ids)} rows (from {rel(BACKLOG)})")
    print(" ".join(ids))
    return 0 if ids else 1


def find_hits(needle, root=ROOT):
    """Hits for needle in every tracked text file under root: (file, line, kind, text), kind "line" or
    "split" (the text runs across two lines). A file is text when it is UTF-8 with no NUL byte,
    whatever its extension (.sql, .jsonld and .page files included)."""
    # -z: git quotes paths with non-ASCII characters otherwise, and a quoted path cannot be opened.
    files = subprocess.check_output(["git", "-C", root, "ls-files", "-z"], text=True).split("\0")
    flat_needle = re.sub(r"\s+", " ", needle).strip().lower()
    hits = []
    for name in files:
        if not name:
            continue
        path = os.path.join(root, name)
        try:
            with open(path, "rb") as f:
                data = f.read()
            if b"\0" in data:
                continue
            text = data.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lines = text.split("\n")
        for i, line in enumerate(lines, 1):
            if needle.lower() in line.lower():
                hits.append((name, i, "line", line.strip()))
        # Split across lines: join each line with the next one and search the joined text.
        for i in range(len(lines) - 1):
            joined = re.sub(r"\s+", " ", lines[i] + " " + lines[i + 1]).lower()
            if flat_needle in joined and flat_needle not in lines[i].lower() and flat_needle not in lines[i + 1].lower():
                hits.append((name, i + 1, "split", (lines[i].strip() + " / " + lines[i + 1].strip())))
    return hits


def cmd_find(args):
    """Search tracked text files; also match text split across lines."""
    needle = args.text
    hits = find_hits(needle)
    if args.json:
        print(json.dumps({"commit": commit(), "text": needle, "hits": [dict(zip(("file", "line", "kind", "text"), h)) for h in hits]}, indent=2))
        return 0
    print(f"commit {commit()}: {len(hits)} hits for {needle!r}")
    for name, i, kind, line in hits:
        print(f"{name}:{i}: [{kind}] {line[:200]}")
    return 0



# ---------- sweep ----------

# A date on the line (YYYY-MM-DD). The repository writes dated notes in many forms (*2026-10-21:*,
# (Superseded 2026-10-13: ...), Added 2026-10-20 ...), so the sweep marks any line that holds a date
# and leaves it to the reader to see whether the date notes the clause in question.
DATED = re.compile(r"\b(19|20)\d\d-\d\d-\d\d\b")


def changed_phrases(diff):
    """The old wording a unified diff (-U1) replaced or deleted: for each run of changed words, those words
    with one word of context on each side, kept when that makes at least two words and eight characters,
    so "at 34 answerable" is searched, not "34" alone. The context may come from an unchanged neighbouring
    line, which -U1 supplies. An addition has no old wording and gives none."""
    phrases = []
    for hunk in re.split(r"^@@[^\n]*@@[^\n]*\n", diff, flags=re.M)[1:]:
        # A hunk ends where the next file's header begins; its "--- a/..." and "+++ b/..." lines are not text.
        body = re.split(r"^diff --git ", hunk, maxsplit=1, flags=re.M)[0]
        # Unchanged lines (" ") belong to both sides, so a word on one can be the context of a change.
        old = [l[1:] for l in body.split("\n") if l[:1] in (" ", "-")]
        new = [l[1:] for l in body.split("\n") if l[:1] in (" ", "+")]
        a, b = " ".join(old).split(), " ".join(new).split()
        for op, i1, i2, _, _ in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op not in ("replace", "delete"):
                continue
            words = a[max(0, i1 - 1):min(len(a), i2 + 1)]
            phrase = " ".join(words).strip(" .,;:()|*`\"'")
            if len(words) >= 2 and len(phrase) >= 8 and phrase not in phrases:
                phrases.append(phrase)
    return phrases


def sweep(base, root=ROOT):
    """For each phrase the branch replaced or deleted since base, every place in the tracked text files that
    still holds it, each marked "dated" when its line holds a date (DATED) and "live" otherwise."""
    try:
        diff = subprocess.check_output(["git", "-C", root, "diff", "-U1", "--no-color", f"{base}...HEAD"],
                                       text=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"sweep: cannot diff {base}...HEAD: {e.stderr.strip()}")
    report = []
    for phrase in changed_phrases(diff):
        hits = [(name, i, "dated" if DATED.search(text) else "live", text) for name, i, _, text in find_hits(phrase, root)]
        report.append((phrase, hits))
    return report


def cmd_sweep(args):
    report = sweep(args.base)
    if args.json:
        print(json.dumps({"commit": commit(), "base": args.base, "phrases": [
            {"phrase": p, "hits": [dict(zip(("file", "line", "state", "text"), h)) for h in hits]} for p, hits in report]}, indent=2))
        return 0
    found = [(p, hits) for p, hits in report if hits]
    places = len({(name, i) for _, hits in found for name, i, _, _ in hits})
    print(f"commit {commit()}: {len(report)} replaced or deleted phrase(s) since {args.base}; {len(found)} still found, "
          f"in {places} place(s). A date on a line may note another clause, or none: read each place.")
    for phrase, hits in found:
        live = sum(1 for h in hits if h[2] == "live")
        print(f"\n{phrase!r}: {live} on a line without a date, {len(hits) - live} on a line with one")
        for name, i, state, text in sorted(hits, key=lambda h: h[2] != "live")[:5]:
            print(f"  {name}:{i}: [{'no date on line' if state == 'live' else 'date on line'}] {text[:150]}")
        if len(hits) > 5:
            print(f"  ... and {len(hits) - 5} more (epm_facts.py --json sweep {args.base} lists them all)")
    return 0


# ---------- decision records ----------

STATUS_WORDS = {"Proposed", "Decided", "Superseded"}
QUOTE = re.compile(r'"[^"]{3,}"')


def _status_parts(status):
    """Return (lead word, set of record numbers named after 'amended by')."""
    lead = re.match(r"\s*(\w+)", status)
    amended = set()
    for clause in re.findall(r"amended by ([^;]*)", status):
        clause = re.sub(r"\([^)]*\)", "", clause)  # drop dates such as "(2026-10-06)"
        amended.update(re.findall(r"(?:EPM-DEC-001-)?\b(\d{4})\b", clause))
    return (lead.group(1) if lead else ""), amended


def decision_problems(folder=DECISIONS):
    """Return a list of problems in the EPM-DEC-001 records and their index."""
    problems = []
    records = {}
    for path in sorted(glob.glob(os.path.join(folder, "EPM-DEC-001-*.md"))):
        number = re.search(r"EPM-DEC-001-(\d{4})", os.path.basename(path)).group(1)
        with open(path) as f:
            text = f.read()
        m = re.search(r"^\| Status \| (.+?) \|\s*$", text, re.M)
        if not m:
            problems.append(f"{number}: no Status row")
            continue
        records[number] = (path, text, m.group(1).strip())
    index_path = os.path.join(folder, "README.md")
    with open(index_path) as f:
        index = {}
        for line in f:
            m = re.match(r"\| \[EPM-DEC-001-(\d{4})\]\(([^)]+)\) \|[^|]*\| ([^|]+) \|", line)
            if m:
                if m.group(1) in index:
                    problems.append(f"{m.group(1)}: listed twice in the index")
                index[m.group(1)] = (m.group(2), m.group(3).strip())
    for number in sorted(set(records) - set(index)):
        problems.append(f"{number}: record not listed in the index")
    for number in sorted(set(index) - set(records)):
        problems.append(f"{number}: index lists a record that does not exist")
    for number, (path, text, status) in sorted(records.items()):
        lead, amended = _status_parts(status)
        if lead not in STATUS_WORDS:
            problems.append(f"{number}: status {status!r} does not start with Proposed, Decided or Superseded")
        for other in sorted(amended):
            if other not in records:
                problems.append(f"{number}: amended by {other}, which does not exist")
        if number in index:
            link, index_status = index[number]
            if link != os.path.basename(path):
                problems.append(f"{number}: index links {link}, file is {os.path.basename(path)}")
            if _status_parts(index_status) != (lead, amended):
                problems.append(f"{number}: index status {index_status!r} differs from record status {status!r}")
        # From 0026 on, quote_problems() checks the recorded words more strictly (block
        # quotes and curly quotes included, against the saved answers); this simpler
        # presence rule covers the earlier records it skips.
        if lead == "Decided" and int(number) < FIRST_QUOTE_CHECKED_DECISION:
            words = re.search(r"^## The decision owner's recorded words\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
            if not words or not QUOTE.search(words.group(1)):
                problems.append(f"{number}: Decided, but no quote under \"The decision owner's recorded words\"")
    return problems


# ---------- quotes ----------

# A quoted span of three or more words, in straight or curly double quotes.
QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')


def _flat(text):
    return re.sub(r"\s+", " ", text).strip()


def answer_corpus(folder=ANSWERS):
    """The decision owner's saved answers, whitespace-collapsed, without each file's HTML header comment."""
    parts = []
    for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
        with open(path) as f:
            parts.append(_flat(re.sub(r"<!--.*?-->", "", f.read(), flags=re.S)))
    return "\n".join(parts)


def _spans(text):
    """Quoted spans of three or more words; an ellipsis splits a span into parts."""
    for m in QUOTED.finditer(text):
        for part in (m.group(1) or m.group(2)).split("…"):
            part = _flat(part)   # punctuation inside the quote marks is kept and must match
            if len(part.split()) >= 3:
                yield part


def block_quotes(text):
    """The paragraphs of every Markdown block quote, found by a CommonMark parser.

    A parser, not a regex: quotes nested in lists, lazy continuation lines and
    blocks that interrupt a quote all follow CommonMark (markdown-it-py). Code
    and HTML inside a quote are checked too, so no quoted text goes unread.
    """
    from markdown_it import MarkdownIt
    paras, depth = [], 0
    for tok in MarkdownIt("commonmark").parse(text):
        if tok.type == "blockquote_open":
            depth += 1
        elif tok.type == "blockquote_close":
            depth -= 1
        elif depth > 0 and tok.type in ("inline", "fence", "code_block"):
            paras.append(tok.content)
        elif depth > 0 and tok.type == "html_block":
            paras.append(re.sub(r"<[^>]+>", " ", tok.content))   # the visible text
    return [p for p in paras if p.strip()]


def displayed_text(tok):
    """The words a reader sees for one block token, as the CommonMark parser renders them.

    Inline text comes from the parsed children: text (entities decoded) and
    inline code, with emphasis markers dropped. Code blocks are shown verbatim.
    Raw HTML is not rendered here; callers that must not miss text refuse it
    (see has_html).
    """
    if tok.type == "inline":
        out = []
        for child in tok.children or []:
            if child.type in ("text", "code_inline"):
                out.append(child.content)
            elif child.type in ("softbreak", "hardbreak"):
                out.append(" ")
        return "".join(out)
    if tok.type in ("fence", "code_block"):
        return tok.content
    return ""


def has_html(tok):
    """True when a block token is, or contains, raw HTML (including comments) or an image.

    Both can hide words or show words the text reading misses (an image shows its
    alt text when it fails to load), so checked text refuses them.
    """
    return tok.type == "html_block" or any(c.type in ("html_inline", "image") for c in (tok.children or []))


def rendered_blocks(text):
    """A Markdown document's displayed text, one whitespace-collapsed line per block.

    Each paragraph, heading, list item and code block is its own line, so a
    quote can match only inside one block. A block that holds raw HTML (such
    as a saved answer's header comment) is left out: its displayed words
    cannot be read reliably, so nothing may be quoted from it.
    """
    from markdown_it import MarkdownIt
    lines = (_flat(displayed_text(t)) for t in MarkdownIt("commonmark").parse(text) if not has_html(t))
    return [line for line in lines if line]


APOSTROPHES = "'\u2019\u02bc"   # U+2018 only opens a quotation; it is never an apostrophe


def _is_delimiter(ch):
    """Punctuation or a symbol that ends a word. Apostrophes, dashes and soft
    hyphens join a word ("agreement’s", "source-author", "Q1–Q18"), so they do not."""
    import unicodedata
    cat = unicodedata.category(ch)
    return cat[0] in "PS" and cat != "Pd" and ch not in APOSTROPHES


def in_corpus_as_words(span, corpus):
    """True when the span's words appear, in order, as whole words of one corpus line.

    Words are whitespace-separated tokens. Inner words must match exactly. The
    first and last words may differ from their source tokens only by delimiter
    punctuation outside them ("approve" in "(approve", "change" in "change.").
    So "agreement" does not match "agreement’s", "workers" does not match
    "workers’", and "author" does not match "source-author". The rule is strict
    on purpose: a quote that fails it can always quote the whole token instead.
    """
    words = span.split()
    if not words:
        return False
    n = len(words)
    for line in corpus.split("\n"):
        tokens = line.split()
        for i in range(len(tokens) - n + 1):
            window = tokens[i:i + n]
            if n > 1 and window[1:-1] != words[1:-1]:
                continue
            first, last = words[0], words[-1]
            if n == 1:
                if _edge_ok(window[0], first, start=True) and _edge_ok(window[0], first, start=False):
                    return True
                continue
            if _edge_ok(window[0], first, start=True) and _edge_ok(window[-1], last, start=False):
                return True
    return False


def _edge_ok(token, word, start):
    """The quoted edge word sits in the source token without cutting a word.

    start=True: word must be a suffix of token; any extra text before it must be
    delimiters. start=False: the mirror image at the end.
    """
    if start:
        if not token.endswith(word):
            return False
        extra = token[:len(token) - len(word)]
    else:
        if not token.startswith(word):
            return False
        extra = token[len(word):]
    return all(_is_delimiter(c) for c in extra)


def rendered_answer_corpus(folder=ANSWERS):
    """The decision owner's saved answers as displayed text, one line per block, to compare with displayed quotes."""
    lines = []
    for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
        with open(path) as f:
            lines.extend(rendered_blocks(f.read()))
    return "\n".join(lines)


def displayed_status_rows(text):
    """(value, contains raw HTML) for every displayed table row whose first cell reads "Status"."""
    from markdown_it import MarkdownIt
    tokens = MarkdownIt("commonmark").enable("table").parse(text)
    rows, current = [], None
    for tok in tokens:
        if tok.type == "tr_open":
            current = []
            rows.append(current)
        elif tok.type == "tr_close":
            current = None
        elif tok.type == "inline" and current is not None:
            current.append((_flat(displayed_text(tok)), has_html(tok)))
    return [(row[1][0], any(html for _, html in row)) for row in rows
            if len(row) >= 2 and row[0][0].lower() == "status"]


RECORDED_WORDS_KEY = "thedecisionownersrecordedwords"
INVISIBLE_MARKS = re.compile("[\ufe00-\ufe0f\U000e0100-\U000e01ef]")   # variation selectors


def section_key(heading):
    """A heading's letters only, normalised and lower-cased, so look-alikes compare equal."""
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFKC", heading).casefold() if ch.isalpha())


def has_invisible(text):
    """True when text holds an invisible format character (Unicode Cf) or a variation selector."""
    import unicodedata
    return bool(INVISIBLE_MARKS.search(text)) or any(unicodedata.category(ch) == "Cf" for ch in text)


def recorded_words(text):
    """Each "The decision owner's recorded words" section: (displayed blocks, contains raw HTML, block-quote paragraphs).

    The displayed text comes back as one string per block, so quote marks pair
    only within a block: a stray mark in one paragraph cannot open a quote that
    closes in the next (issue #251). quote_problems reports a block whose quote
    marks do not pair, so an unclosed quotation is not left unchecked.

    A block-quote paragraph is a quotation in its own right, so it is returned
    whole, to be checked like a quoted span.

    Sections are bounded by the document's own level-two headings (parser level
    0), so a "## " line in a code fence or a heading nested in a block quote is
    not a boundary, and a heading written with a tab or with emphasis is one.
    Raw HTML is reported rather than interpreted: it can hide words or show
    words the text extraction misses.
    """
    from markdown_it import MarkdownIt
    tokens = MarkdownIt("commonmark").parse(text)
    sections, current, depth = [], None, 0
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "heading_open" and tok.tag == "h2" and tok.level == 0:
            current = None
            if section_key(displayed_text(tokens[i + 1])) == RECORDED_WORDS_KEY:
                current = {"parts": [], "html": has_html(tokens[i + 1]), "quoted": []}
                sections.append(current)
            i += 3  # heading_open, inline, heading_close
            continue
        depth += {"blockquote_open": 1, "blockquote_close": -1}.get(tok.type, 0)
        if current is not None:
            current["parts"].append(displayed_text(tok))
            current["html"] = current["html"] or has_html(tok)
            if depth > 0 and tok.type in ("inline", "fence", "code_block"):
                current["quoted"].append(_flat(displayed_text(tok)))
        i += 1
    return [([p for p in sec["parts"] if p], sec["html"], [q for q in sec["quoted"] if q])
            for sec in sections]


# Decision records from this number on quote only saved answers. Records 0001 to
# 0025 quote sessions that were never saved (PR #231 added this check).
FIRST_QUOTE_CHECKED_DECISION = 26


def quote_problems(reviews=REVIEWS, backlog=BACKLOG, answers=ANSWERS, decisions=DECISIONS):
    """Text attributed to the decision owner that is not word for word in a saved answer.

    Checked: in every review file with an `owner_words` column, that column, the
    `scope_note_sentence`, and each quoted span of three or more words in
    `semantic_reason` and `owner_decision`; every block quote in the
    source-correction backlog; and each quoted span of three or more words in
    the displayed text of the "The decision owner's recorded words" section of EPM-DEC-001
    records from 0026 on, compared with the saved answers' displayed text; a
    Decided record must have at least one, raw HTML there is reported, and so is a paragraph there whose quote marks do not pair (an odd count of straight marks, or unequal curly ones). An ellipsis (…) splits a quoted span, and each
    part of three or more words is checked. Each text is searched across all
    saved answers, not only the comment its row cites. Paraphrases are not
    checked. Needs markdown-it-py (check.sh supplies it).
    """
    corpus = answer_corpus(answers)
    problems = []
    if not corpus.strip():
        problems.append(f"no saved answer text in {answers}: nothing to check quotes against")

    def check(where, text):
        if text and _flat(text) not in corpus:
            problems.append(f"{where}: not in a saved answer: {_flat(text)[:90]!r}")

    checked_files = 0
    for path in sorted(glob.glob(os.path.join(reviews, "*.csv"))):
        with open(path, newline="") as f:
            header = next(csv.reader(f), [])
            f.seek(0)
            rows = list(csv.DictReader(f))
        if "owner_words" not in header:
            continue
        repeated = sorted({h for h in header if header.count(h) > 1})
        if repeated:
            problems.append(f"{os.path.basename(path)}: repeated column {repeated}; cannot check it unambiguously")
            continue
        if not rows:
            problems.append(f"{os.path.basename(path)}: has an owner_words column but no rows")
            continue
        checked_files += 1
        name = os.path.basename(path)
        for r in rows:
            where = f"{name} {r.get('row_id', '?')}"
            if not (r["owner_words"] or "").strip():
                problems.append(f"{where}: owner_words is blank")
            check(f"{where} owner_words", r["owner_words"])
            check(f"{where} scope_note_sentence", r.get("scope_note_sentence", ""))
            for col in ("semantic_reason", "owner_decision"):
                for span in _spans(r.get(col, "")):
                    check(f"{where} {col}", span)
    if not checked_files:
        problems.append(f"no review file with an owner_words column in {reviews}: nothing checked")
    with open(backlog) as f:
        text = f.read()
    for para in block_quotes(text):
        check(f"{os.path.basename(backlog)} block quote", para)
    rendered_corpus = rendered_answer_corpus(answers)
    for path in sorted(glob.glob(os.path.join(decisions, "EPM-DEC-001-*.md"))):
        number = int(re.search(r"EPM-DEC-001-(\d{4})", os.path.basename(path)).group(1))
        if number < FIRST_QUOTE_CHECKED_DECISION:
            continue
        with open(path) as f:
            record = f.read()
        name = f"EPM-DEC-001-{number:04d}"
        # Raw HTML can hide or relabel any part of a record (a status, a heading, a
        # quote), so a checked record must be plain Markdown throughout.
        from markdown_it import MarkdownIt
        if any(has_html(t) for t in MarkdownIt("commonmark").enable("table").parse(record)):
            problems.append(f"{name}: raw HTML or an image in a checked decision record; write it in plain Markdown")
            continue
        # Invisible format characters (zero-width spaces, joiners, a BOM) can make two
        # headings or statuses look alike while comparing differently.
        # Checked in the raw file and in the displayed text, where entities are decoded.
        if has_invisible(record) or has_invisible("\n".join(rendered_blocks(record))):
            problems.append(f"{name}: invisible format characters in a checked decision record; remove them")
            continue
        # The status a reader sees: the Status row of the record's displayed tables.
        # A row inside an HTML comment or code block is not a table row, and any
        # pipe-table spelling is. Exactly one is required.
        statuses = displayed_status_rows(record)
        if len(statuses) != 1:
            problems.append(f"{name}: has {len(statuses)} Status rows; a record needs exactly one")
            continue
        if statuses[0][1]:
            problems.append(f"{name}: raw HTML in the Status row; write it in plain Markdown")
            continue
        if not re.fullmatch(r"(Proposed|Decided|Superseded)\b[^\u200b-\u200f\ufeff]*", statuses[0][0]):
            problems.append(f"{name}: Status {statuses[0][0]!r} is not a recognised status (Proposed, Decided or Superseded)")
            continue
        decided = _status_parts(statuses[0][0])[0] == "Decided"
        sections = recorded_words(record)
        if len(sections) > 1:
            problems.append(f"{name}: more than one \"The decision owner's recorded words\" section; cannot check it unambiguously")
            continue
        blocks, html, quoted = sections[0] if sections else ([], False, [])
        if html:
            problems.append(f"{name}: raw HTML in \"The decision owner's recorded words\"; write the section in plain Markdown")
            continue
        unpaired = [b for b in blocks if b.count('"') % 2 or b.count("“") != b.count("”")]
        for block in unpaired:
            # Quote marks pair only within a block, so an unclosed quotation would go unchecked.
            problems.append(f"{name} recorded words: a paragraph has an unpaired quote mark; close the quotation: {_flat(block)[:90]!r}")
        spans = [span for block in blocks for span in _spans(block)] + [q for q in quoted if len(q.split()) >= 3]
        if decided and not spans:
            problems.append(f"{name}: Decided, but its \"The decision owner's recorded words\" section has no quote of three or more words to check")
        for span in spans:
            if not in_corpus_as_words(span, rendered_corpus):
                problems.append(f"{name} recorded words: not in a saved answer: {span[:90]!r}")
    return problems


def cmd_quotes(args):
    problems = quote_problems()
    if args.json:
        print(json.dumps({"commit": commit(), "problems": problems}, indent=2))
    else:
        print(f"commit {commit()}: {len(problems)} quote problem(s) against {rel(ANSWERS)}")
        for p in problems:
            print(f"  {p}")
    return 1 if problems else 0


def cmd_decisions(args):
    problems = decision_problems()
    if args.json:
        print(json.dumps({"commit": commit(), "problems": problems}, indent=2))
    else:
        print(f"commit {commit()}: {len(problems)} problem(s) in {rel(DECISIONS)}")
        for p in problems:
            print(f"  {p}")
    return 1 if problems else 0


# EPM-DEC-001-0049: the repo names the decision owner by role. These are the personal name,
# the family name and the GitHub username, built from fragments so this file does not match itself.
OWNER_NAMES = re.compile("|".join(["ha" + "mid", "ade" + "sokan", "aade" + "ha" + "mid"]), re.I)


def _office_texts(where, data):
    """An Office part's raw XML, and its decoded values: each cell, shared string or paragraph
    as Office displays it, plus every element's text and every attribute value.

    Parsing decodes character references (H&#97;...), and a cell's text comes from its text
    runs (`t` elements) alone, so a name split across runs, or indented XML, is still found.
    """
    import xml.etree.ElementTree as ET
    local = lambda el: el.tag.rsplit("}", 1)[-1]
    out = [(where, data.decode("utf-8", "replace"))]
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return out
    shown = ["".join(t.text or "" for t in el.iter() if local(t) == "t")
             for el in root.iter() if local(el) in ("c", "si", "is", "p")]
    values = [v for el in root.iter() for v in [el.text or "", *el.attrib.values()] if v.strip()]
    out.append((f"{where} (displayed text)", "\n".join(shown)))
    out.append((f"{where} (decoded values)", "\n".join(values)))
    return out


def _name_texts(path, name):
    """(label, text) to scan in one file: the file itself, or each part of an Office file."""
    with open(path, "rb") as f:
        data = f.read()
    if name.lower().endswith((".xlsx", ".docx", ".pptx")):
        import zipfile
        texts = []
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for n in z.namelist():
                texts += _office_texts(f"{name}!{n}", z.read(n))
        return texts
    return [(name, data.decode("utf-8", "replace"))]


def name_problems(root=ROOT):
    """Each tracked path, and each line of a tracked file, that names the decision owner, in any case."""
    # Inherited GIT_DIR or GIT_INDEX_FILE (a hook sets them) would point git at another repository.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    names = subprocess.check_output(["git", "-C", root, "ls-files", "-z"], env=env).decode().split("\0")
    problems = []
    for name in names:
        if not name:
            continue
        if OWNER_NAMES.search(name):
            problems.append(f"{name}: the path names the decision owner")
        path = os.path.join(root, name)
        if os.path.islink(path) or not os.path.isfile(path):
            continue
        for where, text in _name_texts(path, name):
            for i, line in enumerate(text.split("\n"), 1):
                if OWNER_NAMES.search(line):
                    problems.append(f"{where}:{i}: names the decision owner")
    return problems


def cmd_names(args):
    problems = name_problems()
    if args.json:
        print(json.dumps({"commit": commit(), "problems": problems}, indent=2))
    else:
        print(f"commit {commit()}: {len(problems)} tracked line(s) name the decision owner")
        for p in problems:
            print(f"  {p}")
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="epm-facts", description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("counts", help="ledger, scoped sequences, gate, facts, Phase 1, review holds, taxonomy")
    p = sub.add_parser("row", help="where one row stands")
    p.add_argument("row_id")
    p = sub.add_parser("section", help="row IDs for one Phase 1 issue")
    p.add_argument("issue", type=int)
    p = sub.add_parser("find", help="repo-wide search, including text split across lines")
    p.add_argument("text")
    p = sub.add_parser("sweep", help="where wording the branch replaced or deleted since BASE still stands, in every tracked text file")
    p.add_argument("base")
    sub.add_parser("decisions", help="check EPM-DEC-001 records against their index (exit 1 on problems)")
    sub.add_parser("quotes", help="check text attributed to the decision owner against their saved answers (exit 1 on problems)")
    sub.add_parser("names", help="check that no tracked file names the decision owner (exit 1 on problems)")
    args = parser.parse_args(argv)
    return {"counts": cmd_counts, "row": cmd_row, "section": cmd_section, "find": cmd_find, "decisions": cmd_decisions,
            "quotes": cmd_quotes, "names": cmd_names, "sweep": cmd_sweep}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
