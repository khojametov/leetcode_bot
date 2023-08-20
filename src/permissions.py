from aiogram import types
from functools import wraps


class Permissions:
    @staticmethod
    def private_chat(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            if message.chat.type == "private":
                return await func(message, *args, **kwargs)
            else:
                print("It is not a private chat")

        return wrapper

    @staticmethod
    def set_username(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            if message.from_user.username:
                return await func(message, *args, **kwargs)
            else:
                await message.reply("Please set a username")

        return wrapper


permissions = Permissions()
