# Pricing Data Domain — Classification and Evidence

**Status:** Candidate domain. Classification P1–P11 proposed by Hamid
(2026-09-29). Two scope decisions are open (§5). · **Domain:** Pricing ·
**Evidence checked:** 2026-09-29

Pricing is a separate data domain, linked to Customer, Product, Contract,
Supply/Logistics, Market Data, Tax and Finance. It is not a product attribute:
the economically meaningful price depends on product and grade, location,
customer channel, contract, timing, benchmark, taxes and adjustments. MPC
doesn't publish customer-specific price books (commercially sensitive). It does
disclose the pricing **basis** of its contracts, the **benchmarks** it measures
against, realized-price movements, margin definitions, and regulated and
fee-based logistics prices. Every claim below is checked against MPC filings
(source IDs from `source-register.md`). Industry-only definitions are labelled
as such.

## 1. Pricing classification (P1–P11)

| Code | Pricing class | Definition | MPC evidence (verified) |
|---|---|---|---|
| P1 | Market benchmark pricing | Published market observations used to value or formulate prices | Benchmark spot prices (Chicago / USGC CBOB and ULSD, LA CARBOB, LA CARB diesel) and crude benchmarks WTI, MEH, ANS (MPC-S01 Item 7) [E4, E5] |
| P2 | Benchmark margin indicators | Constructed indicators that turn market prices, yields and operating assumptions into an expected margin | R&M Margin Indicator and margin capture (MPC-S07); regional 3-2-1 cracks and blended crack (MPC-S01 Item 7) [E16, E17, E5] |
| P3 | Refined-product price realization | Actual realized sales value by product and volume | Price–volume revenue bridges in every 10-Q and 10-K [E14] |
| P4 | Feedstock and purchased-product pricing | Price or cost of crude, blendstocks, renewable inputs and purchased refined products | Term crude with "market-related pricing provisions" [E2]; margin definitions deduct refinery inputs and purchased products [E18] |
| P5 | Regional / location differentials | Value differences by region, hub, refinery, terminal or delivery area | R&M margin reported by Gulf Coast / Mid-Continent / West Coast [E19]; grade and location differentials in exchanges [E15] |
| P6 | Product and quality pricing | Pricing by product family, grade or specification, renewable attribute, blend | Separate product groups and benchmarks per product and grade (CBOB, ULSD, CARBOB) (MPC-S01) [E4] |
| P7 | Customer and contract pricing | Channel-, customer- or agreement-specific terms, formulas, discounts, settlement rules | "Vast majority" of contracts priced at market at delivery [E1]; fixed-price sales exist [E3]. Details not disclosed. Classes C1–C8 in `customer-classification-evidence.md` |
| P8 | Logistics, distribution and tariff pricing | Pipeline, terminal, marine, freight and service rates | FERC tariffs [E8]; MPLX fees and minimum volumes [E9, E10]; distribution cost per barrel [E18]; Midstream "higher rates and throughputs" [E20] |
| P9 | Incentive, promotion and rebate pricing | Loyalty rewards, trade allowances, volume rebates, posted-price discounts | Marathon Rewards: "at least 5¢ in Rewards on every gallon"; "20¢ per gallon on first fill-up" (MPC-S15) [E21] |
| P10 | Price risk and hedging | Commodity-price exposures, derivatives, limits, fair value | Futures, swaps, options to hedge price risk; fixed-price sales converted to market-based (MPC-S01 Item 7A) [E3]. **Scope open, see §5** |
| P11 | Price governance and audit | Source, methodology, currency, UOM, publication time, effective period, approval, correction history | Market data updated monthly by the second business day after month end (MPC-S07) [E16]; benchmark methodology changes (blended-crack weights, NGL basket) [E5, E7]; margin definition changed (derivative wording) [E18] |

### Keep these concepts separate

| Concept | Meaning | MPC-aligned example |
|---|---|---|
| Market price / benchmark | External or constructed market observation | Crack spread, crude differential, spot assessment |
| Offered or contractual price | What a customer is entitled to under a price list, formula or agreement | Benchmark + terminal differential for a dealer (illustrative; MPC doesn't disclose) |
| Realized net price | What is actually earned at transaction grain after adjustments | Average refined product sales price change of $0.15/gal (Q1 2026) |
| Margin | Value left after input and purchased-product cost | R&M margin $16.87/bbl (2025) |
| Margin capture | Actual margin ÷ market-based indicator | 105% for FY2025 (MPC-S07) |

R&M margin is **not** a customer selling price. It's a defined management
(non-GAAP) measure.

## 2. Evidence register

| # | Evidence (quoted or condensed) | Source |
|---|---|---|
| E1 | "The vast majority of our Refining & Marketing and Renewable Diesel contracts contain pricing that is based on the market price for the product at the time of delivery." Payment due "shortly after delivery" | MPC-S01 Notes, Revenue recognition |
| E2 | Crude bought under "negotiated term contracts and purchases or exchanges on the spot market. Our term contracts generally have market-related pricing provisions." | MPC-S01 Item 1 |
| E3 | Derivatives (futures, swaps, options) hedge commodity price risk, including "fixed price contracts for the sale of refined products … converting the refined product sales to market-based prices". Commodity derivatives aren't designated as accounting hedges | MPC-S01 Item 7A; Notes |
| E4 | Benchmark spot prices ($/gal): Chicago CBOB, Chicago ULSD, USGC CBOB, USGC ULSD, LA CARBOB, LA CARB diesel | MPC-S01 Item 7 |
| E5 | Market indicators ($/bbl): WTI 64.73, MEH 65.87, ANS 69.72 (2025). 3-2-1 cracks: Mid-Continent WTI 13.92, USGC MEH 12.70, West Coast ANS 22.13, blended 14.89. Blended weights 42% USGC / 40% Mid-Con / 18% West Coast from Q2 2024. Sweet differential (0.73), sour (2.76) | MPC-S01 Item 7 |
| E6 | Benchmark cracks "do not reflect the market cost of RINs". Purchased-RIN expense $1.33B (2025), $1.07B (2024) | MPC-S01 Item 7 |
| E7 | C2+ NGL price = Mont Belvieu composite. Basket changed from 2023 (35% ethane) to 2024–2025 (10% ethane) | MPC-S01 Item 7 |
| E8 | FERC oil-pipeline tariffs: indexed ceiling rates, cost-of-service, market-based, settlement and grandfathered rates | MPC-S01 Item 1 |
| E9 | Long-term fee-based agreements with MPLX, some with minimum quarterly throughput and distribution volumes. $3.69/bbl paid to MPLX (2025) | MPC-S01 Item 7 |
| E10 | MPLX marine: "fee-for-capacity contract with MPC". Fuels distribution revenue "based on the volume of MPC's products sold each month" | MPC-S11 |
| E11 | MPLX buys and sells NGLs and gas at index prices. Some compensation is commodity-based rather than fee-based | MPC-S01 Item 7A; Item 1A |
| E12 | California SB X1-2: authorizes a maximum gross gasoline refining margin and penalty, expands CEC reporting, creates the Division of Petroleum Market Oversight. CEC (Aug 2025): no margin-cap action for at least five years | MPC-S01 Item 1A |
| E13 | Litigation exposure under "consumer protection and product pricing laws" | MPC-S01 Item 1A |
| E14 | Price–volume bridges. 2025: sales prices −$0.18/gal, volumes +133 mbpd (MPC-S01). Q1 2026: +$0.15/gal and +105 mbpd (MPC-S04). Q2 2026: +$1.12/gal and +7 mbpd (quarter), +$0.66/gal and +55 mbpd (year to date) (MPC-S03) | MPC-S01, S03, S04 Item 2/7 |
| E15 | Exchanges and matching buy/sells settle "grade or location differentials" in cash | MPC-S01 Notes, Revenue |
| E16 | Market data "including pricing, regional and blended crack spreads and sweet and sour crude differentials, along with a hypothetical Refining and Marketing margin indicator" is published monthly "no later than the close of business on the second business day following the end of each month" | MPC-S07 |
| E17 | Capture "represents MPC's ability to convert benchmark market conditions into realized performance … calculated by dividing our reported R&M Margin to the R&M Margin Indicator." FY2025 capture 105% | MPC-S07 |
| E18 | R&M margin = "sales revenue less cost of refinery inputs and purchased products" (FY2025 10-K). The Q2 2026 10-Q adds "which includes impacts from derivative activity". FY2025: $16.87/bbl; refining opex $5.59; distribution costs $5.67 (2024: $5.48) | MPC-S01 Item 7; MPC-S03; MPC-S07 |
| E19 | R&M margin by region, FY2025 ($ millions): Gulf Coast 6,907; Mid-Continent 7,503; West Coast 3,912; total 18,322. Total includes "Other taxes included in R&M margin" (261) | MPC-S07 |
| E20 | Midstream results "reflect higher rates and throughputs plus contributions from recently acquired assets" (Q4 2025) | MPC-S07 |
| E21 | Marathon Rewards: "at least 5¢ in Rewards on every gallon, every day"; new members "20¢ per gallon on first fill-up" (activated in-app) | MPC-S15 |

Industry definitions (not MPC), from MPC-S14 (EIA):
- **Rack sales:** "Wholesale truckload sales or smaller of petroleum products where title transfers at a terminal."
- **Dealer tank wagon (DTW) sales:** "Wholesale sales of petroleum products priced on a delivered basis to a retail outlet."
- **Bulk sales:** "Wholesale sales of petroleum products in individual transactions which exceed the size of a truckload."

## 3. Evidence notes

1. **R&M margin definition changed.** The FY2025 10-K defines it as sales
   revenue less cost of refinery inputs and purchased products. The Q2 2026
   10-Q adds "which includes impacts from derivative activity". A KPI defined
   on this measure must be versioned by filing, per P11.
2. **Distribution cost figure.** FY2025 is $5.67/bbl. $5.48 is the 2024 value.
3. **Regional margins per barrel** ($14.82 / $17.27 / $20.57) aren't verified
   yet. MPC-S07 confirms the regional margins in $ millions (E19). Per-barrel
   figures need regional net throughput from the same release.
4. **Capacity basis.** MPC-S07 reports FY2025 capacity of 2,963 mbpcd next to
   94% utilization. The 10-K reports 2,986 mbpcd at year end. The
   utilization denominator still needs confirming (fact-sheet open item).
5. **Retail pricing sits with independent operators.** MPC has no
   company-operated retail (Speedway sold in 2021). Marathon and ARCO sites are
   run by jobbers and direct dealers, so posted pump prices are their data.
   MPC's retail-facing pricing is limited to brand-program incentives such as
   Marathon Rewards (E21). Who funds those incentives isn't disclosed.
6. **Rack pricing** is industry practice (EIA definitions; OPIS publishes rack
   price coverage). MPC doesn't describe its own rack pricing. The rack location
   must be a governed terminal location, not a vendor label.
7. **Licensing.** Benchmark values from price reporting agencies and exchanges
   (OPIS, Platts, Argus, NYMEX) are licensed data. Model the concepts, and store
   values only under license.

## 4. Candidate core entities

Price · Price component (benchmark, basis / location / quality differential,
freight, tax, fee, discount, rebate, surcharge) · Price formula (ordered
components, versioned) · Price schedule · Pricing agreement · Price condition ·
Market assessment / benchmark (with methodology version) · Pricing location
(rack terminal, refinery gate, delivery point, hub, pricing zone) · Price event
(publish, approve, correct, override, expire, backdate) · Price realization
(gross-to-net at invoice or shipment line) · Promotion / incentive.

The generic shape is
`Net unit price = benchmark + differentials + freight/surcharges (+ taxes) − discounts − rebates`.
Don't hard-code it: keep the ordered components and the formula version that
applied to each transaction. Taxes may sit outside the commercial price.

**Bitemporal, effective-dated pricing** is the key design rule. Keep both
*valid time* (when the price applied) and *transaction time* (when it was
created, approved, corrected or learned). Late benchmark publications and
corrections change invoices and margins, and overwriting them breaks dispute
handling and revenue reconciliation.

Customer isn't the parent of Pricing. They connect through agreements and
eligibility: the customer master holds stable classification (C1–C8), and an
agreement or eligibility record decides which schedule or formula applies.

## 5. Open scope decisions

1. **Domain name and Market Data.** The source material both lists Market Data
   as a *separate* adjacent domain (owning benchmark observations) and proposes
   the name "Commercial Pricing, Market Data and Price Realization". Pick one:
   (a) Market Data is its own domain and Pricing consumes it, or (b) Market Data
   is a subdomain of Pricing (P1, P2, P11).
2. **P10 Price risk and hedging.** The process map already has
   CM 1.2.2 Confirmations & Risk Management, and derivatives are risk
   instruments, not prices. Options: (a) keep P10 in Pricing, or (b) own it in a
   Commercial Risk domain, with Pricing providing the exposures' price inputs.

**Downstream evidence and recommendation.** See
`../downstream-peers/pricing-market-data-risk-evidence.md`. MPC and seven U.S.
refining peers (Phillips 66, Valero, PBF, HF Sinclair, Delek, CVR, Par Pacific)
point to (1) a separate **Market Data** domain (P1 and the benchmark part of
P11), (2) a **Commercial Risk** domain owning P10, and (3) P2 margin indicators
as KPI Store measures built on Market Data. Pricing keeps P3–P9 and the
price-list part of P11. Pending Hamid's decision.

## 6. What the repo already has

- **Process map:** Sales Pricing Management, Pricing Strategy Management,
  Maintain Price & Discount Master Data, Capture Product/Crude/Feedstock Price,
  Create price tags for new location / material, Determine / Implement sales
  price, Analyze Pricing Performance.
- **Value streams:** Price Management, Market Price Calculation & Validation,
  Rack Price Setting, Channel Pricing & Sales (Commercial Hydrocarbon
  Lifecycle); Maintain Price & Discount Master (O2C).
- **Data products:** Master Pricing, Rack Pricing.
- **Customer domain problem statement:** "Pricing party" role; contract,
  pricing-index, differential, volume and exchange-agreement association.

## 7. Proposed data products (from the source material)

Market Price Observation · Crack Spread and Differential Curve · Commercial
Price Formula · Product–Location Price Schedule · Customer Price Entitlement ·
Price Adjustment · Invoice-Line Price Realization · Margin and Capture Fact.
These are to be reconciled with the existing Master Pricing and Rack Pricing data
products before any are added to `data_product_portfolio.json`.

## 8. Ownership (proposed, federated)

Commercial/marketing: customer-facing schedules, dealer/jobber terms,
promotions, overrides. Trading/supply/economics: benchmarks, differentials,
curves. Refining economics: margin-indicator methodology. Logistics (MPLX-facing):
tariffs, rates, freight. Finance: invoice and revenue reconciliation and official
realized-price and margin reporting. Enterprise data governance: identifiers,
conformance, lineage, UOM/currency, effective-dating policy.
