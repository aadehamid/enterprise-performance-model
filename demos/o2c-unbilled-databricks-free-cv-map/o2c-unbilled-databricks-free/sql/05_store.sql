-- =============================================================================
-- 05_store.sql — Silver KPI metadata + Gold published KPI values
-- Demo 2 (Databricks Free). Not Track A. No DuckDB, no dbt, no MetricFlow.
--
-- PLACEHOLDERS: {{catalog}} = workspace, {{schema}} = o2c_unbilled
--
-- Layer story (locked):
--   ODS        Lakebase dataexpert-day1 / databricks_postgres / o2c_unbilled  (ops tables)
--   Bronze     workspace.o2c_unbilled.raw_*   (replica; Python pipe; no federated join)
--   Silver     dim_party, dim_site, dim_product, br_party_role  (already exist)
--              + dim_kpi_metadata   NEW — one row per KPI (status proposed|approved|drifted|archived; pointer, not the formula)
--   Population fct_unbilled  (ticket grain; compiler source; ticket gate + gallons_net * contract_price; NOT gold)
--   Compiler   Metric View workspace.o2c_unbilled.unbilled_usd  (SUM/GROUP BY via MEASURE())
--   Gold       gold_kpi_value  NEW — published KPI values FROM MEASURE(), not a second SUM()
--
-- Honest seats:
--   fct_unbilled holds the ticket gate + gallons_net * contract_price
--     (population / compiler source).
--   The Metric View compiles SUM/GROUP BY (MEASURE()).
--   Gold and Genie consume MEASURE() and must not re-encode.
--   RC-1 per KPI (one compile path each, no second SUM).
-- C-10: ontology = meaning. Metadata does NOT author the formula
-- (formula_pointer / formula_object point at the Metric View measure).
--
-- Honest Store path: CREATE TABLE IF NOT EXISTS gold_kpi_value, then
-- DELETE Unbilled gold rows and INSERT … MEASURE() … UNION ALL the
-- Unbilled grains. Never CREATE OR REPLACE the whole gold table (that
-- would wipe KPI 2/3). If the warehouse refuses INSERT from a Metric
-- View, scripts/06_store.py falls back to VALUES built from those same
-- MEASURE() results — still not SUM(fct_unbilled).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Silver: dim_kpi_metadata — one row per KPI (status proposed|approved|drifted|archived).
-- Meaning + pointer. Not a second formula.
-- Create the table if missing, then upsert ONLY the Unbilled row.
-- Do NOT CREATE OR REPLACE the table (that wipes KPI 2/3).
-- Gold below upserts ONLY Unbilled rows and must not touch metadata.
-- After 05/06: Unbilled row present (catalog may already have 2/3 if 08/09 ran first).
-- After a full run: expect 3 approved rows (plus definition_hash from live MV text).
-- formula_version is the authored dialect (0.1), not "whatever the retry used."
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS {{catalog}}.{{schema}}.dim_kpi_metadata (
  kpi_id STRING,
  name STRING,
  owner STRING,
  definition STRING,
  uom STRING,
  allowed_grain STRING,
  default_grain_rule STRING,
  gating_rule STRING,
  status STRING,
  formula_pointer STRING,
  formula_object STRING,
  formula_version STRING,
  ontology_iri STRING,
  as_of_date DATE,
  definition_hash STRING
);

-- Free warehouse: ADD COLUMN IF NOT EXISTS is a parse error.
-- 06_store.py DESCRIBE-checks, then ADD COLUMN once if missing.

-- First-time INSERT only. Never DELETE an existing Unbilled row
-- (that would drop definition_hash). Never INSERT status=approved
-- over drifted|proposed|archived. Gold publish is not re-approve
-- (approve_kpi / 14_reapprove.py is the only path that sets approved
-- + refreshes definition_hash).
INSERT INTO {{catalog}}.{{schema}}.dim_kpi_metadata (
  kpi_id,
  name,
  owner,
  definition,
  uom,
  allowed_grain,
  default_grain_rule,
  gating_rule,
  status,
  formula_pointer,
  formula_object,
  formula_version,
  ontology_iri,
  as_of_date
)
SELECT
  CAST('KPI-O2C-UNBILLED-USD' AS STRING)               AS kpi_id,
  CAST('Unbilled USD' AS STRING)                       AS name,
  CAST('Revenue Accounting / Order-to-Cash' AS STRING) AS owner,
  CAST('Unbilled USD at the published grains' AS STRING) AS definition,
  CAST('USD' AS STRING)                                AS uom,
  CAST('enterprise,payer,sold_to,site' AS STRING)      AS allowed_grain,
  CAST('enterprise | payer | sold_to | site' AS STRING) AS default_grain_rule,
  CAST('See fct_unbilled (population / compiler source).' AS STRING) AS gating_rule,
  CAST('approved' AS STRING)                           AS status,
  CAST('unbilled_usd' AS STRING)                       AS formula_pointer,
  CAST('{{catalog}}.{{schema}}.unbilled_usd' AS STRING) AS formula_object,
  CAST('0.1' AS STRING)                                AS formula_version,
  CAST('https://example.org/domain-ontology-kpi/o2c#UnbilledState' AS STRING) AS ontology_iri,
  CAST(DATE '2026-08-01' AS DATE)                      AS as_of_date
FROM (SELECT 1) AS _gate
WHERE NOT EXISTS (
  SELECT 1
  FROM {{catalog}}.{{schema}}.dim_kpi_metadata
  WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
);

-- After 05/06: Unbilled row present. Catalog may already have 2/3 if 08/09 ran first.
-- After a full run: expect 3 rows.
SELECT COUNT(*) AS metadata_rows
FROM {{catalog}}.{{schema}}.dim_kpi_metadata;

SELECT
  kpi_id,
  name,
  owner,
  uom,
  allowed_grain,
  default_grain_rule,
  status,
  formula_pointer,
  formula_object,
  formula_version,
  ontology_iri,
  as_of_date
FROM {{catalog}}.{{schema}}.dim_kpi_metadata;

-- ---------------------------------------------------------------------------
-- Gold: gold_kpi_value — published instances FROM MEASURE().
-- Create if missing, then replace ONLY Unbilled rows (kpi_id).
-- Never CREATE OR REPLACE the whole table (that wipes KPI 2/3).
-- One published measure: MEASURE(unbilled_usd). Grains: enterprise /
-- payer / sold_to / site. Not SUM(fct_unbilled). Not a second formula.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS {{catalog}}.{{schema}}.gold_kpi_value (
  kpi_id STRING,
  grain STRING,
  grain_key STRING,
  grain_label STRING,
  as_of_date DATE,
  value_usd DECIMAL(18, 2),
  ticket_count BIGINT,
  formula_pointer STRING,
  published_ts TIMESTAMP
);

-- Refresh Gold only while Unbilled is already approved.
-- drifted|proposed|archived keep the last approved snapshot (published_ts unchanged).
DELETE FROM {{catalog}}.{{schema}}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
  AND EXISTS (
    SELECT 1
    FROM {{catalog}}.{{schema}}.dim_kpi_metadata
    WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
      AND status = 'approved'
  );

INSERT INTO {{catalog}}.{{schema}}.gold_kpi_value (
  kpi_id,
  grain,
  grain_key,
  grain_label,
  as_of_date,
  value_usd,
  ticket_count,
  formula_pointer,
  published_ts
)
SELECT
  'KPI-O2C-UNBILLED-USD'             AS kpi_id,
  'enterprise'                       AS grain,
  '*'                                AS grain_key,
  'Enterprise'                       AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(unbilled_usd)              AS value_usd,
  MEASURE(unbilled_ticket_count)     AS ticket_count,
  'unbilled_usd'                     AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.unbilled_usd
WHERE EXISTS (
  SELECT 1
  FROM {{catalog}}.{{schema}}.dim_kpi_metadata
  WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
    AND status = 'approved'
)
UNION ALL
SELECT
  'KPI-O2C-UNBILLED-USD'             AS kpi_id,
  'payer'                            AS grain,
  payer                              AS grain_key,
  payer                              AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(unbilled_usd)              AS value_usd,
  MEASURE(unbilled_ticket_count)     AS ticket_count,
  'unbilled_usd'                     AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.unbilled_usd
WHERE EXISTS (
  SELECT 1
  FROM {{catalog}}.{{schema}}.dim_kpi_metadata
  WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
    AND status = 'approved'
)
GROUP BY payer
UNION ALL
SELECT
  'KPI-O2C-UNBILLED-USD'             AS kpi_id,
  'sold_to'                          AS grain,
  sold_to                            AS grain_key,
  sold_to                            AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(unbilled_usd)              AS value_usd,
  MEASURE(unbilled_ticket_count)     AS ticket_count,
  'unbilled_usd'                     AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.unbilled_usd
WHERE EXISTS (
  SELECT 1
  FROM {{catalog}}.{{schema}}.dim_kpi_metadata
  WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
    AND status = 'approved'
)
GROUP BY sold_to
UNION ALL
SELECT
  'KPI-O2C-UNBILLED-USD'             AS kpi_id,
  'site'                             AS grain,
  site                               AS grain_key,
  site_name                          AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(unbilled_usd)              AS value_usd,
  MEASURE(unbilled_ticket_count)     AS ticket_count,
  'unbilled_usd'                     AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.unbilled_usd
WHERE EXISTS (
  SELECT 1
  FROM {{catalog}}.{{schema}}.dim_kpi_metadata
  WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
    AND status = 'approved'
)
GROUP BY site, site_name;

-- Unbilled gold only: 11 rows (enterprise 1 / payer 3 / sold_to 4 / site 3).
-- Each Unbilled grain slice SUM(value_usd) = 179934.00.
-- After 08/09 the table has more kpi_ids; scope these checks to Unbilled.
SELECT
  grain,
  COUNT(*)            AS gold_rows,
  SUM(value_usd)      AS value_usd,
  SUM(ticket_count)   AS tickets
FROM {{catalog}}.{{schema}}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
GROUP BY grain
ORDER BY grain;

SELECT
  grain,
  grain_key,
  grain_label,
  value_usd,
  ticket_count,
  formula_pointer
FROM {{catalog}}.{{schema}}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
ORDER BY grain, value_usd DESC;

-- Join Unbilled gold to metadata on kpi_id (Store catalog ↔ published instances).
SELECT
  g.grain,
  g.grain_key,
  g.value_usd,
  g.ticket_count,
  m.name,
  m.status,
  m.formula_pointer,
  m.formula_object
FROM {{catalog}}.{{schema}}.gold_kpi_value g
INNER JOIN {{catalog}}.{{schema}}.dim_kpi_metadata m
  ON g.kpi_id = m.kpi_id
WHERE g.kpi_id = 'KPI-O2C-UNBILLED-USD'
ORDER BY g.grain, g.value_usd DESC;

-- Grand check: Unbilled enterprise published value.
SELECT SUM(value_usd) AS enterprise_usd
FROM {{catalog}}.{{schema}}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-UNBILLED-USD'
  AND grain = 'enterprise';
