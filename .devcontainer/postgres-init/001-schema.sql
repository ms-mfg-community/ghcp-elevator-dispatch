-- Elevator Dispatch Workshop initial schema.
-- Runs once on first database volume creation.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    dispatcher_strategy TEXT NOT NULL DEFAULT 'nearest-compatible',
    tick_interval REAL NOT NULL DEFAULT 1.0,
    spawn_chance REAL NOT NULL DEFAULT 0.3,
    total_passengers_moved INTEGER NOT NULL DEFAULT 0,
    average_wait_time_seconds REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS passenger_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES simulation_runs(run_id),
    tick INTEGER NOT NULL,
    passenger_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'created', 'assigned', 'boarded', 'exited'
    )),
    elevator_id TEXT,
    floor INTEGER NOT NULL CHECK (floor IN (-1, 1, 2, 3, 4, 5)),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_passenger_events_run_id
    ON passenger_events (run_id);

CREATE INDEX IF NOT EXISTS idx_passenger_events_event_type
    ON passenger_events (event_type);

CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    tick INTEGER NOT NULL,
    origin_floor INTEGER NOT NULL CHECK (origin_floor IN (-1, 1, 2, 3, 4, 5)),
    destination_floor INTEGER NOT NULL CHECK (destination_floor IN (-1, 1, 2, 3, 4, 5))
);
