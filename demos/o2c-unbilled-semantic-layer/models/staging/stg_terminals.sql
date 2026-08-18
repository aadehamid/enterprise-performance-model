select
    terminal_code,
    terminal_name,
    city,
    state,
    mode
from {{ ref('terminals') }}
