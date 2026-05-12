from __future__ import annotations

import asyncio
import random
from contextlib import suppress
from typing import Awaitable
from uuid import uuid4

from api.database import (
    complete_simulation_run,
    insert_passenger_event,
    insert_simulation_run,
    reset_database_tables,
)
from simulation.building import Building
from simulation.dispatcher import Dispatcher
from simulation.elevator import Elevator
from simulation.passenger import Passenger

# Probability that a new passenger appears on any given tick (0.0–1.0).
DEFAULT_SPAWN_CHANCE = 0.3
WAIT_TIME_UPDATE_SECONDS = 60.0
MAX_TICKS = 1000


class SimulationEngine:
    def __init__(
        self,
        tick_interval: float = 1.0,
        spawn_chance: float = DEFAULT_SPAWN_CHANCE,
        max_ticks: int = MAX_TICKS,
        database_engine: object | None = None,
    ) -> None:
        self.building = Building()
        self.dispatcher = Dispatcher()
        self.tick_interval = tick_interval
        self.spawn_chance = spawn_chance
        self.max_ticks = max_ticks
        self.database_engine = database_engine
        self.run_id = uuid4()
        self._run_completed = False
        self._lock = asyncio.Lock()
        self._listeners: set[asyncio.Queue[dict[str, object]]] = set()
        self._running = True

    def set_database_engine(self, database_engine: object | None) -> None:
        self.database_engine = database_engine
        self._schedule_persistence(
            insert_simulation_run(
                self.database_engine,
                self.run_id,
                self.tick_interval,
                self.spawn_chance,
            )
        )

    async def run(self) -> None:
        self._schedule_persistence(
            insert_simulation_run(
                self.database_engine,
                self.run_id,
                self.tick_interval,
                self.spawn_chance,
            )
        )
        while self._running:
            await asyncio.sleep(self.tick_interval)
            await self.tick()

    async def shutdown(self) -> None:
        self._running = False
        await self._complete_current_run()

    async def subscribe(self) -> asyncio.Queue[dict[str, object]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=1)
        self._listeners.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue[dict[str, object]]) -> None:
        self._listeners.discard(queue)

    async def get_state(self) -> dict[str, object]:
        async with self._lock:
            return self.building.snapshot()

    async def add_passenger(self, origin_floor: int, destination_floor: int) -> dict[str, object]:
        async with self._lock:
            passenger = Passenger(
                origin_floor=origin_floor,
                destination_floor=destination_floor,
                requested_tick=self.building.tick,
            )
            self.building.add_passenger(passenger)
            selected_elevator_id = self.dispatcher.assign_passenger(self.building, passenger)
            self._record_passenger_event(passenger, "created", passenger.origin_floor)
            if selected_elevator_id is not None:
                self._record_passenger_event(passenger, "assigned", passenger.origin_floor, selected_elevator_id)
            snapshot = self.building.snapshot()
        await self.publish(snapshot)
        return snapshot

    async def set_paused(self, paused: bool) -> dict[str, object]:
        async with self._lock:
            self.building.paused = paused
            self.building.status_message = "Simulation paused." if paused else "Simulation resumed."
            snapshot = self.building.snapshot()
        await self.publish(snapshot)
        return snapshot

    async def restart(self) -> dict[str, object]:
        async with self._lock:
            await reset_database_tables(self.database_engine)
            self.building = Building()
            self.run_id = uuid4()
            self._run_completed = False
            self._schedule_persistence(
                insert_simulation_run(
                    self.database_engine,
                    self.run_id,
                    self.tick_interval,
                    self.spawn_chance,
                )
            )
            snapshot = self.building.snapshot()
        await self.publish(snapshot)
        return snapshot

    async def tick(self) -> None:
        async with self._lock:
            if self.building.paused:
                snapshot = self.building.snapshot()
            else:
                self.building.tick += 1
                self.dispatcher.dispatch_pending(self.building)
                for elevator in self.building.elevators:
                    self._advance_elevator(elevator)

                self._maybe_spawn_passenger()
                self._maybe_refresh_average_wait_time()

                if self.building.tick >= self.max_ticks:
                    self.building.paused = True
                    self.building.finished = True
                    self.building.status_message = (
                        f"Simulation complete \u2014 maximum of {self.max_ticks:,} ticks reached."
                    )
                    await self._complete_current_run()

                snapshot = self.building.snapshot()

        await self.publish(snapshot)

    async def publish(self, snapshot: dict[str, object]) -> None:
        stale_queues: list[asyncio.Queue[dict[str, object]]] = []
        for queue in self._listeners:
            with suppress(asyncio.QueueEmpty):
                queue.get_nowait()
            try:
                queue.put_nowait(snapshot)
            except asyncio.QueueFull:
                stale_queues.append(queue)

        for queue in stale_queues:
            self._listeners.discard(queue)

    def _advance_elevator(self, elevator: Elevator) -> None:
        if elevator.door_ticks_remaining > 0:
            elevator.door_ticks_remaining -= 1
            if elevator.door_ticks_remaining == 0:
                elevator.door_state = "closed"
                elevator.update_direction()
            return

        if elevator.current_floor in elevator.scheduled_stops:
            self._service_current_floor(elevator)
            return

        target_floor = elevator.next_target_floor()
        if target_floor is None:
            elevator.direction = "idle"
            return

        if target_floor > elevator.current_floor:
            elevator.current_floor += 1
            elevator.direction = "up"
        elif target_floor < elevator.current_floor:
            elevator.current_floor -= 1
            elevator.direction = "down"
        else:
            self._service_current_floor(elevator)

    def _service_current_floor(self, elevator: Elevator) -> None:
        elevator.door_state = "open"
        elevator.door_ticks_remaining = 1

        exiting = elevator.drop_off_passengers()
        elevator.passengers_moved += len(exiting)
        waiting = self.building.waiting_passengers[elevator.current_floor]
        boarded, remaining = elevator.board_passengers(waiting)
        self.building.record_boarding_wait(boarded, self.tick_interval)
        self.building.waiting_passengers[elevator.current_floor] = remaining

        elevator.remove_stop(elevator.current_floor)
        elevator.update_direction()

        for passenger in exiting:
            self._record_passenger_event(passenger, "exited", elevator.current_floor, elevator.id)

        for passenger in boarded:
            self._record_passenger_event(passenger, "boarded", elevator.current_floor, elevator.id)

        if exiting or boarded:
            exited_count = len(exiting)
            boarded_count = len(boarded)
            self.building.status_message = (
                f"{elevator.id} serviced floor {elevator.current_floor}: "
                f"{exited_count} exited, {boarded_count} boarded."
            )

    def _maybe_spawn_passenger(self) -> None:
        if random.random() >= self.spawn_chance:
            return

        floor_count = self.building.floor_count
        origin = random.randint(1, floor_count)
        destination = random.choice(
            [f for f in range(1, floor_count + 1) if f != origin]
        )
        passenger = Passenger(origin_floor=origin, destination_floor=destination, requested_tick=self.building.tick)
        self.building.add_passenger(passenger)
        selected_elevator_id = self.dispatcher.assign_passenger(self.building, passenger)
        self._record_passenger_event(passenger, "created", passenger.origin_floor)
        if selected_elevator_id is not None:
            self._record_passenger_event(passenger, "assigned", passenger.origin_floor, selected_elevator_id)

    def _maybe_refresh_average_wait_time(self) -> None:
        update_ticks = max(1, round(WAIT_TIME_UPDATE_SECONDS / self.tick_interval))
        if self.building.tick - self.building.wait_time_updated_tick >= update_ticks:
            self.building.refresh_average_wait_time()

    def _record_passenger_event(
        self,
        passenger: Passenger,
        event_type: str,
        floor: int,
        elevator_id: str | None = None,
    ) -> None:
        self._schedule_persistence(
            insert_passenger_event(
                self.database_engine,
                self.run_id,
                self.building.tick,
                passenger.id,
                event_type,
                floor,
                elevator_id,
            )
        )

    async def _complete_current_run(self) -> None:
        if self._run_completed:
            return

        self._run_completed = True
        total_passengers_moved = sum(elevator.passengers_moved for elevator in self.building.elevators)
        await complete_simulation_run(
            self.database_engine,
            self.run_id,
            total_passengers_moved,
            self.building.average_passenger_wait_time_seconds,
        )

    def _schedule_persistence(self, operation: Awaitable[None]) -> None:
        if self.database_engine is None:
            operation.close()
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            operation.close()
            return

        task = loop.create_task(operation)
        task.add_done_callback(self._log_persistence_error)

    @staticmethod
    def _log_persistence_error(task: asyncio.Task[None]) -> None:
        with suppress(asyncio.CancelledError):
            exception = task.exception()
            if exception is not None:
                print(f"Database persistence failed: {exception}")
