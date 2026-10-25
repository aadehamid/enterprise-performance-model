# EPM-DEC-001-0097: The pricing measures map to the decision owner's Databricks metric views and Genie agents; they stay market indicators, the crack-spread view is the crack spread's source, and the pricing data products are classified as foundational or derived

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-25, items 1 to 17, except the benchmark view's measure, which is open; delegated under EPM-DEC-001-0028: the benchmark view's value column in item 11; the questions each answer replies to are in `answers-2026-10-25-item-f.md`); open questions listed below |
| Date | 2026-10-25 |
| Questions | Which ontology measures do the pricing metric views and Genie agents serve? Are those measures KPIs? Which view is the crack spread's source? How are the views' layers, lineage and systems recorded? How does `market-data` cover every series the views hold? Which pricing tables and views are data products, and of which kind? What may a Genie agent quote? |
| Source | Claude Code sessions of 2026-10-24 and 2026-10-25; `answers-2026-10-25-item-f.md` |

## Context

The decision owner said they would provide "the replica, silver, and gold tables, metric views, and the genie agents for all pricing Operational metrics/KPI", to close out the data-product side of those measures. On 2026-10-25 they shared files describing three Databricks metric views with their lineage and two Genie agents, then answered three rounds of questions on lineage and data products. Following the rule for customer inputs (EPM-DEC-001-0067), the files stay outside the repository: "The only thing we dont add to the repo is the file that I shaerd with from which you extract those information. but the infor should go in the repo." This record holds what Claude derived from them, in Claude's words. Internal system, table and view names are allowed here by EPM-DEC-001-0040, item 3; the 2026-10-19 amendment of EPM-DEC-001-0050 says they stay readable while the repository is public. Every object named here is in `idp_sbx`, a sandbox catalog (item 7).

The assets:

| Asset | Name | Built from |
|---|---|---|
| Genie agent | Crack Spread Price Analytics (room `01f1a79c27e9120d93e3bc2baa5b11ea`) | a crack-spread metric view (item 1) |
| Metric view (bound) | `idp_sbx.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metrics_vw` | the gold table below, filtered to `Record_Active_Indicator = 'Y'`, no joins |
| Metric view (same result, another pattern) | `idp_sbx.semantic_sem_commercial.mpr_mips_crack_spread_price_fact_metricsfromsilver_vw` | silver, with `KPI_ID`, `Crack_Spread_Sum` and `Effective_End_Datetime` exposed |
| Gold table | `idp_sbx.gold_commercial_core.mpr_mips_crack_spread_price_fact`, built by the job `Job_UDM_Master_Pipeline` | silver: `mpr_price_detail_fact` (the values), `mpr_price_master_dim` (the names), `mips_price_assessment_group_dim`, `mips_price_group_dim` and `mips_price_sheet_dim` (which price masters are crack spreads, and their group); `mips_price_batch_dim` and `mips_price_assessment_fact` are read with no column flowing |
| Genie agent | Executive Summary KPIs Analytics (room `01f1c28220f117e69b6c2e23b778081c`) | the two views below |
| Metric view | `idp_sbx.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw` | the gold table below, a one-to-one projection |
| Gold table | `idp_sbx.gold_commercial_core.mips_mpr_executive_summary_fact` | silver: `mips_price_assessment_fact`, `mips_price_assessment_group_dim`, `mips_price_group_dim`, `mips_price_sheet_dim`, `mips_price_batch_dim`, `mpr_price_master_dim` |
| Metric view (benchmarks) | `idp_sbx.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw` | silver directly, no gold: `mpr_price_detail_fact` joined to `mpr_price_master_dim` on the price master ID |
| Silver tables | `idp_sbx.silver_udm_core.*` (facts) and `idp_sbx.silver_mdm_core.*` (dimensions) | the replica tables |
| Replica tables | `synapse_dev.replica_mips.*`, `replica_mpr.*`, `replica_kittyhawk.*` | the systems MIPS, MPR and KittyHawk |

The Executive Summary agent groups its prices into nine groups: Benchmark, Crack Spread, Gasoline Basis, Gasoline Cash, Distillate Basis, Distillate Cash, Crude, Renewables and NGLs. Its own notes name four of them "Market Margin Potential" measures, under exactly the names `kpi` 1.1.1 uses: Crack Spreads Pricing, Gasoline Market Pricing, Distillate Market Pricing and Crude Market Pricing.

## Decision

### The measures and their sources

1. **The crack spread comes from the crack-spread view, `mpr_mips_crack_spread_price_fact_metrics_vw`.** The decision owner: "Crack view wins. Anyting related to crack spread comes from crack spread specific metric view", and on the two views: "the agent can consume both. But we chose for the agent to consume the one without "silver" in the name. The one with silver is another design pattern that gives the same result." The bound view reads the gold table, which takes each crack's value unchanged from the MPR settle price. The Executive Summary agent's six crack-spread blends, built from MIPS assessment values, are a second presentation of the same series, not a source.
2. **The benchmark view is `mips_mpr_benchmark_prices_fact_vw`,** a metric view of its own: "This is actually another metric view . This one is focused on benchmark prices". It reads silver directly, and its own definition holds the five instruments (572 ICE Brent, 747 NYMEX WTI Cushing, 750 NYMEX Natural Gas, 752 NYMEX Heating Oil, 9471 NYMEX RBOB), a 160-day window and a cap on forward periods. Which measure it serves is open (question 1); until then its coverage and any binding are provisional.
3. **The pricing measures stay market indicators, and the crack spread's KPI ID is kept as an identifier.** The decision owner: "let us keep them as market indicator. Not all of these are KPIs so our intepretation here is correct unless you think otherwise." and "It is okay to leave the KPI_ID even though they may not be KPI . We will need the ID to integrate with other data (e.g governance data in Purview or unity catalog)". The classes stand as EPM-DEC-001-0042 set them and EPM-DEC-001-0050 approved them. Crack Spreads Pricing gets `dcterms:identifier` "KPI-0001" (the agent's identifier), with the gold table's constant `KPI_ID` value "KPI Crack Spread 3-2-1" beside it and a note that this constant labels all 127 series and all 1,090,423 rows of the gold table alike, so it names the measure, not a series. The files give no KPI ID for the other measures.
4. **The mapping of assets to measures.** The decision owner asked for it: "You may need to map to which pricing metric / kpi they map to and let me know." Claude presented the table below on 2026-10-25 as its finding, not as a question, followed by the six numbered questions in the saved answers (block 7). Asked later the same day to approve the mapping as a table (saved answers, blocks 17 and 18), the decision owner: "I agree and align with the mappng." That table put benchmarks with renewables and NGLs under Additional Market Prices; the decision owner asked in the same message whether that row belongs to the benchmark metric view, so the benchmark row is not part of the approval. The benchmark view's row is open (question 1 below):

   | Asset or agent group | Measure in `kpi` 1.1.1 | Evidence |
   |---|---|---|
   | Crack-spread view and agent (127 series) | Crack Spreads Pricing (`crack-spreads`) | the agent's scope; the Executive Summary notes name it; the KPI ID |
   | Executive Summary: Crack Spread group (six blends) | Crack Spreads Pricing (a presentation, item 1) | the same series |
   | Gasoline Basis and Gasoline Cash | Gasoline Market Pricing (`gasoline-prices`) | named in the Executive Summary notes |
   | Distillate Basis and Distillate Cash | Distillate Market Pricing (`distillate-prices`) | named; jet is in the group, as the measure's definition says |
   | Crude (ten differentials) | Crude Market Pricing (`crude-prices`) | named |
   | Renewables and NGLs | Additional Market Prices (`additional-market-prices`) | the measure's name lists both |
   | Benchmark view (five instruments) | open: see question 1 | |
   | none | Price Comparison; R&M Margin Indicator | not served by either agent |

   The identifiers agree where both sides hold them. The six primary regional 3-2-1 series the crack-spread agent names (43870 USGC MEH, 37438 Chicago WTI, 37439 Group/Tulsa WTI, 36855 LA ANS, 37443 PNW ANS, 37471 SLC WTI), the blended cracks (37464, 42023) and the NYMEX crack 39998 are crack-spread series with the same Price Master IDs (`mkt:priceMasterId`) in `market-data` 1.0.0. NYMEX WTI Cushing (747) is there too, as a benchmark (a leg of the WTI cracks), not a series. The other NYMEX cracks the agent names (44934, 44935) are not in `market-data` 1.0.0.
5. **`market-data` covers every series the views hold, by naming the columns that list them.** The decision owner: "Our sereies should cover all of what I just shared. They are more comprehensive", then "can we just add the table columns that will give us this to show that the full series can be obtained ieven if we just list a few in market data". So:
   - the complete set of crack-spread series is the distinct `Price_Master_ID` values in the crack-spread view, each named by `Price_Master_Name` and grouped by `MIPS_Groups_Text` (127 series in 44 groups on 2026-10-25);
   - the complete set for the other groups is the distinct `MIPSDisplayName` values in the Executive Summary view, filtered as the agent's group filters do (by `Price_Group_Name` or `Price_Sheet_Name`);
   - the complete set of benchmarks is the benchmark view's five instruments, under whichever measure question 1 settles;
   - `market-data` keeps its named series and adds the ones the files name, each with its Price Master ID where one is given, as examples linked to their rows.
6. **A Genie agent may quote a value from its bound source.** The decision owner: "Yes . the agent will use the Metric view to get the value", building on "The intention is that the genie agent should be able to add context to the KPI value using the ontology." This amends EPM-DEC-001-0061, items 2 and 3, for this case: an agent may quote a measure's value taken through the metric view the graph binds to that measure, naming the view, and add the ontology's context. Computing a value from the graph, building a crack spread from its legs, and quoting a value from a source the graph does not bind to that measure stay refused.

### The lineage

7. **The names are the sandbox's, marked as sandbox.** The decision owner: "yes mark as sandbox for now". Each table and view records that it is in the `idp_sbx` sandbox catalog.
8. **The layers are recorded, in the decision owner's names,** each linked to the layer it is built from by `prov:wasDerivedFrom`: replica, silver (UDM facts and MDM dimensions), gold, metric view; and the Genie agent, which uses a metric view. Q3 asked whether to record exactly these five layers, in the decision owner's names, linked by derivation (and, as Q3 put it, as data-product distributions, which item 14 replaces); the decision owner: "We record those layesr." The closing summary's row 3 restated it, and the decision owner confirmed the summary: "Yes we are both aligned."
9. **The joins and derivations are recorded as facts.** Q4 proposed table lineage as fact and the joins and derivations as inferred; the decision owner: "record both as facts. I can double check later". The closing summary's row 4 restated it, and the decision owner confirmed the summary. For the crack spread, the gold table's joins were checked against the data on 2026-10-25: all 127 price masters match, and the crack value equals the MPR settle price on every gold row checked since 2026-09-01. For the Executive Summary, the join keys and the derivations of `Price_Master_ID`, `ChangeValue` and `SortColumns` come from column lineage. For the benchmark view, the join and filters come from the view's own definition.
10. **Only the `idp_sbx` silver layer is recorded; the legacy reads are left out.** The decision owner: "Leave legacy out only use the one with udm_core." and "We leave out the legacy". The silver tables' and the crack-spread gold table's reads from the legacy `synapse_dev.mdm_core`, `udm_core` and `commercial_core` tables are not recorded.
11. **Lineage is recorded table to table at every hop, and column to column only for the value columns.** Q7 proposed exactly this, naming the crack price, `assessment_amount`, `Previous_amount` and `ChangeValue`; the decision owner: "I agree." The closing summary's row 7 restated it, and the decision owner confirmed the summary. The value columns are the crack value (gold `Crack_Spread_Price_Amount` from silver `Settle_Price_Amount`), the Executive Summary's `assessment_amount`, `Previous_amount` and `ChangeValue`, and, delegated under EPM-DEC-001-0028 because Q7 predates the benchmark view's lineage and does not name it, the benchmark view's `Settle_Price_Amount`.
12. **The systems each view depends on come from its lineage.** The decision owner: "Lineage is the evidence". The benchmark view depends on MPR and KittyHawk (no MIPS, despite its name); the crack-spread view on MPR (the prices), MIPS (which price masters are crack spreads, from the sheets 'Crack Spreads', 'Crack Spreads - MPC' and 'Crack Spreads - 3rd Party', and their group) and KittyHawk; the Executive Summary view on MIPS, MPR and KittyHawk.

### The data products

13. **All pricing sits under Master Pricing.** The decision owner: "All pricing sits under "Master Pricing" data portfolio". The new pricing data products are recorded as parts (`dcterms:isPartOf`) of the existing `product:master-pricing` (`data-product` 1.1.0, "Master Pricing", active).
14. **Each data product is classified as foundational or derived,** in a new Data Product Kind code list (Q12 proposed the kinds with definitions and the layer mapping, and Q15 the code list with scope notes and the sources in the `authority` module; the closing summary's row 12 restated the kinds, definitions, criteria, the sources at the lowest tier and the layer mapping below, and the decision owner confirmed the summary). The decision owner asked for "the concepts of Foundationa Data Product and Derived Data Produt", researched from good sources, then: "Let us add these definitions that we found in the ontology as well. We can refrence those sources with link. I like the criteria you listed as well." To Q15: "yes". The definitions, in Claude's words:
    - **Foundational data product:** a governed data product that publishes the facts or master data of one business domain, built only from the operational systems of record, with transformations limited to cleansing, validation, conforming and identity resolution, and not modelled for a particular consumer.
    - **Derived data product:** a governed data product built from one or more other data products, adding business logic (aggregation, calculation, measures or a model for a use case) for a known group of consumers.
    - A `skos:scopeNote` lists the criteria that tell them apart: inputs (operational systems, or other data products); logic (cleansing only, or aggregation and measures); consumers (not fitted to one, or fitted to a group of use cases); owner (the source or domain team, or the consuming team); rate of change (stable, or changes more often and can be rebuilt from its sources).
    - The sources, each registered in the `authority` module with its link at tier 5 (generic frameworks): Z. Dehghani, "How to Move Beyond a Monolithic Data Lake to a Distributed Data Mesh", martinfowler.com, 2019; the Data Mesh Architecture site (INNOQ); Databricks, "What is the medallion lakehouse architecture?"; Microsoft Purview, "Create and manage data products"; the Open Data Product Standard 4.0 (Linux Foundation, 2025), whose product type includes raw and derived data; and W3C PROV-O (`prov:wasDerivedFrom`). No MPC, peer or downstream source defines the two kinds, so these are support only, as AGENTS.md's evidence order says of generic frameworks. Q16 proposed this lowest tier; the decision owner: "yes".
    - The layers: silver tables are foundational; gold tables and metric views are derived; replica tables are not data products (they copy a system's own records); Genie agents are not data products but consumers (`prov:SoftwareAgent`) that use (`prov:used`) the metric views.
15. **Each classified data product carries a classification test and a reason, and SHACL shapes check the criteria that can be checked,** as the `kpi` module does for measure kinds: a derived data product is derived from at least one other data product; a foundational one is derived from none and has at least one primary source system. Q15 proposed these; the decision owner: "yes".
16. **Only the new pricing data products are classified now.** The decision owner, to Q17: "Yes we classify the new pricing products now". The portfolio's other data products stay unclassified until a later decision.

Items 13 to 16 are the design of the next `data-product` release; nothing is released by this record.

### Testing

17. **Synthetic data for testing.** The decision owner: "We have the freedom when using synthetic data in Free databrick edition to shape it as we want . as long as it ihas the same shape as the one shared". The views are in another Databricks workspace, so tests in the Free Edition use synthetic tables and views with the same columns and grain.

## Differences between the views and the measures' definitions

Each is a question for the decision owner, not changed here:

1. **Forward periods.** All three views carry forward periods (`Relative_Period_Number`, 0 to 5 in the crack-spread data; `Price_Period_Datetime` with forward monthly averages in the Executive Summary). The five pricing measures' grains in `kpi` 1.1.1 are daily only ("daily, by market hub", "daily, by hub", "daily, by marker").
2. **Crack Spreads Pricing:** the measure's grain is by market hub; the view's series are by Price Master ID, grouped by region. The view's monthly value is the mean of daily settles, which the measure does not state. The agent's trend is a 20-day moving average; the measure compares against a 30-day trend (the Executive Summary agent also uses 30 days).
3. **Gasoline and Distillate Market Pricing:** the measures say "spot prices"; the views hold both cash prices and basis (a differential to the futures contract). The measures' basis is "$/gal as published"; the agent reports cents per gallon, multiplying the stored dollars by 100.
4. **Crude Market Pricing:** the measure covers "Crude oil benchmark prices and differentials, with related futures (natural gas, heating oil, RBOB)". The Executive Summary's Crude group holds differentials only (two of them fuel oil against Brent), and the benchmark futures are in the benchmark view. Three crude instruments (30532, 79068 and 79069) shift their pricing period by two months before monthly averages.
5. **Additional Market Prices:** the renewables group includes credits and RINs, quoted per credit, and soybean oil in cents per pound; the measure's basis says only "as published".

## Open questions

1. **Where the benchmark view belongs.** Crude Market Pricing's definition names crude benchmarks and "related futures (natural gas, heating oil, RBOB)", which are the benchmark view's instruments; Additional Market Prices names "Benchmark" in its label. Recommendation: Crude Market Pricing, because its definition names the instruments, and narrow Additional Market Prices to renewables and NGLs in the next `kpi` release.
2. **The differences above,** each kept, changed in the measure, or noted as the view's own rule.
3. **For the decision owner's team: the crack-spread agent's instructions** name `MEASURE(Crack_Spread_Sum)` for its day-over-day totals, and the bound view has no `Crack_Spread_Sum` (only the other view does). Once the agent reads the bound view, either the view gains the measure or the instructions change.
4. **Who is accountable for Market Data.** Not decided: "we wont make that decision now" (`business-closeout.md`, point 2).
5. **Ownership and stewardship** of the data products: "it will remain parked" (Q17 of the build, EPM-DEC-001-0086).

## What follows

Each of these needs the decision owner's approval of the release; none is given yet.

- **`market-data` 1.1.0,** requiring the current `kpi`: the columns that list each group's series (item 5), the named series the files give with their Price Master IDs, and the link from each series to its measure (`mkt:seriesOf`). Definitions only; the module's shapes reject prices. It also moves `market-data` off `kpi` 1.0.1 (EPM-DEC-001-0077).
- **A `data-product` release:** the Data Product Kind code list (item 14), the pricing data products as parts of Master Pricing with their kind, classification test and reason (items 13 to 16), their tables and views as DCAT distributions with `prov:wasDerivedFrom` from layer to layer (items 8 to 11), the bindings `con:publishesMeasure` from each data product to its measures (EPM-DEC-001-0061, item 1), and SHACL shapes for the kinds (item 15).
- **`system` additions:** MIPS, MPR and Databricks (with the workspace, catalogs and schemas the files give), beside KittyHawk, which the module already holds; each view's dependence on its systems (item 12).
- **`kpi`:** the KPI ID on Crack Spreads Pricing (item 3), and any change the open questions bring.
- **`integration`:** the amended consumer rule (item 6) with its tests, the data-product sources registered at tier 5 (item 14), and any pins that move.

## Known gaps

- **Completeness of series.** Only the named series carry definitions, legs and regions; the rest are known only through the views' columns (item 5).
- **The benchmark view's scaling defect.** The view multiplies all five instruments by 100, which is right for NYMEX Heating Oil (752) and RBOB (9471), converting to cents per gallon, but wrong for ICE Brent (572), NYMEX WTI Cushing (747) and NYMEX Natural Gas (750); the Executive Summary agent divides those three back. Recorded as a known gap for the data product's release note.
- **The benchmark view's 160-day window.** It shows only the last 160 days, so longer trends cannot be answered from it.
- **The KPI ID's lineage.** The crack-spread gold table's `KPI_ID` is a constant with no silver source; it comes only from the legacy table that item 10 leaves out of the record.
- **Validated, not read.** The crack-spread gold table's joins were checked against the data, because the build job's code could not be read; the Executive Summary's joins and derivations come from column lineage only (item 9).
- **Reads with no column flowing.** The crack-spread gold build reads `mips_price_batch_dim` and `mips_price_assessment_fact` without any of their columns reaching gold; their role is not known.
- **The lineage's reach.** It covers the last 180 days of Unity Catalog lineage, and the replica tables are the top of what it records.
- **Freshness.** On 2026-10-25 the newest crack-spread price in gold was from 2026-10-08, and the job last wrote to the table on 2026-10-12.

## Alternatives considered

- **Classify the pricing measures as KPIs.** Not chosen: the decision owner kept them as market indicators (item 3), and none has a target or an accountable owner, which EPM-DEC-001-0042 requires of a KPI.
- **Bind both crack-spread sources.** Not chosen: the decision owner made the crack-spread view the source of anything crack spread (item 1); two bound sources for one measure would leave a consumer to choose.
- **List every series in `market-data`.** Not chosen: the decision owner proposed naming the columns that list them (item 5), so the module does not change each time a series is added.
- **Record the legacy Synapse reads.** Not chosen: the decision owner left them out (item 10).
- **Treat replica tables and Genie agents as data products.** Not chosen: a replica copies a system's own records, which the sources researched keep apart from data products; an agent consumes data products (item 14).

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-f.md`:

- Item F: "Can you add to the plan that I will provide the replica, silver, and gold tables, metric views, and the genie agents for all pricing Operational metrics/KPI. That should close out the data product piesce for that set of metrcis/kpi."
- The assets: "those asset needs to refrelect in the ontology as such. The system should also be refrelected."
- The mapping: "You may need to map to which pricing metric / kpi they map to and let me know. You will need to think carefully to make sure we are not messing things up."
- The first answers: "let us keep them as market indicator."; "It is okay to leave the KPI_ID even though they may not be KPI ."; "Crack view wins."; "Our sereies should cover all of what I just shared."; "We have the freedom when using synthetic data in Free databrick edition to shape it as we want ."
- The columns: "can we just add the table columns that will give us this to show that the full series can be obtained ieven if we just list a few in market data"
- Round 1: "the agent can consume both."; "This is actually another metric view ."; "We record those layesr."; "record both as facts. I can double check later"; "Leave legacy out only use the one with udm_core."; "yes mark as sandbox for now"; "I agree."
- Round 2: "We leave out the legacy"; "Lineage is the evidence"; "I like the criteria you listed as well."
- Round 3: "Yes we classify the new pricing products now"
- The rest: "Yes we are both aligned."; "All pricing sits under "Master Pricing" data portfolio"; "Yes . the agent will use the Metric view to get the value"; "we wont make that decision now"; "it will remain parked"
- This record: "go ahead with the item F decision record."

## Evidence

- `kpi` 1.1.1 (the measures' definitions, grain and basis), `market-data` 1.0.0 (the series and their Price Master IDs), `data-product` 1.1.0 (Master Pricing) and `system` 1.0.0 (KittyHawk), in `business_architecture/ontology/releases/`; the `authority` module's tiers.
- EPM-DEC-001-0028, 0040, 0042, 0050, 0053, 0055, 0059, 0061, 0066, 0067, 0077, 0086.
- The decision owner's files of 2026-10-25 (the pricing assets, the benchmark lineage, the crack-spread gold lineage) and the data-product research note, kept outside the repository.

## Consequences

- EPM-DEC-001-0061 carries a dated note that item 6 amends its items 2 and 3 for an agent that quotes a value through its bound metric view.
- Item F's releases follow this record, each with the decision owner's approval.
- The open questions go to the decision owner, or to their team for question 3, one at a time; each answer is recorded as an amendment to this record.
