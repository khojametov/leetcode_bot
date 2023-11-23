import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy_utils import create_database, drop_database, database_exists
from sqlmodel import SQLModel

from tests.session import TestSession


@pytest.fixture(scope="session")
def db_engine() -> AsyncEngine:
    return create_async_engine(
        "postgresql+asyncpg://localhost/test_leetcode_db", echo=True, future=True
    )


@pytest.fixture(scope="session")
def _create_database():
    db_url = "postgresql://localhost/test_leetcode_db"
    if database_exists(db_url):
        drop_database(db_url)
    create_database(db_url)


@pytest_asyncio.fixture(autouse=True)
async def db_session(db_engine: AsyncEngine, _create_database):
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    TestSession.configure(bind=db_engine)
    async with TestSession(expire_on_commit=False) as session:
        yield session

    await TestSession.remove()
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await db_engine.dispose()
