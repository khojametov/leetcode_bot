import asyncio

import aioredis
import uvicorn
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot


from src.database import db
from src.config import settings
from src.scheduler import app as app_rocketry


TOKEN = settings.api_token
# webhook settings
WEBHOOK_HOST = settings.webhook_host
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

redis = aioredis.from_url("redis://localhost:6369/0", decode_responses=True)

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    await db.init()
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


class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    server = Server(config=uvicorn.Config(app, workers=1, loop="asyncio", port=7777))

    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([api, sched])


if __name__ == "__main__":
    asyncio.run(main())
