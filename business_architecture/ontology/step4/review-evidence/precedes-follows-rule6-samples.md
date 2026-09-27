# Precedes/follows — Rule 6 samples (seed 42, from promotions only)

Method approved 2026-09-26 (seed 42, from promotions only). Samples NOT yet reviewed by Hamid — all outcomes pending `D:hamid-verdict`. Amended 2026-09-27: REL-01241 held (no citation), CM-1-1-4 label corrected.

## REL-00245 (follows)

- **Source:** `CM-1-2-2-2-3` — Manage Trade Modifications
  - Definition: Coordinate the confirmation-side processing of agreed post-execution changes to a trade — including amendments, allocations, partial terminations, and early terminations — by validating counterparty agreement, initiating or validating the required controlled trade-record update, re-confirming revised terms, and triggering applicable lifecycle reporting.
- **Target:** `CM-1-2-2-2-1` — Generate Confirms
  - Definition: Produce and dispatch outgoing trade confirmations from captured deal records — using the templates and terms of the governing agreement — and match incoming counterparty confirmations or equivalent contractual acknowledgements against the captured deal record, using the applicable product, agreement, and confirmation standards, chasing unconfirmed trades within applicable timeliness requirements.
- **Route:** sibling — sibling-nearness
- **Outcome:** pending `D:hamid-verdict`

## REL-00039 (precedes)

- **Source:** `CM-1-1-3-6-3` — Track Movements and Inventory Management
  - Definition: Track scheduled movements from load to discharge — monitoring progress against the schedule, maintaining in-transit inventory visibility by movement, and updating scheduling and inventory records as movements progress — so the network always knows what is en route, where, and when it will arrive.
- **Target:** `CM-1-1-3-6-4` — Discharge & Reconcile Load
  - Definition: Administer the discharge of arriving shipments — confirming received quantities and quality documentation, reconciling discharged against loaded volumes to surface in-transit gains and losses per movement, and closing the movement in scheduling and inventory records.
- **Route:** sibling+two-way+citation — sibling-nearness + two-way (yes:REL-00040:follows:emitting) + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00559 (follows)

- **Source:** `CM-1-3-1-5-3` — Analyze Data
  - Definition: Analyze competitor information against the defined objectives — position and share assessment, conduct and strategy inference, capability and economics estimation, and likely-response analysis — producing evidenced results that state what is known, inferred, and assumed.
- **Target:** `CM-1-3-1-5-1` — Source & Collect Information
  - Definition: Source and collect competitor information from legitimate sources — public filings and disclosures, licensed market data, observable market conduct, and published network and pricing information — recording provenance, and never through anti-competitive exchange or illegitimate means.
- **Route:** sibling+two-way — sibling-nearness + two-way (yes:REL-00553:precedes:emitting)
- **Outcome:** pending `D:hamid-verdict`

## REL-00537 (precedes)

- **Source:** `CM-1-3-1-3-3` — Analyze Data
  - Definition: Analyze consumer data against the defined objectives — segmentation and segment dynamics, needs and preference analysis, behavior and journey analysis, and experience drivers — producing evidenced results with assumptions and confidence stated, within the privacy constraints the data carries.
- **Target:** `CM-1-3-1-3-4` — Document Findings
  - Definition: Document and distribute consumer-analysis findings — governed records with evidence, assumptions, and confidence, respecting the privacy classification of underlying data — to proposition, experience, and planning consumers and Marketing Insight and Metrics Stewardship, maintaining the findings library.
- **Route:** sibling+two-way+citation — sibling-nearness + two-way (yes:REL-00538:follows:emitting) + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00522 (precedes)

- **Source:** `CM-1-3-1-2-2` — Define Analysis Objectives & Scope
  - Definition: Define each company-analysis cycle's objectives, questions, scope, and method with the consuming stakeholders — which businesses, markets, capabilities, and periods, answering which strategic questions — so self-analysis lands where strategy needs it.
- **Target:** `CM-1-3-1-2-3` — Analyze Data
  - Definition: Analyze the company's position against the defined objectives — share and share-trend analysis, portfolio and asset-position assessment, capability strengths and gaps, and performance versus market and benchmarks — producing evidenced results with assumptions and confidence stated.
- **Route:** sibling+citation — sibling-nearness + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00322 (follows)

- **Source:** `CM-1-2-4-1-12` — Settle Pipelines
  - Definition: Settle pipeline transportation charges with carriers — validating pipeline invoices for tariff transportation, fuel, loss allowance, and related charges against actualized pipeline movements and verified tariff determinants, resolving variances, and submitting authorized payment instructions — so pipeline services complete financially on verified movement actuals.
- **Target:** `CM-1-2-3-1-1` — Perform Pipeline Actualization
  - Definition: Actualize pipeline movements of crude, feedstocks, and products — recording actual receipt and delivery volumes, qualities, and dates from pipeline meter tickets, carrier statements, and shipper reports, applying pipeline loss allowance, quality-bank, proration, or other carrier and tariff adjustments where applicable, and reconciling actuals against nominated and scheduled volumes — so pipeline t
- **Route:** two-way+citation — two-way (yes:REL-00296:precedes:emitting) + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00219 (follows)

- **Source:** `CM-1-2-2-1-2` — Manage Credit Limits
  - Definition: Establish, maintain, publish, and adjust credit limits for trading counterparties and counterparty groups — based on approved credit assessments, risk appetite, exposure methodology, and credit-support arrangements — administer documented temporary-excess and exception decisions under delegated authority, and reduce, suspend, or withdraw limits when deterioration or policy triggers require it.
- **Target:** `CM-1-2-2-1-1` — Perform Counterparty Credit Reviews
  - Definition: Assess a counterparty's creditworthiness — at onboarding, on a periodic cycle, and on trigger events — analyzing financial statements, ratings, ownership and support structures, payment behavior, and qualitative factors, and assigning or updating the internal credit assessment that limits and monitoring run on.
- **Route:** sibling+citation — sibling-nearness + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00203 (precedes)

- **Source:** `CM-1-2-1-3-6` — Capture Environmental/Renewable Deals
  - Definition: Record executed purchases, sales, and transfers of program-specific environmental instruments — such as RINs, RECs, and emissions allowances — with program, vintage, quantity, price, and compliance-period detail, so instrument positions are accurate from execution onward.
- **Target:** `CM-1-2-3-1-7` — Perform RINs/REC Actualization
  - Definition: Update environmental-attribute and renewable-instrument trading records from authoritative registry lifecycle events — including issuance or generation, separation where applicable, transfer, acquisition, sale, retirement, and cancellation — and reconcile internal instrument positions to the applicable registry or regulatory system of record.
- **Route:** two-way+citation — two-way (yes:REL-00309:follows:emitting) + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00794 (precedes)

- **Source:** `CM-1-3-5-3-5` — Define Resource Allocation / Budgets
  - Definition: Define the communications resource allocation and budgets — distributing the approved envelope across needs, campaigns, and channels per the mix model — as allocations under the applicable delegation of authority.
- **Target:** `CM-1-3-5-3-6` — Define Communications Plan
  - Definition: Define the communications plan — the consolidated plan of campaigns, channels, audiences, timings, budgets, and responsibilities for the cycle — the single planning artifact the release preparation and execution work from.
- **Route:** sibling+two-way — sibling-nearness + two-way (yes:REL-00796:follows:emitting)
- **Outcome:** pending `D:hamid-verdict`

## REL-00068 (precedes)

- **Source:** `CM-1-1-3-7-9` — Manage Inventory Replenishment
  - Definition: Plan and trigger the replenishment of finished-product stock points across the distribution network — determining when and how much to resupply each terminal and depot within inventory policy and the approved plan — so locations stay between minimum and maximum operating levels without emergency movements.
- **Target:** `CM-1-1-3-6` — Plan & Execute Nominations
  - Definition: Prepare, submit, and manage volume nominations to pipelines, vessels, rail, and terminal operators — matching the short-term schedule to each carrier's cycles, batch specifications, and deadlines, and managing confirmations, revisions, and allocations through the cycle.
- **Route:** citation — citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00083 (precedes)

- **Source:** `CM-1-1-4-7-1` — Capture Product Demand Requirements
  - Definition: Assemble the demand requirements that the refinery production case must satisfy — by product, volume, quality grade, location, and delivery period — drawing on the approved demand forecast, firm contractual commitments, and internal transfer requirements for the planning period.
- **Target:** `CM-1-1-4-7-8` — Perform Scenario Analysis
  - Definition: Compare alternative production cases by varying crude slate, run rates, product mix, price, or constraint assumptions, and quantify the margin and feasibility consequences of each, so the preferred case and its sensitivities are understood before the plan is approved.
- **Route:** sibling — sibling-nearness
- **Outcome:** pending `D:hamid-verdict`

## REL-01242 (precedes)

- **Source:** `CM-1-1-7-2` — Maintain Production Scheduling Master Data
  - Definition: Create, maintain, and retire the reference and parameter data the production scheduling model depends on — unit capacities and constraints, product and recipe definitions, transition and changeover rules, tankage parameters, and scheduling calendars — so scheduling results remain accurate and reproducible.
- **Target:** `CM-1-1-7-1` — Update Refinery Execution Instructions
  - Definition: Maintain and issue the approved daily production-schedule instructions — dated campaign commitments, production and movement requirements, product priorities, planning assumptions, and approved schedule changes — so the refinery's operating teams receive a current, traceable scheduling basis.
- **Route:** sibling+two-way+citation — sibling-nearness + two-way (yes:REL-01119:follows:emitting) + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-00112 (precedes)

- **Source:** `CM-1-1-4-7-8` — Perform Scenario Analysis
  - Definition: Compare alternative production cases by varying crude slate, run rates, product mix, price, or constraint assumptions, and quantify the margin and feasibility consequences of each, so the preferred case and its sensitivities are understood before the plan is approved.
- **Target:** `CM-1-1-4` — Refinery Planning and Optimization
  - Definition: Review data objects included in Refinery Premise
- **Route:** citation — citation
- **Outcome:** pending `D:hamid-verdict`

## REL-01119 (follows)

- **Source:** `CM-1-1-7-1` — Update Refinery Execution Instructions
  - Definition: Maintain and issue the approved daily production-schedule instructions — dated campaign commitments, production and movement requirements, product priorities, planning assumptions, and approved schedule changes — so the refinery's operating teams receive a current, traceable scheduling basis.
- **Target:** `CM-1-1-7-2` — Maintain Production Scheduling Master Data
  - Definition: Create, maintain, and retire the reference and parameter data the production scheduling model depends on — unit capacities and constraints, product and recipe definitions, transition and changeover rules, tankage parameters, and scheduling calendars — so scheduling results remain accurate and reproducible.
- **Route:** sibling+two-way+citation — sibling-nearness + two-way (yes:REL-01242:precedes:emitting) + citation
- **Outcome:** pending `D:hamid-verdict`

## REL-01241 (follows)

- **Source:** `CM-1-1-7-2` — Maintain Production Scheduling Master Data
  - Definition: Create, maintain, and retire the reference and parameter data the production scheduling model depends on — unit capacities and constraints, product and recipe definitions, transition and changeover rules, tankage parameters, and scheduling calendars — so scheduling results remain accurate and reproducible.
- **Target:** `CM-1-1-4` — Refinery Planning and Optimization
  - Definition: Review data objects included in Refinery Premise
- **Route:** citation — citation
- **Outcome:** **HELD** / `D:hamid-verdict` / NoAffirmativeSequenceCitation — no citation in source artifacts

## REL-00125 (follows)

- **Source:** `CM-1-1-7-2-3` — Create Production Scheduling and Sequencing Plan
  - Definition: Build the dated production schedule and sequencing plan for the scheduling horizon — assigning campaigns, schedule-level unit commitments, blends, and movements to dates and sequences within the approved plan, the production wheel, and current constraints — producing the schedule that provides the approved basis for refinery execution.
- **Target:** `CM-1-1-7-2-2` — Review Production Wheel and Run Length
  - Definition: Review and maintain the production wheel — the recurring sequence of product campaigns — and each campaign's run length, balancing transition losses and changeover costs against inventory, demand coverage, and unit constraints, so the schedule is built on an economically sound campaign structure.
- **Route:** sibling — sibling-nearness
- **Outcome:** pending `D:hamid-verdict`

## REL-00131 (follows)

- **Source:** `CM-1-1-7-2-5` — Measure Production Scheduling Performance
  - Definition: Measure and report how well execution followed the issued production schedule and how stable the schedule itself was — adherence, rescheduling frequency, and exception causes at agreed levels — feeding improvements back into scheduling practice and master data.
- **Target:** `CM-1-1-7-2-4` — Manage Production Schedule Exceptions
  - Definition: Detect, assess, and resolve deviations from the production schedule — unit upsets, feed or quality surprises, outage changes, and demand shifts — deciding schedule responses, triggering rescheduling, and escalating deviations that break the approved plan to planning.
- **Route:** sibling — sibling-nearness
- **Outcome:** pending `D:hamid-verdict`

## REL-00137 (follows)

- **Source:** `CM-1-1-7-3-2` — Optimize Plant Energy Balance
  - Definition: Establish and maintain planning and scheduling targets for the refinery's sitewide energy balance — such as expected steam, fuel-gas, power, and energy-recovery requirements — so production schedules reflect energy cost, availability, emissions exposure, and operating constraints.
- **Target:** `CM-1-1-7-3-1` — Optimize Internal vs. External Energy Sources
  - Definition: Decide the economically optimal mix of self-generated and externally purchased energy — fuel gas, fuel oil, steam, and power, including cogeneration versus grid supply — for the planning period, within reliability, contractual, and emissions constraints.
- **Route:** sibling+citation — sibling-nearness + citation
- **Outcome:** pending `D:hamid-verdict`
