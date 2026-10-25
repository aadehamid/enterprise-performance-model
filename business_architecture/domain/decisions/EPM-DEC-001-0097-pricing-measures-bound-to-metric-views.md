# EPM-DEC-001-0097: The pricing measures map to the decision owner's Databricks metric views and Genie agents; they stay market indicators, and the crack-spread view is the crack spread's source

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-25, items 1 to 5; the mapping in item 6 delegated under EPM-DEC-001-0028, except the Benchmark group, which is open); open questions listed below |
| Date | 2026-10-25 |
| Questions | Which ontology measures do the pricing metric views and Genie agents serve? Are those measures KPIs? Which view is the source of the crack spread? How does `market-data` cover every series the views hold? |
| Source | Claude Code sessions of 2026-10-24 and 2026-10-25; `answers-2026-10-25-item-f.md` |

## Context

The decision owner said they would provide "the replica, silver, and gold tables, metric views, and the genie agents for all pricing Operational metrics/KPI", to close out the data-product side of those measures. On 2026-10-25 they shared one file describing two Databricks metric views with their lineage and two Genie agents. Following the rule for customer inputs (EPM-DEC-001-0067), the file stays outside the repository: "The only thing we dont add to the repo is the file that I shaerd with from which you extract those information. but the infor should go in the repo." This record holds what Claude derived from it, in Claude's words. Internal system, table and view names are allowed here by EPM-DEC-001-0040, item 3; the 2026-10-19 amendment of EPM-DEC-001-0050 says they stay readable while the repository is public.

What the file describes:

| Asset | Name |
|---|---|
| Genie agent | Crack Spread Price Analytics (room `01f1a79c27e9120d93e3bc2baa5b11ea`); its data source is `idp_sbx.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metricsfromsilver_vw` |
| Metric view (traced lineage) | `idp_sbx.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw`, built from the gold table below |
| Metric view (the agent's) | `..._metricsfromsilver_vw`: the same series with three more columns (`KPI_ID`, `Crack_Spread_Sum`, `Effective_End_Datetime`); the file traces no lineage for it |
| Gold table | `idp_sbx.gold_commercial_core.mpr_mips_crack_spread_price_fact` |
| Genie agent | Executive Summary KPIs Analytics |
| Metric view | `idp_sbx.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw` |
| Metric view (benchmarks) | `idp_sbx.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw` (also spelled `mpr_mips_benchmark_prices_fact_vw` in the same file) |
| Gold table | `idp_sbx.gold_commercial_core.mips_mpr_executive_summary_fact` |
| Silver tables | `silver_udm_core.mips_price_assessment_fact`, `silver_udm_core.mpr_price_detail_fact`; `silver_mdm_core.mips_price_assessment_group_dim`, `mips_price_group_dim`, `mips_price_sheet_dim`, `mips_price_batch_dim`, `mpr_price_master_dim` |
| Replica tables | `synapse_dev.replica_mips.*`, `synapse_dev.replica_mpr.*`, `synapse_dev.replica_kittyhawk.*`; legacy curated reads from `synapse_dev.mdm_core.*`, `udm_core.*` and `commercial_core.*` |
| Source systems | MIPS (price assessments, sheets, groups, batches), MPR (the price master and daily settlements), KittyHawk (price service, holiday calendar, delivery period) |

The Executive Summary agent groups its prices into nine groups: Benchmark, Crack Spread, Gasoline Basis, Gasoline Cash, Distillate Basis, Distillate Cash, Crude, Renewables and NGLs. Its own notes name four of them "Market Margin Potential" measures, under exactly the names `kpi` 1.1.1 uses: Crack Spreads Pricing, Gasoline Market Pricing, Distillate Market Pricing and Crude Market Pricing.

## Decision

1. **The pricing measures stay market indicators.** The decision owner: "let us keep them as market indicator. Not all of these are KPIs so our intepretation here is correct unless you think otherwise." The classes stand as EPM-DEC-001-0042 set them and EPM-DEC-001-0050 approved them: a KPI is a designation with a target and an owner, and these measures describe the market, not a result the company is accountable for. The crack-spread agent itself describes its values as market-marker estimates, not realized margin.
2. **The KPI ID is kept as an external identifier.** The decision owner: "It is okay to leave the KPI_ID even though they may not be KPI . We will need the ID to integrate with other data (e.g governance data in Purview or unity catalog)". The crack-spread view's `KPI_ID` ("KPI Crack Spread 3-2-1"; the agent calls it KPI-0001) becomes a `dcterms:identifier` on Crack Spreads Pricing, with a note naming the system it comes from, so it carries no claim that the measure is a KPI. The file gives no KPI ID for the other measures. The `KPI_ID` column is in the agent's view and in the gold table, where it comes only from a legacy table (see Known gaps); the bound view's definition does not expose it.
3. **Anything crack spread comes from the crack-spread view.** The decision owner: "Crack view wins. Anyting related to crack spread comes from crack spread specific metric view". `mpr_mips_crack_spread_price_fact_metrics_vw`, built from MPR settle prices, is the bound source of Crack Spreads Pricing. The Executive Summary agent's six crack-spread blends, built from MIPS assessment values, are a second presentation of the same series, not a source.
4. **The crack-spread view is the one whose name lacks `metricsfromsilver`.** The decision owner: "Let us use the one without" the word metricsfromsilver. The agent section of the file names `mpr_mips_crack_spread_price_fact_metricsfromsilver_vw`; the lineage section traces `mpr_mips_crack_spread_price_fact_metrics_vw` from the gold table. The second is the one bound. The crack-spread agent, though, queries the first; see open question 7. This item records the decision owner's choice only.
5. **`market-data` covers every series the views hold, by naming the columns that list them.** The decision owner: "Our sereies should cover all of what I just shared. They are more comprehensive", then "can we just add the table columns that will give us this to show that the full series can be obtained ieven if we just list a few in market data". So:
   - the complete set of crack-spread series is the distinct `Price_Master_ID` values in the crack-spread view, each named by `Price_Master_Name` and grouped by `MIPS_Groups_Text`;
   - the complete set for the other groups is the distinct `MIPSDisplayName` values in the Executive Summary view, filtered as the agent's group filters do (by `Price_Group_Name` or `Price_Sheet_Name`);
   - the complete set of benchmarks is the benchmark view's instruments;
   - `market-data` keeps its named series and adds the ones the file names, each with its Price Master ID where the file gives one, as examples linked to their rows.
6. **The mapping of assets to measures** (delegated under EPM-DEC-001-0028; presented to the decision owner on 2026-10-25):

   | Asset or agent group | Measure in `kpi` 1.1.1 | Evidence |
   |---|---|---|
   | Crack-spread view and agent (all series) | Crack Spreads Pricing (`crack-spreads`) | the agent's scope; the Executive Summary notes name it; the view's KPI ID |
   | Executive Summary: Crack Spread group (six blends) | Crack Spreads Pricing (a presentation, item 3) | the same series |
   | Gasoline Basis and Gasoline Cash | Gasoline Market Pricing (`gasoline-prices`) | named in the Executive Summary notes |
   | Distillate Basis and Distillate Cash | Distillate Market Pricing (`distillate-prices`) | named; jet is in the group, as the measure's definition says |
   | Crude (ten differentials) | Crude Market Pricing (`crude-prices`) | named |
   | Renewables and NGLs | Additional Market Prices (`additional-market-prices`) | the measure's name lists both |
   | Benchmark (ICE Brent, NYMEX WTI Cushing, NYMEX Natural Gas, NYMEX Heating Oil, NYMEX RBOB) | open: see question 1 | |
   | none | Price Comparison; R&M Margin Indicator | not served by either agent |

   The identifiers agree where both sides hold them. The six primary regional 3-2-1 series the crack-spread agent names (43870 USGC MEH, 37438 Chicago WTI, 37439 Group/Tulsa WTI, 36855 LA ANS, 37443 PNW ANS, 37471 SLC WTI), the blended cracks (37464, 42023) and the NYMEX crack 39998 are crack-spread series with the same Price Master IDs (`mkt:priceMasterId`) in `market-data` 1.0.0. NYMEX WTI Cushing (747) is there too, as a benchmark (a leg of the WTI cracks), not a series. The other NYMEX cracks the agent names (44934, 44935) are not in `market-data` 1.0.0.
7. **Synthetic data for testing.** The decision owner: "We have the freedom when using synthetic data in Free databrick edition to shape it as we want . as long as it ihas the same shape as the one shared". The views are in another Databricks workspace, so tests in the Free Edition use synthetic tables and views with the same columns and grain.

## Differences between the views and the measures' definitions

Each is a question for the decision owner, not changed here:

1. **Forward periods.** Both views carry forward months (`Relative_Period_Number`, 0 being the prompt month; `Price_Period_Datetime` with forward monthly averages). The five pricing measures' grains in `kpi` 1.1.1 are daily only ("daily, by market hub", "daily, by hub", "daily, by marker").
2. **Crack Spreads Pricing:** the measure's grain is by market hub; the view's series are by Price Master ID, grouped by region. The view's monthly value is the mean of daily settles, which the measure does not state. The agent's trend is a 20-day moving average; the measure compares against a 30-day trend (the Executive Summary agent also uses 30 days).
3. **Gasoline and Distillate Market Pricing:** the measures say "spot prices"; the views hold both cash prices and basis (a differential to the futures contract). The measures' basis is "$/gal as published"; the agent reports cents per gallon, multiplying the stored dollars by 100.
4. **Crude Market Pricing:** the measure covers "Crude oil benchmark prices and differentials, with related futures (natural gas, heating oil, RBOB)". The Executive Summary's Crude group holds differentials only (two of them fuel oil against Brent), and the benchmark futures sit in its Benchmark group. Three crude instruments (30532, 79068 and 79069) shift their pricing period by two months before monthly averages.
5. **Additional Market Prices:** the renewables group includes credits and RINs, quoted per credit, and soybean oil in cents per pound; the measure's basis says only "as published".

## Open questions

1. **Where the Benchmark group belongs.** Crude Market Pricing's definition names crude benchmarks and "related futures (natural gas, heating oil, RBOB)", which is the Benchmark group; Additional Market Prices names "Benchmark" in its label. Recommendation: Crude Market Pricing, because its definition names the instruments, and narrow Additional Market Prices to renewables and NGLs in the next `kpi` release.
2. **The benchmark view's spelling,** `mips_mpr_benchmark_prices_fact_vw` or `mpr_mips_benchmark_prices_fact_vw`.
3. **Which portfolio data product** each gold table belongs to, or whether they are new data products (EPM-DEC-001-0053 holds the portfolio).
4. **Ownership and stewardship** of the views and agents: Q17, parked until the ontology is first shared with business consumers (EPM-DEC-001-0086).
5. **The differences above,** each kept, changed in the measure, or noted as the view's own rule.
6. **The consumer rule for a Genie agent.** The decision owner, 2026-10-24: "We actually have a genie agent today that may be used to give a KPI value ... The intention is that the genie agent should be able to add context to the KPI value using the ontology." EPM-DEC-001-0061 (item 3) refuses "computing or quoting a value". Recommendation: an agent may quote a value that comes from the source the graph binds to that measure (`con:publishesMeasure`), naming the source, and add the ontology's context; computing a value from the graph, building a crack spread from its legs, and quoting from an unbound source stay refused. To be decided by the decision owner and recorded as an amendment to EPM-DEC-001-0061.
7. **The crack-spread agent's view.** The decision owner chose to bind `mpr_mips_crack_spread_price_fact_metrics_vw`, whose lineage is traced from gold (item 4). The Crack Spread Price Analytics agent queries `mpr_mips_crack_spread_price_fact_metricsfromsilver_vw`, which has three more columns and no traced lineage. Either the agent is repointed to the bound view, or the other view's lineage is traced and it is bound instead. Asked of the decision owner on 2026-10-25; not decided here.
8. **Sandbox or production names.** Every object named here is in `idp_sbx`, a sandbox catalog. The ontology would record these names unless the decision owner gives production ones.

## What follows

Each of these needs the decision owner's approval of the release; none is given yet.

- **`market-data` 1.1.0,** requiring the current `kpi`: the columns that list each group's series (item 5), the named series the file gives with their Price Master IDs, and the link from each series to its measure (`mkt:seriesOf`). Definitions only; the module's shapes reject prices. It also moves `market-data` off `kpi` 1.0.1 (EPM-DEC-001-0077).
- **A `data-product` release:** the replica, silver and gold tables and the metric views as DCAT distributions of their data product, with PROV derivation from replica to view, so a walk goes from a measure to the tables behind it; the bindings `con:publishesMeasure` from each data product to its measures (EPM-DEC-001-0061, item 1).
- **`system` additions:** MIPS, MPR and Databricks (with the workspace, catalogs and schemas the file gives), beside KittyHawk, which the module already holds.
- **`kpi`:** the KPI ID as `dcterms:identifier` on Crack Spreads Pricing (item 2), and any change the open questions bring.
- **`integration`,** if its pins move, and for the consumer rule once question 6 is decided.

## Known gaps

- **Completeness of series.** Only the named series carry definitions, legs and regions; the rest are known only through the views' columns (item 5).
- **The benchmark view's scaling defect.** The view stores ICE Brent (572), NYMEX WTI Cushing (747) and NYMEX Natural Gas (750) multiplied by 100, and the Executive Summary agent divides them back. Recorded by default as a known gap for the data product's release note; the decision owner asked what it meant on 2026-10-25 and has not yet decided otherwise.
- **The KPI ID's lineage.** The crack-spread gold table's `KPI_ID` has no silver source; it comes only from the legacy `synapse_dev.commercial_core` table.
- **Inferred joins.** The file's lineage infers the gold tables' join keys and some derived columns (`Price_Master_ID`, `ChangeValue` and `SortColumns` in the Executive Summary; `MIPS_Groups_Text` in the crack spread) from column lineage, not from pipeline code.
- **The benchmark view has no lineage in the file.** Only the crack-spread and Executive Summary views are traced.
- **Legacy reads.** Every silver table also reads a same-named table in the legacy `synapse_dev.mdm_core` or `udm_core` schema, and the crack-spread gold table reads `synapse_dev.commercial_core.mpr_mips_crack_spread_price_fact`; the file says this is likely a history backfill, reason not confirmed.
- **The lineage's reach.** It covers the last 180 days of Unity Catalog lineage, and the `synapse_dev.replica_*` tables are the top of what it records: nothing upstream of them is traced.

## Alternatives considered

- **Classify the pricing measures as KPIs.** Not chosen: the decision owner kept them as market indicators (item 1), and none has a target or an accountable owner, which EPM-DEC-001-0042 requires of a KPI.
- **Bind both views to Crack Spreads Pricing.** Not chosen: the decision owner made the crack-spread view the source of anything crack spread (item 3); two bound sources for one measure would leave a consumer to choose.
- **List every series in `market-data`.** Not chosen: the decision owner proposed naming the columns that list them (item 5), so the module does not change each time a series is added.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-f.md`:

- Item F: "Can you add to the plan that I will provide the replica, silver, and gold tables, metric views, and the genie agents for all pricing Operational metrics/KPI. That should close out the data product piesce for that set of metrcis/kpi."
- The assets: "those asset needs to refrelect in the ontology as such. The system should also be refrelected."
- The mapping: "You may need to map to which pricing metric / kpi they map to and let me know. You will need to think carefully to make sure we are not messing things up."
- The answers: "let us keep them as market indicator."; "It is okay to leave the KPI_ID even though they may not be KPI ."; "Crack view wins."; "Let us use the one without" (the view whose name lacks metricsfromsilver); "Our sereies should cover all of what I just shared."; "We have the freedom when using synthetic data in Free databrick edition to shape it as we want ."
- The columns: "can we just add the table columns that will give us this to show that the full series can be obtained ieven if we just list a few in market data"
- This record: "go ahead with the item F decision record."

## Evidence

- `kpi` 1.1.1 (the measures' definitions, grain and basis) and `market-data` 1.0.0 (the series and their Price Master IDs), in `business_architecture/ontology/releases/`.
- EPM-DEC-001-0028, 0040, 0042, 0050, 0053, 0055, 0061, 0066, 0067, 0077, 0086.
- The decision owner's file of 2026-10-25, kept outside the repository.

## Consequences

- Item F's releases follow this record, each with the decision owner's approval.
- The open questions go to the decision owner one at a time; each answer is recorded as an amendment to this record.
