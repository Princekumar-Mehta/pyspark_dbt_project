select
    cast(trip_start_time as date) as trip_date,
    count(trip_id) as total_trips,
    round(sum(fare_amount), 2) as daily_revenue,
    round(avg(fare_amount), 2) as avg_fare,
    round(avg(distance_km), 2) as avg_distance_km

from pyspark_dbt.gold.fact_trips

group by cast(trip_start_time as date)
order by trip_date desc
