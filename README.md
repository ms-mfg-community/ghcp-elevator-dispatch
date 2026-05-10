# Elevator Dispatch Workshop

A GitHub Copilot workshop project that simulates a 5-floor,
4-elevator dispatch system with a real-time web dashboard.

## Lab tasks

## What it does

The application under `workspace/` runs an in-memory elevator
simulation driven by a simple dispatcher heuristic. A FastAPI
backend exposes REST endpoints and a WebSocket feed, and an
HTML/CSS/JS dashboard renders the live building view with
animated elevator cabs and passenger dots.

## Project layout

```text
workspace/
├── api/            # FastAPI routes, WebSocket, Pydantic models
├── simulation/     # Domain model: building, elevators,
│                   # passengers, dispatcher, engine
├── tests/          # unittest-based test suite
└── ui/             # HTML template, TypeScript source, served static assets
```

## Getting started

All commands run from the `workspace/` directory.

Install Python dependencies:

```bash
cd workspace
python -m pip install -r requirements.txt
```

Start the app:

```bash
python -m uvicorn api.server:app --reload
```

Open <http://127.0.0.1:8000> to view the dashboard.

## Validation

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

For UI TypeScript changes:

```bash
npm install
npm run build
```

## Contributing

Custom Copilot prompts live in `.github/prompts/`.
Repository-level Copilot instructions are in
`.github/copilot-instructions.md`. Follow those conventions
when extending the project through new lab steps.
