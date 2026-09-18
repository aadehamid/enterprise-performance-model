#!/usr/bin/env python3
"""Step 2 — Normalize identities for all 680 process-map nodes.

Reads business_architecture/business_process/downstream_process_map.json
from the repo clone, derives a URI slug for every node:

  - Nodes with an ID (e.g. "CM 1.2.1.3") -> slug "CM-1-2-1-3"
    (spaces and dots become hyphens; the original code is kept as
    skos:notation, and the URI is https://w3id.org/lsc/ontology/process/{slug})
  - The 11 ID-less stubs -> minted slug "L{level}-{name-slug}"
    (e.g. "L1-human-resources")

Verifies: every node gets exactly one slug; slugs are unique (injective);
every stub slug is recorded for the later consolidated repo-JSON proposal.

Outputs:
  - step2-identity-map.json : [{uri, slug, level, name, skos_notation,
                                 parent_slug, minted, proposed_repo_id}]
  - step2-identity-report.md : human-readable summary + collision checks
"""
import json
import re
import unicodedata
from pathlib import Path

REPO = Path.home() / "workspace" / "enterprise-performance-model"
SRC = REPO / "business_architecture" / "business_process" / "downstream_process_map.json"
OUT_DIR = Path.home() / "workspace" / "ontology-build"
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
            }
        )
        for child in node.get("children", []):
            walk(child, slug)

    for top in data:
        walk(top, None)

    # --- checks ---
    assert len(rows) == 680, f"expected 680 nodes, got {len(rows)}"
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
    assert len(minted) == 11, f"expected 11 minted stubs, got {len(minted)}"

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
