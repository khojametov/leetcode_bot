import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, select

from src.crud import BaseCRUDService
from src.models import BaseModel


class DummyModel(BaseModel, table=True):
    __tablename__ = "dummy"

    id: int = Field(default=None, primary_key=True)

    name: str
    foo: str


@pytest_asyncio.fixture
async def dummy(db_session: AsyncSession) -> DummyModel:
    instance = DummyModel(name="dummy", foo="dummy")
    db_session.add(instance)
    await db_session.commit()
    return instance


crud = BaseCRUDService(model=DummyModel)


@pytest.mark.asyncio
async def test_create(db_session: AsyncSession):
    data = {"name": "a", "foo": "b"}
    obj = await crud.create(db_session, data)
    result = await db_session.execute(select(DummyModel))
    assert result.one()[0] == obj


@pytest.mark.asyncio
async def test_get(db_session: AsyncSession, dummy: DummyModel):
    result = await crud.get(db_session, dummy.id)
    assert result == dummy


@pytest.mark.asyncio
async def test_list(db_session: AsyncSession, dummy: DummyModel):
    result = await crud.list(db_session)
    assert len(result) == 1
    assert result[0] == dummy
