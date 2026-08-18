select
    l.invoice_id,
    i.invoice_date,
    i.payer_id,
    l.ticket_id,
    d.sold_to_id,
    l.product_code,
    l.line_gallons_net,
    l.line_amount_usd
from {{ ref('stg_invoice_lines') }} l
inner join {{ ref('stg_invoices') }} i
    on l.invoice_id = i.invoice_id
inner join {{ ref('stg_deliveries') }} d
    on l.ticket_id = d.ticket_id
