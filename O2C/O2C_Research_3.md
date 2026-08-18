# Enterprise Architecture Reference Document — Order-to-Cash (O2C) in Downstream Oil & Gas Commercial & Marketing

## TL;DR
- Downstream O2C is not standard order-to-cash: it is a **hydrocarbon-aware, tax-heavy, physically-reconciled** value stream where every step must handle temperature/density volume conversion (ASTM D1250-19e1 / API MPMS Ch. 11.1, reference temperatures 15°C and 60°F), formula/index-based pricing (Platts/Argus/OPIS), excise-duty status of stock (duty-paid vs duty-suspended), and channel-specific settlement (rack BOL, into-plane, bunker delivery note, fuel-card).
- The reference technology spine is **SAP S/4HANA for Oil & Gas (IS-Oil Downstream)** — HPM, TDP, EXG, TD, TSW, MAP, MCOE, SSR — integrated in real time with **Terminal Automation Systems** (Toptech TMS7, Implico OpenTAS), **indirect-tax engines** (Vertex O Series), **ETRM/CTRM**, and pricing-agency feeds.
- The hardest problems are exceptions: gross-vs-net volume disputes, loss/gain (evaporation/shrinkage) reconciliation, provisional-to-final price restatement, exchange-imbalance settlement, demurrage, off-spec quality claims, and tax-jurisdiction/duty-status misassignment. These must be engineered into the O2C process, not bolted on.

---

## SECTION 1: END-TO-END VALUE STREAM (L1 CHEVRON MAP)

The downstream O2C lifecycle spans from contract/quote capture through physical fulfilment (which is metered, temperature-corrected and duty-assessed) to invoicing, cash application, dispute resolution and financial close. Master Data Management & Governance is a foundational layer feeding every stage.

```
 DOWNSTREAM COMMERCIAL & MARKETING — ORDER-TO-CASH L1 VALUE STREAM
==================================================================================================

  >>> QUOTE &      >>> CREDIT &     >>> ORDER         >>> SCHEDULING &   >>> PHYSICAL       >>>
      CONTRACT          RISK             MGMT &            LOGISTICS          FULFILMENT
      CAPTURE           ONBOARDING       CALL-OFF          (TSW/TD)           (LOADING)
  -------------    -------------    -------------     -------------      -------------
  - Tender/bid     - Credit app     - Sales order/    - Nomination       - Gantry/rack
  - Formula/index    & scoring        call-off off      & stock proj.      loading (TAS)
    price offer    - Credit limit     contract        - Berth/barge/     - Metered qty
  - Contract         & LC/BG        - ATP / plant      pipeline sched.    - Temp/density
    (term/spot/      setup            determination   - Carrier/hauler     capture
    evergreen)     - Exposure       - Excise/tax        dispatch         - VCF -> net vol
  - Exchange         reservation      status default  - Into-plane /     - BOL / ticket /
    agreement                       - Provisional      barge order         BDN generation
                                      price stamp

    ...>>> INVOICING &   >>> RECEIPT &    >>> DISPUTE &     >>> FINANCIAL      >>> RETENTION &
           BILLING            COLLECTION       DEDUCTION          CLOSE              CONTRACT MGMT
       -------------      -------------    -------------     -------------      -------------
       - BOL->invoice     - Cash app       - Short-del /     - Loss/gain        - Volume/rebate
         actualization    - Fuel/fleet       demurrage         reconciliation     settlement
       - Formula & Avg      card settle    - Off-spec /      - Exchange         - Contract renewal
         (F&A) pricing    - IATA/ICH         contamination     netting &          / evergreen
       - Excise + VAT/       clearing       - Gross/net vol     balance settle   - Price review
         GST + env fees   - Netting          variance        - Provisional->    - Win/loss &
       - Consignment/       (exchange)     - Price              final restate     churn analytics
         consumption      - Collections      restatement     - Period close &
         billing                             claims            revenue recog.

==================================================================================================
  vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
  |  FOUNDATIONAL MASTER DATA MANAGEMENT & GOVERNANCE (ties into EVERY stage above)             |
  |  - Customer/ship-to/BP master + credit segment    - Material master (HPM conv. group/UoM)  |
  |  - Product spec & blend master (RVP, sulphur...)   - Plant/terminal/tank/strapping master   |
  |  - Pricing condition & index master (Platts...)   - Tax/excise-duty determination master   |
  |  - Exchange partner & agreement master            - Carrier/hauler & vehicle master        |
  |  - Governance: data ownership, stewardship, SoD, audit trail, change control, DQ KPIs      |
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Reading the map:** Unlike generic O2C, the physical fulfilment stage sits *inside* the cash cycle because the billable quantity is not known until product is metered at the rack and temperature-corrected to a standard volume; the invoice is an *actualization* of the BOL, not a copy of the order. Similarly, financial close cannot complete until physical loss/gain and exchange balances are reconciled.

---

## SECTION 2: INTEGRATED ORDER-TO-CASH CAPABILITY MAP

| **PILLAR 1: Quote & Contract Mgmt** | **PILLAR 2: Credit & Risk** | **PILLAR 3: Order Mgmt & Fulfilment** |
|---|---|---|
| Tender/bid & spot quote mgmt | Customer credit scoring & onboarding | Sales order / contract call-off |
| Formula/index-based contract pricing | Credit limit & dynamic exposure mgmt | ATP & automatic plant/terminal determination |
| Term/spot/evergreen contract mgmt | LC / bank guarantee / parent guarantee mgmt | Nomination & scheduling (TSW) |
| Exchange/buy-sell/terminalling agreements | Real-time credit block at call-off & loading | Bulk transport & distribution (TD) — rack/pipeline/marine |
| Price protection, DTW & rack posting mgmt | Counterparty & country risk (ETRM linkage) | BOL/ticket/BDN capture & confirmation (TAS) |

| **PILLAR 4: Invoicing & Billing** | **PILLAR 5: Receipt & Collection** | **PILLAR 6: Dispute Management** |
|---|---|---|
| BOL actualization & delivery-based billing | Cash application & lockbox | Short-delivery & quantity-variance claims |
| Formula & Average (F&A) pricing at billing | Fuel/fleet card settlement | Gross-vs-net volume dispute resolution |
| Multi-layer excise + VAT/GST + env fee calc | Card-network & IATA/ICH clearing | Off-spec / contamination quality claims |
| Consignment/consumption billing (retail) | Exchange/net-out settlement | Demurrage & laytime claims |
| Aviation into-plane & marine bunker billing | Collections & dunning | Price-restatement / index-correction disputes |

| **PILLAR 7: Retention & Contract Mgmt** | **PILLAR 8: Master Data Management** | **PILLAR 9: Governance** |
|---|---|---|
| Rebate / volume-incentive settlement | Business-partner & ship-to hierarchy | Data ownership & stewardship model |
| Contract renewal & evergreen mgmt | Material / product-spec / blend master | Segregation of duties & approval workflow |
| Retrospective price review | Pricing condition & index master | Audit trail & regulatory reporting |
| Loyalty & branded-dealer programs | Terminal/tank/strapping & UoM master | Data-quality KPIs & remediation |
| Churn / win-loss analytics | Tax/excise & exchange-partner master | Change control & reference-data lifecycle |

---

## SECTION 3: DEEP-DIVE PROCESS DEFINITION & MASTER DATA BASELINE

### PILLAR 1 — Quote & Contract Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Tender/Bid & Spot Quote Mgmt | Respond to customer/airline/marine tenders; build spot offers | Prices quoted as **differential to a benchmark** not flat price, e.g. NYMEX RBOB basis + differential = spot price; regional index selection (Platts/Argus dominant in Europe & the NY Harbor barge market, OPIS at US rack). Pipeline spot deals are large (5,000–50,000 bbl). Master data: index master, differential condition records, product-grade & spec |
| Formula/Index Contract Pricing | Define price = index average over a pricing period +/- differential | SAP IS-Oil **MAP (Marketing Accounting & Pricing)** and **F&A (Formula & Average Pricing)**; provisional vs final pricing (settle retroactively when index period closes). Master data: pricing formula, quotation source, quotation period, rounding rules |
| Term/Spot/Evergreen Contract Mgmt | Capture sales contracts and call-off restrictions | IS-Oil **MCOE**: multiple ship-to per contract, call-off restrictions, final-delivery indicator, contract-quantity correction on final delivery using ASTM. Master data: contract type, call-off tolerances |
| Exchange / Buy-Sell / Terminalling Agreements | Model reciprocal product supply at different locations between oil companies | IS-Oil **EXG**: exchange agreement links a sales and a purchase contract between two **exchange partners** — SAP: *"IS-OIL functionality establishes a link between sales and purchase contracts by means of the Exchange Agreement."* Exchange types (borrow/loan, buy/sell, terminalling) defined under EXG → Transactions → Define exchange types; **terminalling** is derived from the borrow/loan type via the ownership "Own" indicator (logical inventory not revalued). Master data: exchange partner, exchange type, fee condition records |
| Price Protection / DTW & Rack Posting | Manage branded-dealer DTW prices, rack postings, temporary voluntary allowances (TVA) | **DTW = rack price + transport + brand/credit-card/advertising costs**, set by refiner (per OPIS: DTW "reflects the rack price plus the refiner's costs for secure supplies, special additives, trademarks, credit cards and advertising"); unbranded buys at rack. Postings reset intraday (OPIS freezes supplier prices at benchmark times; RackPro covers 39,000+ daily prices). Master data: posting location, price cluster, TVA/rebate condition |

### PILLAR 2 — Credit & Risk

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Credit Scoring & Onboarding | Assess new customer/counterparty creditworthiness | Distinguish trade customers from trading counterparties; country risk relevant for import/export. Master data: credit segment, risk class, rating |
| Credit Limit & Dynamic Exposure | Track exposure across open orders, deliveries, unbilled, AR | Exposure volatile because value = volume × index that moves daily; must revalue exposure at current price. Master data: credit limit, exposure category, horizon |
| LC / Guarantee Management | Manage documentary/standby LC, bank & parent guarantees | Per The Global Treasurer, *"Physical oil deals usually have a deal specific letter of credit attached"*; margining is common in gas/power markets while LC dominates physical oil. Master data: LC reference, expiry, tolerance, confirming bank |
| Real-time Credit Block | Block order or loading if limit breached | Critical mid-fulfilment: credit can be breached between order and rack loading as price moves; block must reach the TAS to stop the gantry. Master data: credit-check rule, release authorization |
| Counterparty & Portfolio Risk | Monitor VaR, position, hedging limits | ETRM/CTRM linkage — trader books, hedging limits tied to business events. Master data: book, position limit, VaR parameters |

### PILLAR 3 — Order Management & Fulfilment

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Sales Order / Call-off | Convert contract to executable order | IS-Oil MCOE fast order entry, last-order defaulting, automatic item-category redetermination (e.g. consignment). Master data: order type, item category, call-off reference |
| ATP & Plant/Terminal Determination | Determine supplying terminal/plant | MCOE automatic plant determination with alternates if primary is dry. Master data: supplying plant, terminal, product availability |
| Nomination & Scheduling (TSW) | Plan bulk movements across pipeline/vessel/rail/truck | IS-Oil **TSW**: nominations, stock projection worksheet, berth scheduling to minimize demurrage; ticketing confirms actuals. TSW covers rail, pipeline, marine, barge, and truck. Master data: nomination type, transport system, event profile |
| Bulk Transport & Distribution (TD) | Execute scheduled movements, create shipments | IS-Oil **TD**: bulk shipment, vehicle/driver, rack meters, TAS interface, delivery-confirmation processing; quantity conversion at loading and delivery confirmation. Master data: transport unit, vehicle meter, tank |
| BOL/Ticket/BDN Capture | Capture the legal proof of delivery & quantity | Bill of Lading (rack), delivery ticket, marine **Bunker Delivery Note (BDN)**, aviation fuelling ticket; quantity is metered gross then corrected to net. Master data: BOL number range, ticket type |

### PILLAR 4 — Invoicing & Billing (incl. Volume/Measurement, Product Spec, Tax)

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Volume Measurement & Conversion | Convert metered ambient volume to standard net volume before billing | **ASTM D1250-19e1 / API MPMS Ch. 11.1** volume correction: apply the **VCF/CTL** to correct observed volume at ambient temperature to net standard volume; the standard aligns with ISO 91-1 reference temperatures of **15°C and 60°F**, and its metric procedures now also incorporate a **20°C** base, generating output factors CTL, Fp, CPL, CTPL across three commodity groups (crude oil, refined products, lubricating oils). Flow: gross observed volume (GOV) → gross standard volume (GSV) → net standard volume (NSV) after BS&W. IS-Oil **HPM** quantity conversion: material master carries **conversion group + UoM group** (SAP: an HPM material has "a conversion group and unit of measure group … active for the Oil and Gas quantity conversion"); QCI calls ASTM tables (e.g. 56A→TAB5a); MARM alternate-UoM factors are used pre-movement (contract/order), QCI at the actual goods movement. Master data: conversion group, UoM group (L15, GAL60), density/API gravity, tank strapping table |
| Product Spec, Blend & Additization | Ensure billed product matches contracted spec | Physical attributes: **RVP** (Reid Vapour Pressure), octane/cetane, sulphur ppm — **US Ultra-Low-Sulfur Diesel (ULSD) is capped at 15 ppm sulfur by EPA** (a ~97% reduction from 500 ppm low-sulfur diesel; on-road rack mandate effective 1 Sep 2006); flash point, cloud/pour point; **ethanol (E10) / biodiesel (Bx)** blend ratios; branded additization. Master data: product spec, blend recipe, additive package |
| Delivery-Based / BOL Actualization Billing | Bill on actual loaded/delivered quantity, not ordered | Invoice = actualized BOL quantity (net standard volume); F&A applies final formula price. Master data: billing type, actual-qty source |
| Multi-Layer Indirect Tax & Excise | Determine and post excise + VAT/GST + environmental fees | IS-Oil **TDP**: SAP — *"The system calculates and posts excise duty when a goods movement occurs, based on the quantity of material moved, and the location information."* The **handling type** determines ED status at the FROM/TO location and the rate level (ED-free/full/reduced); TDP keeps **split inventory** of the ED portion vs net price and distinguishes **duty-paid vs duty-suspended/bonded (DUP/DUPR)** stock; licenses drive reductions/exemptions. **US federal excise:** all removals of gasoline at a terminal rack are taxable and the **position holder is liable** (IRS Pub 510) — **18.4¢/gal gasoline** and **24.4¢/gal diesel/kerosene**, of which **0.1¢/gal is the LUST fee** (18.3¢ of gasoline goes to the Highway Trust Fund); the IRS collects from ~850 registered suppliers/refiners/blenders rather than every station (CRS R48948). **Dyed diesel** (off-highway, IRS No. 105) carries only the **0.1¢/gal LUST tax** vs 24.4¢ clear. **Jet fuel:** **4.4¢/gal commercial aviation, 21.9¢/gal non-commercial** (incl. LUST). **IFTA** applies to interstate carriers; Form 720/720-TO reporting. Tax engine (Vertex O Series) called real-time for jurisdiction + rate. Master data: excise duty group, handling type, tax status, exemption certificate, jurisdiction |
| Channel-Specific Billing | Apply channel billing model | **Retail:** consignment/consumption billing (bill on sale, not delivery). **Aviation:** into-plane ticket → IATA IS-XML e-invoice via **SIS (Simplified Invoicing & Settlement)**, settled through the **IATA Clearing House (ICH)** against the Revenue Accounting Manual rules. **Marine:** BDN-based invoice; where MFMs are mandated (Singapore since 1 Jan 2017; Rotterdam & Antwerp-Bruges from 1 Jan 2026) the delivered quantity is derived exclusively from the MFM totaliser. **Lubricants:** SKU/packaged billing with vendor-rebate accrual in COGS/margin. Master data: billing model per channel, card scheme, IATA location code |

### PILLAR 5 — Receipt & Collection

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Cash Application | Match incoming payments to AR | High invoice volume from rack loads; match on BOL. Master data: payment method, lockbox key |
| Fuel/Fleet Card Settlement | Settle card transactions from retail network | WEX/Voyager/EFS fleet cards; per-transaction capture with vehicle/driver, purchase controls, IFTA reporting; reconcile card network vs wetstock. Master data: card BIN, merchant, product restriction |
| Card-Network & IATA/ICH Clearing | Clear multi-party settlements | Aviation via IATA SIS/ICH; retail via card acquirers. Master data: clearing member, settlement calendar |
| Exchange / Net-Out Settlement | Settle exchange balances by product or cash | IS-Oil EXG netting — SAP: settlement is "the monthly setting up of a list containing the exchanged materials and fees incurring [and with it] the logical inventory … will be balanced." **Movement (inventory) netting** settles imbalance by product; **financial netting** settles by cash (AP/AR). Balances are tracked via **Logical Inventory Adjustment (LIA)** documents (two standard LIA document types; one keyed independent of the exchange number, one requiring it). Master data: netting type, fee condition, LIA document type |
| Collections & Dunning | Pursue overdue AR | Master data: dunning procedure, collection segment |

### PILLAR 6 — Dispute Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Short-Delivery / Quantity-Variance | Resolve delivered-vs-invoiced quantity gaps | Compare BOL vs ship/tank gauge; ROB (remaining on board), clingage, line-fill losses. Master data: tolerance, variance reason code |
| Gross-vs-Net Volume Dispute | Resolve disputes over temperature basis of billed volume | Rack sales often billed **gross** (metered gallons, not temp-corrected — e.g. OPIS MARC prices reflect "gross volume (metered gallons, not temperature-corrected)"); bulk billed **net**; disputes arise when parties disagree on basis. Master data: gross/net indicator, VCF |
| Off-Spec / Contamination Claims | Handle quality claims | Jet fuel to ATA103/JIG; contamination/cross-grade claims; per IATA Aviation Fuel Supply Model Agreement, short-delivery claims within **15 days** and quality claims within **30 days** of delivery, and a signature on the delivery note is not a waiver of the right to claim. Master data: spec test result, claim type |
| Demurrage & Laytime Claims | Compute vessel detention charges | Laytime starts on valid Notice of Readiness; **demurrage = daily rate × time exceeded** (liquidated damages, "once on demurrage, always on demurrage"); reversible vs non-reversible across load/discharge ports. Master data: charter party, laytime allowed, demurrage rate |
| Price-Restatement Disputes | Resolve provisional→final price differences | Index restatement when Platts/Argus corrects an assessment; cash settlement of retroactive change (contracts often specify ~20 calendar days plus interest). Master data: quotation source, pricing period |

### PILLAR 7 — Retention & Contract Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Rebate / Volume-Incentive Settlement | Accrue and pay volume/loyalty rebates | Lubricants vendor rebates flow into COGS/margin; TVAs ("temporary voluntary allowances") for dealers; jobber incentives. Master data: rebate agreement, tier, accrual |
| Contract Renewal / Evergreen | Manage rolling contracts | Evergreen supply/terminalling agreements. Master data: renewal rule, notice period |
| Retrospective Price Review | Periodic renegotiation | Formula methodology change with retroactive cash settlement. Master data: review clause |
| Loyalty / Branded-Dealer Programs | Manage brand relationship | Lessee-dealer, branded-jobber, company-dealer arrangements (DTW pricing tied to lease); brand fee. Master data: dealer type, brand agreement |
| Churn / Win-Loss Analytics | Analyse retention | Master data: churn reason, competitor |

### PILLAR 8 — Master Data Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Business Partner & Ship-To | Maintain customer/partner hierarchy | Sold-to/ship-to/payer; branded dealer, exchange partner, into-plane agent. Master data: BP role, partner function |
| Material / Product-Spec / Blend | Maintain product masters | HPM material = conversion group + UoM group assigned (UoM group cannot be changed once stock is posted); spec attributes (RVP, sulphur). Master data: material type, spec |
| Pricing Condition & Index | Maintain pricing masters | Index master (Platts/Argus/OPIS symbols), differential, DTW/rack postings. Master data: condition type, quotation |
| Terminal/Tank/Strapping & UoM | Maintain physical asset masters | Tank master, calibration/strapping table, correction factors, silo mgmt. Master data: tank, strapping, UoM group |
| Tax/Excise & Exchange-Partner | Maintain compliance masters | Excise duty group (OIH2), handling type, tax status (OIH4), ED rate table (OIH01), exemption certificate; exchange partner & agreement. Master data: ED group, jurisdiction |

### PILLAR 9 — Governance

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
|---|---|---|
| Data Ownership & Stewardship | Assign accountable owners | Cross-functional: pricing, tax, credit, logistics each own domains. Master data: steward, domain |
| Segregation of Duties & Approval | Enforce SoD across trade lifecycle | ETRM/ERP SoD (trader vs back office); credit-release authority. Master data: role, authorization |
| Audit Trail & Regulatory Reporting | Maintain auditable records | Excise returns (Form 720/720-TO), REMIT/EMIR for trading, environmental. Master data: report type, retention |
| Data-Quality KPIs & Remediation | Measure and fix DQ | Master data: DQ rule, threshold |
| Change Control & Reference Lifecycle | Govern reference-data changes | Master data: change request, effective date |

---

## SECTION 4: SYSTEM LANDSCAPE & INTEGRATION ARCHITECTURE

```
 DOWNSTREAM O2C ENTERPRISE SYSTEM ECOSYSTEM
=====================================================================================================

   [ CRM / COMMERCIAL ]            [ ETRM / CTRM ]                 [ PRICING AGENCIES ]
   - Quote, tender, contact        - Deal capture, position        - Platts / Argus / OPIS
   - Opportunity / retention       - VaR, hedging, P&L               index & rack feeds
          |                              |                                 |
          | contract, customer          | trade, exposure,                | index curves,
          v                             v  provisional price              v  differentials
  +===============================================================================================+
  |                     CORE ERP / INDUSTRY SOLUTION                                              |
  |                     SAP S/4HANA for Oil & Gas (IS-Oil Downstream)                             |
  |   MCOE (contract/order)  MAP + F&A (pricing)   HPM (qty conv.)   TDP (excise)   EXG (exchange)|
  |   TSW (nomination/sched.)  TD (transport/dist.)  SD/MM/FI-CO (std)  SSR/MRN (retail)          |
  +===============================================================================================+
        ^   |               ^     |                ^      |                 ^     |
        |   | order/         |     | tax            |      | BOL/            |     | card/
   credit   v scheduled  tax call  v determination  actual v net volume  settle   v settlement
   check    |   volume    (real-   |  result        volume |  BOL confirm   files  |
        |   |             time)    |                       |                       |
   [ CREDIT/  ]     [ INDIRECT TAX ENGINE ]      [ TERMINAL AUTOMATION ]     [ CARD / IATA / BANK ]
   [ RISK &   ]     [ Vertex O Series /     ]    [ SYSTEM (TAS)        ]     [ - Fleet/fuel card   ]
   [ ETRM     ]     [ OneSource / Avalara   ]    [ Toptech TMS7 /      ]     [   networks (WEX...) ]
   [ exposure ]     [ - excise, VAT/GST,    ]    [ Implico OpenTAS     ]     [ - IATA SIS / ICH    ]
   [          ]     [   env fee, exemption  ]    [ - gantry/rack ctrl  ]     [ - banks / lockbox   ]
                    [   certificate         ]    [ - meter, eBOL       ]
                                                 [ - stock accounting  ]
                                                        ^      |
                                                  gauging|      | actual loaded qty,
                                                 (ATG)   |      v temp/density, BOL
                                             [ FIELD / TANK GAUGING, LOAD RACK, METERS ]

   [ TRANSPORT / LOGISTICS (TMS) ]        [ FLEET TELEMATICS / VMI ]
   - carrier dispatch, freight            - tank level (VMI), auto-replenish
   - marine/barge/pipeline schedule       - delivery confirmation, wetstock
          ^                                        ^
          | freight order, ETA                     | tank readings, consumption
          +----------------------------------------+---> feed ERP order & billing
=====================================================================================================
```

The TAS layer (Toptech TMS7, Implico OpenTAS) sits above the field gauging/meters and integrates to the ERP for real-time transaction data and order updates, sending electronic BOLs (eBOLs) and receiving allocations/master data. OpenTAS explicitly supports SAP integration (e.g. SAP SDM) for the flow from field equipment up to the ERP.

### Critical real-time integration points across the O2C lifecycle

| Integration Point | Systems | Data Exchanged | O2C Stage |
|---|---|---|---|
| Index feed → pricing | Platts/Argus/OPIS → ERP MAP/F&A / ETRM | Daily index, differential, rack posting | Quote, billing |
| Credit check → order/loading | ERP/ETRM credit → SD → TAS | Credit status, block/release | Order, fulfilment |
| Tax determination call | ERP → Vertex/OneSource → ERP | Jurisdiction, excise/VAT rate, exemption | Order, billing |
| Nomination → shipment | TSW → TD → TAS | Scheduled volume, transport system | Scheduling |
| TAS → ERP BOL confirmation | TAS (Toptech/Implico) → ERP TD/HPM | Actual loaded qty, temp/density, BOL#, eBOL | Fulfilment |
| Actual vs scheduled volume | TAS → ERP | GOV/GSV/NSV, VCF, meter reading | Fulfilment, billing |
| Delivery/consumption → billing | VMI/telematics/retail POS → ERP | Tank readings, consignment consumption | Billing |
| Card/IATA settlement | Card network / IATA SIS → ERP FI | Transaction file, IS-XML e-invoice, ICH clearing | Collection |
| Exchange netting | ERP EXG ↔ partner | LIA, balances, fees, net-out | Collection, close |

---

## SECTION 5: DOWNSTREAM OPERATIONAL EXCEPTIONS & RISK MANAGEMENT

### Exception 1 — Temperature-driven volume variance & gross-vs-net billing dispute
**Scenario:** A customer loads product measured at ambient temperature. The BOL shows gross observed volume; the contract requires net standard volume at 15°C/60°F. The customer's receiving gauge disagrees.
**Resolution:**
1. Capture gross observed volume (GOV) at the rack meter plus observed temperature and density/API gravity.
2. Apply the ASTM D1250 / API MPMS Ch. 11.1 volume correction factor (VCF/CTL) to derive gross standard volume (GSV), then deduct BS&W to get net standard volume (NSV).
3. IS-Oil HPM re-derives the quantity from the material's conversion group and QCI table; the invoice is issued on NSV.
4. If the customer disputes, reconcile both parties' temperature and density readings against the certified tank strapping table and meter calibration; adjust with a credit/debit memo and a variance reason code.
**Control:** Contract must explicitly state gross vs net basis and the standard temperature; rack billing (often gross) and bulk billing (often net) must be flagged to avoid basis mismatch.

### Exception 2 — Loss/gain reconciliation (evaporation / shrinkage / theft)
**Scenario:** End-of-period terminal book stock does not equal physical stock.
**Resolution:**
1. Compute Loss/Gain = Closing Inventory + Deliveries − Beginning Inventory − Receipts (per Hart Energy: L/G = CI + D − BI − R).
2. Classify causes: measurement/ticketing inaccuracy, temperature-driven apparent variance, evaporation (published studies cite floating-roof loss leeway of roughly ±0.2% of throughput for petrol and ±0.15% for diesel), clingage/ROB, admixture shrinkage, or theft/abuse.
3. Compare against tolerance; verify ATG values by monthly manual gauging with a calibrated tape.
4. IS-Oil posts gain/loss to dedicated accounts; two-step transfers with profit/loss determination handle in-transit differences.
5. Out-of-tolerance variance triggers investigation (leak test, meter recalibration, security review).
**Control:** Daily/weekly/monthly/annual reconciliation cadence with defined loss tolerances per product.

### Exception 3 — Provisional-to-final price finalization & index restatement
**Scenario:** Product invoiced provisionally; the formula references an index average over a pricing period that closes after delivery, or the agency restates an assessment.
**Resolution:**
1. At delivery, invoice at a provisional price (e.g. forward curve or prior average).
2. When the quotation period closes, F&A recomputes the final price and issues a settlement invoice/credit for the difference plus contractual interest.
3. If Platts/Argus restates a published assessment, re-run the formula and settle the delta.
**Control:** Master data must lock quotation source, period, and rounding; retroactive settlement window (e.g. ~20 calendar days plus interest) defined in contract.

### Exception 4 — Exchange imbalance settlement
**Scenario:** Two partners have exchanged product at different locations; monthly volumes lifted do not balance.
**Resolution:**
1. IS-Oil EXG tracks each partner's logical inventory via Logical Inventory Adjustment (LIA) documents (movement-based or balance-based).
2. At month-end settlement, the system lists exchanged materials and fees and balances the logical inventory.
3. Imbalance is settled either by **movement (inventory) netting** (deliver product to square the balance) or **financial netting** (cash AP/AR).
4. Borrow/loan positions appear as negative stock on the exchange plant until squared (transfer posting movement types 301/302).
**Control:** Netting agreement must define whether settlement is physical or financial and prohibit netting of unrelated claims (LEAP master agreement expressly limits netting to product purchases/sales, excluding quality claims and interest).

### Exception 5 — Credit limit breach mid-fulfilment
**Scenario:** Between order creation and rack loading, the daily index rise pushes the order value above the customer's available credit.
**Resolution:**
1. Dynamic exposure revalues open orders at the current index price.
2. When exposure exceeds the limit, the credit engine sets a block that propagates to the TAS, preventing gantry authorization.
3. Back office reviews: request prepayment, draw on LC/guarantee, or obtain a temporary limit increase with documented approval.
4. On release, the block clears and the TAS authorizes loading.
**Control:** Real-time credit-to-TAS integration; SoD between credit release and sales.

### Exception 6 — Off-spec / contamination quality claim
**Scenario:** Delivered fuel fails spec (e.g. jet fuel water/particulate, cross-grade contamination, high sulphur).
**Resolution:**
1. Retain samples and test against the contracted spec (e.g. ATA103 / JIG for jet fuel; water tests via Shell Water Detector, Aqua-Glo, etc. per AFSMA).
2. Notify within the contractual claim window (per IATA AFSMA: short-delivery within 15 days, quality within 30 days; signature on the delivery note is not a waiver).
3. Quantify remediation (re-blend, downgrade, disposal) and issue credit or replacement.
**Control:** Spec master and test-result capture; claim-window master data; segregation of quality sign-off.

### Exception 7 — Tax jurisdiction / duty-status misassignment
**Scenario:** Product removed as duty-suspended (bonded) but billed/moved as duty-paid, or the wrong tax jurisdiction is applied at the rack.
**Resolution:**
1. IS-Oil TDP handling type governs ED status at FROM/TO location; the tax engine (Vertex) determines jurisdiction from ship-to/terminal.
2. On misassignment, reverse the material/accounting document; re-post with correct handling type and duty status (duty-paid vs duty-suspended DUP/DUPR).
3. For US, correct Form 720/720-TO position-holder reporting; for exemptions, validate the exemption certificate / dyed-diesel status (dyed diesel carries only 0.1¢/gal LUST vs 24.4¢ clear — a large exposure if misclassified).
4. Settle any excise liability/claim delta with the tax office.
**Control:** Exemption-certificate master, handling-type determination rules, and real-time tax-engine calls with jurisdiction validation.

---

## Recommendations
1. **Anchor the architecture on SAP S/4HANA for Oil & Gas (IS-Oil Downstream)** as the O2C system of record, activating HPM, TDP, EXG, TD, TSW, MAP/F&A and MCOE/SSR; do not attempt to replicate hydrocarbon quantity conversion or excise handling in a generic ERP. Note IS-Oil extends the standard sales document item with dozens of oil-specific fields precisely because pricing, tax and quantity conversion behave differently from SAP standard.
2. **Externalize tax to a dedicated engine (Vertex O Series or equivalent)** with real-time determination calls at order and billing; maintain exemption certificates and jurisdiction master centrally. This is essential given the multi-layer stack (federal excise, LUST, state motor-fuel, VAT/GST, environmental/superfund) and duty-suspension rules.
3. **Integrate TAS bidirectionally in real time** (BOL confirmation, actual vs scheduled volume, credit-block-to-gantry) — this is the single highest-value integration because it closes the physical-to-financial gap and is the source of net-volume billing accuracy.
4. **Engineer exceptions as first-class processes** (loss/gain, gross/net, provisional pricing, exchange netting, demurrage, quality, duty-status) with reason codes, tolerances and audit trails, not as manual workarounds.
5. **Stand up MDM & governance before go-live**: business-partner, material/spec, pricing/index, terminal/tank/strapping, tax/excise and exchange-partner domains with named stewards and SoD. The UoM group cannot be changed once stock is posted, so material-master conversion setup must be right first time.
6. **Staged rollout benchmark:** pilot one channel (wholesale/rack) end-to-end, validate net-volume billing accuracy and tax posting, then extend to retail (consignment/wetstock), aviation (IATA SIS/ICH), marine (BDN/MFM — note MFM mandates now in force at Rotterdam & Antwerp-Bruges from 1 Jan 2026) and lubricants (rebate). **Thresholds that would change the plan:** if loss/gain persistently exceeds product tolerance (~±0.2% petrol / ±0.15% diesel), halt rollout and remediate measurement/master data first; if tax-determination error rate exceeds internal audit thresholds, freeze billing automation until reconciled; if credit-block latency to the TAS is not near-real-time, do not automate rack authorization.

## Caveats
- Some SAP table/transaction-code and movement-type details (e.g. OIH01/OIH2/OIH4 excise tables, 301/302 borrow-loan movements, LIA document types) are corroborated by SAP Community and third-party SAP data-dictionary mirrors rather than first-party SAP Help pages (which block automated retrieval) and should be validated against the specific release in use.
- US federal fuel-tax rates cited (18.4¢ gasoline, 24.4¢ diesel/kerosene, 0.1¢ LUST, 4.4¢/21.9¢ jet) are current per IRS Publication 510 (12/2025) and CRS R48948, but state/provincial excise, environmental/superfund fees, dyed-diesel rules, IFTA and EU/UK duty-suspension regimes vary by jurisdiction and change over time; confirm current rules per operating country. Note recent US legislative changes (Working Families Tax Cuts Act) added IRC §6435 dyed-diesel claim provisions effective end-2025 and §45Z clean-fuel credits — verify applicability.
- Evaporation-loss tolerance figures are indicative ranges from published academic/industry studies, not universal legal limits; set company-specific tolerances.
- Pricing-agency methodologies (Platts/Argus/OPIS) evolve; verify current symbols and methodologies before hard-coding formula references. Argus/Platts operate at the spot level and OPIS/DTN at the rack level — index selection must match the contract's reference market.
- Marine MFM regulatory timeline: Singapore mandatory since 1 Jan 2017 (SS 648:2024 tightening from 1 Apr 2025); Rotterdam and Antwerp-Bruges from 1 Jan 2026 per NorthStandard/industry reporting — confirm scope (fuel grades covered) per port.