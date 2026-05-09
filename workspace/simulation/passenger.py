from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count


_PASSENGER_COUNTER = count(1)


@dataclass(slots=True)
class Passenger:
    origin_floor: int
    destination_floor: int
    id: str = field(default_factory=lambda: f"psg-{next(_PASSENGER_COUNTER):04d}")

    def __post_init__(self) -> None:
        for floor in (self.origin_floor, self.destination_floor):
            if floor < 1 or floor > 5:
                raise ValueError("Floors must be between 1 and 5.")
        if self.origin_floor == self.destination_floor:
            raise ValueError("Origin and destination floors must differ.")

    @property
    def direction(self) -> str:
        return "up" if self.destination_floor > self.origin_floor else "down"

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "origin_floor": self.origin_floor,
            "destination_floor": self.destination_floor,
            "direction": self.direction,
        }
