#!/usr/bin/env python3
"""First-pass classifier for the Q11/Q12 row-level relationship-target
disposition report. Mechanical matching only; judgment buckets are
printed for manual review. Reads the committed TTL + identity map."""
import re, json, csv, os, sys
from collections import Counter, defaultdict

# Paths derived from this file; EPM_STEP4_DIR / EPM_REPO_ROOT override.
STEP4 = os.environ.get("EPM_STEP4_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TTL_REL = "business_architecture/ontology/build/output/step3-taxonomy.ttl"


def _find_repo():
    # In-repo layout (<repo>/business_architecture/ontology/step4), then the
    # separate-workspace layout (<ws>/ontology-step4 beside <ws>/enterprise-performance-model).
    for cand in (os.path.join(STEP4, "..", "..", ".."),
                 os.path.join(os.path.dirname(os.path.abspath(STEP4)), "enterprise-performance-model")):
        if os.path.isfile(os.path.join(cand, _TTL_REL)):
            return os.path.abspath(cand)
    sys.exit(f"classify.py: repo not found from {STEP4}; set EPM_REPO_ROOT")


REPO = os.environ.get("EPM_REPO_ROOT") or _find_repo()
# Outputs are proposals only: governed files in target-report/ are never overwritten.
OUT = os.path.join(STEP4, "proposal", "target-report")
TTL = f"{REPO}/business_architecture/ontology/build/output/step3-taxonomy.ttl"
IDMAP = f"{REPO}/business_architecture/ontology/build/output/step2-identity-map.json"

ttl = open(TTL).read()
imap = json.load(open(IDMAP))

by_slug = {}
def walk(node):
    if isinstance(node, dict):
        if node.get("slug"):
            by_slug[node["slug"]] = node
        for v in node.values(): walk(v)
    elif isinstance(node, list):
        for v in node: walk(v)
walk(imap)

# L1 ancestor for branch/domain context
def l1_of(slug):
    seen = set()
    cur = slug
    while cur and cur not in seen:
        seen.add(cur)
        rec = by_slug.get(cur)
        if not rec: return None
        if rec.get("level") == 1: return rec
        cur = rec.get("parent_slug")
    return None

# name index: normalized current preferred label -> slugs
name_idx = defaultdict(list)
for slug, rec in by_slug.items():
    name_idx[rec["name"].strip().lower()].append(slug)

slug_in_parens = re.compile(r"\(([A-Za-z]+-\d[\d-]*)\)\s*$")

# parse mentions: track current subject (proc:SLUG a skos:Concept), then its relatedConcepts literal
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
            rows.append({"subject": current, "verb": verb.strip(), "target": tgt.strip()})
print("mentions:", len(rows))

# Manual dispositions for unmatched targets (Q11 decisions + Q12 amendment).
# Format: target -> (disposition, confidence, candidates, evidence, reason,
#                    emission, review_trigger, decision_ref)
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

def sibling_resolve(source_slug, candidates):
    """Q12 contextual-evidence rule: if the source's parent matches exactly
    one candidate's parent (same decomposition pattern), that candidate is
    the contextually identified target."""
    src = by_slug.get(source_slug, {})
    sparent = src.get("parent_slug")
    if not sparent:
        return None
    matched = [c for c in candidates
               if by_slug.get(c, {}).get("parent_slug") == sparent]
    return matched[0] if len(matched) == 1 else None

def classify(tgt, source_slug=None):
    """Returns (disposition, confidence, candidates, evidence, reason,
    emission, review_trigger, decision_ref)."""
    t = tgt.strip()
    if t in MANUAL:
        return MANUAL[t]
    m = slug_in_parens.search(t)
    if m and m.group(1) in by_slug:
        s = m.group(1)
        return ("ResolvedToConcept", "Resolved", [s],
                f"stable identifier {s} carried in mention text",
                f"target carries its slug; resolves to {by_slug[s]['name']}",
                "emit automatically after subject/target existence checks", "", "Q11+Q12")
    key = t.lower()
    if key in name_idx:
        cands = name_idx[key]
        if len(cands) == 1:
            return ("ResolvedToConcept", "ContextualResolved", cands,
                    "unique exact preferred-label match",
                    f"unique label match to {cands[0]}; no contradicting context",
                    "emit after mechanical uniqueness validation", "", "Q11+Q12")
        sib = sibling_resolve(source_slug, cands) if source_slug else None
        if sib:
            return ("ResolvedToConcept", "ContextualInferredSibling", [sib],
                    f"source and candidate share parent {by_slug[sib]['parent_slug']} (same decomposition pattern)",
                    f"sibling-step inference within {by_slug[sib]['parent_slug']} — held for human review",
                    "HOLD: targeted human review before emission", "", "Q12")
        return ("AmbiguousDeferred", "Deferred", cands,
                "exact label matches multiple concepts; no single contextual target",
                f"label collision across {len(cands)} concepts; source context does not isolate one",
                "no triple; retain candidates + review trigger",
                "label remediation or domain-owner clarification",
                "Q12")
    if t in by_slug:
        return ("ResolvedToConcept", "Resolved", [t],
                "mention is the concept slug",
                f"target is slug {t}",
                "emit automatically after subject/target existence checks", "", "Q11+Q12")
    return ("REVIEW_UNMATCHED", "Deferred", [],
            "no label or slug match", "", "PENDING", "", "")

# classify distinct (target, source) pairs — sibling rule needs the source
distinct = {}
for r in rows:
    distinct.setdefault((r["target"], r["subject"]),
                        classify(r["target"], r["subject"]))

needs_review = {k: c for k, c in distinct.items() if c[0] == "REVIEW_UNMATCHED"}
print("distinct (target, source) pairs:", len(distinct),
      "| still unmatched:", len(needs_review))
auto = Counter(c[0] for c in distinct.values())
print("disposition buckets:", dict(auto))

# branch/domain for sources
def branch_of(slug):
    l1 = l1_of(slug)
    return l1["name"] if l1 else ""

import os
os.makedirs(OUT, exist_ok=True)
with open(f"{OUT}/target-dispositions-v1.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source_slug", "source_label", "branch_domain", "verb",
                "raw_target", "disposition", "candidate_slugs",
                "candidate_labels", "evidence", "confidence",
                "emission_decision", "reason", "review_trigger",
                "decision_reference"])
    for r in rows:
        disp, conf, cands, ev, reason, emit, trigger, ref = distinct[(r["target"], r["subject"])]
        src = by_slug.get(r["subject"], {})
        clabels = " | ".join(by_slug[s]["name"] for s in cands if s in by_slug)
        w.writerow([r["subject"], src.get("name", ""), branch_of(r["subject"]),
                    r["verb"], r["target"], disp,
                    " | ".join(cands), clabels, ev, conf, emit,
                    reason, trigger, ref])
print("wrote", f"{OUT}/target-dispositions-v1.csv")

# summary of non-resolved rows for the review narrative
print("\n=== non-ResolvedToConcept rows (verb, target, count) ===")
from collections import Counter as _C
nonres = _C()
for r in rows:
    d = distinct[(r["target"], r["subject"])][0]
    if d != "ResolvedToConcept":
        nonres[(d, r["verb"], r["target"])] += 1
for (d, v, t), n in sorted(nonres.items(), key=lambda x: (x[0][0], -x[1])):
    print(f"{n:3}x [{d}] {v}: {t[:70]}")
