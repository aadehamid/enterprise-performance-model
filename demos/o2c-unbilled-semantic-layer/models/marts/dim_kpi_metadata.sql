-- One certified KPI row. Grain lives on the fact (gold_kpi_unbilled /
-- fct_unbilled), not here. formula_pointer is the MetricFlow metric name.
-- This is metadata, not a KPI Store catalog.

select
    'KPI-O2C-UNBILLED-USD' as kpi_id,
    'Unbilled USD' as name,
    'Revenue Accounting / Order-to-Cash' as owner,
    'Delivered BOL tickets with no posted invoice line as of as_of_date, valued at net gallons (60F) times contract price. Quality-hold tickets are never unbilled (they are not billable). Default published grain is sold_to + terminal + day. Product is an optional slice.' as definition,
    'USD' as uom,
    'sold_to + terminal + day' as default_grain_rule,
    'certified' as status,
    'unbilled_usd' as formula_pointer,
    date '{{ var("as_of_date") }}' as as_of_date
