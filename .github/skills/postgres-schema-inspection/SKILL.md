---
name: postgres-schema-inspection
description: >-
  Inspect and test the elevator dispatch PostgreSQL schema with psql. Use when listing database schemas,
  describing tables, querying row counts, checking passenger_events, simulation_runs, scenarios, or validating
  the devcontainer Postgres sidecar.
argument-hint: "optional DATABASE_URL override"
---

# PostgreSQL Schema Inspection

## When to Use

- A user asks how to show PostgreSQL schemas or tables for this workshop database.
- A user wants repeatable `psql` commands for `simulation_runs`, `passenger_events`, or `scenarios`.
- You need a smoke test that confirms the devcontainer PostgreSQL sidecar is reachable and initialized.
- You need to verify whether simulation persistence tables exist or contain data.

## Procedure

1. From the repository root, run the bundled inspection script:

   ```bash
   .github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh
   ```

2. The script defaults to the workshop devcontainer database URL:

   ```text
   postgresql://elevator:elevator@postgres:5432/elevator_dispatch
   ```

3. To inspect another database, pass a `DATABASE_URL` environment variable:

   ```bash
   DATABASE_URL="postgresql://user:password@host:5432/database" \
     .github/skills/postgres-schema-inspection/scripts/inspect-postgres-schema.sh
   ```

4. Review the output sections:

   - Connection details and PostgreSQL version
   - Available schemas
   - Public tables
   - Table definitions for `simulation_runs`, `passenger_events`, and `scenarios`
   - Row counts for all workshop tables
   - Passenger event counts by event type
   - Recent simulation runs, passenger events, and scenario rows

## Expected Tables

The workshop schema currently initializes these tables from `.devcontainer/postgres-init/001-schema.sql`:

| Table | Purpose |
| --- | --- |
| `simulation_runs` | Stores run-level simulation metadata if persistence is added. |
| `passenger_events` | Stores passenger lifecycle events associated with a simulation run. |
| `scenarios` | Stores named scenario rows with origin and destination floors. |

The current application creates an optional database engine but does not yet persist simulation events. Empty row
counts are expected unless data has been inserted manually or persistence has been implemented.

## Troubleshooting

- If `psql` is missing, rebuild the devcontainer so the PostgreSQL client feature is installed.
- If `postgres` does not resolve, confirm the Codespace is using `.devcontainer/docker-compose.yml` and the `postgres`
  service is running.
- If tables are missing but the database volume already existed before the init SQL was added, recreate the Postgres
  volume or apply the schema manually. Init scripts run only on first database volume creation.

## Artifact

- [Schema inspection script](./scripts/inspect-postgres-schema.sh)