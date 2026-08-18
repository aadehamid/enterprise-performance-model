# Enterprise Data Product and Consumption Model
**Artifact ID:** EPM-FOUND-006  
**Version:** 2.0 Draft  
**Status:** Working baseline  
**Last updated:** August 4, 2026  

*Foundational and derived products, medallion alignment, semantic views, and Power BI*

**Foundation navigation:** [EPM-FOUND-000](EPM-FOUND-000.md) | [EPM-FOUND-001](EPM-FOUND-001.md) | [EPM-FOUND-002](EPM-FOUND-002.md) | [EPM-FOUND-003](EPM-FOUND-003.md) | [EPM-FOUND-004](EPM-FOUND-004.md) | [EPM-FOUND-005](EPM-FOUND-005.md) | [EPM-FOUND-006](EPM-FOUND-006.md)

## Purpose
This artifact distinguishes data-product purpose from physical medallion processing layers and defines how trusted data reaches consumers.

## Foundational data product
A **foundational data product** provides a trusted, reusable representation of core business entities, events, or transactions.

It answers:

> What happened, to which business object, when, where, and under what conditions?

Examples:

- Trade and Position
- Sales Transaction
- Product Movement
- Inventory
- Market Price
- Customer and Contract
- Transportation Cost
- Refinery Production
- Asset and Unit Availability
- Product and Location Master

Foundational does not mean raw. A foundational product is cleaned, standardized, conformed, governed, discoverable, and reusable.

## Derived data product
A **derived data product** combines foundational products and applies higher-order business logic to support decisions, analysis, or performance management.

It answers:

> What decision-ready insight or performance view can be produced from trusted business facts?

Examples:

- Commercial Margin
- Netback Performance
- Risk Exposure
- P&L Attribution
- Forecast Performance
- Pricing Performance
- Logistics Performance
- Customer Profitability

## Relationship to KPIs
```text
Foundational Data Products
        ↓ supply trusted events and entities
Derived Data Products
        ↓ calculate reusable measures and diagnostics
KPI Store
        ↓ persists official KPI results, targets, thresholds, versions, and status
Semantic / Consumption Views
        ↓ expose governed contracts
Power BI Semantic Models
        ↓ add analytical relationships, measures, hierarchies, formatting, and security
Reports, APIs, AI, Automation
```

One data product may support multiple KPIs. One KPI may depend on multiple data products.

## Medallion alignment
Medallion architecture describes **processing maturity and physical organization**.

Data-product categories describe **business purpose and reuse**.

They are related but not equivalent.

| Layer | Primary purpose | Typical product relationship |
|---|---|---|
| Raw / Bronze | Preserve source data, auditability, replay, and lineage | Usually not yet a business data product |
| Silver | Clean, standardize, conform, and quality-check entities and events | Primary implementation area for many foundational products |
| Gold | Integrate domains, apply business rules, and create decision-ready structures | Primary implementation area for derived products and some integrated foundational products |
| Semantic / Consumption | Expose approved views and stable consumer contracts | Consumer interfaces for products and KPI results |

## Your semantic layer
Your architecture is:

```text
Raw
  ↓
Silver
  ↓
Gold
  ↓
Semantic / Consumption Layer
  ↓
Consumers
```

Consumers access only the semantic layer. This is a sound governed-access pattern.

The individual SQL objects are **semantic views**. Collectively, they implement consumer-facing portions of the enterprise semantic model.

They may provide:

- business-friendly names;
- stable joins and conformed identifiers;
- current-record logic;
- security predicates;
- approved row-level calculations;
- KPI value, target, threshold, and status exposure;
- stable interfaces insulated from Gold implementation changes.

## Semantic model in this context
The term must be used carefully.

- The **Enterprise Performance Semantic Model** is the authoritative system of business meaning.
- The **SQL semantic layer** is the physical consumption boundary implementing selected semantics through views.
- A **Power BI semantic model** is an analytical implementation on top of those views.

A view is not, by itself, the entire semantic model. It is one implementation artifact.

## Where logic belongs
| Logic | Preferred home |
|---|---|
| Source cleansing and code normalization | Silver |
| Entity conformance and reusable detailed business facts | Silver foundational product |
| Cross-source integration and reusable row-level business calculations | Gold data product |
| Official KPI value, target, threshold, version, and status | Gold KPI Store |
| Stable consumer-facing contract and security filter | Semantic SQL view |
| Dynamic time intelligence, analytical measures, hierarchies, formatting | Power BI semantic model |
| Visual-only labels and interactions | Power BI report |

## Worked example: Gasoline Netback CPG
### Raw

- RightAngle sales transactions
- MPR pricing details
- transportation charges
- OPIS observations
- RIN and ethanol prices
- product and location source tables

### Silver foundational products

- Sales Transaction
- Market Price Observation
- Transportation Cost
- Renewable Compliance Cost
- Product Master
- Location Master
- Customer and Contract

### Gold derived product

**Commercial Margin / Netback**

Calculates and retains diagnostic detail for:

- realized sales price;
- product cost;
- freight;
- RIN and renewable components;
- terminal and blending costs;
- gross margin;
- netback;
- price, cost, freight, and mix variances.

### Gold KPI Store

Persists:

- Gasoline Netback CPG;
- ULSD Netback CPG;
- target;
- thresholds;
- status;
- KPI version;
- source run and lineage.

### Semantic / Consumption layer

- `CONSUMPTION.v_kpi_values`
- Commercial Margin semantic views
- conformed dimensions and security-filtered contracts

### Power BI

- Enterprise KPI semantic model
- Commercial Performance semantic model
- executive scorecard
- diagnostic drill-through report

## Data-product minimum contract
Each data product should define:

- purpose and scope;
- business owner and product owner;
- consumers and use cases;
- business concepts and definitions;
- interface and schema;
- grain and keys;
- refresh and service expectations;
- data-quality rules;
- security and privacy;
- lineage;
- known limitations;
- lifecycle status;
- adoption and value measures.

---
Part of the Enterprise Performance Model Foundation Version 2.