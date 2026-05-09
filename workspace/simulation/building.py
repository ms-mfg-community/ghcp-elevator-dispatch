from __future__ import annotations

from dataclasses import dataclass, field

from simulation.elevator import Elevator
from simulation.passenger import Passenger


def _default_elevators() -> list[Elevator]:
    return [
        Elevator(id="ev-01", current_floor=1),
        Elevator(id="ev-02", current_floor=2),
        Elevator(id="ev-03", current_floor=3),
        Elevator(id="ev-04", current_floor=4),
    ]


@dataclass(slots=True)
class Building:
    floor_count: int = 5
    elevators: list[Elevator] = field(default_factory=_default_elevators)
    waiting_passengers: dict[int, list[Passenger]] = field(default_factory=dict)
    pending_passengers: list[Passenger] = field(default_factory=list)
    tick: int = 0
    paused: bool = False
    status_message: str = "Simulation ready. Add a passenger to begin."

    def __post_init__(self) -> None:
        for floor in range(1, self.floor_count + 1):
            self.waiting_passengers.setdefault(floor, [])

    def add_passenger(self, passenger: Passenger) -> None:
        self.waiting_passengers[passenger.origin_floor].append(passenger)

    def queue_passenger(self, passenger: Passenger) -> None:
        if all(queued.id != passenger.id for queued in self.pending_passengers):
            self.pending_passengers.append(passenger)

    def resolve_pending(self, passenger_id: str) -> None:
        self.pending_passengers = [passenger for passenger in self.pending_passengers if passenger.id != passenger_id]

    def floor_snapshot(self) -> list[dict[str, object]]:
        return [
            {
                "floor": floor,
                "waiting_passengers": [passenger.to_dict() for passenger in self.waiting_passengers[floor]],
            }
            for floor in range(self.floor_count, 0, -1)
        ]

    def snapshot(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "paused": self.paused,
            "status_message": self.status_message,
            "queued_requests": len(self.pending_passengers),
            "floors": self.floor_snapshot(),
            "elevators": [elevator.to_dict() for elevator in self.elevators],
        }
