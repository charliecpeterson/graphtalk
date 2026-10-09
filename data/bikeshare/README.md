# Synthetic bike-share data (calendar year 2025)

Fictional city. All data is synthetic.

| File | Rows | What it is |
|---|---|---|
| `trips.csv` | ~149k | One row per trip |
| `stations.csv` | 80 | Station metadata (location, elevation, capacity, opening date) |
| `weather.csv` | 8,760 | Hourly temperature, precipitation, wind, condition |
| `daily_summary.csv` | 365 | Trips per day with daily weather; the easy one for a first Excel chart |

## trips.csv
`trip_id`, `start_time`, `end_time` (local, `YYYY-MM-DD HH:MM:SS`), `rider_type` (member/casual),
`bike_type` (classic/ebike), start/end `station_id`, `station` name and `neighborhood`,
`duration_min`, `distance_km`. A few trips have no end station recorded.

## stations.csv
`station_id`, `station_name`, `neighborhood`, `lat`, `lon`, `elevation_m`, `capacity`, `opened_date`.
Coordinates are synthetic and do not follow a real coastline.

## weather.csv
`datetime`, `temp_c`, `precip_mm` (per hour), `wind_kmh`, `condition`.
