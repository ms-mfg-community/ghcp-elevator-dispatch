from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from .ai import AzureOpenAISettings, build_ai_insight


@dataclass(frozen=True)
class ElevatorCar:
    car_id: str
    current_floor: int
    direction: str = "idle"
    capacity: int = 10
    load: int = 0
    queued_stops: list[int] = field(default_factory=list)

    @property
    def available_space(self) -> int:
        return max(self.capacity - self.load, 0)

    @property
    def occupancy_ratio(self) -> float:
        if self.capacity <= 0:
            return 1.0
        return min(self.load / self.capacity, 1.0)


@dataclass(frozen=True)
class HallCall:
    origin_floor: int
    destination_floor: int
    passengers: int = 1

    @property
    def direction(self) -> str:
        return "up" if self.destination_floor >= self.origin_floor else "down"


def _normalize_direction(direction: str | None) -> str:
    if direction in {"up", "down", "idle"}:
        return direction
    return "idle"


def _parse_time_of_day(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def forecast_demand(
    request_time: str | None,
    recent_calls: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    parsed_time = _parse_time_of_day(request_time)
    recent_calls = recent_calls or []

    if parsed_time:
        minutes = parsed_time.hour * 60 + parsed_time.minute
        if 7 * 60 <= minutes <= 10 * 60:
            return {
                "traffic_mode": "morning-up-peak",
                "predicted_hotspots": [1, 5, 10, 15],
                "reason": "Morning traffic typically originates in the lobby and fans out to office floors.",
            }
        if 11 * 60 + 30 <= minutes <= 13 * 60 + 30:
            return {
                "traffic_mode": "lunch-interfloor",
                "predicted_hotspots": [1, 6, 12],
                "reason": "Midday traffic commonly mixes lobby, cafeteria, and meeting floors.",
            }
        if 16 * 60 + 30 <= minutes <= 19 * 60:
            return {
                "traffic_mode": "evening-down-peak",
                "predicted_hotspots": [1, 12, 18],
                "reason": "Evening traffic trends toward returning riders to the lobby.",
            }

    if recent_calls:
        floor_counts = Counter()
        for recent_call in recent_calls:
            floor_counts[recent_call.get("origin_floor", 1)] += 1
            floor_counts[recent_call.get("destination_floor", 1)] += 1
        hotspots = [floor for floor, _ in floor_counts.most_common(4)]
        return {
            "traffic_mode": "recent-demand-cluster",
            "predicted_hotspots": hotspots,
            "reason": "Recent hall calls indicate emerging demand on the listed floors.",
        }

    return {
        "traffic_mode": "balanced",
        "predicted_hotspots": [1],
        "reason": "Without traffic signals, keep spare capacity near the lobby.",
    }


def _direction_score(car: ElevatorCar, call: HallCall) -> float:
    if car.direction == "idle":
        return 3.0
    if car.direction == call.direction:
        if call.direction == "up" and car.current_floor <= call.origin_floor:
            return 5.0
        if call.direction == "down" and car.current_floor >= call.origin_floor:
            return 5.0
    return -4.0


def score_elevator(car: ElevatorCar, call: HallCall, demand_forecast: dict[str, Any]) -> float:
    if car.available_space < call.passengers:
        return -1000.0

    distance_penalty = abs(car.current_floor - call.origin_floor) * 1.8
    stop_penalty = len(car.queued_stops) * 1.25
    load_penalty = car.occupancy_ratio * 6.0
    forecast_bonus = 2.0 if call.origin_floor in demand_forecast.get("predicted_hotspots", []) else 0.0

    return (
        20.0
        + _direction_score(car, call)
        + forecast_bonus
        - distance_penalty
        - stop_penalty
        - load_penalty
    )


def build_dispatch_plan(
    payload: dict[str, Any],
    settings: AzureOpenAISettings | None = None,
) -> dict[str, Any]:
    settings = settings or AzureOpenAISettings.from_env()

    elevators = [
        ElevatorCar(
            car_id=str(entry["id"]),
            current_floor=int(entry["current_floor"]),
            direction=_normalize_direction(entry.get("direction")),
            capacity=int(entry.get("capacity", 10)),
            load=int(entry.get("load", 0)),
            queued_stops=[int(stop) for stop in entry.get("queued_stops", [])],
        )
        for entry in payload.get("elevators", [])
    ]
    if not elevators:
        raise ValueError("At least one elevator state is required.")

    request_payload = payload.get("request") or {}
    hall_call = HallCall(
        origin_floor=int(request_payload["origin_floor"]),
        destination_floor=int(request_payload["destination_floor"]),
        passengers=int(request_payload.get("passengers", 1)),
    )

    demand_forecast = forecast_demand(
        payload.get("request_time"),
        payload.get("recent_calls"),
    )
    ranked_cars = sorted(
        (
            {
                "car": car,
                "score": round(score_elevator(car, hall_call, demand_forecast), 2),
            }
            for car in elevators
        ),
        key=lambda candidate: candidate["score"],
        reverse=True,
    )
    selected = ranked_cars[0]
    assigned_car = selected["car"]

    dispatch_summary = {
        "assigned_car": assigned_car.car_id,
        "origin_floor": hall_call.origin_floor,
        "destination_floor": hall_call.destination_floor,
        "direction": hall_call.direction,
        "score": selected["score"],
        "traffic_mode": demand_forecast["traffic_mode"],
    }
    ai_insight = build_ai_insight(settings, dispatch_summary)

    return {
        "assigned_elevator": assigned_car.car_id,
        "request": asdict(hall_call),
        "dispatch_reason": (
            f"Car {assigned_car.car_id} best balances proximity, travel direction, "
            "capacity, and predicted demand."
        ),
        "ranked_candidates": [
            {
                "car_id": candidate["car"].car_id,
                "score": candidate["score"],
                "current_floor": candidate["car"].current_floor,
                "direction": candidate["car"].direction,
                "load": candidate["car"].load,
                "capacity": candidate["car"].capacity,
            }
            for candidate in ranked_cars
        ],
        "demand_forecast": demand_forecast,
        "ai_insight": ai_insight,
        "model_used": settings.model,
    }
