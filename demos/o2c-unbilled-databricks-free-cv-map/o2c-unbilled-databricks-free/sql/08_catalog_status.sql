-- =============================================================================
-- 08_catalog_status.sql — keep dim_kpi_metadata; add definition_hash; migrate
-- status certified → approved. Never CREATE OR REPLACE (that wipes rows).
-- Hash fill is Python (SHOW CREATE TABLE of formula_object). See
-- scripts/13_status_drift.py --migrate and scripts/14_reapprove.py.
-- PLACEHOLDERS: {{catalog}} = workspace, {{schema}} = o2c_unbilled
-- status values: proposed | approved | drifted | archived
-- =============================================================================

-- Free warehouse: ADD COLUMN IF NOT EXISTS is a parse error.
-- scripts/13_status_drift.py DESCRIBE-checks, then ADD COLUMN once.
ALTER TABLE {{catalog}}.{{schema}}.dim_kpi_metadata
  ADD COLUMN definition_hash STRING;

UPDATE {{catalog}}.{{schema}}.dim_kpi_metadata
SET status = 'approved'
WHERE status = 'certified';

SELECT kpi_id, status, definition_hash, formula_pointer, formula_object
FROM {{catalog}}.{{schema}}.dim_kpi_metadata
ORDER BY kpi_id;
