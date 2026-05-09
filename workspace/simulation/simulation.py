from __future__ import annotations

import asyncio
from contextlib import suppress

from simulation.building import Building
from simulation.dispatcher import Dispatcher
from simulation.elevator import Elevator
from simulation.passenger import Passenger


class SimulationEngine:
    def __init__(self, tick_interval: float = 1.0) -> None:
        self.building = Building()
        self.dispatcher = Dispatcher()
        self.tick_interval = tick_interval
        self._lock = asyncio.Lock()
        self._listeners: set[asyncio.Queue[dict[str, object]]] = set()
        self._running = True

    async def run(self) -> None:
        while self._running:
            await asyncio.sleep(self.tick_interval)
            await self.tick()

    async def shutdown(self) -> None:
        self._running = False

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
        passenger = Passenger(origin_floor=origin_floor, destination_floor=destination_floor)
        async with self._lock:
            self.building.add_passenger(passenger)
            self.dispatcher.assign_passenger(self.building, passenger)
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

    async def tick(self) -> None:
        async with self._lock:
            if self.building.paused:
                snapshot = self.building.snapshot()
            else:
                self.building.tick += 1
                self.dispatcher.dispatch_pending(self.building)
                for elevator in self.building.elevators:
                    self._advance_elevator(elevator)

                if self.building.tick % 8 == 0:
                    # TODO: Replace this placeholder with randomized passenger generation in the next lab step.
                    self.building.status_message = "Simulation running. Add passengers from the dashboard."

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
        waiting = self.building.waiting_passengers[elevator.current_floor]
        boarded, remaining = elevator.board_passengers(waiting)
        self.building.waiting_passengers[elevator.current_floor] = remaining

        elevator.remove_stop(elevator.current_floor)
        elevator.update_direction()

        if exiting or boarded:
            exited_count = len(exiting)
            boarded_count = len(boarded)
            self.building.status_message = (
                f"{elevator.id} serviced floor {elevator.current_floor}: "
                f"{exited_count} exited, {boarded_count} boarded."
            )
