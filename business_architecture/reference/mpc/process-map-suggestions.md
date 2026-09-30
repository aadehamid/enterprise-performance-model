# Process-Map Suggestions from MPC Material

**Status:** Proposed — none applied · **Date:** 2026-09-29 ·
**Target:** `business_architecture/business_process/downstream_process_map.json`
(and value-stream / data-product JSON where noted)

The process map is the process authority. These are suggestions drawn from
MPC's public filings (see `source-register.md`). Each needs Hamid's decision
(accept / reject / defer), and accepted items go through the normal reviewed
authoring path — IDs, definitions, then the ontology pipeline — never a direct
edit from this folder.

Compared against the map on `main` at `1b3105e`.

| ID | Where in the map | What MPC shows (source) | Suggestion | Ontology impact |
|---|---|---|---|---|
| MPC-P01 | `Midstream` (L1 under Downstream Operations) has **no child processes** | Midstream is one of three reportable segments. It serves R&M through pipelines, terminals, towboats and barges under fee-based agreements (MPC-S01 Item 1, Item 2) | Decide scope first. Recommended: model the **fuels-logistics** part that serves R&M (pipeline transport, terminal operations, marine, storage). Treat gas gathering/processing and NGL fractionation as out of scope unless a KPI needs them | New L2/L3 processes; terminals become sites. Relates to CM 1.2.7 Products Distribution Management and CM 1.3.10 Terminal Loading |
| MPC-P02 | `Refining` and two of its L2 nodes have **no IDs** (`Refinery Performance and Risk Coordination`, `Refinery Asset Reliability and Turnaround Coordination`); the turnaround node has no children | Turnarounds are periodic at every refinery and reported as their own cost line ($1.39/bbl) (MPC-S01 Item 1, Item 7) | Give the nodes IDs. Add turnaround-lifecycle children (plan scope, schedule, execute, restart, close out cost) | Stable URIs for these nodes; a clean anchor for the turnaround-cost KPI |
| MPC-P03 | Refining children are planning-only (CM 1.1.4, 1.1.7) | Refineries are integrated and **move intermediate products between sites** to use capacity, including during partial shutdowns (MPC-S01 Item 1) | Add an inter-refinery intermediate-transfer process under planning/scheduling (or confirm it's covered by CM 1.1.7 and say so in its definition) | Material-flow edge between sites; related to `dependsOnOutputOf` |
| MPC-P04 | No renewable-diesel line of business; renewables appear only as trading/forecast steps (CM 1.2.1.1.3, CM 1.2.1.3.6) and `renewablesSpecific` flags | Renewable Diesel is a reportable segment: feedstock aggregation, pre-treatment, processing, JV operations (MPC-S01 Item 1) | Decide scope. At minimum add renewable **feedstock sourcing** and **renewable fuel marketing**. Full production can stay parked | Product scheme needs a renewable-diesel branch |
| MPC-P05 | RINs covered (CM 1.2.3.1.7, CM 1.2.4.3.6); no LCFS or 45Z credit process found | RINs, LCFS and 45Z credits used toward RFS and LCFS compliance obligations; RIN integrity program (MPC-S01 Item 1) | Broaden to **Regulatory Credit Management**: obligation calculation, credit generation, purchase with integrity vetting, retirement, reporting, across RIN / LCFS / 45Z | One `RegulatoryCredit` concept with kinds, not three parallel process trees |
| MPC-P06 | Marketing (CM 1.3) has brand strategy and brand-standard processes, but no process **names** jobber or direct-dealer channels | Four markets (wholesale incl. export, spot, branded, retail distribution); 7,882 jobber outlets; 1,162 direct-dealer locations (MPC-S01 Item 1, Item 2) | Make the channel explicit — either as a channel dimension on Order Management / Channel Pricing & Sales, or as channel-specific L4 steps (e.g. jobber supply agreements, dealer supply contracts) | Party roles (jobber, direct dealer, wholesale, spot, export customer) in Step 5; channel becomes a KPI dimension |
| MPC-P07 | Company-operated retail steps (if any remain) | MPC sold company-operated retail (Speedway) in 2021; retail now runs through independent jobbers and dealers (MPC-S01 Item 1) | Review retail-facing nodes (e.g. CM 1.3.6.6.15 Manage Brand Loyalty Programs; the `Retail Payments` data product) and mark which ones assume company-operated sites rather than branded jobber/dealer sites. Keep them if the target company differs from MPC, but record that in their scope notes | Scope notes only; no deletion (deprecation protocol) |
| MPC-P08 | CM 1.3.8.4.6 Manage Intercompany Invoicing | R&M pays MPLX $3.69/bbl under long-term fee-based agreements (MPC-S01 Item 7) | Confirm that intercompany logistics fees are in scope of that process and of O2C settlement | Affiliate is a party role; fee agreements become contract instances |
| MPC-P09 | Value stream `Commercial Hydrocarbon Lifecycle` / KPI hooks | R&M margin per barrel, opex/bbl, distribution cost/bbl, turnaround cost/bbl, regional 3-2-1 crack spreads (MPC-S01 Item 7) | Attach these as candidate measures to the matching stages (Price Management, Performance Management & Backcasting). Classify each per the measurement taxonomy — they are **not** automatically KPIs | Seeds the `kpi` module with cited, audited definitions |

## Not suggested

- Adding MPC-specific brands, site names or tools to process *names*. The
  process map stays company-neutral; MPC specifics belong in instance data.
- Changing any node's meaning to fit MPC. Where MPC and the map differ in
  meaning, the difference is raised here, not reconciled silently.
