# EPM Artifact and Chat Map
**Artifact:** EPM-PROJ-004_Artifact_and_Chat_Map  
**Version:** 1.0 Draft  
**Status:** Working Baseline  
**Updated:** August 4, 2026  

*A practical map from questions to the right artifact and working chat*

## Question-to-artifact map
| Question | Canonical artifact |
|---|---|
| What is the EPM and how is the repository organized? | EPM-FOUND-000 |
| What principles govern all design decisions? | EPM-FOUND-000A |
| What are domains, value streams, capabilities, processes, activities, and decisions? | EPM-FOUND-001 |
| How do objectives, KPIs, data products, and consumption connect? | EPM-FOUND-002 |
| What do concepts and relationships mean? | EPM-FOUND-003 |
| How will the meaning be formalized for machines? | EPM-FOUND-004 |
| How do we classify measurements, metrics, and KPIs? | EPM-FOUND-005 |
| What are foundational and derived products and how do they align with medallion? | EPM-FOUND-006 |
| How should the project operate? | EPM-PROJ-002 |
| How do we establish the project? | EPM-PROJ-003 |

## Question-to-chat map
| Work question | Recommended chat |
|---|---|
| Is this Tableau calculation a KPI? | Measurement Classification |
| How should the tall KPI fact work? | KPI Store Design |
| What value stream does this report support? | Commercial Business Architecture |
| Why did Netback change? | Commercial Performance Model |
| Where should this calculation live? | Semantic and Consumption Layer or Data Product Portfolio |
| Should this be Silver or Gold? | Data Product Portfolio |
| How should a concept be represented in OWL? | Ontology Design |
| What should Power BI calculate? | Power BI Standards |
| How should Purview, YAML, SQL, and graph metadata integrate? | System Integration |
| What goes to the steering committee? | Executive Readouts |

## Artifact dependency map
```text
EPM-FOUND-000A Architectural Principles
            ↓ governs
EPM-FOUND-001 Business Architecture
EPM-FOUND-002 Performance and Data Architecture
EPM-FOUND-003 Semantic Model
            ↓ formalized by
EPM-FOUND-004 Ontology Design
            ↓ specialized by
EPM-FOUND-005 Measurement and KPI Model
EPM-FOUND-006 Data Product and Consumption Model
            ↓ operationalized through
KPI Store Technical Design
Tableau Classification Method
Domain Models
Data Product Specifications
Semantic Views
Power BI Semantic Models
Ontology and Knowledge Graph
```
