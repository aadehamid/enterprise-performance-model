# EPM-ARCH-REF-001 — Governed EPM Reference Implementation

**Artifact ID:** EPM-ARCH-REF-001
**Version:** 0.1 Draft
**Status:** Draft (Candidate). Not Approved Baseline.
**Owner:** Enterprise Performance Model Lead
**Last updated:** 2026-10-02
**Derived from:** [EPM-ARCH-PPC-002](EPM-ARCH-PPC-002_Shared_Execution_Technology_and_Homelab_Promotion_Model.md) (Candidate) and ADR-HL-023 in [EPM_Homelab/02-Tool-Selection-and-ADRs.md](../EPM_Homelab/02-Tool-Selection-and-ADRs.md)

**Purpose:** Record which EPM Homelab patterns are candidates for promotion into a governed reference implementation and which remain educational experiments. Responsibilities come first. Tools are replaceable.

## 1. Promotion rule

A Homelab pattern is promoted only when all five hold:

1. It implements an EPM architectural responsibility.
2. It does not become a competing semantic authority.
3. The responsibility is documented independent of the tool.
4. A second implementation could replace the tool without changing EPM meaning.
5. The promotion is recorded by ADR.

This document promotes nothing. It classifies patterns so that each promotion is a separate, traceable decision.

## 2. Tiers

- **Educational runtime.** Learning aid, may take practical shortcuts, not governed.
- **Governed reference-implementation candidate.** Implements an EPM responsibility and may be promoted under the rule above.
- **Promoted.** Candidate with its own promotion ADR. None yet.

PPC integrated proving-ground implementations are outside this repository. PPC failures against a promoted pattern become EPM issues or ADRs.

## 3. Responsibilities and patterns

| EPM responsibility | Homelab pattern | ADR | Tier today |
|---|---|---|---|
| Meaning store: Turtle in git, no client triple store | Turtle in git, Protégé authoring | ADR-HL-004, ADR-HL-021 | Candidate |
| Graph of meaning serving | Neo4j with n10s loaded from published Turtle | ADR-HL-006, ADR-HL-021 | Candidate |
| Semantic constraint validation | pySHACL | ADR-HL-003 | Candidate |
| Ontology consistency gate | Owlready2 / HermiT | ADR-HL-019 | Candidate |
| Orchestration of validation, publication, and builds | Dagster | ADR-HL-009 | Candidate |
| Lightweight reference compute and reconciliation | DuckDB | ADR-HL-010 | Candidate |
| Execution lineage | OpenLineage and Marquez | ADR-HL-012 | Candidate |
| Open catalog and governance reference | OpenMetadata | ADR-HL-024 | Candidate (lab stand-in for Purview; see metadata specification section 5.4) |
| Structured data-quality contract execution | Great Expectations | ADR-HL-025 | Candidate |
| Model-as-code and visual data-model companion | AML with Azimutt | ADR-HL-026 | Candidate, must not replace semantic or process authority |
| Open table format for Silver, Gold, and KPI Store history | DuckLake | ADR-HL-027 | Educational until evaluated |
| Analytical-model lifecycle, only when demos need models | MLflow | ADR-HL-028 | Educational |
| Technical observability of the reference environment | Grafana | ADR-HL-029 | Educational |
| SPARQL classroom | Jena Fuseki | ADR-HL-001 | Educational (no enterprise seat) |
| Agent demonstrations | LangGraph, Ollama, MCP server | ADR-HL-007, ADR-HL-008, ADR-HL-018 | Educational (not semantic authority) |
| Synthetic O2C applications | ERPNext, CRM, Buzz, Semantica | ADR-HL-014 to ADR-HL-017 | Educational |

PPC-specific tools (Twenty, ERPNext as used by PPC, Debezium, Kafka, D1, Dash, and the forecasting, causal, and optimization stack) are not governed EPM patterns.

## 4. Invariants every candidate must preserve

- Process authority stays `business_architecture/business_process/` and `business_architecture/schema/`.
- Machine ontology SoT stays Turtle in git.
- The KPI Store row owns identity, approval, status, and the formula pointer.
- Compute runs `MEASURE()` on the Metric View the Store pointer names.
- Purview, Unity Catalog, and Bigeye remain the enterprise seats. A reference tool demonstrates a responsibility. It does not replace them.

## 5. Open items

- Each Candidate needs its own promotion ADR before it is Promoted.
- DuckLake needs evaluation against the Silver, Gold, and KPI Store history requirement before it leaves the educational tier.
- An EPM Decision Log (EPM-DEC-001) does not exist yet. Until it does, promotion ADRs live in the Homelab ADR file and must be mirrored when EPM-DEC-001 is created.
