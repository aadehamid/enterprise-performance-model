-- =============================================================================
-- 02_facts.sql — star-ish dims + the unbilled population (compiler source)
-- Demo 2 (Databricks Free). Not Track A. No DuckDB, no dbt, no MetricFlow.
--
-- PLACEHOLDERS: {{catalog}} = workspace, {{schema}} = o2c_unbilled
-- (same find/replace as 01_land.sql)
--
-- fct_unbilled is the certified *population* at ticket grain (delivered,
-- no posted invoice as of 2026-08-01, quality-hold excluded,
-- unbilled_usd = gallons_net * contract_price). It is the table the
-- Metric View reads (compiler source). It is NOT gold published KPI values.
-- Gold snapshots live in gold_kpi_value (sql/05_store.sql), sourced FROM
-- MEASURE() on the Metric View — never a second SUM() of this table.
-- =============================================================================

-- Thin dimensions (star-ish). The Metric View does not join these; names
-- are denormalized onto the fact so YAML 03 stays one source table.

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.dim_party AS
SELECT
  p.party_id,
  p.party_name,
  p.legal_name,
  p.party_class,
  p.tax_id,
  p.hq_city,
  p.hq_state
FROM {{catalog}}.{{schema}}.raw_parties p;

-- Role bridge (payer / sold_to / bill_to). GCA holds all three.
CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.br_party_role AS
SELECT party_id, role_code
FROM {{catalog}}.{{schema}}.raw_party_roles;

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.dim_site AS
SELECT
  terminal_code AS site_code,
  terminal_name AS site_name,
  city,
  state,
  mode
FROM {{catalog}}.{{schema}}.raw_terminals;

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.dim_product AS
SELECT
  product_code,
  product_name,
  product_family,
  contract_price_usd,
  list_price_usd,
  uom
FROM {{catalog}}.{{schema}}.raw_products;

-- ---------------------------------------------------------------------------
-- Population ticket set as of 2026-08-01 (compiler source)
--   status = delivered
--   no posted invoice line with invoice_date <= as_of
--   unbilled_usd = gallons_net * contract_price_usd
-- Quality-hold is never billed and never unbilled.
-- Grain: one row per BOL ticket. Easy to audit.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.fct_unbilled AS
WITH posted_as_of AS (
  SELECT
    l.ticket_id
  FROM {{catalog}}.{{schema}}.raw_invoice_lines l
  INNER JOIN {{catalog}}.{{schema}}.raw_invoices i
    ON l.invoice_id = i.invoice_id
  WHERE i.invoice_status = 'posted'
    AND i.invoice_date <= DATE '2026-08-01'
)
SELECT
  t.ticket_id,
  t.bol_ts,
  CAST(t.bol_ts AS DATE)                         AS delivery_date,
  t.terminal_code                                AS site_code,
  s.site_name,
  t.sold_to_id,
  sold.party_name                                AS sold_to_name,
  t.payer_id,
  payer.party_name                               AS payer_name,
  t.bill_to_id,
  bill.party_name                                AS bill_to_name,
  t.product_code,
  pr.product_name,
  t.gallons_net,
  t.gallons_gross,
  t.temperature_f,
  t.status,
  pr.contract_price_usd,
  pr.list_price_usd,
  CAST(t.gallons_net * pr.contract_price_usd AS DECIMAL(18, 2)) AS unbilled_usd,
  DATE '2026-08-01'                              AS as_of_date
FROM {{catalog}}.{{schema}}.raw_tickets t
INNER JOIN {{catalog}}.{{schema}}.raw_products pr
  ON t.product_code = pr.product_code
INNER JOIN {{catalog}}.{{schema}}.raw_parties sold
  ON t.sold_to_id = sold.party_id
INNER JOIN {{catalog}}.{{schema}}.raw_parties payer
  ON t.payer_id = payer.party_id
INNER JOIN {{catalog}}.{{schema}}.raw_parties bill
  ON t.bill_to_id = bill.party_id
INNER JOIN {{catalog}}.{{schema}}.dim_site s
  ON t.terminal_code = s.site_code
LEFT JOIN posted_as_of posted
  ON t.ticket_id = posted.ticket_id
WHERE t.status = 'delivered'
  AND posted.ticket_id IS NULL;

-- Expect 12 tickets, $179,934.00. See data/README.md.
SELECT
  COUNT(*)                         AS unbilled_tickets,
  SUM(unbilled_usd)                AS unbilled_usd,
  COUNT(DISTINCT sold_to_id)       AS sold_to_keys,
  COUNT(DISTINCT payer_id)         AS payer_keys,
  COUNT(DISTINCT site_code)        AS site_keys
FROM {{catalog}}.{{schema}}.fct_unbilled;
