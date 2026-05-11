---
name: postgres-devcontainer
description: >-
  Set up a containerized PostgreSQL database inside a
  GitHub Codespaces dev container with Docker Compose.
  Use when adding Postgres to a devcontainer, creating
  docker-compose.yml for a database service, writing
  init SQL scripts, or wiring DATABASE_URL into a
  Python FastAPI project.
---

# PostgreSQL Dev Container Integration

## When to Use

- Adding a PostgreSQL service to a Codespaces or VS Code
  dev container configuration.
- Creating `docker-compose.yml` with a Python app
  container and a Postgres sidecar.
- Writing idempotent init SQL scripts that run on first
  database creation.
- Wiring `DATABASE_URL` into a FastAPI or async Python
  project.

## Dev Container Structure

```text
.devcontainer/
├── devcontainer.json
├── docker-compose.yml
└── postgres-init/
    └── 001-schema.sql
```

## Procedure

> **Idempotent by default.** Before creating any file,
> check whether it already exists. If it does, merge the
> required keys or sections into the existing content
> rather than overwriting. Specifically:
>
> - **JSON files** (`devcontainer.json`): read the
>   existing object, add missing keys, append to arrays
>   (e.g. `forwardPorts`, `extensions`) without
>   duplicating values, and preserve any user-added
>   fields.
> - **YAML files** (`docker-compose.yml`): add missing
>   services and volumes; do not remove or rewrite
>   existing service definitions.
> - **SQL files** (`001-schema.sql`): append new
>   `CREATE TABLE IF NOT EXISTS` statements. Never drop
>   or recreate existing tables.

### 1. Create `devcontainer.json`

Use [`assets/devcontainer.json`](./assets/devcontainer.json)
as the starting template.

Use `dockerComposeFile` to reference a Compose file.
Set `service` to the app container name. Forward
`7000` (app) and `5432` (Postgres).

Key fields:

| Field | Value |
| --- | --- |
| `dockerComposeFile` | `docker-compose.yml` |
| `service` | `app` |
| `workspaceFolder` | `/workspaces/${localWorkspaceFolderBasename}` |
| `forwardPorts` | `7000` and `5432` |
| `postCreateCommand` | Venv setup, pip install, npm install |

Include VS Code extensions in `customizations.vscode.extensions`:

- `ms-python.python`
- `ms-azuretools.vscode-docker`
- `GitHub.copilot`
- `GitHub.copilot-chat`

### 2. Create `docker-compose.yml`

Use [`assets/docker-compose.yml`](./assets/docker-compose.yml)
as the starting template. It defines two services:

**`app`** — the dev container:

- Image: `mcr.microsoft.com/devcontainers/python:3.12`
- Mount the repo root into `/workspaces/`
- Set `command: sleep infinity`
- Set `depends_on: [postgres]`
- Set `DATABASE_URL` environment variable

**`postgres`** — the database:

- Image: `postgres:16`
- Set `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Expose port `5432`
- Use a named volume for `/var/lib/postgresql/data`
- Mount `./postgres-init` to
  `/docker-entrypoint-initdb.d:ro`

Add a `volumes:` section for the named data volume.

### 3. Create Init SQL Script

Use [`assets/001-schema.sql`](./assets/001-schema.sql)
as the starting template. Place SQL files in
`.devcontainer/postgres-init/`.
Postgres runs files in `/docker-entrypoint-initdb.d/`
alphabetically on first volume creation only.

Guidelines for init scripts:

- Use `CREATE TABLE IF NOT EXISTS` for idempotency.
- Use `UUID` primary keys via `gen_random_uuid()`.
- Use `TIMESTAMPTZ` for time columns.
- Add indexes on foreign keys and common filter columns.
- Name files with numeric prefixes: `001-schema.sql`,
  `002-seed.sql`.

### 4. Wire the Connection String

The app reads `DATABASE_URL` from the environment.
Docker Compose sets it automatically. The connection
string format:

```text
postgresql://<user>:<password>@postgres:5432/<dbname>
```

The hostname `postgres` resolves inside the Compose
network to the database container.

### 5. Keep Database Optional

When `DATABASE_URL` is not set, the app must run in
its default in-memory mode. Check for the variable at
startup and skip database initialization if absent.
Never raise an error for a missing database in
development or workshop environments.

## Python Async Database Stack

For FastAPI projects, use:

| Package | Purpose |
| --- | --- |
| `asyncpg` | Fast async PostgreSQL driver |
| `sqlalchemy[asyncio]` | Async ORM / Core with connection pooling |

Create the async engine only when `DATABASE_URL` is
present. See
[`scripts/create_engine.py`](./scripts/create_engine.py)
for the reference implementation.

## Validation Checklist

- [ ] `devcontainer.json` references `docker-compose.yml`
- [ ] Docker Compose defines `app` and `postgres` services
- [ ] `postgres-init/` is mounted read-only into the
      Postgres container
- [ ] Init SQL uses `IF NOT EXISTS` for idempotency
- [ ] `DATABASE_URL` is set in the `app` service env
- [ ] App starts cleanly when `DATABASE_URL` is absent
- [ ] `psql` can connect from the app container using
      the service hostname `postgres`

## Reference

- [Postgres Docker & SQLAlchemy async patterns](./references/postgres-sqlalchemy.md)
- [Dev Containers specification](https://containers.dev/implementors/json_reference/)
- [Postgres Docker image docs](https://hub.docker.com/_/postgres)
- [SQLAlchemy async engine](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
