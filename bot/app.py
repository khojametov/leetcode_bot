import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from bot.handlers import setup_routers

from src.config import settings as config


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    )

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    router = setup_routers()
    dp.include_router(router)

    if config.custom_bot_api:
        bot.session.api = TelegramAPIServer.from_base(
            config.custom_bot_api, is_local=True
        )

    try:
        if not config.webhook_domain:
            await bot.delete_webhook()
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        else:
            aiohttp_logger = logging.getLogger("aiohttp.access")
            aiohttp_logger.setLevel(logging.CRITICAL)

            await bot.set_webhook(
                url=config.webhook_domain + config.webhook_path,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types(),
            )

            app = web.Application()
            SimpleRequestHandler(dispatcher=dp, bot=bot).register(
                app, path=config.webhook_path
            )
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=config.app_host, port=config.app_port)
            await site.start()

            await asyncio.Event().wait()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
