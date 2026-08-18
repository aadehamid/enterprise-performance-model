# Downstream O&G Knowledge Homelab — Data Strategy and Datasets

**Title:** Downstream O&G Knowledge Homelab — Data Strategy and Datasets  
**Purpose:** Define the public-data foundation, synthetic-data boundaries, acquisition sequence, and source-to-data-product mappings for the homelab’s Gasoline Netback / Refining Margin CPG pilot. This is a practical data strategy for a single-machine educational sandbox, not a production data program.  
**Status:** Draft (personal homelab, not an EPM governed artifact)  
**Owner:** Hamid Adesokan  
**Last updated:** 2026-08-09  

## Data strategy overview

The **Downstream O&G Knowledge Homelab** uses a deliberate hybrid strategy. Free public data supplies the market, reference, regulatory, logistics, and weather context that grounds the KPI Store in observed numbers: petroleum prices and rack context, refinery utilization, compliance aggregates, transport patterns, and disruption signals. The principal public price foundation is EIA data, with EIA’s daily product and crude spot series supporting the netback/crack-spread calculation and Petroleum Marketing Monthly providing a public wholesale/rack proxy ([EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm), [EIA Petroleum Marketing Monthly](https://www.eia.gov/petroleum/marketing/monthly/)).

Synthetic data fills the intentionally unavailable commercial and operational layer: custody-transfer tickets and bills of lading (BOLs), SCADA/historian tags, and a complete order-to-cash (O2C) relational database. Those records are commercially sensitive or critical-infrastructure-sensitive and are not publicly published as real company data. Synthetic invoice and pricing data will be anchored to real EIA rack and spot series, then augmented with controlled contractual differentials; that makes the generated amounts analytically coherent with an actual market history rather than arbitrary noise ([EIA Petroleum Marketing Monthly](https://www.eia.gov/petroleum/marketing/monthly/), [EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)).

## Public dataset catalog

### Market & pricing data

Use EIA as the mandatory core. The EIA API, PMM, spot-price series, and crack-spread methodology jointly support reproducible market inputs, wholesale context, and the margin calculation. The World Bank and IMF series are useful long-history or cross-validation context, while CME is only an illustrative delayed-quote reference. OPIS and Platts are named so their exclusion is explicit, not as ingestion candidates.

| Dataset or reference | What it contains | Format | Free / paid status | Homelab mapping |
|---|---|---|---|---|
| [EIA Open Data API (APIv2)](https://www.eia.gov/opendata/) | Petroleum/liquids time series including prices, supply, refinery activity, storage, trade, and sales; frequency varies by series. | REST JSON or XML; bulk files also available. | Free/open data; free API key and throttling required. | `fact_market_series`; source registry entries for EIA series and release metadata. |
| [EIA Petroleum Marketing Monthly (PMM)](https://www.eia.gov/petroleum/marketing/monthly/) | Monthly crude and product prices/volumes by geography and sales dimensions, including refiner rack gasoline and diesel price context and prime-supplier volumes. | HTML, PDF, and API-queryable series. | Free public U.S. government publication. | `fact_rack_price_monthly`, `fact_prime_supplier_volume`, and pricing-index reference data. |
| [EIA Weekly Petroleum Status Report (WPSR)](https://www.eia.gov/petroleum/supply/weekly/) | Weekly U.S. stocks, production, imports/exports, refinery inputs, and refinery utilization. | HTML/DNAV tables, PDF, and API series. | Free public U.S. government data. | `fact_refinery_market_weekly`; driver context for utilization and supply conditions. |
| [EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm) | Daily WTI/Brent and refined-product spot prices by listed location, including gasoline and ULSD/heating-oil series. | HTML history tables and API series. | Free public data. | `fact_market_price_daily`; canonical price inputs to netback and crack-spread calculations. |
| [EIA 3:2:1 Crack Spread methodology](https://www.eia.gov/todayinenergy/includes/crackspread_explain.php) | EIA explanation of the WTI/LLS versus gasoline/diesel 3:2:1 refining-margin proxy. | HTML methodology and chart. | Free public reference. | KPI calculation specification and `dim_kpi_methodology` evidence. |
| [CME Group delayed quotes](https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html) | WTI, Brent, RBOB gasoline, and NY Harbor ULSD futures/options quotes. | Web tables. | Free delayed quotes only; real-time and bulk historical data are paid. | Optional `fact_futures_reference_delayed`; use for illustration, not backtesting-grade history. |
| [OPIS pricing](https://www.opis.com/product/pricing/) | Commercial rack, retail, wholesale assessments and historical pricing feeds. | Commercial service. | **Paid; excluded.** | No fact table. PMM is the free rack-price proxy. |
| [S&P Global Platts market data](https://www.spglobal.com/commodity-insights/en/products-solutions/crude-oil/crude-oil-market-data) | Commercial physical crude and product price assessments and benchmarks. | Commercial service. | **Paid; excluded.** | No fact table. Use EIA, World Bank, or IMF series for free benchmark context. |
| [World Bank Commodity Price Data (Pink Sheet)](https://www.worldbank.org/en/research/commodity-markets) | Monthly/annual global commodity prices, including crude-oil averages and long history. | Downloadable XLSX/CSV and DataBank access. | Free public data; World Bank open data is generally CC BY 4.0. | `fact_macro_commodity_price_monthly` for long-run market context and cross-checks. |
| [IMF Primary Commodity Prices (PCPS)](https://www.imf.org/en/research/commodity-prices) | Monthly global crude, natural-gas, and other commodity prices, including average petroleum spot price. | SDMX API (JSON/XML) and CSV. | Free public data, generally usable with attribution. | `fact_macro_commodity_price_monthly`; alternate benchmark and SDMX integration exercise. |

### Regulatory & compliance data

These sources add product-quality, renewable-fuel, and incident context without implying that the homelab implements a full compliance program. They are optional after the market/O2C core, but their structures are valuable for future quality rules, compliance measures, and HSE/integrity questions.

| Dataset | What it contains | Format | Free / paid status | Homelab mapping |
|---|---|---|---|---|
| [EPA RFS/RIN public data](https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-renewable-fuel-standard) | Aggregate RIN generation, transaction, retirement, and price-trend information under the Renewable Fuel Standard. | XLS/CSV spreadsheets and PDF guidance. | Free public U.S. government data. | `fact_rin_compliance_aggregate`, `dim_renewable_fuel`, and an optional compliance data product. |
| [EPA gasoline fuel-quality properties](https://www.epa.gov/fuels-registration-reporting-and-compliance-help/public-data-gasoline-fuel-quality-properties) | Reported gasoline properties such as RVP, sulfur, benzene, and octane. | Downloadable CSV/XLS files. | Free public data. | `dim_product_specification` and product-grade/season/PADD quality reference checks. |
| [PHMSA pipeline incident and safety data](https://www.phmsa.dot.gov/data-and-statistics/pipeline/pipeline-incident-20-year-trends) | Incident records and trends covering cause, commodity released, volume, cost, location, and operator for pipeline events. | Downloadable CSV/Excel extracts and dashboards. | Free public U.S. government data. | `fact_pipeline_incident` linked to `dim_terminal_or_pipeline_segment`; optional HSE/integrity KPI context. |

### Logistics & weather data

Logistics data provides network and mode context; weather data supplies historically grounded disruption scenarios. Neither substitutes for actual terminal operations, which remain synthetic.

| Dataset | What it contains | Format | Free / paid status | Homelab mapping |
|---|---|---|---|---|
| [BTS petroleum transport data](https://www.bts.gov/content/crude-oil-and-petroleum-products-transported-united-states-mode) | U.S. crude and petroleum-product movements by pipeline, rail, tanker/barge, and truck, with related freight and ton-mile statistics. | HTML, CSV/Excel, and PDF. | Free public U.S. government data. | `fact_freight_mode_mix` and `dim_transport_mode` for transportation-cost/netback assumptions. |
| [NOAA HURDAT2 best-track data](https://www.nhc.noaa.gov/data/hurdat/) | Six-hourly tropical-cyclone positions, maximum sustained wind, and central pressure for Atlantic and Pacific basins. | Fixed-width text/CSV and GIS-related files. | Free public-domain U.S. federal work. | `fact_storm_track` and `dim_weather_disruption_scenario` for Gulf Coast outage scenarios. |
| [NOAA Storm Events Database](https://www.ncei.noaa.gov/stormevents/ftp.jsp) | County-level storm-event records, including hurricanes, tropical storms, flooding, and damage estimates. | Yearly CSV bulk downloads. | Free public data. | `fact_storm_impact` to enrich disruption scenarios and event annotations. |

### State and aggregator/Kaggle data

Texas RRC provides an optional feedstock-supply context. The Kaggle files are quick-start, structural, or realism-calibration supplements, not authoritative replacement sources. Each Kaggle dataset must be checked on its own page for its uploader-assigned license before use.

| Dataset | What it contains | Format | Free / paid status | Homelab mapping |
|---|---|---|---|---|
| [Texas RRC oil and gas production data](https://www.rrc.texas.gov/oil-and-gas/research-and-statistics/production-data/) | Texas oil/natural-gas production by county/district and historical monthly/well-related records. | PDF reports, downloadable CSV/Excel, and dashboards. | Free public Texas state data. | `fact_crude_supply_monthly` and `dim_crude_supply_origin`; optional upstream context only. |
| [Kaggle: U.S. gasoline and diesel retail prices](https://www.kaggle.com/datasets/mruanova/us-gasoline-and-diesel-retail-prices-19952021) | Historical U.S. gasoline/diesel retail prices from 1995–2021, derived from EIA. | CSV. | License varies by uploader; verify dataset tag. | `fact_retail_price` quick-start historical load. |
| [Kaggle: U.S. gas-station pricing / GasBuddy snapshot](https://www.kaggle.com/datasets/polartech/us-gas-station-pricing-data-gasbuddy-pricing/code) | Station-level retail gas prices. | CSV. | License varies by uploader; verify dataset tag. | `fact_station_price` and `dim_retail_site` for optional retail-network exercises. |
| [Kaggle: Global Fuel Prices 2020–2026](https://www.kaggle.com/datasets/belbino/global-fuel-prices-20202026) | Multi-country gasoline and diesel retail price series. | CSV. | License varies by uploader; verify dataset tag. | `fact_retail_price_global` for an optional international comparison layer. |
| [Kaggle: Timac fuel distribution and sales](https://www.kaggle.com/datasets/olagokeblissman/timac-fuel-distribution-and-sales-dataset) | Depot/distribution-center-level fuel distribution and sales-style records. | CSV. | License varies by uploader; verify dataset tag. | Structural seed/reference for the synthetic wholesale distribution and O2C design. |
| [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | Approximately 100K real e-commerce orders, customers, payments, deliveries, and reviews from 2016–2018. | Relational CSV extracts. | Public Kaggle dataset; CC BY-NC-SA 4.0. | **Realism-calibration reference only, not the primary schema:** sanity-check synthetic O2C record volumes, cardinalities, and distributions against real transactional data. |

No public entity-level Downstream O&G O2C dataset with customer, order, and invoice records exists. Synthetic generation—both relational and unstructured—therefore remains the primary strategy; EIA, World Bank, and Kaggle/Timac sources remain aggregate or structural references rather than substitutes for the homelab’s synthetic O2C corpus.

### Real and synthetic industrial reference datasets

These are templates for schema, sampling, multivariate behavior, anomaly labels, and simulation—not claims that their facilities are downstream terminal data. They should inform a simulated historian design while preserving the clear distinction between real analog data and homelab-generated tags.

| Dataset or reference | What it contains | Format | Free / paid status | Homelab mapping |
|---|---|---|---|---|
| [3W Dataset (Petrobras)](https://github.com/petrobras/3W) | Public oil-well undesirable-event data: multivariate pressure, temperature, and flow time series labeled by event type. | CSV files in split 7z archives; notebooks. | Open/public repository; verify current repository license. | Reference `fact_industrial_event_template` and anomaly-label pattern for a simulated sensor pipeline. |
| [Awesome Industrial Datasets](https://github.com/jonathanwvd/awesome-industrial-datasets) | Curated index of industrial datasets with metadata on real/synthetic sources, labels, and time-series characteristics. | Repository CSV/JSON metadata and generated catalog. | Public index; individual dataset licenses vary. | Discovery register and evidence source for structural templates. |
| [ManyWells via Awesome Industrial Datasets](https://github.com/jonathanwvd/awesome-industrial-datasets) | Large-scale synthetic multivariate oil-and-gas multiphase-flow time series. | Multivariate time series; source format is not specified in the research inventory. | Public synthetic reference; verify source terms. | Template for `fact_historian_reading` pressure/flow/temperature behavior. |
| [Tennessee Eastman Process via Awesome Industrial Datasets](https://github.com/jonathanwvd/awesome-industrial-datasets) | Synthetic chemical-process benchmark with multivariate tags and labeled fault/anomaly scenarios. | MATLAB/CSV time series. | Freely available for academic/research use; check the selected mirror. | Fault-injection structure for a simulated refinery-unit historian. |
| [BATADAL / SWaT / WADI via Awesome Industrial Datasets](https://github.com/jonathanwvd/awesome-industrial-datasets) | Water-domain SCADA sensor/actuator streams with attack and anomaly scenarios; structurally comparable rather than domain-equivalent. | CSV. | Academic/research access; verify current terms. | Historian schema, alarm/event, and anomaly-label design template. |

## Data acquisition plan by phase

Phase 1 is an ingestion-and-generation phase, not a mandate to collect every source in the catalog. Start with the smallest set that can calculate and explain the capstone KPI, preserve raw extracts with source and retrieval metadata, and make every later source an explicit optional increment.

| Roadmap phase | Ingest or reference | Dataset scope and resulting data product |
|---|---|---|
| **Phase 1: Data foundation — ingest public data + design synthetic data** | **Ingest first:** EIA Open Data API, EIA Spot Prices, PMM, and WPSR. Retain the EIA crack-spread methodology as calculation evidence. Optionally load EPA fuel-quality data for the first product-specification dimension. | `market_price_daily`, `rack_price_monthly`, `refinery_market_weekly`, `product_specification`, plus synthetic Customer, Contract, Terminal, Product, Ticket/BOL, Sales Order, Invoice, and Payment tables. This is the minimum foundation for a reproducible weekly netback. |
| **Phase 2: Domain modeling & ontology** | Reference PIDX conventions and the public catalog mappings; optionally model EPA RFS/RIN, PHMSA, and transport/weather concepts. | Business concepts, glossary terms, provenance links, and SHACL rules for products, tickets, quality attributes, price indices, and incidents. |
| **Phase 3: KPI Store & semantic/query layer** | Reuse Phase 1 EIA facts as the calculation input. Add World Bank Pink Sheet or IMF PCPS only when a macro benchmark or alternate source is a useful teaching comparison. | Governed `fact_kpi_result` records with links to market-price inputs, methodology, dimensions, and driver context. |
| **Phase 4: Neo4j graph population** | Reference, rather than broadly ingest, selected PHMSA, BTS, NOAA, RRC, and industrial-template structures when a relationship or scenario is demonstrated. | Curated graph facts such as Terminal–Product–Ticket–Contract–Invoice paths and optional Storm–Disruption–Market context. |
| **Phase 5: AI agent + FastAPI capstone** | Serve Phase 1/3 facts and the source registry. CME delayed quotes may be shown as a current-reference example only. | A question response can retrieve the KPI, its real EIA inputs, synthetic operational drivers, and source/provenance evidence. |
| **Phase 6: Governance polish** | Evaluate optional Kaggle, PHMSA, BTS, NOAA, RRC, and industrial datasets only when a documented use case exists. | Source and traceability entries, license checks, refresh guidance, data-quality checks, and reproducible ingestion/generation runbooks. |

## Synthetic data generation plan

### 9(a) Custody Transfer / BOL / Ticket-Level Transactional Data

Generate the ticket header and measurement fields as a constrained operational event: terminal and rack/bay, product, carrier and driver, truck/trailer, ship-to customer, contract, BOL/ticket number, timestamp, observed gross volume, density, and corrected net-standard volume. Use [Faker](https://github.com/joke2k/faker) or [Mimesis](https://github.com/lk-geimfari/mimesis) only for descriptive fields such as names, addresses, carriers, and license plates; use [PIDX Downstream conventions](https://pidx.org/standards/) for field naming and document shape. Apply the API MPMS 11.1 volume-correction methodology to generated gross quantities so the standard-volume result is a calculated measurement, not an independent random number. Use [SDV](https://github.com/sdv-dev/SDV) multi-table synthesis to preserve Customer → Contract → Terminal → Product → Ticket → Invoice referential integrity after a small hand-authored seed is validated.

**Illustrative synthetic custody-ticket shape**

| Field | Example synthetic value |
|---|---|
| `ticket_id` / `bol_number` | `TKT-2026-000184` / `BOL-2026-000184` |
| `terminal_id`, `rack_bay_id`, `product_code` | `TERM-GC-01`, `RACK-03`, `RBOB-87` |
| `customer_id`, `contract_id`, `carrier_name` | `CUST-014`, `CTR-014-01`, `Pioneer Haulage LLC` |
| `load_timestamp` | `2026-07-15T09:42:00Z` |
| `gross_observed_bbl`, `observed_temperature_f` | `250.40`, `92.0` |
| `net_standard_bbl`, `volume_correction_factor` | `246.78`, `0.9855` |
| `price_index`, `differential_usd_per_gal` | `EIA-PMM-RACK`, `0.031` |

The example is deliberately synthetic: its identifiers, parties, volumes, and contract differential are generated; the selected price-index family can be anchored to the relevant EIA public series. This supports ticket-to-invoice lineage without disclosing or imitating a real terminal’s commercial records.

### 9(b) SCADA/Historian Time-Series Tag Data

First define a small ISA-5.1-style tag list for a simulated terminal, pipeline segment, or refinery unit. Generate base signals with [TimeSynth](https://github.com/TimeSynth/TimeSynth) or [mockseries](https://github.com/cyrilou242/mockseries): mean-reverting pressure, fill/draw tank level, periodic flow, trend, seasonality, noise, and deliberately injected anomaly intervals. Use [Tennessee Eastman Process, ManyWells, and BATADAL/SWaT/WADI structural references](https://github.com/jonathanwvd/awesome-industrial-datasets) to shape multivariate records and event labels; use [3W](https://github.com/petrobras/3W) as a real oil-and-gas sensor-event analogue. Optionally use [DWSIM](https://dwsim.org/) to create physically grounded temperatures, flows, and compositions, then expose readings through an OPC UA server such as `asyncua`/`python-opcua` identified in [awesome-opcua](https://github.com/iswunistuttgart/awesome-opcua), or write them directly to DuckDB/Postgres as a historian analogue.

**Illustrative simulated tag list**

| Tag | Signal shape | Target usage |
|---|---|---|
| `TK101.LEVEL` | Sawtooth fill/draw cycle with noise | Tank inventory and overfill alarm exercise |
| `PL-07.PRESSURE` | Mean-reverting pressure with injected spikes | Pipeline integrity/anomaly scenario |
| `RACK-03.FLOW` | Loading-window flow with zero-flow gaps | Ticket-to-operational-event reconciliation |
| `CDU.TEMP.01` | Stable operating band with fault excursion | Process-simulation and alarm-label example |
| `MTR-01.TOTALIZER` | Monotonic cumulative meter reading | Derived delivered-volume check |

`fact_historian_reading` should minimally carry `tag_id`, `event_timestamp`, `value`, `unit_of_measure`, `quality_code`, and optional `scenario_event_id`. Maintain a separate tag catalog that states its simulated equipment, engineering unit, expected range, sampling rule, and ownership. No real refinery or pipeline historian feed is required or sought.

### 9(c) Relational OLTP Schema for Order-to-Cash (Customers, Orders, Contracts, Terminals, Products, Pricing, Invoices)

1. **Design the logical schema first.** Define Customer, Contract, Product, Terminal/Rack, Price List or Index Formula, Sales Order, Delivery Ticket/BOL, Invoice, and Payment, using [PIDX Downstream conventions](https://pidx.org/standards/) as the industry-informed reference for commercial transaction structures.
2. **Hand-seed 10–50 rows per table.** Encode real business rules in a small reviewable set, including a contract price expressed as EIA rack index plus a differential.
3. **Scale with SDV’s HMA multi-table synthesizer.** [SDV](https://docs.sdv.dev/sdv) can generate statistically representative, foreign-key-aware records across related tables rather than independent rows.
4. **Use Faker/Mimesis for descriptive values.** [Faker](https://github.com/joke2k/faker) and [Mimesis](https://github.com/lk-geimfari/mimesis) populate names, addresses, businesses, and transport descriptors in seed or low-complexity lookup data.
5. **Anchor pricing to EIA rack and spot series.** EIA PMM and daily spot history supply the market index; a generated contractual differential, tax status, and volume create invoice lines that are analytically realistic for netback work ([EIA Petroleum Marketing Monthly](https://www.eia.gov/petroleum/marketing/monthly/), [EIA Spot Prices](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)).
6. **Keep lighter alternatives optional.** [syda](https://pypi.org/project/syda/) and [great-generator](https://github.laiyagushi.com/ravikiranpagidi/great-generator) are lighter schema-driven alternatives when SDV is unnecessary.

**Illustrative O2C entity chain**

```text
Customer
  → Contract (product, terminal eligibility, EIA index + differential)
  → Sales Order
  → Delivery Ticket / BOL (measured and corrected volume)
  → Invoice (quantity × indexed price + differential + applicable tax)
  → Payment

Terminal/Rack and Product are shared master-data dimensions.
Price List / Index Formula links Contract and Invoice Line to the public EIA series.
```

This design makes commercial logic inspectable: a KPI driver can traverse from invoice margin to price index, ticket volume, contract terms, product, and terminal while keeping all company-specific facts synthetic.

## Unstructured Data Generation and Ingestion

### Governing entity-linking rule and scope

**Entity-linking, not independent generation, is the governing rule.** Every unstructured artifact must reference the same synthetic `customer_id`, `order_id`, `invoice_id`, `dispute_id`, and `collection_case_id` used in the relational ERPNext/Postgres data. This allows the knowledge graph to fuse structured and unstructured facts about the same real-world entity rather than creating disconnected corpora.

Generate unstructured artifacts for all 64 Level 2 O2C taxonomy boxes (across 10 Level 1 groups — updated 2026-08-09 per the downstream O&G taxonomy redline, was ~40 boxes/9 groups), not only the process groups with the deepest transactional build. Full taxonomy coverage gives the knowledge graph process-wide context while the lighter custom workflows for Credit & Risk, Collection, Dispute, Close, and Measure & Custody Transfer supply believable state transitions and linked case records.

### Artifact generation plan

| Artifact type | Coverage and generation approach | Required entity-link mechanism |
|---|---|---|
| SOPs | Create 64 LLM-authored Markdown/PDF SOPs, one per Level 2 O2C process box, grounded in the ontology definition for that process. | Tag each artifact with the `process_id` that matches the Document 05 T-Box process node; use the same `process_id` namespace in data-generation scripts and KPI-candidate traceability. |
| Invoices / receipts | Render real PDFs with ReportLab or WeasyPrint directly from ERPNext Sales Invoice and Payment Entry rows. | Use the same `invoice_id` or `payment_id` as the ERPNext row; amounts, quantities, tax, and payment values must match exactly. |
| Emails | Generate LLM-authored threads for dispute escalation, credit-hold notices, collections follow-up, and remittance advice. | Reference a specific `order_id`, `invoice_id`, `dispute_id`, or `collection_case_id` in the subject or message body. |
| Team-channel messages | Use [block/buzz](https://github.com/block/buzz), self-hosted with Docker Compose, and seed scripted and/or agent-authored messages through `buzz-cli`. | Messages must reference the same synthetic IDs; export the Buzz Nostr event log as structured JSON for ingestion. |

### Corpus scale and ingestion path

| Generated corpus | Initial scale / grain | Source-to-graph path |
|---|---|---|
| SOP corpus | One artifact per Level 2 O2C box, 64 documents | File connector → entity-aware chunks linked by `process_id` → process and KPI-candidate graph nodes. |
| Invoice and receipt PDFs | One PDF per relevant ERPNext Sales Invoice or Payment Entry | File connector → extracted facts reconciled to the originating ERPNext/Postgres row by `invoice_id` or `payment_id`. |
| Email threads | Multiple scenario threads across credit, dispute, collection, and remittance processes | Email connector (IMAP/POP3) → entity-aware chunks linked to the referenced transaction or case IDs. |
| Team-channel messages | Scripted or agent-authored exception/dispute discussions | Message-stream connector → exported Buzz JSON → entity-aware chunks linked to the referenced IDs. |

[semantica-agi/semantica](https://github.com/semantica-agi/semantica) is the ingestion mechanism for this combined corpus. Its native connectors for files, email (IMAP/POP3), and message streams fuse the unstructured artifacts with ERPNext/Postgres relational data in the same knowledge graph, using entity-aware chunking and PROV-O provenance to record whether each fact came from a structured row or an unstructured document.

## Data licensing and ethics notes

- **Exclude OPIS and S&P Global Platts.** They are commercial paid services, not free homelab sources; PMM and EIA/World Bank/IMF series are the approved public substitutes ([OPIS pricing](https://www.opis.com/product/pricing/), [S&P Global Platts market data](https://www.spglobal.com/commodity-insights/en/products-solutions/crude-oil/crude-oil-market-data)).
- **Treat CME carefully.** Its free offering is delayed-quotes-only; real-time and bulk historical futures data require paid licensing ([CME delayed quotes](https://www.cmegroup.com/market-data/browse-data/delayed-quotes.html)).
- **Verify every Kaggle license at use time.** The uploader determines the dataset license, so a Kaggle URL is not by itself a reusable-data authorization ([Kaggle common license types](https://www.kaggle.com/getting-started/116476)).
- **Federal-source default.** EIA, EPA, PHMSA, BTS, and NOAA data are generally public-domain U.S. federal outputs, but retain the source URL and check any individual dataset-specific terms or footer before publication or redistribution ([data.gov Open Licenses](https://resources.data.gov/open-licenses/)).
- **Verify SDV’s current terms.** SDV licensing has evolved; confirm the current repository terms before any use outside this personal homelab ([SDV repository](https://github.com/sdv-dev/SDV)).
- **Synthetic data is necessary and appropriate.** No public source publishes real custody-transfer/BOL transactions, refinery or pipeline SCADA/historian streams, or a downstream marketer’s O2C database. Generate those records from documented conventions and market anchors, label them synthetic, and do not present them as operational evidence from a real company.

## Related homelab documents

- `00-Homelab-Charter-and-Roadmap.md`
- `01-Reference-Architecture.md`
- `02-Tool-Selection-and-ADRs.md`
- `03-Curriculum-and-Learning-Modules.md`
- `05-Domain-Model-and-Ontology-Pilot.md`
- `06-Repo-Structure-and-Build-Plan.md`

## See also (enterprise EPM parallel)

For learning-transfer context only, this document loosely parallels the EPM **Source and Traceability Register** and **Data Product Portfolio**: it records candidate source evidence, data-product boundaries, mappings, and appropriate provenance expectations. It is a personal homelab document, not a governed EPM artifact and not a claim of formal linkage or approval.
