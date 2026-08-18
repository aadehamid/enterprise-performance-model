select
    party_id,
    lower(role_code) as role_code
from {{ ref('party_roles') }}
