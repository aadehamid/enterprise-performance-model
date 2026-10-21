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

So "USGC 3-2-1 MEH ex-RIN" is MPC's Gulf Coast crack spread, and "Chicago WTI 3-2-1 ex-RIN" is MPC's Mid-Continent crack spread: same crude, same product markets, same ratio, same RIN treatment. *2026-10-20:* Corrected by EPM-DEC-001-0066: by MPC Economics' definition, the planner's "USGC 3-2-1 MEH ex-RIN" and "Chicago WTI 3-2-1 ex-RIN" are its published series 43870 and 37438, which deduct the RVO cost; MPC's 10-K cracks do not, so they are different series.

## CME Group (industry, the exchange that lists the contracts)

| ID | Source | Retrieved |
|---|---|---|
| CME-CRACK | CME Group, "Trading Crack Spreads", 2024, https://www.cmegroup.com/articles/2024/trading-crack-spreads.html | 2026-10-19 |
| CME-CRACK-INTRO | CME Group, "Introduction to Crack Spreads", 2017, https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads | 2026-10-19 |
| CME-FRESH | CME Group website, "Fresh from the Trading Room: Papering over the cracks", 2026-07-14, produced by ITS for CME Group (the page's footnote), https://www.cmegroup.com/newsletters/fresh-from-the-trading-room/2026-07-14.html | 2026-10-19 |

- CME-CRACK: "A long 3:2:1 crack spread consists of buying two contracts of RBOB plus one contract of ULSD and selling three contracts of WTI."
- CME-CRACK-INTRO: "3:2:1 crack spreads — three crude oil futures contracts versus two gasoline futures contracts and one ULSD futures contract."
- CME-FRESH names the legs and their tickers: "selling two RBOB Gasoline (RB) futures at $2.981 per gallon and one NY Harbor ULSD (HO) futures at $3.5400 per gallon, while buying three WTI Crude Oil (CL) futures". The prices are the article's example, not data the ontology keeps.

So "NYMEX 3-2-1" shares the 3-2-1 ratio with MPC's cracks but is a different series: its legs are exchange futures, and its gasoline leg is RBOB, which MPC's benchmarks do not use.

## U.S. refining peers (secondary)

Added 2026-10-20 to check EPM-DEC-001-0057's rule against peers' own filings, as AGENTS.md's evidence order asks. Each is the FY2025 Form 10-K on sec.gov, read on 2026-10-20.

| ID | Source | Retrieved |
|---|---|---|
| PBF-10K-2025 | PBF Energy Inc., Form 10-K for 2025, filed 2026-02-12, https://www.sec.gov/Archives/edgar/data/1534504/000153450426000010/pbf-20251231.htm | 2026-10-20 |
| PSX-10K-2025 | Phillips 66, Form 10-K for 2025, filed 2026-02-20, https://www.sec.gov/Archives/edgar/data/1534701/000153470126000006/psx-20251231.htm | 2026-10-20 |
| DINO-10K-2025 | HF Sinclair Corporation, Form 10-K for 2025, filed 2026-02-27, https://www.sec.gov/Archives/edgar/data/1915657/000191565726000016/dino-20251231.htm | 2026-10-20 |
| VLO-10K-2025 | Valero Energy Corporation, Form 10-K for 2025, filed 2026-02-25, https://www.sec.gov/Archives/edgar/data/1035002/000162828026011499/vlo-20251231.htm | 2026-10-20 |

- PBF-10K-2025 names its refineries' benchmarks by crude, market and ratio, for example: "The performance of our East Coast refineries generally follows the Dated Brent (NYH) 2-1-1 benchmark refining margin."; "Our Torrance refinery generally follows the ANS (West Coast) 4-3-1 benchmark refining margin."; "Our Toledo refinery generally follows the WTI (Chicago) 4-3-1 benchmark refining margin."; "Our Chalmette refinery generally follows the LLS (Gulf Coast) 2-1-1 benchmark refining margin."; "Our Martinez refinery generally follows the ANS (West Coast) 3-2-1 benchmark refining margin." Its 3-2-1 has different product legs from MPC's: "processing three barrels of crude oil to produce two barrels of gasoline and three-quarters of a barrel jet fuel and one-quarter of a barrel ULSD."
- PSX-10K-2025 reports its own blend: "The composite 3:2:1 market crack spread for our business increased to an average of $20.42 per barrel during 2025". The figure is the filing's, not data the ontology keeps.
- DINO-10K-2025 defines the term only in general: "“Crack spread” is a common measure in the industry and is the difference between market prices for refined products and crude oil." It compares its margin "against publicly available crack spread data".
- VLO-10K-2025 uses neither "crack spread" nor a benchmark refining margin in its text.

This file's reading, not the filings' words: PBF's Martinez "ANS (West Coast) 3-2-1" shares MPC's West Coast crude and ratio but has a jet fuel leg, so by EPM-DEC-001-0057 item 2 it would be a different series from MPC's West Coast crack. Phillips 66 calls its figure a "composite 3:2:1 market crack spread for our business". HF Sinclair compares against public crack data, and Valero's 10-K names no crack benchmark. Nothing in the four filings conflicts with item 2. The peers add no series and change none.
