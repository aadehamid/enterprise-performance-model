# Proposal MPC-P03: two gaps in the physical execution of inter-refinery transfers

| Field | Value |
|---|---|
| Status | Question 1 answered by Hamid on 2026-10-19 and applied: CM 1.1.3.7.13 Reconcile Movement Losses and Gains (EPM-DEC-001-0048). Question 2 (quality of transferred intermediates) is still open |
| Date | 2026-10-18 |
| Decision | EPM-DEC-001-0047: Hamid accepted MPC-P03 "with a physical-execution coverage check" |
| Source suggestion | `business_architecture/reference/mpc/process-map-suggestions.md`, MPC-P03 |

## What the check found

MPC's refineries move intermediate products between sites, including during partial shutdowns (`reference/mpc/mpc-fy2025-10k-fact-sheet.md`, Item 1 operating facts). Hamid ruled "P03: A with a physical-execution coverage check" (`step4/review-evidence/hamid-answers/answers-2026-10-18.md`). This check carries out that condition. It goes through the steps a transfer passes from nomination to settlement; rows 2 to 6 are its physical execution, and rows 1 and 7 frame it. CM 1.1.7's description now names the existing steps.

| Step of a transfer | Covered by | Finding |
|---|---|---|
| Nomination and scheduling | CM 1.1.3.6.1 Plan & Execute Nominations | Covered. The node is generic: it does not say it includes intermediates moving between refineries |
| Movement execution | CM 1.1.3.6.2 Loading Shipment; CM 1.1.3.6.3 Track Movements and Inventory Management | Covered, generic |
| Quantity measurement | CM 1.1.3.7.4 Measure Inventory; CM 1.2.3 Actualizations (final ticket volumes) | Covered |
| Quality measurement | CM 1.2.5.1 Crude/Feed Quality Management | **Gap.** CM 1.2.5.1 covers crude and feedstock quality. No step names the quality of an intermediate that one refinery sends and another receives |
| Receipt and inventory reconciliation | CM 1.1.3.6.4 Discharge & Reconcile Load; CM 1.1.3.7.5 Perform Inventory Reconciliation; CM 1.1.5.1.2.5 Receive actual data for inventory & transfers | Covered |
| Loss and gain | CM 1.1.3.7.13 Reconcile Movement Losses and Gains (added 2026-10-19, EPM-DEC-001-0048) | **Was a gap; filled.** No step names the loss and gain reconciliation of a movement. The Loss Control data product ("Custody transfer, gain/loss, and shrinkage data across movements and terminal operations", `data_product_portfolio.json`) exists without a process that produces it; the worklog's Step 7 row lists "Loss Control ownership" as open |
| Settlement | CM 1.2.4.1.18 Settle Intermediates | Covered |

Assumption behind "covered": CM 1.1.3 (Distribution Planning & Scheduling and Inventory Management) handles intermediates as well as finished products. Its inventory steps include "Develop Intermediates Inventory Policy" (CM 1.1.3.7.2), which supports that reading. If Hamid reads CM 1.1.3 as finished products only, the rows that rest on CM 1.1.3 alone become gaps: nomination and scheduling, and movement execution. Quantity measurement keeps CM 1.2.3, receipt and reconciliation keep CM 1.1.5.1.2.5, and settlement keeps CM 1.2.4.1.18, because those sit outside CM 1.1.3.

## What Hamid decides

1. **Loss and gain.** (A, recommended) Add one step, "Reconcile Movement Losses and Gains", under CM 1.1.3.7 Inventory, covering every movement, not only inter-refinery transfers; it produces the Loss Control data product. (B) Record loss and gain as part of CM 1.1.3.6.4 Discharge & Reconcile Load, by description only. (C) Leave the gap open.
2. **Quality of transferred intermediates.** (A, recommended) Widen CM 1.2.5.1's description so it covers intermediates received as feed from another refinery. (B) Add a step under CM 1.1.7. (C) Leave it.

A is recommended for 1 because the data product already exists and needs a producing process (Step 7 integration), and one generic step avoids a transfer-only duplicate. A is recommended for 2 because a received intermediate is feed to the receiving refinery, which is the scope of CM 1.2.5.1.

## Why nothing was added

Hamid's ruling set the check as a condition. The map gets no new process from a gap the check finds unless he rules on it (EPM-DEC-001-0047, What follows, item 4).
