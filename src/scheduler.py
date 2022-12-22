from rocketry import Rocketry
from rocketry.conds import every, daily

from src.config import settings
from src.scripts import create_statistics, top_solved, clean_left_members

app_rocketry = Rocketry(config={"task_execution": "async"})


# @app_rocketry.task(every("60 seconds"))
# async def repeat():
#     print("Hello World")


@app_rocketry.task(daily.at(settings.time_create_statistics))
async def scheduler_create_statistics():
    await create_statistics()


@app_rocketry.task(daily.at(settings.time_top_solved))
async def scheduler_top_solved():
    await top_solved()


@app_rocketry.task(daily.at(settings.time_clean_left_members))
async def scheduler_clean_left_members():
    await clean_left_members()
