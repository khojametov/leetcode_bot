from aiogram import Bot, Dispatcher, types

from settings import settings

TOKEN = settings.api_token

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    username = message.chat.username
    if not username:
        await message.answer("Please, set your username in Telegram settings")
    await message.answer("Hello Vaska che tam")
