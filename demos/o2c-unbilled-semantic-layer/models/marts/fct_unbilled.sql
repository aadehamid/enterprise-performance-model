-- Grain: one row per unbilled ticket (BOL).
-- Certified rule (same as the unbilled_usd metric):
--   status = delivered
--   no posted invoice line as of var('as_of_date')
--   unbilled_usd = gallons_net * contract_price_usd
-- Default *published* grain (see gold_kpi_unbilled) is sold_to + terminal + day.
-- Product is a slice dimension, not part of the default published grain.
-- Ticket-level is kept here so Finance can audit a number back to a BOL.

select
    ticket_id,
    bol_ts,
    delivery_date,
    terminal_code,
    terminal_name,
    sold_to_id,
    sold_to_name,
    payer_id,
    payer_name,
    bill_to_id,
    bill_to_name,
    product_code,
    product_name,
    gallons_net,
    gallons_gross,
    temperature_f,
    status,
    contract_price_usd,
    list_price_usd,
    contract_value_usd as unbilled_usd,
    date '{{ var("as_of_date") }}' as as_of_date
from {{ ref('fct_delivery') }}
where is_unbilled
  and status = 'delivered'
