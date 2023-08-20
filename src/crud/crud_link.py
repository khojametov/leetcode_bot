from src.crud.base import BaseCRUDService
from src.models import Link
from src.types import ModelType
from datetime import date, datetime
from src.database import AsyncDatabaseSession


class LinksCRUDService(BaseCRUDService[Link]):
    async def get_unexpired(self, db: AsyncDatabaseSession, chat_id: str) -> ModelType:
        result = await db.execute(self.base_query().filter(self.model.chat_id == chat_id, Link.expire_date > datetime.now()))
        return result.scalars().first()