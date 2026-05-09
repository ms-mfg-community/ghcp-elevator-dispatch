# Elevator Dispatch Workshop Starter

This starter project simulates a 5-floor building with 4 elevators and exposes a small FastAPI app with a live dashboard.

## Features

- Dispatcher-based elevator assignment with a simple, teachable heuristic
- In-memory building state with manual passenger creation
- WebSocket-driven dashboard with animated elevator cabs and passenger dots
- Clear module boundaries for later lab extensions

## Project layout

```text
workspace/
├── api/
├── simulation/
├── tests/
└── ui/
```

## Run locally

Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the app from the `workspace` directory:

```bash
python -m uvicorn api.server:app --reload
```

Open <http://127.0.0.1:8000> to view the dashboard.

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Notes for the lab

- Passenger creation is manual for now so the simulation stays predictable.
- `TODO` markers highlight good extension points for future workshop steps.
