# market-data: benchmark series

The `market-data` module defines the published series of the `kpi` module's crack-spreads measure: MPC's Gulf Coast, Mid-Continent, West Coast and blended 3-2-1 crack spreads, and the NYMEX 3:2:1. Each series names its region, its legs (the crude marker or product benchmark and its barrels), whether it excludes the cost of RINs, or the series it blends. It answers competency questions 31 (same or different series) and 34 (which concepts a measure quantifies). Market Data governs benchmark identifiers and assessment conventions (EPM-DEC-001-0046). Definitions only, never prices (EPM-DEC-001-0005). EPM-DEC-001-0057 records the design.

| File | What |
|---|---|
| `regions.csv`, `benchmarks.csv`, `series.csv` | MPC's three refining regions; 12 benchmarks (4 crude markers, 8 product benchmarks); 5 series, with their legs |
| `vocabulary.ttl`, `shapes.ttl` | Classes (benchmark series, benchmark, leg), properties, the benchmark-kind code list, and shapes: a series has legs or a blend, never both; a series is of one kpi measure; no price on a series, benchmark, leg or region |
| `build_market_data.py`, `market-data.ttl` | The build. `--verify` fails unless `market-data.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_market_data.py` | Tests: the recipes match MPC's and CME's wording, the blend, the planner's names resolve to MPC's series, and SHACL rejects broken series |

Evidence: `../../reference/downstream-peers/benchmark-series-evidence.md`. The module is not released yet. A release needs the decision owner's approval.
