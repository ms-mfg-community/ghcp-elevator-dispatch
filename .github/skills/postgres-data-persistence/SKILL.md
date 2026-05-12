# Skill: PostgreSQL Data Persistence for Elevator Dispatch Simulation

Add optional database persistence to the elevator dispatch simulation while preserving the in-memory engine and framework-free dashboard.

## When to Use This Skill

Use this skill when you need to:
- Write simulation event data (passenger spawned, boarded, exited) to PostgreSQL tables.
- Persist simulation run metadata (start time, ticks, final state) for historical analysis.
- Keep the dashboard and API unchanged (data persistence is transparent).
- Support graceful fallback to in-memory mode if the database is unavailable.
- Test event logging without requiring a live database.

**Prerequisites:**
- PostgreSQL sidecar running (from `.devcontainer/docker-compose.yml`).
- Schema initialized via `.devcontainer/postgres-init/001-schema.sql`.
- FastAPI backend (`workspace/api/server.py`).
- Python 3.10+.

## How It Works

### Architecture

```
SimulationEngine (in-memory ticks)
    ↓
   Events (spawned, boarded, exited, completed)
    ↓
Database Module (SQLAlchemy async)
    ↓
PostgreSQL Tables (async writes, non-blocking)
    ↓
Historical Data (query in future labs)
```

### Key Design Principles

1. **Optional Persistence:** If `DATABASE_URL` is not set, simulation runs in-memory mode only.
2. **Non-Blocking Writes:** Event inserts use `asyncio.create_task()` to avoid blocking simulation ticks.
3. **Graceful Error Handling:** Database failures log warnings but do not crash the simulator.
4. **No Schema Migration Framework:** Schema is pre-initialized; no Alembic or Flyway required.
5. **Transparent to UI:** Dashboard and WebSocket remain unchanged.

---

## Step-by-Step Implementation

### Step 1: Create Database Helper Module

**File:** `workspace/api/database.py`

**Responsibilities:**
- Create async SQLAlchemy engine from `DATABASE_URL` environment variable.
- Provide helper functions: `insert_simulation_run()`, `insert_passenger_event()`, `update_simulation_run_completed()`.
- Handle connection errors gracefully (log warning, continue without database).
- Manage engine lifecycle (initialize on app startup, close on shutdown).

**Reference Implementation:**
See `./scripts/database.py` in this skill directory.

**Key Functions:**

```python
async def insert_simulation_run(sim_id, num_floors, num_elevators)
    # Creates a new simulation_runs record

async def insert_passenger_event(sim_run_id, passenger_id, event_type, floor, timestamp, elevator_id=None, wait_time_seconds=None)
    # Logs a passenger event (spawned, boarded, exited)

async def update_simulation_run_completed(sim_id, final_tick, total_passengers)
    # Updates simulation_runs with completion metadata

async def get_session()
    # Returns an async SQLAlchemy session if database is available
```

**DATABASE_URL Format:**
```
postgresql://user:password@host:port/database
# Automatically converted to: postgresql+asyncpg://user:password@host:port/database
```

---

### Step 2: Wire Event Logging to SimulationEngine

**File:** `workspace/simulation/simulation.py`

**Modifications:**

1. **Add database module import:**
   ```python
   import asyncio
   from api.database import (
       insert_simulation_run,
       insert_passenger_event,
       update_simulation_run_completed
   )
   ```

2. **In `SimulationEngine.__init__()`, create simulation run record:**
   ```python
   self.simulation_id = f"sim-{int(time.time())}-{uuid.uuid4().hex[:8]}"
   asyncio.create_task(insert_simulation_run(
       self.simulation_id,
       len(building.floors),
       len(building.elevators)
   ))
   ```

3. **When passenger spawns, log event:**
   ```python
   asyncio.create_task(insert_passenger_event(
       self.simulation_id,
       passenger.id,
       "spawned",
       passenger.source_floor,
       self.tick
   ))
   ```

4. **When passenger boards elevator, log event with wait time:**
   ```python
   wait_time = self.tick - passenger.spawn_tick
   asyncio.create_task(insert_passenger_event(
       self.simulation_id,
       passenger.id,
       "boarded",
       passenger.current_floor,
       self.tick,
       elevator_id=elevator.id,
       wait_time_seconds=wait_time
   ))
   ```

5. **When passenger exits, log event:**
   ```python
   asyncio.create_task(insert_passenger_event(
       self.simulation_id,
       passenger.id,
       "exited",
       passenger.current_floor,
       self.tick
   ))
   ```

6. **When simulation completes, update run record:**
   ```python
   def stop(self):
       self.running = False
       asyncio.create_task(update_simulation_run_completed(
           self.simulation_id,
           self.tick,
           len(self.building.served_passengers)
       ))
   ```

---

### Step 3: Initialize Database in FastAPI Server

**File:** `workspace/api/server.py`

**Modifications:**

1. **Import database shutdown:**
   ```python
   from api.database import close_engine
   ```

2. **Add shutdown event:**
   ```python
   @app.on_event("shutdown")
   async def shutdown_event():
       await close_engine()
   ```

3. **Pass `database_enabled=True` to SimulationEngine:**
   ```python
   engine = SimulationEngine(building, database_enabled=True)
   ```

---

### Step 4: Add Unit Tests

**File:** `workspace/tests/test_database.py`

**Coverage:**
- Insert functions handle missing database gracefully (no errors, no exceptions).
- Mocked sessions validate SQL calls without a live database.
- Integration tests (if `DATABASE_URL` is set) validate inserts and queries.

**Reference Implementation:**
See `./scripts/test_database.py` in this skill directory.

**Run tests:**
```bash
cd workspace
python -m unittest discover -s tests -v
```

---

### Step 5: Validate with Live Simulation

**Duration:** 5–10 minutes

1. **Start the FastAPI app:**
   ```bash
   cd workspace
   python -m uvicorn api.server:app --reload --port 7000
   ```

2. **Open the dashboard** in your browser (localhost:7000 or Codespaces forwarded URL).

3. **Let the simulation run for 30–60 seconds** to accumulate events.

4. **Query PostgreSQL in another terminal:**
   ```bash
   # Check row counts
   psql -h postgres -U elevator -d elevator_dispatch \
       -c "SELECT COUNT(*) FROM passenger_events;"
   
   # View latest simulation run
   psql -h postgres -U elevator -d elevator_dispatch \
       -c "SELECT * FROM simulation_runs ORDER BY started_at DESC LIMIT 1;"
   
   # Summarize events by type
   psql -h postgres -U elevator -d elevator_dispatch \
       -c "SELECT event_type, COUNT(*) FROM passenger_events GROUP BY event_type;"
   ```

5. **Expected results:**
   - `passenger_events` contains rows (spawned, boarded, exited).
   - `simulation_runs` shows active run with start time.
   - Event distribution is balanced across types.

---

## Testing Without a Live Database

If PostgreSQL is not running or `DATABASE_URL` is not set:

1. **Unset the environment variable:**
   ```bash
   unset DATABASE_URL
   ```

2. **Start the app:**
   ```bash
   python -m uvicorn api.server:app --reload --port 7000
   ```

3. **Expected behavior:**
   - App logs: `DATABASE_URL not set. Running in-memory mode.`
   - Dashboard works normally.
   - No data is written to PostgreSQL.
   - No errors or warnings in logs (graceful degradation).

This is the **default and recommended mode for local development and testing**.

---

## Configuration

### Environment Variables

| Variable | Description | Example | Default |
| --- | --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://elevator:elevator@postgres:5432/elevator_dispatch` | Unset (in-memory mode) |
| `FASTAPI_ENV` | Environment (development, staging, production) | `production` | `production` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | `INFO` |

### Schema Requirements

The PostgreSQL database must have these tables pre-initialized:

**simulation_runs:**
```sql
CREATE TABLE simulation_runs (
    id VARCHAR(255) PRIMARY KEY,
    num_floors INTEGER,
    num_elevators INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    final_tick INTEGER,
    total_passengers_served INTEGER
);
```

**passenger_events:**
```sql
CREATE TABLE passenger_events (
    id SERIAL PRIMARY KEY,
    simulation_run_id VARCHAR(255) REFERENCES simulation_runs(id),
    passenger_id INTEGER,
    event_type VARCHAR(50),  -- 'spawned', 'boarded', 'exited'
    floor INTEGER,
    timestamp BIGINT,  -- tick number
    elevator_id INTEGER,
    wait_time_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**scenarios:**
```sql
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    num_floors INTEGER,
    num_elevators INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Schema is automatically initialized via `.devcontainer/postgres-init/001-schema.sql` when the Postgres container starts.

---

## Performance Considerations

### Non-Blocking Writes

Each database insert is wrapped in `asyncio.create_task()`:

```python
asyncio.create_task(insert_passenger_event(...))  # Fire-and-forget
```

This means:
- Simulation ticks are **not blocked** by database I/O.
- Database writes happen **asynchronously** in the background.
- If a write fails, an error is logged but the simulator continues.

### Data Accumulation

A 24-hour simulation with typical passenger spawn rates (5–10 per tick) can create:
- **432,000 ticks** (at 5 ticks/second × 86,400 seconds)
- **2–4 million passenger events** (at 5–10 spawned per tick)
- **Storage:** ~500 MB – 1 GB (depending on row width and indexes)

**For production deployments, consider:**
- Data retention policies (keep only last 7–30 days).
- Archiving or partitioning for historical data.
- Index optimization on (`simulation_run_id`, `event_type`).

---

## Troubleshooting

| Issue | Cause | Solution |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'sqlalchemy'` | SQLAlchemy not installed | `cd workspace && python -m pip install -r requirements.txt` |
| `asyncpg.exceptions.CannotConnectNowError` | PostgreSQL not running | Run `docker-compose up -d` in `.devcontainer/` or restart devcontainer |
| `passenger_events table empty after 1-min run` | Inserts are being called but data not persisted | Check logs for errors; run `psql -c "SELECT * FROM passenger_events LIMIT 1;"` |
| `AttributeError: 'NoneType' has no attribute 'execute'` | `async_session_factory` is None (database unavailable) | This is **expected and correct**; app gracefully falls back to in-memory mode. Check logs for `DATABASE_URL not set` message. |
| `FOREIGN KEY constraint failed` | `simulation_runs` record not created before events inserted | Ensure `insert_simulation_run()` is awaited/created in `SimulationEngine.__init__()`. Consider adding `asyncio.sleep(0.1)` to allow initialization to complete. |

---

## Next Steps

After implementing this skill:

1. **Lab 03 (Analytics):** Add API endpoints (`GET /api/events/`, `GET /api/runs/`) to query historical data.
2. **Lab 04 (Reporting):** Build a dashboard showing wait time trends, system efficiency metrics over time.
3. **Lab 05 (Azure Deployment):** Deploy to Azure Container Apps with Azure Database for PostgreSQL.

---

## References

- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)
- [FastAPI Events](https://fastapi.tiangolo.com/advanced/events/)
- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html) (for analytics queries)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

---

## Files in This Skill

- `SKILL.md` - This file; implementation and validation guidance.
- `scripts/database.py` - Reference implementation of database module.
- `scripts/test_database.py` - Reference unit tests with mocked and integration variants.
