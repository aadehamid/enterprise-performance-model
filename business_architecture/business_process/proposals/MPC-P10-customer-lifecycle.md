# Proposal MPC-P10: the customer lifecycle in the process map

| Field | Value |
|---|---|
| Status | Accepted (the decision owner, 2026-10-23, EPM-DEC-001-0087): P10.1 option A, P10.2 option A and P10.3. Each lands in a release: `core` 2.3.0, `value-stream` 1.1.0 and `data-product` 1.1.0 (EPM-DEC-001-0088) |
| Date | 2026-10-21 |
| Decision | EPM-DEC-001-0067, What follows, item 13 (the plan): "the lifecycle, with a process-map proposal for the stages the map lacks"; EPM-DEC-001-0070 records the lifecycle's mapping |
| Source | The decision owner's customer lifecycle and data-flow inputs (EPM-DEC-001-0067; not in the repository), mapped to `downstream_process_map.json`, `value_stream_order_to_cash.json`, `data_product_portfolio.json` and core 2.1.0's definitions |

## What the map already has

The decision owner's lifecycle has six stages: prospect, onboarding, payment management, risk management, relationship management and offboarding. Most of its work is already in the process map. EPM-DEC-001-0070 links each stage to these processes:

| Stage | Processes (core 2.1.0 names) |
|---|---|
| Prospect | CM 1.3.6.2.1 Manage Sales Pipeline; CM 1.3.6.6.1 Set Up Prospect; CM 1.3.7.4.2 Establish Credit Limit & Risk Code |
| Onboarding | CM 1.3.7.4.6 Perform KYC Due Diligence; CM 1.3.7.4.2; CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data; CM 1.3.7.2.1 Establish Commercial Terms & Contracts |
| Payment management | CM 1.3.8.2.1 Record Customer Receipts and Payment Notifications; CM 1.3.8.2.3 Apply Receipts; CM 1.3.8.3.2 Manage Receivables Collections |
| Risk management | CM 1.3.7.4.3 Monitor Credit Against Limit; CM 1.3.7.4.4 Analyze Portfolio Credit Risk |
| Relationship management | CM 1.3.6.2.2 Manage Key Accounts; CM 1.3.7.5.5 Conduct Customer Service Reviews; CM 1.3.7.2.6 Manage Customer Portal; CM 1.3.7.4.2, whose periodic reviews include the annual credit limit review |
| Offboarding | CM 1.3.7.4.5 Perform Credit-Driven Customer Closure and Reinstatement; CM 1.3.7.1.1, which retires the records |

Three things are missing.

## The proposals

### MPC-P10.1: onboarding coordination for every customer, not only card programs

- **Gap.** Core 2.1.0's scope note for Maintain Customer and Commercial Account Master Data (CM 1.3.7.1.1) says the process decides nothing about qualification, credit or KYC: those are "decided by their owning processes (prospect onboarding coordination, …)", and "Record creation is requested through governed submission (the Set Up Prospect rule, owner's side)". Its scope note for Perform KYC Due Diligence (CM 1.3.7.4.6) says "KYC outcomes gate onboarding (Set Up Prospect requires them; customer master records them)". The map's only onboarding coordinator for commercial customers is CM 1.3.6.6.1 Set Up Prospect (trading counterparties have CM 1.2.1.2.1 Create New Counterparty). It sits under CM 1.3.6.6 Loyalty and Cards Management, and its core definition covers "prospective program-member/cardholder onboarding". The decision owner's lifecycle onboards every customer through the same steps: a first record (a prospect in Salesforce for most customers; jobbers start in Dealer Master and direct dealers in SAP MDG, EPM-DEC-001-0069), the credit and compliance checks, the customer created in SAP MDG, then set up in the systems that use it.
- **Options:**
  - **A (recommended).** Add one L5 process under the L4 CM 1.3.7.1 Manage Commercial Master Data Stewardship, for example CM 1.3.7.1.7 "Coordinate Customer Onboarding". It would cover capturing the setup request, initiating credit, KYC and contract controls through their owners, requesting the governed master record, and confirming the customer is set up in the systems that use it. Setup Prospect stays as the card-program case.
  - **B.** Widen CM 1.3.6.6.1's scope to every customer and move it under CM 1.3.7. Not recommended: moving a node changes its place in the taxonomy, and its card-program steps would no longer fit. CM 1.2.1.2.1 Create New Counterparty is a precedent for an onboarding process kept beside the process it serves.
  - **C.** Change nothing, and let the lifecycle's prospect and onboarding stages rest on the existing processes. The gap the core definitions name stays open.
- *2026-10-23:* **Applied.** The decision owner chose A (EPM-DEC-001-0087). `downstream_process_map.json` holds CM 1.3.7.1.7 Coordinate Customer Onboarding under CM 1.3.7.1, and the curated Step 2 identity map holds its row. It enters the ontology in `core` 2.3.0 (EPM-DEC-001-0088).

### MPC-P10.2: link the Order to Cash credit review to its process

- **Gap.** In `value_stream_order_to_cash.json`, the process "Review Credit Limit & Risk Code" (`p-otc-review-credit-limit-risk-code`) has no `linkedProcessIds`. Every other Credit & Risk process has one. Core 2.1.0's scope note for CM 1.3.7.4.2 Establish Credit Limit & Risk Code lists "periodic and event-triggered reviews" in its scope.
- **What the file already records.** Its `gapAnalysis` lists this item as "missing" with closest process `CM 1.3.7.4.3`, and the process's rationale says: "Present in the O2C process with a definition; no dedicated L5 in LSC. Closest: Monitor Credit Against Limit (CM 1.3.7.4.3)."
- **Options:**
  - **A (recommended).** Set its `linkedProcessIds` to `["CM 1.3.7.4.2"]`. The step revises the credit limit and risk code, which CM 1.3.7.4.2 decides and reviews ("periodic and event-triggered reviews"); monitoring (CM 1.3.7.4.3) watches exposure against a limit and does not decide it. The decision owner's relationship-management stage names the annual credit limit review.
  - **B.** Set it to `["CM 1.3.7.4.3"]`, the closest process the file records.
  - **C.** Leave it unlinked, as the file's gap analysis records.
- *2026-10-23:* **Applied.** The decision owner chose A (EPM-DEC-001-0087); `value-stream` 1.1.0 carries the link, and the gap-analysis entry is removed (EPM-DEC-001-0090).

### MPC-P10.3: a customer master data product

- **Gap.** `data_product_portfolio.json` has no data product for the customer master. The decision owner's inputs name one: a data products platform that serves the customer master, sales, credit exposure and delinquency, fed by the customer data store.
- **Proposal.** Add a "Customer Master" data product to the Marketing & Sales line (`dpl-marketing-sales`), produced by CM 1.3.7.1.1 Maintain Customer and Commercial Account Master Data (the process map's name for it is Maintain Customer Master Data). The data-product module then links it like the others (EPM-DEC-001-0053).

## How the ontology takes it

- An accepted new process gets an ID, a slug and a definition (Steps 2 and 3), and lands in the next `core` release, which needs the decision owner's approval. *2026-10-22:* under the module policy (worklog, "Who approves a release"; EPM-DEC-001-0037), a minor or patch release is the module owner's and a major the decision owner's; Claude asked the decision owner before every release issued on 2026-10-22 (EPM-DEC-001-0074, and 0076 to 0080).
- The value-stream link and the data product are rebuilt by their modules' builds.
- The lifecycle's links in the `party` module then gain the new process.
