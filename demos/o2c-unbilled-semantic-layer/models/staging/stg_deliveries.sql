select
    ticket_id,
    cast(bol_ts as timestamp) as bol_ts,
    cast(bol_ts as date) as delivery_date,
    terminal_code,
    sold_to_id,
    payer_id,
    bill_to_id,
    product_code,
    cast(gallons_net as double) as gallons_net,
    cast(gallons_gross as double) as gallons_gross,
    cast(temperature_f as double) as temperature_f,
    lower(status) as status
from {{ ref('deliveries') }}
