-- quality_hold tickets must never appear in the certified unbilled fact.
select ticket_id
from {{ ref('fct_unbilled') }}
where status != 'delivered'
