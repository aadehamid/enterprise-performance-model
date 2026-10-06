#!/usr/bin/env python3
"""epm-facts: the figures and row facts that agents quote, computed from source.

One place to get the numbers right, so no agent writes its own counting script.
Every answer names the files it read and the commit it read them at.

Usage (from anywhere in the repo):

    python3 scripts/epm_facts.py counts            # ledger, gate, facts, Phase 1, reviews, taxonomy
    python3 scripts/epm_facts.py row REL-00436     # where one row stands
    python3 scripts/epm_facts.py section 201       # row IDs for one Phase 1 issue
    python3 scripts/epm_facts.py find "0024"       # repo-wide search, including text split across lines
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
- A review hold is a non-blank `Hamid_decision` cell that records a hold, in
  any wording ("HOLD ...", "Held for source correction", "Carry forward
  (remains held)"). Other columns are ignored (AGENTS.md, check 1).

Standard library only, except taxonomy triple counts, which use rdflib when it
is installed (`uv run --with rdflib python3 scripts/epm_facts.py counts`).
"""
import argparse
import collections
import contextlib
import csv
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
        cwd = os.getcwd()
        os.chdir(work)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mapping = runpy.run_path(os.path.join(work, "mapping_v2.py"), run_name="__main__")
            gate_out = io.StringIO()
            gate_ok = True
            try:
                with contextlib.redirect_stdout(gate_out):
                    gate = runpy.run_path(os.path.join(work, "evidence-gate.py"), run_name="__main__")
            except SystemExit as e:
                gate_ok = e.code in (0, None)
                gate = {}
            gate_text = gate_out.getvalue()
        finally:
            os.chdir(cwd)
        return mapping, gate, gate_ok and "GATE GREEN" in gate_text, gate_text
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def ledger(mapping):
    v2 = mapping["v2"]
    emitting = set(mapping["emitting_ids"])
    disp = collections.Counter(r["disposition"] for r in v2)
    held = {r["row_id"] for r in v2 if r["row_id"] not in emitting and r["disposition"] not in NOT_HELD}
    return {
        "mentions": len(v2),
        "emitting": len(emitting),
        "held": len(held),
        "deferred": disp["AmbiguousDeferred"],
        "external_governance": disp["ExternalGovernanceReference"],
        "structured_flow": disp["StructuredFlowValue"],
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
    """Per review file: rows whose Hamid_decision records a hold; and per row, its decisions."""
    per_file, per_row = {}, collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(REVIEWS, "*.csv"))):
        try:
            with open(path, newline="") as f:
                reader = list(csv.DictReader(f))
        except (csv.Error, UnicodeDecodeError):
            continue
        if not reader or "Hamid_decision" not in reader[0]:
            continue
        held = []
        for r in reader:
            decision = (r.get("Hamid_decision") or "").strip()
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
    mapping, gate, gate_green, _ = run_pipeline()
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
        "conservation": led["emitting"] + led["held"] + led["deferred"] + led["external_governance"] + led["structured_flow"],
        "canonical_facts_file": len(facts),
        "evidence_gate": {
            "green": gate_green,
            "promoted": gate.get("promoted"),
            "held": gate.get("held_ctx"),
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
        "taxonomy": taxonomy(),
        "sources": [rel(os.path.join(STEP4, "mapping_v2.py")), rel(os.path.join(STEP4, "evidence-gate.py")),
                    rel(FACTS), rel(BACKLOG), rel(REVIEWS) + "/*.csv", rel(TAXONOMY)],
    }
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    led = out["ledger"]
    print(f"commit {out['commit']}")
    print(f"ledger: {led['emitting']} emitting / {led['held']} held / {led['deferred']} deferred / "
          f"{led['external_governance']} external governance / {led['structured_flow']} structured flow "
          f"= {out['conservation']} (of {led['mentions']} mentions)")
    print(f"canonical facts: {out['canonical_facts_file']} in canonical-facts.csv; pipeline builds {led['canonical_facts_pipeline']}")
    eg = out["evidence_gate"]
    print(f"evidence gate: {'GREEN' if eg['green'] else 'NOT GREEN'}; promoted {eg['promoted']} / held {eg['held']}")
    ph = out["phase1"]
    print(f"Phase 1 (EPM-DEC-001-0025): {ph['rows']} rows, {ph['held']} held; not held: {', '.join(ph['not_held']) or 'none'}")
    print("  by issue: " + ", ".join(f"#{k} {v}" for k, v in ph["by_issue"].items()))
    print(f"  held outside Phase 1: {ph['held_outside']}: " + ", ".join(f"{k} {v}" for k, v in ph["held_outside_by_reason"].items()))
    print("review holds (Hamid_decision) by file:")
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
    rec = next((r for r in mapping["v2"] if r["row_id"] == row_id), None)
    if rec is None:
        print(f"{row_id}: not in target-dispositions-v2.csv", file=sys.stderr)
        return 1
    facts = [f for f in stored_facts() if row_id in f["row_ids"].split(";")]
    p1 = phase1_rows()
    _, per_row = review_holds()
    status = "emitting" if row_id in emitting else ("held" if row_id in held else rec["disposition"])
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


def cmd_find(args):
    """Search tracked text files; also match text split across lines."""
    files = subprocess.check_output(["git", "-C", ROOT, "ls-files"], text=True).split("\n")
    needle = args.text
    flat_needle = re.sub(r"\s+", " ", needle).strip().lower()
    hits = []
    for name in files:
        if not name or not name.endswith((".md", ".csv", ".py", ".ttl", ".json", ".txt", ".yaml", ".yml", ".html")):
            continue
        path = os.path.join(ROOT, name)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
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
    if args.json:
        print(json.dumps({"commit": commit(), "text": needle, "hits": [dict(zip(("file", "line", "kind", "text"), h)) for h in hits]}, indent=2))
        return 0
    print(f"commit {commit()}: {len(hits)} hits for {needle!r}")
    for name, i, kind, line in hits:
        print(f"{name}:{i}: [{kind}] {line[:200]}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="epm-facts", description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("counts", help="ledger, gate, facts, Phase 1, review holds, taxonomy")
    p = sub.add_parser("row", help="where one row stands")
    p.add_argument("row_id")
    p = sub.add_parser("section", help="row IDs for one Phase 1 issue")
    p.add_argument("issue", type=int)
    p = sub.add_parser("find", help="repo-wide search, including text split across lines")
    p.add_argument("text")
    args = parser.parse_args(argv)
    return {"counts": cmd_counts, "row": cmd_row, "section": cmd_section, "find": cmd_find}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
