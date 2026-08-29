# Architecture artifacts

## EPM-ARCH-MEANING-vs-COMPUTE

**File:** [EPM-ARCH-MEANING-vs-COMPUTE.jpg](EPM-ARCH-MEANING-vs-COMPUTE.jpg)  
**Status:** Working visual — target band split  
**Owner:** Enterprise Performance Model Lead

The MEANING vs COMPUTE picture. Meaning does not compute. Compute prepares Silver ingredients, compiles once via `MEASURE()` on a Metric View, and publishes Gold.

The JPG footer is binding and overrides two box labels on the drawing:

| Box on the drawing | Read as |
|---|---|
| Process Architecture / “ontology files in git (Turtle)” | Process **authority** stays [`business_architecture/business_process/`](../business_architecture/business_process/) and [`business_architecture/schema/`](../business_architecture/schema/). Turtle may *link* process IRIs. Turtle is not process SoT. |
| Cataloging Tool (Purview / Unity Catalog) as the KPI row | **KPI Store** owns identity, approval, status (`proposed \| approved \| drifted \| archived` on `dim_kpi_metadata`), and the formula pointer. Purview is enterprise discovery. Unity Catalog is the technical catalog (tables, Metric Views, access). Neither is the Store door. |

The only legal join is **one ontology IRI → one KPI Store row → one Metric View**. Agents ask the graph of meaning which KPI, look up the Store row, and submit `MEASURE()` on the Metric View named by the formula pointer. They do not write formulas and they do not read Silver or Gold directly.

**Machine ontology SoT** is Turtle in git. **Enterprise expose path** is Neo4j loaded from that published Turtle. Apache Jena Fuseki is a homelab SPARQL classroom, not a client triple store. There is no enterprise SPARQL seat.

Related:

- [EPM-FOUND-000](../EPM-FOUND-000.md) — Master Index
- [EPM_Homelab/02-Tool-Selection-and-ADRs.md](../EPM_Homelab/02-Tool-Selection-and-ADRs.md) — ADR-HL-001 (lab Fuseki), ADR-HL-021 (enterprise serve), ADR-HL-022 (OntoBricks / dbxmetagen)
- [EPM_Homelab/stack_decisions.md](../EPM_Homelab/stack_decisions.md) — lab vs transfer seats
