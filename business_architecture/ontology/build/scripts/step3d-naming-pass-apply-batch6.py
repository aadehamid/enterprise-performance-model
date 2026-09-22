#!/usr/bin/env python3
"""Step 3d naming pass - normalization-only mechanical Batch 6 (13 renames).

Approved by Hamid 2026-09-21: 13-row table approved as listed, with
"Perform Position & P&L Analysis" (P&L retained, ampersand kept as the
standard paired trading term) and "Manage and Support Emissions Trading"
(plural, standard EPA terminology) confirmed. Alias dispositions per the
approved verdict: 11 old labels retained as skos:altLabel where safe;
2 example-laden legacy card labels are migration-map-only
(prior_name + note, NOT live altLabels) per the generic-alias precedent.

The batch is purely lexical: capitalization, punctuation, abbreviation
expansion, singular/plural, separator normalization, and removal of
overly specific parenthetical examples. No identifier, hierarchy,
definition, scope, or authority change.

Guard patterns (old label is a prefix/substring risk in two rows):
  - "Manage and Support Emission Trading":  Emission Trading not followed by "s"
  - "Formulate and Evaluate Strategic Operating Alternative": not followed by "s"
  - "Setup Prospect" / "Set Up Prospect", "Perform Customer Follow up" /
    "Follow-Up", "Create & Distribute Bill" / "Create and Distribute Bill",
    "Perform Position & PNL Analysis" / "P&L": plain full-label match is
    safe (distinct strings); "PNL" never matches "P&L".
  - "Manage feedstock Data Quality": case-sensitive match only.

Treatment (same discipline as Batches 1-5):
  - prefLabel <- new label. If the new label already sits in alt_labels
    (queued by the Step 3c review), it is promoted out of alt_labels.
  - old label -> appended to skos:altLabel, EXCEPT the two
    migration-map-only rows (CM-1-3-6-6-12, CM-1-3-6-6-4).
  - identity map: name <- new, prior_name <- old,
    scoped_historical_alias stays null, name_change_note recorded.
  - related_concepts "predicate: Old" references become
    "predicate: New (CM-slug)" (slug annotation, Batch 1 convention).
  - prose columns, breadcrumbs, and the parent-display cell updated where
    the old label is an unambiguous reference (already-annotated
    "(CM-slug)" mentions keep their annotation via plain replacement).
  - execution record appended to each renamed row's terminology_notes
    AFTER the global replacements, so the record's own old-label
    mentions survive verbatim.

One-shot migration script. Every replacement asserts its expected count,
so a stale workbook fails loudly instead of silently under-applying.
Run from the repo root:

    python3 business_architecture/ontology/build/scripts/step3d-naming-pass-apply-batch6.py

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
    "CM-1-1-7-3-3": "Manage and Support Emissions Trading",
    "CM-1-2-2-3-9": "Perform Position & P&L Analysis",
    "CM-1-2-4-2-7": "Manage Financial Information Documentation and Reporting",
    "CM-1-2-5-1-1": "Manage Feedstock Data Quality",
    "CM-1-3-2-1-1": "Formulate and Evaluate Strategic Operating Alternatives",
    "CM-1-3-6-5-2": "Manage Promotions and Events Execution",
    "CM-1-3-6-6": "Loyalty and Cards Management (Marketing)",
    "CM-1-3-6-6-1": "Set Up Prospect",
    "CM-1-3-6-6-12": "Manage Additional Card Services",
    "CM-1-3-6-6-4": "Manage Card Administration",
    "CM-1-3-7-3-3": "Change or Cancel Order",
    "CM-1-3-7-5-4": "Perform Customer Follow-Up",
    "CM-1-3-8-1-1": "Create and Distribute Bill",
}
OLD = {
    "CM-1-1-7-3-3": "Manage and Support Emission Trading",
    "CM-1-2-2-3-9": "Perform Position & PNL Analysis",
    "CM-1-2-4-2-7": "Manage Financial Info. Documentation & Reporting",
    "CM-1-2-5-1-1": "Manage feedstock Data Quality",
    "CM-1-3-2-1-1": "Formulate and Evaluate Strategic Operating Alternative",
    "CM-1-3-6-5-2": "Manage Promotions/Events Execution",
    "CM-1-3-6-6": "Loyalty And Cards Management - Marketing",
    "CM-1-3-6-6-1": "Setup Prospect",
    "CM-1-3-6-6-12": "Manage Additional Card Services (On Road Services)",
    "CM-1-3-6-6-4": "Manage Cards Administration (Order New Cards, Change Card Data)",
    "CM-1-3-7-3-3": "Change / Cancel Order",
    "CM-1-3-7-5-4": "Perform Customer Follow up",
    "CM-1-3-8-1-1": "Create & Distribute Bill",
}

# old-label disposition: "retain" -> skos:altLabel; "migration-only" ->
# prior_name + note in the identity map, NOT a live altLabel;
# "no-alt" -> same as migration-only but for the mechanical reason that a
# case-only variant trips the validator's altlabel-collision rule
# (queue rule: case/punctuation-only changes carry no alt label)
DISPOSITION = {
    "CM-1-3-6-6-12": "migration-only",  # parenthetical would falsely narrow scope
    "CM-1-3-6-6-4": "migration-only",   # activity examples, not a useful synonym
    "CM-1-2-5-1-1": "no-alt",           # case-only variant: validator collision
}
MIGRATION_ONLY = {s for s, d in DISPOSITION.items() if d in ("migration-only", "no-alt")}
NO_ALT_REASON = {
    "CM-1-2-5-1-1": (
        "it differs from the new label by case only, which the validator flags "
        "as an altlabel-collision (queue rule: case/punctuation-only changes "
        "carry no alt label)"
    ),
}

PROSE_COLS = (
    "definition", "scope_note", "in_scope", "out_of_scope",
    "key_inputs", "primary_output", "open_questions", "terminology_notes",
)


def old_pat(slug: str) -> str:
    p = re.escape(OLD[slug])
    if slug in ("CM-1-1-7-3-3", "CM-1-3-2-1-1"):
        p += r"(?!s)"
    return p


# (slug, kind, expected_hits) from the pre-execution workbook scan
# kinds: "rc" (related_concepts, gets slug annotation), "prose" (plain
# replace across PROSE_COLS), "bc" (breadcrumb), "parent" (parent-display).
PLAN = [
    ("CM-1-1-7-3-3", "rc", 1), ("CM-1-1-7-3-3", "bc", 1), ("CM-1-1-7-3-3", "prose", 1),
    ("CM-1-2-2-3-9", "rc", 3), ("CM-1-2-2-3-9", "bc", 1), ("CM-1-2-2-3-9", "prose", 1),
    ("CM-1-2-4-2-7", "bc", 1),
    ("CM-1-2-5-1-1", "rc", 1), ("CM-1-2-5-1-1", "bc", 1), ("CM-1-2-5-1-1", "prose", 1),
    ("CM-1-3-2-1-1", "rc", 2), ("CM-1-3-2-1-1", "bc", 1), ("CM-1-3-2-1-1", "prose", 1),
    ("CM-1-3-6-5-2", "bc", 1),
    ("CM-1-3-6-6", "rc", 1), ("CM-1-3-6-6", "bc", 16), ("CM-1-3-6-6", "parent", 15),
    ("CM-1-3-6-6", "prose", 4),
    ("CM-1-3-6-6-1", "rc", 3), ("CM-1-3-6-6-1", "bc", 1), ("CM-1-3-6-6-1", "prose", 3),
    ("CM-1-3-6-6-12", "bc", 1),
    ("CM-1-3-6-6-4", "rc", 1), ("CM-1-3-6-6-4", "bc", 1),
    ("CM-1-3-7-3-3", "rc", 1), ("CM-1-3-7-3-3", "bc", 1), ("CM-1-3-7-3-3", "prose", 1),
    ("CM-1-3-7-5-4", "rc", 5), ("CM-1-3-7-5-4", "bc", 1),
    ("CM-1-3-8-1-1", "rc", 9), ("CM-1-3-8-1-1", "bc", 1),
]

EXEC_NOTE_TMPL = (
    "Step 3d naming pass \u2014 normalization-only mechanical Batch 6 (2026-09-21): "
    "renamed from '{old}' to '{new}'. {alias_note}"
)
EXEC_NOTE_ALIAS_STD = "Prior label retained as altLabel."
EXEC_NOTE_ALIAS_EXC = (
    "Prior label NOT retained as skos:altLabel per the {reason_kind} "
    "disposition (generic-alias precedent): {reason} it is "
    "preserved as prior_name in the identity/migration map."
)


def split_alts(v):
    if not v:
        return []
    return [a.strip() for a in str(v).split("|") if a.strip()]


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

    # 0. collision checks: every new label must be free as a prefLabel and
    #    as an altLabel on every OTHER row; every retained old label must
    #    not collide with another row's prefLabel.
    pref = {}
    alts = {}
    for s, r in by_slug.items():
        pref[r[idx["name"]].value] = s
        for a in split_alts(r[idx["alt_labels"]].value):
            alts.setdefault(a, []).append(s)
    for slug, new_name in NEW.items():
        if new_name in pref and pref[new_name] != slug:
            raise AssertionError(f"new label collision: {new_name!r} is prefLabel of {pref[new_name]}")
        for other in alts.get(new_name, []):
            if other != slug:
                raise AssertionError(f"new label collision: {new_name!r} is altLabel of {other}")
    for slug, old_name in OLD.items():
        if slug in MIGRATION_ONLY:
            continue
        if old_name in pref and pref[old_name] != slug:
            raise AssertionError(f"retained alias collision: {old_name!r} is prefLabel of {pref[old_name]}")
    print("collision checks: 13 new labels free; 11 retained aliases safe")

    # 1. the 13 renames (name/alt swap; terminology notes later)
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        old_name = row[idx["name"]].value
        assert old_name == OLD[slug], f"{slug}: name {old_name!r} != expected {OLD[slug]!r}"
        alt_list = split_alts(row[idx["alt_labels"]].value)
        assert OLD[slug] not in alt_list, f"{slug}: old label already an altLabel"
        if new_name in alt_list:
            alt_list.remove(new_name)  # promote the queued alt label
            promoted = " (promoted from queued altLabel)"
        else:
            promoted = ""
        if slug in MIGRATION_ONLY:
            alias_note = "migration-map-only: no altLabel"
        else:
            alt_list.append(OLD[slug])
            alias_note = "prior label retained as altLabel"
        row[idx["name"]].value = new_name
        row[idx["alt_labels"]].value = " | ".join(alt_list) if alt_list else None
        print(f"renamed {slug}: {OLD[slug]!r} -> {new_name!r} [{alias_note}]{promoted}")

    # 2. scoped replacements with asserted counts
    for slug, kind, expected in PLAN:
        old, new = OLD[slug], NEW[slug]
        pat = old_pat(slug)
        total = 0
        if kind == "rc":
            rx = re.compile(r"([a-z][a-z-]*): " + pat + r"(?= \||$)")
            repl = r"\1: " + new + f" ({slug})"
            cols = [idx["related_concepts"]]
        elif kind == "prose":
            rx = re.compile(pat)
            repl = new
            cols = [idx[c] for c in PROSE_COLS]
        elif kind == "parent":
            rx = re.compile(r"^" + pat + r"$")
            repl = new
            cols = [idx["parent"]]
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
        print(f"{slug}/{kind}: {total} (expected {expected}) OK")

    # 3. execution records (after globals so old-label mentions survive)
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        if slug in MIGRATION_ONLY:
            if DISPOSITION.get(slug) == "no-alt":
                alias_note = EXEC_NOTE_ALIAS_EXC.format(
                    reason_kind="no-altLabel",
                    reason="the old label " + NO_ALT_REASON[slug] + ";")
            else:
                alias_note = EXEC_NOTE_ALIAS_EXC.format(
                    reason_kind="migration-map-only",
                    reason="the old label would falsely narrow scope / is not a "
                           "useful synonym;")
        else:
            alias_note = EXEC_NOTE_ALIAS_STD
        note = EXEC_NOTE_TMPL.format(old=OLD[slug], new=new_name, alias_note=alias_note)
        cur = row[idx["terminology_notes"]].value or ""
        row[idx["terminology_notes"]].value = (cur + " " + note).strip() if cur else note

    # 4. final sweep: no stale references may remain outside —
    #    (a) the 13 renamed rows' own terminology_notes (execution records
    #        legitimately mention the old labels),
    #    (b) name and alt_labels (retained aliases; the two migration-only
    #        rows keep none).
    #    Guarded patterns so the new labels themselves never flag
    #    (Emission Trading(?!s), Alternative(?!s), case-sensitive
    #    "feedstock", exact "PNL" never matching "P&L").
    stale = []
    check_cols = [idx[c] for c in PROSE_COLS] + [idx["related_concepts"], idx["breadcrumb"], idx["parent"]]
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        for ci in check_cols:
            if s in NEW and ci == idx["terminology_notes"]:
                continue
            if s in NEW and ci in (idx["name"], idx["alt_labels"]):
                continue
            v = r[ci].value or ""
            for slug in OLD:
                if re.search(old_pat(slug), v):
                    stale.append((s, headers[ci], OLD[slug]))
    assert not stale, f"stale references remain: {stale[:10]}"
    print("final sweep: no stale references outside renamed rows' notes/aliases")

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
        if slug in MIGRATION_ONLY:
            if DISPOSITION.get(slug) == "no-alt":
                reason = ("the old label is NOT retained as skos:altLabel \u2014 "
                          + NO_ALT_REASON[slug] + "; it is preserved as prior_name "
                          "in the identity/migration map only.")
            else:
                reason = ("the old label is NOT retained as skos:altLabel \u2014 "
                          "it would falsely narrow scope / is not a useful ontology "
                          "synonym; it is preserved as prior_name in the "
                          "identity/migration map only.")
            e["name_change_note"] = (
                "Step 3d naming pass \u2014 normalization-only mechanical Batch 6 (2026-09-21): "
                f"renamed '{OLD[slug]}' -> '{new_name}' (Hamid approval 2026-09-21). "
                "Migration-map-only disposition per the generic-alias precedent: "
                + reason + " "
                "No identifier, hierarchy, or definition change."
            )
        else:
            e["name_change_note"] = (
                "Step 3d naming pass \u2014 normalization-only mechanical Batch 6 (2026-09-21): "
                f"renamed '{OLD[slug]}' -> '{new_name}' (Hamid approval 2026-09-21). "
                "Purely lexical normalization (capitalization / punctuation / "
                "abbreviation / number / separator); prior label retained as "
                "skos:altLabel; no identifier, hierarchy, or definition change."
            )
    IDENTITY_MAP.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print("identity map: 13 overlays updated")

    # 6. naming queue: mark the 13 mechanical rows EXECUTED
    queue_slugs = set(NEW)
    text = QUEUE.read_text(encoding="utf-8")
    lines = text.split("\n")
    marked = 0
    for i, line in enumerate(lines):
        for slug in queue_slugs:
            if line.startswith(f"| `{slug}` |") and "**EXECUTED" not in line:
                assert line.rstrip().endswith("|"), f"queue row has no trailing pipe: {line[:60]}"
                if slug in MIGRATION_ONLY:
                    if DISPOSITION.get(slug) == "no-alt":
                        why = ("NOT retained as altLabel (case-only variant trips the "
                               "validator's altlabel-collision rule), kept as prior_name")
                    else:
                        why = ("NOT retained as altLabel per the migration-map-only "
                               "disposition, kept as prior_name")
                    exec_rec = (
                        f"  **EXECUTED 2026-09-21** (Step 3d naming pass, "
                        f"normalization-only mechanical Batch 6: renamed to '{NEW[slug]}'; "
                        f"historical label '{OLD[slug]}' {why} "
                        f"in the identity map; see naming PR). |"
                    )
                else:
                    exec_rec = (
                        f"  **EXECUTED 2026-09-21** (Step 3d naming pass, "
                        f"normalization-only mechanical Batch 6: renamed to '{NEW[slug]}'; "
                        f"prior label retained as altLabel; see naming PR). |"
                    )
                lines[i] = line.rstrip()[:-1] + exec_rec
                marked += 1
                break
    assert marked == 13, f"queue rows marked: {marked}, expected 13"
    text = "\n".join(lines)
    old_hdr = "## Normalization only (26)"
    new_hdr = "## Normalization only (26 \u2014 13 executed 2026-09-21, 13 remaining)"
    assert old_hdr in text, "queue section header not found"
    text = text.replace(old_hdr, new_hdr)
    old_status = ("and 11 generic-operational entries executed 2026-09-21 (Step 3d naming pass "
                  "Batch 5, Hamid approval 2026-09-21). The remaining 26 queue entries "
                  "are still queued for the consolidated naming pass.")
    new_status = ("and 11 generic-operational entries executed 2026-09-21 (Step 3d naming pass "
                  "Batch 5, Hamid approval 2026-09-21) and 13 normalization-only "
                  "mechanical entries executed 2026-09-21 (Step 3d naming pass Batch 6, "
                  "Hamid approval 2026-09-21). The remaining 13 queue entries "
                  "(normalization-only, judgment) are still queued for the naming pass.")
    assert old_status in text, "queue execution-status line not in expected form"
    text = text.replace(old_status, new_status)
    QUEUE.write_text(text, encoding="utf-8")
    print("queue: 13 mechanical rows marked EXECUTED; header and status updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
