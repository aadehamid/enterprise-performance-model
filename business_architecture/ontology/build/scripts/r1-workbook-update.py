#!/usr/bin/env python3
"""R1 Refining structural reclassification — one-shot workbook update.

Applies the Hamid-approved R1 change set to the Step 3c definition workbook
("Review & authoring" sheet), deterministically and with assertions:

  1. Migrated rows (42): level, parent (display name), breadcrumb from the new
     tree; new prefLabel for the 2 promoted L2s.
  2. Scope-note corrections (package section 4a/4c, enumerated in the cell diff):
     - mechanical rename of the two promoted labels everywhere they are cited
       in scope_note / in_scope / out_of_scope / definition
       (terminology_notes are historical provenance: never touched);
     - CM-1-1-4 scope note: premise / plan / plan-of-record distinction (T9c);
     - CM-1-1-7-2-6 scope note + out_of_scope: execution counterparty is
       Refining; refinery maintenance capability to-be-modeled in R2 (T10).
  3. New Candidate L2 row (approved): definition + scope note verbatim from the
     decision package, Candidate marker in terminology_notes.
  4. Asserted rows (pending) for the 15 moved concepts with no workbook row,
     plus CM-1-1-2-9-1 carrying the informs: CM-1-1-4 interface entry in
     related_concepts.
  5. Controlled-vocabulary validation of every touched value.
  6. Reviewable cell diff.

Usage:
  python3 r1-workbook-update.py   # defaults: in-place workbook update

One-shot and asserted: it refuses to run twice (the new L2 row and the T9c
addition are already present). Re-running on an updated workbook fails loudly
rather than silently double-applying.

Naming-authority note (2026-09-22 fix): breadcrumb and parent display names
are reconstructed from the identity-map executed names, not from
downstream_process_map.json node names. The JSON carried the stale
pre-Step-3d label "Manage and Support Emission Trading" for CM-1-1-7-3-3,
which the original breadcrumb logic copied verbatim into the workbook,
reverting an executed Step 3d label. The identity map is the naming
authority (same names that render TTL prefLabels).
"""
import argparse
import json
import re
from pathlib import Path

from openpyxl import load_workbook

# Repo-relative defaults (script lives at build/scripts/r1-workbook-update.py).
_HERE = Path(__file__).resolve().parent
_BUILD = _HERE.parent
_BUSINESS_ARCH = _BUILD.parent.parent
_D_WORKBOOK = _BUILD / "output" / "step3c-definition-authoring-workbook.xlsx"
_D_IDENTITY_MAP = _BUILD / "output" / "step2-identity-map.json"
_D_SRC_JSON = (_BUSINESS_ARCH / "business_process" /
               "downstream_process_map.json")
_D_CELL_DIFF = _BUILD / "r1" / "r1-cell-diff.md"

DATE = "2026-09-22"
SHEET = "Review & authoring"

OLD_NEW = [
    ("Refinery Planning", "Refinery Planning and Optimization"),
    ("Refinery Scheduling", "Refinery Production Planning and Scheduling"),
]
# stale reference = old label NOT already followed by the new suffix
STALE_RES = [(re.compile(re.escape(o) + r"(?! and Optimization)"), n)
             for o, n in OLD_NEW]
SEMANTIC_COLS = ("scope_note", "in_scope", "out_of_scope", "definition")

NEW_L2_SLUG = "L2-refinery-asset-reliability-and-turnaround-coordination"
NEW_L2_NAME = "Refinery Asset Reliability and Turnaround Coordination"
NEW_L2_DEF = (
    "The Refining capability that coordinates refinery availability, "
    "asset-condition and integrity inputs, maintenance and turnaround windows, "
    "production-plan impacts, readiness, and recovery interfaces so refinery "
    "performance objectives can be planned and managed against approved "
    "maintenance, integrity, and turnaround commitments."
)
NEW_L2_SCOPE = (
    "Coordinates the refinery-operating impact of asset reliability, "
    "inspections, integrity findings, planned maintenance, and turnaround work, "
    "including availability assumptions, outage-window integration, "
    "production-plan and schedule impacts, readiness dependencies, "
    "return-to-service coordination, and escalation of material risks or "
    "constraints.\n\n"
    "Does not own maintenance strategy, engineering design authority, "
    "inspection execution, process-safety policy, work permits, contractor "
    "management, capital approval, or maintenance/turnaround execution unless "
    "separately assigned by the enterprise operating model."
)
NEW_L2_TERM_NOTES = (
    f"R1 Refining reclassification ({DATE}): new Candidate architecture node — "
    "structural placement approved; initially unpopulated; coordination-only. "
    "Review trigger: R2 evidence package / refinery maintenance and turnaround "
    "operating model."
)
NEW_L2_PURPOSE = (
    "Coordinate the refinery-operating impact of asset reliability, integrity "
    "findings, planned maintenance, and turnaround work — availability "
    "assumptions, outage-window integration, production-plan and schedule "
    "impacts, readiness dependencies, return-to-service coordination, and "
    "escalation of material risks or constraints — against approved "
    "maintenance, integrity, and turnaround commitments."
)
NEW_L2_SOURCES = (
    "SRC-OSHA-PSM-001 — process-safety management boundary: coordination "
    "interfaces with maintenance/turnaround windows and integrity inputs; "
    "excludes PSM policy ownership and maintenance/turnaround execution"
)

MIGRATED_42 = [
    "CM-1-1-4", "CM-1-1-7",
    "CM-1-1-4-1", "CM-1-1-4-2", "CM-1-1-4-3", "CM-1-1-4-4", "CM-1-1-4-5",
    "CM-1-1-4-7",
    "CM-1-1-4-1-1", "CM-1-1-4-1-2", "CM-1-1-4-1-3", "CM-1-1-4-1-4",
    "CM-1-1-4-2-1", "CM-1-1-4-2-2",
    "CM-1-1-4-4-1", "CM-1-1-4-4-2", "CM-1-1-4-4-3",
    "CM-1-1-4-7-1", "CM-1-1-4-7-2", "CM-1-1-4-7-3", "CM-1-1-4-7-4",
    "CM-1-1-4-7-5", "CM-1-1-4-7-6", "CM-1-1-4-7-7", "CM-1-1-4-7-8",
    "CM-1-1-7-1", "CM-1-1-7-2", "CM-1-1-7-3",
    "CM-1-1-7-1-1", "CM-1-1-7-1-2", "CM-1-1-7-1-3",
    "CM-1-1-7-2-1", "CM-1-1-7-2-2", "CM-1-1-7-2-3", "CM-1-1-7-2-4",
    "CM-1-1-7-2-5", "CM-1-1-7-2-6",
    "CM-1-1-7-3-1", "CM-1-1-7-3-2", "CM-1-1-7-3-3",
    "CM-1-1-4-6", "CM-1-1-4-6-1",
]
RENAMED = {"CM-1-1-4": "Refinery Planning and Optimization",
           "CM-1-1-7": "Refinery Production Planning and Scheduling"}
ASSERT_SLUGS = [  # moved concepts with no workbook row + the interface row
    "CM-1-1-7",
    "CM-1-1-4-1", "CM-1-1-4-2", "CM-1-1-4-3", "CM-1-1-4-4", "CM-1-1-4-5",
    "CM-1-1-4-1-1", "CM-1-1-4-1-2", "CM-1-1-4-1-3", "CM-1-1-4-1-4",
    "CM-1-1-4-2-1", "CM-1-1-4-2-2",
    "CM-1-1-4-4-1", "CM-1-1-4-4-2", "CM-1-1-4-4-3",
    "CM-1-1-2-9-1",
]


def tree_info(src_json, idmap=None):
    """slug -> {name, level, parent_name, breadcrumb} from the new tree.

    Breadcrumb and parent display names come from the identity-map naming
    authority (executed Step 3d labels), never from the JSON node names —
    the JSON can carry stale pre-naming-pass labels (e.g. "Manage and
    Support Emission Trading" vs executed "Manage and Support Emissions
    Trading"), which previously leaked a reverted label into a breadcrumb.
    """
    data = json.loads(Path(src_json).read_text(encoding="utf-8"))
    info = {}
    idmap = idmap or {}

    def slug_of(node):
        pid = node.get("id")
        if pid:
            return pid.replace(" ", "-").replace(".", "-")
        import unicodedata as ud
        t = ud.normalize("NFKD", node["name"]).encode("ascii", "ignore").decode()
        t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
        return f"L{node['level']}-{t}"

    def disp_name(node):
        slug = slug_of(node)
        return idmap.get(slug, {}).get("name") or node["name"]

    def rec(node, parent_name, trail):
        slug = slug_of(node)
        dn = disp_name(node)
        info[slug] = {"name": node["name"], "level": node["level"],
                      "parent_name": parent_name,
                      "breadcrumb": " > ".join(trail + [dn])}
        for c in node.get("children", []) or []:
            rec(c, dn, trail + [dn])

    for top in data:
        rec(top, None, [])
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook-in", default=_D_WORKBOOK)
    ap.add_argument("--workbook-out", default=_D_WORKBOOK)
    ap.add_argument("--identity-map", default=_D_IDENTITY_MAP)
    ap.add_argument("--src-json", default=_D_SRC_JSON)
    ap.add_argument("--cell-diff", default=_D_CELL_DIFF)
    a = ap.parse_args()

    idmap = {r["slug"]: r for r in
             json.loads(Path(a.identity_map).read_text(encoding="utf-8"))}
    # Naming authority: identity-map executed names. The JSON node names are
    # never used for display strings (see tree_info).
    tinfo = tree_info(a.src_json, idmap)

    wb = load_workbook(a.workbook_in)
    assert SHEET in wb.sheetnames
    ws = wb[SHEET]
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    for h in ("slug", "level", "name", "breadcrumb", "parent", "is_stub",
              "definition", "scope_note", "in_scope", "out_of_scope",
              "status", "concept_type_check", "primary_purpose",
              "reference_sources", "terminology_notes", "related_concepts"):
        assert h in idx, f"missing header {h}"

    # controlled vocabularies
    ws_cv = wb["Controlled vocabularies"]
    cv = {}
    for row in ws_cv.iter_rows(values_only=True):
        if row[0] and row[1]:
            cv[str(row[0]).strip().lower()] = {
                p.strip() for p in str(row[1]).split("|") if p.strip()}
    assert "approved" in cv["status"] and "pending" in cv["status"]
    assert "capability" in cv.get("concept_type_check", {"capability"})

    # snapshot before-values for the cell diff: (row_number, header) -> value
    before = {}
    slug_row = {}
    for rn, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        slug = (row[idx["slug"]] or "").strip()
        if not slug:
            continue
        assert slug not in slug_row, f"duplicate slug {slug}"
        slug_row[slug] = rn
        for h, i in idx.items():
            before[(rn, h)] = row[i]

    n_rows_before = ws.max_row
    diffs = []  # (slug, column, old, new, reason)

    def set_cell(slug, col, value, reason):
        rn = slug_row[slug]
        cell = ws.cell(row=rn, column=idx[col] + 1)
        old = before[(rn, col)]
        old_s = "" if old is None else str(old)
        new_s = "" if value is None else str(value)
        if old_s != new_s:
            diffs.append((slug, col, old_s, new_s, reason))
            cell.value = value

    # ---- 1. migrated rows: level / parent / breadcrumb / name ----
    for slug in MIGRATED_42:
        if slug not in slug_row:
            continue  # asserted below
        ti = tinfo[slug]
        assert idmap[slug]["level"] == ti["level"]
        set_cell(slug, "level", ti["level"], "R1 reparent: level shift")
        set_cell(slug, "parent", ti["parent_name"], "R1 reparent: new parent")
        set_cell(slug, "breadcrumb", ti["breadcrumb"], "R1 reparent: new path")
        if slug in RENAMED:
            set_cell(slug, "name", RENAMED[slug], "R1 rename (label only)")

    # ---- 2a. mechanical stale-label renames in semantic columns ----
    for slug, rn in slug_row.items():
        for col in SEMANTIC_COLS:
            val = before[(rn, col)]
            if val is None or not str(val).strip():
                continue
            new_val = str(val)
            for rx, new in STALE_RES:
                new_val = rx.sub(new, new_val)
            if new_val != str(val):
                set_cell(slug, col, new_val,
                         "mechanical stale-label correction (R1 §4a/4c)")

    # ---- 2b. T9c: premise / plan / plan-of-record distinction ----
    rn = slug_row["CM-1-1-4"]
    cur = str(ws.cell(row=rn, column=idx["scope_note"] + 1).value)
    addition = (" It distinguishes the plan premise (input assumptions, "
                "CM-1-1-4-1), the approved plan (the decision this concept "
                "owns), and the plan of record (the versioned registered case, "
                "CM-1-1-4-7-7).")
    assert "plan of record" not in cur
    set_cell("CM-1-1-4", "scope_note", cur + addition,
             "T9c: premise/plan/plan-of-record distinction (minimum language)")

    # ---- 2c. T10: execution counterparty ----
    for col in ("scope_note", "out_of_scope"):
        rn = slug_row["CM-1-1-7-2-6"]
        cur = str(ws.cell(row=rn, column=idx[col] + 1).value)
        if col == "scope_note":
            old_frag = "maintenance planning and turnaround execution (Refining, per the locked rule)"
        else:
            old_frag = "maintenance planning and turnaround execution (Refining)"
        assert old_frag in cur, f"T10 anchor missing in {col}"
        new_frag = ("maintenance planning and turnaround execution (Refining; "
                    "refinery maintenance capability to be modeled in R2)")
        set_cell("CM-1-1-7-2-6", col, cur.replace(old_frag, new_frag),
                 "T10: execution counterparty = Refining; R2 maintenance capability noted")

    # ---- 3. new Candidate L2 row ----
    assert NEW_L2_SLUG not in slug_row
    ti = tinfo[NEW_L2_SLUG]
    new_row = [""] * len(headers)

    def put(col, value):
        new_row[idx[col]] = value

    put("slug", NEW_L2_SLUG)
    put("level", ti["level"])
    put("name", NEW_L2_NAME)
    put("breadcrumb", ti["breadcrumb"])
    put("parent", ti["parent_name"])
    put("is_stub", "no")
    put("definition", NEW_L2_DEF)
    put("scope_note", NEW_L2_SCOPE)
    put("terminology_notes", NEW_L2_TERM_NOTES)
    put("concept_type_check", "capability")
    put("primary_purpose", NEW_L2_PURPOSE)
    put("reference_sources", NEW_L2_SOURCES)
    put("status", "approved")
    ws.append(new_row)
    slug_row[NEW_L2_SLUG] = ws.max_row
    diffs.append((NEW_L2_SLUG, "(new row)", "", NEW_L2_NAME,
                  "R1 new Candidate L2 (approved row: definition + scope note verbatim)"))

    # ---- 4. asserted rows ----
    for slug in ASSERT_SLUGS:
        assert slug not in slug_row, f"assert target already present: {slug}"
        ti = tinfo[slug]
        row = [""] * len(headers)
        row[idx["slug"]] = slug
        row[idx["level"]] = idmap[slug]["level"]
        row[idx["name"]] = idmap[slug]["name"]
        row[idx["breadcrumb"]] = ti["breadcrumb"]
        row[idx["parent"]] = ti["parent_name"]
        row[idx["is_stub"]] = "no"
        row[idx["status"]] = "pending"
        if slug == "CM-1-1-2-9-1":
            row[idx["related_concepts"]] = (
                "informs: Refinery Planning and Optimization (CM-1-1-4)")
        ws.append(row)
        slug_row[slug] = ws.max_row
        diffs.append((slug, "(new row)", "", idmap[slug]["name"],
                      "R1 asserted row (pending; was ungoverned)"
                      + (" + informs: CM-1-1-4 interface entry"
                         if slug == "CM-1-1-2-9-1" else "")))

    # ---- 5. controlled-vocabulary assertions on touched values ----
    for slug, col, old, new, _reason in diffs:
        if col == "status":
            assert new in cv["status"], f"{slug}: bad status {new}"
        if col == "concept_type_check":
            assert new in cv["concept_type_check"], f"{slug}: bad type {new}"
    # the two promoted names must not be kept as altLabels
    for slug in RENAMED:
        rn = slug_row[slug]
        alt = str(ws.cell(row=rn, column=idx["alt_labels"] + 1).value or "")
        assert "Refinery Planning" not in alt.replace(
            "Refinery Planning and Optimization", ""), slug
    # no stale references left in semantic columns
    for slug, rn in slug_row.items():
        for col in SEMANTIC_COLS:
            v = str(ws.cell(row=rn, column=idx[col] + 1).value or "")
            for rx, _new in STALE_RES:
                assert not rx.search(v), f"stale reference left: {slug}.{col}"

    wb.save(a.workbook_out)

    # ---- 6. cell diff ----
    with open(a.cell_diff, "w", encoding="utf-8") as f:
        f.write("# R1 workbook cell diff — `Review & authoring`\n\n")
        f.write(f"Rows before: {n_rows_before - 1} data rows; "
                f"rows after: {ws.max_row - 1} data rows "
                f"(+1 new Candidate L2, +16 asserted rows).\n\n")
        f.write("Only cells that changed are listed. `terminology_notes` was "
                "never touched except on the new Candidate L2 row (historical "
                "provenance is preserved verbatim).\n\n")
        cur_slug = None
        for slug, col, old, new, reason in diffs:
            if slug != cur_slug:
                f.write(f"## `{slug}`\n\n")
                cur_slug = slug
            f.write(f"### {col} — {reason}\n\n")
            if old:
                f.write(f"- before: {old}\n")
            f.write(f"- after: {new}\n\n")
    print(f"OK: workbook updated — {len(diffs)} cell changes, "
          f"{ws.max_row - 1} data rows.")
    print("cell diff:", a.cell_diff)


if __name__ == "__main__":
    main()
