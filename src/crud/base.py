from typing import Generic, Type
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from src.config.database import AsyncSession
from src.common.types import ModelType, DataDict


class BaseCRUDService(Generic[ModelType]):
    model: Type[ModelType]
    create_fields: set[str]
    update_fields: set[str]

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.create_fields = set(model.__fields__.keys())
        self.update_fields = set(model.__fields__.keys()) - {"id"}

    def _set_field_sets(self) -> None:
        model_fields = set(self.model.__fields__.keys())
        for field_set in ["create_fields", "update_fields"]:
            if not hasattr(self, field_set):
                setattr(self, field_set, model_fields)

    def base_query(self) -> SelectOfScalar[ModelType]:
        return select(self.model)

    async def get(self, db: AsyncSession, id: int) -> ModelType:
        result = await db.execute(self.base_query().filter(self.model.id == id))
        return result.scalars().first()

    async def list(self, db: AsyncSession) -> list[ModelType]:
        result = await db.execute(self.base_query())
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, data: DataDict, commit: bool = True
    ) -> ModelType:
        data = await self.before_create(db, data)
        model = await self.perform_create(db, data, commit)
        await self.after_create(db, model)
        return model

    async def before_create(self, db: AsyncSession, data: DataDict) -> dict:
        return data

    async def after_create(self, db: AsyncSession, model: ModelType) -> dict:
        pass

    async def perform_create(
        self, db: AsyncSession, data: DataDict, commit: bool = True
    ) -> ModelType:
        model = self.model(**data)
        db.add(model)

        if commit:
            await db.commit()

        return model
