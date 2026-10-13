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
SHA column changes. It stops unless the taxonomy, identity map and workbook in
build/output equal their versions in the --to commit. All files are replaced
together: if one replace fails, the others are restored, so a retry starts clean.

adopt: after the workbook or the hold sets change, re-run classify, the context
pass and the mapping pipeline in a temporary copy and compare their outputs with the governed
target-dispositions-v2.csv, context-pass.csv and canonical-facts.csv. A row whose corrected
verb leaves or joins `enables`, `requires` or `assures` leaves or joins that verb's review
file (enables-review.csv and so on); the other rows keep their review notes. The REL
rows must stay the same rows. Every changed disposition or context row, and every
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
# build/output files that must equal their versions in the --to commit, so the pin
# names the commit that produced what baseline/ receives.
PROVENANCE_FILES = BASELINE_FILES + ["step3c-definition-authoring-workbook.xlsx"]
# Columns classify_v2.py computes. The governed dispositions also carry review notes
# (emission_decision, reason, review_trigger, decision_reference) that classify does not
# reproduce, so adopt takes classify's values for these columns of batch rows only.
CLASSIFIED = ["row_id", "baseline_sha", "source_slug", "source_label", "branch_domain", "verb", "raw_target",
              "disposition", "candidate_slugs", "candidate_labels", "evidence", "confidence"]


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


def git_committed(output, sha):
    """Return name -> the bytes of build/output/<name> in commit sha, or None if git has no such file."""
    def committed(name):
        rel = subprocess.run(["git", "-C", output, "ls-files", "--full-name", "--error-unmatch", name],
                             capture_output=True, text=True)
        if rel.returncode:
            return None
        shown = subprocess.run(["git", "-C", output, "show", f"{sha}:{rel.stdout.strip()}"], capture_output=True)
        return None if shown.returncode else shown.stdout
    return committed


def write_all(files):
    """Replace every (path, text) in files, or none: each is staged first, and a failed replace restores the rest."""
    originals, staged, done = {}, [], []
    try:
        for path, text in files:
            with open(path, "rb") as f:
                originals[path] = f.read()
            tmp = path + ".repin-tmp"
            with open(tmp, "w", newline="") as f:
                f.write(text)
            staged.append(tmp)
        for path, _ in files:
            os.replace(path + ".repin-tmp", path)
            done.append(path)
    except BaseException:
        for path in done:
            with open(path, "wb") as f:
                f.write(originals[path])
        raise
    finally:
        for tmp in staged:
            if os.path.isfile(tmp):
                os.remove(tmp)


def repin(step4, output, new, reason, write, today=None, committed=None):
    old = read(os.path.join(step4, "PINNED_SHA.txt")).strip()
    if new == old:
        raise SystemExit(f"already pinned to {new}")
    if not re.fullmatch(r"[0-9a-f]{40}", new):
        raise SystemExit(f"--to must be a full 40-character commit SHA, got {new!r}")
    committed = committed or git_committed(output, new)
    for name in PROVENANCE_FILES:
        with open(os.path.join(output, name), "rb") as f:
            if f.read() != committed(name):
                raise SystemExit(f"build/output/{name} differs from its version in {new[:7]}; "
                                 "commit the rebuild and pin that commit")
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
    write_all(plans + [(os.path.join(step4, "baseline", name), text) for name, text in baseline.items()]
              + [(os.path.join(step4, "PINNED_SHA.txt"), new + "\n"), (checklist, text_c), (mapping, text_m)])
    return total


def _proposals(step4, tmp):
    """Run classify, the context pass and the mapping pipeline in a copy under tmp; return their proposal paths."""
    work = os.path.join(tmp, "step4")
    shutil.copytree(step4, work, ignore=shutil.ignore_patterns("__pycache__", "proposal"))
    # Both scripts honour EPM_STEP4_DIR, so pin it to the copy: an inherited value would write elsewhere.
    env = dict(os.environ, EPM_STEP4_DIR=work)
    report = os.path.join(work, "target-report")
    # classify_v2 turns a corrected verb or target in the baseline taxonomy into the dispositions;
    # the context pass and the mapping read the new dispositions.
    subprocess.run([sys.executable, "classify_v2.py"], cwd=report, env=env, check=True, capture_output=True)
    shutil.copyfile(os.path.join(work, "proposal", "target-report", "target-dispositions-v2.csv"),
                    os.path.join(report, "target-dispositions-v2.csv"))
    subprocess.run([sys.executable, "context_pass.py"], cwd=report, env=env, check=True, capture_output=True)
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
    return (os.path.join(report, "target-dispositions-v2.csv"), os.path.join(report, "context-pass.csv"),
            os.path.join(work, "proposal", "canonical-facts.csv"), os.path.join(work, "proposal"))


def _rows(path, key):
    with open(path, newline="") as f:
        return {key(r): r for r in csv.DictReader(f)}


def _merge_dispositions(path, new_d, batch):
    """Rewrite the governed dispositions with classify's columns for batch rows; keep every review note."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fields, rows = reader.fieldnames, list(reader)
    for r in rows:
        if r["row_id"] in batch:
            r.update({c: new_d[r["row_id"]][c] for c in CLASSIFIED})
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)  # csv default CRLF, as classify_v2 writes
        writer.writeheader()
        writer.writerows(rows)


# The verb-review files the gate checks against the dispositions, each with its verb.
VERB_REVIEWS = [("enables-review.csv", "enables"), ("requires-review.csv", "requires"),
                ("assures-review.csv", "assures")]


def _sync_verb_review(path, leaving, entering, proposal):
    """Drop the rows that left the verb's population and append those that joined it.

    Every other line stays byte for byte: the governed file carries review notes the
    mapping does not reproduce.
    """
    with open(path, newline="") as f:
        lines = f.read().splitlines(keepends=True)
    kept = [ln for ln in lines if ln.split(",", 1)[0] not in leaving]
    with open(proposal, newline="") as f:
        joined = [ln for ln in f.read().splitlines(keepends=True) if ln.split(",", 1)[0] in entering]
    if kept and joined and not kept[-1].endswith(("\n", "\r")):
        kept[-1] += "\n"
    with open(path, "w", newline="") as f:
        f.writelines(kept + joined)


def _contributors(fact):
    return set(fact["row_ids"].split(";")) - {""} if fact else set()


def adopt(step4, batch, write):
    """Compare re-run outputs with the governed files; every change must belong to the batch rows."""
    tmp = tempfile.mkdtemp(prefix="phase1-batch-")
    try:
        new_disp, new_ctx, new_facts, proposal_dir = _proposals(step4, tmp)
        old_d = _rows(os.path.join(step4, "target-report", "target-dispositions-v2.csv"), lambda r: r["row_id"])
        new_d = _rows(new_disp, lambda r: r["row_id"])
        old_c = _rows(os.path.join(step4, "target-report", "context-pass.csv"), lambda r: r["row_id"])
        new_c = _rows(new_ctx, lambda r: r["row_id"])
        fact_key = lambda r: (r["subject"], r["predicate"], r["object"])  # noqa: E731
        old_f = _rows(os.path.join(step4, "canonical-facts.csv"), fact_key)
        new_f = _rows(new_facts, fact_key)
        problems = []
        # A corrected segment keeps its place, so the REL rows must be the same rows.
        if set(old_d) != set(new_d):
            problems.append("dispositions gained or lost rows: a correction moved or removed a segment")
        disp_changed = sorted(k for k in old_d if k in new_d and any(old_d[k][c] != new_d[k][c] for c in CLASSIFIED))
        problems += [f"disposition row {r} changed but is not in the batch" for r in disp_changed if r not in batch]
        # A row that now resolves by slug leaves the context pass; only batch rows may come or go.
        problems += [f"context row {r} gained or lost but is not in the batch"
                     for r in sorted(set(old_c) ^ set(new_c)) if r not in batch]
        ctx_changed = sorted(k for k in old_c if k in new_c and old_c[k] != new_c[k])
        # Outside the batch a context row may gain a note (a new back-link, say) but never change its outcome.
        problems += [f"context row {r} changed its outcome but is not in the batch"
                     for r in ctx_changed if r not in batch and old_c[r]["outcome"] != new_c[r]["outcome"]]
        # Each verb-review file lists its verb's mentions; a corrected verb moves a row in or out.
        moves = {}
        for name, verb in VERB_REVIEWS:
            listed = set(_rows(os.path.join(step4, name), lambda r: r["row_id"]))
            now = {k for k, r in new_d.items() if r["verb"] == verb}
            moves[name] = (listed - now, now - listed)
            problems += [f"{name} row {r} left or joined but is not in the batch"
                         for r in sorted((listed - now) | (now - listed)) if r not in batch]
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
        print(f"disposition rows changed: {len(disp_changed)} {disp_changed}")
        print(f"context rows changed: {len(ctx_changed)} {ctx_changed}")
        print(f"facts added: {len(added)}, removed: {len(removed)}, changed: {len(changed)}")
        for name, (leaving, entering) in moves.items():
            if leaving or entering:
                print(f"{name} rows leaving: {sorted(leaving)}, joining: {sorted(entering)}")
        for p in problems:
            print("STOP", p)
        if problems:
            return 1
        if write:
            _merge_dispositions(os.path.join(step4, "target-report", "target-dispositions-v2.csv"), new_d, batch)
            shutil.copyfile(new_ctx, os.path.join(step4, "target-report", "context-pass.csv"))
            shutil.copyfile(new_facts, os.path.join(step4, "canonical-facts.csv"))
            synced = [name for name, (leaving, entering) in moves.items() if leaving or entering]
            for name in synced:
                _sync_verb_review(os.path.join(step4, name), *moves[name], os.path.join(proposal_dir, name))
            print("wrote target-report/target-dispositions-v2.csv, target-report/context-pass.csv, canonical-facts.csv"
                  + "".join(f", {name}" for name in synced))
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
