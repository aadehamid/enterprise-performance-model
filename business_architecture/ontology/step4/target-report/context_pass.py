#!/usr/bin/env python3
"""Context-confirmation pass for SoleCandidate rows (PR #120 compliance).

For each unique-label-match row, run four independent evidence tests.
Promote when >=1 test passes; hold otherwise.

Tests (strongest first):
  D approved-interface : (source, target) in an approved decision record
  A explicit-reference : target SLUG cited in source's definition or scope note
                         (never terminologyNotes; never empty identifiers;
                          no substring matches)
  C two-way            : target's own mentions point back with a semantically
                         consistent inverse verb (precedes<->follows,
                         informs<->informed-by). Anything else does NOT confirm.
  B structural-nearness: same L2/L3 branch AND verb fits its family:
                         sequence verbs require siblings; other verbs require
                         the target to be neither a strict ancestor nor a
                         strict descendant of the source (no hierarchy
                         masquerading as a relationship).
                         EXCEPTION (Hamid 2026-09-24): B never promotes
                         governed-by. Governance is a claim about authority and
                         the hierarchy says nothing about authority, so
                         closeness alone — at any level — is not evidence for
                         it. B-only governed-by rows are held for human review.

Sampling: per domain, max(10, ceil(5% of promoted)), capped by population.
"""
import re, json, csv, math, os, random
from collections import defaultdict, Counter

# Step 4 working directory: derived from this file; EPM_STEP4_DIR overrides.
BASE = os.environ.get("EPM_STEP4_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Outputs are proposals only: governed files in target-report/ are never overwritten.
OUT = os.path.join(BASE, "proposal", "target-report")
SHA = open(f"{BASE}/PINNED_SHA.txt").read().strip()
imap = {r["slug"]: r for r in json.load(open(f"{BASE}/baseline/step2-identity-map.json"))}
ttl = open(f"{BASE}/baseline/step3-taxonomy.ttl").read()

# --- literal-aware block parse; definitions + scope notes per concept ---
defs, scopes = {}, {}
parts, cur, in_lit = [], [], False
for line in ttl.split("\n"):
    cur.append(line)
    if line.count('"""') % 2 == 1:
        in_lit = not in_lit
    if line == "" and not in_lit:
        parts.append("\n".join(cur)); cur = []
parts.append("\n".join(cur))

def lit_after(block, pred):
    m = re.search(re.escape(pred) + r'\s+("""(?:.*?)"""|"(?:[^"\\]|\\.)*")', block, re.S)
    if not m:
        return ""
    v = m.group(1)
    return v[3:-3] if v.startswith('"""') else v[1:-1]

for b in parts:
    bs = b.strip()
    if not bs.startswith("proc:"):
        continue
    s = re.match(r"(proc:\S+)", bs).group(1)[5:]
    defs[s] = lit_after(bs, "skos:definition")
    scopes[s] = lit_after(bs, "skos:scopeNote")

def ancestors(slug):
    out, seen, cur = [], set(), slug
    while cur and cur not in seen:
        seen.add(cur); out.append(cur)
        cur = imap.get(cur, {}).get("parent_slug")
    return out

def l2_l3(slug):
    return [a for a in ancestors(slug) if imap.get(a, {}).get("level") in (2, 3)]

# --- mention graph (single-candidate rows, resolved or sole) ---
v2rows = list(csv.DictReader(open(f"{BASE}/target-report/target-dispositions-v2.csv")))
graph = defaultdict(list)
for r in v2rows:
    cands = r["candidate_slugs"].split(" | ") if r["candidate_slugs"] else []
    if len(cands) == 1 and r["disposition"] in ("ResolvedToConcept", "SoleCandidate"):
        graph[r["source_slug"]].append((r["verb"], cands[0]))

# approved pairs: decision records only (R1 interface). The sibling package is
# itself pending approval and must NOT feed this test.
APPROVED = {("CM-1-1-2-9-1", "CM-1-1-4")}

SEQ = {"precedes", "follows"}
INVERSE = {"precedes": "follows", "follows": "precedes",
           "informs": "informed-by", "informed-by": "informs"}

def explicit_reference(src, tgt):
    """Target slug cited in source's definition or scope note. Strict."""
    if not src or not tgt:
        return False
    text = (defs.get(src, "") + "\n" + scopes.get(src, "")).lower()
    if not text.strip():
        return False
    return re.search(r"(?<![\w-])" + re.escape(tgt.lower()) + r"(?![\w-])", text) is not None

def two_way(src, verb, tgt):
    """Backlink exists AND carries the semantically consistent inverse verb."""
    need = INVERSE.get(verb)
    if not need:
        return False
    return any(v == need for v, s in graph.get(tgt, []) if s == src)

def structural_nearness(src, verb, tgt):
    """Same L2/L3 branch, plus deterministic per-family verb fit."""
    if not src or not tgt or src == tgt:
        return False
    if not (set(l2_l3(src)) & set(l2_l3(tgt))):
        return False
    if verb in SEQ:
        p = imap.get(src, {}).get("parent_slug")
        return p is not None and p == imap.get(tgt, {}).get("parent_slug")
    # other families: hierarchy is not a relationship
    if tgt in ancestors(src)[1:] or src in ancestors(tgt)[1:]:
        return False
    return True

def sample_n(pop):
    return min(pop, max(10, math.ceil(0.05 * pop)))

def run_pass():
    results = []
    for r in v2rows:
        if r["disposition"] != "SoleCandidate":
            continue
        cands = r["candidate_slugs"].split(" | ")
        if len(cands) != 1:
            continue
        src, tgt = r["source_slug"], cands[0]
        tests = []
        if (src, tgt) in APPROVED:
            tests.append("D:approved-interface")
        if explicit_reference(src, tgt):
            tests.append("A:explicit-reference")
        back = sorted({v for v, s in graph.get(tgt, []) if s == src})
        if two_way(src, r["verb"], tgt):
            tests.append(f"C:two-way(back={INVERSE[r['verb']]})")
        elif back:
            tests.append(f"C:two-way-absent(back-verbs={'/'.join(back)})")
        if structural_nearness(src, r["verb"], tgt):
            tests.append("B:structural-nearness")
        if r["row_id"] in HAMID_APPROVED_GOVERNED_BY:
            tests.append("D:hamid-verdict(2026-09-25)")
        results.append((r, tgt, tests))
    return results

def _real(r, tests):
    """Tests that count toward promotion. B never counts for governed-by
    (Hamid 2026-09-24)."""
    real = [t for t in tests if not t.startswith("C:two-way-absent")]
    if r["verb"] == "governed-by":
        real = [t for t in real if t != "B:structural-nearness"]
    return real

# Hamid's explicit governed-by verdicts, 2026-09-25: these 13 rows are approved
# for emission as core:governedBy on definition/policy/authority evidence (not
# B). His recorded verdict is the evidence basis; the B-exclusion rule still
# applies to every other governed-by row.
HAMID_APPROVED_GOVERNED_BY = {
    "REL-00050", "REL-00067", "REL-00190", "REL-00394", "REL-00399",
    "REL-00406", "REL-00858", "REL-00907", "REL-00937", "REL-01005",
    "REL-01228", "REL-01256", "REL-01313",
}

def main():
    os.makedirs(OUT, exist_ok=True)
    results = run_pass()
    promoted = [x for x in results if _real(x[0], x[2])]
    held = [x for x in results if x not in promoted]
    print(f"SoleCandidate rows: {len(results)} | promoted: {len(promoted)} | held: {len(held)}")
    tc = Counter()
    for r, _, tests in promoted:
        for t in _real(r, tests):
            tc[t.split("(")[0].split(":")[0]] += 1
    print("test pass counts (rows may pass multiple):", dict(tc))

    ORDER = {"D": 0, "A": 1, "C": 2, "B": 3}
    out = []
    for r, tgt, tests in results:
        real = _real(r, tests)
        b_only_gov = (r["verb"] == "governed-by"
                      and "B:structural-nearness" in tests
                      and not real)
        tests_shown = (list(real) if not b_only_gov
                       else ["B:structural-nearness (not evidence for governed-by)"])
        primary = min(real, key=lambda t: ORDER[t[0]]) if real else ""
        back_note = next((t for t in tests if t.startswith("C:two-way-absent")), "")
        out.append({"row_id": r["row_id"], "source_slug": r["source_slug"],
                    "verb": r["verb"], "target_slug": tgt,
                    "target_label": imap.get(tgt, {}).get("name", ""),
                    "branch_domain": r["branch_domain"],
                    "tests_passed": " | ".join(tests_shown),
                    "backlink_note": back_note,
                    "primary_test": primary.split("(")[0] if primary else "",
                    "outcome": "PROMOTE" if real else "HOLD",
                    "baseline_sha": SHA})
    with open(f"{OUT}/context-pass.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print("wrote proposal/target-report/context-pass.csv")

    hc = Counter(x[0]["branch_domain"] for x in held)
    print("held by domain:", dict(hc))

    # compliant per-domain sampling of promoted rows
    random.seed(42)
    by_dom = defaultdict(list)
    for o in out:
        if o["outcome"] == "PROMOTE":
            by_dom[o["branch_domain"]].append(o["row_id"])
    with open(f"{OUT}/context-sample.txt", "w") as f:
        f.write(f"# context sample, seed 42, baseline {SHA}\n")
        for dom in sorted(by_dom):
            pop = by_dom[dom]
            n = sample_n(len(pop))
            samp = sorted(random.sample(pop, n))
            f.write(f"\n## {dom} (pop {len(pop)}, sample {n})\n")
            f.write("\n".join(samp) + "\n")
            print(f"sample {dom}: {n}/{len(pop)}")
    print("wrote proposal/target-report/context-sample.txt")

if __name__ == "__main__":
    main()
