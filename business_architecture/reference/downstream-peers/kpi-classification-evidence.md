# KPI or operational metric: industry practice, and two open planner measures

**Status:** Draft evidence · **Prepared:** 2026-10-18 · **Used for:** the `kpi` module's measure classification (EPM-DEC-001-0042)

This file ranks below MPC's own material (`../mpc/mpc-performance-measures-evidence.md`) in the evidence order (AGENTS.md). Generic frameworks here (Parmenter, the KPI Institute, Kaplan and Norton, ISO 22400, SCOR, Gartner, APQC) are support only. The refining sources (EIA, Solomon, API, AFPM, Aspen, Haverly) are downstream-specific industry sources. Part A sets the classification rule. Part B answers two questions the decision owner asked to have researched on 2026-10-18: what Crude Value to Breakeven is, and whether the Mid-Term Planner's turnaround work is optimization or tracking. Source IDs: KI- for Part A, VT- for Part B. Sources marked weak or secondary must not carry a claim alone. Where this research and EPM-DEC-001-0042 differ, the decision wins; each such place carries a note.

---

# Part A. KPI, operational metric, market indicator, tracker

Research note, 2026-10-18. Scope: a planner's list of about 55 measures for one refining region.

## Answer in brief

The sources agree on one point. A KPI is a metric that the organisation has picked out. It is tied to a stated objective, it has a target and an accountable owner, and it sits in the small top set that leadership reviews. Everything else that is measured is an ordinary metric. Each ordinary metric is either a performance or diagnostic measure, a plan-versus-actual variance, an external market observation, an activity or status report, or an event alert.

The sources disagree on how narrow "KPI" is. Parmenter allows at most 10 per organisation, all non-financial, measured daily or weekly. ISO 22400-2 calls 34 shop-floor ratios, such as utilization efficiency, "KPIs". SCOR and Gartner put the KPIs at the top of a metric hierarchy and call the lower levels diagnostics.

**Inference for the ontology:** treat "KPI" as a designation that the business gives to a metric, not as a kind of metric. The same utilization ratio can be a KPI for the region and an operational metric for one unit. Snowflake's guide says this directly: "The distinction lies in what happens around the number" [KI-09]. The KPI Institute says the same: metrics "become Key Performance Indicators" "when [they] reflect the achievement of a desired state" [KI-03].

In this note, a line marked **Quote** is the source's own words. A line marked **Inference** is the researcher's reading (Claude).

## 1. KPI definitional frameworks

### David Parmenter: four measure types and seven KPI characteristics

Parmenter sorts measures into two groups and four types [KI-01, KI-02].

- **Quote** [KI-01, ch. 1]: "Key result indicators (KRIs) give the board an overall summary of how the organization is performing. Result indicators (RIs) tell management how teams are combining to produce results. Performance indicators (PIs) tell management what teams are delivering. Key performance indicators (KPIs) tell management how the organization is performing in their critical success factors and, by monitoring them, management is able to increase performance dramatically."
- **Quote** [KI-01]: "financial indicators are a result of activities. I thus believe all financial performance measures are RIs."
- **Quote** [KI-01]: result indicators "do not help management fix a problem as it is difficult to pinpoint which teams were responsible", while performance indicators "can be tied to a team or a cluster of teams working closely together for a common purpose."
- **Quote** [KI-01], the 10/80/10 rule: an organisation with over 500 FTEs "will have about 10 KRIs, up to 80 RIs and PIs, and 10 KPIs".

The seven characteristics [KI-02] are: non-financial; measured frequently ("24 by 7, daily, or weekly"); the CEO's attention; clear and concise ("All staff understand the measure and what corrective action is required"); tied to a team ("A team will accept responsibility and can take action"); significant impact on one or more critical success factors; and a limited dark side (unintended consequence). **Quote** [KI-02]: "A monthly, quarterly, or annual measure cannot be a KPI".

**Inference:** under Parmenter, no price, crack spread or dollar margin can be a KPI, and a monthly refinery utilization figure is a KRI or RI. Most of the planner's list falls into Parmenter's RI and PI types.

### The KPI Institute

- **Quote** [KI-03]: a KPI is "A measurable expression for the achievement of a desired level of results, in an area relevant to the evaluated entity's activity."
- **Quote** [KI-03]: a metric is "something we can measure, a value, or a quantity... When metrics reflect the achievement of a desired state, they become Key Performance Indicators. Oftentimes, metrics represent the subordinated measures used for calculating a KPI."

**Inference:** the Institute's test is purpose (a desired level of results), not frequency or currency. It is wider than Parmenter's.

### Kaplan and Norton: strategic versus diagnostic measures

- **Quote** [KI-04], "Linking the Balanced Scorecard to Strategy": managers fail "to distinguish between diagnostic measures—those measures that monitor whether the business remains 'in control' and are able to signal when unusual events are occurring that require immediate attention—versus strategic measures".
- **Quote** [KI-04]: corporations "should have hundreds, perhaps thousands, of measures that they can monitor... But these are not the drivers of businesses' competitive success. Such measures capture the necessary 'hygiene factors'... These measures should be monitored diagnostically with deviations from expectations noted rapidly; in effect, management by exception."
- **Quote** [KI-04]: a scorecard balances "desired outcomes and the performance drivers of those outcomes". This is the outcome (lagging) and driver (leading) pair.
- **Quote** [KI-05], the 1992 HBR article: the scorecard "complements the financial measures with operational measures on customer satisfaction, internal processes, and the organization's innovation and improvement activities—operational measures that are the drivers of future financial performance."

**Inference:** Kaplan and Norton give the "operational metric" class its strongest backing. Most measures are diagnostic: watched by exception, necessary, and not strategic.

### ISO 22400-1 and -2 (KPIs for manufacturing operations management)

- **Quote** [KI-06, ISO 22400-1 sample, 3.1.4]: a key performance indicator is "one or several related values that provide a proxy understanding of a business or manufacturing process".
- **Quote** [KI-06]: a performance indicator is a "measure defined by an organization for use in determining how well it is making progress towards achieving a particular objective". The note says KPIs "are chosen by an organization based on a specific criteria determined by its mission, operating plans and continual improvement procedures".
- **Quote** [KI-06]: "A measure is a factor in generating an indicator; not all measures are indicators." KPIs are, "as a very rough approximation", "the 20% of all performance measures that account for 80% of impacts".
- ISO 22400-2:2014 defines 34 KPIs for batch, continuous and discrete production [KI-07]. They are time ratios on a work unit. NIST's restatement [KI-08]: utilization efficiency is actual production time (APT) divided by actual unit busy time (AUBT). Allocation ratio is AUBT divided by actual order execution time (AOET).

**Inference:** ISO 22400 calls operational ratios "KPIs" at the manufacturing operations level. Its "utilization efficiency" is a time ratio, not throughput over capacity. It is not the same measure as the refinery utilization rate that EIA and MPC publish. A planner's "unit utilization" should name which one it means.

### ISO 9000 and ISO 9001

I did not check the text of ISO 9000:2015 or ISO 9001:2015 for a KPI definition. Clause 9.1 of ISO 9001 requires an organisation to decide what to monitor and measure. It does not, as far as I know, separate KPIs from other measures. I left it out of the rule.

### APQC Open Standards Benchmarking

- **Quote** [KI-10]: "A measure is a means to determine a performance metric value". Measures are grouped into "Cost Effectiveness", "Cycle Time", "Process Efficiency" and "Staff Productivity", plus "Supplemental Information" that "does not fit into the other measure categories" [KI-11].
- **Quote** [KI-12], a 2015 participant report: "Performance measures are divided into key performance indicators, other performance indicators, and supplemental data."

**Inference:** APQC also uses a three-way split: a few KPIs, many other indicators, and context data. Its measure categories describe what a measure is about, not whether it is key.

### Refining-specific guidance

- **EIA, refinery utilization.** **Quote** [KI-13]: refinery utilization rate "Represents the use of the atmospheric crude oil distillation units. The rate is calculated by dividing the gross input to these units by the operable refining capacity of the units."
- **EIA, operable capacity.** **Quote** [KI-14]: "The amount of capacity that, at the beginning of the period, is in operation; not in operation and not under active repair, but capable of being placed in operation within 30 days; or not in operation but under active repair that can be completed within 90 days."
- **Solomon Associates.** Solomon's methods are proprietary. Secondary sources describe the Energy Intensity Index (EII) as actual energy use divided by a "standard" energy use for a refinery with the same units, times 100. NRCan says "A Solomon EII value of 100 is standard" [KI-15]. Lubes'n'Greases quotes Solomon's own article listing "Energy Intensity Index", "Maintenance Cost Efficiency Index", "Operational availability" and "Utilization outside of turnaround" as the "key metrics" used to rank top refineries [KI-16]. Galp names "Availability and Energy Efficiency" (Solomon EII) as its two main refining indicators, with a first-quartile target [KI-17].
- **API RP 754** (process safety indicators). **Quote** [KI-18]: the indicators "are divided into four tiers that represent a leading and lagging continuum. Tier 1 is the most lagging and Tier 4 is the most leading." The fourth edition is now current [KI-19].
- **MPC.** MPC reports benchmark prices and crack spreads in its 10-K under "Market indicators" (repo fact sheet E5, from MPC-KI-01 Item 7) [KI-20]. It defines margin capture as "MPC's ability to convert benchmark market conditions into realized performance... calculated by dividing our reported R&M Margin to the R&M Margin Indicator" [KI-21].

**Inference:** refining practice treats utilization, availability and energy intensity as headline, benchmarked measures. These are the natural KPI candidates. Solomon normalises them for configuration so they can be compared across sites.

## 2. Planning-specific practice

- **SCOR (ASCM).** **Quote** [KI-22]: "Level 1 metrics are diagnostics for the overall health of the supply chain. They are also known as strategic metrics and key performance indicators (KPIs)... Level 2 metrics serve as diagnostics for level 1 metrics... Level 3 metrics serve as diagnostics for level 2 metrics."
- **SCOR information model.** **Quote** [KI-23]: "Only the top-level Metrics are referred to as strategic metrics or key performance indicators." It also names "Descriptive or activity metrics", which "simply monitor how much of something has occurred", and diagnostic metrics, which help "explain why a performance metric is the way it is". Level-1 SCOR metrics include Perfect Order Fulfillment, Order Fulfillment Cycle Time, Total Supply Chain Management Costs and Cash-to-Cash Cycle Time [KI-24]. Forecast accuracy is not in that level-1 list.
- **Gartner Hierarchy of Supply Chain Metrics.** Three tiers: Assess, Diagnose, Correct. **Quote** [KI-25] (Gartner G00270870, as reproduced): "The demand forecast is at the top, not because it's an outcome or a goal, but to highlight what an important driver it is of performance back through the supply chain." The top tier is demand forecast accuracy, perfect order and SCM cost. The Correct tier includes "Production Schedule Variance" and "Plant Utilization" [KI-26].

**Disagreement:** Gartner puts demand forecast accuracy in its top tier. SCOR keeps it below level 1. Gartner itself says it is at the top as a driver, not an outcome. So the source base does not support calling forecast accuracy "only a diagnostic".

**Inference on plan versus actual:** the sources treat a single-period gap between actual and plan (schedule variance, demand vs forecast this week) as a diagnostic or correct-tier metric. Gartner places "Production Schedule Variance" at the bottom tier. Kaplan and Norton's "deviations from expectations noted rapidly" describes this use. A forecast-accuracy measure aggregated over many periods, with a target and owner, can be promoted to KPI. A row that shows one week's variance cannot. I found no ASCM/APICS dictionary text to quote on this point.

## 3. Market prices and crack spreads

- **Quote** [KI-27], MPC 2024 Annual Report and 10-K: "Our financial results are affected by volatile refining margins, which are dependent on factors beyond our control." Feedstock and product prices "fluctuate independently due to a variety of regional and global market factors that are beyond our control".
- **Quote** [KI-27]: "The crack spread is a measure of the difference between market prices for refined products and crude oil, commonly used by the industry as a proxy for the refining margin."
- **Quote** [KI-28], MPC 10-Q Q1 2018: "As a performance benchmark and a comparison with other industry participants, we calculate Midwest (Chicago) and USGC crack spreads that we believe most closely track our operations".
- MPC files these figures under "Market indicators" [KI-20]. PBF labels its price inputs "Market indicators 'as reported by Platts'" [KI-29].
- **Controllability principle.** Management accounting holds that a manager should be held accountable only for results they can influence. I found this principle only in study notes for CIMA's P2 syllabus [KI-30], not in CIMA's own published text. Merchant and Van der Stede's *Management Control Systems* has a chapter on it, but I did not retrieve that text.
- Parmenter rules out all financial measures as KPIs [KI-01].

**Inference:** a crack spread or benchmark price is an external market indicator. It is a driver and a benchmark, not a performance measure of the region. The controllable KPI built on it is margin capture: realised margin divided by the benchmark margin indicator. That is how MPC uses it [KI-21]. Whether "crude value to breakeven" is a market indicator depends on how it is computed. It combines market prices with the region's own LP economics. If it ranks crude choices, it is a decision input. If it scores how well the region bought crude, it is a performance metric. Part B, Q8, finds the first reading.

## 4. Commonly cited criteria

| Criterion | What the sources say | Source |
|---|---|---|
| Strategic link | KPIs reflect critical success factors or a desired level of results. | Parmenter [KI-01, KI-02]; KPI Institute [KI-03]; ISO 22400-1 [KI-06] |
| Few in number | Up to 10 KPIs (Parmenter); about 20% of measures (ISO 22400-1); top level only (SCOR). | [KI-01], [KI-06], [KI-23] |
| Owner and action | A team can be called and can act on it. | Parmenter [KI-02] |
| Controllability | Hold managers accountable only for what they can influence. | CIMA P2 study notes [KI-30]; MPC "beyond our control" [KI-27] |
| Frequency | KPIs daily or weekly (Parmenter). Others accept monthly or annual (Kaplan and Norton revisit annually). | [KI-02], [KI-05] |
| Leading or lagging | Outcome measures lag. Performance drivers lead. API RP 754 sets four tiers from lagging to leading. | [KI-04], [KI-18] |
| Tier | Strategic, diagnostic, correct (Gartner); level 1, 2, 3 (SCOR); KRI, RI and PI, KPI (Parmenter). | [KI-25], [KI-22], [KI-01] |
| Response required | An alarm indicates "an equipment malfunction, process deviation, or abnormal condition requiring a response". | ANSI/ISA-18.2 [KI-31] |

## 5. Proposed decision rule

Apply the tests in order. Stop at the first test that assigns a class. Each test cites its basis. The ordering is my own design (**inference**).

1. **Is it a quantity with a formula, a unit and a time grain?** If no, it is a **Tracker or report**. Examples: a list of due dates, a summary of plan changes, a status table. Basis: SCOR "descriptive or activity metrics" [KI-23]; ISO 22400-1 "not all measures are indicators" [KI-06].
2. **Is it emitted only when a condition is met, as an event, not a series?** If yes, it is an **Alert**. Basis: ISA-18.2 alarm definition [KI-31]; Kaplan and Norton on signals of "unusual events" [KI-04].
3. **Is its value set by an external market or published benchmark that the region cannot influence?** If yes, it is a **Market indicator**. Basis: MPC "Market indicators" and "beyond our control" [KI-20, KI-27]; controllability principle [KI-30]. *(Decided rule, EPM-DEC-001-0042: test 3 also assigns **decision-support indicator** to a value computed from market prices and the planning model to start or rank a decision, with no performance target. Crude Value to Breakeven is that class; see Part B, Q8.)*
4. **Is it actual compared with a plan, forecast, prior version or target, for one period? *(Decided wording, EPM-DEC-001-0042: actual results, or a plan, compared with a plan, forecast, prior plan version or history.)*** If yes, it is a **Plan-variance diagnostic**. Basis: Gartner "Production Schedule Variance" in the Correct tier [KI-26]; Kaplan and Norton "deviations from expectations" [KI-04]. Exception: an accuracy or attainment measure aggregated over periods, with a target and owner, goes on to test 5.
5. **Does the business name it as one of the few measures of a stated objective, with a target and an accountable owner who can act on it?** If yes, it is a **KPI**. Otherwise it is an **Operational metric**. Basis: KPI Institute [KI-03]; Parmenter's team and CSF tests [KI-02]; SCOR "Only the top-level Metrics" [KI-23]; ISO 22400-1 note on KPIs chosen by criteria [KI-06].

Test 5 needs a recorded business decision. A measure's formula does not show whether it is a KPI. Until someone records that decision, classify it as an **Operational metric (KPI candidate)**.

## 6. Classification vocabulary

| Class | Definition used here | Main source | Planner's examples (inference) |
|---|---|---|---|
| KPI | A metric designated as one of the few that show progress on a stated objective, with target and owner. | KPI Institute [KI-03]; SCOR level 1 [KI-22]; Parmenter [KI-01] | Crude (refinery) utilization against operable capacity; clean product make or yield, if the region sets it as an objective; margin capture, if added |
| Operational metric | A recurring performance or diagnostic measure of a unit, asset or flow. Watched by exception. | Kaplan and Norton "diagnostic" [KI-04]; SCOR levels 2 and 3 [KI-22]; Parmenter PI and RI [KI-01]; ISO 22400-2 [KI-07] | Unit utilization; distillate and gasoline yield; pipeline and marine utilization; inter-regional volumes |
| Plan-variance diagnostic | Actual against plan, forecast or a prior version, for one period. (Decided wording also covers a plan compared with history; EPM-DEC-001-0042.) Explains a gap in a higher metric. | Gartner Correct tier [KI-26]; SCOR diagnostic metric [KI-23] | Demand vs forecast; supply vs forecast; opening inventory vs plan. (Week-on-week input-table variances were listed here first; the decision classes them as an alert, because they fire when a table changes by more than a threshold.) |
| Market indicator | An external price, spread or benchmark outside the region's control. A driver and benchmark. | MPC 10-K [KI-20, KI-27]; controllability principle [KI-30] | Crack spreads; benchmark product and crude prices. Crude value to breakeven was listed here first; Part B, Q8 classes it as a decision-support indicator (EPM-DEC-001-0042) |
| Tracker or report | A list, status or schedule of activities and dates. Not a quantity with a target. | SCOR descriptive or activity metric [KI-23] | Turnaround activity tracker; capital project evaluation due dates; MTP submission due dates; plan change summaries; sales and purchase status trends |
| Alert | An event raised when a condition is met, for someone to notice or act on. | ISA-18.2 [KI-31]; Kaplan and Norton [KI-04] | Production rate record alerts |

Two notes on the examples (**inference**):

- A tracker can produce a metric. Parmenter's KPI examples include "Late projects which have passed their original deadline—reported weekly" [KI-02]. "Count of MTP submissions past due" is an operational metric. The due-date list itself is a tracker.
- A record-rate alert does not meet the ISA-18.2 sense of an alarm. A record is not an abnormal condition. It is an event notification. Keep the class name "Alert" or rename it "Event notification" if the business prefers.

## 7. Where the sources disagree

1. **How many KPIs, and how often.** Parmenter: at most 10, daily or weekly, never monthly [KI-01, KI-02]. ISO 22400-2: 34 named KPIs [KI-07]. Kaplan and Norton: up to about 25 scorecard measures, reviewed monthly and revisited annually [KI-04, KI-05].
2. **Financial measures.** Parmenter says no financial measure is a KPI [KI-01]. The balanced scorecard keeps a financial perspective [KI-05]. MPC's margin capture is a ratio of two dollar figures [KI-21].
3. **Operational ratios.** ISO 22400 calls utilization efficiency a KPI [KI-07]. Gartner puts plant utilization in its bottom tier [KI-26]. Parmenter would call it a PI or RI [KI-01].
4. **Forecast accuracy.** Gartner: top tier, as a driver [KI-25]. SCOR: not level 1 [KI-24].
5. **What "utilization" means.** EIA: gross input over operable capacity [KI-13]. ISO 22400-2: production time over busy time [KI-08]. Solomon: utilization measured on a configuration-weighted basis, also reported outside turnaround [KI-16].

## Sources

| ID | Title | Publisher, date or version | URL | Supports |
|---|---|---|---|---|
| KI-01 | *Key Performance Indicators*, ch. 1 "The Great KPI Misunderstanding" (3rd ed.) | David Parmenter / Wiley, 2015 (free chapter) | https://davidparmenter.com/wp-content/uploads/2024/06/chapter-1-The-great-misunderstanding-Third-edition-of-KPI-book-by-David-Parmenter1.pdf | KRI, RI, PI, KPI; financial measures are RIs; 10/80/10 |
| KI-02 | "KPIs have 7 Characteristics that Make Them Unique" | davidparmenter.com, retrieved 2026-10-18 | https://davidparmenter.com/what-is-a-key-performance-indicator-kpi-the-7-characteristics-of-a-kpi-15-examples-of-kpis-reporting-templates/ | Seven characteristics; monthly cannot be KPI; KPI examples |
| KI-03 | KPI 101, "7. Metrics, KPIs, KRIs and Analytics" | The KPI Institute (smartKPIs), retrieved 2026-10-18 | https://smartkpis.kpiinstitute.org/kpi-101/metrics-kpis-kris-and-analytics | KPI and metric definitions |
| KI-04 | Kaplan and Norton, "Linking the Balanced Scorecard to Strategy" | *California Management Review* 39(1), 1996 | https://www.strimgroup.com/wp-content/uploads/pdf/KaplanNorton_Linking-the-BSC-to-Strategy.pdf | Strategic vs diagnostic; outcomes vs drivers |
| KI-05 | Kaplan and Norton, "The Balanced Scorecard—Measures That Drive Performance" | *Harvard Business Review*, Jan–Feb 1992 | https://hbsp.harvard.edu/product/92105-PDF-ENG | Operational measures as drivers |
| KI-06 | ISO 22400-1:2014, Part 1: Overview, concepts and terminology (sample pages) | ISO, 2014 | https://cdn.standards.iteh.ai/samples/56847/9c4b9ea9d588447bb4f0e476c7c147bd/ISO-22400-1-2014.pdf ; https://www.iso.org/standard/56847.html | KPI and PI definitions; "not all measures are indicators" |
| KI-07 | ISO 22400-2:2014, Part 2: Definitions and descriptions | ISO, 2014 | https://standards.iteh.ai/catalog/standards/iso/8a9efc01-6c74-42a2-ad8f-ec19e84b48f0/iso-22400-2-2014 | 34 KPIs, including utilization efficiency |
| KI-08 | Zhu et al., "A hierarchical structure of key performance indicators for operation management and continuous improvement in production systems" | NIST, 2016 | https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=919754 | ISO 22400 utilization efficiency and allocation ratio formulas |
| KI-09 | "What Is a KPI? How to Define and Measure KPIs" | Snowflake, retrieved 2026-10-18 | https://www.snowflake.com/en/analytics/business-intelligence/kpi/ | KPI is a role around a number (support only) |
| KI-10 | Benchmarks on Demand User Guide | APQC, retrieved 2026-10-18 | https://www.apqc.org/what-we-do/benchmarking/bod-user-guide | Measure definition; measure categories |
| KI-11 | "Markdowns as a percentage of retail sales" (measure page) | APQC, retrieved 2026-10-18 | https://www.apqc.org/what-we-do/benchmarking/open-standards-benchmarking/measures/markdowns-percentage-retail-sales | Supplemental information category |
| KI-12 | APQC participant report | APQC, 2015-03-17 | https://www.apqc.org/sites/default/files/files/APQC_ParticipantReport_20150317.pdf | KPIs, other indicators, supplemental data |
| KI-13 | EIA Glossary, "Refinery utilization rate" | U.S. EIA, retrieved 2026-10-18 | https://www.eia.gov/tools/glossary/index.php?id=Refinery | Utilization definition |
| KI-14 | Refinery capacity table definitions | U.S. EIA, retrieved 2026-10-18 | https://www.eia.gov/dnav/pet/TblDefs/pet_pnp_unc_tbldef2.asp | Operable capacity definition |
| KI-15 | *Energy Consumption Benchmark Guide: Conventional Petroleum Refining in Canada* | Natural Resources Canada / CIPEC | https://natural-resources.canada.ca/sites/www.nrcan.gc.ca/files/oee/pdf/publications/infosource/Pub/cipec/BenchmarkGuide.pdf | Solomon EII = 100 is standard (secondary) |
| KI-16 | "Benchmarking Base Oils: Identifying Traits of Top Performers" | Lubes'n'Greases (Solomon authors), 2020-02-24 | https://www.lubesngreases.com/magazine-emea/26/benchmarking-base-oils-identifying-traits-of-top-performers/ | Solomon's key metrics list (lube refineries) |
| KI-17 | Operational Eco-efficiency case study | Galp, c. 2016 | https://www.galp.com/Portals/0/Recursos/Sustentabilidade/SharedResources/Documents/CS-Eco-efficiency_final.pdf | Availability and EII as main refining indicators |
| KI-18 | API RP 754 fact sheet (3rd ed.) | American Petroleum Institute, 3rd ed. Aug 2021 | https://www.api.org/~/media/files/oil-and-natural-gas/refining/process%20safety/rp-754-fact-sheet.pdf | Leading and lagging tiers |
| KI-19 | API RP 754, 4th ed. (catalogue entry) | Accuris store, retrieved 2026-10-18 | https://store.accuristech.com/standards/api-rp-754?product_id=3128966 | 4th edition is current |
| KI-20 | MPC Form 10-K FY2025, Item 7 (via repo fact sheet E5, MPC-KI-01) | Marathon Petroleum, filed 2026-02-26 | https://www.sec.gov/Archives/edgar/data/1510295/000151029526000009/mpc-20251231.htm | "Market indicators" heading for prices and cracks |
| KI-21 | MPC Q4 and full-year 2025 earnings release (via repo E17, MPC-KI-07) | Marathon Petroleum, 2026 | https://ir.marathonpetroleum.com/investor/news-releases/news-details/2026/Marathon-Petroleum-Corp--Reports-Fourth-Quarter-and-Full-Year-2025-Results/default.aspx | Margin capture definition |
| KI-22 | SCOR DS Quick Reference Guide | ASCM | https://www.ascm.org/globalassets/ascm_website_assets/docs/scor/scor-ds-digital-guide_final.pdf | Level 1 = KPIs; levels 2–3 diagnostics |
| KI-23 | The ASCM SCOR Digital Standard Information Model | ASCM, 2025 | https://www.ascm.org/globalassets/ascm_website_assets/docs/scor/information-model-scor-digital-standard-2025.pdf | "Only the top-level Metrics" are KPIs; activity, performance and diagnostic metrics |
| KI-24 | SCOR Digital Standard, intro and front matter | ASCM | https://www.ascm.org/globalassets/ascm_website_assets/docs/intro-and-front-matter-scor-digital-standard.pdf | Level-1 metric list |
| KI-25 | Gartner, "Supply Chain Guide to Metrics" G00270870 (reproduction) | Gartner (Scribd copy) | https://www.scribd.com/document/266166903/Supply-Chain-Guide-to-Metric-270870 | Three tiers; forecast at top "as a driver" |
| KI-26 | Gartner framing presentation, "Hierarchy of Supply Chain Metrics" | Gartner, ECITL 2013 | http://www.ecitl.eu/ecitl_2013/proc/Ind1/KeyNote/04_GartnerFramingPresentation_LogisticsControlTowers.pdf | Schedule variance and plant utilization in Correct tier |
| KI-27 | MPC 2024 Annual Report and Form 10-K, Item 1A and Item 7 | Marathon Petroleum, 2025 | https://www.marathonpetroleum.com/content/documents/Investors/Annual_Report/2024_MPC_Annual_Report_and_10K.pdf | Margins "beyond our control"; crack spread as proxy |
| KI-28 | MPC Form 10-Q, Q1 2018 | Marathon Petroleum, 2018 | https://www.sec.gov/Archives/edgar/data/1510295/000151029518000056/mpc-20180331x10q.htm | Crack spread "as a performance benchmark" |
| KI-29 | PBF Energy Form 10-K FY2025 (via repo `downstream-peers/pricing-market-data-risk-evidence.md`, DP-03) | PBF Energy, filed 2026-02-12 | Accession 0001534504-26-000010 on sec.gov | "Market indicators" from Platts |
| KI-30 | CIMA P2 study notes on the controllability principle | Scribd / thinka (secondary) | https://www.thinka.ai/en-GB/CIMA-CGMA-Professional-Qualification/P2-%E2%80%93-Advanced-Management-Accounting/Reports-for-decision-making | Controllability principle (weak source) |
| KI-31 | "Understanding and Applying the ANSI/ISA-18.2 Alarm Management Standard" | ISA | https://www.isa.org/getmedia/55b4210e-6cb2-4de4-89f8-2b5b6b46d954/PAS-Understanding-ISA-18-2.pdf | Alarm definition |

## Limits of this note

- I did not read ISO 22400-2's KPI tables directly. The formulas come from the NIST restatement [KI-08].
- Solomon's index definitions are proprietary. KI-15–KI-17 are secondary.
- The Gartner tier quote comes from a reproduction on Scribd [KI-25]. The original sits behind Gartner's login.
- I found no ASCM/APICS dictionary entry to quote on plan attainment or plan adherence.
- The controllability source [KI-30] is study notes, not CIMA's own text. Merchant and Van der Stede's *Management Control Systems* would be a better citation, but I did not retrieve it.
- I did not check the FY2025 10-K for the exact "beyond our control" sentence. I quoted the 2024 Annual Report [KI-27].

---

# Part B. Crude Value to Breakeven and the Mid-Term Planner's turnaround work


Each section separates **quoted facts** (with a source ID) from **inference** (my reading). Source IDs point to the source list at the end. Sources marked *weak* or *secondary* there should not carry a claim alone.

---

## Q8. Crude Value to Breakeven ("V2Be")

### Short answer

Reading (a) fits the evidence. "Crude Value to Breakeven" is most likely a crude-selection screen. For each refinery, it compares the breakeven value of a crude (the price at which processing it gives the same refinery profit as the reference slate, from the LP model or an assay valuation) with the crude's delivered market price. The gap ("variance to breakeven") shows which incremental barrels deserve a full LP evaluation. Classify it as a **market-based decision-support indicator**, not a KPI and not an operational metric. It has no target and nobody is held accountable to it. It changes with market prices, and its job is to start a decision.

### Quoted facts

**Breakeven value is a standard LP output for crude selection.**

- Gary, Handwerk and Kaiser's refining textbook defines it: "refiners use the LP to determine the break-even value of crude oils. The break-even value is the value of the crude that produces the same refinery profitability as for a reference crude." It adds that "Many planners also calculate break-even values for each crude at several crude oil volumes. Because the break-even value of crude oil decreases with increasing amount of crude processed, this is a very useful practice ... [to] provide guidance in decisions regarding the amounts of incremental crude oils to process." The method is described as "the difference in value of increments of crude oils compared to [a] reference crude oil ... evaluated in addition to a fixed crude slate." [VT-01, secondary copy]
- AspenTech's Aspen PIMS brochure: "Traders and planners can easily calculate the breakeven cost of a new crude", "Better determine which crudes in the base case would be displaced by the spot crude", and "Spot crude evaluation highlighting break-even price for easier assessment of opportunity crudes." [VT-02]
- The Aspen PIMS certification study guide lists "Calculate breakeven value of new crude oil/products" and "Summarize the impact of the assumed price on a break-even value analysis." [VT-03]
- Haverly's H/COMET training course covers "calculating netback values for a specific region, country or operator refinery; and estimating breakeven prices for opportunity crudes." The H/COMET brochure lists "Crude Substitution analysis to evaluate opportunity crudes", "Find incremental per barrel marginal values" and "Rank economic crudes of interest." [VT-04, VT-05]
- AVEVA's crude evaluation documentation describes the same workflows: "Incremental Blend: vary the amount of a crude in the refinery base blend to review the effect of the crude on the economics", and "Balancing Crude: replace a crude in the refinery base blend with candidate crudes." [VT-06]

**Value is compared with price to rank crudes and set the bid.**

- Haverly: grades are run through a model "to predict their contribution to profits. Their value relative to each other gives a 'pecking order' of preferred feedstocks for a refinery and the expected margin sets the price you are willing to pay." Also: "The value of a crude is usually assessed by asking how much the optimal value changes when some quantity of it is substituted for part of a reference crude slate." [VT-07]
- Oil & Gas Journal: "A crude's refining value is the value a refiner expects to realize for the products, less operating costs, from processing that crude. Subtracting the crude oil cost from the refining value gives a measure of profit ... Most refiners regularly perform these calculations to provide a ranking of current margins for processing different crude oils." [VT-08]
- McKinsey names the monthly step: "processes within monthly planning—such as price forecasting, commercial constraint review, monthly crude ranking, or relative crude value (RCV)—are rarely reviewed and can be a source of value leakage." [VT-09]
- Platts methodology: "the crude netback minus its spot price gives you the refinery margin." [VT-10] Argus uses Aspen PIMS to compute refinery gate values and "publishes the marginal value of a refined barrel of crude." [VT-11]

**Refiners use netback as a first screen, then evaluate in depth.**

- A refiner's answer at an AFPM Q&A forum (Hunt Refining): the crude purchasing group finds candidate crudes, then "our economic/planning group will utilize the assay of the crude to evaluate this crude using our linear program (LP). This will generate the possible net back for processing the crude. In a parallel path, a committee of technical and operations personnel will evaluate how the crude will impact actual operations and equipment." [VT-12]
- An academic model of refinery procurement: "The procurement department evaluates the available crudes on the exchange and computes a netback value for each ... the procurement team shortlists some (called the crude basket) based on their netback values ... The procurement department uses the landed cost of the crude ... to revise the netback values and selects the crude to be purchased." [VT-13]
- Oil & Gas Journal on incremental barrels: "sometimes the yields on incremental barrels are so poor that they do not even cover the cost of the crude oil itself," and LP "shadow value" economics can mislead because they assume incremental yields equal average yields. [VT-14]

**MPC's own language points to crude selection as a commercial lever.**

- MPC FY2025 10-K, Strategy: "We are focused on leveraging the complexity of our facilities by selecting advantaged raw materials, new approaches in the commercial space to be more dynamic amidst changing market conditions ..." [VT-20]
- MPC FY2025 10-K, Crude Oil Supply: "We obtain the crude oil we refine through negotiated term contracts and purchases or exchanges on the spot market." The Galveston Bay and Garyville refineries each "process a wide variety of crude oils." [VT-20]
- MPC reports "margin capture" as "an operations metric that represents MPC's ability to convert benchmark market conditions into realized performance." [VT-22] This is the after-the-fact score at company level, and MPC names it separately from any crude screen.
- Q2 2026 release, project list: Garyville "Feedstock Optimization ... Further optimizes feedstock slate and increases crude throughput by 30 mbpd" (target YE27). [VT-21]
- Peer example, PBF FY2025 10-K: its railcar fleet "provides transportation flexibility within our crude oil sourcing strategy that allows our East Coast refineries to process cost advantaged crude from Canada and the Mid-Continent." [VT-24]

### Inference

1. The measure's own wording matches reading (a). "Values providing a high-level screening" matches breakeven or netback values. "Triggering deeper evaluation on incremental barrels at each refinery" matches the practice in VT-01, VT-04, VT-12 and VT-13: a quick value-versus-price screen first, then a full LP case run before purchase. An "Incremental Crude Value table by refinery" matches the per-refinery, per-volume breakeven tables that VT-01 describes.
2. "Variance to Breakeven" most likely means breakeven value minus delivered price (or the reverse) in $/bbl. A positive variance flags a crude that is worth more to that refinery than it costs.
3. "Previous bbl economics" and a "previous-month window" add a retrospective element. The likeliest reading is that the screen uses the latest closed month's prices and LP base case, because the prompt-month plan is built before current-month data is final. It is still a forward-looking screen. I did not find a public source that uses this exact phrase, so this point is inference.
4. Reading (b) exists in practice, but under other names. Haverly's GRTMPS brochure lists "Back-Casting Analysis to evaluate past performance" [VT-15], and McKinsey says companies should "highlight gaps between planned, scheduled, and actual performance." [VT-09] Those are plan-versus-actual or margin-capture measures. They are not called "breakeven," and they do not "trigger deeper evaluation on incremental barrels."
5. Classification: a **market-based decision-support indicator**. It is computed from market prices and model output, it changes with the market rather than with team effort, and its purpose is to start a buy/no-buy evaluation. It is not an operational metric (it does not measure plant operation) and not a KPI (it has no target and no owner held to it). If the team later wants to score its crude buying, that would be a separate KPI, such as realized crude advantage versus plan, or MPC-style margin capture.

---

## Q9. Turnaround work for a mid-term planner (M+4 to M+36)

### Short answer

For a mid-term planner, turnaround work is **optimization**. The planner chooses turnaround windows and their sequence across refineries and units. The aim is to minimise lost margin and logistics impact, and to plan supply cover and inventory builds around each window. Schedule adherence is **tracking**, and it belongs to the turnaround execution team (maintenance and turnaround management). It runs close to and during the event, which is inside or below M+3.

Measure classes:

- **KPIs (outcomes at site or portfolio level):** operational availability and mechanical availability, annualized turnaround cost (or MPC's planned turnaround cost per barrel), turnaround interval, and lost margin from turnarounds. *(Decided, EPM-DEC-001-0042: a KPI needs a recorded target and owner. MPC's planned turnaround cost per barrel and lost margin from turnarounds are therefore operational metrics marked KPI candidates, not KPIs.)*
- **Operational metrics (event execution):** duration versus plan, cost versus budget, turnaround work hours, scope growth, and startup time to on-spec.
- **Trackers (status, no target):** milestone schedule adherence, scope-freeze date met, readiness checklists, and the turnaround calendar itself.

### Quoted facts

**Turnarounds are planned years ahead, timed to low demand, with supply plans.**

- AFPM: "Turnaround planning teams often begin their work years ahead of when an actual turnaround project is slated to kick off." Teams "build out a budget and timeline" and "begin developing alternative supply plans to make sure ... that any time a facility spends offline doesn't leave customers without essential fuel." Also: "Turnarounds are carefully planned, often for periods of time where fuel demand is typically lower," "In the United States, turnarounds typically happen in the spring or fall," and "most are on a three- to five-year turnaround cycle." AFPM adds that facilities "do not broadcast or coordinate them with other refineries," so coordination happens inside a company's own system, not across companies. [VT-16]
- An Emerson white paper reports: "Many refiners have turnaround scope freeze dates 9–12 months in advance of the turnaround, and extend this date to 16–18 months when a significant capital project is integrated with the turnaround." [VT-17, vendor]

**Timing and sequence are treated as an optimization problem.**

- A 2025 paper in Chemical Engineering Transactions presents "a discrete-time mixed-integer linear programming (MILP) model to optimize long-term maintenance turnaround scheduling in an oil refinery," which "aims to minimize these disruptions by optimizing turnaround schedules while maintaining product supply and maximizing economic performance." Its outputs include "the maintenance schedule, unit utilization rates, intermediate stock levels," and it uses "a 'lost profit factor' for reduced productivity." [VT-18, academic]
- Haverly's GRTMPS brochure lists "Multi-period, multi-location, mixed integer programming" and "Determine optimum feed product, operational, and yield conditions for a single or a multi-site refining network." [VT-15]
- A Dow and Carnegie Mellon study of turnaround rescheduling at an integrated chemical site found that "Anticipative plan recommends more inventory to hedge against future uncertainties." [VT-19, chemicals, support only]

**MPC plans around turnarounds across its system.**

- MPC FY2025 10-K: "shipping intermediate products between facilities during partial refinery shutdowns allows us to utilize processing capacity that is not directly affected by the shutdown work. Planned maintenance activities, or turnarounds, requiring temporary shutdown of certain refinery operating units, are periodically performed at each refinery." [VT-20]
- MPC FY2025 10-K: "Refining throughput can exceed crude oil refining capacity due to the processing of other charge and blendstocks in addition to crude oil and the timing of planned turnaround and major maintenance activity." [VT-20]
- MPC FY2025 10-K on California: the CEC may "regulate the timing and other aspects of refinery turnaround and maintenance activities," and MPC's reporting "includes our plans for turnaround and maintenance activities at our Los Angeles refinery ... and our plans to address potential impacts on feedstock and product inventories in California resulting from such turnaround and maintenance activities." [VT-20] This is a public example of turnaround timing tied to an inventory plan.
- MPC Q2 2026 10-Q: "Net refinery throughput decreased 116 mbpd due to increased planned turnaround activity, primarily in the Mid-Continent region." [VT-23]
- MPC's quarterly outlook gives planned turnaround cost and throughput side by side. The Q4 2025 release guided Q1 2026 at "Refining planned turnaround costs (in millions) $465" and total throughput of 2,740 mbpd. [VT-22] The Q2 2026 release guided Q3 2026 at $290 million and 3,005 mbpd. [VT-21]

**MPC's turnaround cost measure and accounting.**

- MPC FY2025 10-K, accounting policy: "Costs for planned turnaround and other major maintenance activities are expensed in the period incurred. These types of costs include contractor repair services, materials and supplies, equipment rentals and our labor costs." [VT-20]
- MPC reports "Refining planned turnaround costs per barrel" of $1.39 (2025), $1.31 (2024) and $1.11 (2023). [VT-20] The earnings release labels this table "Dollar per Barrel of Net Refinery Throughput." [VT-22]
- MPC excludes these costs from two other measures. "Refining operating costs exclude planned turnaround and depreciation and amortization expense," and segment adjusted EBITDA "excludes refining planned turnaround costs." [VT-20, VT-22]
- MPC explains changes as timing: "Refining planned turnaround costs increased $117 million, or $0.08 per barrel, due to the scope and timing of turnaround activity." [VT-20]
- Peer contrast, Valero FY2025 10-K: "turnaround costs ... are deferred when incurred and amortized on a straight-line basis over the period of time estimated to lapse until the next turnaround occurs." [VT-25] MPC's per-barrel figure is therefore cash-timed and lumpy, and Valero's is smoothed. Cross-company comparisons need this adjustment.
- PBF defines a turnaround as "a periodically required shutdown and comprehensive maintenance event to refurbish and maintain a refinery unit or units ... and occurs generally on a periodic cycle." [VT-24]

**Benchmark turnaround measures.**

- Solomon: "Mechanical Availability (MA) and OA are Solomon's primary metrics for measuring a refiners' availability performance. The world's best refineries consistently deliver greater than 97% OA." Also: "Selecting the most appropriate turnaround interval, duration, work hours, and spend ... are the main handles to deliver strong unit performance," and "Targeting turnaround intervals between 4-6 years can deliver annual days down performance that enables achieving 97%+ Operational Availability." [VT-26]
- Solomon's Turnaround Duration Study measures phases from "Oil-Out to Preparation for Entry" through "Oil-In to On-Spec from Unit," and compares "durations as percent of standard." [VT-27]
- Oil & Gas Journal (Solomon-based): "Solomon's study methodology requires turnaround expenses to be amortized over the turnaround interval," and "there is only an indirect relationship between turnaround interval and minimizing annualized turnaround costs." [VT-28]
- McKinsey (search excerpt; page not fetched): turnaround strategy should optimize "the cost," "the duration of lost production," "the reliability of the plant after the event," and "the interval between events." [VT-29, not verified]

### Inference

1. The M+4 to M+36 horizon sits where turnaround windows are still movable. The scope freeze happens 9 to 18 months out [VT-17], and planning starts "years ahead" [VT-16]. So the mid-term planner's decision is when and in what order, and how to cover supply. It is not whether the crew is on schedule. That fits optimization.
2. MPC's disclosures show the commercial side of that decision: intermediates moved between refineries during shutdowns, quarterly throughput and turnaround cost guidance, and turnaround-linked inventory plans in California [VT-20, VT-21, VT-22]. MPC does not publish how it chooses turnaround timing, so the claim that MPC optimizes timing across refineries is inference.
3. Tracking still exists, but it belongs to another role. Schedule adherence, duration versus plan and cost versus budget are execution measures for the turnaround team. The mid-term planner uses them as inputs (actual dates and durations update the plan) and does not own them.
4. KPI, metric and tracker split:

   | Measure | Class | Why |
   |---|---|---|
   | Operational availability / mechanical availability (Solomon) | KPI | Site outcome, benchmarked, has a target (above 97% OA) [VT-26] |
   | Annualized turnaround cost; MPC planned turnaround cost per barrel | KPI candidate (financial; decided as an operational metric, EPM-DEC-001-0042) | Reported outcome; MPC discloses it [VT-20] |
   | Turnaround interval / run length | KPI (strategy) | Chosen outcome, benchmarked by unit type [VT-26] |
   | Lost margin (lost profit opportunity) from turnarounds | KPI candidate for the planner (decided as an operational metric, EPM-DEC-001-0042); decision value during optimization | Margin given up for planned downtime; the planner's objective function [VT-18] |
   | Duration versus plan; duration as % of standard | Operational metric | Event execution [VT-27] |
   | Cost versus budget; turnaround work hours | Operational metric | Event execution; Solomon links work hours to cost [VT-26] |
   | Schedule (milestone) adherence; scope-freeze met | Tracker | Status against a plan, owned by the turnaround team |
   | Turnaround calendar (unit, window, duration) | Planning output (reference data) | The thing the planner optimizes, not a measure |

5. One caution for the ontology. MPC's "planned turnaround costs per barrel" is expensed as incurred, so it rises in heavy turnaround years. It reflects timing as much as efficiency. A benchmark-style annualized cost (Solomon amortizes over the interval [VT-28]) is the fairer KPI for comparing years or peers.

---

## Source list

| ID | Source | Publisher | Date | Supports | Quality |
|---|---|---|---|---|---|
| VT-01 | Gary, Handwerk, Kaiser, *Petroleum Refining: Technology and Economics*, 5th ed., chapter on refinery economics and LP | CRC Press | 2007 | Definition of break-even value; per-volume breakeven for incremental crude | Primary textbook, but **secondary copy**: quotes read from an unofficial online copy found by search; verify against the book before citing |
| VT-02 | Aspen PIMS brochure, https://www.aspentech.com/-/media/aspentech/home/resources/brochure/pdfs/fy21/q3/at-03906-bro-aspen-pims.pdf | AspenTech | PDF created 2021-02-19 | Breakeven cost of a new crude; displaced crudes; opportunity crudes | Vendor primary (fetched) |
| VT-03 | Aspen PIMS certification study guide, https://www.aspentech.com/en/-/media/aspentech/home/cst-certification/aspen-pims-certification/at-05200_pims-study-guide | AspenTech | undated | Breakeven value is a core PIMS skill | Vendor primary (search excerpt) |
| VT-04 | H/COMET course page, https://www.haverly.com/training | Haverly Systems | accessed 2026-10-18 | Netback values; breakeven prices for opportunity crudes | Vendor primary (search excerpt) |
| VT-05 | H/COMET brochure, https://www.haverly.com/images/downloads/HCOMET%20Crude%20Oil%20Evaluation.pdf | Haverly Systems | undated | Crude substitution; incremental per-barrel marginal values; ranking | Vendor primary (search excerpt) |
| VT-06 | Create a crude evaluation analytic, https://docs.aveva.com/bundle/usc-psn-oilgas/page/1163078.html | AVEVA | accessed 2026-10-18 | Incremental-blend and balancing-crude workflows | Vendor primary (search excerpt) |
| VT-07 | Blog 73, Unstable crude values, https://www.haverly.com/kathy-blog/745-blog-73-unstablecrudevalue | Haverly Systems | 2020-12-17 (search date) | Pecking order; value sets price willing to pay; substitution method | Vendor primary (fetched) |
| VT-08 | Achieving maximum crude oil value depends on accurate evaluation, https://www.ogj.com/home/article/17233650/achieving-maximum-crude-oil-value-depends-on-accurate-evaluation | Oil & Gas Journal | 2002-01-14 | Refining value minus cost; refiners rank crudes regularly | Trade press, older (search excerpt) |
| VT-09 | Improving refinery margins through value chain optimization, https://www.mckinsey.com/industries/oil-and-gas/our-insights/improving-refinery-margins-through-value-chain-optimization | McKinsey | 2025-01-16 | Monthly crude ranking / relative crude value; plan-vs-actual gaps | Consultancy (search excerpt; fetch blocked) |
| VT-10 | Yields and Netbacks methodology, https://www.spglobal.com/content/dam/spglobal/ci/en/documents/platts/en/our-methodology/methodology-specifications/yields-netbacks-methodology.pdf | S&P Global Commodity Insights (Platts) | current methodology | Netback minus spot price = refinery margin | Primary for Platts method (search excerpt) |
| VT-11 | Argus Refinery Gate Values methodology, https://www.argusmedia.com/en/-/media/project/argusmedia/mainsite/english/documents-and-files/methodology/Argus-Refinery-Gate-Values.pdf | Argus Media | current methodology | PIMS-based marginal value of a crude barrel | Primary for Argus method (search excerpt) |
| VT-12 | Q&A, best practices around initial crude oil qualifications, https://www.afpm.org/print/pdf/node/41083 | AFPM (Q&A forum; answer by Hunt Refining) | undated | LP netback screen plus parallel technical review | Industry association, practitioner answer (fetched) |
| VT-13 | Agent-based supply chain management, 2: a refinery application, https://www.sciencedirect.com/science/article/abs/pii/VT-98135402001515 | Computers & Chemical Engineering (Elsevier) | 2002 | Netback-based shortlist, then landed-cost revision | Academic; describes a modeled process (search excerpt) |
| VT-14 | Determining incremental refining yields can reduce runs, increase profits, https://www.ogj.com/home/article/17215104/determining-incremental-refining-yields-can-reduce-runs-increase-profits | Oil & Gas Journal | 2000-05-29 | Incremental-barrel economics differ from average | Trade press, older (search excerpt) |
| VT-15 | GRTMPS brochure, https://www.haverly.com/images/downloads/GRTMPS%20Planning%20&%20Optimization.pdf | Haverly Systems | undated | Multi-period, multi-site MIP; back-casting of past performance | Vendor primary (search excerpt) |
| VT-16 | Refinery Turnarounds 101, https://www.afpm.org/newsroom/blog/refinery-turnarounds-101-what-are-turnarounds-and-why-do-we-need-them | AFPM | 2023-10-17 | Planning years ahead; alternative supply plans; seasons; 3–5 year cycle | Industry association (fetched) |
| VT-17 | Turnarounds: Strategic Opportunities to Improve, https://www.emerson.com/is/content/emerson/en/final-control/flow-controls/documents/d353025x012.pdf | Emerson | undated | Scope freeze 9–12 months (16–18 with capital project) | **Weak**: vendor white paper (search excerpt) |
| VT-18 | Long-term turnaround planning for an oil refinery using a MILP model, https://www.cetjournal.it/cet/25/117/172.pdf | Chemical Engineering Transactions, vol. 117 | 2025 | Turnaround timing as optimization; lost profit factor; stock levels | Academic (search excerpt) |
| VT-19 | Flexible turnaround planning for integrated chemical sites, https://egon.cheme.cmu.edu/ewo/docs/Dow_Rajagopalan_EWO_Fall_2016-website.pdf | Carnegie Mellon EWO / Dow | 2016 | Inventory hedge around turnarounds | **Weak** for refining: chemicals case |
| VT-20 | MPC Form 10-K FY2025, accession 0001510295-26-000009, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000009/mpc-20251231.htm | Marathon Petroleum (SEC EDGAR) | filed 2026-02-26 | Turnaround expensing; per-barrel turnaround cost; shutdown intermediates; California turnaround and inventory plans; advantaged raw materials; spot purchases | Primary filing (fetched) |
| VT-21 | MPC Q2 2026 earnings release, Form 8-K Ex. 99.1, accession 0001510295-26-000060, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000060/ | Marathon Petroleum (SEC EDGAR) | 2026-08-04 | Q3 2026 turnaround cost and throughput outlook; Garyville feedstock optimization | Primary (fetched) |
| VT-22 | MPC Q4 and FY2025 earnings release, Form 8-K Ex. 99.1, accession 0001510295-26-000003, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000003/ | Marathon Petroleum (SEC EDGAR) | 2026-02-03 | Margin capture definition; Q1 2026 outlook; per barrel of net refinery throughput | Primary (fetched) |
| VT-23 | MPC Form 10-Q Q2 2026, accession 0001510295-26-000061, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000061/mpc-20260630.htm | Marathon Petroleum (SEC EDGAR) | filed 2026-08-04 | Throughput loss from planned turnarounds in Mid-Continent | Primary filing (fetched) |
| VT-24 | PBF Energy Form 10-K FY2025, accession 0001534504-26-000010, https://www.sec.gov/Archives/edgar/data/1534504/000153450426000010/pbf-20251231.htm | PBF Energy (SEC EDGAR) | filed 2026-02-12 | Turnaround definition; cost-advantaged crude flexibility | Peer primary filing (fetched) |
| VT-25 | Valero Form 10-K FY2025, accession 0001628280-26-011499, https://www.sec.gov/Archives/edgar/data/1035002/000162828026011499/vlo-20251231.htm | Valero Energy (SEC EDGAR) | filed 2026-02-25 | Turnaround costs deferred and amortized (contrast with MPC) | Peer primary filing (fetched) |
| VT-26 | Turnaround Maintenance Insights, https://www.solomoninsight.com/blog/turnaround-maintenance-insights | Solomon Associates (HSB) | 2024-09-05 | MA and OA as primary metrics; 97% OA; interval, duration, work hours, spend | Benchmarker (fetched) |
| VT-27 | Turnaround Duration Study, https://www.solomoninsight.com/industries/refining/benchmarking/turnaround-duration-study | Solomon Associates (HSB) | accessed 2026-10-18 | Duration phases; duration as % of standard | Benchmarker (search excerpt) |
| VT-28 | Strategy maximizes turnaround performance, https://www.ogj.com/refining-processing/gas-processing/lpg-markets/article/17231501/strategy-maximizes-turnaround-performance | Oil & Gas Journal | 2004-05-24 | Solomon amortizes turnaround cost over interval; annualized cost | Trade press, older (search excerpt) |
| VT-29 | The upside of downtime, https://www.mckinsey.com/capabilities/operations/our-insights/the-upside-of-downtime | McKinsey | undated | Cost, lost-production duration, reliability, interval | **Weak**: quoted from a Perplexity summary; page not fetched; verify before use |

### Gaps

- T.A. Cook (Accenture), KBC and Hydrocarbon Processing: the search found no turnaround KPI text I could quote. A KBC turnaround-strategy white paper exists (https://www.kbc.global/uploads/files/whitepapers/KBC_White_Paper_-_RAM_Turnaround_Strategy_FINAL_14June2016.pdf, 2016), but I did not fetch it.
- EIA: no EIA source on breakeven crude value was found. EIA covers turnaround seasonality, but AFPM [VT-16] already supports that point.
- No public source uses the phrases "Variance to Breakeven" or "V2Be." The Q8 reading rests on matching the description to standard practice.
- MPC does not publish how it chooses turnaround timing or how it screens crudes. MPC evidence shows the outcomes (throughput, cost, inventory plans), not the method.
- Excluded as unreliable: a refinery website at luandarefinery.com, an X (Twitter) article, and an AI-vendor page. Each repeated points that better sources already cover.
