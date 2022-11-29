import asyncio
import os

from rocketry import Rocketry
from rocketry.conds import every, daily

from src.config import settings
from src.scripts import create_statistics, top_solved, clean_left_members

app = Rocketry(config={"task_execution": "async"})

time_create_statistics = os.environ.get()

# @app.task(every("60 seconds"))
# async def repeat():
#     print("Hello World")
#     await create_statistics()
#     print("Done")


@app.task(daily.at(settings.time_create_statistics))
async def scheduler_create_statistics():
    await create_statistics()


@app.task(daily.at(settings.time_top_solved))
async def scheduler_top_solved():
    await top_solved()


@app.task(daily.at(settings.time_clean_left_members))
async def scheduler_clean_left_members():
    await clean_left_members()
