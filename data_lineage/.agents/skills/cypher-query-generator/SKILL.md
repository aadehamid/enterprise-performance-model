---
name: cypher-query-generator
description: >
  Generate Cypher queries for the Lagos Refining & Supply Company (LSC) Data Lineage
  Knowledge Graph in Neo4j. Use when the user asks to query, explore, or
  visualize data lineage, table relationships, column mappings, report
  consumption, master data domains, business context hierarchy, data products,
  data pipelines, data models, server infrastructure, legacy table refactoring,
  or portal chat feedback. Handles requests like "show me the full lineage of
  a table," "which reports consume this view," "trace data from source to semantic
  layer," "find the analyst assigned to a view," "which servers host this data
  system," "is this column used in a report," or "which data models cover this
  data system" — even if the user doesn't mention Cypher or Neo4j explicitly.
  Do NOT use for conceptual or explanatory questions (e.g., "what is the
  difference between Silver and Gold layers?"), for creating diagrams or
  documentation, or for writing SQL, Python, or other non-Cypher code.
license: Proprietary
compatibility: >
  Designed for VS Code with GitHub Copilot Agent Mode.
  Also compatible with Cursor, Windsurf, Antigravity, and other
  Agent Skills-compatible clients.
metadata:
  author: Lagos Refining & Supply Company Data & Analytics Team
  version: "1.1"
---

## 1. Activation Confirmation

When this skill is first activated in a session, briefly confirm to the user:

> **Data Lineage Knowledge Graph skill loaded.** I can generate Cypher queries for:
> - Full lineage (Server → DataSystem → Operational → Replica → Silver → Gold → Semantic → Report)
> - Column-level lineage and report column usage
> - Report consumption
> - Data analyst / role lookups
> - Business context hierarchy
> - Legacy refactoring lineage
> - FlatFile, Synapse pipeline, and Alteryx migration paths
> - Data model (ER Studio) coverage by capability domain or data system
> - Portal chat history and feedback
>
> Describe what you'd like to explore and I'll generate a paste-ready Cypher query for Neo4j Browser.

After the first activation, skip this confirmation and respond directly with the Cypher query.

## 2. Role & Output Rules

You generate **Cypher queries** that the user will **paste into Neo4j Browser** to visualize and interact with the graph. Follow these rules for every query:

- **Do NOT include `:use lsc`** (or any `:use` line) in queries returned for the user to paste into Neo4j Browser. The user is already connected to the correct database. Including it adds an unnecessary step.
- **Prefer graph visualization** — return **nodes and relationships** (e.g., `RETURN n, r, m`) so Neo4j Browser renders a visual graph. The primary value of the knowledge graph is seeing connections visually, which helps users discover unexpected relationships. However, if the user's question clearly calls for a **count**, **list**, or **tabular summary** (e.g., "how many reports...?", "list all table names in...", "count of..."), return the appropriate scalar, aggregation, or property projection instead. When in doubt, return the graph visualization and mention that the user can add `count()` or property projections if they need a summary.
- **Alias all relationships** — Neo4j Browser needs named relationship variables (e.g., `-[c1:CONTAINS]->` not `-[:CONTAINS]->`) to render clickable, labeled edges. Without aliases, edges appear but can't be inspected or filtered in the UI.
- Use **`OPTIONAL MATCH`** for all hops beyond the anchor node — strict `MATCH` drops entire rows when any hop is missing, which silently hides data and makes the user think tables or reports don't exist when they actually do.
- Use **`DERIVED_FROM*1..5`** for variable-length lineage traversal — lineage paths vary in depth (Gold->Replica is 1 hop, Gold->Silver->Replica is 2, and some go deeper). Fixed-hop chains miss tables at unexpected depths.
- **Default to full lineage** — users asking about lineage almost always want to see the complete picture, even if their phrasing only mentions one direction (e.g., "where does X come from"). Showing partial lineage leads to follow-up questions and wasted time. Show the **complete chain** (Server -> DataSystem -> Operational -> Replica -> Silver -> Gold -> Semantic -> Report) unless the user explicitly asks for a partial view (e.g., "just show upstream" or "only show the silver sources").

## 3. Data Flow (Layer Order)

Tables flow through these layers (stored in `Table.layer`):

```
Operational → Replica → Silver → Gold → Semantic
```

- **Operational** — source tables inside external systems (Helios, RightAngle, SAP_S4, Salesforce, LIMS_<site>, BlendPlan_<site>, etc.)
- **Replica** — 1:1 copy of the operational table into the LSC Data Platform (IDP), the enterprise data platform for Lagos Refining & Supply Company on Azure Synapse
- **Silver** — cleaned/conformed dimensions and facts (`mdm_core.*`, `udm_core.*`)
- **Gold** — business-specific aggregated tables. The fully qualified name follows `<business_area>_core.<table_name>`. For example, in `wholesale_core.Margin_Fact` the business area is Wholesale and `Margin_Fact` is the table name. Gold schemas: `wholesale_core`, `refining_core`, `renewables_core`, `trading_core`, `logistics_core`.
- **Semantic** — views consumed by reports (`sem_wholesale.*`, `sem_masterdata.*`, and the `sem_<area>_kpi`, `_ops`, `_planning`, `_pricing` variants)

Pre-standard schemas (`dwh`, `dwh_core`, `dwh_refining`, `dwh_finance`, `dwh_quality`, `persistence`, `staging`) carry a **`:Legacy` label**. Their `layer` property holds the correct medallion layer (Silver). Query legacy items via `MATCH (t:Table:Legacy)`.

## 4. Naming Conventions

`Table.qualifiedName` follows the pattern `schema.tableName`:

| Prefix | Layer | Example |
|---|---|---|
| `<DataSystem>.*` | Operational | `Helios.MarginDetail` |
| `replica_<datasystem>.*` | Replica | `replica_helios.Margin_Detail` |
| `mdm_core.*` | Silver (dim) | `mdm_core.RightAngle_Transaction_Type_Dim` |
| `udm_core.*` | Silver (fact) | `udm_core.Helios_Margin_Fact` |
| `<business_area>_core.*` | Gold | `wholesale_core.Margin_Fact` |
| `sem_<business_area>.*` | Semantic | `sem_wholesale.Margin_vw` |
| `dwh*.*`, `persistence.*`, `staging.*` | Silver + `:Legacy` | `dwh.LSC_Product_Master` |

**Gold disambiguation**: any `*_core` schema is Gold *except* `udm_core` and `mdm_core`, which are Silver. `dwh_core` is Legacy Silver.

`Column.qualifiedName` = `schema.tableName.columnName`

## 5. Common Query Patterns

### Full lineage (primary and default pattern)

When asked for "full lineage" **or any lineage/tracing question that does not explicitly limit scope**, show the complete chain: Server -> DataSystem -> Operational -> Replica -> Silver -> Gold -> Semantic -> Report -> Owner.

```cypher
// Full lineage anchored on a Semantic view
MATCH (sem:Table {qualifiedName: 'sem_wholesale.Margin_vw'})
MATCH upPath = (sem)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (srv:Server)-[h:HOSTS]->(ds)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
RETURN sem, upPath, op, ds, srv, rpt, rpl, c1, h, con
```

To adapt: change the `qualifiedName`, or anchor on a Report (`MATCH (rpt:Report {name: '...'})-[con:CONSUMES]->(sem:Table)`) or DataSystem (`MATCH (ds:DataSystem {name: '...'})-[:CONTAINS]->(op:Table)`).


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

Full lineage with Data Analyst owner for a Semantic view

The below cypher query shows the complete data chain from Server → DataSystem → Operational → Replica → Silver/Gold → Semantic view, plus all Reports consuming the view and the assigned Data Analyst.

```cypher
MATCH (sem:Table {qualifiedName: 'sem_wholesale.Rack_Price_Weekly_vw'})
MATCH upPath = (sem)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (op:Table)-[rpl:REPLICATED_TO]->(upstream)
  WHERE upstream.layer = 'Replica'
OPTIONAL MATCH (ds:DataSystem)-[c1:CONTAINS]->(op)
OPTIONAL MATCH (srv:Server)-[h:HOSTS]->(ds)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
OPTIONAL MATCH (owner:Person)-[hr:HAS_ROLE]->(ra:RoleAssignment)-[at:APPLIES_TO]->(sem)
  WHERE ra.type = 'Data Analyst'
RETURN sem, upPath, op, ds, srv, rpt, rpl, c1, h, con, owner, hr, ra, at

```

### Column-level lineage

```cypher
MATCH (t:Table {qualifiedName: 'wholesale_core.Margin_Fact'})-[hc:HAS_COLUMN]->(col:Column)
OPTIONAL MATCH (col)-[df:DERIVED_FROM]->(srcCol:Column)
OPTIONAL MATCH (srcTable:Table)-[shc:HAS_COLUMN]->(srcCol)
RETURN t, hc, col, df, srcCol, shc, srcTable
```

### Is a column used in a report?

Reports do not link to Column nodes. A report uses a column when the column name appears in the Power Query M code stored on `CONSUMES.expression`. Search that property with `CONTAINS`. It is case-sensitive, so keep the column name's casing (e.g. `Timestamp`, `Margin_Amount`).

```cypher
// Reports that use the Timestamp column of a specific view
MATCH (rpt:Report)-[con:CONSUMES]->(t:Table {qualifiedName: 'sem_masterdata.TransactionType_vw'})
WHERE con.expression CONTAINS 'Timestamp'
RETURN rpt, con, t
```

```cypher
// Reports that use a column in any table or view
MATCH (rpt:Report)-[con:CONSUMES]->(t:Table)
WHERE con.expression CONTAINS 'Margin_Amount'
RETURN rpt, con, t
```

To show which reports consume the view but do **not** use the column, filter with `WHERE NOT con.expression CONTAINS '...'`.

### Data analyst lookup

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

### Reports consuming tables from a DataSystem

```cypher
MATCH (ds:DataSystem {name: 'Helios'})-[c1:CONTAINS]->(op:Table)
OPTIONAL MATCH (op)-[rpl:REPLICATED_TO]->(rep:Table)
OPTIONAL MATCH (sem:Table)-[:DERIVED_FROM*1..5]->(rep)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
  WHERE sem.layer = 'Semantic'
RETURN ds, c1, op, rpl, rep, sem, con, rpt
```

### Reports by business area

When filtering reports by a business area (e.g., "Wholesale Marketing reports," "how many reports in Pipelines & Terminals"), always traverse the business context hierarchy rather than matching schema name patterns. Schema names can miss legacy schemas and non-standard naming.

```cypher
// Reports belonging to a specific business area
MATCH (ba:BusinessArea)-[:HAS_PRODUCT_LINE]->(dpl:DataProductLine)
      -[:OWNS]->(cdd:CapabilityDataDomain)<-[bt:BELONGS_TO]-(rpt:Report)
WHERE ba.name =~ '(?i).*wholesale.*marketing.*'
RETURN ba, dpl, cdd, bt, rpt
```

### Upstream lineage for a group of reports

When tracing upstream sources for a group of reports (e.g., "all Wholesale Marketing reports"), use OPTIONAL MATCH for **every hop after the anchor**. Strict MATCH silently drops reports whose consumed views have no DERIVED_FROM chain, producing incomplete results.

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

When the user asks about "master data," "master data domains," or which tables serve master data, always use the `MasterDataDomain` node with the `REALIZED_IN` relationship. Do **not** confuse `MasterDataDomain` with `CapabilityDataDomain` — they are different node types.

```cypher
// All master data domains and the tables they are realized in, with full lineage
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

To filter by layer: add `WHERE t.layer = 'Gold'` after the first MATCH. To pick one domain: `MATCH (mdd:MasterDataDomain {name: 'Product'})`.

### Search by table or view name

When the user references a table or view by name (not by qualifiedName), search for it at the **Table level** using a CONTAINS filter. Do not assume a DataSystem anchor — this misses tables loaded via FlatFile, migration, or other paths. Only anchor on `DataSystem` when the user explicitly says "from the Helios system" or "from the RightAngle data system."

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

### Business context hierarchy

```cypher
MATCH (ba:BusinessArea)-[hp:HAS_PRODUCT_LINE]->(dpl:DataProductLine)
      -[o:OWNS]->(cdd:CapabilityDataDomain)-[s:SUPPORTS]->(bp:BusinessProcess)
      -[bts:BELONGS_TO_STAGE]->(vs:ValueStreamStage)
RETURN ba, hp, dpl, o, cdd, s, bp, bts, vs
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

Legacy tables carry the `:Legacy` label and use `REFACTORED_TO`:

```cypher
MATCH (legacy:Table:Legacy)-[rt:REFACTORED_TO]->(idp:Table)
OPTIONAL MATCH (view:Table)-[df:DERIVED_FROM]->(idp)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(view)
RETURN legacy, rt, idp, view, rpt, df, con
```

### Synapse pipelines

`DataPipeline` nodes read Replica tables (`READS`) and load Gold tables (`LOADS`). Use them for "how is X loaded" or "which pipeline feeds X":

```cypher
// Pipeline and Gold table behind a Semantic view
MATCH (sem:Table {qualifiedName: 'sem_wholesale.Price_Batch_Dim_vw'})-[df:DERIVED_FROM]->(gold:Table)
OPTIONAL MATCH (p:DataPipeline)-[ld:LOADS]->(gold)
OPTIONAL MATCH (p)-[rd:READS]->(rep:Table)
RETURN sem, df, gold, p, ld, rd, rep
```

### Alteryx-migrated Gold tables

```cypher
MATCH (gold:Table)-[mf:MIGRATED_FROM]->(sb:DataSystem)
  WHERE sb.platform = 'Alteryx Sandbox'
OPTIONAL MATCH upPath = (gold)-[:DERIVED_FROM*1..5]->(upstream:Table)
OPTIONAL MATCH (sem:Table)-[df:DERIVED_FROM]->(gold)
OPTIONAL MATCH (rpt:Report)-[con:CONSUMES]->(sem)
RETURN gold, mf, sb, upPath, sem, rpt, df, con
```

### Session History & User Feedback

Portal chat turns are `Message` nodes. Each `Session` links to its messages with `HAS_MESSAGE`, to its latest message with `LAST_MESSAGE`, and messages chain in order with `NEXT`. `Message.feedback` is `'good'`, `'poor'`, or absent; `Message.feedbackComment` holds the optional comment.

When the user asks to see **all feedback** (no rating named), return every message that has any feedback, with its session, as a graph. Do **not** filter to `'poor'`.

```cypher
// All feedback, good and poor, with the session each message belongs to
MATCH (s:Session)-[hm:HAS_MESSAGE]->(m:Message)
WHERE m.feedback IS NOT NULL
RETURN s, hm, m
ORDER BY m.timestamp DESC
```

When the user asks for poor ratings, bad answers, or downvotes, filter on `'poor'` (use `'good'` for good ratings):

```cypher
MATCH (s:Session)-[hm:HAS_MESSAGE]->(m:Message)
WHERE m.feedback = 'poor'
RETURN s, hm, m
ORDER BY m.timestamp DESC
```

To show whole conversations in order, follow `NEXT` between the session's messages:

```cypher
// Full conversations of every session that received poor feedback
MATCH (s:Session)-[hm:HAS_MESSAGE]->(m:Message)
WHERE EXISTS { (s)-[:HAS_MESSAGE]->(:Message {feedback: 'poor'}) }
OPTIONAL MATCH (m)-[nx:NEXT]->(m2:Message)
OPTIONAL MATCH (s)-[lm:LAST_MESSAGE]->(last:Message)
RETURN s, hm, m, nx, m2, lm, last
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

### Data models for a capability domain or data system

A data model **covers a data system** (or is "for" / "of" a data system) through `BELONGS_TO`: `(dm:DataModel)-[:BELONGS_TO]->(ds:DataSystem)`. A data model covers a **capability domain** through `MODELS`. Do not use `MODELS` for a data system question.

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

```cypher
// Overview: all data models with their domains and systems
MATCH (dm:DataModel)
OPTIONAL MATCH (dm)-[m:MODELS]->(cdd:CapabilityDataDomain)
OPTIONAL MATCH (dm)-[bt:BELONGS_TO]->(ds:DataSystem)
RETURN dm.name AS Model, dm.modelType AS Type,
       cdd.name AS CapabilityDomain, ds.name AS DataSystem
ORDER BY cdd.name, dm.name
```

## 6. Gotchas

1. **Always use `OPTIONAL MATCH`** for hops beyond the anchor node — strict `MATCH` silently drops entire rows when any hop is missing, making the user think data doesn't exist.
2. **Use `DERIVED_FROM*1..5`** instead of fixed-hop chains — paths vary in depth (Gold->Replica is 1 hop, Gold->Silver->Replica is 2 hops, some go deeper). Fixed-hop chains miss tables at unexpected depths.
3. **Schema nodes often have `name: null`** — use `qualifiedName` for display because about half of the Schema nodes have no `name` property.
4. **`replica_files_*` tables** connect to `FlatFile` not `DataSystem` — these are flat-file ingestions that bypass the standard DataSystem path: `(:FlatFile {name: 'LSC Commercial Files'})-[:CONTAINS]->(:Table {layer:'Operational'})`.
5. **`DataSystem -[:CONTAINS]-> Schema` does NOT exist** — this is a common mistake. DataSystem connects to Tables directly via `CONTAINS`, and to Schemas via `HOSTS` or `REPLICATED_TO`. Schema connects to its Tables via `CONTAINS`.
6. **`MIGRATED_FROM` vs `MIGRATED_TO`** — the direction is counterintuitive. Gold tables point outward via `MIGRATED_FROM` to the sandbox ("I was migrated from there"). `MIGRATED_TO` goes from DataSystem to Table.
7. **`Table.layer` valid values**: `Operational`, `Replica`, `Silver`, `Gold`, `Semantic`. There is **no** `Legacy` layer value — using `WHERE t.layer = 'Legacy'` will return zero results.
8. **`RETURN *` with `UNWIND`** causes cartesian explosion — use explicit `RETURN` with named variables to avoid multiplying rows unexpectedly.
9. **Report properties** — The merge key is `reportKey`. It is `webUrl` when that value is non-empty, otherwise `name:` plus `name`. `name` is the display property and two reports may share it, so a name match can return more than one node. Reports have no `qualifiedName`. **`Report` nodes carry a conformed `workspaceName` property** (e.g., `"LSC - Wholesale Marketing"`) representing their Power BI workspace. Always query or aggregate by `rpt.workspaceName` directly when the user asks about workspaces, rather than trying to split the report name.
10. **Server.serverName** — not `Server.name`. The key property is `serverName`, so `WHERE s.name = '...'` will return nothing.
11. **`:Legacy` is a label, not a layer** — query with `MATCH (t:Table:Legacy)`. The `layer` property on legacy tables holds their actual medallion value (Silver), not "Legacy".
12. **Layer derivation from schema prefix**:
    - `udm_core.*`, `mdm_core.*` -> `Silver`
    - `replica*` -> `Replica`
    - `sem_<area>.*` -> `Semantic`
    - `<area>_core.*` -> `Gold` (except `udm_core`, `mdm_core` which are Silver, and `dwh_core` which is Legacy Silver)
    - `dwh*`, `persistence.*`, `staging.*` -> `Silver` + `:Legacy`
13. **Search by table name, not DataSystem name.** When the user references a table by name (e.g., "margin table"), anchor the query on `Table` using `WHERE t.qualifiedName CONTAINS '...' OR t.name CONTAINS '...'`. Only anchor on `DataSystem` when the user explicitly names a data system (e.g., "from the Helios system").
14. **Defensive String Matching (Delimiter Guard)** — Users type names with different spacing and delimiters (e.g., the workspace `"LSC - Wholesale Marketing"` may be typed as `"LSC-Wholesale Marketing"`). When searching or filtering by string fields like `workspaceName`, `name`, or `qualifiedName`, always use case-insensitive regex `=~ '(?i).*<value>.*'` or `CONTAINS` instead of an exact match (`=`). Furthermore, **always replace spaces, hyphens, and dashes in user-provided terms with wildcards (`.*`) in the regex** (e.g. searching for `"LSC-Wholesale Marketing"` should generate `=~ '(?i).*LSC.*Wholesale.*Marketing.*'` instead of a literal hyphen match) to guarantee clean matches and prevent empty results.
15. **Power BI Connection Queries & M-Query logic** — The exact connection code/query or background loading logic that a Power BI report uses to load a conformed database view is stored as the `expression` property on the `[:CONSUMES]` relationship (e.g. `(rpt:Report)-[con:CONSUMES]->(view:Table)` where `con.expression` holds the Power Query M-expression). Do **not** look for it on `Report` properties (like `connectionCodeOrQuery`) or `Table` properties (like `viewDefinition`). Always retrieve it from `con.expression`. The same property answers "is column X used in a report" (see the pattern above).
16. **CapabilityDataDomain lineage queries (Bidirectional & Direct Table Fallback)** —
    - **Tables for a Domain:** When exploring lineage mapped to a `CapabilityDataDomain` (e.g. `"tables that are part of Terminal Ops"`), do **not** anchor strictly on `Report` nodes (e.g. `(rpt:Report)-[:BELONGS_TO]->(cdd)`), because some capability domains primarily contain conformed tables without Power BI front-end reports associated with them. Always query conformed tables directly: `MATCH (t:Table)-[r:BELONGS_TO]->(cdd:CapabilityDataDomain {name: 'Terminal Ops'})` and walk their upstream Medallion lineage paths (`-[:DERIVED_FROM*1..5]->`), ensuring conformed lineage is never hidden.
    - **Domains for a Table:** When asked which capability data domains are linked to a specific Table (or view), match the Table and traverse to the `CapabilityDataDomain` node. Since conformed tables are linked directly to domains via `BELONGS_TO`, query: `MATCH (t:Table {qualifiedName: 'mdm_core.Helios_Credit_Memo_Snapshot_Dim'})-[r:BELONGS_TO]->(cdd:CapabilityDataDomain)`. If that direct relationship does not exist, traverse optionally through downstream semantic views and their consuming reports to retrieve the domain links: `OPTIONAL MATCH (t)<-[:DERIVED_FROM*1..5]-(sem:Table)<-[:CONSUMES]-(rpt:Report)-[:BELONGS_TO]->(cdd:CapabilityDataDomain)`. Make sure to return the Table, the CapabilityDataDomain, and the connecting edges or path variables (e.g. `RETURN t, r, cdd`) so that a fully conformed visual graph is rendered in the dashboard.
17. **SOX and record flags are booleans.** `DataSystem.isSoxRelevant`, `DataSystem.isRecordActive`, and `Policy.isSoxRelevant` are `true`, `false`, or null. Filter with `WHERE ds.isSoxRelevant = true`. Comparing them to `'Yes'` or `'Y'` returns nothing.
18. **"All feedback" means any rating.** `WHERE m.feedback IS NOT NULL` returns good and poor feedback. Only add `= 'poor'` or `= 'good'` when the user names a rating.


## 7. Reference Files

For additional details beyond what's covered above, read these on-demand:

- **[Full node/relationship catalog](references/graph_schema.md)** — all node labels with counts, properties, and complete relationship patterns with source→target and edge counts.
- **[Project overview](references/project_overview.md)** — how the LSC catalog is generated and loaded, planted example paths, canonicalization rules, known gaps, and current graph counts.
- **[Cypher syntax traps](references/cypher_syntax_traps.md)** — invalid forms LLMs often write (SQL-isms, Cypher 25-only clauses on this Cypher 5 database) and their working equivalents. Check every query against it.

## 8. Environment Setup

### Python Environment

Use this virtual environment to run any Python scripts (e.g., `scripts/validate_cypher.py`):

**Default path:**
```
<project root>\.venv
```

**Activation:**
```powershell
.venv\Scripts\Activate.ps1   # from the project root
```

> **IMPORTANT** - When running python scripts, always use the `.venv` in the root of the project as the virtual environment.

> **If the default venv path does not exist** (e.g., different user or machine), ask the user for their Python environment path before running scripts. The venv must have `data-lineage-kg` and its dependencies installed.

### Neo4j Credentials

The graph database connection is configured via a `.env` file:

**Default path:**
```
<project root>\neo4j_instance_credentials.env
```

This file contains `NEO4J_URL`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`. **Do not copy this file into the skill folder** — it contains credentials and should stay outside version-controlled directories.

> **If the default .env path does not exist**, ask the user for the location of their Neo4j credentials file.

### Neo4j Database

The target database is the one named by `NEO4J_DATABASE`, `lsc` for the LSC catalog. When connecting **programmatically** via `Neo4jLoader`, pass it as the database name (`Neo4jLoader(database='lsc')`) or set it in the `.env` file. **Do not** include `:use lsc` in Cypher queries returned to the user for Neo4j Browser — the user is already connected to the correct database and this line would require an extra removal step.

The `Neo4jLoader` class is **already installed** in the project virtual environment — no installation step is needed. Use it to test Cypher queries against the live graph before presenting them to the user.

**When to validate:**
1. **Skip validation** if the query is a simple, straightforward application of the patterns documented above (e.g., standard full lineage, direct lookups).
2. **Perform validation** if the query is complex, involves multiple non-standard joins, or if the user's request is ambiguous.
3. If the request is ambiguous, always ask the user for clarification. While waiting or if you want to test an assumption, write a quick Python script to test the query structure.

**How to validate:**
Write and execute a temporary Python script in the workspace (e.g., `test_query.py`):

```python
from neo4j_loader import Neo4jLoader

# Point to the root .env file (run from the project root)
env_path = "neo4j_instance_credentials.env"

loader = Neo4jLoader(env_path=env_path, database="lsc")

query = """
MATCH (n:Table) RETURN n LIMIT 5
"""

try:
    results = loader.run_query(query)
    print(f"Success! Returned {len(results)} records.")
    # Check if results are empty when they shouldn't be
    if not results:
        print("Warning: Query succeeded but returned 0 records.")
except Exception as e:
    print(f"Error: {e}")
finally:
    loader.close()
```
