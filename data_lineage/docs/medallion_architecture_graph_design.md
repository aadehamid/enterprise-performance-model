# Data Lineage Knowledge Graph — Medallion Architecture Design Document

**Version:** 1.3  
**Date:** March 28, 2026  
**Status:** Approved for implementation  
**Changelog:**  
- v1.3 — Server canonicalization centralized in `neo4j_loader.py` (Phase 7). Duplicate Server nodes merged, test→prod collapse. Location IDP master data loaded (Phase 6a, `load_location_idp.py`). Manual DERIVED_FROM corrections framework added to `load_lineage.py`.  
- v1.2 — Column nodes now implemented (Phase 5). MasterDataDomain load complete (Phase 6). Added Column node model, Server node, HAS_COLUMN/MIGRATED_TO relationships, canonicalization approach. Updated implementation plan and graph counts.  
- v1.1 — Added findings from Phase 3 Reports Full Data Mapping analysis (flat files, Live reports, legacy semantic schema, CDD name mapping, multi-value lineage handling)  

**Scope:** Extending the existing Data Lineage Knowledge Graph to model IDP's Medallion Architecture, including schemas, tables, columns, views, reports, and master data concepts.

---

## 1. Background

### 1.1 Current Graph State

The Knowledge Graph currently models the following node types and relationships:

| Node Label | Count | Key Properties |
|------------|-------|----------------|
| `DataSystem` | 407 | `name`, `isSoxRelevant`, `confidentialityClassification`, `applicationService`, etc. |
| `BusinessArea` | 13 | `name`, `description` |
| `ValueStreamStage` | 3 | `name`, `sequenceOrder`, `description` |
| `DataProductLine` | 4 | `name` |
| `CapabilityDataDomain` | 30 | `name`, `description` |
| `BusinessProcess` | ~12 | `name`, `description` |
| `Policy` | 2 | `type` (SOX, Confidentiality) |

**Existing Relationships:**
- `DataSystem -[:BELONGS_TO]-> BusinessArea`
- `DataSystem -[:SUBJECT_TO]-> Policy`
- `BusinessArea -[:HAS_STAGE]-> ValueStreamStage`
- `BusinessArea -[:HAS_PRODUCT_LINE]-> DataProductLine`
- `DataProductLine -[:OWNS]-> CapabilityDataDomain`
- `BusinessProcess -[:BELONGS_TO_STAGE]-> ValueStreamStage`
- `CapabilityDataDomain -[:SUPPORTS]-> BusinessProcess`

### 1.2 What's Missing

The current graph models *what systems exist* and *how business areas are organized*, but does not model:
- **Where data physically lives** (schemas, tables, columns)
- **How data flows** through the Medallion layers (Replica → Silver → Gold → Semantic)
- **What reports consume** which data assets
- **Master data fragmentation** across teams and systems
- **The IDP platform** as the hosting environment for all medallion layers

---

## 2. IDP Medallion Architecture

The LSC Data Platform (IDP) implements a four-layer Medallion Architecture for data management.

### 2.1 Layer Definitions

| Layer | Schema Pattern | Purpose | Content |
|-------|---------------|---------|---------|
| **Replica** | `replica_<DataSystem>` (e.g., `replica_helios`) | Raw copy from source systems | No transformations; 1:1 copy of operational data |
| **Silver** | `udm_core` (facts), `mdm_core` (dimensions) | Conformed dimensional models | Cleaned, standardized, business-keyed data |
| **Gold** | `<BusinessArea>_core` (e.g., `wholesale_core`) | Business-scoped analytics | Transformed facts & dimensions for specific business areas |
| **Semantic** | `sem_<BusinessArea>` (e.g., `sem_wholesale`), `sem_masterdata` | Reporting consumption | Views consumed by reports and dashboards |

### 2.2 Special Schemas

- **`sem_masterdata`**: Cross-cutting semantic schema housing master data views. Does not belong to a single BusinessArea — serves all business areas.
- **Pre-standard semantic schemas**: semantic schemas that predate the `sem_<BusinessArea>` naming convention. They carry the `:Legacy` label with `layer: 'Semantic'`. `src/medallion.py` lists them. The LSC catalog has none.

### 2.3 Legacy Schemas (Pre-Medallion)

The following schemas predate the Medallion Architecture and are planned for refactoring:

| Schema | Status |
|--------|--------|
| `dwh_core` | Planned for refactoring |
| `staging` | Planned for refactoring |
| `dwh` | Planned for refactoring |
| `persistence` | Planned for refactoring |
| `dwh_refining` | Planned for refactoring |
| `dwh_finance` | Planned for refactoring |
| `dwh_quality` | Planned for refactoring |

These carry the `:Legacy` label (their `layer` comes from `src/medallion.py`) and `refactorTarget: 'Medallion'`.

### 2.4 Fully Qualified Name Examples

| Layer | Example | Interpretation |
|-------|---------|----------------|
| Replica | `replica_helios.Margin_Detail` | Margin_Detail table replicated from Helios |
| Silver | `udm_core.Helios_Margin_Fact` | Fact table in the unified data model |
| Silver | `mdm_core.RightAngle_Transaction_Type_Dim` | Dimension table in the master data model |
| Gold | `wholesale_core.Margin_Fact` | Fact table scoped to the Wholesale Marketing business area |
| Semantic | `sem_wholesale.Margin_vw` | View consumed by Wholesale Marketing reports |

---

## 3. Design Decisions

### 3.1 IDP as a DataSystem with Platform Role

**Decision:** Create IDP as a `DataSystem` node with `role: 'Platform'` and use a `:HOSTS` relationship to connect it to all schemas.

**Rationale:**
- IDP is the *hosting platform* for all medallion layers, not a data source like Helios or SAP_S4.
- Making it a `DataSystem` keeps it visible in the existing DataSystem inventory and queryable with existing patterns.
- The `role: 'Platform'` property and `:HOSTS` relationship distinguish it from source systems, which use `:REPLICATED_TO`.
- Source systems remain the *data origin*; IDP is the *data destination and processing environment*.

**Anti-pattern avoided:** Treating IDP identically to source systems would create confusing dual ownership (e.g., both Helios and IDP claiming `replica_helios`).

```cypher
// IDP as platform
MERGE (idp:DataSystem {name: 'LSC Data Platform (IDP)'})
ON CREATE SET idp.role = 'Platform',
  idp.description = 'Enterprise data platform implementing Medallion architecture'

// IDP hosts all schemas
MERGE (idp)-[:HOSTS]->(s:Schema {qualifiedName: 'replica_helios'})

// Source system replicates to its schema
MATCH (ds:DataSystem {name: 'Helios'})
MERGE (ds)-[:REPLICATED_TO]->(s:Schema {qualifiedName: 'replica_helios'})
```

### 3.2 Schema as a First-Class Node

**Decision:** Model `Schema` as a separate node (not just a property on `Table`).

**Rationale:**
- Schema naming conventions encode both **layer** and **ownership** (`replica_helios` → Replica layer, `wholesale_core` → Gold layer, Wholesale Marketing BusinessArea).
- Schemas are the natural join point between `DataSystem` (source) and `Table` (physical asset).
- Enables questions like "What tables are in `replica_helios`?" via traversal rather than string matching.
- Schema nodes connect to `BusinessArea` (for Gold/Semantic) and to `DataSystem` (for Replica), bridging the business and technical domains.

**Key Properties:**
| Property | Description | Example |
|----------|-------------|---------|
| `qualifiedName` | Unique identifier (merge key) | `replica_helios` |
| `layer` | Medallion layer | `Replica`, `Silver`, `Gold`, `Semantic`, `Legacy` |
| `role` | Optional functional role | `Facts`, `Dimensions`, `Master Data` |
| `isCrossCutting` | Whether schema serves all BAs | `true` (for `sem_masterdata`) |
| `refactorTarget` | Migration target for legacy | `Medallion` |

### 3.3 Layer as a Property (Not a Label)

**Decision:** Encode the medallion layer as a `layer` property on `Schema` and `Table` nodes, not as a Neo4j label.

**Rationale:**
- Labels are best for **stable type identity** (Table, Fact, Dimension, View). A table's type doesn't change.
- Layers represent **refinement state** which could theoretically change (e.g., a table promoted during refactoring).
- Neo4j label changes require `REMOVE`/`SET` operations and can break label-dependent queries; property changes are trivial.
- Only 4 layers + Legacy — a constrained property value is cleaner than 5+ additional labels.

**Anti-pattern avoided:** `:ReplicaTable`, `:SilverTable`, `:GoldTable` as separate labels. This couples identity with refinement state and makes cross-layer queries difficult.

### 3.4 Dimensional Role as a Label (Multi-Label Strategy)

**Decision:** Use Neo4j multi-labels to encode dimensional role: `:Table:Fact`, `:Table:Dimension`, `:Table:View`.

**Rationale:**
- Dimensional role is **stable type identity** — a fact table is always a fact table.
- Multi-labels enable powerful filtering: `MATCH (t:Table:Fact) WHERE t.layer = 'Gold'`.
- Avoids label proliferation while keeping queries clean.

```cypher
// A Gold-layer Fact table
CREATE (:Table:Fact {qualifiedName: 'wholesale_core.Margin_Fact', layer: 'Gold'})

// A Semantic-layer View
CREATE (:Table:View {qualifiedName: 'sem_wholesale.Margin_vw', layer: 'Semantic'})

// A Silver-layer Dimension
CREATE (:Table:Dimension {qualifiedName: 'mdm_core.Product_Dim', layer: 'Silver'})
```

### 3.5 Report → CONSUMES → View

**Decision:** Reports point to what they consume using `:CONSUMES` (Report → Table:View).

**Rationale:**
- Direction follows the data consumption pattern: "Report X consumes View Y."
- Consistent with the existing data model template which already defines `(Report)-[:CONSUMES]->(Table)`.
- Enables both forward queries ("What does this report consume?") and reverse queries ("What reports use this view?").

```cypher
MATCH (r:Report)-[:CONSUMES]->(v:Table:View {layer: 'Semantic'})
```

### 3.6 DERIVED_FROM for Cross-Layer Lineage

**Decision:** Use `:DERIVED_FROM` to capture lineage between tables across medallion layers.

**Rationale:**
- Uniform relationship type across all layers enables variable-length path traversal for full lineage.
- Direction follows the dependency: "Gold table is DERIVED_FROM Silver table."
- Distinct from `:REPLICATED_TO` (which is DataSystem → Schema, meaning data ingestion, not transformation).

```cypher
// Full lineage trace from report to source
MATCH path = (r:Report)-[:CONSUMES]->(:Table:View)-[:DERIVED_FROM*]->(src:Table)
WHERE src.layer = 'Replica'
RETURN path
```

### 3.7 MasterDataDomain as a Standalone Node

**Decision:** Create `MasterDataDomain` as a standalone node representing abstract business entities (Location, Product, Customer, etc.), linked to physical tables via `:REALIZED_IN`.

**Rationale:**
- Master data at LSC is currently **fragmented** — the same concept (e.g., Location) exists as multiple tables defined by different teams with no canonical conformed version.
- A standalone domain node serves as an **anchor** to group all physical implementations of the same business entity.
- Enables MDM program tracking: which domains are fragmented, which have been conformed, and what the canonical version is.
- A simple label (`:MasterData` on Table) cannot answer "How many different versions of Location do we have?" because there's no grouping anchor.
- The relationship direction `MasterDataDomain -[:REALIZED_IN]-> Table` reads naturally: "the Location domain is realized in these tables."

**Key Properties:**
| Property | Description | Example |
|----------|-------------|----------|
| `name` | Business entity name | `Location`, `Product`, `Customer` |
| `status` | Conformance status | `Fragmented`, `In Progress`, `Conformed` |
| `sourceFile` | Provenance — which file created this node | `List of Master Data June5_2025.xlsx` |
| `owner` | Responsible team/person (future) | — |

**Key Relationships:**
| Relationship | From | To | Meaning |
|-------------|------|----|---------|
| `REALIZED_IN` | MasterDataDomain | Table | This domain is physically implemented in this table |
| `CANONICAL_VERSION` | MasterDataDomain | Table | Shortcut to the conformed golden version (when it exists) |
| `REFACTORED_TO` | Table (Legacy) | Table (Medallion) | Legacy table was refactored into its IDP equivalent |

```cypher
// Fragmentation query for MDM program
MATCH (mdd:MasterDataDomain)-[:REALIZED_IN]->(t:Table)
RETURN mdd.name, mdd.status, count(t) AS implementations, collect(t.qualifiedName) AS tables

// MDM backlog: domains with no canonical version
MATCH (mdd:MasterDataDomain)
WHERE NOT (mdd)-[:CANONICAL_VERSION]->()
RETURN mdd.name, mdd.status

// Legacy tables refactored to Medallion equivalents
MATCH (legacy:Table)-[:REFACTORED_TO]->(idp:Table)
RETURN legacy.qualifiedName AS legacyTable, idp.qualifiedName AS idpTable, legacy.layer, idp.layer
```

### 3.8 PrivacyTier / Confidentiality Classification

**Decision:** Keep `confidentialityClassification` as a **property** on `DataSystem`. Do not create a separate `PrivacyTier` node.

**Rationale:**
- Confidentiality classification (Internal, Restricted, Highly Sensitive) is an **intrinsic attribute** of the system's data — it describes the system, not an external rule imposed on it.
- This is fundamentally different from `Policy` (SOX, Confidentiality), which represents **external regulations** that systems must comply with.
- Creating a `PrivacyTier` node with 3-4 values would produce hub nodes where 30+ systems all point to the same "Internal" node — visually cluttered, low information density.
- Property-based filtering (`WHERE ds.confidentialityClassification = 'Restricted'`) is equally powerful for queries.

**Future upgrade path:** If the organization later needs to model **data handling requirements per tier** (e.g., "Restricted systems must encrypt at rest, audit quarterly"), then promoting to a `PrivacyTier` node with those requirements as properties would add real value.

### 3.9 Decisions Updated from Deferred

| Concept | Decision | Status |
|---------|----------|--------|
| **Legacy schemas** | `:Legacy` label and `refactorTarget: 'Medallion'` | **In scope** |
| **DataPipeline nodes** | User will provide pipeline metadata file | **In scope** |
| **LogicalDataAsset** | Deferred until tables are loaded across multiple layers | Deferred |
| **Column as a node** | Implemented in Phase 5 (`load_sttm.py`). Column nodes with HAS_COLUMN and column-level DERIVED_FROM. | **Implemented** |

### 3.10 Flat Files — Property, Not a Separate Node

**Decision:** Model flat files (Excel spreadsheets, ad-hoc extracts) as `Table` nodes with `sourceType: 'FlatFile'` and `layer: 'External'`. Do not create a separate `FlatFile` node label.

**Rationale:**
- Only a handful of rows in the mapping file involve flat files (Excel, Data Armory) — not enough volume to justify a new node type.
- Flat files participate in the same relationship pattern as other tables: `Report -[:CONSUMES]-> Table`.
- A `sourceType` property is sufficient for filtering and keeps the model simple.
- If flat file volume grows significantly, a `:FlatFile` label can be added later without breaking existing queries.

```cypher
// Excel flat file
MERGE (t:Table {qualifiedName: 'Excel'})
ON CREATE SET t.name = 'Excel', t.layer = 'External', t.sourceType = 'FlatFile'
```

### 3.11 Live Reports — connectionType Property

**Decision:** Tag reports that connect directly to source systems (not through IDP) with `connectionType: 'Live'`. Do not create `:CONSUMES` relationships for these reports until specific source systems are identified.

**Rationale:**
- Many rows in the mapping file have `DataSystem.name = 'Live'`, meaning the report connects directly to a source system's operational data store.
- These rows have no Semantic View, Gold/Silver, or Replica columns populated — there is no IDP lineage to model.
- The specific source system for each Live report is not yet known.
- Tagging with a property preserves the information for future enrichment without creating incomplete relationships.

**Report `connectionType` values:**
| Value | Meaning |
|-------|---------|
| `IDP` | Report consumes IDP semantic views |
| `Live` | Report connects directly to source system (TBD) |
| `FlatFile` | Report connects to an Excel or flat file |
| `DataArmory` | Report connects to Data Armory platform |

### 3.12 Report → BELONGS_TO → CapabilityDataDomain

**Decision:** In addition to `Report -[:BELONGS_TO]-> BusinessArea`, also create `Report -[:BELONGS_TO]-> CapabilityDataDomain` based on the mapping file.

**Rationale:**
- The Phase 3 mapping file provides a `CapabilityDataDomain` for every report row, giving a finer-grained categorization than BusinessArea alone.
- This enables queries like "Which reports support the Rack Pricing capability?"
- Uses the same `:BELONGS_TO` relationship type, consistent with the existing pattern.

**CapabilityDataDomain Name Mapping:**
The mapping file uses abbreviated names that must be mapped to the graph's canonical names:

| File Value | Graph Value |
|-----------|-------------|
| `Logistic & Freight` | `Logistics & Freight` |
| `Terminals Ops` | `Terminal Ops` |
| `Plant Ops` | `Refinery Operations` |
| `Maintenance and Reliability` | `Maintenance & Reliability` |

### 3.13 Multi-Value Lineage Cells

**Decision:** Cells in the mapping file containing multiple `schema.table` values separated by newlines (`\n`) represent 1:N or N:N DERIVED_FROM relationships. The loader must split these and create one relationship per pair.

**Example:**
```
Semantic View: sem_wholesale.Rack_Price_Current_vw
Gold/Silver:   udm_core.Helios_Rack_Price_Fact\nmdm_core.Helios_Customer_Dim
Replica:       replica_helios.Rack_Price\nreplica_helios.Customer
```
This produces:
- `sem_wholesale.Rack_Price_Current_vw -[:DERIVED_FROM]-> udm_core.Helios_Rack_Price_Fact`
- `sem_wholesale.Rack_Price_Current_vw -[:DERIVED_FROM]-> mdm_core.Helios_Customer_Dim`
- `udm_core.Helios_Rack_Price_Fact -[:DERIVED_FROM]-> replica_helios.Rack_Price`
- `mdm_core.Helios_Customer_Dim -[:DERIVED_FROM]-> replica_helios.Customer`

---

## 4. Complete Node & Relationship Model

### 4.1 Node Types

| Label(s) | Key Property | Description |
|----------|-------------|-------------|
| `Server` | `serverName` | Physical database server hosting DataSystems |
| `DataSystem` | `name` | Source system or platform (407 in the LSC catalog, including IDP) |
| `BusinessArea` | `name` | Business domain (13 in the LSC catalog) |
| `Schema` | `qualifiedName` | Database schema; encodes layer + ownership |
| `Table` | `qualifiedName` | Physical table or view (base label) |
| `Table:Fact` | `qualifiedName` | Fact table (multi-label) |
| `Table:Dimension` | `qualifiedName` | Dimension table (multi-label) |
| `Table:View` | `qualifiedName` | View, typically in Semantic layer (multi-label) |
| `Column` | `qualifiedName` | Column within a table. Properties: `name`, `dataType`, `keyType`, `definition`, `transformation` |
| `Report` | `name` | BI report or dashboard. Properties: `connectionType` (IDP/Live/FlatFile/DataArmory) |
| `MasterDataDomain` | `name` | Abstract master data domain (Location, Product, etc.) |
| `Policy` | `type` | Regulatory or governance policy (SOX, Confidentiality) |
| `ValueStreamStage` | `name` | Stage in a business value stream |
| `DataProductLine` | `name` | Grouping of capability data domains |
| `CapabilityDataDomain` | `name` | Business capability with data needs |
| `BusinessProcess` | `name` | Business process linked to value stream stages |

### 4.2 Relationships

| Relationship | From | To | Description |
|-------------|------|----|-------------|
| `HOSTS` | Server | DataSystem | Server hosts this data system |
| `BELONGS_TO` | DataSystem | BusinessArea | System serves this business area |
| `BELONGS_TO` | Report | BusinessArea | Report serves this business area |
| `BELONGS_TO` | Schema | BusinessArea | Gold/Semantic schema owned by BA |
| `SUBJECT_TO` | DataSystem | Policy | System subject to this policy |
| `HOSTS` | DataSystem (Platform) | Schema | IDP platform hosts this schema |
| `REPLICATED_TO` | DataSystem (Source) | Schema | Source system data replicated to this schema |
| `REPLICATED_TO` | Table (Operational) | Table (Replica) | Table-level replication from source to IDP |
| `CONTAINS` | Schema | Table | Schema contains this table |
| `CONTAINS` | DataSystem | Table | DataSystem contains this operational table |
| `HAS_COLUMN` | Table | Column | Table contains this column |
| `DERIVED_FROM` | Table | Table | Table-level cross-layer lineage |
| `DERIVED_FROM` | Column | Column | Column-level lineage (field-to-field) |
| `MIGRATED_TO` | Table | DataSystem | Gold table migrated to Alteryx sandbox |
| `CONSUMES` | Report | Table:View | Report consumes this view |
| `BELONGS_TO` | Report | CapabilityDataDomain | Report belongs to this capability domain |
| `REALIZED_IN` | MasterDataDomain | Table | Domain is physically implemented in this table |
| `CANONICAL_VERSION` | MasterDataDomain | Table | Shortcut to the conformed golden version |
| `REFACTORED_TO` | Table (Legacy) | Table (Medallion) | Legacy table refactored into IDP equivalent |
| `HAS_STAGE` | BusinessArea | ValueStreamStage | Existing |
| `HAS_PRODUCT_LINE` | BusinessArea | DataProductLine | Existing |
| `OWNS` | DataProductLine | CapabilityDataDomain | Existing |
| `SUPPORTS` | CapabilityDataDomain | BusinessProcess | Existing |

### 4.3 Relationship Diagram

```
┌──────────┐                                ┌──────────┐
│  Server  │─ :HOSTS ─▶│                    │  Policy   │
└──────────┘           │                    │ (SOX)     │
                       ▼                    └─────▲─────┘
                                                  │ :SUBJECT_TO
┌──────────────┐  :REPLICATED_TO   ┌──────┴──────┐  :BELONGS_TO   ┌──────────────┐
│  DataSystem  │──────────────────▶│   Schema    │◀──────────────│ BusinessArea │
│  (Source)    │                   │ (Replica)   │               │              │
└──────────────┘                   └──────┬──────┘               └──────┬───────┘
                                          │ :CONTAINS                   │ :BELONGS_TO
                                          ▼                             │
┌──────────────┐  :HOSTS           ┌─────────────┐  :DERIVED_FROM      │
│  DataSystem  │──────────────────▶│   Table     │◀──────────────┐     │
│  (IDP)       │                   │ :Fact/:Dim  │               │     │
└──────────────┘                   └──┬───▲──────┘               │     │
                                      │   │ :REALIZED_IN          │     │
                               :HAS_  │   │                       │     │
                              COLUMN  │   │                       │     │
                                      ▼   │                       │     │
                                 ┌────────┴────────┐       ┌─────┴─────┐
                                 │    Column       │       │Table:View │
                                 │ :DERIVED_FROM   │       │(Semantic) │
                                 │   (col→col)     │       └─────▲─────┘
                                 └─────────────────┘             │ :CONSUMES
                                                           ┌─────┴─────┐
                                   ┌──────────────────┐    │  Report   │
                                   │MasterDataDomain  │    └───────────┘
                                   │ (Location, etc.) │
                                   └──────────────────┘
```

---

## 5. Schema Naming Conventions & Layer Mapping

The schema `qualifiedName` deterministically maps to a layer:

| Pattern | Layer | Ownership |
|---------|-------|-----------|
| `replica_<system>` | Replica | DataSystem |
| `udm_core` | Silver | Shared (facts) |
| `mdm_core` | Silver | Shared (dimensions) |
| `<ba>_core` | Gold | BusinessArea |
| `sem_<ba>` | Semantic | BusinessArea |
| `sem_masterdata` | Semantic | Cross-cutting (all BAs) |
| Pre-standard semantic schemas (`src/medallion.py`) | Legacy (Semantic) | BusinessArea |
| `dwh`, `dwh_core`, `dwh_refining`, `dwh_finance`, `dwh_quality`, `persistence`, `staging` | Legacy | Pending refactoring |

---

## 6. Key Queries Enabled by This Model

### 6.1 Platform Overview
```cypher
// All schemas hosted on IDP, grouped by layer
MATCH (idp:DataSystem {name: 'LSC Data Platform (IDP)'})-[:HOSTS]->(s:Schema)
RETURN s.layer, collect(s.qualifiedName) AS schemas
ORDER BY s.layer
```

### 6.2 End-to-End Lineage (Report → Source System)
```cypher
// Trace a report back to its source systems
MATCH (r:Report {name: 'Rack Margin Dashboard'})-[:CONSUMES]->(v:Table:View)
MATCH path = (v)-[:DERIVED_FROM*]->(src:Table)
WHERE src.layer = 'Replica'
MATCH (src)<-[:CONTAINS]-(s:Schema)<-[:REPLICATED_TO]-(ds:DataSystem)
RETURN r.name, v.qualifiedName, [n IN nodes(path) | n.qualifiedName] AS lineage, ds.name AS sourceSystem
```

### 6.3 MDM Fragmentation Assessment
```cypher
// Which master data domains are fragmented?
MATCH (mdd:MasterDataDomain)-[:REALIZED_IN]->(t:Table)
OPTIONAL MATCH (mdd)-[:CANONICAL_VERSION]->(canon)
RETURN mdd.name, mdd.status,
       count(t) AS implementations,
       collect(t.qualifiedName) AS tables,
       canon.qualifiedName AS canonicalVersion
ORDER BY count(t) DESC
```

### 6.4 SOX Compliance Scope
```cypher
// All SOX-relevant systems and what they feed
MATCH (ds:DataSystem)-[:SUBJECT_TO]->(p:Policy {type: 'SOX'})
OPTIONAL MATCH (ds)-[:REPLICATED_TO]->(s:Schema)-[:CONTAINS]->(t:Table)
RETURN ds.name, collect(DISTINCT t.qualifiedName) AS tables
```

### 6.5 Legacy Schema Inventory
```cypher
// What's still on legacy schemas?
MATCH (s:Schema:Legacy)
OPTIONAL MATCH (s)-[:CONTAINS]->(t:Table)
RETURN s.qualifiedName, count(t) AS tableCount, s.refactorTarget
```

### 6.6 Business Area Data Footprint
```cypher
// Everything a business area owns across all layers
MATCH (ba:BusinessArea {name: 'Wholesale Marketing'})
OPTIONAL MATCH (ba)<-[:BELONGS_TO]-(s:Schema)-[:CONTAINS]->(t:Table)
OPTIONAL MATCH (ba)<-[:BELONGS_TO]-(r:Report)
RETURN ba.name,
       collect(DISTINCT s.qualifiedName) AS schemas,
       count(DISTINCT t) AS tables,
       count(DISTINCT r) AS reports
```

### 6.7 Column-Level Lineage
```cypher
// Trace a column back to its source fields
MATCH (tgtCol:Column {qualifiedName: 'wholesale_core.Margin_Fact.Margin_Amount'})
MATCH path = (tgtCol)-[:DERIVED_FROM*]->(srcCol:Column)
WHERE NOT (srcCol)-[:DERIVED_FROM]->()
RETURN [n IN nodes(path) | n.qualifiedName] AS columnLineage
```

### 6.8 Table Column Inventory
```cypher
// All columns in a table with their source mappings
MATCH (t:Table {qualifiedName: 'udm_core.Helios_Margin_Fact'})-[:HAS_COLUMN]->(c:Column)
OPTIONAL MATCH (c)-[:DERIVED_FROM]->(src:Column)
RETURN c.name, c.dataType, c.keyType, src.qualifiedName AS sourceColumn
ORDER BY c.name
```

---

## 7. Data File Analysis

### 7.1 Phase 3 Reports Full Data Mapping (Full Mapping sheet)

**Source:** `Data/Phase 3 Reports Full Data Mapping.xlsx` → sheet `Full Mapping`

The sheet holds one row per report-to-view lineage path. `DataSystem.name` is IDP, Live, Excel or Data Armory.

**Columns:**
| Column | Description |
|--------|-------------|
| `CapabilityDataDomain` | Links report to an existing CDD node |
| `Report` | Report name |
| `Report Connected to SemanticLayer View` | Semantic view consumed by the report (`schema.table` format) |
| `Semantic layer view derived from :Gold:Silver` | Gold/Silver table(s) the semantic view is derived from (newline-separated if multiple) |
| `Gold:Silver objects derived from` | Replica/source table(s) the Gold/Silver objects are derived from (newline-separated if multiple) |
| `DataSystem.name` | Data source: IDP, Live, Excel, or Data Armory |
| `Comment` | Optional notes (mostly empty) |

**Schemas discovered from file:**
| Layer | Schemas |
|-------|---------|
| Semantic | `sem_wholesale`, `sem_masterdata` |
| Gold | `wholesale_core` |
| Silver | `udm_core`, `mdm_core` |
| Replica | `replica_helios`, `replica_rightangle`, `replica_atlas`, `replica_meridian`, `replica_kpler`, `replica_genscape`, `replica_files_commercial` |
| Legacy | `dwh_core`, `staging` |

---

## 8. Implementation Plan

| Phase | Script | Scope | Status |
|-------|--------|-------|--------|
| **Phase 1** | `load_schemas.py` | Create IDP DataSystem, all Schema nodes, wire `:HOSTS` and `:BELONGS_TO` | **Complete** |
| **Phase 2** | `load_tables.py` | Create Table nodes (Fact, Dimension, View); wire `:CONTAINS` to schemas | **Complete** |
| **Phase 3** | `load_lineage.py` | Table-level `:DERIVED_FROM` lineage + Alteryx provenance (Servers, Op Tables, REPLICATED_TO, Sandboxes, MIGRATED_TO) | **Complete** |
| **Phase 4** | `load_reports.py` | Report nodes with `connectionType`; wire `:CONSUMES`→View, `:BELONGS_TO`→CDD | **Complete** |
| **Phase 5** | `load_sttm.py` | Column nodes, `:HAS_COLUMN`, column-level `:DERIVED_FROM` from the STTM files. Post-processing: orphan table linking, Operational source table creation. | **Complete** |
| **Phase 6** | `load_master_data.py` | MasterDataDomain nodes, `:REALIZED_IN`, `:REFACTORED_TO`, operational Table/Server/DataSystem wiring | **Complete** |
| **Phase 6a** | `load_location_idp.py` | Location IDP master data (`comment` & `sourceDataSystem` properties, REALIZED_IN edges) | **Complete** |
| **Phase 7** | `neo4j_loader.py` | Centralized Server canonicalization (`CANONICAL_SERVER_NAMES`, `TEST_TO_PROD_SERVER`, `canonicalize_server_name`). Merged duplicate Server nodes, collapsed test→prod. Manual DERIVED_FROM corrections in `load_lineage.py`. | **Complete** |
| **Phase 8** (Future) | — | DataPipeline nodes, LogicalDataAsset | Pending pipeline metadata |

---

## 9. Files Reference

### Load Scripts (run in order)

| File | Purpose |
|------|---------|
| `src/neo4j_loader.py` | Shared Neo4j connection helper, CSV loader, and canonicalization utilities |
| `src/load_datasystems.py` | Phase 0: DataSystem nodes from CSV |
| `src/load_schemas.py` | Phase 1: Schema nodes, IDP platform wiring, replica links |
| `src/load_tables.py` | Phase 2: Table nodes with multi-labels (Fact/Dimension/View) |
| `src/load_lineage.py` | Phase 3: Table-level DERIVED_FROM + full Alteryx provenance graph |
| `src/load_reports.py` | Phase 4: Report nodes, CONSUMES, BELONGS_TO edges |
| `src/load_sttm.py` | Phase 5: Column nodes, HAS_COLUMN, column-level DERIVED_FROM (STTM files) |
| `src/load_master_data.py` | Phase 6: MasterDataDomain, REALIZED_IN, REFACTORED_TO, operational tables |
| `src/load_location_idp.py` | Phase 6a: Location IDP master data (comments, sourceDataSystem) |

### Utilities

| File | Purpose |
|------|---------|
| `src/audit_sttm_sheets.py` | Audit STTM file sheet structures and column headers |
| `src/_audit_skipped_columns.py` | Find STTM columns skipped during load |
| `src/data_cleaning_utils/` | merge, dedup, append, verify scripts |

### Data Files

| File | Purpose |
|------|---------|
| `Data/schemas.csv` | Schema definitions |
| `Data/tables.csv` | Table definitions (core tables) |
| `Data/reports.csv` | Report definitions + CDD associations |
| `Data/Source_System_from_IDP.csv` | DataSystem rows, enriched with Sharepoint attributes |
| `Data/Phase 3 Reports Full Data Mapping.xlsx` | Mapping: Reports → Semantic Views → Gold/Silver → Replica lineage |
| `Data/Phase 3 Unique Master Data.xlsx` | Master data domain-to-table mappings |
| `Data/new data system files to process/report_alteryx_master_data_requirements_DEC4th.xlsx` | Alteryx master data requirements (2nd master data file) |
| `Data/new data system files to process/Location_Tables_In_IDP.xlsx` | Location IDP tables (comments, operational source DataSystem) |
| `Data/sttms/` | STTM Excel files (column-level lineage source) |

### Reference

| File | Purpose |
|------|---------|
| `src/2_load_data.cypher` | Original Cypher creation steps (Steps 1–8, historical reference) |
| `src/data_model_merge_template.cypher` | Full data model template (arrows.app export) |
| `docs/medallion_architecture_graph_design.md` | This document |
| `AGENTS.md` | AI pair-programming guidance and project conventions |
