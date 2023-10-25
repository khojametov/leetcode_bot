from datetime import datetime, timedelta
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Link
from src.crud import link as link_crud


@pytest_asyncio.fixture
async def unexpired_link(db_session: AsyncSession):
    expire_date = datetime.now() + timedelta(days=1)
    link = Link(chat_id="123", invite_link="link.com", expire_date=expire_date)
    db_session.add(link)
    await db_session.commit()
    return link


@pytest_asyncio.fixture
async def expired_link(db_session: AsyncSession):
    expire_date = datetime.now() - timedelta(days=1)
    link = Link(chat_id="123", invite_link="link.com", expire_date=expire_date)
    db_session.add(link)
    await db_session.commit()
    return link


@pytest.mark.asyncio
async def test_get_unexpired_ok(db_session: AsyncSession, unexpired_link: Link):
    result = await link_crud.get_unexpired(db_session, chat_id=unexpired_link.chat_id)
    assert result == unexpired_link


@pytest.mark.asyncio
async def test_get_unexpired_no_result(db_session: AsyncSession, expired_link: Link):
    result = await link_crud.get_unexpired(db_session, chat_id=expired_link.chat_id)
    assert result is None
