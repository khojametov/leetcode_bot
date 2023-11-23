from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.config.settings import settings

bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
