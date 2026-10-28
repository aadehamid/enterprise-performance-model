<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-28. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 7 blocks.
Block 1: after the close-out walk-through, Claude listed what else needed the decision owner (points 1 and 2, the grill on connecting Databricks to the ontology, exe.dev hosting, the EIA key) and recommended answering the questions while present, then running the rest alone as one goal. The option read: "We do (a) to (c) now, the Databricks grill included. Then I ship all of it alone as one goal." The decision owner chose it.
Block 2: grill round 1. Claude asked four questions with recommendations: Q1, what the integration is for (Genie answers with the ontology's definition, and stewards see metric views tagged with their measure); Q2, which store the agents read (epm_triples in Databricks; AuraDB and Neo4j outside); Q3, which measures get a KPI ID (all 41, KPI-0002 onward); Q4, where the code lives (the demo). Claude also reported that only Crack Spreads had an ID, KPI-0001. The decision owner typed this reply.
Block 3: grill round 2. Claude reported that Crack Spreads is classed as a market indicator and asked: Q5, which classes get KPI and OPM IDs (KPI for the two measures classed kpi from KPI-0002, Crack Spreads keeping KPI-0001; OPM for operational metrics, market indicators, plan-variance diagnostics, the decision-support indicator and alerts; none for trackers, reports and non-measures); Q6, the four-digit padding (kept: text sort, one pattern, the existing KPI-0001); Q7, metric views grouped by fact grain, each measure carrying its ID; Q8, a new pricing metric view; Q9, one Genie agent per subject area; Q10, designed lineage from the ontology, observed lineage from Unity Catalog, Neo4j for systems outside Databricks, with a comparison test. The decision owner typed this reply.
Block 4: grill round 3. Claude reported that the refinery operations view already holds utilization, yields, margin, margin capture and opex; that Databricks has an Agent Bricks Supervisor Agent (GA); and that Free Edition restricts outbound internet access to trusted domains. It asked: Q11, the margin measures stay in the refinery operations view and the new pricing view holds six market-price measures; Q12, one supervisor over three Genie agents, with the multi-agent app pattern as fallback; Q13, a technical graph of about 100 nodes describing the demo pipeline under a Tech label; Q14, a sync of that graph to Delta tables, plus one attempt at a live call to AuraDB; Q15, the same Neo4j database with the Tech label. The decision owner typed this reply.
Block 5: grill round 4. Claude reported that composite databases are an Enterprise Edition feature, not available on Aura, and asked Q16 (switch the local Neo4j to the Enterprise image under the evaluation licence) and Q17 (Aura login details from a local file into a Databricks secret scope). The decision owner answered Q16 with this line, and answered Q17 by naming the local folder that holds the Aura login (the folder path is left out here because it holds a personal account name).
Block 6: Claude asked the decision owner to approve the written brief for the unsupervised run. The option read: "I start now and work through the order alone, logging to night-log-2026-10-28.md." The decision owner chose it.
Block 7: Claude reported the demo's record counts, that utilization comes from refinery daily production and planned utilization from monthly plan targets over 142 days, and recommended extending operations to three years with process units and the price history to three years from EIA, asking whether to use the current EIA key. The decision owner typed the first line. Later the same session the decision owner sent the second line.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Q&A now, then one goal (Recommended)

KPI ID: Give all measure classify as  KPIs an ID like we did for crakc spread but make it incremental. The other measures tagged as Operational metrcis/KPI shoud also have ID that start with "OPM-0001" and make it incremental as KPI. for expample, "OPM-0001", "OPM-0002", "OPM-0003" and so on. Make KPI incremental like this as well . Also can we discuss the bennefit of the triple 0s in the KPI "KPI-0001". what is the benefit of it? do we realy need it. .
We should discuss our strategy on how we organize the mteric view. do we have one metric vie for one measure or logically group them. I do want you to also create a Metric view for all of the pricing operational metrics/KPI. Alos the genie agents.. should we have one agent for one operational/metrics. or an agents that can adress questions on metrics or KPI that are logically together. By the way OPM = Operationam Metrics. This is to distinguisg Operation KPI from the tru KPI i the KPI Store.
Q1. correct
Q2. The pattern is the sourse of truth is the ontology serialized in turtle. This is then projected to consuming application. In this case Neo4J, AuraDB, and databricsk and those must be kept in sync with the source, which we plan to save in git. So since the ontology will be in a delta table, it may be best for the genie agent to read the ontology from that table. Thisontology we have been building can be considered business ontology. There is a graph in neo4j that will have data lineage and other finromation that we can consider techical. We have that today even though we have not simulate it today. And since we are moving the dataplatform to Databrick , data brick will aslo have lineage. The question we need to discuss is apart from the agent consuming the business ontology. how should it handle the lineage in these two places?
Q3 answerd at the beginnin of my response.
Q4. agreed

Yes to all with some coments below

Q8: do we have data for the opretaional metrcis such as utilization as well?
Q9: I like the concept of the supervisor agent. Is this a concept in Databricks? Can you check? If it is let us implement even if we have two agents today.
Q10: Can we add a small techical graph in Neo4j not captured as part of the ontology to demo how genie or Databrick can leverage the graph in neo4j to add additional context. Let us discuss what this should be.

By the way when we complete the grilling we should created an updated data flow in https://app.eraser.io/folder/w07vEqNDXhSrfxz2GdiK as a new file

yes to all with comments below:

Q14: I do want to test the connection to auraDB. This will give me an idea on how this will work with Neo4j enterprise as well.
Q15: Can we use composite database?

Q16: I do not have Enteprise Neo4j on this machine. So we will have to go with what we have.

Approve, start (Recommended)

extedn it and use the current EIA key

also create data description document for this synthetic dataset, including the grains and how they were geretaed with links to scripts/notebook used to generate them
