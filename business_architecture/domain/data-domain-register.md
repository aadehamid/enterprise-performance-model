# Data Domain Register

**ID:** EPM-BA-DOM-001
**Version:** 0.1
**Status:** Draft
**Owner:** Enterprise Performance Model initiative
**Last updated:** 2026-09-29
**Scope:** Downstream Oil & Gas data domains, anchored on Marathon Petroleum Corporation (MPC) public filings
**Review trigger:** Each new domain proposal; Step 5 (party / organization modules) design

## Purpose

One place listing the data domains the Enterprise Performance Model
recognizes: their status, what each owns, where the evidence is, and how they
connect. Evidence stays in the linked reference files. This register records
the outcome.

## Evidence rule

Domain evidence must be close to Downstream Oil & Gas. The order is:

1. MPC's own SEC filings and MPC public materials (`../reference/mpc/`)
2. U.S. refining peers' SEC filings (`../reference/downstream-peers/`)
3. Downstream-specific industry sources (e.g. SAP IS-Oil, the
   industry-specific elements of the APQC Downstream Petroleum PCF, EIA
   petroleum definitions)
4. Broader energy or cross-industry sources, as support only

Generic frameworks never decide a boundary on their own.

## Domains

| Domain | Status | Owns | Classification / key concepts | Evidence |
|---|---|---|---|---|
| **Customer** | Classification adopted (2026-09-29). Domain model: Draft (`customer_domain_problem_statement_v0.1.md`) | Parties in a customer role, customer accounts, roles, channel classification | C1 Brand jobber · C2 Direct dealer · C3 Wholesale marketing customer · C4 Independent retailer · C5 Unbranded customer (C5.1–C5.4) · C6 Spot market buyer · C7 Export / international customer · C8 Crude oil customer; facets: brand status, contract type, product line, segment, geography, delivery tier | `../reference/mpc/customer-classification-evidence.md` |
| **Commercial Pricing & Price Realization** | Proposed (scope per D1–D4, proposed) | Proposed scope: the price MPC offers or contracts, how it is applied and adjusted, and what is realized | P3 realized price · P4 feedstock and purchased-product pricing · P5 regional / location differentials · P6 product and quality · P7 customer and contract · P8 logistics and tariff · P9 incentives, promotions and rebates · P11 (price-list governance) | `../reference/mpc/pricing-domain-evidence.md` |
| **Market Data** | Proposed (D1, proposed) | Proposed scope: external and constructed market observations: benchmarks, assessments, curves, differentials, and their methodology and licensing | P1 market benchmark pricing · P11 (benchmark methodology and publication) | `../reference/downstream-peers/pricing-market-data-risk-evidence.md` |
| **Commercial Risk** | Proposed (D2, proposed). Not yet defined | Proposed scope: commodity price exposure, derivatives, limits, valuations (middle office) | P10 price risk and hedging; process map CM 1.2.2 Confirmations & Risk Management | `../reference/downstream-peers/pricing-market-data-risk-evidence.md` |

Proposed (D3): P2 (benchmark margin indicators, margin capture) isn't a
domain. It becomes KPI Store measures built on Market Data.

The pricing split above (D1–D4) is **proposed, not decided**. It follows
`../reference/mpc/pricing-domain-evidence.md` §5 and stays proposed until
Hamid records a decision. Boundary rules 2 and 3 below depend on it.

## Boundary rules

1. **Customer isn't the parent of Pricing.** They connect through agreements and
   eligibility. The customer master holds stable classification (C1–C8). An
   agreement or eligibility record decides which price schedule or formula
   applies.
2. **Pricing references Market Data and doesn't own it** (depends on D1, proposed). A contract formula
   points to a benchmark. The benchmark observation, its source, methodology
   version and licence live in Market Data.
3. **Pricing creates exposure and Commercial Risk manages it** (depends on D2, proposed). Fixed-price sales
   and purchases are Pricing records. The resulting exposure, hedges and limits
   are Commercial Risk records.
4. **Exchange and matching buy/sell counterparties aren't customers** unless
   they also buy under a revenue-recognized sale (MPC reports these receivables
   as "non-customer balances").
5. **Retail pump prices sit outside MPC's data.** MPC has no company-operated
   retail. Jobbers and direct dealers set posted prices. MPC's retail pricing
   data is limited to brand-program incentives.
6. **Prices are bitemporal.** Keep both when a price applied and when it was
   recorded, approved or corrected.

## How the ontology carries this (Step 5 onward, proposal)

- Each classification (C1–C8, P1–P11) becomes a SKOS concept scheme with codes
  as `skos:notation`, MPC wording as `skos:definition`, and `dcterms:source`
  citations.
- Customer classes are assigned at the customer account / relationship level,
  following the role pattern in `customer_domain_problem_statement_v0.1.md`.
- Domain boundaries map onto the ontology modules (`party`, `organization`,
  `kpi`, and any new module), each introduced by its own decision.

## Open items

- Define the Market Data and Commercial Risk domains (scope, owners, entities).
- Reconcile the proposed pricing data products with the existing Master
  Pricing and Rack Pricing data products.
- Confirm the capacity-utilization basis and regional per-barrel margins
  before any KPI is defined on them.

## Change log

| Date | Change |
|---|---|
| 2026-09-29 | v0.1 created: Customer (classification adopted), Commercial Pricing & Price Realization, Market Data and Commercial Risk (proposed) |
