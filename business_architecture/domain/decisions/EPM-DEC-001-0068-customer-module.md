# EPM-DEC-001-0068: The `party` module: the decision owner's conceptual model as classes, properties and code lists

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028) |
| Date | 2026-10-21 |
| Questions | Competency questions 19 to 26 (answered in pull request 5 of EPM-DEC-001-0067's plan); MPC-P06's channel dimension (EPM-DEC-001-0047, What follows, item 5); EPM-DEC-001-0004's lubricants and marine evidence |
| Source | Claude Code night run, 2026-10-21, pull request 2 of EPM-DEC-001-0067's plan |

## Context

EPM-DEC-001-0067 records the decision owner's customer information, their rules for it and a five-PR plan. Their conceptual data model of Customer has four zones:

- **identity:** party, external identifier, address, contact point;
- **customer anatomy:** party role, party relationship, customer account, customer class, line of business, brand, agreement, site brand assignment;
- **operational context:** party transaction association, product, site;
- **customer classes:** ten classes in four groups.

Every entity is in scope ("nothing on the conceptual is out of scope", EPM-DEC-001-0067). The model is not in the repository. This record turns it into a module and records the choices the model leaves open.

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **A new `party` module**, namespace `https://w3id.org/lsc/ontology/modules/party/`, prefix `party:`, in `business_architecture/ontology/party/`. It is named `party` because the 2026-09-18 module policy makes `party` the sole concept-owning module for the Customer domain, with no `customer` module (`ontology-worklog.md`, step 1 and the Modeling group; `ontology-playbook.md`, Modules). It holds definitions only: no real customer, account or site (EPM-DEC-001-0005). It depends on no other module. Its five example organizations, in `examples.ttl`, are invented test fixtures and are not loaded with the module.
2. **Fifteen entity classes, one per entity, plus Person and Organization: 17 classes in all.** Each definition is Claude's wording of the decision owner's entity. Party has two subclasses, Person and Organization, which are disjoint. They are the only subclasses of party. Product stands in for a Product domain that this repository does not model yet: the class has a definition but no properties or values. *2026-10-23:* `party:Product` has values since `party` 1.1.0: the products MPC's FY2025 Form 10-K names (EPM-DEC-001-0092).
3. **Party roles are dated nodes, not subclasses** (ontology-playbook.md, Step 5). A `party:PartyRole` is held by exactly one party (`party:plays`), has one role type from the party-role list, and is held from a start date (`party:validFrom`) to an optional end date. So one party holds any number of roles at once, and "customer" is never a class of party. A shape rejects any other subclass of party.
4. **The role list has fourteen types:**
   - the model's twelve: Sold-To, Payer, Bill-To, Consignee, Jobber, Dealer, Exchange Counterparty, Throughput Holder, Carrier, Vendor, Surety and Supplier;
   - the two the decision owner added: Position Holder and Loading-Authorized Party (EPM-DEC-001-0067, decision 11; What follows, item 11).
5. **Ship-To is a site, not a role.** The decision owner's inputs list Ship-Tos together with stations, and their role list has no Ship-To. So a ship-to is a `party:Site`, and the party that receives product there holds the Consignee role. This is competency question 21's answer. Systems that keep a ship-to as its own customer number (the decision owner's inputs make Dealer Master the system of record for ship-tos) hold, in this model, one site plus a party in the Consignee role; one sold-to can have many ship-to sites, and the sold-to party can also be the consignee.
6. **The customer class is a dated assignment.** The decision owner's model gives each class assignment to an account its own effective dates. So `party:CustomerClass` is the assignment node: one account, one value from the customer-class list, and a start date. A line of business carries no dates in the model, so `party:managedUnder` links the account to it directly.
7. **Fourteen customer classes in four groups:**
   - the model's ten;
   - the four EPM-DEC-001-0067 adds from the repository's MPC customer classification: independent retailer (C4) and unbranded customer (C5) under Wholesale and unbranded, and spot market buyer (C6) and crude oil customer (C8) under Trading counterparties.
   - The crude oil customer's group follows MPC's own words. MPC's FY2025 Form 10-K reports crude oil revenue from external customers in Refining & Marketing (Note 20) without naming the buyers, and says: "We mitigate credit risk with master netting agreements with companies engaged in the crude oil or refinery feedstock trading and supply business or the petroleum refining industry" (Note 2). Its FY2017 Form 10-K ties those agreements to "sales of crude oil or refinery feedstocks". MPC's filings tie part of these sales to trading and supply companies and refiners, and do not say who all the buyers are (`customer-classification-evidence.md`, C8). Placing the class under Trading counterparties is this record's reading of that wording.
   - The spot market buyer joins Trading counterparties too, not Wholesale and unbranded. MPC's FY2025 Form 10-K, Item 1, says: "We compete in four distinct markets for the sale of refined products—wholesale, including exports, spot, branded and retail distribution", and a note to its refined product sales volumes splits them into volumes "marketed directly to end-users" and "trading/supply volumes such as bulk sales to large unbranded resellers and other downstream companies". Spot is a market of its own. This record reads spot sales as part of the trading and supply volumes; the filing does not say so, and who the spot buyers are is not stated, so the group is this record's reading.
   - Independent retailer and unbranded customer sit in Wholesale and unbranded. MPC lists "independent retailers" beside "wholesale customers" (Item 1) and apart from brand jobbers and direct dealers; its unbranded marketing page names "independent marketers, commercial end-users, unbranded distributors and high-volume retailers" (`customer-classification-evidence.md`, C5). Placing independent retailers there is this record's reading.
   - The groups are top concepts; a class assignment must name a class, not a group.
8. **The channel dimension of MPC-P06 gets its values.** Each class that matches one of MPC's classes C1 to C8 carries its code as `party:mpcClassification`, and each code is used exactly once:

   | Code | Customer class |
   |---|---|
   | C1 | Branded jobber |
   | C2 | Direct dealer |
   | C3 | Wholesale marketing customer |
   | C4 | Independent retailer |
   | C5 | Unbranded customer |
   | C6 | Spot market buyer |
   | C7 | Export customer |
   | C8 | Crude oil customer |

   The other six classes have no MPC code. This builds the values of option A of P06, which the decision owner chose (EPM-DEC-001-0047): "Channel as a dimension, built from C1 to C8" (the option's wording in `decision-packages/2026-10-14/step7-rulings.md`, P06), with no process-map change. An account's channel is its customer class. P06 also suggested that the channel become a dimension of Order Management or of KPIs. That is not done here. *Trigger:* a measure or process that needs a channel breakdown.
   - The codes are a property on the module's classes, not their own SKOS scheme as `data-domain-register.md` once proposed. One class list, carrying the codes, avoids two schemes for the same customers, and the module's definitions are in Claude's words, not MPC's (EPM-DEC-001-0067).
9. **Direct dealers sit under Fuel Supply.** The class definition names a long-term supply agreement and a site brand assignment, not a Brand License (EPM-DEC-001-0067, What follows, item 1).
10. **Code lists, as SKOS schemes** built from `code-lists.csv`:
    - party types (2), party roles (14), relationship types (5), agreement types (7);
    - lines of business (10, with SDP as a label only, EPM-DEC-001-0067);
    - customer classes (14 and 4 groups), site types (6), operating models (3: COCO, CODO, DODO);
    - identifier types (4), address usages (4), contact types (3), transaction kinds (7).
    - Each value has a definition in Claude's words. Agreement types overlap, so an agreement can have more than one.
11. **Relationships follow the decision owner's labels and their two rulings** (EPM-DEC-001-0067):
    - Agreement is scoped to Product, and Customer Account is supplied from Site.
    - "Authorizes brand at site" runs from Agreement to Site Brand Assignment.
    - A brand reaches a party through an agreement (`party:coversBrand`). A party owns or operates a site through a role held at the site (`party:atSite`), which carries the role's dates.
12. **Account facets without values.** Brand status, contract type, product line, segment, geography and delivery tier are secondary facets of the account in the model. The module declares one property for them, `party:accountFacet`, and defines no values: the inputs name the facets but not their values. Statuses (party, account) are likewise declared without a list.
13. **Mappings, not imports** (EPM-DEC-001-0023). Party, Person and Organization carry `skos:closeMatch` to FOAF and W3C ORG. Nothing is imported. The PIDX and OEO mappings still wait for product concepts (EPM-DEC-001-0064): the product line is a facet with no values yet.
14. **The lubricants and marine product-line evidence is parked.** EPM-DEC-001-0004 held this evidence check with the Customer work. None of the decision owner's inputs names lubricants or marine. The product line is a facet with no values in this module. *Trigger:* the product line's values are defined, here or in a Product domain.
15. **SHACL** (`shapes.ttl`), run with every other module's shapes on the whole graph (EPM-DEC-001-0065). The shapes check:
    - each party is a person or an organization, with one legal name and a matching party type;
    - each role is held by one party, with one role type from its list, a start date, and no end before its start;
    - each relationship links two roles;
    - each account belongs to a party;
    - each class assignment names a class, not a group, and has a start date;
    - each site brand assignment names a brand and a site, and is made under an agreement;
    - each coded value comes from its own list;
    - no class other than person and organization is a subclass of party, directly or through any chain of subclass links.

## Alternatives considered

- **Customer as a subclass of party, or one subclass per role.** Not chosen: a party holds several roles at once and over time (playbook Step 5). Competency questions 19 to 24 ask exactly for this.
- **Ship-To as a role.** Not chosen: the decision owner's role list has no Ship-To, and their inputs place it with stations and sites.
- **Customer class as a direct property of the account.** Not chosen: the model gives class assignments effective dates.
- **Extend the `organization` module.** Not chosen: that module models the company's own roles and RACI, which are positions people hold. A customer's party role is a different thing, and keeping them apart avoids two meanings of "role" in one module.
- **Load the example organizations with the module.** Not chosen: they would be data in the ontology (EPM-DEC-001-0005). They stay test fixtures.

## The decision owner's recorded words

This record is Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). It builds on the decision owner's words recorded in EPM-DEC-001-0067 (`answers-2026-10-21-customer.md`). The decision owner can reverse any item.

## Evidence

- EPM-DEC-001-0067, and the decision owner's words in `answers-2026-10-21-customer.md`.
- `business_architecture/reference/mpc/customer-classification-evidence.md` (C1 to C8).
- MPC Form 10-K for FY2025 (Item 1, competition; the refined product sales volumes; Note 2; Note 20), https://www.sec.gov/Archives/edgar/data/1510295/000151029526000009/mpc-20251231.htm, and for FY2017 (Summary of Principal Accounting Policies, accounts receivable), https://www.sec.gov/Archives/edgar/data/1510295/000151029518000024/mpc-20171231x10k.htm, both read 2026-10-21. A search of peers' filings and of SAP and PIDX practice guided items 5 and 7 (EPM-DEC-001-0067 allows peer data as guidance in the Customer domain); none is cited.
- `ontology-playbook.md`, Step 5.
- EPM-DEC-001-0004, 0005, 0023, 0047, 0064, 0065.

## Consequences

- The `party` module is built and checked by `scripts/check.sh`: the code lists must equal a fresh build, and `test_party.py` checks the lists, the vocabulary, the five organizations both ways and the shapes. It is loaded with the regression graph, and its shapes join the Step 9 gate.
- The module is not released. A release needs the decision owner's approval. *2026-10-22:* released as 1.0.0 with their approval (EPM-DEC-001-0074).
- The regression stands at 34 answerable, 1 partial and 9 waiting. Questions 19 to 26 move in pull request 5. *2026-10-21:* the `party` module made Q19 to Q26 answerable: 42 answerable, 1 partial (Q7), 1 waiting (Q17) (EPM-DEC-001-0071). *2026-10-23:* the decision owner parked Q17 until the ontology is first shared with business consumers: 43 answerable, 0 partial, 0 waiting and 1 parked (EPM-DEC-001-0086).
