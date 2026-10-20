# market-data: benchmark series

The `market-data` module defines the published series of the `kpi` module's crack-spreads measure. MPC Economics' definition is the primary source (EPM-DEC-001-0066): its six regional ex-RIN 3-2-1 series (USGC, Chicago, Group 3, LA, PNW, SLC), the NYMEX 3-2-1 and two MPC-weighted blends, each with its Price Master ID. MPC's public Gulf Coast, Mid-Continent, West Coast and blended 3-2-1 cracks from the 10-K are series too. Each series names its region, its legs (the crude marker, product benchmark or RVO cost and its barrels), whether it excludes the cost of RINs, the series it blends, or that its source does not list its legs. An ex-RIN series deducts the RVO cost, so its `mkt:excludesRINCost` is false. It answers competency questions 31 (same or different series) and 34 (which concepts a measure quantifies). Market Data governs benchmark identifiers and assessment conventions (EPM-DEC-001-0046). Definitions only, never prices (EPM-DEC-001-0005). EPM-DEC-001-0057 and EPM-DEC-001-0066 record the design.

| File | What |
|---|---|
| `regions.csv`, `benchmarks.csv`, `series.csv` | MPC's three refining regions and MPC Economics' six market regions; 24 benchmarks (7 crude markers, 16 product benchmarks, the RVO cost); 13 series, with their legs |
| `vocabulary.ttl`, `shapes.ttl` | Classes (benchmark series, benchmark, leg), properties, the benchmark-kind code list, and shapes: a series has legs, a blend, or is marked legs unstated, exactly one; a series is of one kpi measure; no price on a series, benchmark, leg or region |
| `build_market_data.py`, `market-data.ttl` | The build. `--verify` fails unless `market-data.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_market_data.py` | Tests: the recipes match MPC Economics', MPC's and CME's wording, the blends, the Price Master IDs, the planner's names resolve to MPC Economics' ex-RIN series, and SHACL rejects broken series |

Evidence: `../../reference/internal/crack-spread-kpi-definition.md` (primary), `../../reference/mpc/mpc-performance-measures-evidence.md` and `../../reference/downstream-peers/benchmark-series-evidence.md`. The module is not released yet. A release needs the decision owner's approval.
