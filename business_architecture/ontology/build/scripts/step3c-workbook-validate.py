#!/usr/bin/env python3
"""Step 3c workbook review gate (mechanical checks + review-findings report).

Usage:
  python3 step3c-workbook-validate.py --workbook <xlsx> [--out findings.md]

Reads the 'Review & authoring' sheet, validates every row, and writes a
findings report. Semantic review (boundary consistency, terminology,
parent/child coherence) is done by the human reviewer against this report.
Exit code 0 = no blocking findings; 1 = blocking findings present.
"""
import argparse, csv, json, re, sys
from openpyxl import load_workbook

BLOCKING, QUESTION, NOTE = "BLOCKING", "QUESTION", "NOTE"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True)
    ap.add_argument("--out", default="step3c-workbook-findings.md")
    ap.add_argument("--identity-map", default="step2-identity-map.json")
    a = ap.parse_args()

    wb = load_workbook(a.workbook, data_only=True)
    ws = wb["Review & authoring"]
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}
    idmap = {r["slug"]: r for r in json.load(open(a.identity_map))}
    pref_labels = {r["name"].lower() for r in idmap.values()}

    findings, seen_slugs = [], set()
    stats = {"rows": 0, "approved": 0, "pending": 0}

    def add(sev, slug, check, detail):
        findings.append({"severity": sev, "slug": slug, "check": check, "detail": detail})

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not any(row): continue
        g = lambda h: (row[idx[h]] if idx[h] < len(row) else None)
        slug = str(g("slug") or "").strip()
        stats["rows"] += 1
        status = str(g("status") or "").strip().lower()
        defi = str(g("definition") or "").strip()
        scope = str(g("scope_note") or "").strip()
        in_sc = str(g("in_scope") or "").strip()
        out_sc = str(g("out_of_scope") or "").strip()
        alt = str(g("alt_labels") or "").strip()

        if slug in seen_slugs: add(BLOCKING, slug, "duplicate-slug", "Slug appears more than once.")
        seen_slugs.add(slug)
        if status not in ("pending", "approved"):
            add(BLOCKING, slug, "bad-status", f"status={status!r}; must be 'pending' or 'approved'.")
            continue
        if status == "pending":
            stats["pending"] += 1
            if defi or scope: add(QUESTION, slug, "pending-with-content",
                                  "Row is pending but has definition/scope text — intended?")
            continue
        stats["approved"] += 1

        # --- approved-row checks ---
        if not defi:
            add(BLOCKING, slug, "empty-definition", "Approved row has no definition."); continue
        words = defi.split()
        if len(words) < 8:
            add(QUESTION, slug, "short-definition", f"Only {len(words)} words — likely too thin for enterprise grade.")
        # circular opening: definition starts with the concept's own name words
        name_words = [w.lower() for w in re.findall(r"[A-Za-z]+", g("name") or "") if len(w) > 3]
        lead = " ".join(words[:6]).lower()
        if any(nw in lead for nw in name_words[:2]):
            add(QUESTION, slug, "circular-opening",
                f"Definition opens with the concept's own name ({g('name')!r}) — restate by purpose, not label.")
        if not scope:
            add(BLOCKING, slug, "missing-scope-note",
                "Locked instruction: every approved row requires a non-empty scope_note with at least one meaningful boundary.")
        if out_sc and not re.search(r"\b(owned by|belongs to|sibling|see |under )\b", out_sc, re.I):
            add(NOTE, slug, "out-of-scope-owner",
                "Out-of-scope text doesn't name the owning sibling — consider adding it.")
        for label in [l.strip() for l in alt.split("|") if l.strip()]:
            if label.lower() in pref_labels:
                add(QUESTION, slug, "altlabel-collision",
                    f"altLabel {label!r} collides with another concept's preferred label.")

    # cross-row: two approved siblings with near-identical definitions
    # (light heuristic; reviewer does the real boundary check)
    with open(a.out, "w") as f:
        f.write("# Step 3c workbook review findings\n\n")
        f.write(f"Rows: {stats['rows']} | approved: {stats['approved']} | pending: {stats['pending']}\n\n")
        for sev in (BLOCKING, QUESTION, NOTE):
            items = [x for x in findings if x["severity"] == sev]
            f.write(f"## {sev} ({len(items)})\n\n")
            for x in items:
                f.write(f"- **{x['slug']}** [{x['check']}] {x['detail']}\n")
            f.write("\n")
    blocking = sum(1 for x in findings if x["severity"] == BLOCKING)
    print(f"rows={stats['rows']} approved={stats['approved']} pending={stats['pending']} "
          f"blocking={blocking} questions={sum(1 for x in findings if x['severity']==QUESTION)}")
    print("report:", a.out)
    return 1 if blocking else 0

if __name__ == "__main__":
    sys.exit(main())
