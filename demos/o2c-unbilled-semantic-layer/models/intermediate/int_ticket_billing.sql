-- Ticket-level billing status as of var('as_of_date').
-- An invoice line counts only when the parent invoice_date <= as_of.
with lines as (
    select
        l.ticket_id,
        l.invoice_id,
        l.line_gallons_net,
        l.line_amount_usd,
        i.invoice_date,
        i.payer_id as invoice_payer_id
    from {{ ref('stg_invoice_lines') }} l
    inner join {{ ref('stg_invoices') }} i
        on l.invoice_id = i.invoice_id
    where i.invoice_date <= date '{{ var("as_of_date") }}'
      and i.invoice_status = 'posted'
)

select
    d.ticket_id,
    d.bol_ts,
    d.delivery_date,
    d.terminal_code,
    d.sold_to_id,
    d.payer_id,
    d.bill_to_id,
    d.product_code,
    d.gallons_net,
    d.gallons_gross,
    d.temperature_f,
    d.status,
    l.invoice_id,
    l.invoice_date,
    l.line_amount_usd,
    case
        when d.status = 'quality_hold' then false
        when l.ticket_id is not null then true
        else false
    end as is_billed,
    case
        when d.status = 'delivered' and l.ticket_id is null then true
        else false
    end as is_unbilled
from {{ ref('stg_deliveries') }} d
left join lines l
    on d.ticket_id = l.ticket_id
