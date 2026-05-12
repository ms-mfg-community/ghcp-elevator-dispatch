# Elevator Dispatch Application

This folder contains the runnable FastAPI and TypeScript application used by the Elevator Dispatch Workshop. It is the
hands-on code surface for the lab: participants run the app, inspect the simulation model, update behavior with Copilot,
and validate changes with repeatable commands.

## What It Does

The app simulates a 5-floor building with 4 elevators. A simple dispatcher assigns passengers to compatible elevators,
while a FastAPI backend streams live snapshots to a browser dashboard over WebSockets. When `DATABASE_URL` is set, the
app also writes simulation run metadata and passenger lifecycle events to PostgreSQL.

## Prerequisites

| Setup Path | Requirements |
| --- | --- |
| Codespaces or devcontainer | Dependencies are installed by the repository devcontainer. |
| Manual local setup | Python 3.10+, Node.js LTS, npm, and Git. |
| Optional database persistence and inspection | PostgreSQL client (`psql`) and access to the devcontainer Postgres sidecar. |

## Project Layout

```text
workspace/
├── api/          # FastAPI app, routes, WebSocket lifecycle, database helpers
├── simulation/   # Building, elevator, passenger, dispatcher, and tick engine
├── tests/        # unittest-based regression suite
├── ui/           # HTML template, TypeScript source, CSS, served JavaScript
├── scripts/      # Convenience wrappers for workshop utilities
├── package.json  # TypeScript build command
└── requirements.txt
```

## Run Locally

Create and activate a virtual environment from this directory:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
npm install
```

Start the app in in-memory mode:

```bash
python -m uvicorn api.server:app --reload --port 7000
```

Start the app with PostgreSQL persistence enabled:

```bash
DATABASE_URL=postgresql://elevator:elevator@postgres:5432/elevator_dispatch \
python -m uvicorn api.server:app --reload --port 7000
```

Open <http://127.0.0.1:7000> to view the dashboard.

## Verify Changes

Run these commands before handing off code changes:

```bash
python -m compileall .
python -m unittest discover -s tests -v
npm run build
```

## Inspect PostgreSQL

The live simulation state remains in memory, but the app writes database rows when `DATABASE_URL` is configured. From the
repository root, inspect the schema with:

```bash
.github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh
```

Or from this folder, use the convenience wrapper:

```bash
scripts/inspect-postgres-schema.sh
```

Expected tables are `simulation_runs`, `passenger_events`, and `scenarios`. `simulation_runs` stores run metadata, and
`passenger_events` stores `created`, `assigned`, `boarded`, and `exited` events. Clicking **Restart simulation** calls
`POST /api/restart`, clears application table rows, and creates a fresh run row when persistence is enabled.

## Extension Points

| Area | Good Workshop Changes |
| --- | --- |
| `simulation/dispatcher.py` | Try alternative dispatch heuristics while keeping the logic easy to explain. |
| `simulation/simulation.py` | Adjust tick lifecycle, passenger spawning, pause/resume, or completion behavior. |
| `api/database.py` | Extend optional persistence helpers without making the database mandatory. |
| `api/server.py` | Add validated endpoints or API-adjacent behavior through `SimulationEngine` methods. |
| `ui/main.ts` and `ui/static/styles.css` | Extend the live dashboard while keeping served JavaScript in sync. |
| `tests/` | Add focused `unittest` coverage for simulation and dispatcher changes. |

## Notes for the Lab

- Keep live simulation state in memory; use PostgreSQL only for optional run and event persistence.
- Preserve the 5-floor, 4-elevator default scenario.
- Prefer small, explicit modules and teachable heuristics over clever abstractions.
- When changing TypeScript source, run `npm run build` so `ui/static/main.js` stays current.
