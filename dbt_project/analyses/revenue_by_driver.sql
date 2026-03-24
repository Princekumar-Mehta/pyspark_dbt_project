select
    d.driver_id,
    d.full_name as driver_name,
    count(t.trip_id) as total_trips,
    round(sum(t.fare_amount), 2) as total_revenue,
    round(avg(t.fare_amount), 2) as avg_fare,
    round(avg(t.distance_km), 2) as avg_distance_km

from pyspark_dbt.gold.fact_trips t
join pyspark_dbt.gold.dim_drivers d
    on t.driver_id = d.driver_id
    and d.dbt_valid_to = to_date('9999-12-31')

group by d.driver_id, d.full_name
order by total_revenue desc
