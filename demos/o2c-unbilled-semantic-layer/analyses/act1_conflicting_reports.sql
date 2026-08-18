-- Same three reports as scripts/act1_reports.py, for anyone who prefers SQL.
-- Run against o2c.duckdb after dbt run.

-- Report A: sold-to
select sold_to_name as customer, sum(unbilled_usd) as unbilled_usd
from fct_unbilled
group by 1;

-- Report B: payer
select payer_name as customer, sum(unbilled_usd) as unbilled_usd
from fct_unbilled
group by 1;

-- Report C: sloppy
select
    case
        when sold_to_id in ('APEX-HOU', 'APEX-DAL') then sold_to_name
        when sold_to_id = 'METRO-BMT' then payer_name
        else sold_to_name
    end as customer,
    sum(sloppy_value_usd) as unbilled_usd
from fct_delivery
where not is_billed
group by 1;
