#!/usr/bin/env python3
"""Step 3d: PTC-001 consolidated tree pass (partial resolution).

Hamid's decision (2026-09-21, revised proposal with four review
adjustments): open Finance and Refining minimally, reparent the two
movable rows, tombstone Commercial Development, keep Develop Strategic
Business Plan parked under PTC-001-B.

Tree surgery on business_architecture/business_process/downstream_process_map.json:
  1. Pop "Plan Budgets" (CM 1.1.4.6.2) out of Commercial Development ->
     new L2 "Financial Planning and Performance Management" under the
     Finance stub (L2 is a Candidate architecture node; row level 5 -> 3).
  2. Pop "Manage Site Specific Business Risk" (CM 1.1.4.6.3) out ->
     new L2 "Refinery Performance and Risk Coordination" under the
     Refining stub, renamed "Coordinate Site Business Risk Management"
     (level 5 -> 3).
  3. "Commercial Development" (CM 1.1.4.6) becomes an owl:deprecated
     tombstone: marked "deprecated": true, keeps its one parked child
     (CM 1.1.4.6.1, still blocked under PTC-001-B) so the blocked row
     is never orphaned. Removed from active navigation by consumers
     filtering the deprecation flag; lineage preserved.
  4. Node count 680 -> 682 (2 new L2s; tombstone retained).

Identity is stable: moved rows keep slugs/URIs/notations; only
parent_slug and level change.

One-shot. Asserts expected pre-state, so a stale tree fails loudly.
Run from the repo root.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "business_architecture" / "business_process" / "downstream_process_map.json"

FIN_L2_NAME = "Financial Planning and Performance Management"
REF_L2_NAME = "Refinery Performance and Risk Coordination"
RISK_NEW_NAME = "Coordinate Site Business Risk Management"


def find(nodes, pred, trail=()):
    for n in nodes:
        if pred(n):
            return n, trail
        r = find(n.get("children", []) or [], pred, trail + (n.get("name"),))
        if r[0] is not None:
            return r
    return None, ()


def count(nodes):
    return sum(1 + count(n.get("children", []) or []) for n in nodes)


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))

    # --- pre-state assertions ---
    assert count(data) == 680, f"expected 680 nodes, got {count(data)}"

    cd, cd_trail = find(data, lambda n: n.get("id") == "CM 1.1.4.6")
    assert cd is not None, "Commercial Development not found"
    assert cd["level"] == 4 and cd["name"] == "Commercial Development"
    assert cd_trail[-1] == "Refinery Planning", f"unexpected parent: {cd_trail[-1]}"
    kids = {k["id"]: k for k in cd.get("children", [])}
    assert set(kids) == {"CM 1.1.4.6.1", "CM 1.1.4.6.2", "CM 1.1.4.6.3"}, \
        f"unexpected children: {sorted(kids)}"
    assert kids["CM 1.1.4.6.1"]["name"] == "Develop Strategic Business Plan"
    assert kids["CM 1.1.4.6.2"]["name"] == "Plan Budgets"
    assert kids["CM 1.1.4.6.3"]["name"] == "Manage Site Specific Business Risk"
    assert all(k["level"] == 5 for k in kids.values())
    assert "deprecated" not in cd

    fin, _ = find(data, lambda n: n.get("name") == "Finance" and n.get("level") == 1)
    assert fin is not None and "id" not in fin, "Finance stub not found"
    assert not fin.get("children"), "Finance stub already has children"
    ref, _ = find(data, lambda n: n.get("name") == "Refining" and n.get("level") == 1)
    assert ref is not None and "id" not in ref, "Refining stub not found"
    assert not ref.get("children"), "Refining stub already has children"

    # --- surgery ---
    n61 = kids["CM 1.1.4.6.1"]
    n62 = kids["CM 1.1.4.6.2"]
    n63 = kids["CM 1.1.4.6.3"]

    # 1. tombstone: keep parked child, mark deprecated
    cd_children = [n61]
    new_cd = {"id": cd["id"], "level": cd["level"], "name": cd["name"],
              "deprecated": True, "children": cd_children}
    # replace in place under Refinery Planning
    parent, _ = find(data, lambda n: n.get("id") == "CM 1.1.4")
    assert parent is not None
    parent["children"] = [new_cd if c is cd else c for c in parent["children"]]

    # 2. Plan Budgets -> Finance L2 (level 5 -> 3)
    n62["level"] = 3
    fin["children"] = [{
        "level": 2,
        "name": FIN_L2_NAME,
        "children": [n62],
    }]

    # 3. risk row -> Refining L2 (level 5 -> 3, renamed)
    n63["level"] = 3
    n63["name"] = RISK_NEW_NAME
    ref["children"] = [{
        "level": 2,
        "name": REF_L2_NAME,
        "children": [n63],
    }]

    # --- post-state assertions ---
    assert count(data) == 682, f"expected 682 nodes, got {count(data)}"

    # --- write (preserve file's 2-space indent + leading blank line) ---
    SRC.write_text("\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print("tree pass complete: 680 -> 682 nodes")
    print(f"  + L2 {FIN_L2_NAME!r} under Finance, hosting Plan Budgets (L3)")
    print(f"  + L2 {REF_L2_NAME!r} under Refining, hosting {RISK_NEW_NAME!r} (L3)")
    print("  ~ Commercial Development tombstoned (deprecated), parked child retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
