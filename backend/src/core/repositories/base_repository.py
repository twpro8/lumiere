from typing import Sequence, Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas.base_schema import BaseSchema
from src.core.postgres import UUIDBase


class BaseRepository[T: UUIDBase, R: BaseSchema]:
    model: type[T]
    schema: type[R]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[R]:
        query = select(self.model).filter_by(**filter_by).limit(limit).offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.schema.model_validate(model) for model in models]

    async def get_one(self, **filter_by: Any) -> R | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.schema.model_validate(model) if model else None

    async def create(self, data: BaseModel) -> R:
        statement = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(statement)
        model = result.scalar_one()
        return self.schema.model_validate(model)

    async def update(self, id_: UUID, data: BaseModel) -> R:
        statement = (
            update(self.model)
            .where(self.model.id == id_)
            .values(**data.model_dump())
            .returning(self.model)
        )
        result = await self.session.execute(statement)
        model = result.scalar_one()
        return self.schema.model_validate(model)

    async def delete(self, id_: UUID) -> None:
        statement = delete(self.model).where(self.model.id == id_)
        await self.session.execute(statement)
