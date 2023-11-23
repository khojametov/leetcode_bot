from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import BaseCRUDService
from src.models import User, Statistic
from src.common.types import ModelType
from sqlalchemy.orm import selectinload
from sqlmodel import select, func


class UsersCRUDService(BaseCRUDService[User]):
    async def get_with_statistics(self, db: AsyncSession) -> ModelType:
        result = await db.execute(
            self.base_query().options(selectinload(self.model.statistics))
        )
        return result.scalars().all()

    async def get_by_chat_id(self, db: AsyncSession, chat_id: str) -> ModelType:
        result = await db.execute(
            self.base_query().filter(self.model.chat_id == chat_id)
        )
        return result.scalars().one_or_none()

    async def get_rating(self, db: AsyncSession) -> list[Row | Row]:
        total = func.sum(Statistic.easy + Statistic.medium + Statistic.hard).label(
            "total"
        )
        score = func.sum(
            3 * Statistic.hard + 2 * Statistic.medium + Statistic.easy
        ).label("score")
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
