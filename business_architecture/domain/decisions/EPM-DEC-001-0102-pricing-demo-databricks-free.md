# EPM-DEC-001-0102: The synthetic pricing demo in Databricks Free Edition: real public data first, labelled rows, the shared assets' names

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-25, the scope, the scenario, the sources, the generic system names and the pipeline's layers; the design choices delegated under EPM-DEC-001-0028, amendment of 2026-10-25, evening) |
| Date | 2026-10-25 |
| Questions | Item H: how is the demo built, what is real and what is synthesized, and what enters the ontology? |
| Source | Claude Code session of 2026-10-25; the store-tests handoff's item H decisions, which quote the decision owner |

## Context

The decision owner asked for "a realistic synthetic data to demonstrate this in Databrick Free edition" once the ontology was complete, with the pricing assets' names and columns (EPM-DEC-001-0097, item 17: "We have the freedom when using synthetic data in Free databrick edition to shape it as we want . as long as it ihas the same shape as the one shared"). Their item H decisions, recorded in the handoff: Postgres source systems, DuckDB as needed, a replica, a star schema, gold and metric views; "the new demo does not have to mathc it"; "Let us use real data where they are available in the public"; the briefings as the scenario, with "any mention of ChatGPT" removed; and the generic system names ("they work"). The demo is `demos/downstream-pricing-databricks-free/`.

## Decision

**What follows (Claude, under EPM-DEC-001-0028, amendment of 2026-10-25, evening):**

1. **Free Edition supports the demo.** Its limits page (docs.databricks.com, "Databricks Free Edition limitations", updated 2026-10-18) lists no restriction on metric views or Genie, and restricts outbound internet to trusted domains. The run of 2026-10-25 created the `idp_sbx` catalog, four metric views (YAML 1.1, with joins and filters) and two Genie agents through the Genie API.
2. **Real public data wherever it exists, every row labelled.** EIA daily spot prices and the Weekly Petroleum Status Report, cached with their series IDs and the date pulled; MPC's 13 refineries and capacities from its FY2025 Form 10-K. A row is `real` (an EIA value, or one converted only in unit), `spot-anchored` (a formula of EIA values only, such as a front month or a basis) or `synthesized` (anything with a generated part). Because EIA's NYMEX futures series end on 2024-04-05, a benchmark's front month is its spot price.
3. **Not used: EPA RIN prices and NOAA tracks.** EPA publishes RIN prices only as an interactive dashboard, with no file to cite, so RINs and the RVO are synthesized. Hurricane Isaias comes from the scenario, so its effects are synthesized.
4. **EIA wins over the scenario.** The briefings' weekly balances for 2026-09-25 match EIA; their WTI and Brent futures settlements for 2026-09-30 differ from EIA's spot prices, and the demo uses EIA. The README lists both.
5. **The shared assets' names, columns, joins and filters,** including the benchmark view's defect (all five instruments times 100) and its 160-day window, so the ontology's known gaps can be seen in the demo. Two differences, stated in the README: the crack view has no `Crack_Spread_Sum` (as the bound view lacks it), and the MIPS assessment fact carries its batch.
6. **One Postgres server with one database per source system,** in local Docker; the replication reads `SOURCE_PG_DSN`, so the databases can move to another host. Moving them to an exe.dev VM, which the decision owner raised on 2026-10-25, costs money and stays the decision owner's.
7. **The Genie agents' instructions are written for the demo** from the decision owner's description of the two agents; the decision owner's files stay outside the repository (EPM-DEC-001-0067).
8. **No new measure enters `kpi`.** Under the amendment of 2026-10-25 (evening), a measure from the briefings needs an MPC or U.S. refining peer definition. For the five candidates (inventory coverage, product netback versus target, margin at risk, freight cost per barrel, distillate availability), none is defined in the repository's MPC evidence (`business_architecture/reference/mpc/`) or in Valero's or Phillips 66's FY2025 Form 10-K (searched 2026-10-25). Netback appears only in industry sources (Platts, Haverly; `reference/downstream-peers/kpi-classification-evidence.md`). All five stay candidates.

## Alternatives considered

- **Synthesize every price.** Not chosen: the decision owner asked for real data where it is public.
- **Host the source databases in Databricks Lakebase.** Not chosen: the decision owner asked for Postgres source systems replicated with DuckDB, and Free Edition allows one Lakebase project, which the O2C demo already uses.

## The decision owner's recorded words

Saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-25-item-h.md`: "Wehn we complete the ontology I want us to build a realistic synthetic data to demonstrate this in Databrick Free edition"; "Remove any mention of ChatGPT"; "We should simulate source systes as postgres. Use duckdb as needed."; "the new demo does not have to mathc it"; "Let us use real data where they are available in the public"; and, on the generic system names, "they work". Saved in `answers-2026-10-25-item-f.md`: "We have the freedom when using synthetic data in Free databrick edition to shape it as we want . as long as it ihas the same shape as the one shared".

## Evidence

- `demos/downstream-pricing-databricks-free/README.md`, "The last run (2026-10-25)", the row counts and the agents' answers.
- `demos/downstream-pricing-databricks-free/data/public/eia_series.csv` and `mpc_refineries.csv`.
- https://docs.databricks.com/aws/en/getting-started/free-edition-limitations (updated 2026-10-18).
- https://www.epa.gov/fuels-registration-reporting-and-compliance-help/rin-trades-and-price-information (updated 2026-10-15).
- Valero Energy, Form 10-K for 2025, https://www.sec.gov/Archives/edgar/data/1035002/000162828026011499/vlo-20251231.htm; Phillips 66, Form 10-K for 2025, https://www.sec.gov/Archives/edgar/data/1534701/000153470126000006/psx-20251231.htm.

## Consequences

- The demo's offline tests run in `scripts/check.sh`.
- The five candidate measures are listed for the decision owner, with the sources searched.
