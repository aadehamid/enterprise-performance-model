-- =============================================================================
-- 06_complex_metric.sql — SECOND Metric View: contract_vs_list_usd
-- your SQL goes here
--
-- Teaching constraint:
--   This is NOT Unbilled. Delivered-ticket value at contract vs list.
--   CREATE VIEW … WITH METRICS LANGUAGE YAML
--   Version 0.1 FIRST (fields + measures + joins + filter if 0.1 accepts them).
--   No comment / display_name / synonyms.
--   Source is raw_tickets (not fct_unbilled).
--   Star joins: product_dim, sold, payer_dim, site_dim (on: boolean, prefix source.).
   Not product, sold, payer, site — those aliases collide with field names
   (INVALID_EXTRACT_BASE_FIELD_TYPE).
--   Filter: delivered AND temp>=80 AND gal>=5000 AND July 2026
--           AND product_family IN (gasoline, distillate).
--   Measures use gallons_net * product prices. Consumers only MEASURE().
--   SELECT * is refused.
--   Do not change sql/03_metric_view.sql (unbilled_usd).
--   Join aliases: product_dim, sold, payer_dim, site_dim. Keep field names product / site / payer / sold_to.
--   Placeholders: {{catalog}} = workspace, {{schema}} = o2c_unbilled
--
-- Hint (path, not the answer):
--   ../o2c-unbilled-databricks-free/sql/06_complex_metric.sql
--   ../o2c-unbilled-databricks-free/scripts/08_complex_metric.py
-- =============================================================================

-- your SQL goes here
