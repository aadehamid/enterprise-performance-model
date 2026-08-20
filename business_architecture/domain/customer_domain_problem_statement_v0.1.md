# Customer Domain Problem Statement

**ID:** EPM-BA-CUST-001  
**Version:** 0.1  
**Status:** Draft  
**Owner:** Enterprise Performance Model initiative  
**Last updated:** 2026-08-20  
**Scope:** Downstream Oil & Gas Order-to-Cash Customer domain  
**Review trigger:** First approved Customer-domain conceptual/logical model and first source-to-Gold O2C integration proof

## Purpose

Define the enterprise Customer-domain problem that the Enterprise Performance Model homelab will model and demonstrate using synthetic but realistic Downstream Oil & Gas Order-to-Cash data.

This artifact establishes the problem boundary. It is not a canonical Customer data model, ontology, MDM design, or approved enterprise architecture decision.

## Enterprise problem statement

A Downstream Oil & Gas enterprise represents commercial parties differently across CRM, ERP, CTRM, terminal automation, billing, accounts receivable, collections, and supporting systems. These representations use inconsistent identifiers, names, aliases, party roles, account hierarchies, locations, lifecycle states, credit relationships, tax responsibilities, title-transfer relationships, and contractual relationships.

As a result, the enterprise cannot consistently determine which Customer-domain entity participates in a quotation, order, nomination, terminal release, custody-transfer ticket, title transfer, contract, invoice, payment, dispute, collection case, operational metric, or KPI.

The outcome is fragmented lineage, uncertain O2C association, degraded data quality, conflicting customer-level analysis, duplicated calculations, and limited ability to explain performance outcomes by customer.

## Why Customer is not one object

“Customer” is a contextual business role, not automatically one universal enterprise object. A legal organization, commercial account, invoice recipient, payment-responsible entity, delivery location, contract party, credit counterparty, tax-liable party, and title-transfer party can be related but distinct.

The same party may perform multiple roles in one transaction. Conversely, roles within one O2C transaction can be performed by different legal entities or accounts in a corporate hierarchy.

```text
Party / legal entity
  → customer account
  → party role in a commercial, financial, logistics, or operational context
  → participation in a specific O2C transaction
```

A repeated customer value across source tables can suggest a shared party, but it does not prove identity equivalence, role equivalence, title ownership, tax responsibility, or financial responsibility. Interpretation requires source semantics, transaction context, effective dates, cross-reference evidence, and governance review.

## Source-system perspectives

| Source-system perspective | Customer-like objects | Enterprise distinction preserved |
|---|---|---|
| Salesforce CRM | Account, Contact, account hierarchy, opportunity account, site, territory | Selling relationship and CRM ownership |
| SAP S/4 / ERP | Business Partner, customer, sold-to, ship-to, bill-to, payer, hierarchy | Legal party and ERP partner-role semantics |
| RightAngle / CTRM | Counterparty, contract party, pricing party, delivery party, credit counterparty | Commercial agreement, price, delivery, exposure, and credit context |
| Terminal automation system | Loading account, consignee, carrier, driver/company, terminal customer | Physical lifting and custody-transfer context |
| Billing, AR, collections | Invoice account, bill-to, payer, remit-to, dispute party, collection account | Billing, payment, receivable, and exception responsibility |
| Tax and exemption records | Tax-liable party, exemption-certificate party, reseller, tax reporting party | Fuel/excise-tax treatment and exemption responsibility |
| Identity-resolution staging | Source cross-reference, match candidate, candidate canonical party, match confidence, stewardship decision | Governed ambiguity, matching evidence, and review status |

## Customer-domain distinctions

The initial conceptual model must be able to distinguish at minimum:

| Concept | Definition |
|---|---|
| Party / Legal Entity | An individual, organization, or group that can hold rights, obligations, or business relationships |
| Customer Account | A commercial or operational account through which a party transacts |
| Customer Role | A defined role a party or account plays in a business context |
| Customer Location | A business, delivery, billing, or operational location associated with a party or account |
| Corporate Hierarchy | Parent/subsidiary, account, or other controlled relationship among parties |
| Commercial Contract | Agreement that governs commercial terms, pricing, eligibility, title, and obligations |
| Transaction Participation | A role-qualified association between a party/account and an order, ticket, invoice, payment, or case |
| Source Cross-Reference | A governed association between source-system objects and Customer-domain candidates |
| Match Decision | A confidence-scored and stewarded determination about a candidate correspondence |
| Survivorship Decision | A controlled choice of which attribute value is preferred for an approved use, without erasing source provenance |

Use a role-based pattern rather than modeling every role as a permanent subtype of `Customer`:

```text
Party
  ├── LegalEntity
  ├── Organization
  └── Person

CustomerAccount
PartyRole
TransactionPartyParticipation
SourceCrossReference
```

`TransactionPartyParticipation` should retain at least the transaction, party, account where applicable, role code, source system, source object ID, effective period, and evidence reference. This allows the same party to occupy several roles without implying that the roles are equivalent.

## Role catalogue

The initial Customer-domain model must support the following role distinctions.

### Release 0.1 — mandatory O2C and commercial roles

```text
Legal entity
Corporate parent
Customer account
Sold-to
Ship-to
Bill-to
Payer
Consignee
Carrier
Contract party
Pricing party
Credit counterparty
Invoice recipient
Source cross-reference / match candidate
```

### Release 0.2 — financial, title, tax, and exception roles

```text
Ordering party / order requester
Delivery party / receiving party
Title-transfer party
Tax-liable party
Exemption-certificate party
Guarantor / credit-support party
Remit-to party
Dispute party
Collection-responsible party
```

### Release 0.3 — advanced downstream commercial and logistics roles

```text
Broker / agent / marketer
Exchange counterparty
Forwarder / transport coordinator
Terminal operator
Storage account holder
Nominee / beneficial owner
```

`Ship-to`, `consignee`, and `delivery party` must not be assumed synonymous. A ship-to is commonly the ERP delivery recipient or location; a consignee is the party named to receive product in a transportation or custody-transfer context; delivery party is a canonical abstraction; and title-transfer party identifies the party to which ownership or responsibility transfers at the defined contractual point.

## Illustrative O2C role pattern

```text
Terminal custody ticket: TKT-2026-004812

Legal entity / corporate parent → GulfCo Holdings Corp.
Sold-to                         → GulfCo Retail Houston LLC
Consignee / ship-to             → GulfCo Retail Houston LLC
Bill-to / invoice recipient     → GulfCo Retail Holdings Inc.
Payer / remit-to                → GulfCo Treasury Services Inc.
Contract party                  → GulfCo Retail Holdings Inc.
Pricing party                   → GulfCo Retail Holdings Inc.
Credit counterparty             → GulfCo Holdings Corp.
Guarantor                       → GulfCo Holdings Corp.
Title-transfer party            → GulfCo Retail Houston LLC
Tax-liable party                → GulfCo Retail Holdings Inc.
Carrier                         → Pioneer Haulage LLC
```

This pattern is deliberately realistic: the party that receives product does not necessarily hold the contract, receive the invoice, pay the invoice, carry credit exposure, provide a guarantee, own title at a contractual transfer point, or bear a specific tax responsibility. The homelab must preserve these distinctions rather than flattening them into one `customer_id`.

## O2C and performance consequences

Customer identity and role fragmentation affects:

- Order eligibility, allocation, and credit checks.
- Terminal release, custody-transfer, delivery, title-transfer, and product attribution.
- Contract, pricing-index, differential, volume, and exchange-agreement association.
- Tax treatment, exemption evidence, invoice generation, billing timeliness, payment application, and unbilled exposure.
- Dispute, deduction, collection, and receivable analysis.
- Customer profitability, service, credit, and commercial performance measures.
- KPI input lineage, threshold interpretation, action ownership, and AI answers.

The first proof is the unbilled-O2C use case:

```text
Customer identity and role fragmentation
  → uncertain order / release / contract / invoice association
  → uncertain billing, title, credit, and tax context
  → uncertain unbilled population and aging
  → unreliable customer-level exposure analysis
  → need for governed structure, mappings, quality, lineage, and metrics
```

## Meaning, compute, and consume

The Customer-domain pilot follows the Enterprise Performance Model separation of concerns:

```text
MEANING — no KPI computation
  Customer domain model + process architecture
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

The Customer domain is a shared domain concept, not a KPI. A customer-related calculation or Databricks Metric View is not automatically an approved KPI. Formula logic is compiled and governed in the compute layer; ontology, catalog, graph, BI, and agents must not create competing formula definitions.

## Target architecture responsibilities

| Component | Responsibility |
|---|---|
| Sirius Web | Conceptual, logical, and physical Customer/O2C data model; ERDs; model releases |
| Lakebase Postgres | Synthetic source-specific O2C operational records |
| Databricks medallion architecture | Bronze source representations, Silver harmonization, Gold data products and derived O2C facts |
| Unity Catalog | Deployed-asset governance, technical metadata, access control, and native lineage |
| OpenMetadata | Open-source catalog, cross-platform observability, lineage visualization, ownership, glossary, and quality context |
| Apache Jena Fuseki | RDF/OWL/SKOS/SHACL semantics, mapping assertions, provenance, and SPARQL |
| Neo4j Community | Customer/O2C/model/KPI context graph, impact traversal, Cypher, and agent-serving layer |
| Databricks Metric Views | Reusable analytical measure and dimension definitions |
| KPI Store | Approved KPI definitions, formulas, result persistence, thresholds, ownership, evidence, and consumption contracts |
| Python agents and services | Controlled model generation, synthetic-data generation, integration, validation, release projection, and automation |

## End-to-end demonstration objective

The Customer-domain pilot is the business-domain entry point to an integrated Enterprise Performance Model demonstration. Its purpose is to show how a governed business problem moves through domain modeling, semantic meaning, physical implementation, performance measurement, lineage, quality controls, graph context, and agent-assisted consumption.

```text
Customer-domain problem
  → Sirius conceptual/logical/physical model
  → synthetic multi-system source records
  → Lakebase and Databricks Bronze/Silver/Gold data products
  → Unity Catalog and OpenMetadata lineage/observability
  → RDF/OWL/SKOS/SHACL semantics in Fuseki
  → Neo4j Customer/O2C/KPI context graph
  → Metric Views and KPI Store
  → FastAPI/MCP/agent question answering
```

The demonstration must support both deterministic governed KPI/metric retrieval and ad hoc contextual investigation. Example questions include:

- What is unbilled exposure this week by bill-to, consignee, credit-counterparty, or corporate-parent perspective?
- Why is this release unbilled, and which source records, role mappings, contract, title, tax, and quality checks support the explanation?
- Which source-system customer records are unresolved or conflicting, and which Gold facts, metrics, or KPIs are affected?
- Which Customer-domain model elements, Unity Catalog columns, and quality tests would be impacted if the bill-to or title-transfer relationship changes?

The original Gasoline Netback / Refining Margin CPG capstone remains the governed KPI Store pilot. The Customer/unbilled scenario is a Customer-domain and O2C integration proof that establishes reusable identity, role, lineage, quality, and semantic-context patterns.

## First implementation scope

The first Customer-domain vertical slice will:

1. Generate synthetic source-specific Customer-like records for CRM, SAP/ERP, CTRM, terminal, AR/collections, tax/exemption, and identity-resolution staging perspectives.
2. Model the conceptual, logical, and physical Customer/O2C domain in Sirius Web.
3. Preserve source-system identifiers and role semantics in Bronze.
4. Create role-aware, cross-referenced Customer-domain representations in Silver.
5. Build a Gold unbilled-exposure fact that retains role-qualified party links.
6. Associate model elements to ontology terms, Unity Catalog assets, quality controls, OpenMetadata metadata, and Neo4j context.
7. Expose governed measures through Databricks Metric Views and preserve candidate/approved KPI determination in the KPI Store.
8. Produce evidence-driven answers for customer, role, lineage, quality, and unbilled-exposure questions.

## Scope boundaries

In scope:

- Realistic but explicitly synthetic Downstream Oil & Gas O2C records.
- Source-system variants, cross-references, role-aware relationships, title/tax/credit context, and controlled match ambiguity.
- Customer-domain structure and mappings sufficient for the first O2C use case.
- Agent-assisted model generation subject to validation, review, and release controls.

Out of scope:

- A production CRM, ERP, SAP MDG, MDM, CTRM, terminal automation, tax, or collections implementation.
- Fully automated matching or survivorship without human review.
- A universal enterprise party ontology or a complete customer-360 product.
- Replacement of existing source-system operational ownership.
- Automatic approval of metrics as KPIs.

## Success criteria

The first proof is successful when:

- A reviewer can inspect conceptual, logical, and physical Customer/O2C ERDs.
- The same underlying party can be represented in multiple source-system and O2C roles without forced equivalence.
- A source object can be traced through cross-reference/match evidence to a role-qualified Customer-domain representation.
- A Gold unbilled fact can be traced through order, custody, contract, title, tax, invoice, and relevant customer-role relationships.
- The project can identify incomplete, conflicting, duplicate, or unresolved customer associations and show their impact on analytical eligibility.
- Technical lineage, quality results, semantic mappings, and performance measures are connected through stable, versioned identifiers.
- The system can answer which party was involved in an O2C event, in what role, from which source, with what identity confidence, and with what downstream metric/KPI impact.

## Open questions

- Which source-system variants are mandatory in the first synthetic release, versus staged later?
- What initial matching rules and confidence thresholds are appropriate for a synthetic pilot?
- Which attributes are eligible for survivorship, and which must remain source-specific?
- Which steward role approves match decisions and Customer-domain model releases?
- Is unbilled exposure classified as an operational metric, performance indicator, candidate KPI, or only a KPI Store technical-design test case?
- Which Customer-domain ontology terms exist already, and which require formal extension after the Sirius logical model is reviewed?

## Sources and traceability

- Existing `o2c-unbilled-databricks-free-cv-map` demonstration artifacts.
- Existing EPM O2C business architecture, KPI Store, ontology, and homelab materials.
- Meaning → Compute → Consume architecture diagram supplied by the project owner on 2026-08-19.
- Source-system semantics represented in synthetic form for learning and integration demonstration only.
- Model releases, mapping assertions, data-generation runs, quality results, and metric/KPI dependencies will be recorded as versioned project evidence.
