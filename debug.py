import asyncio
from sqlalchemy import select, func

from config.database import db
from src.models import Statistic, User


async def test():
    await db.init()
    total = func.max(Statistic.easy + Statistic.medium + Statistic.hard).label("total")
    score = func.max(3 * Statistic.hard + 2 * Statistic.medium + Statistic.easy).label(
        "score"
    )
    query = (
        select(
            User,
            total,
            score,
        )
        .group_by(User.id)
        .join(Statistic)
        .order_by(total.desc())
    )
    result = await db.execute(query)
    statistics = result.fetchall()
    print(statistics)
    # x = await top_solved()
    # print(x)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
