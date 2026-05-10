from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from simulation.passenger import Passenger

Direction = Literal["up", "down", "idle"]
DoorState = Literal["open", "closed"]


@dataclass(slots=True)
class Elevator:
    id: str
    current_floor: int = 1
    direction: Direction = "idle"
    door_state: DoorState = "closed"
    capacity: int = 8
    passengers: list[Passenger] = field(default_factory=list)
    scheduled_stops: set[int] = field(default_factory=set)
    door_ticks_remaining: int = 0
    passengers_moved: int = 0

    @property
    def available_capacity(self) -> int:
        return self.capacity - len(self.passengers)

    def add_stop(self, floor: int) -> None:
        if 1 <= floor <= 5:
            self.scheduled_stops.add(floor)

    def remove_stop(self, floor: int) -> None:
        self.scheduled_stops.discard(floor)

    def next_target_floor(self) -> int | None:
        if not self.scheduled_stops:
            return None
        return min(self.scheduled_stops, key=lambda floor: abs(floor - self.current_floor))

    def update_direction(self) -> None:
        target = self.next_target_floor()
        if target is None:
            self.direction = "idle"
        elif target > self.current_floor:
            self.direction = "up"
        elif target < self.current_floor:
            self.direction = "down"
        elif self.passengers:
            self.direction = self.passengers[0].direction
        else:
            self.direction = "idle"

    def drop_off_passengers(self) -> list[Passenger]:
        exiting = [passenger for passenger in self.passengers if passenger.destination_floor == self.current_floor]
        if exiting:
            self.passengers = [passenger for passenger in self.passengers if passenger.destination_floor != self.current_floor]
        return exiting

    def board_passengers(self, waiting_passengers: list[Passenger]) -> tuple[list[Passenger], list[Passenger]]:
        if not waiting_passengers or self.available_capacity <= 0:
            return [], waiting_passengers

        target_direction = self.direction
        if target_direction == "idle":
            target_direction = waiting_passengers[0].direction

        boarded: list[Passenger] = []
        remaining: list[Passenger] = []
        for passenger in waiting_passengers:
            if passenger.direction == target_direction and len(boarded) < self.available_capacity:
                boarded.append(passenger)
            else:
                remaining.append(passenger)

        if boarded:
            self.passengers.extend(boarded)
            for passenger in boarded:
                self.add_stop(passenger.destination_floor)
            if self.direction == "idle":
                self.direction = boarded[0].direction

        return boarded, remaining

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "current_floor": self.current_floor,
            "direction": self.direction,
            "door_state": self.door_state,
            "capacity": self.capacity,
            "available_capacity": self.available_capacity,
            "passengers_moved": self.passengers_moved,
            "passengers": [passenger.to_dict() for passenger in self.passengers],
            "scheduled_stops": sorted(self.scheduled_stops),
        }
