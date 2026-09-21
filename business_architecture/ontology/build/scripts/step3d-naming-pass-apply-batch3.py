#!/usr/bin/env python3
"""Step 3d naming pass - scope-ambiguity Batch 3 (E+F, 12 renames).

Approved by Hamid 2026-09-21 on the independent reviewer's recommendation
(approve as proposed; CM-1-3-1-6 capability-versus-process stays a separate
modeling follow-up; preserve the Finance bad-debt authority boundary, the
receipt-recording vs settlement boundary, the reconciliation vs settlement
distinction, and the administered-stream vs receivables-collection
distinction).

Treatment (same discipline as Batches 1 and 2, PRs #91/#92):
  - prefLabel <- new label; the old label is retained as skos:altLabel
    (all 12 legacy labels verified uniquely identifiable, no prefLabel
    collision with another concept).
  - identity map: name <- new, prior_name <- old,
    scoped_historical_alias stays null, name_change_note recorded.
  - related_concepts "predicate: Old" references become
    "predicate: New (CM-slug)" (slug annotation, Batch 1 convention).
  - prose columns (definition/scope/in/out/key inputs/outputs/open
    questions/terminology notes) and breadcrumbs: plain old -> new.
  - execution record appended to each renamed row's terminology_notes
    AFTER the global replacements, so the record's own old-label
    mentions survive verbatim.

Guard words: two new labels contain their old label as a substring
("Marketing Insight and Metrics Stewardship" contains "Insight and
Metrics"; "Determine Bad Debt Allowance" contains "Bad Debt Allowance").
Those occurrences appear in the two self rows' terminology_notes and
must not be double-renamed, so prose/rc/breadcrumb replacements use a
negative lookbehind for the guard word.

One-shot migration script. Every replacement asserts its expected count,
so a stale workbook fails loudly instead of silently under-applying.
Run from the repo root:

    python3 build/scripts/step3d-naming-pass-apply-batch3.py

Edits build/output/step3c-definition-authoring-workbook.xlsx,
build/output/step2-identity-map.json, and step3c-naming-pass-queue.md
in place.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WB = ROOT / "business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx"
SHEET = "Review & authoring"
IDENTITY_MAP = ROOT / "business_architecture/ontology/build/output/step2-identity-map.json"
QUEUE = ROOT / "business_architecture/ontology/step3c-naming-pass-queue.md"

NEW = {
    "CM-1-3-1-6": "Marketing Insight and Metrics Stewardship",
    "CM-1-3-8-1-2": "Perform Self-Billing Accounting",
    "CM-1-3-8-1-5": "Manage Invoice Exceptions, Reversals, and Rebilling",
    "CM-1-3-8-2-1": "Record Customer Receipts and Payment Notifications",
    "CM-1-3-8-2-4": "Manage Unapplied Receipts and Exceptions",
    "CM-1-3-8-2-5": "Perform Cash, Acquirer, and Receivables Reconciliations",
    "CM-1-3-8-3": "Manage Receivables Resolution",
    "CM-1-3-8-3-1": "Manage Receivables Disputes",
    "CM-1-3-8-3-2": "Manage Receivables Collections",
    "CM-1-3-8-3-3": "Determine Bad Debt Allowance",
    "CM-1-3-8-3-4": "Develop Root-Cause Analyses and Action Plans",
    "CM-1-3-8-4-7": "Administer Royalty, Brand Fee, and Contribution Streams",
}
OLD = {
    "CM-1-3-1-6": "Insight and Metrics",
    "CM-1-3-8-1-2": "Perform Accounting For Self-billing",
    "CM-1-3-8-1-5": "Create Exception & Reverse Invoice",
    "CM-1-3-8-2-1": "Receive Cash Receipts / Payment",
    "CM-1-3-8-2-4": "Manage Unapplied Receipts / Exceptions",
    "CM-1-3-8-2-5": "Perform Reconciliations & Settlements",
    "CM-1-3-8-3": "Manage Collection and Disputes",
    "CM-1-3-8-3-1": "Dispute Management",
    "CM-1-3-8-3-2": "Collection Management",
    "CM-1-3-8-3-3": "Bad Debt Allowance",
    "CM-1-3-8-3-4": "Develop Root Cause Analysis/Action Plan",
    "CM-1-3-8-4-7": "Manage Collection of Royalty and Fees",
}
# Guard words: new label contains old label; occurrences of the new label
# (in the self rows' terminology_notes) must not be re-replaced.
GUARD = {
    "CM-1-3-1-6": "Marketing ",
    "CM-1-3-8-3-3": "Determine ",
}

PROSE_COLS = (
    "definition", "scope_note", "in_scope", "out_of_scope",
    "key_inputs", "primary_output", "open_questions", "terminology_notes",
)

# (slug, kind, expected_hits) — kinds: "rc" (related_concepts, gets slug
# annotation), "prose" (plain replace across PROSE_COLS), "bc" (breadcrumb).
PLAN = [
    ("CM-1-3-1-6", "rc", 23), ("CM-1-3-1-6", "prose", 11), ("CM-1-3-1-6", "bc", 1),
    ("CM-1-3-8-1-2", "rc", 1), ("CM-1-3-8-1-2", "bc", 1),
    ("CM-1-3-8-1-5", "rc", 1), ("CM-1-3-8-1-5", "bc", 1),
    ("CM-1-3-8-2-1", "rc", 2), ("CM-1-3-8-2-1", "bc", 1),
    ("CM-1-3-8-2-4", "rc", 2), ("CM-1-3-8-2-4", "bc", 1),
    ("CM-1-3-8-2-5", "rc", 2), ("CM-1-3-8-2-5", "prose", 1), ("CM-1-3-8-2-5", "bc", 1),
    ("CM-1-3-8-3", "rc", 3), ("CM-1-3-8-3", "prose", 5), ("CM-1-3-8-3", "bc", 5),
    ("CM-1-3-8-3-1", "rc", 4), ("CM-1-3-8-3-1", "prose", 4), ("CM-1-3-8-3-1", "bc", 1),
    ("CM-1-3-8-3-2", "rc", 5), ("CM-1-3-8-3-2", "prose", 3), ("CM-1-3-8-3-2", "bc", 1),
    ("CM-1-3-8-3-3", "rc", 4), ("CM-1-3-8-3-3", "prose", 5), ("CM-1-3-8-3-3", "bc", 1),
    ("CM-1-3-8-3-4", "rc", 1), ("CM-1-3-8-3-4", "bc", 1),
    ("CM-1-3-8-4-7", "rc", 2), ("CM-1-3-8-4-7", "prose", 1), ("CM-1-3-8-4-7", "bc", 1),
]

EXEC_NOTE_TMPL = (
    "Step 3d naming pass \u2014 scope-ambiguity Batch 3 (E+F, 2026-09-21): "
    "renamed from '{old}' to '{new}'. Prior label retained as altLabel."
)


def guarded(slug: str, esc: str) -> str:
    """Negative lookbehind for the guard word when one exists."""
    g = GUARD.get(slug)
    return (f"(?<!{re.escape(g)})" if g else "") + esc


def main() -> int:
    from openpyxl import load_workbook

    wb = load_workbook(WB)
    ws = wb[SHEET]
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    by_slug = {}
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        if s:
            by_slug[s] = r

    # 1. the 12 renames (name/alt swap; terminology notes later)
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        old_name = row[idx["name"]].value
        assert old_name == OLD[slug], f"{slug}: name {old_name!r} != expected {OLD[slug]!r}"
        old_alt = row[idx["alt_labels"]].value or ""
        assert old_alt == NEW[slug], f"{slug}: alt {old_alt!r} != expected new label {NEW[slug]!r}"
        row[idx["name"]].value = new_name
        row[idx["alt_labels"]].value = OLD[slug]
        print(f"renamed {slug}: {OLD[slug]!r} -> {new_name!r}")

    # 2. global replacements with asserted counts
    for slug, kind, expected in PLAN:
        old, new = OLD[slug], NEW[slug]
        pat = guarded(slug, re.escape(old))
        total = 0
        if kind == "rc":
            rx = re.compile(r"([a-z][a-z-]*): " + pat + r"(?= \||$)")
            repl = r"\1: " + new + f" ({slug})"
            cols = [idx["related_concepts"]]
        elif kind == "prose":
            rx = re.compile(pat)
            repl = new
            cols = [idx[c] for c in PROSE_COLS]
        else:  # breadcrumb
            rx = re.compile(pat)
            repl = new
            cols = [idx["breadcrumb"]]
        for r in ws.iter_rows(min_row=2):
            for ci in cols:
                v = r[ci].value
                if not v:
                    continue
                new_v, n = rx.subn(repl, v)
                if n:
                    r[ci].value = new_v
                    total += n
        assert total == expected, f"{slug}/{kind}: got {total}, expected {expected}"
        print(f"global {slug}/{kind}: {total} (expected {expected}) OK")

    # 3. execution records (after globals so old-label mentions survive)
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        note = EXEC_NOTE_TMPL.format(old=OLD[slug], new=new_name)
        cur = row[idx["terminology_notes"]].value or ""
        row[idx["terminology_notes"]].value = (cur + " " + note).strip() if cur else note

    # 4. final sweep: no stale references may remain outside the 12
    # renamed rows' own terminology_notes (execution records legitimately
    # mention the old labels), name, and alt_labels (retained aliases).
    stale = []
    check_cols = [idx[c] for c in PROSE_COLS] + [idx["related_concepts"], idx["breadcrumb"]]
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        for ci in check_cols:
            if s in NEW and ci == idx["terminology_notes"]:
                continue
            v = r[ci].value or ""
            for slug, old in OLD.items():
                if re.search(guarded(slug, re.escape(old)), v):
                    stale.append((s, headers[ci], old))
    assert not stale, f"stale references remain: {stale[:10]}"
    print("final sweep: no stale references outside the 12 renamed rows' own notes")

    wb.save(WB)
    print(f"saved {WB}")

    # 5. identity map overlays
    entries = json.loads(IDENTITY_MAP.read_text(encoding="utf-8"))
    by = {e["slug"]: e for e in entries}
    for slug, new_name in NEW.items():
        e = by[slug]
        assert e["name"] == OLD[slug], f"identity map {slug}: {e['name']!r} != {OLD[slug]!r}"
        assert e.get("prior_name") in (None, ""), f"identity map {slug} already has prior_name"
        e["name"] = new_name
        e["prior_name"] = OLD[slug]
        e["scoped_historical_alias"] = None
        e["name_change_note"] = (
            "Step 3d naming pass \u2014 scope-ambiguity Batch 3 (E+F, 2026-09-21): "
            f"renamed '{OLD[slug]}' -> '{new_name}' (Hamid approval 2026-09-21, "
            "independent reviewer recommendation: approve as proposed). Prior "
            "label retained as skos:altLabel; no identifier, hierarchy, or "
            "definition change."
        )
    IDENTITY_MAP.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print("identity map: 12 overlays updated")

    # 6. naming queue: mark the 12 E+F rows EXECUTED
    text = QUEUE.read_text(encoding="utf-8")
    lines = text.split("\n")
    marked = 0
    for i, line in enumerate(lines):
        for slug, new_name in NEW.items():
            if line.startswith(f"| `{slug}` |") and "**EXECUTED" not in line:
                assert line.rstrip().endswith("|"), f"queue row has no trailing pipe: {line[:60]}"
                lines[i] = line.rstrip()[:-1] + (
                    f"  **EXECUTED 2026-09-21** (Step 3d naming pass, scope-ambiguity "
                    f"Batch 3 E+F: renamed to '{new_name}'; prior label retained as "
                    f"altLabel; see naming PR). |"
                )
                marked += 1
                break
    assert marked == 12, f"queue rows marked: {marked}, expected 12"
    text = "\n".join(lines)
    old_hdr = "## Scope ambiguity (33 \u2014 21 executed 2026-09-21, 12 remaining)"
    new_hdr = "## Scope ambiguity (33 \u2014 33 executed 2026-09-21, 0 remaining)"
    assert old_hdr in text, "queue scope-ambiguity header not in expected form"
    text = text.replace(old_hdr, new_hdr)
    old_status = ("and 11 scope-ambiguity entries executed 2026-09-21 (Step 3d naming pass "
                  "Batch 2 D, Hamid approval 2026-09-21). The remaining 57 queue entries "
                  "are still queued for the consolidated naming pass.")
    new_status = ("and 11 scope-ambiguity entries executed 2026-09-21 (Step 3d naming pass "
                  "Batch 2 D, Hamid approval 2026-09-21) and 12 scope-ambiguity entries "
                  "executed 2026-09-21 (Step 3d naming pass Batch 3 E+F, Hamid approval "
                  "2026-09-21). The remaining 45 queue entries are still queued for the "
                  "consolidated naming pass.")
    assert old_status in text, "queue execution-status line not in expected form"
    text = text.replace(old_status, new_status)
    QUEUE.write_text(text, encoding="utf-8")
    print("naming queue: 12 E+F rows marked EXECUTED")

    return 0


if __name__ == "__main__":
    sys.exit(main())
