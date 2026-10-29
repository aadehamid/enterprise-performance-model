# EPM-DEC-001-0109: Databricks and the ontology: KPI and OPM identifiers, metric views by fact grain, Genie agents under a supervisor, the agents read epm_triples, lineage in its own places, a technical graph in Neo4j, and three years of demo data

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-28, for the answers to the grill's questions and the data extension; the build choices delegated under EPM-DEC-001-0028) |
| Date | 2026-10-28 |
| Questions | How Databricks agents use the ontology (Part 2 of the store-tests handoff): which identifiers measures carry, how metric views and Genie agents are organized, which store the agents read, how they handle lineage, what a technical graph in Neo4j adds, and how much synthetic data the demo needs |
| Source | Claude Code session of 2026-10-28; `answers-2026-10-28-databricks-grill.md` |

## Context

The ontology is done (EPM-DEC-001-0107), and the pricing demo rebuilds the pricing assets in Databricks Free Edition with synthetic data (EPM-DEC-001-0102). Since 2026-10-28 its source databases run on an exe.dev VM (EPM-DEC-001-0102, amendment of 2026-10-28). Part 2 of the work connects the two: Databricks agents that answer from the ontology. Claude put the design to the decision owner as a grill, in four rounds of questions with a recommendation each.

What Claude found first, from the repository:

- Only one measure had an identifier: Crack Spreads Pricing carries KPI-0001, the crack-spread Genie agent's identifier (EPM-DEC-001-0097, item 3). The `kpi` module holds 41 measures in eight kinds, and classes Crack Spreads as a market indicator.
- The demo has two Genie agents: Crack Spread Price Analytics, bound to the crack-spread metric view, and Executive Summary KPIs Analytics, bound to the Executive Summary and benchmark-prices metric views. A refinery operations metric view already holds utilization, planned utilization, yields, R&M margin per barrel, margin capture and opex per barrel over 1,846 refinery-days. *2026-10-28, later:* 9,724 refinery-days since the three-year extension (`demos/downstream-pricing-databricks-free/DATA.md`).
- The projection driver writes the whole ontology to Databricks as a Delta table of triples, `epm_triples`.

What Claude found from primary sources, on 2026-10-28:

- Databricks has a Supervisor Agent in Agent Bricks, generally available, which routes a question to Genie agents and other subagents, and the SDK creates it (`w.supervisor_agents`) (docs.databricks.com, "Use Supervisor Agent to create a coordinated multi-agent system"; the Databricks blog, "Agent Bricks Supervisor Agent is Now GA").
- Databricks Free Edition's limits page (updated 2026-10-18) lists no Supervisor Agent limit, and says "outbound internet access is restricted to a limited set of trusted domains" (docs.databricks.com, "Databricks Free Edition limitations").
- Composite databases are "Enterprise Edition" and "Not available on Aura" (Neo4j Operations Manual, "Composite databases: Concepts").

## Decision

**The decision owner's decisions:**

1. **How the work runs:** questions now, then one goal run alone: "Q&A now, then one goal (Recommended)". The brief for that run: "Approve, start (Recommended)".
2. **What the integration is for (Q1):** a Genie user gets the number and the ontology's definition of the measure, and a data steward sees each metric view tagged with the measures it implements: "Q1. correct".
3. **The source of truth and what the agents read (Q2):** "The pattern is the sourse of truth is the ontology serialized in turtle. This is then projected to consuming application. In this case Neo4J, AuraDB, and databricsk and those must be kept in sync with the source, which we plan to save in git. So since the ontology will be in a delta table, it may be best for the genie agent to read the ontology from that table."
4. **Measure identifiers (Q3, Q5, Q6):** "Give all measure classify as  KPIs an ID like we did for crakc spread but make it incremental. The other measures tagged as Operational metrcis/KPI shoud also have ID that start with "OPM-0001" and make it incremental as KPI." OPM means operational metric: "By the way OPM = Operationam Metrics. This is to distinguisg Operation KPI from the tru KPI i the KPI Store." The decision owner accepted round 2's recommendations on which kinds take which prefix and on keeping four digits: "Yes to all with some coments below".
5. **Metric views and Genie agents (Q7, Q8, Q9, Q11, Q12):** metric views are grouped logically, a new metric view holds the pricing measures, and Genie agents each cover measures that belong together under a supervisor: "I do want you to also create a Metric view for all of the pricing operational metrics/KPI" and "I like the concept of the supervisor agent. Is this a concept in Databricks? Can you check? If it is let us implement even if we have two agents today."
6. **Lineage and a technical graph (Q2, Q10, Q13 to Q15):** the agent handles lineage held in two places, Neo4j and Databricks, and a small technical graph in Neo4j, outside the ontology, shows what Neo4j adds: "Can we add a small techical graph in Neo4j not captured as part of the ontology to demo how genie or Databrick can leverage the graph in neo4j to add additional context." A live connection from Databricks to AuraDB is tested: "I do want to test the connection to auraDB. This will give me an idea on how this will work with Neo4j enterprise as well." No composite database: "Q16: I do not have Enteprise Neo4j on this machine. So we will have to go with what we have."
7. **Where the code lives (Q4):** in the demo: "Q4. agreed".
8. **The data extension:** "extedn it and use the current EIA key", and a data description document: "also create data description document for this synthetic dataset, including the grains and how they were geretaed with links to scripts/notebook used to generate them".
9. **A data-flow diagram:** "By the way when we complete the grilling we should created an updated data flow in https://app.eraser.io/folder/w07vEqNDXhSrfxz2GdiK as a new file".

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Identifiers,** in `kpi` 1.3.0. KPI-0001 stays Crack Spreads Pricing, because the pricing assets use it, although the module classes it as a market indicator. The two measures classed as KPIs take KPI-0002 and KPI-0003. Every operational metric, market indicator, plan-variance diagnostic, decision-support indicator and alert takes an OPM identifier, OPM-0001 onward, in the module's order: 30 measures. In round 2 Claude told the decision owner 31, counting Crack Spreads among the market indicators; the rule, not the number, is what was decided, and Crack Spreads keeps KPI-0001. Trackers, reports and non-measures take none. Four digits keep the identifiers sorting as text and give one pattern per prefix. A measure promoted to KPI later takes a new KPI identifier; its OPM identifier is kept and never reused.
2. **Metric views** are grouped by fact grain: one view per subject area that shares a fact and its dimensions, never one per measure. A new view, `pricing_market_margin_metrics_vw`, holds the six market-price measures (Gasoline, Distillate and Crude Market Pricing, Price Comparison, Additional Market Prices and the R&M Margin Indicator). R&M Margin per Barrel and Margin Capture stay in the refinery operations view, at refinery-day grain. Each measure carries its identifier in its name and comment, and each view a tag listing the identifiers it implements. Where the price catalog has no renewables or NGL series, the demo adds synthetic ones, labelled so.
3. **Genie agents:** one per subject area. Crack Spread Price Analytics and Executive Summary KPIs Analytics stay, and a Pricing and Market Margin agent joins them, with a Refinery Operations agent over `refinery_operations_metrics_vw`, the refinery-day subject area the use cases below need. A Supervisor Agent routes between the four, and each subagent's description names the identifiers it answers for, built from `epm_triples`. If Free Edition refuses the Supervisor Agent, the fallback is Databricks' documented multi-agent app pattern, and the record of the run says which ran.
4. **What the agents read:** the Turtle in git is the source of truth; `epm_triples`, AuraDB and the local Neo4j are projections kept in sync with it. Inside Databricks the agents read the ontology from `epm_triples`, through a definitions view per agent.
5. **Lineage:** each place answers for its own scope. The ontology holds designed lineage (the `data-product` module's pricing tables and their lineage by layer); Unity Catalog records observed lineage in its system tables; Neo4j's technical graph holds what runs outside Databricks. A test compares designed and observed lineage after each demo run and names any edge found in only one. If Free Edition lacks the lineage system tables, the test is skipped with that reason.
6. **The technical graph:** about 100 nodes describing the demo pipeline, which the business ontology does not model: the six source databases on the exe.dev VM (*2026-10-28, later:* seven, with `eia_weekly`), the replication and build steps, every table and view at each layer with its row count and last refresh, and the data-quality checks with their last result. Each node links to the ontology by IRI where one exists (system, data product, KPI or OPM identifier). It lives in the local Neo4j and in AuraDB under a `Tech` label, in the same database as the ontology, so one Cypher query walks from a gold table to the measure it implements. The projection's counts and hashes count only the ontology's labels.
7. **Databricks and Neo4j:** a sync step run from the laptop copies the technical graph into two Delta tables, `tech_graph_nodes` and `tech_graph_edges`, which the agents read; Neo4j stays the source. A live connection from Databricks to AuraDB is tried and reported, with the AuraDB login in a Databricks secret scope written from the local login file without printing it. Free Edition's restriction on outbound access may block it; the record of the run quotes the error if so.
8. **The data extension:** three years of refinery operations with process units (about 14,000 refinery-days and about 140,000 unit-days), monthly plan targets for the same span, and three years of EIA price history fetched with the current EIA key. `rightangle` and `reference_data_hub` stay as they are. A data description document gives every table, its grain, its row count, how it is generated and a link to the script that generates it. *2026-10-28, later:* built over 748 trading days (2023-10-21 to 2026-10-20), because each refinery-day joins that day's crack: 9,724 refinery-days and 76,296 unit-days, fewer than the estimate above, and 481 monthly plan targets (13 refineries over the 37 calendar months the window touches). Freight landed in `rightangle` and the event table in `reference_data_hub`, so those two databases did change; EIA's weekly data by PADD landed in a seventh database, `eia_weekly`. `demos/downstream-pricing-databricks-free/DATA.md` is the data description document.

## Alternatives considered

- **IDs for all 41 measures as KPIs.** Claude's round 1 recommendation; not chosen. The decision owner separated KPIs from operational metrics.
- **Renumbering Crack Spreads as an OPM.** Not chosen: it would break the pricing assets' KPI-0001.
- **No padding.** Not chosen: identifiers would sort wrongly as text (KPI-10 before KPI-2).
- **One metric view or one Genie agent per measure.** Not chosen: it repeats joins and dimensions and gives Genie more places to choose between.
- **A composite database for the ontology and the technical graph.** Not chosen: composite databases need Neo4j Enterprise Edition, which this machine does not have, and Aura does not offer them.
- **AuraDB as the agents' source inside Databricks.** Not chosen: Genie queries only Unity Catalog tables, and Free Edition restricts outbound access.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-28-databricks-grill.md`:

- "Q&A now, then one goal (Recommended)"
- "Give all measure classify as  KPIs an ID like we did for crakc spread but make it incremental."
- "By the way OPM = Operationam Metrics. This is to distinguisg Operation KPI from the tru KPI i the KPI Store."
- "So since the ontology will be in a delta table, it may be best for the genie agent to read the ontology from that table."
- "Yes to all with some coments below"
- "I like the concept of the supervisor agent. Is this a concept in Databricks? Can you check? If it is let us implement even if we have two agents today."
- "I do want to test the connection to auraDB. This will give me an idea on how this will work with Neo4j enterprise as well."
- "Q16: I do not have Enteprise Neo4j on this machine. So we will have to go with what we have."
- "Approve, start (Recommended)"
- "extedn it and use the current EIA key"

## Evidence

- `business_architecture/ontology/kpi/measure-classification.csv` (the 41 measures and their kinds); EPM-DEC-001-0097, item 3 (KPI-0001).
- `demos/downstream-pricing-databricks-free/sql/05_metric_views.sql` (the refinery operations measures); `pricing_demo/genie.py` (the two agents).
- Databricks, "Use Supervisor Agent to create a coordinated multi-agent system", https://docs.databricks.com/aws/en/agents/agent-bricks/multi-agent-supervisor (read 2026-10-28).
- Databricks, "Databricks Free Edition limitations", https://docs.databricks.com/aws/en/getting-started/free-edition-limitations (updated 2026-10-18, read 2026-10-28).
- Neo4j Operations Manual, "Composite databases: Concepts", https://neo4j.com/docs/operations-manual/current/scalability/composite-databases/concepts/ (read 2026-10-28).

## Consequences

- `kpi` 1.3.0 carries the identifiers (decision 1 above), with its shapes, tests and changelog; it still requires core 2.3.0, and the modules that require kpi 1.2.0 keep that pin.
- The demo README's "Use cases" section (PR #399) lists the 18 questions the build answers, the data each needs beyond what the demo held then (EIA's weekly data by PADD, synthetic freight, an event table, synthetic plan versions and a decision log; *2026-10-28, later:* of these, EIA's weekly data by PADD, the freight and the event table have landed with the three-year history, described in `demos/downstream-pricing-databricks-free/DATA.md`, and the plan versions and the decision log were still to come; *2026-10-28, later still:* the plan versions, the decision log and its evidence items landed in PR E2, with the full decision dossiers in a database the pipeline never replicates, `decision_truth`) and the minimal part of the decision owner's enterprise-context-engineering repository the demo takes. Each question becomes an acceptance test of this build.
- Later pull requests build, against the reloaded stores: the store reload; the data extension and the data description document; the pricing metric view and the identifiers on every metric view; the definitions views from `epm_triples`; the Pricing and Market Margin and Refinery Operations Genie agents and the Supervisor Agent; the lineage test; the technical graph, its Delta copy and the AuraDB connection test; and the Eraser data-flow diagram. Each records what ran. *2026-10-28, later:* the data extension and `DATA.md` landed in PR E1; the rest of this list is still to come.
