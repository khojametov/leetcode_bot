from datetime import date

import src.crud as crud
from src.config import settings
from config.database import db
from src.crawler import get_solved_problems
from src.models import User
from src.bot import bot


async def create_statistic_for_user(user: User, day: date) -> None:
    easy, medium, hard = await get_solved_problems(user.leetcode_profile)
    statistic = await crud.statistic.get_statistic_by_date(db, user.id, day)
    if statistic:
        statistic.hard = hard
        statistic.medium = medium
        statistic.easy = easy
    else:
        data = {
            "user_id": user.id,
            "easy": easy,
            "medium": medium,
            "hard": hard,
            "date": day,
        }
        await crud.statistic.create(db, data)


async def create_statistics() -> None:
    users = await crud.user.list(db)
    for user in users:
        await create_statistic_for_user(user, date.today())


async def top_solved() -> str:
    users = crud.user.get_with_statistics(db)

    solved_for_today = [user.get_solved() for user in users]
    sorted_by_total = sorted(
        solved_for_today,
        key=lambda x: (x["total"], x["hard"], x["medium"], x["easy"]),
        reverse=True,
    )
    message = "Top solved for today\n\nsolved  username\n"
    for i in range(10):
        if sorted_by_total[i][1] == 0:
            break
        message += f"{sorted_by_total[i][1]}  {sorted_by_total[i][0]}\n"
    return message


async def clean_left_members() -> None:
    users = crud.user.list(db)
    for user in users:
        try:
            info = await bot.get_chat_member(
                chat_id=settings.GROUP_ID, user_id=user.chat_id
            )
            if info.status != "member":
                await db.delete(user)
                await db.commit()
        except Exception as e:
            print(e)
            continue

    await db.close()
