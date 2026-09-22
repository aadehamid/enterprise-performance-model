#!/usr/bin/env python3
"""R1 Refining structural reclassification — one-shot source-JSON update.

Applies the Hamid-approved R1 move set to
`business_architecture/business_process/downstream_process_map.json`,
deterministically and with assertions:

  * move CM-1-1-4 (Refinery Planning -> Refinery Planning and Optimization)
    and CM-1-1-7 (Refinery Scheduling -> Refinery Production Planning and
    Scheduling) from CM-1-1 to L1-refining, promoting both to L2 and shifting
    their whole subtrees one level up;
  * re-anchor the tombstone CM-1-1-4-6 (still deprecated) under CM-1-1 at L3,
    with CM-1-1-4-6-1 (PTC-001-B hold) under it at L4;
  * add the new Candidate L2 Refinery Asset Reliability and Turnaround
    Coordination under L1-refining (no children in R1);
  * all other trees byte-unchanged.

The writer preserves the source file's exact serialization framing
(leading blank line, 2-space indent, trailing newline) so the textual diff
shows only the structural moves, not formatting churn.

Usage:
  python3 r1-json-update.py   # defaults: in-place update + diff under build/r1

One-shot and asserted: it refuses to run twice (a second run would find the
movers already under Refining and fail loudly) rather than double-applying.
"""
import argparse
import json
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BUILD = _HERE.parent
_BUSINESS_ARCH = _BUILD.parent.parent
_D_SRC = _BUSINESS_ARCH / "business_process" / "downstream_process_map.json"
_D_DIFF = _BUILD / "r1" / "r1-json-diff.md"

DATE = "2026-09-22"
MOVERS = ("CM-1-1-4", "CM-1-1-7")
RENAMES = {"CM-1-1-4": "Refinery Planning and Optimization",
           "CM-1-1-7": "Refinery Production Planning and Scheduling"}
TOMBSTONE = "CM-1-1-4-6"
TOMBSTONE_CHILD = "CM-1-1-4-6-1"
NEW_L2_NAME = "Refinery Asset Reliability and Turnaround Coordination"


def slug_of(node):
    pid = node.get("id")
    if pid:
        return pid.replace(" ", "-").replace(".", "-")
    import unicodedata as ud
    t = ud.normalize("NFKD", node["name"]).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return f"L{node['level']}-{t}"


def find_node(tree, slug):
    """Return (parent_list, index, node) for slug, or None."""
    stack = [(tree, None)]
    for lst, _ in stack:
        for i, n in enumerate(lst):
            if slug_of(n) == slug:
                return lst, i, n
            if n.get("children"):
                stack.append((n["children"], n))
    return None


def set_level(node, level):
    node["level"] = level
    for c in node.get("children", []) or []:
        set_level(c, level + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=_D_SRC)
    ap.add_argument("--diff-out", default=_D_DIFF)
    a = ap.parse_args()
    src = Path(a.src)

    raw = src.read_text(encoding="utf-8")
    prefix = raw[:len(raw) - len(raw.lstrip())]   # framing before '['
    suffix = raw[len(raw.rstrip()):]              # framing after ']'
    data = json.loads(raw)

    # ---- baseline sanity (must run on the pre-R1 tree) ----
    before = {}
    def rec(n, pslug):
        s = slug_of(n)
        before[s] = (n["level"], pslug)
        for c in n.get("children", []) or []:
            rec(c, s)
    for top in data:
        rec(top, None)
    assert len(before) == 682, f"expected 682 nodes, got {len(before)}"
    for m in MOVERS:
        assert before[m][1] == "CM-1-1", f"{m} not under CM-1-1: {before[m]}"

    changes = []

    def detach(slug):
        hit = find_node(data, slug)
        assert hit, f"node not found: {slug}"
        lst, i, node = hit
        del lst[i]
        return node

    # ---- 1. promote the two roots to L2 under L1-refining ----
    refining = find_node(data, "L1-refining")[2]
    # insert directly after the (empty) Refining L2 stubs keep their order:
    # place movers right before the first stub-less L2 is not required; append
    # after the two existing L2s' current order is alphabetical by placement —
    # we place them in decision-package order:
    #   Refinery Performance and Risk Coordination,
    #   Refinery Planning and Optimization,
    #   Refinery Production Planning and Scheduling,
    #   Refinery Asset Reliability and Turnaround Coordination.
    for slug in MOVERS:
        node = detach(slug)
        node["name"] = RENAMES[slug]
        set_level(node, 2)
        refining.setdefault("children", []).append(node)
        changes.append((slug, before[slug],
                        (2, "L1-refining"),
                        f"renamed '{RENAMES[slug]}', subtree shifted up one level"))

    # order the four Refining L2s per the decision package
    order = {"L2-refinery-performance-and-risk-coordination": 0,
             "CM-1-1-4": 1, "CM-1-1-7": 2}
    refining["children"].sort(key=lambda n: order.get(slug_of(n), 99))

    # ---- 2. tombstone re-anchor under CM-1-1 (L3), hold stays under it (L4) ----
    tomb = detach(TOMBSTONE)
    assert tomb.get("deprecated") is True, "tombstone must stay deprecated"
    set_level(tomb, 3)
    cm11 = find_node(data, "CM-1-1")[2]
    cm11.setdefault("children", []).append(tomb)
    changes.append((TOMBSTONE, before[TOMBSTONE], (3, "CM-1-1"),
                    "tombstone re-anchored under CM-1-1 (still deprecated)"))
    changes.append((TOMBSTONE_CHILD, before[TOMBSTONE_CHILD], (4, TOMBSTONE),
                    "PTC-001-B hold: unchanged owner, shifted with tombstone"))

    # ---- 3. new Candidate L2 (no children in R1) ----
    new_l2 = {"level": 2, "name": NEW_L2_NAME, "children": []}
    refining["children"].append(new_l2)
    changes.append(("L2-refinery-asset-reliability-and-turnaround-coordination",
                    None, (2, "L1-refining"),
                    "new Candidate L2 (initially unpopulated)"))

    # ---- assertions: exact move set, nothing else ----
    after = {}
    def rec2(n, pslug):
        s = slug_of(n)
        after[s] = (n["level"], pslug)
        for c in n.get("children", []) or []:
            rec2(c, s)
    for top in data:
        rec2(top, None)
    assert len(after) == 683, f"expected 683 nodes, got {len(after)}"
    moved = {s for s in before if before[s] != after[s]}
    expected_moved = {
        # 40 active movers
        "CM-1-1-4", "CM-1-1-4-1", "CM-1-1-4-2", "CM-1-1-4-3", "CM-1-1-4-4",
        "CM-1-1-4-5", "CM-1-1-4-7",
        "CM-1-1-4-1-1", "CM-1-1-4-1-2", "CM-1-1-4-1-3", "CM-1-1-4-1-4",
        "CM-1-1-4-2-1", "CM-1-1-4-2-2",
        "CM-1-1-4-4-1", "CM-1-1-4-4-2", "CM-1-1-4-4-3",
        "CM-1-1-4-7-1", "CM-1-1-4-7-2", "CM-1-1-4-7-3", "CM-1-1-4-7-4",
        "CM-1-1-4-7-5", "CM-1-1-4-7-6", "CM-1-1-4-7-7", "CM-1-1-4-7-8",
        "CM-1-1-7",
        "CM-1-1-7-1", "CM-1-1-7-2", "CM-1-1-7-3",
        "CM-1-1-7-1-1", "CM-1-1-7-1-2", "CM-1-1-7-1-3",
        "CM-1-1-7-2-1", "CM-1-1-7-2-2", "CM-1-1-7-2-3", "CM-1-1-7-2-4",
        "CM-1-1-7-2-5", "CM-1-1-7-2-6",
        "CM-1-1-7-3-1", "CM-1-1-7-3-2", "CM-1-1-7-3-3",
        # 2 tombstone/hold rows
        TOMBSTONE, TOMBSTONE_CHILD,
    }
    assert moved == expected_moved, \
        f"move set mismatch: extra={moved - expected_moved} missing={expected_moved - moved}"
    # no node lost its subtree
    for s in before:
        assert s in after, f"node lost: {s}"
    # PTC-002-adjacent and feedstock cluster untouched
    assert after["CM-1-1-4-6-3"] == before["CM-1-1-4-6-3"]
    assert all(after[s] == before[s] for s in before if s.startswith("CM-1-2-5-"))

    # ---- write, preserving the original framing ----
    body = json.dumps(data, indent=2, ensure_ascii=False)
    src.write_text(prefix + body + suffix, encoding="utf-8")

    with open(a.diff_out, "w", encoding="utf-8") as f:
        f.write("# R1 source-JSON structural diff\n\n")
        f.write(f"682 → 683 nodes ({DATE}). The file framing (leading blank "
                f"line, 2-space indent, trailing newline) is preserved, so the "
                f"textual diff below shows only structural moves.\n\n")
        f.write("| slug | before (level, parent) | after (level, parent) | note |\n")
        f.write("|---|---|---|---|\n")
        for slug, b, aft, note in changes:
            f.write(f"| `{slug}` | {b} | {aft} | {note} |\n")
    print(f"OK: {src} 682 → 683 nodes; diff: {a.diff_out}")


if __name__ == "__main__":
    main()
