# Downstream petroleum process flows and relationship evidence

Research date: 2026-10-12. Purpose: support review of the held process relationships in an enterprise ontology modeled on Marathon Petroleum. This brief describes industry patterns; it does not establish MPC's internal authorities or approve workbook relationships.

## Summary

The typical downstream flow connects demand estimates, supply and refinery economics, an approved operating plan, detailed schedules, physical movements, measured actuals, commercial settlement, and accounting. Separate controls bound the decisions along that flow. APQC distinguishes demand management, supply-network evaluation, production schedules, bulk transportation, commodity trading, and commodity-position management. AspenTech describes integrated refinery planning, scheduling, plant data, and production reconciliation. These support a connected flow with feedback, rather than a universal sequence that every transaction must follow. [A1: 3.6–3.7, 4.1, 4.3–4.4; A2]

Three distinctions matter most for the held rows:

- A recommendation helps its recipient decide. It does not grant authority or establish a maintained operating capability. The repository explicitly records this for feedstock-slate advice to refinery planning. [M1: recommendation versus enablement; PTC-002]
- An artifact consumed by another process supports an output dependency. A binding policy supports governance; a binding capacity or limit supports constraint. The same producer may supply different artifacts with different semantics. [M1: mapping answers 1–3; governed-by guard; constrained-by]
- A detected exception supports a trigger only when it invokes a named response. Routine reports, reviews, and successive steps do not establish an event-to-response link. [M1: triggers]

The supplied `worklist.csv` contains 247 distinct row IDs, rather than approximately 244: 204 enables, 19 governed-by, 15 informed-by, three precedes, three uses-input, and one each constrained-by, requires, and assures. This is a direct count of the supplied file. Examples below target its process labels and selected row IDs; they are research interpretations, not disposition changes. [W1]

### Evidence labels and limits

**Company disclosure** means a named company reported the practice in a cited filing. **Industry pattern** means the cited downstream framework or specialist source describes the flow. **Interpretation** means this brief applies the repository's predicate tests to that evidence. Proposed owners are functional roles for ontology modeling unless a filing names the owner. The cited filings do not disclose a complete responsibility matrix. [M1; A1; P1–P7]

The peer reference note was read first. Its pricing, market-data, and risk distinctions were checked against current source material where used below. All seven named peers contribute evidence. APQC's industry-specific trading and bulk-fuel elements carry more weight than its reusable marketing, finance, and product-development elements. Vendor documentation shows a supported operating pattern, not adoption by every refiner. ISDA's lifecycle paper dates from April 2012; use its artifact distinctions, not its historical adoption rates or operational deadlines. [M2; A1; A2; T1–T2]

## Predicate distinctions for the reviewing agent

All entries in this table are interpretations of the approved repository mapping. The natural-language example names producer A and recipient B; most canonical predicates run from B to A. [M1]

| Predicate | Evidence needed | Example and boundary |
|---|---|---|
| `B core:enabledBy A` | A maintains a capability, governed operating base, control, or prerequisite that makes B able to operate. Target identity must be explicit. | Maintained, validated scheduling master data may enable schedule generation. One forecast handed to a scheduler establishes a different kind of relationship. |
| `B core:informedBy A` | A supplies advice, estimates, analysis, or feedback for B's judgment. | Feedstock economics recommends a slate; the refinery planning owner accepts, modifies, or rejects it. |
| `B core:dependsOnOutputOf A` | B consumes a particular output of A. | Settlement calculation consumes actual delivered quantities from actualization. Name those quantities. |
| `B core:governedBy A` | B explicitly operates under A-owned policy, authority, rules, or approved criteria. | Trading operates under a board-approved derivative policy administered through a named control process. Monitoring alone does not prove policy ownership. |
| `B core:triggeredBy A` | A generates or detects a defined condition and invokes B's response. | A formally referred delinquency invokes collections. Ordinary credit monitoring is insufficient without the referral condition. |
| `A core:precedes B` | Evidence establishes ordering within a defined workflow. | In a particular physical trade, scheduling occurs before delivery actualization. Preserve transaction scope and exceptions. |
| `B core:requires A` | B cannot validly start, proceed, or reach its controlled state without A or A's condition. | Credit clearance or collateral is required for a credit-controlled trade path. This does not require that path for prepaid business. |
| `B core:constrainedBy A` | A supplies a binding restriction on B's feasible choices. | Approved credit exposure limits bound an order's releasable value; tank capacity bounds a movement plan. |
| `B core:assuredBy A` | A performs defined verification, reconciliation, quality checking, control testing, or oversight over B or its outcomes. | A confirmation check verifies captured trade terms. Documents supplied to a checker do not themselves assure the trade. |

The mapping prohibits promotion based only on similar labels, hierarchy proximity, or a plausible industry connection. It also prohibits remapping an existing source verb at emission. Industry evidence can support a proposed source correction or author clarification; it cannot establish which workbook target an ambiguous sentence meant. [M1: unique-candidate rule; hierarchy non-duplication; no emission-time remapping]

## Planning and scheduling

### Typical flow and handoffs

The following table describes an industry pattern and proposes functional decision owners. Predicate conclusions are interpretations. It separates the economic recommendation, approved planning basis, detailed movement schedule, and execution record. [A1: 4.1.1–4.1.7, 4.3.1–4.3.2, 4.4.2, 4.4.5–4.4.6; A2]

| Process | Output and consumer | Decision role and relationship implication |
|---|---|---|
| Demand forecasting | Baseline and consensus demand estimates; revisions and accuracy measures feed supply and production planning. Promotions and sales histories contribute evidence. | Sales/marketing participate in consensus forecasting. Analysis informs the forecasting owner; a published forecast consumed by planning is an output dependency. Forecasting-process master data may be an enabling base when explicitly maintained for that function. [A1: 3.4.1, 4.1.2] |
| Supply-network and regional optimization | Inventory targets, identified long/short positions, transport alternatives, costs of supply, and proposed sourcing/distribution balances. | The supply-planning role selects a feasible network plan. Cost-to-serve analysis informs that choice. Available inventory and capacities bound it; current stock records are inputs. Trading can cover a shortage or place excess after the decision. [A1: 3.6.2–3.6.3, 4.1.3, 4.1.6, 4.4.2] |
| Refinery planning and optimization | Economic feedstock, product, and production alternatives from an LP model; an approved plan supplies the scheduling basis. Crude assays and calibrated plant models are planning inputs. | The refinery planning owner chooses the plan under the enterprise's actual authority rules. Specialist software supports the economics; it does not assign that authority. In this repository, supply and trading advises while refinery planning decides. [A2; M1: PTC-002] |
| Production scheduling | Detailed timing, quantities, resource assignments, and released production instructions translate a planning basis into executable work. | The scheduling role resolves the detailed schedule with operations. APQC distinguishes generating schedules from executing them. A schedule is consumed by execution; infrastructure/model maintenance can enable scheduling; operational capacity constrains it. [A1: 4.1.5, 4.3.1–4.3.2; A2] |
| Inventory replenishment | Destination requirements, consolidation at source, replenishment proposals, dispatch/load plans, and resulting orders. | The supply/distribution role chooses the replenishment and dispatch plan. Inventory targets govern or constrain its choices when approved and binding; inventory observations and forecasts are inputs. Replenishment performance informs policy review. [A1: 4.1.3.1, 4.1.6, 4.4.6] |
| Physical distribution scheduling | Nominations and schedules for pipeline, truck, rail, barge, tanker, and berth movements; execution produces shipment records and carrier documents. | The logistics/scheduling role coordinates the movements within transport contracts and physical capacity. An arrival plan is an input to movement preparation; the completed delivery supplies actualization data. [A1: 4.4.2] |
| Energy and utility management | A support-utilities strategy and supply/availability basis for gas, electricity, steam, hydrogen, and other utilities, whether generated internally or purchased. | The planning/operations role determines the feasible production path within that utility basis. A supply capability can enable operations; a specific energy-balance estimate is an input or advice; a shortage bounds execution. These are proposed semantic distinctions, not a disclosed universal organization chart. [A1: 4.1.1, 4.1.1.10; A2] |

LP means linear programming in refinery planning. AspenTech explicitly describes LP models, feedstock and product optimization, assays as inputs, and calibration to plant data. Its integrated application connects planning, scheduling, live operating constraints, production reconciliation, and model recalibration. Do not infer that every site uses the same horizon, planning cadence, or solver. [A2]

AspenTech's scheduling page explicitly describes turning optimal plan results into feasible schedules, using scheduler knowledge, and linking planning and scheduling models. Its crude-scheduling description identifies receipt, tank transfers, and crude-distillation-unit feed schedules. This supplies concrete schedule artifacts beyond a generic planning-to-execution label. It supports planning outputs feeding scheduling and operating constraints bounding scheduling; the software description does not establish who approves the final schedule. [A2: Unified scheduling; Crude schedule optimization]

### Peer evidence and implications

**Company disclosure:** Valero buys crude and other feedstocks through term and spot contracts, with market-related prices. PBF describes refinery-specific pipeline, waterborne, rail, and truck access, and short-term/spot supply arrangements. These establish that a commercially attractive slate must also fit the refinery's supply access. They do not establish that trading owns refinery operating decisions. [P1: Item 1, Feedstock supply; P3: Item 1, refinery descriptions, Feedstocks and supply arrangements]

**Company disclosure:** CVR defines economic capacity by crude/feedstock costs, product values, regulatory compliance costs, and downstream-unit constraints. It describes differing crude-processing capabilities at Coffeyville and Wynnewood. This supports distinguishing economic planning recommendations from binding physical constraints. [P6: Glossary, Capacity; Item 1, Petroleum segment]

**Company disclosure:** Delek says its refineries depend on its logistics segment for substantial parts of crude supply and refined-product distribution networks. PBF describes logistics assets receiving, handling, storing, and transferring material under fee-based agreements. These support genuine logistics capabilities and contractual handoffs; a broad logistics-to-refining label still needs an identified capability and target. [P5: Item 1A, logistics dependence; P3: Item 1, Logistics]

**Interpretation for held rows:**

- `Recommend Feedstock Slate And Run Rate` to `Refinery Planning and Optimization` is the standing advice-versus-decision example. Identify the recommendation as advice unless evidence gives it a binding role. [W1; M1: REL-00445; A2]
- `Manage Lot/Batch Inventory` to `Perform Inventory Reconciliation` should identify the inventory records being checked. Supplying those records is an output handoff; comparing records against measured physical stocks is assurance over the records. [W1: REL-00044; A1: 4.4.5.5]
- `Develop Finished Product Inventory Policy` to `Manage Inventory Replenishment` may express governance through approved inventory targets. In the reverse direction, replenishment results inform policy revision; reciprocal enablement requires independent capability evidence in each direction. [W1; A1: 4.1.3.1, 4.1.6; M1]
- `Energy & Utility Management` or `Optimize Plant Energy Balance` to `Daily Execution Planning` needs an artifact or restriction. Utility availability, an energy-balance estimate, and a recommendation to change the utility mix have different meanings. [W1; A1: 4.1.1.10; A2; M1]
- `Distribution Backcasting` can consume actual inventory/movement records and compare the realized distribution with the plan. APQC supports inventory reconciliation and monitoring dispatch attainment, but does not independently identify this workbook label or all of its target relationships. [W1; A1: 4.1.6.8, 4.4.5.5; M1]

## Supply and trading

### Acquisition, asset optimization, and strategy

**Industry pattern:** APQC separates defining trading objectives, developing and testing candidate strategies, and selecting a strategy. Opportunity evaluation then seeks value consistent with the strategy and within capital-allocation and risk limits. Execution selects counterparties, establishes terms, obtains credit clearance or collateral, confirms terms, and communicates them to operations for fulfillment. [A1: 3.6.1–3.6.3]

**Interpretation:** Forecasts, asset optimization, supply-network economics, and credit/market analyses inform strategy selection. The selected strategy and approved limits become governing criteria for opportunity evaluation. An approved trade supplies contractual inputs to operations. None of these handoffs transfers the recipient's decision authority to the analyst or trade recorder. [A1: 3.6.1–3.6.3; M1]

**Company disclosure:** Phillips 66 describes moving physical commodities to more profitable locations, storing them to capture seasonal/time premiums, and blending to capture quality upgrades. It uses derivatives to balance physical systems, meet customer needs, manage transaction exposures, and conduct limited trading outside its physical business. This supports asset-linked trading and several optimization choices, rather than a single strategy-to-trade chain. [P2: Note 19, Commodity derivative contracts; Item 7A]

**Company disclosure:** CVR's Gunvor arrangement supplies crude and intermediation logistics to reduce inventory held at certain locations and mitigate pricing risk. Par Pacific's Citi arrangement finances and holds title to certain crude inventories, while the inventory remains on Par's consolidated balance sheet under its accounting treatment. Delek also describes inventory intermediation and an obligation to repurchase inventories. Financing, physical custody, legal title, economic exposure, and accounting recognition therefore need separate artifacts and conditions. Do not equate title transfer with physical delivery or a journal posting. [P6: Note 14, Crude oil supply agreement; P7: Note 13, Inventory financing agreements; P5: Item 1A, Inventory intermediation; M1]

### Trade lifecycle

This is an industry pattern for physical and financial commodity trades, with conditional branches. ISDA distinguishes capture, controls processing, settlement, options, collateral, close-out, and maturity. APQC adds the physical-operation handoff. ION describes integrating trade, risk, physical data, invoicing, settlement, and journals. The following role allocation is a modeling interpretation of those sources. [T1: Section II; T2; A1: 3.6.3, 4.4.2]

| Stage | Artifact and handoff | Predicate implication |
|---|---|---|
| Contract/transaction negotiation | Agreed counterparty, quantity, product/quality, location, price or formula, delivery period, and payment terms. Trader/commercial owner agrees within delegated authority. | Contracts supply terms to capture, confirmation, operations, and settlement. Authority and limits govern or constrain the decision. [A1: 3.6.3; T1: Section II.1–3] |
| Trade capture | A recorded transaction becomes the common source for position, risk, confirmation, collateral, and finance processing. | Those consumers depend on captured trade outputs. Risk policy does not become enablement merely because the capture system checks limits. [T1: Section II.1; M1: enablement is not reciprocal] |
| Confirmation and disputes | The counterparty or broker validates agreed terms against recorded terms. Discrepancies require correction at capture and may require revised confirmations or invoices. | Verification may assure capture accuracy. A discrepancy is a trigger only when routed into a defined correction/dispute workflow. Confirmation records are inputs to later checks. [T1: Section II.1–2] |
| Scheduling/nominations | Physical trades generate logistics instructions and booked transport movements. Financial-only trades do not need a physical shipment. | Operations consumes agreed deal terms. A transport contract may enable access or constrain nominations. Do not impose shipping on financial settlement. [A1: 3.6.3.5, 4.4.2; T1: Section II.3] |
| Actualization and inventory reconciliation | Measured delivery quantities replace or reconcile nominated/contract quantities; records support stock and settlement calculations. | Settlement depends on actualized quantities when used. Reconciliation assures quantity records. Forecast arrivals are not actual delivery evidence. [T1: Section II.3; A1: 4.4.5.5] |
| Settlement/invoicing | Contract prices/formulas, quantities, costs, and applicable adjustments produce payable/receivable amounts. Some trades use provisional invoices and later true-ups. | Consumption of terms, actuals, and prices is an output dependency. An unresolved discrepancy can invoke exception handling; an undisputed amount can still be paid under the applicable arrangement. [T1: Section II.3; T2] |
| Accounting and close | Journal entries, accruals, subledger balances, and general-ledger outputs support financial reporting and reconciliation. | Accounting consumes transaction and settlement data. A maintained chart/system base can enable posting, but one posting or close feed is an output dependency. A period deadline is a cadence unless evidence specifies a triggering event. [T2; M1: enablement is not reciprocal] |

**Interpretation for exchanges and close-out:** Exchange obligations may involve quantity/quality/location balances and differential payments rather than ordinary gross sales. PBF explicitly describes inventory-exchange accounting and cash-settled grade/location differences. ISDA lists termination and novation as lifecycle events. A terminated or novated trade may invoke settlement recalculation, but the responsible activity and event condition must be stated; not every contract termination entails the same cash workflow. [P3: Note 17, Revenues/exchange arrangements; T1: Section II.6, Annex C; M1]

### Market, credit, and inventory risk

**Company disclosure:** Phillips 66's board approves an "Authority Limitations" document that prohibits specified derivative practices and establishes VaR limits. Its global risk group monitors compliance daily. Valero's risk-control group monitors and manages commodity-derivative positions daily under a risk policy periodically reviewed with the board or a relevant committee. These are disclosed controls; they do not prove the risk group owns all trading-strategy decisions. [P2: Item 7A; P1: Item 7A]

**Company disclosure:** Phillips 66 reviews counterparty payment ability, expected billing exposure, payment timing, ratings or financial statements, contract terms, country/political risk, and business strategy. It establishes a counterparty credit limit from that review and may require collateral or prepayment. This supports analysis feeding a limit decision and a limit constraining exposure. It does not establish that every analyst can approve the limit. [P2: Note 7, Credit losses]

**Industry pattern:** APQC separates commodity-position management from executing trades, explicitly citing separation of duties. It includes volumetric positions, supply-plan monitoring, daily mark-to-market profit/loss, and pricing-exposure reports. [A1: 3.7, 3.7.1–3.7.3]

**Interpretation:** A risk scenario or advanced credit analysis usually informs limit selection; an approved limit then constrains eligible transactions. A risk report informs strategy and oversight, while a compliance check may assure adherence to policy. A breach can trigger escalation only if the process definition names the breach and response. Inventory positions inform trading decisions and enter exposure calculations; stock availability can also constrain physical delivery. Keep the record, the limit, and the escalation event separate. [A1: 3.6.2, 3.7; P1: Item 7A; P2: Item 7A, Note 7; M1]

This distinction is directly relevant to `Conduct Advanced Risk Analytics` and `Manage And Run Risk Scenarios` feeding `Manage Risk Limits`, `Market Risk Management` paired with `Trade Capture`, and `Manage Risk Reporting` feeding `Trading Strategy Management`. Reports and recommendations do not become prerequisites merely because decisions benefit from them. [W1; M1: recommendation rule, enablement is not reciprocal; A1: 3.6.1–3.7]

### Trading compliance, RINs, emissions, and tax

**Regulatory requirement:** CFTC Part 45 distinguishes swap creation reporting, lifecycle/continuation reporting, recordkeeping, and determination of the reporting counterparty. A dealer can be the reporting party when its counterparty is a commercial end user; other counterparty combinations follow different rules. Therefore, a generic physical trade-capture activity does not prove a refinery must send every trade or confirmation to a swap data repository. Determine instrument and party status first. [R1: §§45.2–45.4, 45.8]

**Interpretation:** A reportable swap execution or lifecycle event can invoke a required reporting workflow. The captured record supplies data; the legal rule governs the obligation; the defined event triggers the report. `Report Trades to SDR` followed by `Report Confirmation To SDR` requires current, applicable rule and workflow evidence. The labels alone do not establish two separate obligatory reports or their ordering. [W1; R1; M1]

**Regulatory requirement:** FERC's anti-manipulation rule applies to jurisdictional natural-gas or electric-energy transactions and associated transportation/transmission services. A downstream enterprise's gas or power activity can therefore have a distinct compliance scope. Do not extend that stated rule automatically to every gasoline rack sale. [R2: 18 CFR §§1c.1–1c.2]

**Regulatory requirement:** EPA describes RIN generation, assigned/separated RIN trading, and retirement for compliance. Refiners and gasoline/diesel importers are obligated parties. Trading partners agree outside EMTS, enter separate buy/sell records, and EMTS transfers RINs after matching and a quality check. RIN accounts distinguish D-code and vintage. [R3: RIN lifecycle; Market participants; RIN transactions in EMTS]

**Company disclosure:** PBF's RIN obligation depends on EPA percentages and domestic shipments of on-road fuels. If blending does not satisfy the obligation, it buys RINs. PBF separately describes the environmental-credit liability and use of derivatives to address certain exposures. This ties physical activity, compliance quantities, acquired credits, and accounting outputs without making them the same process. [P3: Item 7A, Environmental credits; Note 2, Renewable energy credit and emissions obligations]

**Interpretation:** Renewable forecasts inform prospective obligation and procurement planning; measured production/blending/shipment records feed actualization and compliance calculations. A validated transaction base can enable accurate account maintenance. A RIN trade event invokes the applicable EMTS workflow; the regulation governs it. A report can inform compliance-policy review, but the report does not acquire authority to change policy. RINs, renewable-energy certificates, and emissions allowances require separate scheme-specific evidence. APQC separately models carbon-certificate positions; EPA's cited RIN rules do not establish the other schemes' lifecycle. [W1: Forecast Renewables, Perform RINs/REC Actualization, Manage RINs Reporting; R3; A1: 3.7.4; M1]

**Interpretation for energy/emissions optimization:** Carbon-position and cost data can inform the internal-versus-external energy choice. A binding permit, cap, or allowance requirement can constrain it. Merely trading allowances does not establish that an emissions-trading activity owns energy-sourcing decisions. [W1; A1: 3.7.4, 4.1.1.10; M1]

**Company disclosure:** Valero describes tariff impacts on renewable feedstocks, changes to feedstock slates, use of free-trade zones, and duty-drawback claims. Tax/customs consequences can affect sourcing economics and generate claim-processing work. This does not show that tax compliance owns the refinery slate decision. Commercial indirect-tax determination, master data, billing, and tax reporting are treated in the next section. [P1: Item 7, trade-policy discussion]

## Commercial and marketing

### Wholesale, branded marketing, pricing, and sales

**Company disclosure:** Valero sells wholesale through a rack network to wholesalers, distributors, retailers, and truck-delivered end users. HF Sinclair distinguishes sites supplied with branded fuel from additional sites paying Sinclair licensing fees. A brand licence and a fuel-supply contract therefore describe different commercial relationships. Neither disclosure establishes that the refiner operates the retailer or owns all of its pricing decisions. [P1: Item 1, Marketing; P4: Item 1, Marketing operations]

**Industry pattern:** APQC separately names wholesale/rack fuel pricing, retail fuel pricing, wholesale/retail distribution strategy, direct-supply strategy, and wholesale/rack account management. The last includes lifting agreements, qualified truck transport, and rack clearances. These downstream-specific elements support separate channel and delivery-mode handoffs. [A1: 3.3.3.1–3.3.3.2, 3.4.2.7.1–3.4.2.7.2, 3.5.3]

**Company disclosure:** Phillips 66's revenue policy distinguishes fixed and variable transaction prices, including market-index pricing. CVR describes bulk sales at spot prices with a Group 3 basis differential to NYMEX prices and other adjustments reported by price indices. Commercial pricing can therefore consume a contractual formula and quotations; the process that maintains market data need not own commercial pricing. [P2: Note 1, Revenue recognition; P6: Item 1, Petroleum product marketing]

**Interpretation:** Competitive intelligence and profitability analysis inform price strategy. Approved commercial policy and delegated authority govern offers. A configured price/formula is an output consumed by quotation, order processing, or billing. Maintaining validated price/discount data can enable those capabilities, while a particular rebate calculation is a transactional input. Sales planning supplies targets and account plans; sales execution pursues opportunities within those terms. Analytics can recommend changes without owning price approval or the customer commitment. [W1: Analyze Pricing Performance, Implement sales price, Maintain Price & Discount Master Data, Sales Planning; A1: 3.3.3, 3.4–3.5; P2: Note 1; M1]

### Fuel order-to-cash and credit

**Industry pattern:** APQC separates receiving orders, maintaining customer/account information, checking availability and fulfillment, processing adjustments, and tracking delivery/invoicing. The reusable flow connects approved account and terms, accepted order, fulfillment, delivery evidence, invoice, payment, and receivables handling. Channel-specific contracts can change the sequence or billing basis. [A1: 3.5.5; P2: Note 1; P4: Note 1, Revenue recognition]

**Company disclosure:** HF Sinclair recognizes refined-product, excess-crude, and RIN revenue when delivery by pipeline, in-tank, or rack transfers control, typically when title passes and the customer is billed. Revenue excludes taxes billed to customers. Some lubricant distributor/marketer contracts have return or repurchase provisions that can defer recognition until end-customer sales. Consequently, an invoice, physical movement, title transfer, and revenue recognition are related but distinct events. [P4: Note 1, Revenue recognition]

**Company disclosure:** Phillips 66's aviation application asks for legal identity, tax/exemption information, consumption estimates, authorized aircraft, contacts, pricing-delivery preferences, a portal administrator, and payment arrangements. Phillips 66 approves the account before listing it at eligible fueling locations and provides access to transaction invoices. This is a concrete commercial-channel example of prerequisites and master-data handoffs, not a universal wholesale onboarding rule. [C1: Company information; Aircraft and consumption details; Contact information; Payment method; Payment terms]

| Handoff | Output, owner, and relationship interpretation |
|---|---|
| Commercial terms to order acceptance | The commercial owner agrees product, price/formula, payment, and delivery terms. Order management consumes these terms; delegated authority governs commitment. [A1: 3.5.4–3.5.5; C1; M1] |
| Credit assessment to limit/release | Credit evidence informs the authorized credit decision. An approved limit constrains exposure; a mandatory clearance is a prerequisite for the credit-controlled path. [P2: Note 7, Credit losses; A1: 3.6.3.3; M1] |
| Accepted order to fulfillment | Product, quantity, location, and timing feed fulfillment. Order acceptance is a trigger only where the workflow invokes fulfillment on acceptance. [A1: 3.5.5; M1] |
| Delivery to invoice | Quantity and contract/control-transfer evidence feed billing. The applicable contract determines whether delivery invokes billing, provisional billing, or another path. [P4: Note 1; T1: Section II.3; M1] |
| Invoice/payment to receivables | Invoice and remittance records supply receivables balances and matching data. Corrections or credit memos alter balances; a maintained receivables capability is different from those individual records. [A1: 9.2.2–9.2.4, generic finance support; C1; M1] |
| Dispute/delinquency to follow-up | A disputed item supplies evidence for investigation. Formal referral can invoke collections; a threshold or referral rule must identify the event and recipient. [W1: Manage Receivables Disputes, Manage Card Delinquency and Collections Referral; M1: triggers, REL-00897; C2] |

**Generic support:** SAP describes credit checks on orders/deliveries, alerts or blocks, and a responsible credit manager's release/cancellation decision. This illustrates how a measured exposure, a binding limit, a blocking event, and an authorized exception decision differ. It does not prove any peer uses that product or workflow. [C2]

### Tax determination and commercial master data

**Generic support with a downstream example:** SAP distinguishes tax codes/rates, calculation procedures, account keys, plant location, customer/material tax classifications, and validity dates. Phillips 66's aviation application states that applicable taxes are billed absent proper exemption information. This supports separating the classification base, the transaction-level tax determination, invoice outputs, and ledger/reporting records. [C3; C1: Company information]

**Interpretation:** Tax rules govern determination; customer/product/location classifications are inputs; maintained validated classifications may enable automated determination. The calculated tax feeds the invoice. Billing and actual taxable transactions feed reconciliation/reporting. A taxability decision can produce a master-data update, but a transaction calculation that reads existing classifications should not be reversed into ownership of master data. `Determine Taxability` to `Maintain Tax Master Data` needs the source definition to specify whether it establishes reusable classifications or merely reads them. [W1; C3; M1]

Commercial workflow configuration is an operating capability when it maintains valid execution rules. Approved policy parameters govern it; customer/product/price records feed individual transactions. `Maintain Commercial Policy Content and Approved Parameters` should not be conflated with the stewardship that records them. Decision approval, implementation, and data maintenance need separately named outputs and authority. These are modeling interpretations, supported by the application inputs and configured credit/tax controls. [W1; C1–C3; M1]

### Card, fleet, and loyalty programs

**Provider-specific operational evidence:** WEX documents account, driver, and vehicle/card setup; authorization profiles; card status changes; transaction reports; exception reports; invoices; and payments. Exception reports can select transaction dates, drivers, cards, vehicles, merchants, products, and quantity/grade/multiple-purchase exceptions. These are documented fleet-provider capabilities, not an MPC disclosure. [C4: Fuel cards & drivers; Controls & reports; Billing & payments]

**Interpretation:** Maintained account/card/driver/vehicle and acceptance infrastructure can enable the fleet program. Assigned authorization profiles govern or constrain allowed purchases. Transaction records feed bills and exception analysis. An exception report informs investigation; a rule that routes suspected fraud or referred delinquency can trigger a response. Suspension changes permission state. Reporting, referral, suspension authority, collections, and allowance calculation must remain distinguishable. [C4; W1: card/fleet rows; M1: triggers, REL-00897/REL-00901]

**Generic supporting framework:** APQC separates loyalty-program definition, member acquisition, monitoring, and optimization. A member identifier links participation and purchases; monitoring compares benefits and proposes changes. Therefore, program rules and maintained member records can supply an operating base, transaction/member outputs feed program analysis, and proposed changes inform the program owner. The sources reviewed do not establish MPC's reward accrual, redemption, card-issuer, or fraud-routing design. [A1: 3.2.6; M1]

### Communications, marketing analytics, product lifecycle, and R&D

**Generic supporting framework:** APQC distinguishes audience understanding, marketing strategy, budgets, communications/promotional planning, execution, performance evaluation, and incorporating learning. Marketing and finance participate in budget development. Projected ROI supports revising budgets. This supports analysis informing budget and mix decisions; it does not assign the analyst budget authority. Approved messages, target audiences, schedules, and authorized budgets are different artifacts. [A1: 3.2, 3.3.2, 3.3.4]

**Interpretation for held rows:** Brand strategy supplies direction and approved criteria to communications and channel design when explicitly binding. Consumer, competitor, marketer, campaign-ROI, and spend analyses inform owners' decisions. A specific campaign/content plan feeds execution. A promotional calendar can feed demand forecasting as an expected demand driver; it is not an unconditional trigger for a customer sale. Reciprocal strategy/planning or analysis/value-proposition links need separate directional artifacts rather than reciprocal enablement. [W1; A1: 3.2–3.4.1; M1]

**Company disclosure:** HF Sinclair's Lubricants & Specialties innovation risk distinguishes identifying viable products, completing R&D, obtaining regulatory approvals or IP protection, commercialization, and market acceptance. Its extended development spending may never yield profitable products. This is useful evidence that technical research and market-launch decisions are different activities, especially for specialty products; it should not be generalized into an identical development path for all bulk fuels. [P4: Item 1, Lubricants & Specialties; Item 1A, competitive market and continuous product-development risk]

**Generic supporting framework:** APQC separates portfolio assessment and prioritization, lifecycle introduction/retirement and review, discovery research, technology feasibility, and product development. It involves senior management and relevant technical/operating stakeholders in selected decisions. The reviewed evidence does not establish a universal downstream stage-gate committee. [A1: 2.1.1–2.1.2, 2.2.1]

**Interpretation:** Customer/technical-service collaboration, research-partner results, and feasibility studies inform product choices or supply specific experimental outputs. Approved formulations/specifications can feed development or manufacturing. Required regulatory approval is a prerequisite for the applicable product path; IP advice or licensing rights need separate evidence. Portfolio recommendations and post-launch metrics inform product-change decisions. A maintained licensed research environment can enable research, but the existence of an IP function does not make its clearance an unconditional prerequisite for every product. [W1: R&D Collaboration, Concept & Feasibility Study, Manage Licensing & IP, Lifecycle Management; P4: Item 1A; A1: 2.1–2.2; M1]

## Governance patterns and decision rights

**Company disclosure:** Phillips 66 provides a concrete policy-owner/control distinction: the board approves derivative authority limits, and the global risk group monitors them. Valero describes board/committee review of risk policy and daily monitoring by risk control. These sources identify oversight and control mechanisms, but do not provide all transaction-approval delegations or committee charters. [P2: Item 7A; P1: Item 7A]

**Industry pattern:** APQC explicitly separates trade execution from position/risk management. Strategy objectives and risk/capital limits govern opportunity evaluation; credit clearance or collateral precedes execution in its specified trade path. ISDA distinguishes transaction capture, independent checking, and settlement activities. Together these support separating proposing, approving, recording, executing, and checking, rather than treating them as interchangeable authority. [A1: 3.6–3.7; T1: Section II]

The following are recommended relationship tests, not undisclosed company practices. [M1; P1–P2; A1: 3.6–3.7]

| Governance instrument or action | Who decides in the model | Relationship test |
|---|---|---|
| Policy, approved criteria, delegation of authority | The named policy owner or delegating authority; the delegate acts within the grant. | Identify the instrument and owner for `governedBy`. General compliance monitoring does not establish ownership. |
| Limit, allocation, operating envelope | The authorized approver establishes the limit; operating/trading roles act within it. | The limit bounds feasible choices for `constrainedBy`. Analytics that proposes it is `informedBy`. |
| Committee recommendation | The committee advises the accountable owner unless its charter grants approval authority. | Use advice semantics when the owner can reject/modify the proposal. Membership or review does not prove a veto. |
| Committee approval or required gate | The charter/delegation names the approval body and scope. | Governance concerns authority; `requires` concerns the mandatory approval condition for the stated path. Do not assert both without their respective evidence. |
| Reconciliation, confirmation, audit/control test | The checker verifies the defined activity/output; the operational owner retains its authority unless explicitly reassigned. | Defined checking supports `assuredBy`. The finding may separately inform an owner or trigger a corrective workflow. |
| Exception escalation | A detector/referrer invokes a named response; an authorized owner decides disposition. | Record condition, route, recipient, and response for `triggeredBy`. Invocation does not approve the eventual action. |

Supply and trading's recommendation to refinery planning is the repository's explicit decision-right boundary. Apply the same test to credit analytics versus credit-limit approval, campaign ROI versus budget allocation, product recommendations versus portfolio change, and compliance findings versus policy revision. Peer practice can corroborate that these distinctions are reasonable; the workbook definition must still identify MPC-model actors and rights. [M1: recommendation rule/PTC-002; W1; A1; P1–P2]

## Reusable relationship patterns

These are reusable interpretations of the mapping, with source-supported examples. They are not permission to replace a held row's verb. [M1]

| Pattern | Preferred semantic reading | Evidence anchor and limit |
|---|---|---|
| Analytics recommends; owner decides. | Advice supports `informedBy`; approval remains with the named owner. | Slate, risk scenarios, ROI, and feasibility analysis. [M1; A1: 3.6.1, 3.3.2, 2.2.1; A2] |
| A transaction output feeds the next calculation. | `dependsOnOutputOf`, with the consumed artifact named. | Captured terms, actual delivered quantity, quotations, invoices. [T1: Section II; T2; P2: Note 1] |
| A maintained operating base makes a function usable. | Potential `enabledBy`, bounded to the capability supplied. | Validated models, master data, card/driver configuration, transport access. Identity and capability still need source confirmation. [A1: 4.1.5.1; C1; C4; M1] |
| Policy controls conduct; a limit bounds choices. | `governedBy` for owned rules; `constrainedBy` for binding restrictions. | Board derivative policy and VaR limits. [P2: Item 7A; M1] |
| A controlled path cannot proceed without clearance. | `requires`, with path and condition specified. | Credit clearance/collateral in APQC's spot-trade path. [A1: 3.6.3.3; M1] |
| Monitoring detects; formal routing invokes a response. | Report content may inform; a specified routed condition supports `triggeredBy`. | Capture discrepancies, suspected fraud, referred delinquency. [T1: Section II.1–2; M1: triggers] |
| A check verifies an output. | `assuredBy` when the source performs defined checking. | Confirmation validates terms; reconciliation compares book/physical inventories. [T1: Section II.2; A1: 4.4.5.5; M1] |
| Work occurs in order on one transaction. | Scoped `precedes`; sequence does not independently prove enablement. | Scheduling before physical delivery actualization; financial-only trades take another path. [A1: 4.4.2; T1: Section II.3; M1] |
| Actual performance feeds a later planning cycle. | Feedback generally informs the next decision; actual-data consumption may be an output dependency. | Forecast accuracy, plan/actual reconciliation, dispatch attainment. Specify cycle and artifact. [A1: 4.1.2.9, 4.1.6.8; A2; M1] |
| A report demonstrates compliance; policy authorizes conduct. | Reporting outputs can inform oversight; checking may assure compliance; policy governs. | RIN transactions/retirement, risk exposure reports, compliance review. Reports do not automatically govern their policy owner. [R3; A1: 3.7; P1–P2; M1] |
| Parent and child share a label or domain. | Hierarchy alone establishes no independent semantic edge. | A target-owned rule, artifact, control, or external capability must be evidenced separately. [M1: hierarchy non-duplication] |
| Two functions exchange information. | Each direction can independently support `informedBy`; reciprocal output dependencies or enablement need stronger evidence. | Strategy/performance and policy/analytics feedback. The repository blocks unreviewed reciprocal `dependsOnOutputOf`. [M1: no-two-cycle and recommendation rules] |

### Questions to apply to each held row

1. Identify the exact source and target activities from author-backed identifiers or explicit references. Industry similarity alone cannot resolve the target. [M1]
2. Name the artifact, maintained capability, binding rule, required condition, verification task, or invoking event. If none is specified, retain the ambiguity. [M1]
3. Identify who proposes, approves, records, executes, and checks. Preserve the recipient's decision rights. [M1; A1: 3.6–3.7; P1–P2]
4. State the transaction/channel/path and any exception, such as credit-controlled versus prepaid, physical versus financial, fuel-supplied versus brand-licensed, or provisional versus final billing. [A1: 3.6.3; P4: Item 1/Note 1; T1: Section II.3]
5. Separate research-supported correction proposals from existing author evidence and approvals. Do not promote, retarget, or remap merely because a proposed relationship fits industry practice. [M1]

## Sources

Sources were read or retrieved on 2026-10-12. Filing dates below follow the peer reference catalog, corroborated by the filing/index or signed report where inspected. Section references in the prose locate the particular claim. Saved web extracts and search results are in the current folder's `.firecrawl/`; commercial supporting extracts are in `/private/tmp/.firecrawl-commercial/`. No repository files were changed. [M2]

### Repository and downstream framework

- **W1.** The research worklist supplied with the brief (not saved in the repository). The approved answers drafted from this research are in [register.csv](register.csv), a separate file. Counts and process labels are direct observations, not source claims about industry practice.
- **M1.** [Verb-predicate mapping v2](../../verb-predicate-mapping-v2.md), approved 2026-09-29 with recorded updates through 2026-10-12. Sections: mapping answers; enablement; recommendation rule; governed-by guard; assured-by scope; constrained-by; triggers; hierarchy and identity gates.
- **M2.** [Pricing, market-data, and price-risk peer evidence](../../../../reference/downstream-peers/pricing-market-data-risk-evidence.md), draft 2026-09-29. Used first as a source locator and domain-distinction reference, not as a substitute for filings.
- **A1.** APQC, [Petroleum Downstream PCF v7.2.2 workbook](../../../../reference/APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx). Cover says generated 2025-05-19; repository catalog dates release 2025-05-30. Cited numbers are hierarchy IDs. Stable PCF IDs include 12908 for 3.6, 12953 for 3.7, 12899 for 4.1.3, 12923 for 4.4.2, and 19611 for 4.4.5.5. Generic marketing, product, and finance content is explicitly supporting evidence. Extraction: `.firecrawl/apqc-local.txt`. [APQC overview](https://www.apqc.org/pcf).
- **A2.** AspenTech, [Refinery planning](https://www.aspentech.com/en/applications/msc/refinery-planning), [Unified planning and scheduling](https://www.aspentech.com/en/products/msc/aspen-unified-for-downstream-planning-and-scheduling), [Unified scheduling](https://www.aspentech.com/en/products/msc/aspen-unified-scheduling), and [Crude schedule optimization](https://www.aspentech.com/en/resources/data-sheet/aspen-unified-scheduling---crude-schedule-optimization), undated product pages retrieved 2026-10-12. Sections on LP/assays, plan/actual/model calibration, feasible schedules, receipts/tank transfers/unit feeds. Sources: `.firecrawl/planning.json`, `.firecrawl/schedule-find.json`. Vendor evidence; no claimed universal adoption.

### US refining-peer SEC disclosures

| ID | Filing and date | Sections used |
|---|---|---|
| P1 | Valero Energy, FY2025 Form 10-K, filed 2026-02-25, accession 0001628280-26-011499. [SEC filing](https://www.sec.gov/Archives/edgar/data/1035002/000162828026011499/vlo-20251231.htm) | Item 1, Feedstock supply/Marketing; Item 7, trade policy; Item 7A, Commodity price risk. Extract `.firecrawl/peers0.md`. |
| P2 | Phillips 66, FY2025 Form 10-K, filed 2026-02-20, accession 0001534701-26-000006. [SEC filing](https://www.sec.gov/Archives/edgar/data/1534701/000153470126000006/psx-20251231.htm) | Item 7A, derivatives/Authority Limitations; Note 1, Revenue recognition; Note 7, Credit losses; Note 19, Derivatives and financial instruments. Extract `.firecrawl/psx250.md`. |
| P3 | PBF Energy, FY2025 Form 10-K, filed 2026-02-12, accession 0001534504-26-000010. [SEC filing](https://www.sec.gov/Archives/edgar/data/1534504/000153450426000010/pbf-20251231.htm) | Item 1, refinery supply/logistics; Item 7A, Environmental credits; Note 2, environmental-credit accounting policy; Note 17, exchange arrangements. Extract `.firecrawl/pbf25.md`; index in `.firecrawl/pbf0.md`. |
| P4 | HF Sinclair, FY2025 Form 10-K, filed 2026-02-27, accession 0001915657-26-000016. [SEC filing](https://www.sec.gov/Archives/edgar/data/1915657/000191565726000016/dino-20251231.htm) | Item 1, Marketing/Lubricants & Specialties; Item 1A, customer credit and continuous product-development risks; Note 1, Revenue recognition. Extract `/private/tmp/.firecrawl-commercial/hf.json0.md`. |
| P5 | Delek US Holdings, FY2025 Form 10-K, filed 2026-02-27, accession 0001628280-26-012664. [SEC filing](https://www.sec.gov/Archives/edgar/data/1694426/000162828026012664/dk-20251231.htm) | Item 1A, logistics dependence, inventory intermediation and liquidity; accounting policy, receivables/credit assessment. Extract `.firecrawl/delek25.md`. |
| P6 | CVR Energy, FY2025 Form 10-K, filed 2026-02-18, accession 0001376139-26-000014. [SEC filing](https://www.sec.gov/Archives/edgar/data/1376139/000137613926000014/cvi-20251231.htm) | Glossary, Capacity; Item 1, Petroleum segment/refinery capabilities/product marketing; Note 14, Commitments and contingencies, Crude oil supply agreement. Extract `.firecrawl/cvr0.md`. |
| P7 | Par Pacific, FY2025 Form 10-K, filed/signed 2026-02-25, accession 0000821483-26-000005. [SEC filing](https://www.sec.gov/Archives/edgar/data/821483/000082148326000005/parr-20251231.htm) | Note 13, Inventory financing agreements; Note 16, Derivatives; Note 17, Fair value measurements. Extract `.firecrawl/par25.md`. |

### Trading and regulatory sources

- **T1.** ISDA, [Commodities trade processing lifecycle events](https://www.isda.org/a/ReiDE/commoditieslifecycleevents-april-25.pdf), April 2012. Section II on capture, controls and settlement; Section II.6/Annex C on close-out/novation; physical actualization and provisional settlement discussed in Section II.3. The URL's filename is not its publication year. Saved `.firecrawl/ctrm2.md`. Broader commodities support, not refinery-specific authority evidence.
- **T2.** ION Commodities, [Financial managers and controllers](https://iongroup.com/who-we-serve/commodities/financial-managers-and-controllers/), undated, retrieved 2026-10-12. Sections on trade/risk/physical data integration, settlement/invoicing, accounting treatment, journal generation, and financial reporting. Saved `.firecrawl/ctrm1.md`. CTRM vendor evidence.
- **R1.** CFTC regulations, [17 CFR Part 45](https://www.ecfr.gov/current/title-17/chapter-I/part-45), retrieved current-text page 2026-10-12; §§45.2–45.4 and 45.8. CFTC [rulemaking register](https://www.cftc.gov/LawRegulation/DoddFrankAct/Rulemakings/DF_17_Recordkeeping/index.htm) provides rule history. Saved `.firecrawl/cftc1.md`. Apply instrument/party status and current exceptions before inferring a reporting obligation.
- **R2.** FERC, [Prohibition of energy market manipulation](https://www.ferc.gov/enforcement-legal/enforcement/prohibition-energy-market-manipulation), and [18 CFR Part 1c](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-A/part-1c), retrieved 2026-10-12. §§1c.1–1c.2 identify jurisdictional gas/electricity and related services. Saved `.firecrawl/ferc0.md` and `ferc1.md`.
- **R3.** EPA, [RINs under the Renewable Fuel Standard](https://www.epa.gov/renewable-fuel-standard/renewable-identification-numbers-rins-under-renewable-fuel-standard-program), updated 2025-12-31. Sections RIN lifecycle, Market participants, and RIN transactions in EMTS. Saved `.firecrawl/rfs0.md`. The brief does not use its general deadline examples to assert current-year deadlines or exemptions.

### Commercial operating sources and generic support

- **C1.** Phillips 66, [General aviation contract fuel application](https://www.phillips66.com/aviation/application-form/), undated, retrieved 2026-10-12. Company information; Aircraft and consumption details; Contact information; Payment method; Payment terms. First-party downstream-channel example. Extract `/private/tmp/.firecrawl-commercial/psx-ops.json1.md`.
- **C2.** SAP S/4HANA Sales, [Credit check process](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/7b24a64d9d0941bda1afa753263d9e39/4e63bf186cc943be821bc0b8be3557a6.html), retrieved 2026-10-12. Checks, blocks, and credit-manager release/cancellation. Generic ERP support. Extract `/private/tmp/.firecrawl-commercial/credit.json0.md`.
- **C3.** SAP ERP Sales and Distribution, [Tax determination procedure](https://help.sap.com/docs/SUPPORT_CONTENT/sd/3362915540.html), undated, retrieved 2026-10-12. Tax classifications, codes/rates, calculation procedure, and account keys. Generic ERP support. Extract `/private/tmp/.firecrawl-commercial/sap.json0.md`.
- **C4.** WEX, [Fleet accounts support](https://customer.wexinc.com/customer-support/customer-support-fleet-accounts/), retrieved 2026-10-12. Fuel cards & drivers; Controls & reports; Billing & payments. Provider-specific operational evidence. Extract `/private/tmp/.firecrawl-commercial/wex.json0.md`.

### Unresolved evidence boundaries

No reviewed source establishes MPC's full delegation matrix, committee charters, loyalty accounting design, or workbook target identities. APQC is a process taxonomy and contains some inherited generic descriptions; adjacency and hierarchy are not causal evidence. Web retrieval returned rate-limit errors on some attempts, followed by successful retrievals for the sources used. A guessed Aspen scheduling URL returned no useful content and was replaced by the cited current scheduling page. No failed retrieval is used as substantive evidence. The row reviewer must use source-author definitions and applicable approval records for final decisions. [M1; A1; source extracts listed above]
