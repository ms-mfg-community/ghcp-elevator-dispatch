# Basement Floor Contract

## Canonical Floor Model

- Store basement as floor `-1` in Python domain objects, API payloads, tests, and any persisted event data
  that records a floor number.
- Display basement as `B1` in user-facing surfaces.
- Keep above-ground floors as positive integers `1` through `5`.
- Keep the default ordered floor list as `[-1, 1, 2, 3, 4, 5]` for state and validation.
- Render the building visually as `5, 4, 3, 2, 1, B1` from top to bottom.

## Validation Rules

- A passenger source and destination must both be valid supported floors.
- A passenger source and destination must not be the same floor.
- Every elevator must be allowed to travel to floor `-1`.
- Dispatcher logic must treat basement requests like any other valid floor request.

## API Shape

The `/api/state` floor list should include basement with the same base fields as other floors. If labels are
exposed, basement should include `"label": "B1"`.

```json
{
  "floor": -1,
  "label": "B1",
  "passengers_waiting": 0
}
```

## UI Requirements

- Render B1 below floor 1.
- Use distinct but restrained styling for the basement row.
- Keep elevator cabin positions stable when moving between B1 and floor 1.
- Preserve desktop and mobile responsiveness with six total levels.

## Persistence Boundary

Keep simulation state in memory. Update database-related code only if existing database tables, fixtures, or tests
explicitly validate or serialize floor values. Do not add a new database or persistence layer for this feature.
