import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message


class PrivateFilter(BaseFilter):
    def __call__(self, message: Message, *args, **kwargs) -> bool:
        if message.chat.type != "private":
            logging.info("It is not private chat")
            return False
        return True


class UsernameFilter(BaseFilter):
    def __call__(self, message: Message, *args, **kwargs) -> bool:
        if not message.from_user.username:
            await message.reply("Please set username")
            return False
        return True
