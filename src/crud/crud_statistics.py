from src.crud.base import BaseCRUDService
from src.models import Statistic
from src.common.types import ModelType
from datetime import date
from src.config.database import AsyncDatabaseSession


class StatisticsCRUDService(BaseCRUDService[Statistic]):
    async def get_statistic_by_date(
        self, db: AsyncDatabaseSession, user_id: int, date: date
    ) -> ModelType:
        result = await db.execute(
            self.base_query().filter(
                self.model.user_id == user_id, self.model.date == date
            )
        )
        return result.scalars().first()
