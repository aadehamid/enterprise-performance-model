select
    invoice_id,
    ticket_id,
    product_code,
    cast(line_gallons_net as double) as line_gallons_net,
    cast(line_amount_usd as double) as line_amount_usd
from {{ ref('invoice_lines') }}
