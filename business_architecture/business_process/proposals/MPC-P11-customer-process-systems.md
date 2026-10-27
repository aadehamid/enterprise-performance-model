# Proposal MPC-P11: the systems the customer-lifecycle processes use

| Field | Value |
|---|---|
| Status | Accepted (the decision owner, 2026-10-26, EPM-DEC-001-0104): the strong and medium rows, 21 links across 12 processes; the weak rows stay out. Proposed 2026-10-26, because it changes the process map, the process authority (EPM-DEC-001-0103) |
| Date | 2026-10-26 |
| Decision | EPM-DEC-001-0099, item 11: "The customer processes' system links go to a process-map proposal (MPC-P11), after the decision owner checks the weak ones." |
| Source | The processes in `party/lifecycle.csv` and the system stages linked to them (EPM-DEC-001-0070); each customer system's `party:customerRole` and data flows in `party` 1.2.0 (EPM-DEC-001-0069), from the decision owner's customer inputs (kept out of the repository, EPM-DEC-001-0067) |

## The gap

The `system` module links a system to a process only where the process map's `systems` field names it (EPM-DEC-001-0055). The customer-lifecycle processes' entries name no system, so no customer process has a system link. The lifecycle reaches Salesforce, SAP MDG and SAP S/4HANA only through its system stages (EPM-DEC-001-0070).

## The proposal

Add each system below to the named process's `systems` field in `downstream_process_map.json`. Once accepted and applied, the `system` module's next release gains the systems and links, and each system the `party` module also holds gets `skos:exactMatch` to it.

### Proposed (strong and medium evidence)

| Process | System | Evidence | Strength |
|---|---|---|---|
| CM 1.3.6.2.1 Manage Sales Pipeline | Salesforce | Salesforce's role: "Where a prospect is first captured"; the prospect business stage corresponds to the prospect system stage, whose system is Salesforce | Strong |
| CM 1.3.6.6.1 Set Up Prospect | Salesforce | Same | Strong |
| CM 1.3.7.4.6 Perform KYC Due Diligence | Bridger Insight | Its role: "The compliance check of a customer against government watchlists." | Strong |
| CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data | SAP MDG | Its role: the point of control for customer creation and governance, the system of record for the customer; onboarding corresponds to the master system stage (SAP MDG) | Strong |
| CM 1.3.7.1.1 | MAGIC | Its role: it assigns the SAP MDG customer number, converts the prospect and syncs the customer daily | Strong |
| CM 1.3.7.1.1 | Information Steward | Its role: "Monitors customer data quality." | Medium |
| CM 1.3.7.1.1 | Profisee | Its role: customer data storage and mastering, with customer ID mapping, roll-ups and cross-references | Medium |
| CM 1.3.7.1.7 Coordinate Customer Onboarding | SAP MDG, MAGIC | The setup runs Salesforce, then SAP MDG (creates the customer), then MAGIC (account integration), then SAP S/4HANA and RightAngle; onboarding corresponds to the master and record system stages | Strong |
| CM 1.3.7.1.7 | Salesforce, SAP S/4HANA, RightAngle | Same flow | Medium |
| CM 1.3.7.4.2 Establish Credit Limit & Risk Code | SAP S/4HANA | Its role: it "adds credit and collection data" | Medium |
| CM 1.3.7.4.2 | Salesforce | Its role: a new customer setup and credit check start there | Medium |
| CM 1.3.7.2.1 Establish Commercial Terms & Contracts | Sirion | Its role: "Enriches the customer before the customer is assigned to a contract." | Medium |
| CM 1.3.8.2.1 Record Customer Receipts and Payment Notifications | SAP S/4HANA | The financial system of record; payment management corresponds to the settle system stage (SAP S/4HANA) | Strong |
| CM 1.3.8.2.3 Apply Receipts | SAP S/4HANA | Same | Strong |
| CM 1.3.8.3.2 Manage Receivables Collections | SAP S/4HANA | Same, and it holds credit and collection data | Strong |
| CM 1.3.7.4.3 Monitor Credit Against Limit | SAP S/4HANA | Credit data | Medium |
| CM 1.3.7.2.6 Manage Customer Portal | Customer Portal (MyMPC) | Its role: "The customer portal" | Strong |
| CM 1.3.7.2.6 | Salesforce | Its role: it serves the customer portal | Medium |

### Not proposed (weak evidence)

| Process | System | Why not |
|---|---|---|
| CM 1.3.7.4.3 Monitor Credit Against Limit | Allocation Manager | Its role names operational locks and limits, which may not be credit limits |
| CM 1.3.7.4.5 Perform Credit-Driven Customer Closure and Reinstatement | SAP S/4HANA | Only general credit data links them |
| CM 1.3.7.4.4 Analyze Portfolio Credit Risk | Data Products IDP | Its role names credit exposure and delinquency data, not the analysis |

No candidate for CM 1.3.6.2.2 Manage Key Accounts or CM 1.3.7.5.5 Conduct Customer Service Reviews: no role names them.

## How the ontology takes it

The process map changes only through an accepted proposal (AGENTS.md). Accepted, it is applied to `downstream_process_map.json` in its own pull request; the `system` module then names the new systems (SAP MDG, Salesforce, MAGIC, Bridger Insight, Information Steward, Sirion, Customer Portal) through its register, links them, and matches each to its `party` customer system, in a minor release.
