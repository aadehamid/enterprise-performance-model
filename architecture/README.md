# Architecture artifacts

## EPM-ARCH-MEANING-vs-COMPUTE

**File:** [EPM-ARCH-MEANING-vs-COMPUTE.jpg](EPM-ARCH-MEANING-vs-COMPUTE.jpg)  
**Status:** Working visual — target band split  
**Owner:** Enterprise Performance Model Lead

The MEANING vs COMPUTE picture. Meaning (Turtle in git) does not compute. Compute prepares ingredients, compiles once in the semantic layer, and publishes Gold. The only legal join is **one ontology IRI → one certified catalog row → one semantic-layer object**. Agents ask the graph of meaning which KPI, look up the catalog, and submit the certified measure. They do not write formulas and they do not read Silver or Gold directly.

**Machine ontology SoT** is Turtle in git. **Enterprise expose path** is Neo4j loaded from that published Turtle. Apache Jena Fuseki is a homelab SPARQL classroom, not a client triple store.

Related:

- [EPM-FOUND-000](../EPM-FOUND-000.md) — Master Index
- [EPM_Homelab/02-Tool-Selection-and-ADRs.md](../EPM_Homelab/02-Tool-Selection-and-ADRs.md) — ADR-HL-001 (lab Fuseki), ADR-HL-021 (enterprise serve), ADR-HL-022 (OntoBricks / dbxmetagen)
- [EPM_Homelab/stack_decisions.md](../EPM_Homelab/stack_decisions.md) — lab vs transfer seats
