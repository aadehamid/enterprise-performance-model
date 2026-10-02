# EPM-ARCH-PPC-002 — Shared Execution Technology and Homelab Promotion Model

**Status:** Proposed  
**Purpose:** Clarify which PPC-selected technologies can strengthen EPM execution and how to treat technologies already proven in EPM Homelab.

## 1. Key finding
PPC did not independently invent many EPM execution tools. EPM Homelab already contains Dagster, DuckDB, Neo4j, Fuseki, Ollama, LangGraph, OpenLineage, synthetic O2C data/apps and agent evidence paths.

The correct action is not to copy PPC technology into EPM. It is to decide which homelab patterns deserve promotion into a governed EPM reference implementation.

## 2. Strong alignment
| Technology/pattern | EPM role |
|---|---|
| AML + Azimutt | proposed model-as-code/visual data-model companion; must not replace semantic/process authority |
| Jena/Fuseki | lab/validation/SPARQL runtime; Turtle in Git remains machine ontology SoT |
| Neo4j Community | graph-of-meaning serving/traversal from published Turtle |
| Dagster | orchestration of validation, publication, synchronization and reference data-product/KPI builds |
| DuckDB | lightweight reference compute, reconciliation and demo analytics |
| DuckLake | optional open reference for Silver/Gold/KPI Store history; evaluate before adoption |
| OpenMetadata | open catalog/governance reference implementation analogous to selected Purview responsibilities |
| Great Expectations | data/DQ contract execution where rules concern records/tables |
| SHACL | semantic constraint validation where rules concern RDF meaning |
| OpenLineage | pipeline/job/dataset lineage event standard |
| MLflow | optional analytical-model lifecycle when EPM demos require models |
| LangGraph/Ollama | homelab/consumer demonstrations; not semantic authority |
| Grafana | optional technical observability for reference environment |

## 3. Tools that remain implementation-specific
PPC's Twenty, ERPNext, Debezium, Kafka, D1, Dash, forecasting/causal/optimization stack should not enter governed EPM merely because PPC uses them.

EPM may use small application demos, but EPM's purpose is architecture/semantic authority, not a full fictional operating company.

## 4. Model-as-code
AML/Azimutt can close a gap between EPM semantic/business models and conceptual/logical data models. AML entities should map to EPM semantic IDs. AML must not become ontology SoT or process SoT.

## 5. OpenMetadata reference
EPM can use OpenMetadata in Homelab/reference implementation to demonstrate glossary/domain/data-product/lineage/quality synchronization. Enterprise mappings to Purview/Unity Catalog remain architecture concerns and should not be replaced by the homelab tool.

## 6. Quality split
Use SHACL for semantic graph constraints and Great Expectations for structured data-quality checks. OpenMetadata can contextualize results. OpenLineage captures execution lineage.

## 7. Promotion rule
A Homelab technology/pattern is promoted only when:
1. it implements an EPM architectural responsibility;
2. it does not become a competing semantic authority;
3. the responsibility is documented independent of the tool;
4. a second implementation could replace the tool without changing EPM meaning;
5. the promotion is recorded by ADR.

## 8. PPC feedback
PPC can test promoted patterns at larger integration scale. Failures should create EPM issues/ADRs, not silent PPC forks.
