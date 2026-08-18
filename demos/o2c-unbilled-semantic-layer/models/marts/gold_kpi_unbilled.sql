-- Published snapshot of the *same* certified rule, rolled to the default
-- published grain: sold_to + terminal + day, as_of 2026-08-01.
-- This is not a second formula — it selects from fct_unbilled.

select
    sold_to_id,
    sold_to_name,
    terminal_code,
    terminal_name,
    delivery_date,
    as_of_date,
    sum(gallons_net) as unbilled_gallons_net,
    sum(unbilled_usd) as unbilled_usd,
    count(*) as ticket_count
from {{ ref('fct_unbilled') }}
group by
    sold_to_id,
    sold_to_name,
    terminal_code,
    terminal_name,
    delivery_date,
    as_of_date
