# The Problem: Unbilled O2C Exposure Is Also a Customer-Domain Problem

## Purpose

This demonstration shows how a Downstream Oil & Gas enterprise can identify, explain, govern, and consume unbilled Order-to-Cash exposure using a Databricks lakehouse, governed metric definitions, semantic context, and traceable data assets.

The demonstration uses synthetic but realistic O2C records. It does not represent a production implementation, a financial close, or an approved enterprise KPI.

## Immediate business problem

A downstream commercial organization may release product, complete a custody transfer, or otherwise fulfill an order before an invoice is issued, linked, or recognized in the expected billing process. The resulting unbilled population can represent revenue-recognition risk, billing-process delay, disputed fulfillment, incomplete source integration, or a data-quality problem.

The enterprise needs to answer questions such as:

- Which fulfilled O2C events remain unbilled?
- What is the unbilled quantity and monetary exposure?
- How old is each unbilled event?
- Which source event, commercial agreement, price basis, and billing condition explain the exposure?
- Is the condition operationally valid, a billing exception, or a data defect?
- Which customer, contract, terminal, product, and time-period views are valid for analysis?

## Upstream enterprise problem: fragmented customer identity and roles

Unbilled O2C exposure is not only a billing-timeliness problem. A downstream enterprise represents commercial parties differently across CRM, ERP, CTRM, terminal automation, billing, receivables, tax/exemption, collections, and supporting systems.

A Salesforce Account, SAP Business Partner, SAP customer role, RightAngle counterparty, terminal loading account, terminal consignee, ERP invoice account, tax-exemption party, and collections payer may refer to related parties. They can also represent different legal entities, commercial accounts, delivery locations, financial responsibilities, tax responsibilities, title-transfer parties, or credit relationships within one corporate family.

These source-specific records can use incompatible identifiers, names, account hierarchies, locations, lifecycle states, ownership structures, and business-role semantics. The same source-customer value can appear in multiple O2C tables because one party plays several roles, such as sold-to, ship-to, bill-to, payer, consignee, contract party, credit counterparty, title-transfer party, tax-liable party, or guarantor.

Repeated values are evidence for investigation, not proof of identity or role equivalence. Reliable interpretation requires transaction context, source-system semantics, effective dates, governed cross-reference evidence, and explicit role definitions.

## Why this matters for unbilled exposure

Without a governed Customer-domain model and controlled identity/role mappings, the enterprise cannot reliably associate a fulfillment event with the appropriate contractual, title, billing, payment, credit, tax, and performance context.

```text
Fragmented customer-like source objects
  → uncertain party identity, hierarchy, and role
  → incomplete O2C event association
  → unreliable delivery-to-contract-to-invoice linkage
  → uncertain billing, title, credit, and tax context
  → uncertain unbilled exposure and customer performance measures
```

For example, the party receiving a terminal release may be the ship-to or consignee, while the contract is held by a parent commercial entity, invoices are sent to a shared-services bill-to account, payments come from a treasury payer, credit exposure is held against a CTRM counterparty, title transfers to a delivery party, and tax responsibility belongs to a different entity. Treating these roles as one interchangeable `customer_id` can misstate unbilled exposure and invalidate customer-level performance analysis.

## Demonstration approach

The demonstration creates a governed, traceable path:

```text
Synthetic source-system party records
  → Bronze source representations
  → Silver role-aware Customer and O2C harmonization
  → Gold unbilled exposure fact
  → reusable metric definitions and Metric Views
  → governed metric / candidate-KPI context
  → contextual views, lineage, quality evidence, and AI consumption
```

The scope deliberately preserves source-system differences. It does not force every record into a presumed golden customer. It uses governed cross-reference, candidate-match, confidence, role, and stewardship concepts to make ambiguity visible and reviewable.

## Meaning, compute, and consume

The demonstration follows the Enterprise Performance Model separation of concerns:

```text
MEANING — no KPI computation
  Customer domain and O2C process architecture
  → ontology modules and controlled vocabulary
  → graph of meaning and named KPI context

COMPUTE
  Candidate KPI Register + Cataloging Store + Silver ingredients
  → Semantic Layer certified measure object
  → governed compiler/calculation process
  → Gold published result snapshot

CONSUME
  BI, in-platform AI, external graph/agent tools, automation, and APIs
```

The Customer domain is a shared domain concept, not a KPI. Unbilled exposure is a first derived operational measurement use case; its classification as an operational metric, performance indicator, candidate KPI, or approved KPI remains subject to KPI governance. A Metric View or calculation does not itself establish an approved KPI.

## Scope boundaries

In scope:

- Synthetic Customer/O2C data representing CRM, ERP, CTRM, terminal automation, billing/receivables, tax/exemption, collections, and customer identity-resolution staging perspectives.
- Unbilled exposure as the first derived operational measurement use case.
- Role-aware party relationships across order, contract, custody event, title transfer, invoice, payment, dispute, tax, and collection contexts.
- Lineage from source representation through lakehouse facts, metric definitions, and consuming analytical or AI surfaces.
- Data-quality controls for identity, relationship, completeness, timeliness, role consistency, and analytical eligibility conditions.

Out of scope:

- Full enterprise MDM, SAP MDG, CRM, ERP, CTRM, terminal-automation, tax, or collections-product implementation.
- Autonomous survivorship, automated master-data approval, or production identity resolution.
- Financial close, revenue-recognition policy, tax calculation, or formal regulatory reporting.
- Automatic classification of an unbilled measure as an approved enterprise KPI.

## Success criteria

The demonstration succeeds when it can:

1. Identify unbilled O2C events from controlled synthetic source data.
2. Trace an unbilled fact to fulfillment, contract, party-role, title, tax, and billing evidence.
3. Distinguish sold-to, ship-to/consignee, bill-to, payer, contract party, credit-counterparty, title-transfer, and tax-liability perspectives.
4. Show source-to-Bronze-to-Silver-to-Gold lineage for the unbilled fact.
5. Surface identity ambiguity, source cross-reference, match confidence, and quality-rule outcomes rather than hiding them.
6. Publish reusable analytical measures without treating every measure as an approved KPI.
7. Support a governed question such as: “Which unbilled terminal releases are attributable to this customer under the bill-to, consignee, title-transfer, tax-liable, and credit-counterparty perspectives?”

## Relationship to the Customer-domain problem statement

This document defines the first executable downstream O2C use case. The parent enterprise-domain problem, source-system variants, Customer role catalogue, target architecture responsibilities, and end-to-end demonstration objective are defined in:

```text
business_architecture/domain/customer_domain_problem_statement_v0.1.md
```
