# MPLX FY2025 Form 10-K — Fact Sheet

**Status:** Read for MPC-P01 · **Source:** MPLX-S01 (MPLX LP Form 10-K for the fiscal year ended 2025-12-31, accession 0001552000-26-000009, filed 2026-02-26, https://www.sec.gov/Archives/edgar/data/1552000/000155200026000009/mplx-20251231.htm) · **Extracted:** 2026-10-13

EPM-DEC-001-0011 asks for this read before ruling on MPC-P01 (the empty Midstream L1). Quotes are verbatim from the filing.

## 1. What MPLX is

| Fact | Value (quoted) | Ontology note |
|---|---|---|
| Business | "We are a diversified, large-cap master limited partnership formed by MPC in 2012 (as our sponsor) that owns and operates midstream energy infrastructure and logistics assets, and provides fuels distribution services." | `ref-mpc` holds MPLX as `org:FormalOrganization` (EPM-DEC-001-0033) |
| Ownership | "MPC owned our general partner and approximately 64 percent of our outstanding common units as of February 20, 2026." | Agrees with MPC's 10-K (as of 2025-12-31) and `refmpc:mpc-controls-mplx` |
| Segments | "two reportable segments: Crude Oil and Products Logistics and Natural Gas and NGL Services." | Not MPC's segments; MPC reports MPLX inside its Midstream segment |

## 2. The two segments

| Segment | What it does (quoted) |
|---|---|
| Crude Oil and Products Logistics | "primarily engages in the gathering, transportation, storage and distribution of crude oil, refined products, other hydrocarbon-based products, and renewables." |
| Natural Gas and NGL Services | "provides wellhead to market services including gathering, treating, processing and transportation of natural gas and NGLs." |

## 3. How MPLX serves MPC

- "In 2025, MPC accounted for 48 percent of our total revenues and other income, primarily within our Crude Oil and Products Logistics segment." Excluding significant non-cash items, the share was 48, 49 and 50 percent for 2025, 2024 and 2023.
- MPLX has "fee-based agreements with minimum volume commitments with MPC which provide us with a stable and predictable revenue stream". Under them, "we provide transportation, terminal and storage services to MPC and most of these agreements include minimum committed volumes from MPC."

## 4. Assets named (Item 2)

| Asset | Value (quoted or tabled) |
|---|---|
| Crude pipeline systems | 5,259 miles (includes "approximately 16 miles of pipeline leased from third parties and 1,168 miles of inactive pipeline") |
| Refined product pipeline systems | 3,787 miles |
| Gathering, processing, fractionation | "As of December 31, 2025, gathering and processing assets available to MPLX included approximately 9.4 Bcf/d of gas gathering capacity, 11.2 Bcf/d of natural gas processing capacity and 819 mbpd of fractionation and de-ethanization capacity." |

## 5. What this means for MPC-P01

MPC-P01 recommends modeling the fuels-logistics work that serves Refining & Marketing (pipeline transport, terminal operations, marine, storage) and leaving gas gathering, processing and NGL fractionation out unless a KPI needs them. The filing supports that line:

- The work that serves MPC sits in **Crude Oil and Products Logistics**: transport, terminals and storage under fee-based agreements with minimum volumes, where most of MPC's 48 percent of MPLX revenue falls.
- **Natural Gas and NGL Services** is wellhead-to-market gas and NGL work that does not serve the downstream refining and marketing processes in the map.

The ruling on P01 is Hamid's (EPM-DEC-001-0011): it adds children to the process map's Midstream L1, which is the source author's.

## Open items

- MPC-S08 (the MPLX annual report PDF) is not needed while this 10-K covers the facts.
