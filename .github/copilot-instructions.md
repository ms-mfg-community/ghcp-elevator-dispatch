# Copilot Instructions

This repository is a workshop project for an elevator dispatch simulation. Keep generated application code under the top-level `workspace/` directory unless the user explicitly asks to change repository-level docs, prompt files, or configuration.

## Project Shape

- Treat `workspace/` as the application root.
- The backend is a Python 3.10+ FastAPI app in `workspace/api/`.
- The simulation domain model lives in `workspace/simulation/`.
- Browser UI files live in `workspace/ui/`; `workspace/ui/templates/index.html` serves the page and `workspace/ui/static/` contains served assets.
- Tests live in `workspace/tests/` and use the Python standard library `unittest` framework.

## Architecture Guidelines

- Keep simulation state in memory. Do not add a database, authentication system, queue service, or persistent storage unless the user asks.
- Preserve the educational starter-project style: small modules, clear names, explicit state transitions, and simple heuristics that are easy to explain in a workshop.
- Keep dispatch behavior isolated in `workspace/simulation/dispatcher.py` and simulation tick/lifecycle behavior in `workspace/simulation/simulation.py`.
- Keep API request validation in `workspace/api/server.py` using Pydantic models and FastAPI route handlers.
- Maintain the 5-floor, 4-elevator default scenario unless a prompt explicitly changes those requirements.
- Use straightforward scheduling heuristics; do not introduce ML or optimization libraries for dispatch logic.

## Python Conventions

- Use type hints and dataclasses consistently with the existing simulation modules.
- Prefer async-safe access through `SimulationEngine` methods when API code reads or mutates building state.
- Do not bypass the engine lock for state mutations that can be reached from FastAPI routes or WebSocket updates.
- Raise clear validation errors for invalid floor numbers and same-floor passenger trips.
- Add or update `unittest` tests for dispatch, passenger validation, simulation ticks, and API-adjacent behavior when changing those areas.

## Frontend Conventions

- Keep the UI framework-free unless the user asks for a framework.
- The served JavaScript is `workspace/ui/static/main.js`. If changing TypeScript source in `workspace/ui/main.ts`, also ensure the served JavaScript stays in sync by running the TypeScript build or making the equivalent update.
- Preserve the dashboard plus live building visualization: elevator cabs, floors, shafts, waiting passenger dots, riding passenger dots, and status controls.
- Keep CSS responsive and compatible with modern desktop and mobile browsers.

## Validation Commands

Run commands from the `workspace/` directory unless noted otherwise.

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

For UI TypeScript changes, run:

```bash
npm install
npm run build
```

To run the app locally:

```bash
python -m uvicorn api.server:app --reload
```

## Change Discipline

- Keep changes focused on the current lab prompt or user request.
- Do not rewrite unrelated generated files or prompt files.
- Do not modify files under `completed/` unless the user explicitly asks.
- Preserve existing user or formatter edits when updating files.