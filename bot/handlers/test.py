from aiogram import Router, types
from sqlalchemy import select, func
from src.database import db
from src.models import Statistic

router = Router()


@router.message(commands=["test"])
async def test():
    query = select(Statistic.date, func.count(Statistic.id)).group_by(Statistic.date)
    result = await db.execute(query)
    print(result.scalars().all())
