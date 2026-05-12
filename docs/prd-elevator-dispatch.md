# Product Requirements Document: Elevator Dispatch System

## Document Control

- File name: `docs/prd-elevator-dispatch.md`
- Owner: Workshop facilitator
- Stakeholders: Workshop participants, facilitator
- Status: Approved
- Created: 2026-05-09
- Last updated: 2026-05-12
- Target release or lab milestone: Labs 01-04 complete; Labs 02.03-02.06 persistence and reset workflows; Azure
  migration preparation

## Summary

Build an elevator dispatch simulation for a 5-floor, 4-elevator building, exposed through a FastAPI backend and
visualized in a real-time browser dashboard. The live simulation state remains in memory, while an optional PostgreSQL
persistence path records simulation runs and passenger lifecycle events when `DATABASE_URL` is configured. The project
serves as a hands-on workshop starter that teaches modular Python design, state management, async WebSocket
communication, simple scheduling heuristics, database-backed event logging, and Copilot-assisted engineering workflows.

The repository should also function as a workshop lab environment. Participants need a clear setup path, prerequisite
checklist, repeatable validation commands, and discoverable Copilot customizations for prompts, skills, agents,
path-specific instructions, issue metadata, and Azure migration guidance.

## Dashboard Target State

The screenshot below shows the desired state of the live
dashboard after Lab 01 is complete.

![Dashboard target state](images/live-dashboard-target-state.png)

## Workshop Setup and Prerequisites

### Must-Have Now

| Requirement | Notes |
| --- | --- |
| GitHub account | Required to fork, clone, or open the assigned workshop repository. |
| GitHub Copilot access | Required for Copilot Chat, agent mode, prompt files, and skill-driven workflows. |
| VS Code | Primary workshop editor with GitHub Copilot and Copilot Chat extensions enabled. |
| Git | Required for local clone, branch, commit, and pull request workflows. |

### Supported Setup Paths

| Path | Target User | Required Runtime |
| --- | --- | --- |
| GitHub Codespaces | Workshop participants who need the fastest setup | Repository devcontainer builds the runtime and tools. |
| VS Code Dev Containers | Participants using local containers | Docker Desktop or compatible container engine plus Dev Containers extension. |
| Manual setup | Participants who cannot use containers | Python 3.10+, Node.js LTS, npm, Git, and optional PostgreSQL client. |

### Permissions and Policy Requirements

- Most labs require repository write access and any active Copilot license.
- Labs that use GitHub Actions, Copilot coding agent, organization-managed Copilot settings, or cloud deployment tooling
  may require additional organization permissions.
- Participants in managed enterprise environments should confirm that Codespaces, Copilot agent mode, MCP servers,
  GitHub Actions, and required marketplace extensions are allowed before the workshop.

### Pre-Configured Developer Tooling

The preferred Codespaces path should provide these tools through `.devcontainer/devcontainer.json` and
`.devcontainer/docker-compose.yml`:

| Tooling Area | Expected Capability |
| --- | --- |
| Python | Python 3.10+ runtime, `.venv` under `workspace/`, FastAPI dependencies installed. |
| TypeScript | Node.js LTS, npm, TypeScript compiler, `npm run build`. |
| GitHub | GitHub CLI, Copilot extensions, pull request and GitHub Actions extensions. |
| Containers | Docker-in-Docker with Debian trixie-compatible `"moby": false` configuration. |
| Database | PostgreSQL 16 sidecar, `DATABASE_URL`, init SQL, and `psql` client. |
| Cloud/IaC | Azure CLI, Azure Developer CLI (`azd`), Terraform, Bicep support. |
| Agent tooling | MCP Inspector support and repository-local Copilot prompts, skills, instructions, and agents. |

## Problem Statement

Workshop participants need a well-structured, educational
codebase that demonstrates real-time full-stack development.
Existing elevator simulations are either too trivial (no UI)
or too complex (ML-based schedulers, databases). This project
fills the gap with a clear domain model, straightforward
dispatch heuristic, and a live visualization that participants
can extend in subsequent lab steps.

## Goals

- Provide a running 5-floor, 4-elevator simulation out of the box through Codespaces or a documented local setup path.
- Render a live building view with animated elevator cabs,
  passenger dots, floor-level metadata, per-cab movement
  totals, and average passenger wait time.
- Keep the codebase small, readable, and easy to extend in
  a workshop setting.
- Demonstrate async Python, WebSocket streaming, and vanilla HTML/CSS/TypeScript without frameworks.
- Demonstrate optional PostgreSQL event persistence without making the database required for baseline use.
- Provide workshop-grade setup documentation, validation commands, and troubleshooting guidance modeled on a hands-on
  lab experience.
- Include reusable Copilot assets that demonstrate prompts, skills, instructions, agents, and repeatable verification
  workflows.

## Non-Goals

- Making database persistence required for the core simulation.
- Authentication or authorization.
- ML-based or optimization-library dispatch algorithms.
- Mobile-native or framework-based (React, Vue) UI.
- Multi-building or multi-tenant support.
- Implementing production cloud deployment, secret management, or enterprise identity integration in the starter app.

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
  6. All in-memory state resets to initial values; tick resumes from 0.
  7. If PostgreSQL persistence is enabled, application tables are cleared before the fresh run row is created.
- Outcome: A fresh simulation begins with no leftover
  passengers, elevator state, or previous persisted event history.

### Use Case 5: Persist Passenger Events for Inspection

- Actor: Participant
- Trigger: Starts the app with `DATABASE_URL` configured.
- Preconditions: PostgreSQL sidecar is running and the schema has been initialized.
- Main flow:
  1. Start `uvicorn` with `DATABASE_URL=postgresql://elevator:elevator@postgres:5432/elevator_dispatch`.
  2. Let the simulation tick or add passengers manually.
  3. Query `simulation_runs` and `passenger_events` with `psql`.
  4. Observe `created`, `assigned`, `boarded`, and `exited` records.
- Alternate or error flows:
  - `DATABASE_URL` absent: the app runs in memory and skips persistence.
  - Database unavailable: persistence operations fail without crashing the simulation.
- Outcome: Participants can inspect database-backed run history and passenger lifecycle events for future analytics labs.

### Use Case 6: Reset Database Tables for a Clean Demo

- Actor: Participant or facilitator
- Trigger: Runs the reset-all-tables prompt or clicks **Restart simulation** in the UI.
- Preconditions: PostgreSQL sidecar is running.
- Main flow:
  1. Verify expected tables exist.
  2. Query current row counts and records.
  3. Delete rows from `passenger_events`, `scenarios`, and `simulation_runs` while preserving schema.
  4. Confirm row counts are reset.
- Alternate or error flows:
  - App is still running: a fresh `simulation_runs` row or new passenger events may appear immediately after restart.
- Outcome: Database state is aligned with the visible simulation lifecycle.

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
| FR-023 | The repository README shall provide tutorial-style setup paths, prerequisites, validation commands, repository tour, and troubleshooting. | Must | Modeled on hands-on lab structure |
| FR-024 | The repository shall include reusable Copilot prompts and skills for repeatable lab operations. | Should | Prompt and skill files under `.github/` |
| FR-025 | The devcontainer shall provide optional PostgreSQL schema inspection support without making persistence mandatory. | Should | PostgreSQL sidecar, init SQL, and psql script |
| FR-026 | When `DATABASE_URL` is set, the simulation shall write run metadata to `simulation_runs`. | Must | Optional persistence path |
| FR-027 | When `DATABASE_URL` is set, passenger lifecycle events shall be written to `passenger_events`. | Must | Events: `created`, `assigned`, `boarded`, `exited` |
| FR-028 | POST `/api/restart` shall clear PostgreSQL application tables before creating the fresh run row. | Must | Applies only when persistence is enabled |
| FR-029 | The repository shall include prompt files for table reset, reset-on-restart, GitHub issue-type discovery, and Azure migration preparation. | Should | Prompts `02.05`, `02.06`, `03.00`, `04.00`, `04.01` |
| FR-030 | Azure deployment conventions shall be captured in path-scoped instructions for `workspace/**`. | Should | `.github/instructions/azure-deployment.instructions.md` |

## Non-Functional Requirements

| ID | Category | Requirement | Target |
| --- | --- | --- | --- |
| NFR-001 | Performance | Tick loop runs once per second without blocking the event loop. | 1 s tick interval |
| NFR-002 | Reliability | WebSocket reconnection is handled by the client. | Auto-reconnect within 2 s |
| NFR-003 | Maintainability | Modules stay under 200 lines each. | All current modules comply |
| NFR-004 | Accessibility | Floor labels and elevator IDs use semantic HTML text. | Screen-reader friendly labels |
| NFR-005 | Portability | Runs on Python 3.10+ with no OS-specific dependencies. | Windows, macOS, Linux |
| NFR-006 | Onboarding | New participants can select a setup path and validate the environment from README instructions. | 15 minutes or less for Codespaces |
| NFR-007 | Workshop repeatability | Setup and validation commands are scriptable and documented. | Commands work in Codespaces and devcontainer paths |
| NFR-008 | Resilience | Database persistence must not block or crash the simulation when unavailable. | In-memory fallback |
| NFR-009 | Operability | Database reset workflows preserve schema and constraints. | Delete rows, do not drop schema |

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
- Documentation surfaces: Repository README for workshop onboarding, `workspace/README.md` for app-level commands,
  PRDs for product intent, and `.github/` customizations for Copilot-driven workflows.
- Setup states: Fresh Codespace, rebuilt devcontainer, manual local environment, database sidecar reachable, and database
  sidecar unavailable but app still runs in memory.
- Database states: In-memory only, persistence enabled, tables reset manually, and tables reset via restart.

## Data Requirements

- Entities: `Building`, `Elevator`, `Passenger`; optional PostgreSQL tables for persistence and future analytics labs.
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
- Data lifecycle: Core simulation state is in-memory and resets on server restart or `POST /api/restart`. PostgreSQL rows
  are written only when `DATABASE_URL` is set. `POST /api/restart` removes rows from `passenger_events`, `scenarios`, and
  `simulation_runs`, then prepares a fresh run row.
- Validation: Floor numbers 1–5, origin ≠ destination.
- Seed data: Elevators start at floors 1–4. No passengers
  at boot.
- Optional PostgreSQL tables:
  - `simulation_runs`: run-level metadata, dispatcher strategy, tick interval, spawn chance, movement totals, and wait
    time aggregates.
  - `passenger_events`: passenger lifecycle events (`created`, `assigned`, `boarded`, `exited`) with tick, elevator, and
    floor values.
  - `scenarios`: named scenario rows for future replay labs.
- Privacy: No PII collected.

## API and Integration Requirements

- `GET /` — Serves `index.html`.
- `GET /api/state` — Returns a full building snapshot.
- `POST /api/passengers` — Creates a passenger
  (`{ origin_floor, destination_floor }`). Returns 201 on
  success, 400 on validation failure.
- `POST /api/control` — Sets pause state
  (`{ paused: bool }`).
- `POST /api/restart` — Resets all simulation state and resumes ticking from 0. If persistence is enabled, clears
  application table rows before creating the fresh run row. Returns the fresh snapshot.
- `WS /ws` — Streams JSON building snapshots each tick.
- Static assets mounted at `/static`.
- Configuration: `tick_interval`, `spawn_chance`, and
  `max_ticks` are constructor parameters on
  `SimulationEngine`.
- Optional devcontainer PostgreSQL sidecar for persistence, reset, and schema inspection labs. The app must still run when
  `DATABASE_URL` is absent.
- Development tooling integrations: GitHub Copilot, GitHub CLI, Docker-in-Docker, PostgreSQL client, Azure CLI, azd,
  Terraform, Bicep, and MCP Inspector are supported by the Codespaces/devcontainer path.

## Technical Approach

Keep simulation logic in `workspace/simulation/`, API logic in `workspace/api/`, UI files in `workspace/ui/`, and tests in
`workspace/tests/`. All core runtime state lives in memory inside a single `SimulationEngine` instance protected by an
asyncio lock.

The repository should remain workshop-first: small modules, explicit state transitions, and simple setup instructions.
The devcontainer may include optional services and tools that support later labs, but those services must not obscure the
starter app or make the baseline simulation harder to run.

### Proposed Components

| Component | Responsibility | Files or Location |
| --- | --- | --- |
| Passenger | Domain object with origin, destination, direction | `simulation/passenger.py` |
| Elevator | Cab state, movement, boarding, drop-off | `simulation/elevator.py` |
| Building | Floor queues, pending list, snapshots, wait-time aggregation | `simulation/building.py` |
| Dispatcher | Nearest-compatible-cab heuristic, pending retry | `simulation/dispatcher.py` |
| SimulationEngine | Tick loop, spawn, publish, async lock | `simulation/simulation.py` |
| Database helpers | Optional SQLAlchemy async engine, inserts, run completion, table reset | `api/database.py` |
| FastAPI server | Routes, validation, database engine lifecycle, WebSocket, static mount | `api/server.py` |
| Dashboard UI | HTML template, TypeScript source, CSS, served JS | `ui/` |
| Tests | unittest suite for spawn, dispatch, metrics | `tests/` |
| Devcontainer | Codespaces runtime, tooling features, app/Postgres Compose services | `.devcontainer/` |
| Copilot customizations | Repository instructions, path instructions, prompts, skills, agents | `.github/` |
| Documentation | Tutorial README, app quickstart, product requirements | `README.md`, `workspace/README.md`, `docs/` |

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
  → Optional SQLAlchemy async engine created if DATABASE_URL is set
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
  → Optional created/assigned passenger events are scheduled for PostgreSQL
  → Snapshot published

Service a floor
  → Elevator opens doors (1 tick)
  → Drop off arriving passengers (passengers_moved++)
  → Board compatible waiting passengers
  → Optional exited/boarded passenger events are scheduled for PostgreSQL
  → Record boarding wait time
  → Close doors, update direction

Restart simulation
  → POST /api/restart calls engine.restart()
  → Optional PostgreSQL tables are cleared in dependency-safe order
  → In-memory Building resets to initial state
  → New run ID is generated and optional simulation_runs row is created
  → Snapshot published
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
- [x] AC-011: Given `DATABASE_URL` is configured, when passengers are created, assigned, boarded, or exited, then
  matching rows are written to `passenger_events`.
- [x] AC-012: Given `DATABASE_URL` is configured, when the user clicks "Restart simulation", then old persisted records
  are removed and a fresh `simulation_runs` row is created.
- [x] AC-013: Given `DATABASE_URL` is absent, when the simulation runs or restarts, then the app continues in memory
  without database errors.

## Testing Strategy

- Unit tests: Passenger spawn probability, dispatcher assignment and queuing, `passengers_moved` counter, average wait
  time refresh timing, database helper SQL parameters, table reset order, and restart persistence sequencing.
- Integration tests: Devcontainer/database labs validate PostgreSQL connectivity, schema inspection, event writes, and
  reset behavior separately from pure simulation unit tests.
- Manual validation:

  ```bash
  python -m venv .venv
  .venv\Scripts\Activate.ps1   # Windows
  pip install -r requirements.txt
  python -m compileall api simulation tests
  python -m unittest discover -s tests -v
  npm run build
  python -m uvicorn api.server:app --reload
  ```

  Run with PostgreSQL persistence enabled:

  ```bash
  DATABASE_URL=postgresql://elevator:elevator@postgres:5432/elevator_dispatch \
  python -m uvicorn api.server:app --reload --port 7000
  ```

  From the repository root, inspect the optional PostgreSQL schema:

  ```bash
  .github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh
  ```

  Confirm persisted event counts:

  ```bash
  PGPASSWORD=elevator psql -h postgres -U elevator -d elevator_dispatch \
    -c "SELECT event_type, COUNT(*) FROM passenger_events GROUP BY event_type;"
  ```

- Test data: Inline fixtures in test methods.
- Regression risks: Dispatch heuristic changes may affect
  elevator selection order; wait-time math depends on
  tick-interval alignment.

## Dependencies

- Internal: `simulation/`, `api/`, `ui/`, `tests/`, `.github/`, `.devcontainer/`, `docs/`.
- External packages: `fastapi >=0.115,<1.0`,
  `uvicorn[standard] >=0.32,<1.0`, `asyncpg >=0.30,<1.0`, `sqlalchemy[asyncio] >=2.0,<3.0`.
- Dev tooling: TypeScript compiler (`npm run build`),
  Python `compileall`, `unittest`, GitHub CLI, PostgreSQL client, Docker-in-Docker, Azure CLI, azd, Terraform, Bicep,
  MCP Inspector.

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Random spawning makes demos non-deterministic | Medium | High | Configurable `spawn_chance`; set to 0.0 for controlled demos |
| In-memory state lost on restart | Low | Certain | Intentional for workshop simplicity; document in README |
| WebSocket disconnect during demo | Medium | Low | Client auto-reconnects; status message indicates state |
| Devcontainer feature incompatibility breaks Codespaces rebuild | High | Medium | Prefer verified feature IDs; document Debian trixie Docker-in-Docker requirements |
| Setup friction consumes workshop time | Medium | Medium | Provide Codespaces-first path, validation commands, and troubleshooting table |
| Optional PostgreSQL persistence is mistaken for required baseline behavior | Medium | Medium | State clearly that baseline simulation remains in-memory |
| Running app repopulates tables immediately after reset | Low | Medium | Document that restart creates a fresh run row and ticking can add events |

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
| 2026-05-11 | Codespaces-first setup documentation | Matches workshop delivery needs and minimizes local install friction | Facilitator |
| 2026-05-11 | PostgreSQL sidecar remains optional | Enables future persistence labs while preserving the starter app's in-memory simplicity | Facilitator |
| 2026-05-11 | Copilot assets are part of the lab surface | Prompts, skills, instructions, and agents teach repeatable agentic workflows | Facilitator |
| 2026-05-12 | PostgreSQL event persistence is optional and tied to `DATABASE_URL` | Keeps baseline app simple while enabling analytics and inspection labs | Facilitator |
| 2026-05-12 | Restart clears persisted application rows before creating a fresh run | Keeps database history aligned with the visible simulation lifecycle | Facilitator |
| 2026-05-12 | Azure deployment guidance lives in scoped instructions and migration prompts | Prepares future Azure labs without changing starter runtime behavior | Facilitator |

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
9. Document tutorial-style setup paths, prerequisites, useful commands, repository tour, and troubleshooting.
10. Add reusable Copilot prompts and skills for devcontainer setup and PostgreSQL schema inspection.
11. Add optional database persistence helpers and simulation event hooks for `simulation_runs` and `passenger_events`.
12. Add reset-all-tables and reset-on-restart workflows with unit coverage.
13. Add GitHub issue-type discovery prompt and labels/issue taxonomy guidance.
14. Add Azure deployment instructions and migration prompt scaffolding.

## Appendix

- Target state screenshot:
  [live-dashboard-target-state.png](images/live-dashboard-target-state.png)
- Initialization prompt:
  `.github/prompts/01.00.initialize-project.prompt.md`
- Copilot instructions:
  `.github/copilot-instructions.md`
- PostgreSQL schema inspection skill:
  `.github/skills/postgres-schema-inspection/SKILL.md`
- PostgreSQL data persistence skill:
  `.github/skills/postgres-data-persistence/SKILL.md`
- Reset tables prompt:
  `.github/prompts/02.05.reset-all-tables.prompt.md`
- Reset tables on restart prompt:
  `.github/prompts/02.06.reset-tables-upon-restart-simulation.prompt.md`
- Azure deployment instructions:
  `.github/instructions/azure-deployment.instructions.md`
