# EPM-DEC-001-0067: The Customer domain resumes on the decision owner's information: its sources, its scope and the plan

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-10-20 to 2026-10-21, for the sources, the scope, the five accepted recommendations, the two new roles, the visibility and the plan; the readings marked as Claude's delegated under EPM-DEC-001-0028) |
| Date | 2026-10-21 |
| Questions | Competency questions 19 to 26; EPM-DEC-001-0004, whose wait for the decision owner's details this record ends; Phase C of EPM-DEC-001-0052; MPC-P06's channel dimension (EPM-DEC-001-0047, What follows, item 5) |
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

Claude asked questions about each input as it arrived. The decision owner's answers are saved in `answers-2026-10-21-customer.md`, 17 blocks. Its header comment, in Claude's words, records the question each block answers, including the six recommendations block 14 answers.

## Decision

**The decision owner's decisions** (their words, with the block of `answers-2026-10-21-customer.md` each is in; the question each answers is in that file's header comment):

1. "Customer information" (block 1).
2. "decide once you've seen my data. I will share them one at a time to process" (block 2).
3. "all of the files and images should stay out of the repo, by the way." (block 4).
4. "yes, derived definitions can go in the repo. We will use repo information, MPC publickly published information for this. We can use Peer data to guide and resolve ambuiguity but peer data should not go into the repo at this point" (block 5), then "Actually Peer comparison is fine to use as guidance. This rule is specifically for Customer domainhere is the next one" (block 6).
5. "Now here are the core system and attributes that defines a customer in each system. And also attributes used to enrich customer in each system. These two categories of attrobutes must be captured" (block 7).
6. Block 8, in full:
   > 3. correct them
   > 1. dedup them
   > 2. use external MPC search and Peer to resolve these ones.
7. "Now make sure you have all of this captured to represent both the life cycle and data flow of Customer ." and "I will share the conceptual data model for customer next. Which we want to capture separately." (block 9).
8. Block 11, in full:
   > 1. they are in scope
   > 2. scoped to product connects to product from agreement, customer account connects to site throuhg "supplied from". I did not see "authorizes brand at site
   > 3. correct. L&S is probably logistic and storage. can you confrim that and SDP through an external search when you are ready.
9. "let us just call it SDP for now?" (block 13).
10. Block 14, in full:
    > 1. nothing on the conceptual is out of scope
    > I am okay with the rest. and it is EIS
    > bring me the plan
11. "yes, keep it private, add both roles, go ahead" (block 15).

**What follows (Claude, under EPM-DEC-001-0028):**

These items are Claude's wording and Claude's reading of the decision owner's answers. Items 1 to 5 restate recommendations 2 to 6 of block 14's question (the answers file's header comment), which the decision owner accepted with "I am okay with the rest"; they rejected recommendation 1 with "nothing on the conceptual is out of scope".

1. **Direct dealers sit under a Fuel Supply agreement.** MPC's filings describe "long-term supply contracts with direct dealers who operate locations mainly under the ARCO® brand" (`reference/mpc/customer-classification-evidence.md`, C2). MPC's FY2025 Form 10-K calls the brand its own ("Our Marathon and ARCO trademarks are material to the conduct of our refining and marketing operations", Item 1, Trademarks, Patents and Licenses), and a full-text search of MPC's 10-K filings on EDGAR on 2026-10-21 found no "brand license". Their brand reaches the site through a Site Brand Assignment.
2. **Four classes from the repository's MPC customer classification are to be added**, in the `customer` module's pull request (`reference/mpc/customer-classification-evidence.md`: C4 and C6 from MPC's Form 10-K, C5 from MPC's Unbranded Marketing page, and C8, which the decision owner added on 2026-09-29 for the crude oil revenue MPC reports): independent retailer (C4), unbranded customer (C5), spot market buyer (C6) and crude oil customer (C8). With the ten classes Claude read in the decision owner's model, that makes 14.
3. **The exchange or trading counterparty stays a customer class.** The decision owner's model says it becomes a customer only when a revenue-recognized relationship exists.
4. **"Authorizes brand at site" points to Site Brand Assignment,** not to Site. The model defines a site brand assignment as the link of a site to a brand under an agreement. The decision owner wrote that they did not see this relationship (block 11). Claude then showed where the image draws it. The decision owner has not answered on it since, so this item rests on their acceptance of recommendation 5 in block 14, and stays open to them.
5. **MPLX's filings count as MPC's public information.** MPC consolidates MPLX.
6. **Claude's reading of the decision owner's answers:**
   - Block 2 answers whether to accept two candidates that four peers' filings suggested: a delivery-mode facet and a brand-licensing relationship.
   - Block 8's three answers are, in their numbering: correct the misspelled labels (3), remove repeated attributes (1), and search for the meaning of six internal codes (2).
   - Block 11's third answer confirms Claude's reading of COCO, CODO and DODO (company-owned company-operated, company-owned dealer-operated, dealer-owned dealer-operated).
   - "and it is EIS" (block 14) gives the spelling of a landscape system's name.
7. **Sources for the Customer domain**, by decision 4: derived definitions go into the repository; their sources are repository information and MPC's public information, MPLX's included; peer data and the external report guide choices and do not go into the repository. Elsewhere in the repository, peer comparison stays allowed as guidance and as evidence, as before.
8. **L&S is Logistics and Storage.** MPLX's FY2023 Form 10-K, filed 2024-02-28 (accession 0001552000-24-000007), names "Logistics and Storage (“L&S”)" as one of its two segments. By FY2025 MPLX calls that segment Crude Oil and Products Logistics (MPLX FY2025 Form 10-K, accession 0001552000-26-000009; `reference/mpc/mplx-fy2025-10k-fact-sheet.md`).
9. **SDP stays a label without an expansion.** No MPC or MPLX filing contains it, by EDGAR full-text search on 2026-10-21.
10. **The two peer candidates are covered by the decision owner's own model,** so neither is added separately. In the model, a customer account carries a delivery tier, and a brand is owned by or licensed to a party through a Brand License agreement.
11. **Two roles are to be added**, in the `customer` module's pull request, by "add both roles": Position Holder and Loading-Authorized Party. The Loading-Authorized Party answers competency question 22. The Position Holder is the party whose product a terminal lifting draws on, which the model's terminal-rack class names. The model's own role list, as Claude read it, has twelve roles.
12. **The repository stays private** for the whole Customer work, by "keep it private". This narrows the standing rule of EPM-DEC-001-0050's amendment of 2026-10-19 (public while work needs it) for the Customer work. EPM-DEC-001-0040 item 3 lets internal system names into the repository, and its amendment notes that they are readable while the repository is public. Keeping it private keeps the Customer modules' internal system and field names unreadable from outside. GitHub does not enforce ruleset 25440735 on a private repository, so each Customer pull request merges through `merge-on-verdict.sh`, which waits for a MERGE verdict on the current head and for `checks` to pass.
13. **The plan, in five pull requests:**
    1. this record;
    2. the `customer` module, the conceptual model;
    3. the systems, the data flow and the attributes;
    4. the lifecycle, with a process-map proposal for the stages the map lacks;
    5. competency questions 19 to 26.
    - MPC-P06's channel dimension is applied in pull request 2.
    - The process map changes only after the decision owner approves the proposal.
    - `customer` 1.0.0 is released only with their approval.
14. **Still open from EPM-DEC-001-0004:** the lubricants and marine product-line evidence. None of the inputs covers it, so it stays open. The `customer` module's pull request is planned to settle or park it.

## Alternatives considered

- **Commit the decision owner's diagrams and table as reference files.** Not chosen: they asked for the files to stay out.
- **Put peers' filings into the repository for the Customer domain, as `customer-classification-evidence.md` did.** Not chosen: the decision owner wrote that peer data should not go into the repo, for the Customer domain.
- **Keep Agreement, Site, Site Brand Assignment and Party Transaction Association out of scope**, as Claude first recommended. Not chosen: the decision owner put every entity in scope.
- **Frame direct dealers with a Brand License agreement**, as the conceptual model's class note does. Not chosen: MPC's filings describe supply contracts with direct dealers, call the ARCO trademark MPC's own, and do not mention a brand licence (item 1).
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
- "Now here are the core system and attributes that defines a customer in each system."
- "Which we want to capture separately."
- "they are in scope"
- "scoped to product connects to product from agreement", "customer account connects to site throuhg" and "I did not see" (block 11)
- "correct. L&S is probably logistic and storage."
- "let us just call it SDP for now?"
- "nothing on the conceptual is out of scope"
- "I am okay with the rest. and it is EIS"
- "yes, keep it private, add both roles, go ahead"

The readings marked as Claude's above are under the delegation: "yes, extend the delegation to steps 5 to 12." (`delegation-steps-5-12.md`). The decision owner can reverse any item.

## Evidence

- `answers-2026-10-21-customer.md`.
- `business_architecture/reference/mpc/customer-classification-evidence.md` (C1 to C8) and `mpc-fy2025-10k-fact-sheet.md` (direct dealers).
- MPLX FY2023 Form 10-K, https://www.sec.gov/Archives/edgar/data/1552000/000155200024000007/mplx-20231231.htm, retrieved 2026-10-21; `reference/mpc/mplx-fy2025-10k-fact-sheet.md` (FY2025).
- MPC FY2025 Form 10-K, Item 1, Trademarks, Patents and Licenses, https://www.sec.gov/Archives/edgar/data/1510295/000151029526000009/mpc-20251231.htm, read 2026-10-21; EDGAR full-text search of MPC's 10-K filings for "brand license", 2026-10-21, no hits.
- EPM-DEC-001-0004, 0005, 0028, 0040, 0047, 0050, 0052.

## Consequences

- EPM-DEC-001-0004's wait is over. Competency questions 19 to 26 still wait until the `customer` module answers them.
- The regression stands at 34 answerable, 1 partial and 9 waiting.
- The repository stays private until the Customer work is done.
