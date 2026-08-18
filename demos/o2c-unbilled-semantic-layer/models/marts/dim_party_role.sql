select
    r.party_id,
    p.party_name,
    r.role_code,
    p.party_class
from {{ ref('stg_party_roles') }} r
inner join {{ ref('stg_parties') }} p
    on r.party_id = p.party_id
