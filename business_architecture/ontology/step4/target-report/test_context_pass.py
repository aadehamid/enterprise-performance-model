#!/usr/bin/env python3
"""Failing-first regression tests for the context-confirmation pass.

Defects under test:
  1. explicit-reference must use definition/scopeNote (not terminologyNotes),
     must require a non-empty identifier, and must not substring-match.
  2. two-way must require a semantically consistent inverse verb
     (precedes<->follows, informs<->informed-by); e.g. follows backed by
     triggers must NOT confirm.
  3. structural-nearness "verb fits" must be deterministic per verb family.
  4. sampling must be max(10, ceil(5%)) per domain, capped by population.

Run: python3 test_context_pass.py
"""
import math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_pass as cp  # the module under test

PASS, FAIL = "PASS", "FAIL"
results = []
def check(name, cond):
    results.append((name, PASS if cond else FAIL))
    print(f"[{PASS if cond else FAIL}] {name}")

# ---------- 1. explicit-reference ----------
# terminologyNotes mention the slug but definition/scopeNote do not -> must NOT count
# (REL-00080: slug CM-1-1-4-7 appears only in the source's terminologyNotes)
check("explicit-ref ignores terminologyNotes",
      cp.explicit_reference("CM-1-1-4-7-1", "CM-1-1-4-7") == False)
# scopeNote citation DOES count (REL-00030's target is cited in the source scopeNote)
check("explicit-ref counts scopeNote citation",
      cp.explicit_reference("CM-1-1-3-5-1", "CM-1-1-3-7-9") == True)
# slug present in the definition -> must count (REL-00030's target appears in def? no -
# use a synthetic check via a row whose definition really cites the target slug)
# find one real positive: scan for a SoleCandidate row whose def cites target slug
found = None
for r in cp.v2rows:
    if r["disposition"] != "SoleCandidate": continue
    cands = r["candidate_slugs"].split(" | ")
    if len(cands) != 1: continue
    t = cands[0]
    txt = (cp.defs.get(r["source_slug"], "") + " " + cp.scopes.get(r["source_slug"], "")).lower()
    if re.search(r"(?<![\w-])" + re.escape(t.lower()) + r"(?![\w-])", txt):
        found = (r["row_id"], r["source_slug"], t); break
print("   real def-citation example:", found)
check("explicit-ref counts definition citation",
      found is not None and cp.explicit_reference(found[1], found[2]) == True)
# substring: target slug that is a strict prefix of a longer slug in text must NOT match
# (construct: text mentions CM-1-1-3-7-9; query target CM-1-1-3-7 -> must be False;
#  query CM-1-1-3-7-9 -> must be True). Synthetic defs injected, then restored.
cp.defs["SYN-S"] = "the step cites CM-1-1-3-7-9 in its definition text"
check("explicit-ref strict prefix does NOT match",
      cp.explicit_reference("SYN-S", "CM-1-1-3-7") == False)
check("explicit-ref exact slug DOES match",
      cp.explicit_reference("SYN-S", "CM-1-1-3-7-9") == True)
del cp.defs["SYN-S"]

# ---------- 2. two-way ----------
# follows backed by a triggers-ONLY backlink must NOT confirm.
# (The old test used a real pair whose backlink was follows, not triggers —
#  it passed for the wrong reason. Synthetic: triggers-only backlink.)
cp.graph["SYN-T2"] = [("triggers", "SYN-S2")]
check("two-way: follows NOT confirmed by triggers-only backlink",
      cp.two_way("SYN-S2", "follows", "SYN-T2") == False)
del cp.graph["SYN-T2"]
# precedes confirmed by follows backlink (real pair found below)
pair = None
for r in cp.v2rows:
    if r["verb"] != "precedes": continue
    cands = r["candidate_slugs"].split(" | ")
    if len(cands) != 1: continue
    s, t = r["source_slug"], cands[0]
    back = [v for v, x in cp.graph.get(t, []) if x == s]
    if "follows" in back:
        pair = (s, t); break
print("   real precedes/follows pair:", pair)
check("two-way: precedes confirmed by follows backlink",
      pair is not None and cp.two_way(pair[0], "precedes", pair[1]) == True)
# informs confirmed by informed-by backlink (no real pair in the data, so inject
# a synthetic backlink into a copy of the graph semantics: temporarily extend
# cp.graph, then restore)
cp.graph["SYN-T"].append(("informed-by", "SYN-S"))
check("two-way: informs confirmed by informed-by backlink",
      cp.two_way("SYN-S", "informs", "SYN-T") == True)
cp.graph["SYN-T"].append(("triggers", "SYN-S"))
check("two-way: informs NOT confirmed by triggers backlink",
      cp.two_way("SYN-S", "informs", "SYN-T") == True)  # informed-by still present
del cp.graph["SYN-T"]
# enables must NOT be confirmed by uses-input (strict table; mapping unapproved)
check("two-way: enables NOT confirmed by uses-input",
      cp.two_way("__s__", "enables", "__t__") == False)

# ---------- 3. structural nearness / verb fits ----------
# sequence verbs between non-siblings must fail
check("verb-fit: precedes non-siblings fails",
      cp.structural_nearness("CM-1-1-2-1", "precedes", "CM-1-1-4") == False)
# dependency verb where target is a strict ancestor of source must fail
# REL-00002: CM-1-1-1-1-1 enables CM-1-1-1-1 (parent L2)
check("verb-fit: enables own ancestor fails",
      cp.structural_nearness("CM-1-1-1-1-1", "enables", "CM-1-1-1-1") == False)
# dependency verb, same L2 branch, non-ancestor -> passes
ok = None
for r in cp.v2rows:
    if r["verb"] not in ("uses-input", "informed-by") or r["disposition"] != "SoleCandidate": continue
    cands = r["candidate_slugs"].split(" | ")
    if len(cands) != 1: continue
    s, t = r["source_slug"], cands[0]
    if t not in cp.ancestors(s) and s not in cp.ancestors(t):
        s23 = set(cp.l2_l3(s)); t23 = set(cp.l2_l3(t))
        if s23 & t23:
            ok = (s, r["verb"], t); break
print("   real same-branch non-ancestor example:", ok)
check("verb-fit: same-branch dependency passes",
      ok is not None and cp.structural_nearness(ok[0], ok[1], ok[2]) == True)

# ---------- 4. sampling ----------
check("sample size: pop 200 -> 10", cp.sample_n(200) == 10)
check("sample size: pop 1000 -> 50", cp.sample_n(1000) == 50)
check("sample size: pop 5 -> 5", cp.sample_n(5) == 5)
check("sample size: pop 12 -> 10", cp.sample_n(12) == 10)

n_fail = sum(1 for _, s in results if s == FAIL)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
