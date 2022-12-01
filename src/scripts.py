from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import db
from src.crawler import get_solved_problems
from src.models import User, Statistic
from src.bot import bot


async def create_statistic_for_user(user: User, day: date) -> None:
    easy, medium, hard = await get_solved_problems(user.leetcode_profile)
    query = select(Statistic).filter(
        Statistic.user_id == user.id, Statistic.date == day
    )
    result = await db.execute(query)
    statistic = result.scalars().first()
    if statistic:
        statistic.hard = hard
        statistic.medium = medium
        statistic.easy = easy
    else:
        statistic = Statistic(
            user_id=user.id, easy=easy, medium=medium, hard=hard, date=day
        )
        db.add(statistic)
    await db.commit()


async def create_statistics() -> None:
    query = select(User)
    users = await db.execute(query)
    users = users.scalars().all()
    for user in users:
        await create_statistic_for_user(user, date(2022, 11, 24))


async def top_solved() -> str:
    query = select(User).options(selectinload(User.statistics))
    result = await db.execute(query)
    users = result.scalars().all()

    solved_for_today = [user.get_solved() for user in users]
    sorted_by_total = sorted(
        solved_for_today, key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True
    )
    message = "Top solved for today\n\nsolved  username\n"
    for i in range(10):
        if sorted_by_total[i][1] == 0:
            break
        message += f"{sorted_by_total[i][1]}  {sorted_by_total[i][0]}\n"
    return message


async def clean_left_members() -> None:
    await db.init()
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    for user in users:
        try:
            info = await bot.get_chat_member(
                chat_id=settings.group_id, user_id=user.chat_id
            )
            if info.status != "member":
                await db.delete(user)
                await db.commit()
        except Exception as e:
            print(e)
            continue

    await db.close()
