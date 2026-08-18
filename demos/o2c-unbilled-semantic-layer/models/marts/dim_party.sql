select
    party_id,
    party_name,
    legal_name,
    party_class,
    tax_id,
    hq_city,
    hq_state
from {{ ref('stg_parties') }}
