<!-- The decision owner's words on item F, verbatim from the Claude Code sessions of 2026-10-24 and 2026-10-25. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 16 blocks, separated by blank lines.
Blocks 1 to 5 (2026-10-24, as the store-tests handoff recorded them): the decision owner added item F to the plan (block 1); said the assets go into the ontology while the shared files stay out (block 2); said a Genie agent may be used to give a KPI value, with the ontology adding context (block 3; the handoff kept only these two parts, joined by an ellipsis); said the assets touch the crack spread (block 4); and asked for market-data to grow beyond the crack spread (block 5).
Block 6 (2026-10-25): the decision owner shared one file with the lineage, metric views and Genie agent descriptions of the pricing measures, and asked Claude to map them to the ontology. The file stays outside the repository.
Block 7 (2026-10-25): Claude presented the mapping and six points needing care (classification; one measure with two sources; view names that disagree; a known data defect; series coverage; the sandbox environment). The decision owner answered points 1, 2, 3, 5 and 6; the numbers are Claude's points.
Block 8 (2026-10-25): Claude asked for the full list of crack-spread series; the decision owner proposed naming the columns that enumerate them instead.
Block 9 (2026-10-25): the decision owner asked what point 4 (the benchmark view's data defect, recorded by default as a known gap) meant; Claude explained it in the same session.
Block 10: the decision owner's instruction to write this record.
Blocks 11 to 16 (2026-10-25): Claude ran three rounds of numbered questions (Q1 to Q17) on lineage, the views and data products, then asked the remaining item F questions; the record says what each question was. Block 11 is round 1, block 12 round 2, block 13 round 3, block 14 the decision owner's confirmation, and blocks 15 and 16 the answers to the remaining questions: block 15 answers which portfolio data product the gold tables sit under, then whether a Genie agent may quote a value from its bound source; block 16 answers who is accountable for Market Data, then ownership and stewardship (Q17 of the build, parked by EPM-DEC-001-0086). In blocks 11 and 12 two local file paths, which contain an account name, are replaced by [a file path]; the files themselves stay outside the repository.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Can you add to the plan that I will provide the replica, silver, and gold tables, metric views, and the genie agents for all pricing Operational metrics/KPI. That should close out the data product piesce for that set of metrcis/kpi.

those asset needs to refrelect in the ontology as such. The system should also be refrelected. The only thing we dont add to the repo is the file that I shaerd with from which you extract those information. but the infor should go in the repo.

We actually have a genie agent today that may be used to give a KPI value ... The intention is that the genie agent should be able to add context to the KPI value using the ontology.

asset will touch the crack spread

add that to item F in the handoff

See the lineage and metric view, and genie agents description for the operational metric/KPI in the below path. There is one Metric View and agent specific to crack spread. The other metric view and agent are for the other pricing metric/kpi. You may need to map to which pricing metric / kpi they map to and let me know. You will need to think carefully to make sure we are not messing things up. By the way those are in databrick. But not this databrick that we are using for testing. they are not there in the Free Databrick. if we want to test those out we may need to create synthetic data to try it out.

1. let us keep them as market indicator. Not all of these are KPIs so our intepretation here is correct unless you think otherwise. let me know lets think through this. It is okay to leave the KPI_ID even though they may not be KPI . We will need the ID to integrate with other data (e.g governance data in Purview or unity catalog)
2. Crack view wins. Anyting related to crack spread comes from crack spread specific metric view
3. Let us use the one without "metricsfromsilver"
5. Our sereies should cover all of what I just shared. They are more comprehensive
6. correct . We have the freedom when using synthetic data in Free databrick edition to shape it as we want . as long as it ihas the same shape as the one shared

on the below question, can we just add the table columns that will give us this to show that the full series can be obtained ieven if we just list a few in market data

What is this one below. Idont get it.

go ahead with the item F decision record.

Q1. the agent can consume both. But we chose for the agent to consume the one without "silver" in the name. The one with silver is another design pattern that gives the same result. Are you missing information from the one we plan to use that I can provide to you
Q2. here is the path to the benchmark lineage and the correct name. This is actually another metric view . This one is focused on benchmark prices [a file path]
Q3. We record those layesr. But I do want to add the concepts of Foundationa Data Product and Derived Data Produt. Do a light reserch of high quality sources to help us make this classification
Q4. record both as facts. I can double check later
Q5. Leave legacy out only use the one with udm_core. that is the wone you are seeing correct?
Q6 yes mark as sandbox for now
Q7. I agree.

Q8. See the file below. does this answer your question? [a file path]
Q9: We leave out the legacy
Q10. Yes
Q11. Lineage is the evidence
On the data product. Let us add these definitions that we found in the ontology as well. We can refrence those sources with link. I like the criteria you listed as well. is there a way we can include that.

Q13. yes
Q14. yes
Q15. yes
Q16. yes
Q17. Yes we classify the new pricing products now

Yes we are both aligned.

All pricing sits under "Master Pricing" data portfolio
Yes . the agent will use the Metric view to get the value

we wont make that decision now
it will remain parked
