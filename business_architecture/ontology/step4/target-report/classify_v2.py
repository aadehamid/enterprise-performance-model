#!/usr/bin/env python3
"""Target disposition classifier v2 — regenerated against the pinned main SHA.

Reads baseline/step3-taxonomy.ttl + baseline/step2-identity-map.json
(pinned at PINNED_SHA.txt). Emits one row per relationship mention with
a row_id (used as the verb-evidence key in release artifacts).

Changes vs v1:
- unique exact preferred-label matches are marked SoleCandidate
  (candidate found, NOT resolved) pending the context-confirmation pass.
  PR #120: a label match only finds candidates; it never resolves.
- baseline_sha recorded on every row (release-checklist requirement).
"""
import re, json, csv, os
from collections import Counter, defaultdict

# Step 4 working directory: derived from this file; EPM_STEP4_DIR overrides.
BASE = os.environ.get("EPM_STEP4_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Outputs are proposals only: governed files in target-report/ are never overwritten.
OUT = os.path.join(BASE, "proposal", "target-report")
TTL = f"{BASE}/baseline/step3-taxonomy.ttl"
IDMAP = f"{BASE}/baseline/step2-identity-map.json"
SHA = open(f"{BASE}/PINNED_SHA.txt").read().strip()

ttl = open(TTL).read()
imap = json.load(open(IDMAP))
by_slug = {r["slug"]: r for r in imap if r.get("slug")}

def l1_of(slug):
    seen, cur = set(), slug
    while cur and cur not in seen:
        seen.add(cur)
        rec = by_slug.get(cur)
        if not rec: return None
        if rec.get("level") == 1: return rec
        cur = rec.get("parent_slug")
    return None

name_idx = defaultdict(list)
for slug, rec in by_slug.items():
    name_idx[rec["name"].strip().lower()].append(slug)

slug_in_parens = re.compile(r"\(([A-Za-z]+-\d[\d-]*)\)\s*$")

rows = []
current = None
for line in ttl.splitlines():
    m = re.match(r"proc:([A-Za-z]+-\d[\d-]*)\s+a\s+skos:Concept", line)
    if m:
        current = m.group(1)
        continue
    m = re.search(r'intake:relatedConcepts\s+"([^"]*)"', line)
    if m and current:
        for part in m.group(1).split("|"):
            part = part.strip()
            if not part or ":" not in part:
                continue
            verb, tgt = part.split(":", 1)
            rows.append({"subject": current, "verb": verb.strip(),
                         "target": tgt.strip()})
print("mentions:", len(rows))

MANUAL = {
    "Data Governance": (
        "ExternalGovernanceReference", "Deferred", [],
        "Q11: cross-cutting enterprise domain",
        "Data Governance is an enterprise governance domain, never a proc: node under Commercial",
        "retain via approved future property; no process triple",
        "implementation design of governance-reference property",
        "Q11"),
    "contemporaneous assumption basis for Regional Backcasting": (
        "StructuredFlowValue", "Deferred", [],
        "Q11/Q5: produced information value (intake:primaryOutput-style produces: verb)",
        "information flowing into Regional Backcasting, not an activity; governed structured flow value per Q5",
        "retain as governed structured flow value; no process triple",
        "consumer needing InformationObject identity (Q5 revisit trigger)",
        "Q11"),
    "Monthly Operating Plan": (
        "StructuredFlowValue", "Deferred", [],
        "Q11: plan-of-record artifact (produces: verb)",
        "plan artifact, not a process, per the R1 plan-vs-artifact distinction",
        "retain as governed structured flow value; no process triple",
        "consumer needing plan-artifact identity",
        "Q11"),
    "Manage Trading Books & Strategies Structure": (
        "ResolvedToConcept", "ContextualResolved", ["CM-1-2-2-3-1"],
        "Q11 correction (2026-09-22): batch 12 split this into Establish And Maintain Book Structure",
        "phrase maps to CM-1-2-2-3-1 per the approved batch 12 split; labels aren't identity",
        "emit process-dependency triple",
        "",
        "Q11"),
    "Network Design": (
        "AmbiguousDeferred", "Deferred", ["CM-1-3-3-4"],
        "Q12 amendment (2026-09-22): bare mention on Brand Imaging row; network type uncertain",
        "may mean retail/supply/distribution/terminal/channel network design; plausibility is not evidence",
        "no triple; retain candidates + review trigger",
        "R2 network-design decomposition or first consumer need",
        "Q11+Q12"),
}

def sibling_candidates(source_slug, candidates):
    src = by_slug.get(source_slug, {})
    sparent = src.get("parent_slug")
    if not sparent:
        return []
    return [c for c in candidates
            if by_slug.get(c, {}).get("parent_slug") == sparent]

def classify(tgt, source_slug=None):
    t = tgt.strip()
    if t in MANUAL:
        return MANUAL[t]
    m = slug_in_parens.search(t)
    if m and m.group(1) in by_slug:
        s = m.group(1)
        return ("ResolvedToConcept", "StableIdentifier", [s],
                f"stable identifier {s} carried in mention text",
                f"target carries its slug; resolves to {by_slug[s]['name']}",
                "emit automatically after subject/target existence checks", "", "Q11+Q12")
    key = t.lower()
    if key in name_idx:
        cands = name_idx[key]
        if len(cands) == 1:
            return ("SoleCandidate", "CandidateOnly", cands,
                    "unique exact preferred-label match (candidate filter only, per PR #120)",
                    f"label filter leaves one candidate: {cands[0]}; resolution requires context evidence",
                    "HOLD: context-confirmation pass", "", "Q12")
        sibs = sibling_candidates(source_slug, cands) if source_slug else []
        if len(sibs) == 1:
            return ("ResolvedToConcept", "ContextualInferredSibling", sibs,
                    f"source and candidate share parent {by_slug[sibs[0]]['parent_slug']} (same decomposition pattern)",
                    "sibling-step inference — human review required before emission",
                    "HOLD: targeted human review before emission", "", "Q12")
        return ("AmbiguousDeferred", "Deferred", cands,
                "exact label matches multiple concepts; no single contextual target",
                f"label collision across {len(cands)} concepts; source context does not isolate one",
                "no triple; retain candidates + review trigger",
                "label remediation or domain-owner clarification",
                "Q12")
    if t in by_slug:
        return ("ResolvedToConcept", "StableIdentifier", [t],
                "mention is the concept slug",
                f"target is slug {t}",
                "emit automatically after subject/target existence checks", "", "Q11+Q12")
    return ("REVIEW_UNMATCHED", "Deferred", [],
            "no label or slug match", "", "PENDING", "", "")

distinct = {}
for r in rows:
    distinct.setdefault((r["target"], r["subject"]),
                        classify(r["target"], r["subject"]))

needs_review = {k: c for k, c in distinct.items() if c[0] == "REVIEW_UNMATCHED"}
print("distinct (target, source) pairs:", len(distinct),
      "| still unmatched:", len(needs_review))
print("disposition buckets:", dict(Counter(c[0] for c in distinct.values())))

def branch_of(slug):
    l1 = l1_of(slug)
    return l1["name"] if l1 else ""

os.makedirs(OUT, exist_ok=True)
with open(f"{OUT}/target-dispositions-v2.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["row_id", "baseline_sha", "source_slug", "source_label",
                "branch_domain", "verb", "raw_target", "disposition",
                "candidate_slugs", "candidate_labels", "evidence", "confidence",
                "emission_decision", "reason", "review_trigger",
                "decision_reference"])
    for i, r in enumerate(rows, start=1):
        disp, conf, cands, ev, reason, emit, trigger, ref = distinct[(r["target"], r["subject"])]
        src = by_slug.get(r["subject"], {})
        clabels = " | ".join(by_slug[s]["name"] for s in cands if s in by_slug)
        w.writerow([f"REL-{i:05d}", SHA, r["subject"], src.get("name", ""),
                    branch_of(r["subject"]), r["verb"], r["target"], disp,
                    " | ".join(cands), clabels, ev, conf, emit,
                    reason, trigger, ref])
print("wrote proposal/target-report/target-dispositions-v2.csv")

nonres = Counter()
for r in rows:
    d = distinct[(r["target"], r["subject"])][0]
    if d != "ResolvedToConcept":
        nonres[(d, r["verb"], r["target"])] += 1
print("\n=== non-ResolvedToConcept rows ===")
for (d, v, t), n in sorted(nonres.items(), key=lambda x: (x[0][0], -x[1])):
    print(f"{n:3}x [{d}] {v}: {t[:70]}")
