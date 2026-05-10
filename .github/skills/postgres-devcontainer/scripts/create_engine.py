"""Optional async database engine bootstrapper.

Creates a SQLAlchemy async engine from DATABASE_URL when the
environment variable is set.  Returns None when absent so the
app continues in in-memory mode.
"""

import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

DATABASE_URL = os.environ.get("DATABASE_URL")


def create_engine() -> AsyncEngine | None:
    if DATABASE_URL is None:
        return None
    return create_async_engine(
        DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )


engine = create_engine()
