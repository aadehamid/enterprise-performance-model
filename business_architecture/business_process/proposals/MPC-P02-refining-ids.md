# Proposal MPC-P02: IDs for the three Refining nodes without one

| Field | Value |
|---|---|
| Status | Proposed. The process map changes only through its authoring path; this file does not edit it |
| Date | 2026-10-13 |
| Decision | EPM-DEC-001-0012: "Raise a process-map proposal (not a direct edit) to assign IDs to the three nodes." |
| Source suggestion | `reference/mpc/process-map-suggestions.md`, MPC-P02 |
| Recommendation | Delegated under EPM-DEC-001-0028 (pending in #242) |

## The nodes

In `downstream_process_map.json`, three nodes under Downstream Operations have no `id`:

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

None on identity. Slugs are identity and labels are presentation (ontology skill, Step 2), and the three slugs above are already stable IRIs. When the map takes these IDs, the next taxonomy build adds `skos:notation` `"RF 1"`, `"RF 1.1"` and `"RF 1.2"`; nothing else changes. So `core` 1.0.0 does not wait for this proposal to land in the map.

## Not in this proposal

The turnaround-lifecycle children that MPC-P02 also suggests wait for Step 7, with the turnaround-cost measure (EPM-DEC-001-0012).
