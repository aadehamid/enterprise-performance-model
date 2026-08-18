-- =============================================================================
-- 06_complex_metric.sql — SECOND Metric View: contract_vs_list_usd
--
-- This is NOT Unbilled. It is delivered-ticket value at contract vs list.
-- Proves the compiler writes SQL for joins + filters + cross-table multiply.
-- Do not replace or change unbilled_usd (sql/03_metric_view.sql).
--
-- Dialect: YAML version 0.1 first (fields + measures + joins + filter).
-- No 1.1 agent metadata (comment / display_name / synonyms).
-- If Free refuses joins/filter on 0.1, scripts/08_complex_metric.py retries
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

CREATE OR REPLACE VIEW {{catalog}}.{{schema}}.contract_vs_list_usd
WITH METRICS
LANGUAGE YAML
AS $$
version: 0.1
source: {{catalog}}.{{schema}}.raw_tickets
filter: source.status = 'delivered' AND source.temperature_f >= 80 AND source.gallons_net >= 5000 AND CAST(source.bol_ts AS DATE) BETWEEN DATE '2026-07-01' AND DATE '2026-07-31' AND product_dim.product_family IN ('gasoline', 'distillate')
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
measures:
  - name: delivered_contract_usd
    expr: SUM(source.gallons_net * product_dim.contract_price_usd)
  - name: delivered_list_usd
    expr: SUM(source.gallons_net * product_dim.list_price_usd)
  - name: list_minus_contract_usd
    expr: SUM(source.gallons_net * (product_dim.list_price_usd - product_dim.contract_price_usd))
  - name: delivered_ticket_count
    expr: COUNT(1)
  - name: hot_rack_contract_usd
    expr: SUM(CASE WHEN source.temperature_f >= 88 THEN source.gallons_net * product_dim.contract_price_usd ELSE 0 END)
  - name: marine_contract_usd
    expr: SUM(CASE WHEN site_dim.mode = 'marine_rack' THEN source.gallons_net * product_dim.contract_price_usd ELSE 0 END)
  - name: rbob_contract_usd
    expr: SUM(CASE WHEN source.product_code = 'RBOB' THEN source.gallons_net * product_dim.contract_price_usd ELSE 0 END)
$$;

DESCRIBE TABLE EXTENDED {{catalog}}.{{schema}}.contract_vs_list_usd;

-- Unsliced — compiler must emit joins + filter + multiply.
-- Expected from data/*.csv (delivered, temp>=80, gal>=5000, July 2026,
-- gasoline|distillate; quality_hold excluded by status):
--   delivered_contract_usd 110064.00
--   delivered_list_usd     114450.00
--   list_minus_contract_usd  4386.00
--   delivered_ticket_count        7
--   hot_rack_contract_usd   50887.20
--   marine_contract_usd     83948.80
--   rbob_contract_usd       62899.20
SELECT
  MEASURE(delivered_contract_usd)   AS delivered_contract_usd,
  MEASURE(delivered_list_usd)       AS delivered_list_usd,
  MEASURE(list_minus_contract_usd)  AS list_minus_contract_usd,
  MEASURE(delivered_ticket_count)   AS delivered_ticket_count,
  MEASURE(hot_rack_contract_usd)    AS hot_rack_contract_usd,
  MEASURE(marine_contract_usd)      AS marine_contract_usd,
  MEASURE(rbob_contract_usd)        AS rbob_contract_usd
FROM {{catalog}}.{{schema}}.contract_vs_list_usd;

-- By sold_to
SELECT
  sold_to,
  MEASURE(delivered_contract_usd)   AS delivered_contract_usd,
  MEASURE(delivered_list_usd)       AS delivered_list_usd,
  MEASURE(list_minus_contract_usd)  AS list_minus_contract_usd,
  MEASURE(delivered_ticket_count)   AS delivered_ticket_count,
  MEASURE(hot_rack_contract_usd)    AS hot_rack_contract_usd,
  MEASURE(marine_contract_usd)      AS marine_contract_usd,
  MEASURE(rbob_contract_usd)        AS rbob_contract_usd
FROM {{catalog}}.{{schema}}.contract_vs_list_usd
GROUP BY sold_to
ORDER BY delivered_contract_usd DESC;

-- By product
SELECT
  product,
  product_family,
  MEASURE(delivered_contract_usd)   AS delivered_contract_usd,
  MEASURE(delivered_list_usd)       AS delivered_list_usd,
  MEASURE(list_minus_contract_usd)  AS list_minus_contract_usd,
  MEASURE(delivered_ticket_count)   AS delivered_ticket_count,
  MEASURE(hot_rack_contract_usd)    AS hot_rack_contract_usd,
  MEASURE(marine_contract_usd)      AS marine_contract_usd,
  MEASURE(rbob_contract_usd)        AS rbob_contract_usd
FROM {{catalog}}.{{schema}}.contract_vs_list_usd
GROUP BY product, product_family
ORDER BY delivered_contract_usd DESC;

-- Store pointer + Gold snapshot for this KPI (not Unbilled).
-- Skipped if dim_kpi_metadata / gold_kpi_value is missing (run sql/05_store.sql first).
-- DELETE then INSERT so a re-run updates pointer / status / iri / gold.
-- formula_pointer is the measure name (delivered_contract_usd), not the view name.
-- formula_object is the view. formula_version is the authored dialect (0.1),
-- not "whatever the retry used."
-- Gold grains follow allowed_grain: enterprise / sold_to / product.
-- One published measure: MEASURE(delivered_contract_usd).
DELETE FROM {{catalog}}.{{schema}}.dim_kpi_metadata
WHERE kpi_id = 'KPI-O2C-CONTRACT-VS-LIST-USD';

INSERT INTO {{catalog}}.{{schema}}.dim_kpi_metadata
SELECT
  CAST('KPI-O2C-CONTRACT-VS-LIST-USD' AS STRING) AS kpi_id,
  CAST('Contract vs list USD' AS STRING)         AS name,
  CAST('Revenue Accounting / Order-to-Cash' AS STRING) AS owner,
  CAST('Delivered-ticket value at contract vs list (see Metric View)' AS STRING) AS definition,
  CAST('USD' AS STRING)                          AS uom,
  CAST('enterprise,sold_to,product' AS STRING)   AS allowed_grain,
  CAST('enterprise | sold_to | product' AS STRING) AS default_grain_rule,
  CAST('See contract_vs_list_usd Metric View (not Unbilled).' AS STRING) AS gating_rule,
  CAST('certified' AS STRING)                    AS status,
  CAST('delivered_contract_usd' AS STRING)       AS formula_pointer,
  CAST('{{catalog}}.{{schema}}.contract_vs_list_usd' AS STRING) AS formula_object,
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
WHERE kpi_id = 'KPI-O2C-CONTRACT-VS-LIST-USD';

INSERT INTO {{catalog}}.{{schema}}.gold_kpi_value (
  kpi_id, grain, grain_key, grain_label, as_of_date,
  value_usd, ticket_count, formula_pointer, published_ts
)
SELECT
  'KPI-O2C-CONTRACT-VS-LIST-USD'     AS kpi_id,
  'enterprise'                       AS grain,
  '*'                                AS grain_key,
  'Enterprise'                       AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(delivered_contract_usd)    AS value_usd,
  MEASURE(delivered_ticket_count)    AS ticket_count,
  'delivered_contract_usd'           AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.contract_vs_list_usd
UNION ALL
SELECT
  'KPI-O2C-CONTRACT-VS-LIST-USD'     AS kpi_id,
  'sold_to'                          AS grain,
  sold_to                            AS grain_key,
  sold_to                            AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(delivered_contract_usd)    AS value_usd,
  MEASURE(delivered_ticket_count)    AS ticket_count,
  'delivered_contract_usd'           AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.contract_vs_list_usd
GROUP BY sold_to
UNION ALL
SELECT
  'KPI-O2C-CONTRACT-VS-LIST-USD'     AS kpi_id,
  'product'                          AS grain,
  product                            AS grain_key,
  product_family                     AS grain_label,
  DATE '2026-08-01'                  AS as_of_date,
  MEASURE(delivered_contract_usd)    AS value_usd,
  MEASURE(delivered_ticket_count)    AS ticket_count,
  'delivered_contract_usd'           AS formula_pointer,
  current_timestamp()                AS published_ts
FROM {{catalog}}.{{schema}}.contract_vs_list_usd
GROUP BY product, product_family;
