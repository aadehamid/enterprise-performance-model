# Precedes/Follows — Rule 6 Samples

Redrawn 2026-09-27 from 256 promotions using seed 42. All outcomes pending `D:hamid-verdict`.

18 samples, including 4 citation-only rows (riskiest group).

## REL-00056 (precedes)

- **Source:** `CM-1-1-3-7-4` — Measure Inventory
  - Definition: Establish the measured physical quantity of crude, intermediate, and product inventory across the network — from tank gauging, metering, and vessel and pipeline measurements converted to standard conditions — so book stock, reconciliation, and planning rest on accurate physical positions.
- **Target:** `CM-1-1-3-7-5` — Perform Inventory Reconciliation
  - Definition: Reconcile book inventory against measured physical inventory by location and material, quantify and classify gains and losses, investigate variances beyond tolerance, and post agreed corrections so stock records remain accurate and losses are made visible.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00058:follows:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00070 (precedes)

- **Source:** `CM-1-1-3-8-1` — Generate Orders
  - Definition: Create the delivery orders that feed secondary distribution scheduling — deriving replenishment needs for managed retail sites and customer tanks from stock readings, consumption forecasts, and agreed service levels, and converting them into deliverable orders with quantities and windows.
- **Target:** `CM-1-1-3-8-2` — Schedule Secondary Distribution
  - Definition: Build and maintain the daily secondary delivery schedule — assigning orders to vehicles, compartments, routes, and time windows within fleet, driver, site-access, and product-segregation constraints — to meet required delivery windows at efficient fleet utilization and cost.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00072:follows:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00072 (follows)

- **Source:** `CM-1-1-3-8-2` — Schedule Secondary Distribution
  - Definition: Build and maintain the daily secondary delivery schedule — assigning orders to vehicles, compartments, routes, and time windows within fleet, driver, site-access, and product-segregation constraints — to meet required delivery windows at efficient fleet utilization and cost.
- **Target:** `CM-1-1-3-8-1` — Generate Orders
  - Definition: Create the delivery orders that feed secondary distribution scheduling — deriving replenishment needs for managed retail sites and customer tanks from stock readings, consumption forecasts, and agreed service levels, and converting them into deliverable orders with quantities and windows.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00070:precedes:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00207 (follows)

- **Source:** `CM-1-2-1-3-8` — Capture Structured Deals
  - Definition: Record executed structured and non-standard transactions — multi-leg, embedded-optionality, tolling, prepay, and similar bespoke deals — decomposing them into capturable components so their positions, risks, and obligations are fully represented rather than approximated.
- **Target:** `CM-1-2-1-3-2` — Obtain Trade Approval
  - Definition: Secure the approvals a trade requires before execution — verifying the trader's authority under the delegation of authority, escalating deals beyond that authority, and documenting each approval — so every executed trade is traceably authorized.
- **Route:** sibling+citation
  - Detail: sibling-nearness + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00209 (precedes)

- **Source:** `CM-1-2-1-3-8` — Capture Structured Deals
  - Definition: Record executed structured and non-standard transactions — multi-leg, embedded-optionality, tolling, prepay, and similar bespoke deals — decomposing them into capturable components so their positions, risks, and obligations are fully represented rather than approximated.
- **Target:** `CM-1-2-2-2` — Confirmations Management
  - Definition: Independently confirm and match executed trades with counterparties by generating, receiving, validating, documenting, modifying, reporting, and resolving discrepancies in trade confirmations, so the organization and its counterparty have evidenced agreement on the applicable trade terms.
- **Route:** citation
  - Detail: citation: "and settlement, which follow their instrument types (Confirmations Management, CM-1-2-2-2; Settlements, CM-1-2-4-1). In scope: Decompose structured deals into capturable"
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00212 (precedes)

- **Source:** `CM-1-2-1-3-9` — Capture Transportation Deals
  - Definition: Record executed transportation capacity deals — pipeline capacity, vessel charters, railcar commitments, and trucking capacity, with route or path, capacity, period, and rates — so transport positions, obligations, and costs are represented from execution onward.
- **Target:** `CM-1-2-4-1-12` — Settle Pipelines
  - Definition: Settle pipeline transportation charges with carriers — validating pipeline invoices for tariff transportation, fuel, loss allowance, and related charges against actualized pipeline movements and verified tariff determinants, resolving variances, and submitting authorized payment instructions — so pipeline services complete financially on verified movement actuals.
- **Route:** citation
  - Detail: citation: "CM-1-1-3-6-1); transport settlement follows the mode-specific settlement nodes (CM-1-2-4-1-12/-13/-4/-5); physical transport operation is owned by Midstream and carriers. In"
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00228 (follows)

- **Source:** `CM-1-2-2-1-5` — Perform Margining
  - Definition: Administer margin obligations for cleared and other applicable margined positions — receiving, validating, forecasting, and issuing or responding to margin calls as applicable, reconciling margin balances against CCP, exchange, broker, and counterparty statements, and escalating failed or disputed calls — so margin obligations are met and margin held matches what positions require.
- **Target:** `CM-1-2-1-3-4` — Capture Exchange Trades
  - Definition: Record exchange-executed futures and listed-options trades with contract, delivery month, quantity, price, account, clearing-broker, and allocation details; validate captured execution data against available execution and broker messages; and resolve trade-capture exceptions so the trading record reflects the executed cleared position.
- **Route:** citation
  - Detail: citation: "or liquidity visibility. Cleared positions arrive from Capture Exchange Trades (CM-1-2-1-3-4); contractual credit support is administered at Manage Collateral (CM-1-2-2-1-3"
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00230 (precedes)

- **Source:** `CM-1-2-2-1-5` — Perform Margining
  - Definition: Administer margin obligations for cleared and other applicable margined positions — receiving, validating, forecasting, and issuing or responding to margin calls as applicable, reconciling margin balances against CCP, exchange, broker, and counterparty statements, and escalating failed or disputed calls — so margin obligations are met and margin held matches what positions require.
- **Target:** `CM-1-2-4-1-16` — Settle Broker
  - Definition: Settle broker and clearing-member account activity — reconciling broker statements against internal trade, position, and margin records, validating commissions, fees, and charges, preparing, submitting, tracking, and reconciling authorized broker-facing payment or collateral-transfer instructions, including margin transfers, through the designated Treasury, banking, or payment-operations process, and resolving statement discrepancies — so broker accounts remain accurate, funded, and evidenced.
- **Route:** citation
  - Detail: citation: "cash movements execute through settlement and finance processes (Settle Broker, CM-1-2-4-1-16). In scope: Validate externally calculated margin requirements and run internal"
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00241 (precedes)

- **Source:** `CM-1-2-2-2-1` — Generate Confirms
  - Definition: Produce and dispatch outgoing trade confirmations from captured deal records — using the templates and terms of the governing agreement — and match incoming counterparty confirmations or equivalent contractual acknowledgements against the captured deal record, using the applicable product, agreement, and confirmation standards, chasing unconfirmed trades within applicable timeliness requirements.
- **Target:** `CM-1-2-2-2-5` — Manage Confirm Disputes
  - Definition: Resolve confirmation mismatches and disputes — logging discrepancies between the capture record and the counterparty's confirmation, investigating against execution evidence, agreeing the correct terms with the counterparty, and driving the resolution into the records and any required re-reporting.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00251:follows:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00345 (follows)

- **Source:** `CM-1-2-4-1-4` — Settle Trucks
  - Definition: Settle truck transportation charges with carriers — validating freight invoices against actualized movements and verified freight-charge determinants, applying contracted rates and accessorials, resolving invoice variances, and submitting authorized payment instructions — so trucking services complete financially on verified movement actuals.
- **Target:** `CM-1-2-3-1-2` — Perform Truck Actualization
  - Definition: Actualize truck movements of crude, feedstocks, and products — recording actual loaded and delivered volumes, qualities, and dates from bills of lading, terminal lifting records, and truck tickets, recorded on the contractually applicable measurement and temperature/volume basis — so truck transactions settle on verified actuals.
- **Route:** two-way+citation
  - Detail: two-way (yes:REL-00298:precedes:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00515 (precedes)

- **Source:** `CM-1-3-1-1-3` — Analyze Data
  - Definition: Analyze the collected market data against the defined objectives — market sizing, demand and supply balance, channel and margin structure, trend and scenario analysis — producing evidenced analytical results with their assumptions and confidence stated.
- **Target:** `CM-1-3-1-1-4` — Document Findings
  - Definition: Document and distribute the market-analysis findings — governed findings records with their evidence, assumptions, and confidence — to the consuming strategy, planning, and insight processes, maintaining the findings library so analysis is reusable and auditable.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00516:follows:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00529 (follows)

- **Source:** `CM-1-3-1-3-1` — Source & Collect Information
  - Definition: Source and collect the consumer data the analysis cycle needs — research studies, panels, transaction and loyalty data, and demographic and market data — within consent, privacy, and licensing constraints, and organize it for analysis.
- **Target:** `CM-1-3-1-3-2` — Define Analysis Objectives & Scope
  - Definition: Define each consumer-analysis cycle's objectives, questions, scope, and method with the consuming stakeholders — which segments, behaviors, journeys, and markets, answering which proposition and experience questions — so consumer research answers real decisions.
- **Route:** sibling+two-way
  - Detail: sibling-nearness + two-way (yes:REL-00532:precedes:emitting)
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00530 (precedes)

- **Source:** `CM-1-3-1-3-1` — Source & Collect Information
  - Definition: Source and collect the consumer data the analysis cycle needs — research studies, panels, transaction and loyalty data, and demographic and market data — within consent, privacy, and licensing constraints, and organize it for analysis.
- **Target:** `CM-1-3-1-3-3` — Analyze Data
  - Definition: Analyze consumer data against the defined objectives — segmentation and segment dynamics, needs and preference analysis, behavior and journey analysis, and experience drivers — producing evidenced results with assumptions and confidence stated, within the privacy constraints the data carries.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00536:follows:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00533 (precedes)

- **Source:** `CM-1-3-1-3-2` — Define Analysis Objectives & Scope
  - Definition: Define each consumer-analysis cycle's objectives, questions, scope, and method with the consuming stakeholders — which segments, behaviors, journeys, and markets, answering which proposition and experience questions — so consumer research answers real decisions.
- **Target:** `CM-1-3-1-3-3` — Analyze Data
  - Definition: Analyze consumer data against the defined objectives — segmentation and segment dynamics, needs and preference analysis, behavior and journey analysis, and experience drivers — producing evidenced results with assumptions and confidence stated, within the privacy constraints the data carries.
- **Route:** sibling+citation
  - Detail: sibling-nearness + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00540 (follows)

- **Source:** `CM-1-3-1-4-1` — Source & Collect Information
  - Definition: Source and collect customer and marketer data for the analysis cycle — volumes, margins, service and relationship records, marketer network data, and external context — under the applicable data controls, organized for analysis.
- **Target:** `CM-1-3-1-4-2` — Define Analysis Objectives & Scope
  - Definition: Define each customer-and-marketer analysis cycle's objectives, questions, scope, and method with the consuming stakeholders — which segments, channels, marketers, and periods, answering which proposition and channel questions.
- **Route:** sibling+two-way
  - Detail: sibling-nearness + two-way (yes:REL-00543:precedes:emitting)
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00548 (precedes)

- **Source:** `CM-1-3-1-4-3` — Analyze Data
  - Definition: Analyze customer and marketer data against the defined objectives — needs and segment analysis, channel and counterparty economics, performance and share-of-wallet, and relationship health — producing evidenced results with assumptions and confidence stated.
- **Target:** `CM-1-3-1-4-4` — Document Findings
  - Definition: Document and distribute customer-and-marketer findings — governed records with evidence, assumptions, and confidence, handled per commercial-sensitivity classification — to proposition, channel, and sales consumers and Marketing Insight and Metrics Stewardship, maintaining the findings library.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00550:follows:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00809 (follows)

- **Source:** `CM-1-3-5-4-2` — Create Promotional Event Calendar
  - Definition: Create and maintain the promotional event calendar — the scheduled promotional events across channels and periods — synchronized with the communications plan, supply and inventory readiness, and the forecast-input process.
- **Target:** `CM-1-3-5-4-1` — Define Promotional Plan
  - Definition: Define the promotional plan — which promotions run, for which offers, audiences, channels, and periods, with what mechanics, budgets, and success measures — within the pricing and claims guardrails.
- **Route:** sibling+two-way+citation
  - Detail: sibling-nearness + two-way (yes:REL-00807:precedes:emitting) + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

## REL-00814 (follows)

- **Source:** `CM-1-3-5-4-4` — Create Site Level Marketing Calendar
  - Definition: Create and maintain the site-level marketing calendar — the consolidated marketing activity view per site or site cluster — so sites see one coherent calendar instead of competing programs.
- **Target:** `CM-1-3-5-4-1` — Define Promotional Plan
  - Definition: Define the promotional plan — which promotions run, for which offers, audiences, channels, and periods, with what mechanics, budgets, and success measures — within the pricing and claims guardrails.
- **Route:** sibling+citation
  - Detail: sibling-nearness + citation
- **Outcome:** `D:hamid-verdict` **PASS** 2026-09-27

