-- fare_amount should never be zero or negative
select trip_id, fare_amount
from {{ ref('trips') }}
where fare_amount <= 0
