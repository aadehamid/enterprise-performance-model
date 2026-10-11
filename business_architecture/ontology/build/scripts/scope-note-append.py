#!/usr/bin/env python3
"""Append source-author scope-note sentences to the Step 3c definition workbook.

Phase 1 source corrections (EPM-DEC-001-0025) add one sentence per answered
question to the scope note of a process on the "Review & authoring" sheet. The
input is a review CSV with `scope_note_slug` and `scope_note_sentence` columns;
rows with a blank slug add nothing. Hamid approved this as the one reusable
script for every Phase 1 batch (#205, 2026-10-11).

Rules:
- Only `approved` rows are edited, because only they reach the taxonomy.
- An unknown slug, or a row that is not `approved`, stops the run before any
  write.
- A sentence already in the scope note as a whole sentence is skipped, so a
  re-run changes nothing. Text that only contains it, inside a longer
  sentence, does not count.

Usage:
  scope-note-append.py --corrections <review.csv> [--workbook <xlsx>] [--check]
--check reports what would change and writes nothing.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

WB = Path(__file__).resolve().parents[1] / "output" / "step3c-definition-authoring-workbook.xlsx"
SHEET = "Review & authoring"


def corrections(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if rows and not {"scope_note_slug", "scope_note_sentence"} <= rows[0].keys():
        sys.exit(f"{path}: needs scope_note_slug and scope_note_sentence columns")
    out = []
    for r in rows:
        slug = (r["scope_note_slug"] or "").strip()
        sentence = " ".join((r["scope_note_sentence"] or "").split())
        if not slug:
            continue
        if not sentence:
            sys.exit(f"{path}: {slug} has a slug but no sentence")
        out.append((slug, sentence))
    return out


def has_sentence(note, sentence):
    """True when `sentence` stands in `note` as a whole sentence: at the start or
    after sentence-ending punctuation and any whitespace, and at the end or before a space."""
    return re.search(r"(?:^|(?<=[.!?])\s+)" + re.escape(sentence) + r"(?=\s|$)", note) is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corrections", required=True)
    ap.add_argument("--workbook", default=str(WB))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    from openpyxl import load_workbook

    wb = load_workbook(args.workbook)
    ws = wb[SHEET]
    idx = {c.value: i for i, c in enumerate(ws[1])}
    by_slug = {r[idx["slug"]].value: r for r in ws.iter_rows(min_row=2) if r[idx["slug"]].value}

    edits = corrections(args.corrections)
    errors = []
    for slug, _ in edits:
        if slug not in by_slug:
            errors.append(f"{slug}: not in the workbook")
        elif (by_slug[slug][idx["status"]].value or "").strip() != "approved":
            errors.append(f"{slug}: status is {by_slug[slug][idx['status']].value!r}, not 'approved'")
    if errors:
        sys.exit("refused, nothing written:\n  " + "\n  ".join(errors))

    added = skipped = 0
    for slug, sentence in edits:
        cell = by_slug[slug][idx["scope_note"]]
        note = (cell.value or "").strip()
        if has_sentence(note, sentence):
            skipped += 1
            print(f"skip {slug}: sentence already present")
            continue
        cell.value = f"{note} {sentence}" if note else sentence
        added += 1
        print(f"add  {slug}: {sentence[:70]}…")

    print(f"{added} added, {skipped} already present")
    if added and not args.check:
        wb.save(args.workbook)
        print(f"saved {args.workbook}")


if __name__ == "__main__":
    main()
