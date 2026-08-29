# Architecture artifacts

## EPM-ARCH-MEANING-vs-COMPUTE

**Source:** [EPM-ARCH-MEANING-vs-COMPUTE.svg](EPM-ARCH-MEANING-vs-COMPUTE.svg)  
**Raster:** [EPM-ARCH-MEANING-vs-COMPUTE.jpg](EPM-ARCH-MEANING-vs-COMPUTE.jpg)  
**Status:** Working visual — target band split  
**Owner:** Enterprise Performance Model Lead

The picture **is** the authority for the boxes. Edit the SVG and re-export the JPG. Do not add a footer that contradicts the drawing.

| Box | Seat |
|---|---|
| Process Architecture | `business_architecture/business_process/` and `business_architecture/schema/`. Turtle may link process IDs. Not process SoT. |
| Ontology modules / Named KPI | Turtle in git. Machine ontology SoT. |
| Graph of meaning | Neo4j / Cypher loaded from published Turtle. No client triple store. Fuseki = lab SPARQL only. |
| KPI Store | `dim_kpi_metadata`: identity, approval, formula pointer, IRI. Status `proposed \| approved \| drifted \| archived`. |
| Purview / Unity Catalog / Bigeye | Discovery, technical catalog, quality. **Not** the Store door. |
| Compiler | `MEASURE()` on the Metric View named by the Store pointer. |

Join: **one ontology IRI → one KPI Store row → one Metric View**. Agents ask the graph which KPI, look up the Store row, submit `MEASURE()`. They do not write formulas and they do not read Silver or Gold.

Related:

- [EPM-FOUND-000](../EPM-FOUND-000.md)
- [EPM_Homelab/02-Tool-Selection-and-ADRs.md](../EPM_Homelab/02-Tool-Selection-and-ADRs.md) — ADR-HL-001, ADR-HL-021, ADR-HL-022
- [EPM_Homelab/stack_decisions.md](../EPM_Homelab/stack_decisions.md)
