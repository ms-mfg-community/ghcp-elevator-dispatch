from __future__ import annotations

BASEMENT_FLOOR = -1
ABOVE_GROUND_FLOORS = [1, 2, 3, 4, 5]
SUPPORTED_FLOORS = [BASEMENT_FLOOR, *ABOVE_GROUND_FLOORS]
DISPLAY_FLOORS = [*reversed(ABOVE_GROUND_FLOORS), BASEMENT_FLOOR]


def is_supported_floor(floor: int) -> bool:
    return floor in SUPPORTED_FLOORS


def floor_label(floor: int) -> str:
    return "B1" if floor == BASEMENT_FLOOR else f"Floor {floor}"


def floor_distance(start_floor: int, end_floor: int) -> int:
    start_index = SUPPORTED_FLOORS.index(start_floor)
    end_index = SUPPORTED_FLOORS.index(end_floor)
    return abs(end_index - start_index)


def next_floor_toward(current_floor: int, target_floor: int) -> int:
    current_index = SUPPORTED_FLOORS.index(current_floor)
    target_index = SUPPORTED_FLOORS.index(target_floor)
    if target_index > current_index:
        return SUPPORTED_FLOORS[current_index + 1]
    if target_index < current_index:
        return SUPPORTED_FLOORS[current_index - 1]
    return current_floor
