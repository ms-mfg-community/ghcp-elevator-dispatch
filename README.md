# Elevator Dispatch Workshop - Hands-On Lab

A hands-on GitHub Copilot workshop for building and extending a real-time elevator dispatch simulation. The lab uses a
Python FastAPI backend, a framework-free TypeScript dashboard, a PostgreSQL devcontainer sidecar, and repository-level
Copilot customizations so participants can practice prompts, skills, instructions, and iterative application changes on
a small but realistic codebase.

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
PostgreSQL is optional for the current app because the simulation still runs in memory, but `psql` is useful for schema
inspection labs.

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

Start the dashboard:

```bash
python -m uvicorn api.server:app --reload --port 7000
```

Open <http://127.0.0.1:7000> to view the live elevator dashboard.

## The Application

The application simulates a 5-floor building with 4 elevators. A simple dispatcher assigns passengers to the nearest
compatible elevator, while a FastAPI server exposes REST endpoints and a WebSocket stream. The browser dashboard renders
live elevator cabs, passenger dots, floor metadata, movement totals, queued passengers, and average wait time.

```mermaid
flowchart LR
   Browser[Browser dashboard\nHTML CSS TypeScript]
   FastAPI[FastAPI app\nREST endpoints and WebSocket]
   Engine[SimulationEngine\nasync tick loop and lock]
   Domain[Simulation domain\nBuilding Elevators Passengers Dispatcher]
   Postgres[(PostgreSQL sidecar\noptional future persistence)]
   Tests[unittest suite\ndispatch and simulation checks]

   Browser <-->|REST and WebSocket| FastAPI
   FastAPI --> Engine
   Engine --> Domain
   FastAPI -. optional DATABASE_URL .-> Postgres
   Tests --> Engine
   Tests --> Domain
```

| Area | Responsibility | Location |
| --- | --- | --- |
| API | FastAPI routes, request validation, WebSocket updates | `workspace/api/` |
| Simulation | Building, elevators, passengers, dispatcher, tick lifecycle | `workspace/simulation/` |
| UI | HTML template, TypeScript source, served JavaScript, CSS | `workspace/ui/` |
| Tests | `unittest` coverage for dispatcher and simulation behavior | `workspace/tests/` |
| Devcontainer | Codespaces runtime, Docker-in-Docker, PostgreSQL sidecar, tooling | `.devcontainer/` |
| Copilot customization | Prompts, skills, agents, path-specific instructions | `.github/` |

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
| Lab 02 | Add PostgreSQL devcontainer support | Compose sidecar, init SQL, optional database engine. |
| Lab 03 | Add cloud and modernization tooling | Devcontainer features for GitHub, Azure, Docker, Terraform, Bicep, MCP, and psql. |
| Lab 04 | Create reusable Copilot assets | Prompts and skills that automate repeatable workshop tasks. |
| Future labs | Persistence, analytics, deployment, and richer dispatch experiments | Incremental extensions driven by PRDs and tests. |

### Lab Progress

- [x] Setup: fork or open the workshop repository, choose an environment path, and validate the toolchain.
- [x] Lab 01: Initialize the FastAPI elevator dispatch app, dashboard, simulation modules, and tests.
- [x] Lab 02: Add the PostgreSQL devcontainer sidecar, init schema, and optional database engine bootstrap.
- [x] Lab 03: Add cloud and modernization tooling to the devcontainer.
- [x] Lab 04: Create reusable Copilot prompts and skills, including PostgreSQL schema inspection.
- [ ] Future lab: Persist simulation runs and passenger events to PostgreSQL.
- [ ] Future lab: Add dashboard analytics for run history and dispatch performance.
- [ ] Future lab: Prepare an Azure deployment path with infrastructure-as-code validation.

## Pre-Configured Copilot Features

| Feature | Location | Notes |
| --- | --- | --- |
| Repository instructions | `.github/copilot-instructions.md` | Project structure, architecture, Python, frontend, PRD, and change-discipline rules. |
| Path instructions | `.github/instructions/` | TypeScript and `unittest` conventions. |
| Prompt files | `.github/prompts/` | Reusable lab workflows for initialization, task lists, PostgreSQL, and devcontainer tooling. |
| Skills | `.github/skills/` | PostgreSQL devcontainer setup and schema inspection workflows. |
| Agents | `.github/agents/` | Documentation and Markdown lint/edit helpers. |

## Useful Commands

| Task | Command |
| --- | --- |
| Create venv | `cd workspace && python -m venv .venv` |
| Activate venv | `source workspace/.venv/bin/activate` |
| Install Python deps | `cd workspace && python -m pip install -r requirements.txt` |
| Install UI deps | `cd workspace && npm install` |
| Run app | `cd workspace && python -m uvicorn api.server:app --reload --port 7000` |
| Compile Python | `cd workspace && python -m compileall .` |
| Run tests | `cd workspace && python -m unittest discover -s tests -v` |
| Build UI | `cd workspace && npm run build` |
| Inspect Postgres schema | `.github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh` |
| Connect with psql | `psql postgresql://elevator:elevator@postgres:5432/elevator_dispatch` |

## Repository Structure

```text
ghcp-temp-elevator-disptach/
├── .devcontainer/                 # Codespaces and devcontainer configuration
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── postgres-init/             # PostgreSQL init SQL
├── .github/
│   ├── agents/                    # Custom Copilot agent profiles
│   ├── instructions/              # Path-specific instructions
│   ├── prompts/                   # Reusable prompt workflows
│   ├── skills/                    # Project skills and script artifacts
│   └── copilot-instructions.md    # Repository-wide Copilot instructions
├── docs/                          # PRDs and reference images
├── workspace/
│   ├── api/                       # FastAPI application
│   ├── simulation/                # Elevator dispatch domain model
│   ├── tests/                     # unittest suite
│   ├── ui/                        # Dashboard template and assets
│   ├── package.json               # TypeScript build tooling
│   └── requirements.txt           # Python dependencies
└── README.md
```

## PostgreSQL Sidecar

The devcontainer includes a PostgreSQL 16 sidecar for future persistence and analytics labs. The current app still keeps
simulation state in memory, so empty database tables are expected until a persistence lab writes data.

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

## Troubleshooting

| Symptom | Try This |
| --- | --- |
| Codespace opens in recovery mode | Review the creation log, then check recent `.devcontainer/` feature changes. Docker-in-Docker on Debian trixie must use `"moby": false`. |
| `npm` is missing | Rebuild the devcontainer so the Node feature is installed, or install Node.js LTS for manual setup. |
| `psql` is missing | Rebuild the devcontainer so the PostgreSQL client package is installed. |
| Postgres tables are missing | Recreate the Postgres volume or apply `.devcontainer/postgres-init/001-schema.sql`; init scripts run only when the volume is first created. |
| Port 7000 is already in use | Start uvicorn with another port, for example `--port 7001`. |
| UI changes are not reflected | Update `workspace/ui/main.ts`, run `npm run build`, and verify `workspace/ui/static/main.js` changed. |

## Contributing

Keep application code under `workspace/`. Product requirements documents belong in `docs/` and should use the `prd-*.md`
naming pattern. Custom Copilot prompts, skills, instructions, and agents belong under `.github/`.

Before opening a pull request or handing off work, run the relevant validation commands and summarize any checks that
could not be run in the current environment.

## License

See [LICENSE](LICENSE).
