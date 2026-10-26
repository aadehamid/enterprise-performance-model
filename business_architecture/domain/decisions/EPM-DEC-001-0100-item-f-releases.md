# EPM-DEC-001-0100: Item F's five releases: kpi 1.2.0, market-data 1.1.0, data-product 1.2.0, system 1.2.0 and integration 2.2.0

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-25, for the release plan; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-25 |
| Questions | How do the decisions of EPM-DEC-001-0097 and the qSKOS dispositions of EPM-DEC-001-0098 ship? |
| Source | Claude Code session of 2026-10-25; `answers-2026-10-25-queue-delegation.md` |

## Context

EPM-DEC-001-0097 records the decision owner's decisions on the pricing measures, their metric views and Genie agents, and lists five releases under "What follows". EPM-DEC-001-0098 gives each qSKOS finding a disposition, and its item 7 routes kpi's, market-data's and data-product's fixes to these releases. On 2026-10-25 Claude put the plan of the five releases to the decision owner, and they chose "Approve the plan (Recommended)".

## Decision

**The decision owner's decision:** release the five as planned.

**What follows (Claude, under EPM-DEC-001-0028):** the build choices, each from the evidence order the amendment of 2026-10-25 (evening) names.

1. **`kpi` 1.2.0.** Crack Spreads Pricing carries `dcterms:identifier` "KPI-0001" and a `skos:note` on the gold table's constant (0097, item 3). Additional Market Prices is now "Additional Market Prices (Renewables, NGLs)": label, definition and classification reason change, and a `skos:changeNote` keeps the planner list's name; the slug stays (0097, item 4). Narrowing a definition while keeping its IRI and kind is a minor change here: no released package used the measure for benchmarks or crude, and the crude and benchmark prices move to Crude Market Pricing, whose definition already named them. R&M Margin Indicator loses its repeated alias, and the build refuses one (0098, item 3).
2. **`market-data` 1.1.0.** A new class, `mkt:MarketPrice`, names the prices the views report for the other measures, linked by `mkt:priceOf`, because `mkt:seriesOf` is the crack series' property and its domain would make each price a crack series. Where a view's price has the same name and market as a benchmark already in the module (LA CARBOB, USGC CBOB, USGC ULSD, and NYMEX WTI 747), that benchmark gains the link instead of a second concept. The benchmark view's other four instruments get labels with their Price Master ID, as MPC Economics' inputs do. `mkt:SeriesEnumeration` records 0097 item 5's columns, with the view's full name as a string, since market-data requires only kpi. Two NYMEX cracks the files name without legs (44934, 44935) join as series with legs unstated.
3. **`data-product` 1.2.0.** The portfolio file, which is process authority, does not change. The pricing tables and views are built from `data-product/pricing/` into `pricing.ttl`, as `dp:PlatformTable`, and the data products among them as `dp:PlatformDataProduct`, not `dp:DataProduct`, whose shapes require a portfolio line and status. 0097's plan named the tables as DCAT distributions; item 14 replaced that with classified data products, so they are platform tables. Replica tables are recorded one by one where the lineage names them, and as no data products (item 14).
4. **The binding of a view to its measures** is `dp:servesMeasure`, stated in data-product. 0097's plan named `con:publishesMeasure`, whose domain is the portfolio's `dp:DataProduct` and which lives in integration, which requires data-product; a binding there would type each view as a portfolio data product. The consumer rule relies on `dp:servesMeasure` instead.
5. **Catalogs and schemas are parts of each table's full name,** not systems. The system module's kinds are the process map's (application, office tool, working document), and a schema is a storage location, not a system. Databricks itself is a system, of kind application.
6. **`system` 1.2.0.** MIPS and Databricks come from `other-systems.csv`, named by the decision owner's pricing assets, not by the process map, so they support no process. MIPS's alternative label "Market Information and Pricing System" is the Executive Summary agent's expansion. MPR gains a definition from the same files, with a note that they expand MPR both as Master Price Record and as Market Price Report. Databricks' definition comes from its documentation, marked as the vendor's, and quoted whole in `reference/vendors/`.
7. **`integration` 2.2.0.** `rule:value-through-bound-view` is a new may-answer rule; `rule:no-values` keeps refusing a computed value and a value from an unbound source, with a change note (0097, item 6). The decision owner's pricing assets are tier 1, as the decision owner's own material; Databricks' documentation is tier 4; the six kind sources are tier 5 (0097, item 14).
8. **Known gaps** go in the changelogs of market-data and data-product, from 0097's list.

## Alternatives considered

- **Hold the releases until production names exist.** Not chosen: the decision owner said to mark the sandbox names (0097, item 7).
- **Put the bindings in integration with `con:publishesMeasure`.** Not chosen, for item 4's reason.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-queue-delegation.md`: "Approve the plan (Recommended)".

## Evidence

- EPM-DEC-001-0097 and the decision owner's pricing assets it cites (held outside the repository).
- EPM-DEC-001-0098, item 7.
- `reference/vendors/README.md`, the Databricks row.

## Consequences

- The packages are in `releases/kpi/1.2.0/`, `releases/market-data/1.1.0/`, `releases/data-product/1.2.0/`, `releases/system/1.2.0/` and `releases/integration/2.2.0/`; released packages do not change.
