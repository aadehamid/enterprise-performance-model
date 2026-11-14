# Graph Schema Reference

Detailed node and relationship catalog for the Lagos Refining & Supply Company (LSC) Data Lineage Knowledge Graph. This file is loaded on-demand when the agent needs specific property names, relationship counts, or constraint details.

---

## Node Labels & Key Properties

| Label | Count | Key Property | Other Notable Properties |
|---|---|---|---|
| **Server** | 210 | `serverName` | createdAt. Hosts end in `lsc.internal` (e.g. `HELIOS.prod.db.lsc.internal`) |
| **DataSystem** | 407 | `name` | platform, systemId, applicationType, applicationService, ingestionMethod, dataModality, refreshFrequency, purviewReplicaSchemaName, confidentialityClassification, isSoxRelevant, isRecordActive, scope, status, description, createdAt |
| **Schema** | 257 | `qualifiedName` | name (often null), layer, role, isCrossCutting, refactorTarget, createdAt |
| **Table** | 7,419 | `qualifiedName` | name, tableName, layer, comment, sourceDataSystem, sourceFile, sttmLink, tableauReportEntity, viewDefinition, createdAt, updatedAt |
| **Column** | 30,972 | `qualifiedName` | name, dataType, keyType, createdAt |
| **FlatFile** | 1 | `name` | `LSC Commercial Files` |
| **Report** | 2,628 | `reportKey` | name, webUrl, workspaceName, connectionType, source, state, lastSeen, sourceFile, createdAt. `reportKey` is `webUrl` when that value is non-empty, otherwise `name:` plus `name`. `name` is the display property and is not unique. |
| **DataProduct** | 12 | `name` | sourceFile, createdAt |
| **MasterDataDomain** | 11 | `name` | status, sourceFile, createdAt |
| **Policy** | 2 | `type` | `SOX`, `Confidentiality`. description, confidentialityClassification, isSoxRelevant |
| **BusinessArea** | 13 | `name` | description, createdAt |
| **DataProductLine** | 4 | `name` | |
| **CapabilityDataDomain** | 30 | `name` | description, createdAt |
| **BusinessProcess** | 12 | `name` | description, sequenceLabel |
| **ValueStreamStage** | 3 | `name` | description, sequenceOrder |
| **DataPipeline** | 7 | `name` | synapseDataflow, alteryxWorkflow, sourceFile. Synapse pipeline that reads Replica tables and loads Gold tables (e.g. `PL_Wholesale_Margin`) |
| **DataModel** | 42 | `name` | fileName, modelType (`Conceptual` \| `Logical`), folderLink, sourceFile. ER Studio `.DM1` data model linked to a CapabilityDataDomain and optionally a DataSystem |
| **Dimension** | 98 | `qualifiedName` | Multi-label on Table. Query: `MATCH (t:Table:Dimension)` |
| **Fact** | 60 | `qualifiedName` | Multi-label on Table. Query: `MATCH (t:Table:Fact)` |
| **View** | 2,300 | `qualifiedName` | Multi-label on Table. Query: `MATCH (t:Table:View)` |
| **Person** | 291 | `name` | createdAt |
| **RoleAssignment** | 2,314 | `(type, scope)` | status, createdAt. `type` = `'Data Analyst'` \| `'Data Analyst Backup'`. `scope` = Table qualifiedName or Report key |
| **Legacy** | 124 | `qualifiedName` | Multi-label on Table/Schema nodes from pre-standard schemas. 117 Tables + 7 Schemas. Query: `MATCH (t:Table:Legacy)` |
| **Session** | 50 | `id` | Root of a portal chat session |
| **Message** | 200 | `id` | question, cypher, answer, feedback (`'good'` \| `'poor'` \| absent), feedbackComment, timestamp. The SQLite archive column stays `feedback_comment`. |

---

## `sourceFile` as a Grouping Filter

`Table.sourceFile` names the workbook that defined the table metadata. STTM workbooks follow `STTM_<DataSystem>_Replica.xlsx`. Legacy tables come from `Legacy_DWH_Inventory.xlsx`. Flat-file tables carry their upload file name.

```cypher
// All legacy warehouse tables from the inventory workbook
MATCH (t:Table) WHERE t.sourceFile = 'Legacy_DWH_Inventory.xlsx'
RETURN t
```

Common values: `'Legacy_DWH_Inventory.xlsx'`, `'STTM_Helios_Replica.xlsx'`, `'STTM_RightAngle_Replica.xlsx'`, `'Budget_Upload.xlsx'`.

---

## Relationship Patterns

### Data Lineage

| Pattern | Count | Description |
|---|---:|---|
| `(:Table)-[:DERIVED_FROM]->(:Table)` | 2,633 | Table-level lineage between layers |
| `(:Column)-[:DERIVED_FROM]->(:Column)` | 13,170 | Column-level lineage |
| `(:Table)-[:REPLICATED_TO]->(:Table)` | 1,721 | Operational → Replica |
| `(:Table)-[:HAS_COLUMN]->(:Column)` | 30,972 | Table contains column |
| `(:Table)-[:MIGRATED_FROM]->(:DataSystem)` | 9 | Gold table sourced from Alteryx Sandbox |
| `(:Table)-[:REFACTORED_TO]->(:Table)` | 89 | Legacy → IDP Silver/Gold |
| `(:DataSystem)-[:MIGRATED_TO]->(:Table)` | 110 | DataSystem migrated to Table |
| `(:DataPipeline)-[:READS]->(:Table)` | 27 | Pipeline reads a Replica table |
| `(:DataPipeline)-[:LOADS]->(:Table)` | 9 | Pipeline writes a Gold table |

### Infrastructure

| Pattern | Count | Description |
|---|---:|---|
| `(:Server)-[:HOSTS]->(:DataSystem)` | 314 | Server hosts DataSystem |
| `(:DataSystem)-[:HOSTS]->(:Schema)` | 294 | DataSystem hosts Schema |
| `(:DataSystem)-[:CONTAINS]->(:Table)` | 2,147 | Operational tables within DataSystem |
| `(:DataSystem)-[:REPLICATED_TO]->(:Schema)` | 9 | DataSystem replicated to Schema |
| `(:Schema)-[:CONTAINS]->(:Table)` | 7,419 | Every table sits in one Schema |
| `(:FlatFile)-[:CONTAINS]->(:Table)` | 13 | Flat-file Operational tables |
| `(:DataSystem)-[:SUBJECT_TO]->(:Policy)` | 15 | DataSystem subject to Policy |

### Consumption

| Pattern | Count | Description |
|---|---:|---|
| `(:Report)-[:CONSUMES]->(:Table)` | 13,073 | Report consumes a table or view. `expression` holds the Power Query M code; `source` and `lastSeen` record where and when the link was seen |
| `(:DataProduct)-[:REALIZED_BY]->(:Table)` | 353 | DataProduct realized by Semantic view |
| `(:MasterDataDomain)-[:REALIZED_IN]->(:Table)` | 161 | Business concept realized in physical table |

### Role Assignments

| Pattern | Count | Description |
|---|---:|---|
| `(:Person)-[:HAS_ROLE]->(:RoleAssignment)` | 2,419 | Person has role assignment |
| `(:RoleAssignment)-[:APPLIES_TO]->(:Table)` | 799 | Role scoped to a table or view |
| `(:RoleAssignment)-[:APPLIES_TO]->(:Report)` | 1,515 | Role scoped to a report |

### Business Context

| Pattern | Count | Description |
|---|---:|---|
| `(:DataSystem)-[:BELONGS_TO]->(:BusinessArea)` | 246 | DataSystem belongs to BusinessArea |
| `(:Schema)-[:BELONGS_TO]->(:BusinessArea)` | 35 | Schema belongs to BusinessArea |
| `(:Table)-[:BELONGS_TO]->(:CapabilityDataDomain)` | 176 | Conformed table belongs to domain |
| `(:Report)-[:BELONGS_TO]->(:CapabilityDataDomain)` | 199 | Report belongs to domain |
| `(:DataProduct)-[:BELONGS_TO]->(:CapabilityDataDomain)` | 12 | DataProduct belongs to domain |
| `(:DataModel)-[:MODELS]->(:CapabilityDataDomain)` | 38 | Data model models domain |
| `(:DataModel)-[:BELONGS_TO]->(:DataSystem)` | 20 | Data model covers a source system |
| `(:DataProductLine)-[:OWNS]->(:CapabilityDataDomain)` | 17 | Product line owns domain |
| `(:CapabilityDataDomain)-[:SUPPORTS]->(:BusinessProcess)` | 46 | Domain supports process |
| `(:BusinessProcess)-[:BELONGS_TO_STAGE]->(:ValueStreamStage)` | 12 | Process belongs to stage |
| `(:BusinessProcess)-[:INFORMS]->(:BusinessProcess)` | 1 | Process informs another |
| `(:BusinessArea)-[:HAS_PRODUCT_LINE]->(:DataProductLine)` | 4 | BusinessArea has product line |
| `(:BusinessArea)-[:HAS_STAGE]->(:ValueStreamStage)` | 3 | BusinessArea has stage |
| `(:ValueStreamStage)-[:NEXT_STAGE]->(:ValueStreamStage)` | 2 | Stage sequence |
| `(:ValueStreamStage)-[:LOOPS_BACK_TO]->(:ValueStreamStage)` | 1 | Stage loop-back |

### Conversation History & Feedback

| Pattern | Count | Description |
|---|---:|---|
| `(:Session)-[:HAS_MESSAGE]->(:Message)` | 200 | Chat session links to each message |
| `(:Session)-[:LAST_MESSAGE]->(:Message)` | 50 | Latest message in the session |
| `(:Message)-[:NEXT]->(:Message)` | 150 | Message order within a session |

30 messages carry feedback: 20 `'good'` and 10 `'poor'`.

---

## Constraints & Indexes

Every label except the role labels (`Dimension`, `Fact`, `View`, `Legacy`) has one node key constraint named `<Label>_constraint`.

| Label | Node key |
|---|---|
| BusinessArea, BusinessProcess, CapabilityDataDomain, DataModel, DataPipeline, DataProduct, DataProductLine, DataSystem, FlatFile, MasterDataDomain, Person, ValueStreamStage | `name` |
| Table, Column, Schema | `qualifiedName` |
| Report | `reportKey` |
| Server | `serverName` |
| Policy | `type` |
| RoleAssignment | `(type, scope)` |
| Session, Message | `id` |

There are no fulltext or standalone range indexes. Filter by `name` or `qualifiedName` with `CONTAINS` or `=~ '(?i)...'`.

`DataSystem.isSoxRelevant`, `DataSystem.isRecordActive`, and `Policy.isSoxRelevant` are booleans. Use `ds.isSoxRelevant = true`.

---

## Graph Statistics Summary

- **26 node labels** (22 primary labels plus the `Dimension`, `Fact`, `View`, and `Legacy` role labels)
- **29 relationship types**
- **~44.9K nodes** total (dominated by Column: 31.0K, Table: 7.4K, Report: 2.6K, RoleAssignment: 2.3K)
- **~78.5K relationships** total (dominated by HAS_COLUMN: 31.0K, DERIVED_FROM: 15.8K, CONSUMES: 13.1K, CONTAINS: 9.6K)

*Counts from the LSC synthetic catalog, seed 26, generated 2026-11-01.*
