# Project Overview

Background context for the Lagos Refining & Supply Company (LSC) Data Lineage Knowledge Graph. This file is loaded on-demand when the agent needs to understand the project structure, how the catalog is built, data quality rules, or known limitations.

---

## What This Graph Models

A Neo4j knowledge graph that models the **medallion architecture data lineage** for LSC (Lagos Refining & Supply Company), a fictional downstream oil and gas company: refining, supply and trading, pipelines and terminals, wholesale marketing, and renewable fuels. Its enterprise data platform is the **LSC Data Platform (IDP)** on Azure Synapse (`lsc-idp-prod.sql.azuresynapse.net`). The graph traces data from operational source systems (Helios, RightAngle, SAP_S4, Salesforce, IBM_Maximo, AVEVA_PI, Toptech_TMS, LabWare_LIMS, site LIMS and BlendPlan instances, and others) through the Replica, Silver, Gold, and Semantic layers, at both table and column level. It connects tables to the Power BI reports that consume them and maps master data domains to their physical tables.

LSC has five Gold business areas: Wholesale Marketing (`wholesale_core`), Refining & Planning (`refining_core`), Renewable Fuels (`renewables_core`), Supply & Trading (`trading_core`), and Pipelines & Terminals (`logistics_core`).

### High-Level Schema

```
Server -[:HOSTS]-> DataSystem -[:CONTAINS]-> Table   (operational source tables)
DataSystem -[:HOSTS]-> Schema -[:CONTAINS]-> Table   (every table sits in one Schema)
FlatFile -[:CONTAINS]-> Table                 (flat-file source -> operational table)
Table  -[:HAS_COLUMN]-> Column                (table contains column)
Table  -[:DERIVED_FROM]-> Table               (table-level lineage between layers)
Column -[:DERIVED_FROM]-> Column              (column-level lineage)
Table  -[:REPLICATED_TO]-> Table              (operational -> replica)
Table  -[:MIGRATED_FROM]-> DataSystem         (gold -> Alteryx sandbox)
DataPipeline -[:READS]-> Table                (pipeline reads replica)
DataPipeline -[:LOADS]-> Table                (pipeline writes gold)
Report -[:CONSUMES]-> Table                   (report -> semantic view, M code on con.expression)
Report -[:BELONGS_TO]-> CapabilityDataDomain  (report ownership)
Table  -[:BELONGS_TO]-> CapabilityDataDomain  (conformed table ownership)
DataProduct -[:BELONGS_TO]-> CapabilityDataDomain (product -> domain ownership)
DataProduct -[:REALIZED_BY]-> Table           (product -> semantic view)
MasterDataDomain -[:REALIZED_IN]-> Table      (business concept -> physical table)
Table  -[:REFACTORED_TO]-> Table              (legacy dwh table -> IDP equivalent)
DataModel -[:MODELS]-> CapabilityDataDomain   (model -> domain)
DataModel -[:BELONGS_TO]-> DataSystem         (model covers a specific source system)
Session -[:HAS_MESSAGE]-> Message             (portal chat history and feedback)
```

---

## How the Catalog Is Built

The LSC catalog is synthetic. No production data ships with it.

| Step | Script | What It Does |
|------|--------|--------------|
| 1 | `src/generate_shareable_catalog.py` | Writes a deterministic catalog for a seed (default 26) to `synthetic_data/`: node and relationship JSONL files plus `manifest.json` with counts and expected answers |
| 2 | `src/load_synthetic_catalog.py --database lsc` | Runs `synthetic/ingest.cypher` against an empty or LSC database and asserts the manifest counts |
| 3 | `src/verify_synthetic_catalog.py --database lsc` | Checks the loaded database holds exactly the generated catalog and answers every competency question in `synthetic/competency_questions.json` |

The data model lives in `synthetic/lsc_data_model.json`. Every competency question has a planted path, for example:

- `Helios.MarginDetail` → `replica_helios.Margin_Detail` → `udm_core.Helios_Margin_Fact` → `wholesale_core.Margin_Fact` → `sem_wholesale.Margin_vw`, loaded by pipeline `PL_Wholesale_Margin`, realized by data product `Rack Margin Analytics` in domain `Wholesale Marketing`.
- `RightAngle.TransactionType` → `replica_rightangle.Transaction_Type` → `mdm_core.RightAngle_Transaction_Type_Dim` → `sem_masterdata.TransactionType_vw`, consumed by reports `Trading Deal Activity` and `Transaction Type Reference`.
- Legacy `dwh.LSC_Product_Master` refactors to `wholesale_core.Product_Dim`, which realizes master data domain `Product`.

> **Note for skill users:** The generator and loader build the graph. They are **not required** to use this skill. You only need access to the Neo4j database to run the Cypher queries this skill generates.

---

## Data Quality & Canonicalization

- **Server names** follow `<SYSTEM>.prod.db.lsc.internal` for named source systems (e.g. `HELIOS.prod.db.lsc.internal`) and `sqlsrv-NNN.lsc.internal` or `sqlsrv-<site>-NN.lsc.internal` for other hosts. The IDP is hosted on `sqlsrv-wri-01.lsc.internal`.
- **DataSystem names** keep their product casing (`RightAngle`, `SAP_S4`, `Helios`). Plant systems carry a site suffix (`LIMS_HOU`, `BlendPlan_RTM`).
- **Table qualifiedNames** are `schema.tableName`. Operational names keep source casing (`Helios.MarginDetail`); Replica and later layers use snake case (`replica_helios.Margin_Detail`).
- **Medallion layer** is derived from the schema name only. `dwh*`, `persistence`, and `staging` tables and Silver tables with `Union` in their name carry the `:Legacy` label.

---

## Current Graph Counts

*LSC synthetic catalog, seed 26, generated 2026-11-01.*

| Metric | Count |
|--------|------:|
| Table nodes | 7,419 |
| Column nodes | 30,972 |
| Schema nodes | 257 |
| DataSystem nodes | 407 |
| DataProduct nodes | 12 |
| DataPipeline nodes | 7 |
| DataModel nodes | 42 |
| FlatFile nodes | 1 |
| Server nodes | 210 |
| MasterDataDomain nodes | 11 |
| CapabilityDataDomain nodes | 30 |
| Report nodes | 2,628 |
| DERIVED_FROM edges | 15,803 |
| CONTAINS edges | 9,579 |
| HAS_COLUMN edges | 30,972 |
| REPLICATED_TO edges | 1,730 |
| REFACTORED_TO edges | 89 |
| REALIZED_BY edges | 353 |
| REALIZED_IN edges | 161 |
| BELONGS_TO edges | 688 |
| MODELS edges | 38 |
| CONSUMES edges | 13,073 |
| HOSTS edges | 608 |
| MIGRATED_TO edges | 110 |

**Tables by layer:** Operational 2,160 · Replica 1,721 · Silver 759 · Gold 43 · Semantic 2,736 · (117 carry `:Legacy` label)

---

## Known Gaps

> These gaps exist in the LSC catalog. They are documented here so that agents can explain empty query results when users hit these edges.

- **1,973 Semantic views have no DERIVED_FROM lineage.** 1,527 of them sit in the `sem_<area>_kpi`, `_ops`, `_planning`, and `_pricing` schemas; the rest are in the base `sem_<area>` schemas. Examples: `sem_masterdata.Customer_Ship_To_Snapshot_vw`, `sem_masterdata.Blend_Recipe_Detail_vw`, `sem_wholesale.Lifting_Forecast_Open_vw`, `sem_wholesale.Supply_Agreement_History_vw`.
- **439 Operational tables have no Replica copy.** They exist in their source DataSystem but are not yet replicated into the IDP.
- **Flat-file tables stop at the Operational layer.** The 13 `replica_files_commercial.*` tables under FlatFile `LSC Commercial Files` have no `REPLICATED_TO` or downstream edges.
- **Column DERIVED_FROM edges carry no `transformation` property.**

---

## Data Sources

| File | Description |
|------|-------------|
| `synthetic/lsc_data_model.json` | Graph data model (labels, keys, properties, relationships) |
| `synthetic/ingest.cypher` | Constraint and `MERGE` statements generated from the model |
| `synthetic/competency_questions.json` | Questions with check queries and manifest keys |
| `synthetic_data/nodes/*.jsonl`, `synthetic_data/rels/*.jsonl` | Generated catalog |
| `synthetic_data/manifest.json` | Expected counts and competency answers |
