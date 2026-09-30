# Pricing as a Data Domain — Evidence

**Status:** Draft (candidate domain, not adopted) · **Date:** 2026-09-29 ·
**Domain:** Pricing

This is evidence for treating Pricing as a data domain, gathered the same way
as the customer classification: MPC's 10-K filings first, then MPC's own public
materials, then neutral industry definitions (EIA) where MPC doesn't disclose
its methods. MPC says little about *how* it sets commercial prices, which is
competitively sensitive. What it does disclose is the pricing **basis** of its
contracts, the **benchmarks** it measures against, and the **regulated and
fee-based** prices in its logistics business.

## 1. What MPC discloses (FY2025 10-K, MPC-S01, unless noted)

| # | Evidence (quoted or condensed) | Location | Pricing concept it grounds |
|---|---|---|---|
| P1 | "The vast majority of our Refining & Marketing and Renewable Diesel contracts contain pricing that is based on the market price for the product at the time of delivery." Payment is due "shortly after delivery". | Notes, Revenue recognition | **Pricing basis**: market-based, priced at delivery. Pricing event = delivery (title/control transfer) |
| P2 | Crude is bought under "negotiated term contracts and purchases or exchanges on the spot market. Our term contracts generally have market-related pricing provisions." | Item 1, Crude Oil Supply | **Purchase pricing**: term vs spot; market-related (index-linked) formulas |
| P3 | Derivatives hedge "fixed price sales of refined products … by converting the refined product sales to market-based prices" | Item 7A; Notes, Derivatives | **Fixed-price** sales exist, alongside market-based; price-risk link |
| P4 | Benchmark spot prices (dollars per gallon): Chicago CBOB, Chicago ULSD, USGC CBOB, USGC ULSD, LA CARBOB, LA CARB diesel | Item 7, R&M | **Market price assessment** by product × location |
| P5 | Market indicators: WTI, MEH, ANS crude prices; regional 3-2-1 crack spreads; blended crack weighted 42% USGC / 40% Mid-Continent / 18% West Coast (from Q2 2024); sweet and sour crude differentials | Item 7, R&M | **Benchmarks, spreads and differentials** as derived price measures, with methodology changes over time |
| P6 | Benchmark cracks "do not reflect the market cost of RINs". Purchased-RIN expense $1.33 B (2025), $1.07 B (2024) | Item 7 | **Regulatory credit price** as a separate price component |
| P7 | C2+ NGL pricing is a Mont Belvieu composite. Barrel mix changed between 2023 and 2024 (e.g. ethane 35% → 10%) | Item 7, Midstream | **Composite price index** with a versioned composition |
| P8 | FERC-regulated pipeline tariffs: indexed ceiling rates, cost-of-service, market-based and settlement rates, "grandfathered rates" | Item 1, Rate Regulation | **Regulated tariff** as a price type with its own rules |
| P9 | Long-term fee-based agreements with MPLX, some with minimum quarterly throughput and distribution volumes. $3.69/bbl paid to MPLX in 2025 | Item 7 | **Fee / intercompany service price** with volume commitments |
| P10 | MPLX marine business "generates revenue under a fee-for-capacity contract with MPC". Fuels distribution revenue "based on the volume of MPC's products sold each month" | MPC-S11 (Business of MPC 2026) | **Capacity-based and volume-based fees** |
| P11 | MPLX buys and sells NGLs and natural gas "at index" prices, and some MPLX compensation is commodity-based rather than fee-based | Item 7A; Item 1A | **Index pricing** and fee-based vs commodity-based contracts |
| P12 | California SB X1-2: authorizes a maximum gross gasoline refining margin and penalty, expands price/supply reporting to the CEC, and created the Division of Petroleum Market Oversight. In Aug 2025 the CEC said it wouldn't act on a margin cap for at least five years | Item 1A | **Regulatory oversight** of pricing and margin; reporting obligations |
| P13 | Exposure to litigation under "consumer protection and product pricing laws" | Item 1A | **Pricing compliance** |
| P14 | R&M revenue fell $7.45 B in 2025, "primarily due to a decrease in average refined product sales prices of $0.18 per gallon" | Item 7 | **Realized price** as a reported measure |
| P15 | Exchange contracts and matching buy/sell arrangements settle "grade or location differentials" in cash | Notes, Revenue | **Quality and location differentials** as price adjustments |

## 2. Industry price-type definitions (not disclosed by MPC)

MPC doesn't describe its rack, dealer-tank-wagon or bulk price-setting. The
repo's process map already has these concepts (see §4), so neutral
definitions come from the U.S. Energy Information Administration (MPC-S14):

| Price type | EIA definition |
|---|---|
| Rack sales | "Wholesale truckload sales or smaller of petroleum products where title transfers at a terminal." |
| Dealer tank wagon (DTW) sales | "Wholesale sales of petroleum products priced on a delivered basis to a retail outlet." |
| Bulk sales | "Wholesale sales of petroleum products in individual transactions which exceed the size of a truckload." |

These tie price types to the customer classes. For example, rack pricing
typically serves unbranded and jobber liftings at terminals, and DTW pricing
serves delivered-to-station supply. That link is industry practice, not MPC
disclosure, and must be labelled as such.

## 3. Candidate concepts for the domain

| Concept | Grounded by | Notes |
|---|---|---|
| Market price assessment (product × location × date × source) | P4, P5, P7 | External reference data (exchanges, price reporting agencies). Needs licensing notes before any values are stored |
| Benchmark / index and its methodology version | P5, P7 | Composition changes over time, so methodology must be versioned |
| Spread and differential (crack, sweet/sour, grade, location) | P5, P15 | Derived price measures. They belong to the KPI chain, not master data |
| Price agreement / pricing term on a contract (basis, formula, pricing event, period) | P1, P2, P3 | Market-based vs fixed. Formula = index + differential; pricing event = delivery |
| Price type (rack, DTW, bulk, spot, term, contract) | §2, P2 | Industry vocabulary. The process map already uses rack pricing |
| Tariff and fee (regulated tariff, fee-for-capacity, volume-based fee, minimum-volume commitment) | P8, P9, P10 | Logistics and intercompany pricing |
| Regulatory credit price component (RIN, LCFS) | P6 | Interacts with the regulatory-credit suggestion MPC-P05 |
| Realized price | P14 | A measure, owned by the KPI chain |
| Pricing compliance and reporting obligation | P12, P13 | Governance attributes, not prices |

## 4. What the repo already has

- **Process map:** Sales Pricing Management, Pricing Strategy Management,
  Maintain Price & Discount Master Data, Capture Product/Crude/Feedstock
  Price, Create price tags for new location / material, Determine /
  Implement sales price, Analyze Pricing Performance, and others.
- **Value stream (Commercial Hydrocarbon Lifecycle):** Price Management,
  Market Price Calculation & Validation, Rack Price Setting, Channel Pricing &
  Sales.
- **O2C value stream:** Maintain Price & Discount Master.
- **Data products:** Master Pricing, Rack Pricing.
- **Customer domain problem statement:** "Pricing party" role;
  "Contract, pricing-index, differential, volume, and exchange-agreement
  association".

## Open items

- Decide the domain boundary (see the recommendation in the PR discussion):
  price *data* vs price *measures* (KPIs) vs price *risk* (derivatives, owned
  by commercial risk).
- Licensing: benchmark values from price reporting agencies and exchanges are
  licensed data. Model the concepts, and store values only under license.
- Read the MPLX 10-K (MPC-S08) for tariff and fee structures in more detail.
