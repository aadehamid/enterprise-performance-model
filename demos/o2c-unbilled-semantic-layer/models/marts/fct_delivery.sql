select
    b.ticket_id,
    b.bol_ts,
    b.delivery_date,
    b.terminal_code,
    t.terminal_name,
    b.sold_to_id,
    sold.party_name as sold_to_name,
    b.payer_id,
    payer.party_name as payer_name,
    b.bill_to_id,
    bill.party_name as bill_to_name,
    b.product_code,
    p.product_name,
    b.gallons_net,
    b.gallons_gross,
    b.temperature_f,
    b.status,
    b.is_billed,
    b.is_unbilled,
    b.invoice_id,
    b.invoice_date,
    p.contract_price_usd,
    p.list_price_usd,
    round(b.gallons_net * p.contract_price_usd, 2) as contract_value_usd,
    round(b.gallons_gross * p.list_price_usd, 2) as sloppy_value_usd
from {{ ref('int_ticket_billing') }} b
inner join {{ ref('stg_parties') }} sold
    on b.sold_to_id = sold.party_id
inner join {{ ref('stg_parties') }} payer
    on b.payer_id = payer.party_id
inner join {{ ref('stg_parties') }} bill
    on b.bill_to_id = bill.party_id
inner join {{ ref('stg_terminals') }} t
    on b.terminal_code = t.terminal_code
inner join {{ ref('stg_products') }} p
    on b.product_code = p.product_code
