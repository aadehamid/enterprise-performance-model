# Executive Summary KPIs Analytics

Answers questions about the Executive Summary pricing groups: current price, previous price, day-over-day change and forward monthly averages, across benchmark, crack spread, gasoline, distillate, crude, renewable and NGL markets. Pricing only, in USD.

## Sources and their measures
Always use `MEASURE()`, and use only the measures of the view you query:
- Benchmark Prices: `${catalog}.semantic_sem_commercial.mips_mpr_benchmark_prices_fact_vw`. Measures: `Avg_Settle_Price` and `Record_Count`. It has no `assessment_amount`, `Previous_amount` or `ChangeValue`.
- Every other group: `${catalog}.semantic_sem_commercial.mips_mpr_executive_summary_fact_vw`. Measures: `assessment_amount` (current), `Previous_amount`, `ChangeValue` and `Record_Count`. All three value measures are sums.

## The groups
1. Benchmark: ICE Brent, NYMEX WTI (Cushing), NYMEX Natural Gas, NYMEX Heating Oil, NYMEX RBOB.
2. Crack Spread: `Price_Sheet_Name = 'Crack Spreads'` and the six blends NYMEX 3-2-1, Blended Crack Ex Rin Prompt, USGC 3-2-1 MEH Ex RIN Prompt, Chi WTI 3-2-1 Ex RIN Prompt, LA ANS 3-2-1 Ex RIN Prompt, PNW ANS 3-2-1 Ex RIN Prompt. These are a presentation; crack-spread questions belong to the crack-spread view.
3. Gasoline Basis and Gasoline Cash: `Price_Group_Name` 'Basis' or 'Cash', with `Parent_Price_group_name = 'Gasoline'`.
4. Distillate Basis and Distillate Cash: the same, with `Parent_Price_group_name = 'Diesel'` (distillate and diesel mean the same here).
5. Crude: the two crude reporting sheets; values are differentials in $/bbl.
6. Renewables and NGLs: `Price_Group_Name` 'Renewables' or 'NGL''s'.

## Rules
- A blend appears in several groups, and the view sums: always filter `Price_Group_Name` (and the parent group for gasoline or distillate), defaulting to 'Cash', and `SortColumns = 1` for the prompt unless forward months are asked.
- Units as stored: cracks and crude in $/bbl; gasoline and distillate in $/gal (multiply by 100 for cents per gallon); renewables in $/unit (multiply by 100 for cents) except CBOT SBO, already in cents/lb; NGLs already in cents per gallon.
- The benchmark view multiplies all five instruments by 100. That is right for NYMEX HO and RBOB (cents per gallon) and wrong for Brent, WTI and Natural Gas: divide those three by 100 (EPM-DEC-001-0097, known gap). The view shows only the last 160 days.
- For a benchmark's change and previous value, use `MEASURE(Avg_Settle_Price)` at the front month (`Relative_Period_Number = 1`) on the selected date and on the latest earlier date, each corrected for the x100 defect.
- Monthly averages group by the month of `Price_Period_Datetime` and divide the sum by the count: `MEASURE(assessment_amount) / MEASURE(Record_Count)`, with `Price_Group_Name` and `MIPSDisplayName` filtered to one blend. A sum alone is not a price. For Bakken - Patoka, SYN and WCS (Price Master IDs 30532, 79068, 79069), add two months to `Price_Period_Datetime` before grouping.
- On the benchmark view, a monthly average is `MEASURE(Avg_Settle_Price)` grouped by the month of `Contract_Period_Datetime`.
- For a date with no value, current uses that date only; change and previous fall back up to three days.
- Round to two decimals. This is synthetic demo data: every row carries a provenance label in the gold table.
