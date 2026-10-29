# Downstream pricing demo: synthetic data in Databricks Free Edition

This demo rebuilds the pricing assets the ontology binds its pricing measures to (EPM-DEC-001-0097) in a Databricks Free Edition workspace, from real public data where it exists and synthetic data where it does not. It covers six source systems and EIA's weekly public data in Postgres, DuckDB replication, the replica layer, a silver star schema, gold tables, four metric views and the two Genie agents. Every object the shared `idp_sbx` asset also has keeps its name and columns, except the replica schemas, which follow the source databases' names since 2026-10-28 (see "The source systems"), so the ontology's walk from a measure to its metric view works here. The tables added on 2026-10-28 for the three-year extension (process units, freight, the event table, EIA's weekly data) have no counterpart in the shared asset; their names follow its style. Every price row says whether it is real, spot-anchored or synthesized. The design choices are in EPM-DEC-001-0102.

The scenario is the decision owner's executive briefings for October 2026, in [SCENARIO.md](SCENARIO.md): diesel scarcity, Hurricane Isaias, a freight spike that closes arbitrage, and the G7 stock release. It drives only the synthesized parts.

## The pipeline

```
Postgres, one database per source system (the exe.dev VM through an SSH tunnel; the local Docker container is the fallback)
  -> DuckDB replication: out/replica/<system>/<table>.parquet, with _change_ts and _replicated_at
  -> Unity Catalog volume idp_sbx.replica_landing.raw
  -> replica tables        idp_sbx.replica_<system>.*                         sql/02_replica.sql
  -> silver star schema    idp_sbx.silver_mdm_core.* (dims), silver_udm_core.* (facts)   sql/03_silver.sql
  -> gold                  idp_sbx.gold_commercial_core.*                     sql/04_gold.sql
  -> metric views          idp_sbx.semantic_sem_commercial.*                  sql/05_metric_views.sql
  -> Genie agents          Crack Spread Price Analytics; Executive Summary KPIs Analytics   genie/
```

## Run it

You need Docker, [uv](https://docs.astral.sh/uv/), and a Databricks Free Edition workspace with a personal access token. Copy `.env.example` to `.env` and fill it in; the scripts also read `~/.config/databricks/epm.env`. They never print a secret. To stop, restart, purge or reload the demo's stores together with the ontology's, see `business_architecture/ontology/projection/ontology-stores-runbook.html`.

```bash
cd demos/downstream-pricing-databricks-free
docker compose -f docker/docker-compose.yml up -d          # the seven source databases
# A volume created before 2026-10-28 holds the old database names. Rename them once: the postgres image runs
# docker/init/ only on an empty data directory (hub.docker.com/_/postgres, "Initialization scripts", read 2026-10-28).
#   for p in mips:price_assessment mpr:price_reference kittyhawk:reference_data_hub ctrm:rightangle planning:aspen_pims prodacct:production_accounting; do
#     docker exec pricing-demo-sources psql -U demo -d postgres -c "ALTER DATABASE ${p%%:*} RENAME TO ${p##*:}"; done
uv sync
uv run python -m pricing_demo.load_postgres                # generate and load the source tables
uv run python -m pricing_demo.replicate                    # Postgres -> Parquet with DuckDB
uv run python -m pricing_demo.databricks setup             # catalog idp_sbx (or DEMO_CATALOG), schemas, volume
uv run python -m pricing_demo.databricks upload            # Parquet -> the volume
uv run python -m pricing_demo.databricks build             # replica, silver, gold, metric views
uv run python -m pricing_demo.genie                        # the two Genie agents
uv run python -m pricing_demo.databricks counts            # row counts
uv run python -m pricing_demo.databricks purge             # list what a purge drops; --yes drops it
uv run --with pytest python -m pytest -q tests             # offline tests
```

Postgres listens only on this machine (127.0.0.1:55432), with the throwaway login `demo`. To move the source databases to another host, change `SOURCE_PG_DSN`; nothing else names the host. Since 2026-10-28 the source databases (seven since the three-year extension) also run on an exe.dev VM, `databases.exe.xyz`, where Postgres listens only on the VM's localhost. Open a tunnel and leave it running, `ssh -N -L 127.0.0.1:5433:127.0.0.1:5432 databases.exe.xyz`, then set `SOURCE_PG_DSN=postgresql://demo:<password>@127.0.0.1:5433` in `.env`. The VM's `demo` login has its own generated password, kept only in the local `.env`. The local container stays as the fallback.

Every replication run is a full snapshot: the downstream layers replace their contents from it. The run writes `out/replica/manifest.json` with each table's rows only after every table is there and not empty; `upload` refuses a replica that does not match its manifest, and `build` checks each replica table's rows and its `_replicated_at` against the manifest, so a volume still holding an earlier run's files fails, and that every silver and gold table and metric view exists and holds rows. Each source database loads in one transaction. Databricks Free Edition limits outbound internet to trusted domains, so the replication pushes from the machine that can reach Postgres rather than letting Databricks pull.

## The runs (2026-10-25 to 2026-10-28)

The first window ran from 2026-04-01 to 2026-10-20, 142 trading days; the table and the paragraph after it are its runs. Since 2026-10-28 the window runs three years ("The three-year run" below).

The offline tests check the data, the SQL text and the agents' instructions; they cannot execute a metric view, so the views' behaviour rests on the live runs below. The benchmark view's row count moves with `CURRENT_DATE()`, because the view keeps only the last 160 days: rerunning `counts` on a later date gives a different figure, which is the shared view's design, not a defect.

Free Edition created the `idp_sbx` catalog, so the objects carry their shared names, except the replica schemas, which follow the source databases' names since 2026-10-28. Rows of the first window, from `databricks counts`:

| Layer | Object | Rows |
|---|---|---|
| Replica | `replica_price_reference.pricedetail` / `pricemaster` | 113,742 / 132 |
| | `replica_price_assessment.mips_priceassessment` / `mips_priceassessmentgroup` / `mips_pricegroup` / `mips_pricesheet` / `mips_pricebatch` | 50,552 / 188 / 66 / 7 / 142 |
| | `replica_reference_data_hub.*`, `replica_rightangle.deal` and `movement`, `replica_aspen_pims.plan_target`, `replica_production_accounting.refinery` and `refinery_daily` | 10, 504 each, 91, 13 and 1,846 |
| Silver | `silver_udm_core.mpr_price_detail_fact` / `mips_price_assessment_fact` | 113,742 / 50,552 |
| Gold | `gold_commercial_core.mpr_mips_crack_spread_price_fact` | 108,204 (127 series in 44 groups, 142 days, periods 0 to 5) |
| | `gold_commercial_core.mips_mpr_executive_summary_fact` | 50,552 |
| | `gold_commercial_core.refinery_operations_daily_fact` | 1,846 |
| Metric views | `mpr_mips_crack_spread_price_fact_metrics_vw`, `mips_mpr_executive_summary_fact_vw`, `mips_mpr_benchmark_prices_fact_vw` (160-day window), `refinery_operations_metrics_vw` | 108,204, 50,552, 4,251 (2026-10-25 and 26; 4,173 on 2026-10-28), 1,846 |

Both Genie agents answered from their metric views: the Chicago WTI 3-2-1 crack, ex-RIN, prompt, at $49.84/bbl on the latest date; NYH ULSD cash at $5.27/gal on 2026-10-20, up $0.09, which is EIA's published spot. `SELECT *` on a metric view is refused (`METRIC_VIEW_MISSING_MEASURE_FUNCTION`), as it should be. After the review fixes the pipeline ran again the same day, with the same counts: the Executive Summary agent gave ICE Brent's front month as $115.22/bbl (the benchmark view's value divided by 100) and NYH ULSD's forward monthly averages as $5.27, $5.22, $5.13 and $5.15/gal (sum divided by count). On 2026-10-26 (UTC) it ran again after round 2's fixes, with the same counts (the benchmark view's 4,251 on that date). A build run after a fresh replication but without the upload stopped with "holds rows replicated at … not this run's …", as it should. On 2026-10-28 the pipeline ran from the exe.dev VM through the tunnel, under the new database names: the same counts in every replica, silver and gold table and in three of the four metric views; the benchmark view held 4,173 on that date, because its 160-day window moves with the date.

### The three-year run (2026-10-28)

The window now runs from 2023-10-21 to 2026-10-20: 748 trading days. The pipeline ran twice on 2026-10-28 with the same counts in every replica, silver, gold and metric-view object (46 in all): first from the local container, then from the exe.dev VM through the tunnel, after `eia_weekly` was created there for the `demo` role. [DATA.md](DATA.md) gives every table with its grain, its row count and the script that makes it. The main figures:

| Object | Rows |
|---|---|
| `replica_price_reference.pricedetail`, `silver_udm_core.mpr_price_detail_fact` | 599,148 |
| `replica_price_assessment.mips_priceassessment`, its silver fact, the Executive Summary gold and view | 266,288 |
| `gold_commercial_core.mpr_mips_crack_spread_price_fact` and its view | 569,976 (127 series, 748 days, periods 0 to 5) |
| `refinery_daily`, its silver fact, the refinery operations gold and view | 9,724 (13 refineries, 748 days) |
| `unit_daily`, its silver fact and `refinery_unit_operations_daily_fact` | 76,296 |
| `plan_target` and its silver fact | 481 (13 refineries, 37 months) |
| `freight_rate` and its silver fact | 1,496 (2 routes, 748 days) |
| `market_event` and its silver dimension | 9 |
| `eia_weekly.weekly_value` and its silver fact | 8,792 (28 series from 2020-10-16) |
| `mips_mpr_benchmark_prices_fact_vw` | 4,134 on 2026-10-28 (the last 160 days) |

The Genie agents were not asked again on the three-year data; their instructions and views are unchanged.

## Real, spot-anchored, synthesized

Every row in the price and operations tables carries `DemoProvenance` (in silver and gold, `Demo_Provenance_Label`), a column the shared tables do not have:

- **real:** an EIA value as published on that date, or converted only in unit (propane to cents per gallon). The EIA series are cached in `data/public/` with their series IDs and the date pulled (`eia_series.csv`; EIA's weekly series by PADD in `eia_weekly.csv` and `eia_weekly_series.csv`, listed in [DATA.md](DATA.md)); `python -m pricing_demo.public_data --refresh` pulls them again. MPC's 13 refineries and their capacities come from MPC's FY2025 Form 10-K (`data/public/mpc_refineries.csv`).
- **spot-anchored:** a formula of EIA values only: a benchmark's front month, which is the spot price, because EIA's NYMEX futures table says "Futures prices after April 5, 2024, are not available" ([pet_pri_fut_s1_d](https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm), release of 2026-10-21); a basis, cash minus the front month; the NYMEX 3-2-1 crack. An EIA value carried to a date the series has no observation for (at most seven days back) is spot-anchored too.
- **synthesized:** anything with a generated part: forward months 2 to 7, inland differentials, crude differentials, renewables and RINs, butane, refinery runs and yields, process-unit throughputs and capacities, plan targets, deals, deal freight and the product tanker freight rates.

| Demo price | EIA series |
|---|---|
| NYMEX WTI front month | PET.RWTC.D, WTI Cushing spot |
| ICE Brent front month | PET.RBRTE.D, Europe Brent spot |
| NYMEX Natural Gas front month | NG.RNGWHHD.D, Henry Hub spot |
| NYMEX Heating Oil front month, NYH ULSD cash | PET.EER_EPD2DXL0_PF4_Y35NY_DPG.D |
| NYMEX RBOB front month, NYH CBOB cash | PET.EER_EPMRU_PF4_Y35NY_DPG.D, NY Harbor conventional regular: EIA's spot table lists RBOB only for Los Angeles ([pet_pri_spt_s1_d](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm), release of 2026-10-21) |
| USGC ULSD, USGC CBOB, USGC Jet cash | PET.EER_EPD2DXL0_PF4_RGC_DPG.D, PET.EER_EPMRU_PF4_RGC_DPG.D, PET.EER_EPJK_PF4_RGC_DPG.D |
| LA CARBOB, LA CARB No. 2 cash | PET.EER_EPMRR_PF4_Y05LA_DPG.D, PET.EER_EPD2DC_PF4_Y05LA_DPG.D |
| Propane Mt. Belvieu | PET.EER_EPLLPA_PF4_Y44MB_DPG.D |
| U.S. utilization, crude runs, gasoline and distillate stocks (weekly) | PET.WPULEUS3.W, PET.WCRRIUS2.W, PET.WGTSTUS1.W, PET.WDISTUS1.W |

Not used, and why: EPA publishes RIN prices only as an interactive dashboard, with no file to cite (RIN Trades and Price Information, updated 2026-10-15), so RINs and the RVO are synthesized. Hurricane Isaias comes from the scenario, not from NOAA track data, so its effects are labelled synthesized.

## The scenario against EIA

Where the briefings and EIA differ, EIA wins:

| Briefing figure | EIA | In the demo |
|---|---|---|
| Week ending 2026-09-25: utilization 92.5%, crude runs 16.3 million b/d, gasoline stocks 204.4 million bbl, distillate stocks 105.2 million bbl | 92.5%, 16,257 thousand b/d, 204,362 thousand bbl, 105,180 thousand bbl | The same |
| 2026-09-30: WTI settled $90.42, Brent $103.50 (futures settlements) | WTI Cushing spot $97.18, Brent spot $115.91 | EIA's spot prices, as the front month |
| October 8: Brent settled at $104.28 | Brent spot $130.18 | EIA |
| October 9: Brent settled near $104.72, WTI around $91.85 | Brent spot $130.03, WTI spot $98.73 | EIA |
| October 16: Brent settled at $109.86, WTI closed at $101.41 | Brent spot $119.33, WTI spot $108.21 | EIA |
| October 22: Brent settled at $113.17, WTI at $99.47 | Outside the cache, which ends on 2026-10-20 | Not in the demo |

## Use cases

The questions the demo is built to answer, agreed with the decision owner on 2026-10-28 (their words are in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-28-use-cases.md`). The first two came out of the Databricks-to-ontology design. Numbers 3 to 6 share the second's shape: the supervisor agent answers by combining two or more Genie agents. Numbers 7 to 12 come from the levers in `SCENARIO.md`, the decision owner's October 2026 briefings. Numbers 13 to 17 trace past decisions to their outcomes, on the backcasting processes the process map already holds (Regional Backcasting, CM 1.1.5, and Distribution Backcasting, CM 1.1.6). Number 18 tests the minimal part of the decision owner's enterprise-context-engineering repository the demo takes (below).

Each becomes an acceptance test. It passes when the supervisor calls the agents named (for number 1, when the trace through the technical graph names the right objects), the answer matches a SQL check against the metric views, and the answer uses what the "Where the ontology matters" column names. That column is the point of the demo: it says what an agent would get wrong, or could not find, from the data alone. None is built yet; "Waits for" says what each needs. Every row that names Refinery operations also waits for a Refinery Operations Genie agent over `refinery_operations_metrics_vw`: today the view exists but no agent serves it, and the demo has two Genie agents, Crack Spread Price Analytics and Executive Summary KPIs Analytics. Every row from 2 on also waits for the supervisor.

| # | Question | Agents and sources | Where the ontology matters | Waits for |
|---|---|---|---|---|
| 1 | If the price reference feed is late today, which KPIs, metric views and Genie agents are affected? | The technical graph, from the source database to the metric views | Maps the three pricing metric views to the measures they implement (the refinery operations view is the demo's own and gets its mapping in Part 2), with each measure's KPI or OPM identifier (`kpi` 1.3.0, EPM-DEC-001-0109), the data product it belongs to and the processes and roles that use the measure, so the answer names who to tell, not only which tables are stale | The technical graph |
| 2 | Why did margin capture drop at a refinery last week, and was the crack spread the cause? | Refinery operations and Crack Spread, under the supervisor | `kpi` defines margin capture as reported R&M margin over the R&M Margin Indicator, quarterly and company-wide, and says it is not to be confused with the crack spread. The agent must say the demo's daily refinery figure is the demo's own, and keep the two measures apart | The supervisor |
| 3 | Did the refineries that ran below plan utilization last month also lose margin capture, and how did the crack spread move over the same weeks? | Refinery operations (actual and planned utilization) and Crack Spread | `kpi` defines Crude Utilization monthly by refinery over constrained crude capacity, and says it is not MPC's published figure, which is company-wide over average calendar-day capacity; it keeps the measure apart from Unit Utilization and names the plan it is compared against (the submitted mid-term plan) | The supervisor (three years of history landed 2026-10-28) |
| 4 | Which month had the widest gap between the benchmark 3-2-1 crack and the realized R&M margin per barrel, and what were utilization and yields that month? | Crack Spread and Refinery operations | Classes the crack as a market indicator (KPI-0001, the shared asset's ID) and R&M margin per barrel as an operational metric with an OPM identifier (`kpi` 1.3.0), so the answer reads one as the market's signal and the other as performance | The supervisor (three years of history landed 2026-10-28) |
| 5 | When Brent rose above $110, how did gasoline and distillate market prices and the Gulf Coast crack respond, and did distillate yield shift? | Executive Summary, Pricing and Market Margin, Crack Spread and Refinery operations | `market-data` defines each price the Executive Summary view reports, Brent's differentials and the gasoline and distillate prices among them, with how each is reported (cash, basis, differential, assessment or settlement), so the agent compares like with like and does not mix a differential with an outright price | The pricing metric view and its agent; the supervisor |
| 6 | How does the New York Harbor ULSD forward curve compare with the distillate yield the Gulf Coast refineries ran this quarter? | Executive Summary and Refinery operations | `market-data` defines NYH ULSD as a distillate price the Executive Summary view reports, apart from the NYMEX NY Harbor ULSD futures benchmark (HO); `party`'s product scheme places ULSD under distillates, the group the yield is measured on | The supervisor |
| 7 | Which regions have distillate stocks below their five-year average while our runs fell and the crack widened? | EIA stocks by PADD, Refinery operations and Crack Spread (the briefing's Distillate Availability and Margin-at-Risk alert, October 5) | `ref-mpc` records each of MPC's 13 refineries and its MPC refining region (Gulf Coast, Mid-Continent, West Coast), the key for a stated mapping to EIA's PADDs; the product scheme says which products count as distillate | Its data landed 2026-10-28 (EIA weekly stocks by PADD, from 2020-10-16) |
| 8 | What is the Gulf Coast diesel netback to New York Harbor against export to Europe after freight, and how does it compare with the crack and the realized margin? | Freight, Pricing and Market Margin, Crack Spread and Refinery operations (crack against realized margin, and delivered netbacks, October 9 and 12) | The ontology's `authority` module tiers the documents the modules cite, not data series, so the synthetic label on freight is the demo's own, as every price row already says whether it is real, spot-anchored or synthesized; the ontology's part is the measures being compared, defined in `kpi`, so the agent can say which inputs are public and which are generated | The pricing metric view and its agent (synthetic tanker freight landed 2026-10-28) |
| 9 | Which refineries did Hurricane Isaias hit, how far did runs and margin capture fall, how fast did they recover, and which KPIs moved? | The event table, Refinery operations, Crack Spread and the technical graph (event to impact, October 9) | Links the affected refineries to the processes, roles and measures they feed, so the impact is stated in business terms: which plans, which owners, which measures and their KPI and OPM identifiers | The technical graph (the event table landed 2026-10-28) |
| 10 | How much margin did the autumn turnarounds cost, at the crack during each outage? | The event table, Refinery operations and Crack Spread | `kpi` defines Lost Margin from Turnarounds per turnaround and refinery, and links it to `core`'s Refinery Asset Reliability and Turnaround Coordination capability, so the agent computes the defined measure, not an ad hoc one | Its data landed 2026-10-28 (the event table) |
| 11 | After the dyed-diesel order and China's export restart, how did New York Harbor diesel, its forward curve, the crack and East Coast stocks move? | The event table, Executive Summary, Crack Spread and EIA stocks by PADD (policy as a market driver, October 9 and 16) | The product scheme and its PIDX families tell ULSD from other distillates; `market-data` defines each price series, so the answer follows the products the order covers | Its data landed 2026-10-28 (the event table, EIA weekly stocks by PADD) |
| 12 | With distillate cracks above gasoline cracks, did our refineries shift yield toward distillate, and what did that earn? | Crack Spread and Refinery operations (diesel as the dominant signal, October 16 and 19) | The product scheme groups the products into gasoline and distillates, the groups the cracks and yields are stated in | The supervisor |
| 13 | For last month's plan, what did we assume, what happened, and how much of the margin gap came from the market and how much from our operations? | Plan versions with their assumptions, Refinery operations and Crack Spread | `core` holds the backcasting processes, Regional Backcasting (CM 1.1.5) and Distribution Backcasting (CM 1.1.6), with their steps and planned inputs and outputs, among them "Learnings from Backcast Runs" (an output of the CM 1.1.5.7 steps); `kpi`'s plan-variance diagnostics name the comparisons, so the answer follows the business's own backcast | Plan versions with assumptions, synthetic |
| 14 | Which decisions this year had the largest gap between expected and actual outcome, which role made them, and what did the backcast record as the lesson? | The decision log, the decision trail in the technical graph, and the backcast outcomes | `organization`'s RACI says which role is responsible and accountable for each backcasting step, so "who made it" is a governed role, not a free-text name | The decision log, synthetic; the decision trail |
| 15 | When we cut runs at the Gulf Coast refineries for Hurricane Isaias, did that beat running through at the cracks that actually prevailed? | The decision log, the event table, Refinery operations and Crack Spread | The decision trail uses PROV-O, which the ontology already uses, to link the decision to the plan it changed, the measure it aimed at and the outcome, so the comparison is between defined measures | The decision log; the event table |
| 16 | Did the October shift toward distillate pay off against the plan's yields? | Plan versions, Refinery operations and Crack Spread | The product groups, and the yield measures' "compared against" fields in `kpi` (Distillate Yield: the opening forecast plan, the latest weekly schedule, the short-term LP plan, the distribution plan), define what "against the plan" compares | Plan versions with assumptions |
| 17 | Is our forecasting improving: how has plan-vs-actual error for the crack and utilization moved over three years? | Plan versions and the actuals in every view | For utilization, `kpi`'s "compared against" field names the plan the actual is judged against (the submitted mid-term plan); for the crack, `kpi` names no plan, only its 30-day trend and 5-year history, so the plan's crack assumption comes from the plan versions. A falling error is the continuous-improvement signal backcasting exists for | Plan versions with their assumptions (three years of history landed 2026-10-28) |
| 18 | Why did we cut runs at Galveston Bay during Hurricane Isaias? Label what the records show, what is inferred and what we cannot know. | The decision log's agent-visible evidence, the event table, Refinery operations and Crack Spread | Supplies the identities the answer must use: Galveston Bay as an `ref-mpc` refinery, the deciding role from `organization`, the measures from `kpi`, so each claim cites a governed IRI as well as its evidence | The decision log and its evidence items; the event table |

The data these need beyond the first window (2026-04-01 to 2026-10-20), and what has landed:
- Three years of history, from 2023-10-21 to 2026-10-20 (landed 2026-10-28; [DATA.md](DATA.md) has every table, its grain, its row count and the script that makes it).
- EIA's weekly distillate and gasoline stocks, refinery utilization and crude runs by PADD, with U.S. product supplied and exports, which EIA publishes weekly for the U.S. only (landed 2026-10-28, in the `eia_weekly` source database, from 2020-10-16 so a five-year average exists for every week).
- Tanker freight from the US Gulf Coast to New York Harbor and to Europe, generated and labeled synthetic, shaped to the briefing's freight spike (landed 2026-10-28, `rightangle.freight_rate`). EIA publishes no freight series: its Petroleum & Other Liquids data page (https://www.eia.gov/petroleum/data.php, read 2026-10-28) lists none, and its own tanker-rate articles credit "Data source: Argus Freight", a paid service (for example https://www.eia.gov/todayinenergy/detail.php?id=67064, read 2026-10-28).
- A disruption and policy event table (landed 2026-10-28, `reference_data_hub.market_event`), built from the briefings in `SCENARIO.md`, which hold every event the questions name (the dyed-diesel order and China's export restart among them), with the five events the generator already holds in `pricing_demo/timeline.py` (the export bans, the G7 reserve release, Hurricane Isaias, the freight spike and the turnaround season).
- Plan versions with the crack, prices and yields each assumed, and a decision log of planning and commercial decisions, both synthetic. In the technical graph, each decision links by PROV-O to the plan version it changed, the outcome measured, the variance and the lesson, and to the backcasting process and the measure by IRI. The ontology itself does not change: decisions are data, and the ontology supplies the classes.

From the decision owner's enterprise-context-engineering repository on GitHub (its README and `docs/strategy/synthetic-data-generation-strategy.md`, read 2026-10-28), the demo takes the minimal part that use cases 13 to 18 need, and nothing else:
- **The decision dossier's fields** for the decision log: decision time, statement, owner roles, affected entities, drivers, constraints, options, the selected option, expected and actual outcome, rationale, known uncertainties and a synthetic flag. The owner roles come from `organization` and the affected entities are refinery and measure IRIs.
- **Hidden truth apart from what the agents see.** The full dossiers will sit in a schema only the tests read; the agents will see two or three short evidence items per decision, each showing part of the rationale.
- **Evidence, inference, unknown.** Every agent answer will label each claim as observed, inferred or unknown.
- **Claim-level citations.** Each claim will cite the metric-view query, the evidence item or the ontology IRI behind it.
- **As-of-date context.** A question about a past decision will use the plan and assumptions as of the decision date.

It leaves out that repository's documents, OT and historian data, storage design, separate fictional company, versioned contracts and evaluation rubric.


## The source systems

The demo names each source database after a public product where one exists (RightAngle, Aspen PIMS) and gives the others generic names (the decision owner, 2026-10-28). The real names stay in the ontology. The replica schemas follow the database names (`replica_rightangle`); the silver and gold tables keep the shared asset's names, so its queries run unchanged.

| Database | Demo name | Real system | Before 2026-10-28 |
|---|---|---|---|
| `price_assessment` | Market Price Assessment System | MIPS | `mips` |
| `price_reference` | Price Reference Master | MPR | `mpr` |
| `reference_data_hub` | Commercial Reference Data Hub | KittyHawk | `kittyhawk` |
| `rightangle` | RightAngle, the Commodity Trading and Risk Management (CTRM) system | RightAngle | `ctrm` |
| `aspen_pims` | Aspen PIMS, the refinery planning model | Aspen PIMS | `planning` |
| `production_accounting` | Refinery Production Accounting | Refinery production accounting (no product named) | `prodacct` |

## What matches the shared assets, and what does not

- **Matches:** the schema, table, view and column names, except the replica schemas, which follow the source databases' public or generic names since 2026-10-28: the three pricing replicas are `replica_price_assessment`, `replica_price_reference` and `replica_reference_data_hub`, where the shared asset has `replica_mips`, `replica_mpr` and `replica_kittyhawk`, and the three operations replicas (`replica_rightangle`, `replica_aspen_pims`, `replica_production_accounting`) are the demo's own; the crack gold's joins (the MPR settle price unchanged, the MIPS crack sheets, the level-1 group) and constants (`KPI_ID` 'KPI Crack Spread 3-2-1', `Source_System_Id` '17'); the metric views' fields, measures, joins and filters; the benchmark view's defect, all five instruments times 100, and its 160-day window (EPM-DEC-001-0097, Known gaps).
- **Matches, on purpose:** the three crude series the shared system stores two months early (Bakken - Patoka, SYN and WCS; Price Master IDs 30532, 79068, 79069) carry that two-month lag, so the Executive Summary agent's shift rule holds here too.
- **Spelled as the shared asset spells it:** the MPR price master dimension's `Facitlity_Id`, with the shared silver table's misspelling, so a query that names this column runs here unchanged.
- **Differs:** the price detail's high and low prices are left empty, because the demo generates only the settle. The crack view has no `Crack_Spread_Sum`, as the bound view lacks it, so the recreated crack agent says so instead of summing (EPM-DEC-001-0097, Known gaps). The silver fact for MIPS assessments carries `Price_Batch_Id`, so gold takes the effective date from the batch directly. The demo's refinery operations and their metric view are the demo's own; their formulas are not the ontology's definitions, which live in the `kpi` module.
- **The Genie agents' instructions** are written for this demo from the decision owner's description of the two agents. They are not copies.

## Files

| Path | What |
|---|---|
| `pricing_demo/` | `public_data.py` (EIA cache), `timeline.py` (scenario events), `catalog.py` (price masters, MIPS hierarchy), `generate.py` (every source table, seeded), `load_postgres.py`, `replicate.py` (DuckDB), `databricks.py` (setup, upload, build, counts, purge), `genie.py` |
| `sql/` | The four Databricks layers |
| `genie/` | The two agents' instructions |
| `docker/` | The Postgres server and its seven databases |
| `data/public/` | Real public data, cited |
| `tests/` | Determinism, shapes, labels, the scenario's relabelling |
| `DATA.md` | Every table: its grain, its row count, how it is made and the script that makes it |
