# Context sample review (seed 42, baseline 6ab2197ba3fe6246bdb501391d22b71d0338d2c7)

51 rows: 41 Commercial & Marketing, 10 Refining. Verdict per row: OK / FLAG.

## REL-00008 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-1-1-1-4** --precedes--> **CM-1-1-2** (Regional Optimization)
Definition: Approve and publish the agreed demand forecast as the versioned planning basis, and translate it into the component-level forecast plan — the detailed breakdown by product grade or component, location, and period — that downstream planning processes consume.
Scope: Covers the release step of the forecast cycle: final approval, version identification, disaggregation of the agreed forecast to the component level used by planning, and distribution to its consumers. The published version is the fixed reference that both planning and forecast-performance measurement run against. Excludes acting on the forecast — supply, production, inventory, and allocation decisions are owned by Regional Optimization (CM-1-1-2) and Refinery Planning and Optimization (CM-1-1-4); excludes the consumers' own receipt and case-assembly steps, owned by Receive Demand Forecast (CM-
Tests: A:explicit-reference 
Verdict: OK — forecast publish precedes regional optimization; scope names the L2 explicitly. (Precedes-a-whole-L2 pattern, same family as REL-00112; the sequence claim itself is sound.)

## REL-00048 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-1-3-7-12** --uses-input--> **CM-1-1-3-7-4** (Measure Inventory)
Definition: Monitor and control actual and projected inventory positions for finished products and intermediates: identify operating-limit, availability, ownership, quality, location, and balance exceptions, coordinate timely response, and provide reliable current-position information to planning and operational stakeholders.
Scope: Covers the recurring review of physical and book inventory positions, movements, and commitments; minimum, maximum, safety-stock, and operating-limit exceptions; short-term availability and imbalance risks; escalation and coordination of corrective actions; and maintenance of the operational inventory-position view that planning and execution consume — a recurring operational control rhythm that complements planning cycles. Excludes inventory-policy design (CM-1-1-3-7-1/-2/-3), formal measurement methodology (CM-1-1-3-7-4), reconciliation and adjustment governance (CM-1-1-3-7-5), and replenish
Tests: A:explicit-reference | B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00050 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-1-3-7-12** --governed-by--> **CM-1-1-3-7-3** (Develop Finished Product Inventory Policy)
Definition: Monitor and control actual and projected inventory positions for finished products and intermediates: identify operating-limit, availability, ownership, quality, location, and balance exceptions, coordinate timely response, and provide reliable current-position information to planning and operational stakeholders.
Scope: Covers the recurring review of physical and book inventory positions, movements, and commitments; minimum, maximum, safety-stock, and operating-limit exceptions; short-term availability and imbalance risks; escalation and coordination of corrective actions; and maintenance of the operational inventory-position view that planning and execution consume — a recurring operational control rhythm that complements planning cycles. Excludes inventory-policy design (CM-1-1-3-7-1/-2/-3), formal measurement methodology (CM-1-1-3-7-4), reconciliation and adjustment governance (CM-1-1-3-7-5), and replenish
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00054 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-1-3-7-3** --enables--> **CM-1-1-3-7-9** (Manage Inventory Replenishment)
Definition: Establish and maintain the policy governing finished-product inventories across refineries and the distribution network — target and minimum operating levels, safety stock by product and location, brand and quality segregation rules, and review triggers — so customer supply reliability is protected at an efficient working-capital cost.
Scope: Covers policy for saleable products at refinery rack, terminal, and depot level, including service-level-driven safety stocks, seasonal and regulatory grade-transition stock rules, and segregation of branded versus unbranded stock. Sets the policy that Plan Finished Goods Inventory (CM-1-1-2-13) plans within — the plan-period target decision itself is owned there per its approved boundary. Excludes replenishment management, owned by Manage Inventory Replenishment (CM-1-1-3-7-9); excludes physical terminal operation, owned by Midstream.
In scope: Set target, minimum operating, and safety stock 
Tests: A:explicit-reference | B:structural-nearness C:two-way-absent(back-verbs=governed-by)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00058 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-1-3-7-5** --follows--> **CM-1-1-3-7-4** (Measure Inventory)
Definition: Reconcile book inventory against measured physical inventory by location and material, quantify and classify gains and losses, investigate variances beyond tolerance, and post agreed corrections so stock records remain accurate and losses are made visible.
Scope: Covers the recurring book-to-physical comparison across tanks, terminals, and in-transit stock: computing over/short by material and location, separating apparent loss (measurement and accounting effects) from physical loss, investigating out-of-tolerance variances, and agreeing corrections to book stock, following hydrocarbon-management good practice (EI HM 32). Excludes taking the physical measurements, owned by Measure Inventory (CM-1-1-3-7-4); excludes financial write-off approval and valuation entries, owned by Finance under the locked Finance rule. A standing loss-control capability that
Tests: A:explicit-reference | C:two-way(back=precedes) | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00184 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-1-3-10** --precedes--> **CM-1-2-2-2-4** (Report Confirmation To SDR)
Definition: Determine whether an executed swap or other transaction is reportable under an applicable trade-reporting regime and, where the organization is the reporting counterparty or has delegated reporting responsibility, submit required creation data to the designated registered swap data repository within applicable deadlines; correct errors and retain required reporting evidence.
Scope: Covers reportability determination, creation-data submission, corrections, resubmissions, acknowledgements, and evidence retention under applicable regimes. Under US CFTC Part 45, this includes creation-data reporting as defined by the applicable rule. Confirmation-event and continuation reporting may be handled by Report Confirmation To SDR (CM-1-2-2-2-4) where the reporting model and regulation require it. Excludes regulatory-policy ownership and monitoring, which belong to Regulatory & Compliance (CM-1-2-4-3); excludes the legal determination of reporting responsibility where Legal/Complian
Tests: A:explicit-reference C:two-way-absent(back-verbs=informed-by)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00190 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-1-3-2** --governed-by--> **CM-1-2-2-3** (Market Risk Management)
Definition: Secure the approvals a trade requires before execution — verifying the trader's authority under the delegation of authority, escalating deals beyond that authority, and documenting each approval — so every executed trade is traceably authorized.
Scope: Covers the pre-execution authorization step: checking the deal against the trader's delegated authority, routing above-authority and non-standard deals (including structured deals) for escalated approval, and recording who approved what. Includes escalation and documented approval, rejection, or conditional approval of trades that exceed delegated authority, approach or breach a limit, are non-standard, or require a documented risk or compliance exception; it does not itself set, waive, or permanently amend risk limits, credit limits, or delegation-of-authority policy. The delegation of author
Tests: B:structural-nearness 
Verdict: OK with note — promoted on B alone; governance-by-process is plausible (risk owns the authority framework) but B-only governed-by rows deserve batch-reviewer eyes.

## REL-00200 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-1-3-5** --precedes--> **CM-1-2-4-1-14** (Settle Terminal/Storage)
Definition: Record executed storage and throughput deals — facility, capacity, injection and withdrawal rights, fees, and period — so capacity positions, obligations, and costs are represented in the trading system from execution onward.
Scope: Covers deal entry for storage capacity transactions: leased tankage and cavern capacity, throughput commitments, and capacity resale, with their rights, fee structures, and periods. The negotiation of storage and throughput agreements is owned by Negotiate Storage / Throughput Agreements (CM-1-2-7-1-3); this node captures the executed deal into the trading record. Excludes storage inventory administration (Manage Third Party Storage, CM-1-1-3-7-11); excludes storage settlement (Settle Terminal/Storage, CM-1-2-4-1-14).
In scope: Capture storage and throughput deal terms | represent capacity rig
Tests: A:explicit-reference 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00210 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-1-3-9** --follows--> **CM-1-2-1-3-2** (Obtain Trade Approval)
Definition: Record executed transportation capacity deals — pipeline capacity, vessel charters, railcar commitments, and trucking capacity, with route or path, capacity, period, and rates — so transport positions, obligations, and costs are represented from execution onward.
Scope: Covers deal entry for transportation capacity transactions across modes, including capacity acquired, released, or resold. The ongoing administration of carrier relationships and contracts is owned by Manage Carrier Contracts (CM-1-2-1-2-9) and Manage Product Transport Agreements (CM-1-2-7-1-2); nominations that use the captured capacity are owned by Plan & Execute Nominations (CM-1-1-3-6-1); transport settlement follows the mode-specific settlement nodes (CM-1-2-4-1-12/-13/-4/-5); physical transport operation is owned by Midstream and carriers.
In scope: Capture transportation capacity deal t
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00238 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-2-1-8** --uses-input--> **CM-1-2-2-1-6** (Perform Advanced Credit Risk Analytics)
Definition: Produce governed internal credit-risk reports — exposures, limit utilization, breaches, credit-support and margin positions, and concentrations, at agreed cadences and levels for management and committees — and provide controlled inputs to applicable external or regulatory reporting through their accountable owners, so the credit risk picture is current, consistent, and decision-ready.
Scope: Covers credit-risk report production and distribution: standard management and committee reporting, breach and exception reporting, credit-support and concentration views, and controlled inputs to external and regulatory reporting owned by their accountable processes. Excludes financial reporting and disclosures, owned by Finance under its locked rule; excludes regulatory filing ownership (Regulatory & Compliance, CM-1-2-4-3); excludes defining enterprise KPIs (KPI workstream).
In scope: Produce management and committee credit-risk reporting | report breaches and exceptions | report credit-sup
Tests: B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00256 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-2-3-10** --uses-input--> **CM-1-2-2-3-2** (Establish & Maintain Delegation Of Authority (DOA))
Definition: Monitor adherence to the organization's own market-risk policies and control framework — mandate and delegation-of-authority adherence, control-cycle completion, exception-procedure use, and policy-required documentation — surfacing violations and control gaps to the accountable owners.
Scope: Covers internal risk-policy compliance monitoring: checking that trading activity stays within mandates and the delegation of authority, that control cycles complete with their designated approvals, that exceptions follow their documented procedures, and that policy-required records exist; escalating violations and recurring gaps. The boundary with regulatory compliance is internal-versus-external rules: adherence to the organization's own risk framework is monitored here; compliance with external law, regulation, and market rules is owned by Regulatory & Compliance (CM-1-2-4-3). Excludes poli
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00260 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-2-3-11** --enables--> **CM-1-2-2-3-13** (Manage Risk Reporting)
Definition: Define, maintain, and run the market-risk scenario and stress set — historical and hypothetical market shocks, commodity and basis stresses, and event scenarios — quantifying their P&L and risk impacts so the organization knows what adverse markets would do to the book before they happen.
Scope: Covers trading-book scenario and stress analysis: maintaining the approved scenario library, running scenarios on the control calendar and on demand, quantifying P&L and measure impacts, and feeding results to limits, appetite discussions, and reporting. This is the trading and market-risk scenario home that batch 02's approved Perform Scenario Analysis (CM-1-1-4-7-8) explicitly points to — production-case scenario analysis stays there. Excludes credit stress testing (CM-1-2-2-1-6); excludes scenario methodology approval (risk governance).
In scope: Maintain the approved scenario and stress li
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00308 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-3-1-6** --precedes--> **CM-1-2-4-1-6** (Settle First Purchaser/Leases)
Definition: Actualize crude and condensate lease purchases — recording actual volumes, gravities, and qualities from run tickets and LACT meter records taken at lease-tank custody transfer, applying the contractual gravity, quality, and deduction adjustments and division-of-interest references — so first-purchase transactions settle on verified actuals.
Scope: Covers matching lease custody-transfer evidence — run tickets from manual gauging or LACT meter records — to lease purchase contracts; recording actual volumes and qualities per lease and run; applying gravity and quality adjustments, deductions, and division-of-interest references maintained under Manage Lease Contract (CM-1-2-1-2-8); and closing lease runs for settlement. Measurement procedures at the lease tank follow API MPMS Ch. 18 custody-transfer practice, performed by the gathering party. Included only where the downstream organization purchases at the lease/wellhead, per the batch 09 
Tests: A:explicit-reference | C:two-way(back=follows) 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00347 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-4-1-5** --follows--> **CM-1-2-3-1-4** (Perform Vessel & Barge Actualization)
Definition: Settle marine transportation charges — validating freight, charter hire, and voyage-related invoices against actualized voyages and verified freight, laytime, and voyage-cost determinants, applying charter party and freight-agreement terms, resolving variances, and submitting authorized payment instructions — so marine services complete financially on verified voyage actuals.
Scope: Covers logistics-service settlement for marine movements: validating owner and operator invoices for freight, charter hire, deadfreight, and other agreed voyage-service charges against actualized voyages and the determinants recorded at actualization (CM-1-2-3-1-4), applying charter party and contract-of-affreightment terms, resolving variances, and preparing and submitting authorized payment instructions through the designated finance processes. Freight and agreed voyage-service charges are settled here; demurrage, detention, despatch, and delay compensation follow the governing charter party
Tests: A:explicit-reference | C:two-way(back=precedes) 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00351 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-4-1-7** --follows--> **CM-1-2-1-3-11** (Capture Transmission Deals)
Definition: Settle transactions with independent system operators, regional transmission organizations, and power pools — validating ISO settlement statements across the day-ahead and real-time settlement cycles and their subsequent true-up versions, performing independent shadow-settlement checks, disputing discrepancies within ISO timelines, and submitting authorized payment and receipt instructions — so ISO-cleared activity completes financially per market rules.
Scope: Covers ISO/RTO and power-pool settlement: receiving and validating settlement statements for energy, capacity, ancillary services, transmission, and associated charge types under the market's two-settlement (day-ahead/real-time) design and multi-version true-up calendar; performing shadow settlement against internal scheduling and metering data; raising statement disputes within the ISO's dispute windows; and preparing and submitting authorized payment and receipt instructions through the designated finance processes. The applicable ISO/RTO settlement statement is the governing market settleme
Tests: A:explicit-reference 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00356 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-4-1-9** --informed-by--> **CM-1-2-2-2-2** (Manage Confirmation Documentation)
Definition: Manage the controlled working and evidentiary document set used by trading settlement — generating, receiving, validating, distributing, and retaining settlement statements, payment instructions, supporting actualization evidence, and applicable invoices — so every settlement is executed and evidenced from controlled, complete documents.
Scope: Covers the settlement document working set across all settlement processes: outbound invoice and statement generation and distribution; inbound document receipt, registration, and completeness checking; association of supporting evidence (tickets, inspection reports, statements) with the settlement record; netting statement documentation; and retention and retrieval of the settlement working set per the applicable requirements. This process controls settlement documents for trading settlement purposes; it is not the legal system of record for every enterprise invoice and does not own enterpris
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00361 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-4-2-10** --uses-input--> **CM-1-2-4-1** (Settlements)
Definition: Calculate, post, and true up accruals for trading activity — un-invoiced delivered or received volumes, expected fees and charges, and estimated prices pending final determination — per the enterprise accrual methodology, so each period's books are complete for activity not yet settled.
Scope: Covers the accrual cycle: identifying accruable activity from actualized movements and open settlement items, estimating accrual values per the enterprise methodology, posting accruals at cut-off, reversing or truing up against actual settlements, and analyzing accrual accuracy. Accruals may be based on actualized but uninvoiced activity, estimated unactualized activity where policy permits, expected service charges, or deferred pricing, depending on the approved close methodology (including provisional-price estimates pending final price determination per the batch 14 crude pricing pattern). 
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00374 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-4-2-4** --follows--> **CM-1-2-4-1** (Settlements)
Definition: Record trading receivables, payables, and actuals in the accounting records — recording authorized settlement outcomes and validated invoices in AR/AP, posting actualized transaction values, monitoring open items and aging, and keeping the payables and receivables position complete and current — so the financial position reflects settled and actualized activity.
Scope: Covers AR/AP and actuals recording for trading activity: recording authorized settlement outcomes and validated invoices in AR/AP (invoice validation itself remains with Settlements per the batch 14 Q3 chain), posting actualized values and settlement outcomes to the accounting records, monitoring open items, aging, and unmatched instructions, and coordinating overdue items with Settlements and Credit Risk through the accountable owners. Cash receipts are applied by Manage Cash Application (CM-1-2-4-2-9); accrual of un-invoiced activity by Manage Accruals (CM-1-2-4-2-10); payment release and ba
Tests: A:explicit-reference C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00390 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-4-2-9** --uses-input--> **CM-1-2-4-1** (Settlements)
Definition: Apply cash receipts to open trading receivables — matching bank-reported receipts against invoices, settlement statements, and netting arrangements, investigating and coordinating resolution of unapplied, unidentified, short, and over payments, and evidencing application — so the receivables position is accurate and cash is accounted for daily.
Scope: Covers cash application for trading receivables: matching bank-reported receipts against open items using invoice references, settlement statements, and netting agreements; applying receipts and posting application entries; investigating and coordinating resolution of unapplied, unidentified, short, and over payments with Settlements, AR, Credit, and counterparty contacts as applicable — Credit Risk makes any resulting credit decision under the batch 11 boundary, not this process; and evidencing daily application. Bank account operation, cash positioning, and funds movement are owned by Treasu
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00437 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-5-1-4** --enables--> **CM-1-2-5-2-1** (Coordinate Feedstock Trading)
Definition: Develop the recommended spot feedstock procurement slate — the quality-screened spot supply candidates that address residual demand, supply disruption, quality constraints, timing needs, or economic opportunities after considering committed term supply, ranked by current economic attractiveness and availability — so spot procurement decisions start from a vetted, refinery-compatible option set.
Scope: Covers spot procurement-slate development: quantifying the requirement against current feedstock demand (CM-1-2-5-2-2) and committed term supply, screening available spot cargoes and grades for refinery quality compatibility, ranking candidates on current economics, logistics feasibility, and timing, and recommending the spot slate to the feedstock recommendation and trading processes. Spot supply means feedstock assessed or acquired for a discrete, near-term market opportunity or short-duration requirement — spot purchases may fill residual demand, replace disrupted term supply, resolve quali
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00440 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-2-5-2-1** --enables--> **CM-1-2-1-3** (Trade Capture)
Definition: Coordinate feedstock supply requirements with the trading processes — translating demand, slate recommendations, and schedule imbalances into requested purchases, sales, or exchanges with their grade, quality, quantity, timing, and delivery requirements, evaluating proposed trades for plan and schedule fit, and incorporating agreed volumes back into the supply plan.
Scope: Covers the feedstock-side interface to trading, mirroring Coordinate Product Trading (CM-1-1-3-5-2, batch 05): specifying what the feedstock plan needs — grade, quality, quantity, timing, location, delivery basis; requesting trading action; evaluating proposed deals for refinery compatibility, schedule feasibility, and plan fit; and incorporating agreed volumes into the supply plan and downstream logistics planning (CM-1-2-5-3). Trading decides the deal; planning decides the plan (decide-versus-advise, batch 05); the binding plan is Refinery Planning and Optimization's (PTC-002). Excludes trad
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00590 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-2-1-2** --precedes--> **CM-1-3-2-1-3** (Develop & Test Brand Hypothesis)
Definition: Establish the brand objectives and the testable strategic hypotheses for each brand-strategy cycle — what the brand must achieve, in which markets and channels, and which beliefs about consumers, customers, and competitors the strategy depends on.
Scope: Covers objective and hypothesis setting for brand strategy: translating corporate and commercial direction into brand objectives; stating the strategic hypotheses (market, consumer, customer/marketer, competitor beliefs) the strategy rests on in testable form; and setting the cycle's decision calendar. The first step of the brand-strategy lifecycle: objectives and hypotheses frame the alternatives (CM-1-3-2-1-1) and the testing (CM-1-3-2-1-3). Excludes corporate strategy (its owner); the testing itself (CM-1-3-2-1-3); strategy development and approval (CM-1-3-2-1-4).
In scope: Set brand object
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00720 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-4-3-1** --precedes--> **CM-1-3-4-3-2** (Conduct Product Development)
Definition: Coordinate the product and service development program — evidence-based stage-gate reviews, development standards, cross-functional coordination, and program-level tracking — recording gate outcomes under the applicable delegation of authority.
Scope: Covers development governance: coordinating evidence-based stage-gate reviews (concept entry, development, validation, pre-launch readiness) and recording outcomes under the applicable delegation of authority; setting development standards (documentation, specification control, testing evidence); convening the functions each gate requires (Regulatory, Quality, Legal, Product Stewardship, supply, operations, Finance); and tracking the program. Gate outcomes never substitute for regulatory, quality, investment, launch, or commercial approval by their accountable owners; where the Q3 gate applies
Tests: A:explicit-reference | C:two-way(back=follows) | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00728 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-4-4-1** --enables--> **CM-1-3-4-4-4** (Protect Intellectual Assets)
Definition: Establish and maintain the intellectual-asset framework — asset categories, identification and disclosure procedures, ownership and decision-rights principles, and handling rules — operationalizing approved Legal IP policy, so intellectual assets are recognized and handled consistently from creation.
Scope: Covers framework setup: defining asset categories (patentable inventions, marks, trade secrets/know-how, copyrights, data assets); establishing identification, disclosure/intake, and external idea/submission procedures; setting classification, handling, confidentiality and trade-secret handling, documentation/provenance, retention and access principles, and brand/trademark use guidance; setting business decision rights under the applicable delegation of authority; and defining escalation paths to Legal. The framework operationalizes approved Legal IP policy and business procedures — it does no
Tests: B:structural-nearness C:two-way-absent(back-verbs=follows)
Verdict: OK — framework enables protection; backlink follows is sequence-consistent and was correctly not counted as two-way.

## REL-00772 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-5-1-4** --follows--> **CM-1-3-5-1-3** (Perform Account Planning)
Definition: Analyze the gaps between the demand forecast, sales plan, targets, and actual margin performance — where assumptions, plans, and commitments diverged from governed actuals, and why — producing the evidence the next planning cycle corrects from.
Scope: Covers margin-gap analysis: comparing governed actual volume, mix, and margin (Finance and settlement data — consumed, never produced) against the demand forecast and sales-plan assumptions, targets, and margin expectations; building the margin bridge and decomposing variance drivers by segment, channel, account, and cause; distinguishing plan quality, input quality, execution, and market causes; and feeding findings to the next cycle, the forecast-input process, and Marketing Performance Analysis (CM-1-3-5-5). Terminology (review): the locked name compares objects of different kinds — the pro
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00864 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-6-4-3** --uses-input--> **CM-1-3-8-2** (Manage Cash Application, A/R & Revenue Accounting)
Definition: Calculate, validate, and settle earned rebates at agreed settlement points: verify performance against the arrangement's conditions, compute amounts due, resolve calculation discrepancies with the customer or partner, and prepare the appropriate authorized settlement request in the agreed form.
Scope: Settlement distinguishes rebate calculation, rebate validation, accrual coordination, credit memo request, cash payment request, and offset/netting request from accounting and funds movement, which remain with Finance/Treasury. Prepare the appropriate authorized credit, offset, accrual-release, or payment request through the accountable accounting/treasury processes. Credit-memo settlements execute through Manage Customer Invoicing and Billing controls (Create Credit Memo); accrual releases coordinate with Analyze and Calculate Accruals. Discrepancies over earned amounts under an arrangement a
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00932 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-7-2-2** --enables--> **CM-1-3-7-3-1** (Capture & Validate Order)
Definition: Formally issue customer quotes and manage renewals through governed systems: produce quotes from approved prices, established terms, and the approved quote content requirements; manage validity periods, revisions, and versioning; and run contract-anchored renewal cycles so expiring arrangements are re-quoted and re-executed on time.
Scope: Quotes are issued with their approved legal status, validity period, conditions, disclaimers, and binding/non-binding treatment as determined by the applicable legal, contract, and commercial framework. A quote does not create a binding commitment unless the applicable approval, acceptance, and contract/order controls establish one. Quotes price exclusively from governed price and discount master data and established terms — never from ad-hoc values (no-self-exception). Quote composition for a specific opportunity is Develop Quote's (Sales Execution); this process issues the controlled documen
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00950 [Commercial & Marketing] PROMOTE via C:two-way
**CM-1-3-7-3-2** --follows--> **CM-1-3-7-3-1** (Capture & Validate Order)
Definition: Allocate available product and supply capacity to validated orders and release allocated orders to the physical scheduling and fulfillment processes. Apply approved allocation rules, including contractual commitments, approved priority classes, fairness rules, regulatory/safety obligations, and authorized shortage/disruption procedures.
Scope: Allocation rules are applied, not made: allocation policies, including shortage and disruption procedures, are approved by the accountable commercial and supply leadership under their own approvals, with Legal review where allocation touches contractual or regulatory obligations; this process applies the approved rules, documents allocation decisions, and escalates conflicts it cannot resolve within them. Allocation and release operate in daily/intraday operating cycles and may be re-run on supply, credit, order, contract, or disruption events. Release requires the applicable validation, alloc
Tests: C:two-way(back=precedes) | B:structural-nearness 
Verdict: OK — strongest in sample: C (precedes backlink) + B.

## REL-01004 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-8-1-2** --uses-input--> **CM-1-3-7-3-4** (Manage Fulfillment)
Definition: Account for customer self-billing arrangements: receive customer-issued billing documents under executed self-billing agreements, validate each against confirmed fulfillment evidence and governed prices and terms, record the validated self-bill, and resolve differences with the customer per the agreement.
Scope: Self-billing operates only under executed agreements that meet the applicable tax-law conditions — fact-dependent by jurisdiction, determined by the Tax function; no self-billing without a qualifying agreement. The applicable agreement must specify the parties' billing responsibility, tax/document treatment, acceptance rules, evidence basis, data exchange, correction process, retention obligations, and settlement mechanism. A customer's self-bill never overrides governed evidence or prices: validation compares to confirmed fulfillment evidence and governed data, and differences resolve per the
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01005 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-8-1-2** --governed-by--> **CM-1-3-7-2-1** (Establish Commercial Terms & Contracts)
Definition: Account for customer self-billing arrangements: receive customer-issued billing documents under executed self-billing agreements, validate each against confirmed fulfillment evidence and governed prices and terms, record the validated self-bill, and resolve differences with the customer per the agreement.
Scope: Self-billing operates only under executed agreements that meet the applicable tax-law conditions — fact-dependent by jurisdiction, determined by the Tax function; no self-billing without a qualifying agreement. The applicable agreement must specify the parties' billing responsibility, tax/document treatment, acceptance rules, evidence basis, data exchange, correction process, retention obligations, and settlement mechanism. A customer's self-bill never overrides governed evidence or prices: validation compares to confirmed fulfillment evidence and governed data, and differences resolve per the
Tests: B:structural-nearness 
Verdict: OK with note — B-only governed-by; terms process plausibly governs billing. Same B-only note as REL-00190.

## REL-01026 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-8-2-4** --follows--> **CM-1-3-8-2-3** (Apply Receipts)
Definition: Own the exception state for cash that cannot be applied: research unidentified and unapplied receipts, contact customers through the service channels, resolve each item within policy time bounds — application, refund request, or other authorized disposition — and maintain aged visibility of everything unresolved.
Scope: An explicit, aged, owned state: every unapplied or unidentified item carries an owner, aging, and a policy resolution clock — nothing is silently netted, absorbed, or left to age invisibly. Exception resolution, refund request, offset, transfer, or reclassification must preserve segregation of duties between investigation, approval, accounting posting, and Treasury execution. Resolutions follow their authorized paths: application on evidence, refund by authorized payment request under the payment-authority rule, offset per approved rules, or escalation. Unresolved credits, overpayments, uncash
Tests: B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01114 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-6-7** --uses-input--> **CM-1-3-6-1-2** (Manage Relationship with License Brand Providers)
Definition: The process of governing brand standards across the branded network: defining and maintaining the standards that govern brand presentation and customer experience at branded sites and channels, verifying conformance through inspection programs, and managing the brand imaging of sites and assets to those standards.
Scope: Standards-versus-rights boundary: brand assets — trademarks, trade dress, visual identity — are owned, registered, and legally protected under Manage Licensing & IP and the enterprise brand governance framework; this process defines, applies, monitors, and coordinates conformance to usage and presentation standards, makes no legal determinations, and grants no rights. Standards may cover visual identity, trade dress, site appearance, forecourt/store experience, signage principles, digital brand use, uniforms, collateral, partner use, and approved customer-experience manifestations. They do not
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01133 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-6-2** --enables--> **CM-1-2-6-3** (Supply Operations)
Definition: Manage refined-product demand on the supply side — maintaining the operational demand picture the supply chain runs on, forecasting location-level product demand for supply operations, and managing product-exchange volumes as a balancing lever — so supply operations, replenishment, and trading coordination work from one current, operational demand view.
Scope: Covers the operational demand cycle: managing the current demand picture against supply capability (CM-1-2-6-2-1), operational location-level demand forecasting for the supply-chain context (CM-1-2-6-2-3, under the batch 03 constraint), and operational management of product-exchange volumes as a supply and demand balancing lever (CM-1-2-6-2-2). The enterprise published demand forecast is owned by Produce Demand Forecast (CM-1-1-1-1) and consumed here as an input; trading's forward-view intake is Receive Demand Forecast (CM-1-2-1-1-2); the refinery-planning demand basis is Capture Product Deman
Tests: B:structural-nearness C:two-way-absent(back-verbs=uses-input)
Verdict: OK on resolution — G1 enables; merge-vs-emit is a mapping decision for Hamid, resolution itself correct.

## REL-01165 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-9-3** --uses-input--> **CM-1-3-9-2** (Service & Support Delivery)
Definition: The process of measuring the service operation on a recurring cycle: infrastructure and channel performance, workforce operational performance, and overall service effectiveness — consolidated into an integrated service performance view.
Scope: The process consolidates the three measurement domains into an integrated service performance view for operating-model, workforce, technology, facilities, and service-improvement owners. It does not set staffing, change technology, approve capital, alter service levels, or publish enterprise KPIs. The analysis rules apply in full (b21/b23/b35): measurement analyzes and informs — the owners decide; all metrics are evidence-layer with candidate KPIs routed only via the KPI Store; and this is the governed measurement side of the batch 35 formal-research distinction. Employee measurement per the b
Tests: A:explicit-reference | B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01196 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-2-3** --informed-by--> **CM-1-3-1-3** (Consumer Analysis)
Definition: Develop and maintain the approved value proposition offered to end consumers in the company's downstream markets — the strategic promise concerning fuel, convenience, loyalty, and experience value — through a recurring, hypothesis-driven strategy cycle grounded in governed consumer evidence, so consumer-facing offers and experiences deliver a deliberate, approved promise.
Scope: Covers the consumer (B2C) value-proposition lifecycle: establishing principles and objectives (CM-1-3-2-3-3), formulating and evaluating delivery alternatives (CM-1-3-2-3-2), testing with consumer evidence (CM-1-3-2-3-1), and developing and updating the approved proposition strategy (CM-1-3-2-3-4). Consumer evidence comes from Consumer Analysis (CM-1-3-1-3) under its privacy and publication controls (batch 21 shared statement; aggregate/de-identified default). The proposition is the strategic promise; concrete offers, network, and experience designs live at CM-1-3-3-1/-4 and CM-1-3-2-5; loyalt
Tests: A:explicit-reference | B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01200 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-3-1** --informed-by--> **CM-1-3-2-3** (Consumer Value Proposition)
Definition: Define the concrete customer offers that deliver the approved value propositions — which customer groups are targeted, what each offer contains, how it is validated, and how its performance will be measured — through a recurring offer-design cycle, so execution sells defined, validated offers rather than improvised ones.
Scope: Covers the offer-definition lifecycle: defining target customer groups (CM-1-3-3-1-1), defining the customer offer (CM-1-3-3-1-2), validating it with evidence (CM-1-3-3-1-3), and defining its measurement framework (CM-1-3-3-1-4). Designs within approved strategic direction: the value propositions (CM-1-3-2-2/-3) and brand strategy (CM-1-3-2-1) set the promise; this cluster turns the promise into defined offers. Defined offers become executable only after required commercial, pricing, legal, operational, product/service, and approval controls are satisfied. Offer price terms are designed with, 
Tests: B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01217 [Commercial & Marketing] PROMOTE via A:explicit-reference
**CM-1-3-6-1** --informed-by--> **CM-1-3-3-3** (Sales & Distribution Channel Design)
Definition: Manage the company's channel partner relationships — franchisees, licensed-brand providers, dealers, jobbers, and marketers — executing the designed engagement models, coordinating partner qualification and activation through the accountable control owners, reporting partner performance, and developing partner capability.
Scope: Covers channel partner relationship execution: managing franchisee relationships under their franchise agreements (CM-1-3-6-1-1), managing licensed-brand provider relationships (CM-1-3-6-1-2), reporting franchise performance (CM-1-3-6-1-3), and training and certifying franchise site managers (CM-1-3-6-1-4). Executes the engagement models designed at CM-1-3-3-3-4 and the channel offerings created at CM-1-3-3-3-1. Onboarding model (review): this process owns the commercial side — coordinate commercial partner qualification, selection recommendation, onboarding readiness, and relationship activat
Tests: A:explicit-reference | B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01245 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-2-1-1** --enables--> **CM-1-2-1-4** (Trading Strategy Management)
Definition: The front-office capability to assemble and maintain a forward commercial view of supply, demand, generation, renewables, market conditions, and revenue, and to identify how the asset portfolio can be used commercially within approved plans and constraints.
Scope: Covers receiving and consolidating production, demand, and power-generation forecasts from their owning processes; producing the renewables forward view; identifying and valuing commercial use of asset flexibility; and projecting trading revenue, margin, and exposure. This capability consumes forecasts rather than owning their production: the approved demand forecast is owned by Produce Demand Forecast (CM-1-1-1-1) per the batch 03 decision, and production plans and schedules by Refinery Planning and Optimization (CM-1-1-4) and Refinery Production Planning and Scheduling (CM-1-1-7). Excludes t
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01249 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-7-1** --enables--> **CM-1-3-7-3** (Capture And Manage Order Fulfillment)
Definition: The capability that stewards the governed commercial master data on which sales, pricing, fulfillment, billing, and service transactions depend — customer, price and discount, product and service, tax, and location/site records, together with the workflow configurations and commercial policy content that control how they change — maintaining each domain as validated, effective-dated, auditable records through concurrent stewardship processes.
Scope: Governed Submission and Stewardship Rule: accountable business processes decide the business content of a governed record — such as a price, rebate term, credit status, tax position, product definition, policy, workflow authority, or customer qualification outcome. Master-data stewardship validates submission completeness and authority, applies only approved changes through controlled workflows, effective-dates and versions the record, preserves lineage and audit evidence, monitors quality, and distributes the governed record to consumers. Submitting processes do not write directly to governed
Tests: B:structural-nearness C:two-way-absent(back-verbs=uses-input)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01250 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-7-1** --enables--> **CM-1-3-8-1** (Manage Customer Invoicing and Billing)
Definition: The capability that stewards the governed commercial master data on which sales, pricing, fulfillment, billing, and service transactions depend — customer, price and discount, product and service, tax, and location/site records, together with the workflow configurations and commercial policy content that control how they change — maintaining each domain as validated, effective-dated, auditable records through concurrent stewardship processes.
Scope: Governed Submission and Stewardship Rule: accountable business processes decide the business content of a governed record — such as a price, rebate term, credit status, tax position, product definition, policy, workflow authority, or customer qualification outcome. Master-data stewardship validates submission completeness and authority, applies only approved changes through controlled workflows, effective-dates and versions the record, preserves lineage and audit evidence, monitors quality, and distributes the governed record to consumers. Submitting processes do not write directly to governed
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01279 [Commercial & Marketing] PROMOTE via B:structural-nearness
**CM-1-3-8-4** --uses-input--> **CM-1-3-8-2** (Manage Cash Application, A/R & Revenue Accounting)
Definition: The capability that closes and evidences O2C's books and obligations: running period-end processing on the Finance calendar, reconciling receivables to the general ledger with control evidence, analyzing and calculating accruals, reconciling and preparing indirect-tax reporting, preparing taxability-treatment recommendations for Tax approval, executing intercompany invoicing per approved transfer-pricing policies, and administering royalty, brand-fee, and contribution streams under executed agreements.
Scope: Accounting Execution Rule: O2C accounting, reconciliation, accrual calculation, tax-reporting preparation, intercompany invoicing, and royalty/fee administration execute under Finance- and Tax-approved policies, methodologies, calendars, agreements, delegations, and controlled evidence requirements. Finance and Tax retain policy, accounting/tax interpretation, elections, filing ownership, sign-off authority, and financial-statement responsibility. Period-end close proceeds only with complete, reconciled, evidenced inputs from feeding processes or a documented Finance-approved close exception. 
Tests: B:structural-nearness 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00085 [Refining] PROMOTE via B:structural-nearness
**CM-1-1-4-7-2** --uses-input--> **CM-1-1-4-7-3** (Capture Crude Availability)
Definition: Assess candidate crude oils and feedstocks for processing suitability and economic value in the planning period, using assay and quality data, expected yields against the refinery configuration, and delivered-cost economics, to produce the evaluated set available to the optimization case.
Scope: Covers technical and economic screening of candidate crudes and feedstocks for planning: confirming assay and quality data is current and complete, estimating yields and processing fit against unit configuration and specification limits, valuing each candidate on a delivered-cost and netback basis, and flagging handling or compatibility issues. Excludes laboratory assay testing and certification, and excludes purchase, negotiation, and trade execution, owned by Supply And Trading (CM-1-2). Approval of the final crude slate remains with Refinery Planning and Optimization (CM-1-1-4).
In scope: C
Tests: B:structural-nearness C:two-way-absent(back-verbs=enables)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00089 [Refining] PROMOTE via A:explicit-reference
**CM-1-1-4-7-3** --enables--> **CM-1-1-4-7-2** (Evaluate Crude & Feedstock)
Definition: Establish which crude and feedstock volumes can realistically be secured and delivered inside the planning period — by grade, source, and arrival window — covering already-contracted supply, term liftings, and credible spot opportunities.
Scope: Covers the supply-side volume basis of an optimization case: confirming contracted and term volumes, identifying credible additional spot availability, and stating arrival windows and any logistics or quality qualifications. Establishes what is available, not what is bought or where it is sent. Excludes securing supply and executing trades, owned by Supply And Trading (CM-1-2); excludes arrival and delivery scheduling, owned by Plan Feedstock Arrival (CM-1-2-5-3-3); excludes placing secured supply across refineries, owned by Allocate Crude and Feedstock (CM-1-1-2-10).
In scope: Confirm contrac
Tests: A:explicit-reference | B:structural-nearness C:two-way-absent(back-verbs=uses-input)
Verdict: OK on resolution — G1 enables; merge proposal stands for Hamid.

## REL-00090 [Refining] PROMOTE via A:explicit-reference
**CM-1-1-4-7-3** --informed-by--> **CM-1-2** (Supply And Trading)
Definition: Establish which crude and feedstock volumes can realistically be secured and delivered inside the planning period — by grade, source, and arrival window — covering already-contracted supply, term liftings, and credible spot opportunities.
Scope: Covers the supply-side volume basis of an optimization case: confirming contracted and term volumes, identifying credible additional spot availability, and stating arrival windows and any logistics or quality qualifications. Establishes what is available, not what is bought or where it is sent. Excludes securing supply and executing trades, owned by Supply And Trading (CM-1-2); excludes arrival and delivery scheduling, owned by Plan Feedstock Arrival (CM-1-2-5-3-3); excludes placing secured supply across refineries, owned by Allocate Crude and Feedstock (CM-1-1-2-10).
In scope: Confirm contrac
Tests: A:explicit-reference 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00111 [Refining] PROMOTE via B:structural-nearness
**CM-1-1-4-7-8** --uses-input--> **CM-1-1-4-7-5** (Capture Refinery Level Constraints)
Definition: Compare alternative production cases by varying crude slate, run rates, product mix, price, or constraint assumptions, and quantify the margin and feasibility consequences of each, so the preferred case and its sensitivities are understood before the plan is approved.
Scope: Covers case-based analysis inside the optimization cycle: defining the scenarios worth testing, running them against the case basis, reading marginal values and binding constraints, quantifying margin and feasibility differences, and documenting the comparison that supports the recommended case. Excludes selecting and approving the production plan, owned by Refinery Planning and Optimization (CM-1-1-4). Excludes trading and market risk scenarios, owned by Manage And Run Risk Scenarios (CM-1-2-2-3-11). Excludes comparing actual performance to the approved plan, owned by Regional Backcasting (CM
Tests: B:structural-nearness C:two-way-absent(back-verbs=constrains)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00118 [Refining] PROMOTE via A:explicit-reference
**CM-1-1-7-1-3** --enables--> **CM-1-1-3-7-5** (Perform Inventory Reconciliation)
Definition: Close the refinery's daily production balance — reconciling measured feed receipts, unit charges and yields, blending, shipments, fuel and loss, and inventory changes into an accounted material balance — and actualize production against the schedule so planning, scheduling, and backcasting run on verified actuals.
Scope: Covers daily production and yield accounting per refinery hydrocarbon-management practice (EI HM 31): assembling measured quantities, balancing the site by unit and material, attributing imbalance and apparent loss for investigation, and publishing the day's actuals. Excludes owning the physical measurement basis, which sits with Measure Inventory (CM-1-1-3-7-4) with readings taken by asset operators; excludes periodic network book-to-physical stock reconciliation, owned by Perform Inventory Reconciliation (CM-1-1-3-7-5), which this balance feeds; excludes financial and cost accounting, owned 
Tests: A:explicit-reference 
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00120 [Refining] PROMOTE via B:structural-nearness
**CM-1-1-7-2-1** --enables--> **CM-1-1-7-2-3** (Create Production Scheduling and Sequencing Plan)
Definition: Create, maintain, and retire the reference and parameter data the production scheduling model depends on — unit capacities and constraints, product and recipe definitions, transition and changeover rules, tankage parameters, and scheduling calendars — so scheduling results remain accurate and reproducible.
Scope: Covers stewardship of production-scheduling-specific reference and parameter data over its lifecycle: requesting and validating changes, applying effective dates, and confirming scheduling results remain consistent after a change. Excludes supply-planning master data, owned by Maintain Supply Planning Master Data (CM-1-1-2-12); excludes demand-forecast data preparation (CM-1-1-1-1-1); excludes customer, price, product, tax, and location master data (Manage Commercial Master Data Stewardship, CM-1-3-7-1); excludes enterprise master-data policy and governance, which sit with the Data Governance 
Tests: B:structural-nearness C:two-way-absent(back-verbs=uses-input)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00122 [Refining] PROMOTE via A:explicit-reference
**CM-1-1-7-2-2** --enables--> **CM-1-1-7-2-3** (Create Production Scheduling and Sequencing Plan)
Definition: Review and maintain the production wheel — the recurring sequence of product campaigns — and each campaign's run length, balancing transition losses and changeover costs against inventory, demand coverage, and unit constraints, so the schedule is built on an economically sound campaign structure.
Scope: Covers the periodic review of campaign sequence and duration: the transition structure (which product can follow which at what cost), wheel cycle time, run lengths per product against demand and storage, and wheel exceptions for demand shifts and outages. Excludes building the dated schedule itself, owned by Create Production Scheduling and Sequencing Plan (CM-1-1-7-2-3); excludes plan-period product mix decisions, owned by Refinery Planning and Optimization (CM-1-1-4); excludes executing transitions, owned by Refining.
In scope: Maintain the campaign transition structure and costs | set wheel
Tests: A:explicit-reference | B:structural-nearness C:two-way-absent(back-verbs=follows)
Verdict: OK on resolution — G2 disguised sequence; no-separate-triple proposal stands for Hamid.

## REL-00129 [Refining] PROMOTE via B:structural-nearness
**CM-1-1-7-2-4** --enables--> **CM-1-1-7-2-5** (Measure Production Scheduling Performance)
Definition: Detect, assess, and resolve deviations from the production schedule — unit upsets, feed or quality surprises, outage changes, and demand shifts — deciding schedule responses, triggering rescheduling, and escalating deviations that break the approved plan to planning.
Scope: Covers the schedule exception rhythm: monitoring execution feedback against the schedule, assessing deviation impact, deciding and coordinating the schedule response, triggering rescheduling through Create Production Scheduling and Sequencing Plan (CM-1-1-7-2-3), escalating plan-level breaks to Refinery Planning and Optimization (CM-1-1-4), and recording exception causes for performance measurement. The operational decision to depart from the schedule for safety, reliability, or immediate process conditions belongs to Refining under the locked rule; this process manages the schedule consequenc
Tests: B:structural-nearness C:two-way-absent(back-verbs=follows)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-00140 [Refining] PROMOTE via B:structural-nearness
**CM-1-1-7-3-3** --enables--> **CM-1-1-7-3-1** (Optimize Internal vs. External Energy Sources)
Definition: Manage the refinery's emissions-allowance and credit position from the planning side — tracking emissions against allowances by program and period, forecasting surplus or shortfall from the production and energy plans, and supporting allowance purchase, sale, and banking decisions — so compliance obligations are met at the best economic outcome.
Scope: Covers allowance position management per emissions-trading program mechanics: maintaining the position by program, forecasting surplus and shortfall from schedule and energy plans, preparing the economic case for trades and banking, incorporating allowance prices into scheduling and energy decisions, and supporting compliance true-up. Excludes regulatory emissions monitoring and reporting, owned by EHS & Government Reporting under its locked rule; excludes trade negotiation and execution, owned by the trading function (Supply And Trading where modeled); excludes the financial accounting treatm
Tests: B:structural-nearness C:two-way-absent(back-verbs=informed-by)
Verdict: OK — definition/scope supports the verb and target; evidence test appropriate.

## REL-01241 [Refining] PROMOTE via A:explicit-reference
**CM-1-1-7-2** --follows--> **CM-1-1-4** (Refinery Planning and Optimization)
Definition: Develop and maintain the refinery production schedule that implements the approved monthly plan — sequencing campaigns, schedule-level unit commitments, blends, and movements over the scheduling horizon, managing schedule exceptions, and coordinating the interfaces the schedule depends on — so the plan becomes a current schedule that provides the approved basis for refinery execution.
Scope: Covers the refinery scheduling layer between planning and operations: maintaining scheduling master data, reviewing the production wheel and run lengths, creating the dated sequencing plan, managing exceptions, measuring scheduling performance, and managing interfaces to planning, operations, and engineering and maintenance. Under the approved planning-scheduling-operations hierarchy, Refining owns detailed unit-operation scheduling and all operational execution; this L4 owns the production schedule that provides the approved basis for that execution. Excludes the monthly plan itself, owned by
Tests: A:explicit-reference 
Verdict: OK — scheduling follows planning; definition directly supports the sequence.

