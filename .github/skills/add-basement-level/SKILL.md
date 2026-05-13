---
name: add-basement-level
description: "Use when: adding basement support, B1, floor -1, elevator floor ranges, basement passengers, basement API state, basement dashboard rendering, or validating all floors remain accessible in the elevator dispatch simulation."
argument-hint: "Add basement level support using floor -1 in state and B1 in user-facing labels."
license: MIT
user-invocable: true
---

# Add Basement Level to Elevator Dispatch Simulation

## Goal

Update this solution to include a basement level stored as floor `-1` and displayed as `B1`. The basement must be accessible to every elevator and must work consistently across the simulation domain model, API state, dashboard rendering, tests, and existing data-adjacent behavior.

## Skill Assets

- `assets/basement-floor-contract.md`: the shared convention for floor IDs, labels, validation, API shape, UI ordering, and persistence boundaries.
- `assets/coding-agent-handoff.md`: a concise implementation handoff for GitHub Copilot Coding Agent.
- `scripts/validate-basement-support.sh`: standalone compile, unit test, and UI build validation from the repository root.
- `scripts/check-api-basement-state.sh`: standalone API state smoke check for a running local app.

## Implementation Rules

- Use `-1` as the simulation and API floor identifier for the basement.
- Use `B1` only as the user-facing label.
- Keep the default scenario to six accessible levels: `B1` plus floors `1` through `5`.
- Keep the educational starter-project style: clear names, simple heuristics, explicit state transitions.
- Do not introduce new persistence, authentication, queues, ML, or optimization libraries.
- Update database-related code only when existing schema, fixtures, or tests constrain valid floor values.

## Required Coverage

- Simulation: building floors, elevator allowed floors, passenger validation, dispatching, and ticks must allow floor `-1`.
- API: `/api/state` and WebSocket state must include basement floor data in the same structure as other floors, with a `B1` label where labels are exposed.
- UI: the dashboard must render B1 at the bottom, style it distinctly, and animate elevator movement through it.
- Tests: add or update `unittest` coverage for passenger validation, dispatcher behavior, simulation lifecycle, and API-adjacent state.
- Documentation: update workspace documentation and PRD references when they describe supported floors.

## Validation

Run the standalone validation script after implementation:

```bash
bash .github/skills/add-basement-level/scripts/validate-basement-support.sh
```

With the app running locally on port `7000`, run the API smoke check:

```bash
bash .github/skills/add-basement-level/scripts/check-api-basement-state.sh
```

## Regression Testing

Verify that every elevator can still reach every supported level and that no existing floor becomes blocked or inaccessible because B1 was added. If validation fails, continue diagnosing until the root cause is fixed or clearly documented.

## Lessons Learned and Gotchas

- Treat `-1` as an internal value only. Any user-facing label, including status messages and scheduled-stop text, should
	use `B1` through the shared floor-label helper.
- After changing dashboard layout code, verify all four elevator cabs are visible in separate shafts and remain inside
	the building grid at both B1 and floor 5.
- Avoid dynamic CSS position strings that rely on `calc()` multiplication. Addition-based length expressions are more
	reliable for cab and shaft offsets across browser contexts.
- Absolute-positioned shaft tracks should not also depend on CSS grid placement; otherwise later cabs can be shifted into
	the wrong shaft or clipped out of view.
- A Codespaces forwarded URL returning `HTTP ERROR 502` is not always an application crash. Check local app health with
	`curl http://127.0.0.1:7000/api/state`, confirm port `7000` forwarding, and account for GitHub's one-time development
	port warning before editing simulation code.
