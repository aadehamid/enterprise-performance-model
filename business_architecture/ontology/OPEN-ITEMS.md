# What is open on the ontology

The ontology is done (EPM-DEC-001-0107), and this page lists what stays open on it. Each row points to the record that holds the detail; where they differ, the record wins. It leaves out the pricing demo's work and the repository's own tooling. Last checked on 2026-10-31. On 2026-11-02 a row for releasing the technical-graph module was added, then removed the same day when the decision owner approved its `1.0.0` (EPM-DEC-001-0112).

## Decisions for the decision owner

| Item | What is needed | Record |
|---|---|---|
| Releasing the logical-model module | Approve `logical-model 1.0.0`, which holds the customer logical model, from one page, with the list of doubtful links. The package is built only when the release is cut. *Added 2026-11-02.* | EPM-DEC-001-0113, decision 10 |
| Turning on the release-tag store sync | Add its seven repository secrets, or keep syncing by hand | #426 |

## What we need from the business

Each answer goes into the named record and that module's next release. `business-closeout.md` gives the full wording of each point.

| Point | What the business needs to say | Who | Module |
|---|---|---|---|
| 1 | Who owns the meaning of each module or concept scheme, who stewards its data and who keeps its systems (competency question 17; stays with the decision owner, who convenes the business leads; *2026-11-02:* the follow-up release ships with it open, EPM-DEC-001-0086, amendment) | Business leads per domain | `organization` |
| 2 | Confirm the Risk Group's mandate for Market Data, or name the accountable group (stays with the decision owner) | The Risk Group, or whoever sets its mandate | `market-data` |
| 5 | Confirm the PIDX family letters with PIDX, or give the PIDX codes MPC trades | Commercial product owners, with PIDX | `party` |
| 6 | Whether the Forecaster in the backcasting activities is the Local Refinery Forecaster; merging them is a major release | The refinery Economics and Planning process owner | `organization` |
| 9 | Confirm or replace three working role definitions | The managers of those roles | `organization` |
| 10 | What is in and out for each of 33 measures, in business words | Each measure's owner | `kpi` |
| 11 | What Federal Health is, and what MPC sends each of Drop Tank, GasBuddy, DTN and Federal Health | The customer-data owner | `party` |
| 12 | What TopDay and VALT do | Their owners | `system` |
| 13 | Fuller descriptions of CargoTracker and Allocation Manager, and whether Allocation Manager also allocates product | Their owners | `system`, `party` |
| 14 | Which Oracle Hyperion product and which Quorum product | The owners of the backcast's actual-data steps; the customer | `system`, `party` |
| 15 | Polaris's vendor and what it does | Marathon Pipeline LLC's scheduling owners | `party` |
| 16 | Confirm or correct the descriptions drafted for the internal systems | Each system's owner | `system`, `party` |
| 17 | Whether Dealer Master's billing customer number is the SAP customer number, maps to it, or is separate | Dealer Master's owners | `party` |
| 18 | Whether Dealer Master's fuel volumes reach the Enterprise Data Lake, and by which flow | Dealer Master's owners, with the Enterprise Data Lake's owners | `party` |

These also wait on the business, and their changelogs hold the detail:

| Module | What is needed | Record |
|---|---|---|
| `kpi` | The full list of Additional Market Prices; a silver source for the crack spread's KPI ID | `kpi` 1.2.0 changelog |
| `market-data` | Definitions for the unnamed series; source wording for the 40 market prices; the legs of four series | `market-data` 1.1.0 changelog |
| `data-product` | The benchmark view's scaling and 160-day window, KPI ID lineage, joins read from code, lineage reach, production names and fresh data | `data-product` 1.2.0 changelog |
| `data-product` | Definitions for 33 portfolio data products | `data-product` 1.1.0 changelog |
| `system` | Fuller MIPS and MPR descriptions, MPR's expansion and XPIMS's meaning | `system` changelogs |
| `system` | Owners to confirm three weak links: Allocation Manager for CM 1.3.7.4.3, SAP S/4HANA for CM 1.3.7.4.5, and Data Products IDP for CM 1.3.7.4.4 | EPM-DEC-001-0104, item 3 |

## Gaps the process map and value streams still record

| Gap | Where it stands | Record |
|---|---|---|
| Six enabling functions have no processes: Supply Chain, Shared Services, Process Excellence & IT, Human Resources, Legal & Corporate Communications, and EHS & Government Reporting | Human Resources and EHS would hold deferred areas listed below. No ruling asks for depth in the others | `downstream_process_map.json`; #454 |
| Loss Control is produced by `CM 1.1.3.7.13` but is not linked to a stage of the commercial value stream | Partly filled | `value_stream_commercial_lifecycle.json`, `gapAnalysis` |
| Retail transaction capture and payment processing are not broken down | Open | The same list |
| Blending operations may span Refining and are not broken down | Open | The same list |
| No data products for customer credit, receivables or collections | Open | `value_stream_order_to_cash.json`, `gapAnalysis` |
| Collection and dispute steps collapse into one process each, Close AR Sub Ledger has no named process, and Process Bad Debt carries another name | Recorded, not changed | The same list |
| No buyer-side procure-to-pay processes for intercompany fees | Open | MPC-P08 ruling, `reference/mpc/process-map-suggestions.md` |

## Work we can do without the business

| Item | What is needed | Record |
|---|---|---|
| Keeping the stores in step with Git | Automatic checks, a drift check for the technical graph, and content comparison. The plan is in the guide and the walkthrough | #455 |
| A small fix in the next `market-data` release | Reword its one shape message that holds an apostrophe | EPM-DEC-001-0106 |
| The process playbook's log | Backfill the entries of batches 1 to 20 | `business-process-architecture-playbook.md`, §9 |

## Parked, each until its trigger

| Item | What would reopen it | Record |
|---|---|---|
| Held process-map rows | A corrected source; each row is then judged again | EPM-DEC-001-0025, 0083 |
| Refinery operating execution: unit operations, line-ups, blend execution and process control | The trigger each item names | EPM-DEC-001-0063 |
| Product recalls and regulatory audits, human capital, data and analytics governance, and remediation: ruled in scope on 2026-09-17, deferred on 2026-10-31 | A new decision by the decision owner; the deferral records no trigger | `apqc-scope-decisions.md`; #454 |
| Physical maintenance execution | A separate approval | MPC-P02b ruling |
| Renewable diesel production | A ruling to bring it in | MPC-P04 ruling |
| IOF Supply Chain mapping | A concept layer for logistics assets or movements, or a consumer that needs IOF terms | EPM-DEC-001-0064 |
| IRIs that resolve | A registered, hosted namespace in place of the w3id placeholder | EPM-DEC-001-0039 |
| Usage and integration | A separate, later task | EPM-DEC-001-0107 |
