# Downstream Oil & Gas Commercial & Marketing
# Order-to-Cash (O2C) Enterprise Architecture Blueprint

| Attribute | Value |
| :--- | :--- |
| **Document ID** | EPM-BA-O2C-DS-001 |
| **Title** | Downstream O&G Order-to-Cash Operational Blueprint |
| **Domain** | Downstream Commercial & Marketing — Order to Cash |
| **Version** | 1.0 |
| **Status** | Draft / Candidate Baseline |
| **Workstream** | Domain Modeling (Downstream Business Architecture) |
| **Audience** | Enterprise Architects, Process Owners, MDM Stewards, Finance Controllers, Commercial Ops |
| **Channels in Scope** | B2B C&I, Wholesale/Rack, Retail Station Networks, Lubricants, Aviation, Marine |
| **Out of Scope** | Upstream production accounting, midstream pure tariff/transportation O2C (except terminal/pipeline custody interfaces), crude trading books, refining process control |
| **Related EPM Artifacts** | Downstream Business Architecture; Enterprise Measurement Catalog; KPI Store; Data Product Portfolio |

---

## Document Purpose

This blueprint is an Enterprise Architecture reference for the end-to-end **Order-to-Cash (O2C)** value stream in Downstream Oil & Gas Commercial & Marketing. It is intentionally *not* a generic manufacturing or retail O2C description. It surfaces the physical, logistical, financial, tax, pricing, legal, and measurement realities that differentiate hydrocarbon commercial operations: temperature/pressure volume correction, multi-unit of measure (UoM) accounting, rack and formula pricing, motor fuel excise frameworks, terminal automation custody events, exchange/borrow/loan netting, multi-channel title transfer models, and channel-specific settlement instruments (BOL, BDN, uplift ticket, POS shift close, LIA).

The blueprint is structured for use as:

1. A capability and process baseline for KPI/metric design in the Enterprise Performance Model.
2. A master-data and integration contract reference for domain modeling and system integration workstreams.
3. An exception/risk catalog for controls design (credit, tax, measurement, title, and settlement).

---

## SECTION 1: END-TO-END VALUE STREAM (L1 CHEVRON MAP)

### 1.1 Scope of the O2C Lifecycle

Downstream Commercial O2C begins at **commercial opportunity / contract capture** (not merely sales order entry) and ends at **cash application, dispute closure, and period financial close**, with continuous feedback into credit exposure, contract performance, and customer retention. Operational custody events (rack load, bulk drop, into-plane uplift, bunker delivery, retail pump dispense) are first-class economic events—not warehouse “goods issue” analogues—because quantity, quality, tax status, and title often crystallize only at the meter/ticket.

Industry terminal/pipeline commercial platforms describe O2C as the cycle managed **from order to invoice**, synchronizing logistics and commercial management to reduce invoicing error and accelerate month-end close ([Emerson DeltaV O2CManager](https://www.emerson.com/en/automation-systems/advanced-industry-software/oil-and-gas/software-for-energy-transportation-storage/order-to-cash-software)). Large operators have treated O2C as a transformation lever for pipeline/terminal commercial excellence, integrating nomination, scheduling, measurement, and billing ([Infosys O2C transformation](https://www.infosys.com/industries/oil-and-gas/insights/order-to-cash-transformation.html)). Process-mining deployments in integrated oil majors similarly target B2B sales O2C first-time quality and cycle time ([Celonis / MOL Group](https://www.celonis.com/solutions/stories/mol-order-to-cash)).

### 1.2 L1 Chevron Value Stream Map (ASCII)

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  FOUNDATIONAL LAYER (runs continuously across every chevron)                                                          ║
║  ┌──────────────────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────────────────────────┐ ║
║  │ MDM & Product/Customer Hub   │   │ Credit, Tax & Legal Master    │   │ Governance, Controls & Audit Trail       │ ║
║  │ • Customer/Ship-to/Payer     │   │ • Credit limits & collateral  │   │ • SOX / internal control narratives      │ ║
║  │ • Material / HPM / Specs     │   │ • FEIN, licenses, exemptions  │   │ • Measurement SOP / API MPMS adherence   │ ║
║  │ • Terminal/Rack/Depot plant  │   │ • Bonded vs duty-paid status  │   │ • Data quality SLAs & stewardship        │ ║
║  │ • Carrier / Driver / Trailer │   │ • Sanction/KYC screening      │   │ • Contract & price approval authorities  │ ║
║  │ • Contract & price condition │   │ • Incoterms / title rules     │   │ • Exception taxonomy & RCA               │ ║
║  └──────────────┬───────────────┘   └──────────────┬───────────────┘   └──────────────────┬───────────────────────┘ ║
╚═════════════════╪══════════════════════════════════╪══════════════════════════════════════╪════════════════════════╝
                  │ feeds / constrains               │                                      │
                  ▼                                  ▼                                      ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ 1.QUOTE &  │─▶│ 2.CREDIT & │─▶│ 3.ORDER &  │─▶│ 4.FULFILL  │─▶│ 5.MEASURE  │─▶│ 6.INVOICE  │─▶│ 7.CASH &   │─▶│ 8.DISPUTE  │
│ CONTRACT   │  │ RISK       │  │ NOMINATE   │  │ & LOGISTICS│  │ & TITLE    │  │ & TAX      │  │ COLLECT    │  │ CLOSE &    │
│ CAPTURE    │  │ RELEASE    │  │ SCHEDULE   │  │ EXECUTE    │  │ TRANSFER   │  │ BILL       │  │ SETTLE     │  │ RETAIN     │
└────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘
     │                │               │               │               │               │               │               │
     ▼                ▼               ▼               ▼               ▼               ▼               ▼               ▼
 Formula / index   Exposure vs     Call-off /      TAS load /      GOV→GSV→NSV     Multi-channel   ACH/wire/card   Quantity,
 term sheets;      limit; bond;    rack appoint-   bulk drop /     QCI; BOL/BDN/   billing; excise  lockbox;       quality, tax,
 volume commit;    sanctions;      ment; VMI       into-plane /    uplift ticket;  dyed/clear;     netting;       price, freight
 exchange/EXG;     payment terms   auto-order;     bunker; retail  certificate of  LIA / fee       deduction      disputes;
 channel SPA       release         secondary TD    POS dispense    quality         settlement      handling       contract renew
```

### 1.3 Chevron Definitions (L1)

| L1 Chevron | Business Outcome | Primary Downstream Triggers | MDM / Governance Tie-In |
| :--- | :--- | :--- | :--- |
| **1. Quote & Contract Capture** | Commercially approved instrument (SPA, rack access agreement, dealer/commission contract, into-plane MSA, bunker GT&C, lube supply agreement, exchange agreement) | RFQ; bid; index nomination; branded dealer onboarding; airport tender; port bunker inquiry | Customer legal entity, ship-to, payer hierarchy; product grade family; price procedure; Incoterms; jurisdiction tax profile; contract version control |
| **2. Credit & Risk Release** | Orderable credit envelope and counterparty clearance | New account; limit review; open AR + unbilled lifts + contingent tax; mark-to-market on formula books | Credit master, collateral/LC, parent guarantee, insurance; sanctions list; license validity |
| **3. Order & Nominate / Schedule** | Executable commercial order + logistics nomination | Rack order / card lock; C&I call-off; VMI forecast; aviation flight schedule; vessel nomination; retail tank forecast | Order type by channel; plant/rack determination; carrier/driver qualifications; appointment slots; inventory ownership model |
| **4. Fulfill & Logistics Execute** | Physical movement authorized and executed under control | TAS load authorization; bulk truck routing; into-plane dispatch; bunker barge/stem; retail tank truck; pipeline batch | Terminal/plant, tank, meter, compartment, driver PIN, carrier SCAC; product availability / allocation |
| **5. Measure & Title Transfer** | Custody quantity/quality locked; title/risk per Incoterms | Meter ticket; temperature/density sample; seal; BOL; BDN; uplift ticket; POS gallon totalizer | UoM dual/triple posting (observed vs standard); QCI parameters; batch/spec; tax status (clear/dyed/bonded) |
| **6. Invoice & Tax Bill** | Customer-ready fiscal document + statutory tax reporting events | Auto-bill on ticket; cycle bill; fee bill (throughput, into-plane service); exchange differential invoice | Price condition determination; tax engine jurisdiction stack; exemption certificates; invoice form variants |
| **7. Cash & Collect / Settle** | Applied cash; reduced exposure; partner netting closed | ACH debit per rack agreement; wire; card; lockbox; netting statement; retail sweep | Bank master; payment advice matching keys (BOL#, ticket#, invoice#); tolerance rules |
| **8. Dispute, Close & Retain** | Root-caused variance closed; books closed; contract performance scored | Short-pay; temperature claim; quality off-spec; tax rebill; freight claim; period-end accruals | Dispute codes; write-off authority; KPI feedback; renewal/churn workflow |

### 1.4 Channel Variants Overlay on the Chevron

| Channel | Distinct O2C Signature |
| :--- | :--- |
| **Wholesale / Rack** | High-velocity card-lock / rack orders; meter ticket + BOL as invoice support; short payment terms (often ~10 days ACH); rack or OPIS/Platts-referenced pricing ([OPIS rack pricing](https://www.opis.com/blog/wholesale-rack-fuel-pricing-essentials/); [QT Fuels Wholesale Rack Agreement](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf)) |
| **B2B C&I** | Contract call-offs; VMI/tank telemetry; multi-drop bulk; often delivered duty-paid with destination tax; freight & demurrage components ([Shell eVMI](https://www.shell.com/business-customers/commercial-fuels/evmi.html)) |
| **Retail Station Networks** | Dealer / lessee-dealer / commission-agent models; consignment inventory ownership variants; POS shift/day close; brand fee & rebate nets; tank wagon replenishment ([C-Store Trader dealer models](https://www.cstoretrader.com/guides/dealer-vs-lessee-dealer-vs-commission/); [Petrosoft consigned stations](https://help.petrosoftinc.com/Content/Station_Home/Station_Options/consigned_station.htm)) |
| **Lubricants** | Packaged + bulk; SKU explosion (viscosity grade, OEM approvals); warehouse pick/pack; returns & core charges; less volume-correction intensive than fuels but dense product master |
| **Aviation** | Into-plane uplifts; flight/tail number; airport FBO fees; IATA/into-plane service charges; uplift ticket reconciliation ([Aviation fuel invoice reconciliation](https://invoicedataextraction.com/blog/aviation-fuel-invoice-reconciliation); [DOI Aviation Fuel Management Handbook](https://www.doi.gov/sites/default/files/documents/2024-09/doi-aviation-fuel-management-handbook-sept-2024.pdf)) |
| **Marine** | Stem nomination; barge/ship-to-ship; BDN as statutory & commercial document; mass/volume dual; sulfur/MARPOL attributes; demurrage ([ExxonMobil BDN](https://www.exxonmobil.com/en/marine/technicalresource/marine-resources/bunker-delivery-notes); [BDN 2025 guide](https://vesselchain.org/bunker-delivery-note-guide-2025/)) |

### 1.5 Master Data Management Insertion Points

MDM is not a “side process.” It is a **hard gate** at chevrons 1–3 and a **reconciliation dimension** at 5–8:

```
Contract Capture ──requires──▶ Golden Customer + Product Spec + Price Procedure + Tax Profile
Credit Release   ──reads─────▶ Exposure dimensions keyed by Payer + Product Family + Location
Order Entry      ──validates─▶ Ship-to tank/rack eligibility, carrier card, product grade availability
Fulfillment      ──consumes──▶ Terminal plant/tank/meter masters from TAS + ERP plant
Measurement      ──applies───▶ QCI tables (density, CTL/CPL, VCF) per API MPMS / ASTM D1250
Billing          ──derives───▶ Taxability from product tax class + destination + exemption cert
Cash/Dispute     ──matches───▶ Alternate keys: Ticket ID, BOL, BDN, Uplift #, POS batch
```

Quantity conversion is foundational: SAP IS-Oil TSW/HPM designs require QCI conversion data defined for material, plant, storage location, and batch so goods movements and nominations post correctly ([SAP TSW help](https://help.sap.com/docs/SUPPORT_CONTENT/isoil/3139386109.html); [SAP QCI integration](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/0f4ab800d01c4366b0c9aaff06a64320/40ea5e9072ae42119c3425a9f9294d5f.html); [SAP Community HPM/QCI](https://community.sap.com/t5/enterprise-resource-planning-q-a/sap-is-oil-and-gas-hpm-module-implementation-without-qci-interface/qaq-p/12108628)). Physical volume correction algorithms are defined under **API MPMS Chapter 11.1 / ASTM D1250** for temperature and pressure effects on density and volume of crude, refined products, and lubricants ([ASTM D1250-19e1](https://www.astm.org/d1250-19e01.html); [API Petroleum Measurement catalog](https://www.api.org/-/media/files/publications/2024-catalog/2024-petroleum-measurement.pdf)).

---

## SECTION 2: INTEGRATED ORDER-TO-CASH CAPABILITY MAP

### 2.1 Capability Pillar Grid (L1 → L2/L3 Downstream-Specific)

| Capability Pillar (L1) | L2/L3 Specialized Capabilities (Downstream O&G) |
| :--- | :--- |
| **A. Quote & Contract Management** | A1 Formula & Index-Linked Pricing Contract Design · A2 Rack Access / Throughput & Terminaling Agreements · A3 Exchange, Buy-Sell & Location Swap Structuring · A4 Channel Contract Archetypes (Dealer / Commission / Into-Plane / Bunker GT&C / Lube SPA) · A5 Volume Commitment, Allocation & Take-or-Pay Administration |
| **B. Credit & Risk Management** | B1 Multi-Dimensional Credit Exposure (lifted unbilled + open AR + contingent tax + MTM) · B2 Collateral, LC, Parent Guarantee & Prepay Controls · C3 Counterparty KYC / Sanctions / Beneficial Ownership · B4 Payment Term & Method Risk by Channel · B5 Credit Release at Order, Load Authorization & Invoice |
| **C. Order Management & Fulfillment** | C1 Multi-Channel Order Capture (rack card, EDI, portal, VMI auto-order, aviation schedule, vessel stem) · C2 Nomination, Appointment & Slotting (rack, pipeline, marine berth) · C3 Secondary Distribution / Bulk Fleet Execution (TD) · C4 Terminal Automation Load Control & BOL Issuance · C5 Allocation, Rationing & Product Availability Management |
| **D. Invoicing & Billing** | D1 Ticket-to-Invoice Automation (BOL/BDN/Uplift/POS) · D2 Multi-Component Billing (product, freight, into-plane fee, throughput, demurrage, additive) · D3 Excise / Motor Fuel / Sales Tax Determination & Exemption · D4 Exchange Differential & LIA Settlement Billing · D5 Cycle, Self-Bill, Consignment & Commission Settlement Runs |
| **E. Receipt & Collection** | E1 Cash Application on Ticket/BOL Keys · E2 ACH Debit / Card / Wire / Lockbox Orchestration · E3 Partner Netting & Intercompany Settlement · E4 Deduction Management (shortage, quality, tax, freight) · E5 Unapplied Cash & Suspense Clearing |
| **F. Dispute Management** | F1 Quantity Dispute (temp/density/VCF/meter factor) · F2 Quality / Spec Off-Grade Claims · F3 Price & Index Publication Disputes · F4 Tax Rebill & Exemption Certificate Failures · F5 Demurrage, Detention & Service-Level Claims |
| **G. Customer Retention & Contract Performance** | G1 Contract Utilization & Uplift Analytics · G2 Rebate, Brand Fee & Incentive True-Up · G3 Churn / Dealer Network Health · G4 Service Level & OTIF by Channel · G5 Renewal, Reprice & Index Roll Management |
| **H. Master Data Management** | H1 Customer / Hierarchy / Ship-to Tank Topology · H2 Hydrocarbon Product, Spec, Additive & Tax Class · H3 Location Topology (Terminal, Rack, Bay, Depot, Station, Airport, Port) · H4 Partner Exchange & Book-Out Structures · H5 Carrier, Driver, Trailer, Compartment & Card Assets |
| **I. Governance, Controls & Compliance** | I1 Measurement Governance (API MPMS / ASTM) · I2 Pricing Authority & Index Feed Controls · I3 Tax & Excise Regulatory Compliance · I4 SOX / Revenue Recognition Controls for Title Transfer · I5 Data Quality, Lineage & Stewardship for O2C Data Products |

### 2.2 Capability × Channel Heat Map

| Capability | Rack | C&I | Retail | Lubes | Aviation | Marine |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Formula/Index Contract | ● | ● | ◐ | ◐ | ● | ● |
| Rack Access Agreement | ● | ◐ | ○ | ○ | ○ | ○ |
| Exchange/Borrow/Loan | ● | ● | ○ | ○ | ◐ | ◐ |
| VMI / Telemetry Order | ○ | ● | ● | ◐ | ○ | ○ |
| TAS / BOL Integration | ● | ● | ● | ○ | ◐ | ◐ |
| BDN / Marine Docs | ○ | ○ | ○ | ○ | ○ | ● |
| Into-Plane Uplift | ○ | ○ | ○ | ○ | ● | ○ |
| Consignment/Commission | ○ | ○ | ● | ◐ | ○ | ○ |
| Excise Dyed/Clear | ● | ● | ● | ○ | ◐ | ◐ |
| Partner Netting | ● | ● | ○ | ○ | ◐ | ● |

Legend: ● Core · ◐ Partial / situational · ○ Rare

---

## SECTION 3: DEEP-DIVE PROCESS DEFINITION & MASTER DATA BASELINE

For each pillar, L2 processes are defined with Downstream-specific mechanics and master data attributes.

### 3.A Quote & Contract Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **A1 Formula & Index-Linked Pricing Design** | Design, approve, and version price procedures that convert market publications and differentials into invoiceable unit prices; maintain effective dating and fallback logic. | Fuel price formation typically cascades **NYMEX → Spot → Rack**, with basis differentials that can decouple from futures on local outages ([OPIS](https://www.opis.com/blog/wholesale-rack-fuel-pricing-essentials/)). Contracts reference Platts/OPIS/Argus assessments with grade, location, and timing rules ([Platts Americas Refined Oil Products methodology](https://www.spglobal.com/commodityinsights/plattscontent/_assets/_files/en/our-methodology/methodology-specifications/americas-refined-oil-products-methodology.pdf); [Platts US gasoline blend value](https://www.spglobal.com/energy/en/pricing-benchmarks/our-methodology/subscriber-notes/050126-platts-launches-new-gasoline-blend-value-calculations-in-us)). **MD attributes:** Index ID, publication lag (e.g., prior day mean), differential ($/gal or ¢/gal), escalation clauses, currency, UoM (gal @60°F / m³ @15°C / MT), holiday calendar, price cap/floor, additive package adder, RIN/LCFS cost pass-through flags. |
| **A2 Rack Access & Terminaling Agreements** | Establish customer right to lift at named terminals/racks, credit terms, BOL rules, and payment mechanics. | Wholesale rack agreements define barrel as **42 net U.S. gallons at 60°F**, payment often **ACH debit ~10 days from delivery**, supported by invoice + rack meter ticket/BOL, with late fees ([QT Fuels Wholesale Rack Agreement](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf)). Pipeline/terminal GT&Cs define custody, quality, and liability frameworks ([Energy Transfer Petroleum Products GT&Cs](https://cms.energytransfer.com/wp-content/uploads/2019/04/GTsCsPetroleumProducts-02012019v9_1_Final.pdf)). **MD:** Terminal ID, rack/bay eligibility, carrier authorization list, card-lock ID, product slate, minimum lift, appointment window, insurance certificates, access hours. |
| **A3 Exchange, Buy-Sell & Location Swap Structuring** | Structure partner product exchanges (like-kind or differential), borrows/loans, and book-outs to optimize logistics footprint without unnecessary physical haul. | IS-Oil EXG patterns track exchange balances, borrow/loan, LIA (Logical Inventory Adjustment) documents, and netting of customer/vendor invoices including product and tax postings ([SAP EXG discussion](https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/exchange-borrow-loan-invoice-the-difference-quantity-after-lia/m-p/7554007); [SAP netting statements](https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/netting-statements-in-financial-transactions/td-p/2656532)). **MD:** Exchange agreement ID, partner dual role (customer+vendor), product pair equivalence (e.g., CBOB↔RBOB with octane adjust), location pair, imbalance tolerance, settlement frequency, fee schedule, tax handling method, imbalance price index. |
| **A4 Channel Contract Archetypes** | Instantiate legal/commercial templates per channel with correct title, inventory ownership, and fee models. | **Retail:** dealer-owned vs lessee-dealer vs commission agent changes who owns inventory and who is merchant of record ([C-Store Trader](https://www.cstoretrader.com/guides/dealer-vs-lessee-dealer-vs-commission/)); consignment stations track supplier-owned inventory at site ([Petrosoft](https://help.petrosoftinc.com/Content/Station_Home/Station_Options/consigned_station.htm); [Petro-Data consignment](http://www.petrodatainc.com/S7CONS.PDF)). **Aviation:** into-plane MSA + airport authority permits. **Marine:** bunker GT&C + stem confirmation. **Lubes:** SPA with OEM approval lists. **MD:** Contract type code, title transfer rule (FCA rack / DAP tank / into-wing / FOB barge), inventory ownership flag, brand license, rebate table, SLA KPIs. |
| **A5 Volume Commitment & Allocation Admin** | Administer MVCs, ratable lifts, allocation during supply disruption, and force majeure notices. | Downstream allocation is often terminal- and grade-specific (e.g., ULSD vs B5, winter RVP gasoline). Pipeline batch calendars and terminal inventory constrain call-offs. **MD:** Commitment volume by period/grade/location, ratability band, allocation priority class, FM clause ID, substitution rules (grade give/take). |

### 3.B Credit & Risk Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **B1 Multi-Dimensional Exposure** | Continuously compute counterparty exposure across booked, lifted-unbilled, open AR, disputed, and contingent tax. | Rack customers can lift continuously on card authorization; exposure spikes on weekends/holidays before invoicing. Formula-priced volumes create MTM risk vs index. Unbilled BOL tickets are material. **MD:** Exposure segments (product family, terminal region), unbilled aging buckets, MTM curve source, tax contingency flag, parent/child exposure roll-up. |
| **B2 Collateral & Prepay Controls** | Manage LC, cash deposit, surety, parent guarantee; auto-switch to prepay when limit breached. | Motor fuel dealers and jobbers often require bonds for tax liabilities in addition to trade credit. **MD:** Instrument type, expiry, evergreen flag, covered entities, drawdown rules. |
| **B3 KYC / Sanctions / Licensing** | Screen counterparties; validate fuel reseller / aviation / marine licenses. | Resellers may need IRS 637 registration / state supplier licenses to purchase tax-free or at rack. Dyed diesel purchasers need proper exemption documentation ([26 CFR §48.4082-1](https://www.law.cornell.edu/cfr/text/26/48.4082-1); [MO clear/dyed requirements](https://dor.mo.gov/taxation/business/tax-types/motor-fuel/documents/Tax-Requirements-of-Clear-and-Dyed-Diesel-Motor-Fuel.pdf)). **MD:** License type/jurisdiction/expiry, 637 status, exemption cert ID, screening list version, beneficial owner. |
| **B4 Payment Term Risk by Channel** | Align terms with lift velocity and fraud patterns. | Rack ACH short cycle vs aviation monthly airline settlements vs marine stem letters of indemnity. Card-not-present rack fraud controls. **MD:** Default terms by channel, hard-block vs soft-warn, dual control thresholds. |
| **B5 Multi-Gate Credit Release** | Enforce credit at quote, order save, load-authorize (TAS), and invoice release. | TAS load authorization is a real-time credit gate—failure mode is truck turned away at rack. **MD:** Release hierarchy, override authority matrix, real-time interface SLA to TAS. |

### 3.C Order Management & Fulfillment

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **C1 Multi-Channel Order Capture** | Capture executable demand with complete logistics & tax attributes. | Order types: rack spot, rack contract call-off, C&I delivery order, VMI auto-replenishment, aviation flight plan uplift, marine stem, lube sales order, retail tank replenishment, exchange lift. SAP MCOE-style downstream order features include plant determination, item category redetermination, contract call-off restrictions, final delivery indicator ([SAP IS-Oil training outline](https://www.proexcellency.com/products/sap-is-oil-gas-online-training)). **MD:** Order type, contract reference, ship-to tank ID, product grade + additive, tax status (taxable/exempt/dyed), requested UoM, carrier preference, driver card. |
| **C2 Nomination, Appointment & Slotting** | Reserve terminal/pipeline/marine capacity and time windows. | Rack appointments reduce congestion; pipeline nominations per cycle; marine berth/barge windows; airport hydrant/into-plane slots. TSW nominates and schedules hydrocarbon movements with QCI-aware quantities ([SAP TSW](https://help.sap.com/docs/SUPPORT_CONTENT/isoil/3139386109.html)). **MD:** Nomination cycle ID, appointment slot, batch ID, vessel IMO, voyage number, flight number/tail. |
| **C3 Secondary Distribution Execution (TD)** | Plan and execute bulk truck delivery from terminal/depot to customer tank or station. | Multi-compartment trucks; product sequencing to avoid contamination; seal numbers; delivery ticket with compartment-level temp/density; split drops; night deliveries. SAP IS-Oil TD is the classic secondary distribution construct ([ResolveTech SAP S/4 Downstream](https://resolvetech.com/sap-s4hana-downstream-oil-and-gas/)). **MD:** Vehicle ID, compartment map, trailer capacity, driver HOS, delivery sequence, geofence, stick reading method. |
| **C4 Terminal Automation & BOL** | Authorize load, control valves/meters, capture ticket, print/transmit BOL. | TAS enforces PIN/card, preset quantity, product arm, additive injection, overfill protection; issues BOL/meter ticket consumed by ERP billing ([Emerson TerminalManager](https://www.emerson.com/documents/automation/terminalmanager-en-186128.pdf); [BOL automation](https://mangancontinuity.com/bill-of-lading-automation/)). **MD:** Badge/PIN, preset mode (gross/net), additive recipe, meter ID, BOL number range, seal range, carrier SCAC. |
| **C5 Allocation & Availability** | Constrain orders to physical bookable inventory and allocation rules. | Book-stock vs physical tank gauge; pipeline in-transit; exchange receipts due; biofuel blendstock availability; RVP seasonal cutover. **MD:** ATP rules, allocation quota, blend recipe constraints, seasonal grade calendar. |

### 3.D Invoicing & Billing

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **D1 Ticket-to-Invoice Automation** | Transform custody documents into AR invoices with minimal manual touch. | Invoice basis documents: rack meter ticket/BOL, bulk delivery ticket, aviation uplift ticket, marine BDN, retail POS gallon summary, exchange LIA. Payment often references ticket/BOL copy ([QT agreement](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf)). BDN is both MARPOL compliance artifact and commercial quantity document ([ExxonMobil BDN](https://www.exxonmobil.com/en/marine/technicalresource/marine-resources/bunker-delivery-notes); [Vesselchain BDN guide](https://vesselchain.org/bunker-delivery-note-guide-2025/)). **MD:** Billing document type by channel, copy control from delivery/ticket, alternate quantity fields (GOV/GSV/NSV/mass), external ticket ID. |
| **D2 Multi-Component Billing** | Bill product energy/volume plus ancillary commercial components. | Components: product, freight, stop-off, demurrage/detention, into-plane service fee, throughput/terminaling fee, additive, dye, bio blend premium, environmental fees, airport concession fees. Aviation invoices commonly mix fuel + FBO/handler fees and require line-level reconciliation ([Aviation invoice reconciliation](https://invoicedataextraction.com/blog/aviation-fuel-invoice-reconciliation)). **MD:** Condition types, account assignment, fee rate tables by airport/port/terminal, currency, taxability per component. |
| **D3 Excise, Motor Fuel & Indirect Tax** | Determine, invoice, remit, and report complex fuel taxes; manage exemptions and dyed product. | Federal/state motor fuel tax stacks; dyed diesel/kerosene exempt from certain highway taxes if properly dyed and documented ([26 CFR §48.4082-1](https://www.law.cornell.edu/cfr/text/26/48.4082-1)); nontaxable use credits for undyed fuel in off-highway use ([IRS Fuel Tax Credit](https://www.irs.gov/credits-deductions/businesses/fuel-tax-credit)); state-by-state regimes ([FTA motor fuel book](https://taxadmin.org/wp-content/uploads/resources/motor-fuels/motor-fuel-state.book_.pdf)). Origin vs destination basis; rack vs retail collection points; aviation and marine special regimes. **MD:** Tax jurisdiction chain, product tax class (clear ULSD, dyed ULSD, gasoline RVP class, Jet-A, MGO, VLSFO), exemption cert, dye indicator, IRS 637, point-of-taxation rule, filing entity. |
| **D4 Exchange Differential & LIA Billing** | Settle imbalances, fees, and quality give-and-take on partner exchanges. | After physical lifts both ways, net quantity differences are invoiced; tax postings must mirror product movements; LIA adjusts book positions ([SAP EXG](https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/exchange-borrow-loan-invoice-the-difference-quantity-after-lia/m-p/7554007)). **MD:** Imbalance UoM, settlement price rule, fee per barrel moved, tax reverse-charge flags. |
| **D5 Cycle / Consignment / Commission Settlement** | Run periodic settlements where classic “invoice per delivery” is insufficient. | Commission agents: settle commission on gallons sold, not title transfer at rack. Consignment: bill on retail sell-through or tank withdrawal. Lube rebates and brand image funds. **MD:** Settlement calendar, POS source system ID, commission rate table, shrink allowance, sell-through cut-off. |

### 3.E Receipt & Collection

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **E1 Intelligent Cash Application** | Match remittances to invoices using hydrocarbon document keys. | Remittance advice often cites BOL numbers, ticket IDs, load dates, or BDN numbers rather than invoice numbers—matching engine must use these alternate keys. **MD:** Matching key priority, tolerance (value & volume), auto-write-off limit. |
| **E2 Payment Rail Orchestration** | Execute ACH debit, wire, card, lockbox, retail sweep. | Rack agreements may mandate ACH debit on due date ([QT](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf)). Retail dealer sweeps and card settlements (fleet cards, network cards). **MD:** Bank account, mandate ID, payment method per payer, retry rules, NSF handling. |
| **E3 Partner Netting** | Offset AR/AP across exchange and dual-role counterparties. | Netting statements consolidate buy/sell and exchange fees into single cash movement ([SAP netting](https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/netting-statements-in-financial-transactions/td-p/2656532)). **MD:** Netting agreement, eligible document types, close calendar, residual cash threshold. |
| **E4 Deduction Management** | Capture short-pays with structured reason codes and workflow. | Typical deductions: temperature/quantity, quality, tax overcharge, freight, demurrage counterclaim, retail promo. **MD:** Reason taxonomy, evidence checklist (ticket, COA, gauge), owner role. |
| **E5 Suspense & Unapplied Cash** | Clear unidentified receipts quickly given high ticket volumes. | High-volume rack produces many small invoices; unapplied cash ages into credit risk noise. **MD:** Suspense GL, aging SLA, research work queue. |

### 3.F Dispute Management

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **F1 Quantity / Measurement Dispute** | Investigate variance between billed NSV and customer claim. | Root causes: wrong observed temperature, density/API gravity, meter factor, VCF table version, air vs vacuum mass, shore vs ship figures, foaming/entrained air, stick vs meter. Resolution path: retrieve TAS ticket raw data → re-run QCI (API MPMS 11.1 / ASTM D1250) → meter proving records → issue credit/rebill ([ASTM D1250](https://www.astm.org/d1250-19e01.html); [API MPMS catalog](https://www.api.org/-/media/files/publications/2024-catalog/2024-petroleum-measurement.pdf)). **MD:** Ticket raw observations (TOV/GOV, temp, pressure, density), VCF version, meter factor, proving certificate ID. |
| **F2 Quality / Spec Dispute** | Handle off-spec claims (octane, sulfur, water, flash, viscosity, FAME%, cold properties). | COA vs actual; pipeline contamination; wrong additive; bio blend stratification. May trigger product return, regrade, or price adjustment (e.g., octane giveaway). Blending economics and octane/RVP constraints are first-class ([Mines blending notes](https://people.mines.edu/jjechura/wp-content/uploads/sites/120/2019/02/CBEN409_11_Blending_Optimization-1.pdf); [Platts blend value](https://www.spglobal.com/energy/en/pricing-benchmarks/our-methodology/subscriber-notes/050126-platts-launches-new-gasoline-blend-value-calculations-in-us)). **MD:** Spec limits per grade/season/jurisdiction, COA ID, lab method (ASTM), retention sample ID. |
| **F3 Price / Index Dispute** | Resolve incorrect index, differential, effective date, or UoM conversion. | Common: used gross vs net gallons; wrong OPIS rack average; holiday publication; currency. **MD:** Index snapshot store (immutable), contract price procedure version, calculation audit log. |
| **F4 Tax Dispute & Rebill** | Correct taxability, exemption, or jurisdiction errors. | Dyed product sold as clear (or reverse); missing exemption cert; wrong destination state on drop; aviation vs highway use. May require amended returns. **MD:** Cert image, effective dates, use-type code, amended return flag. |
| **F5 Logistics Service Claims** | Demurrage, detention, no-show appointment, into-plane delay, stem short-delivery. | Marine demurrage and airport delay penalties are high-value. **MD:** Laytime terms, NOR timestamps, appointment actuals, reason codes. |

### 3.G Customer Retention & Contract Performance

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **G1 Utilization & Uplift Analytics** | Track actual vs committed volumes by grade/location. | Terminal share of wallet; rack lift patterns; aviation airport coverage. Feeds KPI Store candidates (contract attainment, lost lift). **MD:** Commitment baseline, actual NSV, weather/force majeure flags. |
| **G2 Rebate / Brand / Incentive True-Up** | Calculate volume rebates, image funds, dealer incentives. | Retail brand networks: cents-per-gallon rebates, co-op advertising. Fleet card incentives. **MD:** Program ID, accrual rate, clawback rules. |
| **G3 Network Health (Retail)** | Monitor dealer financial stress, station downtime, brand compliance. | Early-warning for credit and churn. **MD:** Station status, mystery shop scores, out-of-fuel events. |
| **G4 OTIF & Service Level** | Measure on-time-in-full by channel with hydrocarbon definitions of “full.”** | “Full” means within measurement tolerance of ordered NSV, correct grade, correct tax status. **MD:** Tolerance band, grade substitution policy. |
| **G5 Renewal & Index Roll** | Manage contract end-of-term and index basis changes. | Seasonal grade changes force reprice; regulatory sulfur/RVP changes. **MD:** Renewal workflow, notice period, new index mapping. |

### 3.H Master Data Management (O2C-Critical Domains)

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **H1 Party & Account Topology** | Govern sold-to, ship-to, bill-to, payer, end-use consumer, dealer of record. | One legal entity may lift at 50 terminals; one payer may cover 200 stations; aviation needs airline + handler + airport. **MD:** Hierarchy, tax ID, licenses, credit link, EDI endpoint. |
| **H2 Product / Spec / Tax Class** | Maintain hydrocarbon and packaged product masters with dual UoM and taxability. | Fuels: base grade, oxygenate, RVP class, sulfur class, biodiesel %; lubes: viscosity, OEM spec; marine: ISO 8217 grade, sulfur. HPM dynamic conversion parameters. **MD:** Material, base UoM, alternate UoM, density defaults, QCI group, tax class, dangerous goods. |
| **H3 Location Topology** | Terminal, rack, bay, tank, depot, station, airport hydrant, port berth. | Inventory ownership can differ by tank (throughput customer stock vs company stock). **MD:** Plant/SLoc/tank, latitude/longitude, jurisdiction, TAS system ID. |
| **H4 Exchange & Book Structures** | Partner agreements and logical inventory books. | Book-out chains; location swaps. **MD:** Agreement, book ID, imbalance GL. |
| **H5 Logistics Asset Masters** | Carriers, drivers, trailers, compartments, cards, vessels, aircraft. | Load control depends on valid card/PIN and compartment cleanliness certification. **MD:** Asset ID, certifications, blacklist status. |

### 3.I Governance, Controls & Compliance

| L2 Process Name | Definition & Core Business Activities | Downstream O&G Specifics & Master Data Attributes |
| :--- | :--- | :--- |
| **I1 Measurement Governance** | Own standards, meter proving cadence, VCF software versions. | API MPMS chapters cover vocabulary, tanks, metering, proving, marine measurement, and quantity calculation (Ch. 12 NSV concepts) ([API catalog](https://www.api.org/-/media/files/publications/2024-catalog/2024-petroleum-measurement.pdf)). **MD:** Standard version, proving schedule, software adjunct version for D1250. |
| **I2 Pricing Authority Controls** | Segregate who can change rack postings vs contract differentials. | Rack price sheets change multiple times per day; controls against unauthorized overrides. **MD:** Approval matrix, price freeze windows. |
| **I3 Tax & Excise Compliance** | Filing, remittance, dye compliance, exemption audit. | Civil/criminal exposure for misuse of dyed fuel ([MO guidance](https://dor.mo.gov/taxation/business/tax-types/motor-fuel/documents/Tax-Requirements-of-Clear-and-Dyed-Diesel-Motor-Fuel.pdf)). **MD:** Filing calendar, return mapping from invoice tax lines. |
| **I4 Revenue Recognition / Title Controls** | Align billing and revenue with Incoterms and custody events. | Title at flange vs destination tank changes cut-off. Exchange imbalances are not “sales” until settled. **MD:** Title rule code, cut-off calendar. |
| **I5 O2C Data Product Stewardship** | Define quality rules for tickets, invoices, exposure feeds into KPI Store. | Ticket completeness (temp, density, VCF) is a data product SLA, not optional. **MD:** DQ rules, lineage to TAS/ERP, steward RACI. |

### 3.3 Cross-Cutting Physical Measurement Baseline (applies to C–F)

| Concept | Definition in Downstream O2C | Typical Master / Transaction Attributes |
| :--- | :--- | :--- |
| **GOV (Gross Observed Volume)** | Volume at observed temperature/pressure, including free water as applicable per method | Observed temp, pressure, meter reading, tank gauge |
| **GSV (Gross Standard Volume)** | GOV corrected by VCF (CTL/CPL) to standard conditions (e.g., 60°F / 15°C) | VCF, CTL, CPL, reference density |
| **NSV (Net Standard Volume)** | GSV minus sediment & water (S&W) or other deductions per contract/API Ch.12 practice | S&W %, NSV, method |
| **Mass / Weight** | Often used in marine and some pipeline; air vs vacuum basis must be explicit | Density, weight factor, vacuum/air flag |
| **QCI** | System interface/engine performing dynamic hydrocarbon quantity conversion for ERP postings | Material/plant/SLoc/batch conversion data ([SAP QCI](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/0f4ab800d01c4366b0c9aaff06a64320/40ea5e9072ae42119c3425a9f9294d5f.html)) |
| **Standard conditions** | Contractual basis for “net gallon” / “net barrel” — commonly 60°F US ([QT barrel definition](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf)) | Std temp/pressure profile ID |

---

## SECTION 4: SYSTEM LANDSCAPE & INTEGRATION ARCHITECTURE

### 4.1 Target-State Logical Architecture (ASCII)

```
                    ┌──────────────────────────────────────────────────────────┐
                    │  EXPERIENCE & COMMERCIAL EDGE                             │
                    │  CRM / CPQ / Dealer Portal / Customer Portal / Mobile      │
                    │  Aviation Ops Portal · Marine Stem Desk · Lube B2B Shop    │
                    └───────────────┬─────────────────────────────┬─────────────┘
                                    │ quotes, contracts, orders   │ claims, self-service
                                    ▼                             ▼
┌──────────────┐    ┌──────────────────────────────────────────────────────────┐    ┌──────────────────┐
│ Market Data  │    │              CORE COMMERCIAL ERP / INDUSTRY SOLUTION      │    │ Credit / Treasury │
│ Platts/OPIS/ │───▶│  SD/O2C · IS-Oil (HPM, TSW, TD, EXG, TDP) or equivalent  │◀──▶│ Limit · Collateral│
│ Argus · NYMEX│    │  Pricing engine · Billing · AR · Netting · Exchanges      │    │ Sanctions · KYC   │
└──────────────┘    └───────────┬───────────────┬───────────────┬───────────────┘    └──────────────────┘
                                │               │               │
           nominations/orders   │               │ invoices      │ settlements
                                ▼               │               ▼
┌───────────────────────────────────────────────┼──────────────────────────────────────────────────────┐
│  LOGISTICS & CUSTODY FABRIC                   │                                                      │
│  ┌─────────────────────┐  ┌──────────────────▼──────────┐  ┌─────────────────────────────────────┐ │
│  │ Terminal Automation │  │ Secondary Distribution / TMS │  │ Fleet Telemetry / VMI / ATG        │ │
│  │ System (TAS)        │  │ Bulk truck · routing · TD    │  │ Tank gauges · pump totalizers      │ │
│  │ Load control · BOL  │  │ Delivery ticket · seals      │  │ eVMI auto-replenishment            │ │
│  │ Additive · cardlock │  └──────────────────────────────┘  └─────────────────────────────────────┘ │
│  └──────────┬──────────┘                                                                            │
│             │ tickets / inventory                                                                   │
│  ┌──────────▼──────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐ │
│  │ Pipeline SCADA /    │  │ Aviation Fueling / FBO      │  │ Marine Bunkerting · Barge · BDN    │ │
│  │ Nomination systems  │  │ Into-plane · uplift tickets │  │ Mass flow · MARPOL docs            │ │
│  └─────────────────────┘  └─────────────────────────────┘  └─────────────────────────────────────┘ │
└────────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                     │ custody events (ticket, BDN, uplift, gauge)
                                     ▼
                    ┌──────────────────────────────────────────────────────────┐
                    │  MEASUREMENT & QUALITY                                    │
                    │  QCI / QuantityWare / OpenTAS QCM · LIMS · COA · Proving  │
                    │  API MPMS 11.1 / ASTM D1250 VCF engines                    │
                    └──────────────────────────┬───────────────────────────────┘
                                               │ corrected NSV + quality
                                               ▼
┌──────────────────┐    ┌──────────────────────────────────────────────────────┐    ┌──────────────────┐
│ Indirect Tax     │◀──▶│  FINANCE & COMPLIANCE CORE                            │───▶│ Bank / Payment   │
│ Engine           │    │  GL · AR · AP netting · Excise returns · SOX controls │    │ ACH · Wire · Card│
│ Vertex/Sabrix/   │    └──────────────────────────┬───────────────────────────┘    └──────────────────┘
│ custom fuel tax  │                               │
└──────────────────┘                               ▼
                    ┌──────────────────────────────────────────────────────────┐
                    │  DATA / ANALYTICS / EPM                                   │
                    │  Ticket & Invoice Data Products · KPI Store · Power BI    │
                    │  Credit exposure cubes · OTIF · Dispute aging             │
                    └──────────────────────────────────────────────────────────┘
```

Industry platforms emphasize ERP integration of terminal/pipeline O2C, inventory visibility, and month-end acceleration ([Emerson O2C](https://www.emerson.com/en/automation-systems/advanced-industry-software/oil-and-gas/software-for-energy-transportation-storage/order-to-cash-software)). SAP S/4 Downstream industry solutions package refining-to-distribution processes including TSW/TD/HPM constructs ([ResolveTech](https://resolvetech.com/sap-s4hana-downstream-oil-and-gas/)). VMI solutions close the loop from tank telemetry to automated ordering ([Shell eVMI](https://www.shell.com/business-customers/commercial-fuels/evmi.html); [Fox Insights VMI](https://www.foxinsights.ai/en/resources/what-is-vmi-fuel-distribution)).

### 4.2 Critical Real-Time / Near-Real-Time Integration Points

| # | Integration | Pattern | Latency Target | Payload Essentials | Failure Mode if Broken |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **CRM/CPQ → ERP Contract** | Event / batch | Minutes–hours | Contract ID, price procedure, ship-to slate, credit terms | Orders blocked or wrong price |
| 2 | **Market Data → Pricing** | Scheduled feed + snapshot store | Multiple/day | Index ID, timestamp, value, UoM | Systematic misbills; disputes |
| 3 | **ERP Order → TAS Authorization** | Real-time sync/async | Seconds | Order/preset, customer card, product, max qty, credit token | Truck denied at rack; lost lift |
| 4 | **TAS → ERP Delivery/Ticket** | Real-time event | Seconds–minutes | BOL#, meter tickets, GOV, temp, density, additive, seals, driver | Unbilled lifts; inventory mismatch |
| 5 | **Ticket → QCI Engine → ERP Goods Issue** | Inline sync | Seconds | Observed values in; NSV/mass out | Wrong inventory & COGS |
| 6 | **ATG/VMI → Order Management** | Event + forecast | Minutes–hourly | Tank ID, gross/net level, ullage, rate of consumption | Run-outs or overfills |
| 7 | **TD Mobile → ERP Proof of Delivery** | Event | Minutes | Compartment qty, temp, stick before/after, GPS, signature | Billing delay; theft risk |
| 8 | **Into-Plane System → Billing** | Event | Minutes | Uplift ticket, flight/tail, gallons/liters, density, fee codes | Airline reconciliation breaks |
| 9 | **Marine BDN → ERP + Document Archive** | Event + eBDN | Minutes | BDN#, mass/volume, sulfur, viscosity, barge ID, timestamps | MARPOL + commercial exposure |
| 10 | **ERP Billing → Tax Engine** | Inline | Seconds | Ship-from/to, product tax class, exemptions, dye flag | Incorrect excise; filing error |
| 11 | **ERP AR → Credit Engine** | Near real-time | Minutes | Open items, unbilled tickets, disputes | Over-limit lifts |
| 12 | **AR → Bank ACH Debit** | Scheduled | Daily | Invoice list, mandate, amount | Cash delay; NSF cascade |
| 13 | **EXG Balances → Netting** | Period batch | Daily/weekly | Dual postings, fees, tax | Working capital leakage |
| 14 | **POS/Station → Consignment Settlement** | Shift/daily | Hours | Pump totalizer, grade mix, price book | Shrink and revenue leakage |
| 15 | **O2C Events → EPM Data Products** | Stream/CDC | Near real-time | Normalized ticket/invoice/exposure facts | Blind KPI Store / bad decisions |

### 4.3 Integration Control Requirements

1. **Immutable ticket store** — raw TAS observations retained even after QCI recalculation.
2. **Exactly-once billing keys** — BOL/ticket unique constraints prevent double bill.
3. **Clock sync** — terminal, ERP, and bank cut-offs aligned to contract time zones (often Central for US rack).
4. **Credit token expiry** — TAS auth tokens short-lived to prevent stale approvals.
5. **Tax determination audit** — every invoice line stores full jurisdiction and cert reference.
6. **Index snapshot immutability** — price disputes require as-published frozen values, not live re-query.

---

## SECTION 5: DOWNSTREAM OPERATIONAL EXCEPTIONS & RISK MANAGEMENT

### 5.1 Exception Catalog (Critical Edge Cases)

#### Exception 1 — Temperature / VCF Quantity Variance (Rack or Bulk)

**Scenario.** Customer ordered 8,000 gross gallons. Hot summer rack meter tickets 8,000 GOV at 92°F. Billed NSV after VCF is ~7,900 gallons. Customer short-pays the “missing” 100 gallons, claiming meter error.

**O2C resolution path.**

1. **Capture:** Deduction reason code *QTY-TEMP* linked to invoice and BOL#.
2. **Evidence pack:** TAS ticket (observed temp, API gravity/density, meter ID), VCF engine version (API MPMS 11.1 / ASTM D1250), contract clause stating net gallons @60°F ([ASTM D1250](https://www.astm.org/d1250-19e01.html); [QT barrel @60°F](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf)).
3. **Re-perform QCI** with stored raw observations; compare to billed NSV.
4. **If calculation correct:** Issue formal dispute denial with calculation worksheet; collect residual; educate counterparty.
5. **If meter/temp probe fault:** Pull proving/calibration records; credit NSV difference; open maintenance notification; evaluate prior lifts on same meter (systematic bias).
6. **Control uplift:** Dashboard of GOV–NSV spreads by terminal/meter; DQ rule requiring temp/density on every ticket before billing release.

#### Exception 2 — Dyed vs Clear Diesel Tax Misclassification

**Scenario.** C&I construction customer entitled to dyed ULSD for off-road equipment is loaded with clear ULSD due to wrong product arm / order tax status. Invoice includes highway excise; customer refuses tax portion. Alternatively, dyed product is diverted to highway use—regulatory violation.

**O2C resolution path.**

1. **Detect:** Tax engine vs product dye indicator mismatch; or state inspection notice.
2. **Quarantine AR tax lines**; freeze further lifts on that ship-to until cert/product status validated ([26 CFR §48.4082-1](https://www.law.cornell.edu/cfr/text/26/48.4082-1); [MO dyed fuel guidance](https://dor.mo.gov/taxation/business/tax-types/motor-fuel/documents/Tax-Requirements-of-Clear-and-Dyed-Diesel-Motor-Fuel.pdf)).
3. **If supplier error (clear sold when dyed ordered):** Arrange product swap or credit tax + price differential; file amended tax return if remitted; RCA on TAS product mapping and order default tax class.
4. **If customer misuse of dyed:** Escalate to compliance; potential report; terminate dyed eligibility; rebill tax where legally required.
5. **Master data fix:** Ship-to default product slate, exemption cert effective dating, driver training flags on BOLs (“NONTAXABLE USE ONLY” legends).
6. **Preventive control:** Two-person rule for tax class overrides; cert expiry blocking in order entry.

#### Exception 3 — Exchange Imbalance & Netting Break

**Scenario.** Partner exchange at two terminals: Company A lifts 50 kbbl gasoline at Partner terminal; Partner lifts 47 kbbl at Company terminal in the month. Fees and tax treatments differ by state. Month-end imbalance invoice disagrees by volume and tax.

**O2C resolution path.**

1. **Reconcile operational tickets both ways** to exchange book (not just GL).
2. **Apply LIA** for identified gains/losses and measurement tolerances ([SAP EXG/LIA](https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/exchange-borrow-loan-invoice-the-difference-quantity-after-lia/m-p/7554007)).
3. **Price residual imbalance** per agreement index + location differential.
4. **Tax alignment:** Ensure each physical lift carried correct origin/destination tax; imbalance settlement may be financial-only without second tax event—per agreement and counsel.
5. **Generate netting statement** combining AR/AP and fees into one cash move ([SAP netting](https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/netting-statements-in-financial-transactions/td-p/2656532)).
6. **Dispute slice:** Volume vs fee vs tax separated—never net into a single opaque “misc” deduction.
7. **Control:** Weekly exchange balance dashboard with tolerance breach alerts before month-end cliff.

#### Exception 4 — Aviation Uplift Ticket vs Airline Operational Log Mismatch

**Scenario.** Into-plane agent bills 12,450 USG Jet-A for flight XX123 tail Nxxx. Airline operations log shows 12,100 USG. Service fees and airport concession fees also differ.

**O2C resolution path.**

1. **Match keys:** Flight number, tail, date/time window, airport ICAO, ticket number ([Aviation invoice reconciliation](https://invoicedataextraction.com/blog/aviation-fuel-invoice-reconciliation)).
2. **Retrieve** hydrant/truck meter ticket, density/temp, and fueler signature; compare to aircraft fuel slip.
3. **Split dispute:** energy/volume vs into-plane service fee vs third-party airport fees.
4. **If under-delivery proven:** Credit volume; review whether defuel/refuel or meter jump occurred; check for shared hydrant allocation errors.
5. **If airline log incomplete:** Provide ticket image pack; enforce contractual meter primacy clause.
6. **Process fix:** Require electronic uplift capture with photo of aircraft gauge/fuel slip; SLA for ticket transmission < X minutes after disconnect.
7. **Credit impact:** Unbilled/disputed aviation volumes remain in exposure until closed.

#### Exception 5 — Marine BDN Quantity Challenge (Ship vs Barge Figures)

**Scenario.** Barge delivers VLSFO; BDN shows 1,500.000 MT. Vessel chief engineer claims 1,472 MT by ship tank measurement. Buyer short-pays and threatens off-spec claim on viscosity/sulfur.

**O2C resolution path.**

1. **Secure documents:** BDN (including mandatory MARPOL fields), meter or tank calc sheets, COA, seal numbers, timestamps, NOR/SOF ([ExxonMobil BDN](https://www.exxonmobil.com/en/marine/technicalresource/marine-resources/bunker-delivery-notes); [BDN guide](https://vesselchain.org/bunker-delivery-note-guide-2025/)).
2. **Determine contractual measurement hierarchy** (mass flow meter vs barge tanks vs ship tanks) and whether surveyor was called.
3. **Quantity path:** Recompute with correct density in air/vacuum basis; check list/trim corrections; confirm no pipeline content double-count.
4. **Quality path:** Retain sample per MARPOL; if sulfur out of spec, initiate non-conformance—may trigger fuel replacement, speed claims, or rejection independent of quantity.
5. **Commercial settlement:** Issue credit note / debit note; update stem file; demurrage if delay from dispute at berth.
6. **Preventive:** Prefer calibrated mass flow meters; independent surveyor triggers at threshold; eBDN integration to ERP to avoid re-key errors.
7. **Accounting:** Accrue revenue at provisional BDN; true-up post-survey within close calendar.

#### Exception 6 (Bonus) — Retail Consignment Shrink & Commission Settlement Gap

**Scenario.** Commission-agent station shows pump totalizer sales exceeding tank truck drops + opening stock by 1.8% for the month (beyond shrink allowance). Dealer claims supplier short-dropped; supplier claims theft or meter drift.

**O2C resolution path.**

1. Confirm **inventory ownership model** (consignment vs dealer-owned) ([C-Store Trader](https://www.cstoretrader.com/guides/dealer-vs-lessee-dealer-vs-commission/); [Petrosoft consignment](https://help.petrosoftinc.com/Content/Station_Home/Station_Options/consigned_station.htm)).
2. Reconcile: opening stick/ATG + BOL drops − closing ATG − metered sales = shrink.
3. Validate compartment delivery tickets (temp-corrected) and ATG calibration.
4. If supplier short-drop: credit inventory and adjust commission base.
5. If station loss: charge dealer per contract shrink clause; potential security review; credit limit rethink.
6. Settlement run: commission on *authorized* gallons only; hold payment until variance cleared.
7. Control: weekly ATG vs book variance alerts; sealed drop SOP; camera on tank fills.

### 5.2 Risk-to-Control Matrix (Summary)

| Risk | Primary Chevron | Preventive Control | Detective Control | Corrective Path |
| :--- | :--- | :--- | :--- | :--- |
| Mismeasured volume | 5–6 | Proving + QCI governance | GOV–NSV analytics | Rebill/credit + meter work order |
| Excise misclassification | 3–6 | Cert & dye hard-stops | Tax exception reports | Amend + rebill |
| Credit overrun at rack | 2–4 | Real-time TAS credit token | Unbilled exposure aging | Block card; collect; revise limit |
| Exchange book break | 4–7 | Dual-entry ticket to EXG book | Weekly imbalance dashboard | LIA + netting true-up |
| Aviation/marine doc mismatch | 5–6 | e-ticket/eBDN mandatory fields | Auto match to ops logs | Survey + credit note |
| Retail shrink | 4–7 | Sealed drops + ATG | Variance > threshold alert | Chargeback / police / process fix |
| Index price error | 1,6 | Immutable snapshots | Price variance vs prior day | Auto reprice job + notify |
| Double billing ticket | 6 | Unique external ticket key | Duplicate detection job | Void/credit immediately |

---

## APPENDIX A: Channel-Specific O2C Swim Narratives

### A.1 Wholesale Rack (Jobber / Reseller)

1. Credit-approved customer receives rack access + cards.
2. Driver arrives; TAS validates card, order/preset, product, credit.
3. Load with additive/dye as ordered; meter ticket + BOL issued.
4. ERP ingests ticket; QCI computes NSV; tax engine applies rack origin stack.
5. Price from contract (posted rack or OPIS mean ± differential).
6. Invoice + ticket/BOL to customer; ACH debit on due date ([QT](https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf); [OPIS](https://www.opis.com/blog/wholesale-rack-fuel-pricing-essentials/)).
7. Exceptions: wrong product, overfill, card fraud, tax license lapse.

### A.2 B2B C&I with VMI

1. ATG telemetry streams tank inventory ([Shell eVMI](https://www.shell.com/business-customers/commercial-fuels/evmi.html)).
2. Forecasting creates delivery proposals; planner confirms.
3. TD bulk truck loads at terminal (company or exchange stock).
4. On-site drop with before/after gauge; delivery ticket signed.
5. Bill product + freight; destination tax; possible pump-out fees.
6. Collect on negotiated terms; disputes on stick vs meter.

### A.3 Retail Network

1. Station forecast / low-tank alert.
2. Brand/supplier delivers under dealer or consignment terms.
3. POS sells to motorists; shift close sends totals.
4. Settlement: wholesale invoice and/or commission statement + rebate accruals.
5. Cash collection via sweep or dealer payment; card network settlement separate.
6. Shrink and pricebook compliance managed continuously.

### A.4 Lubricants

1. Quote by SKU pack size and OEM approval.
2. Warehouse pick/pack or bulk fill; COA if required.
3. Ship via parcel/LTL; POD.
4. Invoice with freight and any core/deposit.
5. Returns and shelf-life exceptions common relative to fuels.

### A.5 Aviation Into-Plane

1. Airline schedule / ad-hoc release to into-plane agent.
2. Fueler uplifts; ticket captures aircraft ID, quantity, density, time.
3. Bill fuel formula price + into-plane fee + airport fees.
4. Airline reconciles tickets to flight ops ([reconciliation practice](https://invoicedataextraction.com/blog/aviation-fuel-invoice-reconciliation)).
5. Disputes split volume vs fees; credit exposure until match.

### A.6 Marine Bunker

1. Stem confirmation (grade, sulfur, quantity, port, window, price).
2. Barge alongside; deliver against nomination.
3. BDN issued—commercial + statutory ([ExxonMobil](https://www.exxonmobil.com/en/marine/technicalresource/marine-resources/bunker-delivery-notes)).
4. Invoice on BDN quantity/quality; collect per GT&C (often very short terms or security).
5. Quantity/quality claims via surveyor; demurrage parallel track.

---

## APPENDIX B: Suggested O2C Data Products (for EPM / KPI Store linkage)

| Data Product | Grain | Key Measures | Primary Sources |
| :--- | :--- | :--- | :--- |
| **Custody Ticket Fact** | 1 ticket line | GOV, GSV, NSV, mass, temp, density | TAS, TD mobile, into-plane, BDN |
| **Commercial Invoice Fact** | 1 invoice line | Extended price, tax, freight, fees | ERP billing |
| **Unbilled Lift Fact** | 1 ticket not yet invoiced | NSV, estimated value, age hours | TAS vs ERP match |
| **Credit Exposure Snapshot** | Payer × day | AR, unbilled, disputed, MTM | AR + tickets + credit |
| **Exchange Balance Fact** | Agreement × product × loc × day | In, out, imbalance | EXG book |
| **Tax Line Fact** | Invoice tax line | Jurisdiction, rate, dye flag, cert | Tax engine |
| **Dispute Case Fact** | Case × reason | Amount, volume, cycle time | Dispute system |
| **Contract Attainment Fact** | Contract × period | Committed vs actual NSV | Contract + tickets |

These are **data products / measures**, not automatically KPIs. Promotion to the KPI Store requires objective, owner, target, threshold, and action per EPM measurement classification rules.

---

## APPENDIX C: Glossary (Downstream O2C)

| Term | Meaning |
| :--- | :--- |
| **BOL** | Bill of Lading — custody/transport document issued at load |
| **BDN** | Bunker Delivery Note — marine delivery & compliance document |
| **GOV/GSV/NSV** | Gross Observed / Gross Standard / Net Standard Volume |
| **VCF / CTL / CPL** | Volume Correction Factor / Correction for Temperature on Liquid / Pressure |
| **QCI** | Quantity Conversion Interface/engine |
| **HPM** | Hydrocarbon Product Management (industry ERP concept) |
| **TSW** | Trader's & Scheduler's Workbench (nomination/scheduling) |
| **TD** | Secondary Distribution (bulk truck) |
| **EXG / LIA** | Exchange agreement accounting / Logical Inventory Adjustment |
| **TAS** | Terminal Automation System |
| **Rack** | Wholesale loading rack at terminal |
| **Posted Rack Price** | Supplier’s wholesale price at a terminal rack |
| **Formula Price** | Index ± differential (± fees) |
| **Dyed Fuel** | Chemically marked non-highway diesel/kerosene with distinct tax treatment |
| **Into-Plane** | Fueling service delivering jet fuel into aircraft |
| **Stem** | Marine bunker nomination/order |
| **VMI / ATG** | Vendor Managed Inventory / Automatic Tank Gauge |
| **Commission Agent** | Retail operator selling supplier-owned fuel for commission |
| **NSV@60°F** | US customary net standard volume basis commonly contracted |

---

## APPENDIX D: Source Evidence Index (Inline-Cited Works)

Primary sources used throughout this blueprint include:

- Emerson Order-to-Cash for energy logistics — https://www.emerson.com/en/automation-systems/advanced-industry-software/oil-and-gas/software-for-energy-transportation-storage/order-to-cash-software
- Infosys O&G O2C transformation — https://www.infosys.com/industries/oil-and-gas/insights/order-to-cash-transformation.html
- Celonis MOL O2C — https://www.celonis.com/solutions/stories/mol-order-to-cash
- OPIS wholesale rack pricing — https://www.opis.com/blog/wholesale-rack-fuel-pricing-essentials/
- QT Fuels Wholesale Rack Agreement — https://www.qtfuels.com/app/themes/quiktrip-fuels/public/WholesaleRackAgreement.pdf
- Energy Transfer Petroleum Products GT&Cs — https://cms.energytransfer.com/wp-content/uploads/2019/04/GTsCsPetroleumProducts-02012019v9_1_Final.pdf
- Platts Americas refined products methodology — https://www.spglobal.com/commodityinsights/plattscontent/_assets/_files/en/our-methodology/methodology-specifications/americas-refined-oil-products-methodology.pdf
- Platts US gasoline blend value note — https://www.spglobal.com/energy/en/pricing-benchmarks/our-methodology/subscriber-notes/050126-platts-launches-new-gasoline-blend-value-calculations-in-us
- ASTM D1250 / API MPMS 11.1 — https://www.astm.org/d1250-19e01.html
- API Petroleum Measurement catalog — https://www.api.org/-/media/files/publications/2024-catalog/2024-petroleum-measurement.pdf
- SAP TSW help — https://help.sap.com/docs/SUPPORT_CONTENT/isoil/3139386109.html
- SAP QCI integration — https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/0f4ab800d01c4366b0c9aaff06a64320/40ea5e9072ae42119c3425a9f9294d5f.html
- SAP HPM/QCI community — https://community.sap.com/t5/enterprise-resource-planning-q-a/sap-is-oil-and-gas-hpm-module-implementation-without-qci-interface/qaq-p/12108628
- SAP EXG borrow/loan — https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/exchange-borrow-loan-invoice-the-difference-quantity-after-lia/m-p/7554007
- SAP netting — https://community.sap.com/t5/sap-for-oil-gas-and-energy-discussions/netting-statements-in-financial-transactions/td-p/2656532
- ResolveTech SAP S/4 Downstream — https://resolvetech.com/sap-s4hana-downstream-oil-and-gas/
- Shell eVMI — https://www.shell.com/business-customers/commercial-fuels/evmi.html
- ExxonMobil BDN — https://www.exxonmobil.com/en/marine/technicalresource/marine-resources/bunker-delivery-notes
- BDN 2025 guide — https://vesselchain.org/bunker-delivery-note-guide-2025/
- IRS Fuel Tax Credit — https://www.irs.gov/credits-deductions/businesses/fuel-tax-credit
- 26 CFR §48.4082-1 dyed fuel — https://www.law.cornell.edu/cfr/text/26/48.4082-1
- Missouri clear/dyed motor fuel — https://dor.mo.gov/taxation/business/tax-types/motor-fuel/documents/Tax-Requirements-of-Clear-and-Dyed-Diesel-Motor-Fuel.pdf
- FTA motor fuel state book — https://taxadmin.org/wp-content/uploads/resources/motor-fuels/motor-fuel-state.book_.pdf
- C-Store Trader dealer models — https://www.cstoretrader.com/guides/dealer-vs-lessee-dealer-vs-commission/
- Petrosoft consigned stations — https://help.petrosoftinc.com/Content/Station_Home/Station_Options/consigned_station.htm
- Aviation invoice reconciliation — https://invoicedataextraction.com/blog/aviation-fuel-invoice-reconciliation
- DOI Aviation Fuel Management Handbook — https://www.doi.gov/sites/default/files/documents/2024-09/doi-aviation-fuel-management-handbook-sept-2024.pdf
- Emerson TerminalManager — https://www.emerson.com/documents/automation/terminalmanager-en-186128.pdf
- Colorado School of Mines blending — https://people.mines.edu/jjechura/wp-content/uploads/sites/120/2019/02/CBEN409_11_Blending_Optimization-1.pdf

---

## Artifact Update Block (Enterprise Performance Model)

| Field | Content |
| :--- | :--- |
| **Workstream** | Domain Modeling — Downstream Business Architecture |
| **Target artifact** | O2C Downstream O&G Operational Blueprint (EPM-BA-O2C-DS-001) |
| **Objective** | Establish exhaustive O2C value stream, capability, process/master data, systems, and exception baseline for Downstream Commercial & Marketing |
| **Conclusions** | Downstream O2C is custody-event-centric; measurement (GOV/GSV/NSV + QCI), excise tax status, channel title models, and exchange netting are non-optional architectural objects—not optional extensions of generic O2C |
| **Decisions / Status** | Draft/Candidate baseline produced; not yet Approved Baseline |
| **Definitions added** | GOV/GSV/NSV, QCI/HPM/TSW/TD/EXG/LIA, rack access, dyed fuel tax path, channel archetypes, unbilled lift exposure |
| **Assumptions** | US-centric tax/measurement examples generalized with SI notes; SAP IS-Oil used as reference industry solution pattern, not a tool mandate; midstream pure tariff O2C out of scope except custody interfaces |
| **Open questions** | (1) Client-specific channel mix and system inventory? (2) Which ticket fields are already in the enterprise data platform? (3) KPI Store pilot metrics to bind first (e.g., unbilled lift age, OTIF NSV, dispute cycle time)? (4) Exchange/netting legal entity model? |
| **Source evidence** | See Appendix D (primary industry, standards, regulatory, and vendor documentation) |
| **Artifacts to create/update** | Promote into Downstream Business Architecture canonical pack; seed Measurement Catalog entries for NSV/unbilled/exposure; link future KPI candidates |
| **Suggested version/status** | v1.0 Draft → review for Candidate; after process-owner validation → Approved Baseline |
| **Next action** | Map this blueprint’s data products to existing Power BI entities; select 5–7 pilot O2C KPIs; confirm system landscape against actual enterprise inventory |

---

*End of Document — EPM-BA-O2C-DS-001 v1.0*
