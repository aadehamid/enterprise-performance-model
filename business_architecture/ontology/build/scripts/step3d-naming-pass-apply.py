#!/usr/bin/env python3
"""Step 3d Phase 1 execution: critical semantic-collision renames (8).

Approved by Hamid 2026-09-21 with two label-policy refinements:
  1. CM-1-1-1-1 -> "Produce Demand Forecast" (verb-led); "Demand Forecasting"
     is NOT retained as an altLabel (L3 keeps it as prefLabel).
  2. The five "Define KPI Framework" rows take domain-specific Measurement
     Framework labels; the shared generic label is NOT retained as an ontology
     altLabel (scoped historical aliases live in the identity/migration map).

One-shot migration script. Every replacement asserts its expected count, so a
stale workbook fails loudly instead of silently under-applying. Run from the
repo root:

    python3 build/scripts/step3d-naming-pass-apply.py

Edits build/output/step3c-definition-authoring-workbook.xlsx in place.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from openpyxl import load_workbook

WB = Path("business_architecture/ontology/build/output/step3c-definition-authoring-workbook.xlsx")
SHEET = "Review & authoring"

NEW = {
    "CM-1-1-1-1":   "Produce Demand Forecast",
    "CM-1-1-3-7":   "Inventory Management",
    "CM-1-1-3-7-12": "Monitor and Control Inventory Positions",
    "CM-1-3-3-1-4": "Define Offer Measurement Framework",
    "CM-1-3-3-2-5": "Define Pricing Measurement Framework",
    "CM-1-3-3-3-5": "Define Channel Measurement Framework",
    "CM-1-3-3-4-4": "Define Network Measurement Framework",
    "CM-1-3-3-6-5": "Define Operating Model Measurement Framework",
}
OLD = {
    "CM-1-1-1-1":   "Demand Forecasting",
    "CM-1-1-3-7":   "Inventory",
    "CM-1-1-3-7-12": "Manage Inventory",
    "CM-1-3-3-1-4": "Define KPI Framework",
    "CM-1-3-3-2-5": "Define KPI Framework",
    "CM-1-3-3-3-5": "Define KPI Framework",
    "CM-1-3-3-4-4": "Define KPI Framework",
    "CM-1-3-3-6-5": "Define KPI Framework",
}
OLD_ALT = {
    "CM-1-1-1-1":   "Product Demand Forecasting",
    "CM-1-1-3-7":   "Inventory Management | Stock Management",
    "CM-1-1-3-7-12": "Monitor and Control Inventory Positions | Inventory Position Management",
    "CM-1-3-3-1-4": "Define Offer Measurement Framework",
    "CM-1-3-3-2-5": "Define Pricing Measurement Framework",
    "CM-1-3-3-3-5": "Define Channel Measurement Framework",
    "CM-1-3-3-4-4": "Define Network Measurement Framework",
    "CM-1-3-3-6-5": "Define Operating Model Measurement Framework",
}
NEW_ALT = {
    "CM-1-1-1-1":   None,  # keeps "Product Demand Forecasting"
    "CM-1-1-3-7":   "Inventory | Stock Management",
    "CM-1-1-3-7-12": "Manage Inventory | Inventory Position Management",
    "CM-1-3-3-1-4": "",
    "CM-1-3-3-2-5": "",
    "CM-1-3-3-3-5": "",
    "CM-1-3-3-4-4": "",
    "CM-1-3-3-6-5": "",
}
SCOPED_ALIAS = {
    "CM-1-3-3-1-4": "Define KPI Framework (Offer)",
    "CM-1-3-3-2-5": "Define KPI Framework (Pricing)",
    "CM-1-3-3-3-5": "Define KPI Framework (Channel)",
    "CM-1-3-3-4-4": "Define KPI Framework (Network)",
    "CM-1-3-3-6-5": "Define KPI Framework (Operating Model)",
}

# Global mechanical replacements: (pattern, replacement, expected_total_hits)
GLOBAL = [
    (r"Demand Forecasting \(CM-1-1-1-1([^)]*)\)",
     r"Produce Demand Forecast (CM-1-1-1-1\1)", 9),
    (r"Manage Inventory \(CM-1-1-3-7-12\)",
     r"Monitor and Control Inventory Positions (CM-1-1-3-7-12)", 3),
    (r"Manage Inventory, CM-1-1-3-7-12",
     r"Monitor and Control Inventory Positions, CM-1-1-3-7-12", 1),
    (r"constrained-by: Inventory(?= \||$)",
     r"constrained-by: Inventory Management (CM-1-1-3-7)", 5),
    (r"enables: Manage Inventory(?= \||$)",
     r"enables: Monitor and Control Inventory Positions (CM-1-1-3-7-12)", 6),
    (r"uses-input: Manage Inventory(?= \||$)",
     r"uses-input: Monitor and Control Inventory Positions (CM-1-1-3-7-12)", 1),
    (r"informed-by: Demand Forecasting(?= \||$)",
     r"informed-by: Produce Demand Forecast (CM-1-1-1-1)", 10),
    (r"uses-input: Demand Forecasting(?= \||$)",
     r"uses-input: Produce Demand Forecast (CM-1-1-1-1)", 4),
    (r"enables: Demand Forecasting(?= \||$)",
     r"enables: Produce Demand Forecast (CM-1-1-1-1)", 2),
]

# Per-row prose replacements: (slug, column, old_substring, new_substring)
ROWS = [
    # --- KPI cluster: 9 definite cross-reference updates ---
    ("CM-1-3-3-1", "terminology_notes",
     "Define Customer Offer \u2192 Validate Customer Offer \u2192 Define KPI Framework",
     "Define Customer Offer \u2192 Validate Customer Offer \u2192 Define Offer Measurement Framework"),
    ("CM-1-3-3-1-3", "related_concepts",
     "precedes: Define KPI Framework",
     "precedes: Define Offer Measurement Framework (CM-1-3-3-1-4)"),
    ("CM-1-3-3-2-2", "related_concepts",
     "precedes: Define KPI Framework",
     "precedes: Define Pricing Measurement Framework (CM-1-3-3-2-5)"),
    ("CM-1-3-3-2-3", "related_concepts",
     "follows: Define KPI Framework",
     "follows: Define Pricing Measurement Framework (CM-1-3-3-2-5)"),
    ("CM-1-3-3-3", "terminology_notes",
     "Develop Channel Structure, Size & Engagement Model \u2192 Define KPI Framework",
     "Develop Channel Structure, Size & Engagement Model \u2192 Define Channel Measurement Framework"),
    ("CM-1-3-3-3-4", "related_concepts",
     "precedes: Define KPI Framework",
     "precedes: Define Channel Measurement Framework (CM-1-3-3-3-5)"),
    ("CM-1-3-3-4-1", "related_concepts",
     "precedes: Define KPI Framework",
     "precedes: Define Network Measurement Framework (CM-1-3-3-4-4)"),
    ("CM-1-3-3-6", "terminology_notes",
     "Define Procedural Framework & Guidelines \u2192 Define KPI Framework",
     "Define Procedural Framework & Guidelines \u2192 Define Operating Model Measurement Framework"),
    ("CM-1-3-3-6-4", "related_concepts",
     "precedes: Define KPI Framework",
     "precedes: Define Operating Model Measurement Framework (CM-1-3-3-6-5)"),
    # --- stale template note (names diverge, "identical name" becomes false) ---
    ("CM-1-3-3-1-4", "terminology_notes",
     "Template row (identical name at CM-1-3-3-2-5 and CM-1-3-3-3-5 by design)",
     "Template row (sibling rows CM-1-3-3-2-5 and CM-1-3-3-3-5 by design)"),
    # --- CM-1-1-3-7 terminology note: collision note becomes stale after rename ---
    ("CM-1-1-3-7", "terminology_notes",
     "Preferred normalized label 'Inventory Management' queued for the consolidated "
     "naming pass; current label retained for batch traceability, together with the "
     "L4-versus-L5 'Manage Inventory' label collision.",
     "Step 3d naming pass (2026-09-21): renamed to 'Inventory Management' "
     "('Inventory' retained as altLabel); the L4-versus-L5 label collision is resolved "
     "\u2014 the L5 is now 'Monitor and Control Inventory Positions' ('Manage Inventory' "
     "retained as its altLabel)."),
    # --- CM-1-1-2-13: "(Inventory)" domain tags denote the renamed capability ---
    ("CM-1-1-2-13", "out_of_scope",
     "(Develop Finished Product Inventory Policy, Inventory)",
     "(Develop Finished Product Inventory Policy, Inventory Management)"),
    ("CM-1-1-2-13", "out_of_scope",
     "inventory measurement and reconciliation (Inventory)",
     "inventory measurement and reconciliation (Inventory Management)"),
    ("CM-1-1-2-13", "out_of_scope",
     "(Manage Inventory Replenishment, Inventory)",
     "(Manage Inventory Replenishment, Inventory Management)"),
    ("CM-1-1-2-13", "out_of_scope",
     "re-brand inventory management (Inventory)",
     "re-brand inventory management (Inventory Management)"),
    ("CM-1-1-2-13", "scope_note",
     "the Inventory cluster under Distribution Planning & Scheduling",
     "the Inventory Management cluster under Distribution Planning & Scheduling"),
    ("CM-1-1-2-13", "terminology_notes",
     "the Inventory cluster under Distribution Planning & Scheduling (CM-1-1-3-7)",
     "the Inventory Management cluster under Distribution Planning & Scheduling (CM-1-1-3-7)"),
    # --- no-slug Demand Forecasting prose -> L4 (verified per row, see proposal) ---
    ("CM-1-1-2-12", "out_of_scope",
     "(Prepare Master Data To Create Demand Forecast, Demand Forecasting)",
     "(Prepare Master Data To Create Demand Forecast, Produce Demand Forecast (CM-1-1-1-1))"),
    ("CM-1-2-1-1-2", "terminology_notes",
     "(Demand Forecasting owns the approved forecast)",
     "(Produce Demand Forecast owns the approved forecast)"),
    ("CM-1-2-1-3", "terminology_notes",
     "the Demand Forecasting process precedent",
     "the Produce Demand Forecast process precedent"),
    ("CM-1-2-5-2", "terminology_notes",
     "like the batch 03 Demand Forecasting precedent",
     "like the batch 03 Produce Demand Forecast precedent"),
    ("CM-1-3-5-1", "terminology_notes",
     "produced through Demand Forecasting",
     "produced through Produce Demand Forecast"),
    ("CM-1-3-5-1-2", "definition",
     "feed Demand Forecasting, in what form",
     "feed Produce Demand Forecast, in what form"),
    ("CM-1-3-5-1-2", "in_scope",
     "with Demand Forecasting",
     "with Produce Demand Forecast"),
    ("CM-1-3-5-1-2", "scope_note",
     "are Demand Forecasting's",
     "are Produce Demand Forecast's"),
    ("CM-1-3-5-1-2", "key_inputs",
     "Demand Forecasting's input requirements (CM-1-1-1-1)",
     "Produce Demand Forecast's input requirements (CM-1-1-1-1)"),
    ("CM-1-3-5-1-4", "scope_note",
     "follow Demand Forecasting's governance",
     "follow Produce Demand Forecast's governance"),
]


def main() -> int:
    wb = load_workbook(WB)
    ws = wb[SHEET]
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    text_cols = [idx[c] for c in (
        "definition", "scope_note", "in_scope", "out_of_scope",
        "related_concepts", "terminology_notes", "key_inputs",
        "primary_output", "open_questions")]
    by_slug = {}
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        if s:
            by_slug[s] = r

    # 1. the 8 renames
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        old_name = row[idx["name"]].value
        assert old_name == OLD[slug], f"{slug}: name {old_name!r} != expected {OLD[slug]!r}"
        row[idx["name"]].value = new_name
        old_alt = row[idx["alt_labels"]].value or ""
        assert old_alt == OLD_ALT[slug], f"{slug}: alt {old_alt!r} != expected {OLD_ALT[slug]!r}"
        if NEW_ALT[slug] is not None:
            row[idx["alt_labels"]].value = NEW_ALT[slug] or None
        # execution record on the row itself
        note = (f"Step 3d naming pass (2026-09-21): renamed from '{OLD[slug]}' to "
                f"'{new_name}' \u2014 critical semantic-collision resolution.")
        if slug in SCOPED_ALIAS:
            note += (f" Prior label retired from ontology aliases (a shared generic altLabel "
                     f"would recreate the collision); scoped historical alias "
                     f"'{SCOPED_ALIAS[slug]}' recorded in the identity/migration map.")
        elif slug == "CM-1-1-1-1":
            note += " Prior label not retained as altLabel: the L3 keeps it as prefLabel."
        else:
            note += f" Prior label '{OLD[slug]}' retained as altLabel."
        cur = row[idx["terminology_notes"]].value or ""
        row[idx["terminology_notes"]].value = (cur + " " + note).strip() if cur else note
        print(f"renamed {slug}: {OLD[slug]!r} -> {new_name!r}")

    # 2. global mechanical replacements with asserted counts
    for pat, repl, expected in GLOBAL:
        rx = re.compile(pat)
        total = 0
        for r in ws.iter_rows(min_row=2):
            for ci in text_cols:
                v = r[ci].value
                if not v:
                    continue
                new_v, n = rx.subn(repl, v)
                if n:
                    r[ci].value = new_v
                    total += n
        assert total == expected, f"{pat!r}: got {total}, expected {expected}"
        print(f"global {pat!r}: {total} (expected {expected}) OK")

    # 3. per-row prose replacements, exactly one hit each
    for slug, col, old, new in ROWS:
        row = by_slug[slug]
        v = row[idx[col]].value or ""
        assert v.count(old) == 1, f"{slug}[{col}]: {old!r} found {v.count(old)}x"
        row[idx[col]].value = v.replace(old, new)
    print(f"per-row replacements: {len(ROWS)} OK")

    # 4. final sweep: no stale references may remain
    stale = []
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        for ci in text_cols + [idx["name"], idx["alt_labels"]]:
            v = r[ci].value or ""
            if re.search(r"Demand Forecasting \(CM-1-1-1-1", v):
                stale.append((s, ci, "DF-slug"))
            if re.search(r"Manage Inventory [\(,]CM-1-1-3-7-12", v):
                stale.append((s, ci, "MI-slug"))
            if re.search(r"constrained-by: Inventory(?= \||$)", v):
                stale.append((s, ci, "constrained"))
            if re.search(r"(enables|uses-input|informed-by): (Manage Inventory|Demand Forecasting)(?= \||$)", v):
                stale.append((s, ci, "noslug-relation"))
    # the 8 renamed rows' own terminology_notes legitimately mention old labels
    stale = [x for x in stale if x[0] not in NEW]
    assert not stale, f"stale references remain: {stale[:10]}"
    print("final sweep: no stale references outside the 8 renamed rows' own notes")

    wb.save(WB)
    print(f"saved {WB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
