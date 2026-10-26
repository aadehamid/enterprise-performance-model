<!-- The decision owner's words on item H, verbatim from the Claude Code session of 2026-10-25, as the store-tests handoff recorded them. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 4 blocks, separated by blank lines.
Block 1: Claude asked five numbered questions on the open items; question 5 was about item F's release approvals and the data being stale in the sandbox. The decision owner answered all five in one line; the words after "5." answer question 5 and ask for the synthetic-data demo.
Block 2: Claude asked about the demo's scope, the briefings and the source systems; the decision owner answered by number.
Block 3: Claude proposed source systems and asked whether the new demo must match the O2C demo; the decision owner answered.
Block 4: Claude proposed generic names for the source systems in the demo; the decision owner answered.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

1. Let us go with your recommendation. Why did you think this win? 2. I agree . But can you explain why this is the best route. 3. I will go with your recommendation 4. Should we move to he ontology skills itesef since the Playbook is a guide on how to create an ontology. what do you think? 5. Agreed It isokay if the data is stale. we are in DV in the sandbox. What about the synthetic data. Wehn we complete the ontology I want us to build a realistic synthetic data to demonstrate this in Databrick Free edition

1. yes 2. yes 3. Remove any mention of ChatGPT> . and It is okay to save this in EMP repo as another demo of the work. Just like we have OTC. We will need to also revisit that OTC demo to make sure they are all one demo. But we can do that at a later point. We should simulate source systes as postgres. Use duckdb as needed. Let know what you think of the choice of the sources systems from which we will replicate data and to replica > model with star schema (facts and dimenstions) like we did here > gold > metric view

the new demo does not have to mathc it. I did not have this much detail when I built the OTC So I will have to revist it later. We should use the best robust and realistic approach. Let us use real data where they are available in the public

they work
