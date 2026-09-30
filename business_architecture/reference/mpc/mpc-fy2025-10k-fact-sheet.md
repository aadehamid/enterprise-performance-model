# MPC FY2025 Form 10-K — Fact Sheet

**Status:** Draft · **Source:** MPC-S01 (FY2025 10-K, filed 2026-02-26) unless
noted · **Extracted:** 2026-09-29

Figures are as reported. `mbpcd` = thousand barrels per calendar day;
`mbpd` = thousand barrels per day; `mbbls` = thousand barrels.
The "Ontology note" column says how the fact is expected to be modeled; it is
a proposal, not a decision.

## 1. Enterprise and legal structure

| Fact | Value | 10-K location | Ontology note |
|---|---|---|---|
| Company | Marathon Petroleum Corporation; "integrated, downstream and midstream energy company" | Item 1, Overview | `org:FormalOrganization` instance |
| Origin | Incorporated in Delaware 2009-11-09; spun off from Marathon Oil 2011-06-30 | Item 1, Corporate History | `prov` / event history, low priority |
| Andeavor acquisition | Completed 2018-10-01 | Item 1, Corporate History | Explains West Coast assets |
| Speedway sale | Company-operated retail sold to 7-Eleven, 2021-05-14 | Item 1, Corporate History | MPC no longer operates company-owned retail stations |
| MPLX LP | Sponsored MLP formed 2012; at 2025-12-31 MPC owned the general partner and ~64% of common units (~647 million); MPC controls and consolidates MPLX | Item 1, Overview; Item 7 | Separate legal entity, controlled and consolidated; `org:subOrganizationOf` vs an ownership relation needs a decision |
| Employees | ~18,500 (about 3,800 under collective bargaining) | Item 1, Human Capital | — |
| Management system | Operational Excellence Management System; RC14001 scope, ISO 9001-aligned, Plan-Do-Check-Act | Item 1, Human Capital | Possible governance reference |

## 2. Reportable segments (three)

| Segment | What it does (10-K wording, condensed) |
|---|---|
| Refining & Marketing | Refines crude and other feedstocks in Gulf Coast, Mid-Continent and West Coast refineries; buys refined products and ethanol for resale; sells to wholesale (domestic + export), spot buyers, Marathon®-branded jobbers, and ARCO® direct dealers |
| Midstream | Primarily MPLX. Gathers, transports, stores, distributes crude, refined products (incl. renewable diesel); gas gathering/processing; NGL transport, fractionation, storage, marketing. Serves R&M under long-term fee-based agreements |
| Renewable Diesel | Processes renewable feedstocks into renewable diesel; wholly owned Dickinson facility plus joint ventures |

Segment adjusted EBITDA (all reportable segments): $12.78 B (2025),
$12.10 B (2024), $19.81 B (2023). — Item 7.

**Ontology note:** segments are organizational units *and* reporting
dimensions. Model them once (organization module) and let KPIs reference
them as a dimension.

## 3. Refineries (13; 2,986 mbpcd crude capacity at 2025-12-31)

| Region | Refinery | Capacity (mbpcd) | Notes from 10-K |
|---|---|---|---|
| Gulf Coast (1,248) | Galveston Bay, Texas City, TX | 631 | Largest; combined Texas City + Galveston Bay; STAR project +40 mbpcd (2023); 1,055 MW cogeneration |
| | Garyville, LA | 617 | Export access; OSHA VPP Star |
| Mid-Continent (1,186) | Catlettsburg, KY | 307 | Sweet + sour incl. Utica; asphalt |
| | Robinson, IL | 253 | Anode-grade coke |
| | Detroit, MI | 146 | Only operating refinery in Michigan |
| | El Paso, TX | 133 | |
| | St. Paul Park, MN | 105 | |
| | Canton, OH | 100 | Utica crude |
| | Mandan, ND | 72 | Mainly North Dakota sweet |
| | Salt Lake City, UT | 70 | Largest in Utah |
| West Coast (552) | Los Angeles, CA | 365 | Largest West Coast refinery; CARB fuels |
| | Anacortes, WA | 119 | Canadian, ND, ANS, international crudes |
| | Kenai, AK | 68 | Mainly Alaska crude |

Capacity history: 2,986 (2025), 2,963 (2024), 2,950 (2023) mbpcd. — Item 7.

Process units named: atmospheric and vacuum distillation, fluid catalytic
cracking, hydrocracking, catalytic reforming, coking, desulfurization, sulfur
recovery. — Item 1.

Operating facts relevant to process modeling (Item 1):
- Refineries are integrated with each other via pipelines, terminals and
  barges; **intermediate products move between refineries** to optimize
  operations, including during partial shutdowns.
- **Turnarounds** (planned maintenance with temporary unit shutdown) are
  performed periodically at each refinery.
- "Refining throughput can exceed crude oil refining capacity" because of
  other charge and blendstocks and turnaround timing. — Item 2.

**Ontology note:** `Refinery` (a site), `ProcessUnit`, `Region` and
`CrudeCapacity` (a quantity with unit and as-of date) are candidate classes.
Capacity is a dated quantity, not a static attribute.

## 4. Feedstock and production (mbpd)

| Crude supply by origin | 2025 | 2024 | 2023 |
|---|---|---|---|
| United States | 1,966 | 1,840 | 1,782 |
| Canada | 599 | 604 | 597 |
| Other international | 222 | 270 | 298 |
| **Total crude** | **2,787** | **2,714** | **2,677** |

Other charge and blendstocks: 202 (2025), 208 (2024). Crude is bought under
term contracts (market-related pricing) and spot purchases or exchanges.

| Refinery production by product group | 2025 | 2024 | 2023 |
|---|---|---|---|
| Gasoline | 1,499 | 1,490 | 1,526 |
| Distillates | 1,093 | 1,070 | 1,037 |
| Propane | 67 | 67 | 66 |
| NGLs and petrochemicals | 195 | 192 | 182 |
| Heavy fuel oil | 90 | 59 | 52 |
| Asphalt | 79 | 81 | 80 |
| **Total** | **3,023** | **2,959** | **2,943** |

Named products include reformulated gasoline, blend-grade gasoline (for
ethanol blending), ULSD, jet fuel, kerosene, No. 1 and No. 2 fuel oils,
propylene, xylene, butane, benzene, toluene, cumene, fuel-grade and
anode-grade coke, asphalt (cements, polymer-modified, emulsified, industrial,
roofing flux). Refinery-based asphalt capacity 143 mbpcd.

**Ontology note:** the six product groups are a ready-made top level for a
product SKOS scheme; named products sit beneath them.

## 5. Sales channels and markets

| Fact | Value |
|---|---|
| Four refined-product markets | Wholesale (incl. exports), spot, branded, retail distribution |
| Brand jobber outlets | 7,882 in 40 states, DC and Mexico (mainly Marathon® brand; also Shell, Mobil, Tesoro, others) |
| Direct dealer locations | 1,162 under long-term supply contracts, mainly Southern California, largely ARCO® |
| Total refined product sales | 3,718 mbpd (2025); 3,585 (2024); 3,510 (2023) |
| Of which marketed directly to end-users (incl. branded retail) | 2,449 mbpd (2025) |
| Exports | 401 mbpd (2025): gasoline 114, distillates 195, asphalt/NGLs/other 92; mainly from Garyville, Galveston Bay, Anacortes, Los Angeles |
| Propane split | ~80% home heating / ~20% industrial-petrochemical |
| Seasonality | Gasoline, diesel and asphalt demand higher in spring and summer |

**Ontology note:** jobber, direct dealer, wholesale customer, spot buyer and
export customer are *roles* a party plays, not subclasses of customer — a
case for the ORG / party role pattern (Step 5).

## 6. Logistics assets

| Fact | Value | Location |
|---|---|---|
| R&M owned and operated terminals | 18 (2 light products, 16 asphalt), 5,119 mbbls tank storage | Item 2 |
| MPLX owned and operated terminals | 88 (81 light products, 7 asphalt), 34,993 mbbls tank storage | Item 2 |
| MPC-retained marine | 4 Jones Act MR product tankers, 3 Jones Act 750-series ATBs | Item 1 |
| Other modes | Transport trucks and trailers; leased and owned railcars; MPLX towboats and barges | Item 1 |
| Fees R&M pays MPLX | $3.69 per barrel (2025), inside distribution costs | Item 7 |

## 7. Renewable Diesel

| Facility | Ownership | Capacity |
|---|---|---|
| Dickinson, ND renewable diesel | Wholly owned | 184 million gal/yr |
| Martinez Renewables (CA) | 50/50 JV with Neste | 730 million gal/yr incl. pretreatment; full capacity late 2024 |
| Cincinnati, OH aggregation; Beatrice, NE pre-treatment | Wholly owned | Feedstock supply to Dickinson and Martinez |
| Green Bison Soy Processing, Spiritwood, ND | 25% (ADM 75%) | ~600 million lb/yr refined soybean oil |

Renewable diesel generates federal RINs, 45Z tax credits and LCFS credits,
which MPC uses toward its RFS and LCFS compliance obligations. MPC runs a RIN
integrity program to vet purchased RINs. — Item 1.

## 8. KPIs and measures MPC reports (Item 7)

| Measure | Definition as reported | 2025 | 2024 | 2023 |
|---|---|---|---|---|
| Crude oil refining capacity | Capacity at year end (mbpcd) | 2,986 | 2,963 | 2,950 |
| Net refinery throughput | mbpd | 2,989 | 2,922 | 2,903 |
| R&M margin per barrel (non-GAAP) | Sales revenue less cost of refinery inputs and purchased products, ÷ net refinery throughput | $16.87 | $16.01 | $23.00 |
| Refining operating costs per barrel | Excludes planned turnaround and D&A | $5.59 | $5.34 | $5.31 |
| Distribution costs per barrel | Excludes D&A | $5.67 | $5.48 | $5.33 |
| R&M adjusted EBITDA per barrel | Margin − opex − distribution − LIFO adj. − other | $5.63 | $5.33 | $12.94 |
| Planned turnaround costs per barrel | — | $1.39 | $1.31 | $1.11 |
| D&A per barrel | — | $1.49 | $1.65 | $1.72 |

**R&M margin (full definition):** "the difference between the prices of
refined products sold and the costs of crude oil and other charge and
blendstocks refined, including the costs to transport these inputs to our
refineries and the costs of products purchased for resale."

**Regional crack spreads (MPC's benchmarks, all 3-2-1):**
- Gulf Coast: 3 bbl MEH crude → 2 bbl USGC CBOB + 1 bbl USGC ULSD
- Mid-Continent: 3 bbl WTI → 2 bbl Chicago CBOB + 1 bbl Chicago ULSD
- West Coast: 3 bbl ANS → 2 bbl LA CARBOB + 1 bbl LA CARB diesel

The benchmark cracks exclude the cost of RINs. The sweet and sour crude
differentials explain why realized margin differs from the blended crack.

**Ontology note:** this is a clean example of the KPI chain.
*Crack spread* is a market indicator (benchmark), *R&M margin per barrel* is a
reported non-GAAP measure, and *margin capture* (realized ÷ benchmark) would
be a derived KPI. Each needs a formula, unit (USD/bbl), time grain and
dimension (region). The definitions above are candidates for the `kpi`
module, cited to MPC-S01.

## Open items

- **Capacity basis.** The Q4 2025 earnings release excerpt (MPC-S07, not yet
  read in full) appears to show 2,963 mbpcd alongside a utilization %. The 10-K
  gives 2,986 at year end. Confirm whether utilization uses average or
  year-end capacity before defining `CrudeCapacityUtilization`.
- Read MPC-S03 (Q2 2026 10-Q) for changes since FY2025.
- Read MPC-S08 (MPLX 10-K) before modeling Midstream processes.
