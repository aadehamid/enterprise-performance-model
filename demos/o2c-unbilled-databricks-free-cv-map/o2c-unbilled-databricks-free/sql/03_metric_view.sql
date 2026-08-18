-- =============================================================================
-- 03_metric_view.sql — Unity Catalog Metric View (the compiler for this demo)
--
-- LIVE-PROVEN dialect: YAML version 0.1 (fields + measures only).
-- Same YAML that scripts/04_metric_view.py sends. Do not author 1.1 here.
-- No comment / display_name / synonyms (those are YAML 1.1 agent metadata).
--
-- Honest seats:
--   fct_unbilled holds the ticket gate + gallons_net * contract_price
--     (population / compiler source).
--   This Metric View compiles SUM/GROUP BY (queried with MEASURE()).
--   Gold and Genie consume MEASURE() and must not re-encode.
--   RC-1 still holds for Gold/Genie (one compile path, no second SUM).
--
-- This YAML is the authored compile input for demo 2.
-- A Store catalog would point at this view (formula_pointer = unbilled_usd).
-- It is NOT ontology Turtle. Ontology = meaning (sold-to ≠ payer ≠ site).
-- Meaning sidecar (not compiled; YAML 0.1 does not embed IRIs):
--   ontology/o2c-meaning.ttl
--
-- Compiler: Unity Catalog Metric Views
--   CREATE VIEW … WITH METRICS LANGUAGE YAML
--   every measure is queried with MEASURE()
--   SELECT * is refused
--
-- Syntax from official docs (2026):
--   https://docs.databricks.com/aws/en/uc-semantics/metric-views/create
--   https://docs.databricks.com/aws/en/business-semantics/metric-views/yaml-reference
--   Pack dialect is version 0.1 — fields + measures only.
--
-- PLACEHOLDERS: {{catalog}} = workspace, {{schema}} = o2c_unbilled
-- Live compile succeeded 2026-08-14 on Databricks Free Edition with
-- version: 0.1 (CREATE VIEW WITH METRICS + MEASURE() + SELECT * refused
-- METRIC_VIEW_MISSING_MEASURE_FUNCTION). Do not put a workspace URL here.
-- =============================================================================

CREATE OR REPLACE VIEW {{catalog}}.{{schema}}.unbilled_usd
WITH METRICS
LANGUAGE YAML
AS $$
version: 0.1
source: {{catalog}}.{{schema}}.fct_unbilled
fields:
  - name: payer
    expr: source.payer_name
  - name: sold_to
    expr: source.sold_to_name
  - name: site
    expr: source.site_code
  - name: site_name
    expr: source.site_name
  - name: as_of
    expr: source.as_of_date
  - name: delivery_date
    expr: source.delivery_date
  - name: product
    expr: source.product_code
measures:
  - name: unbilled_usd
    expr: SUM(source.unbilled_usd)
  - name: unbilled_ticket_count
    expr: COUNT(1)
$$;

-- If the statement above succeeded, Metric Views compile on this warehouse.
-- Inspect the stored YAML (View Text). Live compile of version 0.1 succeeded 2026-08-14.
DESCRIBE TABLE EXTENDED {{catalog}}.{{schema}}.unbilled_usd;
