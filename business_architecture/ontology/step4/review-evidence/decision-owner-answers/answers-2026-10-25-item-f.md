<!-- The decision owner's words on item F, verbatim from the Claude Code sessions of 2026-10-24 and 2026-10-25. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 16 blocks, separated by blank lines.
Blocks 1 to 5 (2026-10-24, as the store-tests handoff recorded them): the decision owner added item F to the plan (block 1); said the assets go into the ontology while the shared files stay out (block 2); said a Genie agent may be used to give a KPI value, with the ontology adding context (block 3; the handoff kept only these two parts, joined by an ellipsis); said the assets touch the crack spread (block 4); and asked for market-data to grow beyond the crack spread (block 5).
Block 6 (2026-10-25): the decision owner shared one file with the lineage, metric views and Genie agent descriptions of the pricing measures, and asked Claude to map them to the ontology. The file stays outside the repository.
Block 7 (2026-10-25): Claude presented the mapping of each agent group to a kpi measure (the table in EPM-DEC-001-0097, item 4) as its finding, not as a question ("Each agent and each of its price groups maps to one of the ontology's existing pricing measures."), then listed six numbered points and asked the first as a question; the decision owner answered 1, 2, 3, 5 and 6 by number. The questions, as asked:
1. Classification: do these stay market indicators, or become KPIs? Recommendation: keep them market indicators, and record the KPI-0001 as an identifier on Crack Spreads Pricing.
2. One measure, two sources: both agents answer crack spreads; which source wins, or does each get a scope?
3. Names that don't agree: the crack view is called ..._metricsfromsilver_vw in the agent section and ..._metrics_vw in the lineage section; the benchmark view is written both mips_mpr_... and mpr_mips_....
4. The benchmark view stores Brent, WTI and Natural Gas x100 (record as a known gap).
5. Series coverage: market-data holds 13 crack series against 127+, and none of the other markers.
6. Environment: everything is in idp_sbx (sandbox); testing in Free Edition needs synthetic data shaped like the assets.
Block 8 (2026-10-25): Claude asked "can you share the full list of crack-spread series?"; the decision owner proposed naming the columns that enumerate them instead, and Claude withdrew the question.
Block 9 (2026-10-25): the decision owner asked what question 4 (the benchmark view's data defect, recorded by default as a known gap) meant; Claude explained it in the same session.
Block 10: the decision owner's instruction to write this record.
Blocks 11 to 13 (2026-10-25): three rounds of numbered questions, each with a recommendation; "yes" accepts the recommendation. The questions, as asked:
Round 1 (block 11):
Q1 Which crack view the ontology binds: (a) bind ..._metrics_vw and record the agent's use of ..._metricsfromsilver_vw as open; (b) bind ..._metricsfromsilver_vw; (c) both. Recommended (a).
Q2 Record the benchmark view under the agent's Data sources spelling (mips_mpr_benchmark_prices_fact_vw), lineage "not traced", tracing as a follow-up? Recommended yes.
Q3 Record exactly the five layers (replica, silver, gold, metric view, Genie agent) as data-product distributions linked by "derived from", with the owner's names? Recommended yes.
Q4 Record table lineage as fact, and joins/derivations marked as inferred pending engineering confirmation? Recommended yes.
Q5 Leave the legacy Synapse reads out of the lineage and list them as an open question? Recommended yes.
Q6 Record the sandbox names, each marked sandbox, and replace them with production names later? Recommended yes.
Q7 Table-level lineage for every hop, column level only for the value columns? Recommended yes.
Round 2 (block 12; the paragraph beginning "On the data product" answers Q12):
Q8 What the crack view exposes: ..._metrics_vw lacks KPI_ID, Crack_Spread_Sum, Effective_End_Datetime; can the owner share its definition; until then record KPI_ID on the gold table and flag Crack_Spread_Sum? Recommended yes.
Q9 Which silver tables count: keep idp_sbx.silver_udm_core.* and idp_sbx.silver_mdm_core.*, leave out synapse_dev.udm_core.*, mdm_core.*, commercial_core.*? Recommended yes.
Q10 Record the benchmark view's 160-day window as a known gap? Recommended yes.
Q11 Link each view to the systems its lineage reaches, whatever its name says? Recommended yes.
Q12 Add a code list of data-product kinds (Foundational, Derived) with the stated definitions and the layer mapping, and check the criteria as shapes? Recommended yes; classify only the new pricing products now.
Round 3 (block 13):
Q13 Record KPI-0001 as the identifier on Crack Spreads Pricing, the gold column's value beside it, and note that the column labels all 127 series alike? Recommended yes.
Q14 Record the agent's need for Crack_Spread_Sum (absent from ..._metrics_vw) as an open item for the owner's team, and bind the view as it is? Recommended yes.
Q15 Model the data-product definitions and criteria as: a Data Product Kind code list with definitions and scope notes listing the criteria; the sources in the authority module with tiers; a classification test and reason per product (kpi's pattern); SHACL shapes for the checkable criteria? Recommended yes.
Q16 Give these sources the lowest tier (generic frameworks), noting no MPC, peer or downstream source defines the term? Recommended yes.
Q17 Classify only the new pricing products now (silver facts and dimensions, the two gold tables, the three metric views)? Recommended yes.
Block 14 answers Claude's closing question, "Have we reached a shared understanding?", asked under a table of 14 decisions: 1 bind ..._metrics_vw, the agent can consume either view; 2 the benchmark view is mips_mpr_benchmark_prices_fact_vw, read from silver; 3 record the layers replica, silver (UDM facts, MDM dimensions), gold, metric view, Genie agent, linked by "derived from"; 4 record both the joins and the derivations as facts; 5 keep idp_sbx silver, leave out the legacy synapse_dev tables; 6 sandbox names, marked as sandbox; 7 table-level lineage for every hop, column-level only for the value columns; 8 KPI-0001 as the identifier, the gold constant beside it, labelling all 127 series alike; 9 an open item for the owner's team on Crack_Spread_Sum; 10 known gaps on the benchmark view (the x100 defect, the 160-day window); 11 each view linked to the systems its lineage reaches; 12 a Data Product Kind code list, Foundational and Derived, with definitions, criteria and sources at the lowest tier, silver foundational, gold and metric views derived, replicas and agents not data products; 13 a classification test and reason on each product, plus shapes; 14 classify only the new pricing products now. The mapping of block 7 was not in that table.
Blocks 15 and 16 answer the four remaining item F questions, as asked: "which portfolio data product the gold tables sit under (for example External Market Data)" and "the Genie consumer rule: may an agent quote a value from its bound source" (block 15); "who is accountable for Market Data" and "ownership and stewardship (Q17, parked)", Q17 of the build, parked by EPM-DEC-001-0086 (block 16).
In blocks 11 and 12 two local file paths, which contain an account name, are replaced by [a file path]; the files themselves stay outside the repository.
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
