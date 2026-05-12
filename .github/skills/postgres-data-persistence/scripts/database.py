"""
Reference implementation: PostgreSQL data persistence for elevator dispatch simulation.

This module manages the async SQLAlchemy engine and provides helper functions
to insert simulation events and run metadata into PostgreSQL.

Copy this file to workspace/api/database.py and adapt as needed.
"""

import os
import logging
import time
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Global engine and session factory
engine = None
async_session_factory = None

# Initialize on module load
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Convert postgresql:// to postgresql+asyncpg://
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    try:
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            connect_args={"timeout": 5}
        )
        async_session_factory = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info(f"Database engine initialized: {DATABASE_URL}")
    except Exception as e:
        logger.warning(f"Failed to initialize database engine: {e}. Running in-memory mode.")
        engine = None
        async_session_factory = None
else:
    logger.info("DATABASE_URL not set. Running in-memory mode.")


async def get_session() -> Optional[AsyncSession]:
    """
    Return an async session if database is available, otherwise None.
    
    Returns:
        AsyncSession if database is configured, None otherwise.
    """
    if async_session_factory is None:
        return None
    return async_session_factory()


async def close_engine():
    """
    Close the database engine on app shutdown.
    
    Call this in FastAPI shutdown event:
        @app.on_event("shutdown")
        async def shutdown():
            await close_engine()
    """
    if engine:
        await engine.dispose()
        logger.info("Database engine closed.")


async def insert_simulation_run(
    sim_id: str,
    num_floors: int,
    num_elevators: int
) -> bool:
    """
    Insert a simulation run record.
    
    Args:
        sim_id: Unique simulation ID.
        num_floors: Number of floors in the building.
        num_elevators: Number of elevators.
    
    Returns:
        True if successful, False otherwise.
    """
    if engine is None:
        return False
    
    session = await get_session()
    if session is None:
        return False
    
    try:
        await session.execute(
            text("""
            INSERT INTO simulation_runs (id, num_floors, num_elevators, started_at)
            VALUES (:id, :num_floors, :num_elevators, NOW())
            """),
            {
                "id": sim_id,
                "num_floors": num_floors,
                "num_elevators": num_elevators
            }
        )
        await session.commit()
        logger.debug(f"Inserted simulation run: {sim_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to insert simulation run: {e}")
        return False
    finally:
        await session.close()


async def insert_passenger_event(
    simulation_run_id: str,
    passenger_id: int,
    event_type: str,
    floor: int,
    timestamp: float,
    elevator_id: Optional[int] = None,
    wait_time_seconds: Optional[float] = None
) -> bool:
    """
    Insert a passenger event (spawned, boarded, exited).
    
    Args:
        simulation_run_id: ID of the parent simulation run.
        passenger_id: Unique passenger ID.
        event_type: Type of event ('spawned', 'boarded', 'exited').
        floor: Floor where the event occurred.
        timestamp: Simulation tick when event occurred.
        elevator_id: Optional elevator ID (for 'boarded' events).
        wait_time_seconds: Optional wait time (for 'boarded' events).
    
    Returns:
        True if successful, False otherwise.
    """
    if engine is None:
        return False
    
    session = await get_session()
    if session is None:
        return False
    
    try:
        await session.execute(
            text("""
            INSERT INTO passenger_events 
            (simulation_run_id, passenger_id, event_type, floor, timestamp, elevator_id, wait_time_seconds)
            VALUES (:sim_run_id, :pass_id, :event_type, :floor, :ts, :elev_id, :wait_time)
            """),
            {
                "sim_run_id": simulation_run_id,
                "pass_id": passenger_id,
                "event_type": event_type,
                "floor": floor,
                "ts": int(timestamp),
                "elev_id": elevator_id,
                "wait_time": wait_time_seconds
            }
        )
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to insert passenger event: {e}")
        return False
    finally:
        await session.close()


async def update_simulation_run_completed(
    sim_id: str,
    final_tick: int,
    total_passengers: int
) -> bool:
    """
    Update simulation run with completion metadata.
    
    Args:
        sim_id: ID of the simulation run to update.
        final_tick: Final tick number when simulation stopped.
        total_passengers: Total number of passengers served.
    
    Returns:
        True if successful, False otherwise.
    """
    if engine is None:
        return False
    
    session = await get_session()
    if session is None:
        return False
    
    try:
        await session.execute(
            text("""
            UPDATE simulation_runs 
            SET completed_at = NOW(), final_tick = :final_tick, total_passengers_served = :total_pass
            WHERE id = :sim_id
            """),
            {
                "sim_id": sim_id,
                "final_tick": final_tick,
                "total_pass": total_passengers
            }
        )
        await session.commit()
        logger.debug(f"Updated simulation run completion: {sim_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update simulation run: {e}")
        return False
    finally:
        await session.close()


# Utility function to generate simulation ID
def generate_simulation_id() -> str:
    """Generate a unique simulation ID."""
    return f"sim-{int(time.time())}-{uuid.uuid4().hex[:8]}"
