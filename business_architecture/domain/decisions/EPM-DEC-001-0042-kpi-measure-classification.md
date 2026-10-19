# EPM-DEC-001-0042: most planner measures are operational metrics; a KPI is a designation with a target and an owner

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028; Hamid's instructions recorded in EPM-DEC-001-0040) |
| Date | 2026-10-18 |
| Questions | How to classify the measures in Hamid's planner list (EPM-DEC-001-0040, Hamid's decisions 6 and 7); what Crude Value to Breakeven is; whether the Mid-Term Planner's turnaround work is optimization or tracking |
| Source | Claude Code session, 2026-10-18; research in `reference/mpc/mpc-performance-measures-evidence.md` and `reference/downstream-peers/kpi-classification-evidence.md` |

## Context

Hamid said most of his list are operational metrics, not KPIs, and asked for each to be classified from industry practice and MPC's public information, with KPI candidates marked and no target or owner invented (EPM-DEC-001-0040). The classification is in `business_architecture/ontology/kpi/measure-classification.csv`: one row per distinct measure.

## Decision

1. **A KPI is a designation, not a kind of measure.** A measure is a KPI only when the business names it as one of the few measures of a stated objective, with a target and an accountable owner. The same ratio can be a KPI for a region and an operational metric for a unit. Basis: the KPI Institute (KI-03), SCOR "Only the top-level Metrics are referred to as strategic metrics or key performance indicators" (KI-23), Parmenter's team and critical-success-factor tests (KI-01, KI-02), ISO 22400-1's note that KPIs are chosen by criteria (KI-06).
2. **The rule.** Apply the tests in order and stop at the first that assigns a class:
   1. No formula, unit or time grain: **tracker or report** (or **not a measure**, for a capability request).
   2. Emitted only when a condition is met: **alert**.
   3. Value set by an external market or benchmark the region cannot influence: **market indicator**. A value computed from market prices and the planning model to start or rank a decision, with no performance target: **decision-support indicator**.
   4. Actual against a plan, forecast, prior plan version or history, for one period: **plan-variance diagnostic**.
   5. Designated as above, with a target and owner: **KPI**. Otherwise: **operational metric**. Where the evidence makes a measure a strong KPI candidate, the row says `kpi_candidate = yes`.
3. **Result.** 41 measures: 32 from Hamid's list, 8 that MPC publishes and 1 from industry practice. By class: 15 operational metrics, 7 market indicators, 6 plan-variance diagnostics, 6 trackers or reports, 2 alerts, 2 not measures (future capabilities, parked), 2 KPIs and 1 decision-support indicator. Six operational metrics are KPI candidates: Crude Utilization, R&M Margin per Barrel, Margin Capture, Refining Operating Costs per Barrel, Planned Turnaround Costs per Barrel and Lost Margin from Turnarounds.
4. **No row of Hamid's list is a KPI on present evidence.** None has a recorded target or owner. The two KPIs are MPC's own: Relative Refining Margin per Barrel by Region and Relative Adjusted EBITDA per Barrel of Total Throughput, which MPC's annual cash bonus sets with targets (MPC-S16, MPC-S18).
5. **Crude Value to Breakeven is a decision-support indicator.** It is a crude-selection screen: each crude's breakeven value from the LP model against its delivered price, flagging incremental barrels for a full evaluation. Its after-the-fact counterpart is margin capture (VT-01, VT-02, VT-04, VT-09, VT-12; MPC-S07). No public source uses the name "V2Be", so the reading matches the list's description to standard practice.
6. **The Mid-Term Planner's turnaround work is optimization.** At M+4 to M+36 the planner chooses turnaround windows and their sequence, and plans supply and inventory around them; schedule adherence is the turnaround team's tracking (VT-16, VT-17, VT-18; MPC-S01). The TAR Activities Tracker stays a tracker for the Prompt Planner. Planned Turnaround Costs per Barrel (MPC) and Lost Margin from Turnarounds are the turnaround measures the mid-term view affects.
7. **Comparison is part of a variance measure, and only a view of other measures.** "Demand vs. Forecast" is defined by its comparison. "Pipeline Utilization" against the distribution plan, or against five years of history, is the same measure asked against different references, not a second measure (competency question 30). The `compared_against` column records the references each persona uses.
8. **Utilization and per-barrel measures carry their basis.** MPC's crude utilization divides by average calendar-day capacity; the planner list divides by constrained capacity; peers use stream-day or regional bases (`mpc-performance-measures-evidence.md`, §2). A definition names its denominator, and R&M margin per barrel is versioned because MPC added derivative impacts in 2026 (MPC-S17).

## Alternatives considered

- **Call every row on the list a KPI.** Not chosen: Hamid said most are operational metrics, and no row has a target or owner.
- **Parmenter's narrow rule (at most 10 KPIs, none financial, none monthly).** Not chosen as the rule: it would exclude margin capture and all of MPC's bonus metrics. It is cited as support.
- **ISO 22400's wide use of "KPI" for shop-floor ratios.** Not chosen: it would make every utilization ratio a KPI, which does not separate the few from the many.
- **Treat Crude Value to Breakeven as a market indicator.** Not chosen: it depends on each refinery's LP model, not on the market alone.

## Hamid's recorded words

Hamid's instructions are recorded in EPM-DEC-001-0040 and saved in `business_architecture/ontology/step4/review-evidence/hamid-answers/answers-2026-10-18.md`: "Some of these are not actually KPI, majority are operational metrics. Please lassify those as such." and "7. Mark candidate based on industry best practices and publickly available information". On the two open measures he wrote "8 and 9.. can you research this". The rule, the classes and every row's verdict are Claude's, made under EPM-DEC-001-0028 (saved in `delegation-steps-5-12.md`: "yes, extend the delegation to steps 5 to 12."), and Hamid can reverse them.

## Evidence

`business_architecture/reference/mpc/mpc-performance-measures-evidence.md` (MPC first); `business_architecture/reference/downstream-peers/kpi-classification-evidence.md` (industry practice, support only for the generic frameworks; Part B for Crude Value to Breakeven and turnarounds); `business_architecture/ontology/kpi/measure-classification.csv`.

## Consequences

- The `kpi` module defines these 41 measures (definitions only, EPM-DEC-001-0005), with the class, the candidate flag and the personas from the table.
- A measure moves to KPI only by a recorded business decision naming its target and owner.
