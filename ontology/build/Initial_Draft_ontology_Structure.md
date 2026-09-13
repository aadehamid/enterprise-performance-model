# Enterprise URI Strategy & Semantic Architecture Specification
## Business Architecture, ER/Studio (CDM/LDM/PDM), Purview, Unity Catalog, & KPI Store

---

## 1. Architectural Namespace Design & Strategy

### 1.1 Why Domain-Specific Namespaces?
In an enterprise semantic fabric, separate namespaces are maintained for each architectural layer and source authority. This prevents naming collisions and isolates lifecycles across systems:
* **Decoupled Lifecycles:** If a physical table in Databricks Unity Catalog or Microsoft Purview is refactored, renamed, or migrated, the upstream logical entity (`ldm:`) and the operational business process (`biz:`) remain unchanged.
* **Autonomous Governance & Ownership:** Each namespace maps directly to an authoritative organizational owner (e.g., Enterprise Architecture owns `biz:`, Data Governance owns `ldm:`, Platform Engineering owns `unity:`).
* **Distinct Entity Identity:** Prevents collisions when the same conceptual entity exists across layers (e.g., `cdm:SalesOrder` vs. `ldm:SalesOrder` vs. `unity:.../dim_sales_order`).

### 1.2 Hash (`#`) vs. Slash (`/`) URI Conventions
* **Hash URIs (`#`):** Used for ontologies, schemas (TBox), and relatively static vocabularies (`core#`, `kpi-ont#`). The client downloads the document and resolves the fragment identifier locally.
* **Slash URIs (`/`):** Used for large, dynamic enterprise instance data (ABox) like catalog tables, models, and metric definitions (`models/logical/`, `catalog/unity/`). This allows individual resources to be dereferenced independently via HTTP without downloading the entire estate metadata.

---

## 2. Enterprise Namespace Registry

| Layer / Role | Prefix | Base URI | Syntax Type | Local Identifier (Fragment/Path) | Authority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Core Ontology** | `core:` | `https://meta.company.internal/ontology/core#` | Hash (`#`) | Predicates & Classes (`LogicalEntity`, `mapsToPhysical`) | Enterprise Data Governance Guild |
| **KPI Ontology** | `kpi-ont:` | `https://meta.company.internal/ontology/kpi#` | Hash (`#`) | Metric Classes (`Metric`, `aggregationMethod`) | BI & Analytics CoE |
| **Business Architecture** | `biz:` | `https://meta.company.internal/business/processes/` | Slash (`/`) | Process ID / Name (`OrderFulfillment`, `Invoicing`) | Enterprise Architecture Office |
| **Conceptual Model (ER/Studio)** | `cdm:` | `https://meta.company.internal/models/conceptual/` | Slash (`/`) | Business Concept (`SalesOrder`, `Customer`) | Lead Data Architects |
| **Logical Model (ER/Studio)** | `ldm:` | `https://meta.company.internal/models/logical/` | Slash (`/`) | Model / Entity (`SalesOrder`, `SalesOrderHeader`) | Data Modeling Guild |
| **Physical Model (ER/Studio)** | `pdm:` | `https://meta.company.internal/models/physical/` | Slash (`/`) | DBMS Design (`Databricks_DimSalesOrder`) | Data Modeling / DBAs |
| **Databricks Unity Catalog** | `unity:` | `https://meta.company.internal/catalog/unity/` | Slash (`/`) | 3-Level Namespace (`catalog/schema/table`) | Lakehouse Platform Team |
| **Microsoft Purview Catalog** | `purview:` | `https://meta.company.internal/catalog/purview/` | Slash (`/`) | Qualified Asset Path (`server/database/table`) | Enterprise Cloud Governance |
| **KPI / Metric Store** | `kpi:` | `https://meta.company.internal/metrics/` | Slash (`/`) | Metric Identifier (`OrderFulfillmentCycleTime`) | Financial & Business Analytics |

---

## 3. End-to-End Semantic Metamodel & Lineage Matrix