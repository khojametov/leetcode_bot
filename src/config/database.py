from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings

Base = declarative_base()


def get_db_url():
    return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None
        self.database_url = get_db_url()

    def __getattr__(self, name):
        return getattr(self._session, name)

    async def init(self):
        self._engine = create_async_engine(self.database_url, echo=True, future=True)

        self._session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )()

    async def execute_query(self, statement):
        result = await self._session.execute(statement)
        return result.scalars().all()


db = AsyncDatabaseSession()
