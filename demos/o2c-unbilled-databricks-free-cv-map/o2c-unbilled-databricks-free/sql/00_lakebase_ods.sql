-- =============================================================================
-- 00_lakebase_ods.sql — Act 0 ODS on Lakebase project dataexpert-day1
-- Schema o2c_unbilled only. Not the compiler. Not the Metric View.
-- Replica lands into workspace.o2c_unbilled. No Azure. No workspace URL.
--
-- Demo 2 / Track B (Databricks Free). Not demo 1. Not MetricFlow.
-- Seeds are the seven CSVs in data/. Run this in Lakebase Postgres
-- (SQL editor or psql) against project dataexpert-day1. Do not wget.
-- Idempotent: DELETE these seven tables, then INSERT. Never drop or
-- truncate any other schema.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS o2c_unbilled;

SET search_path TO o2c_unbilled;

-- ---------------------------------------------------------------------------
-- DDL — CREATE TABLE IF NOT EXISTS (Postgres types from CSV headers)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS parties (
  party_id TEXT,
  party_name TEXT,
  legal_name TEXT,
  party_class TEXT,
  tax_id TEXT,
  hq_city TEXT,
  hq_state TEXT,
  PRIMARY KEY (party_id)
);

CREATE TABLE IF NOT EXISTS party_roles (
  party_id TEXT,
  role_code TEXT,
  PRIMARY KEY (party_id, role_code)
);

CREATE TABLE IF NOT EXISTS products (
  product_code TEXT,
  product_name TEXT,
  product_family TEXT,
  contract_price_usd NUMERIC(10, 3),
  list_price_usd NUMERIC(10, 3),
  expansion_per_f NUMERIC(10, 5),
  uom TEXT,
  PRIMARY KEY (product_code)
);

CREATE TABLE IF NOT EXISTS terminals (
  terminal_code TEXT,
  terminal_name TEXT,
  city TEXT,
  state TEXT,
  mode TEXT,
  PRIMARY KEY (terminal_code)
);

CREATE TABLE IF NOT EXISTS tickets (
  ticket_id TEXT,
  bol_ts TIMESTAMPTZ,
  terminal_code TEXT,
  sold_to_id TEXT,
  payer_id TEXT,
  bill_to_id TEXT,
  product_code TEXT,
  gallons_net NUMERIC(12, 2),
  gallons_gross NUMERIC(12, 2),
  temperature_f NUMERIC(5, 1),
  status TEXT,
  PRIMARY KEY (ticket_id)
);

CREATE TABLE IF NOT EXISTS invoices (
  invoice_id TEXT,
  invoice_date DATE,
  payer_id TEXT,
  bill_to_id TEXT,
  invoice_status TEXT,
  invoice_amount_usd NUMERIC(18, 2),
  line_count INTEGER,
  PRIMARY KEY (invoice_id)
);

CREATE TABLE IF NOT EXISTS invoice_lines (
  invoice_id TEXT,
  ticket_id TEXT,
  product_code TEXT,
  line_gallons_net NUMERIC(12, 2),
  line_amount_usd NUMERIC(18, 2),
  PRIMARY KEY (invoice_id, ticket_id)
);

-- ---------------------------------------------------------------------------
-- DML — idempotent reload of data/*.csv into o2c_unbilled only
-- ---------------------------------------------------------------------------

-- Delete children first. Scoped to search_path o2c_unbilled.
DELETE FROM invoice_lines;
DELETE FROM invoices;
DELETE FROM tickets;
DELETE FROM party_roles;
DELETE FROM parties;
DELETE FROM products;
DELETE FROM terminals;

-- parties.csv → 8 row(s)
INSERT INTO parties (party_id, party_name, legal_name, party_class, tax_id, hq_city, hq_state) VALUES
  ('APEX-PAYER', 'Apex Fuels LLC', 'Apex Fuels LLC', 'marketer', '76-4412901', 'Houston', 'TX'),
  ('APEX-HOU', 'Apex Fuels Houston Rack', 'Apex Fuels LLC — Houston Rack Desk', 'wholesale_rack', '76-4412901', 'Houston', 'TX'),
  ('APEX-DAL', 'Apex Fuels Dallas Dealer', 'Apex Fuels LLC — Dallas Dealer Network', 'dealer', '76-4412901', 'Dallas', 'TX'),
  ('APEX-BILL', 'Apex Fuels LLC Accounts Payable', 'Apex Fuels LLC', 'shared_services', '76-4412901', 'Houston', 'TX'),
  ('GCA', 'Gulf Coast Aviation Inc', 'Gulf Coast Aviation Inc', 'aviation', '72-8831044', 'Houston', 'TX'),
  ('METRO-PAYER', 'Metro Lubricants', 'Metro Lubricants Company', 'distributor', '74-2291880', 'Beaumont', 'TX'),
  ('METRO-BMT', 'Metro Lubes Beaumont', 'Metro Lubricants Company — Beaumont', 'distributor_site', '74-2291880', 'Beaumont', 'TX'),
  ('METRO-BILL', 'Metro Lubricants Shared Services', 'Metro Lubricants Company', 'shared_services', '74-2291880', 'Beaumont', 'TX');

-- party_roles.csv → 10 row(s)
INSERT INTO party_roles (party_id, role_code) VALUES
  ('APEX-PAYER', 'payer'),
  ('APEX-HOU', 'sold_to'),
  ('APEX-DAL', 'sold_to'),
  ('APEX-BILL', 'bill_to'),
  ('GCA', 'payer'),
  ('GCA', 'sold_to'),
  ('GCA', 'bill_to'),
  ('METRO-PAYER', 'payer'),
  ('METRO-BMT', 'sold_to'),
  ('METRO-BILL', 'bill_to');

-- products.csv → 3 row(s)
INSERT INTO products (product_code, product_name, product_family, contract_price_usd, list_price_usd, expansion_per_f, uom) VALUES
  ('RBOB', 'RBOB Gasoline', 'gasoline', 2.184, 2.269, 0.00069, 'US gallon'),
  ('ULSD', 'Ultra-Low Sulfur Diesel', 'distillate', 2.312, 2.407, 0.00045, 'US gallon'),
  ('JETA', 'Jet-A', 'aviation', 2.156, 2.248, 0.00051, 'US gallon');

-- terminals.csv → 3 row(s)
INSERT INTO terminals (terminal_code, terminal_name, city, state, mode) VALUES
  ('HSC', 'Houston Ship Channel', 'Houston', 'TX', 'marine_rack'),
  ('DAL', 'Dallas', 'Dallas', 'TX', 'pipeline_rack'),
  ('BMT', 'Beaumont', 'Beaumont', 'TX', 'refinery_rack');

-- tickets.csv → 19 row(s)
INSERT INTO tickets (ticket_id, bol_ts, terminal_code, sold_to_id, payer_id, bill_to_id, product_code, gallons_net, gallons_gross, temperature_f, status) VALUES
  ('BOL-2026-0001', TIMESTAMPTZ '2026-06-10 08:00:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 7000.0, 7140.0, 88.0, 'delivered'),
  ('BOL-2026-0002', TIMESTAMPTZ '2026-06-12 09:00:00+00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 6400.0, 6464.0, 80.0, 'delivered'),
  ('BOL-2026-0003', TIMESTAMPTZ '2026-06-15 07:30:00+00', 'HSC', 'GCA', 'GCA', 'GCA', 'JETA', 5000.0, 5075.0, 82.0, 'delivered'),
  ('BOL-2026-0004', TIMESTAMPTZ '2026-06-20 11:00:00+00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 8000.0, 8080.0, 77.0, 'delivered'),
  ('BOL-2026-0005', TIMESTAMPTZ '2026-07-02 06:45:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 6100.0, 6222.0, 89.0, 'delivered'),
  ('BOL-2026-0101', TIMESTAMPTZ '2026-07-20 06:10:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 8000.0, 8160.0, 90.0, 'delivered'),
  ('BOL-2026-0102', TIMESTAMPTZ '2026-07-22 14:30:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 7500.0, 7605.0, 85.0, 'delivered'),
  ('BOL-2026-0103', TIMESTAMPTZ '2026-07-25 08:45:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 9200.0, 9384.0, 92.0, 'delivered'),
  ('BOL-2026-0104', TIMESTAMPTZ '2026-07-28 11:20:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 6800.0, 6884.0, 82.0, 'delivered'),
  ('BOL-2026-0105', TIMESTAMPTZ '2026-07-15 16:00:00+00', 'DAL', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 4000.0, 4080.0, 88.0, 'delivered'),
  ('BOL-2026-0201', TIMESTAMPTZ '2026-07-21 07:00:00+00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 5500.0, 5610.0, 86.0, 'delivered'),
  ('BOL-2026-0202', TIMESTAMPTZ '2026-07-24 09:15:00+00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'ULSD', 6100.0, 6171.5, 80.0, 'delivered'),
  ('BOL-2026-0203', TIMESTAMPTZ '2026-07-29 13:40:00+00', 'DAL', 'APEX-DAL', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 4800.0, 4896.0, 87.0, 'delivered'),
  ('BOL-2026-0301', TIMESTAMPTZ '2026-07-18 10:00:00+00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 9000.0, 9090.0, 78.0, 'delivered'),
  ('BOL-2026-0302', TIMESTAMPTZ '2026-07-26 15:30:00+00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 7200.0, 7272.0, 79.0, 'delivered'),
  ('BOL-2026-0401', TIMESTAMPTZ '2026-07-19 05:50:00+00', 'HSC', 'GCA', 'GCA', 'GCA', 'JETA', 6500.0, 6601.25, 84.0, 'delivered'),
  ('BOL-2026-0402', TIMESTAMPTZ '2026-07-27 12:10:00+00', 'HSC', 'GCA', 'GCA', 'GCA', 'JETA', 5800.0, 5890.7, 83.0, 'delivered'),
  ('BOL-2026-0501', TIMESTAMPTZ '2026-07-23 10:20:00+00', 'HSC', 'APEX-HOU', 'APEX-PAYER', 'APEX-BILL', 'RBOB', 5600.0, 5712.0, 91.0, 'quality_hold'),
  ('BOL-2026-0502', TIMESTAMPTZ '2026-07-30 14:00:00+00', 'BMT', 'METRO-BMT', 'METRO-PAYER', 'METRO-BILL', 'ULSD', 4300.0, 4343.0, 76.0, 'quality_hold');

-- invoices.csv → 6 row(s)
INSERT INTO invoices (invoice_id, invoice_date, payer_id, bill_to_id, invoice_status, invoice_amount_usd, line_count) VALUES
  ('INV-2026-0001', DATE '2026-06-14', 'APEX-PAYER', 'APEX-BILL', 'posted', 30084.80, 2),
  ('INV-2026-0002', DATE '2026-06-21', 'GCA', 'GCA', 'posted', 10780.00, 1),
  ('INV-2026-0003', DATE '2026-06-28', 'METRO-PAYER', 'METRO-BILL', 'posted', 18496.00, 1),
  ('INV-2026-0004', DATE '2026-07-12', 'APEX-PAYER', 'APEX-BILL', 'posted', 13322.40, 1),
  ('INV-2026-0005', DATE '2026-08-03', 'APEX-PAYER', 'APEX-BILL', 'posted', 15721.60, 1),
  ('INV-2026-0006', DATE '2026-07-31', 'APEX-PAYER', 'APEX-BILL', 'draft', 0.00, 0);

-- invoice_lines.csv → 6 row(s)
INSERT INTO invoice_lines (invoice_id, ticket_id, product_code, line_gallons_net, line_amount_usd) VALUES
  ('INV-2026-0001', 'BOL-2026-0001', 'RBOB', 7000.0, 15288.00),
  ('INV-2026-0001', 'BOL-2026-0002', 'ULSD', 6400.0, 14796.80),
  ('INV-2026-0002', 'BOL-2026-0003', 'JETA', 5000.0, 10780.00),
  ('INV-2026-0003', 'BOL-2026-0004', 'ULSD', 8000.0, 18496.00),
  ('INV-2026-0004', 'BOL-2026-0005', 'RBOB', 6100.0, 13322.40),
  ('INV-2026-0005', 'BOL-2026-0104', 'ULSD', 6800.0, 15721.60);

-- ---------------------------------------------------------------------------
-- Counts — expect 8 / 10 / 3 / 3 / 19 / 6 / 6
-- ANALYZE so n_live_tup is current; COUNT(*) is the source of truth.
-- ---------------------------------------------------------------------------

ANALYZE parties, party_roles, products, terminals, tickets, invoices, invoice_lines;

SELECT schemaname, relname, n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'o2c_unbilled'
ORDER BY relname;

SELECT 'parties' AS tbl, COUNT(*) AS n FROM parties
UNION ALL SELECT 'party_roles', COUNT(*) FROM party_roles
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'terminals', COUNT(*) FROM terminals
UNION ALL SELECT 'tickets', COUNT(*) FROM tickets
UNION ALL SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL SELECT 'invoice_lines', COUNT(*) FROM invoice_lines
ORDER BY 1;
