-- 02_replica.sql: one replica table per source table, read from the Parquet files the replication landed in the
-- volume. Each keeps the source's columns plus _change_ts and _replicated_at. Mirrors synapse_dev.replica_* (EPM-DEC-001-0097).

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_currency AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_currency.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_unitofmeasure AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_unitofmeasure.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_pricebatch AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_pricebatch.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_pricesheet AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_pricesheet.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_pricegroup AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_pricegroup.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_priceassessmentgroup AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_priceassessmentgroup.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mips.mips_priceassessment AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mips/mips_priceassessment.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mpr.pricemaster AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mpr/pricemaster.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_mpr.pricedetail AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/mpr/pricedetail.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_kittyhawk.priceservice AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/kittyhawk/priceservice.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_kittyhawk.holidaycalendar AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/kittyhawk/holidaycalendar.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_kittyhawk.deliveryperiodcategory AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/kittyhawk/deliveryperiodcategory.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_ctrm.deal AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/ctrm/deal.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_ctrm.movement AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/ctrm/movement.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_planning.plan_target AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/planning/plan_target.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_prodacct.refinery AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/prodacct/refinery.parquet', format => 'parquet');

CREATE OR REPLACE TABLE ${catalog}.replica_prodacct.refinery_daily AS
SELECT * FROM read_files('/Volumes/${catalog}/replica_landing/raw/prodacct/refinery_daily.parquet', format => 'parquet');
