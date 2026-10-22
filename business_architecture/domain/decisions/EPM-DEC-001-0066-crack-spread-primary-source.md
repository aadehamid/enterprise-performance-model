# EPM-DEC-001-0066: The crack spread's primary source is MPC Economics' definition; the market-data module takes its published series

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-20, for the source order and scope; the modelling delegated under EPM-DEC-001-0028) |
| Date | 2026-10-20 |
| Questions | Competency questions 31 and 34; the sources of the crack-spreads measure's series; corrects EPM-DEC-001-0057 item 3; Phase E of EPM-DEC-001-0052, its Step 11 item (every competency question answerable or parked by decision) |
| Source | Claude Code session, 2026-10-20 |

## Context

EPM-DEC-001-0057 built the `market-data` module from MPC's FY2025 Form 10-K, Item 7, and from CME Group. The U.S. refining peers' FY2025 Form 10-Ks were read afterwards, on 2026-10-20, and recorded in `reference/downstream-peers/benchmark-series-evidence.md`. The same day the decision owner supplied MPC Economics' "3-2-1 Crack Spread KPI Definition", now saved without its governance section and implementation paths in `business_architecture/reference/internal/crack-spread-kpi-definition.md`.

The definition names six primary published regional 3-2-1 series (USGC, Chicago, Group 3 (Tulsa), LA, PNW and SLC), each with its MPR Price Master ID; the NYMEX 3-2-1; and two published results of an MPC-weighted 3-2-1. It defines two treatments of the Renewable Volume Obligation (RVO): Ex-RVO, whose formula deducts the RVO cost, and Inc-RVO, whose formula does not. It says "'Ex-RVO' and 'ex-RIN' mean the same thing".

## Decision

**The decision owner's decision:** "Below is actually the source you should consider primary spurce for Crack Spread," and "follow by MPC publickly available information, follow by Peer, follow by additional high quality references. Capture the nuances and completementary information as nedded". Then: "Dont add the governance portion of the text". Asked how much to keep and whether to change the module, they chose "Definition + series IDs (Recommended)" and "Update the market-data module (Recommended)" (`answers-2026-10-20-crack-spread-source.md`).

**What follows (Claude, under EPM-DEC-001-0028):**
1. **Source order for the crack spread:** MPC Economics' definition first (tier 1, process authority, as the decision owner's measure list is); then MPC's public filings; then U.S. refining peers' SEC filings; then industry sources such as CME Group. A later source adds what an earlier one leaves out; where they differ, the earlier one wins (EPM-DEC-001-0059).
2. **The published series come in.** The six primary regional ex-RIN series (Price Master IDs 43870, 37438, 37439, 36855, 37443 and 37471), the NYMEX 3-2-1 with its ID 39998, and the two MPC-weighted blends (37464 and 42023) are series of the `crack-spreads` measure. Each carries its Price Master ID as `mkt:priceMasterId`. Giving ID 39998 to the CME-sourced NYMEX series reads section 4.3's "NYMEX 3-2-1 industry benchmark" as that exchange series; that reading is this record's.
3. **RIN treatment is told apart, and 0057 item 3 is corrected.** By the definition's formulas, an ex-RIN (Ex-RVO) series deducts the RVO cost; MPC's 10-K cracks "do not reflect the market cost of RINs", as the Inc-RVO formula does not. So the planner's "USGC 3-2-1 MEH ex-RIN" and "Chicago WTI 3-2-1 ex-RIN" are MPC Economics' series 43870 and 37438, not MPC's 10-K Gulf Coast and Mid-Continent cracks: same crude and product markets, opposite RIN treatment, so two series by 0057's item 2. The 10-K cracks stay as MPC's public series. `mkt:excludesRINCost` is false for an ex-RIN series, and its scope note says the labels run opposite to the property's name.
4. **Recipes as the definition gives them.** For USGC, Chicago, Group 3 and LA, the legs are the input prices of section 4.2: three barrels of crude, two of gasoline, one of ULSD, and the RVO cost (ID 13056, a new benchmark kind, compliance cost) on each of the three product barrels. PNW and SLC are marked `mkt:legsUnstated`, because the definition does not list their inputs. Two pairings are this record's reading, not the definition's words: the input table's Gulf Coast row belongs to the USGC series, and the crude inputs 14133, 747 and 4055 are named MEH, WTI and ANS after the series that use them. Each ex-RIN regional series carries the Ex-RVO formula and the averaging rule (daily published values, monthly mean) as a scope note. Prices stay out (EPM-DEC-001-0005).
5. **Market regions are a separate scheme.** USGC, Chicago, Group 3 (Tulsa), LA, PNW and SLC are price markets, kept apart from MPC's three refining regions.
6. **The MPC-weighted blends** weight USGC, Chicago and LA 0.40, 0.40 and 0.20 before 5 May 2024 and 0.42, 0.40 and 0.18 after, as a scope note. MPC's 10-Q gives the same 40/42/18 split for 2025 and 2026. The definition does not say how 37464 and 42023 differ, and the record does not guess.
7. **The NYMEX diesel leg** is CME's NY Harbor ULSD futures contract (ticker HO); the definition calls it NYMEX Heating Oil, kept as a note on the benchmark.
8. **Left out for now:** the NYMEX leg cracks (44934, 44935), the 6-3-2-1 cracks, the regional variants (NYH, El Paso, San Francisco, USWC), and any published Inc-RVO series, which the definition names without IDs or recipes. Each can be added from the same source.

## Alternatives considered

- **Keep MPC's 10-K as the primary source.** Not chosen: the decision owner set the order.
- **Model the 10-K cracks and the Economics series as one series each region.** Not chosen: their RIN treatment differs, and 0057's own rule makes them two series.
- **Leave PNW and SLC out until their inputs are known.** Not chosen: the definition names them as two of the six primary series.

## The decision owner's recorded words

In the Claude Code session on 2026-10-20 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-20-crack-spread-source.md`): "Below is actually the source you should consider primary spurce for Crack Spread,"; "follow by MPC publickly available information, follow by Peer, follow by additional high quality references. Capture the nuances and completementary information as nedded"; "Dont add the governance portion of the text"; and their choices "Definition + series IDs (Recommended)" and "Update the market-data module (Recommended)". The modelling choices above are Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

`business_architecture/reference/internal/crack-spread-kpi-definition.md` (MPC Economics, sections 2 to 4 and the rules of section 5); `business_architecture/reference/mpc/mpc-performance-measures-evidence.md`, rows 10 and 11; MPC Form 10-Q for the quarter ended 2026-03-31, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000042/mpc-20260331.htm, retrieved 2026-10-20 ("Blended 3-2-1 Mid-Continent/USGC/West Coast crack spread is 40/42/18 percent in 2026 and 2025"; row 10 of the MPC evidence cites the same weights from the Q2 2026 Form 10-Q, MPC-S03); `business_architecture/reference/downstream-peers/benchmark-series-evidence.md` (CME Group; the peers' FY2025 Form 10-Ks); EPM-DEC-001-0005, 0057, 0059.

## Consequences

- The `market-data` module has 13 series, 24 benchmarks and 9 regions (3 refining, 6 market). It is built and checked by `scripts/check.sh`; it is released only with the decision owner's approval.
- The source tiers hold 64 sources, 10 in tier 1.
- The regression stands at 34 answerable, 1 partial and 9 waiting; questions 31 and 34 stay answerable. *2026-10-21:* the `party` module made Q19 to Q26 answerable: 42 answerable, 1 partial (Q7), 1 waiting (Q17) (EPM-DEC-001-0071).
