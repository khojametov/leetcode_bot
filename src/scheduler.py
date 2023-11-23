from fastapi import Depends
from rocketry import Rocketry
from rocketry.conds import daily
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.scripts import create_statistics, top_solved, clean_left_members
from src.core.deps import get_db

app_rocketry = Rocketry(config={"task_execution": "async"})


# @app_rocketry.task(every("60 seconds"))
# async def repeat():
#     print("Hello World")


@app_rocketry.task(daily.at(settings.TIME_CREATE_STATISTICS))
async def scheduler_create_statistics(db: AsyncSession = Depends(get_db)):
    await create_statistics(db)


@app_rocketry.task(daily.at(settings.TIME_TOP_SOLVED))
async def scheduler_top_solved(db: AsyncSession = Depends(get_db)):
    await top_solved(db)


@app_rocketry.task(daily.at(settings.TIME_CLEAN_LEFT_MEMBERS))
async def scheduler_clean_left_members(db: AsyncSession = Depends(get_db)):
    await clean_left_members(db)
