from __future__ import annotations

import os
from typing import Any


def create_database_engine() -> Any | None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        return None

    from sqlalchemy.ext.asyncio import create_async_engine

    async_database_url = database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
    return create_async_engine(async_database_url, echo=False)


async def dispose_database_engine(database_engine: Any | None) -> None:
    if database_engine is not None:
        await database_engine.dispose()
