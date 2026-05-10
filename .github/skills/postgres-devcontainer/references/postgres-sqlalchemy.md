# Postgres Docker & SQLAlchemy Async Reference

Supplemental knowledge for the `postgres-devcontainer`
skill. The agent loads this file when deeper context is
needed beyond the procedural steps in SKILL.md.

## Postgres Docker Image Conventions

### Environment Variables

| Variable | Purpose |
| --- | --- |
| `POSTGRES_USER` | Superuser name (default: `postgres`) |
| `POSTGRES_PASSWORD` | Superuser password (required) |
| `POSTGRES_DB` | Database created on first start (default: value of `POSTGRES_USER`) |
| `PGDATA` | Override data directory (default: `/var/lib/postgresql/data`) |

### Init Scripts

Files in `/docker-entrypoint-initdb.d/` run **once** on
first volume creation, in alphabetical order. Supported
extensions:

- `.sql` — executed via `psql`
- `.sql.gz` — decompressed then executed
- `.sh` — sourced as a shell script

Scripts run as the `POSTGRES_USER` against `POSTGRES_DB`.
They do **not** re-run on subsequent container restarts
as long as the data volume persists.

### Volume Lifecycle

- Named volumes (`postgres-data:`) persist across
  container rebuilds inside a Codespace.
- Deleting the Codespace removes the volume.
- To re-run init scripts, delete the named volume:
  `docker volume rm <project>_postgres-data`.

### Health Checks

Use `pg_isready` to verify the database is accepting
connections before the app container starts:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U elevator"]
  interval: 5s
  timeout: 3s
  retries: 5
```

Then reference it from the app service:

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

## SQLAlchemy Async Patterns

### Engine Creation

- Use `create_async_engine()` from
  `sqlalchemy.ext.asyncio`.
- Replace `postgresql://` with `postgresql+asyncpg://`
  in the connection URL so SQLAlchemy routes through the
  `asyncpg` driver.
- Set `echo=False` in production; `echo=True` for
  debugging SQL statements.

### Session Management

Use `async_sessionmaker` for request-scoped sessions:

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

engine = create_async_engine(url, echo=False)
SessionLocal = async_sessionmaker(
    engine, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
```

### Table Metadata

Define tables with `DeclarativeBase` or `MetaData`:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Create tables at startup only when the engine exists:

```python
async def init_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### Connection Pooling Defaults

| Setting | Default | Notes |
| --- | --- | --- |
| `pool_size` | 5 | Max persistent connections |
| `max_overflow` | 10 | Extra connections above pool_size |
| `pool_timeout` | 30 s | Wait time for a connection |
| `pool_recycle` | -1 | Set to 1800 for long-lived apps |

For a workshop with a single user, the defaults are
sufficient. Do not tune unless load testing.

### Common Pitfalls

- **Forgetting `expire_on_commit=False`** — causes
  `DetachedInstanceError` when accessing attributes
  after commit in async contexts.
- **Mixing sync and async engines** — never use
  `create_engine()` with `asyncpg`. Always use
  `create_async_engine()`.
- **Not closing the engine** — call `engine.dispose()`
  in the FastAPI shutdown handler to release pool
  connections cleanly.
