from datetime import datetime
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Statistic
from src.crud import user as crud_user


@pytest_asyncio.fixture
async def user_with_statistics(db_session: AsyncSession) -> User:
    user = User(
        chat_id="123",
        telegram_username="@username",
        leetcode_profile="test",
        full_name="John Doe",
    )
    statistic = Statistic(easy=1, medium=2, hard=3, date=datetime.now(), user=user)
    db_session.add(user)
    db_session.add(statistic)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def users(db_session: AsyncSession) -> tuple[User, User]:
    user1 = User(
        chat_id="123",
        telegram_username="@username1",
        leetcode_profile="test1",
        full_name="John Doe",
    )
    user2 = User(
        chat_id="234",
        telegram_username="@username2",
        leetcode_profile="test2",
        full_name="Jonny Deep",
    )
    statistic1 = Statistic(easy=10, medium=10, hard=10, date=datetime.now(), user=user1)
    statistic2 = Statistic(easy=10, medium=10, hard=11, date=datetime.now(), user=user2)
    db_session.add(user1)
    db_session.add(user2)
    db_session.add(statistic1)
    db_session.add(statistic2)
    await db_session.commit()
    return user1, user2


def get_score(statistic: Statistic):
    return 3 * statistic.hard + 2 * statistic.medium + statistic.easy


def get_total(statistic: Statistic):
    return statistic.hard + statistic.medium + statistic.easy


@pytest.mark.asyncio
async def test_get_with_statistics_ok(
    db_session: AsyncSession, user_with_statistics: User
):
    result = await crud_user.get_with_statistics(db_session)
    assert result[0] == user_with_statistics
    assert result[0].statistics == user_with_statistics.statistics


@pytest.mark.asyncio
async def test_get_by_chat_id(db_session: AsyncSession, user_with_statistics: User):
    result = await crud_user.get_by_chat_id(
        db_session, chat_id=user_with_statistics.chat_id
    )
    assert result == user_with_statistics

    result = await crud_user.get_by_chat_id(db_session, chat_id="wrong chat id")
    assert result is None


@pytest.mark.asyncio
async def test_get_rating(db_session: AsyncSession, users: List[User]):
    result = await crud_user.get_rating(db_session)
    assert result[0] == (
        users[1],
        get_total(users[1].statistics[0]),
        get_score(users[1].statistics[0]),
    )
    assert result[1] == (
        users[0],
        get_total(users[0].statistics[0]),
        get_score(users[0].statistics[0]),
    )
