from src.database import AsyncDatabaseSession
from src.crud.base import BaseCRUDService
from src.models import User, Statistic
from src.types import ModelType
from sqlalchemy.orm import selectinload
from sqlmodel import select, func


class UsersCRUDService(BaseCRUDService[User]):
    async def get_with_statistics(self, db: AsyncDatabaseSession) -> ModelType:
        result = await db.execute(self.base_query().options(selectinload(self.model.statistics)))
        return result.scalars().all()

    async def get_by_chat_id(self, db: AsyncDatabaseSession, chat_id: str) -> ModelType:
        result = await db.execute(self.base_query().filter(self.model.chat_id == chat_id))
        return result.scalars().first()

    async def get_rating(self, db: AsyncDatabaseSession) -> ModelType:
        total = func.sum(Statistic.easy + Statistic.medium + Statistic.hard).label("total")
        score = func.sum(3 * Statistic.hard + 2 * Statistic.medium + Statistic.easy).label(
            "score"
        )
        query = (
            select(
                User,
                total,
                score,
            )
            .join(Statistic)
            .group_by(User.id)
            .order_by(total.desc(), score.desc())
        )
        result = await db.execute(query)
        return result.all()
