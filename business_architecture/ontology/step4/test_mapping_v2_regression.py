#!/usr/bin/env python3
"""Regression test: mapping_v2.py must never overwrite governed CSVs.

The 717-vs-457 failure (PR #167 HOLD): a stale mapping_v2.py regenerated
717 facts and overwrote the governed canonical-facts.csv, clobbering the
457-fact canonical set. This test fails if the script writes outside
proposal/ or if proposal output diverges from governed truth.
"""
import csv
import hashlib
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GOVERNED = ["canonical-facts.csv", "contradictions.csv", "enables-review.csv"]
EXPECTED_FACTS = 457


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    failures = []

    # Snapshot governed files before running the script
    before = {f: sha256(os.path.join(BASE, f)) for f in GOVERNED}

    # Run the script
    result = subprocess.run(
        [sys.executable, os.path.join(BASE, "mapping_v2.py")],
        capture_output=True, text=True, cwd=BASE)
    if result.returncode != 0:
        failures.append(f"mapping_v2.py exited {result.returncode}: {result.stderr[:500]}")

    # 1. Governed files must be byte-identical (script writes to proposal/ only)
    for f in GOVERNED:
        after = sha256(os.path.join(BASE, f))
        if after != before[f]:
            failures.append(
                f"GOVERNED FILE OVERWRITTEN: {f} changed after mapping_v2.py run "
                f"({before[f][:8]} -> {after[:8]}). Script must write to proposal/ only.")

    # 2. Proposal facts must match governed canonical facts byte-identically
    prop = os.path.join(BASE, "proposal", "canonical-facts.csv")
    gov = os.path.join(BASE, "canonical-facts.csv")
    if not os.path.exists(prop):
        failures.append("proposal/canonical-facts.csv not generated")
    else:
        with open(prop) as f:
            prop_rows = list(csv.DictReader(f))
        with open(gov) as f:
            gov_rows = list(csv.DictReader(f))
        if len(prop_rows) != EXPECTED_FACTS:
            failures.append(
                f"proposal facts = {len(prop_rows)}, expected {EXPECTED_FACTS} "
                f"(717-vs-457 regression)")
        if len(prop_rows) != len(gov_rows):
            failures.append(
                f"proposal ({len(prop_rows)}) != governed ({len(gov_rows)}) fact count")
        if sha256(prop) != sha256(gov):
            failures.append("proposal/canonical-facts.csv differs from governed canonical-facts.csv")

    if failures:
        print("FAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS: governed files untouched, proposal = {EXPECTED_FACTS} facts, byte-identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
