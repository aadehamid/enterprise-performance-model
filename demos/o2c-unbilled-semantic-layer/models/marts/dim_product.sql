select
    product_code,
    product_name,
    product_family,
    contract_price_usd,
    list_price_usd,
    expansion_per_f,
    uom
from {{ ref('stg_products') }}
