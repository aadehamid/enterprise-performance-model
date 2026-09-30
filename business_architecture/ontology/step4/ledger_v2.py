#!/usr/bin/env python3
"""Ledger v2 builder: per-predicate conservation + relatedConcepts
mention -> canonical fact -> mirror merge + contradictions.

Reads only the pinned baseline (baseline/step3-taxonomy.ttl,
baseline/step2-identity-map.json) and the disposition artifacts.
Writes q2-ledger-v2.md and supporting CSVs.
"""
import re, json, csv, os
from collections import Counter, defaultdict

# Step 4 working directory: derived from this file; EPM_STEP4_DIR overrides.
BASE = os.environ.get("EPM_STEP4_DIR") or os.path.dirname(os.path.abspath(__file__))
SHA = open(f"{BASE}/PINNED_SHA.txt").read().strip()
ttl = open(f"{BASE}/baseline/step3-taxonomy.ttl").read()
imap = {r["slug"]: r for r in json.load(open(f"{BASE}/baseline/step2-identity-map.json"))}

# ---- block parser: subject -> {predicate: [values]} ----
def parse_blocks(ttl_text):
    blocks = {}
    for b in ttl_text.split("\n\n"):
        b = b.strip()
        if not b:
            continue
        m = re.match(r"([A-Za-z][\w:.-]*)\s", b)
        if not m:
            continue
        subj = m.group(1)
        preds = defaultdict(list)
        # predicate-object pairs: split on ';' not inside quotes/brackets
        # simpler: find all predicate positions then slice
        pos = [(mm.start(), mm.group(1)) for mm in
               re.finditer(r"(?:^|[;\]])\s*([a-zA-Z][\w]*:[a-zA-Z][\w]*)", b, re.M)]
        # values: quoted literals (single or triple-quoted)
        for i, (st, p) in enumerate(pos):
            seg = b[st:b.find("\n\n", st) if False else len(b)]
            # take until next predicate position or end
            end = pos[i + 1][0] if i + 1 < len(pos) else len(b)
            seg = b[st:end]
            for vm in re.finditer(r'"""(.*?)"""|"((?:[^"\\]|\\.)*)"', seg, re.S):
                v = vm.group(1) if vm.group(1) is not None else vm.group(2)
                # only the first literal per predicate segment (ignore nested [] blocks' literals? keep simple: first)
                preds[p].append(v)
                break
        blocks[subj] = preds
    return blocks

blocks = parse_blocks(ttl)
proc_blocks = {s: p for s, p in blocks.items() if s.startswith("proc:")}
print("proc blocks:", len(proc_blocks))

# ---- 1. predicate census ----
census = Counter()
for s, preds in proc_blocks.items():
    for p, vs in preds.items():
        if p.startswith("intake:"):
            census[p] += len(vs)
total = sum(census.values())
print("intake triples:", total)
for p, n in sorted(census.items()):
    print(f"  {p}: {n}")
assert total == 5571, total
