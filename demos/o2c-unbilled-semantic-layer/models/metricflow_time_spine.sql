{{
  config(
    materialized='table'
  )
}}

select
    cast(date_day as date) as date_day
from (
    select
        unnest(generate_series(
            date '2026-01-01',
            date '2026-08-31',
            interval '1 day'
        )) as date_day
) dates
