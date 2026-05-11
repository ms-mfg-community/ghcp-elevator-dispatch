#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL="${DATABASE_URL:-postgresql://elevator:elevator@postgres:5432/elevator_dispatch}"

if ! command -v psql >/dev/null 2>&1; then
  echo "psql was not found on PATH. Rebuild the devcontainer or install the PostgreSQL client." >&2
  exit 1
fi

echo "Using database: ${DATABASE_URL}"
echo

psql "${DATABASE_URL}" -v ON_ERROR_STOP=1 <<'SQL'
\echo '== Connection =='
SELECT current_database() AS database, current_user AS user, version();

\echo ''
\echo '== Schemas =='
\dn

\echo ''
\echo '== Public Tables =='
\dt public.*

\echo ''
\echo '== simulation_runs Schema =='
\d public.simulation_runs

\echo ''
\echo '== passenger_events Schema =='
\d public.passenger_events

\echo ''
\echo '== scenarios Schema =='
\d public.scenarios

\echo ''
\echo '== Row Counts =='
SELECT 'simulation_runs' AS table_name, COUNT(*) AS row_count FROM public.simulation_runs
UNION ALL
SELECT 'passenger_events', COUNT(*) FROM public.passenger_events
UNION ALL
SELECT 'scenarios', COUNT(*) FROM public.scenarios
ORDER BY table_name;

\echo ''
\echo '== Passenger Events By Type =='
SELECT event_type, COUNT(*) AS row_count
FROM public.passenger_events
GROUP BY event_type
ORDER BY event_type;

\echo ''
\echo '== Recent Simulation Runs =='
SELECT run_id, started_at, ended_at, dispatcher_strategy, total_passengers_moved, average_wait_time_seconds
FROM public.simulation_runs
ORDER BY started_at DESC
LIMIT 10;

\echo ''
\echo '== Recent Passenger Events =='
SELECT event_id, run_id, tick, passenger_id, event_type, elevator_id, floor, timestamp
FROM public.passenger_events
ORDER BY timestamp DESC
LIMIT 20;

\echo ''
\echo '== Scenario Rows =='
SELECT scenario_id, name, tick, origin_floor, destination_floor
FROM public.scenarios
ORDER BY name, tick
LIMIT 20;
SQL