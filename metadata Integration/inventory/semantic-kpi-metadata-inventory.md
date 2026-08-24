# Stage A - Semantic / KPI metadata inventory (Demo 2 only)

**ID:** EPM-STAGE-A-SEMANTIC-KPI-INVENTORY  
**Status:** Draft evidence. Not a catalog. Not process authority. Not Stage B.  
**Pin:** `aadehamid/enterprise-performance-model` `814cb79d2b79b51210d4e21170f4579c1940b891`  
**Scope:** `demos/o2c-unbilled-databricks-free-cv-map/o2c-unbilled-databricks-free/`  
**Extracted:** 2026-08-23 19:58 CT  
**Out of scope:** learner folder, Track A, MetricFlow/dbt, `models/marts/schema.yml` (phantom), joined demos.

Read-only. Names, formulas, and classifications are copied from the files. Nothing was rewritten.

## Vocabulary (do not collide with the catalog enum)

| Kind | Allowed values |
|---|---|
| claim_label | fact / candidate / unresolved |
| classification | named_kpi / measure / population_fact / interchange_projection / meaning_term / catalog_table / published_cut / catalog_lifecycle_helper |
| mapping_status | recorded / cited / not_applicable / unresolved |

`proposed | approved | drifted | archived` is **catalog_status** on `dim_kpi_metadata` only. It is never used as classification or mapping_status. mapping_status is never `approved`.

## Authority (copied from these files, not invented)

| Concern | SoT in these files |
|---|---|
| Compile | Databricks Unity Catalog Metric Views (`sql/03_metric_view.sql` and sibling MV SQL) |
| Store catalog | `dim_kpi_metadata` (`sql/05_store.sql`, `sql/08_catalog_status.sql`) |
| Ontology | Turtle in git (`ontology/o2c-meaning.ttl`). Fuseki is not. |
| Gold | Published cut from `MEASURE()`. Not re-approve. |
| Ossie | 0.1.1 projection. Not compile SoT. |

### Current governance (not pinned)

Process authority is `business_architecture/business_process/` and `business_architecture/schema/` only. Domain folder is draft context. That lock is PRs #6/#7/#9 on current main. It is not a SHA in this manifest. Do not cite those folders as pinned evidence.

## Source artifacts

| File | Blob SHA | Size |
|---|---|---|
| sql/03_metric_view.sql | efe32788b6c758ef8ffe19cc38ad27e0d702cdd4 | 2657 |
| sql/05_store.sql | 854ca5a22fa908380884c467f32b4eaa55dda4db | 10690 |
| sql/08_catalog_status.sql | d9652d440f773f65e5953d8b9821232c2f9b8ba1 | 1038 |
| sql/02_facts.sql | a6cc9e16f4a398413c264f5e6a8b29b2fc4a2d5f | 4268 |
| sql/06_complex_metric.sql | 766f8d79e6e4cf462d8311680b66dfc05d28dab5 | 9836 |
| sql/07_temp_adjusted.sql | f5d8db8b74f69ec1dd06a88b0ba012aeee5878ef | 10075 |
| osi/unbilled.ossie.yaml | 2e889441d9c8b5480b305d44ef51140077fa19d5 | 6280 |
| ontology/o2c-meaning.ttl | 6ce06388b5434b0ff2d68ff2381c85fb3a2c5713 | 8591 |

## Rows

### POP-FCT-UNBILLED — fact / population_fact / recorded

`sql/02_facts.sql` `a6cc9e16…`. Table `fct_unbilled`. Ticket grain. `unbilled_usd = gallons_net * contract_price_usd`. Gate: delivered, no posted invoice as of 2026-08-01, quality-hold excluded (status ≠ delivered). Compiler source. Not gold. File comment: 12 tickets, $179,934.00.

### MV-UNBILLED-USD — fact / measure / recorded

`sql/03_metric_view.sql` `efe32788…`. View `unbilled_usd`. YAML 0.1. `SUM(source.unbilled_usd)`, `COUNT(1)`. Fields: payer, sold_to, site, site_name, as_of, delivery_date, product. Source: `fct_unbilled`. Compile SoT. `MEASURE()` only.

### KPI-O2C-UNBILLED-USD — fact / named_kpi / recorded

`sql/05_store.sql` `854ca5a2…`. File first-insert literal is `approved` `WHERE NOT EXISTS`. Live warehouse state was not re-read this pass. Do not un-approve a live row from this inventory. `catalog_status` is not set (not a live observed enum). Pointer `unbilled_usd` → `workspace.o2c_unbilled.unbilled_usd`. IRI `#UnbilledState`. Owner Revenue Accounting / Order-to-Cash. Grain enterprise \| payer \| sold_to \| site. `definition_hash` column exists; first-time INSERT omits the hash (Python fills). Never `INSERT` approved over drifted\|proposed\|archived. Named KPI 1:1 with this row.

### GOLD-KPI-VALUE-UNBILLED — fact / published_cut / recorded

Same file. `gold_kpi_value` from `MEASURE(unbilled_usd)` / `MEASURE(unbilled_ticket_count)`. Grains enterprise / payer / sold_to / site (11 rows). DELETE/INSERT only when Unbilled `status='approved'`. Gold publish is not re-approve.

### CATALOG-STATUS-HELPER — fact / catalog_lifecycle_helper / recorded

`sql/08_catalog_status.sql` `d9652d44…`. Add `definition_hash`. `UPDATE status='approved' WHERE status='certified'`. Enum: proposed \| approved \| drifted \| archived. Hash fill is Python (13 / 14), not this SQL.

### OSSIE-UNBILLED — fact / interchange_projection / recorded

`osi/unbilled.ossie.yaml` `2e889441…`. Ossie 0.1.1. Header: projection of the Metric View; not compile SoT; Databricks does not read it; nobody compiles it; not OWL; not a second formula. `compile_sot=sql/03_metric_view.sql`, `kpi_id=KPI-O2C-UNBILLED-USD`. Compile stays Databricks Metric Views.

### MV-CONTRACT-VS-LIST — fact / measure / recorded

`sql/06_complex_metric.sql` `766f8d79…`. View `contract_vs_list_usd`. NOT Unbilled. Source `raw_tickets`. Joins products/parties/terminals. Filter: delivered, temp≥80, gal≥5000, July 2026, gasoline\|distillate. Published pointer measure `delivered_contract_usd`. File expected 110064.00 / 7.

### KPI-O2C-CONTRACT-VS-LIST-USD — fact / named_kpi / recorded

Same file. `kpi_id` as written. IRI `#Obligation`. Same-file DELETE then INSERT into `dim_kpi_metadata` (status literal `certified`). 08 migrates certified→approved. Live warehouse status not re-read. Gold DELETE/INSERT **not** EXISTS-gated on approved (unlike Unbilled). See UNRES-06-07-GOLD-GATE.

### GOLD-KPI-VALUE-CONTRACT-VS-LIST — fact / published_cut / recorded

Same file `766f8d79…`. `gold_kpi_value` from `MEASURE(delivered_contract_usd)` / `MEASURE(delivered_ticket_count)`. Grains enterprise / sold_to / product. DELETE/INSERT not EXISTS-gated. File evidence, not live warehouse. Gold publish is not re-approve.

### MV-TEMP-ADJUSTED — fact / measure / recorded

`sql/07_temp_adjusted.sql` `f5d8db8b…`. View `temp_adjusted_delivered_usd`. NOT Unbilled. `temp_adjusted_usd = SUM(gallons_net * contract_price * (1 + expansion_per_f * (temperature_f - 60)))`. Filter: delivered, gal≥4000, Jun–Jul 2026, gasoline\|distillate\|aviation. File expected 256066.39 / 17.

### KPI-O2C-TEMP-ADJUSTED-USD — fact / named_kpi / recorded

Same file. IRI `#Obligation` (shared with contract-vs-list). Same-file DELETE then INSERT into `dim_kpi_metadata` (status literal `certified`). 08 migrates. Live warehouse status not re-read. Gold DELETE/INSERT **not** EXISTS-gated. See UNRES-06-07-GOLD-GATE.

### GOLD-KPI-VALUE-TEMP-ADJUSTED — fact / published_cut / recorded

Same file `f5d8db8b…`. `gold_kpi_value` from `MEASURE(temp_adjusted_usd)` / `MEASURE(delivered_ticket_count)`. Grains enterprise / product / site. DELETE/INSERT not EXISTS-gated. File evidence, not live warehouse. Gold publish is not re-approve.

### TTL-UNBILLEDSTATE — fact / meaning_term / cited

`ontology/o2c-meaning.ttl` `6ce06388…`. `#UnbilledState` is a state of an Obligation, not a KPI class. Matches Unbilled `ontology_iri`. Turtle is ontology SoT. Does not author the formula.

### TTL-OBLIGATION — fact / meaning_term / cited

Same file. `#Obligation` = delivered BOL / ticket. Both delivered KPIs bind here. Shared IRI is a file fact.

## Unresolved

| ID | Field | Note |
|---|---|---|
| UNRES-QUALITY-FRESHNESS | quality_freshness | Not declared in these files. |
| UNRES-PROCESS-USED-IN | process_used_in | No process column on `dim_kpi_metadata` in these files. Do not cite the process/schema folders as pinned evidence. |
| UNRES-06-07-FILE-STATUS-LITERAL | catalog_status | 06/07 INSERT `certified`; 08 migrates. Warehouse not re-read. |
| UNRES-06-07-GOLD-GATE | gold_publish_gate | 05 Unbilled Gold is gated; 06/07 Gold is not. Python companions not inventoried. |
| UNRES-DEFINITION-HASH-FILL | definition_hash | Column in 05/08; fill is Python. 06/07 INSERT omit it. |

## Dropped (Fable trim)

ADR-META rows. Fuseki. Neo4j. Vocabulary baseline. Generator. SHACL. OpenMetadata/Purview fixtures. Stage B.

## §8.2 fields

Used where the Demo 2 files have the fact: path, SHA, technical id, name, description, classification, formula, aggregation, grain, time, dimensions, physical deps, lineage, owner, catalog metadata, mapping_status.

Absent: quality_freshness (see UNRES-QUALITY-FRESHNESS). Forbidden: mapping_status `approved`; classification `approved KPI`.
