<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-23 (the ontology's close-out). Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 32 blocks, separated by blank lines.
The decision owner said they wanted to close the items waiting on them so the ontology could close. Claude asked the questions with the AskUserQuestion tool, one item at a time, each with options and a recommendation.
Block 1: "How should we settle Q17 so the ontology can close?" Options: 1 "Park until sharing (Recommended)": park Q17 by a recorded decision until the ontology is first shared with business consumers, when the business confirms meanings; 2 "Build the relation now, assign later"; 3 "Assign per module now". The decision owner typed block 1.
Blocks 2 to 4: the three MPC-P10 questions. P10.1 (onboarding): "Add a new L5 (Recommended)", CM 1.3.7.1.7 Coordinate Customer Onboarding under CM 1.3.7.1, Set Up Prospect kept as the card-program case; "Widen Set Up Prospect"; "Change nothing". P10.2 (the Order to Cash credit review's link): "CM 1.3.7.4.2 (Recommended)"; "CM 1.3.7.4.3"; "Leave unlinked". P10.3: "Add Customer Master (Recommended)", on the Marketing & Sales line, produced by CM 1.3.7.1.1; "Don't add it". Block 2 answers P10.1, block 3 P10.2, block 4 P10.3.
Block 5: "Product codes: the PIDX and OEO mappings wait for product values. How should we close this?" Options: "10-K slate in party (Recommended)": product values from the refined-product categories in MPC's FY2025 Form 10-K, each cited, mapped to PIDX product codes by identifier and to OEO fuel classes, in a party minor release; "New Product module"; "Park with the business".
Block 6: "Your answers so far need six releases. None changes a released IRI. Do you approve building and issuing them?" The six: core 2.3.0 (the new L5), value-stream 1.1.0 (the credit review's link, ranges for produces and consumes), data-product 1.1.0 (Customer Master), party 1.1.0 (the 10-K product values with their PIDX and OEO mappings, the lifecycle linked to the new process, and its projection fixes), kpi 1.1.1 (one range) and integration 1.0.1 (its projection fixes). Options: "Approve all six (Recommended)"; "Approve, but ask per tag"; "Not yet". The question undercounted two modules' projection fixes (it said 7 for party and 3 for integration; `projection/pipeline.py` lists 8 and 5); Claude told the decision owner straight after the answer, and the modules and kind of fix are as asked.
Block 7: "Which reviewer should we use for this close-out?" Options: "Keep Codex (Recommended)", with Codex giving the independent review and the Cursor bot the PR verdict; "I'll add Ollama credits".
Block 8: after Claude listed the eight pull requests, the decision owner set the session goal with block 8.
Block 9: later in the session, after the PR reviewer held that the extra fixes had no recorded yes, Claude asked: "Correction to the release approval: party 1.1.0 carries 8 projection fixes (not 7) and integration 1.0.1 carries 5 (not 3). The extra ones: party gets a cardinality shape for `feeds`, and integration gets cardinality shapes for `authority:rank` and `authority:evidenceTier`. Each adds a shape only; none changes a released IRI. Do you approve the releases with 8 and 5?" Options: "Approve 8 and 5 (Recommended)"; "Only the original 7 and 3".
Block 10: later in the session, after research showed PIDX publishes no IRIs and its codes name company-requested traded grades grouped in one-letter families dated 2015, Claude asked how party 1.1.0 should handle PIDX. Options: "Family codes, flagged (Recommended)": each product records its PIDX family letter as a plain identifier, with the PIDX workbook as its source, PIDX's copyright notice and a note that the family list dates from 2015; no IRIs; the close-out package asks the business to confirm the letters with PIDX; "No PIDX now, to the business".
Block 11: later in the session, after the independent review held integration 1.0.1 because narrowing con:reliesOn from "the property or class an answer reads" to properties (rdfs:range rdf:Property) narrows a published definition, which the playbook makes a major release, Claude asked how to close that last gap. Options: "Major: integration 2.0.0 (Recommended)": release 2.0.0 instead of 1.0.1, with the range and the narrowed definition (no class value was ever used, and nothing consumes the ontology yet), the other four fixes riding along; "Patch 1.0.1, keep this gap open": keep property or class and leave con:reliesOn on the projection's exception list.
Blocks 12 to 18: earlier in the same session, while the releases were in review, the decision owner raised the RDF-to-LPG projection guideline. Block 12 asked whether the projection documents were being updated. Claude answered that the guideline (lpg-projection/, v2.2, copied from the enterprise-people-graph repository) was not being changed and recommended a v2.3 with the lessons learned. Block 13 followed. Claude asked where the method should live, with options "Make it a skill (Recommended)": a new ontology-to-lpg skill in personal-agent-skills as the one source, the ontology skill's Step 12, the people-graph guideline and EPM's copy pointing to it; "Update the guideline only"; "Fold it into the ontology skill". Block 14 is the choice. Block 15 asked about keeping the guideline in the people-graph repository; Claude recommended moving it into the skill and asked, with options "Move it into the skill (Recommended)" and "Keep it in people-graph". Block 16 is the choice. Block 17 followed Claude's note that the skill was queued after the releases. Block 18 asked for the skill to be tested; Claude answered that the guideline moves into the skill, which holds both the preparation and the projection, and that a fresh agent would test it on the library example and on EPM's released packages.
Blocks 19 and 20: later in the session, while the ontology-to-lpg skill was being built and tested, the decision owner asked whether the skill should be built differently and whether high-quality external references could guide it (block 19). Claude asked "How should we finish the ontology-to-lpg skill?" Options: "Read from engine (Recommended)": gate on what n10s.validation.shacl.listShapes() says it compiled, keep the Python subset only as an advisory dry run, drop the carry-over of hand cases, and cite S3PG and PG-Schema as background; "Keep fixing as is"; "Read from engine, no new refs". Block 20 is the choice.
Blocks 21 to 25: the decision owner asked to install the neo4j-contrib/neo4j-skills plugin and to see which Neo4j skills help (block 21), and said the projection would later be tested on Neo4j Aura (block 22). Claude installed neo4j-skills 1.0.1 and found that n10s is not available on Aura (the neosemantics documentation, "Availability & Installation"). The decision owner then said an Aura instance was ready (block 23), that its credentials were in place (block 24) and that it is the free tier (block 25). The credentials are in a local credentials file outside the repository. Claude's read-only probe found Aura kernel 5.27-aura, no n10s procedures, the APOC import and export procedures, and an empty database.
Block 26: the decision owner on the Aura data and Apache Jena: never empty the Aura instance without telling them first, and load the ontology into Jena and explore it in both stores as a separate task after the ontology is complete.
Blocks 27 and 28: later the same day, the decision owner allowed Claude to delete the data it loads into Aura and Jena after thorough testing, said both would be loaded again with the projection skill in a separate task (block 27), and asked whether the projection skill should also load the ontology into any triple store (block 28).
Block 29: Claude recommended a triple-store add-on in the ontology-to-lpg skill and asked "Add a triple-store add-on to the ontology-to-lpg skill?" Options: "Add it now (Recommended)": load the same validated files into any SPARQL store through the W3C SPARQL 1.1 Graph Store HTTP Protocol, one named graph per package, with per-predicate counts checked against the files and the Neo4j export, tested on a local Jena Fuseki and the data deleted after; "Add it later"; "Separate skill". Block 29 is the choice.
Blocks 30 to 32: later the same day, the decision owner set out the plan for after the ontology is complete: load the whole ontology into Jena and into a Databricks triple store, project it to a local Neo4j and to Aura, then rebuild both from the Databricks store and check that no data is lost; the end goal is linking KPIs computed in Unity Catalog metric views to the business processes they support (block 30). Claude found that Databricks has no built-in triple store and compared a plain Delta triple table with OntoBricks (Databricks Labs), which holds one ontology per domain and builds instance data only from Unity Catalog tables. Claude asked "What should 'the Databricks triple store' be for the no-loss tests?" Options: "Delta table + OntoBricks later (Recommended)": a plain Delta triple table is the lossless store and the source for reloading Neo4j, and OntoBricks comes later for linking Unity Catalog data and metric views; "OntoBricks only"; "Delta table only". Block 31 is the choice. Claude asked "When should the skill get its Databricks add-on?" Options: "In the later task (Recommended)"; "Now, before merging". Block 32 is the choice.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

I agree with 1. Can we document this as a package to go with the ontology so that we know what to close out with the business.

Add a new L5 (Recommended)

CM 1.3.7.4.2 (Recommended)

Add Customer Master (Recommended)

10-K slate in party (Recommended)

Approve all six (Recommended)

Keep Codex (Recommended)

aligned. keep gooing until the ontology is done after addressing all the outstanding question. stop the goal gracefully when you are completely done

Approve 8 and 5 (Recommended)

Family codes, flagged (Recommended)

Major: integration 2.0.0 (Recommended)

By the way are updating RDF to LPG projection documents/playbook... I am not sure what we call it.

okay let us make sure we also update the guideline to project RDF/OWL/SHACL etc (basically ontology based on w3C standrad) to LPG given all of the expreinces we have had in this process of creting our ontology. It should capture all of the best practices etc. Do you think we should make a skill out of this projection guidline/playbook?

Make it a skill (Recommended)

so the skill will stay in personal skill repo. correct? We can still keep the guideline/playbook in the people graph so that we avoid copying things around. Actually do you think we should move the guideline / playbook to personal skill repo from people graph?

Move it into the skill (Recommended)

add that as part of the goal

let us make sure we test the skill to ensure it works . The guideline gives what should be done to prepare for the projection and the skill do the projection with the user. correct?

Do we need to look at how we construct the skill differently. Are there any high quality external refreces either from Neo4j or somewhere else that can further guide us? what do you think

Read from engine (Recommended)

Also let us install https://github.com/neo4j-contrib/neo4j-skills And further see where any of the skills from Neo4j may help. We can refrence any relevant one as well

When all of this is done. and we complete the ontology. We will eventual test projection to Aura. So I need of the skills that depends on Aura will work then

I have an aura instance ready to go. Let me know the logical stage to set it up. I like your approach by the way

done . Aura cred moved to that location

it is free tier by the way

keep going until all the PRs merge. When you ested it end to end. We will clean up the Aura DB but before you do that let me know. I want to explore the graph a bit before we delete what we put in there. We can always repeate the process so no harm donw. I just want to use that to explore the ontology in triple store end to end and in Aura at the same time. We can always do this part once we have completed the ontology creation goal 100%. Oh by the way can we also load all of the onttology into  https://jena.apache.org/ I will use both the triple store to go over the ontoloy we have built end to end and to explore the same in Aura. Again this task is after we have completed ontology 100% that exploration and testing will be after that and a different task.

by the way you can delete  data you load into aura DB and jena  after your thorough testing to make sure things work and the projection happens with no loss of data. 
We will load jena and aura DB back with the projection skill to test it out in a separate task after we have built the ontology 100%.

In that case do we also wants to add to the projection skill to alos be able to load the ontology into any triple store as well?

Add it now (Recommended)

Okay. Eventually I plan to load the ontology into Databricks so that I can connect data in Unity Catalog with it . This includes the KPI computed through metric view so that I can link the KPI from metric view to the end to end business process it supports through the ontology. So what this means is that I will also like to try loading the entire ontology into databrick triple store . I have a free edition of Databrick And I want to be able to load the Neo4 J database in this case both local and Aura using the data brick triplle store as the soure.
So here is the full picture:
1. create the ontology 100 %
2. test and validate loading to oad to triple store, Jena and Databrick triple store
3. Project to a local Neo4 J as planned
4. Load Aura DB as planed and test and validate that no data is lost
5. then delete the data in local Neo4j and Aura. and then try to load both Neo4 J local and Aura again but this time the source will be databrick triple store. test and validate with the original ontology to ensure no data is lost
makes sesne? lest discuss

Delta table + OntoBricks later (Recommended)

In the later task (Recommended)
