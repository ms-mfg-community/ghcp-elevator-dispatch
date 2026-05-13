from __future__ import annotations

BASEMENT_FLOOR = -1
ABOVE_GROUND_FLOORS = [1, 2, 3, 4, 5]
SUPPORTED_FLOORS = [BASEMENT_FLOOR, *ABOVE_GROUND_FLOORS]
DISPLAY_FLOORS = list(reversed(ABOVE_GROUND_FLOORS)) + [BASEMENT_FLOOR]


def is_supported_floor(floor: int) -> bool:
    return floor in SUPPORTED_FLOORS


def floor_label(floor: int) -> str:
    return "B1" if floor == BASEMENT_FLOOR else f"Floor {floor}"


def supported_floor_error() -> str:
    labels = ", ".join(floor_label(floor) for floor in SUPPORTED_FLOORS)
    return f"Floors must be one of: {labels}."


def _floor_index(floor: int, name: str) -> int:
    if not is_supported_floor(floor):
        raise ValueError(f"{name} is not supported. {supported_floor_error()}")
    return SUPPORTED_FLOORS.index(floor)


def floor_distance(start_floor: int, end_floor: int) -> int:
    start_index = _floor_index(start_floor, "Start floor")
    end_index = _floor_index(end_floor, "End floor")
    return abs(end_index - start_index)


def next_floor_toward(current_floor: int, target_floor: int) -> int:
    current_index = _floor_index(current_floor, "Current floor")
    target_index = _floor_index(target_floor, "Target floor")
    if target_index > current_index:
        return SUPPORTED_FLOORS[current_index + 1]
    if target_index < current_index:
        return SUPPORTED_FLOORS[current_index - 1]
    return current_floor
