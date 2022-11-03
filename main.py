import os

from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot

from bot import bot, dp, TOKEN
from settings import settings


# webhook settings
WEBHOOK_HOST = settings.webhook_host
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
        print("Webhook set to ", WEBHOOK_URL)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()


@app.post(WEBHOOK_PATH)
async def bot_webhook(updates: dict):
    telegram_update = types.Update(**updates)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)
