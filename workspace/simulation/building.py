from __future__ import annotations

from dataclasses import dataclass, field

from simulation.elevator import Elevator
from simulation.floors import DISPLAY_FLOORS, SUPPORTED_FLOORS, floor_label
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
    floor_count: int = len(SUPPORTED_FLOORS)
    accessible_floors: list[int] = field(default_factory=lambda: list(SUPPORTED_FLOORS))
    elevators: list[Elevator] = field(default_factory=_default_elevators)
    waiting_passengers: dict[int, list[Passenger]] = field(default_factory=dict)
    pending_passengers: list[Passenger] = field(default_factory=list)
    tick: int = 0
    paused: bool = False
    finished: bool = False
    status_message: str = "Simulation ready. Add a passenger to begin."
    total_passenger_wait_time_seconds: float = 0.0
    boarded_passenger_count: int = 0
    average_passenger_wait_time_seconds: float = 0.0
    wait_time_updated_tick: int = 0

    def __post_init__(self) -> None:
        for floor in self.accessible_floors:
            self.waiting_passengers.setdefault(floor, [])

    def add_passenger(self, passenger: Passenger) -> None:
        self.waiting_passengers[passenger.origin_floor].append(passenger)

    def queue_passenger(self, passenger: Passenger) -> None:
        if all(queued.id != passenger.id for queued in self.pending_passengers):
            self.pending_passengers.append(passenger)

    def resolve_pending(self, passenger_id: str) -> None:
        self.pending_passengers = [passenger for passenger in self.pending_passengers if passenger.id != passenger_id]

    def record_boarding_wait(self, passengers: list[Passenger], tick_interval: float) -> None:
        for passenger in passengers:
            waited_ticks = max(0, self.tick - passenger.requested_tick)
            self.total_passenger_wait_time_seconds += waited_ticks * tick_interval
            self.boarded_passenger_count += 1

    def refresh_average_wait_time(self) -> None:
        if self.boarded_passenger_count == 0:
            self.average_passenger_wait_time_seconds = 0.0
        else:
            self.average_passenger_wait_time_seconds = (
                self.total_passenger_wait_time_seconds / self.boarded_passenger_count
            )
        self.wait_time_updated_tick = self.tick

    def floor_snapshot(self) -> list[dict[str, object]]:
        return [
            {
                "floor": floor,
                "label": floor_label(floor),
                "waiting_passengers": [passenger.to_dict() for passenger in self.waiting_passengers[floor]],
            }
            for floor in DISPLAY_FLOORS
            if floor in self.waiting_passengers
        ]

    def snapshot(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "paused": self.paused,
            "finished": self.finished,
            "status_message": self.status_message,
            "queued_requests": len(self.pending_passengers),
            "average_passenger_wait_time_seconds": self.average_passenger_wait_time_seconds,
            "wait_time_updated_tick": self.wait_time_updated_tick,
            "floors": self.floor_snapshot(),
            "elevators": [elevator.to_dict() for elevator in self.elevators],
        }
