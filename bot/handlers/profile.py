from aiogram import Router, F, types
from sqlalchemy import select

from src.bot import redis
from src.database import db
from src.models import User

router = Router()


@router.message(F.text == "My profile")
async def my_profile(message: types.Message):
    query = select(User).filter(User.chat_id == message.chat.id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        profile_info = "Chat id: {}\nFull name: {}\nLeetcode profile: {}".format(
            user.chat_id, user.full_name, user.leetcode_profile
        )
    else:
        redis_data = await redis.hgetall(message.chat.id)
        if not redis_data:
            await message.answer(text="You have not registered yet")
            return
        profile_info = "Chat id: {}\nFull name: {}\nLeetcode profile: {}".format(
            message.chat.id, redis_data["full_name"], redis_data["leetcode_profile"]
        )
    await message.answer(text=profile_info)
