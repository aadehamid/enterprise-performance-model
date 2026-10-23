# EPM-DEC-001-0070: The customer lifecycle, linked to processes and systems, and proposal MPC-P10

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) for the lifecycle and its links; MPC-P10 is proposed and waits for the decision owner; *2026-10-23:* accepted (EPM-DEC-001-0087) |
| Date | 2026-10-21 |
| Questions | Pull request 4 of EPM-DEC-001-0067's plan; the customer lifecycle from onboarding (EPM-DEC-001-0052, Phase C) |
| Source | Claude Code night run, 2026-10-21 |

## Context

The decision owner's inputs give two views of a customer's life (EPM-DEC-001-0067; the inputs are not in the repository):

- **Six business stages:** prospect, onboarding, payment management, risk management, relationship management and offboarding.
- **Five system stages**, from input 6's pane on where the customer shows up in systems: prospect (Salesforce), master (SAP MDG), record (SAP S/4HANA), execute (the execution systems) and settle (invoices and postings back to SAP S/4HANA).

They asked for the lifecycle to be captured (EPM-DEC-001-0067, "both the life cycle and data flow of Customer"). EPM-DEC-001-0052 says the lifecycle's process nodes are proposed, not applied, under the process-map rule (AGENTS.md).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Both lifecycles are SKOS schemes** in the `party` module: `party:lifecycle-stage` (six stages) and `party:system-stage` (five). Each stage has a definition in Claude's words from the inputs.
2. **Each business stage links to the core processes that do its work** (`party:stageProcess`). The links run to existing core 2.1.0 concepts only, so nothing in the process map changes. *2026-10-23:* since `party` 1.1.0 the build reads core 2.3.0, and onboarding also links to CM 1.3.7.1.7, which MPC-P10.1 added to the map (EPM-DEC-001-0087, 0092). The mapping rests on each process's core definition and scope note; the names are core 2.1.0's labels:
   - **Prospect:** Manage Sales Pipeline (CM 1.3.6.2.1), Set Up Prospect (CM 1.3.6.6.1, today card programs only), and Establish Credit Limit & Risk Code (CM 1.3.7.4.2), which assesses the credit application.
   - **Onboarding:** Perform KYC Due Diligence (CM 1.3.7.4.6), CM 1.3.7.4.2, Maintain Customer and Commercial Account Master Data (CM 1.3.7.1.1) and Establish Commercial Terms & Contracts (CM 1.3.7.2.1). *2026-10-23:* and Coordinate Customer Onboarding (CM 1.3.7.1.7), since `party` 1.1.0 (EPM-DEC-001-0092).
   - **Payment management:** Record Customer Receipts and Payment Notifications (CM 1.3.8.2.1), Apply Receipts (CM 1.3.8.2.3) and Manage Receivables Collections (CM 1.3.8.3.2).
   - **Risk management:** Monitor Credit Against Limit (CM 1.3.7.4.3) and Analyze Portfolio Credit Risk (CM 1.3.7.4.4).
   - **Relationship management:** Manage Key Accounts (CM 1.3.6.2.2), Conduct Customer Service Reviews (CM 1.3.7.5.5), Manage Customer Portal (CM 1.3.7.2.6) and CM 1.3.7.4.2. Core 2.1.0's scope note for CM 1.3.7.4.2 lists "periodic and event-triggered reviews" in its scope, which covers the annual credit limit review.
   - **Offboarding:** Perform Credit-Driven Customer Closure and Reinstatement (CM 1.3.7.4.5) and CM 1.3.7.1.1, which retires the records.
3. **Each system stage links to the customer systems that hold the record** (`party:stageSystem`):
   - prospect: Salesforce; master: SAP MDG; record and settle: SAP S/4HANA;
   - execute: RightAngle, Polaris, Dealer Master and Terminal download. Input 6 also names card systems here, but none in the customer system list executes card transactions (the Brand Credit Card System is a source of dealers), so none is linked.
4. **The two lifecycles correspond** (`party:correspondsTo`) where the inputs show it: prospect to prospect; onboarding to master and record; payment management to settle. Risk management, relationship management and offboarding have no system stage in input 6, so they have no correspondence.
5. **Three gaps become proposal MPC-P10**, in `business_architecture/business_process/proposals/MPC-P10-customer-lifecycle.md`:
   - **P10.1:** onboarding coordination for every customer. Core 2.1.0's scope note for CM 1.3.7.1.1 names "prospect onboarding coordination", but the map's only onboarding coordinator for commercial customers is under Loyalty and Cards (trading counterparties have CM 1.2.1.2.1 Create New Counterparty). The recommendation is a new L5 process under the L4 CM 1.3.7.1.
   - **P10.2:** the Order to Cash process "Review Credit Limit & Risk Code" has no linked process. The value stream's own rationale names CM 1.3.7.4.3 Monitor Credit Against Limit as the closest; the proposal recommends CM 1.3.7.4.2, which revises limits and risk codes, and gives the decision owner both.
   - **P10.3:** a customer master data product, produced by CM 1.3.7.1.1, on the Marketing & Sales line.
   - *2026-10-23:* the decision owner accepted all three (EPM-DEC-001-0087). `party` 1.1.0 links the onboarding stage to the new CM 1.3.7.1.7 (EPM-DEC-001-0092).
   - Each waits for the decision owner. Until then the lifecycle rests on the existing processes. *2026-10-23:* no longer: the decision owner accepted all three (EPM-DEC-001-0087), and they are applied in `core` 2.3.0, `value-stream` 1.1.0, `data-product` 1.1.0 and `party` 1.1.0 (EPM-DEC-001-0089 to 0092).

## Alternatives considered

- **Add the lifecycle stages as process-map nodes.** Not chosen: the stages are a view across existing processes, and the process map changes only through an approved proposal.
- **Link each system stage to a process.** Not chosen: input 6 describes system stages by system, not by process. The business stages carry the process links.

## The decision owner's recorded words

This record is Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). It builds on the decision owner's words recorded in EPM-DEC-001-0067 (`answers-2026-10-21-customer.md`). The decision owner can reverse any item, and decides MPC-P10.

## Evidence

- Core 2.1.0 definitions of the processes named above (`business_architecture/ontology/releases/core/2.1.0/core.ttl`).
- `business_architecture/business_process/downstream_process_map.json`, `value_stream_order_to_cash.json` and `data_product_portfolio.json`.
- EPM-DEC-001-0052, 0053, 0067, 0068, 0069.

## Consequences

- `party/lifecycle.csv` is the source of the links. `build_party.py` builds `lifecycle.ttl` from it, and fails unless each process is in core 2.1.0 (*2026-10-23:* core 2.3.0 since `party` 1.1.0, EPM-DEC-001-0092), each system is a customer system, each stage has a link, and each stage has exactly the links items 2 to 4 decide. The module's shapes check the decided links at graph level for each of the eleven stages that holds at least one lifecycle link, so there a real process or system on the wrong stage, a process that does not exist, or a correspondence these items do not grant fails. A stage with no link, a link under another predicate and a stage these items do not name are rejected by the build only. `scripts/check.sh` checks the file is current, and `test_party_lifecycle.py` pins the links by hand.
- The regression loads `lifecycle.ttl` with the module.
- MPC-P10 waits for the decision owner. *2026-10-23:* accepted (EPM-DEC-001-0087).
