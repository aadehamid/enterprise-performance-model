#!/usr/bin/env python3
"""Step 2 — Normalize identities for all process-map nodes.

Reads business_architecture/business_process/downstream_process_map.json
from this clone, derives a URI slug for every node:

  - Nodes with an ID (e.g. "CM 1.2.1.3") -> slug "CM-1-2-1-3"
    (spaces and dots become hyphens; the original code is kept as
    skos:notation, and the URI is https://w3id.org/lsc/ontology/process/{slug})
  - The 13 ID-less stubs -> minted slug "L{level}-{name-slug}"
    (e.g. "L1-human-resources")

A node marked "deprecated": true in the JSON (e.g. the CM-1-1-4-6
Commercial Development tombstone from the Step 3d PTC-001 tree pass)
carries deprecated: true into the identity map; its slug/URI are
preserved for lineage.

Verifies: every node gets exactly one slug; slugs are unique (injective);
every stub slug is recorded for the later consolidated repo-JSON proposal.

Outputs (next to this script, under build/output/):
  - step2-identity-map.json : [{uri, slug, level, name, skos_notation,
                                 parent_slug, minted, proposed_repo_id,
                                 deprecated}]
  - step2-identity-report.md : human-readable summary + collision checks
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "business_architecture" / "business_process" / "downstream_process_map.json"
OUT_DIR = Path(__file__).resolve().parent / "output"
BASE = "https://w3id.org/lsc/ontology/process/"

ID_RE = re.compile(r"^[A-Z]+ \d+(\.\d+)*$")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def id_to_slug(pid: str) -> str:
    assert ID_RE.match(pid), f"ID does not match expected pattern: {pid!r}"
    return pid.replace(" ", "-").replace(".", "-")


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))

    rows = []

    def walk(node, parent_slug):
        pid = node.get("id")
        name = node["name"]
        level = node["level"]
        if pid:
            slug = id_to_slug(pid)
            minted = False
            notation = pid
            proposed_repo_id = pid
        else:
            slug = f"L{level}-{slugify(name)}"
            minted = True
            notation = None
            proposed_repo_id = slug  # proposal for the consolidated repo-JSON update
        rows.append(
            {
                "uri": BASE + slug,
                "slug": slug,
                "level": level,
                "name": name,
                "skos_notation": notation,
                "parent_slug": parent_slug,
                "minted": minted,
                "proposed_repo_id": proposed_repo_id,
                "deprecated": bool(node.get("deprecated", False)),
            }
        )
        for child in node.get("children", []) or []:
            walk(child, slug)

    for top in data:
        walk(top, None)

    # --- checks ---
    # expected counts are derived from the input JSON, not hardcoded: the
    # tree grows (R1 added the Refinery Asset Reliability and Turnaround
    # Coordination L2). The tripwire is node/row correspondence, not 682.
    def count_nodes(nodes):
        return sum(1 + count_nodes(n.get("children", []) or []) for n in nodes)
    n_nodes = count_nodes(data)
    assert len(rows) == n_nodes, f"node/row mismatch: {len(rows)} rows for {n_nodes} nodes"
    slugs = [r["slug"] for r in rows]
    assert len(set(slugs)) == len(slugs), "slug collision detected"
    uris = [r["uri"] for r in rows]
    assert len(set(uris)) == len(uris), "URI collision detected"
    # every non-root node must have a parent that exists
    slug_set = set(slugs)
    for r in rows:
        if r["parent_slug"] is not None:
            assert r["parent_slug"] in slug_set, f"orphan: {r['slug']}"
    # every id-derived slug must round-trip to a unique original id
    notations = [r["skos_notation"] for r in rows if r["skos_notation"]]
    assert len(set(notations)) == len(notations), "notation collision"

    minted = [r for r in rows if r["minted"]]
    # minted stubs == ID-less nodes in the input (13 baseline + R1's new L2)
    def count_idless(nodes):
        return sum((0 if n.get("id") else 1) + count_idless(n.get("children", []) or [])
                   for n in nodes)
    assert len(minted) == count_idless(data), \
        f"minted/ID-less mismatch: {len(minted)} minted"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "step2-identity-map.json").write_text(
        json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    lines = [
        "# Step 2 — Identity normalization report",
        "",
        f"- Nodes processed: {len(rows)}",
        f"- IDs preserved as skos:notation: {len(notations)} (all unique, all match `CM <dotted>` pattern)",
        f"- Minted stub slugs: {len(minted)}",
        f"- Deprecated tombstones: {sum(1 for r in rows if r['deprecated'])}",
        "- Slug collisions: none",
        "- URI collisions: none",
        "- Orphan nodes: none",
        "",
        "## Minted stub slugs (for the consolidated repo-JSON proposal)",
        "",
        "| Level | Name | Minted slug | Proposed repo `id` |",
        "|---|---|---|---|",
    ]
    for r in minted:
        lines.append(
            f"| L{r['level']} | {r['name']} | `{r['slug']}` | `{r['proposed_repo_id']}` |"
        )
    lines += [
        "",
        "## URI pattern",
        "",
        f"`{BASE}{{slug}}` — e.g. `{BASE}CM-1-2-1-3`, `{BASE}L1-human-resources`.",
        "No version segment; versions ride on `owl:versionInfo` (Appendix B).",
    ]
    (OUT_DIR / "step2-identity-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(f"OK: {len(rows)} nodes, {len(minted)} minted stubs, no collisions.")


if __name__ == "__main__":
    main()
