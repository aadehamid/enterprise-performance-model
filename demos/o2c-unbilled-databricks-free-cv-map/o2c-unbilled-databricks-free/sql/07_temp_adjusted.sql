-- =============================================================================
-- 07_temp_adjusted.sql — THIRD Metric View: temp_adjusted_delivered_usd
--
-- Volume-correction / temperature-adjusted delivered value (rack math).
-- This is NOT Unbilled and NOT contract-vs-list.
-- Proves the compiler writes SQL for joins + filters + expansion multiply.
-- Do not replace or change unbilled_usd (sql/03_metric_view.sql).
--
-- Dialect: YAML version 0.1 first (fields + measures + joins + filter).
-- No 1.1 agent metadata (comment / display_name / synonyms).
-- If Free refuses joins/filter on 0.1, scripts/09_temp_adjusted.py retries
-- the SAME shape with version: 1.1 on THIS view only.
--
-- Source: raw_tickets (not fct_unbilled). Star joins, many-to-one.
-- LEFT OUTER is the engine default.
--
-- Compiler: Unity Catalog Metric Views
--   CREATE VIEW … WITH METRICS LANGUAGE YAML
--   every measure is queried with MEASURE()
--   SELECT * is refused
--
-- Official:
--   https://docs.databricks.com/aws/en/uc-semantics/metric-views/create
--   https://docs.databricks.com/aws/en/uc-semantics/metric-views/joins
--   https://docs.databricks.com/aws/en/business-semantics/metric-views/yaml-reference
--
-- PLACEHOLDERS: {{catalog}} = workspace, {{schema}} = o2c_unbilled
-- Demo 2 / Track B. Not MetricFlow. Not Track A.
-- =============================================================================

-- Join aliases are product_dim / payer_dim / site_dim / sold.
-- Free treats a field name as shadowing a join of the same name
-- (INVALID_EXTRACT_BASE_FIELD_TYPE on STRING). Field names stay
-- payer / site / product so MEASURE() GROUP BY matches the lesson.
-- Same star shape: many-to-one, on: boolean, source. prefix.
-- Official join docs use name: product; that collides with field product.

CREATE OR REPLACE VIEW {{catalog}}.{{schema}}.temp_adjusted_delivered_usd
WITH METRICS
LANGUAGE YAML
AS $$
version: 0.1
source: {{catalog}}.{{schema}}.raw_tickets
filter: source.status = 'delivered' AND source.gallons_net >= 4000 AND CAST(source.bol_ts AS DATE) BETWEEN DATE '2026-06-01' AND DATE '2026-07-31' AND product_dim.product_family IN ('gasoline', 'distillate', 'aviation')
joins:
  - name: product_dim
    source: {{catalog}}.{{schema}}.raw_products
    on: source.product_code = product_dim.product_code
  - name: sold
    source: {{catalog}}.{{schema}}.raw_parties
    on: source.sold_to_id = sold.party_id
  - name: payer_dim
    source: {{catalog}}.{{schema}}.raw_parties
    on: source.payer_id = payer_dim.party_id
  - name: site_dim
    source: {{catalog}}.{{schema}}.raw_terminals
    on: source.terminal_code = site_dim.terminal_code
fields:
  - name: payer
    expr: payer_dim.party_name
  - name: sold_to
    expr: sold.party_name
  - name: site
    expr: source.terminal_code
  - name: site_name
    expr: site_dim.terminal_name
  - name: product
    expr: source.product_code
  - name: product_family
    expr: product_dim.product_family
  - name: mode
    expr: site_dim.mode
measures:
  - name: contract_at_net_usd
    expr: SUM(source.gallons_net * product_dim.contract_price_usd)
  - name: contract_at_gross_usd
    expr: SUM(source.gallons_gross * product_dim.contract_price_usd)
  - name: temp_adjusted_usd
    expr: SUM(source.gallons_net * product_dim.contract_price_usd * (1 + product_dim.expansion_per_f * (source.temperature_f - 60)))
  - name: expansion_delta_usd
    expr: SUM(source.gallons_net * product_dim.contract_price_usd * (product_dim.expansion_per_f * (source.temperature_f - 60)))
  - name: delivered_ticket_count
    expr: COUNT(1)
  - name: net_gallons
    expr: SUM(source.gallons_net)
  - name: gross_gallons
    expr: SUM(source.gallons_gross)
  - name: weighted_temp_x_gallons
    expr: SUM(source.temperature_f * source.gallons_net)
  - name: marine_temp_adjusted_usd
    expr: SUM(CASE WHEN site_dim.mode = 'marine_rack' THEN source.gallons_net * product_dim.contract_price_usd * (1 + product_dim.expansion_per_f * (source.temperature_f - 60)) ELSE 0 END)
$$;

DESCRIBE TABLE EXTENDED {{catalog}}.{{schema}}.temp_adjusted_delivered_usd;

-- Unsliced — compiler must emit joins + filter + expansion multiply.
-- Expected from data/*.csv (delivered, gal>=4000, Jun–Jul 2026,
-- gasoline|distillate|aviation; quality_hold excluded by status):
--   contract_at_net_usd       252617.20
--   contract_at_gross_usd     256450.62
--   temp_adjusted_usd         256066.39
--   expansion_delta_usd         3449.19
--   delivered_ticket_count          17
--   net_gallons               112900.00
--   gross_gallons             114625.45
--   weighted_temp_x_gallons  9487200.00
--   marine_temp_adjusted_usd  138692.75
SELECT
  MEASURE(contract_at_net_usd)       AS contract_at_net_usd,
  MEASURE(contract_at_gross_usd)     AS contract_at_gross_usd,
  MEASURE(temp_adjusted_usd)         AS temp_adjusted_usd,
  MEASURE(expansion_delta_usd)       AS expansion_delta_usd,
  MEASURE(delivered_ticket_count)    AS delivered_ticket_count,
  MEASURE(net_gallons)               AS net_gallons,
  MEASURE(gross_gallons)             AS gross_gallons,
  MEASURE(weighted_temp_x_gallons)   AS weighted_temp_x_gallons,
  MEASURE(marine_temp_adjusted_usd)  AS marine_temp_adjusted_usd
FROM {{catalog}}.{{schema}}.temp_adjusted_delivered_usd;

-- By product
SELECT
  product,
  product_family,
  MEASURE(contract_at_net_usd)       AS contract_at_net_usd,
  MEASURE(temp_adjusted_usd)         AS temp_adjusted_usd,
  MEASURE(expansion_delta_usd)       AS expansion_delta_usd,
  MEASURE(delivered_ticket_count)    AS delivered_ticket_count,
  MEASURE(net_gallons)               AS net_gallons,
  MEASURE(marine_temp_adjusted_usd)  AS marine_temp_adjusted_usd
FROM {{catalog}}.{{schema}}.temp_adjusted_delivered_usd
GROUP BY product, product_family
ORDER BY temp_adjusted_usd DESC;

-- By site
SELECT
  site,
  site_name,
  mode,
  MEASURE(contract_at_net_usd)       AS contract_at_net_usd,
  MEASURE(temp_adjusted_usd)         AS temp_adjusted_usd,
  MEASURE(delivered_ticket_count)    AS delivered_ticket_count,
  MEASURE(net_gallons)               AS net_gallons,
  MEASURE(marine_temp_adjusted_usd)  AS marine_temp_adjusted_usd
FROM {{catalog}}.{{schema}}.temp_adjusted_delivered_usd
GROUP BY site, site_name, mode
ORDER BY temp_adjusted_usd DESC;

-- Store pointer + Gold snapshot for this KPI (not Unbilled).
-- DELETE then INSERT so a re-run updates pointer / status / iri / gold.
-- formula_pointer is the measure name (temp_adjusted_usd); formula_object is the view.
-- formula_version is the authored dialect (0.1), not "whatever the retry used."
-- Gold grains follow allowed_grain: enterprise / product / site.
-- One published measure: MEASURE(temp_adjusted_usd).
DELETE FROM {{catalog}}.{{schema}}.dim_kpi_metadata
WHERE kpi_id = 'KPI-O2C-TEMP-ADJUSTED-USD';

INSERT INTO {{catalog}}.{{schema}}.dim_kpi_metadata
SELECT
  CAST('KPI-O2C-TEMP-ADJUSTED-USD' AS STRING) AS kpi_id,
  CAST('Temp-adjusted delivered USD' AS STRING) AS name,
  CAST('Revenue Accounting / Order-to-Cash' AS STRING) AS owner,
  CAST('Temperature-adjusted delivered value (see Metric View)' AS STRING) AS definition,
  CAST('USD' AS STRING)                          AS uom,
  CAST('enterprise,product,site' AS STRING)      AS allowed_grain,
  CAST('enterprise | product | site' AS STRING)  AS default_grain_rule,
  CAST('See temp_adjusted_delivered_usd Metric View (not Unbilled).' AS STRING) AS gating_rule,
  CAST('certified' AS STRING)                    AS status,
  CAST('temp_adjusted_usd' AS STRING)            AS formula_pointer,
  CAST('{{catalog}}.{{schema}}.temp_adjusted_delivered_usd' AS STRING) AS formula_object,
  CAST('0.1' AS STRING)                          AS formula_version,
  CAST('https://example.org/domain-ontology-kpi/o2c#Obligation' AS STRING) AS ontology_iri,
  CAST(DATE '2026-08-01' AS DATE)                AS as_of_date;

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

DELETE FROM {{catalog}}.{{schema}}.gold_kpi_value
WHERE kpi_id = 'KPI-O2C-TEMP-ADJUSTED-USD';

INSERT INTO {{catalog}}.{{schema}}.gold_kpi_value (
  kpi_id, grain, grain_key, grain_label, as_of_date,
  value_usd, ticket_count, formula_pointer, published_ts
)
SELECT
  'KPI-O2C-TEMP-ADJUSTED-USD'        AS kpi_id,
  'enterprise'                       AS grain,
  '*'                                AS grain_key,
  'Enterprise'                       AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(temp_adjusted_usd)         AS value_usd,
  MEASURE(delivered_ticket_count)    AS ticket_count,
  'temp_adjusted_usd'                AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.temp_adjusted_delivered_usd
UNION ALL
SELECT
  'KPI-O2C-TEMP-ADJUSTED-USD'        AS kpi_id,
  'product'                          AS grain,
  product                            AS grain_key,
  product_family                     AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(temp_adjusted_usd)         AS value_usd,
  MEASURE(delivered_ticket_count)    AS ticket_count,
  'temp_adjusted_usd'                AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.temp_adjusted_delivered_usd
GROUP BY product, product_family
UNION ALL
SELECT
  'KPI-O2C-TEMP-ADJUSTED-USD'        AS kpi_id,
  'site'                             AS grain,
  site                               AS grain_key,
  site_name                          AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(temp_adjusted_usd)         AS value_usd,
  MEASURE(delivered_ticket_count)    AS ticket_count,
  'temp_adjusted_usd'                AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.temp_adjusted_delivered_usd
GROUP BY site, site_name;
