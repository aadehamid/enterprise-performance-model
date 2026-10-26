# Downstream pricing demo: synthetic data in Databricks Free Edition

This demo rebuilds the pricing assets the ontology binds its pricing measures to (EPM-DEC-001-0097) in a Databricks Free Edition workspace, from real public data where it exists and synthetic data where it does not. It covers six source systems in Postgres, DuckDB replication, the replica layer, a silver star schema, gold tables, four metric views and the two Genie agents. Every object has the name and columns the shared `idp_sbx` asset has, so the ontology's walk from a measure to its metric view works here. Every price row says whether it is real, spot-anchored or synthesized. The design choices are in EPM-DEC-001-0102.

The scenario is the decision owner's executive briefings for October 2026, in [SCENARIO.md](SCENARIO.md): diesel scarcity, Hurricane Isaias, a freight spike that closes arbitrage, and the G7 stock release. It drives only the synthesized parts.

## The pipeline

```
Postgres (Docker, one database per source system)
  -> DuckDB replication: out/replica/<system>/<table>.parquet, with _change_ts and _replicated_at
  -> Unity Catalog volume idp_sbx.replica_landing.raw
  -> replica tables        idp_sbx.replica_<system>.*                         sql/02_replica.sql
  -> silver star schema    idp_sbx.silver_mdm_core.* (dims), silver_udm_core.* (facts)   sql/03_silver.sql
  -> gold                  idp_sbx.gold_commercial_core.*                     sql/04_gold.sql
  -> metric views          idp_sbx.semantic_sem_commercial.*                  sql/05_metric_views.sql
  -> Genie agents          Crack Spread Price Analytics; Executive Summary KPIs Analytics   genie/
```

## Run it

You need Docker, [uv](https://docs.astral.sh/uv/), and a Databricks Free Edition workspace with a personal access token. Copy `.env.example` to `.env` and fill it in; the scripts also read `~/.config/databricks/epm.env`. They never print a secret.

```bash
cd demos/downstream-pricing-databricks-free
docker compose -f docker/docker-compose.yml up -d          # the six source databases
uv sync
uv run python -m pricing_demo.load_postgres                # generate and load the source tables
uv run python -m pricing_demo.replicate                    # Postgres -> Parquet with DuckDB
uv run python -m pricing_demo.databricks setup             # catalog idp_sbx (or DEMO_CATALOG), schemas, volume
uv run python -m pricing_demo.databricks upload            # Parquet -> the volume
uv run python -m pricing_demo.databricks build             # replica, silver, gold, metric views
uv run python -m pricing_demo.genie                        # the two Genie agents
uv run python -m pricing_demo.databricks counts            # row counts
uv run --with pytest python -m pytest -q tests             # offline tests
```

Postgres listens only on this machine (127.0.0.1:55432), with the throwaway login `demo`. To move the source databases to another host, such as an exe.dev VM, change `SOURCE_PG_DSN`; nothing else names the host, and a remote host needs its own password and network rules.

Every replication run is a full snapshot: the downstream layers replace their contents from it. The run writes `out/replica/manifest.json` with each table's rows only after every table is there and not empty; `upload` refuses a replica that does not match its manifest, and `build` checks each replica table's rows against the manifest and that every silver and gold table and metric view exists. Each source database loads in one transaction. Databricks Free Edition limits outbound internet to trusted domains, so the replication pushes from the machine that can reach Postgres rather than letting Databricks pull.

## The last run (2026-10-25)

Free Edition created the `idp_sbx` catalog, so the objects carry their shared names. Rows, from `databricks counts`:

| Layer | Object | Rows |
|---|---|---|
| Replica | `replica_mpr.pricedetail` / `pricemaster` | 113,742 / 132 |
| | `replica_mips.mips_priceassessment` / `mips_priceassessmentgroup` / `mips_pricegroup` / `mips_pricesheet` / `mips_pricebatch` | 50,552 / 188 / 66 / 7 / 142 |
| | `replica_kittyhawk.*`, `replica_ctrm.deal` and `movement`, `replica_planning.plan_target`, `replica_prodacct.refinery` and `refinery_daily` | 10, 504 each, 91, 13 and 1,846 |
| Silver | `silver_udm_core.mpr_price_detail_fact` / `mips_price_assessment_fact` | 113,742 / 50,552 |
| Gold | `gold_commercial_core.mpr_mips_crack_spread_price_fact` | 108,204 (127 series in 44 groups, 142 days, periods 0 to 5) |
| | `gold_commercial_core.mips_mpr_executive_summary_fact` | 50,552 |
| | `gold_commercial_core.refinery_operations_daily_fact` | 1,846 |
| Metric views | `mpr_mips_crack_spread_price_fact_metrics_vw`, `mips_mpr_executive_summary_fact_vw`, `mips_mpr_benchmark_prices_fact_vw` (160-day window), `refinery_operations_metrics_vw` | 108,204, 50,552, 4,251, 1,846 |

Both Genie agents answered from their metric views: the Chicago WTI 3-2-1 crack, ex-RIN, prompt, at $49.84/bbl on the latest date; NYH ULSD cash at $5.27/gal on 2026-10-20, up $0.09, which is EIA's published spot. `SELECT *` on a metric view is refused (`METRIC_VIEW_MISSING_MEASURE_FUNCTION`), as it should be. After the review fixes the pipeline ran again the same day, with the same counts: the Executive Summary agent gave ICE Brent's front month as $115.22/bbl (the benchmark view's value divided by 100) and NYH ULSD's forward monthly averages as $5.27, $5.22, $5.13 and $5.15/gal (sum divided by count).

## Real, spot-anchored, synthesized

Every row in the price and operations tables carries `DemoProvenance` (in silver and gold, `Demo_Provenance_Label`), a column the shared tables do not have:

- **real:** an EIA value as published on that date, or converted only in unit (propane to cents per gallon). The EIA series are cached in `data/public/` with their series IDs and the date pulled (`eia_series.csv`); `python -m pricing_demo.public_data --refresh` pulls them again. MPC's 13 refineries and their capacities come from MPC's FY2025 Form 10-K (`data/public/mpc_refineries.csv`).
- **spot-anchored:** a formula of EIA values only: a benchmark's front month, which is the spot price, because EIA's NYMEX futures table says "Futures prices after April 5, 2024, are not available" ([pet_pri_fut_s1_d](https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm), release of 2026-10-21); a basis, cash minus the front month; the NYMEX 3-2-1 crack. An EIA value carried to a date the series has no observation for (at most seven days back) is spot-anchored too.
- **synthesized:** anything with a generated part: forward months 2 to 7, inland differentials, crude differentials, renewables and RINs, butane, refinery runs and yields, plan targets, deals and freight.

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

## The source systems

The demo uses generic names; the real names stay in the ontology (the decision owner: "they work").

| Database | Demo name | Real system |
|---|---|---|
| `mips` | Market Price Assessment System | MIPS |
| `mpr` | Price Reference Master | MPR |
| `kittyhawk` | Commercial Reference Data Hub | KittyHawk |
| `ctrm` | Commodity Trading and Risk Management (CTRM) System | RightAngle |
| `planning` | Refinery Planning Model | Aspen PIMS |
| `prodacct` | Refinery Production Accounting | Refinery production accounting (no product named) |

## What matches the shared assets, and what does not

- **Matches:** the schema, table, view and column names; the crack gold's joins (the MPR settle price unchanged, the MIPS crack sheets, the level-1 group) and constants (`KPI_ID` 'KPI Crack Spread 3-2-1', `Source_System_Id` '17'); the metric views' fields, measures, joins and filters; the benchmark view's defect, all five instruments times 100, and its 160-day window (EPM-DEC-001-0097, Known gaps).
- **Differs:** the price detail's high and low prices are left empty, because the demo generates only the settle. The crack view has no `Crack_Spread_Sum`, as the bound view lacks it, so the recreated crack agent says so instead of summing (EPM-DEC-001-0097, Known gaps). The silver fact for MIPS assessments carries `Price_Batch_Id`, so gold takes the effective date from the batch directly. The demo's refinery operations and their metric view are the demo's own; their formulas are not the ontology's definitions, which live in the `kpi` module.
- **The Genie agents' instructions** are written for this demo from the decision owner's description of the two agents. They are not copies.

## Files

| Path | What |
|---|---|
| `pricing_demo/` | `public_data.py` (EIA cache), `timeline.py` (scenario events), `catalog.py` (price masters, MIPS hierarchy), `generate.py` (every source table, seeded), `load_postgres.py`, `replicate.py` (DuckDB), `databricks.py` (setup, upload, build, counts), `genie.py` |
| `sql/` | The four Databricks layers |
| `genie/` | The two agents' instructions |
| `docker/` | The Postgres server and its six databases |
| `data/public/` | Real public data, cited |
| `tests/` | Determinism, shapes, labels, the scenario's relabelling |
