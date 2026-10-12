#!/usr/bin/env python3
"""Phase 1 batch steps that are the same for every batch, as tested commands.

    python3 phase1_batch.py repin --to <commit> --reason "<batch>" [--write]
    python3 phase1_batch.py adopt --rows REL-00001,REL-00002 [--write]

repin: point Step 4 at the commit that carries the batch's workbook and
taxonomy. Copies the rebuilt taxonomy and identity map into baseline/, writes
PINNED_SHA.txt, re-stamps baseline_sha in the seven SHA-stamped CSVs, and puts
a new pin statement above the old one in the release checklist and the mapping
document, keeping the old one word for word. It reads every input before it
writes, and stops if any CSV row is not stamped with the old pin, so only the
SHA column changes.

adopt: after the hold sets change, re-run the context pass and the mapping
pipeline in a temporary copy and compare their outputs with the governed
context-pass.csv and canonical-facts.csv. Every changed context row, and every
row a fact gains or loses, must be a batch row; anything else stops the run.
With --write, the governed files take the new outputs.

Without --write, both commands only report. Standard library only.
"""
import argparse
import csv
import datetime
import io
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import contextlib

STEP4 = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(os.path.dirname(STEP4), "build", "output")
# The evidence gate's SHA-stamped files (evidence-gate.py section 1).
SHA_FILES = ["target-report/target-dispositions-v2.csv", "target-report/context-pass.csv",
             "target-report/sibling-review-package-v2.csv", "label-report/label-dispositions-v1.2.csv",
             "requires-review.csv", "assures-review.csv", "enables-review.csv"]
CHECKLIST_PIN = re.compile(r"^- \*\*PINNED_SHA:\*\* .*$", re.M)
MAPPING_PIN = re.compile(r"^\*\*Baseline:\*\* .*$", re.M)
BASELINE_FILES = ["step3-taxonomy.ttl", "step2-identity-map.json"]


def read(path):
    with open(path) as f:
        return f.read()


def restamp(step4, old, new):
    """Rewrite baseline_sha from old to new in the seven CSVs; return the row count. Stops on any other value."""
    plans, total = [], 0
    for name in SHA_FILES:
        path = os.path.join(step4, name)
        with open(path, newline="") as f:
            raw = f.read()
        rows = list(csv.reader(io.StringIO(raw)))
        col = rows[0].index("baseline_sha")
        stray = [r[col] for r in rows[1:] if r and r[col] != old]
        if stray:
            raise SystemExit(f"{name}: {len(stray)} rows are not stamped {old}; refusing to re-pin")
        count = sum(1 for r in rows[1:] if r)
        if raw.count(old) != count:
            raise SystemExit(f"{name}: the old pin appears outside the baseline_sha column; refusing to re-pin")
        plans.append((path, raw.replace(old, new)))
        total += count
    return plans, total


def repin(step4, output, new, reason, write, today=None):
    old = read(os.path.join(step4, "PINNED_SHA.txt")).strip()
    if new == old:
        raise SystemExit(f"already pinned to {new}")
    if not re.fullmatch(r"[0-9a-f]{40}", new):
        raise SystemExit(f"--to must be a full 40-character commit SHA, got {new!r}")
    # Read every input before any write, so a missing file stops the run with nothing changed.
    baseline = {name: read(os.path.join(output, name)) for name in BASELINE_FILES}
    plans, total = restamp(step4, old, new)
    day = today or datetime.date.today().isoformat()
    checklist = os.path.join(step4, "release-checklist.md")
    mapping = os.path.join(step4, "verb-predicate-mapping-v2.md")
    text_c, text_m = read(checklist), read(mapping)
    pin_c, pin_m = CHECKLIST_PIN.findall(text_c), MAPPING_PIN.findall(text_m)
    if len(pin_c) != 1 or len(pin_m) != 1:
        raise SystemExit("expected exactly one pin statement in release-checklist.md and verb-predicate-mapping-v2.md")
    # The new statement goes first; the previous one stays, word for word, as history beneath it.
    previous_c = pin_c[0].replace("- **PINNED_SHA:** ", "", 1)
    previous_m = pin_m[0].replace("**Baseline:** ", "", 1)
    text_c = CHECKLIST_PIN.sub(lambda _: (
        f"- **PINNED_SHA:** `{new}` (re-pinned {day} for {reason}, from `{old}`; all 7 SHA-stamped CSVs "
        f"re-stamped, {total:,} rows; the re-pin itself changes only the SHA column). "
        "Promotion was approved against `6a155bc2`.\n"
        f"  - Previous pin: {previous_c}"), text_c)
    text_m = MAPPING_PIN.sub(lambda _: (
        f"**Baseline:** `{new}` (re-pinned {day} for {reason}; was `{old}`).\n\n"
        f"*Previous baseline:* {previous_m}"), text_m)
    print(f"re-pin {old[:7]} -> {new[:7]}: {total:,} rows in {len(plans)} CSVs; taxonomy and identity map from build/output")
    if not write:
        return total
    for path, raw in plans:
        with open(path, "w", newline="") as f:
            f.write(raw)
    for name, text in baseline.items():
        with open(os.path.join(step4, "baseline", name), "w") as f:
            f.write(text)
    with open(os.path.join(step4, "PINNED_SHA.txt"), "w") as f:
        f.write(new + "\n")
    with open(checklist, "w") as f:
        f.write(text_c)
    with open(mapping, "w") as f:
        f.write(text_m)
    return total


def _proposals(step4, tmp):
    """Run the context pass and mapping pipeline in a copy under tmp; return their proposal file paths."""
    work = os.path.join(tmp, "step4")
    shutil.copytree(step4, work, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
    # context_pass.py honours EPM_STEP4_DIR, so pin it to the copy: an inherited value would write elsewhere.
    env = dict(os.environ, EPM_STEP4_DIR=work)
    subprocess.run([sys.executable, "context_pass.py"], cwd=os.path.join(work, "target-report"),
                   env=env, check=True, capture_output=True)
    # mapping_v2 reads the governed context-pass.csv, so give it the new one first.
    shutil.copyfile(os.path.join(work, "proposal", "target-report", "context-pass.csv"),
                    os.path.join(work, "target-report", "context-pass.csv"))
    cwd = os.getcwd()
    os.chdir(work)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(os.path.join(work, "mapping_v2.py"), run_name="__main__")
    finally:
        os.chdir(cwd)
    return os.path.join(work, "target-report", "context-pass.csv"), os.path.join(work, "proposal", "canonical-facts.csv")


def _rows(path, key):
    with open(path, newline="") as f:
        return {key(r): r for r in csv.DictReader(f)}


def _contributors(fact):
    return set(fact["row_ids"].split(";")) - {""} if fact else set()


def adopt(step4, batch, write):
    """Compare re-run outputs with the governed files; every change must belong to the batch rows."""
    tmp = tempfile.mkdtemp(prefix="phase1-batch-")
    try:
        new_ctx, new_facts = _proposals(step4, tmp)
        old_c = _rows(os.path.join(step4, "target-report", "context-pass.csv"), lambda r: r["row_id"])
        new_c = _rows(new_ctx, lambda r: r["row_id"])
        fact_key = lambda r: (r["subject"], r["predicate"], r["object"])  # noqa: E731
        old_f = _rows(os.path.join(step4, "canonical-facts.csv"), fact_key)
        new_f = _rows(new_facts, fact_key)
        problems = []
        if set(old_c) != set(new_c):
            problems.append("context pass gained or lost rows")
        ctx_changed = sorted(k for k in old_c if k in new_c and old_c[k] != new_c[k])
        problems += [f"context row {r} changed but is not in the batch" for r in ctx_changed if r not in batch]
        added, removed = sorted(set(new_f) - set(old_f)), sorted(set(old_f) - set(new_f))
        changed = sorted(k for k in set(old_f) & set(new_f) if old_f[k] != new_f[k])
        for label, keys in (("added", added), ("removed", removed), ("changed", changed)):
            for k in keys:
                before, after = _contributors(old_f.get(k)), _contributors(new_f.get(k))
                # Every contributor gained or lost must be a batch row; unchanged contributors may stay.
                outside = sorted((before ^ after) - batch)
                if outside:
                    problems.append(f"fact {' '.join(k)} {label}: rows outside the batch gained or lost {outside}")
                elif before == after and not (after & batch):
                    problems.append(f"fact {' '.join(k)} {label} but carries no batch row")
        print(f"context rows changed: {len(ctx_changed)} {ctx_changed}")
        print(f"facts added: {len(added)}, removed: {len(removed)}, changed: {len(changed)}")
        for p in problems:
            print("STOP", p)
        if problems:
            return 1
        if write:
            shutil.copyfile(new_ctx, os.path.join(step4, "target-report", "context-pass.csv"))
            shutil.copyfile(new_facts, os.path.join(step4, "canonical-facts.csv"))
            print("wrote target-report/context-pass.csv and canonical-facts.csv")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("repin")
    p.add_argument("--to", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("adopt")
    p.add_argument("--rows", required=True, help="comma-separated batch row IDs")
    p.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "repin":
        repin(STEP4, OUTPUT, args.to, args.reason, args.write)
        return 0
    return adopt(STEP4, {r.strip() for r in args.rows.split(",") if r.strip()}, args.write)


if __name__ == "__main__":
    sys.exit(main())
