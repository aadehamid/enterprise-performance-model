# EPM-DEC-001-0067: The Customer domain resumes on the decision owner's information: its sources, its scope and the plan

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-20 to 2026-10-21, for the sources, the scope, the five accepted recommendations, the two new roles, the visibility and the plan; the readings marked as Claude's delegated under EPM-DEC-001-0028) |
| Date | 2026-10-21 |
| Questions | Competency questions 19 to 26; EPM-DEC-001-0004 (Customer work waits for the decision owner's details); Phase C of EPM-DEC-001-0052; MPC-P06's channel dimension (EPM-DEC-001-0047, What follows, item 5) |
| Source | Claude Code session, 2026-10-20 to 2026-10-21 |

## Context

EPM-DEC-001-0004 held the Customer domain until the decision owner shared their customer information. EPM-DEC-001-0052 set its scope as Phase C: a conceptual data model of Customer, the customer lifecycle from onboarding as proposed process-map nodes, and the channel dimension of MPC-P06.

In this session the decision owner sent seven inputs, one at a time:

1. a diagram of how customer data is ingested, from the first request through credit and compliance approval to the systems that receive the customer;
2. a diagram of the applications the customer passes through, in three columns: create, enrich and consume;
3. a later, dated version of the second diagram's core path;
4. a diagram of the customer lifecycle in six stages;
5. a table of six core systems, each with the attributes that define a customer there (Create) and the attributes that enrich it afterwards (Enrich);
6. a conceptual data model of Customer: entities in four zones, their relationships, ten customer classes, and a pane showing where the customer shows up in systems;
7. an external research report on the Customer domain in downstream oil and gas.

None of these seven inputs is in the repository, by the decision owner's rule below. Input 7 is a report prepared on 2026-10-13. It is not the earlier customer report tracked at the repository root since 2026-08-21 (`Enterprise_Customer_Domain_Downstream_Oil_Gas_Report.pdf`, with `Customer Domain in Downstream Oil & Gas — Modeling Guide.html`, commit e96b7d0). Those two files predate this session, are not among the seven inputs, and the `customer` module does not cite them.

Claude asked questions about each input as it arrived. The decision owner's answers, with their full context, are saved in `answers-2026-10-21-customer.md`.

## Decision

**The decision owner's decisions:**

1. **Which open item they gave first:** "Customer information".
2. **The two candidates the peers' filings suggested** (a delivery-mode facet and a brand-licensing relationship, `reference/downstream-peers/customer-classification-evidence.md`): "decide once you've seen my data".
3. **The inputs stay out of the repository:** "all of the files and images should stay out of the repo, by the way."
4. **What may go in, and from which sources:** "yes, derived definitions can go in the repo. We will use repo information, MPC publickly published information for this. We can use Peer data to guide and resolve ambuiguity but peer data should not go into the repo at this point". Then: "Actually Peer comparison is fine to use as guidance. This rule is specifically for Customer domainhere is the next one" (the decision owner sent the rule and "here is the next one" without a space between them).
5. **What must be captured:** both categories of attributes ("These two categories of attrobutes must be captured"), and "both the life cycle and data flow of Customer". The conceptual data model is captured separately ("Which we want to capture separately").
6. **The attributes:** misspelled labels are corrected ("correct them"), repeated attributes are removed ("dedup them"), and the internal codes are resolved by search ("use external MPC search and Peer to resolve these ones.").
7. **The conceptual model's scope:** "nothing on the conceptual is out of scope".
8. **Two relationships:** "scoped to product connects to product from agreement" and "customer account connects to site throuhg" the relationship labelled supplied from.
9. **Abbreviations:** COCO, CODO and DODO as Claude read them ("correct."); "L&S is probably logistic and storage"; and for SDP, "let us just call it SDP for now?". A landscape system's name: "it is EIS".
10. **Claude's other recommendations on the research report:** "I am okay with the rest." These are items 1 to 5 under What follows.
11. **The plan, the visibility and the two roles:** "yes, keep it private, add both roles, go ahead".

**What follows (Claude, under EPM-DEC-001-0028):**

These items are Claude's wording. Items 1 to 5 are the recommendations the decision owner accepted with "I am okay with the rest".

1. **Direct dealers sit under a Fuel Supply agreement.** MPC's filings describe "long-term supply contracts with direct dealers who operate locations mainly under the ARCO® brand" (`reference/mpc/customer-classification-evidence.md`, C2). No MPC filing describes a brand licence for them. Their brand reaches the site through a Site Brand Assignment.
2. **Four classes from MPC's filings are to be added**, in the `customer` module's pull request, to the conceptual model's ten: independent retailer (C4), unbranded customer (C5), spot market buyer (C6) and crude oil customer (C8). That makes 14 customer classes.
3. **The exchange or trading counterparty stays a customer class.** The conceptual model already says it becomes a customer only when a revenue-recognized relationship exists.
4. **"Authorizes brand at site" points to Site Brand Assignment,** not to Site. The conceptual model defines a site brand assignment as linking a site to a brand "under an AGREEMENT". The decision owner said they did not see this relationship in their diagram. Claude showed them where it is drawn, and they did not ask for it to be removed.
5. **MPLX's filings count as MPC's public information.** MPC consolidates MPLX.
6. **Sources for the Customer domain**, by item 4 of the decision owner's decisions:
   - The repository cites only repository information and MPC's public information, MPLX's included.
   - Peer filings and the external report guide choices but are not cited.
   - Elsewhere in the repository, peer comparison stays allowed as guidance and as evidence, as before.
7. **L&S is Logistics and Storage.** MPLX's FY2023 Form 10-K, filed 2024-02-28 (accession 0001552000-24-000007), names "Logistics and Storage (“L&S”)" as one of its two segments. By FY2025 MPLX calls that segment Crude Oil and Products Logistics.
8. **SDP stays a label without an expansion.** No MPC or MPLX filing contains it, by EDGAR full-text search on 2026-10-21.
9. **The two peer candidates are covered by the decision owner's own model,** so neither is added separately. A customer account carries a delivery tier. A brand is owned by or licensed to a party through a Brand License agreement.
10. **Two roles are to be added**, in the `customer` module's pull request, to the conceptual model's twelve, by "add both roles": Position Holder and Loading-Authorized Party. They answer competency question 22.
11. **The repository stays private** for the whole Customer work, by "keep it private". The Customer modules hold internal system and field names, which EPM-DEC-001-0040 item 3 allows only while the repository is private. GitHub does not enforce ruleset 25440735 on a private repository. So each Customer pull request merges through `merge-on-verdict.sh`, which waits for a MERGE verdict on the current head and for `checks` to pass.
12. **The plan, in five pull requests:**
    1. this record;
    2. the `customer` module, the conceptual model;
    3. the systems, the data flow and the attributes;
    4. the lifecycle, with a process-map proposal for the stages the map lacks;
    5. competency questions 19 to 26.
    - MPC-P06's channel dimension is applied in pull request 2.
    - The process map changes only after the decision owner approves the proposal.
    - `customer` 1.0.0 is released only with their approval.
13. **Still open from EPM-DEC-001-0004:** the lubricants and marine product-line evidence. None of the inputs covers it. It is settled or parked in pull request 2.

## Alternatives considered

- **Commit the decision owner's diagrams and table as reference files.** Not chosen: they asked for the files to stay out.
- **Cite peers' filings for the Customer domain, as `customer-classification-evidence.md` did.** Not chosen: the decision owner limited the Customer domain to repository and MPC sources.
- **Keep Agreement, Site, Site Brand Assignment and Party Transaction Association out of scope**, as Claude first recommended. Not chosen: the decision owner put every entity in scope.
- **Frame direct dealers with a Brand License agreement**, as the conceptual model's class note does. Not chosen: MPC's filings describe supply contracts and no licence.
- **Make the repository public while the pull requests merge**, as EPM-DEC-001-0050's amendment allows, so the ruleset is enforced. Not chosen: the decision owner kept it private.

## The decision owner's recorded words

In the Claude Code session of 2026-10-20 to 2026-10-21 (saved in `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-10-21-customer.md`):

- "Customer information"
- "decide once you've seen my data. I will share them one at a time to process"
- "all of the files and images should stay out of the repo, by the way."
- "yes, derived definitions can go in the repo. We will use repo information, MPC publickly published information for this. We can use Peer data to guide and resolve ambuiguity but peer data should not go into the repo at this point"
- "Actually Peer comparison is fine to use as guidance. This rule is specifically for Customer domainhere is the next one"
- "These two categories of attrobutes must be captured"
- "correct them", "dedup them", "use external MPC search and Peer to resolve these ones."
- "Now make sure you have all of this captured to represent both the life cycle and data flow of Customer ."
- "Which we want to capture separately."
- "they are in scope"
- "scoped to product connects to product from agreement", "customer account connects to site throuhg" and "I did not see"
- "correct. L&S is probably logistic and storage."
- "let us just call it SDP for now?"
- "nothing on the conceptual is out of scope"
- "I am okay with the rest. and it is EIS"
- "yes, keep it private, add both roles, go ahead"

The readings marked as Claude's above are under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

- `answers-2026-10-21-customer.md`.
- `business_architecture/reference/mpc/customer-classification-evidence.md` (C1 to C8) and `mpc-fy2025-10k-fact-sheet.md` (direct dealers).
- MPLX FY2023 Form 10-K, https://www.sec.gov/Archives/edgar/data/1552000/000155200024000007/mplx-20231231.htm, retrieved 2026-10-21.
- EPM-DEC-001-0004, 0005, 0028, 0040, 0047, 0050, 0052.

## Consequences

- EPM-DEC-001-0004's wait is over. Competency questions 19 to 26 still wait until the `customer` module answers them.
- The regression stands at 34 answerable, 1 partial and 9 waiting.
- The repository stays private until the Customer work is done.
