<!-- The decision owner's words on item F, verbatim from the Claude Code sessions of 2026-10-24 and 2026-10-25. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 10 blocks, separated by blank lines.
Blocks 1 to 5 (2026-10-24, as the store-tests handoff recorded them): the decision owner added item F to the plan (block 1); said the assets go into the ontology while the shared files stay out (block 2); said a Genie agent may be used to give a KPI value, with the ontology adding context (block 3; the handoff kept only these two parts, joined by an ellipsis); said the assets touch the crack spread (block 4); and asked for market-data to grow beyond the crack spread (block 5).
Block 6 (2026-10-25): the decision owner shared one file with the lineage, metric views and Genie agent descriptions of the pricing measures, and asked Claude to map them to the ontology. The file stays outside the repository.
Block 7 (2026-10-25): Claude presented the mapping and six points needing care (classification; one measure with two sources; view names that disagree; a known data defect; series coverage; the sandbox environment). The decision owner answered points 1, 2, 3, 5 and 6; the numbers are Claude's points.
Block 8 (2026-10-25): Claude asked for the full list of crack-spread series; the decision owner proposed naming the columns that enumerate them instead.
Block 9 (2026-10-25): the decision owner asked what point 4 (the benchmark view's data defect, recorded by default as a known gap) meant; Claude explained it in the same session.
Block 10: the decision owner's instruction to write this record.
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
