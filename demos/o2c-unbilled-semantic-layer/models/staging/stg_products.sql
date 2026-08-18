select
    product_code,
    product_name,
    product_family,
    cast(contract_price_usd as double) as contract_price_usd,
    cast(list_price_usd as double) as list_price_usd,
    cast(expansion_per_f as double) as expansion_per_f,
    uom
from {{ ref('products') }}
