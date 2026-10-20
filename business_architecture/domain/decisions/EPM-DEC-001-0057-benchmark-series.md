# EPM-DEC-001-0057: Benchmark series: one crack-spreads measure, five series, told apart by region, legs, RIN treatment and blend

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-19 |
| Questions | Competency questions 31 (when two published series are the same Named KPI) and 34 (which domain concepts a measure quantifies), which waited for the Market Data definitions; Phase E of EPM-DEC-001-0052, its Step 11 item (every competency question answerable or parked by decision) |
| Source | Claude Code session, 2026-10-19 |

## Context

The `kpi` module defines one measure, `crack-spreads`, a market indicator (EPM-DEC-001-0042). The planner's measure list names three cracks: "NYMEX 3-2-1", "USGC 3-2-1 MEH ex-RIN" and "Chicago WTI 3-2-1 ex-RIN". MPC's FY2025 Form 10-K, Item 7, defines Gulf Coast, Mid-Continent and West Coast crack spreads, each from a crude marker and two product benchmarks in a 3-2-1 ratio, and a blended crack spread weighted from the three by regional capacity, all without the cost of RINs (`business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 10 and 11). CME Group defines the exchange's 3:2:1 from WTI, RBOB and NY Harbor ULSD futures. EPM-DEC-001-0046 puts benchmark identifiers and assessment conventions in Market Data.

## Decision

**What follows (Claude, under EPM-DEC-001-0028, from the evidence order: MPC first, then an industry source):**
1. **A `market-data` module** for benchmark series, benchmarks and refining regions, separate from `kpi`, because Market Data governs them (EPM-DEC-001-0046) and their identifiers change apart from the measure.
2. **One measure, several series.** Each series is `mkt:seriesOf` the crack-spreads measure. Two series are the same series only when region, legs and RIN treatment are all the same; otherwise they are different series of one measure, not two measures. A blended series is built from other series.
3. **The planner's names resolve.** "USGC 3-2-1 MEH ex-RIN" is an alternative label of MPC's Gulf Coast crack spread, and "Chicago WTI 3-2-1 ex-RIN" of its Mid-Continent crack spread, because MPC's wording gives the same crude, product markets, ratio and RIN treatment. "NYMEX 3-2-1" is a fifth series, defined from CME Group: it shares the ratio but uses exchange futures and RBOB.
4. **Recipes, not prices.** A leg names a benchmark and its barrels; no price is stored (EPM-DEC-001-0005). The blended series' weights change by period, so they are a cited note, not a value.
5. **Regions are MPC's.** Gulf Coast, Mid-Continent and West Coast, with the refineries MPC's Item 2 lists in each. A series or benchmark names its region where the source gives one.
6. **Questions 31 and 34 are answerable.**

## Alternatives considered

- **Each series as its own measure.** Not chosen: the classification put the cracks under one market indicator (EPM-DEC-001-0042), and competency question 30 treats a different view as the same measure.
- **Store current crack values.** Not chosen: values stay in the systems (EPM-DEC-001-0005).

## The decision owner's recorded words

None for these choices. The delegation: "yes, extend the delegation to steps 5 to 12." (`business_architecture/ontology/step4/review-evidence/decision-owner-answers/delegation-steps-5-12.md`). The evidence order follows their instruction: "Use Marathon petroleum comapnies as the stand in company as primary and sue all other downstream oil and gas peer as secondary sources of refrecnes." (`answers-2026-10-19-completion-search.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 10 and 11, and finding 3; `business_architecture/reference/downstream-peers/benchmark-series-evidence.md` (CME Group, "Trading Crack Spreads", 2024; "Introduction to Crack Spreads", 2017; "Fresh from the Trading Room", 2026-07-14); EPM-DEC-001-0005, 0042, 0046. *2026-10-20:* checked against four U.S. refining peers' FY2025 Form 10-Ks (PBF Energy, Phillips 66, HF Sinclair, Valero), recorded in the same evidence file's peers section; they support the rule in item 2 and change no series.

## Consequences

- The regression stands at 23 answerable, 7 partial and 14 waiting.
- The module is built and checked by `scripts/check.sh`; it is released only with the decision owner's approval.
