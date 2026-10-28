<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-27. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 4 blocks.
Block 1: during the session, the decision owner set a final step for the stores: once every change had merged, remove the ontology data from local Neo4j, AuraDB and Databricks, confirm the stores are empty, then load the latest version back.
Block 2: the decision owner asked Claude to confirm with them before reloading, after the purge.
Block 3: Claude asked whether it may purge the ontology data from four stores: the local Neo4j pipeline (epm-lpg, Bolt 17687), the local Neo4j driver (lpg-local-neo4j-1, Bolt 17711), AuraDB, and the Databricks table epm_triples; the pricing demo's Postgres and its idp_sbx catalog not touched. The decision owner chose this option.
Block 4: after the purge, Claude asked whether to reload now or wait until the business close-out points are worked through and reload once at the start of Part 2. The option read: "Stores stay empty; the runbook says so, dated; the handoff makes the reload the first step of Part 2, after the close-out answers ship, with the counts and hash checks." The decision owner chose this option.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Once we are done with everything, we will remove all of the ontology data projected to  local neo4j, Aura DB, and Databricks. 
We will confirm that we are starting afresh. Then we will load the very latest and potentially final version of the ontology back to al of them

When we are done with all of this and have removed the data before reloading. Please confirm before we reload.

Yes, purge those four (Recommended)

Wait, reload at Part 2 (Recommended)
