import asyncio
import unittest
from uuid import uuid4

from api.database import (
    complete_simulation_run,
    ensure_database_schema,
    insert_passenger_event,
    insert_simulation_run,
    reset_database_tables,
)
from simulation.passenger import Passenger
from simulation.simulation import SimulationEngine


class FakeConnection:
    def __init__(self) -> None:
        self.executions: list[dict[str, object]] = []
        self.statements: list[str] = []

    async def execute(self, statement: object, parameters: dict[str, object] | None = None) -> None:
        self.statements.append(str(statement))
        if parameters is None:
            parameters = {}
        self.executions.append(parameters)


class FakeBeginContext:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> FakeConnection:
        return self.connection

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


class FakeDatabaseEngine:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    def begin(self) -> FakeBeginContext:
        return FakeBeginContext(self.connection)


class DatabaseHelperTests(unittest.IsolatedAsyncioTestCase):
    async def test_insert_simulation_run_no_database_does_nothing(self) -> None:
        result = await insert_simulation_run(None, uuid4(), 1.0, 0.3)

        self.assertIsNone(result)

    async def test_insert_passenger_event_uses_existing_schema_parameters(self) -> None:
        database_engine = FakeDatabaseEngine()
        run_id = uuid4()

        await insert_passenger_event(database_engine, run_id, 7, "psg-0001", "created", 3, "ev-01")

        self.assertEqual(len(database_engine.connection.executions), 1)
        self.assertEqual(database_engine.connection.executions[0]["run_id"], run_id)
        self.assertEqual(database_engine.connection.executions[0]["event_type"], "created")
        self.assertEqual(database_engine.connection.executions[0]["floor"], 3)
        self.assertEqual(database_engine.connection.executions[0]["elevator_id"], "ev-01")

    async def test_insert_passenger_event_allows_basement_floor_parameter(self) -> None:
        database_engine = FakeDatabaseEngine()
        run_id = uuid4()

        await insert_passenger_event(database_engine, run_id, 7, "psg-0001", "created", -1)

        self.assertEqual(database_engine.connection.executions[0]["floor"], -1)

    async def test_ensure_database_schema_allows_basement_constraints(self) -> None:
        database_engine = FakeDatabaseEngine()

        await ensure_database_schema(database_engine)

        statements = "\n".join(database_engine.connection.statements)
        self.assertIn("DROP CONSTRAINT IF EXISTS passenger_events_floor_check", statements)
        self.assertIn("CHECK (floor IN (-1, 1, 2, 3, 4, 5))", statements)
        self.assertIn("CHECK (origin_floor IN (-1, 1, 2, 3, 4, 5))", statements)
        self.assertIn("CHECK (destination_floor IN (-1, 1, 2, 3, 4, 5))", statements)

    async def test_complete_simulation_run_updates_aggregate_fields(self) -> None:
        database_engine = FakeDatabaseEngine()
        run_id = uuid4()

        await complete_simulation_run(database_engine, run_id, 12, 4.5)

        self.assertEqual(len(database_engine.connection.executions), 1)
        self.assertEqual(database_engine.connection.executions[0]["run_id"], run_id)
        self.assertEqual(database_engine.connection.executions[0]["total_passengers_moved"], 12)
        self.assertEqual(database_engine.connection.executions[0]["average_wait_time_seconds"], 4.5)

    async def test_reset_database_tables_no_database_does_nothing(self) -> None:
        result = await reset_database_tables(None)

        self.assertIsNone(result)

    async def test_reset_database_tables_deletes_in_dependency_order(self) -> None:
        database_engine = FakeDatabaseEngine()

        await reset_database_tables(database_engine)

        self.assertEqual(len(database_engine.connection.statements), 3)
        self.assertIn("DELETE FROM passenger_events", database_engine.connection.statements[0])
        self.assertIn("DELETE FROM scenarios", database_engine.connection.statements[1])
        self.assertIn("DELETE FROM simulation_runs", database_engine.connection.statements[2])


class SimulationPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_add_passenger_records_created_and_assigned_events(self) -> None:
        recorded_events: list[tuple[str, str | None, int]] = []

        async def record_event(
            database_engine: object,
            run_id: object,
            tick: int,
            passenger_id: str,
            event_type: str,
            floor: int,
            elevator_id: str | None = None,
        ) -> None:
            recorded_events.append((event_type, elevator_id, floor))

        engine = SimulationEngine(spawn_chance=0.0, database_engine=object())

        from unittest.mock import patch

        with patch("simulation.simulation.insert_passenger_event", side_effect=record_event):
            await engine.add_passenger(1, 3)
            await asyncio.sleep(0)

        self.assertEqual(recorded_events, [("created", None, 1), ("assigned", "ev-01", 1)])

    async def test_elevator_service_records_boarded_and_exited_events(self) -> None:
        recorded_events: list[tuple[str, str | None, int]] = []

        async def record_event(
            database_engine: object,
            run_id: object,
            tick: int,
            passenger_id: str,
            event_type: str,
            floor: int,
            elevator_id: str | None = None,
        ) -> None:
            recorded_events.append((event_type, elevator_id, floor))

        engine = SimulationEngine(spawn_chance=0.0, database_engine=object())
        elevator = engine.building.elevators[0]
        elevator.current_floor = 3
        elevator.add_stop(3)
        elevator.passengers = [Passenger(origin_floor=1, destination_floor=3)]
        engine.building.add_passenger(Passenger(origin_floor=3, destination_floor=5))

        from unittest.mock import patch

        with patch("simulation.simulation.insert_passenger_event", side_effect=record_event):
            engine._advance_elevator(elevator)
            await asyncio.sleep(0)

        self.assertEqual(recorded_events, [("exited", "ev-01", 3), ("boarded", "ev-01", 3)])

    async def test_restart_resets_database_before_creating_new_run(self) -> None:
        operations: list[str] = []

        async def reset_tables(database_engine: object) -> None:
            operations.append("reset")

        async def create_run(
            database_engine: object,
            run_id: object,
            tick_interval: float,
            spawn_chance: float,
            dispatcher_strategy: str = "nearest-compatible",
        ) -> None:
            operations.append("insert_run")

        engine = SimulationEngine(spawn_chance=0.0, database_engine=object())

        from unittest.mock import patch

        with (
            patch("simulation.simulation.reset_database_tables", side_effect=reset_tables),
            patch("simulation.simulation.insert_simulation_run", side_effect=create_run),
        ):
            snapshot = await engine.restart()
            await asyncio.sleep(0)

        self.assertEqual(operations, ["reset", "insert_run"])
        self.assertEqual(snapshot["tick"], 0)

    async def test_restart_returns_snapshot_without_database(self) -> None:
        engine = SimulationEngine(spawn_chance=0.0)
        engine.building.tick = 12

        snapshot = await engine.restart()

        self.assertEqual(snapshot["tick"], 0)
        self.assertEqual(snapshot["queued_requests"], 0)


if __name__ == "__main__":
    unittest.main()