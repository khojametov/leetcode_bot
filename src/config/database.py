from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings


def get_db_url() -> str:
    return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


# class AsyncDatabaseSession:
#     def __init__(self):
#         self._session = None
#         self._engine = None
#         self.database_url = get_db_url()
#
#     def __getattr__(self, name):
#         return getattr(self._session, name)
#
#     async def init(self):
#         self._engine = create_async_engine(self.database_url, echo=True, future=True)
#
#         self._session = sessionmaker(
#             self._engine, expire_on_commit=False, class_=AsyncSession
#         )()


engine = create_async_engine(get_db_url(), echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# db = AsyncDatabaseSession()
