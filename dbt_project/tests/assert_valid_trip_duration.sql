-- trip should end after it starts
select trip_id, trip_start_time, trip_end_time
from {{ ref('trips') }}
where trip_end_time <= trip_start_time
