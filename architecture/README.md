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

### Example consumer: PPC

Meaning-vs-Compute is unchanged. PPC is the first integrated proving-ground consumer of EPM. It is an example consumer, not an authority. It must preserve the join:

`ontology IRI → KPI Store row → Metric View → MEASURE()`

A consumer may use a different runtime, but it may not introduce a second meaning store, author formulas in the graph, or infer approval from file presence. See the proposed consumer artifacts below.

## EPM-ARCH-PPC proposed artifacts

**Status:** Proposed (maps to Candidate in EPM-FOUND-000). Not Approved Baseline.

| File | Subject |
|---|---|
| [EPM-ARCH-PPC-001](EPM-ARCH-PPC-001_Publishable_EPM_Consumer_Contract.md) | Publishable EPM consumer contract: versioned release bundle, authority metadata, extension process |
| [EPM-ARCH-PPC-002](EPM-ARCH-PPC-002_Shared_Execution_Technology_and_Homelab_Promotion_Model.md) | Shared execution technology and the Homelab promotion rule |
| [EPM-ARCH-PPC-003](EPM-ARCH-PPC-003_Process_Conformance_and_Executable_Semantics_Extension.md) | Process conformance and executable semantics |
| [EPM-PPC-UPDATE-PLAN_Existing_Artifacts](../ARCHIVE/EPM-PPC-UPDATE-PLAN_Existing_Artifacts.md) | Archived working change plan for existing EPM artifacts (provenance, not canonical) |
| [EPM-ARCH-REL-001](EPM-ARCH-REL-001_EPM_Consumer_Release_Contract.md) | EPM consumer release contract (Draft, Candidate). Derived from PPC-001 |
| [EPM-ARCH-REF-001](EPM-ARCH-REF-001_Governed_EPM_Reference_Implementation.md) | Governed EPM reference implementation (Draft, Candidate). Derived from PPC-002 |

Related:

- [EPM-FOUND-000](../EPM-FOUND-000.md)
- [EPM_Homelab/02-Tool-Selection-and-ADRs.md](../EPM_Homelab/02-Tool-Selection-and-ADRs.md) — ADR-HL-001, ADR-HL-021, ADR-HL-022
- [EPM_Homelab/stack_decisions.md](../EPM_Homelab/stack_decisions.md)
