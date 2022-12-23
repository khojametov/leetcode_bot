import logging

from aiogram import Router, types

from src.bot import redis
from src.database import db
from src.models import User
from datetime import timedelta, date

router = Router()


@router.chat_join_request()
async def join(req: types.ChatJoinRequest, msg: types.Message):
    chat_id = req.from_user.id
    data = await redis.hgetall(chat_id)
    if data and "approved" in data and data["approved"] == "1":
        try:
            user = User(
                chat_id=chat_id,
                telegram_username=data["username"],
                leetcode_profile=data["leetcode_profile"],
                full_name=data["full_name"],
            )
            db.add(user)
            await db.commit()

            from src.scripts import create_statistic_for_user

            await create_statistic_for_user(user, date.today() - timedelta(days=1))
            await create_statistic_for_user(user, date.today())
            await req.approve()
        except Exception as e:
            logging.error(e)
            db.rollback()
            await msg.answer(
                chat_id=chat_id, text="Something went wrong please contact to admins"
            )
    else:
        await req.decline()
