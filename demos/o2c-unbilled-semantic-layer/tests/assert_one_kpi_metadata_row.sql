-- dim_kpi_metadata must be exactly one certified Unbilled USD row.
select n
from (
    select count(*) as n
    from {{ ref('dim_kpi_metadata') }}
) t
where n != 1
