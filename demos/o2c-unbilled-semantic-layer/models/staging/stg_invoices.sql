select
    invoice_id,
    cast(invoice_date as date) as invoice_date,
    payer_id,
    bill_to_id,
    lower(invoice_status) as invoice_status,
    cast(invoice_amount_usd as double) as invoice_amount_usd,
    cast(line_count as integer) as line_count
from {{ ref('invoices') }}
