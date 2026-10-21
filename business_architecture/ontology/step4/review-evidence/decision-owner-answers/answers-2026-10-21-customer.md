<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-20 to 2026-10-21 (session 7). Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 17 blocks, separated by blank lines; numbered blocks are counted as one block each.
Block 1: Claude asked which open items the decision owner was ready to give (release approvals, customer information, Q17 and the Forecaster and PSM questions, the skill rebuild plan); this is their choice, as the tool returned it.
Block 2: Claude asked whether to accept two candidates that four peers' filings suggested: a delivery-mode facet and a brand-licensing relationship.
Block 3: sent with input 1, a diagram of how customer data is ingested.
Block 4: sent while input 2, a diagram of the applications the customer passes through, was being read.
Block 5: Claude asked whether derived definitions may go into the repository, since the files stay out.
Block 6: Claude asked whether an existing file of peer data (reference/downstream-peers/customer-classification-evidence.md) should be removed under block 5's rule. Sent with input 3, a dated version of input 2's core path; the decision owner typed "domain" and "here is the next one" without a space.
Block 7: sent with input 5, a table of six core systems and their customer attributes (input 4, a lifecycle diagram, came with the words "here is another one", which are not saved here).
Block 8: answers Claude's three numbered questions about input 5: 1, whether repeated attributes are the same field; 2, the meaning of six internal codes (HOLDORDIND, Taboot, TID Nbr, ZBAID, MPA_Flag, CR_Incentive_Flag); 3, whether to correct misspelled labels.
Block 9: continues block 8.
Block 10: sent with input 6, a conceptual data model of Customer. The decision owner wrote "left pane" for the lifecycle and the other systems, and "left pane" again for the legend. In the image the legend is the left pane and the lifecycle and the other systems are the right pane, so Claude read the first "left pane" as the right pane; that reading is Claude's.
Block 11: answers Claude's three numbered questions about input 6: 1, whether the maroon zone B entities are in scope; 2, which entities three dashed relationships connect ("scoped to product", "supplied from", "authorizes brand at site"); 3, whether COCO, CODO and DODO are company-owned company-operated, company-owned dealer-operated and dealer-owned dealer-operated, and what L&S and SDP stand for.
Block 12: sent with input 7, an external research report.
Block 13: answers Claude's report that SDP appears in no MPC or MPLX filing.
Block 14: answers six recommendations Claude made after reading the report: 1, keep Agreement, Site, Site Brand Assignment and Party Transaction Association out of scope; 2, frame direct dealers with a Fuel Supply agreement, the brand reaching the site through a site brand assignment, not a Brand License; 3, add four classes from the repository's MPC customer classification (independent retailer, unbranded customer, spot market buyer, crude oil customer); 4, keep the exchange counterparty a customer class; 5, point "authorizes brand at site" to Site Brand Assignment; 6, count MPLX's filings as MPC public information. Claude had also asked about two landscape system names, including "PIS" against "EIS".
Block 15: answers three questions about the plan: keep the repository private; add Position Holder and Loading-Authorized Party roles; start.
Block 16: sets the goal for the run.
Block 17: their approval of the run's brief, as the tool returned it.
Do not edit the body; scripts/epm_facts.py quotes checks quotes against this file. -->

Customer information

decide once you've seen my data. I will share them one at a time to process

In the  image below is the customer data ingestions. Parse it very carefully and summarize what you parsed save the details you will need this for Customer domain.

all of the files and images should stay out of the repo, by the way.

yes, derived definitions can go in the repo. We will use repo information, MPC publickly published information for this. We can use Peer data to guide and resolve ambuiguity but peer data should not go into the repo at this point

Actually Peer comparison is fine to use as guidance. This rule is specifically for Customer domainhere is the next one

Now here are the core system and attributes that defines a customer in each system. And also attributes used to enrich customer in each system. These two categories of attrobutes must be captured

3. correct them
1. dedup them
2. use external MPC search and Peer to resolve these ones.

Now make sure you have all of this captured to represent both the life cycle and data flow of Customer .
I will share the conceptual data model for customer next. Which we want to capture separately.

Use the additional information on the left pane of the image for the customer lifecycle. Additional system , downstream, of the core one is also listed.
The middle part is the actual conceptual data model for customer.. The left pane is the legend

1. they are in scope
2. scoped to product connects to product from agreement, customer account connects to site throuhg "supplied from". I did not see "authorizes brand at site
3. correct. L&S is probably logistic and storage. can you confrim that and SDP through an external search when you are ready.

But this one is an report from an external research that I did you may find it useful when you start building this out

let us just call it SDP for now?

1. nothing on the conceptual is out of scope
I am okay with the rest. and it is EIS
bring me the plan

yes, keep it private, add both roles, go ahead

Goal set: keep going until you complete the Customer domain work end to end. You have my permission to run command and watch PR until merges.
I want you to use /night-run

Approve, start the run (Recommended)
