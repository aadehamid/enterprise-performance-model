# Proposal MPC-P03: two gaps in the physical execution of inter-refinery transfers

| Field | Value |
|---|---|
| Status | Proposed, for Hamid. No process is added until he rules |
| Date | 2026-10-18 |
| Decision | EPM-DEC-001-0047: Hamid accepted MPC-P03 "with a physical-execution coverage check" |
| Source suggestion | `business_architecture/reference/mpc/process-map-suggestions.md`, MPC-P03 |

## What the check found

MPC's refineries move intermediate products between sites, including during partial shutdowns (`reference/mpc/mpc-fy2025-10k-fact-sheet.md`, Item 1 operating facts). Hamid asked whether the map covers the physical execution of those transfers, not only their planning and settlement. The check went through the five parts of physical execution he named. CM 1.1.7's description now names the existing steps.

| Part of physical execution | Covered by | Finding |
|---|---|---|
| Nomination and scheduling | CM 1.1.3.6.1 Plan & Execute Nominations | Covered. The node is generic: it does not say it includes intermediates moving between refineries |
| Movement execution | CM 1.1.3.6.2 Loading Shipment; CM 1.1.3.6.3 Track Movements and Inventory Management | Covered, generic |
| Quantity measurement | CM 1.1.3.7.4 Measure Inventory; CM 1.2.3 Actualizations (final ticket volumes) | Covered |
| Quality measurement | CM 1.2.5.1 Crude/Feed Quality Management | **Gap.** CM 1.2.5.1 covers crude and feedstock quality. No step names the quality of an intermediate that one refinery sends and another receives |
| Receipt and inventory reconciliation | CM 1.1.3.6.4 Discharge & Reconcile Load; CM 1.1.3.7.5 Perform Inventory Reconciliation; CM 1.1.5.1.2.5 Receive actual data for inventory & transfers | Covered |
| Loss and gain | none | **Gap.** No step names the loss and gain reconciliation of a movement. The Loss Control data product ("Custody transfer, gain/loss, and shrinkage data across movements and terminal operations", `data_product_portfolio.json`) exists without a process that produces it; the worklog's Step 7 row lists "Loss Control ownership" as open |
| Settlement | CM 1.2.4.1.18 Settle Intermediates | Covered |

Assumption behind "covered": CM 1.1.3 (Distribution Planning & Scheduling and Inventory Management) handles intermediates as well as finished products. Its inventory steps include "Develop Intermediates Inventory Policy" (CM 1.1.3.7.2), which supports that reading. If Hamid reads CM 1.1.3 as finished products only, every row above except settlement becomes a gap.

## What Hamid decides

1. **Loss and gain.** (A, recommended) Add one step, "Reconcile Movement Losses and Gains", under CM 1.1.3.7 Inventory, covering every movement, not only inter-refinery transfers; it produces the Loss Control data product. (B) Record loss and gain as part of CM 1.1.3.6.4 Discharge & Reconcile Load, by description only. (C) Leave the gap open.
2. **Quality of transferred intermediates.** (A, recommended) Widen CM 1.2.5.1's description so it covers intermediates received as feed from another refinery. (B) Add a step under CM 1.1.7. (C) Leave it.

A is recommended for 1 because the data product already exists and needs a producing process (Step 7 integration), and one generic step avoids a transfer-only duplicate. A is recommended for 2 because a received intermediate is feed to the receiving refinery, which is the scope of CM 1.2.5.1.

## Why nothing was added

Hamid's ruling set the check as a condition. The map gets no new process from a gap the check finds unless he rules on it (EPM-DEC-001-0047, What follows, item 4).
