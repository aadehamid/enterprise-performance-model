#!/usr/bin/env python3
"""Step 3d naming pass — scope-ambiguity Batch 1 (A+B+C, 10 renames).

Approved by Hamid 2026-09-21 with three reviewer refinements adopted:
  1. CM-1-1-3-6-2 -> "Administer Scheduled Shipment Loading" (not
     "Administer Shipment Loading"): "Scheduled" distinguishes
     scheduled-load administration from physical loading, dispatch,
     and carrier operations. Old labels retained as altLabels:
     "Loading Shipment", "Load Administration",
     "Shipment Loading Administration".
  2. CM-1-3-7-4-6 "Perform KYC Due Diligence" confirmed: the approved
     scope note already states the Commercial/Credit-vs-Compliance/Legal
     boundary verbatim (frameworks owned by Compliance/Legal; this
     process executes, escalates, never clears/excepts/decides).
  3. CM-1-3-7-1-6 -> "Maintain Commercial Policy Content and Approved
     Parameters": the scope note says parameters are maintained "on the
     owners' approved direction" and content is approved policy content.

Also records the queue slug correction CM-1-3-7-8-1 -> CM-1-3-6-8-1
in the naming-pass queue (explicit metadata repair, not silent).

One-shot migration script. Every replacement asserts its expected count,
so a stale workbook fails loudly instead of silently under-applying.
Run from the repo root:

    python3 build/scripts/step3d-naming-pass-apply-batch1.py

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
    "CM-1-1-3-6-2": "Administer Scheduled Shipment Loading",
    "CM-1-1-3-8-3": "Maintain Secondary Distribution Scheduling Basis",
    "CM-1-2-4-1-8": "Settle Environmental Instruments",
    "CM-1-2-4-2-2": "Manage Production & Inventory Accounting",
    "CM-1-2-6-2-3": "Forecast Operational Refined Product Demand",
    "CM-1-2-6-3-2": "Fulfill Replenishment From Trading Sources",
    "CM-1-2-6-3-3": "Coordinate S&T-Sourced Primary Transportation",
    "CM-1-3-6-6-2": "Manage Card Program Billing Coordination",
    "CM-1-3-6-6-6": "Manage Card Delinquency and Collections Referral",
    "CM-1-3-6-8-1": "Conduct Commercial Audit to Validate Reported Sales",
}
OLD = {
    "CM-1-1-3-6-2": "Loading Shipment",
    "CM-1-1-3-8-3": "Setup Scheduling System",
    "CM-1-2-4-1-8": "Settle Emissions",
    "CM-1-2-4-2-2": "Manage Production Accounting",
    "CM-1-2-6-2-3": "Forecast Refined Product Demand",
    "CM-1-2-6-3-2": "Manage Replenishment",
    "CM-1-2-6-3-3": "Manage Primary Distribution Transportation",
    "CM-1-3-6-6-2": "Manage Invoicing",
    "CM-1-3-6-6-6": "Manage Bad Debt",
    "CM-1-3-6-8-1": "Conduct Audit To Validate Reported Sales",
}
OLD_ALT = {
    "CM-1-1-3-6-2": "Load Administration | Shipment Loading Administration",
    "CM-1-1-3-8-3": "Maintain Secondary Distribution Scheduling Basis",
    "CM-1-2-4-1-8": "Settle Environmental Instruments",
    "CM-1-2-4-2-2": "Manage Production & Inventory Accounting",
    "CM-1-2-6-2-3": "Forecast Operational Refined Product Demand",
    "CM-1-2-6-3-2": "Fulfill Replenishment From Trading Sources",
    "CM-1-2-6-3-3": "Coordinate S&T-Sourced Primary Transportation",
    "CM-1-3-6-6-2": "Manage Card Program Billing Coordination",
    "CM-1-3-6-6-6": "Manage Card Delinquency and Collections Referral",
    "CM-1-3-6-8-1": "Conduct Commercial Audit to Validate Reported Sales",
}
# All old labels are retained as altLabels (verified: no prefLabel
# collision elsewhere; uniquely resolvable and semantically safe).
NEW_ALT = {
    "CM-1-1-3-6-2": "Loading Shipment | Load Administration | Shipment Loading Administration",
    "CM-1-1-3-8-3": "Setup Scheduling System",
    "CM-1-2-4-1-8": "Settle Emissions",
    "CM-1-2-4-2-2": "Manage Production Accounting",
    "CM-1-2-6-2-3": "Forecast Refined Product Demand",
    "CM-1-2-6-3-2": "Manage Replenishment",
    "CM-1-2-6-3-3": "Manage Primary Distribution Transportation",
    "CM-1-3-6-6-2": "Manage Invoicing",
    "CM-1-3-6-6-6": "Manage Bad Debt",
    "CM-1-3-6-8-1": "Conduct Audit To Validate Reported Sales",
}

# Global mechanical replacements: (pattern, replacement, expected_total_hits)
GLOBAL = [
    # --- Loading Shipment -> Administer Scheduled Shipment Loading ---
    (r"(precedes|follows): Loading Shipment(?= \||$)",
     r"\1: Administer Scheduled Shipment Loading (CM-1-1-3-6-2)", 3),
    # --- Settle Emissions -> Settle Environmental Instruments ---
    (r"\(Settle Emissions, CM-1-2-4-1-8\)",
     r"(Settle Environmental Instruments, CM-1-2-4-1-8)", 2),
    (r"precedes: Settle Emissions(?= \||$)",
     r"precedes: Settle Environmental Instruments (CM-1-2-4-1-8)", 1),
    # --- Forecast Refined Product Demand -> Forecast Operational ... ---
    (r"\(Forecast Refined Product Demand, CM-1-2-6-2-3\)",
     r"(Forecast Operational Refined Product Demand, CM-1-2-6-2-3)", 3),
    (r"Forecast Refined Product Demand \(CM-1-2-6-2-3\)",
     r"Forecast Operational Refined Product Demand (CM-1-2-6-2-3)", 1),
    (r"uses-input: Forecast Refined Product Demand(?= \||$)",
     r"uses-input: Forecast Operational Refined Product Demand (CM-1-2-6-2-3)", 1),
    (r"\(Forecast Refined Product Demand\)",
     r"(Forecast Operational Refined Product Demand, CM-1-2-6-2-3)", 2),
    # --- Manage Replenishment -> Fulfill Replenishment From Trading Sources ---
    # (?<!Inventory ) guard: "Manage Inventory Replenishment" is a different
    # concept and must not be touched.
    (r"(?<!Inventory )(enables|follows): Manage Replenishment(?= \||$)",
     r"\1: Fulfill Replenishment From Trading Sources (CM-1-2-6-3-2)", 4),
    # --- Manage Invoicing -> Manage Card Program Billing Coordination ---
    (r"enables: Manage Invoicing(?= \||$)",
     r"enables: Manage Card Program Billing Coordination (CM-1-3-6-6-2)", 2),
    # --- Manage Bad Debt -> Manage Card Delinquency and Collections Referral ---
    # "Bad Debt Allowance" (CM-1-3-8-3-3, Batch 3) is a different label and
    # must not be touched: the pattern anchors on "Manage Bad Debt".
    (r"(enables|uses-input): Manage Bad Debt(?= \||$)",
     r"\1: Manage Card Delinquency and Collections Referral (CM-1-3-6-6-6)", 2),
    # --- Conduct Audit To Validate Reported Sales -> Conduct Commercial ... ---
    (r"uses-input: Conduct Audit To Validate Reported Sales(?= \||$)",
     r"uses-input: Conduct Commercial Audit to Validate Reported Sales (CM-1-3-6-8-1)", 1),
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

    # 1. the 10 renames
    for slug, new_name in NEW.items():
        row = by_slug[slug]
        old_name = row[idx["name"]].value
        assert old_name == OLD[slug], f"{slug}: name {old_name!r} != expected {OLD[slug]!r}"
        row[idx["name"]].value = new_name
        old_alt = row[idx["alt_labels"]].value or ""
        assert old_alt == OLD_ALT[slug], f"{slug}: alt {old_alt!r} != expected {OLD_ALT[slug]!r}"
        row[idx["alt_labels"]].value = NEW_ALT[slug]
        note = (f"Step 3d naming pass \u2014 scope-ambiguity Batch 1 (A+B+C, 2026-09-21): "
                f"renamed from '{OLD[slug]}' to '{new_name}'. "
                f"Prior label(s) retained as altLabel(s): '{NEW_ALT[slug]}'.")
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
        print(f"global {pat[:60]!r}: {total} (expected {expected}) OK")

    # 3. final sweep: no stale references may remain outside the 10
    # renamed rows' own terminology_notes (execution records legitimately
    # mention the old labels there).
    stale = []
    for r in ws.iter_rows(min_row=2):
        s = r[idx["slug"]].value
        for ci in text_cols + [idx["name"], idx["alt_labels"]]:
            # The 10 renamed rows legitimately mention old labels in their
            # own name (no), alt_labels (retained), and terminology_notes
            # (execution record) — skip those three columns for them.
            if s in NEW and ci in (idx["terminology_notes"], idx["name"], idx["alt_labels"]):
                continue
            v = r[ci].value or ""
            for slug, old in OLD.items():
                if old == "Manage Replenishment":
                    # must not match "Manage Inventory Replenishment"
                    found = re.search(r"(?<!Inventory )" + re.escape(old), v)
                else:
                    # "Bad Debt Allowance" never contains "Manage Bad Debt";
                    # plain substring search is safe for the rest
                    found = old in v
                if found:
                    stale.append((s, headers[ci], old))
    assert not stale, f"stale references remain: {stale[:10]}"
    print("final sweep: no stale references outside the 10 renamed rows' own notes")

    wb.save(WB)
    print(f"saved {WB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
