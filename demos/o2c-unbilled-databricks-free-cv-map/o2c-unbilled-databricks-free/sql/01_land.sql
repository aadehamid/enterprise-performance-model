-- =============================================================================
-- 01_land.sql — schema, volume, then land the seven CSVs
-- Demo 2 (Databricks Free). Not Track A. No DuckDB, no dbt, no MetricFlow.
--
-- PLACEHOLDERS — find/replace in this file (and 02/03/04) before you run:
--   {{catalog}}  →  workspace     (or the catalog name under Catalog in the sidebar)
--   {{schema}}   →  o2c_unbilled  (or `default` if CREATE SCHEMA is denied)
--
-- Free Edition facts this file relies on (official, 2026):
--   * Unity Catalog on by default; workspace catalog + default schema.
--   * Free users have USE CATALOG / USE SCHEMA / WRITE VOLUME on those by default.
--   * Outbound internet restricted — upload CSVs via the workspace UI. Do not wget.
--   * One SQL warehouse, 2X-Small. Attach the default Serverless Starter Warehouse.
--
-- Untested on workspace — needs Hamid URL.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Part A — run this first (before any upload)
-- ---------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS {{catalog}}.{{schema}}
COMMENT 'O2C Unbilled USD demo 2 — Databricks Free. Not the Track A DuckDB pack.';

-- Volume is the only landing zone we use. Free has no custom storage.
CREATE VOLUME IF NOT EXISTS {{catalog}}.{{schema}}.landing
COMMENT 'Upload the seven CSVs from data/ here via Catalog Explorer. Do not wget.';

-- Confirm you are on the Free warehouse (2XS). If this fails, you are not
-- attached to a SQL warehouse with CAN USE.
SELECT current_catalog() AS catalog_name,
       current_schema()  AS schema_name,
       current_user()    AS ran_as;

-- ---------------------------------------------------------------------------
-- STOP. Upload the seven files from data/ into:
--   /Volumes/{{catalog}}/{{schema}}/landing/
--
-- Catalog Explorer: {{catalog}} → {{schema}} → Volumes → landing → Upload.
-- Filenames must match exactly (tickets.csv, invoices.csv, …).
-- Then run Part B.
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- Part B — run after the UI upload
-- read_files is Databricks SQL. Infer + CAST so money/dates stay typed.
-- If read_files is refused on this warehouse, use the COPY INTO block at the
-- bottom (commented). Untested on workspace — needs Hamid URL.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_parties AS
SELECT
  CAST(party_id AS STRING)     AS party_id,
  CAST(party_name AS STRING)   AS party_name,
  CAST(legal_name AS STRING)   AS legal_name,
  CAST(party_class AS STRING)  AS party_class,
  CAST(tax_id AS STRING)       AS tax_id,
  CAST(hq_city AS STRING)      AS hq_city,
  CAST(hq_state AS STRING)     AS hq_state
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/parties.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_party_roles AS
SELECT
  CAST(party_id AS STRING)   AS party_id,
  CAST(role_code AS STRING)  AS role_code
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/party_roles.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_products AS
SELECT
  CAST(product_code AS STRING)                         AS product_code,
  CAST(product_name AS STRING)                         AS product_name,
  CAST(product_family AS STRING)                       AS product_family,
  CAST(contract_price_usd AS DECIMAL(10, 3))           AS contract_price_usd,
  CAST(list_price_usd AS DECIMAL(10, 3))               AS list_price_usd,
  CAST(expansion_per_f AS DECIMAL(10, 5))              AS expansion_per_f,
  CAST(uom AS STRING)                                  AS uom
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/products.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_terminals AS
SELECT
  CAST(terminal_code AS STRING) AS terminal_code,
  CAST(terminal_name AS STRING) AS terminal_name,
  CAST(city AS STRING)          AS city,
  CAST(state AS STRING)         AS state,
  CAST(mode AS STRING)          AS mode
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/terminals.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_tickets AS
SELECT
  CAST(ticket_id AS STRING)            AS ticket_id,
  CAST(bol_ts AS TIMESTAMP)            AS bol_ts,
  CAST(terminal_code AS STRING)        AS terminal_code,
  CAST(sold_to_id AS STRING)           AS sold_to_id,
  CAST(payer_id AS STRING)             AS payer_id,
  CAST(bill_to_id AS STRING)           AS bill_to_id,
  CAST(product_code AS STRING)         AS product_code,
  CAST(gallons_net AS DECIMAL(12, 2))  AS gallons_net,
  CAST(gallons_gross AS DECIMAL(12, 2)) AS gallons_gross,
  CAST(temperature_f AS DECIMAL(5, 1)) AS temperature_f,
  CAST(status AS STRING)               AS status
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/tickets.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_invoices AS
SELECT
  CAST(invoice_id AS STRING)                    AS invoice_id,
  CAST(invoice_date AS DATE)                    AS invoice_date,
  CAST(payer_id AS STRING)                      AS payer_id,
  CAST(bill_to_id AS STRING)                    AS bill_to_id,
  CAST(invoice_status AS STRING)                AS invoice_status,
  CAST(invoice_amount_usd AS DECIMAL(18, 2))    AS invoice_amount_usd,
  CAST(line_count AS INT)                       AS line_count
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/invoices.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

CREATE OR REPLACE TABLE {{catalog}}.{{schema}}.raw_invoice_lines AS
SELECT
  CAST(invoice_id AS STRING)                   AS invoice_id,
  CAST(ticket_id AS STRING)                    AS ticket_id,
  CAST(product_code AS STRING)                 AS product_code,
  CAST(line_gallons_net AS DECIMAL(12, 2))     AS line_gallons_net,
  CAST(line_amount_usd AS DECIMAL(18, 2))      AS line_amount_usd
FROM read_files(
  '/Volumes/{{catalog}}/{{schema}}/landing/invoice_lines.csv',
  format => 'csv',
  header => true,
  inferSchema => true
);

-- Sanity: 8 parties, 19 tickets, 6 invoices, 6 lines.
SELECT 'raw_parties' AS tbl, COUNT(*) AS n FROM {{catalog}}.{{schema}}.raw_parties
UNION ALL
SELECT 'raw_party_roles', COUNT(*) FROM {{catalog}}.{{schema}}.raw_party_roles
UNION ALL
SELECT 'raw_products', COUNT(*) FROM {{catalog}}.{{schema}}.raw_products
UNION ALL
SELECT 'raw_terminals', COUNT(*) FROM {{catalog}}.{{schema}}.raw_terminals
UNION ALL
SELECT 'raw_tickets', COUNT(*) FROM {{catalog}}.{{schema}}.raw_tickets
UNION ALL
SELECT 'raw_invoices', COUNT(*) FROM {{catalog}}.{{schema}}.raw_invoices
UNION ALL
SELECT 'raw_invoice_lines', COUNT(*) FROM {{catalog}}.{{schema}}.raw_invoice_lines
ORDER BY 1;

-- ---------------------------------------------------------------------------
-- Fallback if read_files is unavailable on this warehouse (untested).
-- Uncomment, run after Part A + upload. Explicit columns, then COPY INTO.
-- ---------------------------------------------------------------------------
--
-- CREATE TABLE IF NOT EXISTS {{catalog}}.{{schema}}.raw_tickets (
--   ticket_id STRING,
--   bol_ts TIMESTAMP,
--   terminal_code STRING,
--   sold_to_id STRING,
--   payer_id STRING,
--   bill_to_id STRING,
--   product_code STRING,
--   gallons_net DECIMAL(12, 2),
--   gallons_gross DECIMAL(12, 2),
--   temperature_f DECIMAL(5, 1),
--   status STRING
-- );
--
-- COPY INTO {{catalog}}.{{schema}}.raw_tickets
-- FROM '/Volumes/{{catalog}}/{{schema}}/landing/tickets.csv'
-- FILEFORMAT = CSV
-- FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
-- COPY_OPTIONS ('force' = 'true');
