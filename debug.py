import asyncio

from src.scripts import clean_left_members


async def test():
    # await db.init()
    # x = await top_solved()
    # print(x)
    await clean_left_members()


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
