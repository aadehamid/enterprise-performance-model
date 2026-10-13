# Proposal MPC-P02: IDs for the three Refining nodes without one

| Field | Value |
|---|---|
| Status | Proposed. The process map changes only through its authoring path; this file does not edit it |
| Date | 2026-10-13 |
| Decision | EPM-DEC-001-0012: "Raise a process-map proposal (not a direct edit) to assign IDs to the three nodes." |
| Source suggestion | `business_architecture/reference/mpc/process-map-suggestions.md`, MPC-P02 |
| Recommendation | Delegated under EPM-DEC-001-0028 (merged in #242): keep the minted slugs; the IDs become notation only |

## The nodes

MPC-P02 targets three Refining nodes that have no `id` in `business_architecture/business_process/downstream_process_map.json`. (The map has 14 nodes without an `id` in all; Midstream's is MPC-P01's open scope question, and the L0 roots and Enabling Functions nodes are outside MPC-P02.)

| Node | Level | Ontology slug today (minted in Step 2) |
|---|---|---|
| Refining | L1 | `L1-refining` |
| Refinery Performance and Risk Coordination | L2 | `L2-refinery-performance-and-risk-coordination` |
| Refinery Asset Reliability and Turnaround Coordination | L2 | `L2-refinery-asset-reliability-and-turnaround-coordination` |

## Proposed IDs

| Node | Proposed `id` | Why |
|---|---|---|
| Refining | `RF 1` | Each L1 under Downstream Operations takes its own prefix: Commercial & Marketing is `CM 1`. `RF` for Refining follows the two-letter pattern and collides with no existing prefix (the map uses only `CM`). |
| Refinery Performance and Risk Coordination | `RF 1.1` | The first L2 under `RF 1`, in map order. |
| Refinery Asset Reliability and Turnaround Coordination | `RF 1.2` | The second new L2 under `RF 1`. |

Refining's two other L2 children keep their IDs, `CM 1.1.4` (Refinery Planning and Optimization) and `CM 1.1.7` (Refinery Production Planning and Scheduling). The R1 reclassification moved them under Refining with their IDs, slugs and IRIs unchanged (`step4/playbook/ontology-worklog.md`, 3d-c), and an ID does not change when its node moves.

## Effect on the ontology

Identity must not move. The three nodes were published under minted slugs, and slugs are identity (ontology skill, Step 2). But `business_architecture/ontology/build/step2-identity-map.py` derives a slug from a node's ID, so a plain re-run after the map takes these IDs would mint `RF-1`, `RF-1-1` and `RF-1-2` and change three IRIs. Two things prevent that:

1. When the map takes the IDs, the curated identity map (`business_architecture/ontology/build/output/step2-identity-map.json`) records each one as `skos_notation` on the node's existing entry; the slug stays. The next taxonomy build then adds `skos:notation` `"RF 1"`, `"RF 1.1"` and `"RF 1.2"` and nothing else.
2. `business_architecture/ontology/build/step2-identity-map.py` pins the three slugs to these IDs (`SLUG_PINS`, in this change), so a re-run cannot remint them.

The script is not the regeneration path today: the committed identity map carries overlays added after Step 2 (the naming pass's prior names and rename notes), which a re-run would drop. With the pins in place, `core` 1.0.0 can ship the three minted IRIs, and they stay stable after the IDs land.

## Not in this proposal

The turnaround-lifecycle children that MPC-P02 also suggests wait for Step 7, with the turnaround-cost measure (EPM-DEC-001-0012).
