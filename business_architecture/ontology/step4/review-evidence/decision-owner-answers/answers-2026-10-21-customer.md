<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-20 to 2026-10-21 (session 7). Context (Claude's words, kept in this comment so they do not enter the quote corpus): Claude asked which open items the decision owner was ready to give; block 1 is their choice, as the tool returned it. They then sent their customer information one input at a time: three data-flow diagrams, a lifecycle diagram, a table of each core system's Create and Enrich attributes, a conceptual data model of Customer, and an external research report. None of those inputs is in this repository, by block 4. Blocks 2 to 14 are the words they sent with the inputs and their answers to Claude's questions, in order. Block 8 answers three numbered questions about the attribute table (3: misspelled labels; 1: repeated attributes; 2: six internal codes). Block 10 answers three numbered questions about the conceptual model (1: the zone B entities; 2: three dashed relationships; 3: the abbreviations COCO, CODO and DODO, L&S and SDP). Block 13 answers six recommendations about the research report, numbered 1 to 6; item 1 was to keep Agreement, Site, Site Brand Assignment and Party Transaction Association out of scope. Block 14 answers three questions about the plan: keep the repository private, add the Position Holder and Loading-Authorized Party roles, and start. Block 15 sets the goal for the run. Block 16 is their approval of the run's brief, as the tool returned it. Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

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
