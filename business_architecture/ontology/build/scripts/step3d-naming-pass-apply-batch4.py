#!/usr/bin/env python3
"""Step 3d naming pass - directionality-missing Batch 4 (11 renames).

Approved by Hamid 2026-09-21 (explicit go-ahead in chat).

Two groups:
  A. Claims lifecycle (7 rows, CM-1-2-4-4-2..8): plain "Claim" labels read
     as one-sided; the lifecycle is two-directional (outbound claims we
     raise, inbound claims raised against us). New labels taken verbatim
     from the queue's Q3 reading.
  B. Consumer value-proposition cluster (4 children of CM-1-3-2-3): the
     template's B2B "Customer"/"CVP" wording is reused under the Consumer
     cluster. Consumer-directional labels from the workbook's queued
     alt_labels (the queue file's note for this row is truncated
     mid-sentence; the workbook carries the full queued labels).
     NOTE: executed label for CM-1-3-2-3-4 is "Develop and Update Consumer
     Value Proposition Strategy" (workbook queued value), not the
     chat-proposed "Develop/Update ..." — flagged for Hamid's review.

B2B-cluster protection: the four old consumer labels are also the live
prefLabels of the B2B siblings CM-1-3-2-2-1..4 (the pre-existing duplicate
prefLabel pairs). All global replacements for the 4 consumer slugs are
scoped to rows CM-1-3-2-3* only; the CM-1-3-2-2* B2B cluster (breadcrumbs,
related_concepts, terminology notes) is left untouched. This resolves the
4 duplicate pairs on the consumer side; the B2B side keeps its labels.

Treatment (same discipline as Batches 1-3):
  - prefLabel <- new label; the old label is retained as skos:altLabel.
  - identity map: name <- new, prior_name <- old,
    scoped_historical_alias stays null, name_change_note recorded.
  - related_concepts "predicate: Old" references become
    "predicate: New (CM-slug)" (slug annotation, Batch 1 convention).
  - prose columns and breadcrumbs: plain old -> new.
  - execution record appended to each renamed row's terminology_notes
    AFTER the global replacements, so the record's own old-label
    mentions survive verbatim.

No guard words needed: no new label contains its old label as a substring.

One-shot migration script. Every replacement asserts its expected count,
so a stale workbook fails loudly instead of silently under-applying.
Run from the repo root:

    python3 build/scripts/step3d-naming-pass-apply-batch4.py

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
    # A. claims lifecycle (queued labels verbatim)
    "CM-1-2-4-4-2": "Create Outbound Delay Compensation Claim",
    "CM-1-2-4-4-3": "Receive Inbound Delay Compensation Claim",
    "CM-1-2-4-4-4": "Assess Inbound Claim",
    "CM-1-2-4-4-5": "Negotiate Outbound Claim",
    "CM-1-2-4-4-6": "Validate and Negotiate Inbound Claim",
    "CM-1-2-4-4-7": "Invoice Agreed Outbound Claim",
    "CM-1-2-4-4-8": "Process Invoice for Agreed Inbound Claim",
    # B. consumer value-proposition cluster (workbook queued labels verbatim)
    "CM-1-3-2-3-1": "Test Consumer Value Proposition",
    "CM-1-3-2-3-2": "Formulate and Evaluate Consumer Value Proposition Alternatives",
    "CM-1-3-2-3-3": "Establish Consumer Value Proposition Principles and Objectives",
    "CM-1-3-2-3-4": "Develop and Update Consumer Value Proposition Strategy",
}
OLD = {
    "CM-1-2-4-4-2": "Create Claim",
    "CM-1-2-4-4-3": "Receive Demurrage Claim",
    "CM-1-2-4-4-4": "Assess Claim",
    "CM-1-2-4-4-5": "Communicate and Negotiate Claim",
    "CM-1-2-4-4-6": "Validate and Negotiate Claim",
    "CM-1-2-4-4-7": "Send Claim Invoice",
    "CM-1-2-4-4-8": "Receive Claim Invoice",
    "CM-1-3-2-3-1": "Test Customer value proposition",
    "CM-1-3-2-3-2": "Formulate and Evaluate Strategic Operating Alternatives (CVP)",
    "CM-1-3-2-3-3": "Establish CVP principles and objectives",
    "CM-1-3-2-3-4": "Develop/Update Strategy (CVP)",
}

CONSUMER_SLUGS = {"CM-1-3-2-3-1", "CM-1-3-2-3-2", "CM-1-3-2-3-3", "CM-1-3-2-3-4"}

PROSE_COLS = (
    "definition", "scope_note", "in_scope", "out_of_scope",
    "key_inputs", "primary_output", "open_questions", "terminology_notes",
)

# (slug, kind, scope, expected_hits)
# kinds: "rc" (related_concepts, gets slug annotation), "prose" (plain
# replace across PROSE_COLS), "bc" (breadcrumb).
# scope: "global" or "consumer" (rows CM-1-3-2-3* only — protects the
# B2B siblings CM-1-3-2-2* that share the old labels).
PLAN = [
    ("CM-1-2-4-4-2", "rc", "global", 2), ("CM-1-2-4-4-2", "bc", "global", 1),
    ("CM-1-2-4-4-3", "rc", "global", 1), ("CM-1-2-4-4-3", "bc", "global", 1),
    ("CM-1-2-4-4-4", "rc", "global", 2), ("CM-1-2-4-4-4", "prose", "global", 1),
    ("CM-1-2-4-4-4", "bc", "global", 1),
    ("CM-1-2-4-4-5", "rc", "global", 2), ("CM-1-2-4-4-5", "bc", "global", 1),
    ("CM-1-2-4-4-6", "rc", "global", 2), ("CM-1-2-4-4-6", "bc", "global", 1),
    ("CM-1-2-4-4-7", "rc", "global", 1), ("CM-1-2-4-4-7", "bc", "global", 1),
    ("CM-1-2-4-4-8", "rc", "global", 1), ("CM-1-2-4-4-8", "bc", "global", 1),
    ("CM-1-3-2-3-1", "rc", "consumer", 3), ("CM-1-3-2-3-1", "prose", "consumer", 1),
    ("CM-1-3-2-3-1", "bc", "consumer", 1),
    ("CM-1-3-2-3-2", "rc", "consumer", 2), ("CM-1-3-2-3-2", "prose", "consumer", 1),
    ("CM-1-3-2-3-2", "bc", "consumer", 1),
    ("CM-1-3-2-3-3", "rc", "consumer", 1), ("CM-1-3-2-3-3", "prose", "consumer", 1),
    ("CM-1-3-2-3-3", "bc", "consumer", 1),
    ("CM-1-3-2-3-4", "rc", "consumer", 1), ("CM-1-3-2-3-4", "prose", "consumer", 1),
    ("CM-1-3-2-3-4", "bc", "consumer", 1),
]

EXEC_NOTE_TMPL = (
    "Step 3d naming pass \u2014 directionality-missing Batch 4 (2026-09-21): "
    "renamed from '{old}' to '{new}'. Prior label retained as altLabel."
)


def in_consumer_scope(slug: str) -> bool:
    return slug == "CM-1-3-2-3" or slug.startswith("CM-1-3-2-3-")


def in_b2b_scope(slug: str) -> bool:
    return slug == "CM-1-3-2-2" or slug.startswith("CM-1-3-2-2-")


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

    # 1. the 11 renames (name/alt swap; terminology notes later)
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        old_name = row[idx["name"]].value
        assert old_name == OLD[slug], f"{slug}: name {old_name!r} != expected {OLD[slug]!r}"
        old_alt = row[idx["alt_labels"]].value or ""
        assert old_alt == NEW[slug], f"{slug}: alt {old_alt!r} != expected {NEW[slug]!r}"
        row[idx["name"]].value = new_name
        row[idx["alt_labels"]].value = OLD[slug]
        print(f"renamed {slug}: {OLD[slug]!r} -> {new_name!r}")

    # 2. scoped replacements with asserted counts
    for slug, kind, scope, expected in PLAN:
        old, new = OLD[slug], NEW[slug]
        pat = re.escape(old)
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
            s = r[idx["slug"]].value or ""
            if scope == "consumer" and not in_consumer_scope(s):
                continue
            for ci in cols:
                v = r[ci].value
                if not v:
                    continue
                new_v, n = rx.subn(repl, v)
                if n:
                    r[ci].value = new_v
                    total += n
        assert total == expected, f"{slug}/{kind}/{scope}: got {total}, expected {expected}"
        print(f"global {slug}/{kind}/{scope}: {total} (expected {expected}) OK")

    # 3. execution records (after globals so old-label mentions survive)
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        note = EXEC_NOTE_TMPL.format(old=OLD[slug], new=new_name)
        cur = row[idx["terminology_notes"]].value or ""
        row[idx["terminology_notes"]].value = (cur + " " + note).strip() if cur else note

    # 4. final sweep: no stale references may remain outside —
    #    (a) the 11 renamed rows' own terminology_notes (execution records
    #        legitimately mention the old labels),
    #    (b) name and alt_labels (retained aliases),
    #    (c) the B2B cluster CM-1-3-2-2* for the 4 consumer old labels
    #        (the B2B siblings legitimately keep the Customer/CVP labels).
    stale = []
    check_cols = [idx[c] for c in PROSE_COLS] + [idx["related_concepts"], idx["breadcrumb"]]
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        for ci in check_cols:
            if s in NEW and ci == idx["terminology_notes"]:
                continue
            v = r[ci].value or ""
            for slug, old in OLD.items():
                if slug in CONSUMER_SLUGS and in_b2b_scope(s):
                    continue
                if re.search(re.escape(old), v):
                    stale.append((s, headers[ci], old))
    assert not stale, f"stale references remain: {stale[:10]}"
    print("final sweep: no stale references outside renamed rows' notes and the B2B cluster")

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
            "Step 3d naming pass \u2014 directionality-missing Batch 4 (2026-09-21): "
            f"renamed '{OLD[slug]}' -> '{new_name}' (Hamid approval 2026-09-21, "
            "independent reviewer recommendation: approve as proposed). Prior "
            "label retained as skos:altLabel; no identifier, hierarchy, or "
            "definition change."
        )
    IDENTITY_MAP.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print("identity map: 11 overlays updated")

    # 6. naming queue: mark the 8 directionality rows EXECUTED (7 claims rows
    #    + the CM-1-3-2-3 parent row covering its 4 renamed children)
    queue_slugs = {
        "CM-1-2-4-4-2", "CM-1-2-4-4-3", "CM-1-2-4-4-4", "CM-1-2-4-4-5",
        "CM-1-2-4-4-6", "CM-1-2-4-4-7", "CM-1-2-4-4-8", "CM-1-3-2-3",
    }
    text = QUEUE.read_text(encoding="utf-8")
    lines = text.split("\n")
    marked = 0
    for i, line in enumerate(lines):
        for slug in queue_slugs:
            if line.startswith(f"| `{slug}` |") and "**EXECUTED" not in line:
                assert line.rstrip().endswith("|"), f"queue row has no trailing pipe: {line[:60]}"
                if slug == "CM-1-3-2-3":
                    exec_rec = (
                        "  **EXECUTED 2026-09-21** (Step 3d naming pass, "
                        "directionality-missing Batch 4: 4 children renamed to "
                        "consumer-directional labels — CM-1-3-2-3-1 'Test Consumer "
                        "Value Proposition', CM-1-3-2-3-2 'Formulate and Evaluate "
                        "Consumer Value Proposition Alternatives', CM-1-3-2-3-3 "
                        "'Establish Consumer Value Proposition Principles and "
                        "Objectives', CM-1-3-2-3-4 'Develop and Update Consumer "
                        "Value Proposition Strategy'; prior labels retained as "
                        "altLabels; B2B siblings under CM-1-3-2-2 untouched; "
                        "see naming PR). |"
                    )
                else:
                    exec_rec = (
                        f"  **EXECUTED 2026-09-21** (Step 3d naming pass, "
                        f"directionality-missing Batch 4: renamed to '{NEW[slug]}'; "
                        f"prior label retained as altLabel; see naming PR). |"
                    )
                lines[i] = line.rstrip()[:-1] + exec_rec
                marked += 1
                break
    assert marked == 8, f"queue rows marked: {marked}, expected 8"
    text = "\n".join(lines)
    old_hdr = "## Directionality missing (8)"
    new_hdr = "## Directionality missing (8 \u2014 8 executed 2026-09-21, 0 remaining)"
    assert old_hdr in text, "queue directionality header not in expected form"
    text = text.replace(old_hdr, new_hdr)
    old_status = ("and 12 scope-ambiguity entries executed 2026-09-21 (Step 3d naming pass "
                  "Batch 3 E+F, Hamid approval 2026-09-21). The remaining 45 queue entries "
                  "are still queued for the consolidated naming pass.")
    new_status = ("and 12 scope-ambiguity entries executed 2026-09-21 (Step 3d naming pass "
                  "Batch 3 E+F, Hamid approval 2026-09-21) and 8 directionality-missing "
                  "entries executed 2026-09-21 (Step 3d naming pass Batch 4, Hamid approval "
                  "2026-09-21). The remaining 37 queue entries are still queued for the "
                  "consolidated naming pass.")
    assert old_status in text, "queue execution-status line not in expected form"
    text = text.replace(old_status, new_status)
    QUEUE.write_text(text, encoding="utf-8")
    print("naming queue: 8 directionality rows marked EXECUTED")

    return 0


if __name__ == "__main__":
    sys.exit(main())
