# Neo4j Data Lineage Knowledge Graph — LLM Context

Use this document as system-prompt context when asking an LLM to generate Cypher
queries against the Lagos Refining & Supply Company (LSC) Data Lineage Knowledge Graph.

---

## 1. Data Flow (Layer Order)

Tables flow through these layers (stored in `Table.layer`):

```
Operational → Replica → Silver → Gold → Semantic
```

- **Operational** — source tables inside external systems (Helios, RightAngle, SAP_S4, Salesforce, LIMS_<site>, BlendPlan_<site>, etc.)
- **Replica** — 1:1 copy of the operational table into the LSC Data Platform (IDP)
- **Silver** — cleaned/conformed dimensions and facts (`mdm_core.*`, `udm_core.*`)
- **Gold** — business-specific aggregated tables (`wholesale_core.*`, `refining_core.*`, `renewables_core.*`, `trading_core.*`, `logistics_core.*`)
- **Semantic** — views consumed by reports (`sem_wholesale.*`, `sem_masterdata.*`, and the `sem_<area>_kpi`, `_ops`, `_planning`, `_pricing` variants)

Pre-standard schemas (`dwh`, `dwh_core`, `dwh_refining`, `dwh_finance`, `dwh_quality`, `persistence`, `staging`) carry a **`:Legacy` label** instead of a separate layer value. Their `layer` property holds the correct medallion layer (Silver). Query legacy items via `MATCH (t:Table:Legacy)`.

---

## 2. Naming Conventions

`Table.qualifiedName` follows the pattern `schema.tableName`:

| Prefix | Layer | Example |
|---|---|---|
| `replica_helios.*` | Replica | `replica_helios.Margin_Detail` |
| `replica_rightangle.*` | Replica | `replica_rightangle.Transaction_Type` |
| `replica_files_commercial.*` | Operational (flat file) | `replica_files_commercial.Budget_Upload` |
| `mdm_core.*` | Silver (dim) | `mdm_core.RightAngle_Transaction_Type_Dim` |
| `udm_core.*` | Silver (fact) | `udm_core.Helios_Margin_Fact` |
| `<business_area>_core.*` (e.g. `wholesale_core.*`) | Gold | `wholesale_core.Margin_Fact` |
| `sem_<business_area>.*` (e.g. `sem_wholesale.*`, `sem_masterdata.*`) | Semantic | `sem_wholesale.Margin_vw` |
| `dwh.*` / `dwh_core.*` | Silver + `:Legacy` label | `dwh.LSC_Product_Master` |
| `dwh_refining.*` / `dwh_finance.*` / `dwh_quality.*` | Silver + `:Legacy` label | `dwh_finance.vw_Cinder_Permit_To_Work_Hist` |
| `persistence.*` | Silver + `:Legacy` label | `persistence.LSC_Raffia_Compliance_Obligation` |
| `staging.*` | Silver + `:Legacy` label | `staging.LSC_Atlas_Rack_Lifting_Agg` |

`Column.qualifiedName` = `schema.tableName.columnName`

### Sample qualifiedName values per layer

| Layer | Examples |
|---|---|
| Operational | `Helios.MarginDetail`, `RightAngle.TransactionType`, `SAP_S4.Customer` |
| Replica | `replica_helios.Margin_Detail`, `replica_rightangle.Transaction_Type`, `replica_helios.Price_Batch` |
| Silver | `mdm_core.RightAngle_Transaction_Type_Dim`, `mdm_core.LSC_Product_Union_Dim`, `udm_core.Helios_Margin_Fact` |
| Silver (:Legacy) | `dwh.LSC_Product_Master`, `dwh_core.LSC_Cascade_Turnaround_Bridge`, `persistence.LSC_Raffia_Compliance_Obligation` |
| Gold | `wholesale_core.Margin_Fact`, `wholesale_core.Product_Dim`, `refining_core.Refinery_Margin_Fact`, `logistics_core.Tank_Inventory_Fact` |
| Semantic | `sem_wholesale.Margin_vw`, `sem_wholesale.Price_Batch_Dim_vw`, `sem_masterdata.TransactionType_vw` |

---

## 3. Node Labels & Key Properties

| Label | Count | Key Property | Other Notable Properties |
|---|---|---|---|
| **Server** | 210 | `serverName` | createdAt |
| **DataSystem** | 407 | `name` | platform, systemId, applicationType, ingestionMethod, status |
| **Schema** | 257 | `qualifiedName` | name (often null), layer, role |
| **Table** | 7419 | `qualifiedName` | name, layer, **sourceFile** (grouping key — see below), sourceDataSystem, viewDefinition |
| **Column** | 30972 | `qualifiedName` | name, dataType, keyType |
| **FlatFile** | 1 | `name` | `LSC Commercial Files` |
| **Report** | 2628 | `reportKey` | name, connectionType, sourceFile, **workspaceName**, webUrl, state. `reportKey` is `webUrl` when set, otherwise `name:` plus `name`. `name` is the display property and is not unique. |
| **DataProduct** | 12 | `name` | sourceFile |
| **MasterDataDomain** | 11 | `name` | status |
| **Policy** | 2 | `type` | description, confidentialityClassification, isSoxRelevant |
| **BusinessArea** | 13 | `name` | description |
| **DataProductLine** | 4 | `name` | |
| **CapabilityDataDomain** | 30 | `name` | description |
| **BusinessProcess** | 12 | `name` | description, sequenceLabel |
| **ValueStreamStage** | 3 | `name` | description, sequenceOrder |
| **Dimension** | 98 | `qualifiedName` | Multi-label on Table |
| **Fact** | 60 | `qualifiedName` | Multi-label on Table |
| **View** | 2300 | `qualifiedName` | Multi-label on Table |
| **Person** | 291 | `name` | createdAt |
| **RoleAssignment** | 2314 | `(type, scope)` | status, createdAt. `type` = 'Data Analyst' \| 'Data Analyst Backup'. `scope` = Table qualifiedName or Report key |
| **Legacy** | 124 | `qualifiedName` | Multi-label on Table/Schema nodes from pre-standard schemas. Query: `MATCH (t:Table:Legacy)` |
| **Session** | 50 | `id` | Root of a portal chat session |
| **Message** | 200 | `id` | question, cypher, answer, feedback ('good'\|'poor'\|absent), feedbackComment, timestamp. The SQLite archive column stays `feedback_comment`. |
| **DataPipeline** | 7 | `name` | synapseDataflow, alteryxWorkflow, sourceFile. Represents a Synapse pipeline that reads Replica tables and loads Gold tables. |
| **DataModel** | 42 | `name` | fileName, modelType (`Conceptual` \| `Logical`), folderLink, sourceFile. ER Studio `.DM1` data model artifacts linked to a CapabilityDataDomain and optionally a specific DataSystem. |

### `sourceFile` as a grouping filter

`Table.sourceFile` identifies the workbook that defined the table metadata. STTM workbooks follow `STTM_<DataSystem>_Replica.xlsx`. Use it to group tables by source document:

```cypher
// All legacy warehouse tables from the inventory workbook
MATCH (t:Table) WHERE t.sourceFile = 'Legacy_DWH_Inventory.xlsx'
RETURN t
```

Common `sourceFile` values: `'Legacy_DWH_Inventory.xlsx'`, `'STTM_Helios_Replica.xlsx'`, `'STTM_RightAngle_Replica.xlsx'`.

---

## 4. Relationship Patterns

### Data Lineage
```
(:Table)-[:DERIVED_FROM]->(:Table)                     // 2633 — table-level lineage
(:Column)-[:DERIVED_FROM]->(:Column)                   // 13170 — column-level lineage
(:Table)-[:REPLICATED_TO]->(:Table)                    // 1721 — Operational → Replica
(:Table)-[:HAS_COLUMN]->(:Column)                      // 30972
(:Table)-[:MIGRATED_FROM]->(:DataSystem)               // 9   — Gold migrated from Alteryx Sandbox
(:Table)-[:REFACTORED_TO]->(:Table)                    // 89  — Legacy → IDP Silver/Gold
(:DataSystem)-[:MIGRATED_TO]->(:Table)                 // 110
(:DataPipeline)-[:READS]->(:Table)                     // 27  — Replica tables read by a pipeline
(:DataPipeline)-[:LOADS]->(:Table)                     // 9   — Gold tables written by a pipeline
```

### Infrastructure
```
(:Server)-[:HOSTS]->(:DataSystem)                      // 314
(:DataSystem)-[:HOSTS]->(:Schema)                      // 294
(:DataSystem)-[:CONTAINS]->(:Table)                    // 2147 — Operational tables
(:DataSystem)-[:REPLICATED_TO]->(:Schema)              // 9
(:Schema)-[:CONTAINS]->(:Table)                        // 7419 — every table sits in one Schema
(:FlatFile)-[:CONTAINS]->(:Table)                      // 13  — flat file Operational tables
(:DataSystem)-[:SUBJECT_TO]->(:Policy)                 // 15
```

### Consumption
```
(:Report)-[con:CONSUMES]->(:Table)                     // 13073 — report consumes table/view. The relationship carries a conformed `expression` property (i.e. `con.expression` contains the Power Query M loading logic, including the selected column names).
(:DataProduct)-[:REALIZED_BY]->(:Table)                // 353
(:MasterDataDomain)-[:REALIZED_IN]->(:Table)           // 161
```

### Role Assignments
```
(:Person)-[:HAS_ROLE]->(:RoleAssignment)              // 2419
(:RoleAssignment)-[:APPLIES_TO]->(:Table)             // 799  — scoped to a table or view
(:RoleAssignment)-[:APPLIES_TO]->(:Report)            // 1515 — scoped to a report
```

### Business Context
```
(:DataSystem)-[:BELONGS_TO]->(:BusinessArea)           // 246
(:Schema)-[:BELONGS_TO]->(:BusinessArea)               // 35
(:Table)-[:BELONGS_TO]->(:CapabilityDataDomain)        // 176
(:Report)-[:BELONGS_TO]->(:CapabilityDataDomain)       // 199
(:DataProduct)-[:BELONGS_TO]->(:CapabilityDataDomain)  // 12
(:DataModel)-[:MODELS]->(:CapabilityDataDomain)        // 38 — data model models a capability domain
(:DataModel)-[:BELONGS_TO]->(:DataSystem)              // 20 — data model covers a specific source system
(:DataProductLine)-[:OWNS]->(:CapabilityDataDomain)    // 17
(:CapabilityDataDomain)-[:SUPPORTS]->(:BusinessProcess) // 46
(:BusinessProcess)-[:BELONGS_TO_STAGE]->(:ValueStreamStage) // 12
(:BusinessProcess)-[:INFORMS]->(:BusinessProcess)      // 1
(:BusinessArea)-[:HAS_PRODUCT_LINE]->(:DataProductLine) // 4
(:BusinessArea)-[:HAS_STAGE]->(:ValueStreamStage)      // 3
(:ValueStreamStage)-[:NEXT_STAGE]->(:ValueStreamStage) // 2
(:ValueStreamStage)-[:LOOPS_BACK_TO]->(:ValueStreamStage) // 1
```

### Conversation History & Feedback
```
(:Session)-[:HAS_MESSAGE]->(:Message)                  // 200
(:Session)-[:LAST_MESSAGE]->(:Message)                 // 50
(:Message)-[:NEXT]->(:Message)                         // 150
```

---

## 5. Output Rules

- **Prefer graph visualization** — return **nodes and relationships** (e.g., `RETURN n, r, m`) so Neo4j Browser renders a visual graph. However, if the user's question clearly calls for a **count**, **list**, or **tabular summary** (e.g., "how many reports...?", "list all table names in...", "count of..."), return the appropriate scalar, aggregation, or property projection instead. When in doubt, return the graph visualization and mention that the user can add `count()` or property projections if they need a summary.
- Alias **all relationships** so they render as edges in the graph.
- Use `OPTIONAL MATCH` for all hops beyond the anchor node.
- **Default to full lineage.** Any question about lineage, tracing, origin, data flow, or "where does X come from / go to" should show the **complete chain** (Server -> DataSystem -> Operational -> Replica -> Silver -> Gold -> Semantic -> Report) unless the user explicitly asks for a partial view (e.g., "just show upstream" or "only show the silver sources"). When in doubt, show more context, not less.

---

## 6. Common Query Patterns

### Full Lineage (primary and default pattern)

When asked for **"full lineage"** **or any lineage/tracing question that does not explicitly limit scope**, the query must show the
complete chain: **Server -> DataSystem -> Operational -> Replica -> Silver -> Gold -> Semantic -> Report**.

The canonical pattern anchors on a Semantic view and walks both upstream and downstream:

```cypher
// Full lineage for a Semantic view
MATCH (sem:Table {qualifiedName: 'sem_wholesale.Margin_vw'})

// Upstream: walk DERIVED_FROM chain through Gold/Silver/Replica
MATCH upPath = (sem)-[:DERIVED_FROM*1..5]->(upstream:Table)

// For each Replica leaf, get Operational → DataSystem → Server
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (srv:Server)-[h:HOSTS]->(ds)

// Downstream: Reports consuming the semantic view
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)

RETURN sem, upPath, op, ds, srv, rpt, rpl, c1, h, con
```

To adapt this pattern:
- **Anchor on a different table**: change the `qualifiedName` in the first MATCH.
- **Anchor on a Report**: start with `MATCH (rpt:Report {name: '...'})-[con:CONSUMES]->(sem:Table)` then follow the same upstream chain from `sem`.
- **Anchor on a DataSystem**: start with `MATCH (ds:DataSystem {name: '...'})-[:CONTAINS]->(op:Table)-[:REPLICATED_TO]->(rep:Table)` then follow downstream.

### Report full lineage
```cypher
MATCH (rpt:Report {name: 'Rack Margin Dashboard'})-[con:CONSUMES]->(sem:Table)
MATCH upPath = (sem)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (srv:Server)-[h:HOSTS]->(ds)
RETURN rpt, con, sem, upPath, op, rpl, ds, c1, srv, h
```

### Column-level lineage for a table
```cypher
MATCH (t:Table {qualifiedName: 'wholesale_core.Margin_Fact'})-[hc:HAS_COLUMN]->(col:Column)
OPTIONAL MATCH (col)-[df:DERIVED_FROM]->(srcCol:Column)
OPTIONAL MATCH (srcTable:Table)-[shc:HAS_COLUMN]->(srcCol)
RETURN t, hc, col, df, srcCol, shc, srcTable
```

### Is a column used in a report?

Reports do not link to Column nodes. Search the Power Query M code on `CONSUMES.expression` for the column name (case-sensitive):

```cypher
MATCH (rpt:Report)-[con:CONSUMES]->(t:Table {qualifiedName: 'sem_masterdata.TransactionType_vw'})
WHERE con.expression CONTAINS 'Timestamp'
RETURN rpt, con, t
```

### Business context hierarchy
```cypher
MATCH (ba:BusinessArea)-[hp:HAS_PRODUCT_LINE]->(dpl:DataProductLine)
      -[o:OWNS]->(cdd:CapabilityDataDomain)-[s:SUPPORTS]->(bp:BusinessProcess)
      -[bts:BELONGS_TO_STAGE]->(vs:ValueStreamStage)
RETURN ba, hp, dpl, o, cdd, s, bp, bts, vs
```

### Find the Data Analyst for a Semantic view
```cypher
MATCH (p:Person)-[hr:HAS_ROLE]->(ra:RoleAssignment)-[at:APPLIES_TO]->(t:Table)
WHERE t.qualifiedName = 'sem_wholesale.Rack_Price_Weekly_vw'
  AND ra.type = 'Data Analyst'
RETURN p, hr, ra, at, t
```

### All views assigned to a specific analyst
```cypher
MATCH (p:Person {name: 'Nkechi Morales'})-[hr:HAS_ROLE]->(ra:RoleAssignment)-[at:APPLIES_TO]->(t:Table)
RETURN p, hr, ra, at, t
```

### All reports consuming tables from a specific DataSystem
```cypher
MATCH (ds:DataSystem {name: 'Helios'})-[c1:CONTAINS]->(op:Table)
OPTIONAL MATCH (op)-[rpl:REPLICATED_TO]->(rep:Table)
OPTIONAL MATCH (sem:Table)-[:DERIVED_FROM*1..5]->(rep)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
  WHERE sem.layer = 'Semantic'
RETURN ds, c1, op, rpl, rep, sem, con, rpt
```

### Reports by business area

When filtering reports by a business area (e.g., "Wholesale Marketing reports," "how many reports in Pipelines & Terminals"), always traverse the business context hierarchy rather than matching schema name patterns.

```cypher
// Reports belonging to a specific business area
MATCH (ba:BusinessArea)-[:HAS_PRODUCT_LINE]->(dpl:DataProductLine)
      -[:OWNS]->(cdd:CapabilityDataDomain)<-[bt:BELONGS_TO]-(rpt:Report)
WHERE ba.name =~ '(?i).*wholesale.*marketing.*'
RETURN ba, dpl, cdd, bt, rpt
```

### Upstream lineage for a group of reports

When tracing upstream sources for a group of reports, use OPTIONAL MATCH for **every hop after the anchor**. Strict MATCH silently drops reports whose consumed views have no DERIVED_FROM chain.

```cypher
// Upstream sources for all Wholesale Marketing reports (preserves all 44 reports)
MATCH (ba:BusinessArea)-[:HAS_PRODUCT_LINE]->(dpl:DataProductLine)
      -[:OWNS]->(cdd:CapabilityDataDomain)<-[:BELONGS_TO]-(rpt:Report)
WHERE ba.name =~ '(?i).*wholesale.*marketing.*'
OPTIONAL MATCH (rpt)-[con:CONSUMES]->(sem:Table)
OPTIONAL MATCH upPath = (sem)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (srv:Server)-[h:HOSTS]->(ds)
RETURN rpt, con, sem, upPath, op, rpl, ds, c1, srv, h
```

### Master data domains

When the user asks about "master data," always use `MasterDataDomain` with `REALIZED_IN`. Do **not** confuse with `CapabilityDataDomain`.

```cypher
// All master data domains with full lineage
MATCH (mdd:MasterDataDomain)-[ri:REALIZED_IN]->(t:Table)
OPTIONAL MATCH upPath = (t)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (sem:Table)-[df:DERIVED_FROM]->(t)
  WHERE sem.layer = 'Semantic'
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
RETURN mdd, ri, t, upPath, upstream, op, rpl, ds, c1, sem, df, rpt, con
```

### Search by table or view name

When the user references a table or view by name (not qualifiedName), search at the **Table level**. Do not assume a DataSystem anchor.

```cypher
// Find any table with "Price_Batch" in its name and trace full lineage
MATCH (t:Table)
WHERE t.qualifiedName CONTAINS 'Price_Batch' OR t.name CONTAINS 'Price_Batch'
OPTIONAL MATCH upPath = (t)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (srv:Server)-[h:HOSTS]->(ds)
OPTIONAL MATCH (sem:Table)-[df:DERIVED_FROM*1..5]->(t)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
  WHERE sem.layer = 'Semantic'
RETURN srv, h, ds, c1, op, rpl, upstream, upPath, t, sem, df, rpt, con
```

### FlatFile lineage (alternate path)

Flat-file-sourced tables use `FlatFile` instead of `DataSystem`:

```cypher
MATCH (ff:FlatFile)-[c:CONTAINS]->(op:Table)
OPTIONAL MATCH (op)-[rpl:REPLICATED_TO]->(rep:Table)
OPTIONAL MATCH (slv:Table)-[df1:DERIVED_FROM]->(rep)
OPTIONAL MATCH (sem:Table)-[df2:DERIVED_FROM]->(slv)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
RETURN ff, op, rep, slv, sem, rpt, c, rpl, df1, df2, con
```

### Legacy refactoring lineage (alternate path)

Legacy tables carry the `:Legacy` label and use `REFACTORED_TO` instead of `DERIVED_FROM` for their first hop:

```cypher
MATCH (legacy:Table:Legacy)-[rt:REFACTORED_TO]->(idp:Table)
OPTIONAL MATCH (view:Table)-[df:DERIVED_FROM]->(idp)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(view)
RETURN legacy, rt, idp, view, rpt, df, con
```

### Synapse pipelines

`DataPipeline` nodes read Replica tables and load Gold tables:

```cypher
MATCH (sem:Table {qualifiedName: 'sem_wholesale.Price_Batch_Dim_vw'})-[df:DERIVED_FROM]->(gold:Table)
OPTIONAL MATCH (p:DataPipeline)-[ld:LOADS]->(gold)
OPTIONAL MATCH (p)-[rd:READS]->(rep:Table)
RETURN sem, df, gold, p, ld, rd, rep
```

### Alteryx-migrated Gold tables

Gold tables migrated from Alteryx Sandbox use `MIGRATED_FROM` to link back to the source DataSystem:

```cypher
MATCH (gold:Table)-[mf:MIGRATED_FROM]->(sb:DataSystem)
  WHERE sb.platform = 'Alteryx Sandbox'
OPTIONAL MATCH upPath = (gold)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (sem:Table)-[df:DERIVED_FROM]->(gold)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
RETURN gold, mf, sb, upPath, sem, rpt, df, con
```

### Data models for a capability domain or data system

A data model covers a **data system** through `BELONGS_TO` and a **capability domain** through `MODELS`:

```cypher
// All data models for a capability domain
MATCH (dm:DataModel)-[m:MODELS]->(cdd:CapabilityDataDomain)
WHERE cdd.name =~ '(?i).*Rack.*Pricing.*'
OPTIONAL MATCH (dm)-[bt:BELONGS_TO]->(ds:DataSystem)
RETURN dm, m, cdd, bt, ds
```

```cypher
// All data models that cover a specific data system
MATCH (dm:DataModel)-[bt:BELONGS_TO]->(ds:DataSystem {name: 'Helios'})
OPTIONAL MATCH (dm)-[m:MODELS]->(cdd:CapabilityDataDomain)
RETURN dm, bt, ds, m, cdd
```

### Session History & User Feedback
To explore user feedback, use `Message.feedback` (`'good'`, `'poor'`, or absent). "All feedback" means any rating:

```cypher
// All messages with feedback, good and poor, with their sessions
MATCH (s:Session)-[hm:HAS_MESSAGE]->(m:Message)
WHERE m.feedback IS NOT NULL
RETURN s, hm, m
ORDER BY m.timestamp DESC
```

```cypher
// Messages marked as "poor" feedback with their questions, answers, and comments
MATCH (s:Session)-[hm:HAS_MESSAGE]->(m:Message)
WHERE m.feedback = 'poor'
RETURN s, hm, m
ORDER BY m.timestamp DESC
```

### Power BI reports consuming Conformed Views with their connection queries

When asked about Power BI reports loading conformed database views and their exact background connection code/query, use the `expression` property on the `[:CONSUMES]` relationship to retrieve it:

```cypher
// Power BI reports loading Semantic conformed database views with their connection code/query
MATCH (rpt:Report)-[con:CONSUMES]->(view:Table)
WHERE view.layer = 'Semantic' AND con.expression IS NOT NULL
RETURN rpt.name AS `Report Name`, view.qualifiedName AS `Conformed View`, con.expression AS `Connection Query`
LIMIT 5
```

---

## 7. Important Gotchas

1. **Always use `OPTIONAL MATCH`** for hops beyond the anchor node. Strict `MATCH` drops entire rows when any hop is missing.

2. **Use `DERIVED_FROM*1..5`** instead of fixed 1-hop or 2-hop chains. Some paths are Gold → Replica (1 hop), others are Gold → Silver → Replica (2 hops), and some go deeper.

3. **Schema nodes often have `name: null`**. Use `qualifiedName` for display. Every Table node has `name`.

4. **`replica_files_*` tables** are Operational tables with **no DataSystem or Server** — they connect to FlatFile instead: `(:FlatFile)-[:CONTAINS]->(:Table {layer:'Operational'})`.

5. **`DataSystem -[:CONTAINS]-> Schema` does NOT exist**. DataSystem connects to Schema via `HOSTS` or `REPLICATED_TO`. Don't confuse with `Schema -[:CONTAINS]-> Table`.

6. **`MIGRATED_FROM` vs `MIGRATED_TO`**: Gold tables point outward via `MIGRATED_FROM` to the sandbox DataSystem. `MIGRATED_TO` goes from DataSystem to Table.

7. **`Table.layer` valid values**: `Operational`, `Replica`, `Silver`, `Gold`, `Semantic`. There is **no** `Legacy` layer value — legacy provenance is tracked via the `:Legacy` label.

8. **`RETURN *` with `UNWIND`** can cause cartesian explosion. Prefer explicit `RETURN` with named variables.

9. **Report.reportKey is the merge key** — it is `webUrl` when that value is non-empty, otherwise `name:` plus `name`. `name` is the display property. A question that names a report matches `rpt.name`, and that match can return more than one report. Reports have no `qualifiedName`.

10. **Server.serverName** — not `Server.name`. The key property is `serverName`.

11. **`:Legacy` is a label, not a layer** — Query pre-standard schema objects with `MATCH (t:Table:Legacy)` or `MATCH (s:Schema:Legacy)`. Their `layer` property holds the correct medallion value (Silver).

12. **`Table.layer` must be derived from the schema name or object prefix** — never guess or leave blank:
    | Schema / Prefix | layer value |
    |---|---|
    | `udm_core.*`, `mdm_core.*` | `Silver` |
    | `replica*` | `Replica` |
    | `sem_<business_area>.*` (e.g. `sem_wholesale.*`, `sem_masterdata.*`) | `Semantic` |
    | `<business_area>_core.*` (e.g. `wholesale_core.*`) | `Gold` |
    | `dwh*`, `dwh_core.*`, `persistence.*`, `staging.*` | `Silver` (also carry `:Legacy` label) |
    **Gold disambiguation**: any `*_core` schema is Gold *except* `udm_core`, `mdm_core` (Silver) and `dwh_core` (Legacy Silver).

13. **Reports belong to business areas via the hierarchy, not by schema name.** To find all reports in a business area, traverse `BusinessArea -> HAS_PRODUCT_LINE -> DataProductLine -> OWNS -> CapabilityDataDomain <- BELONGS_TO <- Report`. Do not filter by schema name patterns (e.g., `sem_wholesale.*`) as this misses legacy and non-standard schemas.

14. **`MasterDataDomain` is not the same as `CapabilityDataDomain`.** MasterDataDomain connects to tables via `REALIZED_IN`. CapabilityDataDomain connects to reports and conformed tables via `BELONGS_TO` and to business processes via `SUPPORTS`. When the user mentions "master data," always use MasterDataDomain.

15. **Search by table name, not DataSystem name.** When the user references a table by name (e.g., "margin table"), anchor the query on `Table` using `WHERE t.qualifiedName CONTAINS '...' OR t.name CONTAINS '...'`. Only anchor on `DataSystem` when the user explicitly names a data system (e.g., "from the Helios system").

16. **Defensive String Matching (Delimiter Guard)** — Users type names with different spacing and delimiters (e.g., the workspace `"LSC - Wholesale Marketing"` may be typed as `"LSC-Wholesale Marketing"`). When searching or filtering by string fields like `workspaceName`, `name`, or `qualifiedName`, always use case-insensitive regex `=~ '(?i).*<value>.*'` or `CONTAINS` instead of an exact match (`=`). Furthermore, **always replace spaces, hyphens, and dashes in user-provided terms with wildcards (`.*`) in the regex** (e.g. searching for `"LSC-Wholesale Marketing"` should generate `=~ '(?i).*LSC.*Wholesale.*Marketing.*'` instead of a literal hyphen match) to guarantee clean matches and prevent empty results.

17. **CapabilityDataDomain lineage queries (Bidirectional & Direct Table Fallback)** —
    - **Tables for a Domain:** When exploring lineage mapped to a `CapabilityDataDomain` (e.g. `"tables that are part of Terminal Ops"`), do **not** anchor strictly on `Report` nodes (e.g. `(rpt:Report)-[:BELONGS_TO]->(cdd)`), because some capability domains primarily contain conformed tables without Power BI front-end reports associated with them. Always query conformed tables directly: `MATCH (t:Table)-[r:BELONGS_TO]->(cdd:CapabilityDataDomain {name: 'Terminal Ops'})` and walk their upstream Medallion lineage paths (`-[:DERIVED_FROM*1..5]->`), ensuring conformed lineage is never hidden.
    - **Domains for a Table:** When asked which capability data domains are linked to a specific Table (or view), match the Table and traverse to the `CapabilityDataDomain` node. Since conformed tables are linked directly to domains via `BELONGS_TO`, query: `MATCH (t:Table {qualifiedName: 'mdm_core.Helios_Credit_Memo_Snapshot_Dim'})-[r:BELONGS_TO]->(cdd:CapabilityDataDomain)`. If that direct relationship does not exist, traverse optionally through downstream semantic views and their consuming reports to retrieve the domain links: `OPTIONAL MATCH (t)<-[:DERIVED_FROM*1..5]-(sem:Table)<-[:CONSUMES]-(rpt:Report)-[:BELONGS_TO]->(cdd:CapabilityDataDomain)`. Make sure to return the Table, the CapabilityDataDomain, and the connecting edges or path variables (e.g. `RETURN t, r, cdd`) so that a fully conformed visual graph is rendered in the dashboard.

18. **Data models "cover" a data system via `BELONGS_TO`.** `(dm:DataModel)-[:BELONGS_TO]->(ds:DataSystem {name: 'Helios'})`. `MODELS` points at a CapabilityDataDomain, never a DataSystem.

19. **"All feedback" means any rating.** Filter `m.feedback IS NOT NULL`. Add `= 'poor'` or `= 'good'` only when the user names a rating.

---

## 8. Constraints & Indexes

Every primary label has a node key constraint named `<Label>_constraint` on its key property (see table in section 3). There are no fulltext or standalone range indexes.

- **Node keys** `qualifiedName` on Table, Column, and Schema; `reportKey` on Report; `serverName` on Server; `type` on Policy; `(type, scope)` on RoleAssignment; `id` on Session and Message; `name` on every other primary label.
- **Booleans** `DataSystem.isSoxRelevant`, `DataSystem.isRecordActive`, and `Policy.isSoxRelevant` are `true`, `false`, or null. Filter with `ds.isSoxRelevant = true`. A compare to `'Yes'` matches nothing.

---

## 9. Graph Statistics Summary

- **26 node labels** (22 primary labels plus the `Dimension`, `Fact`, `View`, and `Legacy` role labels)
- **29 relationship types**
- **~44.9K nodes** total (dominated by Column: 31.0K, Table: 7.4K, Report: 2.6K, RoleAssignment: 2.3K)
- **~78.5K relationships** total (dominated by HAS_COLUMN: 31.0K, DERIVED_FROM: 15.8K, CONSUMES: 13.1K, CONTAINS: 9.6K)
