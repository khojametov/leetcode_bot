from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import async_session


async def get_db() -> Generator[AsyncSession, None, None]:
    with async_session() as _session:
        yield _session
