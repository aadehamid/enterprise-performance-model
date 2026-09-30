# Downstream Evidence: Pricing vs Market Data vs Price Risk

**Status:** Draft · **Date:** 2026-09-29 · **Question:** Should Market Data and
Price Risk sit inside the Pricing domain, or be separate domains?

Evidence is ranked by how close it is to Downstream Oil & Gas. Tier 1 is MPC,
Tier 2 is U.S. refining peers' SEC filings, and Tier 3 is downstream-specific
industry sources. Tier 4 is broader energy or cross-industry material and is
used only as support, never as the deciding evidence.

## Sources

| ID | Source | Tier | Filed / date | Accession or URL |
|---|---|---|---|---|
| DP-01 | Phillips 66, Form 10-K FY2025 | 2 | 2026-02-20 | 0001534701-26-000006 |
| DP-02 | Valero Energy, Form 10-K FY2025 | 2 | 2026-02-25 | 0001628280-26-011499 |
| DP-03 | PBF Energy, Form 10-K FY2025 | 2 | 2026-02-12 | 0001534504-26-000010 |
| DP-04 | HF Sinclair, Form 10-K FY2025 | 2 | 2026-02-27 | 0001915657-26-000016 |
| DP-05 | Delek US Holdings, Form 10-K FY2025 | 2 | 2026-02-27 | 0001628280-26-012664 |
| DP-06 | CVR Energy, Form 10-K FY2025 | 2 | 2026-02-18 | 0001376139-26-000014 |
| DP-07 | Par Pacific Holdings, Form 10-K FY2025 | 2 | 2026-02-25 | 0000821483-26-000005 |
| DP-08 | SAP Community, "Formula & Average Pricing in the Oil & Gas Industry" (practitioner blog on SAP IS-Oil) | 3 | 2015, modified 2022 | https://community.sap.com/t5/sap-for-oil-gas-and-energy-blog-posts/formula-amp-average-pricing-in-the-oil-amp-gas-industry/ba-p/13154535 |
| DP-09 | APQC PCF Downstream Petroleum v7.2.2 — **industry-specific elements only** | 3 | 2025-05-30 | `../APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx` |
| DP-10 | CCRO, Governance and Controls best practices (energy trading) | 4 | 2002–2003 (as filed at SEC) | https://www.sec.gov/Archives/edgar/data/67646/000119312503054119/dex991.htm |

MPC sources use the IDs in `../mpc/source-register.md`. All Tier 2 filings were
retrieved from EDGAR on 2026-09-29.

## Finding 1 — Market data is external, vendor-sourced, and used by many functions

| Evidence | Source |
|---|---|
| Physical forward contracts and OTC swaps "are generally valued using forward quotes provided by brokers and price index developers, such as Platts and Oil Price Information Service." | DP-01 (Phillips 66), fair value note |
| Derivatives "are valued using market quotations from independent price reporting agencies and commodity exchange price curves that are corroborated with market data." | DP-07 (Par Pacific), fair value note |
| Market indicators "as reported by Platts". "Effective RIN basket price is recalculated based on information as reported by Argus." ASCI (Argus Sour Crude Index) used "to approximate market prices for sour, heavy crude oil" | DP-03 (PBF) |
| Each refinery's margin is compared with its own benchmark crack: Tyler and El Dorado → Gulf Coast 5-3-2; Big Spring → Gulf Coast 3-2-1; Krotz Springs → Gulf Coast 2-1-1, "(Argus pricing)" / "(Platts pricing)" per component | DP-05 (Delek) |
| Market data obtained "from reputable market sources, including the NYMEX, CBOT, and Argus Media" | DP-06 (CVR) |
| MPC's sour crude basket includes the Argus Sour Crude Index. MPC publishes its own market data and margin indicator monthly | MPC-S01 Item 7; MPC-S07 |

**What it shows:** downstream refiners get benchmark data from licensed
external vendors and use the same observations for fair-value accounting,
refinery margin benchmarks, RIN pricing and investor reporting, as well as for
commercial pricing. Commercial pricing is one consumer among several.

## Finding 2 — Price risk is governed by a separate risk function under board policy

| Evidence | Source |
|---|---|
| "Our use of derivative instruments is governed by an 'Authority Limitations' document approved by our Board of Directors … establishes Value at Risk (VaR) limits. Compliance with these limits is monitored daily by our global risk group." | DP-01 (Phillips 66), Item 7A |
| "Our positions in commodity derivative instruments are monitored and managed on a daily basis by our risk control group to ensure compliance with our stated risk management policy that is periodically reviewed with our Board and/or relevant Board committee." | DP-02 (Valero), Item 7A |
| Hedging adjusted in line with "internal price risk management policies". Commodity derivatives aren't designated as accounting hedges | MPC-S01 Item 7A |

**What it shows:** price risk has its own policy, limits (VaR), board
oversight and a named control group that monitors daily. That is a different
owner and control regime from the commercial teams that set prices.

## Finding 3 — Commercial pricing is a channel activity

| Evidence | Source |
|---|---|
| "We sell our products on a wholesale basis through an extensive rack marketing network." "The majority of our rack volume is sold through unbranded channels." | DP-02 (Valero) |
| "Bulk sales — Volume sales through third-party pipelines, in contrast to tanker truck quantity rack sales." | DP-06 (CVR), glossary |
| Revenue recognized "when delivered (via pipeline, in-tank or rack), and the customer obtains control" | DP-04 (HF Sinclair) |
| "The vast majority" of R&M contracts priced at market at delivery | MPC-S01 Notes |

**What it shows:** the price types (rack, bulk, delivered) are tied to sales
channels and delivery modes. They are the commercial pricing domain's own
vocabulary, and they link to the Customer classification (C1–C8).

## Finding 4 — Downstream systems separate quotations from price formulas

| Evidence | Source |
|---|---|
| "Third party providers like Argus, CMAI, Opis publish the market price of these products on a daily basis; these prices are commonly known as quotes." F&A pricing "uses external quotations such as Platts, Reuters, and others to determine the price of a material." "The price quotations used by F&A pricing are defined in the quotation table … Quotation data can be entered manually … or electronically by remote connection to a data provider using the External Quotation Interface." | DP-08 (SAP IS-Oil) |
| Downstream PCF (industry-specific elements): **4.1.7 Evaluate commodity values** (gather market prices, forecast prices, develop forward curves, develop and maintain benchmark prices) is separate from **3.3.3.1 Develop and manage wholesale/rack fuels pricing** and from **3.7 Manage commodity positions** (3.7.3.5 "Create and communicate pricing exposure report") | DP-09 |
| Repo process map: **CM 1.2.2.3.3 Setup And Manage Curves** sits under Market Risk Management (middle office), not under Sales Pricing | `../../business_process/downstream_process_map.json` |

**What it shows:** the oil-industry system design and the downstream process
framework both hold market quotations as their own maintained data that
pricing formulas *reference*. The repo already places curve management with
risk.

## Supporting only (Tier 4)

- CCRO (DP-10): "The middle office should validate each forward curve daily."
  When front and middle office disagree, the curve "should be marked to the
  price chosen by the middle office." This comes from energy trading generally,
  but it matches Finding 2 and the repo's process-map placement.
- Excluded: APQC cross-industry elements (e.g. 9.7.5 hedging), which aren't
  specific to downstream.

## Conclusion (recommendation, for Hamid's decision)

1. **Market Data is its own domain.** Downstream refiners buy it from licensed
   vendors and use it across valuation, margin benchmarking, RIN pricing,
   planning and commercial pricing (Findings 1, 4). Pricing formulas reference
   it; they don't own it.
2. **Price risk belongs to a Commercial Risk domain.** Peers govern it with
   board-approved limits, monitored daily by a separate risk group
   (Finding 2), and the repo already places curves and market risk in the
   middle office.
3. **Pricing = Commercial Pricing & Price Realization.** It covers channel price
   types, formulas, schedules, adjustments, incentives and realization
   (Finding 3), references Market Data benchmarks, and passes fixed-price
   exposures on to Commercial Risk.

Limits of this evidence: filings describe governance and data sources, not
internal data-domain boundaries. The recommendation is an inference from
consistent downstream practice. No filing states it outright.
