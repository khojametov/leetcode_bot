from aiogram import Router, F, types, html
from prettytable import PrettyTable
from sqlalchemy import func, select

from bot.keyboards.reply import main_menu
from src.database import db
from src.models import Statistic, User

router = Router()


@router.message(F.text == "Back to main menu")
async def back_to_main_menu(message: types.Message):
    await message.answer(text="back to menu", reply_markup=main_menu())


@router.message(F.text == "Contact to admins")
async def contact_to_admins(message: types.Message):
    await message.answer(text="@dilshodbek_xojametov")


@router.message(F.text == "Rating")
async def rating(message: types.Message):
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
    fields = ["#", "username", "solved", "score"]
    table = PrettyTable(fields)
    values = []
    for i, statistic in enumerate(statistics):
        values.append(
            [i + 1, statistic[0].telegram_username, statistic[1], statistic[2]]
        )
    table.add_rows(values)
    await message.answer(text=html.code(table))
