# MPC-P04: renewable feedstock sourcing and renewable fuel marketing, fit-gap

| Field | Value |
|---|---|
| Status | Applied 2026-10-18 (EPM-DEC-001-0047): one step added, one description widened; no other node needed |
| Ruling | Hamid accepted MPC-P04 "with reuse before new process creation"; production stays parked |
| Source suggestion | `business_architecture/reference/mpc/process-map-suggestions.md`, MPC-P04 |

MPC's Renewable Diesel segment runs a wholly owned plant at Dickinson, a 50/50 joint venture at Martinez, and feedstock aggregation and pre-treatment sites (`reference/mpc/mpc-fy2025-10k-fact-sheet.md` §7). The ruling asked whether the map's existing sourcing and marketing processes cover renewables by specialization, which controls are different, and which interfaces credit eligibility needs.

## Sourcing

| Need | Existing process | Fit |
|---|---|---|
| Buy feedstock | CM 1.2.5.2.1 Coordinate Feedstock Trading; CM 1.2.1.3.3 Capture Physical Trades | Fits. A vegetable oil or fat is a feedstock trade like any other |
| Plan demand and slate | CM 1.2.5.2.2 Develop Feedstock Demand; CM 1.2.5.2.3 Plan Optimal Feedstock Slate And Run Rate | Fits |
| Move and store it | CM 1.2.5.3 Crude/Feed Transportation Management; CM 1.2.5.4.2 Manage Feedstock Inventory | Fits |
| Feedstock quality | CM 1.2.5.1 Crude/Feed Quality Management | Fits for quality |
| Traceability and carbon intensity | none | **Gap, a different control.** Credit eligibility depends on the feedstock's origin and carbon intensity (`reference/downstream-peers/regulatory-credit-evidence.md`, RC-02 and RC-03). Added as CM 1.2.5.1.5 |

## Marketing

| Need | Existing process | Fit |
|---|---|---|
| Sell the fuel | CM 1.3.6.2 Sales Execution; CM 1.3.7 Order Management | Fits. Renewable diesel is a product sold through the same channels |
| Trade the environmental attributes | CM 1.2.1.3.6 Capture Environmental/Renewable Deals | Fits |
| Credits that travel with the fuel | CM 1.2.4.3.8.1 Manage Environmental Compliance Credits | Fits. EPA: assigned RINs "travel with that batch of fuel" (RC-01); transfer is part of that lifecycle |

No marketing step is added: every marketing need fits an existing process, so a renewable-only marketing node would duplicate one.

## Not in scope

Renewable fuel production (pre-treatment, hydrotreating, the plant and joint-venture operations) stays parked. The map holds no plant operations for petroleum refining either.

The two changes: CM 1.2.5's description says renewable feedstocks run through it, and CM 1.2.5.1.5 Manage Renewable Feedstock Traceability and Carbon-Intensity Evidence is new.
