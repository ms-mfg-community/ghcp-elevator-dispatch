# Elevator Dispatch Application

This folder contains the runnable FastAPI and TypeScript application used by the Elevator Dispatch Workshop. It is the
hands-on code surface for the lab: participants run the app, inspect the simulation model, update behavior with Copilot,
and validate changes with repeatable commands.

## What It Does

The app simulates a 6-level building (B1 plus floors 1-5) with 4 elevators. A simple dispatcher assigns passengers to
compatible elevators, while a FastAPI backend streams live snapshots to a browser dashboard over WebSockets. When
`DATABASE_URL` is set, the app also writes simulation run metadata and passenger lifecycle events to PostgreSQL.

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
.venv/bin/python -m compileall api simulation tests
.venv/bin/python -m unittest discover -s tests -v
npm run build
```

If `npm run build` fails with `tsc: Permission denied` because the tracked TypeScript shim under `node_modules` is not
executable, temporarily restore executable bits for validation and then reset the mode-only changes before handoff:

```bash
chmod 755 node_modules/.bin/tsc node_modules/typescript/bin/tsc
npm run build
chmod 644 node_modules/.bin/tsc node_modules/typescript/bin/tsc
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

The PostgreSQL schema intentionally avoids optional PostgreSQL extensions. Azure Database for PostgreSQL Flexible Server
may reject `pgcrypto` unless it is allow-listed, so the application generates UUID values in Python instead of relying on
`gen_random_uuid()`.

## Azure Deployment Notes

The current Azure workshop deployment uses Azure Container Apps, Azure Container Registry, Log Analytics, a
user-assigned managed identity with `AcrPull`, and optional Azure Database for PostgreSQL Flexible Server. The deployed
workshop endpoint verified on 2026-05-13 was:

<https://ca-elevator-dispatch-dev.bluetree-41095b7a.eastus2.azurecontainerapps.io/>

Useful deployment checks:

```bash
azd env get-values
az containerapp revision list \
  --name ca-elevator-dispatch-dev \
  --resource-group rg-elevator-dispatch \
  --query '[].{name:name,active:properties.active,traffic:properties.trafficWeight,health:properties.healthState,replicas:properties.replicas}' \
  -o table
curl -fsS https://ca-elevator-dispatch-dev.bluetree-41095b7a.eastus2.azurecontainerapps.io/api/state
```

Deployment gotchas found during the Azure migration:

- `azd deploy` needs `AZURE_CONTAINER_REGISTRY_ENDPOINT` when deploying to existing Azure resources. Set it with
  `azd env set AZURE_CONTAINER_REGISTRY_ENDPOINT crelevatordispatchdev.azurecr.io` if the value is missing.
- Azure CLI read operations can succeed while ARM write operations are blocked by MFA policy. Refresh `azd` with
  `azd auth login --tenant-id 54d665dd-30f1-45c5-a8d5-d6ffcdb518f9` before retrying `azd deploy`.
- A `504` from Container Apps usually means traffic is on an unhealthy revision. Check revision health and console logs
  before changing ingress settings.
- `HEAD /` returns `405` because the dashboard route is a FastAPI `GET` route. Use `curl -fsS https://<app>/` for the
  dashboard smoke test.
- Terraform state files can contain generated database credentials. They are ignored by Git in this repository; never
  commit or share them, and rotate credentials if state is exposed outside the dev environment.

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
- Preserve the 6-level, 4-elevator default scenario with B1 stored as floor `-1` and displayed as `B1`.
- Prefer small, explicit modules and teachable heuristics over clever abstractions.
- When changing TypeScript source, run `npm run build` so `ui/static/main.js` stays current.
