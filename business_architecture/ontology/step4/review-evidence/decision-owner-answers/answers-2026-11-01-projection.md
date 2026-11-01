<!-- The decision owner's words, verbatim from the Claude Code session of 2026-11-01. Context (Claude's words, kept in this comment so they do not enter the quote corpus). Claude asked three questions about projecting the releases into Neo4j: (1) one release record per module, (2) keep all module content in Neo4j, (3) one standard store form.
Block 1: the decision owner's earlier remark on the scope.
Block 2: the decision owner's answer to the three questions.
Block 3: the decision owner's added requirement for the walkthrough.
Block 4: the decision owner's second added requirement for the walkthrough.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

This only affects projection from turttle to lpg in Neo4j. Triple stres and delta tables hold all three graphs for each module fully

1. yes 2. I will follow your recommendation 3. there should be one local store. why did we have two? Are we referring to jena and local neo4j? there should be a local Neo4j and Jena. This same approach should apply to Aura as well. basically projection from tripples to lpg should follow the approach here. I am aligned with your other recommendations. Let us add these details in the documents, guide, wlakthtough and so on of the release.

In the walkthrough, please, can you add a session on what is needed to be able to project to either Neo4j , Aura, and Databricks. This must include any required information that is needed such as URL, keys, personal token, and so on to be able to make the connection. I want my colleagues to be able to take the walk through and create the same thing we have in QA/Prod enviroment following the walkthrough without missing any information. It should be straight forward. This means the path ot the scripts used for all of this must also be provided, including the validation scripts etc.

Also the how to create technical graph from databricks as source and its projection to ontology and dusbsequent projection to Neo4J /Aura must alos have the same detailed information. There should aslo be a section that deribes the link between Databricks objects such as Metric View, its mesaure/metrics/KPI, the underlyitng tables and its lineage is linked to the ontology and how the ontology contextualize the objects in Databricks.
