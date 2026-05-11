# Product Requirements Document: Elevator Dispatch System

## Document Control

- File name: `docs/prd-elevator-dispatch.md`
- Owner: Workshop facilitator
- Stakeholders: Workshop participants, facilitator
- Status: Approved
- Created: 2026-05-09
- Last updated: 2026-05-09
- Target release or lab milestone: Lab 01 – Initialize Project

## Summary

Build an in-memory elevator dispatch simulation for a
5-floor, 4-elevator building, exposed through a FastAPI
backend and visualized in a real-time browser dashboard.
The project serves as a hands-on workshop starter that
teaches modular Python design, state management, async
WebSocket communication, and simple scheduling heuristics.

## Dashboard Target State

The screenshot below shows the desired state of the live
dashboard after Lab 01 is complete.

![Dashboard target state](images/live-dashboard-target-state.png)

## Problem Statement

Workshop participants need a well-structured, educational
codebase that demonstrates real-time full-stack development.
Existing elevator simulations are either too trivial (no UI)
or too complex (ML-based schedulers, databases). This project
fills the gap with a clear domain model, straightforward
dispatch heuristic, and a live visualization that participants
can extend in subsequent lab steps.

## Goals

- Provide a running 5-floor, 4-elevator simulation out of
  the box after a single setup command.
- Render a live building view with animated elevator cabs,
  passenger dots, floor-level metadata, per-cab movement
  totals, and average passenger wait time.
- Keep the codebase small, readable, and easy to extend in
  a workshop setting.
- Demonstrate async Python, WebSocket streaming, and
  vanilla HTML/CSS/TypeScript without frameworks.

## Non-Goals

- Database or persistent storage integration.
- Authentication or authorization.
- ML-based or optimization-library dispatch algorithms.
- Mobile-native or framework-based (React, Vue) UI.
- Multi-building or multi-tenant support.

## Users and Personas

| Persona | Needs | Success Looks Like |
| --- | --- | --- |
| Workshop participant | A starter codebase to learn from and extend | Can run the app, see the dashboard, and modify dispatch logic within a lab session |
| Workshop facilitator | A reliable demo with clear extension points | Can walk through code modules, explain heuristics, and assign incremental lab tasks |

## Use Cases

### Use Case 1: Run the Simulation

- Actor: Participant
- Trigger: Starts the FastAPI server
- Preconditions: Python venv created, dependencies installed
- Main flow:
  1. Activate `.venv` and run `uvicorn api.server:app --port 7000`.
  2. Open `http://localhost:7000` in a browser.
  3. Observe elevators moving, passengers spawning, and
     the dashboard updating in real time.
- Alternate or error flows:
  - Port 7000 in use: uvicorn reports a bind error;
    participant picks another port with `--port`.
- Outcome: Live dashboard renders the building view with
  elevator cabs, passenger dots, and status indicators.

### Use Case 2: Add a Passenger Manually

- Actor: Participant
- Trigger: Submits the Add Passenger form in the UI
- Preconditions: Simulation is running
- Main flow:
  1. Select an origin floor and a destination floor.
  2. Click "Add passenger".
  3. The dispatcher assigns the passenger to an elevator.
  4. A status message confirms the assignment.
- Alternate or error flows:
  - Same origin and destination: API returns 400.
  - All elevators full: passenger is queued; status
    message explains the situation.
- Outcome: Passenger appears as a waiting dot on the
  origin floor and boards when an elevator arrives.

### Use Case 3: Pause and Resume

- Actor: Participant
- Trigger: Clicks "Pause simulation" / "Resume simulation"
- Preconditions: Simulation is running
- Main flow:
  1. Click "Pause simulation".
  2. Tick counter stops; elevators freeze in place.
  3. Click "Resume simulation".
  4. Ticks resume; elevators continue moving.
- Outcome: Participant can inspect building state at a
  point in time.

### Use Case 4: Max Ticks Reached and Restart

- Actor: Participant
- Trigger: Simulation reaches 1 000 ticks
- Preconditions: Simulation is running
- Main flow:
  1. Tick counter reaches 1 000.
  2. Simulation auto-pauses and sets `finished` to true.
  3. Status message reads "Simulation complete —
     maximum of 1 000 ticks reached."
  4. UI shows an alert banner and a "Restart
     simulation" button.
  5. Participant clicks "Restart simulation".
  6. All state resets to initial values; tick resumes
     from 0.
- Outcome: A fresh simulation begins with no leftover
  passengers or elevator state.

## Functional Requirements

| ID | Requirement | Priority | Notes |
| --- | --- | --- | --- |
| FR-001 | The building shall have exactly 5 floors (1–5). | Must | Hardcoded default |
| FR-002 | The building shall have exactly 4 elevators (ev-01 through ev-04). | Must | Default start floors: 1, 2, 3, 4 |
| FR-003 | Each elevator shall have a max capacity of 8 passengers. | Must | |
| FR-004 | Each elevator shall move at most one floor per simulation tick. | Must | |
| FR-005 | Elevator doors shall open for one tick when servicing a floor. | Must | |
| FR-006 | The dispatcher shall assign passengers using a nearest-compatible-cab heuristic. | Must | Idle or same-direction elevators preferred |
| FR-007 | If no compatible elevator exists, the passenger shall be queued until one becomes available. | Must | Pending passenger list in Building |
| FR-008 | Passengers shall spawn randomly each tick based on a configurable spawn chance (default 0.3). | Must | |
| FR-009 | Users shall be able to add passengers manually via an API endpoint and the UI form. | Must | POST `/api/passengers` |
| FR-010 | The API shall validate that origin ≠ destination and both floors are 1–5. | Must | Returns 400 on invalid input |
| FR-011 | The simulation shall expose a WebSocket at `/ws` that streams building snapshots. | Must | |
| FR-012 | The UI shall render a live building view with elevator cabs and passenger dots. | Must | |
| FR-013 | Each elevator shall track a `passengers_moved` counter incremented on drop-off. | Must | |
| FR-014 | The building shall compute a rolling `average_passenger_wait_time_seconds` refreshed every 60 simulation-seconds. | Must | |
| FR-015 | The UI shall display per-cab movement totals, total passengers moved, and average wait time below the building view. | Must | Movement summary section |
| FR-016 | The UI shall show floor-level metadata (waiting count, elevator status) beside each floor row. | Should | |
| FR-017 | The simulation shall support pause and resume via POST `/api/control`. | Must | |
| FR-018 | The UI shall show dotted gridlines on the shaft grid to delineate cells. | Should | |
| FR-019 | The simulation shall stop after 1 000 ticks, auto-pause, set `finished` to true, and display a completion message. | Must | `MAX_TICKS = 1000` |
| FR-020 | The UI shall show an alert banner and a "Restart simulation" button when the simulation finishes. | Must | |
| FR-021 | POST `/api/restart` shall reset all simulation state to initial values and resume ticking from 0. | Must | |
| FR-022 | Each elevator cab shall have a distinct color: ev-01 green, ev-02 blue, ev-03 purple, ev-04 medium grey. | Must | Applied via CSS class per cab |

## Non-Functional Requirements

| ID | Category | Requirement | Target |
| --- | --- | --- | --- |
| NFR-001 | Performance | Tick loop runs once per second without blocking the event loop. | 1 s tick interval |
| NFR-002 | Reliability | WebSocket reconnection is handled by the client. | Auto-reconnect within 2 s |
| NFR-003 | Maintainability | Modules stay under 200 lines each. | All current modules comply |
| NFR-004 | Accessibility | Floor labels and elevator IDs use semantic HTML text. | Screen-reader friendly labels |
| NFR-005 | Portability | Runs on Python 3.10+ with no OS-specific dependencies. | Windows, macOS, Linux |

## User Experience Requirements

- Primary screens: Single-page dashboard at `/`.
- Required states: connecting, running, paused, finished.
- Content: Hero banner with tick and queued counts, origin/
  destination selectors, Add passenger and Pause buttons,
  live building view, movement summary row, average wait
  time row, status message.
- Accessibility: Keyboard-navigable form controls, high-
  contrast text on light background, `aria-hidden` on
  decorative passenger dots.
- Responsive: Fluid layout with `clamp()` typography; no
  fixed-width breakpoints.

## Data Requirements

- Entities: `Building`, `Elevator`, `Passenger`.
- Required fields:
  - Passenger: `id`, `origin_floor`, `destination_floor`,
    `requested_tick`, `direction` (derived).
  - Elevator: `id`, `current_floor`, `direction`,
    `door_state`, `capacity`, `passengers`,
    `scheduled_stops`, `door_ticks_remaining`,
    `passengers_moved`.
  - Building: `floor_count`, `elevators`,
    `waiting_passengers`, `pending_passengers`, `tick`,
    `paused`, `status_message`,
    `total_passenger_wait_time_seconds`,
    `boarded_passenger_count`,
    `average_passenger_wait_time_seconds`,
    `wait_time_updated_tick`.
- Data lifecycle: All state is in-memory; resets on server
  restart.
- Validation: Floor numbers 1–5, origin ≠ destination.
- Seed data: Elevators start at floors 1–4. No passengers
  at boot.
- Privacy: No PII collected.

## API and Integration Requirements

- `GET /` — Serves `index.html`.
- `GET /api/state` — Returns a full building snapshot.
- `POST /api/passengers` — Creates a passenger
  (`{ origin_floor, destination_floor }`). Returns 201 on
  success, 400 on validation failure.
- `POST /api/control` — Sets pause state
  (`{ paused: bool }`).
- `POST /api/restart` — Resets all simulation state and
  resumes ticking from 0. Returns the fresh snapshot.
- `WS /ws` — Streams JSON building snapshots each tick.
- Static assets mounted at `/static`.
- Configuration: `tick_interval`, `spawn_chance`, and
  `max_ticks` are constructor parameters on
  `SimulationEngine`.
- No external services or databases.

## Technical Approach

Keep simulation logic in `workspace/simulation/`, API logic
in `workspace/api/`, UI files in `workspace/ui/`, and tests
in `workspace/tests/`. All state lives in memory inside a
single `SimulationEngine` instance protected by an asyncio
lock.

### Proposed Components

| Component | Responsibility | Files or Location |
| --- | --- | --- |
| Passenger | Domain object with origin, destination, direction | `simulation/passenger.py` |
| Elevator | Cab state, movement, boarding, drop-off | `simulation/elevator.py` |
| Building | Floor queues, pending list, snapshots, wait-time aggregation | `simulation/building.py` |
| Dispatcher | Nearest-compatible-cab heuristic, pending retry | `simulation/dispatcher.py` |
| SimulationEngine | Tick loop, spawn, publish, async lock | `simulation/simulation.py` |
| FastAPI server | Routes, validation, WebSocket, static mount | `api/server.py` |
| Dashboard UI | HTML template, TypeScript source, CSS, served JS | `ui/` |
| Tests | unittest suite for spawn, dispatch, metrics | `tests/` |

### Data Model

```text
Building
├── floor_count: int = 5
├── elevators: list[Elevator]  (4 cabs)
├── waiting_passengers: dict[int, list[Passenger]]
├── pending_passengers: list[Passenger]
├── tick: int
├── paused: bool
├── status_message: str
├── total_passenger_wait_time_seconds: float
├── boarded_passenger_count: int
├── average_passenger_wait_time_seconds: float
└── wait_time_updated_tick: int

Elevator
├── id: str
├── current_floor: int
├── direction: "up" | "down" | "idle"
├── door_state: "open" | "closed"
├── capacity: int = 8
├── passengers: list[Passenger]
├── scheduled_stops: set[int]
├── door_ticks_remaining: int
└── passengers_moved: int

Passenger
├── id: str           (auto "psg-NNNN")
├── origin_floor: int
├── destination_floor: int
├── requested_tick: int
└── direction: str    (derived property)
```

### Key Flows

```text
Server start
  → SimulationEngine created (4 elevators, 5 floors)
  → asyncio.create_task(engine.run())

Each tick
  → engine.tick() acquires lock
  → Increment building.tick
  → Dispatcher retries pending passengers
  → Advance each elevator (move / service floor)
  → Maybe spawn a random passenger
  → Maybe refresh average wait time (every 60 sim-seconds)
  → Publish snapshot to all WebSocket subscribers

Add passenger (manual)
  → POST /api/passengers validates input
  → engine.add_passenger() acquires lock
  → Passenger added to floor queue
  → Dispatcher assigns or queues
  → Snapshot published

Service a floor
  → Elevator opens doors (1 tick)
  → Drop off arriving passengers (passengers_moved++)
  → Board compatible waiting passengers
  → Record boarding wait time
  → Close doors, update direction
```

## Acceptance Criteria

- [x] AC-001: Given a fresh server start, when a user
  opens `/`, then the dashboard renders 5 floor rows and
  4 elevator shafts.
- [x] AC-002: Given a running simulation, when a tick
  fires, then each elevator moves at most one floor.
- [x] AC-003: Given a passenger request with origin 3 and
  destination 5, when the dispatcher runs, then the
  closest idle or same-direction elevator is assigned.
- [x] AC-004: Given all elevators at capacity, when a
  passenger is added, then the passenger is queued and the
  status message indicates capacity is full.
- [x] AC-005: Given passengers exit an elevator, when the
  floor is serviced, then `passengers_moved` increments.
- [x] AC-006: Given passengers have boarded, when 60
  simulation-seconds elapse, then
  `average_passenger_wait_time_seconds` is refreshed.
- [x] AC-007: Given the UI is connected, when state
  changes, then the movement summary displays per-cab
  totals, overall total, and average wait time.
- [x] AC-008: Given the user clicks "Pause simulation",
  when the next tick fires, then the tick counter does not
  advance.
- [x] AC-009: Given the simulation is running, when tick
  reaches 1 000, then the simulation auto-pauses,
  `finished` is true, and the status message says
  "Simulation complete".
- [x] AC-010: Given the simulation has finished, when the
  user clicks "Restart simulation", then all state
  resets and ticking resumes from 0.

## Testing Strategy

- Unit tests: Passenger spawn probability, dispatcher
  assignment and queuing, `passengers_moved` counter,
  average wait time refresh timing.
- Integration tests: Not required for Lab 01 (in-memory
  only).
- Manual validation:

  ```bash
  python -m venv .venv
  .venv\Scripts\Activate.ps1   # Windows
  pip install -r requirements.txt
  python -m compileall api simulation tests
  python -m unittest discover -s tests -v
  python -m uvicorn api.server:app --reload
  ```

- Test data: Inline fixtures in test methods.
- Regression risks: Dispatch heuristic changes may affect
  elevator selection order; wait-time math depends on
  tick-interval alignment.

## Dependencies

- Internal: `simulation/`, `api/`, `ui/`, `tests/`.
- External packages: `fastapi >=0.115,<1.0`,
  `uvicorn[standard] >=0.32,<1.0`.
- Dev tooling: TypeScript compiler (`npm run build`),
  Python `compileall`, `unittest`.

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Random spawning makes demos non-deterministic | Medium | High | Configurable `spawn_chance`; set to 0.0 for controlled demos |
| In-memory state lost on restart | Low | Certain | Intentional for workshop simplicity; document in README |
| WebSocket disconnect during demo | Medium | Low | Client auto-reconnects; status message indicates state |

## Open Questions

- [x] Should the wait-time metric use a rolling window or
  cumulative average? — Decision: cumulative average,
  refreshed every 60 simulation-seconds.
- [x] Should the dispatcher use load balancing across
  elevators? — Decision: not for Lab 01; keep the
  nearest-compatible heuristic simple for the workshop.

## Decisions

| Date | Decision | Rationale | Owner |
| --- | --- | --- | --- |
| 2026-05-09 | Cumulative average for wait time | Simpler to implement and explain; rolling window deferred to a future lab | Facilitator |
| 2026-05-09 | No load balancing in dispatcher | Keeps the heuristic easy to read and extend in subsequent labs | Facilitator |
| 2026-05-09 | 60-second refresh interval | Balances update frequency with meaningful sample size | Facilitator |

## Implementation Plan

1. Scaffold project structure under `workspace/`.
2. Implement `Passenger`, `Elevator`, `Building` domain
   objects with dataclasses and type hints.
3. Implement `Dispatcher` with nearest-compatible-cab
   heuristic.
4. Implement `SimulationEngine` with async tick loop,
   spawn logic, and wait-time tracking.
5. Implement FastAPI server with REST and WebSocket
   endpoints.
6. Build HTML/CSS/TypeScript dashboard with building view,
   movement summary, and controls.
7. Write unittest suite covering spawn, dispatch, metrics.
8. Validate: `compileall`, `unittest discover`, manual
   browser check.

## Appendix

- Target state screenshot:
  [live-dashboard-target-state.png](images/live-dashboard-target-state.png)
- Initialization prompt:
  `.github/prompts/01.00.initialize-project.prompt.md`
- Copilot instructions:
  `.github/copilot-instructions.md`
