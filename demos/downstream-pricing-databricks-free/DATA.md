# The pricing demo's data

Every table the demo creates, what one row is (its grain), how many rows a run makes, and how its values come about: real (an EIA value as published, or converted only in unit), spot-anchored (a formula of EIA values only, or an EIA value carried from an earlier date) or synthesized (anything with a generated part). The generator is seeded (`SEED` in [`pricing_demo/config.py`](pricing_demo/config.py)), so the same code always makes the same rows; it reads no clock and no network.

The decision owner asked for this document on 2026-10-28: "also create data description document for this synthetic dataset, including the grains and how they were geretaed with links to scripts/notebook used to generate them". The demo has no notebook; every table comes from the scripts linked below.

## The window

Three years of trading days, from 2023-10-21 to 2026-10-20 (`WINDOW_START`, `WINDOW_END` in [`pricing_demo/config.py`](pricing_demo/config.py)): the 748 days on which EIA published the WTI spot price. Every daily table uses these days, so each refinery-day joins that day's crack spread. EIA's weekly series by PADD start on 2020-10-16 (`WEEKLY_START`), so a five-year seasonal average exists for every week in the window. Until 2026-10-28 the window was 2026-04-01 to 2026-10-20 (142 days).

## Where the values come from

| Source | Real or generated | Script |
|---|---|---|
| EIA's daily spot prices (11 series) and U.S. weekly refinery series (4) | Real, cached in `data/public/` with series IDs and the date pulled (`eia_series.csv`) | [`pricing_demo/public_data.py`](pricing_demo/public_data.py), `refresh()` and `load()` |
| EIA's weekly series by PADD (28) | Real, cached in `data/public/eia_weekly.csv`, described in `eia_weekly_series.csv` | [`pricing_demo/public_data.py`](pricing_demo/public_data.py), `refresh()` and `weekly()` |
| MPC's 13 refineries and their crude capacities | Real, from MPC's FY2025 Form 10-K, Item 2 (`data/public/mpc_refineries.csv`) | read in [`pricing_demo/generate.py`](pricing_demo/generate.py), `build()` |
| The scenario's events | Calibration only: the decision owner's briefings in [`SCENARIO.md`](SCENARIO.md) | [`pricing_demo/timeline.py`](pricing_demo/timeline.py), `EVENTS`, `BRIEFING_EVENTS`, `TURNAROUNDS` |
| Price masters and the MIPS hierarchy | The shared assets' identifiers (EPM-DEC-001-0097) | [`pricing_demo/catalog.py`](pricing_demo/catalog.py), `benchmark_masters()`, `crack_masters()`, `crack_groups()` |
| Every source table | As each row says | [`pricing_demo/generate.py`](pricing_demo/generate.py), `build()`; [`pricing_demo/load_postgres.py`](pricing_demo/load_postgres.py) loads them |

## The source databases

Seven Postgres databases, one per source (`SYSTEMS` in [`pricing_demo/config.py`](pricing_demo/config.py)). Six stand for MPC's source systems under public or generic names (README.md, "The source systems"); `eia_weekly` holds EIA's public weekly data, landed as its own source so the replication and the layers treat it like the others. An eighth database, `decision_truth`, holds the hidden decision dossiers and is never replicated (`HIDDEN_SYSTEMS`; its section is below). Each section of [`generate.py`](pricing_demo/generate.py)'s `build()` makes one database's tables; the plan versions, decisions and evidence come from [`decisions.py`](pricing_demo/decisions.py), which reads the tables `build()` has already made.

### `price_reference` (Price Reference Master)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `pricemaster` | one price master (a benchmark or a crack series) | 132 | The shared assets' 5 benchmarks and 127 crack series ([`catalog.py`](pricing_demo/catalog.py)); each row's `DemoProvenance` says whether its series is published or generated |
| `pricedetail` | price master x trading day x forward period | 599,148 | Benchmarks: period 0 is EIA's spot (real, or spot-anchored when carried), period 1 the spot again (spot-anchored: EIA has no futures after 2024-04-05), later periods a backwardated curve (synthesized). Cracks: `crack_value()` from EIA's product and crude prices: spot-anchored where every leg is an EIA price, synthesized where a leg is generated (a residual-fuel leg, the RIN deduction of an ex-RIN crack, the MPC blend); the group's variants and every forward period are synthesized |

### `price_assessment` (Market Price Assessment System)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `mips_currency` | one currency | 1 | USD |
| `mips_unitofmeasure` | one unit | 6 | `UNIT_IDS` in `generate.py` |
| `mips_pricebatch` | one published batch per trading day | 748 | One per day |
| `mips_pricesheet` | one sheet | 7 | The shared sheets |
| `mips_pricegroup` | one group in the sheet hierarchy | 66 | The shared hierarchy |
| `mips_priceassessmentgroup` | one assessed series | 188 | The shared series and their units |
| `mips_priceassessment` | assessed series x trading day x sort order (forward period) | 266,288 | Cash prices real where EIA publishes them, basis spot-anchored, inland differentials, crude differentials, renewables and butane synthesized, forward periods synthesized |

### `reference_data_hub` (Commercial Reference Data Hub)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `priceservice` | one price service | 2 | Fixed |
| `holidaycalendar` | one exchange holiday | 30 | `exchange_holidays()`: the common U.S. exchange holidays by rule, generated reference data, not a copy of NYMEX's schedule |
| `deliveryperiodcategory` | one delivery-period kind | 3 | Fixed |
| `market_event` | one disruption or policy event | 9 | `timeline.EVENTS` (5), `timeline.BRIEFING_EVENTS` (2: the dyed-diesel order and China's export restart) and `timeline.TURNAROUNDS` (2 scenario turnarounds, not MPC's schedule). Each names its source: a `SCENARIO.md` section or the timeline. `EvidenceStatus` reads "not checked", `EvidenceProbability` is empty and `EvidenceCitations` is an empty JSON array until the outside-context step checks each event against public sources |

### `rightangle` (RightAngle, the CTRM system)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `deal` | one trade | 2,673 | Two to five a day, product, route and volume drawn at random; freight per barrel rises with the scenario's freight spike (synthesized) |
| `movement` | one movement per trade | 2,673 | One per deal, loading one to ten days after the trade (synthesized) |
| `freight_rate` | route x trading day | 1,496 | Two product-tanker routes, U.S. Gulf Coast to New York Harbor (Jones Act MR) and to Northwest Europe (MR), in $/bbl: a base rate with seasonality and noise, rising from mid-August 2026 to four times the base by 2026-10-09, after the briefing's "increased more than 300% since mid-August" (`FREIGHT_ROUTES`, `FREIGHT_SPIKE`, `freight_multiplier()`; synthesized). EIA publishes no freight series and the market's assessments are paid (README.md, "Use cases") |

### `aspen_pims` (Aspen PIMS, the refinery planning model)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `plan_target` | refinery x month | 481 | 13 refineries x 37 months (October 2023 to October 2026). Planned utilization is the average of EIA's weekly U.S. utilization in the same month a year earlier (real input), capped at 97%; planned yields are fixed with a seasonal tilt: distillate 35.5% from October to February and 34.0% otherwise, gasoline 47.5% from May to August and 46.5% otherwise (synthesized) |
| `plan_version` | refinery x plan month | 455 | One version per plan target, made on the 15th of the month before the plan month. Its assumptions are the averages of the 20 trading days up to and including that date, never later (17 for the 13 December 2023 versions, whose plan date of 2023-11-15 has only 17 trading days of data behind it; a plan date with fewer than 10 gets no version, which is why October and November 2023 have none): the region's benchmark crack (the price master the refinery operations gold table joins), WTI, NYH ULSD and NYH RBOB, from `pricedetail`; its runs and yields are the plan target's. October and November 2023 have no version, because no price data precedes their plan dates (synthesized; [`pricing_demo/decisions.py`](pricing_demo/decisions.py), `plan_versions()`) |
| `decision_log` | decision | 10 | The public part of each synthetic decision: when, what, the owner roles (slugs from the ontology's `organization/roles.csv`), the refineries (with their `ref-mpc` IRIs), the measures (KPI and OPM identifiers from `kpi` 1.3.0), the option chosen and the outcome expected. No driver, constraint, option list, rationale or actual outcome (synthesized; `decisions.py`, `decisions()` and `build()`) |
| `decision_evidence` | evidence item | 22 | Two or three short items per decision, a meeting note, an approval or a plan change, each written at the decision and showing only part of its rationale, with the author's role (synthesized; `decisions.py`, `decisions()`) |

The decision log and its evidence live in the planning system because backcasting, the practice that compares decisions with outcomes (Regional Backcasting, CM 1.1.5, and Distribution Backcasting, CM 1.1.6, in the ontology's `core`), is the planning function's, and plan changes are its records.

### `production_accounting` (Refinery Production Accounting)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `refinery` | one refinery | 13 | MPC's 13 refineries and their FY2025 crude capacities (real) |
| `refinery_daily` | refinery x trading day | 9,724 | Crude runs from EIA's weekly U.S. utilization with noise, cut by the scenario's hurricane and turnarounds (`HURRICANE_RUN_CUTS`, `TURNAROUNDS`); yields and opex generated (synthesized) |
| `unit_daily` | refinery x process unit x trading day | 76,296 | Up to nine units per refinery (`UNITS` in `generate.py`). The unit kinds are the ones MPC's FY2025 Form 10-K, Item 1, names ("atmospheric and vacuum distillation, fluid catalytic cracking, hydrocracking, catalytic reforming, coking, desulfurization, sulfur recovery"), except sulfur recovery, which the demo does not model, and with desulfurization split by stream into distillate, naphtha and gasoline units, a split the demo makes; which refinery has which unit, and every capacity and load ratio, are generated, because the 10-K gives no per-refinery unit list. Hydrocracking appears only at refineries of 250 mbpcd or more and coking at 140 mbpcd or more. Atmospheric distillation runs exactly the refinery's crude runs; every other unit runs a share of them with noise, never above its capacity (synthesized, its own random stream) |

### `eia_weekly` (EIA's Weekly Petroleum Status Report, by PADD)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `series` | one EIA series | 28 | The registry `EIA_WEEKLY` in [`public_data.py`](pricing_demo/public_data.py), with EIA's description and unit and the date pulled (real) |
| `weekly_value` | series x week ending | 8,792 | EIA's values from 2020-10-16 to 2026-10-20, as published (real) |

The 28 series, by measure; each is cited by its EIA series ID and was pulled on 2026-10-28:

| Measure | PADD 1 | PADD 2 | PADD 3 | PADD 4 | PADD 5 | U.S. |
|---|---|---|---|---|---|---|
| Distillate stocks (thousand barrels) | PET.WDISTP11.W | PET.WDISTP21.W | PET.WDISTP31.W | PET.WDISTP41.W | PET.WDISTP51.W | PET.WDISTUS1.W |
| Total gasoline stocks (thousand barrels) | PET.WGTSTP11.W | PET.WGTSTP21.W | PET.WGTSTP31.W | PET.WGTSTP41.W | PET.WGTSTP51.W | PET.WGTSTUS1.W |
| Refinery utilization (percent of operable capacity) | PET.W_NA_YUP_R10_PER.W | PET.W_NA_YUP_R20_PER.W | PET.W_NA_YUP_R30_PER.W | PET.W_NA_YUP_R40_PER.W | PET.W_NA_YUP_R50_PER.W | PET.WPULEUS3.W |
| Refiner net input of crude oil (thousand barrels per day) | PET.WCRRIP12.W | PET.WCRRIP22.W | PET.WCRRIP32.W | PET.WCRRIP42.W | PET.WCRRIP52.W | PET.WCRRIUS2.W |

Product supplied and exports are weekly for the U.S. only: distillate product supplied PET.WDIUPUS2.W, finished motor gasoline product supplied PET.WGFUPUS2.W, distillate exports PET.WDIEXUS2.W and motor gasoline exports PET.W_EPM0F_EEX_NUS-Z00_MBBLD.W (thousand barrels per day).

### `decision_truth` (hidden: loaded, never replicated)

| Table | Grain | Rows | How it is made |
|---|---|---|---|
| `decision_dossier` | decision | 10 | The whole of each decision, in the dossier shape of the decision owner's enterprise-context-engineering repository (README.md, "Use cases"): decision time, statement, owner roles, affected entities (refinery, role and measure identifiers), drivers, constraints, options, the selected option, approval status, the expected outcome, the actual outcome, the data behind it, the ground-truth rationale, known uncertainties and a synthetic flag. Every actual outcome is computed from the tables above after the decision, never written by hand (synthesized; `decisions.py`, `decisions()` and `build()`) |

This database is the hidden truth the tests check the agents' answers against, so the agents must never see it. It is in `HIDDEN_SYSTEMS`, not `SYSTEMS` ([`pricing_demo/config.py`](pricing_demo/config.py)): `load_postgres` fills it, and the replication, the upload and the SQL never read it, which the tests check. The ten decisions:

| Decision | What | Outcome against expectation |
|---|---|---|
| D01, D02 | Cut crude runs at Garyville and Galveston Bay ahead of Hurricane Isaias | The lowest utilization during the storm, computed from `refinery_daily` |
| D03 | Restart Garyville unit by unit as power returns | The first day back above 90% of pre-storm runs |
| D04, D05 | Hold the Robinson and Anacortes turnarounds on schedule | The throughput lost against the 28 days before, and its margin at the region's crack on each day |
| D06 | Raise distillate yield targets while diesel is scarce | The system distillate yield from 1 to 20 October (the window's end) against 1 to 19 September, before the scarcity began on 20 September |
| D07 | Ship a ULSD cargo to New York Harbor rather than export it | The domestic freight premium over the export route, from `freight_rate` |
| D08 | Defer crude purchases after the G7 emergency-stock release | WTI ten trading days later, from EIA's spot in `pricedetail` |
| D09 | Hold export nominations as China restarts product exports | NYH ULSD eight trading days later |
| D10 | Hold Gulf Coast runs through the weakest 20-day crack before August 2026 | The USGC 3-2-1 crack twenty trading days later |

## The Databricks layers

The replication ([`pricing_demo/replicate.py`](pricing_demo/replicate.py)) copies every source table to Parquet with DuckDB, adding `_change_ts` and `_replicated_at`; [`pricing_demo/databricks.py`](pricing_demo/databricks.py) uploads the files and runs the SQL in [`sql/`](sql/). The replica tables hold exactly the source rows ([`sql/02_replica.sql`](sql/02_replica.sql)).

| Layer | Table or view | Grain | Rows | How it is made |
|---|---|---|---|---|
| Silver, dimensions (`silver_mdm_core`) | `mpr_price_master_dim`, `mips_price_batch_dim`, `mips_price_sheet_dim`, `mips_price_group_dim`, `mips_price_assessment_group_dim`, `refinery_dim` | as their source tables | 132, 748, 7, 66, 188, 13 | Renamed and typed from the replica ([`sql/03_silver.sql`](sql/03_silver.sql)) |
| | `market_event_dim`, `eia_weekly_series_dim` | one event; one EIA series | 9, 28 | Renamed from the replica |
| Silver, facts (`silver_udm_core`) | `mpr_price_detail_fact`, `mips_price_assessment_fact` | as their source tables | 599,148, 266,288 | Renamed and typed |
| | `refinery_production_daily_fact`, `refinery_plan_target_fact`, `ctrm_deal_fact` | refinery-day; refinery-month; deal | 9,724, 481, 2,673 | Renamed and typed; the deal fact joins each deal to its movement |
| | `refinery_unit_daily_fact`, `freight_rate_fact`, `eia_weekly_fact` | unit-day; route-day; series-week | 76,296, 1,496, 8,792 | Renamed and typed; the EIA fact carries each series' measure, area and unit |
| | `refinery_plan_version_fact`, `decision_evidence_fact` | plan version; evidence item | 455, 22 | Renamed and typed |
| Silver, dimensions (`silver_mdm_core`), E2 | `decision_dim` | decision | 10 | The decision log's public columns, renamed |
| Gold (`gold_commercial_core`) | `mpr_mips_crack_spread_price_fact` | crack series x day x forward period | 569,976 | The MPR settle price for the 127 crack series on the three crack sheets, unchanged, 748 days x 6 periods ([`sql/04_gold.sql`](sql/04_gold.sql)) |
| | `mips_mpr_executive_summary_fact` | assessment | 266,288 | Each assessment joined to its group, parent group, sheet, batch and price master |
| | `refinery_operations_daily_fact` | refinery-day | 9,724 | Utilization, yields, plan, the region's benchmark crack and the demo's R&M margin per barrel |
| | `refinery_unit_operations_daily_fact` | unit-day | 76,296 | Each unit's throughput over its capacity: unit utilization. Its grain is finer than the refinery operations view's, so the view does not carry it |
| | `refinery_plan_backcast_fact` | plan version | 455 | Each plan version against its month: the assumed crack, runs, utilization and yields beside the averages of the refinery operations gold table over the month's trading days, with the crack and utilization errors |
| | `decision_evidence_detail_fact` | evidence item | 22 | Each evidence item with its decision's public columns: what the agents may read about a decision |
| Metric views (`semantic_sem_commercial`) | `mpr_mips_crack_spread_price_fact_metrics_vw` | as the crack gold | 569,976 | [`sql/05_metric_views.sql`](sql/05_metric_views.sql) |
| | `mips_mpr_executive_summary_fact_vw` | as the Executive Summary gold | 266,288 | |
| | `mips_mpr_benchmark_prices_fact_vw` | price detail of the five benchmarks, periods 0 to 7 (Brent to 6), of the last 160 days | 4,134 when counted, with Databricks' `CURRENT_DATE()` at 2026-10-29 (UTC) | The window moves with `CURRENT_DATE()`, so the count changes from day to day |
| | `refinery_operations_metrics_vw` | as the refinery operations gold | 9,724 | |
| | `pricing_market_margin_metrics_vw` (E3) | one prompt assessment (`SortColumns` 1): blend x day, the crack sheets left out | 45,628 | The Executive Summary gold joined to each assessment group's unit; 61 blends x 748 days |
| | `refinery_unit_operations_metrics_vw` (E3) | as the unit gold | 76,296 | |
| Definitions views (`ontology_definitions`), E3 | `measure_definitions_vw` | one measure with a KPI or OPM identifier, per release graph | 33 | Read from the ontology's triple table, `workspace.epm_ontology.epm_triples`, which the projection driver writes from the Turtle source of truth ([`sql/06_definitions.sql`](sql/06_definitions.sql)) |
| | `crack_spread_definitions_vw`, `executive_summary_definitions_vw`, `pricing_market_margin_definitions_vw`, `refinery_operations_definitions_vw` | as above, the identified measures one subject area's metric views carry; the pricing and market margin view also keeps OPM-0026, the R&M Margin Indicator, which no metric view computes | 1, 6, 6, 7 | Filters of `measure_definitions_vw` by identifier |
| Technical graph (`tech_graph`), E5 | `tech_graph_nodes` | one node of the technical graph or the decision trail | 134 | Created empty by [`sql/07_tech_graph.sql`](sql/07_tech_graph.sql); filled by `python -m pricing_demo.tech_graph sync` from the pipeline's Neo4j, the graph's source: the node's IRI, class, name and other properties as JSON |
| | `tech_graph_edges` | one relationship | 510 | The same sync: source and target IRIs, the relationship type, and whether the target is an ontology resource |

## Measure identifiers and definitions (E3)

Every metric-view measure's comment starts with the KPI or OPM identifiers it implements, from `kpi` 1.3.0 (`business_architecture/ontology/kpi/measure-identifiers.csv`), or with "No identifier" (row counts, and the sums a ratio is built from). A measure with identifiers carries them in its display name and synonyms too; a measure with none has neither, and each view's comment and its `epm_measure_identifiers` tag list every identifier its measures carry (EPM-DEC-001-0109, decision 2). The fields are Databricks' metric view YAML 1.1 `comment`, `display_name` and `synonyms` ("Metric view YAML syntax reference", updated 2026-10-28) and Unity Catalog tags on views ("Apply tags to Unity Catalog securable objects", updated 2026-10-26).

| Metric view | Identifiers |
|---|---|
| `mpr_mips_crack_spread_price_fact_metrics_vw` | KPI-0001 Crack Spreads Pricing |
| `mips_mpr_executive_summary_fact_vw` | KPI-0001 and OPM-0017 to OPM-0021, by price group: a row's group says which measure it is |
| `mips_mpr_benchmark_prices_fact_vw` | OPM-0019 Crude Market Pricing (the benchmark futures) |
| `pricing_market_margin_metrics_vw` | OPM-0017 Gasoline Market Pricing (Gasoline Cash), OPM-0018 Distillate Market Pricing (Diesel Cash), OPM-0019 Crude Market Pricing (the two crude reporting sheets and Benchmark), OPM-0020 Price Comparison (Basis: each hub's cash price less New York Harbor's), OPM-0021 Additional Market Prices (Renewables and NGL's) |
| `refinery_operations_metrics_vw` | OPM-0002 Crude Utilization (actual and planned), OPM-0004 Distillate Yield, OPM-0005 Gasoline Yield, OPM-0024 R&M Margin per Barrel, OPM-0025 Margin Capture, OPM-0027 Refining Operating Costs per Barrel |
| `refinery_unit_operations_metrics_vw` | OPM-0001 Unit Utilization |

What the demo cannot compute as `kpi` defines it, and what it does instead:

- **OPM-0026 R&M Margin Indicator:** not computed. `kpi` gives its basis as "not published": MPC posts the indicator monthly but not how it is built. No view has the measure; the pricing view's comment says so, and its definition is in `pricing_market_margin_definitions_vw`.
- **OPM-0024 R&M Margin per Barrel and OPM-0025 Margin Capture:** the demo's own formulas. R&M margin is the region's benchmark crack scaled by the clean-product yield, less opex ([`sql/04_gold.sql`](sql/04_gold.sql)); margin capture divides it by the benchmark crack, because the indicator it should divide by is not published.
- **OPM-0001 Unit Utilization:** `kpi` divides by constrained unit capacity; the demo's unit capacity is its generated capacity, with no separate constrained figure.
- **OPM-0020 Price Comparison** is the difference between any two markers; the view computes the basis pair, and another pair is one blend's price less the other's.

Each definitions view has these columns: `Identifier`, `Label`, `Definition`, `Grain`, `Basis`, `Not_To_Be_Confused_With` (the other measures' labels), `Kind` (the measure kind's label), `Release_Graph` and `Measure_Iri`. Each value is the triple's literal, unshortened. `Grain` and `Basis` are empty for OPM-0023 Marketing Performance vs. Plan, which `kpi` gives neither. One row of `refinery_operations_definitions_vw`, from the run below:

| Column | Value |
|---|---|
| `Identifier` | OPM-0001 |
| `Label` | Unit Utilization |
| `Definition` | A process unit's throughput as a share of its constrained capacity, for one refinery. |
| `Grain` | hourly and daily, by unit and refinery |
| `Basis` | unit throughput (bbl/d) / constrained unit capacity (bbl/d), averaged over the period |
| `Not_To_Be_Confused_With` | Crude Utilization |
| `Kind` | Operational metric |
| `Release_Graph` | https://w3id.org/lsc/ontology/modules/kpi/1.3.0 |
| `Measure_Iri` | https://w3id.org/lsc/ontology/modules/kpi/measure/unit-utilization |

## The runs

Rows from `python -m pricing_demo.databricks counts` on 2026-10-28, after the generator, `load_postgres`, `replicate`, `setup`, `upload` and `build` ran on this code. The pipeline ran twice that day with the same counts in all 46 objects: from the local container (`127.0.0.1:55432`), then from the exe.dev VM `databases.exe.xyz` through the SSH tunnel (README.md, "Run it"), after `eia_weekly` was created there for the `demo` role. Every source table's count above is the generator's, which `load_postgres` checks after each load and the replica's manifest records; the build checks each replica table against that manifest.

The decision trail ran later on 2026-10-28, again twice with the same counts, now in 54 objects: the 46 above, three replica tables (`plan_version` 455, `decision_log` 10, `decision_evidence` 22), `refinery_plan_version_fact` 455, `decision_evidence_fact` 22, `decision_dim` 10, `refinery_plan_backcast_fact` 455 and `decision_evidence_detail_fact` 22. The VM run came after `decision_truth` was created there for the `demo` role. `load_postgres` loaded `decision_dossier`'s 10 rows into `decision_truth` in both runs, and no Databricks object holds them. On 2026-10-29 the source databases were loaded again in both places after the review fixes (the dossiers' measures as `kpi` IRIs; D01 and D02 describing the cut as the generator applies it), with the same row counts.

E3 ran on 2026-10-29 from the local container: the generator, `load_postgres`, `replicate`, `setup`, `upload`, `build` and `counts`, on this code. The 54 objects above kept their counts (the benchmark view's 4,134 by Databricks' `CURRENT_DATE()`, 2026-10-29 in UTC), and the seven new objects held the rows the table above gives: 61 objects in all. The build set each metric view's tag, and Unity Catalog's `information_schema.table_tags` listed all six. On 2026-10-20 the pricing view gave NYH CBOB at $2.897/gal with a basis of 0, USGC CBOB at $3.157/gal with a basis of $0.26, NYH ULSD at $5.265/gal and propane at 113.3 cents/gal.

E5, on 2026-10-29, ran `setup` and `sql/07_tech_graph.sql` alone, not the whole pipeline: the two `tech_graph` tables are new, and the 61 objects above were not rebuilt. `tech_graph collect` counted all 63 and read the source databases on the exe.dev VM: `price_assessment` 7 tables and 267,304 rows, `price_reference` 2 and 599,280, `reference_data_hub` 4 and 44, `rightangle` 3 and 6,842, `aspen_pims` 4 and 968, `production_accounting` 3 and 86,033, `eia_weekly` 2 and 8,820, and `decision_truth` 1 and 10. The sync then filled the two tables with 134 and 510 rows. The README's "The technical graph, the decision trail and the AuraDB test" gives the rest of the run.

## The technical graph and the decision trail (E5)

Built by [`pricing_demo/tech_graph.py`](pricing_demo/tech_graph.py) with the SPARQL Anything queries in [`sparql/`](sparql/), and committed as Turtle in [`graph/`](graph/). Everything in them is about the demo's own pipeline and its synthetic decisions; the IRIs under `urn:pricing-demo:` are the demo's, and the links to `https://w3id.org/lsc/ontology/` are the ontology's resources.

| Node class | Count | Read from | Links to the ontology |
|---|---|---|---|
| `ReplicaTable`, `SilverTable`, `GoldTable`, `MetricView`, `DefinitionsView`, `TechGraphTable` | 25, 19, 6, 6, 5, 2 | The CREATE statements in `sql/*.sql` (objects.rq), with rows counted in Databricks and last refresh from its `information_schema.tables` | 24 tables to the `data-product` table they are designed as (links.rq, from `data-product/pricing/tables.csv`); each metric view to the `kpi` measures its `epm_measure_identifiers` tag lists (20 links, joined in `kpi/measure-identifiers.csv`) |
| `SourceDatabase`, `Host` | 8, 1 | Postgres, through `SOURCE_PG_DSN` (runtime.rq) | 4 databases to the `system` module's MIPS, MPR, KittyHawk and RightAngle |
| `PipelineStep` | 17 | The `uv run ... python -m pricing_demo.<module> [<step>]` lines of the README's "Run it" (steps.rq); `wiring.rq` links each to the next and each node to the step that makes or fills it (the two `tech_graph` tables point to `sync`, which fills them; the build creates them empty) | none |
| `QualityCheck` | 7 | The checks `tech_graph collect` runs, with result, detail and time (runtime.rq) | none |
| `GenieAgent`, `Orchestrator`, `TripleTable` | 4, 1, 1 | `genie.AGENTS` and the triple table's name, through the live facts | the 2 original agents to their `data-product` designs |
| `Decision` (`prov:Activity`), `EvidenceItem` (`prov:Entity`) | 10, 22 | `aspen_pims.decision_log` and `decision_evidence` (decisions.rq) | `organization` roles (owners and authors), `ref-mpc` refineries, `kpi` measures |

Edges between nodes: `READS_FROM` (a table or view to what its SQL reads), `COPIES` (a replica table to its source database), `HOSTED_ON`, `PRODUCED_BY`, `NEXT`, `CHECKS`, `BINDS` (an agent to its views), `ROUTES_TO` (the orchestrator to the agents), `RECORDED_IN` (a decision or item to its replica table), and PROV-O's `USED` and `WAS_GENERATED_BY`. Edges to the ontology: `IMPLEMENTS`, `DESIGNED_AS`, `STANDS_FOR`, `WAS_ASSOCIATED_WITH`, `WAS_ATTRIBUTED_TO`, `AFFECTS` and `CONCERNS`. Every edge starts at a `Tech` node, and no ontology node gets the `Tech` label or points at one.
