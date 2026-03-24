select
    p.payment_method,
    p.payment_status,
    p.online_payment_status,
    count(t.trip_id) as total_trips,
    round(sum(t.fare_amount), 2) as total_revenue,
    round(avg(t.fare_amount), 2) as avg_fare

from pyspark_dbt.gold.fact_trips t
join pyspark_dbt.gold.dim_payments p
    on t.trip_id = p.trip_id
    and p.dbt_valid_to = to_date('9999-12-31')

group by p.payment_method, p.payment_status, p.online_payment_status
order by total_revenue desc
