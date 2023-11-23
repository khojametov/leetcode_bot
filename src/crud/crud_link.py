from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import BaseCRUDService
from src.models import Link
from src.common.types import ModelType
from datetime import datetime


class LinksCRUDService(BaseCRUDService[Link]):
    async def get_unexpired(self, db: AsyncSession, chat_id: str | int) -> ModelType:
        result = await db.execute(
            self.base_query().filter(
                self.model.chat_id == str(chat_id), Link.expire_date > datetime.now()
            )
        )
        return result.scalars().first()
