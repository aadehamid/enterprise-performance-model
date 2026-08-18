-- =============================================================================
-- 04_queries.sql — Act 1 conflict, Act 2 MEASURE(), Act 3 SELECT * refused
--
-- Honest seats: fct_unbilled holds the population (ticket gate +
-- gallons_net * contract_price). The Metric View compiles SUM/GROUP BY
-- (MEASURE()). This file does NOT re-encode the valuation. Act 1 groups
-- the population; Act 2 consumes MEASURE().
--
-- PLACEHOLDERS: {{catalog}} = workspace, {{schema}} = o2c_unbilled
-- =============================================================================


-- ##########################################################################
-- ACT 1 — two workbooks, both titled "Unbilled USD", both against the fact.
-- Grand totals MATCH ($179,934.00). Rows FIGHT.
-- That is the grain lesson: customer_grain ∈ {payer, sold-to, site}.
-- ##########################################################################

-- Report A: group the population ticket set by sold-to, label it "customer".
-- Expect 4 rows, ORDER BY usd DESC: Houston Rack $79,362.40,
-- Metro Lubes Beaumont $37,454.40, Dallas Dealer $36,598.40,
-- Gulf Coast Aviation $26,518.80.
SELECT
  sold_to_name AS customer,
  SUM(unbilled_usd) AS unbilled_usd,
  COUNT(*) AS tickets
FROM {{catalog}}.{{schema}}.fct_unbilled
GROUP BY sold_to_name
ORDER BY unbilled_usd DESC;

-- Report B: the SAME tickets, grouped by payer, also labeled "customer".
-- Expect 3 rows. Apex Fuels LLC $115,960.80 = Houston + Dallas.
-- Metro Lubricants $37,454.40. Gulf Coast Aviation $26,518.80.
SELECT
  payer_name AS customer,
  SUM(unbilled_usd) AS unbilled_usd,
  COUNT(*) AS tickets
FROM {{catalog}}.{{schema}}.fct_unbilled
GROUP BY payer_name
ORDER BY unbilled_usd DESC;

-- Teaching point: both reports are honest about the ticket set and the
-- column they sum. They still lie about the word "customer".
-- If a slide adds Apex Fuels LLC (payer) to Houston Rack + Dallas Dealer
-- (sold-to), Unbilled USD is double-counted. Aviation matches on both
-- reports because GCA is payer AND sold-to (same org).


-- ##########################################################################
-- ACT 2 — same number through the Metric View. MEASURE() at each grain.
-- The compiler writes the GROUP BY. You do not write a second formula.
-- Official rule: every measure uses MEASURE(); SELECT * is refused.
-- https://docs.databricks.com/aws/en/uc-semantics/metric-views/query
-- ##########################################################################

-- Unsliced — must equal Act 1 grand total $179,934.00 / 12 tickets.
SELECT
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {{catalog}}.{{schema}}.unbilled_usd;

-- Sold-to grain — must match Report A row-for-row.
SELECT
  sold_to,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {{catalog}}.{{schema}}.unbilled_usd
GROUP BY sold_to
ORDER BY unbilled_usd DESC;

-- Payer grain — must match Report B row-for-row.
SELECT
  payer,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {{catalog}}.{{schema}}.unbilled_usd
GROUP BY payer
ORDER BY unbilled_usd DESC;

-- Site grain — same ticket set, third customer_grain.
-- HSC $97,145.20 (6) / DAL $45,334.40 (4) / BMT $37,454.40 (2).
SELECT
  site,
  site_name,
  MEASURE(unbilled_usd)          AS unbilled_usd,
  MEASURE(unbilled_ticket_count) AS tickets
FROM {{catalog}}.{{schema}}.unbilled_usd
GROUP BY site, site_name
ORDER BY unbilled_usd DESC;

-- The three grains AGREE on the grand total because they share one measure.
-- They DISAGREE on the row labels because you chose a different group-by.
-- That is what "the formula stays still" means.


-- ##########################################################################
-- ACT 3 — SELECT * on a metric view is refused.
-- Official: "Because measures require the MEASURE() function to evaluate
-- properly, you must specify individual columns rather than using SELECT *."
-- Expect an error. That error is the teaching point, not a bug.
-- ##########################################################################

-- SELECT * FROM {{catalog}}.{{schema}}.unbilled_usd;
--
-- Uncomment the line above after Act 2. Document the error message you get.
-- Then go back to MEASURE(unbilled_usd).


-- Optional sloppy twin (not the certified metric). Same title, different
-- number: ambient gallons * list price, includes quality-hold, mixes
-- sold-to labels (Apex) with the payer label (Metro). Leave it here so
-- you can see why a consumption semantic layer replaces workbooks instead of averaging
-- them. Do not put this expression in the Metric View.
SELECT
  CASE
    WHEN t.sold_to_id IN ('APEX-HOU', 'APEX-DAL') THEN sold.party_name
    WHEN t.sold_to_id = 'METRO-BMT' THEN payer.party_name
    ELSE sold.party_name
  END AS customer,
  SUM(CAST(t.gallons_gross * pr.list_price_usd AS DECIMAL(18, 2))) AS unbilled_usd
FROM {{catalog}}.{{schema}}.raw_tickets t
INNER JOIN {{catalog}}.{{schema}}.raw_products pr
  ON t.product_code = pr.product_code
INNER JOIN {{catalog}}.{{schema}}.raw_parties sold
  ON t.sold_to_id = sold.party_id
INNER JOIN {{catalog}}.{{schema}}.raw_parties payer
  ON t.payer_id = payer.party_id
LEFT JOIN (
  SELECT l.ticket_id
  FROM {{catalog}}.{{schema}}.raw_invoice_lines l
  INNER JOIN {{catalog}}.{{schema}}.raw_invoices i
    ON l.invoice_id = i.invoice_id
  WHERE i.invoice_status = 'posted'
    AND i.invoice_date <= DATE '2026-08-01'
) billed
  ON t.ticket_id = billed.ticket_id
WHERE billed.ticket_id IS NULL
GROUP BY 1
ORDER BY 2 DESC;
