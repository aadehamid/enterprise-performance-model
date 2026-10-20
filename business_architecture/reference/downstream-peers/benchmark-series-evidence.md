# Benchmark series: MPC's regional crack spreads and the NYMEX 3:2:1

**Status:** Evidence · **Prepared:** 2026-10-19 · **Used for:** the `market-data` module (EPM-DEC-001-0057), competency questions 31 and 34.

The planner's measure list names three crack spreads: "NYMEX 3-2-1", "USGC 3-2-1 MEH ex-RIN" and "Chicago WTI 3-2-1 ex-RIN" (the `kpi` module's `crack-spreads` measure, classification reason). This file records the primary wording that tells them apart.

## MPC (primary, MPC-S01)

From `../mpc/mpc-performance-measures-evidence.md`, rows 10 and 11, which quote MPC's FY2025 Form 10-K, Item 7:

- "we calculate Gulf Coast, Mid-Continent and West Coast crack spreads that we believe most closely track our operations and slate of products."
- Gulf Coast: "three barrels of MEH crude producing two barrels of USGC CBOB gasoline and one barrel of USGC ULSD".
- Mid-Continent: "three barrels of WTI crude producing two barrels of Chicago CBOB gasoline and one barrel of Chicago ULSD".
- West Coast: "three barrels of ANS crude producing two barrels of LA CARBOB and one barrel of LA CARB Diesel."
- The cracks "do not reflect the market cost of RINs".
- The blended crack spread is weighted by MPC's refining capacity by region in each period.
- MPC does not use LLS or RBOB (row 11).

So "USGC 3-2-1 MEH ex-RIN" is MPC's Gulf Coast crack spread, and "Chicago WTI 3-2-1 ex-RIN" is MPC's Mid-Continent crack spread: same crude, same product markets, same ratio, same RIN treatment.

## CME Group (industry, the exchange that lists the contracts)

| ID | Source | Retrieved |
|---|---|---|
| CME-CRACK | CME Group, "Trading Crack Spreads", 2024, https://www.cmegroup.com/articles/2024/trading-crack-spreads.html | 2026-10-19 |
| CME-CRACK-INTRO | CME Group, "Introduction to Crack Spreads", 2017-05-09, https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads | 2026-10-19 |

- CME-CRACK: "A long 3:2:1 crack spread consists of buying two contracts of RBOB plus one contract of ULSD and selling three contracts of WTI."
- CME-CRACK-INTRO: "3:2:1 crack spreads — three crude oil futures contracts versus two gasoline futures contracts and one ULSD futures contract."
- CME's NYMEX product list names the legs as Light Sweet Crude (CL), RBOB Gasoline (RB) and NY Harbor ULSD (HO).

So "NYMEX 3-2-1" shares the 3-2-1 ratio with MPC's cracks but is a different series: its legs are exchange futures, and its gasoline leg is RBOB, which MPC's benchmarks do not use.
