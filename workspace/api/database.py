from __future__ import annotations

import os
from typing import Any
from uuid import UUID


def _sql(statement: str) -> Any:
    try:
        from sqlalchemy import text
    except ModuleNotFoundError:
        return statement
    return text(statement)


def create_database_engine() -> Any | None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None

    from sqlalchemy.ext.asyncio import create_async_engine

    async_database_url = database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
    return create_async_engine(async_database_url, echo=False)


async def dispose_database_engine(database_engine: Any | None) -> None:
    if database_engine is not None:
        await database_engine.dispose()


async def ensure_database_schema(database_engine: Any | None) -> None:
    if database_engine is None:
        return

    async with database_engine.begin() as connection:
        await connection.execute(_sql("ALTER TABLE passenger_events DROP CONSTRAINT IF EXISTS passenger_events_floor_check"))
        await connection.execute(
            _sql(
                """
                ALTER TABLE passenger_events
                ADD CONSTRAINT passenger_events_floor_check
                CHECK (floor IN (-1, 1, 2, 3, 4, 5))
                """
            )
        )
        await connection.execute(_sql("ALTER TABLE scenarios DROP CONSTRAINT IF EXISTS scenarios_origin_floor_check"))
        await connection.execute(
            _sql(
                """
                ALTER TABLE scenarios
                ADD CONSTRAINT scenarios_origin_floor_check
                CHECK (origin_floor IN (-1, 1, 2, 3, 4, 5))
                """
            )
        )
        await connection.execute(_sql("ALTER TABLE scenarios DROP CONSTRAINT IF EXISTS scenarios_destination_floor_check"))
        await connection.execute(
            _sql(
                """
                ALTER TABLE scenarios
                ADD CONSTRAINT scenarios_destination_floor_check
                CHECK (destination_floor IN (-1, 1, 2, 3, 4, 5))
                """
            )
        )


async def insert_simulation_run(
    database_engine: Any | None,
    run_id: UUID,
    tick_interval: float,
    spawn_chance: float,
    dispatcher_strategy: str = "nearest-compatible",
) -> None:
    if database_engine is None:
        return

    async with database_engine.begin() as connection:
        await connection.execute(
            _sql(
                """
                INSERT INTO simulation_runs (
                    run_id,
                    dispatcher_strategy,
                    tick_interval,
                    spawn_chance
                )
                VALUES (:run_id, :dispatcher_strategy, :tick_interval, :spawn_chance)
                ON CONFLICT (run_id) DO NOTHING
                """
            ),
            {
                "run_id": run_id,
                "dispatcher_strategy": dispatcher_strategy,
                "tick_interval": tick_interval,
                "spawn_chance": spawn_chance,
            },
        )


async def insert_passenger_event(
    database_engine: Any | None,
    run_id: UUID,
    tick: int,
    passenger_id: str,
    event_type: str,
    floor: int,
    elevator_id: str | None = None,
) -> None:
    if database_engine is None:
        return

    async with database_engine.begin() as connection:
        await connection.execute(
            _sql(
                """
                INSERT INTO passenger_events (
                    run_id,
                    tick,
                    passenger_id,
                    event_type,
                    elevator_id,
                    floor
                )
                VALUES (:run_id, :tick, :passenger_id, :event_type, :elevator_id, :floor)
                """
            ),
            {
                "run_id": run_id,
                "tick": tick,
                "passenger_id": passenger_id,
                "event_type": event_type,
                "elevator_id": elevator_id,
                "floor": floor,
            },
        )


async def complete_simulation_run(
    database_engine: Any | None,
    run_id: UUID,
    total_passengers_moved: int,
    average_wait_time_seconds: float,
) -> None:
    if database_engine is None:
        return

    async with database_engine.begin() as connection:
        await connection.execute(
            _sql(
                """
                UPDATE simulation_runs
                SET ended_at = now(),
                    total_passengers_moved = :total_passengers_moved,
                    average_wait_time_seconds = :average_wait_time_seconds
                WHERE run_id = :run_id
                  AND ended_at IS NULL
                """
            ),
            {
                "run_id": run_id,
                "total_passengers_moved": total_passengers_moved,
                "average_wait_time_seconds": average_wait_time_seconds,
            },
        )


async def reset_database_tables(database_engine: Any | None) -> None:
    if database_engine is None:
        return

    async with database_engine.begin() as connection:
        await connection.execute(_sql("DELETE FROM passenger_events"))
        await connection.execute(_sql("DELETE FROM scenarios"))
        await connection.execute(_sql("DELETE FROM simulation_runs"))
