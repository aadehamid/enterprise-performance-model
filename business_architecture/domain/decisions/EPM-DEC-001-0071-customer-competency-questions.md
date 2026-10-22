# EPM-DEC-001-0071: Competency questions 19 to 26 answered by the `party` module

| Field | Value |
|---|---|
| Status | Decided (delegated under EPM-DEC-001-0028; the real organisations of item 3 by the decision owner, 2026-10-21) |
| Date | 2026-10-21 |
| Questions | Competency questions 19 to 26 (section VII, "Customer / Party — first domain module"); pull request 5 of EPM-DEC-001-0067's plan |
| Source | Claude Code night run, 2026-10-21 |

## Context

Questions 19 to 26 waited for the Customer module (EPM-DEC-001-0004, then EPM-DEC-001-0067). The `party` module now holds the decision owner's conceptual model (EPM-DEC-001-0068), the systems and attributes (EPM-DEC-001-0069) and the lifecycle (EPM-DEC-001-0070). Each question gets a SPARQL query in `regression/queries/`, run by `scripts/check.sh` against the release and the module graphs (EPM-DEC-001-0019).

## Decision

**What follows (Claude, under EPM-DEC-001-0028):**

1. **Each question's answer, and the query that tests it:**

   | Q | Answer in the graph | Queries |
   |---|---|---|
   | 19 | A party is the identity of a person or an organization. A customer account is the container the party transacts through. They are two classes, and an account is not a kind of party. | `q19-party-vs-account.rq` |
   | 20 | Any role in the party-role list. A party plays any number of roles at once, as MPC and MPLX do. | `q20-roles-one-party.rq`, `q20b-real-parties-both-ways.rq` |
   | 21 | Roles are dated holds, not subclasses of party. A ship-to is a site, and the party that receives product there holds the Consignee role. No Ship-To role exists. | `q21a-roles-are-dated.rq`, `q21b-ship-to-is-a-site.rq`, `q21c-no-ship-to-role.rq` (must be none) |
   | 22 | A Loading-Authorized Party is a role held for a period. The permission that grants it is a separate record, the authorization. | `q22-loading-authorized-party.rq` |
   | 23 | Credit sits on the customer account. A credit roll-up relationship counts one role's exposure under another's. | `q23-where-credit-sits.rq` |
   | 24 | Yes. A party plays several role nodes, each with its kind from the one party-role list (Sold-To, Supplier and Exchange Counterparty among them), its dates and the agreement it works under, so the same organisation can hold one role in one deal and another in the next. MPC holds roles of two kinds. There is no second "Customer" class. | `q24a-one-party-many-roles.rq`, `q24b-no-customer-class.rq` (must be none) |
   | 25 | A customer-grained measure binds to the customer account by default. A measure about one role binds to that role, and a measure about a location binds to the site. None binds to the bare word customer. | `q25-measure-binding.rq` |
   | 26 | A party transaction association names the role a party played in the transaction, and the agent must refuse "who is the customer" without a role (the consumer rule, which relies on `party:roleType`). | `q26-one-role-per-order.rq` |

2. **Question 25's binding rule** is a scope note on `party:CustomerAccount`. Core 2.1.0's wording rules out the collapsed customer and names the account among the levels:
   - Establish Credit Limit & Risk Code (CM 1.3.7.4.2) says limits and risk codes "attach at the level the governed customer-domain model defines" and are "never assigned to a collapsed 'customer'".
   - Monitor Credit Against Limit (CM 1.3.7.4.3) says exposure "aggregates at the Party/Customer Account/credit-group level".
   - Analyze Customer Profitability (CM 1.3.7.2.5) analyzes "customers, accounts, channels, and segments".
   - Choosing the account as the default grain is this record's, under the delegation: credit terms and the customer class sit on the account (EPM-DEC-001-0068), and exposure aggregates from it. A named role or a site is the grain when the measure is about one of them.
3. **Section VII's done-when, with real organisations.** It asks for five real multi-role organisations described both ways. Customer records stay out of the ontology (EPM-DEC-001-0005), and the decision owner's customer data is not in the repository (EPM-DEC-001-0067). The decision owner chose the real ones: "use MPC and MPLX as the real organisations" (`answers-2026-10-21-real-parties.md`).
   - `party/reference-parties.ttl` describes them on ref-mpc's IRIs, as public reference facts (EPM-DEC-001-0005): MPC holds the Throughput Holder and Payer roles, and MPLX the Carrier and Vendor roles, under MPLX's fee-based agreements with minimum volume commitments with MPC. Each role holds from 2012-10-31, the date of the first agreements the filing's exhibit index lists (Exhibits 10.1 and 10.2). Each role cites MPLX's FY2025 Form 10-K (`reference/mpc/mplx-fy2025-10k-fact-sheet.md`, section 3). No transaction, price or volume is recorded.
   - Query `q20b-real-parties-both-ways.rq` reads them party to roles and role to party, and `test_party.py` pins both ways by hand. The five invented organisations of `examples.ttl` stay as test fixtures.
   - The done-when names five organisations; the decision owner chose these two. That is their decision, recorded here.
4. **Two negative tests** in `regression/test_run.py` show the "must be none" queries fire: adding a Ship-To role fails question 21, and adding a Customer subclass of party fails question 24.

## The decision owner's recorded words

On section VII's done-when, in the Claude Code session of 2026-10-21 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-real-parties.md`): "use MPC and MPLX as the real organisations".

The rest of this record is Claude's, under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

- Core 2.1.0's wording on CM 1.3.7.4.2 and CM 1.3.7.4.3 (their scope notes) and CM 1.3.7.2.5 (its definition) (`business_architecture/ontology/releases/core/2.1.0/core.ttl`).
- `business_architecture/ontology/competency-questions.md`, section VII.
- EPM-DEC-001-0005, 0019, 0061, 0067, 0068, 0069, 0070.

## Consequences

- MPLX's FY2025 Form 10-K, which the reference parties cite, is a described source (`src:mplx-s01`) in evidence tier 2, as one of the MPC evidence files in `reference/mpc/` (EPM-DEC-001-0059).
- The regression stands at 42 answerable, 1 partial (Q7) and 1 waiting (Q17, EPM-DEC-001-0045).
- The `party` module is not released. A release needs the decision owner's approval. *2026-10-22:* released as 1.0.0 with their approval (EPM-DEC-001-0074).
