from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import BaseCRUDService
from src.models import Statistic
from src.common.types import ModelType
from datetime import date


class StatisticsCRUDService(BaseCRUDService[Statistic]):
    async def get_statistic_by_date(
        self, db: AsyncSession, user_id: int, date_: date
    ) -> ModelType:
        result = await db.execute(
            self.base_query().filter(
                self.model.user_id == user_id, self.model.date == date_
            )
        )
        return result.scalars().first()
