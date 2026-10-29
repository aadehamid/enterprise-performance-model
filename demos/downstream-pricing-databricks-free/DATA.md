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

Seven Postgres databases, one per source (`SYSTEMS` in [`pricing_demo/config.py`](pricing_demo/config.py)). Six stand for MPC's source systems under public or generic names (README.md, "The source systems"); `eia_weekly` holds EIA's public weekly data, landed as its own source so the replication and the layers treat it like the others. Each section of [`generate.py`](pricing_demo/generate.py)'s `build()` makes one database's tables.

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

## The Databricks layers

The replication ([`pricing_demo/replicate.py`](pricing_demo/replicate.py)) copies every source table to Parquet with DuckDB, adding `_change_ts` and `_replicated_at`; [`pricing_demo/databricks.py`](pricing_demo/databricks.py) uploads the files and runs the SQL in [`sql/`](sql/). The replica tables hold exactly the source rows ([`sql/02_replica.sql`](sql/02_replica.sql)).

| Layer | Table or view | Grain | Rows | How it is made |
|---|---|---|---|---|
| Silver, dimensions (`silver_mdm_core`) | `mpr_price_master_dim`, `mips_price_batch_dim`, `mips_price_sheet_dim`, `mips_price_group_dim`, `mips_price_assessment_group_dim`, `refinery_dim` | as their source tables | 132, 748, 7, 66, 188, 13 | Renamed and typed from the replica ([`sql/03_silver.sql`](sql/03_silver.sql)) |
| | `market_event_dim`, `eia_weekly_series_dim` | one event; one EIA series | 9, 28 | Renamed from the replica |
| Silver, facts (`silver_udm_core`) | `mpr_price_detail_fact`, `mips_price_assessment_fact` | as their source tables | 599,148, 266,288 | Renamed and typed |
| | `refinery_production_daily_fact`, `refinery_plan_target_fact`, `ctrm_deal_fact` | refinery-day; refinery-month; deal | 9,724, 481, 2,673 | Renamed and typed; the deal fact joins each deal to its movement |
| | `refinery_unit_daily_fact`, `freight_rate_fact`, `eia_weekly_fact` | unit-day; route-day; series-week | 76,296, 1,496, 8,792 | Renamed and typed; the EIA fact carries each series' measure, area and unit |
| Gold (`gold_commercial_core`) | `mpr_mips_crack_spread_price_fact` | crack series x day x forward period | 569,976 | The MPR settle price for the 127 crack series on the three crack sheets, unchanged, 748 days x 6 periods ([`sql/04_gold.sql`](sql/04_gold.sql)) |
| | `mips_mpr_executive_summary_fact` | assessment | 266,288 | Each assessment joined to its group, parent group, sheet, batch and price master |
| | `refinery_operations_daily_fact` | refinery-day | 9,724 | Utilization, yields, plan, the region's benchmark crack and the demo's R&M margin per barrel |
| | `refinery_unit_operations_daily_fact` | unit-day | 76,296 | Each unit's throughput over its capacity: unit utilization. Its grain is finer than the refinery operations view's, so the view does not carry it |
| Metric views (`semantic_sem_commercial`) | `mpr_mips_crack_spread_price_fact_metrics_vw` | as the crack gold | 569,976 | [`sql/05_metric_views.sql`](sql/05_metric_views.sql) |
| | `mips_mpr_executive_summary_fact_vw` | as the Executive Summary gold | 266,288 | |
| | `mips_mpr_benchmark_prices_fact_vw` | price detail of the five benchmarks, periods 0 to 7 (Brent to 6), of the last 160 days | 4,134 when counted, with Databricks' `CURRENT_DATE()` at 2026-10-29 (UTC) | The window moves with `CURRENT_DATE()`, so the count changes from day to day |
| | `refinery_operations_metrics_vw` | as the refinery operations gold | 9,724 | |

## The runs

Rows from `python -m pricing_demo.databricks counts` on 2026-10-28, after the generator, `load_postgres`, `replicate`, `setup`, `upload` and `build` ran on this code. The pipeline ran twice that day with the same counts in all 46 objects: from the local container (`127.0.0.1:55432`), then from the exe.dev VM `databases.exe.xyz` through the SSH tunnel (README.md, "Run it"), after `eia_weekly` was created there for the `demo` role. Every source table's count above is the generator's, which `load_postgres` checks after each load and the replica's manifest records; the build checks each replica table against that manifest.
