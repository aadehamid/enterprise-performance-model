-- 02_replica.sql: one replica table per source table, read from the Parquet files the replication landed in the
-- volume. Each keeps the source's columns plus _change_ts and _replicated_at. Mirrors synapse_dev.replica_* (EPM-DEC-001-0097).

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_currency AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_currency.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_unitofmeasure AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_unitofmeasure.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_pricebatch AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_pricebatch.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_pricesheet AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_pricesheet.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_pricegroup AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_pricegroup.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_priceassessmentgroup AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_priceassessmentgroup.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_assessment.mips_priceassessment AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_assessment/mips_priceassessment.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_reference.pricemaster AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_reference/pricemaster.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_price_reference.pricedetail AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/price_reference/pricedetail.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_reference_data_hub.priceservice AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/reference_data_hub/priceservice.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_reference_data_hub.holidaycalendar AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/reference_data_hub/holidaycalendar.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_reference_data_hub.deliveryperiodcategory AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/reference_data_hub/deliveryperiodcategory.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_rightangle.deal AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/rightangle/deal.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_rightangle.movement AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/rightangle/movement.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_aspen_pims.plan_target AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/aspen_pims/plan_target.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_production_accounting.refinery AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/production_accounting/refinery.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_production_accounting.refinery_daily AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/production_accounting/refinery_daily.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_reference_data_hub.market_event AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/reference_data_hub/market_event.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_rightangle.freight_rate AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/rightangle/freight_rate.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_production_accounting.unit_daily AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/production_accounting/unit_daily.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_eia_weekly.series AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/eia_weekly/series.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_eia_weekly.weekly_value AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/eia_weekly/weekly_value.parquet', format => 'parquet');

-- Added for E2 (2026-10-28): plan versions, the decision log and its evidence items, from Aspen PIMS. The decision
-- dossiers (database decision_truth) are hidden truth and never replicated (config.HIDDEN_SYSTEMS).
CREATE OR REPLACE TABLE ${catalog}.replica_aspen_pims.plan_version AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/aspen_pims/plan_version.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_aspen_pims.decision_log AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/aspen_pims/decision_log.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_aspen_pims.decision_evidence AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/aspen_pims/decision_evidence.parquet', format => 'parquet');
