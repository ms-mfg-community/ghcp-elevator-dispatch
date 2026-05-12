# Elevator Dispatch Workshop - Hands-On Lab

A hands-on GitHub Copilot workshop for building and extending a real-time elevator dispatch simulation. The lab uses a
Python FastAPI backend, a framework-free TypeScript dashboard, an optional PostgreSQL persistence path, a PostgreSQL
devcontainer sidecar, and repository-level Copilot customizations so participants can practice prompts, skills,
instructions, and iterative application changes on a small but realistic codebase.

> Pre-work: complete setup before the workshop session begins so you can spend the session building, testing, and using
> Copilot rather than installing tools.

## Prerequisites

### Must-Have Now

| Requirement | Notes |
| --- | --- |
| GitHub account | Required to fork or clone the repository. |
| GitHub Copilot access | Individual, Business, Enterprise, or another plan enabled by your organization. |
| VS Code | Latest stable release with GitHub Copilot and GitHub Copilot Chat enabled. |
| Git | Configured with your GitHub credentials. |

### Additional Tools by Path

| Path | Tools |
| --- | --- |
| GitHub Codespaces | No local runtime install required. The devcontainer installs Python, Node, GitHub CLI, Docker, Azure CLI, azd, Terraform, Bicep, psql, and MCP Inspector support. |
| VS Code + Dev Containers | Docker Desktop or a compatible container engine, plus the VS Code Dev Containers extension. |
| Manual setup | Python 3.10+, Node.js LTS, npm, PostgreSQL client (`psql`), GitHub CLI (`gh`), and optionally Docker for PostgreSQL. |

### Permissions and Licensing

Most labs work with any GitHub Copilot license and repository write access. Labs that use GitHub Actions, Copilot coding
agent, or organization-managed Copilot features may require permissions from your GitHub organization administrator.

If your organization restricts Copilot agent mode, MCP servers, Codespaces, or GitHub Actions by policy, confirm access
before the workshop.

## Choose Your Path

| Path | Time | Best For | Recommendation |
| --- | --- | --- | --- |
| Codespaces | 5-10 min | In-person workshops and zero local install | Start here |
| VS Code + Docker Desktop | ~15 min | Developers already using containers locally | Supported |
| Manual setup | ~20 min | Developers who prefer direct local installs | Advanced |

### Option A - GitHub Codespaces

1. Fork this repository or open your assigned workshop copy.
2. Select **Code** > **Codespaces** > **Create codespace on main**.
3. Wait for the container to build. The first build can take several minutes while features and dependencies install.
4. Verify the core tools:

   ```bash
   python --version
   gh --version
   docker --version
   psql --version
   ```

5. Run the validation commands in [Verify the Application](#verify-the-application).

### Option B - VS Code + Docker Desktop

1. Install Docker Desktop and start it.
2. Install the VS Code Dev Containers extension.
3. Fork and clone this repository.
4. Open the repository folder in VS Code.
5. When prompted, choose **Reopen in Container**, or run **Dev Containers: Reopen in Container** from the Command Palette.
6. Wait for the devcontainer to build, then run the validation commands below.

### Option C - Manual Setup

Manual setup is useful when you cannot use Codespaces or a devcontainer. Install Python 3.10+, Node.js LTS, npm, and Git.
PostgreSQL is optional for the app because the simulation engine still keeps live state in memory, but setting
`DATABASE_URL` enables persistence for simulation runs and passenger events.

The Codespaces and devcontainer path defines `DATABASE_URL` for the app container automatically. Manual local setup only
uses PostgreSQL if you export `DATABASE_URL` yourself.

```bash
cd workspace
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm install
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Verify the Application

Run these commands from `workspace/` with the virtual environment activated:

```bash
python -m compileall .
python -m unittest discover -s tests -v
npm run build
```

Start the dashboard with the current environment. In Codespaces and the devcontainer this uses the PostgreSQL sidecar
because `DATABASE_URL` is already configured; in a manual shell without `DATABASE_URL`, it runs in in-memory-only mode:

```bash
python -m uvicorn api.server:app --reload --port 7000
```

Force an in-memory-only run from a Unix-like shell that already has `DATABASE_URL` set:

```bash
env -u DATABASE_URL python -m uvicorn api.server:app --reload --port 7000
```

Start the dashboard with PostgreSQL event persistence explicitly:

```bash
DATABASE_URL=postgresql://elevator:elevator@postgres:5432/elevator_dispatch \
python -m uvicorn api.server:app --reload --port 7000
```

Open <http://127.0.0.1:7000> to view the live elevator dashboard.

## The Application

The application simulates a 5-floor building with 4 elevators. A simple dispatcher assigns passengers to the nearest
compatible elevator, while a FastAPI server exposes REST endpoints and a WebSocket stream. The browser dashboard renders
live elevator cabs, passenger dots, floor metadata, movement totals, queued passengers, and average wait time. When
`DATABASE_URL` is configured, the server also writes simulation run metadata and passenger lifecycle events to PostgreSQL
without changing the dashboard experience.

```mermaid
flowchart LR
   Browser[Browser dashboard\nHTML CSS TypeScript]
   FastAPI[FastAPI app\nREST endpoints and WebSocket]
   Engine[SimulationEngine\nasync tick loop and lock]
   Domain[Simulation domain\nBuilding Elevators Passengers Dispatcher]
   Postgres[(PostgreSQL sidecar\noptional run and event persistence)]
   Tests[unittest suite\ndispatch simulation database checks]

   Browser <-->|REST and WebSocket| FastAPI
   FastAPI --> Engine
   Engine --> Domain
   Engine -. optional DATABASE_URL .-> Postgres
   Tests --> Engine
   Tests --> Domain
```

| Area | Responsibility | Location |
| --- | --- | --- |
| API | FastAPI routes, request validation, database helpers, WebSocket updates | `workspace/api/` |
| Simulation | Building, elevators, passengers, dispatcher, tick lifecycle | `workspace/simulation/` |
| UI | HTML template, TypeScript source, served JavaScript, CSS | `workspace/ui/` |
| Tests | `unittest` coverage for dispatcher, simulation, and database helper behavior | `workspace/tests/` |
| Devcontainer | Codespaces runtime, Docker-in-Docker, PostgreSQL sidecar, tooling | `.devcontainer/` |
| Copilot customization | Prompts, skills, agents, path-specific instructions | `.github/` |

### Runtime API Quick Reference

| Endpoint | Purpose |
| --- | --- |
| `GET /` | Serves the dashboard HTML. |
| `GET /api/state` | Returns the latest simulation snapshot. |
| `POST /api/passengers` | Adds a validated passenger request with different origin and destination floors. |
| `POST /api/control` | Pauses or resumes the simulation. |
| `POST /api/restart` | Restarts the in-memory simulation and resets persistence tables when `DATABASE_URL` is configured. |
| `GET /ws` | Streams live state snapshots to the dashboard over WebSockets. |

## Dashboard Target State

Use this screenshot as the target state for the live dashboard layout.

![Dashboard target state](docs/images/live-dashboard-target-state.png)

## What You Will Learn

| Topic | Practice |
| --- | --- |
| Copilot instructions | Use repository and path-specific instructions to guide code generation. |
| Prompt files | Run reusable `.prompt.md` workflows for setup and feature changes. |
| Skills | Package repeatable procedures, such as PostgreSQL schema inspection, as `SKILL.md` assets. |
| FastAPI | Add validated REST endpoints and WebSocket behavior. |
| Simulation design | Extend a small domain model with explicit state transitions. |
| Frontend without frameworks | Update TypeScript, CSS, and HTML while preserving the live dashboard. |
| Devcontainer tooling | Work with Codespaces, Docker-in-Docker, PostgreSQL, psql, Azure tooling, Terraform, and Bicep. |
| Verification loops | Run compile, unit test, UI build, and database inspection checks after changes. |

## Lab Modules

| Module | Focus | Outcome |
| --- | --- | --- |
| Setup | Fork, Codespaces, prerequisites, validation | A working development environment. |
| Lab 01 | Initialize the elevator dispatch app | Baseline FastAPI app, simulation, UI, and tests. |
| Lab 02 | Add PostgreSQL and persistence labs | Compose sidecar, init SQL, event persistence, and table reset workflows. |
| Lab 03 | Use GitHub metadata and PR review workflows | Issue type discovery plus Review-agent prompts for small UI PRs. |
| Lab 04 | Prepare Azure migration guidance | Azure deployment instructions and migration prompt scaffolding. |
| Future labs | Basement support, analytics, deployment implementation, and richer dispatch experiments | Incremental extensions driven by prompts, PRDs, and tests. |

### Lab Progress

This checklist follows the numeric prompt sequence in `.github/prompts/` so participants can see which reusable
workflows have been authored or completed.

- [x] `00.00`: Create meta/update README and PRD prompt assets for maintaining workshop documentation.
- [x] `01.00`: Initialize the FastAPI elevator dispatch app, dashboard, simulation modules, and tests.
- [x] `01.01`: Create the README task-list workflow that anchors the lab sequence.
- [x] `02.00`: Add the PostgreSQL devcontainer sidecar, init schema, and optional database engine bootstrap.
- [x] `02.01`: Add cloud and modernization tooling to the devcontainer.
- [x] `02.02`: Add a Coding Agent prompt for GitHub Copilot CLI/devcontainer feature work.
- [x] `02.03`: Persist simulation runs and passenger lifecycle events to PostgreSQL when `DATABASE_URL` is set.
- [ ] `02.04`: Optional Coding Agent exercise to add a basement level and update the UI animation.
- [x] `02.05`: Add a reset-all-tables prompt that verifies tables, queries records, deletes rows, and validates counts.
- [x] `02.06`: Reset PostgreSQL tables whenever the UI **Restart simulation** flow calls `POST /api/restart`.
- [x] `03.00`: List repository-supported GitHub issue types through MCP.
- [x] `03.01`: Add GitHub Copilot Review-agent prompt variants for reviewing ev-02 and ev-04 cab color PRs.
- [x] `04.00`: Establish Azure deployment custom instructions scoped to `workspace/**`.
- [ ] `04.01`: Expand the Azure migration prompt into an executable deployment lab.
- [ ] Future: Add dashboard analytics for run history and dispatch performance.

## Completed Reference Solution

During lab demonstrations, facilitators may move the current `workspace/` contents into a top-level `completed/` folder
and then rebuild the app in a fresh, empty `workspace/` by running the indexed prompts in sequence. The `completed/`
folder is intended to act as a facilitator reference solution and is excluded from repository-level Copilot context so
participants practice rebuilding from prompts, instructions, tests, and visible documentation instead of copying the
finished app.

Keep these caveats in mind:

- Treat `completed/` as a reference snapshot, not an implementation source for Copilot during rebuild labs.
- Content exclusion controls Copilot context; it is not a filesystem or Git security boundary.
- Expect functionally equivalent rebuilt code rather than byte-for-byte identical output.
- Validate after each prompt or lab cluster with `compileall`, `unittest`, `npm run build`, and an app smoke test.
- Reset PostgreSQL tables or volumes when a clean database state is needed for the rebuilt workspace.

## Pre-Configured Copilot Features

| Feature | Location | Notes |
| --- | --- | --- |
| Repository instructions | `.github/copilot-instructions.md` | Project structure, architecture, Python, frontend, PRD, and change-discipline rules. |
| Path instructions | `.github/instructions/` | TypeScript, `unittest`, and Azure deployment conventions. |
| Prompt files | `.github/prompts/` | Reusable lab workflows for initialization, PostgreSQL, GitHub issue metadata, PR review, and Azure migration. |
| Skills | `.github/skills/` | PostgreSQL devcontainer setup, schema inspection, and data persistence workflows. |
| Agents | `.github/agents/` | Documentation and Markdown lint/edit helpers. |

## Useful Commands

| Task | Command |
| --- | --- |
| Create venv | `cd workspace && python -m venv .venv` |
| Activate venv | `source workspace/.venv/bin/activate` |
| Install Python deps | `cd workspace && python -m pip install -r requirements.txt` |
| Install UI deps | `cd workspace && npm install` |
| Run app with current environment | `cd workspace && python -m uvicorn api.server:app --reload --port 7000` |
| Run app without persistence | `cd workspace && env -u DATABASE_URL python -m uvicorn api.server:app --reload --port 7000` |
| Run app with Postgres persistence | `cd workspace && DATABASE_URL=postgresql://elevator:elevator@postgres:5432/elevator_dispatch python -m uvicorn api.server:app --reload --port 7000` |
| Compile Python | `cd workspace && python -m compileall .` |
| Run tests | `cd workspace && python -m unittest discover -s tests -v` |
| Build UI | `cd workspace && npm run build` |
| Inspect Postgres schema | `.github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh` |
| Connect with psql | `psql postgresql://elevator:elevator@postgres:5432/elevator_dispatch` |
| Count persisted rows | `PGPASSWORD=elevator psql -h postgres -U elevator -d elevator_dispatch -c "SELECT event_type, COUNT(*) FROM passenger_events GROUP BY event_type;"` |

## Repository Structure

```text
ghcp-elevator-dispatch/
├── .devcontainer/                 # Codespaces and devcontainer configuration
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── postgres-init/             # PostgreSQL init SQL
├── .github/
│   ├── agents/                    # Custom Copilot agent profiles
│   ├── instructions/              # Path-specific instructions
│   ├── prompts/                   # Reusable prompt workflows, numbered by lab sequence
│   ├── skills/                    # Project skills and script artifacts
│   └── copilot-instructions.md    # Repository-wide Copilot instructions
├── docs/                          # PRDs and reference images
├── completed/                     # Excluded facilitator reference solution, when populated
├── workspace/
│   ├── api/                       # FastAPI application
│   ├── simulation/                # Elevator dispatch domain model
│   ├── tests/                     # unittest suite, including database helper tests
│   ├── ui/                        # Dashboard template and assets
│   ├── package.json               # TypeScript build tooling
│   └── requirements.txt           # Python dependencies
└── README.md
```

## PostgreSQL Sidecar

The devcontainer includes a PostgreSQL 16 sidecar for persistence and analytics labs. The simulation still keeps live
state in memory, but the FastAPI app can write run metadata and passenger lifecycle events to PostgreSQL when
`DATABASE_URL` is set. The devcontainer sets this variable to the default sidecar connection string; manual environments
must opt in by exporting it. Clicking **Restart simulation** clears the application tables before creating the fresh run
row.

Default connection string:

```text
postgresql://elevator:elevator@postgres:5432/elevator_dispatch
```

Inspect the initialized schema:

```bash
.github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh
```

Expected tables:

- `simulation_runs`
- `passenger_events`
- `scenarios`

Runtime behavior:

- `simulation_runs` records run metadata, including dispatcher strategy, tick interval, spawn chance, totals, and wait
   time aggregates.
- `passenger_events` records `created`, `assigned`, `boarded`, and `exited` events.
- `scenarios` is reserved for future replay and analytics labs.
- `POST /api/restart` deletes records from `passenger_events`, `scenarios`, and `simulation_runs`, then creates a fresh
   run row when persistence is enabled.

## Troubleshooting

| Symptom | Try This |
| --- | --- |
| Codespace opens in recovery mode | Review the creation log, then check recent `.devcontainer/` feature changes. Docker-in-Docker on Debian trixie must use `"moby": false`. |
| `npm` is missing | Rebuild the devcontainer so the Node feature is installed, or install Node.js LTS for manual setup. |
| `psql` is missing | Rebuild the devcontainer so the PostgreSQL client package is installed. |
| Postgres tables are missing | Recreate the Postgres volume or apply `.devcontainer/postgres-init/001-schema.sql`; init scripts run only when the volume is first created. |
| Passenger events are not written | Start uvicorn with `DATABASE_URL=postgresql://elevator:elevator@postgres:5432/elevator_dispatch`. |
| Tables repopulate after reset | Stop or pause the running app, or remember that the simulation may immediately write a fresh run or new passenger events after restart. |
| Port 7000 is already in use | Start uvicorn with another port, for example `--port 7001`. |
| UI changes are not reflected | Update `workspace/ui/main.ts`, run `npm run build`, and verify `workspace/ui/static/main.js` changed. |

## Contributing

Keep application code under `workspace/`. Product requirements documents belong in `docs/` and should use the `prd-*.md`
naming pattern. Custom Copilot prompts, skills, instructions, and agents belong under `.github/`.

Before opening a pull request or handing off work, run the relevant validation commands and summarize any checks that
could not be run in the current environment.

## License

See [LICENSE](LICENSE).
