#!/usr/bin/env python3
"""Step 3c workbook review gate (mechanical checks + review-findings report).

Synced 2026-09-19 to the post-#31 semantic-intake workbook. This is the
same class of follow-up as #30 (lock the reviewer guide, then make the
script enforce it). The locked human text is
`step3c-reviewer-instructions.md` v2026-09-19.

Why this sync exists
--------------------
#31 evolved the definition workbook into a 6-sheet semantic-intake
workbook (Phase 1/2 fields, Controlled vocabularies, Reference register,
status values `blocked` / `retired`). #32 then approved five L4 rows
against that contract. The #30 gate still described the old 2-sheet,
`pending|approved`-only workbook, so an approved row with an empty
`primary_purpose` or a made-up source id would have passed.

What this script does *not* do
------------------------------
- Emit RDF or merge into the taxonomy. New fields stay intake-only.
- Backfill Phase 1 onto the 15 rows approved in #29. That is a semantic
  pass, not a gate sync. Those slugs live in PRE_INTAKE_APPROVED: empty
  Phase 1 is a NOTE (visible, not silent), not BLOCKING.
- Soften the #30 finding on `CM-1-3-3-5-6` (approved, no scope_note).
  Still BLOCKING; still waiting on a definition follow-up.

Usage:
  python3 step3c-workbook-validate.py --workbook <xlsx> [--out findings.md]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from openpyxl import load_workbook

BLOCKING, QUESTION, NOTE = "BLOCKING", "QUESTION", "NOTE"

# Workbook Controlled vocabularies sheet, field `status`.
# `blocked` / `retired` are legal parking states; they never merge.
STATUS_OK = {"pending", "approved", "blocked", "retired"}

# Only these may sit on an approved row. mixed/needs-review and
# not-process require Hamid's decision and must stay pending (or move
# to blocked/retired after that decision).
APPROVABLE_TYPE = {"process", "capability"}

CONCEPT_TYPE_OK = {
    "process",
    "capability",
    "mixed/needs-review",
    "not-process",
}

# Rows approved in #29, before #31 invented Phase 1 columns.
# Dated 2026-09-18. Do not grow this set — new approvals must satisfy
# Phase 1. Do not delete a slug from this set as a way to "force"
# backfill; run an authored backfill PR instead.
PRE_INTAKE_APPROVED = {
    "CM-1",
    "CM-1-1-2",
    "CM-1-1-4",
    "CM-1-1-5",
    "CM-1-1-6",
    "CM-1-3-3-5-6",
    "L1-refining",
    "L1-midstream",
    "L1-supply-chain-mgmt",
    "L1-finance",
    "L1-shared-services",
    "L1-process-excellence-it",
    "L1-human-resources",
    "L1-legal-corp-comm",
    "L1-ehs-gov-reporting",
}

# Review & authoring headers that must exist after #31. Missing any of
# these means someone pointed the gate at a pre-intake workbook.
REQUIRED_HEADERS = (
    "slug",
    "name",
    "definition",
    "scope_note",
    "in_scope",
    "out_of_scope",
    "alt_labels",
    "status",
    "concept_type_check",
    "primary_purpose",
    "reference_sources",
    "open_questions",
    "process_horizon",
)

# First token of a reference_sources pipe-segment. #32 cites bare
# source_ids (`SRC-EIA-GLOSS-001`); the column guide also allows a
# relevance note after the id.
SOURCE_ID_RE = re.compile(r"(SRC-[A-Z0-9-]+)")

HERE = Path(__file__).resolve().parent
DEFAULT_IDENTITY = HERE.parent / "output" / "step2-identity-map.json"


def cell(value) -> str:
    return str(value or "").strip()


def split_pipe(value) -> list[str]:
    return [part.strip() for part in cell(value).split("|") if part.strip()]


def source_id_from_segment(segment: str) -> str | None:
    match = SOURCE_ID_RE.search(segment)
    return match.group(1) if match else None


def load_reference_ids(wb) -> set[str]:
    """Source ids from the Reference register sheet (header row `source_id`)."""
    if "Reference register" not in wb.sheetnames:
        return set()
    ws = wb["Reference register"]
    header_row = None
    source_col = 0
    for row in ws.iter_rows(min_row=1, max_row=20, values_only=False):
        values = [cell(c.value) for c in row]
        if "source_id" in values:
            header_row = row[0].row
            source_col = values.index("source_id")
            break
    if header_row is None:
        return set()
    ids = set()
    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        sid = cell(row[source_col] if source_col < len(row) else "")
        if sid:
            ids.add(sid)
    return ids


def load_allowed_values(wb, field: str, fallback: set[str]) -> set[str]:
    """Parse `Field | Allowed values` from Controlled vocabularies.

    The sheet is the governed list. Fallback exists only so a stripped
    test workbook still has a deterministic vocab.
    """
    if "Controlled vocabularies" not in wb.sheetnames:
        return set(fallback)
    ws = wb["Controlled vocabularies"]
    for row in ws.iter_rows(min_row=1, values_only=True):
        if cell(row[0]).lower() == field:
            raw = cell(row[1] if len(row) > 1 else "")
            return {part.strip() for part in raw.split("|") if part.strip()} or set(fallback)
    return set(fallback)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True)
    ap.add_argument("--out", default="step3c-workbook-findings.md")
    ap.add_argument(
        "--identity-map",
        default=str(DEFAULT_IDENTITY),
        help="Identity map JSON (defaults next to this script under ../output/)",
    )
    a = ap.parse_args()

    wb = load_workbook(a.workbook, data_only=True)
    if "Review & authoring" not in wb.sheetnames:
        print("missing sheet: Review & authoring", file=sys.stderr)
        return 1
    ws = wb["Review & authoring"]
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    missing = [h for h in REQUIRED_HEADERS if h not in idx]
    if missing:
        print("workbook is missing post-#31 headers: " + ", ".join(missing), file=sys.stderr)
        print("point --workbook at the semantic-intake xlsx, not a pre-#31 copy", file=sys.stderr)
        return 1

    idmap = {r["slug"]: r for r in json.load(open(a.identity_map))}
    pref_labels = {r["name"].lower() for r in idmap.values()}
    registered_sources = load_reference_ids(wb)
    horizon_ok = load_allowed_values(
        wb,
        "process_horizon",
        {
            "strategic",
            "tactical",
            "monthly",
            "weekly",
            "daily",
            "intraday",
            "event-driven",
            "continuous",
            "periodic",
            "not-applicable",
            "needs-review",
        },
    )

    findings = []
    seen = set()
    stats = {"rows": 0, "approved": 0, "pending": 0, "blocked": 0, "retired": 0}

    def add(sev, slug, check, detail):
        findings.append({"severity": sev, "slug": slug, "check": check, "detail": detail})

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue

        def g(h):
            i = idx[h]
            return row[i] if i < len(row) else None

        slug = cell(g("slug"))
        stats["rows"] += 1
        status = cell(g("status")).lower()
        defi = cell(g("definition"))
        scope = cell(g("scope_note"))
        out_sc = cell(g("out_of_scope"))
        alt = cell(g("alt_labels"))
        concept_type = cell(g("concept_type_check"))
        purpose = cell(g("primary_purpose"))
        sources = cell(g("reference_sources"))
        questions = cell(g("open_questions"))
        horizon = cell(g("process_horizon"))

        if slug in seen:
            add(BLOCKING, slug, "duplicate-slug", "Slug appears more than once.")
        seen.add(slug)

        if status not in STATUS_OK:
            add(
                BLOCKING,
                slug,
                "bad-status",
                f"status={status!r}; must be one of {sorted(STATUS_OK)} "
                "(workbook Controlled vocabularies, post-#31).",
            )
            continue

        if concept_type and concept_type not in CONCEPT_TYPE_OK:
            add(
                BLOCKING,
                slug,
                "bad-concept-type",
                f"concept_type_check={concept_type!r}; must match Controlled vocabularies.",
            )

        if horizon and horizon not in horizon_ok:
            add(
                BLOCKING,
                slug,
                "bad-process-horizon",
                f"process_horizon={horizon!r}; must match Controlled vocabularies.",
            )

        # blocked / retired are parking states. Count them; do not run
        # the approved-row merge gate. A later tree pass (see PTC-001)
        # is what retires or moves the node in the repo JSON.
        if status in ("blocked", "retired"):
            stats[status] += 1
            continue

        if status == "pending":
            stats["pending"] += 1
            # Draft definition text on a pending row is fine and common.
            # Only ask when it looks like someone forgot to flip status.
            if defi or scope:
                add(
                    QUESTION,
                    slug,
                    "pending-with-content",
                    "Row is pending but has definition/scope text — intended?",
                )
            continue

        stats["approved"] += 1

        # --- approved-row checks (merge gate) ---
        if questions:
            add(
                BLOCKING,
                slug,
                "approved-with-open-questions",
                "Locked instruction: a material open_questions value cannot sit on an approved row.",
            )

        if concept_type and concept_type not in APPROVABLE_TYPE:
            add(
                BLOCKING,
                slug,
                "unapprovable-concept-type",
                f"concept_type_check={concept_type!r} cannot be approved without Hamid's decision.",
            )

        pre_intake = slug in PRE_INTAKE_APPROVED
        missing_phase1 = []
        if not concept_type:
            missing_phase1.append("concept_type_check")
        if not purpose:
            missing_phase1.append("primary_purpose")
        if not sources:
            missing_phase1.append("reference_sources")
        if missing_phase1:
            if pre_intake:
                # Explicit grandfather. Same stance as #30 on the
                # pre-existing CM-1-3-3-5-6 scope-note gap: flag it,
                # do not silently skip, do not rewrite the row here.
                add(
                    NOTE,
                    slug,
                    "pre-intake-missing-phase-1",
                    "Approved in #29 before semantic intake; empty "
                    + ", ".join(missing_phase1)
                    + ". Not blocking. Backfill in a later authored pass — "
                    "do not grow PRE_INTAKE_APPROVED.",
                )
            else:
                add(
                    BLOCKING,
                    slug,
                    "missing-phase-1",
                    "Post-#31 approval requires concept_type_check, "
                    "primary_purpose, and reference_sources. Missing: "
                    + ", ".join(missing_phase1)
                    + ".",
                )

        if sources:
            if not registered_sources:
                add(
                    QUESTION,
                    slug,
                    "reference-register-unreadable",
                    "reference_sources is set but the Reference register sheet has no source_id rows.",
                )
            for segment in split_pipe(sources):
                sid = source_id_from_segment(segment)
                if not sid:
                    add(
                        BLOCKING,
                        slug,
                        "source-id-unparseable",
                        f"reference_sources segment {segment!r} has no SRC-* id.",
                    )
                elif sid not in registered_sources:
                    add(
                        BLOCKING,
                        slug,
                        "unknown-source-id",
                        f"{sid} is not on the Reference register. Register the source before citing it.",
                    )

        if not defi:
            add(BLOCKING, slug, "empty-definition", "Approved row has no definition.")
            continue
        words = defi.split()
        if len(words) < 8:
            add(
                QUESTION,
                slug,
                "short-definition",
                f"Only {len(words)} words — likely too thin for enterprise grade.",
            )
        # Circular definition: the definition restates the label instead of
        # explaining it — "Refinery Planning is the process of refinery
        # planning". Reusing a domain noun is NOT circular: "Regional
        # Optimization" must be free to say "regional". The pre-#34 test
        # substring-matched either of the first two label words anywhere in the
        # first six words, which fired on 10 rows, none of them circular,
        # including four approved L3 parents. Now anchored at the opening.
        name = (g("name") or "").strip()
        if name:
            name_pat = r"\s+".join(re.escape(w) for w in name.split())
            lead_raw = " ".join(words[:14])
            circular = re.match(
                rf"^(the\s+)?{name_pat}\b\s*(is|are|means|refers to|covers|involves|:|,|\u2014|-|$)",
                lead_raw,
                re.I,
            ) or re.search(
                rf"\b(is|are)\s+the\s+(process|activity|practice|act|function)\s+of\s+{name_pat}\b",
                lead_raw,
                re.I,
            )
            if circular:
                add(
                    QUESTION,
                    slug,
                    "circular-definition",
                    f"Definition restates the label ({name!r}) instead of explaining it — define by purpose.",
                )
        if not scope:
            add(
                BLOCKING,
                slug,
                "missing-scope-note",
                "Locked instruction: every approved row requires a non-empty scope_note with at least one meaningful boundary.",
            )
        # NOTE, not BLOCKING: #30 locked "do not invent an owner". A
        # missing owner name is a hint, not a failed merge.
        # Recognises the two conventions actually in use: a prose owner phrase,
        # and a trailing parenthetical owner or slug — "trade execution (Supply
        # And Trading)", "(CM-1-1-2-10)". Pre-#34 this only matched the prose
        # form and noted all five #32 rows, each of which does name its owners.
        _owner_named = re.search(
            r"\b(owned by|belongs to|sibling|see |under )\b", out_sc or "", re.I
        ) or re.search(r"\(\s*(?:CM-[\d-]+|L\d[\w-]*|[A-Z][^()]{2,})\)", out_sc or "")
        if out_sc and not _owner_named:
            add(
                NOTE,
                slug,
                "out-of-scope-owner",
                "Out-of-scope text doesn't name the owning sibling — add it only when that owner is already in the taxonomy.",
            )
        for label in split_pipe(alt):
            if label.lower() in pref_labels:
                add(
                    QUESTION,
                    slug,
                    "altlabel-collision",
                    f"altLabel {label!r} collides with another concept's preferred label.",
                )

    # cross-row: two approved siblings with near-identical definitions
    # (light heuristic; reviewer does the real boundary check)
    with open(a.out, "w") as f:
        f.write("# Step 3c workbook review findings\n\n")
        f.write(
            f"Rows: {stats['rows']} | approved: {stats['approved']} | "
            f"pending: {stats['pending']} | blocked: {stats['blocked']} | "
            f"retired: {stats['retired']}\n\n"
        )
        f.write(
            "Gate: step3c-reviewer-instructions.md v2026-09-19 "
            "(semantic-intake sync after #31/#32). "
            "PRE_INTAKE_APPROVED empty Phase 1 is NOTE, not BLOCKING.\n\n"
        )
        for sev in (BLOCKING, QUESTION, NOTE):
            items = [x for x in findings if x["severity"] == sev]
            f.write(f"## {sev} ({len(items)})\n\n")
            for x in items:
                f.write(f"- **{x['slug']}** [{x['check']}] {x['detail']}\n")
            f.write("\n")
    blocking = sum(1 for x in findings if x["severity"] == BLOCKING)
    print(
        f"rows={stats['rows']} approved={stats['approved']} pending={stats['pending']} "
        f"blocked={stats['blocked']} retired={stats['retired']} "
        f"blocking={blocking} questions={sum(1 for x in findings if x['severity']==QUESTION)} "
        f"notes={sum(1 for x in findings if x['severity']==NOTE)}"
    )
    print("report:", a.out)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
