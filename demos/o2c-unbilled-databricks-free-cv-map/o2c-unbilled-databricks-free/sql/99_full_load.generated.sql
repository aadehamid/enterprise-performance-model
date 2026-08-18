-- =============================================================================
-- 99_full_load.generated.sql — single-file live load for Databricks Free
-- GENERATED 2026-08-14 from data/*.csv + 02/03/04 logic.
-- Placeholders already substituted: catalog=workspace, schema=o2c_unbilled.
--
-- Do not edit by hand for a re-run: regenerate from the CSVs, or re-run this file.
-- Human-authored sources stay in 01_land.sql / 02_facts.sql / 03_metric_view.sql /
-- 04_queries.sql (those still use {{catalog}} / {{schema}}).
--
-- Why VALUES, not Volume upload: Free outbound internet is restricted and UI
-- CSV upload is flaky. CREATE OR REPLACE TABLE … AS SELECT * FROM VALUES …
-- lands the seven seeds without wget or Catalog Explorer upload.
--
-- Metric View dialect: version 0.1 (live-proven 2026-08-14 on Free).
-- Same 0.1 as sql/03_metric_view.sql and scripts/04_metric_view.py
-- (fields + measures only; no YAML 1.1 comment / display_name / synonyms).
-- SELECT * is refused; every measure uses MEASURE().
--
-- No workspace URL. No PAT. Not Azure. Not demo 1.
-- =============================================================================

-- Schema may already exist (CREATE IF NOT EXISTS is a no-op then).
CREATE SCHEMA IF NOT EXISTS workspace.o2c_unbilled
COMMENT 'O2C Unbilled USD demo 2 — Databricks Free. Not the Track A DuckDB pack.';

-- ---------------------------------------------------------------------------
-- Raw tables from data/*.csv (typed, same CASTs as 01_land.sql)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_parties AS
SELECT
  CAST(party_id AS STRING)    AS party_id,
  CAST(party_name AS STRING)  AS party_name,
  CAST(legal_name AS STRING)  AS legal_name,
  CAST(party_class AS STRING) AS party_class,
  CAST(tax_id AS STRING)      AS tax_id,
  CAST(hq_city AS STRING)     AS hq_city,
  CAST(hq_state AS STRING)    AS hq_state
FROM VALUES
  ('APEX-PAYER', 'Apex Fuels LLC', 'Apex Fuels LLC', 'marketer', '76-4412901', 'Houston', 'TX'),
  ('APEX-HOU', 'Apex Fuels Houston Rack', 'Apex Fuels LLC — Houston Rack Desk', 'wholesale_rack', '76-4412901', 'Houston', 'TX'),
  ('APEX-DAL', 'Apex Fuels Dallas Dealer', 'Apex Fuels LLC — Dallas Dealer Network', 'dealer', '76-4412901', 'Dallas', 'TX'),
  ('APEX-BILL', 'Apex Fuels LLC Accounts Payable', 'Apex Fuels LLC', 'shared_services', '76-4412901', 'Houston', 'TX'),
  ('GCA', 'Gulf Coast Aviation Inc', 'Gulf Coast Aviation Inc', 'aviation', '72-8831044', 'Houston', 'TX'),
  ('METRO-PAYER', 'Metro Lubricants', 'Metro Lubricants Company', 'distributor', '74-2291880', 'Beaumont', 'TX'),
  ('METRO-BMT', 'Metro Lubes Beaumont', 'Metro Lubricants Company — Beaumont', 'distributor_site', '74-2291880', 'Beaumont', 'TX'),
  ('METRO-BILL', 'Metro Lubricants Shared Services', 'Metro Lubricants Company', 'shared_services', '74-2291880', 'Beaumont', 'TX')
AS v(party_id, party_name, legal_name, party_class, tax_id, hq_city, hq_state);

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_party_roles AS
SELECT
  CAST(party_id AS STRING)  AS party_id,
  CAST(role_code AS STRING) AS role_code
FROM VALUES
  ('APEX-PAYER', 'payer'),
  ('APEX-HOU', 'sold_to'),
  ('APEX-DAL', 'sold_to'),
  ('APEX-BILL', 'bill_to'),
  ('GCA', 'payer'),
  ('GCA', 'sold_to'),
  ('GCA', 'bill_to'),
  ('METRO-PAYER', 'payer'),
  ('METRO-BMT', 'sold_to'),
  ('METRO-BILL', 'bill_to')
AS v(party_id, role_code);

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_products AS
SELECT
  CAST(product_code AS STRING)               AS product_code,
  CAST(product_name AS STRING)               AS product_name,
  CAST(product_family AS STRING)             AS product_family,
  CAST(contract_price_usd AS DECIMAL(10, 3)) AS contract_price_usd,
  CAST(list_price_usd AS DECIMAL(10, 3))     AS list_price_usd,
  CAST(expansion_per_f AS DECIMAL(10, 5))    AS expansion_per_f,
  CAST(uom AS STRING)                        AS uom
FROM VALUES
  ('RBOB', 'RBOB Gasoline', 'gasoline', 2.184, 2.269, 0.00069, 'US gallon'),
  ('ULSD', 'Ultra-Low Sulfur Diesel', 'distillate', 2.312, 2.407, 0.00045, 'US gallon'),
  ('JETA', 'Jet-A', 'aviation', 2.156, 2.248, 0.00051, 'US gallon')
AS v(product_code, product_name, product_family, contract_price_usd, list_price_usd, expansion_per_f, uom);

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_terminals AS
SELECT
  CAST(terminal_code AS STRING) AS terminal_code,
  CAST(terminal_name AS STRING) AS terminal_name,
  CAST(city AS STRING)          AS city,
  CAST(state AS STRING)         AS state,
  CAST(mode AS STRING)          AS mode
FROM VALUES
  ('HSC', 'Houston Ship Channel', 'Houston', 'TX', 'marine_rack'),
  ('DAL', 'Dallas', 'Dallas', 'TX', 'pipeline_rack'),
  ('BMT', 'Beaumont', 'Beaumont', 'TX', 'refinery_rack')
AS v(terminal_code, terminal_name, city, state, mode);

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_tickets AS
SELECT
  CAST(ticket_id AS STRING)             AS ticket_id,
  CAST(bol_ts AS TIMESTAMP)             AS bol_ts,
  CAST(terminal_code AS STRING)         AS terminal_code,
  CAST(sold_to_id AS STRING)            AS sold_to_id,
  CAST(payer_id AS STRING)              AS payer_id,
  CAST(bill_to_id AS STRING)            AS bill_to_id,
  CAST(product_code AS STRING)          AS product_code,
  CAST(gallons_net AS DECIMAL(12, 2))   AS gallons_net,
  CAST(gallons_gross AS DECIMAL(12, 2)) AS gallons_gross,
  CAST(temperature_f AS DECIMAL(5, 1))  AS temperature_f,
  CAST(status AS STRING)                AS status
FROM VALUES
  ('BOL-2026-0001', TIMESTAMP '2026-06-10 08:00:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 7000.0, 7140.0, 88.0, 'delivered'),
  ('BOL-2026-0002', TIMESTAMP '2026-06-12 09:00:00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 6400.0, 6464.0, 80.0, 'delivered'),
  ('BOL-2026-0003', TIMESTAMP '2026-06-15 07:30:00', 'HSC', 'GCA', 'GCA', 'GCA', 'JETA', 5000.0, 5075.0, 82.0, 'delivered'),
  ('BOL-2026-0004', TIMESTAMP '2026-06-20 11:00:00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 8000.0, 8080.0, 77.0, 'delivered'),
  ('BOL-2026-0005', TIMESTAMP '2026-07-02 06:45:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 6100.0, 6222.0, 89.0, 'delivered'),
  ('BOL-2026-0101', TIMESTAMP '2026-07-20 06:10:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 8000.0, 8160.0, 90.0, 'delivered'),
  ('BOL-2026-0102', TIMESTAMP '2026-07-22 14:30:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 7500.0, 7605.0, 85.0, 'delivered'),
  ('BOL-2026-0103', TIMESTAMP '2026-07-25 08:45:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 9200.0, 9384.0, 92.0, 'delivered'),
  ('BOL-2026-0104', TIMESTAMP '2026-07-28 11:20:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 6800.0, 6884.0, 82.0, 'delivered'),
  ('BOL-2026-0105', TIMESTAMP '2026-07-15 16:00:00', 'DAL', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 4000.0, 4080.0, 88.0, 'delivered'),
  ('BOL-2026-0201', TIMESTAMP '2026-07-21 07:00:00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 5500.0, 5610.0, 86.0, 'delivered'),
  ('BOL-2026-0202', TIMESTAMP '2026-07-24 09:15:00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 6100.0, 6171.5, 80.0, 'delivered'),
  ('BOL-2026-0203', TIMESTAMP '2026-07-29 13:40:00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 4800.0, 4896.0, 87.0, 'delivered'),
  ('BOL-2026-0301', TIMESTAMP '2026-07-18 10:00:00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 9000.0, 9090.0, 78.0, 'delivered'),
  ('BOL-2026-0302', TIMESTAMP '2026-07-26 15:30:00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 7200.0, 7272.0, 79.0, 'delivered'),
  ('BOL-2026-0401', TIMESTAMP '2026-07-19 05:50:00', 'HSC', 'GCA', 'GCA', 'GCA', 'JETA', 6500.0, 6601.25, 84.0, 'delivered'),
  ('BOL-2026-0402', TIMESTAMP '2026-07-27 12:10:00', 'HSC', 'GCA', 'GCA', 'GCA', 'JETA', 5800.0, 5890.7, 83.0, 'delivered'),
  ('BOL-2026-0501', TIMESTAMP '2026-07-23 10:20:00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 5600.0, 5712.0, 91.0, 'quality_hold'),
  ('BOL-2026-0502', TIMESTAMP '2026-07-30 14:00:00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 4300.0, 4343.0, 76.0, 'quality_hold')
AS v(ticket_id, bol_ts, terminal_code, sold_to_id, payer_id, bill_to_id, product_code, gallons_net, gallons_gross, temperature_f, status);

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_invoices AS
SELECT
  CAST(invoice_id AS STRING)                 AS invoice_id,
  CAST(invoice_date AS DATE)                 AS invoice_date,
  CAST(payer_id AS STRING)                   AS payer_id,
  CAST(bill_to_id AS STRING)                 AS bill_to_id,
  CAST(invoice_status AS STRING)             AS invoice_status,
  CAST(invoice_amount_usd AS DECIMAL(18, 2)) AS invoice_amount_usd,
  CAST(line_count AS INT)                    AS line_count
FROM VALUES
  ('INV-2026-0001', DATE '2026-06-14', 'APEX-PAYER', 'APEX-BILL', 'posted', 30084.80, 2),
  ('INV-2026-0002', DATE '2026-06-21', 'GCA', 'GCA', 'posted', 10780.00, 1),
  ('INV-2026-0003', DATE '2026-06-28', 'METRO-PAYER', 'METRO-BILL', 'posted', 18496.00, 1),
  ('INV-2026-0004', DATE '2026-07-12', 'APEX-PAYER', 'APEX-BILL', 'posted', 13322.40, 1),
  ('INV-2026-0005', DATE '2026-08-03', 'APEX-PAYER', 'APEX-BILL', 'posted', 15721.60, 1),
  ('INV-2026-0006', DATE '2026-07-31', 'APEX-PAYER', 'APEX-BILL', 'draft', 0.00, 0)
AS v(invoice_id, invoice_date, payer_id, bill_to_id, invoice_status, invoice_amount_usd, line_count);

CREATE OR REPLACE TABLE workspace.o2c_unbilled.raw_invoice_lines AS
SELECT
  CAST(invoice_id AS STRING)               AS invoice_id,
  CAST(ticket_id AS STRING)                AS ticket_id,
  CAST(product_code AS STRING)             AS product_code,
  CAST(line_gallons_net AS DECIMAL(12, 2)) AS line_gallons_net,
  CAST(line_amount_usd AS DECIMAL(18, 2))  AS line_amount_usd
FROM VALUES
  ('INV-2026-0001', 'BOL-2026-0001', 'RBOB', 7000.0, 15288.00),
  ('INV-2026-0001', 'BOL-2026-0002', 'ULSD', 6400.0, 14796.80),
  ('INV-2026-0002', 'BOL-2026-0003', 'JETA', 5000.0, 10780.00),
  ('INV-2026-0003', 'BOL-2026-0004', 'ULSD', 8000.0, 18496.00),
  ('INV-2026-0004', 'BOL-2026-0005', 'RBOB', 6100.0, 13322.40),
  ('INV-2026-0005', 'BOL-2026-0104', 'ULSD', 6800.0, 15721.60)
AS v(invoice_id, ticket_id, product_code, line_gallons_net, line_amount_usd);

-- Sanity: 8 parties, 10 roles, 3 products, 3 terminals, 19 tickets, 6 invoices, 6 lines.
SELECT 'raw_parties' AS tbl, COUNT(*) AS n FROM workspace.o2c_unbilled.raw_parties
UNION ALL
SELECT 'raw_party_roles', COUNT(*) FROM workspace.o2c_unbilled.raw_party_roles
UNION ALL
SELECT 'raw_products', COUNT(*) FROM workspace.o2c_unbilled.raw_products
UNION ALL
SELECT 'raw_terminals', COUNT(*) FROM workspace.o2c_unbilled.raw_terminals
UNION ALL
SELECT 'raw_tickets', COUNT(*) FROM workspace.o2c_unbilled.raw_tickets
UNION ALL
SELECT 'raw_invoices', COUNT(*) FROM workspace.o2c_unbilled.raw_invoices
UNION ALL
SELECT 'raw_invoice_lines', COUNT(*) FROM workspace.o2c_unbilled.raw_invoice_lines
ORDER BY 1;

-- ---------------------------------------------------------------------------
-- 02_facts.sql logic — star-ish dims + certified unbilled fact
-- fct_unbilled is the certified *population* at ticket grain (delivered,
-- no posted invoice as of 2026-08-01, quality-hold excluded,
-- unbilled_usd = gallons_net * contract_price). Not a second published formula.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE TABLE workspace.o2c_unbilled.dim_party AS
SELECT
  p.party_id,
  p.party_name,
  p.legal_name,
  p.party_class,
  p.tax_id,
  p.hq_city,
  p.hq_state
FROM workspace.o2c_unbilled.raw_parties p;

CREATE OR REPLACE TABLE workspace.o2c_unbilled.br_party_role AS
SELECT party_id, role_code
FROM workspace.o2c_unbilled.raw_party_roles;

CREATE OR REPLACE TABLE workspace.o2c_unbilled.dim_site AS
SELECT
  terminal_code AS site_code,
  terminal_name AS site_name,
  city,
  state,
  mode
FROM workspace.o2c_unbilled.raw_terminals;

CREATE OR REPLACE TABLE workspace.o2c_unbilled.dim_product AS
SELECT
  product_code,
  product_name,
  product_family,
  contract_price_usd,
  list_price_usd,
  uom
FROM workspace.o2c_unbilled.raw_products;

CREATE OR REPLACE TABLE workspace.o2c_unbilled.fct_unbilled AS
WITH posted_as_of AS (
  SELECT
    l.ticket_id
  FROM workspace.o2c_unbilled.raw_invoice_lines l
  INNER JOIN workspace.o2c_unbilled.raw_invoices i
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
FROM workspace.o2c_unbilled.raw_tickets t
INNER JOIN workspace.o2c_unbilled.raw_products pr
  ON t.product_code = pr.product_code
INNER JOIN workspace.o2c_unbilled.raw_parties sold
  ON t.sold_to_id = sold.party_id
INNER JOIN workspace.o2c_unbilled.raw_parties payer
  ON t.payer_id = payer.party_id
INNER JOIN workspace.o2c_unbilled.raw_parties bill
  ON t.bill_to_id = bill.party_id
INNER JOIN workspace.o2c_unbilled.dim_site s
  ON t.terminal_code = s.site_code
LEFT JOIN posted_as_of posted
  ON t.ticket_id = posted.ticket_id
WHERE t.status = 'delivered'
  AND posted.ticket_id IS NULL;

-- Expect 12 tickets, $179,934.00.
SELECT
  COUNT(*)                         AS unbilled_tickets,
  SUM(unbilled_usd)                AS unbilled_usd,
  COUNT(DISTINCT sold_to_id)       AS sold_to_keys,
  COUNT(DISTINCT payer_id)         AS payer_keys,
  COUNT(DISTINCT site_code)        AS site_keys
FROM workspace.o2c_unbilled.fct_unbilled;

-- ---------------------------------------------------------------------------
-- 03_metric_view.sql logic — version 0.1 (live-proven 2026-08-14 on Free).
-- Same 0.1 as sql/03_metric_view.sql / scripts/04_metric_view.py.
-- Fields needed by Act 2 queries are included (site_name, ticket count).
-- Paste this block as one statement. Monaco auto-indent can mangle YAML;
-- set the editor value rather than typing line-by-line if indent breaks.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW workspace.o2c_unbilled.unbilled_usd
WITH METRICS
LANGUAGE YAML
AS $$
version: 0.1
source: workspace.o2c_unbilled.fct_unbilled
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

-- ---------------------------------------------------------------------------
-- 04_queries.sql — Act 1 conflict + Act 2 MEASURE()
-- ---------------------------------------------------------------------------

-- ACT 1 Report A: sold-to labeled "customer". Expect 4 rows, $179,934.00.
SELECT
  sold_to_name AS customer,
  SUM(unbilled_usd) AS unbilled_usd,
  COUNT(*) AS tickets
FROM workspace.o2c_unbilled.fct_unbilled
GROUP BY sold_to_name
ORDER BY unbilled_usd DESC;

-- ACT 1 Report B: payer labeled "customer". Expect 3 rows. Apex = Houston + Dallas.
SELECT
  payer_name AS customer,
  SUM(unbilled_usd) AS unbilled_usd,
  COUNT(*) AS tickets
FROM workspace.o2c_unbilled.fct_unbilled
GROUP BY payer_name
ORDER BY unbilled_usd DESC;

-- ACT 2 unsliced — must equal Act 1 grand total $179,934.00 / 12 tickets.
SELECT
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM workspace.o2c_unbilled.unbilled_usd;

-- ACT 2 sold-to grain — must match Report A row-for-row.
SELECT
  sold_to,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM workspace.o2c_unbilled.unbilled_usd
GROUP BY sold_to
ORDER BY unbilled_usd DESC;

-- ACT 2 payer grain — must match Report B row-for-row.
SELECT
  payer,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM workspace.o2c_unbilled.unbilled_usd
GROUP BY payer
ORDER BY unbilled_usd DESC;

-- ACT 2 site grain — HSC $97,145.20 (6) / DAL $45,334.40 (4) / BMT $37,454.40 (2).
SELECT
  site,
  site_name,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM workspace.o2c_unbilled.unbilled_usd
GROUP BY site, site_name
ORDER BY unbilled_usd DESC;
