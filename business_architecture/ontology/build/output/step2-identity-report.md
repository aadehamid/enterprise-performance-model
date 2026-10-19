# Step 2 — Identity normalization report

*2026-10-18:* this is the report of the last Step 2 run, kept as built. Since then MPC-P02 gave Refining and its two ID-less L2 nodes the IDs `RF 1`, `RF 1.1` and `RF 1.2` (EPM-DEC-001-0047). The curated identity map carries them with `minted: false` and their slugs pinned, and adds rows for the new nodes, so the three Refining rows in the stub table below are no longer stubs. The next identity pass regenerates this report.

- Nodes processed: 683 (at the Step 2 run; later changes are in the dated notes above and below, each with its own count)
- IDs preserved as skos:notation: 669 (at the Step 2 run) (all unique, all match `CM <dotted>` pattern)
- Minted stub slugs: 14
- Deprecated tombstones: 1
- Slug collisions: none
- URI collisions: none
- Orphan nodes: none

## Minted stub slugs (for the consolidated repo-JSON proposal)

| Level | Name | Minted slug | Proposed repo `id` |
|---|---|---|---|
| L0 | Downstream Operations | `L0-downstream-operations` | `L0-downstream-operations` |
| L1 | Refining | `L1-refining` | `L1-refining` |
| L2 | Refinery Performance and Risk Coordination | `L2-refinery-performance-and-risk-coordination` | `L2-refinery-performance-and-risk-coordination` |
| L2 | Refinery Asset Reliability and Turnaround Coordination | `L2-refinery-asset-reliability-and-turnaround-coordination` | `L2-refinery-asset-reliability-and-turnaround-coordination` |
| L1 | Midstream | `L1-midstream` | `L1-midstream` |
| L0 | Enabling Functions | `L0-enabling-functions` | `L0-enabling-functions` |
| L1 | Supply Chain Mgmt. | `L1-supply-chain-mgmt` | `L1-supply-chain-mgmt` |
| L1 | Finance | `L1-finance` | `L1-finance` |
| L2 | Financial Planning and Performance Management | `L2-financial-planning-and-performance-management` | `L2-financial-planning-and-performance-management` |
| L1 | Shared Services | `L1-shared-services` | `L1-shared-services` |
| L1 | Process Excellence & IT | `L1-process-excellence-it` | `L1-process-excellence-it` |
| L1 | Human Resources | `L1-human-resources` | `L1-human-resources` |
| L1 | Legal & Corp Comm | `L1-legal-corp-comm` | `L1-legal-corp-comm` |
| L1 | EHS & Gov Reporting | `L1-ehs-gov-reporting` | `L1-ehs-gov-reporting` |

## URI pattern

`https://w3id.org/lsc/ontology/process/{slug}` — e.g. `https://w3id.org/lsc/ontology/process/CM-1-2-1-3`, `https://w3id.org/lsc/ontology/process/L1-human-resources`.
No version segment; versions ride on `owl:versionInfo` (Appendix B).

*2026-10-19:* EPM-DEC-001-0048 added CM 1.1.3.7.13 Reconcile Movement Losses and Gains to the map; the curated identity map holds its row, as Step 2 would emit it. This adds one node and one ID; the 2026-10-18 note at the top of this report gives the Refining changes (three IDs on existing nodes, five new nodes).

*2026-10-18:* the counts above are the last Step 2 run's. MPC-P05 (EPM-DEC-001-0047) added CM 1.2.4.3.8 and its two children to the map (three nodes, three IDs), and the curated identity map holds a row for each, as Step 2 would emit it; the next identity pass regenerates this report.
