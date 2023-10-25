from datetime import datetime, timedelta
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import statistic as crud_statistics
from src.models import User, Statistic


@pytest.fixture
def date_fixture() -> datetime:
    return datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S") - timedelta(
        days=1
    )


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    user_ = User(
        chat_id="123",
        telegram_username="@username",
        leetcode_profile="test",
        full_name="John Doe",
    )
    db_session.add(user_)
    await db_session.commit()
    return user_


@pytest_asyncio.fixture
async def statistics(
    db_session: AsyncSession, user: User, date_fixture
) -> List[Statistic]:
    statistic1 = Statistic(
        easy=10, medium=10, hard=10, date=date_fixture - timedelta(days=1), user=user
    )
    statistic2 = Statistic(easy=10, medium=10, hard=11, date=date_fixture, user=user)
    db_session.add(statistic1)
    db_session.add(statistic2)
    await db_session.commit()
    return [statistic1, statistic2]


@pytest.mark.asyncio
async def test_get_statistic_by_date_ok(
    db_session: AsyncSession, date_fixture, user: User, statistics: List[Statistic]
):
    result = await crud_statistics.get_statistic_by_date(
        db_session, user_id=user.id, date=date_fixture
    )
    assert result == statistics[1]
