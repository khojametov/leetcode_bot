from aiogram import types
from functools import wraps


class Permission:
    def private_chat(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(message: types.Message, *args, **kwargs):
                if message.chat.type != "private":
                    print("It is not private chat")
                    return
                return await func(message, *args, **kwargs)

            return wrapper

        return decorator

    def set_username(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(message: types.Message, *args, **kwargs):
                if not message.from_user.username:
                    await message.reply("Please set username")
                    return
                return await func(message, *args, **kwargs)

            return wrapper

        return decorator


permissions = Permission()
