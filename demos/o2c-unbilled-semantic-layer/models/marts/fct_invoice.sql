select
    i.invoice_id,
    i.invoice_date,
    i.payer_id,
    payer.party_name as payer_name,
    i.bill_to_id,
    bill.party_name as bill_to_name,
    i.invoice_status,
    i.invoice_amount_usd,
    i.line_count
from {{ ref('stg_invoices') }} i
inner join {{ ref('stg_parties') }} payer
    on i.payer_id = payer.party_id
inner join {{ ref('stg_parties') }} bill
    on i.bill_to_id = bill.party_id
