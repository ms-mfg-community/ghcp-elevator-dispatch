from __future__ import annotations

from simulation.building import Building
from simulation.elevator import Elevator
from simulation.floors import floor_distance
from simulation.passenger import Passenger


class Dispatcher:
    def assign_passenger(self, building: Building, passenger: Passenger) -> str | None:
        candidates: list[tuple[int, int, str, Elevator]] = []
        has_capacity = False

        for elevator in building.elevators:
            if elevator.available_capacity <= 0:
                continue

            has_capacity = True
            score = self._score_elevator(elevator, passenger)
            if score is None:
                continue
            candidates.append((score, floor_distance(elevator.current_floor, passenger.origin_floor), elevator.id, elevator))

        if not candidates:
            if has_capacity:
                building.status_message = (
                    f"All compatible elevators are busy. {passenger.id} is queued until an elevator becomes available."
                )
            else:
                building.status_message = (
                    f"All elevators are full. {passenger.id} will stay queued until capacity frees up."
                )
            building.queue_passenger(passenger)
            return None

        _, _, _, selected = min(candidates)
        selected.add_stop(passenger.origin_floor)
        selected.update_direction()
        building.resolve_pending(passenger.id)
        building.status_message = f"Assigned {passenger.id} to {selected.id}."
        return selected.id

    def dispatch_pending(self, building: Building) -> None:
        for passenger in list(building.pending_passengers):
            self.assign_passenger(building, passenger)

    def _score_elevator(self, elevator: Elevator, passenger: Passenger) -> int | None:
        distance = floor_distance(elevator.current_floor, passenger.origin_floor)
        if elevator.direction == "idle":
            return distance

        if elevator.direction == passenger.direction:
            if elevator.direction == "up" and elevator.current_floor <= passenger.origin_floor:
                return distance + 1
            if elevator.direction == "down" and elevator.current_floor >= passenger.origin_floor:
                return distance + 1

        return None
