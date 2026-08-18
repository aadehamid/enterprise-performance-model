# Domain Model and Ontology Pilot — Gasoline Netback CPG

**Purpose:** Define the concrete, small OWL/SHACL/RDF model and KPI specification for the Downstream O&G Knowledge Homelab capstone. It connects synthetic terminal custody events to a transparent Gasoline Netback CPG calculation while preserving relational facts as the source of record.

**Status:** Draft (personal homelab, not an EPM governed artifact)  
**Owner:** Hamid Adesokan  
**Last updated:** 2026-08-10

## Pilot scope and competency questions

This capstone is a deliberately narrow, educational analog of a downstream commercial-margin pilot. **Gasoline Netback CPG** means revenue realized per gallon of gasoline sold at the rack, less the applicable cost basis, expressed in cents per gallon. In the initial model, “revenue realized” is represented by a public rack-price proxy plus any synthetic contractual adjustment; the cost basis is a public crude-price proxy plus a synthetic transportation adjustment. It is not a financial close, tax calculation, or production margin model.

The pilot keeps the operational shape of downstream order-to-cash: a terminal releases a product through a custody ticket, a customer and contract contextualize the release, price observations supply a price basis, and a KPI specification describes the calculation. Ticket volumes and synthetic commercial fields reside in PostgreSQL. Ontop exposes those rows as virtual RDF first; RDF/OWL supplies the meaning and Neo4j Community Edition is a serving/query projection, not an independent source of truth.

The market-price references are intentionally public proxies: EIA publishes daily petroleum spot series and the Petroleum Marketing Monthly publishes refiner rack-price statistics, including a regular-gasoline rack series ([EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm); [EIA PMM rack-price reference](https://www.eia.gov/dnav/pet/pet_pri_refmg_a_epmr_prg_dpgal_m.htm)). Synthetic tickets make the custody-transfer portion safe to share and repeat.

The graph should answer these competency questions:

1. Which KPI in the homelab measures gasoline commercial-margin performance, and what business objective does it serve?
2. Which input metrics and drivers explain Gasoline Netback CPG for a terminal, product, and week?
3. Which terminal, product, customer, contract, and custody tickets supply the volume facts underlying a particular KPI result?
4. Which EIA series or synthetic data product backs each price or volume number used in the calculation?
5. What total net gasoline volume was released through a selected terminal in a given week?
6. How did Netback CPG change week over week, and which component changed: rack price, crude cost basis, transportation adjustment, or mix?
7. Which tickets fail the minimum semantic and data-quality requirements for inclusion in a KPI run?
8. Which Neo4j nodes and relationships correspond to the RDF concepts used by a graph-grounded query or agent?

The O2C process taxonomy adds the following business competency questions, each anchored to a Level 2 process:

9. **Master Data Mgmt / Maintain Customer Master:** Which customer-master records are incomplete, duplicate, or awaiting governance review before they can support an order?
10. **Quote & Sale / Establish Commercial Terms & Contracts:** Which commercial terms and contracts govern a selected customer quote or renewal?
11. **Credit & Risk / Monitor Credit Against Limit:** Which customers are at or above their assigned credit limit, by risk code?
12. **Order & Fulfillment / Allocate & Release Order:** Which validated orders can be allocated and released from a terminal, and which are blocked?
13. **Billing / Create & Distribute Bill:** What elapsed time passes from a fulfilled order to creation and distribution of its bill?
14. **Receipt / Apply Receipts:** Which received payments and remittance advices remain unapplied to open invoices?
15. **Collection / Analyze AR Aging:** What is the AR aging distribution by customer and by day-past-due bucket?
16. **Dispute / Validate Deductions:** Which deductions are valid, and what value remains unresolved by deduction reason and customer?
17. **Close / Perform Revenue Accounting:** What is the age and value of unbilled lifts awaiting revenue accounting?
18. **Ontology reasoning gate (ADR-HL-019):** Which OWL classes or property assertions in this T-Box fail an HermiT consistency or classification check, and what is the earliest pipeline stage at which that failure is caught?

Question 18 is answered by a new Dagster asset that loads this T-Box into Owlready2 and runs `sync_reasoner()` (HermiT) before Morph-KGC materializes a Turtle release, gating the release on a reported-consistent result (ADR-HL-019, `02-Tool-Selection-and-ADRs.md`). This pattern is borrowed from AWS Context Ontology Accelerator's ontology-engine reasoning step ([Owlready2 reasoning docs](https://owlready2.readthedocs.io/en/v0.51/reasoning.html); [COA GitHub repo](https://github.com/aws/context-ontology-accelerator)).

## Domain concepts (T-Box) — classes

| OWL class | One-line definition | `rdfs:subClassOf` |
|---|---|---|
| `hl:Terminal` | A physical rack/terminal location from which product is released. | — |
| `hl:Product` | A marketable petroleum product recognized by a ticket and price basis. | — |
| `hl:Gasoline` | Product family for gasoline releases in the pilot. | `hl:Product` |
| `hl:Diesel` | Product family retained to show extensibility beyond gasoline. | `hl:Product` |
| `hl:CustodyTicket` | A synthetic bill-of-lading-like record of a measured product release. | — |
| `hl:Customer` | The receiving commercial party named on a custody ticket. | — |
| `hl:Contract` | A simplified commercial agreement that can govern pricing for a release. | — |
| `hl:PriceIndex` | A named benchmark series, such as an EIA spot or PMM rack series. | — |
| `hl:PriceObservation` | A dated value observed from a `PriceIndex` and used by a calculation. | `hl:Metric` |
| `hl:KPI` | A managed performance indicator with an objective, formula, dimensions, and grain. | — |
| `hl:Metric` | A supporting numeric measure or driver used to calculate or explain a KPI. | — |
| `hl:DataProduct` | A reusable logical collection of homelab facts, such as a ticket fact table. | — |
| `hl:DataSource` | A system or publisher supplying a data product or reference series. | — |

The classes are intentionally conceptual rather than an exhaustive physical data model. `hl:CustodyTicket` represents a small subset of real O2C measurement context; this pilot uses net and gross gallons but does not model temperature correction, title transfer, tax, invoices, disputes, or settlement.

## Object and datatype properties

| Property | Type | Domain | Range | Description |
|---|---|---|---|---|
| `hl:hasTerminal` | object | `hl:CustodyTicket` | `hl:Terminal` | Associates one release with its origin terminal. |
| `hl:hasProduct` | object | `hl:CustodyTicket` | `hl:Product` | Associates a ticket with the released product. |
| `hl:hasCustomer` | object | `hl:CustodyTicket` | `hl:Customer` | Identifies the receiving customer. |
| `hl:governedByContract` | object | `hl:CustodyTicket` | `hl:Contract` | Links a ticket to its simplified contract context. |
| `hl:hasPriceObservation` | object | `hl:CustodyTicket` | `hl:PriceObservation` | Connects a release to the price observation used for its initial pricing basis. |
| `hl:sourcedFromSeries` | object | `hl:PriceObservation` | `hl:PriceIndex` | States which benchmark series supplied the observation. |
| `hl:computesKPI` | object | `hl:Metric` | `hl:KPI` | States that a metric contributes to a KPI. |
| `hl:suppliedBy` | object | `hl:DataProduct` | `hl:DataSource` | Identifies the publisher/system that supplies a data product. |
| `hl:netVolumeGallons` | datatype | `hl:CustodyTicket` | `xsd:decimal` | Net corrected release volume in gallons. |
| `hl:grossVolumeGallons` | datatype | `hl:CustodyTicket` | `xsd:decimal` | Gross observed release volume in gallons. |
| `hl:ticketTimestamp` | datatype | `hl:CustodyTicket` | `xsd:dateTime` | Timestamp at which the synthetic custody event occurred. |
| `hl:seriesIdentifier` | datatype | `hl:PriceIndex` | `xsd:string` | Publisher's stable or configured series key. |
| `hl:observedPriceUsdPerGallon` | datatype | `hl:PriceObservation` | `xsd:decimal` | Observed price basis, normalized to USD per gallon. |
| `hl:hasFormula` | datatype | `hl:KPI` | `xsd:string` | Human-readable controlled formula expression. |
| `hl:hasDimension` | datatype | `hl:KPI` | `xsd:string` | Declared reporting dimension name. |
| `hl:hasTimeGrain` | datatype | `hl:KPI` | `xsd:string` | Declared aggregation grain, initially `week`. |

## Turtle example — T-Box skeleton

The following small T-Box is intentionally usable in Protégé, RDFLib, and pySHACL workflows. It is a teaching skeleton, not a complete OWL ontology.

```turtle
@prefix hl:   <https://example.org/homelab/ontology#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

hl:Terminal a owl:Class .
hl:Product a owl:Class .
hl:Gasoline a owl:Class ; rdfs:subClassOf hl:Product .
hl:CustodyTicket a owl:Class .
hl:PriceIndex a owl:Class .
hl:PriceObservation a owl:Class .

hl:hasTerminal a owl:ObjectProperty ;
  rdfs:domain hl:CustodyTicket ; rdfs:range hl:Terminal .
hl:hasProduct a owl:ObjectProperty ;
  rdfs:domain hl:CustodyTicket ; rdfs:range hl:Product .
hl:hasPriceObservation a owl:ObjectProperty ;
  rdfs:domain hl:CustodyTicket ; rdfs:range hl:PriceObservation .
hl:sourcedFromSeries a owl:ObjectProperty ;
  rdfs:domain hl:PriceObservation ; rdfs:range hl:PriceIndex .
hl:netVolumeGallons a owl:DatatypeProperty ;
  rdfs:domain hl:CustodyTicket ; rdfs:range xsd:decimal .
hl:seriesIdentifier a owl:DatatypeProperty ;
  rdfs:domain hl:PriceIndex ; rdfs:range xsd:string .
```

## Turtle example — T-Box extension for O2C taxonomy and customer master data

This extension uses the O2C Process Taxonomy v2 (downstream O&G redline, approved 2026-08-09) as the controlled process backbone. The 10 Level 1 groups and 64 Level 2 process names below preserve the taxonomy table's wording in `rdfs:label`; the local names provide stable, Turtle-safe identifiers. A new Level 1 group, `hl:MeasureAndCustodyTransfer`, was elevated from what the underlying research treated as an Order & Fulfillment addition, per an explicit governance decision to mirror the EPM blueprint's separate "Measure/Title" chevron. The customer-domain classes are the 10 canonical entities from the Customer Data Dictionary summary.

```turtle
@prefix hl:   <https://example.org/homelab/ontology#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

hl:ProcessGroup a owl:Class ;
  rdfs:comment "A Level 1 Order-to-Cash process group." .
hl:Level2Process a owl:Class ;
  rdfs:comment "A Level 2 process belonging to one Order-to-Cash process group." .

hl:belongsToProcessGroup a owl:ObjectProperty ;
  rdfs:domain hl:Level2Process ; rdfs:range hl:ProcessGroup .

hl:MasterDataMgmt a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Master Data Mgmt" .
hl:QuoteAndSale a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Quote & Sale" .
hl:CreditAndRisk a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Credit & Risk" .
hl:OrderAndFulfillment a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Order & Fulfillment" .
hl:MeasureAndCustodyTransfer a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Measure & Custody Transfer" .
hl:Billing a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Billing" .
hl:Receipt a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Receipt" .
hl:Collection a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Collection" .
hl:Dispute a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Dispute" .
hl:Close a owl:NamedIndividual, hl:ProcessGroup ;
  rdfs:label "Close" .

hl:MaintainCustomerMaster a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Customer Master" ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainPriceAndDiscountMaster a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Price & Discount Master" ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainProductMaster a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Product Master" ;
  rdfs:comment "Extended attributes: dye status, API gravity/density defaults, UoM conversion group, RIN D-code eligibility." ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainExciseAndEnvironmentalCreditMaster a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Excise & Environmental Credit Master" ;
  rdfs:comment "Renamed from Maintain Tax Master (2026-08-09 downstream O&G redline)." ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainWorkflows a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Workflows" ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainTerminalAndLocationMaster a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Terminal & Location Master (incl. TCN)" ;
  rdfs:comment "New 2026-08-09 — TSW Location/Transport-System master objects and IRS Terminal Control Number Directory." ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainExchangePartnerMaster a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Exchange Partner Master" ;
  rdfs:comment "New 2026-08-09 — counterparties in exchange/borrow-loan agreements." ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .
hl:MaintainQuantityConversionRules a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Quantity Conversion/UoM Rules" ;
  rdfs:comment "New 2026-08-09 — QCI conversion groups, AGA/API standard routines." ;
  hl:belongsToProcessGroup hl:MasterDataMgmt .

hl:MaintainCommercialPolicies a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Commercial Policies" ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:EstablishCommercialTermsAndContracts a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Establish Commercial Terms & Contracts" ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:DefineFinancingAndPaymentMethods a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Define Financing & Payment Methods" ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:IssueQuotesAndRenewals a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Issue Quotes & Renewals" ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:DevelopAndMonitorRevenuePlan a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Develop & Monitor Revenue Plan" ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:AnalyzeCustomerProfitability a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Analyze Customer Profitability" ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:EstablishAndManageExchangeAgreements a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Establish & Manage Exchange Agreements" ;
  rdfs:comment "New 2026-08-09 — buy/sell, borrow/loan, in-lieu/LIA netting agreements (SAP EXG functional area)." ;
  hl:belongsToProcessGroup hl:QuoteAndSale .
hl:NegotiateChannelSpecificAgreements a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Negotiate Channel-Specific Agreements (DODO/CODO/Jobber)" ;
  rdfs:comment "New 2026-08-09 — retail channel-type agreements; includes carrier Access Agreements for rack lifting." ;
  hl:belongsToProcessGroup hl:QuoteAndSale .

hl:MaintainCreditPolicies a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Maintain Credit Policies" ;
  hl:belongsToProcessGroup hl:CreditAndRisk .
hl:EstablishCreditLimitAndRiskCode a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Establish Credit Limit & Risk Code" ;
  hl:belongsToProcessGroup hl:CreditAndRisk .
hl:MonitorCreditAgainstLimit a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Monitor Credit Against Limit" ;
  hl:belongsToProcessGroup hl:CreditAndRisk .
hl:ReviewCreditLimitAndRiskCode a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Review Credit Limit and Risk Code" ;
  hl:belongsToProcessGroup hl:CreditAndRisk .
hl:AnalyzePortfolioCreditRisk a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Analyze Portfolio Credit Risk" ;
  hl:belongsToProcessGroup hl:CreditAndRisk .
hl:PerformCustomerClosureAndReinstatement a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Perform Customer Closure and Reinstatement" ;
  hl:belongsToProcessGroup hl:CreditAndRisk .
hl:IssueAndManageLettersOfCredit a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Issue & Manage Letters of Credit" ;
  rdfs:comment "New 2026-08-09 — document-triggered payment assurance for large cargo transactions." ;
  hl:belongsToProcessGroup hl:CreditAndRisk .

hl:CaptureAndValidateNomination a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Capture & Validate Nomination" ;
  rdfs:comment "Renamed from Capture & Validate Order (2026-08-09) — SAP TSW nomination object: line items assigned to shipping docs, sent to partner, confirmed/rejected by carrier." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:AllocateAndReleaseOrder a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Allocate & Release Order" ;
  rdfs:comment "Extended: Stock Projection Worksheet, Location Balancing, Three-Way Pegging (SAP TSW)." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:TrackAndForecastOrder a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Track & Forecast Order" ;
  rdfs:comment "Extended: Worklist and Berth Planning Board (marine-specific scheduling)." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:ChangeCancelOrder a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Change/Cancel Order" ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:ManageTerminalLiftingAndGateOperations a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Manage Terminal Lifting & Gate Operations" ;
  rdfs:comment "Renamed from Manage Fulfillment (2026-08-09) — gate entry, vehicle pre-authorization, loading-bay assignment/queuing (Terminal Automation System scope)." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:ManageReturns a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Manage Returns" ;
  rdfs:comment "Deprioritized 2026-08-09 — low relevance for bulk fuel; retained for the lubricants channel only." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:ExecuteExchangeLifting a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Execute Exchange Lifting (Borrow/Loan)" ;
  rdfs:comment "New 2026-08-09 — physical lifting under an exchange/borrow-loan agreement rather than a standalone sale." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .
hl:AuthorizeAndFulfillIntoPlaneBunkerDelivery a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Authorize & Fulfill Into-Plane/Bunker Delivery" ;
  rdfs:comment "New 2026-08-09 — aviation into-plane pre-authorization and marine bunker delivery fulfillment." ;
  hl:belongsToProcessGroup hl:OrderAndFulfillment .

hl:PerformCustodyTransferAndQuantityQualityDetermination a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Perform Custody Transfer & Quantity/Quality Determination" ;
  rdfs:comment "New Level 1 group 2026-08-09 (elevated from an Order & Fulfillment addition per governance decision) — GOV/GSV/NSV conversion via QCI, API MPMS 11.1/ASTM D1250 volume correction." ;
  hl:belongsToProcessGroup hl:MeasureAndCustodyTransfer .
hl:IssueCustodyTransferDocumentation a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Issue Custody Transfer Documentation (Bill of Lading / Bunker Delivery Note)" ;
  rdfs:comment "New 2026-08-09 — BOL issuance; marine variant is the MARPOL Annex VI-mandated Bunker Delivery Note (BDN)." ;
  hl:belongsToProcessGroup hl:MeasureAndCustodyTransfer .

hl:CreateAndDistributeBill a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Create & Distribute Bill" ;
  hl:belongsToProcessGroup hl:Billing .
hl:PerformAccountingForSelfBilling a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Perform Accounting for Self-Billing" ;
  hl:belongsToProcessGroup hl:Billing .
hl:DetermineExciseMotorFuelTaxLiabilityAndDyeStatus a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Determine Excise/Motor Fuel Tax Liability & Dye Status" ;
  rdfs:comment "Renamed from Determine Taxability & Record Tax Liabilities (2026-08-09) — dyed vs. clear diesel, federal/state excise, RIN D-code." ;
  hl:belongsToProcessGroup hl:Billing .
hl:CreateExceptionInvoice a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Create Exception Invoice" ;
  hl:belongsToProcessGroup hl:Billing .
hl:GenerateAndReportRinCredits a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Generate & Report RIN Credits" ;
  rdfs:comment "New 2026-08-09 — EPA Renewable Identification Number generation/reporting." ;
  hl:belongsToProcessGroup hl:Billing .
hl:FileFederalAndStateMotorFuelExciseTaxReturns a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "File Federal & State Motor Fuel Excise Tax Returns (Form 720/State Equivalents)" ;
  rdfs:comment "New 2026-08-09." ;
  hl:belongsToProcessGroup hl:Billing .
hl:BillExchangePartnerNetting a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Bill Exchange Partner Netting (LIA/Borrow-Loan)" ;
  rdfs:comment "New 2026-08-09 — in-lieu/LIA and borrow-loan settlement billing." ;
  hl:belongsToProcessGroup hl:Billing .

hl:ReceivePayments a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Receive Payments" ;
  hl:belongsToProcessGroup hl:Receipt .
hl:ReceiveRemittanceAdvice a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Receive Remittance Advice" ;
  hl:belongsToProcessGroup hl:Receipt .
hl:ApplyReceipts a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Apply Receipts" ;
  hl:belongsToProcessGroup hl:Receipt .
hl:ManageUnappliedReceipts a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Manage Unapplied Receipts" ;
  hl:belongsToProcessGroup hl:Receipt .
hl:PerformReconciliationsAndSettlements a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Perform Reconciliations & Settlements" ;
  hl:belongsToProcessGroup hl:Receipt .
hl:ReconcileFuelFleetCardTransactions a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Reconcile Fuel/Fleet Card Transactions" ;
  rdfs:comment "New 2026-08-09." ;
  hl:belongsToProcessGroup hl:Receipt .
hl:ProcessLcDocumentPresentationAndBankPayment a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Process LC Document Presentation & Bank Payment" ;
  rdfs:comment "New 2026-08-09 — payment is document-triggered (SPA → LC issuance → shipment → document presentation → bank payment), not just delivery-triggered." ;
  hl:belongsToProcessGroup hl:Receipt .

hl:EstablishCollectionTargets a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Establish Collection Targets" ;
  hl:belongsToProcessGroup hl:Collection .
hl:AnalyzeARAging a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Analyze AR Aging" ;
  hl:belongsToProcessGroup hl:Collection .
hl:ExecuteCollections a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Execute Collections" ;
  hl:belongsToProcessGroup hl:Collection .
hl:NegotiateSettlements a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Negotiate Settlements" ;
  hl:belongsToProcessGroup hl:Collection .
hl:InitiateLegalAction a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Initiate Legal Action" ;
  hl:belongsToProcessGroup hl:Collection .

hl:ValidateDeductions a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Validate Deductions" ;
  hl:belongsToProcessGroup hl:Dispute .
hl:ReceiveAndValidateQueries a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Receive & Validate Queries" ;
  hl:belongsToProcessGroup hl:Dispute .
hl:CreateCreditMemoChargeBack a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Create Credit Memo/Charge Back" ;
  hl:belongsToProcessGroup hl:Dispute .
hl:PerformAppeasements a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Perform Appeasements" ;
  hl:belongsToProcessGroup hl:Dispute .
hl:DevelopRootCauseAnalysisAndActionPlan a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Develop Root Cause Analysis & Action Plan" ;
  hl:belongsToProcessGroup hl:Dispute .
hl:ManageQuantityQualityClaims a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Manage Quantity/Quality Claims (Custody Disputes)" ;
  rdfs:comment "New 2026-08-09 — bunker/rack/pipeline claims; receipt-time trigger (e.g., marine note of protest), not only post-invoice." ;
  hl:belongsToProcessGroup hl:Dispute .

hl:PerformRevenueAccounting a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Perform Revenue Accounting" ;
  rdfs:comment "Extended: two-step plant-to-plant transfer profit/loss postings; exchange-agreement accounting treatment." ;
  hl:belongsToProcessGroup hl:Close .
hl:ProcessBadDebt a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Process Bad Debt" ;
  hl:belongsToProcessGroup hl:Close .
hl:CloseARSubLedger a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Close AR Sub Ledger" ;
  hl:belongsToProcessGroup hl:Close .
hl:ReconcileExciseEnvironmentalCreditAndIndirectTax a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Reconcile Excise, Environmental Credit & Indirect Tax" ;
  rdfs:comment "Renamed from Reconcile Indirect Tax (2026-08-09)." ;
  hl:belongsToProcessGroup hl:Close .
hl:ReconcileTankSilobookStockToPhysicalInventory a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Reconcile Tank/Silo Book Stock to Physical Inventory" ;
  rdfs:comment "New 2026-08-09 — HPM silo management tank-dip vs. book-stock control." ;
  hl:belongsToProcessGroup hl:Close .
hl:CloseExchangeBalanceNettingPosition a owl:NamedIndividual, hl:Level2Process ;
  rdfs:label "Close Exchange Balance/Netting Position" ;
  rdfs:comment "New 2026-08-09." ;
  hl:belongsToProcessGroup hl:Close .

hl:Party a owl:Class ;
  rdfs:comment "A canonical real-world individual or organization that can participate in a customer relationship." .
hl:Organization a owl:Class ;
  rdfs:subClassOf hl:Party ;
  rdfs:comment "A legally or operationally recognized organization represented as a party." .
hl:Person a owl:Class ;
  rdfs:subClassOf hl:Party ;
  rdfs:comment "An individual person represented as a party." .
hl:CustomerRelationship a owl:Class ;
  rdfs:comment "A governed commercial relationship between customer-related parties." .
hl:Address a owl:Class ;
  rdfs:comment "A physical, postal, or billing location associated with a party." .
hl:ContactPoint a owl:Class ;
  rdfs:comment "An email, telephone, or other communication channel associated with a party." .
hl:CustomerRole a owl:Class ;
  rdfs:comment "A role assignment that states how a party participates in the customer domain." .
hl:Identifier a owl:Class ;
  rdfs:comment "A business, source-system, or regulatory identifier assigned to a party." .
hl:CustomerHierarchy a owl:Class ;
  rdfs:comment "A governed grouping or parent-child structure among customer parties." .
hl:GovernanceRecord a owl:Class ;
  rdfs:comment "A stewardship, approval, quality, or survivorship record governing customer master data." .

hl:Customer rdfs:subClassOf hl:Party .
hl:hasAddress a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:Address .
hl:hasContactPoint a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:ContactPoint .
hl:hasCustomerRole a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:CustomerRole .
hl:hasIdentifier a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:Identifier .
hl:hasCustomerRelationship a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:CustomerRelationship .
hl:relatesFromParty a owl:ObjectProperty ;
  rdfs:domain hl:CustomerRelationship ; rdfs:range hl:Party .
hl:relatesToParty a owl:ObjectProperty ;
  rdfs:domain hl:CustomerRelationship ; rdfs:range hl:Party .
hl:memberOfCustomerHierarchy a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:CustomerHierarchy .
hl:governedByRecord a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:GovernanceRecord .
hl:engagedInProcess a owl:ObjectProperty ;
  rdfs:domain hl:Party ; rdfs:range hl:Level2Process .
hl:roleType a owl:DatatypeProperty ;
  rdfs:domain hl:CustomerRole ; rdfs:range xsd:string .
```

## Turtle example — A-Box instance data

Two gasoline tickets make the example aggregation concrete. The price observation is a benchmark reference, not a claim that EIA price data describes a specific real terminal transaction.

```turtle
@prefix hl:  <https://example.org/homelab/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

hl:GulfDemoTerminal a hl:Terminal ;
  hl:terminalCode "GDT-01" .

hl:RegularGasoline a hl:Gasoline ;
  hl:productCode "RFG-REG" .

hl:EiaPmmRegularRack a hl:PriceIndex ;
  hl:seriesIdentifier "EPMR_PRG_DPGAL" .

hl:PriceObs2026W31 a hl:PriceObservation ;
  hl:sourcedFromSeries hl:EiaPmmRegularRack ;
  hl:observedPriceUsdPerGallon "2.145"^^xsd:decimal .

hl:Ticket1001 a hl:CustodyTicket ;
  hl:hasTerminal hl:GulfDemoTerminal ;
  hl:hasProduct hl:RegularGasoline ;
  hl:hasPriceObservation hl:PriceObs2026W31 ;
  hl:grossVolumeGallons "8020.0"^^xsd:decimal ;
  hl:netVolumeGallons "8000.0"^^xsd:decimal ;
  hl:ticketTimestamp "2026-08-03T10:15:00Z"^^xsd:dateTime .

hl:Ticket1002 a hl:CustodyTicket ;
  hl:hasTerminal hl:GulfDemoTerminal ;
  hl:hasProduct hl:RegularGasoline ;
  hl:hasPriceObservation hl:PriceObs2026W31 ;
  hl:grossVolumeGallons "12050.0"^^xsd:decimal ;
  hl:netVolumeGallons "12000.0"^^xsd:decimal ;
  hl:ticketTimestamp "2026-08-05T14:30:00Z"^^xsd:dateTime .

hl:DemoWholesaleCustomer a hl:Organization ;
  rdfs:label "Demo Wholesale Customer" ;
  hl:hasCustomerRole hl:BillToCustomerRole ;
  hl:engagedInProcess hl:ValidateDeductions .

hl:BillToCustomerRole a hl:CustomerRole ;
  hl:roleType "Bill-to customer" .
```

## SPARQL example queries

**1. Total net gasoline volume through the demo terminal during the ISO week beginning 2026-08-03.**

```sparql
PREFIX hl: <https://example.org/homelab/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?gallons) AS ?totalNetGallons)
WHERE {
  ?ticket a hl:CustodyTicket ;
          hl:hasTerminal hl:GulfDemoTerminal ;
          hl:hasProduct ?product ;
          hl:netVolumeGallons ?gallons ;
          hl:ticketTimestamp ?timestamp .
  ?product a hl:Gasoline .
  FILTER(?timestamp >= "2026-08-03T00:00:00Z"^^xsd:dateTime &&
         ?timestamp <  "2026-08-10T00:00:00Z"^^xsd:dateTime)
}
```

**2. Which tickets reference which EIA benchmark series?**

```sparql
PREFIX hl: <https://example.org/homelab/ontology#>

SELECT ?ticket ?seriesId
WHERE {
  ?ticket a hl:CustodyTicket ;
          hl:hasPriceObservation ?observation .
  ?observation hl:sourcedFromSeries ?series .
  ?series hl:seriesIdentifier ?seriesId .
}
ORDER BY ?ticket
```

**3. List the ticket volume and observed price basis used for a selected terminal.**

```sparql
PREFIX hl: <https://example.org/homelab/ontology#>

SELECT ?ticket ?netGallons ?priceUsdPerGallon
WHERE {
  ?ticket hl:hasTerminal hl:GulfDemoTerminal ;
          hl:netVolumeGallons ?netGallons ;
          hl:hasPriceObservation ?observation .
  ?observation hl:observedPriceUsdPerGallon ?priceUsdPerGallon .
}
ORDER BY ?ticket
```

## SHACL shapes example

These SHACL Core constraints establish the minimum release facts required before a synthetic ticket can participate in a KPI calculation. Run them with pySHACL as part of the RDFLib/Dagster validation step.

```turtle
@prefix hl:   <https://example.org/homelab/ontology#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

hl:CustodyTicketShape a sh:NodeShape ;
  sh:targetClass hl:CustodyTicket ;
  sh:property [
    sh:path hl:hasProduct ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:class hl:Product
  ] ;
  sh:property [
    sh:path hl:hasTerminal ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:class hl:Terminal
  ] ;
  sh:property [
    sh:path hl:netVolumeGallons ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:datatype xsd:decimal ; sh:minExclusive 0
  ] .

hl:PriceObservationShape a sh:NodeShape ;
  sh:targetClass hl:PriceObservation ;
  sh:property [
    sh:path hl:sourcedFromSeries ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:class hl:PriceIndex
  ] .
```

## R2RML / Ontop mapping sketch

The default is **virtual-RDF-first**: PostgreSQL remains authoritative for `custody_ticket`, while Ontop maps its rows into live RDF rather than copying every operational fact into a triple store. Materialize only stable, curated facts later when a Fuseki or Neo4j projection adds a clear learning or serving benefit.

```turtle
@prefix rr:  <http://www.w3.org/ns/r2rml#> .
@prefix hl:  <https://example.org/homelab/ontology#> .

<#CustodyTicketMap> a rr:TriplesMap ;
  rr:logicalTable [ rr:tableName "custody_ticket" ] ;
  rr:subjectMap [
    rr:template "https://example.org/homelab/ticket/{ticket_id}" ;
    rr:class hl:CustodyTicket
  ] ;
  rr:predicateObjectMap [
    rr:predicate hl:netVolumeGallons ;
    rr:objectMap [ rr:column "net_volume_gallons" ]
  ] ;
  rr:predicateObjectMap [
    rr:predicate hl:ticketTimestamp ;
    rr:objectMap [ rr:column "ticket_timestamp" ]
  ] ;
  rr:predicateObjectMap [
    rr:predicate hl:hasTerminal ;
    rr:objectMap [ rr:template "https://example.org/homelab/terminal/{terminal_id}" ]
  ] ;
  rr:predicateObjectMap [
    rr:predicate hl:hasProduct ;
    rr:objectMap [ rr:template "https://example.org/homelab/product/{product_code}" ]
  ] .
```

## KPI Store specification for this pilot

| Field | Pilot specification |
|---|---|
| **KPI Name** | Gasoline Netback CPG |
| **Business Objective** | Learn to trace a reproducible terminal-level commercial-margin proxy from custody volume and price inputs to a reviewed weekly result. |
| **Owner** | Hamid Adesokan (personal homelab owner). |
| **Formula** | `Netback CPG = (Rack Price − Crude Cost Basis − Transportation Adjustment) × 100`. Inputs are normalized to USD/gallon before multiplication. A future weighted result uses net-gallon weights across eligible tickets. |
| **Dimensions** | Terminal, Product, Week; optional diagnostic dimensions: Customer, Contract, Price Index, and Data Source. |
| **Time Grain** | Weekly, with daily ticket events assigned to their ISO week. PMM monthly rack values are used only as a benchmark/proxy and must be explicitly carried or allocated to the week; this is a documented simplification, not a daily rack-price claim. |
| **Target/Threshold** | Illustrative learning threshold: green at or above 20.0 CPG; amber from 10.0 to under 20.0 CPG; red below 10.0 CPG. Values are placeholders, not commercial targets. |
| **Review Cadence** | Weekly refresh and self-review after source ingestion; monthly model-quality review of assumptions, mapping, and test results. |
| **Data Sources** | EIA WTI Cushing spot proxy `PET.RWTC.D` for crude cost basis; EIA PMM/DNAV regular-gasoline rack series key `EPMR_PRG_DPGAL` for rack-price benchmark; PostgreSQL `custody_ticket` synthetic table for release volume; manual synthetic transportation adjustment. The EIA Open Data service documents petroleum data access, while PMM is the public rack-price proxy ([EIA Open Data](https://www.eia.gov/opendata/); [EIA PMM](https://www.eia.gov/petroleum/marketing/monthly/)). |
| **Measurement Classification** | **Candidate KPI.** It has a named objective, formula, dimensions, grain, illustrative thresholds, and review routine, but it is personal, synthetic/proxy-based, and lacks an enterprise accountable owner, agreed formal target, governed lineage, approval workflow, and official performance-consumption mandate. It is therefore not an “approved KPI.” |
| **Quality and lineage rule** | Include only SHACL-conformant tickets with a terminal, product, positive net volume, timestamp, and identified source/series for each price observation. Retain source retrieval timestamp and mapping version in the relational data product. |

This mirrors the discipline of a KPI Store specification without asserting that the homelab operates an enterprise KPI Store. Supporting ticket detail, observations, and diagnostic metrics remain in the data product/semantic layer; the reviewed weekly Netback CPG result is the candidate KPI output.

### O2C taxonomy-seeded KPI candidates

The following are **CANDIDATE KPIs** seeded from the O2C Process Taxonomy, not approved KPIs. Each must progress through the measurement classification path — raw measure → business measure → derived measure → operational metric → diagnostic/analytical metric → performance indicator → candidate KPI → approved KPI — and meet the stated governance criteria before it can be treated as approved.

| Level 2 process | Candidate KPI | Candidate status |
|---|---|---|
| Analyze AR Aging | DSO (Days Sales Outstanding) | Candidate only; requires an agreed formula, accountable owner, dimensions, targets, thresholds, review cadence, quality controls, lineage, and approval. |
| Create & Distribute Bill | Billing cycle time / OTIF on NSV | Candidate only; requires the same classification, definition, and approval controls. |
| Validate Deductions | Dispute-to-cash leakage rate | Candidate only; requires the same classification, definition, and approval controls. |
| Perform Revenue Accounting | Unbilled lift age | Candidate only; requires the same classification, definition, and approval controls. |
| Perform Custody Transfer & Quantity/Quality Determination | Custody transfer quantity variance (GOV vs. GSV/NSV) | Candidate only; requires the same classification, definition, and approval controls. Added 2026-08-09 with the Measure & Custody Transfer group. |
| Manage Quantity/Quality Claims (Custody Disputes) | Custody dispute rate per lifting | Candidate only; requires the same classification, definition, and approval controls. Added 2026-08-09. |

## RDF-to-Neo4j (LPG) mapping table for this pilot

Import the curated RDF projection through neosemantics (`n10s`) only after mappings and SHACL checks are stable. The table describes the intended LPG representation; exact n10s configuration determines namespace handling.

| RDF element | Neo4j equivalent | Import interpretation |
|---|---|---|
| `hl:Terminal` | node label `:Terminal` | One terminal node per terminal IRI. |
| `hl:Product`, `hl:Gasoline`, `hl:Diesel` | labels `:Product`, plus `:Gasoline` or `:Diesel` | Preserve base and subtype labels for Cypher filtering. |
| `hl:CustodyTicket` | node label `:CustodyTicket` | One node per ticket IRI. |
| `hl:Customer` | node label `:Customer` | One receiving-party node per IRI. |
| `hl:Contract` | node label `:Contract` | One simplified contract node per IRI. |
| `hl:PriceIndex` | node label `:PriceIndex` | Benchmark-series node with `seriesIdentifier`. |
| `hl:PriceObservation` | node label `:PriceObservation` | Dated price-fact node with numeric price property. |
| `hl:KPI` | node label `:KPI` | KPI-spec/result node; `hasFormula`, dimensions, and grain become properties. |
| `hl:Metric` | node label `:Metric` | Supporting input or explanatory measure node. |
| `hl:DataProduct`, `hl:DataSource` | labels `:DataProduct`, `:DataSource` | Lineage/catalog nodes. |
| `hl:hasTerminal`, `hl:hasProduct`, `hl:hasCustomer`, `hl:governedByContract` | relationships `:HAS_TERMINAL`, `:HAS_PRODUCT`, `:HAS_CUSTOMER`, `:GOVERNED_BY_CONTRACT` | Directed from `:CustodyTicket`. |
| `hl:hasPriceObservation`, `hl:sourcedFromSeries`, `hl:computesKPI`, `hl:suppliedBy` | relationships `:HAS_PRICE_OBSERVATION`, `:SOURCED_FROM_SERIES`, `:COMPUTES_KPI`, `:SUPPLIED_BY` | Preserve direction from the RDF predicate. |
| `hl:netVolumeGallons`, `hl:grossVolumeGallons`, `hl:ticketTimestamp` | node properties `netVolumeGallons`, `grossVolumeGallons`, `ticketTimestamp` | Properties on `:CustodyTicket`. |
| `hl:seriesIdentifier`, `hl:observedPriceUsdPerGallon` | node properties of the same name | Properties on `:PriceIndex` and `:PriceObservation`. |
| `hl:hasFormula`, `hl:hasDimension`, `hl:hasTimeGrain` | node properties `hasFormula`, `hasDimension`, `hasTimeGrain` | Properties on `:KPI`; multi-valued dimensions may import as an array. |

## Related homelab documents

- `00-Homelab-Charter-and-Roadmap.md`
- `01-Reference-Architecture.md`
- `02-Tool-Selection-and-ADRs.md`
- `03-Curriculum-and-Learning-Modules.md`
- `04-Data-Strategy-and-Datasets.md`
- `06-Repo-Structure-and-Build-Plan.md`

## See also (enterprise EPM parallel)

This document is a personal, simplified educational analog of the enterprise EPM **Commercial Margin / Gasoline Netback Pilot**, **KPI Store**, and **Downstream O2C Operational Blueprint** concept pages. It is not formally linked to, a substitute for, or a replacement of those governed enterprise artifacts.
