import asyncio

import uvicorn
from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot

from src.scheduler import app_rocketry
from src.config.settings import settings
from src.bot import bot, dp
from src.bot import constants

WEBHOOK_PATH = f"/bot/{settings.API_TOKEN}"
WEBHOOK_URL = f"{settings.WEBHOOK_HOST}{WEBHOOK_PATH}"

app = FastAPI()

commands = [
    types.BotCommand(command="/" + constants.START, description="Start the bot"),
    types.BotCommand(
        command="/" + constants.REGISTER, description="Register for leetcode group"
    ),
    types.BotCommand(
        command="/" + constants.MY_PROFILE, description="Your profile info"
    ),
    types.BotCommand(command="/" + constants.ADMINS, description="Contact to admins"),
    types.BotCommand(
        command="/" + constants.RATING, description="Leetcode group rating"
    ),
]


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    print(webhook_info.url)
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)
        print("Webhook set to ", WEBHOOK_URL)
    await bot.set_my_commands(commands)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()


@app.post(WEBHOOK_PATH)
async def bot_webhook(updates: dict):
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    telegram_update = types.Update(**updates)
    await dp.process_update(telegram_update)


class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    server = Server(
        config=uvicorn.Config(
            app, workers=1, loop="asyncio", port=settings.PORT, host=settings.HOST
        )
    )

    api = asyncio.create_task(server.serve())
    scheduler = asyncio.create_task(app_rocketry.serve())
    await asyncio.wait([api, scheduler])


if __name__ == "__main__":
    asyncio.run(main())
